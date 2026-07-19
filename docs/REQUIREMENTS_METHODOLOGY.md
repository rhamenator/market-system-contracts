# Requirements methodology (DO-178-inspired, retrofitted)

This defines the shared requirements-traceability scheme used across all
four repositories in the Smart Dynamic Hedge system
(`smart-dynamic-hedge`, `market-intelligence-mcp`, `trade-guard-mcp`,
`market-system-contracts`). It lives here because this is the repository
already responsible for cross-repo shared conventions.

## Why "DO-178-inspired" and not DO-178 itself

DO-178C is the aviation software assurance standard built around two ideas
this system adopts by analogy, not by certification claim: (1) every
requirement traces forward to the code that implements it and the test
that verifies it, and backward from every test to the requirement it
verifies, with no orphans in either direction; (2) requirements exist at
two levels — high-level (system/functional behavior) and low-level
(implementation-adjacent, specific enough to design and test against).
This project is not an airborne system, is not seeking certification, and
does not claim DAL-level structural coverage (MC/DC etc.) — "DO-178-style"
here means borrowing the *traceability discipline*, not the certification
process.

## Why "recovery" rather than "requirements-first" for existing code

Most of this system was built conversationally — architecture decisions
and constraints were established in discussion and encoded directly into
code and tests, not written as requirements first. **Requirements
recovery** is the standard term for retroactively reconstructing a
requirements baseline from an existing implementation (its code, its
tests, its docs, and — for this project specifically — the design
conversation that produced it). Every recovered requirement's `Source`
field says where it came from, so the baseline is auditable rather than
invented after the fact.

Going forward, new work should flip this: write the requirement, then the
code, then the test — but recovery remains the correct approach for
already-built code.

## Requirement levels

- **HLR (High-Level Requirement)** — a system- or component-level
  behavior, stated in terms a non-implementer would recognize as correct
  or violated by observing the running system. Technology-agnostic.
- **LLR (Low-Level Requirement)** — implementation-adjacent detail derived
  from one or more HLRs, specific enough that a single test (or small,
  named set of tests) can verify it directly. An LLR names the exact
  boundary condition, error code, default value, or algorithm it pins
  down.

Every LLR has a `Traces-to:` field naming its parent HLR(s). No LLR may
exist without a parent HLR — if you can't name the parent, the LLR is
either not actually a requirement (it's an implementation detail with no
behavioral consequence) or reveals a missing HLR that should be added
first.

## Requirement ID scheme

`{PREFIX}-{LEVEL}-{NNN}`, prefixes per repository:

| Repository | Prefix |
|---|---|
| `smart-dynamic-hedge` | `SDH` |
| `market-intelligence-mcp` | `MIM` |
| `trade-guard-mcp` | `TGM` |
| `market-system-contracts` | `MSC` |

IDs are never reused or renumbered, even when a requirement is retired —
retired requirements are marked `Status: Superseded` or `Status:
Withdrawn` with a reason, not deleted, so historical traceability
(including in old test names/comments) stays valid.

## Requirement record format

Each requirement is a Markdown entry with these fields:

```text
### {ID} — {short title}

Statement: The {system/component} shall {testable behavior}.
Traces-to: {parent HLR ID(s), LLR only}
Source: {file:line, doc section, or "conversation, {date}" this was recovered from}
Rationale: {why — often the incident, threat, or design tradeoff behind it}
Verification: Test | Analysis | Inspection | Demonstration
Status: Implemented | Partial | Open | Superseded
Implementation: {file:function/type, per language if ported to more than one}
Verifying tests: {test name(s), per language}
```

`Verification` methods, DO-178 vocabulary:

- **Test** — an automated test exercises the behavior directly. Preferred;
  use for anything that can be.
- **Analysis** — verified by reasoning/proof rather than execution (e.g. "this
  code path is unreachable because the type system prevents the input").
- **Inspection** — verified by code/doc review rather than execution (e.g. a
  naming convention, a comment requirement).
- **Demonstration** — verified by running the system and observing behavior
  manually; used only when Test/Analysis/Inspection don't apply (e.g. "the
  dashboard displays a warning banner").

## Traceability matrix

Each repository's `requirements/TRACEABILITY.md` is the master table:
LLR → implementation location(s) → verifying test(s) → status. It exists
so two questions are always answerable by inspection, not archaeology:

1. **Forward**: for requirement X, what code implements it and what test
   proves it?
2. **Backward**: for this test, what requirement does it verify? (A test
   with no requirement behind it is either dead weight or reveals an
   undocumented requirement — add the requirement, don't just leave the
   test floating.)

A `Status: Open` entry (no implementation or no verifying test yet) is not
a failure — an honest gap is exactly what this process is for. What's not
acceptable is a requirement marked `Implemented` with no verifying test,
or code implementing safety-relevant behavior with no requirement at all.

## Per-repository layout

```text
requirements/
  README.md           overview, current recovery scope/status for this repo
  HLR.md              high-level requirements
  LLR.md              low-level requirements, each traces to an HLR
  TRACEABILITY.md      the matrix
```

## Scope and pacing

Recovering requirements for an entire multi-repo system in one pass is not
realistic and produces shallow, low-value entries. Each repository's
`requirements/README.md` states its own current recovery scope (e.g. "this
covers the Python/C++/Rust code that exists as of 2026-07-19; the
market-intelligence-mcp and trade-guard-mcp repositories have not had a
recovery pass yet"). Extend coverage incrementally, the same way the
codebase itself grows.
