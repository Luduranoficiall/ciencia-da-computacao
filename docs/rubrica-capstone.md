# Rubrica — projeto capstone (autoavaliação e revisão por pares)

Use esta grelha para **avaliar o seu** projeto final de especialização ou um **PR de colega**. Escala **0–4** por critério. Some e compare com a tabela de níveis no fim.

**Regra:** cada nota precisa de **evidência** (link para commit, trecho de README, teste, captura).

---

## Critérios (peso igual; total 28 pontos)

### 1. Correção funcional

| Nota | Descrição |
|------|-----------|
| 0 | Não executa ou quebra no caminho feliz documentado. |
| 1 | Executa parcialmente; erros conhecidos não listados. |
| 2 | Caminho feliz coberto; falhas parciais documentadas. |
| 3 | Casos de borda tratados ou explicitamente fora de escopo com justificação. |
| 4 | Comportamento previsível sob entradas inválidas; mensagens de erro úteis. |

### 2. Testes e automação

| Nota | Descrição |
|------|-----------|
| 0 | Sem testes. |
| 1 | Testes manuais só no README. |
| 2 | Testes automáticos no repositório; não correm em CI. |
| 3 | CI executa testes (e opcionalmente lint) em PR. |
| 4 | Cobertura razoável nos módulos críticos ou property-based em parte do domínio. |

### 3. Documentação e reprodutibilidade

| Nota | Descrição |
|------|-----------|
| 0 | README inexistente ou enganoso. |
| 1 | Instruções incompletas; outra pessoa não reproduz. |
| 2 | README com passos; reproduz em máquina parecida à do autor. |
| 3 | Reproduz com `Dockerfile`/`compose` ou script único; versões fixadas. |
| 4 | Outra pessoa reproduz em máquina limpa em menos de 15 min seguindo só o README. |

### 4. Modelagem de dados e persistência (se aplicável)

| Nota | Descrição |
|------|-----------|
| 0 | N/A mal explicado ou dados ad hoc sem esquema. |
| 1 | Esquema frágil; migrações inexistentes. |
| 2 | Esquema coerente; migrações ou scripts versionados. |
| 3 | Índices e consultas discutidos no README ou ADR. |
| 4 | Evolução do esquema documentada; rollback ou estratégia de deploy descrita. |

### 5. Segurança e privacidade

| Nota | Descrição |
|------|-----------|
| 0 | Segredos no Git; vulnerabilidades óbvias ignoradas. |
| 1 | Segredos fora do repo mas sem orientação. |
| 2 | Variáveis de ambiente; menção a OWASP ou checklist mínimo. |
| 3 | Threat model de 1 página ou ASVS parcial preenchido. |
| 4 | Correções ligadas a issues; dependências verificadas (ex.: `npm audit` / equivalente). |

### 6. Observabilidade e operação (se aplicável)

| Nota | Descrição |
|------|-----------|
| 0 | `print` espalhado sem estrutura. |
| 1 | Logs legíveis mas inconsistentes. |
| 2 | Logs estruturados ou níveis básicos. |
| 3 | Métrica ou healthcheck exposto. |
| 4 | Trace ou correlação entre serviços em ambiente de demo. |

### 7. Comunicação técnica

| Nota | Descrição |
|------|-----------|
| 0 | Impossível entender o objetivo. |
| 1 | Objetivo vago; decisões não explicadas. |
| 2 | README + diagrama simples ou lista de decisões. |
| 3 | ADR curto; limitações honestas. |
| 4 | Texto que serve de onboarding para terceiro em 1 leitura. |

---

## Conversão para nível

| Pontuação | Nível |
|-----------|--------|
| 0–8 | Insuficiente — não apresentar como capstone |
| 9–15 | Em progresso — foco em corrigir lacunas antes de divulgar |
| 16–22 | Bom — portfólio sólido para juniores pleno |
| 23–28 | Excelente — referência para entrevistas técnicas profundas |

---

## Uso em revisão por pares

1. Cada revisor preenche a grelha **sozinho**.
2. Comparar divergências **maiores que 1 ponto** num critério — discutir evidência.
3. Média das notas por critério → soma final (opcional).

---

## Ligação com especializações

Guias em [specializations/](../specializations/) devem referenciar esta rubrica como **contrato** do capstone.

---

*Inspirada em práticas de revisão de código e critérios de trabalhos finais de graduação; adapte pesos se a instituição ou equipa exigir.*
