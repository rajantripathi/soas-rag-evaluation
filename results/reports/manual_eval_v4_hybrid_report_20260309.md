# manual_eval_v4 Hybrid Retrieval Report

## Setup
- Corpus: data/processed/corpus_manual_v1_uzsupp_v2.jsonl
- Eval set: data/eval/manual_eval_v4.jsonl
- Embedding model: intfloat/multilingual-e5-large
- Prompting: grounded prompt
- Hybrid strategy: retrieve top-k from BM25 and top-k from vector, merge candidates, rerank by vector similarity

## Overall
| System | Recall@k |
| --- | ---: |
| vector_only | 0.7950 |
| bm25_only | 0.6700 |
| hybrid | 0.7950 |

## En
| System | Recall@k |
| --- | ---: |
| vector_only | 0.6300 |
| bm25_only | 0.6200 |
| hybrid | 0.6300 |

## Uz
| System | Recall@k |
| --- | ---: |
| vector_only | 0.9600 |
| bm25_only | 0.7200 |
| hybrid | 0.9600 |

## En Governance
| System | Recall@k |
| --- | ---: |
| vector_only | 0.8000 |
| bm25_only | 0.7800 |
| hybrid | 0.8000 |

## En History
| System | Recall@k |
| --- | ---: |
| vector_only | 0.4000 |
| bm25_only | 0.4000 |
| hybrid | 0.4000 |

## En Institutions
| System | Recall@k |
| --- | ---: |
| vector_only | 0.3200 |
| bm25_only | 0.3200 |
| hybrid | 0.3200 |

## En Culture
| System | Recall@k |
| --- | ---: |
| vector_only | 1.0000 |
| bm25_only | 0.9800 |
| hybrid | 1.0000 |

## Uz Governance
| System | Recall@k |
| --- | ---: |
| vector_only | 0.9800 |
| bm25_only | 0.6200 |
| hybrid | 0.9800 |

## Uz History
| System | Recall@k |
| --- | ---: |
| vector_only | 0.9600 |
| bm25_only | 0.8000 |
| hybrid | 0.9600 |

## Uz Institutions
| System | Recall@k |
| --- | ---: |
| vector_only | 0.9600 |
| bm25_only | 0.7200 |
| hybrid | 0.9600 |

## Uz Culture
| System | Recall@k |
| --- | ---: |
| vector_only | 0.9400 |
| bm25_only | 0.7400 |
| hybrid | 0.9400 |

## Summary
- Hybrid retrieval is useful only if lexical candidates recover relevant documents that vector retrieval misses.
- The main question is whether hybrid improves Uzbek recall without degrading English retrieval.
