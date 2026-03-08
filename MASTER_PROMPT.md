You are my end-to-end research engineering agent working inside an Isambard project directory.

Project title:
Culturally Grounded Multilingual RAG Evaluation for Global South Knowledge

Important constraints:
- Everything must be stored and run on Isambard only.
- Do not assume local laptop execution.
- Assume Slurm for batch execution.
- Keep all paths relative to this project directory unless cluster storage requires otherwise.
- Do not hardcode secrets.
- Keep everything config driven and reproducible.
- Never overwrite previous experiment outputs.
- All outputs must be written under results/, data/, logs/, or cluster-safe subdirectories inside this repo.
- Prefer Python scripts with clear CLI arguments.
- Use smoke tests before large runs.
- If package compatibility becomes an issue, adapt conservatively.

Primary goals:
1. Inspect the environment first.
2. Scaffold the missing repository files.
3. Create a reliable Python environment.
4. Download datasets directly on Isambard into data/raw.
5. Build a processed corpus.
6. Build one vector index.
7. Run one smoke evaluation.
8. Prepare Slurm jobs for larger experiments.
9. Save all outputs and logs on Isambard.
10. Write a short progress report into results/reports/.

Required repo structure:
- README.md
- experiment_program.md
- MASTER_PROMPT.md
- pyproject.toml
- .gitignore
- configs/
- data/raw/
- data/processed/
- data/eval/
- data/indexes/
- scripts/
- src/
- prompts/
- slurm/
- results/reports/
- results/logs/

Required files to create if missing:
- README.md
- pyproject.toml
- .gitignore
- scripts/check_env.sh
- scripts/bootstrap_env.sh
- scripts/build_corpus.py
- scripts/chunk_corpus.py
- scripts/build_index.py
- scripts/run_eval.py
- scripts/score_results.py
- scripts/summarize_runs.py
- src/datasets.py
- src/retrieval.py
- src/generation.py
- src/evaluation.py
- src/orchestration.py
- src/utils.py
- prompts/baseline.txt
- prompts/grounded.txt
- slurm/eval_smoke.sbatch
- slurm/build_index.sbatch
- slurm/aggregate.sbatch
- configs/base.yaml
- configs/exp_smoke.yaml

Dataset priorities:
- miracl/miracl
- tydiqa primary_task
- yakhyo/uz-wiki if available
If one fails, continue gracefully and record failure.

Execution order:
A. Inspect environment and summarize findings
B. Scaffold missing files
C. Create environment
D. Install dependencies
E. Run dataset fetch script
F. Build smoke corpus
G. Build one smoke index
H. Run one smoke evaluation
I. Prepare Slurm job files
J. Write a progress report

Rules:
- Do not pretend something succeeded if it failed.
- Show exact commands before important actions.
- Keep code simple and readable.
- Use JSONL and CSV outputs.
- Add help text to scripts.
- Make each script rerunnable.

Begin now with environment inspection and planning.
