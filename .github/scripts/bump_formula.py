"""Generate and atomically update reproducible formulas from an exporter uv.lock."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import time
import tomllib
import urllib.parse
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

POLL_ATTEMPTS = 20
POLL_DELAY_SECONDS = 15
PYPI_HOST = "files.pythonhosted.org"
FORMULAS: Mapping[str, Path] = {
    "immich-export": Path("Formula/immich-export.rb"),
    "paperless-export": Path("Formula/paperless-export.rb"),
    "unpacksort": Path("Formula/unpacksort.rb"),
}
TARGETS = ("macos-arm64", "macos-x86_64", "linux-arm64", "linux-x86_64")
_VERSION_RE = re.compile(
    r"(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
)
_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_LOCK_URL_RE = re.compile(
    r"https://raw\.githubusercontent\.com/fileworks/"
    r"(?P<package>immich-export|paperless-export|unpacksort)/[0-9a-f]{40}/uv\.lock"
)
_WHEEL_TAG_RE = re.compile(
    r"-(?P<python>cp\d+|py\d(?:\.py\d+)*)-(?P<abi>[^-]+)-(?P<platform>.+)\.whl$"
)


class BumpError(RuntimeError):
    """A request or release cannot be applied safely."""


@dataclass(frozen=True, order=True)
class ReleaseVersion:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, value: str) -> ReleaseVersion:
        match = _VERSION_RE.fullmatch(value)
        if match is None:
            raise BumpError(f"Invalid release version: {value!r}")
        return cls(*(int(match.group(name)) for name in ("major", "minor", "patch")))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


@dataclass(frozen=True)
class Artifact:
    url: str
    sha256: str


@dataclass(frozen=True)
class LockedResource:
    name: str
    version: str
    artifacts: Mapping[str, Artifact]


@dataclass(frozen=True)
class FormulaConfig:
    class_name: str
    description: str
    homepage: str
    extra: str | None = None


CONFIGS: Mapping[str, FormulaConfig] = {
    "immich-export": FormulaConfig(
        class_name="ImmichExport",
        description="Export Immich into a plain, human-readable folder tree",
        homepage="https://github.com/fileworks/immich-export",
    ),
    "paperless-export": FormulaConfig(
        class_name="PaperlessExport",
        description="Paperless-ngx export wrapper and atomic tax view",
        homepage="https://github.com/fileworks/paperless-export",
        extra="pdf",
    ),
    "unpacksort": FormulaConfig(
        class_name="Unpacksort",
        description="Safely unpack, deduplicate, classify, and sort nested archives",
        homepage="https://github.com/fileworks/unpacksort",
    ),
}


class BumpOutcome(str, Enum):
    UPDATED = "updated"
    EQUAL = "equal"
    STALE = "stale"
    BOOTSTRAP_REQUIRED = "bootstrap_required"


def validate_formula(value: str) -> str:
    if value not in FORMULAS:
        allowed = ", ".join(sorted(FORMULAS))
        raise BumpError(f"Unsupported formula {value!r}; expected one of: {allowed}")
    return value


def _normalized_project_name(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).lower()


def _validate_artifact(url: str, digest: str, *, suffix: str) -> Artifact:
    parsed = urllib.parse.urlparse(url)
    if (
        parsed.scheme != "https"
        or parsed.hostname != PYPI_HOST
        or parsed.query
        or parsed.fragment
        or not parsed.path.endswith(suffix)
        or _SHA256_RE.fullmatch(digest) is None
    ):
        raise BumpError(f"Invalid immutable release artifact: {url!r}")
    return Artifact(url=url, sha256=digest)


def parse_pypi_sdist(
    package: str,
    requested: ReleaseVersion,
    payload: Mapping[str, Any],
) -> Artifact:
    info = payload.get("info")
    urls = payload.get("urls")
    if not isinstance(info, Mapping) or not isinstance(urls, list):
        raise BumpError("PyPI response is missing info or artifact data")
    if _normalized_project_name(str(info.get("name", ""))) != package:
        raise BumpError("PyPI response project does not match the requested formula")
    if str(info.get("version", "")) != str(requested):
        raise BumpError("PyPI response version does not match the requested release")

    sdists = [
        item
        for item in urls
        if isinstance(item, Mapping) and item.get("packagetype") == "sdist"
    ]
    if len(sdists) != 1:
        raise BumpError(f"Expected exactly one sdist, found {len(sdists)}")
    artifact = sdists[0]
    url = str(artifact.get("url", ""))
    parsed = urllib.parse.urlparse(url)
    filename = urllib.parse.unquote(Path(parsed.path).name)
    if filename != f"{package.replace('-', '_')}-{requested}.tar.gz":
        raise BumpError("PyPI sdist filename does not match the requested release")
    digests = artifact.get("digests")
    digest = str(digests.get("sha256", "")) if isinstance(digests, Mapping) else ""
    return _validate_artifact(url, digest, suffix=".tar.gz")


def fetch_sdist(
    package: str,
    version: ReleaseVersion,
    *,
    attempts: int = POLL_ATTEMPTS,
    delay_seconds: float = POLL_DELAY_SECONDS,
    opener: Callable[..., Any] = urllib.request.urlopen,
    sleeper: Callable[[float], None] = time.sleep,
) -> Artifact:
    endpoint = f"https://pypi.org/pypi/{package}/{version}/json"
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            with opener(endpoint, timeout=30) as response:
                payload = json.load(response)
            if not isinstance(payload, Mapping):
                raise BumpError("PyPI response is not a JSON object")
            return parse_pypi_sdist(package, version, payload)
        except Exception as exc:  # noqa: BLE001 - publication delay and HTTP failures retry together
            last_error = exc
            if attempt < attempts:
                print(
                    f"[{attempt}/{attempts}] release is not ready ({exc}); retrying",
                    file=sys.stderr,
                )
                sleeper(delay_seconds)
    raise BumpError(f"PyPI release {package}=={version} was not ready: {last_error}")


def validate_lock_provenance(package: str, url: str, digest: str) -> None:
    match = _LOCK_URL_RE.fullmatch(url)
    if match is None or match.group("package") != package:
        raise BumpError("Lock URL must name the exporter's immutable Git commit")
    if _SHA256_RE.fullmatch(digest) is None:
        raise BumpError("Lock provenance is missing a valid SHA-256 digest")


def fetch_lock(
    package: str,
    url: str,
    digest: str,
    *,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> bytes:
    validate_lock_provenance(package, url, digest)
    with opener(url, timeout=30) as response:
        content = response.read()
    actual = hashlib.sha256(content).hexdigest()
    if actual != digest:
        raise BumpError(f"Lock digest mismatch: expected {digest}, got {actual}")
    return content


def _marker_supported(marker: str | None) -> bool:
    """Return whether an edge is selected by Python 3.12 on macOS or Linux.

    uv records marker expressions on dependency edges. Keep this evaluator
    deliberately narrow: a new marker shape blocks publication until generation
    support is reviewed instead of silently selecting the wrong closure.
    """

    if marker is None:
        return True
    decisions = {
        "implementation_name != 'PyPy'": True,
        "os_name == 'nt'": False,
        "platform_python_implementation == 'CPython'": True,
        "platform_python_implementation == 'PyPy'": False,
        "python_full_version < '3.13'": True,
        "python_full_version < '3.14'": True,
        "python_full_version >= '3.13'": False,
        "sys_platform != 'cygwin'": True,
        "sys_platform == 'win32'": False,
        "sys_platform != 'win32'": True,
        "sys_platform == 'darwin'": True,
        "sys_platform == 'linux'": True,
        "platform_system == 'Darwin'": True,
        "platform_system == 'Linux'": True,
    }
    if marker not in decisions:
        raise BumpError(f"Unsupported uv.lock dependency marker: {marker!r}")
    return decisions[marker]


def _wheel_score(filename: str, target: str) -> tuple[int, str] | None:
    match = _WHEEL_TAG_RE.search(filename)
    if match is None:
        return None
    python_tag = match.group("python")
    abi = match.group("abi")
    platform = match.group("platform")
    if platform == "any" and python_tag in {"py3", "py2.py3"} and abi == "none":
        return (0, filename)

    if python_tag == "cp312" and abi == "cp312":
        interpreter_score = 1
    elif python_tag.startswith("cp") and abi == "abi3" and int(python_tag[2:]) <= 312:
        interpreter_score = 2 + (312 - int(python_tag[2:]))
    else:
        return None

    operating_system, architecture = target.split("-", 1)
    if operating_system == "macos":
        if (
            "macosx" not in platform
            or (architecture not in platform and "universal2" not in platform)
        ):
            return None
    elif operating_system == "linux":
        linux_arch = "aarch64" if architecture == "arm64" else architecture
        if "manylinux" not in platform or not platform.endswith(linux_arch):
            return None
    else:
        raise BumpError(f"Unknown generation target: {target}")
    return (interpreter_score, filename)


def _select_artifacts(package: Mapping[str, Any]) -> Mapping[str, Artifact]:
    wheels = package.get("wheels")
    if not isinstance(wheels, list):
        raise BumpError(f"Locked package {package.get('name')!r} has no wheel inventory")
    selected: dict[str, Artifact] = {}
    for target in TARGETS:
        candidates: list[tuple[tuple[int, str], Artifact]] = []
        for wheel in wheels:
            if not isinstance(wheel, Mapping):
                continue
            url = str(wheel.get("url", ""))
            filename = urllib.parse.unquote(Path(urllib.parse.urlparse(url).path).name)
            score = _wheel_score(filename, target)
            raw_hash = str(wheel.get("hash", ""))
            digest = raw_hash.removeprefix("sha256:")
            if score is not None:
                candidates.append((score, _validate_artifact(url, digest, suffix=".whl")))
        if not candidates:
            raise BumpError(
                f"Locked package {package.get('name')!r} has no compatible wheel for {target}"
            )
        selected[target] = min(candidates, key=lambda candidate: candidate[0])[1]
    return selected


def parse_locked_resources(
    package_name: str,
    requested: ReleaseVersion,
    lock_content: bytes,
    *,
    legacy_root_version: ReleaseVersion | None = None,
) -> list[LockedResource]:
    try:
        lock = tomllib.loads(lock_content.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise BumpError(f"uv.lock is not valid UTF-8 TOML: {exc}") from exc
    packages = lock.get("package")
    if not isinstance(packages, list):
        raise BumpError("uv.lock has no package inventory")
    by_name: dict[str, Mapping[str, Any]] = {}
    for package in packages:
        if not isinstance(package, Mapping):
            raise BumpError("uv.lock contains an invalid package record")
        name = _normalized_project_name(str(package.get("name", "")))
        if not name or name in by_name:
            raise BumpError(f"uv.lock contains a duplicate or empty package name: {name!r}")
        by_name[name] = package

    root = by_name.get(package_name)
    accepted_root = legacy_root_version or requested
    if root is None or str(root.get("version", "")) != str(accepted_root):
        raise BumpError("uv.lock project version does not match the requested release")
    config = CONFIGS[package_name]
    pending = list(root.get("dependencies", []))
    if config.extra is not None:
        optional = root.get("optional-dependencies", {})
        if not isinstance(optional, Mapping) or config.extra not in optional:
            raise BumpError(f"uv.lock is missing required extra {config.extra!r}")
        pending.extend(optional[config.extra])

    selected: set[str] = set()
    while pending:
        edge = pending.pop()
        if not isinstance(edge, Mapping):
            raise BumpError("uv.lock contains an invalid dependency edge")
        if not _marker_supported(str(edge["marker"]) if "marker" in edge else None):
            continue
        name = _normalized_project_name(str(edge.get("name", "")))
        if name in selected:
            continue
        dependency = by_name.get(name)
        if dependency is None:
            raise BumpError(f"uv.lock is missing dependency {name!r}")
        selected.add(name)
        children = dependency.get("dependencies", [])
        if not isinstance(children, list):
            raise BumpError(f"uv.lock dependency list for {name!r} is invalid")
        pending.extend(children)

    resources = [
        LockedResource(
            name=name,
            version=str(by_name[name].get("version", "")),
            artifacts=_select_artifacts(by_name[name]),
        )
        for name in sorted(selected)
    ]
    if any(not resource.version for resource in resources):
        raise BumpError("uv.lock contains an unversioned dependency")
    return resources


def read_formula_version(formula_path: Path, package: str) -> ReleaseVersion:
    text = formula_path.read_text(encoding="utf-8")
    match = re.search(
        rf'(?m)^\s*url "[^"]*/{re.escape(package.replace("-", "_"))}-'
        rf'(?P<version>{_VERSION_RE.pattern})\.tar\.gz"$',
        text,
    )
    if match is None:
        raise BumpError(f"{formula_path} URL does not identify a supported release")
    return ReleaseVersion.parse(match.group("version"))


def _resource_block(resource: LockedResource, target: str, indent: str = "  ") -> list[str]:
    artifact = resource.artifacts[target]
    return [
        f'{indent}resource "{resource.name}" do',
        f'{indent}  url "{artifact.url}"',
        f'{indent}  sha256 "{artifact.sha256}"',
        f"{indent}end",
    ]


def _render_resources(resources: list[LockedResource]) -> list[str]:
    universal = [
        resource
        for resource in resources
        if len({artifact for artifact in resource.artifacts.values()}) == 1
    ]
    platform_specific = [resource for resource in resources if resource not in universal]
    lines: list[str] = []
    for operating_system in ("macos", "linux"):
        lines.append(f"  on_{operating_system} do")
        for architecture in ("arm64", "x86_64"):
            ruby_architecture = "arm" if architecture == "arm64" else "intel"
            lines.append(f"    on_{ruby_architecture} do")
            target = f"{operating_system}-{architecture}"
            for resource in platform_specific:
                lines.extend(_resource_block(resource, target, indent="      "))
                lines.append("")
            if lines[-1] == "":
                lines.pop()
            lines.append("    end")
        lines.append("  end")
        lines.append("")
    for resource in universal:
        lines.extend(_resource_block(resource, TARGETS[0]))
        lines.append("")
    return lines


def render_formula(
    package: str,
    version: ReleaseVersion,
    application: Artifact,
    resources: list[LockedResource],
    *,
    lock_url: str,
    lock_sha256: str,
) -> str:
    config = CONFIGS[package]
    resources = sorted(resources, key=lambda resource: resource.name)
    inventory_names = [package, *(resource.name for resource in resources)]
    inventory_lines = [
        "    " + " ".join(inventory_names[index : index + 5])
        for index in range(0, len(inventory_names), 5)
    ]
    lines = [
        "# This file is generated atomically by .github/scripts/bump_formula.py.",
        f"# Runtime lock: {lock_url}",
        f"# Runtime lock SHA-256: {lock_sha256}",
        f"class {config.class_name} < Formula",
        "  include Language::Python::Virtualenv",
        "",
        f'  desc "{config.description}"',
        f'  homepage "{config.homepage}"',
        f'  url "{application.url}"',
        f'  sha256 "{application.sha256}"',
        '  license "MIT"',
        "",
        '  depends_on "hatch" => :build',
        '  depends_on "python@3.12"',
        "",
    ]
    if any(resource.name == "lxml" for resource in resources):
        lines.extend(
            [
                '  uses_from_macos "libxml2"',
                '  uses_from_macos "libxslt"',
                "",
            ]
        )
    lines.extend(_render_resources(resources))
    lines.extend(
        [
            "  RUNTIME_INVENTORY = %w[",
            *inventory_lines,
            "  ].freeze",
            "",
            "  def install",
            '    ENV["PIP_NO_INDEX"] = "1"',
            '    ENV["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"',
            '    system formula_opt_libexec("hatch")/"bin/hatchling", "build", "-t", "wheel"',
            "",
            '    wheelhouse = buildpath/"wheelhouse"',
            "    wheelhouse.mkpath",
            "    resources.each do |resource|",
            "      wheelhouse.install resource.cached_download => resource.downloader.basename",
            "    end",
            "",
            '    venv = virtualenv_create(libexec, "python3.12")',
            '    venv.pip_install Dir[wheelhouse/"*.whl"], build_isolation: false',
            '    wheel = Dir["dist/*.whl"]',
            '    odie "Expected exactly one application wheel" unless wheel.one?',
            "    venv.pip_install_and_link wheel.first, build_isolation: false",
            "  end",
            "",
            "  test do",
            '    assert_match version.to_s, shell_output("#{bin}/' + package + ' --version")',
            '    assert_match "Usage", shell_output("#{bin}/' + package + ' --help")',
        ]
    )
    if package == "unpacksort":
        lines.extend(
            [
                "",
                '    (testpath/"source").mkpath',
                '    (testpath/"source/hello.txt").write("hello from the formula test\\n")',
                '    system "tar", "-czf", testpath/"fixture.tar.gz",',
                '           "-C", testpath/"source", "hello.txt"',
                '    system bin/"unpacksort", testpath/"fixture.tar.gz", testpath/"out"',
                "",
                '    extracted = Dir.glob("#{testpath}/out/**/hello.txt").first',
                '    refute_nil extracted, "unpacksort did not extract the fixture"',
                '    assert_equal "hello from the formula test\\n", File.read(extracted)',
                '    manifest = testpath/"out/manifest.jsonl"',
                '    assert_path_exists manifest',
                '    assert_match "hello.txt", manifest.read',
            ]
        )
    lines.extend(
        [
            "",
            "    script = <<~PYTHON",
            "      import importlib.metadata",
            "      import json",
            "      import pathlib",
            "      import sysconfig",
            "      site = pathlib.Path(sysconfig.get_paths()[\"purelib\"])",
            "      names = sorted(",
            "          distribution.metadata[\"Name\"].lower().replace(\"_\", \"-\").replace(\".\", \"-\")",
            "          for distribution in importlib.metadata.distributions(path=[site])",
            "      )",
            "      print(json.dumps(names))",
            "    PYTHON",
            '    actual = JSON.parse(shell_output("#{libexec}/bin/python -c #{Shellwords.escape(script)}"))',
            "    assert_equal RUNTIME_INVENTORY.sort, actual",
            "  end",
            "end",
            "",
        ]
    )
    return "\n".join(lines)


def atomic_write(path: Path, text: str) -> None:
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        if path.exists():
            os.chmod(temporary, path.stat().st_mode)
        os.replace(temporary, path)
        temporary = None
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except OSError as exc:
        raise BumpError(f"Could not atomically update {path}: {exc}") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def update_formula(
    formula_name: str,
    version_text: str,
    *,
    lock_url: str,
    lock_sha256: str,
    sdist_fetcher: Callable[[str, ReleaseVersion], Artifact] = fetch_sdist,
    lock_fetcher: Callable[[str, str, str], bytes] = fetch_lock,
    legacy_lock_version: str | None = None,
) -> BumpOutcome:
    package = validate_formula(formula_name)
    requested = ReleaseVersion.parse(version_text)
    formula_path = FORMULAS[package]
    if not formula_path.is_file():
        return BumpOutcome.BOOTSTRAP_REQUIRED
    current = read_formula_version(formula_path, package)
    if requested < current:
        return BumpOutcome.STALE
    if package not in CONFIGS:
        return BumpOutcome.BOOTSTRAP_REQUIRED

    lock_content = lock_fetcher(package, lock_url, lock_sha256)
    legacy_root_version = (
        ReleaseVersion.parse(legacy_lock_version) if legacy_lock_version is not None else None
    )
    if legacy_root_version is not None and not (
        package == "immich-export"
        and requested == ReleaseVersion.parse("0.0.4")
        and legacy_root_version == ReleaseVersion.parse("0.0.3")
    ):
        raise BumpError("Legacy lock migration is restricted to Immich Export 0.0.4")
    resources = parse_locked_resources(
        package,
        requested,
        lock_content,
        legacy_root_version=legacy_root_version,
    )
    application = sdist_fetcher(package, requested)
    rendered = render_formula(
        package,
        requested,
        application,
        resources,
        lock_url=lock_url,
        lock_sha256=lock_sha256,
    )
    original = formula_path.read_text(encoding="utf-8")
    if rendered == original:
        return BumpOutcome.EQUAL
    atomic_write(formula_path, rendered)
    if read_formula_version(formula_path, package) != requested:
        raise BumpError("Formula verification did not resolve to the requested version")
    return BumpOutcome.UPDATED


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("formula", choices=sorted(FORMULAS))
    parser.add_argument("version")
    parser.add_argument("--lock-url", required=True)
    parser.add_argument("--lock-sha256", required=True)
    parser.add_argument("--legacy-lock-version")
    args = parser.parse_args(argv)
    try:
        outcome = update_formula(
            args.formula,
            args.version,
            lock_url=args.lock_url,
            lock_sha256=args.lock_sha256,
            legacy_lock_version=args.legacy_lock_version,
        )
    except BumpError as exc:
        parser.exit(2, f"error: {exc}\n")
    print(f"{args.formula} {args.version}: {outcome.value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
