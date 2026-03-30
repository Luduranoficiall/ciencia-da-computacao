# Ferramentas Python (`tools/`)

| Script | Função |
|--------|--------|
| [`validate_data_schemas.py`](validate_data_schemas.py) | JSON Schema sobre `data/*.json` (requer `requirements-dev.txt`) |
| [`resolve_python.sh`](resolve_python.sh) | Escolhe `.venv/bin/python` ou `python3` com `jsonschema` |
| [`validate_curriculum.py`](validate_curriculum.py) | DAG, estrutura, `--topo`, `--mermaid`, `--strict` |
| [`curriculum_progress.py`](curriculum_progress.py) | Progresso vs grafo (`--json`, `--md`, `--validate`) |
| [`check_readme_mermaid.py`](check_readme_mermaid.py) | Nós do bloco Mermaid do README definidos |
| [`check_mermaid_curriculum_sync.py`](check_mermaid_curriculum_sync.py) | Mapa + arestas Mermaid = `curriculum.json` |
| [`mermaid_diagram_coverage.py`](mermaid_diagram_coverage.py) | Lista omit vs disciplinas fora do diagrama; `--report`, `--json` |
| [`check_exercicios_semester.py`](check_exercicios_semester.py) | Cabeçalhos em `docs/exercicios-por-disciplina.md` com `sem. **SN**` alinhados a `graduacao-4-anos.md` (`validate_exercicios_semesters` para testes) |
| [`curriculum_common.py`](curriculum_common.py) | Carga do grafo, Kahn, validações partilhadas |
| [`readme_mermaid_common.py`](readme_mermaid_common.py) | Parser Mermaid + `load_mermaid_node_map` |
| [`repo_paths.py`](repo_paths.py) | `repo_root()` |

Verificação local alinhada ao CI: [`verify_repo.sh`](verify_repo.sh) (primeiro schemas, depois grafo).

**Setup:** `python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt` (na raiz do repo). Em sistemas com PEP 668, use sempre venv para instalar `jsonschema`.

**Pre-commit (opcional):** `pip install pre-commit && pre-commit install` — vê [`.pre-commit-config.yaml`](../.pre-commit-config.yaml).
