# Progresso automático contra o grafo

O ficheiro [`data/curriculum.json`](../data/curriculum.json) define **disciplinas** e **pré-requisitos**. O ficheiro [`data/progress.json`](../data/progress.json) lista os **IDs que você já concluiu** (prova de nível fechada, na sua honestidade).

O script **`tools/curriculum_progress.py`** cruza os dois e responde:

1. **Prontas para iniciar** — todos os pré-requisitos já estão em `completed`.
2. **Sugestões** — entre as prontas, uma ordenação por **quantos filhos ainda pendentes** cada disciplina tem no grafo (impacto direto), com desempate por etapa e ID.
3. **Bloqueadas** — falta qual pré-requisito (por exemplo: `calc3` bloqueada por `calc2`).
4. **Desbloqueios** — cada ID concluído e que arestas saem dele para disciplinas ainda pendentes.

Isto **não** substitui o [checklist.md](../checklist.md) linha a linha; é uma **vista de dependências** alinhada ao JSON. O checklist continua a ser a lista humana detalhada.

---

## Formato de `progress.json`

```json
{
  "version": 1,
  "completed": ["discreta", "prog1", "geo"]
}
```

Os **IDs** são exatamente os do `curriculum.json` (`discreta`, `calc1`, `ed`, …).

---

## Comandos

Na raiz do repositório:

```bash
# Relatorio legivel
python3 tools/curriculum_progress.py

# Saida JSON (para ferramentas; inclui lista completa `suggestions` ordenada)
python3 tools/curriculum_progress.py --json

# Relatorio em Markdown (redirecione para ficheiro se quiser)
python3 tools/curriculum_progress.py --md
python3 tools/curriculum_progress.py --md --top-next 8

# So validar que todos os IDs existem (usado no CI)
python3 tools/curriculum_progress.py --validate

# Progresso alternativo (ex.: copia local nao commitada)
python3 tools/curriculum_progress.py --progress data/progress.local.json
```

Exemplo com dados de demonstração:

```bash
python3 tools/curriculum_progress.py --progress data/progress.example.json
```

---

## Ficheiro local não commitado

Se não quiser commitar o seu `progress.json`, use `data/progress.local.json` (está no [`.gitignore`](../.gitignore)) e o flag `--progress`.

---

## Relação com o validador do grafo

- `python3 tools/validate_curriculum.py` — garante que o **curriculum** é um DAG coerente.
- `python3 tools/curriculum_progress.py --validate` — garante que **progress** só referencia IDs válidos.

Ambos correm no workflow **Curriculum data** quando alteras `data/` ou `tools/curriculum_*`.

---

## Código partilhado

[`tools/curriculum_common.py`](../tools/curriculum_common.py) — carregamento do JSON, pré-requisitos, ordenação topológica — é usado pelo validador e pelo analisador de progresso.
