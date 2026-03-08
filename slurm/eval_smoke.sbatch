#!/bin/bash
#SBATCH --job-name=soas-rag-smoke
#SBATCH --output=logs/eval_smoke_%j.out
#SBATCH --error=logs/eval_smoke_%j.err
#SBATCH --time=00:30:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G

set -euo pipefail
mkdir -p logs results/logs results/reports
module load cray-python/3.11.7 || true
source .venv/bin/activate

python scripts/run_eval.py --config configs/exp_smoke.yaml
