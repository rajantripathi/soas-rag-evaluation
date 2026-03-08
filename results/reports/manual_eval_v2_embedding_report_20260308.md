# Manual Eval v2 Embedding Comparison

## Experiment Setup
- Evaluation file: data/eval/manual_eval_v2.jsonl
- Corpus and chunking: unchanged baseline corpus_manual_v1.jsonl
- Retrieval mode: vector
- Prompt style: grounded
- Conditions: baseline simple_vector, intfloat/multilingual-e5-large, sentence-transformers/paraphrase-multilingual-mpnet-base-v2
- All other parameters held fixed

## Overall Results
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 200 | 1.0000 | 0.0000 | 0.4900 |
| e5_large | 200 | 1.0000 | 0.0000 | 0.5100 |
| mpnet | 200 | 1.0000 | 0.0000 | 0.4350 |

## English Results
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 100 | 1.0000 | 0.0000 | 0.6100 |
| e5_large | 100 | 1.0000 | 0.0000 | 0.6300 |
| mpnet | 100 | 1.0000 | 0.0000 | 0.6200 |

## Uzbek Results
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 100 | 1.0000 | 0.0000 | 0.3700 |
| e5_large | 100 | 1.0000 | 0.0000 | 0.3900 |
| mpnet | 100 | 1.0000 | 0.0000 | 0.2500 |

## English Governance Results
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 25 | 1.0000 | 0.0000 | 0.7600 |
| e5_large | 25 | 1.0000 | 0.0000 | 0.8000 |
| mpnet | 25 | 1.0000 | 0.0000 | 0.8000 |

## English History Results
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 25 | 1.0000 | 0.0000 | 0.3600 |
| e5_large | 25 | 1.0000 | 0.0000 | 0.4000 |
| mpnet | 25 | 1.0000 | 0.0000 | 0.4000 |

## English Institutions Results
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 25 | 1.0000 | 0.0000 | 0.3200 |
| e5_large | 25 | 1.0000 | 0.0000 | 0.3200 |
| mpnet | 25 | 1.0000 | 0.0000 | 0.3200 |

## English Culture Results
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 25 | 1.0000 | 0.0000 | 1.0000 |
| e5_large | 25 | 1.0000 | 0.0000 | 1.0000 |
| mpnet | 25 | 1.0000 | 0.0000 | 0.9600 |

## Uzbek Governance Results
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 25 | 1.0000 | 0.0000 | 0.9200 |
| e5_large | 25 | 1.0000 | 0.0000 | 1.0000 |
| mpnet | 25 | 1.0000 | 0.0000 | 0.6000 |

## Uzbek History Results
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 25 | 1.0000 | 0.0000 | 0.1600 |
| e5_large | 25 | 1.0000 | 0.0000 | 0.1600 |
| mpnet | 25 | 1.0000 | 0.0000 | 0.1200 |

## Uzbek Institutions Results
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 25 | 1.0000 | 0.0000 | 0.1200 |
| e5_large | 25 | 1.0000 | 0.0000 | 0.1200 |
| mpnet | 25 | 1.0000 | 0.0000 | 0.0800 |

## Uzbek Culture Results
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 25 | 1.0000 | 0.0000 | 0.2800 |
| e5_large | 25 | 1.0000 | 0.0000 | 0.2800 |
| mpnet | 25 | 1.0000 | 0.0000 | 0.2000 |

## Key Findings
- Uzbek history recall@k: baseline=0.1600, e5_large=0.1600, mpnet=0.1200
- Uzbek institutions recall@k: baseline=0.1200, e5_large=0.1200, mpnet=0.0800
