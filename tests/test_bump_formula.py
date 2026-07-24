from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from _support import import_scripts

import_scripts()

import bump_formula


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
    def test_exact_allowlist(self) -> None:
        for allowed in ("immich-export", "paperless-export"):
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
                    bump_formula.update_formula("immich-export", "1.2.3"),
                    bump_formula.BumpOutcome.EQUAL,
                )
                self.assertEqual(
                    bump_formula.update_formula("immich-export", "1.2.2"),
                    bump_formula.BumpOutcome.STALE,
                )
                outcome = bump_formula.update_formula(
                    "immich-export",
                    "1.2.4",
                    sdist_fetcher=lambda *_args: bump_formula.Sdist(
                        "https://files.pythonhosted.org/packages/immich_export-1.2.4.tar.gz",
                        "c" * 64,
                    ),
                )
                self.assertEqual(outcome, bump_formula.BumpOutcome.UPDATED)
                text = formula.read_text(encoding="utf-8")
                self.assertIn("immich_export-1.2.4.tar.gz", text)
                self.assertIn("c" * 64, text)

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
