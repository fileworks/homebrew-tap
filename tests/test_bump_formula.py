from __future__ import annotations

import json
import os
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from _support import import_scripts

import_scripts()

import bump_formula

LOCK_URL = (
    "https://raw.githubusercontent.com/fileworks/immich-export/"
    f"{'1' * 40}/uv.lock"
)
LOCK_SHA256 = "2" * 64


def pypi_payload(package: str, version: str, *, digest: str = "a" * 64) -> dict[str, object]:
    normalized = package.replace("-", "_")
    return {
        "info": {"name": package, "version": version},
        "urls": [
            {
                "packagetype": "sdist",
                "url": (
                    "https://files.pythonhosted.org/packages/source/"
                    f"{normalized[0]}/{normalized}/{normalized}-{version}.tar.gz"
                ),
                "digests": {"sha256": digest},
            }
        ],
    }


def lock_fixture(package: str = "immich-export", version: str = "1.2.3") -> bytes:
    extra = (
        '\n[package.optional-dependencies]\npdf = [{ name = "native-runtime" }]\n'
        if package == "paperless-export"
        else ""
    )
    return (
        "version = 1\n"
        'requires-python = ">=3.12"\n\n'
        "[[package]]\n"
        f'name = "{package}"\n'
        f'version = "{version}"\n'
        'source = { editable = "." }\n'
        'dependencies = [{ name = "pure-runtime" }, '
        '{ name = "windows-only", marker = "sys_platform == \'win32\'" }]\n'
        f"{extra}\n"
        "[[package]]\n"
        'name = "pure-runtime"\n'
        'version = "2.0.0"\n'
        'source = { registry = "https://pypi.org/simple" }\n'
        "wheels = [\n"
        '  { url = "https://files.pythonhosted.org/packages/pure_runtime-2.0.0-py3-none-any.whl", '
        f'hash = "sha256:{"3" * 64}" }},\n'
        "]\n\n"
        "[[package]]\n"
        'name = "native-runtime"\n'
        'version = "3.0.0"\n'
        'source = { registry = "https://pypi.org/simple" }\n'
        "wheels = [\n"
        + "".join(
            '  { url = "https://files.pythonhosted.org/packages/'
            f'native_runtime-3.0.0-cp312-cp312-{platform}.whl", '
            f'hash = "sha256:{"4" * 64}" }},\n'
            for platform in (
                "macosx_11_0_arm64",
                "macosx_10_13_x86_64",
                "manylinux_2_17_aarch64",
                "manylinux_2_17_x86_64",
            )
        )
        + "]\n\n"
        "[[package]]\n"
        'name = "windows-only"\n'
        'version = "1.0.0"\n'
        'source = { registry = "https://pypi.org/simple" }\n'
        "wheels = []\n"
    ).encode()


class Response:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload

    def __enter__(self) -> Response:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode()


