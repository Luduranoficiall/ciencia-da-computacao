#!/usr/bin/env python3
"""
Valida data/curriculum.json: nos unicos, arestas validas, DAG (sem ciclos),
ordenacao topologica. Apenas biblioteca padrao.

Uso:
  python3 tools/validate_curriculum.py
  python3 tools/validate_curriculum.py --topo
  python3 tools/validate_curriculum.py --mermaid
  python3 tools/validate_curriculum.py --strict   # falha se existirem avisos
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from curriculum_common import (
    collect_graph_warnings,
    kahn_topological,
    load_graph,
    mermaid,
    validate_structure,
)
from repo_paths import repo_root


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida o grafo do curriculo.",
        epilog="Codigos de saida: 0 OK, 1 validacao/DAG, 2 I/O ou JSON invalido.",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=repo_root() / "data" / "curriculum.json",
        help="Caminho para curriculum.json",
    )
    parser.add_argument("--topo", action="store_true", help="Imprime ordenacao topologica (uma linha por no).")
    parser.add_argument("--mermaid", action="store_true", help="Imprime diagrama Mermaid para colar no GitHub.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Codigo de saida 1 se houver avisos (ex.: nos isolados no grafo).",
    )
    args = parser.parse_args()

    if not args.data.is_file():
        print(f"ERRO: ficheiro nao encontrado: {args.data}", file=sys.stderr)
        return 2

    try:
        nodes, edges = load_graph(args.data)
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"ERRO ao ler JSON: {e}", file=sys.stderr)
        return 2

    err = validate_structure(nodes, edges)
    if err:
        for e in err:
            print(f"ERRO: {e}", file=sys.stderr)
        return 1

    order, leftover = kahn_topological(nodes, edges)
    if leftover:
        print(
            f"ERRO: grafo com ciclo (nos nao ordenados): {', '.join(leftover)}",
            file=sys.stderr,
        )
        return 1

    print(f"OK: {len(nodes)} nos, {len(edges)} arestas, DAG valido.")

    warns = collect_graph_warnings(nodes, edges)
    for w in warns:
        print(f"AVISO: {w}", file=sys.stderr)
    if args.strict and warns:
        print("ERRO: --strict com avisos pendentes.", file=sys.stderr)
        return 1

    if args.topo:
        for nid in order:
            st = nodes[nid]["stage"]
            print(f"  etapa {st}: {nid}")

    if args.mermaid:
        print(mermaid(nodes, edges))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
