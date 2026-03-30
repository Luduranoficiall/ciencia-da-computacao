#!/usr/bin/env bash
# Verificacao local alinhada ao CI (curriculum-data.yml).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PYTHON="$(bash "$ROOT/tools/resolve_python.sh")"

run() {
  echo "==> $*"
  "$@"
}

run "$PYTHON" tools/validate_data_schemas.py
run "$PYTHON" tools/validate_curriculum.py --strict
run "$PYTHON" tools/check_readme_mermaid.py
run "$PYTHON" tools/check_mermaid_curriculum_sync.py
run "$PYTHON" tools/check_exercicios_semester.py
run "$PYTHON" tools/mermaid_diagram_coverage.py
run "$PYTHON" tools/curriculum_progress.py --validate
run "$PYTHON" -m unittest discover -s tools -p 'test_*.py' -v
echo "OK: todas as verificacoes passaram."
