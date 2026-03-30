#!/usr/bin/env python3
"""Testes para curriculum_common (grafo, validacao, DAG)."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from curriculum_common import (
    collect_graph_warnings,
    kahn_topological,
    load_graph,
    validate_structure,
)


class TestLoadGraph(unittest.TestCase):
    def test_duplicate_ids_raise(self) -> None:
        raw = {
            "nodes": [
                {"id": "a", "title": "A", "stage": 1, "tags": []},
                {"id": "a", "title": "A2", "stage": 1, "tags": []},
            ],
            "edges": [],
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(raw, f)
            path = Path(f.name)
        try:
            with self.assertRaises(ValueError) as ctx:
                load_graph(path)
            self.assertIn("duplicados", str(ctx.exception).lower())
        finally:
            path.unlink(missing_ok=True)

    def test_duplicate_edges_raise(self) -> None:
        raw = {
            "nodes": [
                {"id": "a", "title": "A", "stage": 1, "tags": []},
                {"id": "b", "title": "B", "stage": 2, "tags": []},
            ],
            "edges": [["a", "b"], ["a", "b"]],
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(raw, f)
            path = Path(f.name)
        try:
            with self.assertRaises(ValueError) as ctx:
                load_graph(path)
            self.assertIn("duplicada", str(ctx.exception).lower())
        finally:
            path.unlink(missing_ok=True)


class TestValidateStructure(unittest.TestCase):
    def test_stage_regression_reported(self) -> None:
        nodes = {
            "late": {"id": "late", "title": "Late", "stage": 3, "tags": []},
            "early": {"id": "early", "title": "Early", "stage": 1, "tags": []},
        }
        edges = [("late", "early")]
        err = validate_structure(nodes, edges)
        self.assertTrue(any("regressiva" in e for e in err))

    def test_empty_title_reported(self) -> None:
        nodes = {"a": {"id": "a", "title": "   ", "stage": 1, "tags": ["x"]}}
        err = validate_structure(nodes, [])
        self.assertTrue(any("title" in e.lower() for e in err))

    def test_empty_tag_string_reported(self) -> None:
        nodes = {
            "a": {"id": "a", "title": "A", "stage": 1, "tags": ["ok", "  "]},
        }
        err = validate_structure(nodes, [])
        self.assertTrue(any("tags" in e.lower() for e in err))

    def test_object_id_must_match_key(self) -> None:
        nodes = {
            "ok": {
                "id": "wrong",
                "title": "T",
                "stage": 1,
                "tags": ["x"],
            },
        }
        err = validate_structure(nodes, [])
        self.assertTrue(any("coincidir" in e.lower() for e in err))


class TestKahn(unittest.TestCase):
    def test_known_dag_order_length(self) -> None:
        root = Path(__file__).resolve().parent.parent / "data" / "curriculum.json"
        nodes, edges = load_graph(root)
        order, leftover = kahn_topological(nodes, edges)
        self.assertEqual(len(leftover), 0)
        self.assertEqual(len(order), len(nodes))


class TestGraphWarnings(unittest.TestCase):
    def test_production_graph_has_no_warnings(self) -> None:
        root = Path(__file__).resolve().parent.parent / "data" / "curriculum.json"
        nodes, edges = load_graph(root)
        self.assertEqual(collect_graph_warnings(nodes, edges), [])

    def test_isolated_nodes_reported(self) -> None:
        nodes = {
            "a": {"id": "a", "title": "A", "stage": 1, "tags": ["x"]},
            "b": {"id": "b", "title": "B", "stage": 2, "tags": ["y"]},
        }
        self.assertTrue(collect_graph_warnings(nodes, []))


if __name__ == "__main__":
    unittest.main()
