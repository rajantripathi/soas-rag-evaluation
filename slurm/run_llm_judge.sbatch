#!/bin/bash
#SBATCH --job-name=llm_judge
#SBATCH --output=logs/llm_judge_%j.out
#SBATCH --error=logs/llm_judge_%j.err
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --gres=gpu:1

set -euo pipefail
mkdir -p logs results/eval_llm_judge
module load cray-python/3.11.7 || true
source .venv/bin/activate

echo "Starting LLM-as-judge evaluation..."
date

# Use the best experiment run (will need to update this path after eval completes)
python scripts/run_llm_judge.py \
  --predictions results/eval_20260308T212757Z_65999103ae4c/predictions.jsonl \
  --output results/eval_llm_judge/scores.jsonl \
  --model mistralai/Mistral-7B-Instruct-v0.3 \
  --n-items 100

echo "LLM judge evaluation completed!"
date
