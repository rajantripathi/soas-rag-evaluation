#!/bin/bash
#SBATCH --job-name=q1-en-supp
#SBATCH --account=u6ef
#SBATCH --partition=workq
#SBATCH --nodes=1
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --output=results/logs/q1_en_supplement_%j.out
#SBATCH --error=results/logs/q1_en_supplement_%j.err

set -euo pipefail
mkdir -p results/logs

echo "=== Clean English Supplementation (E1) ==="
echo "Job ID: ${SLURM_JOB_ID}"
echo "Node: $(hostname)"
echo "Start: $(date)"

module load cray-python/3.11.7 || true
source .venv/bin/activate

# Step 1: Build clean supplement (no gold_answer leakage)
echo "--- Building clean English supplement ---"
python scripts/build_english_supplement_clean.py \
    --eval-file data/eval/manual_eval_v5.jsonl \
    --base-corpus data/processed/corpus_manual_v1.jsonl \
    --uz-supplement data/processed/supplementary_uz_v2.jsonl \
    --output data/processed/supplementary_en_clean.jsonl

# Step 2: Merge into supplemented corpus
echo "--- Merging corpus ---"
python -c "
from src.utils import read_jsonl, write_jsonl
from pathlib import Path
base = read_jsonl(Path('data/processed/corpus_manual_v1.jsonl'))
uz_supp = read_jsonl(Path('data/processed/supplementary_uz_v2.jsonl'))
en_supp = read_jsonl(Path('data/processed/supplementary_en_clean.jsonl'))
merged = base + uz_supp + en_supp
output = Path('data/processed/corpus_manual_v1_full_supp_clean.jsonl')
write_jsonl(output, merged)
print(f'Merged: {len(base)} base + {len(uz_supp)} UZ supp + {len(en_supp)} EN supp = {len(merged)} total')
"

# Step 3: Run retrieval on supplemented corpus with best model (e5-large)
echo "--- Running retrieval on supplemented corpus ---"
python scripts/run_eval.py \
    --config configs/exp_manual_v2_e5_full_supp.yaml \
    2>&1 | tail -20

echo "=== Complete: $(date) ==="
