# Isambard and Repository Locations

## Known Locations

| Environment | Location |
| --- | --- |
| Local active Git repo | `/Users/rajantripathi/Projects/soas-rag-evaluation` |
| GitHub remote | `https://github.com/rajantripathi/soas-rag-evaluation.git` |
| Isambard working path referenced by scripts | `/home/u6ef/rajantripathi.u6ef/soas_rag_eval` |
| Isambard project acknowledgement | `u6ef` |
| Local loose staging scripts | `/Users/rajantripathi/soas-rag-evaluation-staging` |

The staging directory contains older loose experiment scripts and Slurm templates. The active repository is the Git-managed project under `/Users/rajantripathi/Projects/soas-rag-evaluation`.

## Isambard Verification Note

From the current local environment, the `isambard` SSH hostname was not resolvable, so the cluster filesystem was not directly inspected during this documentation update. The Isambard path above is taken from tracked scripts and reports in the repository.

## Expected Cluster Workflow

```bash
cd /home/u6ef/rajantripathi.u6ef/soas_rag_eval
bash scripts/check_env.sh
bash scripts/bootstrap_env.sh
source .venv/bin/activate
```

Smoke run:

```bash
python scripts/fetch_datasets.py --config configs/base.yaml
python scripts/build_corpus.py --config configs/exp_smoke.yaml
python scripts/build_index.py --config configs/exp_smoke.yaml
python scripts/run_eval.py --config configs/exp_smoke.yaml
```

Representative Slurm pattern:

```bash
sbatch slurm/build_index.sbatch
sbatch slurm/eval_array.sbatch
sbatch slurm/aggregate.sbatch
```

## Artifact Policy

Tracked in Git:

- source code
- configs
- Slurm templates
- docs
- selected reports
- figures
- small evaluation samples

Not tracked in Git:

- full raw datasets
- processed corpora
- generated indexes
- full run directories
- cluster logs
- model caches

This split keeps the public repository lightweight while preserving enough information to reproduce the methodology on the cluster.

## Rehydration Checklist

1. Clone the GitHub repository into the Isambard working directory.
2. Bootstrap the Python environment with `scripts/bootstrap_env.sh`.
3. Fetch or stage datasets according to `configs/base.yaml`.
4. Rebuild corpus JSONL files.
5. Rebuild indexes for the target experiment config.
6. Run evaluation jobs.
7. Regenerate reports with `scripts/generate_research_outputs.py`.
8. Confirm the run logs include config hash and Git commit.

## Practical Notes

- Embedding retrieval expects SentenceTransformer models to be available locally on the cluster when `local_files_only=True` is used.
- Large run outputs should remain on Isambard storage and be summarized into tracked reports.
- Any new supplement must be checked for leakage against evaluation `gold_answer` fields before results are reported.
