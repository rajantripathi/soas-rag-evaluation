#!/bin/bash
#SBATCH --job-name=q1-bge-m3
#SBATCH --account=u6ef
#SBATCH --partition=workq
#SBATCH --nodes=1
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --output=results/logs/q1_bge_m3_%j.out
#SBATCH --error=results/logs/q1_bge_m3_%j.err

set -euo pipefail
mkdir -p results/logs

echo "=== BGE-M3 Baseline Experiment (E2) ==="
echo "Job ID: ${SLURM_JOB_ID}"
echo "Node: $(hostname)"
echo "Start: $(date)"

module load cray-python/3.11.7 || true
source .venv/bin/activate

python scripts/run_bge_m3_baseline.py \
    --config configs/exp_q1_bge_m3.yaml \
    --eval-file data/eval/manual_eval_v5.jsonl \
    --output-dir results/q1_experiments/bge_m3_baseline \
    --seed 42

echo "=== Complete: $(date) ==="
