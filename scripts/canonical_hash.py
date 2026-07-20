#!/usr/bin/env python3
"""Reference implementation of this package's canonical-hashing spec.

See docs/CANONICAL_HASHING.md for the full specification this
implements. In short: recursively sort every JSON object's members by
key (compared as Unicode code points), leave array element order alone,
serialize as compact UTF-8 JSON with no insignificant whitespace and no
\\uXXXX-escaping of non-ASCII characters, then SHA-256 the UTF-8 bytes
and format as ``sha256:<64 lowercase hex characters>``.

This module has no dependency beyond the standard library, matching the
rest of this package's minimal-dependency policy -- `jsonschema`/
`referencing` (see requirements-dev.txt) are dev-only schema-validation
tooling, not something a canonicalizer needs.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def canonicalize(value: Any) -> Any:
    """Recursively sorts every dict's keys (by Unicode code point) while
    leaving list order untouched. Returns a new structure; does not
    mutate the input.
    """
    if isinstance(value, dict):
        return {key: canonicalize(value[key]) for key in sorted(value.keys())}
    if isinstance(value, list):
        return [canonicalize(item) for item in value]
    return value


def canonical_json(value: Any) -> str:
    """The canonical compact JSON serialization: sorted object keys, no
    insignificant whitespace, non-ASCII characters emitted literally
    (not \\uXXXX-escaped).
    """
    return json.dumps(canonicalize(value), separators=(",", ":"), ensure_ascii=False)


def canonical_hash(value: Any) -> str:
    """``sha256:<64 lowercase hex characters>`` of the canonical JSON
    serialization's UTF-8 bytes -- matches
    ``common.schema.json#/$defs/sha256-hash``.
    """
    body = canonical_json(value).encode("utf-8")
    return "sha256:" + hashlib.sha256(body).hexdigest()


def main() -> int:
    """Generates (or verifies, with --check) the test-vector file from
    its declared inputs -- run this after adding a new vector's `input`
    so `canonical`/`sha256` are computed, not hand-transcribed.
    """
    check_mode = "--check" in sys.argv
    root = Path(__file__).resolve().parent.parent
    vectors_path = root / "testdata" / "canonical-hashing" / "vectors.json"
    doc = json.loads(vectors_path.read_text(encoding="utf-8"))

    failures = 0
    for vector in doc["vectors"]:
        expected_canonical = canonical_json(vector["input"])
        expected_hash = canonical_hash(vector["input"])
        if check_mode:
            if vector.get("canonical") != expected_canonical:
                print(f"FAIL {vector['name']}: canonical mismatch\n  got:      {expected_canonical}\n  expected: {vector.get('canonical')}")
                failures += 1
            elif vector.get("sha256") != expected_hash:
                print(f"FAIL {vector['name']}: hash mismatch\n  got:      {expected_hash}\n  expected: {vector.get('sha256')}")
                failures += 1
            else:
                print(f"ok   {vector['name']}")
        else:
            vector["canonical"] = expected_canonical
            vector["sha256"] = expected_hash

    if not check_mode:
        vectors_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {vectors_path}")
        return 0

    if failures:
        print(f"\n{failures} failure(s)")
        return 1
    print(f"\nAll {len(doc['vectors'])} canonical-hashing vectors verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
