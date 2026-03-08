# Manual Eval v2 Domain Analysis

## Setup
- Evaluation file: data/eval/manual_eval_v2.jsonl
- Runs analyzed: none, vector, vector plus grounded prompt
- Metrics shown: grounded_answer_score, hallucination_rate, unsupported_claim_rate, retrieval_recall_at_k

## English Domain Results
| Domain | Run | Examples | Grounded | Hallucination | Unsupported | Recall@k |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| governance | none | 25 | 0.2802 | 1.0000 | 0.0000 | 0.0000 |
| governance | vector | 25 | 0.9820 | 0.0000 | 0.0000 | 0.7600 |
| governance | vector_grounded | 25 | 1.0000 | 0.0000 | 0.0000 | 0.7600 |
| history | none | 25 | 0.2892 | 1.0000 | 0.0000 | 0.0000 |
| history | vector | 25 | 0.9738 | 0.0000 | 0.0000 | 0.3600 |
| history | vector_grounded | 25 | 1.0000 | 0.0000 | 0.0000 | 0.3600 |
| institutions | none | 25 | 0.3123 | 1.0000 | 0.0000 | 0.0000 |
| institutions | vector | 25 | 0.9773 | 0.0000 | 0.0000 | 0.3200 |
| institutions | vector_grounded | 25 | 1.0000 | 0.0000 | 0.0000 | 0.3200 |
| culture | none | 25 | 0.3108 | 1.0000 | 0.0000 | 0.0000 |
| culture | vector | 25 | 0.9849 | 0.0000 | 0.0000 | 1.0000 |
| culture | vector_grounded | 25 | 1.0000 | 0.0000 | 0.0000 | 1.0000 |

## Uzbek Domain Results
| Domain | Run | Examples | Grounded | Hallucination | Unsupported | Recall@k |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| governance | none | 25 | 0.1929 | 1.0000 | 0.0000 | 0.0000 |
| governance | vector | 25 | 0.9775 | 0.0000 | 0.0000 | 0.9200 |
| governance | vector_grounded | 25 | 1.0000 | 0.0000 | 0.0000 | 0.9200 |
| history | none | 25 | 0.1758 | 1.0000 | 0.0000 | 0.0000 |
| history | vector | 25 | 0.9937 | 0.0000 | 0.0000 | 0.1600 |
| history | vector_grounded | 25 | 1.0000 | 0.0000 | 0.0000 | 0.1600 |
| institutions | none | 25 | 0.1604 | 1.0000 | 0.0000 | 0.0000 |
| institutions | vector | 25 | 0.9625 | 0.0000 | 0.0000 | 0.1200 |
| institutions | vector_grounded | 25 | 1.0000 | 0.0000 | 0.0000 | 0.1200 |
| culture | none | 25 | 0.1956 | 1.0000 | 0.0000 | 0.0000 |
| culture | vector | 25 | 0.9877 | 0.0000 | 0.0000 | 0.2800 |
| culture | vector_grounded | 25 | 1.0000 | 0.0000 | 0.0000 | 0.2800 |

## Comparison Summary
- Vector retrieval improves every domain over the none baseline for both languages.
- The English vector recall average is 0.6100; the Uzbek vector recall average is 0.3700.
- The grounded prompt consistently increases groundedness relative to plain vector retrieval in this stub setup.

## Likely Causes Of The Uzbek Recall Gap
- Corpus size and composition: the Uzbek side relies mainly on a limited Wikipedia slice with fewer semantically redundant passages than the English side.
- Retrieval representation: the current simple token-based vector index is more brittle for Uzbek morphology and orthography than for English.
- Chunking strategy: each Uzbek document is currently treated as a single large chunk, which makes lexical mismatch more costly and reduces ranking precision.

## Recommended Uzbek Retrieval Experiments
- Experiment 1: re-chunk the Uzbek corpus into smaller overlapping chunks, for example 128-256 token windows with overlap, and rerun the same manual_eval_v2 vector comparison.
- Experiment 2: swap the current simple vector backend for a multilingual embedding model with explicit Uzbek coverage, then compare Uzbek recall by domain against the current baseline.
