# Session Progress Report

## Completed
- Inspected the Isambard environment from inside the project directory.
- Created the core repository files, configs, prompts, scripts, and Slurm templates.
- Bootstrapped a project-local Python 3.11 virtual environment using cray-python/3.11.7.
- Installed the minimum Python dependencies needed for dataset loading and the smoke pipeline.
- Downloaded tydiqa and yakhyo/uz-wiki into data/raw/.
- Built a smoke corpus with 80 normalized documents and a smoke evaluation set with 30 examples.
- Built one smoke vector index in data/indexes/smoke_index/.
- Ran one smoke evaluation and wrote outputs under results/eval_20260308T145506Z_35149641e9b2/.
- Validated Slurm templates with sbatch --test-only.

## Results
- grounded_answer_score: 1.0
- hallucination_rate: 0.0
- unsupported_claim_rate: 0.0
- retrieval_recall_at_k: 0.9667

## Failures And Constraints
- miracl/miracl failed under the installed datasets stack because dataset scripts are no longer supported in this loader path.
- GPU visibility was not available from the login node, so accelerator checks still need a scheduled job allocation.
- The current smoke evaluation set is synthetic and Uzbek-heavy because the available fetched corpus source was yakhyo/uz-wiki.

## Recommended Next Commands
- cd /home/u6ef/rajantripathi.u6ef/soas_rag_eval
- module load cray-python/3.11.7
- source .venv/bin/activate
- python scripts/fetch_datasets.py --config configs/base.yaml
- python scripts/build_corpus.py --config configs/exp_smoke.yaml
- python scripts/build_index.py --config configs/exp_smoke.yaml
- python scripts/run_eval.py --config configs/exp_smoke.yaml
- sbatch slurm/eval_smoke.sbatch
