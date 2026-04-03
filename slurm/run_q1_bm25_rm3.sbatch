#!/bin/bash
#SBATCH --job-name=q1-bm25-rm3
#SBATCH --account=u6ef
#SBATCH --time=00:30:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --output=results/logs/q1_bm25_rm3_%j.out
#SBATCH --error=results/logs/q1_bm25_rm3_%j.err

set -euo pipefail
mkdir -p results/logs

echo "=== BM25+RM3 Baseline (E4) ==="
echo "Job ID: ${SLURM_JOB_ID}"
echo "Node: $(hostname)"
echo "Start: $(date)"

source .venv/bin/activate

python scripts/run_bm25_rm3.py \
    --config configs/exp_q1_bm25_rm3.yaml \
    --eval-file data/eval/manual_eval_v5.jsonl \
    --output-dir results/q1_experiments/bm25_rm3_baseline \
    --fb-docs 10 \
    --fb-terms 20 \
    --original-query-weight 0.5

echo "=== Complete: $(date) ==="
