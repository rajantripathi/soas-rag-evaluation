#!/bin/bash
#SBATCH --job-name=q1-bm25-rm3
#SBATCH --account=u6ef
#SBATCH --partition=gh200
#SBATCH --nodes=1
#SBATCH --gpus-per-node=0
#SBATCH --time=00:30:00
#SBATCH --output=results/logs/q1_bm25_rm3_%j.out
#SBATCH --error=results/logs/q1_bm25_rm3_%j.err

set -euo pipefail

echo "=== BM25+RM3 Baseline Experiment ==="
echo "Job ID: ${SLURM_JOB_ID}"
echo "Node: $(hostname)"
echo "Start: $(date)"

source .venv/bin/activate

# Run BM25+RM3 baseline (CPU only, no GPU needed)
python scripts/run_bm25_rm3.py \
    --config configs/exp_q1_bm25_rm3.yaml \
    --eval-file data/eval/manual_eval_v5.jsonl \
    --output-dir results/q1_experiments/bm25_rm3_baseline \
    --fb-docs 10 \
    --fb-terms 20 \
    --original-query-weight 0.5

echo "=== Complete: $(date) ==="
