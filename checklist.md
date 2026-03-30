# Checklist de progresso

Use este arquivo para acompanhar a trilha do [README](README.md). **Organização em 4 anos (semestres):** [docs/graduacao-4-anos.md](docs/graduacao-4-anos.md). No GitHub, marque com `x` dentro dos colchetes (`[x]`). Pode duplicar o arquivo para o seu fork e ir commitando conquistas.

Para uma **vista automática de bloqueios** (o que falta antes de cada disciplina no grafo), mantenha [data/progress.json](data/progress.json) com os IDs concluídos e rode `python3 tools/curriculum_progress.py` — ver [docs/curriculum-progresso.md](docs/curriculum-progresso.md).

**Regra:** em cada etapa, cumpra **pelo menos uma** “prova de nível” por disciplina (ou o equivalente que você documentou no seu repositório de estudos).

**Exercícios ampliados (teoria + código + tempo estimado):** [docs/exercicios-por-disciplina.md](docs/exercicios-por-disciplina.md).

---

## Pré-voo (semanas 1–4)

- [ ] Curso ou material de **aprender a aprender** + rotina fixa definida
- [ ] Sistema de **notas** (Zettelkasten ou similar) em uso
- [ ] **Git**: branch, merge/rebase, PR ou fluxo equivalente documentado para você
- [ ] **Terminal**: scripts ou Makefile/task runner para tarefas repetidas

---

## Etapa 1 — Fundamentos

- [ ] Matemática discreta — provas/listas + **3 algoritmos** implementados
- [ ] Circuitos digitais — **somador + multiplexador** em simulador livre
- [ ] Linguagens (conceitos) — **comparação** de 2 linguagens (≈1 página)
- [ ] Programação I — **5 exercícios** + **1 CLI com testes**
- [ ] Geometria analítica — problemas + **vetores no código**
- [ ] **Engenharia:** repo com README, `.editorconfig`, convenção de commits

---

## Etapa 2 — Cálculo, ED, código

- [ ] Cálculo I — derivadas em **modelo simples** no código
- [ ] Álgebra linear I — **matrizes** + visualização **2D**
- [ ] Estruturas de dados — **fila, heap, BST** do zero + testes
- [ ] Programação II — projeto médio com **módulos** e tipagem onde couber
- [ ] OO — domínio modelado com **testes de unidade**
- [ ] **Engenharia:** TDD em ≥30% do código novo; **CI** (lint + testes)

---

## Etapa 3 — Grafos, arquitetura, prob., Cálculo II

- [ ] Algoritmos em grafos — DFS/BFS/Dijkstra + **1 problema** estilo contest
- [ ] Arquitetura I — experimento **cache / layout** de loop
- [ ] Probabilidade e estatística — **Monte Carlo** alinhado à teoria
- [ ] Cálculo II — integral aplicada com **checagem numérica**
- [ ] Programação funcional — **parser minúsculo** com ADTs / funções puras

---

## Etapa 4 — Análise, numérico, BD, Arq II

- [ ] Análise de algoritmos — prova de limites + **implementação** com análise no README
- [ ] Métodos numéricos — sistema linear vs **biblioteca**
- [ ] Banco de dados — esquema normalizado, consultas, **índices** explicados
- [ ] Arquitetura II — microbenchmark **pipeline / branch**
- [ ] Programação lógica — puzzles com **clpfd** ou similar
- [ ] **Engenharia:** **migrations**; **ADR** curto de decisão de dados

---

## Etapa 5 — Redes, ES, SO, PO, gráfica

- [ ] Redes — cliente/servidor + **protocolo** documentado + **Wireshark**
- [ ] Engenharia de software — requisitos, **diagrama de contexto**, riscos
- [ ] Sistemas operacionais — processos/threads; **deadlock** proposital + correção
- [ ] Programação matemática / PO — problema pequeno com **solver**
- [ ] Computação gráfica — **linha raster** ou **projeção 3D→2D**
- [ ] **Engenharia:** OWASP Top 10 **lido**; **1 vulnerabilidade** corrigida em lab

---

## Etapa 6 — Autômatos, IA, distribuídos, grafos, Cálculo III

- [ ] Linguagens formais e autômatos — **AFN→AFD** ou parser **LL(1)** simples
- [ ] Inteligência artificial — agente de busca + **classificador** baseline
- [ ] Sistemas distribuídos — **idempotência** + retries com **backoff** (HTTP)
- [ ] Teoria dos grafos — **post** explicando um teorema
- [ ] Cálculo III — **gradiente 2D** + interpretação em código

---

## Etapa 7 — Teoria, DL, compiladores, quântica, pesquisa

- [ ] Teoria da computação — **redução** ou MT **limitada** implementada
- [ ] Deep learning — rede pequena com **pipeline reprodutível**
- [ ] Compiladores — **lexer + parser** para linguagem mínima
- [ ] Computação quântica — notas + exercícios de **curso aberto** (se for da trilha)
- [ ] Metodologia da pesquisa — **3 papers** + resumo crítico

---

## Módulos extras (recomendados — primeira classe)

Detalhe curado (links + provas): [extras/modulos-elevados.md](extras/modulos-elevados.md).

- [ ] Concorrência e paralelismo (leitura + **código** com race e correção)
- [ ] Segurança aplicada (**threat model** de um app seu)
- [ ] Observabilidade (**logs/métricas** em projeto de estudo)
- [ ] Design de APIs (**contrato** versionado + idempotência documentada)
- [ ] LGPD / ética com dados (checklist aplicado a um caso de uso)

---

## Especialização (escolha ≥1 trilha profunda)

Marque a trilha alvo e use o guia em [`specializations/`](specializations/). Lista de exercícios-síntese por trilha + capstone: [docs/exercicios-por-disciplina.md](docs/exercicios-por-disciplina.md) (secção **Etapa 8 — Capstone, trilhas e portfólio**).

- [ ] Ciência de dados / ML engineering — **capstone** concluído
- [ ] Web full stack — **capstone** concluído
- [ ] DevOps / plataforma — **capstone** concluído
- [ ] Cybersecurity — **capstone** concluído (só em ambiente autorizado)
- [ ] Computação gráfica / jogos — **capstone** concluído
- [ ] Sistemas embarcados — **capstone** concluído
- [ ] Teoria / métodos formais — **capstone** concluído

---

## Demonstração pública (contínuo)

- [ ] Perfil GitHub com **repos** de estudo e histórico honesto
- [ ] Pelo menos **3 textos** seus (blog, gist, posts) explicando conceitos difíceis
- [ ] **Contribuição open source** ou projeto colaborativo documentado
