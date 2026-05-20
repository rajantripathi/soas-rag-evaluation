#!/bin/bash
#SBATCH --job-name=q1-mdpr
#SBATCH --output=logs/q1_mdpr_%j.out
#SBATCH --error=logs/q1_mdpr_%j.err
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=128G

set -euo pipefail
mkdir -p logs results/q1_experiments

echo "=== E3: mDPR Baseline ==="
echo "Job ID: ${SLURM_JOB_ID:-local}"
echo "Node: $(hostname)"
echo "Start: $(date)"

source .venv/bin/activate

OPENBLAS_NUM_THREADS=8 python scripts/run_mdpr_baseline.py \
    --config configs/exp_q1_mdpr.yaml \
    --eval-file data/eval/manual_eval_v5.jsonl \
    --output-dir results/q1_experiments/mdpr_baseline \
    --seed 42

echo "=== Complete: $(date) ==="
