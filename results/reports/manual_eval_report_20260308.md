# Manual Evaluation Update

## GitHub Push Status
- SSH authentication to GitHub succeeded from Isambard.
- Remote origin is git@github.com:rajantripathi/soas-rag-evaluation.git.
- The experiments branch is visible remotely at commit f78af30dfbdeb79576bc55cf0d84a4d09adf205d.
- Repository URL: https://github.com/rajantripathi/soas-rag-evaluation
- Branch URL: https://github.com/rajantripathi/soas-rag-evaluation/tree/experiments
- Note: the MIRACL compatibility and manual-eval changes from this session are on Isambard but have not been pushed yet.

## Dataset Status
- miracl/miracl failed through the datasets script loader because datasets 4.6.1 no longer supports dataset scripts.
- MIRACL was recovered through a compatible raw-file path using Hugging Face Hub downloads into data/raw/miracl_en/.
- tydiqa remains staged in data/raw/tydiqa_primary_task/.
- yakhyo/uz-wiki remains staged in data/raw/uz_wiki/.
- Manual corpus data/processed/corpus_manual_v1.jsonl contains 240 rows: 80 MIRACL English chunks, 80 TyDi English documents, and 80 Uzbek Wikipedia documents.

## Eval Set Status
- data/eval/manual_eval_v1.jsonl was created with 40 culturally grounded questions.
- Split: 20 English questions and 20 Uzbek questions.
- English questions are grounded in TyDi English documents present in the manual corpus.
- Uzbek questions are grounded in Uzbek Wikipedia documents present in the manual corpus.

## Experiment Results
- none baseline run: results/eval_20260308T154548Z_19d6866c6d0a/
  - grounded_answer_score: 0.2924
  - hallucination_rate: 1.0
  - unsupported_claim_rate: 0.0
  - retrieval_recall_at_k: 0.0
- vector run: results/eval_20260308T154548Z_5b61201a52be/
  - grounded_answer_score: 1.0
  - hallucination_rate: 0.0
  - unsupported_claim_rate: 0.0
  - retrieval_recall_at_k: 1.0
- In this deterministic stub setup, retrieval clearly improved grounding on the manual set because the retrieved top document matched the intended source document.

## Next Steps
- Commit and push the MIRACL compatibility and manual-eval changes if you want GitHub to reflect the new state.
- Replace the current heuristic generator and scorer with a stronger model-backed answerer and judge once credentials or a safe local backend are available.
- Expand MIRACL English coverage beyond the first shard if broader English retrieval coverage is needed.
- Add a Slurm job template for the manual none vs vector comparison when you want repeatable batch runs.
