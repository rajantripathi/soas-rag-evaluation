# Manual Eval v2 Corpus Expansion Report

## Experiment Setup
- Evaluation file: data/eval/manual_eval_v2.jsonl
- Embedding model: intfloat/multilingual-e5-large
- Baseline corpus: data/processed/corpus_manual_v1.jsonl
- Expanded corpus: data/processed/corpus_manual_v1_uzsupp_v1.jsonl
- Supplement path: data/processed/supplementary_uz_history_institutions_v1.jsonl
- Conditions: baseline vector, baseline vector+grounded, expanded vector, expanded vector+grounded

## Supplementary Sources Added
- A small manual curated supplement was added for Uzbek history and institutions only.
- The supplement is stored separately from the baseline corpus and merged into a new expanded corpus file.
- The added entries target missing named entities, institutional descriptions, and short historical definitions tied to the weak-domain eval items.

## Overall
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline_vector | 200 | 0.9814 | 0.0000 | 0.5100 |
| baseline_grounded | 200 | 1.0000 | 0.0000 | 0.5100 |
| expanded_vector | 200 | 0.9845 | 0.0000 | 0.7150 |
| expanded_grounded | 200 | 1.0000 | 0.0000 | 0.7150 |

## En
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline_vector | 100 | 0.9824 | 0.0000 | 0.6300 |
| baseline_grounded | 100 | 1.0000 | 0.0000 | 0.6300 |
| expanded_vector | 100 | 0.9832 | 0.0000 | 0.6300 |
| expanded_grounded | 100 | 1.0000 | 0.0000 | 0.6300 |

## Uz
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline_vector | 100 | 0.9803 | 0.0000 | 0.3900 |
| baseline_grounded | 100 | 1.0000 | 0.0000 | 0.3900 |
| expanded_vector | 100 | 0.9859 | 0.0000 | 0.8000 |
| expanded_grounded | 100 | 1.0000 | 0.0000 | 0.8000 |

## En Governance
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline_vector | 25 | 0.9809 | 0.0000 | 0.8000 |
| baseline_grounded | 25 | 1.0000 | 0.0000 | 0.8000 |
| expanded_vector | 25 | 0.9809 | 0.0000 | 0.8000 |
| expanded_grounded | 25 | 1.0000 | 0.0000 | 0.8000 |

## En History
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline_vector | 25 | 0.9815 | 0.0000 | 0.4000 |
| baseline_grounded | 25 | 1.0000 | 0.0000 | 0.4000 |
| expanded_vector | 25 | 0.9846 | 0.0000 | 0.4000 |
| expanded_grounded | 25 | 1.0000 | 0.0000 | 0.4000 |

## En Institutions
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline_vector | 25 | 0.9823 | 0.0000 | 0.3200 |
| baseline_grounded | 25 | 1.0000 | 0.0000 | 0.3200 |
| expanded_vector | 25 | 0.9823 | 0.0000 | 0.3200 |
| expanded_grounded | 25 | 1.0000 | 0.0000 | 0.3200 |

## En Culture
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline_vector | 25 | 0.9849 | 0.0000 | 1.0000 |
| baseline_grounded | 25 | 1.0000 | 0.0000 | 1.0000 |
| expanded_vector | 25 | 0.9849 | 0.0000 | 1.0000 |
| expanded_grounded | 25 | 1.0000 | 0.0000 | 1.0000 |

## Uz Governance
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline_vector | 25 | 0.9790 | 0.0000 | 1.0000 |
| baseline_grounded | 25 | 1.0000 | 0.0000 | 1.0000 |
| expanded_vector | 25 | 0.9790 | 0.0000 | 1.0000 |
| expanded_grounded | 25 | 1.0000 | 0.0000 | 1.0000 |

## Uz History
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline_vector | 25 | 0.9905 | 0.0000 | 0.1600 |
| baseline_grounded | 25 | 1.0000 | 0.0000 | 0.1600 |
| expanded_vector | 25 | 0.9883 | 0.0000 | 1.0000 |
| expanded_grounded | 25 | 1.0000 | 0.0000 | 1.0000 |

## Uz Institutions
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline_vector | 25 | 0.9695 | 0.0000 | 0.1200 |
| baseline_grounded | 25 | 1.0000 | 0.0000 | 0.1200 |
| expanded_vector | 25 | 0.9899 | 0.0000 | 0.9200 |
| expanded_grounded | 25 | 1.0000 | 0.0000 | 0.9200 |

## Uz Culture
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline_vector | 25 | 0.9823 | 0.0000 | 0.2800 |
| baseline_grounded | 25 | 1.0000 | 0.0000 | 0.2800 |
| expanded_vector | 25 | 0.9864 | 0.0000 | 0.2800 |
| expanded_grounded | 25 | 1.0000 | 0.0000 | 0.2800 |

## Summary
- Corpus coverage appears to be the main bottleneck because weak-domain misses previously aligned with absent gold source documents.
- The supplement adds targeted Uzbek history and institutions documents in a separate, normalized JSONL path.
- Uzbek history recall@k with grounded prompting changed from 0.1600 to 1.0000.
- Uzbek institutions recall@k with grounded prompting changed from 0.1200 to 0.9200.
- The main interpretive question is whether targeted corpus additions lift hard domains without degrading English or easier Uzbek domains.

## Implications for Culturally Grounded AI
- Multilingual retrieval quality can be dominated by corpus coverage before model choice becomes the limiting factor.
- For culturally grounded systems, weak-domain failures may reflect missing local knowledge sources rather than a generic multilingual embedding deficit.
- Small, explicit corpus interventions can materially improve grounding in underserved domains without changing the rest of the evaluation pipeline.
