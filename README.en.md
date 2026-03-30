# Computer Science — intensive self-directed track

**Canonical curriculum (Portuguese):** [README.md](README.md)

This repository is a **dense, engineering-minded** complement to open playlists (especially the excellent [Universidade-Livre / ciencia-da-computacao](https://github.com/Universidade-Livre/ciencia-da-computacao) roadmap). Expect **proof-of-level tasks**, **CI**, **security hygiene**, and **public artifacts**—not “video-only” learning.

**4-year undergraduate-style pacing (8 semesters, PT):** [docs/graduacao-4-anos.md](docs/graduacao-4-anos.md).

## Navigation (same tree as the Portuguese README)

| Area | File / folder |
|------|----------------|
| Progress checklist | [checklist.md](checklist.md) |
| Bibliography | [extras/bibliography/](extras/bibliography/) |
| Advanced modules (PT) | [extras/modulos-elevados.md](extras/modulos-elevados.md) |
| Tools | [extras/ferramentas.md](extras/ferramentas.md) |
| Video index (UBL) | [extras/cursos-referencia-ubl.md](extras/cursos-referencia-ubl.md) |
| Specializations | [specializations/](specializations/) |
| Contributing | [CONTRIBUTING.md](CONTRIBUTING.md) · [CODEOWNERS](.github/CODEOWNERS) · [MAINTAINERS.md](MAINTAINERS.md) |
| Conduct | [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) |
| Security | [SECURITY.md](SECURITY.md) |
| Support | [SUPPORT.md](SUPPORT.md) |
| Study repo template | [templates/repositorio-de-estudos/](templates/repositorio-de-estudos/) |
| FAQ (PT; calendar vs graph, `verify_repo`) | [FAQ.md](FAQ.md) |
| Roadmap | [docs/roadmap.md](docs/roadmap.md) |
| 90-day intensive (PT) | [docs/plano-intensivo-90-dias.md](docs/plano-intensivo-90-dias.md) |
| 4-year degree pacing (PT) | [docs/graduacao-4-anos.md](docs/graduacao-4-anos.md) |
| Capstone rubric (PT) | [docs/rubrica-capstone.md](docs/rubrica-capstone.md) |
| Curriculum graph (JSON) | [data/curriculum.json](data/curriculum.json) · [tools/README.md](tools/README.md) · [requirements-dev.txt](requirements-dev.txt) · `tools/verify_repo.sh` |
| Progress vs blockers (PT doc) | [data/progress.json](data/progress.json) · `python3 tools/curriculum_progress.py` · [docs/curriculum-progresso.md](docs/curriculum-progresso.md) |
| PT / EN glossary | [docs/glossario.md](docs/glossario.md) |
| Exercise bank by course (PT) | [docs/exercicios-por-disciplina.md](docs/exercicios-por-disciplina.md) (S1–S8 + capstone / tracks) |
| Link checks (CI) | [`.github/workflows/links.yml`](.github/workflows/links.yml) |

## What “more intensive” means here

| Dimension | Focus |
|-----------|--------|
| Method | Loop: study → build → explain (Feynman) → measure (tests, benchmarks). |
| Engineering | Git fluency, TDD where it fits, code review, minimal CI, basic threat modeling. |
| Math | Same spine as a CS degree (discrete, calculus, linear algebra, probability) with applied hooks. |
| Systems | Concurrency and I/O taken as seriously as in-memory algorithms. |
| Career | Portfolio with acceptance criteria; OSS contribution as a habit. |

## Diagrams (SVG in `assets/`)

Dependency overview, parallel tracks, learning loop, **typical study week**, and **math prerequisite map** are shown in [README.md](README.md) under **Imagens do currículo**. Files in `assets/`: `grafo-pre-requisitos.svg`, `trilhas-paralelas.svg`, `ciclo-aprendizado.svg`, `ciclo-semana-estudo.svg`, `mapa-matematica.svg`. Optional local PNG exports (not committed by default) are documented in the Portuguese README.

## License

Text and structure: [LICENSE](LICENSE) (MIT). Third-party courses and books keep their own terms.

---

*For the full staged tables (“Prova de nível”), Mermaid graph, and Portuguese copy, open [README.md](README.md).*
