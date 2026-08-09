# Publication-readiness audit

Audit date: 2026-08-09

## Executive summary

No critical or high-severity publication blockers remain in the reviewed
working tree. The repository is suitable for public source visibility as a
versioned schema and validation package after these changes are committed and
the sibling repositories are made public together.

## Findings and remediation

- **PUB-001 — Medium — Broken architecture link:** README linked to
  `smart-dynamic-hedge`; corrected to the public
  `smart-dynamic-hedge-project` repository.
- **PUB-002 — Medium — Missing automated validation gate:** added pinned
  GitHub Actions for schema, fixture, boundary-case, canonical-hash, dependency
  consistency, and vulnerability checks.
- **PUB-003 — Medium — Missing private reporting process:** added
  `SECURITY.md` and Dependabot configuration.

## Verification completed

- Gitleaks 8.30.1 scanned all refs, five commits, and the final working tree:
  no findings.
- `python scripts/validate_schemas.py`: all schemas, fixtures, negative cases,
  and canonical-hashing vectors passed.
- `python -m pip check`: no broken dependency found.
- `python -m pip_audit --requirement requirements-dev.txt`: no known
  vulnerabilities found.
- GPL-3.0-or-later license and NOTICE are present.

## Residual limitations

Bindings are not generated yet, the schemas are not yet a load-bearing shared
runtime package, and consumers must still authenticate messages and enforce
their own authorization policy.
