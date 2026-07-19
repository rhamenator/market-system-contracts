# Changelog

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
