#!/usr/bin/env bash
# Emite o interpretador Python a usar: .venv se existir e tiver jsonschema, senao python3.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  if "$ROOT/.venv/bin/python" -c "import jsonschema" 2>/dev/null; then
    echo "$ROOT/.venv/bin/python"
    exit 0
  fi
fi
if python3 -c "import jsonschema" 2>/dev/null; then
  echo "python3"
  exit 0
fi
echo "ERRO: instale dependencias de desenvolvimento: python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt" >&2
exit 1
