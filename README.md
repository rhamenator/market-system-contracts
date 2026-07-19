# market-system-contracts

Canonical, versioned schema package shared by three sibling repositories:

- [`smart-dynamic-hedge`](https://github.com/rhamenator/smart-dynamic-hedge) — strategy, research, GUI, and autonomy plane.
- [`market-intelligence-mcp`](https://github.com/rhamenator/market-intelligence-mcp) — lawful public/licensed market-intelligence collection.
- [`trade-guard-mcp`](https://github.com/rhamenator/trade-guard-mcp) — authoritative account state, risk policy, and execution.

Its purpose is to prevent three hand-copied, drifting definitions of the same
concepts. All three repositories should compile or validate against the same
schema version rather than maintaining their own copies of `TradeIntent`,
`EvidenceBundle`, `InstrumentId`, and related types.

## Status

This is a **Phase 1** scaffold: hand-written JSON Schema 2020-12 documents and
golden fixtures exist and validate. Not yet built:

- generated Rust, Python, TypeScript, and C++ bindings;
- a canonical JSON serialization and hashing specification (needed so
  `canonical-hash` / `deterministic-input-hash` fields are reproducible
  across languages);
- a formal compatibility/versioning policy document;
- cross-language round-trip test vectors.

Treat every schema here as reviewed but not yet load-bearing in a running
service. See `CHANGELOG.md` for what exists today.

## Layout

```text
schemas/2.0.0/     JSON Schema 2020-12 documents, one concept per file
testdata/golden/   Example instances validated against the schemas above
testdata/cases/    Boundary/negative test-case suites (JSON-Schema-Test-Suite style)
scripts/           Validation tooling (no service code lives in this repo)
```

## Testing philosophy

Every constraining pattern in `schemas/2.0.0/` needs a matching file in
`testdata/cases/` proving it rejects what it claims to reject, not just
that a happy-path example passes. `decimal-string`'s pattern once silently
accepted negative zero (`-0`, `-0.0`, ...) despite its own description
saying that's invalid — the boundary-case suite caught it, ad hoc
inspection hadn't. Each case file is self-describing:

```json
{
  "schema-ref": "common.schema.json#/$defs/decimal-string",
  "tests": [{ "description": "...", "data": "-0", "valid": false }]
}
```

Add cases *before* trusting a new pattern, not after a bug report.

## Naming conventions

- External field names, JSON Schema `$id`s, MCP tool names, and file names use
  hyphens.
- Generated language bindings use each language's native identifier
  convention (`snake_case` for Python/Rust, `camelCase` for TypeScript) at the
  binding-generation boundary only — the wire format stays hyphenated.
- Every record carries an explicit `schema-version` field.
- Every enum is designed to be extended with `unknown`/`other` fallback
  values so an unrecognized provider code round-trips instead of failing
  closed at parse time.

## Canonical scalar rules

See `schemas/2.0.0/common.schema.json`. In short: money/price/quantity/rate
fields are decimal-safe strings (never binary floating point at an external
boundary), timestamps are UTC RFC 3339, and identifiers are opaque and never
a display symbol.

## Validating locally

```bash
python -m venv .venv
. .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python scripts/validate_schemas.py
```

This checks that every schema is a well-formed Draft 2020-12 document with
resolvable internal `$ref`s, that every fixture under `testdata/golden/`
validates against its mapped schema, and that every boundary/negative case
under `testdata/cases/` gets the pass/fail verdict it declares.

## Where this comes from

These schemas transcribe section "Shared contracts and canonical tool
catalog" of the `smart-dynamic-hedge-v2-prompt-bundle` coding-agent prompt
package (2026-07-19). See that bundle's `05-source-policy-and-legal-boundaries.md`
for the legal/licensing rules (`SourceUseDecision`, `MnpiClassification`) that
these schemas encode, and `06-implementation-order-and-acceptance.md` for the
phased delivery plan this repository is Phase 1 of.

## License

GNU General Public License v3.0 (or, at your option, any later version). See
[LICENSE](LICENSE) and [NOTICE](NOTICE).
