"""Carrega IDs obrigatorios do grafo curriculum.json (raiz do repo)."""

from __future__ import annotations

import json
from pathlib import Path


def load_required_module_slugs(curriculum_path: Path) -> list[str]:
    if not curriculum_path.is_file():
        raise FileNotFoundError(f"curriculum.json nao encontrado: {curriculum_path}")
    with curriculum_path.open(encoding="utf-8") as f:
        data = json.load(f)
    nodes = data.get("nodes")
    if not isinstance(nodes, list):
        raise ValueError("curriculum.json: 'nodes' deve ser lista")
    slugs: list[str] = []
    seen: set[str] = set()
    for item in nodes:
        if not isinstance(item, dict) or "id" not in item:
            raise ValueError("cada node precisa de 'id'")
        sid = str(item["id"])
        if sid in seen:
            raise ValueError(f"ID duplicado em curriculum.json: {sid}")
        seen.add(sid)
        slugs.append(sid)
    return slugs


def completion_fraction(completed: set[str], required: list[str]) -> tuple[int, int]:
    req = set(required)
    return len(completed & req), len(req)
