#!/bin/bash
#SBATCH --job-name=q1-en-supp
#SBATCH --account=u6ef
#SBATCH --partition=gh200
#SBATCH --nodes=1
#SBATCH --gpus-per-node=0
#SBATCH --time=00:15:00
#SBATCH --output=results/logs/q1_en_supplement_%j.out
#SBATCH --error=results/logs/q1_en_supplement_%j.err

set -euo pipefail

echo "=== Clean English Supplementation (E1) ==="
echo "Job ID: ${SLURM_JOB_ID}"
echo "Start: $(date)"

source .venv/bin/activate

# Step 1: Build clean supplement (no gold answer leakage)
echo "--- Building clean EN supplement ---"
python scripts/build_english_supplement_clean.py \
    --eval-file data/eval/manual_eval_v5.jsonl \
    --base-corpus data/processed/corpus.jsonl \
    --output data/processed/supplementary_en_clean.jsonl \
    --seed 42

# Step 2: Merge into supplemented corpus
echo "--- Merging EN supplement into corpus ---"
python -c "
import json, sys
from pathlib import Path
sys.path.insert(0, '.')
from src.utils import read_jsonl, write_jsonl

base = read_jsonl(Path('data/processed/corpus.jsonl'))
supp = read_jsonl(Path('data/processed/supplementary_en_clean.jsonl'))
merged = base + supp
output = Path('data/processed/corpus_en_supplemented.jsonl')
write_jsonl(output, merged)
print(f'Merged: {len(base)} base + {len(supp)} supplement = {len(merged)} total')
"

echo "=== Complete: $(date) ==="
