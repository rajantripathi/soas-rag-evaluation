# Manual Eval v2 Comparison

## Experiment Setup
- Evaluation file: data/eval/manual_eval_v2.jsonl
- Total examples: 200
- Language balance: 100 English, 100 Uzbek
- Domain balance per language: 25 governance, 25 history, 25 institutions, 25 culture
- Fixed parameters: same corpus, same index, same stub generator, same retrieval backend, same top_k
- Conditions: none, vector, vector plus grounded prompt

## Overall Results
| Run | Examples | Grounded | Hallucination | Unsupported | Recall@k |
| --- | ---: | ---: | ---: | ---: | ---: |
| none | 200 | 0.2396 | 1.0000 | 0.0000 | 0.0000 |
| vector | 200 | 0.9799 | 0.0000 | 0.0000 | 0.4900 |
| vector_grounded | 200 | 1.0000 | 0.0000 | 0.0000 | 0.4900 |

## English Results
| Run | Examples | Grounded | Hallucination | Unsupported | Recall@k |
| --- | ---: | ---: | ---: | ---: | ---: |
| none | 100 | 0.2981 | 1.0000 | 0.0000 | 0.0000 |
| vector | 100 | 0.9795 | 0.0000 | 0.0000 | 0.6100 |
| vector_grounded | 100 | 1.0000 | 0.0000 | 0.0000 | 0.6100 |

## Uzbek Results
| Run | Examples | Grounded | Hallucination | Unsupported | Recall@k |
| --- | ---: | ---: | ---: | ---: | ---: |
| none | 100 | 0.1812 | 1.0000 | 0.0000 | 0.0000 |
| vector | 100 | 0.9803 | 0.0000 | 0.0000 | 0.3700 |
| vector_grounded | 100 | 1.0000 | 0.0000 | 0.0000 | 0.3700 |

## Comparison Summary
- The no-retrieval baseline uses the stub fallback text, so recall stays at zero and hallucination stays maximal.
- Vector retrieval materially improves grounding by returning the intended source document for most items.
- The grounded prompt variant is strongest in this stub setup because it trims the answer to the first retrieved sentence.

## Caveats
- Results come from a deterministic stub generator and heuristic metrics rather than a model-backed judge.
- The benchmark is manually curated and still relatively small despite expansion to 200 items.
- English coverage depends on TyDi English plus the MIRACL raw-file workaround rather than a broader production corpus.

## Recommended Next Steps
- Add a stronger generation backend and rerun the same comparison.
- Add Slurm templates for repeatable manual_eval_v2 comparison jobs.
- Expand culturally grounded English and Uzbek corpora beyond the current staged sources.
