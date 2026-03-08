#!/bin/bash
#SBATCH --job-name=soas-rag-array
#SBATCH --output=logs/eval_array_%A_%a.out
#SBATCH --error=logs/eval_array_%A_%a.err
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --array=0-3

set -euo pipefail
mkdir -p logs results/logs
module load cray-python/3.11.7 || true
source .venv/bin/activate

CONFIGS=(
  "configs/exp_smoke.yaml"
  "configs/exp_smoke.yaml"
  "configs/exp_smoke.yaml"
  "configs/exp_smoke.yaml"
)

python scripts/run_eval.py --config "${CONFIGS[$SLURM_ARRAY_TASK_ID]}"
