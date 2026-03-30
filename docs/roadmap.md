# Roadmap (ideias)

Lista **não comprometida** — prioridades mudam com tempo e contribuições. Para contribuir já, veja [CONTRIBUTING.md](../CONTRIBUTING.md).

## Currículo e conteúdo

- [x] Plano **graduação 4 anos** (8 semestres): [`graduacao-4-anos.md`](graduacao-4-anos.md).
- [x] Banco de exercícios com **semestre sugerido (S1–S8)** + **Etapa 8** (capstone e trilhas) + verificação em [`tools/check_exercicios_semester.py`](../tools/check_exercicios_semester.py) e testes [`tools/test_exercicios_semester.py`](../tools/test_exercicios_semester.py).
- [x] FAQ: conflito **calendário vs grafo** e papel do `verify_repo.sh` — [FAQ.md](../FAQ.md).
- [ ] Revisar periodicamente links da UBL e espelhos se playlists mudarem.
- [x] Guia por tema com recursos e provas: [`extras/modulos-elevados.md`](../extras/modulos-elevados.md).
- [x] Ficheiro [`glossario.md`](glossario.md) com termos PT/EN mais usados na grade.

## Mídia e acessibilidade

- [x] Diagrama SVG **ciclo de uma semana** — [`../assets/ciclo-semana-estudo.svg`](../assets/ciclo-semana-estudo.svg) (+ PNG na mesma pasta).
- [x] Mapa SVG **só de matematica** — [`../assets/mapa-matematica.svg`](../assets/mapa-matematica.svg).
- [x] SVG com `<?xml … UTF-8?>`, `<title>` e `<desc>` revisados nos cinco ficheiros em `assets/` (texto visível corrigido onde estava corrompido).
- [x] Visao geral em ingles: [`README.en.md`](../README.en.md) (curriculo detalhado permanece em PT no `README.md`).

## Automação e repo

- [x] Grafo formal em [`data/curriculum.json`](../data/curriculum.json) + validador [`tools/validate_curriculum.py`](../tools/validate_curriculum.py) + CI `curriculum-data.yml` (inclui `docs/exercicios-por-disciplina.md` e `docs/graduacao-4-anos.md` nos gatilhos).
- [x] [`data/progress.json`](../data/progress.json) + [`tools/curriculum_progress.py`](../tools/curriculum_progress.py) (bloqueios / prontas / sugestões por impacto / `--json` / `--md`) + doc [`curriculum-progresso.md`](curriculum-progresso.md).
- [ ] Se o repositório crescer: [pre-commit](https://pre-commit.com/) só para `markdownlint` ou formatação de tabelas (local, opcional).
- [ ] Avaliar **Renovate** em paralelo ao Dependabot só se a gestão de PRs de Actions ficar pesada (hoje não é necessário).

## Comunidade

- [ ] Etiquetar issues “aceita PR” quando a direção estiver clara.
- [ ] Sincronizar com melhorias relevantes do upstream [UBL](https://github.com/Universidade-Livre/ciencia-da-computacao) sem perder o foco “trilha potente”.

---

*Última revisão de estrutura: março de 2026. Apague itens feitos ou mova para issues fechadas com referência.*
