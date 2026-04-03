#!/bin/bash
#SBATCH --job-name=q1-analysis
#SBATCH --account=u6ef
#SBATCH --partition=gh200
#SBATCH --nodes=1
#SBATCH --gpus-per-node=0
#SBATCH --time=00:30:00
#SBATCH --output=results/logs/q1_analysis_%j.out
#SBATCH --error=results/logs/q1_analysis_%j.err

set -euo pipefail

echo "=== Q1 Analysis: Extended Metrics + Cultural Specificity ==="
echo "Job ID: ${SLURM_JOB_ID}"
echo "Start: $(date)"

source .venv/bin/activate

# Create output directory
mkdir -p results/q1_experiments

# Step 1: Compute extended metrics for ALL conditions
echo "--- Computing extended metrics ---"
python scripts/compute_extended_metrics.py \
    --results-dir results \
    --eval-file data/eval/manual_eval_v5.jsonl \
    --output results/q1_experiments/extended_metrics.json \
    --top-k 1 3 5 10 20 50 100

# Step 2: Cultural specificity analysis (CRG, CSS)
echo "--- Computing cultural specificity analysis ---"
python scripts/compute_cultural_specificity_analysis.py \
    --results-dir results \
    --eval-file data/eval/manual_eval_v5.jsonl \
    --output-dir results/q1_experiments \
    --n-resamples 10000

echo "=== Complete: $(date) ==="
