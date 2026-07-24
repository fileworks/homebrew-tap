"""Validate and atomically update a supported formula from a PyPI release."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import time
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
}
_VERSION_RE = re.compile(
    r"(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
)
_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_URL_LINE_RE = re.compile(r'(?m)^(?P<indent>\s*)url "[^"\r\n]+"$')
_SHA_LINE_RE = re.compile(r'(?m)^(?P<indent>\s*)sha256 "[0-9a-f]{64}"$')


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
class Sdist:
    url: str
    sha256: str


class BumpOutcome(str, Enum):
    UPDATED = "updated"
    EQUAL = "equal"
    STALE = "stale"


def validate_formula(value: str) -> str:
    if value not in FORMULAS:
        allowed = ", ".join(sorted(FORMULAS))
        raise BumpError(f"Unsupported formula {value!r}; expected one of: {allowed}")
    return value


def _normalized_project_name(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).lower()


def parse_pypi_sdist(
    package: str,
    requested: ReleaseVersion,
    payload: Mapping[str, Any],
) -> Sdist:
    info = payload.get("info")
    urls = payload.get("urls")
    if not isinstance(info, Mapping) or not isinstance(urls, list):
        raise BumpError("PyPI response is missing info or artifact data")
    if _normalized_project_name(str(info.get("name", ""))) != package:
        raise BumpError("PyPI response project does not match the requested formula")
    if str(info.get("version", "")) != str(requested):
        raise BumpError("PyPI response version does not match the requested release")

    sdists = [item for item in urls if isinstance(item, Mapping) and item.get("packagetype") == "sdist"]
    if len(sdists) != 1:
        raise BumpError(f"Expected exactly one sdist, found {len(sdists)}")
    artifact = sdists[0]
    url = str(artifact.get("url", ""))
    parsed = urllib.parse.urlparse(url)
    expected_stem = package.replace("-", "_")
    filename = urllib.parse.unquote(Path(parsed.path).name)
    if (
        parsed.scheme != "https"
        or parsed.hostname != PYPI_HOST
        or filename != f"{expected_stem}-{requested}.tar.gz"
    ):
        raise BumpError("PyPI sdist URL does not match the requested package and version")
    digests = artifact.get("digests")
    sha256 = str(digests.get("sha256", "")) if isinstance(digests, Mapping) else ""
    if _SHA256_RE.fullmatch(sha256) is None:
        raise BumpError("PyPI sdist is missing a valid SHA-256 digest")
    return Sdist(url=url, sha256=sha256)


def fetch_sdist(
    package: str,
    version: ReleaseVersion,
    *,
    attempts: int = POLL_ATTEMPTS,
    delay_seconds: float = POLL_DELAY_SECONDS,
    opener: Callable[..., Any] = urllib.request.urlopen,
    sleeper: Callable[[float], None] = time.sleep,
) -> Sdist:
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


def read_formula_version(formula_path: Path, package: str) -> ReleaseVersion:
    text = formula_path.read_text(encoding="utf-8")
    matches = list(_URL_LINE_RE.finditer(text))
    if len(matches) != 1:
        raise BumpError(f"{formula_path} does not contain exactly one supported URL line")
    match = matches[0]
    url = re.search(r'"([^"]+)"', match.group(0))
    if url is None:
        raise BumpError(f"{formula_path} has an invalid URL")
    filename = urllib.parse.unquote(Path(urllib.parse.urlparse(url.group(1)).path).name)
    pattern = re.compile(
        rf"{re.escape(package.replace('-', '_'))}-(?P<version>{_VERSION_RE.pattern})\.tar\.gz"
    )
    version_match = pattern.fullmatch(filename)
    if version_match is None:
        raise BumpError(f"{formula_path} URL does not identify a supported {package} release")
    return ReleaseVersion.parse(version_match.group("version"))


def render_formula(text: str, sdist: Sdist) -> str:
    rendered, url_count = _URL_LINE_RE.subn(
        lambda match: f'{match.group("indent")}url "{sdist.url}"',
        text,
    )
    rendered, sha_count = _SHA_LINE_RE.subn(
        lambda match: f'{match.group("indent")}sha256 "{sdist.sha256}"',
        rendered,
    )
    if url_count != 1 or sha_count != 1:
        raise BumpError(
            "Formula did not match the expected unique url/sha256 shape "
            f"(url={url_count}, sha256={sha_count})"
        )
    return rendered


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
    sdist_fetcher: Callable[[str, ReleaseVersion], Sdist] = fetch_sdist,
) -> BumpOutcome:
    package = validate_formula(formula_name)
    requested = ReleaseVersion.parse(version_text)
    formula_path = FORMULAS[package]
    if not formula_path.is_file():
        raise BumpError(f"Known formula is missing: {formula_path}")
    current = read_formula_version(formula_path, package)
    if requested == current:
        return BumpOutcome.EQUAL
    if requested < current:
        return BumpOutcome.STALE

    sdist = sdist_fetcher(package, requested)
    original = formula_path.read_text(encoding="utf-8")
    rendered = render_formula(original, sdist)
    atomic_write(formula_path, rendered)
    if read_formula_version(formula_path, package) != requested:
        raise BumpError("Formula verification did not resolve to the requested version")
    return BumpOutcome.UPDATED


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("formula", choices=sorted(FORMULAS))
    parser.add_argument("version")
    args = parser.parse_args(argv)
    try:
        outcome = update_formula(args.formula, args.version)
    except BumpError as exc:
        parser.exit(2, f"error: {exc}\n")
    print(f"{args.formula} {args.version}: {outcome.value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
