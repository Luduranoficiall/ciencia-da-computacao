#!/usr/bin/env python3
"""
Verifica o diagrama Mermaid do README contra o grafo canonico:

1. Conjunto de nos `X[...]` (exceto subgraphs) == chaves de readme_mermaid_map.json
2. Cada valor do mapa e unico (1:1 com disciplinas no diagrama)
3. Valores existem em curriculum.json
4. Cada aresta Mermaid existe em curriculum.json

Uso:
  python3 tools/check_mermaid_curriculum_sync.py
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from curriculum_common import load_graph
from readme_mermaid_common import (
    analyze_mermaid,
    diagram_node_ids,
    extract_mermaid_block,
    load_mermaid_node_map,
    subgraph_ids,
)
from repo_paths import repo_root


def main() -> int:
    parser = argparse.ArgumentParser(description="Mermaid README vs curriculum.json")
    parser.add_argument(
        "--readme",
        type=Path,
        default=repo_root() / "README.md",
        help="Markdown com bloco mermaid",
    )
    parser.add_argument(
        "--map",
        type=Path,
        default=repo_root() / "data" / "readme_mermaid_map.json",
        help="Mapeamento ID Mermaid -> ID curriculum",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=repo_root() / "data" / "curriculum.json",
        help="curriculum.json",
    )
    args = parser.parse_args()

    if not args.readme.is_file():
        print(f"ERRO: {args.readme} nao encontrado", file=sys.stderr)
        return 2
    if not args.map.is_file():
        print(f"ERRO: {args.map} nao encontrado", file=sys.stderr)
        return 2

    try:
        mermaid = extract_mermaid_block(args.readme)
    except ValueError as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 2

    _defs, short_edges, struct_err = analyze_mermaid(mermaid)
    if struct_err:
        for e in struct_err:
            print(f"ERRO: {e}", file=sys.stderr)
        return 1

    try:
        cmap = load_mermaid_node_map(args.map)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"ERRO mapa: {e}", file=sys.stderr)
        return 2

    subs = subgraph_ids(mermaid)
    dnodes = diagram_node_ids(_defs, subs)
    map_keys = set(cmap.keys())
    if dnodes != map_keys:
        missing = sorted(dnodes - map_keys)
        extra = sorted(map_keys - dnodes)
        if missing:
            print(
                f"ERRO: IDs no diagrama Mermaid sem entrada em readme_mermaid_map.json: {missing}",
                file=sys.stderr,
            )
        if extra:
            print(
                f"ERRO: Chaves no mapa sem no correspondente no diagrama: {extra}",
                file=sys.stderr,
            )
        return 1

    dup_targets = [cid for cid, n in Counter(cmap.values()).items() if n > 1]
    if dup_targets:
        print(
            f"ERRO: curriculum id repetido no mapa (ambiguo): {sorted(dup_targets)}",
            file=sys.stderr,
        )
        return 1

    try:
        nodes, edges = load_graph(args.data)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"ERRO curriculum: {e}", file=sys.stderr)
        return 2

    for short, cid in sorted(cmap.items()):
        if cid not in nodes:
            print(
                f"ERRO: mapa {short!r} -> {cid!r}: ID inexistente em curriculum.json",
                file=sys.stderr,
            )
            return 1

    edge_set = set(tuple(e) for e in edges)
    errors: list[str] = []

    for a, b in sorted(short_edges):
        if a not in cmap:
            errors.append(f"Aresta {a} --> {b}: ID {a!r} sem entrada em readme_mermaid_map.json")
            continue
        if b not in cmap:
            errors.append(f"Aresta {a} --> {b}: ID {b!r} sem entrada em readme_mermaid_map.json")
            continue
        ca, cb = cmap[a], cmap[b]
        if (ca, cb) not in edge_set:
            errors.append(
                f"Aresta Mermaid {a} --> {b} ({ca} -> {cb}) nao existe em curriculum.json"
            )

    if errors:
        for e in errors:
            print(f"ERRO: {e}", file=sys.stderr)
        return 1

    print(
        f"OK: mapa ({len(cmap)} nos) + {len(short_edges)} arestas Mermaid conferem com "
        f"{args.data.name}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
