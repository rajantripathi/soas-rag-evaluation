# Experiment Program
Project: English-Uzbek Retrieval Evaluation

Goal
Evaluate retrieval against intended source-document identifiers for culturally
grounded English and Uzbek questions. Generated-answer quality is out of scope
for the validated results.

Languages
- English
- Uzbek

Datasets
1. MIRACL retrieval dataset
2. TyDi QA multilingual QA
3. Uzbek Wikipedia corpus
4. Optional: Lex.uz legal corpus

Experiment Variables
retrieval_mode:
  - none
  - vector

chunk_size:
  - 256
  - 512

chunk_overlap:
  - 32
  - 64

top_k:
  - 3
  - 5

prompt_style:
  - baseline
  - grounded

Evaluation Metrics

Primary
- retrieval_recall_at_k

Secondary
- hallucination_rate
- unsupported_claim_rate
- latency

The grounded-answer, hallucination, and unsupported-claim scores are heuristic
diagnostics produced with a generation stub. No human or LLM-as-judge evaluation
has been completed.

Experiment Rules

1. All experiments must be config driven
2. Never overwrite previous experiment outputs
3. Every run must produce:
   - JSONL outputs
   - CSV metrics
   - experiment metadata
4. Raw datasets must never be modified
5. New experiments must create new folders under results/
6. Small smoke test must pass before running large batch jobs

Execution Phases

Phase 1
Environment setup and dataset download

Phase 2
Corpus preprocessing and chunking

Phase 3
Vector index construction

Phase 4
Baseline evaluation

Phase 5
Full experiment matrix

Phase 6
Aggregation and report generation
