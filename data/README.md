# Dados do currículo

| Ficheiro | Conteúdo |
|----------|----------|
| [curriculum.json](curriculum.json) | Nós (disciplinas), `stage`, `tags`, arestas `pré-requisito → disciplina`. Deve ser um **DAG** (sem ciclos). Versão atual do ficheiro: campo `version` (ex.: 2). |
| [readme_mermaid_map.json](readme_mermaid_map.json) | Mapa **bijectivo** com os nos do diagrama: `ID curto → id` do curriculum; cada disciplina aparece uma vez (`check_mermaid_curriculum_sync.py`). |
| [readme_mermaid_diagram_omit.json](readme_mermaid_diagram_omit.json) | Lista fechada de disciplinas **só no grafo completo**, fora do Mermaid resumido; tem de bater certo com o diff real (`mermaid_diagram_coverage.py`). |
| [progress.json](progress.json) | IDs concluídos (`completed`). Pode ficar vazio `[]` no repo; use `progress.local.json` para estado pessoal (gitignore). |
| [progress.example.json](progress.example.json) | Exemplo para testar o analisador de bloqueios. |
| [course_presentation.json](course_presentation.json) | Textos da página pública do curso (trimestres, microcertificados, parceiros, alinhamento com a plataforma). JSON Schema: [schemas/course_presentation.schema.json](schemas/course_presentation.schema.json). |

Índice das ferramentas: [../tools/README.md](../tools/README.md). **JSON Schema** dos dados: [schemas/README.md](schemas/README.md). Dependência: [../requirements-dev.txt](../requirements-dev.txt).

Validação e grafo:

```bash
python3 tools/validate_curriculum.py
python3 tools/validate_curriculum.py --strict   # falha se houver avisos (nos isolados, tags em falta)
python3 tools/check_readme_mermaid.py           # nos do diagrama Mermaid do README sem fantasma
python3 tools/check_mermaid_curriculum_sync.py # cada aresta Mermaid existe no curriculum.json
python3 tools/mermaid_diagram_coverage.py      # omit list == disciplinas fora do diagrama
python3 tools/mermaid_diagram_coverage.py --report  # relatorio Markdown (stdout)
python3 tools/validate_curriculum.py --topo
python3 tools/validate_curriculum.py --mermaid
```

Progresso (o que falta para desbloquear cada disciplina):

```bash
python3 tools/curriculum_progress.py
python3 tools/curriculum_progress.py --json
python3 tools/curriculum_progress.py --md
python3 tools/curriculum_progress.py --validate
```

Guia: [docs/curriculum-progresso.md](../docs/curriculum-progresso.md).

O workflow **Curriculum data** no GitHub corre validação + `--validate` do progresso quando estes ficheiros mudam.
