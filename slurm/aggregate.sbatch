#!/bin/bash
#SBATCH --job-name=soas-rag-aggregate
#SBATCH --output=logs/aggregate_%j.out
#SBATCH --error=logs/aggregate_%j.err
#SBATCH --time=00:15:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G

set -euo pipefail
mkdir -p logs results/reports
module load cray-python/3.11.7 || true
source .venv/bin/activate

python scripts/summarize_runs.py --results-dir results
