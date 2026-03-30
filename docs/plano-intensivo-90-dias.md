# Plano intensivo — 90 dias (alta carga)

Este documento é **voluntariamente agressivo**: pressupõe que você já aceitou **risco de fadiga**, tem **blocos de tempo protegidos** e sabe pedir ajuda. Não substitui [README.md](../README.md), [checklist.md](../checklist.md) nem a sua vida. Se algo falhar, use a secção **Degradação** no fim.

**Referência de carga:** “intensivo” aqui aponta para **~50–70 h/semana** de trabalho profundo (estudo + implementação + escrita). Ajuste para baixo se tiver emprego em tempo integral ou responsabilidades de cuidado.

---

## Princípios operacionais

1. **Uma prova de nível por semana** (mínimo) — algo que possa mostrar em repositório ou texto público.
2. **Duas trilhas em paralelo** sempre: **(A) matéria nova** + **(B) manutenção** (revisão espaçada, consertar dívida de exercícios, CI verde).
3. **Nenhuma semana sem código** — mesmo que seja 3 h num script pequeno.
4. **Sexta é buffer** — se a semana desmoronar, salva-se o mínimo na sexta; não empilhe culpa para o fim do plano.

---

## Mapa rápido: 90 dias ≈ 13 semanas

| Semana | Foco A (novo) | Foco B (manutenção) | Horas alvo | Entregável mínimo |
|--------|---------------|---------------------|------------|-------------------|
| 0 (dias 1–7) | Pré-voo + Git + terminal | Rotina de sono e calendário | 25–35 | Repositório de estudos com `.editorconfig` + 3 commits significativos |
| 1 | Discreta (início forte) + Prog I | Notas ligadas por conceito | 50–60 | 3 algoritmos da discreta em código + 5 exercícios Prog I |
| 2 | Discreta (fecho) + Circuitos | Revisão Prog I | 55–65 | Simulação somador + MUX + 1 CLI com testes |
| 3 | Geometria + início Cálculo I | Zettelkasten / flashcards | 55–65 | Vetores em código + derivada aplicada a modelo simples |
| 4 | Cálculo I (ritmo) + **ED** (abertura) | CI a verde no repo de estudos | 60–70 | Início ED: fila + heap **com testes** |
| 5 | **ED** (fecho) + Álgebra linear | Revisão cálculo | 60–70 | BST + multiplicação de matrizes + visual 2D |
| 6 | Prog II + OO | Refatorar projeto médio | 60–70 | Domínio OO com testes + módulos |
| 7 | **Recuperação** | Fechar buracos; nada de matéria nova pesada | 30–40 | Documento “o que falhei e por quê” + ajuste do plano |
| 8 | Grafos + Arq I | Competitive programming leve | 60–70 | DFS/BFS/Dijkstra + 1 problema + experimento cache |
| 9 | Prob/Est + Cálculo II | Monte Carlo + integral numérica | 60–70 | Simulação + verificação numérica documentada |
| 10 | Funcional + Análise (abertura) | Revisão grafos | 60–70 | Parser minúsculo + 1 prova de limites + implementação |
| 11 | BD + Arq II + Redes (abertura) | Migrations + microbenchmark | 65–75 | Esquema normalizado + captura Wireshark mínima |
| 12 | SO + Eng. SW | OWASP Top 10 leitura | 65–75 | Deadlock proposital + correção + diagrama de contexto |
| 13 | **Integração** | Portfólio + 1 texto longo | 40–50 | README de “trimestre” com links para todas as provas |

Semanas 7 e 13 são **válvulas de escape**. Sem elas, planos intensivos tendem a colapsar silenciosamente.

---

## Cruzamento com as 7 etapas do README

Este plano de 90 dias **não completa** a graduação — cobre aproximadamente **etapas 1–5** com compressão brutal, assumindo que você já domina parte do pré-voo ou aceita atrasar tópicos (ex.: linguagens formais, IA, teoria profunda) para **ciclo seguinte**.

| Etapa README | Cobertura aproximada no plano |
|--------------|------------------------------|
| 1 | Semanas 0–3 |
| 2 | Semanas 4–6 |
| 3 | Semanas 8–9 (+ funcional na 10) |
| 4 | Semanas 10–11 |
| 5 | Semana 12 (SO, ES, redes parcial) |

**O que fica de fora de propósito em 90 dias:** autômatos completos, IA/ML profundo, compiladores, cálculo III, teoria da computação, DL — tratados como **fase 2** (outro bloco de 90 dias).

---

## Ritmo diário sugerido (dias úteis)

| Bloco | Duração | Conteúdo típico |
|-------|---------|-----------------|
| Manhã 1 | 90–120 min | Teoria nova (vídeo/leitura ativa) |
| Manhã 2 | 60–90 min | Exercícios difíceis ou implementação |
| Tarde 1 | 90 min | Projeto / prova de nível |
| Tarde 2 | 45 min | Revisão espaçada (ontem, semana passada) |
| Noite | 0–45 min | Opcional: leitura leve ou desligar |

**Fim de semana:** um dia com **4–6 h** (projeto ou recuperação); outro com **descanso real**.

---

## Sinais de alerta (pare ou degrade)

- Dormir mal **3+ noites** seguidas por culpa de estudo.
- Parar de abrir o repositório **5 dias** seguidos.
- Estudar só vídeo **duas semanas** sem commit.

Ação: ativar **Degradação** abaixo na mesma semana.

---

## Degradação (como salvar o plano)

1. Cortar **25%** das horas e **uma** coluna de “foco A” por semana.
2. Manter **só** prova de nível mínima + **uma** trilha (ex.: só código, matemática em modo manutenção).
3. Estender o horizonte: estes 90 dias viram **120 dias** com as mesmas metas.

---

## Ferramentas de verificação

- [checklist.md](../checklist.md) — marcar caixas com honestidade.
- [data/curriculum.json](../data/curriculum.json) + `python3 tools/validate_curriculum.py --topo` — ver dependências formais (não é ordem pedagógica ótima, é **consistência** do grafo).

---

*Documento vivo: ajuste datas e cargas ao seu contexto; o objetivo é exigência com sustentabilidade, não heroísmo.*
