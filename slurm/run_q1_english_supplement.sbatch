#!/bin/bash
#SBATCH --job-name=q1-en-supp
#SBATCH --output=logs/q1_en_supplement_%j.out
#SBATCH --error=logs/q1_en_supplement_%j.err
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G

set -euo pipefail
mkdir -p logs

echo "=== E1: Clean English Supplementation ==="
echo "Job ID: ${SLURM_JOB_ID:-local}"
echo "Start: $(date)"

source .venv/bin/activate

# Step 1: Build clean English supplement (no gold_answer leakage)
echo "--- Building clean EN supplement ---"
python scripts/build_english_supplement_clean.py \
    --eval-file data/eval/manual_eval_v5.jsonl \
    --base-corpus data/processed/corpus_manual_v1.jsonl \
    --uz-supplement data/processed/supplementary_uz_v2.jsonl \
    --output data/processed/supplementary_en_clean.jsonl

# Step 2: Merge into fully supplemented corpus
echo "--- Merging corpus ---"
python -c "
import json, sys
from pathlib import Path
def read_jsonl(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]
base = read_jsonl('data/processed/corpus_manual_v1.jsonl')
uz_supp = read_jsonl('data/processed/supplementary_uz_v2.jsonl')
en_supp = read_jsonl('data/processed/supplementary_en_clean.jsonl')
merged = base + uz_supp + en_supp
with open('data/processed/corpus_full_supp_clean.jsonl', 'w') as f:
    for row in merged:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')
print(f'Merged: {len(base)} base + {len(uz_supp)} UZ + {len(en_supp)} EN = {len(merged)} total')
"

echo "=== Complete: $(date) ==="
