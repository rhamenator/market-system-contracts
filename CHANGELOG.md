# Changelog

## Unreleased

- Fixed `common.schema.json#/$defs/decimal-string`: the pattern alone
  accepted `-0`, `-0.0`, `-0.000`, etc. (negative zero), contradicting its
  own description ("negative zero are invalid"). Added a `not` constraint
  to reject it while still allowing genuine negative decimals like `-0.5`.
  Found by the new adversarial test-case suite, not by inspection.
- Added `testdata/cases/`: a JSON-Schema-Test-Suite-style suite of
  self-describing `{schema-ref, tests: [{data, valid}]}` files exercising
  boundary and negative cases for `decimal-string`, `schema-version`, and
  `sha256-hash` (leading zeros, exponent notation, wrong length/case hex,
  missing prefixes, wrong JSON type, etc.) — 41 cases, all currently
  passing. This is the enforcement mechanism for the "SQLite-grade testing"
  bar: every pattern in this package needs a case file proving it rejects
  what it claims to reject, not just that it accepts a happy-path example.
- `scripts/validate_schemas.py` now runs the case suite in addition to
  schema well-formedness and golden-fixture checks.

## 2.0.0 — 2026-07-19

Initial schema set, matching `04-shared-contracts-and-tool-catalog.md` from the
`smart-dynamic-hedge-v2-prompt-bundle`:

- `common.schema.json` — decimal-safe strings, UTC timestamps, opaque IDs, hashes.
- `instrument-id.schema.json`
- `entity.schema.json` — `EntityId`, `ActorProfile`, `ActorRelationship`.
- `legal-status.schema.json` — `LegalStatus`, `MnpiClassification`.
- `source-use-decision.schema.json`
- `source-record.schema.json`
- `market-intelligence-event.schema.json`
- `evidence-bundle.schema.json`
- `signal-assessment.schema.json`
- `trade-intent.schema.json`
- `jurisdiction-venue-profile.schema.json`
- `tool-descriptor.schema.json`

Not yet implemented: generated Rust/Python/TypeScript/C++ bindings, canonical
JSON hashing specification and cross-language test vectors, compatibility
policy tooling. See README.md "Status" section.