class BumpFormulaTests(unittest.TestCase):
    def test_ci_audits_every_supported_formula(self) -> None:
        workflow = (
            Path(__file__).parents[1] / ".github/workflows/ci.yml"
        ).read_text(encoding="utf-8")
        matrix = workflow.split("formula:", maxsplit=1)[1].split("\n    steps:", maxsplit=1)[0]
        for formula in bump_formula.FORMULAS:
            self.assertIn(formula, matrix)

    def test_exact_allowlist(self) -> None:
        for allowed in ("immich-export", "paperless-export", "unpacksort"):
            self.assertEqual(bump_formula.validate_formula(allowed), allowed)
        for rejected in ("other", "../immich-export", "Immich-export", "immich-export;id"):
            with self.assertRaises(bump_formula.BumpError):
                bump_formula.validate_formula(rejected)

    def test_strict_versions_and_order(self) -> None:
        self.assertLess(
            bump_formula.ReleaseVersion.parse("1.9.9"),
            bump_formula.ReleaseVersion.parse("1.10.0"),
        )
        for rejected in ("1.2", "v1.2.3", "1.2.3rc1", "01.2.3", "1.2.3 --help", "1.2.3\n"):
            with self.assertRaises(bump_formula.BumpError):
                bump_formula.ReleaseVersion.parse(rejected)

    def test_pypi_response_must_match_exact_artifact(self) -> None:
        version = bump_formula.ReleaseVersion.parse("1.2.3")
        expected = bump_formula.parse_pypi_sdist(
            "immich-export",
            version,
            pypi_payload("immich-export", "1.2.3"),
        )
        self.assertEqual(expected.sha256, "a" * 64)
        cases = [
            pypi_payload("paperless-export", "1.2.3"),
            pypi_payload("immich-export", "1.2.4"),
            {"info": {"name": "immich-export", "version": "1.2.3"}, "urls": []},
        ]
        for payload in cases:
            with self.assertRaises(bump_formula.BumpError):
                bump_formula.parse_pypi_sdist("immich-export", version, payload)

    def test_fetch_retries_transient_publication_delay(self) -> None:
        calls = 0

        def opener(*_args: object, **_kwargs: object) -> Response:
            nonlocal calls
            calls += 1
            if calls < 3:
                raise OSError("not ready")
            return Response(pypi_payload("immich-export", "1.2.3"))

        result = bump_formula.fetch_sdist(
            "immich-export",
            bump_formula.ReleaseVersion.parse("1.2.3"),
            attempts=3,
            delay_seconds=0,
            opener=opener,
            sleeper=lambda _seconds: None,
        )
        self.assertEqual(result.sha256, "a" * 64)
        self.assertEqual(calls, 3)

    def test_update_is_monotonic_exact_and_atomic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            formula = root / "immich-export.rb"
            formula.write_text(
                'class ImmichExport < Formula\n'
                '  url "https://files.pythonhosted.org/packages/immich_export-1.2.3.tar.gz"\n'
                f'  sha256 "{"b" * 64}"\n'
                "end\n",
                encoding="utf-8",
            )
            with patch.dict(bump_formula.FORMULAS, {"immich-export": formula}, clear=True):
                self.assertEqual(
                    bump_formula.update_formula(
                        "immich-export",
                        "1.2.2",
                        lock_url=LOCK_URL,
                        lock_sha256=LOCK_SHA256,
                    ),
                    bump_formula.BumpOutcome.STALE,
                )
                outcome = bump_formula.update_formula(
                    "immich-export",
                    "1.2.4",
                    lock_url=LOCK_URL,
                    lock_sha256=LOCK_SHA256,
                    sdist_fetcher=lambda *_args: bump_formula.Artifact(
                        "https://files.pythonhosted.org/packages/immich_export-1.2.4.tar.gz",
                        "c" * 64,
                    ),
                    lock_fetcher=lambda *_args: lock_fixture(version="1.2.4"),
                )
                self.assertEqual(outcome, bump_formula.BumpOutcome.UPDATED)
                text = formula.read_text(encoding="utf-8")
                self.assertIn("immich_export-1.2.4.tar.gz", text)
                self.assertIn("c" * 64, text)
                self.assertIn('resource "pure-runtime"', text)
                self.assertNotIn("windows-only", text)
                self.assertEqual(
                    bump_formula.update_formula(
                        "immich-export",
                        "1.2.4",
                        lock_url=LOCK_URL,
                        lock_sha256=LOCK_SHA256,
                        sdist_fetcher=lambda *_args: bump_formula.Artifact(
                            "https://files.pythonhosted.org/packages/"
                            "immich_export-1.2.4.tar.gz",
                            "c" * 64,
                        ),
                        lock_fetcher=lambda *_args: lock_fixture(version="1.2.4"),
                    ),
                    bump_formula.BumpOutcome.EQUAL,
                )

    def test_generation_is_byte_stable_and_covers_all_supported_targets(self) -> None:
        resources = bump_formula.parse_locked_resources(
            "paperless-export",
            bump_formula.ReleaseVersion.parse("1.2.3"),
            lock_fixture("paperless-export"),
        )
        application = bump_formula.Artifact(
            "https://files.pythonhosted.org/packages/paperless_export-1.2.3.tar.gz",
            "5" * 64,
        )
        kwargs = {
            "lock_url": LOCK_URL.replace("immich-export", "paperless-export"),
            "lock_sha256": LOCK_SHA256,
        }
        first = bump_formula.render_formula(
            "paperless-export",
            bump_formula.ReleaseVersion.parse("1.2.3"),
            application,
            resources,
            **kwargs,
        )
        second = bump_formula.render_formula(
            "paperless-export",
            bump_formula.ReleaseVersion.parse("1.2.3"),
            application,
            list(reversed(resources)),
            **kwargs,
        )
        self.assertEqual(first, second)
        for selector in ("on_macos", "on_linux", "on_arm", "on_intel"):
            self.assertIn(selector, first)
        self.assertIn("native-runtime", first)
        self.assertIn("PIP_NO_INDEX", first)
        self.assertIn('.replace("_", "-").replace(".", "-")', first)

    def test_generated_system_dependencies_follow_the_locked_resources(self) -> None:
        resources = bump_formula.parse_locked_resources(
            "paperless-export",
            bump_formula.ReleaseVersion.parse("1.2.3"),
            lock_fixture("paperless-export"),
        )
        resources[0] = replace(resources[0], name="lxml")
        rendered = bump_formula.render_formula(
            "paperless-export",
            bump_formula.ReleaseVersion.parse("1.2.3"),
            bump_formula.Artifact(
                "https://files.pythonhosted.org/packages/paperless_export-1.2.3.tar.gz",
                "5" * 64,
            ),
            resources,
            lock_url=LOCK_URL.replace("immich-export", "paperless-export"),
            lock_sha256=LOCK_SHA256,
        )
        self.assertIn('uses_from_macos "libxml2"', rendered)
        self.assertIn('uses_from_macos "libxslt"', rendered)

    def test_unpacksort_formula_exercises_real_extraction_and_manifest(self) -> None:
        resources = bump_formula.parse_locked_resources(
            "unpacksort",
            bump_formula.ReleaseVersion.parse("1.2.3"),
            lock_fixture("unpacksort"),
        )
        rendered = bump_formula.render_formula(
            "unpacksort",
            bump_formula.ReleaseVersion.parse("1.2.3"),
            bump_formula.Artifact(
                "https://files.pythonhosted.org/packages/unpacksort-1.2.3.tar.gz",
                "5" * 64,
            ),
            resources,
            lock_url=LOCK_URL.replace("immich-export", "unpacksort"),
            lock_sha256=LOCK_SHA256,
        )
        self.assertIn('system bin/"unpacksort", testpath/"fixture.tar.gz"', rendered)
        self.assertIn('"unpacksort did not extract the fixture"', rendered)
        self.assertIn('manifest = testpath/"out/manifest.jsonl"', rendered)

    def test_supported_lock_markers_match_cpython_312_targets(self) -> None:
        for marker in (
            "implementation_name != 'PyPy'",
            "platform_python_implementation == 'CPython'",
            "python_full_version < '3.14'",
            "sys_platform != 'cygwin'",
        ):
            self.assertTrue(bump_formula._marker_supported(marker))
        for marker in (
            "os_name == 'nt'",
            "platform_python_implementation == 'PyPy'",
            "sys_platform == 'win32'",
        ):
            self.assertFalse(bump_formula._marker_supported(marker))

    def test_rejects_missing_wheels_duplicate_packages_and_mutable_lock_urls(self) -> None:
        invalid = lock_fixture().replace(
            b"https://files.pythonhosted.org/packages/pure_runtime-2.0.0-py3-none-any.whl",
            b"https://example.com/latest.whl",
        )
        with self.assertRaises(bump_formula.BumpError):
            bump_formula.parse_locked_resources(
                "immich-export",
                bump_formula.ReleaseVersion.parse("1.2.3"),
                invalid,
            )
        duplicate = lock_fixture() + lock_fixture().split(b"[[package]]", 2)[2]
        with self.assertRaises(bump_formula.BumpError):
            bump_formula.parse_locked_resources(
                "immich-export",
                bump_formula.ReleaseVersion.parse("1.2.3"),
                duplicate,
            )
        with self.assertRaises(bump_formula.BumpError):
            bump_formula.validate_lock_provenance(
                "immich-export",
                "https://raw.githubusercontent.com/fileworks/immich-export/main/uv.lock",
                LOCK_SHA256,
            )

    def test_atomic_failure_preserves_original(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            formula = Path(directory) / "formula.rb"
            original = "unchanged\n"
            formula.write_text(original, encoding="utf-8")
            with patch.object(os, "replace", side_effect=OSError("blocked")):
                with self.assertRaises(bump_formula.BumpError):
                    bump_formula.atomic_write(formula, "changed\n")
            self.assertEqual(formula.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
