#!/usr/bin/env python3
"""
Cobertura do diagrama Mermaid resumido vs curriculum.json completo.

Sem flags: verifica se readme_mermaid_diagram_omit.json lista exatamente as
disciplinas que nao aparecem no mapa (falha = conjuntos diferentes).

  python3 tools/mermaid_diagram_coverage.py
  python3 tools/mermaid_diagram_coverage.py --report
  python3 tools/mermaid_diagram_coverage.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from curriculum_common import load_graph
from readme_mermaid_common import load_mermaid_node_map
from repo_paths import repo_root


def load_omit_ids(path: Path) -> list[str]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    ids = raw.get("ids")
    if not isinstance(ids, list):
        raise ValueError(f"{path.name}: campo 'ids' deve ser uma lista.")
    out: list[str] = []
    for x in ids:
        if not isinstance(x, str) or not x.strip():
            raise ValueError(f"{path.name}: cada id deve ser string nao vazia.")
        out.append(x.strip())
    if len(out) != len(set(out)):
        raise ValueError(f"{path.name}: ids duplicados na lista.")
    return sorted(out)


def missing_in_diagram(
    curriculum_ids: set[str], map_values: set[str]
) -> list[str]:
    return sorted(curriculum_ids - map_values)


def report_by_stage(
    nodes: dict[str, dict], mapped: set[str], missing: list[str]
) -> str:
    lines: list[str] = []
    lines.append("# Cobertura: diagrama Mermaid resumido vs curriculum\n")
    n = len(nodes)
    m = len(mapped)
    lines.append(f"- **No grafo (curriculum.json):** {n} disciplinas\n")
    lines.append(f"- **No diagrama resumido (mapa):** {m} disciplinas\n")
    lines.append(f"- **So no grafo (fora do diagrama):** {len(missing)}\n")
    lines.append("\n## Por etapa (ausentes do diagrama)\n")
    by_stage: dict[int, list[str]] = {}
    for nid in missing:
        st = nodes[nid].get("stage", "?")
        by_stage.setdefault(int(st) if isinstance(st, int) else 0, []).append(nid)
    for st in sorted(by_stage.keys()):
        lines.append(f"\n### Etapa {st}\n\n")
        for nid in sorted(by_stage[st]):
            title = nodes[nid].get("title", "")
            lines.append(f"- `{nid}` — {title}\n")
    lines.append("\n## IDs no mapa Mermaid\n\n")
    for nid in sorted(mapped):
        title = nodes[nid].get("title", "")
        lines.append(f"- `{nid}` — {title}\n")
    return "".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Cobertura do diagrama Mermaid vs curriculum completo."
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Imprime relatorio Markdown para stdout (nao falha).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Imprime JSON (cobertura) para stdout; com --report nao valida omit.",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=repo_root() / "data" / "curriculum.json",
    )
    parser.add_argument(
        "--map",
        type=Path,
        default=repo_root() / "data" / "readme_mermaid_map.json",
    )
    parser.add_argument(
        "--omit",
        type=Path,
        default=repo_root() / "data" / "readme_mermaid_diagram_omit.json",
    )
    args = parser.parse_args()

    if not args.data.is_file() or not args.map.is_file():
        print("ERRO: curriculum.json ou mapa em falta.", file=sys.stderr)
        return 2

    try:
        nodes, _edges = load_graph(args.data)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"ERRO curriculum: {e}", file=sys.stderr)
        return 2

    try:
        cmap = load_mermaid_node_map(args.map)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"ERRO mapa: {e}", file=sys.stderr)
        return 2

    curriculum_ids = set(nodes.keys())
    map_values = set(cmap.values())
    missing = missing_in_diagram(curriculum_ids, map_values)

    if args.json:
        payload = coverage_payload(nodes, map_values, missing)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.report:
        print(report_by_stage(nodes, map_values, missing), end="")
        return 0

    if not args.omit.is_file():
        print(f"ERRO: {args.omit} nao encontrado (necessario para verificacao).", file=sys.stderr)
        return 2

    try:
        allowed = load_omit_ids(args.omit)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"ERRO omit list: {e}", file=sys.stderr)
        return 2

    for oid in allowed:
        if oid not in curriculum_ids:
            print(
                f"ERRO: omit list contem {oid!r} que nao existe em curriculum.json",
                file=sys.stderr,
            )
            return 1

    extra_in_curriculum = sorted(set(missing) - set(allowed))
    stale_in_omit = sorted(set(allowed) - set(missing))
    if extra_in_curriculum or stale_in_omit:
        if extra_in_curriculum:
            print(
                "ERRO: disciplinas sem entrada no diagrama nem em readme_mermaid_diagram_omit.json:",
                ", ".join(extra_in_curriculum),
                file=sys.stderr,
            )
        if stale_in_omit:
            print(
                "ERRO: readme_mermaid_diagram_omit.json lista IDs que ja estao no mapa ou nao faltam:",
                ", ".join(stale_in_omit),
                file=sys.stderr,
            )
        return 1

    print(
        f"OK: cobertura — {len(map_values)}/{len(curriculum_ids)} no diagrama; "
        f"{len(allowed)} omitidas por desenho (lista fechada)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
