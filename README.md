# homebrew-tap

The Homebrew tap for the `fileworks` CLIs:

```sh
brew tap fileworks/tap
brew install fileworks/tap/immich-export
brew install fileworks/tap/paperless-export
```

Both formulas are live at **0.0.3** and are bumped automatically by each CLI's
release workflow — no manual edit is ever needed here.

## How it works

- `Formula/*.rb` install each CLI into its own virtualenv, pip-pinned to the
  exact released version (the personal-tap pattern — no vendored resource
  blocks to maintain).
- `.github/workflows/bump.yml` is a `workflow_dispatch` triggered by each CLI's
  release pipeline (`gh workflow run bump.yml -f formula=<name> -f version=<x.y.z>`).
  It waits for the sdist to appear on PyPI, rewrites the formula's
  `url`/`sha256` (`.github/scripts/bump_formula.py`), commits, and pushes.
  The pip pin uses Ruby's `#{version}` interpolation, which Homebrew derives
  from the `url` — so it follows automatically.

The repo must be named exactly `homebrew-tap` so `brew tap fileworks/tap`
resolves.

## License

MIT
