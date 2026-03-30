#!/usr/bin/env python3
"""
Verifica o primeiro bloco ```mermaid do README: cada ID em arestas deve estar
definido (no[label] ou subgraph id [...]). Evita nos fantasma como C sem definicao.

Uso:
  python3 tools/check_readme_mermaid.py
  python3 tools/check_readme_mermaid.py --readme caminho/README.md
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from readme_mermaid_common import analyze_mermaid, extract_mermaid_block
from repo_paths import repo_root


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida nos do Mermaid resumido no README.")
    parser.add_argument(
        "--readme",
        type=Path,
        default=repo_root() / "README.md",
        help="Ficheiro Markdown com bloco mermaid",
    )
    args = parser.parse_args()

    if not args.readme.is_file():
        print(f"ERRO: {args.readme} nao encontrado", file=sys.stderr)
        return 2

    try:
        block = extract_mermaid_block(args.readme)
    except ValueError as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 2

    _defs, edges, errors = analyze_mermaid(block)
    if errors:
        for e in errors:
            print(f"ERRO: {e}", file=sys.stderr)
        return 1

    print(f"OK: Mermaid README — {len(_defs)} nos/subgrafos, {len(edges)} arestas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
