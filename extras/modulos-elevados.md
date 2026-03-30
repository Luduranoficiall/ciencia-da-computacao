# Módulos elevados — recursos e provas de nível

Complemento à tabela **Módulos extras que elevam o nível** no [README principal](../README.md). A ideia é **não só listar links**: cada bloco traz **o que estudar**, **por onde começar** e uma **prova de nível** que você documenta no seu repositório de estudos.

---

## 1. Concorrência e paralelismo

**Por que importa:** entrevistas e produção exigem raciocínio sobre ordem de eventos, exclusão mútua e modelos de memória — não basta “usar thread”.

| Tipo | Recurso |
|------|---------|
| Livro (referência) | Herlihy & Shavit — *The Art of Multiprocessor Programming* |
| Curso gratuito (SO + threads) | [OSTEP — concorrência](https://pages.cs.wisc.edu/~remzi/OSTEP/) (capítulos sobre threads e locks) |
| Prática em linguagem | [Tour de concorrência em Go](https://go.dev/tour/concurrency/1) ou capítulos equivalentes em Rust (ownership + `Send`/`Sync`) |

**Prova de nível (escolha uma):**

- Implementar **produtor-consumidor** com fila limitada + testes que reproduzem condição de corrida antes da correção; ou  
- Explicar em **uma página** o seu bug real de race e como instrumentou (log, TSAN, etc.).

---

## 2. Segurança aplicada

**Por que importa:** *features* sem modelo de ameaça viram incidente; auth e segredos mal colocados são padrão em vazamentos.

| Tipo | Recurso |
|------|---------|
| Lista de riscos web | [OWASP Top 10](https://owasp.org/www-project-top-ten/) |
| Modelagem | [OWASP Threat Dragon](https://owasp.org/www-project-threat-dragon/) (ferramenta) ou STRIDE em papel |
| Leitura curta | [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/) (tópicos que você usa no stack) |

**Prova de nível:**

- **Threat model** (diagrama + lista de riscos) de **uma aplicação sua** + uma mitigação implementada em commit referenciado; ou  
- Corrigir **uma vulnerabilidade intencional** num lab (ex.: DVWA) com relatório curto (só em ambiente autorizado).

---

## 3. Observabilidade

**Por que importa:** sem logs estruturados, métricas e *traces*, você opera às cegas — pior em sistemas distribuídos.

| Tipo | Recurso |
|------|---------|
| Conceitos | Google — [*Site Reliability Engineering*](https://sre.google/sre-book/table-of-contents/) (capítulos sobre monitorização e alertas) |
| Padrão moderno | [OpenTelemetry](https://opentelemetry.io/docs/) (visão geral + um SDK na sua linguagem) |
| E-book introdutório | *Distributed Systems Observability* (Cindy Sridharan) — citado na [bibliografia de engenharia](bibliography/00_aprendizado_engenharia.md) |

**Prova de nível:**

- Um **serviço de estudo** com **log JSON** + **uma métrica** (ex.: contador de pedidos) exposta e **gráfico** ou screenshot no README; ou  
- Um *trace* de **uma requisição** atravessando dois processos (mesmo que local com Docker Compose).

---

## 4. Design de APIs e sistemas

**Por que importa:** contratos estáveis, versionamento e idempotência reduzem incidentes e retrabalho entre equipas.

| Tipo | Recurso |
|------|---------|
| Contrato HTTP | [OpenAPI Specification](https://swagger.io/specification/) + gerador na sua stack |
| Estilo REST | [REST API Tutorial](https://restfulapi.net/) ou guias da sua empresa/framework |
| Livro (sistemas de dados) | Kleppmann — *Designing Data-Intensive Applications* (capítulos sobre replicação e *stream processing*) |

**Prova de nível:**

- **OpenAPI** (ou equivalente) versionado para **3 rotas** + política de erro documentada; ou  
- Documento de **1 página** descrevendo **idempotência** e *retries* num fluxo seu (diagrama simples).

---

## 5. Ética e legislação (LGPD)

**Por que importa:** dados pessoais em projeto de estudo também exigem base legal e minimização — e demonstra maturidade em entrevistas.

| Tipo | Recurso |
|------|---------|
| Autoridade | [ANPD](https://www.gov.br/anpd/pt-br) — textos oficiais e guias |
| Leitura guiada | [LGPD (Lei 13.709)](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm) (Planalto) — artigos sobre bases legais e direitos do titular |
| Checklist | Montar checklist próprio: “o que coleciono?”, “por quê?”, “quanto tempo guardo?” |

**Prova de nível:**

- **Política de privacidade** de **1 página** para um projeto seu (mesmo fictício mas coerente) + tabela de dados tratados; ou  
- Registro de decisão (**ADR**) “por que não guardamos X” num repositório de estudo.

---

## Como encaixar no tempo

Sugestão: **1 módulo por mês** em paralelo à etapa da grade, com **uma prova de nível** fechada antes de mudar de tema. Marque no [checklist](../checklist.md) quando cumprir.

---

## Ver também

- [Bibliografia — engenharia](bibliography/00_aprendizado_engenharia.md)  
- [Glossário PT/EN](../docs/glossario.md)
