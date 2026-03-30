#!/usr/bin/env python3
"""Testes para mermaid_diagram_coverage."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from mermaid_diagram_coverage import load_omit_ids, missing_in_diagram


class TestMissing(unittest.TestCase):
    def test_missing_computed(self) -> None:
        self.assertEqual(
            missing_in_diagram({"a", "b", "c"}, {"a", "b"}),
            ["c"],
        )


class TestOmitListFile(unittest.TestCase):
    def test_duplicate_ids_raise(self) -> None:
        raw = {"ids": ["x", "x"]}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(raw, f)
            p = Path(f.name)
        try:
            with self.assertRaises(ValueError) as ctx:
                load_omit_ids(p)
            self.assertIn("duplicados", str(ctx.exception).lower())
        finally:
            p.unlink(missing_ok=True)


class TestProductionCoverage(unittest.TestCase):
    def test_omit_matches_curriculum(self) -> None:
        root = Path(__file__).resolve().parent.parent
        r = subprocess.run(
            [sys.executable, str(root / "tools" / "mermaid_diagram_coverage.py")],
            cwd=root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, msg=r.stderr + r.stdout)


if __name__ == "__main__":
    unittest.main()
