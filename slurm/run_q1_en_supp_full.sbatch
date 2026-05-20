#!/bin/bash
#SBATCH --job-name=q1-e1-full
#SBATCH --output=logs/q1_e1_full_%j.out
#SBATCH --error=logs/q1_e1_full_%j.err
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=128G

set -euo pipefail
mkdir -p logs results/q1_experiments data/indexes

echo "=== E1: Clean EN Supplement + e5-large ==="
echo "Job ID: ${SLURM_JOB_ID}"
echo "Start: $(date)"

source .venv/bin/activate
export OPENBLAS_NUM_THREADS=8

# Step 1: Build index on the full supplement clean corpus
echo "--- Building index ---"
python scripts/build_index.py --config configs/exp_q1_full_supp_clean.yaml

# Step 2: Run retrieval evaluation
echo "--- Running evaluation ---"
python scripts/run_eval.py --config configs/exp_q1_full_supp_clean.yaml

echo "=== Complete: $(date) ==="
