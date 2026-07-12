"""Rewrite a formula's url/sha256/version pin to a new PyPI release.

Usage: bump_formula.py <formula> <version>

Polls PyPI until the sdist for the requested version is visible (releases can
lag a few seconds behind the publish step), then updates:
  - url "…"     → the sdist download URL
  - sha256 "…"  → the sdist digest

The pip install pin inside the formula uses Ruby's `#{version}` interpolation,
which Homebrew derives from the url — so it follows automatically.
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from pathlib import Path

POLL_ATTEMPTS = 20
POLL_DELAY_SECONDS = 15


def fetch_sdist(package: str, version: str) -> tuple[str, str]:
    url = f"https://pypi.org/pypi/{package}/{version}/json"
    last_error: Exception | None = None
    for attempt in range(1, POLL_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                payload = json.load(response)
            for artifact in payload["urls"]:
                if artifact["packagetype"] == "sdist":
                    return artifact["url"], artifact["digests"]["sha256"]
            raise RuntimeError(f"{package}=={version} has no sdist on PyPI")
        except Exception as exc:  # noqa: BLE001 - retry on any transient failure
            last_error = exc
            print(f"[{attempt}/{POLL_ATTEMPTS}] not on PyPI yet ({exc}); retrying…")
            time.sleep(POLL_DELAY_SECONDS)
    raise SystemExit(f"Gave up waiting for {package}=={version} on PyPI: {last_error}")


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    formula_name, version = sys.argv[1], sys.argv[2]
    if not re.fullmatch(r"[a-z0-9-]+", formula_name):
        raise SystemExit(f"Suspicious formula name: {formula_name!r}")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise SystemExit(f"Not a semver version: {version!r}")

    formula_path = Path("Formula") / f"{formula_name}.rb"
    if not formula_path.is_file():
        raise SystemExit(f"No such formula: {formula_path}")

    sdist_url, sha256 = fetch_sdist(formula_name, version)
    text = formula_path.read_text(encoding="utf-8")
    text, url_subs = re.subn(r'url "[^"]+"', f'url "{sdist_url}"', text, count=1)
    text, sha_subs = re.subn(r'sha256 "[^"]+"', f'sha256 "{sha256}"', text, count=1)
    if not (url_subs and sha_subs):
        raise SystemExit(
            f"Formula {formula_path} did not match the expected shape "
            f"(url:{url_subs} sha256:{sha_subs})"
        )
    formula_path.write_text(text, encoding="utf-8")
    print(f"Updated {formula_path}: {version} ({sdist_url})")


if __name__ == "__main__":
    main()
