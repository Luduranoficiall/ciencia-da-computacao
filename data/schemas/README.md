# JSON Schema (`data/schemas/`)

Ficheiros de [JSON Schema (draft 2020-12)](https://json-schema.org/) usados por [`tools/validate_data_schemas.py`](../tools/validate_data_schemas.py) antes das validações lógicas do grafo.

| Schema | Dados |
|--------|--------|
| `curriculum.schema.json` | `data/curriculum.json` |
| `progress.schema.json` | `data/progress.json` |
| `readme_mermaid_map.schema.json` | `data/readme_mermaid_map.json` |
| `readme_mermaid_diagram_omit.schema.json` | `data/readme_mermaid_diagram_omit.json` |
| `course_presentation.schema.json` | `data/course_presentation.json` (textos da landing / oferta formativa; validado no CI) |

Dependência: `pip install -r requirements-dev.txt` (pacote `jsonschema`).
