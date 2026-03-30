#!/usr/bin/env python3
"""
Valida ficheiros JSON em data/ contra data/schemas/*.schema.json (JSON Schema).

Requer: pip install -r requirements-dev.txt

Uso:
  python3 tools/validate_data_schemas.py
  python3 tools/validate_data_schemas.py --verbose
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from repo_paths import repo_root

try:
    import jsonschema
    from jsonschema import Draft202012Validator
except ImportError:
    jsonschema = None  # type: ignore
    Draft202012Validator = None  # type: ignore

# (ficheiro em data/, nome do schema)
DATA_FILES: list[tuple[str, str]] = [
    ("curriculum.json", "curriculum.schema.json"),
    ("progress.json", "progress.schema.json"),
    ("readme_mermaid_map.json", "readme_mermaid_map.schema.json"),
    ("readme_mermaid_diagram_omit.json", "readme_mermaid_diagram_omit.schema.json"),
    ("course_presentation.json", "course_presentation.schema.json"),
]


def validate_one(
    data_path: Path,
    schema_path: Path,
    verbose: bool,
) -> list[str]:
    """Devolve lista de mensagens de erro (vazia se OK)."""
    errs: list[str] = []
    try:
        instance = json.loads(data_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"{data_path.name}: JSON invalido ({e})"]
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"{schema_path.name}: schema JSON invalido ({e})"]
    validator = Draft202012Validator(schema)
    for error in validator.iter_errors(instance):
        loc = "/".join(str(x) for x in error.absolute_path) or "(root)"
        msg = f"{data_path.name}: {error.message} (em {loc})"
        errs.append(msg)
        if not verbose and len(errs) >= 12:
            errs.append(f"{data_path.name}: ... (use --verbose para mais)")
            break
    return errs


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida data/*.json contra JSON Schema.")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Lista todos os erros de schema (sem truncar).",
    )
    args = parser.parse_args()

    if jsonschema is None or Draft202012Validator is None:
        print(
            "ERRO: pacote 'jsonschema' nao instalado. Corra: pip install -r requirements-dev.txt",
            file=sys.stderr,
        )
        return 2

    root = repo_root()
    data_dir = root / "data"
    schema_dir = data_dir / "schemas"
    all_errs: list[str] = []

    for data_name, schema_name in DATA_FILES:
        data_path = data_dir / data_name
        schema_path = schema_dir / schema_name
        if not data_path.is_file():
            all_errs.append(f"ERRO: ficheiro em falta: {data_path}")
            continue
        if not schema_path.is_file():
            all_errs.append(f"ERRO: schema em falta: {schema_path}")
            continue
        all_errs.extend(validate_one(data_path, schema_path, args.verbose))

    if all_errs:
        for e in all_errs:
            print(f"ERRO: {e}", file=sys.stderr)
        return 1

    print(f"OK: JSON Schema — {len(DATA_FILES)} ficheiros em data/ validados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
