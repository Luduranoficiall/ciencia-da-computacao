"""Raiz do repositorio (unico ponto de verdade para caminhos relativos aos tools/)."""
from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent
