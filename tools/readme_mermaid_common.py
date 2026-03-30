"""
Extracao e analise do bloco Mermaid do README (partilhado entre validadores).
"""
from __future__ import annotations

import json
import re
from pathlib import Path


def extract_mermaid_block(readme: Path) -> str:
    text = readme.read_text(encoding="utf-8")
    start = text.find("```mermaid")
    if start < 0:
        raise ValueError(f"Nenhum bloco ```mermaid em {readme}")
    start = text.find("\n", start) + 1
    end = text.find("```", start)
    if end < 0:
        raise ValueError(f"Bloco mermaid nao fechado em {readme}")
    return text[start:end]


def analyze_mermaid(body: str) -> tuple[set[str], set[tuple[str, str]], list[str]]:
    """Devolve (definicoes, arestas, erros)."""
    defs: set[str] = set()
    edges: set[tuple[str, str]] = set()
    errors: list[str] = []

    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("%%"):
            continue
        if line == "end":
            continue

        m = re.match(r"^subgraph\s+(\w+)\s*\[", line)
        if m:
            defs.add(m.group(1))
            continue

        if re.match(r"^(flowchart|graph)\s", line):
            continue

        m = re.match(r"^(\w+)\s*\[", line)
        if m:
            defs.add(m.group(1))
            continue

        # Multiplas arestas na mesma linha: A --> B & C --> D
        for segment in re.split(r"\s*&\s*", line):
            segment = segment.strip()
            if not segment:
                continue
            for a, b in re.findall(r"(\w+)\s*-->\s*(\w+)", segment):
                edges.add((a, b))
            for a, b in re.findall(r"(\w+)\s*-\.->\s*(\w+)", segment):
                edges.add((a, b))

    for a, b in sorted(edges):
        if a not in defs:
            errors.append(f"Aresta {a} --> {b}: origem {a!r} nao definida (falta no[...] ou subgraph).")
        if b not in defs:
            errors.append(f"Aresta {a} --> {b}: destino {b!r} nao definido.")

    return defs, edges, errors


def subgraph_ids(body: str) -> set[str]:
    """IDs declarados em `subgraph NOME [...]` (containers, nao nos de disciplina)."""
    return set(re.findall(r"(?m)^\s*subgraph\s+(\w+)\s*\[", body))


def diagram_node_ids(defs: set[str], subgraphs: set[str]) -> set[str]:
    """IDs de nos `X[label]` = defs menos identificadores de subgraph."""
    return defs - subgraphs


def load_mermaid_node_map(path: Path) -> dict[str, str]:
    """Carrega data/readme_mermaid_map.json (chaves curtas -> id do curriculum)."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    nodes = raw.get("nodes")
    if not isinstance(nodes, dict):
        raise ValueError(f"{path.name}: campo 'nodes' deve ser um objeto.")
    out: dict[str, str] = {}
    for k, v in nodes.items():
        if not isinstance(k, str) or not isinstance(v, str):
            raise ValueError(f"Mapeamento invalido: {k!r} -> {v!r}")
        out[k] = v
    return out
