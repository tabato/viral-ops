# Security Policy

If you find a security vulnerability in viral-ops — for example, something that could expose API keys or allow unintended access — please **do not open a public GitHub issue**.

Instead, use GitHub's private vulnerability reporting:

→ [Report a vulnerability privately](https://github.com/tabato/viral-ops/security/advisories/new)

This keeps the details confidential until a fix is in place.

## What counts as a security issue

- A way to expose or leak API keys
- A way to run unintended code through input (e.g. the YAML config files)
- Anything in the gallery HTML output that could be used for XSS

## What doesn't need a private report

- Bugs that don't have security implications — open a regular issue for those
- Feature requests
