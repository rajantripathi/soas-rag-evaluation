# Culturally Grounded Multilingual RAG Evaluation: Corpus Coverage Report

## Setup
- Retrieval model: `intfloat/multilingual-e5-large`
- Prompting: grounded prompt
- Best corpus condition: expanded Uzbek supplement v2
- `manual_eval_v4` size: 400 items, balanced as 50 items per language-domain cell
- `manual_eval_v4` preserves all `manual_eval_v2` items and adds one deterministic alternate phrasing per original item

## Baseline vs Supplement Comparison on manual_eval_v2
## Overall Recall on manual_eval_v2
| Condition | Recall@k |
| --- | ---: |
| baseline corpus | 0.5100 |
| supplement v1 | 0.7150 |
| supplement v2 | 0.8050 |

## Uzbek Domain Recall on manual_eval_v2
| Condition | Recall@k |
| --- | ---: |
| baseline_history | 0.1600 |
| supplement_v1_history | 1.0000 |
| supplement_v2_history | 0.9600 |
| baseline_institutions | 0.1200 |
| supplement_v1_institutions | 0.9200 |
| supplement_v2_institutions | 0.9600 |
| baseline_culture | 0.2800 |
| supplement_v1_culture | 0.2800 |
| supplement_v2_culture | 1.0000 |

## manual_eval_v4 Results with Best Setup
## Overall Recall on manual_eval_v4
| Condition | Recall@k |
| --- | ---: |
| supplement v2 + manual_eval_v4 | 0.7950 |

## English Recall on manual_eval_v4
| Condition | Recall@k |
| --- | ---: |
| supplement v2 + manual_eval_v4 | 0.6300 |

## Uzbek Recall on manual_eval_v4
| Condition | Recall@k |
| --- | ---: |
| supplement v2 + manual_eval_v4 | 0.9600 |

## Domain Recall on manual_eval_v4: governance
| Condition | Recall@k |
| --- | ---: |
| english | 0.8000 |
| uzbek | 0.9800 |

## Domain Recall on manual_eval_v4: history
| Condition | Recall@k |
| --- | ---: |
| english | 0.4000 |
| uzbek | 0.9600 |

## Domain Recall on manual_eval_v4: institutions
| Condition | Recall@k |
| --- | ---: |
| english | 0.3200 |
| uzbek | 0.9600 |

## Domain Recall on manual_eval_v4: culture
| Condition | Recall@k |
| --- | ---: |
| english | 1.0000 |
| uzbek | 0.9400 |

## Analysis
- Baseline versus supplement runs show that corpus coverage, not prompt choice or chunk size alone, is the dominant bottleneck for culturally grounded Uzbek retrieval.
- Targeted cultural knowledge sources improve retrieval most when they add the exact local entities, institutions, and historical subjects that the baseline corpus does not contain.
- Supplement v1 demonstrated that a small curated corpus patch can resolve hard Uzbek history and institutions gaps.
- Supplement v2 showed that a more general structured-source expansion from Uzbek Wikipedia can extend those gains to culture while preserving English performance.
- This implies that knowledge representation in AI systems is partly a corpus design problem: if culturally specific knowledge is absent or weakly represented, retrieval quality will systematically underperform for those communities.
- For culturally grounded AI systems, reproducible local supplements are a practical mechanism for improving grounding without destabilizing the rest of the pipeline.
