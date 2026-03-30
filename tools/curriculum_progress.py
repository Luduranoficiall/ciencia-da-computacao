#!/usr/bin/env python3
"""
Cruza data/curriculum.json com data/progress.json (disciplinas concluidas)
e mostra o que esta bloqueado, o que pode iniciar e estatisticas.

Uso:
  python3 tools/curriculum_progress.py
  python3 tools/curriculum_progress.py --json
  python3 tools/curriculum_progress.py --md > relatorio.md
  python3 tools/curriculum_progress.py --validate   # so valida IDs; exit 1 se erro
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from curriculum_common import kahn_topological, load_graph, predecessors, validate_structure
from repo_paths import repo_root


def load_progress(path: Path) -> tuple[set[str], list[str]]:
    """Devolve (completed_ids, erros de formato)."""
    errors: list[str] = []
    if not path.is_file():
        errors.append(f"Ficheiro de progresso nao encontrado: {path}")
        return set(), errors
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"JSON invalido: {e}")
        return set(), errors
    ver = raw.get("version", 1)
    if ver != 1:
        errors.append(f"Versao de progress.json nao suportada: {ver}")
    done = raw.get("completed")
    if not isinstance(done, list):
        errors.append("Campo 'completed' deve ser uma lista de strings (IDs).")
        return set(), errors
    out: set[str] = set()
    for x in done:
        if not isinstance(x, str):
            errors.append(f"ID invalido em completed (nao e string): {x!r}")
            continue
        out.add(x.strip())
    out.discard("")
    return out, errors


def validate_progress_ids(completed: set[str], nodes: dict[str, dict]) -> list[str]:
    err: list[str] = []
    known = set(nodes.keys())
    for cid in sorted(completed):
        if cid not in known:
            err.append(f"ID em completed desconhecido no curriculum: {cid!r}")
    return err


def analyze(
    nodes: dict[str, dict],
    edges: list[tuple[str, str]],
    completed: set[str],
) -> dict:
    pred = predecessors(nodes, edges)
    pending = set(nodes) - completed
    ready: list[str] = []
    blocked: list[dict] = []
    for nid in sorted(pending, key=lambda x: (nodes[x]["stage"], x)):
        need = [p for p in pred[nid] if p not in completed]
        if not need:
            ready.append(nid)
        else:
            blocked.append(
                {
                    "id": nid,
                    "title": nodes[nid]["title"],
                    "stage": nodes[nid]["stage"],
                    "missing_prerequisites": need,
                }
            )
    ready.sort(key=lambda x: (nodes[x]["stage"], x))

    def direct_pending_children(rid: str) -> int:
        return sum(1 for u, v in edges if u == rid and v in pending)

    suggestions = sorted(
        ready,
        key=lambda rid: (-direct_pending_children(rid), nodes[rid]["stage"], rid),
    )
    suggestions_full = [
        {
            "id": rid,
            "title": nodes[rid]["title"],
            "stage": nodes[rid]["stage"],
            "direct_pending_children": direct_pending_children(rid),
        }
        for rid in suggestions
    ]

    # Desbloqueios: a partir do que ja fizeste, que arestas "ativam" filhos ainda pendentes
    unlocks: dict[str, list[str]] = {}
    for u in sorted(completed):
        children = sorted(v for (a, v) in edges if a == u and v not in completed)
        if children:
            unlocks[u] = children

    order, leftover = kahn_topological(nodes, edges)
    dag_ok = len(leftover) == 0

    return {
        "dag_ok": dag_ok,
        "total_nodes": len(nodes),
        "completed_count": len(completed),
        "pending_count": len(pending),
        "ready": ready,
        "blocked": blocked,
        "unlocks_from_completed": unlocks,
        "topological_order": order if dag_ok else [],
        "suggestions": suggestions_full,
    }


def print_report(data: dict, nodes: dict[str, dict], top_next: int) -> None:
    print(
        f"Progresso: {data['completed_count']}/{data['total_nodes']} disciplinas em completed."
    )
    if not data["dag_ok"]:
        print("AVISO: grafo do curriculum nao e DAG valido — relatorio pode ser incompleto.")
        return

    print("\n--- Prontas para iniciar (todos os pre-requisitos cumpridos) ---")
    if not data["ready"]:
        print("  (nenhuma — ou ja concluiu tudo, ou falta marcar pre-requisitos em completed)")
    for nid in data["ready"]:
        n = nodes[nid]
        print(f"  [{n['stage']}] {nid}: {n['title']}")

    print(
        "\n--- Sugestoes (entre as prontas: mais filhos pendentes diretos no grafo primeiro) ---"
    )
    sug = data["suggestions"][:top_next]
    if not data["ready"]:
        print("  (nenhuma pronta — concluiu tudo ou falta pre-requisito em completed)")
    elif not sug:
        print("  (nenhuma)")
    else:
        for s in sug:
            k = s["direct_pending_children"]
            print(
                f"  [{s['stage']}] {s['id']}: {s['title']}  "
                f"(desbloqueia {k} pendente(s) direto(s))"
            )

    print("\n--- Bloqueadas (falta pre-requisito no conjunto completed) ---")
    if not data["blocked"]:
        print("  (nenhuma)")
    for b in sorted(data["blocked"], key=lambda x: (x["stage"], x["id"])):
        miss = ", ".join(b["missing_prerequisites"])
        print(f"  [{b['stage']}] {b['id']}: falta → {miss}")

    print("\n--- O que cada conclusao desbloqueia (filhos ainda pendentes) ---")
    um = data["unlocks_from_completed"]
    if not um:
        print("  (nada a listar ou grafo vazio neste recorte)")
    for u, children in sorted(um.items()):
        print(f"  {u} → {', '.join(children)}")


def md_report(data: dict, nodes: dict[str, dict], top_next: int) -> str:
    lines: list[str] = []
    lines.append("# Relatorio de progresso\n")
    lines.append(
        f"**Progresso:** {data['completed_count']}/{data['total_nodes']} disciplinas em `completed`.\n"
    )
    if not data["dag_ok"]:
        lines.append(
            "\n> **Aviso:** o grafo do curriculum nao e um DAG valido; relatorio incompleto.\n"
        )
        return "\n".join(lines)

    lines.append("\n## Prontas para iniciar\n")
    if not data["ready"]:
        lines.append(
            "- *(nenhuma — ou ja concluiu tudo, ou falta marcar pre-requisitos em completed)*\n"
        )
    else:
        for nid in data["ready"]:
            n = nodes[nid]
            lines.append(f"- **[{n['stage']}]** `{nid}` — {n['title']}\n")

    lines.append("\n## Sugestoes (impacto direto no grafo)\n")
    lines.append(
        "Entre as prontas, ordenadas por quantos **filhos ainda pendentes** cada uma tem "
        f"(tie-break: etapa menor, depois ID). Mostrando as {top_next} primeiras.\n\n"
    )
    sug = data["suggestions"][:top_next]
    if not data["ready"]:
        lines.append(
            "- *(nenhuma pronta — concluiu tudo ou falta pre-requisito em completed)*\n"
        )
    elif not sug:
        lines.append("- *(nenhuma)*\n")
    else:
        for s in sug:
            k = s["direct_pending_children"]
            lines.append(
                f"- **[{s['stage']}]** `{s['id']}` — {s['title']} "
                f"({k} pendente(s) direto(s) abaixo no grafo)\n"
            )

    lines.append("\n## Bloqueadas\n")
    if not data["blocked"]:
        lines.append("- *(nenhuma)*\n")
    else:
        for b in sorted(data["blocked"], key=lambda x: (x["stage"], x["id"])):
            miss = ", ".join(f"`{x}`" for x in b["missing_prerequisites"])
            lines.append(f"- **[{b['stage']}]** `{b['id']}` — {b['title']}: falta {miss}\n")

    lines.append("\n## Desbloqueios a partir do concluido\n")
    um = data["unlocks_from_completed"]
    if not um:
        lines.append("- *(nada a listar)*\n")
    else:
        for u, children in sorted(um.items()):
            ch = ", ".join(f"`{c}`" for c in children)
            lines.append(f"- `{u}` → {ch}\n")

    return "".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Analisa progresso face ao grafo do curriculum.")
    parser.add_argument(
        "--data",
        type=Path,
        default=repo_root() / "data" / "curriculum.json",
        help="curriculum.json",
    )
    parser.add_argument(
        "--progress",
        type=Path,
        default=repo_root() / "data" / "progress.json",
        help="progress.json (lista completed)",
    )
    out = parser.add_mutually_exclusive_group()
    out.add_argument("--json", action="store_true", help="Saida em JSON para scripts.")
    out.add_argument(
        "--md",
        action="store_true",
        help="Saida em Markdown (UTF-8) para colar em notas ou Gist.",
    )
    parser.add_argument(
        "--top-next",
        type=int,
        default=5,
        metavar="N",
        help="Quantas sugestoes mostrar no texto/Markdown (padrao: 5).",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="So valida progress + curriculum; exit 1 se IDs invalidos.",
    )
    args = parser.parse_args()

    if not args.data.is_file():
        print(f"ERRO: {args.data} nao encontrado", file=sys.stderr)
        return 2

    try:
        nodes, edges = load_graph(args.data)
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"ERRO curriculum: {e}", file=sys.stderr)
        return 2

    err = validate_structure(nodes, edges)
    if err:
        for e in err:
            print(f"ERRO curriculum: {e}", file=sys.stderr)
        return 1
    _, leftover = kahn_topological(nodes, edges)
    if leftover:
        print(f"ERRO: ciclo no curriculum: {leftover}", file=sys.stderr)
        return 1

    completed, perr = load_progress(args.progress)
    for e in perr:
        print(f"ERRO progresso: {e}", file=sys.stderr)
    if perr:
        return 1

    id_err = validate_progress_ids(completed, nodes)
    if id_err:
        for e in id_err:
            print(f"ERRO: {e}", file=sys.stderr)
        return 1

    if args.validate:
        print(f"OK: progresso valido ({len(completed)} IDs reconhecidos).")
        return 0

    report = analyze(nodes, edges, completed)

    if args.json:
        out = {
            "completed": sorted(completed),
            "ready": [
                {"id": x, "title": nodes[x]["title"], "stage": nodes[x]["stage"]}
                for x in report["ready"]
            ],
            "suggestions": report["suggestions"],
            "blocked": report["blocked"],
            "unlocks_from_completed": report["unlocks_from_completed"],
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    if args.md:
        print(md_report(report, nodes, args.top_next), end="")
        return 0

    print_report(report, nodes, args.top_next)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
