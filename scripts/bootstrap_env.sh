#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  cat <<'EOF'
Usage: bash scripts/bootstrap_env.sh

Create or refresh a local project virtualenv for Isambard.
This script prefers a newer Python module when available.
EOF
  exit 0
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if command -v module >/dev/null 2>&1; then
  module load cray-python/3.11.7 || true
fi

echo "COMMAND: python3 --version"
python3 --version

if ! python3 - <<'PY'
import sys
sys.exit(0 if sys.version_info >= (3, 10) else 1)
PY
then
  echo "Python 3.10+ is required. Load a newer module before continuing." >&2
  exit 1
fi

if [[ ! -d ".venv" ]]; then
  echo "COMMAND: python3 -m venv .venv"
  python3 -m venv .venv
fi

echo "COMMAND: .venv/bin/python -m pip install --upgrade pip setuptools wheel"
.venv/bin/python -m pip install --upgrade pip setuptools wheel

echo "COMMAND: .venv/bin/python -m pip install -e ."
.venv/bin/python -m pip install -e .
