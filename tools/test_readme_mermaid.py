#!/usr/bin/env python3
"""Testes para readme_mermaid_common e check_mermaid_curriculum_sync."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from readme_mermaid_common import (
    analyze_mermaid,
    diagram_node_ids,
    extract_mermaid_block,
    subgraph_ids,
)


class TestAmpersandEdges(unittest.TestCase):
    def test_two_edges_one_line(self) -> None:
        body = """
flowchart LR
  A[A]
  B[B]
  C[C]
  A --> B & B --> C
"""
        defs, edges, err = analyze_mermaid(body)
        self.assertEqual(err, [])
        self.assertIn(("A", "B"), edges)
        self.assertIn(("B", "C"), edges)


class TestSubgraphHelpers(unittest.TestCase):
    def test_subgraph_ids_and_diagram_nodes(self) -> None:
        body = """
flowchart TB
  subgraph sx [X]
    A[aa]
  end
  B[bb]
"""
        defs, _e, err = analyze_mermaid(body)
        self.assertEqual(err, [])
        subs = subgraph_ids(body)
        self.assertEqual(subs, {"sx"})
        self.assertEqual(diagram_node_ids(defs, subs), {"A", "B"})


class TestAnalyzeMermaid(unittest.TestCase):
    def test_ok_small_graph(self) -> None:
        body = """
flowchart TB
  A[One]
  B[Two]
  A --> B
"""
        defs, edges, err = analyze_mermaid(body)
        self.assertEqual(err, [])
        self.assertIn("A", defs)
        self.assertIn("B", defs)
        self.assertIn(("A", "B"), edges)

    def test_undefined_node_fails(self) -> None:
        body = """
flowchart TB
  A[One]
  A --> Z
"""
        _d, _e, err = analyze_mermaid(body)
        self.assertTrue(any("Z" in e for e in err))


class TestExtractBlock(unittest.TestCase):
    def test_extracts_from_temp_readme(self) -> None:
        content = """# T
```mermaid
flowchart LR
  X[X]
```
Rest
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            p = Path(f.name)
        try:
            b = extract_mermaid_block(p)
            self.assertIn("flowchart LR", b)
            self.assertIn("X[X]", b)
        finally:
            p.unlink(missing_ok=True)


class TestMermaidCurriculumSync(unittest.TestCase):
    def test_readme_matches_json(self) -> None:
        import subprocess
        import sys

        root = Path(__file__).resolve().parent.parent
        r = subprocess.run(
            [sys.executable, str(root / "tools" / "check_mermaid_curriculum_sync.py")],
            cwd=root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, msg=r.stderr + r.stdout)


if __name__ == "__main__":
    unittest.main()
