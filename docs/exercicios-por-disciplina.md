# Banco de exercícios por disciplina

Complemento à coluna **Prova de nível** do [README principal](../README.md). Cada bloco mistura **teoria curta**, **implementação** e **leitura crítica** — use como lista mínima e aumente dificuldade quando estiver confortável.

**Como usar**

- **Tempo** é ordem de grandeza para um autodidata com base; ajuste ao seu ritmo.
- **D / M / F** = dificuldade (D = desafio, costuma exigir pesquisa extra).
- **Critério de feito:** você consegue **explicar em voz alta** a solução e **apontar onde erraria** se mudasse o enunciado.
- IDs do grafo (`data/curriculum.json`) aparecem entre crases quando batem com o JSON — úteis para cruzar com `curriculum_progress.py`.
- **Semestre sugerido** (**S1**–**S8**) em cada disciplina alinha-se ao [plano de graduação em 4 anos](graduacao-4-anos.md); **pré-requisitos** continuam definidos só no JSON.

**Semestre sugerido por ID** (mesma convenção que `graduacao-4-anos.md`):

| IDs | Sem. |
|-----|------|
| `discreta`, `circuitos`, `ling_prog`, `prog1`, `geo` | S1 |
| `calc1`, `alg_lin1`, `ed`, `prog2`, `oo` | S2 |
| `grafos`, `arq1`, `prob_est`, `calc2`, `funcional`, `met_num`, `teo_grafos` | S3 |
| `analise_alg`, `bd`, `arq2`, `prog_logica`, `calc3` | S4 |
| `redes`, `eng_sw`, `so`, `prog_mat`, `comp_grafica` | S5 |
| `automatos`, `ia`, `dist` | S6 |
| `teo_comp`, `dl`, `compiladores`, `quantica` | S7 |
| `met_pesquisa` (+ capstone / trilhas em `specializations/`) | S8 |

*`teo_grafos` pode antecipar desbloqueio mental para `compiladores`; reforço em S6 se ainda não estiver fechado — ver notas no plano de 4 anos.*

