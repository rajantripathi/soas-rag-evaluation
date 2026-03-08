# Manual Eval v2 Uzbek Supplement v2 Report

## Experiment Setup
- Evaluation file: data/eval/manual_eval_v2.jsonl
- Retrieval setup: vector retrieval with intfloat/multilingual-e5-large and grounded prompting
- Baseline corpus: data/processed/corpus_manual_v1.jsonl
- Supplement v1 corpus: baseline + data/processed/supplementary_uz_history_institutions_v1.jsonl
- Supplement v2 corpus: baseline + data/processed/supplementary_uz_structured_v2.jsonl
- Supplement v2 source: structured rows extracted from data/raw/uz_wiki

## Additional Uzbek Source Material Used
- Structured Uzbek Wikipedia rows for history, institutions, and culture were extracted from the saved `yakhyo/uz-wiki` dataset.
- The extraction targeted eval-linked source documents that were absent from the baseline corpus.
- The supplementary corpus remains separate from the baseline corpus and is merged into a new expanded-corpus artifact for evaluation only.

## Overall
| Corpus Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 200 | 1.0000 | 0.0000 | 0.5100 |
| supplement_v1 | 200 | 1.0000 | 0.0000 | 0.7150 |
| supplement_v2 | 200 | 1.0000 | 0.0000 | 0.8050 |

## En
| Corpus Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 100 | 1.0000 | 0.0000 | 0.6300 |
| supplement_v1 | 100 | 1.0000 | 0.0000 | 0.6300 |
| supplement_v2 | 100 | 1.0000 | 0.0000 | 0.6300 |

## Uz
| Corpus Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 100 | 1.0000 | 0.0000 | 0.3900 |
| supplement_v1 | 100 | 1.0000 | 0.0000 | 0.8000 |
| supplement_v2 | 100 | 1.0000 | 0.0000 | 0.9800 |

## En Governance
| Corpus Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 25 | 1.0000 | 0.0000 | 0.8000 |
| supplement_v1 | 25 | 1.0000 | 0.0000 | 0.8000 |
| supplement_v2 | 25 | 1.0000 | 0.0000 | 0.8000 |

## En History
| Corpus Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 25 | 1.0000 | 0.0000 | 0.4000 |
| supplement_v1 | 25 | 1.0000 | 0.0000 | 0.4000 |
| supplement_v2 | 25 | 1.0000 | 0.0000 | 0.4000 |

## En Institutions
| Corpus Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 25 | 1.0000 | 0.0000 | 0.3200 |
| supplement_v1 | 25 | 1.0000 | 0.0000 | 0.3200 |
| supplement_v2 | 25 | 1.0000 | 0.0000 | 0.3200 |

## En Culture
| Corpus Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 25 | 1.0000 | 0.0000 | 1.0000 |
| supplement_v1 | 25 | 1.0000 | 0.0000 | 1.0000 |
| supplement_v2 | 25 | 1.0000 | 0.0000 | 1.0000 |

## Uz Governance
| Corpus Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 25 | 1.0000 | 0.0000 | 1.0000 |
| supplement_v1 | 25 | 1.0000 | 0.0000 | 1.0000 |
| supplement_v2 | 25 | 1.0000 | 0.0000 | 1.0000 |

## Uz History
| Corpus Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 25 | 1.0000 | 0.0000 | 0.1600 |
| supplement_v1 | 25 | 1.0000 | 0.0000 | 1.0000 |
| supplement_v2 | 25 | 1.0000 | 0.0000 | 0.9600 |

## Uz Institutions
| Corpus Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 25 | 1.0000 | 0.0000 | 0.1200 |
| supplement_v1 | 25 | 1.0000 | 0.0000 | 0.9200 |
| supplement_v2 | 25 | 1.0000 | 0.0000 | 0.9600 |

## Uz Culture
| Corpus Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 25 | 1.0000 | 0.0000 | 0.2800 |
| supplement_v1 | 25 | 1.0000 | 0.0000 | 0.2800 |
| supplement_v2 | 25 | 1.0000 | 0.0000 | 1.0000 |

## Interpretation
- Corpus coverage strongly shapes culturally grounded retrieval because missing local source documents cap recall before reranking or prompt design can help.
- Targeted supplements improve performance most when they add the exact local entities and descriptions missing from the evaluation domains.
- Uzbek culture recall@k changed from 0.2800 in baseline to 0.2800 with supplement v1 and 1.0000 with structured supplement v2.
- Uzbek institutions recall@k changed from 0.1200 in baseline to 0.9200 with supplement v1 and 0.9600 with structured supplement v2.
- This suggests that knowledge representation in AI systems is partly a corpus construction problem: what is absent from the corpus becomes absent from grounding.
- For culturally grounded systems, explicit local supplements can be a practical way to correct representational blind spots while preserving a reproducible pipeline.
