# Historical Isambard Reproducibility Notes

## Public and Environment-Specific Locations

| Environment | Location |
| --- | --- |
| GitHub remote | `https://github.com/rajantripathi/soas-rag-evaluation.git` |
| Working directory | `<project-directory>` |
| Historical Isambard working directory | site- and account-specific; not published |
| Isambard project acknowledgement | `u6ef` |

The computations reported in this repository used Isambard-AI under project `u6ef`. This is a historical reproducibility note, not a statement of current or future access. Users must obtain their own authorised compute allocation and adapt paths and scheduler settings to their environment.

## Isambard Verification Note

No new Isambard run was performed for the public-release audit. The checked-in reports describe the historical experimental results; reproduction requires independent access to a suitable environment and the excluded source corpora and indexes.

## Expected Cluster Workflow

```bash
cd <project-directory>
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
- the 400-row retrieval-only pilot benchmark and preview sample

Not tracked in Git:

- full raw datasets
- processed corpora
- generated indexes
- full run directories
- cluster logs
- model caches

This split keeps the public repository lightweight and documents the method, but it is not a complete archival snapshot of the historical cluster state.

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
- Any new supplement must be checked for leakage against internal answer-bearing evaluation fields before results are reported.
