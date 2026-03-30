# Contribuindo

Obrigado por considerar melhorar este repositório. Ele é um **guia curricular** (texto, listas e links), não um pacote de software.

Dúvidas de uso costumam estar no [FAQ.md](FAQ.md). Issues e PRs usam os modelos em [`.github/`](.github/). Papéis e prioridades de quem mantém o repo: [MAINTAINERS.md](MAINTAINERS.md).

Índice das ferramentas: [tools/README.md](tools/README.md). **JSON Schema** em [data/schemas/](data/schemas/) + [requirements-dev.txt](requirements-dev.txt) (`jsonschema`): [tools/validate_data_schemas.py](tools/validate_data_schemas.py) corre antes do resto em [tools/verify_repo.sh](tools/verify_repo.sh). Setup local sugerido: `python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt`. **Pre-commit** opcional: [`.pre-commit-config.yaml`](.pre-commit-config.yaml). O grafo em [data/curriculum.json](data/curriculum.json) é validado por [tools/validate_curriculum.py](tools/validate_curriculum.py) (DAG sem ciclos; `--strict` inclui convenções). O diagrama Mermaid resumido no [README.md](README.md) é verificado por [tools/check_readme_mermaid.py](tools/check_readme_mermaid.py) (cada `A --> B` exige `A` e `B` definidos) e por [tools/check_mermaid_curriculum_sync.py](tools/check_mermaid_curriculum_sync.py): o mapa [data/readme_mermaid_map.json](data/readme_mermaid_map.json) deve ter **exatamente** um par por cada `no[...]` do diagrama (exceto subgraphs), **sem** `id` de curriculum repetido no mapa, e cada aresta do diagrama deve existir no [data/curriculum.json](data/curriculum.json). As disciplinas que **não** entram no diagrama resumido devem estar listadas em [data/readme_mermaid_diagram_omit.json](data/readme_mermaid_diagram_omit.json) — [tools/mermaid_diagram_coverage.py](tools/mermaid_diagram_coverage.py) confere que essa lista coincide com o conjunto real de “só no grafo completo” (ao mudar a grade, atualize o mapa **ou** o omit). O ficheiro [docs/exercicios-por-disciplina.md](docs/exercicios-por-disciplina.md) deve ter **um** cabeçalho `### … (`id`) — sem. **SN**` por disciplina do grafo, com **N** alinhado a [docs/graduacao-4-anos.md](docs/graduacao-4-anos.md) — [tools/check_exercicios_semester.py](tools/check_exercicios_semester.py) (`verify_repo.sh`). O progresso em [data/progress.json](data/progress.json) é validado por [tools/curriculum_progress.py](tools/curriculum_progress.py) (`--validate`: IDs existentes). Código partilhado: [tools/curriculum_common.py](tools/curriculum_common.py). O workflow [`.github/workflows/curriculum-data.yml`](.github/workflows/curriculum-data.yml) corre validações e testes quando `data/`, `README.md` ou esses scripts mudam. Guia: [docs/curriculum-progresso.md](docs/curriculum-progresso.md). Verificação local rápida: `tools/verify_repo.sh`.

O [Dependabot](https://docs.github.com/code-security/dependabot) está configurado em [`.github/dependabot.yml`](.github/dependabot.yml) para **atualizar Actions** (`github-actions`) em grupo, com checagem **mensal**.

O workflow [`.github/workflows/stale.yml`](.github/workflows/stale.yml) ([actions/stale](https://github.com/actions/stale)) rotula issues (**120** dias) e PRs (**60** dias) sem atividade com a label **`stale`**; **não fecha** itens (`days-before-*-close: -1`). Issues com **`good first issue`** e PRs em *draft* ficam isentos conforme o YAML.

**Labels:** definições em [`.github/labels.yml`](.github/labels.yml). Após empurrar para o GitHub, o workflow [`.github/workflows/sync-labels.yml`](.github/workflows/sync-labels.yml) atualiza as labels do repositório (também pode rodar manualmente em **Actions → Sync labels**). Isso alinha os nomes usados nos [templates de issue](.github/ISSUE_TEMPLATE/).

O ficheiro [`.github/CODEOWNERS`](.github/CODEOWNERS) sugere **revisor padrão** em PRs (ajuste o `@` ao seu utilizador GitHub; nas definições do repositório pode exigir aprovação de *code owners*, se quiser).

Em `push`/`pull_request` para `main` ou `master`, o workflow [`.github/workflows/links.yml`](.github/workflows/links.yml) **só corre** quando mudam `**/*.md`, o próprio `links.yml` ou [`.lycheeignore`](.lycheeignore) (poupa minutos em commits só com PNG/SVG, etc.). O **cron semanal** e **`workflow_dispatch`** continuam a verificar tudo.

Esse workflow faz duas checagens: (1) [Lychee](https://github.com/lycheeverse/lychee) em todos os `.md`, com **`--require-https`**; (2) existência de **destinos relativos** no disco. Padrões ignorados: [`.lycheeignore`](.lycheeignore).

## Rulesets e proteção de `main` (opcional)

Quem mantém o repositório no GitHub pode **exigir PR** para a branch padrão, **checks obrigatórios** (ex.: workflow *Links (Markdown)* a verde) e, em conjunto com [`.github/CODEOWNERS`](.github/CODEOWNERS), **revisão de code owners**.

- **Rulesets** (recomendado hoje pela GitHub): [Sobre rulesets](https://docs.github.com/pt/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets).
- **Regras de branch clássicas** (alternativa): [Sobre branches protegidas](https://docs.github.com/pt/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).

Sugestão para um repo só de documentação: *Require a pull request before merging*; *Require status checks* com o job de links (atenção ao filtro `paths`: um PR que só mexe em PNG não dispara o workflow — nesse caso o merge pode não exigir esse check, ou corre-se *workflow_dispatch* antes do merge).

## O que ajuda

- Corrigir links quebrados, typos e formatação.
- Sugerir **recursos abertos** de qualidade (com licença e contexto claros).
- Ampliar bibliografia ou especializações com **curadoria**: por que esse recurso entra, para quem serve.
- Issues descrevendo lacunas (ex.: “falta trilha em X com pré-requisitos Y”).

## O que evitar

- Copiar blocos grandes de outros README sem atribuição e sem adicionar valor.
- Incluir material que viole direitos autorais ou regras de plataformas de curso.
- Spam, autopromoção sem relevência ou links afiliados disfarçados.

## Processo

1. Abra uma **issue** para mudanças grandes (nova trilha, reorganização da grade).
2. Para ajustes pequenos, um **pull request** direto costuma bastar.
3. Mantenha o tom: **português claro**, frases objetivas, tabelas quando fizer sentido.

## Conduta

Este projeto adota o [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) (baseado no Contributor Covenant). Trate colaboradores e leitores com respeito; discordância técnica é bem-vinda, hostilidade não.

## Licença

Ao contribuir, você concorda que o conteúdo novo neste repositório seja licenciado sob os termos do [LICENSE](LICENSE).
