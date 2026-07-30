# Contributing

Formula versions and resources are **not** edited by hand. Each product's
release pipeline dispatches its version plus an immutable `uv.lock` URL and
SHA-256 digest. The tap regenerates the complete formula from the authenticated
application sdist and locked macOS/Linux wheels. A manual edit will be
overwritten and may make the installed inventory diverge from the released
lock.

Changes to formula *structure* — dependencies, install steps, test blocks — are
ordinary pull requests:

```console
brew style Formula/
brew audit --strict fileworks/tap/<name>
brew install --build-from-source Formula/<name>.rb
brew test <name>
```

Formula installation sets `PIP_NO_INDEX=1`, builds the staged application
source, and installs only declared wheel resources. To reproduce CI locally,
prefetch with `brew fetch --deps` and `brew fetch --build-from-source`, then run
the install with `PIP_NO_INDEX=1`.

Use a Conventional Commit subject. The tap itself is unversioned; there is no
release to cut.
