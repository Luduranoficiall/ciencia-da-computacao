#!/usr/bin/env python3
"""Testes para JSON Schema dos dados."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

try:
    import jsonschema
    from jsonschema import Draft202012Validator
except ImportError:
    jsonschema = None
    Draft202012Validator = None

ROOT = Path(__file__).resolve().parent.parent


@unittest.skipUnless(jsonschema is not None, "requer: pip install -r requirements-dev.txt")
class TestValidateDataSchemas(unittest.TestCase):
    def test_production_passes(self) -> None:
        r = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "validate_data_schemas.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, msg=r.stderr + r.stdout)

    def test_curriculum_title_empty_rejected(self) -> None:
        schema = json.loads(
            (ROOT / "data/schemas/curriculum.schema.json").read_text(encoding="utf-8")
        )
        instance = {
            "version": 1,
            "nodes": [
                {
                    "id": "a",
                    "title": "",
                    "stage": 1,
                    "tags": ["x"],
                }
            ],
            "edges": [],
        }
        v = Draft202012Validator(schema)
        with self.assertRaises(jsonschema.ValidationError):
            v.validate(instance)


if __name__ == "__main__":
    unittest.main()
