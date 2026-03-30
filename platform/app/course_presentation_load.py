"""Carrega `data/course_presentation.json` (textos da landing pública)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_course_presentation(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(str(path))
    with path.open(encoding="utf-8") as f:
        return json.load(f)
