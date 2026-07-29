<img src=".github/icon.svg" alt="" width="72" height="72" align="left">

# homebrew-tap

The unversioned Homebrew tap for the independently released `fileworks` CLIs.

## Install

```sh
brew tap fileworks/tap
brew install fileworks/tap/immich-export
brew install fileworks/tap/paperless-export
```

Current formula versions:

- `immich-export`: `0.0.4`
- `paperless-export`: `1.0.0`

## Overview

The Homebrew tap for the fileworks command-line tools. It carries no version of
its own; each formula tracks the product it installs.

## Formulas

| Formula | Installs | Source |
|---|---|---|
| `immich-export` | Immich → local tree exporter | [fileworks/immich-export](https://github.com/fileworks/immich-export) |
| `paperless-export` | Paperless-ngx exporter and tax view | [fileworks/paperless-export](https://github.com/fileworks/paperless-export) |

Versions are listed above under Install and are bumped automatically by each
product's release pipeline.

## Safe release queue

Exporter release workflows dispatch a strict formula/version pair plus their
repository and workflow-run provenance. The tap validates that request, stores
it as an inspectable GitHub issue labeled `formula-bump`, and only then starts
the serialized drain.

The drain always scans every open queue record. It accepts only the two known
formulas, processes versions monotonically, validates the requested PyPI sdist
and digest, writes the selected formula atomically, and closes a record only
after its result is present on `main`. Equal versions are idempotent no-ops;
lower versions are recorded as stale and cannot roll a formula back.

If a drain fails, the issue remains open. Inspect open records with:

```sh
gh issue list --repo fileworks/homebrew-tap --label formula-bump --state open
```

After correcting the cause, rerun any recent `bump` workflow from the Actions
page; its surviving drain scans all open records, not only the triggering one.
A reviewed manual formula PR is the emergency rollback/update path.

The queue and formulas are covered by pull-request CI. The full downstream
release chain will remain “tested but not yet observed” until the next warranted
exporter release exercises it; no synthetic package version is created merely
to prove automation.

## Local contributor instructions

Create an ignored `CLAUDE.local.md` at the repository root for per-clone paths,
commands, or preferences. Do not put credentials or other secrets in it.

## Development

Formula `url` and `sha256` lines are written by the release pipeline — see
[CONTRIBUTING.md](CONTRIBUTING.md) before editing one by hand. Structural
changes are ordinary pull requests validated with `brew style`, `brew audit
--strict --online`, and a real install test.

## License

MIT
