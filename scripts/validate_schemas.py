#!/usr/bin/env python3
"""Validate every schema in schemas/<version>/ is well-formed JSON Schema 2020-12
and that all internal $ref targets resolve. Run from the repo root."""
from __future__ import annotations

import json
import sys
from pathlib import Path

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

    if failures:
        print(f"\n{failures} failure(s)")
        return 1
    print("\nAll schemas and golden fixtures are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
