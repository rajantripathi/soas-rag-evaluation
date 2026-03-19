#!/bin/bash
#SBATCH --job-name=build_index_full_supp
#SBATCH --output=logs/build_index_full_supp_%j.out
#SBATCH --error=logs/build_index_full_supp_%j.err
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --gres=gpu:1

set -euo pipefail
mkdir -p logs data/indexes results/logs
module load cray-python/3.11.7 || true
source .venv/bin/activate

# Limit OpenBLAS threads to avoid warnings
export OPENBLAS_NUM_THREADS=8

echo "Starting index build for full supplement corpus..."
date

python scripts/build_index.py --config configs/exp_manual_v5_vector_grounded_e5_full_supplement.yaml

echo "Index build completed!"
date
