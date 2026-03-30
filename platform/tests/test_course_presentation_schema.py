"""
Mesmo contrato que `tools/validate_data_schemas.py` (CI): o ficheiro de marketing
tem de cumprir `data/schemas/course_presentation.schema.json`.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

try:
    from jsonschema import Draft202012Validator
except ImportError:
    Draft202012Validator = None


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@pytest.mark.skipif(Draft202012Validator is None, reason="requer jsonschema")
def test_course_presentation_file_matches_schema() -> None:
    root = _repo_root()
    data_path = root / "data" / "course_presentation.json"
    schema_path = root / "data" / "schemas" / "course_presentation.schema.json"
    assert data_path.is_file(), f"Em falta: {data_path}"
    assert schema_path.is_file(), f"Em falta: {schema_path}"
    instance = json.loads(data_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(instance)


@pytest.mark.skipif(Draft202012Validator is None, reason="requer jsonschema")
def test_public_course_presentation_response_matches_schema(client) -> None:
    root = _repo_root()
    schema_path = root / "data" / "schemas" / "course_presentation.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    r = client.get("/public/course-presentation")
    assert r.status_code == 200
    Draft202012Validator(schema).validate(r.json())
