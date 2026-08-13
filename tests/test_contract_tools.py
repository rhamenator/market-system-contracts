import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from canonical_hash import canonical_hash, canonical_json, canonicalize  # noqa: E402
from validate_schemas import resolve_json_pointer, resolve_schema_ref  # noqa: E402


class CanonicalHashTests(unittest.TestCase):
    def test_canonicalize_sorts_nested_objects_without_mutating_array_order(self):
        value = {"z": [{"b": 2, "a": 1}, 0], "a": "é"}
        self.assertEqual({"a": "é", "z": [{"a": 1, "b": 2}, 0]}, canonicalize(value))
        self.assertEqual('{"a":"é","z":[{"a":1,"b":2},0]}', canonical_json(value))

    def test_hash_is_stable_across_object_key_order(self):
        self.assertEqual(canonical_hash({"a": 1, "b": 2}), canonical_hash({"b": 2, "a": 1}))
        self.assertRegex(canonical_hash({}), r"^sha256:[0-9a-f]{64}$")

    def test_json_pointer_decodes_escaped_tokens_and_array_indexes(self):
        document = {"a/b": {"~key": ["zero", "one"]}}
        self.assertEqual("one", resolve_json_pointer(document, "/a~1b/~0key/1"))

    def test_schema_ref_rejects_unknown_documents(self):
        with self.assertRaises(KeyError):
            resolve_schema_ref("missing.schema.json#/value", {})

    def test_committed_vectors_remain_reproducible(self):
        vectors = json.loads((ROOT / "testdata/canonical-hashing/vectors.json").read_text(encoding="utf-8"))
        for vector in vectors["vectors"]:
            with self.subTest(vector=vector["name"]):
                self.assertEqual(vector["canonical"], canonical_json(vector["input"]))
                self.assertEqual(vector["sha256"], canonical_hash(vector["input"]))


if __name__ == "__main__":
    unittest.main()
