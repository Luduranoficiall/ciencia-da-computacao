# Especialização: Ciência de dados e ML engineering

## Pré-requisitos mínimos (do núcleo)

- Probabilidade e estatística, Cálculo I–II (para otimização e DL).
- Programação II, estruturas de dados, banco de dados.
- Álgebra linear.

## Trilha sugerida

1. **Manipulação e qualidade de dados** — Pandas/Polars, tipos de dados, valores ausentes, vieses.
2. **Visualização** — princípios de percepção; ggplot2 ou equivalente em Python.
3. **ML supervisionado** — regressão, árvores, ensembles; validação cruzada e métricas.
4. **ML não supervisionado** — clustering, redução de dimensionalidade.
5. **Pipelines** — treino, serialização de modelo, inferência batch vs online.
6. **MLOps leve** — experiment tracking, containers, testes em dados.

## Recursos (curtos)

- [Kaggle Learn](https://www.kaggle.com/learn), ISL/ESL (ver [bibliografia](../extras/bibliography/05_ia_ml.md)).
- [Papers With Code](https://paperswithcode.com/) para aprofundar tarefas.

## Capstone (escolha um)

- **A:** Prever algo com dataset público com **relatório** de vazamento de dados e fairness básico.
- **B:** Serviço HTTP de inferência com testes, Dockerfile e métricas de latência documentadas.
- **C:** Reproduzir um paper pequeno (ex.: arquitetura clássica de visão ou NLP) com código limpo.

## Prova de nível

Notebook ou repo com `README` reprodutível, testes em funções puras de feature engineering e política de versionamento de dados explícita.
