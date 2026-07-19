#!/usr/bin/env python3
"""Validate every schema in schemas/<version>/, every golden fixture, and
every JSON-Schema-Test-Suite-style test-case file in testdata/cases/.

Three things are checked, in order, for each schema version directory:

1. every *.schema.json file is a well-formed Draft 2020-12 schema with
   resolvable internal $refs;
2. every fixture under testdata/golden/ validates against its mapped
   schema (a positive-only "this is what a real record looks like" check);
3. every case in testdata/cases/*.json validates (or is correctly
   rejected) against the schema fragment it names — this is where
   boundary/negative behavior (leading zeros, negative zero, malformed
   hashes, etc.) is actually exercised. A case file that never turns up a
   failure is a schema with no adversarial testing, not a schema that
   happens to be perfect; add cases before trusting a pattern.

Run from anywhere; paths are resolved relative to this file's repo root.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema.validators import Draft202012Validator
from referencing import Registry, Resource


def load_registry(schema_dir: Path) -> tuple[Registry, dict[str, dict]]:
    resources = []
    docs: dict[str, dict] = {}
    for path in sorted(schema_dir.glob("*.schema.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        docs[path.name] = doc
        resources.append((path.name, Resource.from_contents(doc)))
        if "$id" in doc:
            resources.append((doc["$id"], Resource.from_contents(doc)))
    return Registry().with_resources(resources), docs


FIXTURE_SCHEMA_MAP = {
    "instrument-id.equity.json": "instrument-id.schema.json",
    "instrument-id.option.json": "instrument-id.schema.json",
    "trade-intent.no-action-example.json": "trade-intent.schema.json",
}


def resolve_json_pointer(document: Any, pointer: str) -> Any:
    """Resolves a JSON Pointer (the part after '#') against `document`."""
    if pointer in ("", "/"):
        return document
    node = document
    for raw_token in pointer.lstrip("/").split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if isinstance(node, list):
            node = node[int(token)]
        else:
            node = node[token]
    return node


def resolve_schema_ref(schema_ref: str, docs: dict[str, dict]) -> Any:
    """Resolves a `file.schema.json#/json/pointer` reference against the
    already-loaded schema documents for one version directory."""
    if "#" in schema_ref:
        filename, pointer = schema_ref.split("#", 1)
    else:
        filename, pointer = schema_ref, ""
    if filename not in docs:
        raise KeyError(f"unknown schema file in schema-ref: {filename!r}")
    return resolve_json_pointer(docs[filename], pointer)


def run_case_files(cases_dir: Path, docs: dict[str, dict], registry: Registry) -> int:
    failures = 0
    for case_path in sorted(cases_dir.glob("*.json")):
        case_doc = json.loads(case_path.read_text(encoding="utf-8"))
        schema_ref = case_doc["schema-ref"]
        try:
            sub_schema = resolve_schema_ref(schema_ref, docs)
        except (KeyError, IndexError, TypeError) as exc:
            print(f"FAIL {case_path.name}: could not resolve schema-ref {schema_ref!r}: {exc}")
            failures += 1
            continue

        validator = Draft202012Validator(sub_schema, registry=registry)
        for test in case_doc["tests"]:
            data = test["data"]
            expected_valid = test["valid"]
            errors = list(validator.iter_errors(data))
            actual_valid = not errors
            label = f"{case_path.name}: {test['description']}"
            if actual_valid == expected_valid:
                print(f"ok   {label}")
            else:
                failures += 1
                if expected_valid:
                    print(f"FAIL {label}: expected valid, got errors: {[e.message for e in errors]}")
                else:
                    print(f"FAIL {label}: expected INVALID, but {data!r} passed validation")
    return failures


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    failures = 0
    for version_dir in sorted((root / "schemas").glob("*")):
        if not version_dir.is_dir():
            continue
        registry, docs = load_registry(version_dir)
        for name, doc in docs.items():
            try:
                Draft202012Validator.check_schema(doc)
                validator = Draft202012Validator(doc, registry=registry)
                validator.check_schema(doc)
            except Exception as exc:  # noqa: BLE001
                print(f"FAIL {version_dir.name}/{name}: {exc}")
                failures += 1
            else:
                print(f"ok   {version_dir.name}/{name}")

        fixtures_dir = root / "testdata" / "golden"
        if fixtures_dir.exists():
            for fixture_path in sorted(fixtures_dir.glob("*.json")):
                schema_name = FIXTURE_SCHEMA_MAP.get(fixture_path.name)
                if schema_name is None or schema_name not in docs:
                    continue
                instance = json.loads(fixture_path.read_text(encoding="utf-8"))
                validator = Draft202012Validator(docs[schema_name], registry=registry)
                errors = sorted(validator.iter_errors(instance), key=str)
                if errors:
                    for err in errors:
                        print(f"FAIL fixture {fixture_path.name} against {schema_name}: {err.message}")
                    failures += len(errors)
                else:
                    print(f"ok   fixture {fixture_path.name} against {schema_name}")

        cases_dir = root / "testdata" / "cases"
        if cases_dir.exists():
            failures += run_case_files(cases_dir, docs, registry)

    if failures:
        print(f"\n{failures} failure(s)")
        return 1
    print("\nAll schemas, golden fixtures, and test cases passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
