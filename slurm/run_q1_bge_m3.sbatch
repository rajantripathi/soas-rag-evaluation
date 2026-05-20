#!/bin/bash
#SBATCH --job-name=q1-bge-m3
#SBATCH --output=logs/q1_bge_m3_%j.out
#SBATCH --error=logs/q1_bge_m3_%j.err
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G

set -euo pipefail
mkdir -p logs results/q1_experiments

echo "=== E2: BGE-M3 Baseline ==="
echo "Job ID: ${SLURM_JOB_ID:-local}"
echo "Node: $(hostname)"
echo "Start: $(date)"

source .venv/bin/activate

python scripts/run_bge_m3_baseline.py \
    --config configs/exp_q1_bge_m3.yaml \
    --eval-file data/eval/manual_eval_v5.jsonl \
    --output-dir results/q1_experiments/bge_m3_baseline \
    --seed 42

echo "=== Complete: $(date) ==="
