#!/bin/bash
#SBATCH --job-name=eval_cross_lingual
#SBATCH --output=logs/cross_lingual_%j.out
#SBATCH --error=logs/cross_lingual_%j.err
#SBATCH --time=00:30:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G

set -euo pipefail
mkdir -p logs results/cross_lingual
module load cray-python/3.11.7 || true
source .venv/bin/activate

echo "Starting cross-lingual evaluation..."
date

# Test English system on Uzbek test set
echo "=== ENGLISH SYSTEM ON UZBEK TEST SET (20 items) ==="
python scripts/evaluate.py \
  --config configs/exp_manual_v5_vector_grounded_e5.yaml \
  --eval-file data/eval/uzbek_sample.jsonl \
  --corpus-file data/processed/corpus_manual_v1_uzsupp_v2.jsonl \
  --output results/cross_lingual/english_on_uzbek.jsonl

echo ""
echo "=== UZBEK SYSTEM ON ENGLISH TEST SET (20 items) ==="
python scripts/evaluate.py \
  --config configs/exp_manual_v5_vector_grounded_e5.yaml \
  --eval-file data/eval/english_sample.jsonl \
  --corpus-file data/processed/corpus_manual_v1_uzsupp_v2.jsonl \
  --output results/cross_lingual/uzbek_on_english.jsonl

echo ""
echo "Cross-lingual evaluation completed!"
date
