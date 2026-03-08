# Culturally Grounded Multilingual RAG Evaluation

This repository builds and runs a conservative multilingual RAG evaluation pipeline on Isambard.

## Scope

- Download datasets directly on Isambard into `data/raw/`
- Build a normalized smoke corpus into `data/processed/`
- Build a vector index into `data/indexes/`
- Run a smoke evaluation and write outputs under `results/`
- Prepare Slurm scripts for repeatable larger runs

## Project Layout

- `configs/`: YAML experiment configuration
- `data/raw/`: raw downloaded datasets
- `data/processed/`: normalized documents and chunked corpora
- `data/eval/`: evaluation examples
- `data/indexes/`: saved indexes
- `scripts/`: CLI entrypoints
- `src/`: library code
- `prompts/`: prompt templates
- `slurm/`: batch job templates
- `results/reports/`: progress reports and summaries
- `results/logs/`: run logs and command logs

## Isambard Setup

```bash
bash scripts/check_env.sh
bash scripts/bootstrap_env.sh
source .venv/bin/activate
python scripts/fetch_datasets.py --config configs/base.yaml
python scripts/build_corpus.py --config configs/exp_smoke.yaml
python scripts/build_index.py --config configs/exp_smoke.yaml
python scripts/run_eval.py --config configs/exp_smoke.yaml
python scripts/summarize_runs.py --results-dir results
```

## Slurm

Smoke evaluation:

```bash
sbatch slurm/eval_smoke.sbatch
```

Index build:

```bash
sbatch slurm/build_index.sbatch
```

Array evaluation:

```bash
sbatch slurm/eval_array.sbatch
```

Aggregation:

```bash
sbatch slurm/aggregate.sbatch
```

## Notes

- Outputs are append-only and timestamped.
- The default smoke path uses a deterministic local generator to avoid secrets and fragile model installs.
- Retrieval uses a conservative hashed bag-of-words vector index for the first smoke path.
