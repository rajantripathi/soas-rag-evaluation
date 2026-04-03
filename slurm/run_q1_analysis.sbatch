#!/bin/bash
#SBATCH --job-name=q1-analysis
#SBATCH --output=logs/q1_analysis_%j.out
#SBATCH --error=logs/q1_analysis_%j.err
#SBATCH --time=00:30:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G

set -euo pipefail
mkdir -p logs results/logs

echo "=== Q1 Analysis: Extended Metrics + Cultural Specificity ==="
echo "Job ID: ${SLURM_JOB_ID:-local}"
echo "Start: $(date)"

module load cray-python/3.11.7 || true
source .venv/bin/activate

# E5: Extended metrics for ALL existing conditions
echo "--- E5: Computing extended metrics ---"
python scripts/compute_extended_metrics.py \
    --results-dir results \
    --eval-file data/eval/manual_eval_v5.jsonl \
    --output results/q1_experiments/extended_metrics.json \
    --top-k 1 3 5 10 20 50 100

# E6: Cultural specificity analysis (CRG, CSS)
echo "--- E6: Computing cultural specificity analysis ---"
python scripts/compute_cultural_specificity_analysis.py \
    --results-dir results \
    --eval-file data/eval/manual_eval_v5.jsonl \
    --output-dir results/q1_experiments \
    --n-resamples 10000

echo "=== Complete: $(date) ==="
