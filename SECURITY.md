# Security policy

## Supported code

Security and integrity fixes are applied to the current `main` branch and the
latest schema version under `schemas/`.

## Reporting a vulnerability

Please use GitHub's private vulnerability-reporting flow from the repository's
**Security** tab. If that flow is unavailable, email
`rich@yourfoxprodeveloper.com` with the affected schema or script, revision,
impact, reproduction steps, and any proposed mitigation.

Do not open a public issue for an unpatched vulnerability. In particular,
report validation bypasses, canonical-hash mismatches, unsafe references, and
dependency compromise privately. You should receive an acknowledgment within
seven days.

## Security boundary

This repository defines data contracts and validation tools. It does not hold
credentials, connect to providers, or execute orders. Consumers remain
responsible for authenticating messages and enforcing their own policy.
