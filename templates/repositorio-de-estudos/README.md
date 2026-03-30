# Template: repositório pessoal de estudos

Use esta pasta como **modelo** para criar o seu próprio repositório (no GitHub, GitLab, etc.) e registrar provas de nível, notas e código por disciplina — alinhado à [grade principal](../../README.md) e ao [checklist](../../checklist.md).

## Como usar

1. Crie um repositório vazio **seu** (não faça fork deste currículo se o objetivo é só seus estudos privados — copie os arquivos que quiser).
2. Copie para a raiz do seu repo:
   - `disciplina-README-template.md` (renomeie cópias para `README.md` dentro de cada pasta de matéria).
3. Opcional: copie [`.editorconfig`](.editorconfig) para padronizar indentação entre linguagens.
4. Preencha o `README.md` da raiz (exemplo abaixo).

## Árvore sugerida

Ajuste nomes às etapas que você segue.

```text
meu-cc-estudos/
├── README.md                 # visão geral + link para seu checklist
├── .editorconfig
├── etapa-01/
│   ├── matematica-discreta/
│   │   ├── README.md         # a partir do template
│   │   ├── notas/
│   │   └── codigo/
│   └── programacao-i/
│       └── ...
├── etapa-02/
│   └── ...
├── projetos-transversais/    # labs que cruzam matérias
└── portfolio/                # demos públicas
```

## README na raiz (modelo mínimo)

Substitua os campos entre `« »`.

```markdown
# Estudos — Ciência da Computação

Currículo de referência: [descrever: ex. trilha potente / UBL].

## Objetivo

«Ex.: Concluir etapa 2 até DATA com foco em ED.»

## Onde está o quê

| Pasta        | Conteúdo        |
|-------------|-----------------|
| etapa-01/…  | Fundamentos     |
| …           | …               |

## Regras para mim

- Todo módulo com **README** atualizado ao fechar a semana.
- **Prova de nível** referenciada por commit ou release.
```

## Relação com este currículo

- Marque itens no [checklist.md](../../checklist.md) deste repositório de currículo **ou** mantenha uma cópia no seu repo.
- Para playlists e livros extras, use [extras/cursos-referencia-ubl.md](../../extras/cursos-referencia-ubl.md) e [extras/bibliography/](../../extras/bibliography/).
