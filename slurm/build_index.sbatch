#!/bin/bash
#SBATCH --job-name=soas-rag-index
#SBATCH --output=logs/build_index_%j.out
#SBATCH --error=logs/build_index_%j.err
#SBATCH --time=00:30:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G

set -euo pipefail
mkdir -p logs data/indexes
module load cray-python/3.11.7 || true
source .venv/bin/activate

python scripts/build_index.py --config configs/exp_smoke.yaml
