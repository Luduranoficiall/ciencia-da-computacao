# Perguntas frequentes

Respostas curtas sobre **este repositório** (trilha potente + estrutura). Para a grade de vídeos da [Universidade Livre](https://github.com/Universidade-Livre/ciencia-da-computacao), use também o repositório e o Telegram deles.

---

## Este curso substitui uma faculdade?

Não oficialmente. O objetivo é **aproximar** o que se espera de um bacharelado em Ciência da Computação, usando materiais abertos e **provas de nível** que você executa e documenta. Diploma e validação formal dependem de IES ou processos que você buscar por fora.

---

## Por onde começo se já sei programar?

1. Leia o [README](README.md) e marque o [checklist](checklist.md).
2. **Não pule** discreta, circuitos e geometria se ainda não domina — elas pagam depois em ED, arquitetura e teoria.
3. Faça a **prova de nível** das matérias que achar fáceis rapidamente (para “destravar” o checklist) e use o tempo ganho nos buracos reais (muitas vezes matemática ou sistemas).

---

## Quantas horas por semana?

Depende da sua vida e do prazo. Como referência **grosseira**: quem quiser ritmo próximo a graduação em tempo integral costuma pensar em **40+ h/semana** de estudo profundo; em meio período, **15–25 h** já exige anos de calendário. O importante é **consistência** e o ciclo estudar → implementar → explicar → medir.

---

## Posso mudar a ordem das matérias?

Sim, desde que respeite **pré-requisitos** (veja o diagrama Mermaid e o SVG de dependências no README). Pular base costuma gerar buraco que aparece em compiladores, probabilidade ou sistemas.

---

## Plano em 4 anos (S1–S8) vs grafo em JSON — o que manda?

O ficheiro [`data/curriculum.json`](data/curriculum.json) define **só** as dependências (o que bloqueia o quê). O guia [docs/graduacao-4-anos.md](docs/graduacao-4-anos.md) e os **semestres sugeridos** em [docs/exercicios-por-disciplina.md](docs/exercicios-por-disciplina.md) são **orientação de calendário**; se o texto sugerir uma ordem impossível no grafo, **prevalece o JSON**. Para ver bloqueios com o teu progresso: `python3 tools/curriculum_progress.py` e [docs/curriculum-progresso.md](docs/curriculum-progresso.md).

---

## O que o `verify_repo.sh` verifica além do grafo?

`bash tools/verify_repo.sh` corre JSON Schema sobre `data/`, valida o DAG, sincronismo Mermaid ↔ `curriculum.json`, **cabeçalhos de exercícios com semestre S1–S8** (`tools/check_exercicios_semester.py`) e testes em `tools/`. É o mesmo tipo de verificação que o CI principal do currículo usa.

---

## Onde estão os vídeos?

Neste repo a ênfase é **currículo + engenharia + checklist**. Links de playlists em massa continuam excelentes no repositório da UBL; aqui há o guia [extras/cursos-referencia-ubl.md](extras/cursos-referencia-ubl.md).

---

## Como registro meu progresso?

- Marque o [checklist.md](checklist.md) (no seu fork ou numa cópia).
- Use o [template de repositório de estudos](templates/repositorio-de-estudos/) com um `README` por disciplina.

---

## Por que “prova de nível”?

Para evitar **ilusão de competência** só com vídeo. Cada item sugere algo **verificável** (código, experimento, texto). Você adapta ao seu contexto, mas mantém o critério “outra pessoa (ou eu no mês que vem) consegue ver o resultado”.

---

## E se eu travar numa matéria?

- Reduza o escopo: um capítulo, um exercício, um algoritmo.
- Escreva o que não entendeu em **uma pergunta específica** (ótimo para comunidade ou tutor).
- Volte aos pré-requisitos listados na tabela da etapa.

---

## Posso contribuir com este repositório?

Sim. Veja [CONTRIBUTING.md](CONTRIBUTING.md) e o [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Correções de link e typos são muito bem-vindas.

---

## Licença do meu código de estudos?

O que **você** escreve é seu; escolha a licença do seu repositório. O **texto estrutural** deste currículo está sob [LICENSE](LICENSE) (MIT). Cursos e livros de terceiros têm **suas próprias** licenças e regras.

---

## Como reporto um problema de segurança?

Leia [SECURITY.md](SECURITY.md) (escopo, o que não é responsabilidade deste repo e canais de reporte).

---

## Onde peço ajuda com a trilha ou com um curso?

Neste projeto: [SUPPORT.md](SUPPORT.md) (FAQ, issues, links para a comunidade da [UBL](https://github.com/Universidade-Livre/ciencia-da-computacao)).

---

## Como exijo que o CI de links passe antes de dar merge?

Isto configura-se no GitHub (**rulesets** ou **branch protection**), não neste repositório. Resumo e links oficiais: secção **Rulesets e proteção de `main`** em [CONTRIBUTING.md](CONTRIBUTING.md). Lembre do filtro `paths` do workflow de links: PRs que só alteram ficheiros fora de `**/*.md` podem não disparar esse job.

---

## O badge de “Links” no README fica cinza ou quebrado

Isso costuma acontecer antes do primeiro run do Actions ou se o repositório no GitHub **não** for `luduranoficiall/ciencia-da-computacao`. Edite as duas URLs do badge no topo do [README](README.md) para o seu `usuario/repositorio`.

---

## Ainda tenho dúvida

Abra uma issue com o modelo **Dúvida** em `.github/ISSUE_TEMPLATE/` ou procure primeiro por issues fechadas com palavras-chave parecidas.
