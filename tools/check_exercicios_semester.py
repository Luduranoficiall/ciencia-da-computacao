#!/usr/bin/env python3
"""Garante que docs/exercicios-por-disciplina.md marca semestre sugerido (S1-S8) por ID.

O mapa deve bater com docs/graduacao-4-anos.md; o grafo continua canónico em data/curriculum.json.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "exercicios-por-disciplina.md"
CURRICULUM = ROOT / "data" / "curriculum.json"

# Alinhado a docs/graduacao-4-anos.md (secção "Uma página: onde está cada ID").
SEMESTER_BY_ID: dict[str, int] = {
    "discreta": 1,
    "circuitos": 1,
    "ling_prog": 1,
    "prog1": 1,
    "geo": 1,
    "calc1": 2,
    "alg_lin1": 2,
    "ed": 2,
    "prog2": 2,
    "oo": 2,
    "grafos": 3,
    "arq1": 3,
    "prob_est": 3,
    "calc2": 3,
    "funcional": 3,
    "met_num": 3,
    "teo_grafos": 3,
    "analise_alg": 4,
    "bd": 4,
    "arq2": 4,
    "prog_logica": 4,
    "calc3": 4,
    "redes": 5,
    "eng_sw": 5,
    "so": 5,
    "prog_mat": 5,
    "comp_grafica": 5,
    "automatos": 6,
    "ia": 6,
    "dist": 6,
    "teo_comp": 7,
    "dl": 7,
    "compiladores": 7,
    "quantica": 7,
    "met_pesquisa": 8,
}

HEADING_RE = re.compile(
    r"^### .+ \(`(?P<id>[a-z0-9_]+)`\)\s*—\s*sem\.\s*\*\*S(?P<s>\d)\*\*"
)


def validate_exercicios_semesters(
    doc_text: str,
    *,
    curriculum_ids: set[str],
    semester_by_id: dict[str, int],
    doc_label: str,
) -> list[str]:
    """Devolve lista de mensagens de erro; vazia se tudo OK."""
    errors: list[str] = []
    lines = doc_text.splitlines()

    by_cid: dict[str, list[int]] = defaultdict(list)
    for i, line in enumerate(lines, 1):
        if not line.startswith("### "):
            continue
        id_m = re.search(r"\(`([a-z0-9_]+)`\)", line)
        if not id_m:
            continue
        cid = id_m.group(1)
        if cid not in curriculum_ids:
            errors.append(
                f"{doc_label}:{i}: ID `{cid}` em cabeçalho não existe em curriculum.json "
                "(use título sem (`id`) para secções fora do grafo, ex.: capstone)."
            )
            continue
        by_cid[cid].append(i)

    for cid, line_nos in sorted(by_cid.items()):
        first = line_nos[0]
        for dup in line_nos[1:]:
            errors.append(
                f"{doc_label}:{dup}: secção duplicada para `{cid}` (primeira ocorrência: linha {first})"
            )
        line = lines[first - 1]
        m = HEADING_RE.match(line)
        if not m:
            errors.append(f"{doc_label}:{first}: cabeçalho com (`{cid}`) sem '— sem. **SN**' canónico")
            continue
        got = int(m.group("s"))
        exp = semester_by_id.get(cid)
        if exp is None:
            errors.append(f"{doc_label}:{first}: ID `{cid}` sem entrada em semester_by_id (ferramenta)")
            continue
        if got != exp:
            errors.append(
                f"{doc_label}:{first}: `{cid}` semestre **S{got}** no doc, esperado **S{exp}** (graduacao-4-anos)"
            )

    for cid in sorted(curriculum_ids - set(by_cid.keys())):
        errors.append(
            f"disciplina `{cid}` em curriculum.json sem secção em {doc_label} (cabeçalho ### ... (`{cid}`))"
        )

    return errors


def run_check(
    doc_path: Path = DOC,
    curriculum_path: Path = CURRICULUM,
    semester_by_id: dict[str, int] | None = None,
) -> int:
    semester_by_id = semester_by_id or SEMESTER_BY_ID
    data = json.loads(curriculum_path.read_text(encoding="utf-8"))
    curriculum_ids = {c["id"] for c in data["nodes"]}

    unknown_in_map = set(semester_by_id) - curriculum_ids
    if unknown_in_map:
        print("check_exercicios_semester: IDs no mapa que não existem no curriculum:", file=sys.stderr)
        for x in sorted(unknown_in_map):
            print(f"  {x}", file=sys.stderr)
        return 1

    doc_text = doc_path.read_text(encoding="utf-8")
    errors = validate_exercicios_semesters(
        doc_text,
        curriculum_ids=curriculum_ids,
        semester_by_id=semester_by_id,
        doc_label=doc_path.name,
    )

    if errors:
        print("check_exercicios_semester: falhou", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    print("OK: exercicios-por-disciplina.md e mapa S1-S8 alinhados ao curriculum.")
    return 0


def main() -> int:
    return run_check()


if __name__ == "__main__":
    raise SystemExit(main())