**Recursos transversais (não substituem as listas abaixo):** [Exercism](https://exercism.org/), [LeetCode](https://leetcode.com/), [Codeforces](https://codeforces.com/), [Project Euler](https://projecteuler.net/) (matemática + código), [MIT OCW](https://ocw.mit.edu/) (listas oficiais por curso).

---

## Etapa 1 — Fundamentos

### Matemática discreta (`discreta`) — sem. **S1**

| # | Tipo | Enunciado (resumo) | Tempo |
|---|------|-------------------|-------|
| 1 | Prova | Prove que \(\sqrt{2}\) é irracional (contradição clássica). | 1–2 h |
| 2 | Prova | Indução: soma dos primeiros \(n\) ímpares; soma geométrica finita. | 2–3 h |
| 3 | Código | Implemente gcd estendido e inverso modular (com testes em casos pequenos). | 2–4 h |
| 4 | Prova | Relações: defina ordem parcial num conjunto pequeno; identifique máximos/minimos. | 2 h |
| 5 | M/D | Combinatória: contar permutações com restrição; depois generalize com fórmula. | 3–5 h |

### Circuitos digitais (`circuitos`) — sem. **S1**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Lab | Meio-somador e somador completo em simulador (Logisim-evolution, Digital, etc.). | 2–3 h |
| 2 | Lab | Multiplexador 4:1 a partir de portas; documente tabela verdade. | 2 h |
| 3 | Teoria | Explique *setup/hold* em 1 página (mesmo que só leia datasheets depois). | 1–2 h |

### Linguagens de programação — conceitos (`ling_prog`) — sem. **S1**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Texto | Compare duas linguagens: tipagem estática vs dinâmica, avaliação estrita vs preguiçosa, GC vs RAII. | 2–3 h |
| 2 | Leitura | Leia a especificação de um tipo somo (Rust `enum` ou ADT em Haskell) e relate com seu texto. | 2 h |

### Programação I (`prog1`) — sem. **S1**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Código | 5 exercícios de lógica + estruturas (listas, dicionários) com asserts ou testes. | 4–8 h |
| 2 | Código | CLI que lê CSV/JSON, valida entrada e falha com código de saída ≠ 0 em erro. | 4–8 h |
| 3 | D | Parser recursivo descendente **mínimo** para expressões aritméticas (só inteiros). | 8–16 h |

### Geometria analítica (`geo`) — sem. **S1**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Cálculo | Distância ponto–reta, interseção de retas, área de polígono simples no plano. | 3–5 h |
| 2 | Código | Represente vetores 2D; rotacione e projete; visualize (matplotlib ou similar). | 3–6 h |

---

## Etapa 2 — Cálculo, estruturas, OO

### Cálculo I (`calc1`) — sem. **S2**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Cálculo | Regra da cadeia e derivada implícita em 3 exercícios clássicos. | 3–5 h |
| 2 | Código | Modele posição/velocidade; use derivada numérica e compare com analítica (erro vs \(h\)). | 4–6 h |

### Álgebra linear I (`alg_lin1`) — sem. **S2**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Código | Multiplicação de matrizes, transposta, identidade — sem usar biblioteca de álgebra (só laços). | 3–5 h |
| 2 | Viz | Aplique transformações 2D (escala, rotação, cisalhamento) a um conjunto de pontos e plote. | 3–5 h |

### Estruturas de dados (`ed`) — sem. **S2**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Código | Fila (array circular), min-heap, BST com insert/delete — **testes de invariantes**. | 10–20 h |
| 2 | Análise | Para cada estrutura, anote \(O(\cdot)\) médio/pior caso das operações usadas. | 2–3 h |

### Programação II (`prog2`) — sem. **S2**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Projeto | Módulos separados, tipos claros (mypy ou equivalente onde couber), README com como rodar. | 12–24 h |
| 2 | Revisão | Troque código com você mesmo em “PR”: uma feature, um bugfix, checklist de estilo. | 2–4 h |

### Orientação a objetos (`oo`) — sem. **S2**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Código | Modele domínio (ex.: biblioteca, estacionamento) com testes de unidade nos invariantes. | 8–16 h |
| 2 | Texto | Onde OO ajuda e onde composição/funções puras seriam melhores — 1 página. | 2 h |

---

## Etapa 3 — Grafos, arquitetura, probabilidade, cálculo II

### Algoritmos em grafos (`grafos`) — sem. **S3**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Código | DFS/BFS com rastreamento de pai; Dijkstra com heap; **testes** em grafos pequenos. | 10–16 h |
| 2 | Contest | 1 problema estilo Codeforces (rating alvo: seu nível + 100) com editorial estudado depois. | 2–4 h |

### Arquitetura de computadores I (`arq1`) — sem. **S3**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Lab | Experimento: dois loops com mesmo trabalho, ordens de acesso diferentes — meça tempo/cache (perf, valgrind, `perf stat`). | 4–8 h |
| 2 | Teoria | Explique pipeline em 5 estágios; onde entram hazards (dados/controle). | 2–4 h |

### Probabilidade e estatística (`prob_est`) — sem. **S3**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Simulação | Estime \(\pi\) ou integral conhecida por Monte Carlo; compare variância com \(N\). | 3–5 h |
| 2 | Teoria | Bayes em problema de “falso positivo”; árvore de probabilidades. | 2–4 h |

### Cálculo II (`calc2`) — sem. **S3**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Cálculo | Integral definida (área entre curvas); volume de sólido de revolução (um exercício). | 4–6 h |
| 2 | Código | Verificação numérica (trapézio/Simpson) vs resultado analítico; gráfico do erro. | 3–5 h |

### Programação funcional (`funcional`) — sem. **S3**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Código | Parser combinator minúsculo ou parser por recursão com ADTs (sem efeitos onde possível). | 8–20 h |
| 2 | Teoria | Diferença entre avaliação estrita e preguiçosa com **um** exemplo que quebra expectativas. | 2 h |

---

## Etapa 4 — Análise, numérico, BD, arquitetura II

### Análise de algoritmos (`analise_alg`) — sem. **S4**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Prova | Limite assintótico de um algoritmo que você implementou (melhor/pior caso). | 4–8 h |
| 2 | Prova | Árvores binárias de busca: altura média (discussão) ou análise de um trecho de inserção. | 4–8 h |

### Métodos numéricos (`met_num`) — sem. **S3**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Código | Resolver \(Ax=b\) por eliminação gaussiana; comparar com numpy/scipy em matriz bem condicionada. | 4–8 h |
| 2 | Estudo | Condicionamento: exemplo de matriz mal condicionada e explosão numérica. | 2–4 h |

### Banco de dados (`bd`) — sem. **S4**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Projeto | Esquema 3FN; migrações; consultas com `EXPLAIN` e justificativa de índice. | 8–16 h |
| 2 | Teoria | Transações ACID: exemplo de anomalia se isolar mal; como o nível de isolamento muda o cenário. | 2–4 h |

### Arquitetura II (`arq2`) — sem. **S4**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Lab | Microbenchmark: branch prediction ou pipeline (documente metodologia, ambiente, ruído). | 4–8 h |
| 2 | Leitura | Resumo de um capítulo de memória virtual (TLB, page fault). | 2–4 h |

### Programação lógica (`prog_logica`) — sem. **S4**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Lab | Sudoku ou scheduling pequeno com restrições (`clpfd` ou equivalente). | 6–12 h |
| 2 | Teoria | Quando lógica pura não escala — 1 parágrafo honesto. | 30 min |

---

## Etapa 5 — Redes, ES, SO, otimização, gráfica

### Redes (`redes`) — sem. **S5**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Projeto | Cliente/servidor TCP; protocolo em texto com versionamento; captura Wireshark anotada. | 12–24 h |
| 2 | Teoria | Handshake TCP; o que acontece se um dos lados sumir no meio. | 2 h |

### Engenharia de software (`eng_sw`) — sem. **S5**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Doc | Requisitos, diagrama de contexto (C4 L1 ou equivalente), lista de riscos com mitigação. | 6–10 h |
| 2 | Processo | Defina “Definition of Done” para um projeto seu — mensurável. | 1–2 h |

### Sistemas operacionais (`so`) — sem. **S5**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Código | Processos vs threads; **deadlock proposital** (4 recursos) e correção por ordenação de locks. | 6–12 h |
| 2 | Leitura | Resumo de escalonamento (preemptivo vs cooperativo) com trade-off. | 2 h |

### Programação matemática / PO (`prog_mat`) — sem. **S5**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Lab | Modele problema pequeno (transporte, dieta) em solver (OR-Tools, PuLP, JuMP…). | 6–12 h |
| 2 | Teoria | Dualidade em 2D (desenho) ou explicação textual de preço sombra. | 3–5 h |

### Computação gráfica (`comp_grafica`) — sem. **S5**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Código | Bresenham ou Wu para segmentos; **ou** projeção 3D→2D com matriz. | 8–16 h |
| 2 | Teoria | Pipeline gráfico moderno vs imediato — parágrafo com fontes. | 1–2 h |

---

## Etapa 6 — Autômatos, IA, distribuídos, teoria de grafos, cálculo III

### Linguagens formais e autômatos (`automatos`) — sem. **S6**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Código | AFN → AFD (subset construction) em conjuntos de estados; testes com strings. | 12–24 h |
| 2 | Alternativa | Parser LL(1) para gramática LL(1) mínima; tabela de parse. | 12–24 h |

### Inteligência artificial (`ia`) — sem. **S6**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Código | Agente de busca (A* ou uniform-cost) em grid com custos. | 6–12 h |
| 2 | Código | Classificador baseline (logistic regression ou árvore) com train/val e métrica justificada. | 8–16 h |

### Sistemas distribuídos (`dist`) — sem. **S6**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Código | Cliente HTTP com **idempotência** (chave de idempotência) + retries exponenciais + jitter. | 8–16 h |
| 2 | Teoria | Explicação de “pelo menos uma vez” vs “exatamente uma vez” (honestidade sobre impossibilidade). | 2–3 h |

### Teoria dos grafos (`teo_grafos`) — sem. **S3** *([plano 4 anos](graduacao-4-anos.md): reforço em **S6** se ainda não fechou)*

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Texto | Post técnico: teorema escolhido (ex.: Turán, Hall, coloração) com exemplo construtivo. | 6–10 h |
| 2 | Exercícios | 5 exercícios de livro-texto (demonstração ou contraexemplo). | 6–10 h |

### Cálculo III (`calc3`) — sem. **S4**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Cálculo | Gradiente de função escalar em \(\mathbb{R}^2\); interpretação geométrica. | 4–6 h |
| 2 | Código | Campo vetorial simples; derivada direcional numérica vs analítica. | 4–6 h |

---

## Etapa 7 — Teoria avançada, DL, compiladores, quântica, pesquisa

### Teoria da computação (`teo_comp`) — sem. **S7**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Prova/impl | Redução simples (ex.: SAT → 3SAT esboço) **ou** MT limitada a \(n\) passos com fita finita. | 12–24 h |
| 2 | Leitura | Hierarquia de Chomsky: posição da sua linguagem favorita de programação (com ressalvas). | 2 h |

### Deep learning (`dl`) — sem. **S7**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Projeto | Rede pequena (MNIST ou tabular); seeds fixas; métricas; gráficos de treino no README. | 16–40 h |
| 2 | D | Regularização: dropout/weight decay — um experimento controlado (comparação). | 6–12 h |

### Compiladores (`compiladores`) — sem. **S7**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Projeto | Lexer + parser + eval ou codegen mínimo para linguagem com expressões e `if`. | 24–60 h |
| 2 | Teoria | Conflitos LR vs LL — quando cada um dói. | 2 h |

### Computação quântica (`quantica`) — sem. **S7**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Curso | Notas + exercícios de um MOOC aberto (Qiskit, IBM, etc.) até circuito de 2 qubits útil. | 20–40 h |
| 2 | Matemática | Revisão: números complexos, produto interno, unitárias como “rotações” preservando norma. | 4–8 h |

### Metodologia da pesquisa (`met_pesquisa`) — sem. **S8**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Leitura | 3 papers; para cada um: problema, método, limitação, **o que você reproduziria**. | 12–20 h |
| 2 | Escrita | Resumo de 1 página citando corretamente (BibTeX ou equivalente). | 3–5 h |

---

## Etapa 8 — Capstone, trilhas e portfólio (S8)

Bloco **fora** do grafo `data/curriculum.json`: não há nó `capstone`; combine com `met_pesquisa`, [rubrica-capstone.md](rubrica-capstone.md) e uma ou mais trilhas em [`specializations/`](../specializations/).

### Projeto capstone / TCC — sem. **S8**

| # | Tipo | Enunciado | Tempo |
|---|------|-----------|-------|
| 1 | Entrega | Repositório **público**: objetivo mensurável, licença, README que outra pessoa segue até reproduzir (ou justifica bloqueio honesto). | 20–80 h |
| 2 | Qualidade | **CI** (testes ou lint mínimo) + histórico de commits legível; nada de segredos no Git. | 8–20 h |
| 3 | Avaliação | Preencha a [rubrica-capstone.md](rubrica-capstone.md) no teu projeto; liste 3 melhorias priorizadas por risco. | 2–4 h |
| 4 | Comunicação | Artigo técnico curto **ou** lightning talk (10 min): problema, decisões, limitações, o que farias diferente. | 4–12 h |

### Trilhas de especialização — sem. **S8**

Escolha **pelo menos uma** trilha; o exercício-síntese fecha o “perfil especialista” além do núcleo.

| Trilha | Guia | Exercício-síntese |
|--------|------|-------------------|
| Dados / ML | [data_science.md](../specializations/data_science.md) | Pipeline reprodutível (Makefile/`just`/script único); métrica + baseline; README com limitações. |
| Web | [web_development.md](../specializations/web_development.md) | App deployável ou demo local com contrato de API; sessão/auth ou rate-limit **documentado**. |
| DevOps / plataforma | [devops.md](../specializations/devops.md) | Serviço com healthcheck, logs estruturados e um alerta ou dashboard mínimo; IaC ou manifest versionado. |
| Segurança | [cybersecurity.md](../specializations/cybersecurity.md) | Threat model STRIDE + um achado corrigido (lab) com write-up. |
| Gráfica / jogos | [computer_graphics.md](../specializations/computer_graphics.md) | Demo interativa ou vídeo: pipeline escolhido explicado; trade-off performance vs qualidade. |
| Embarcados / IoT | [embedded_systems.md](../specializations/embedded_systems.md) | Firmware ou simulação: pinagem/periférico documentado; teste de regressão ou property simples. |
| Teoria / métodos formais | [theory_formal_methods.md](../specializations/theory_formal_methods.md) | Prova esboçada, modelo formal mínimo, ou uso de verificador; 1 página “o que garantimos”. |

---

## Módulos transversais (além da grade)

Use em paralelo com [extras/modulos-elevados.md](../extras/modulos-elevados.md).

| Tema | Exercício-síntese |
|------|-------------------|
| Concorrência | Data race mínima + correção (mutex, canal, ou atomics) com teste de stress. |
| Segurança | Threat model STRIDE de um app seu; uma vulnerabilidade OWASP corrigida em lab. |
| Observabilidade | Logs estruturados + uma métrica RED ou USE em serviço de estudo. |
| APIs | Contrato OpenAPI; idempotência documentada; versionamento. |
| LGPD | Mapeamento de bases e bases legais para um caso fictício realista. |

---

## Verificação automática do repositório

- `bash tools/verify_repo.sh` — inclui JSON Schema, DAG, Mermaid, **alinhamento deste ficheiro** aos semestres S1–S8 (`tools/check_exercicios_semester.py`) e `unittest` em `tools/`.
- O grafo em `data/curriculum.json` é validado por `python3 tools/validate_curriculum.py`. Alterações nas dependências devem manter **DAG**, **IDs únicos** e **arestas sem duplicata** — ver `tools/curriculum_common.py` e testes em `tools/test_curriculum_validation.py`.
