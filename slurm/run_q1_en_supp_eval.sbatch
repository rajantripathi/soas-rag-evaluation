#!/bin/bash
#SBATCH --job-name=q1-en-supp-e5
#SBATCH --output=logs/q1_en_supp_e5_%j.out
#SBATCH --error=logs/q1_en_supp_e5_%j.err
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=128G

set -euo pipefail
mkdir -p logs results/q1_experiments

echo "=== E1: EN Clean Supplement + e5-large ==="
echo "Job ID: ${SLURM_JOB_ID}"
echo "Start: $(date)"

source .venv/bin/activate
export OPENBLAS_NUM_THREADS=8

# Build index and run retrieval using existing pipeline
python scripts/run_eval.py --config configs/exp_q1_full_supp_clean.yaml

echo "=== Complete: $(date) ==="
