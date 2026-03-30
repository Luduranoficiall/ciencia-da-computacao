"""Testes para check_exercicios_semester (mapa S1-S8 vs cabeçalhos)."""
from __future__ import annotations

import contextlib
import io
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from check_exercicios_semester import (
    SEMESTER_BY_ID,
    run_check,
    validate_exercicios_semesters,
)


def _write(tmp: Path, name: str, content: str) -> Path:
    p = tmp / name
    p.write_text(content, encoding="utf-8")
    return p


class TestValidateExerciciosSemesters(unittest.TestCase):
    def test_minimal_ok(self) -> None:
        curriculum_ids = {"a", "b"}
        semester = {"a": 1, "b": 2}
        doc = """### Alpha (`a`) — sem. **S1**
### Beta (`b`) — sem. **S2**
"""
        err = validate_exercicios_semesters(
            doc,
            curriculum_ids=curriculum_ids,
            semester_by_id=semester,
            doc_label="t.md",
        )
        self.assertEqual(err, [])

    def test_missing_section(self) -> None:
        err = validate_exercicios_semesters(
            "### A (`a`) — sem. **S1**\n",
            curriculum_ids={"a", "b"},
            semester_by_id={"a": 1, "b": 2},
            doc_label="t.md",
        )
        self.assertTrue(any("`b`" in e and "sem secção" in e for e in err))

    def test_wrong_semester(self) -> None:
        err = validate_exercicios_semesters(
            "### A (`a`) — sem. **S2**\n",
            curriculum_ids={"a"},
            semester_by_id={"a": 1},
            doc_label="t.md",
        )
        self.assertTrue(any("S2" in e and "S1" in e for e in err))

    def test_malformed_heading(self) -> None:
        err = validate_exercicios_semesters(
            "### A (`a`) sem suffix\n",
            curriculum_ids={"a"},
            semester_by_id={"a": 1},
            doc_label="t.md",
        )
        self.assertTrue(any("canónico" in e for e in err))

    def test_unknown_id_not_in_curriculum(self) -> None:
        err = validate_exercicios_semesters(
            "### Z (`zzz`) — sem. **S1**\n",
            curriculum_ids={"a"},
            semester_by_id={"a": 1, "zzz": 1},
            doc_label="t.md",
        )
        self.assertTrue(any("zzz" in e and "não existe" in e for e in err))
        self.assertTrue(any("`a`" in e for e in err))

    def test_duplicate_headings(self) -> None:
        doc = """### A (`a`) — sem. **S1**
### A again (`a`) — sem. **S1**
"""
        err = validate_exercicios_semesters(
            doc,
            curriculum_ids={"a"},
            semester_by_id={"a": 1},
            doc_label="t.md",
        )
        self.assertTrue(any("duplicada" in e for e in err))


class TestRunCheckIntegration(unittest.TestCase):
    def test_production_repo_passes(self) -> None:
        root = Path(__file__).resolve().parent.parent
        code = run_check(
            doc_path=root / "docs" / "exercicios-por-disciplina.md",
            curriculum_path=root / "data" / "curriculum.json",
            semester_by_id=SEMESTER_BY_ID,
        )
        self.assertEqual(code, 0, "exercicios-por-disciplina.md deve alinhar com curriculum.json")

    def test_run_check_fails_on_bad_doc(self) -> None:
        curriculum = {
            "version": 1,
            "description": "t",
            "nodes": [{"id": "only", "title": "Only", "stage": 1, "tags": []}],
            "edges": [],
        }
        with TemporaryDirectory() as td:
            tmp = Path(td)
            cpath = _write(tmp, "c.json", json.dumps(curriculum))
            _write(tmp, "x.md", "### Only (`only`) — sem. **S9**\n")
            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                code = run_check(
                    doc_path=tmp / "x.md",
                    curriculum_path=cpath,
                    semester_by_id={"only": 1},
                )
        self.assertEqual(code, 1)
        self.assertIn("S9", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
