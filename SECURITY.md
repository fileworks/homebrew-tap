# Security policy

Report vulnerabilities privately through GitHub Security Advisories for
`fileworks/homebrew-tap`.

## What a tap can get wrong

This repository contains no product code. Its security surface is the integrity
of what it points at:

- **A formula's `url` and `sha256`.** They are written by the release pipeline
  from the published artifact. A formula whose checksum does not match its
  upstream release is the report we most want to receive.
- **The bump workflow's permissions.** It takes a repository-dispatch payload
  from a product release and edits a formula. A path from an untrusted dispatch
  to arbitrary formula content would be a real finding.

Formulas install from upstream releases; vulnerabilities in the tools themselves
belong in their own repositories.
