# Changelog

## Unreleased (4): jurisdiction/venue profile schema, real international fixtures

`jurisdiction-venue-profile.schema.json` existed as a Phase 1 scaffold
with no fixtures, no test cases, and mostly untyped placeholder fields —
nothing proved it was actually usable outside the U.S.

- **Tightened `venue-profile`'s `session-phases` shape**: was
  `{"type": "object"}` per item (accepts anything); now requires
  `phase-name` (a closed enum: `pre-market`/`regular`/`auction-open`/
  `auction-close`/`after-hours`/`overnight`/`other`), `opens-local-time`,
  `closes-local-time`. Deliberately *not* using this package's usual
  extensible-enum convention here — session phases are a closed,
  well-known set, unlike provider-specific codes.
- **Added `testdata/cases/jurisdiction-venue-profile.json` and
  `jurisdiction-profile.json`**: 15 cases total, including two genuinely
  different realistic fixtures per type — NYSE Arca (US, `America/New_York`,
  USD, T+1, penny ticks) vs. Tokyo Stock Exchange (Japan, `Asia/Tokyo`,
  JPY, T+2, yen-band tick rules, a split lunch-break session structure
  with two `regular` phases) for venues; US vs. Japan (a different
  regulatory regime and a nonzero-leverage crypto-derivative
  classification) for jurisdictions — not palette-swapped U.S. data.
  Plus boundary/negative cases for every required field and the new
  `session-phases` item shape.

## Unreleased (3): canonical JSON serialization and hashing specification

Closes the Phase 1 gap the README's "Status" section named: "a canonical
JSON serialization and hashing specification (needed so `canonical-hash`
/ `deterministic-input-hash` fields are reproducible across languages)".

- **Added `docs/CANONICAL_HASHING.md`**: the algorithm (recursively sort
  object keys by Unicode code point, leave array order alone, compact
  UTF-8 JSON with non-ASCII emitted literally, SHA-256, `sha256:` prefix)
  every `sha256-hash`-shaped field must follow. Documents a real,
  verified cross-language hazard: numeric fields that are genuine JSON
  `number`s rather than `decimal-string` (e.g. `TradeIntent.confidence`)
  are not guaranteed to format identically in every language —
  JavaScript's `JSON.stringify(0.0)` produces `"0"`, not `"0.0"`, unlike
  Python and Rust's `serde_json`, which agree for this system's actual
  values (verified, not assumed — see below).
- **`scripts/canonical_hash.py`**: dependency-free reference
  implementation (stdlib `json`/`hashlib` only), doubling as the
  generator for `testdata/canonical-hashing/vectors.json` — vector
  `canonical`/`sha256` fields are generated from `input`, never
  hand-transcribed, same discipline as this package's decimal-string test
  cases and `smart-dynamic-hedge`'s own "don't trust a memorized hash
  constant" lesson.
- **`testdata/canonical-hashing/vectors.json`**: 11 vectors — empty
  object/array, key sorting at multiple nesting levels, array-order
  preservation, non-ASCII text, a `decimal-string` value, small
  integers/booleans, and the full `trade-intent.no-action-example.json`
  golden fixture (the one containing the float-formatting caveat's actual
  test case, `"confidence": 0.0`).
- **`scripts/validate_schemas.py`** now also verifies the canonical-hashing
  vectors, so `python scripts/validate_schemas.py` remains the one
  command that checks everything in this package.
- **Cross-repo verification, not just documentation**: added 6 tests to
  `market-intelligence-mcp`'s `market_intelligence_core::sha256` module
  (`canonical_hashing_spec_conformance`) that hash the *same* inputs as
  this package's vectors and assert the *exact same* committed hash
  strings — including the float-formatting caveat's own test case,
  which passes, confirming Rust's `serde_json` and Python's `json` module
  really do agree for this system's actual values rather than the spec
  merely asserting they should. `market-intelligence-mcp`'s
  `evidence_builder::build_evidence_bundle` (added in that repo's own
  latest pass) is the first real producer of a `canonical-hash` in this
  system, and needed no code change to conform — `serde_json::Value`'s
  `Object` is a `BTreeMap` in that workspace (no `preserve_order`
  feature), so sorted-key output was already free.

## Unreleased (2)

- Added `docs/REQUIREMENTS_METHODOLOGY.md`: the shared DO-178-inspired
  requirements-recovery scheme (HLR/LLR levels, ID prefixes per repo,
  traceability-matrix format, verification-method vocabulary) used across
  all four repositories in this system. `smart-dynamic-hedge` is the
  first repo to apply it (`requirements/HLR.md`/`LLR.md`/`TRACEABILITY.md`
  there); `market-intelligence-mcp` and `trade-guard-mcp` haven't had a
  recovery pass yet.

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
