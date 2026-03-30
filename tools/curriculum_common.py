"""
Carregamento e utilitarios do grafo em data/curriculum.json.
Usado por validate_curriculum.py e curriculum_progress.py.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict, deque
from pathlib import Path


def load_graph(path: Path) -> tuple[dict[str, dict], list[tuple[str, str]]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    node_list = raw.get("nodes")
    if not isinstance(node_list, list):
        raise ValueError("Campo 'nodes' deve ser uma lista.")
    ids = [n.get("id") for n in node_list]
    if any(not isinstance(i, str) or not i.strip() for i in ids):
        errors = [i for i in ids if not isinstance(i, str) or not i.strip()]
        raise ValueError(f"Cada no precisa de 'id' string nao vazio. Problemas: {errors!r}")
    dup = [k for k, v in Counter(ids).items() if v > 1]
    if dup:
        raise ValueError(f"IDs duplicados em nodes: {sorted(dup)}")
    nodes = {n["id"]: n for n in node_list}
    edge_list = raw.get("edges")
    if not isinstance(edge_list, list):
        raise ValueError("Campo 'edges' deve ser uma lista.")
    edges: list[tuple[str, str]] = []
    for pair in edge_list:
        if len(pair) != 2:
            raise ValueError(f"Aresta invalida (precisa [from, to]): {pair}")
        edges.append((pair[0], pair[1]))
    seen_pairs: set[tuple[str, str]] = set()
    for u, v in edges:
        if (u, v) in seen_pairs:
            raise ValueError(f"Aresta duplicada: [{u!r}, {v!r}]")
        seen_pairs.add((u, v))
    return nodes, edges


def validate_structure(nodes: dict[str, dict], edges: list[tuple[str, str]]) -> list[str]:
    errors: list[str] = []
    seen_ids = set(nodes.keys())
    for a, b in edges:
        if a not in seen_ids:
            errors.append(f"Aresta origem inexistente: {a!r}")
        if b not in seen_ids:
            errors.append(f"Aresta destino inexistente: {b!r}")
    stages = [n.get("stage") for n in nodes.values()]
    if any(s is None or not isinstance(s, int) for s in stages):
        errors.append("Cada no deve ter 'stage' inteiro.")
    for nid, meta in sorted(nodes.items()):
        inner_id = meta.get("id")
        if inner_id is not None and inner_id != nid:
            errors.append(
                f"No {nid!r}: campo 'id' no objeto ({inner_id!r}) deve coincidir com a chave."
            )
        title = meta.get("title")
        if not isinstance(title, str) or not title.strip():
            errors.append(f"No {nid!r}: campo 'title' deve ser string nao vazia.")
        tags = meta.get("tags")
        if not isinstance(tags, list) or len(tags) == 0:
            errors.append(f"No {nid!r}: campo 'tags' deve ser lista nao vazia.")
        else:
            for i, tag in enumerate(tags):
                if not isinstance(tag, str) or not tag.strip():
                    errors.append(
                        f"No {nid!r}: tags[{i}] deve ser string nao vazia (convencao do repo)."
                    )
    for u, v in edges:
        if u not in seen_ids or v not in seen_ids:
            continue
        su, sv = nodes[u].get("stage"), nodes[v].get("stage")
        if isinstance(su, int) and isinstance(sv, int) and su > sv:
            errors.append(
                f"Aresta com etapa regressiva (pre-requisito depois do dependente): "
                f"{u!r} etapa {su} -> {v!r} etapa {sv}"
            )
    return errors


def collect_graph_warnings(
    nodes: dict[str, dict], edges: list[tuple[str, str]]
) -> list[str]:
    """
    Avisos nao fatais: nos sem qualquer aresta (indegree e outdegree zero).
    Tags/titulos exigentes ficam em validate_structure().
    """
    warnings: list[str] = []
    inc: dict[str, int] = {nid: 0 for nid in nodes}
    out: dict[str, int] = {nid: 0 for nid in nodes}
    for u, v in edges:
        out[u] += 1
        inc[v] += 1
    isolated = sorted(nid for nid in nodes if inc[nid] == 0 and out[nid] == 0)
    if isolated:
        warnings.append(
            "Nos isolados (sem arestas — nao ligam o grafo): " + ", ".join(isolated)
        )
    return warnings


def kahn_topological(
    nodes: dict[str, dict], edges: list[tuple[str, str]]
) -> tuple[list[str], list[str]]:
    indeg: dict[str, int] = {nid: 0 for nid in nodes}
    adj: dict[str, list[str]] = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    q = deque(sorted(nid for nid in nodes if indeg[nid] == 0))
    out: list[str] = []
    while q:
        u = q.popleft()
        out.append(u)
        for v in sorted(adj[u]):
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    leftover = sorted(set(nodes) - set(out))
    return out, leftover


def predecessors(
    nodes: dict[str, dict], edges: list[tuple[str, str]]
) -> dict[str, list[str]]:
    """Para cada no, lista de IDs que sao pre-requisitos diretos."""
    pred: dict[str, list[str]] = {nid: [] for nid in nodes}
    for u, v in edges:
        pred[v].append(u)
    for nid in pred:
        pred[nid].sort()
    return pred


def mermaid(nodes: dict[str, dict], edges: list[tuple[str, str]]) -> str:
    lines = ["flowchart TB"]
    for nid in sorted(nodes.keys()):
        label = str(nodes[nid].get("title", "")).replace('"', "'")
        lines.append(f'  {nid}["{label}"]')
    for u, v in edges:
        lines.append(f"  {u} --> {v}")
    return "\n".join(lines)
