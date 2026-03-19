#!/bin/bash
#SBATCH --job-name=run_eval_full_supp
#SBATCH --output=logs/run_eval_full_supp_%j.out
#SBATCH --error=logs/run_eval_full_supp_%j.err
#SBATCH --time=00:30:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G

set -euo pipefail
mkdir -p logs results/logs
module load cray-python/3.11.7 || true
source .venv/bin/activate

echo "Starting evaluation with full supplement corpus..."
date

python scripts/run_eval.py --config configs/exp_manual_v5_vector_grounded_e5_full_supplement.yaml

echo "Evaluation completed!"
date

echo "Results written to: "
find results -name "eval_*" -type d -newer logs/run_eval_full_supp_${SLURM_JOB_ID}.out | head -1
