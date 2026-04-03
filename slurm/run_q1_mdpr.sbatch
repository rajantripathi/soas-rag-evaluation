#!/bin/bash
#SBATCH --job-name=q1-mdpr
#SBATCH --account=u6ef
#SBATCH --partition=gh200
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --time=02:00:00
#SBATCH --output=results/logs/q1_mdpr_%j.out
#SBATCH --error=results/logs/q1_mdpr_%j.err

set -euo pipefail

echo "=== mDPR Baseline Experiment ==="
echo "Job ID: ${SLURM_JOB_ID}"
echo "Node: $(hostname)"
echo "Start: $(date)"

module load cuda/12.3

source .venv/bin/activate

python scripts/run_mdpr_baseline.py \
    --config configs/exp_q1_mdpr.yaml \
    --eval-file data/eval/manual_eval_v5.jsonl \
    --output-dir results/q1_experiments/mdpr_baseline \
    --seed 42

echo "=== Complete: $(date) ==="
