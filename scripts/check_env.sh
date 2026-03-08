#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  cat <<'EOF'
Usage: bash scripts/check_env.sh

Report the current machine, Python, package manager, Slurm, GPU, and storage details.
EOF
  exit 0
fi

echo "COMMAND: uname -a"
uname -a || true
echo

echo "COMMAND: pwd"
pwd || true
echo

echo "COMMAND: python3 --version"
python3 --version || true
echo

echo "COMMAND: which python3"
which python3 || true
echo

echo "COMMAND: which pip"
which pip || true
echo

echo "COMMAND: which pip3"
which pip3 || true
echo

echo "COMMAND: which sbatch"
which sbatch || true
echo

echo "COMMAND: which srun"
which srun || true
echo

echo "COMMAND: ls"
ls || true
echo

echo "COMMAND: nvidia-smi"
nvidia-smi || true
echo

echo "COMMAND: df -h ."
df -h . || true
