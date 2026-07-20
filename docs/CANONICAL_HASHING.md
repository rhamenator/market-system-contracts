# Canonical JSON serialization and hashing

This specification closes the Phase 1 gap the README's "Status" section
named: "a canonical JSON serialization and hashing specification (needed
so `canonical-hash` / `deterministic-input-hash` fields are reproducible
across languages)". Any of the three sibling repositories, in any
language, that computes a `sha256-hash`-shaped value
(`common.schema.json#/$defs/sha256-hash`) over a JSON document — an
`EvidenceBundle`'s `canonical-hash`, a `TradeIntent`'s
`deterministic-input-hash`, or any future field with the same shape —
must follow this algorithm exactly, or a hash computed by one repository
can never be independently reverified by another.

## Why this is needed, not merely nice to have

`trade-guard-mcp`'s `check-evidence-eligibility` gate receives an
`EvidenceBundle` from `market-intelligence-mcp` carrying a `canonical-hash`
it did not itself compute. Verifying that hash — confirming the bundle
hasn't been tampered with in transit — requires `trade-guard-mcp` to
recompute the *identical* hash `market-intelligence-mcp` computed,
independently, in a different Rust codebase. Two structurally identical
JSON objects serialized by two different `serde_json` call sites are not
guaranteed to produce identical bytes unless both follow the same
canonicalization rule — object key insertion order, for one, is not
part of any JSON value's semantic identity, but it does affect the raw
bytes a naive `to_string()` produces.

## Algorithm

Given a JSON value that has already been validated against its schema:

1. **Recursively sort every object's members** by key, comparing keys as
   sequences of Unicode code points (not locale-aware, not UTF-16 code
   units — see "Language-specific notes" below for why this distinction
   matters). Nested objects are sorted at every level, including objects
   inside arrays.
2. **Leave array element order untouched.** An array's element order is
   part of its meaning; canonicalization only removes the
   otherwise-insignificant freedom in object member order.
3. **Serialize as compact JSON**: UTF-8 encoding, no insignificant
   whitespace (no space after `:` or `,`, no trailing newline), non-ASCII
   characters emitted literally rather than `\uXXXX`-escaped.
4. **SHA-256 the UTF-8 bytes** of that serialization.
5. **Format as `sha256:<64 lowercase hex characters>`**, matching
   `common.schema.json#/$defs/sha256-hash` exactly.

## The float caveat — read this before hashing anything with a `number` field

This package's own scalar convention (`common.schema.json`) already
sidesteps JSON's classic floating-point serialization ambiguity for
*money, price, and quantity* fields: those are `decimal-string`, an
opaque string, never a raw JSON number. That was a deliberate design
choice specifically so canonical hashing would not need to solve
cross-language float formatting.

**Not every numeric field follows that convention.** `TradeIntent.confidence`
and `SignalAssessment.confidence`/`score` are genuine JSON `number`
fields (`{"type": "number", "minimum": 0, "maximum": 1}}`), because a
confidence score isn't money and doesn't need decimal-exact arithmetic.
This is a real, demonstrated hazard: the `confidence: 0.0` field in the
"trade-intent.no-action-example.json golden fixture" test vector below
canonicalizes to the literal text `0.0` in Python and (verified
separately) in Rust's `serde_json` — but `JSON.stringify(0.0)` in
JavaScript produces `"0"`, not `"0.0"`, because JavaScript has no
distinct integer/float number types. A hash computed in a future
TypeScript implementation over a document containing `"confidence": 0.0`
would **not** match this document's hash.

**Until a JavaScript/TypeScript implementation exists and this caveat is
resolved for it**, any payload being canonically hashed across the
Rust-only repositories (`market-intelligence-mcp`, `trade-guard-mcp`) is
safe under this algorithm, since `serde_json` and Python's `json` module
agree on float formatting for every value this system actually produces
(`0.0`–`1.0` confidence scores at reasonable precision). Treat this as a
tracked, documented gap for the day a TypeScript binding is added, not a
silent one.

## Language-specific notes

- **Rust**: sort keys with `str::cmp` (byte-wise UTF-8 comparison, which
  is equivalent to codepoint order for valid UTF-8). `serde_json::Value`'s
  `Object` variant is a `BTreeMap` by default (not the `preserve_order`
  feature), so `serde_json::to_string` on a `Value` already emits sorted
  keys — the canonicalization step is "don't enable `preserve_order`",
  not "manually sort".
- **Python**: `sorted(dict.keys())` on `str` keys already compares by
  code point. `json.dumps(..., sort_keys=True, separators=(",", ":"),
  ensure_ascii=False)` implements this algorithm directly — see
  `scripts/canonical_hash.py`, the reference implementation.
- **TypeScript/JavaScript** (not yet implemented anywhere in this
  system): default `Array.prototype.sort()` on strings compares UTF-16
  code units, which disagrees with codepoint order for characters outside
  the Basic Multilingual Plane (e.g. emoji). Use `Array.from(str)` to
  split by codepoint, or `Intl.Collator` with a codepoint-order
  comparator, not the bare `<` operator on strings containing astral
  characters. Also see the float caveat above — unresolved for this
  language today.

## Reference implementation and test vectors

`scripts/canonical_hash.py` is the reference implementation (stdlib
only, no dependency). `testdata/canonical-hashing/vectors.json` holds the
test vectors: each entry's `canonical` and `sha256` fields are *generated
from* `input` by running `python scripts/canonical_hash.py`, never
hand-transcribed — the same "don't trust a memorized hash constant"
discipline `smart-dynamic-hedge` applied after finding a transcription
typo in one of its own SHA-256 test vectors.

A new language implementation should reproduce every vector's `sha256`
field from that vector's `input` and treat any mismatch as a
non-conformance bug in the new implementation, not in the vectors —
`python scripts/canonical_hash.py --check` re-verifies the committed
vectors were generated correctly (i.e. that they're internally
consistent, not stale relative to the reference implementation itself).

## What this does not specify

- **Which fields get hashed.** This document specifies *how* to
  canonicalize and hash a JSON value, not which subset of an
  `EvidenceBundle`'s fields belong inside its own `canonical-hash` (e.g.
  whether `canonical-hash` itself, or `service-attestation`, should be
  excluded from the value being hashed to avoid a self-referential
  definition). That's a per-schema decision each `*.schema.json` file's
  own description should state explicitly; not yet done for every field
  that has one — tracked as a `README.md` "Status" follow-up.
- **Signature/attestation formats.** `service-attestation` in
  `evidence-bundle.schema.json` is an opaque string today; a real
  signature scheme (what's signed, key format, verification) is separate,
  future work.
