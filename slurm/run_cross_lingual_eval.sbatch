#!/bin/bash
#SBATCH --job-name=xl_eval
#SBATCH --partition=workq
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --time=1:00:00
#SBATCH --output=slurm/cross_lingual_eval_%j.out
#SBATCH --error=slurm/cross_lingual_eval_%j.err

# Cross-lingual RAG evaluation
# Measures cultural bias: English corpus → Uzbek queries, Uzbek corpus → English queries

cd /home/u6ef/rajantripathi.u6ef/soas_rag_eval
source .venv/bin/activate

echo "=== Cross-Lingual Evaluation ==="
echo "Started: $(date)"
echo "Node: $(hostname)"
echo ""

python3 scripts/run_cross_lingual_eval.py

echo ""
echo "Completed: $(date)"
