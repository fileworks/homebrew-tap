# Contributing

Formula versions are **not** edited by hand. Each product's release pipeline
dispatches a bump, and the `url` and `sha256` lines are rewritten from the
published artifact. A manual edit to those lines will be overwritten and, in the
meantime, may not match the upstream release.

Changes to formula *structure* — dependencies, install steps, test blocks — are
ordinary pull requests:

```console
brew style Formula/
brew audit --strict --online Formula/<name>.rb
brew install --build-from-source Formula/<name>.rb
brew test <name>
```

Use a Conventional Commit subject. The tap itself is unversioned; there is no
release to cut.
