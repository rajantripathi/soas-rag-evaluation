# Manual Eval v2 Chunking Comparison

## Experiment Setup
- Evaluation file: data/eval/manual_eval_v2.jsonl
- Retrieval mode: vector
- Prompt style: grounded
- Conditions: baseline document chunks, chunk_small (256/64), chunk_smaller (128/32)
- All other parameters held fixed

## Overall Results
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 200 | 1.0000 | 0.0000 | 0.4900 |
| chunk_small | 200 | 1.0000 | 0.0000 | 0.4850 |
| chunk_smaller | 200 | 1.0000 | 0.0000 | 0.4850 |

## English Results
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 100 | 1.0000 | 0.0000 | 0.6100 |
| chunk_small | 100 | 1.0000 | 0.0000 | 0.6200 |
| chunk_smaller | 100 | 1.0000 | 0.0000 | 0.6200 |

## Uzbek Results
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 100 | 1.0000 | 0.0000 | 0.3700 |
| chunk_small | 100 | 1.0000 | 0.0000 | 0.3500 |
| chunk_smaller | 100 | 1.0000 | 0.0000 | 0.3500 |

## English Governance Results
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 25 | 1.0000 | 0.0000 | 0.7600 |
| chunk_small | 25 | 1.0000 | 0.0000 | 0.7600 |
| chunk_smaller | 25 | 1.0000 | 0.0000 | 0.8000 |

## English History Results
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 25 | 1.0000 | 0.0000 | 0.3600 |
| chunk_small | 25 | 1.0000 | 0.0000 | 0.4000 |
| chunk_smaller | 25 | 1.0000 | 0.0000 | 0.4000 |

## English Institutions Results
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 25 | 1.0000 | 0.0000 | 0.3200 |
| chunk_small | 25 | 1.0000 | 0.0000 | 0.3200 |
| chunk_smaller | 25 | 1.0000 | 0.0000 | 0.3200 |

## English Culture Results
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 25 | 1.0000 | 0.0000 | 1.0000 |
| chunk_small | 25 | 1.0000 | 0.0000 | 1.0000 |
| chunk_smaller | 25 | 1.0000 | 0.0000 | 0.9600 |

## Uzbek Governance Results
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 25 | 1.0000 | 0.0000 | 0.9200 |
| chunk_small | 25 | 1.0000 | 0.0000 | 0.8400 |
| chunk_smaller | 25 | 1.0000 | 0.0000 | 0.8400 |

## Uzbek History Results
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 25 | 1.0000 | 0.0000 | 0.1600 |
| chunk_small | 25 | 1.0000 | 0.0000 | 0.1600 |
| chunk_smaller | 25 | 1.0000 | 0.0000 | 0.1600 |

## Uzbek Institutions Results
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 25 | 1.0000 | 0.0000 | 0.1200 |
| chunk_small | 25 | 1.0000 | 0.0000 | 0.1200 |
| chunk_smaller | 25 | 1.0000 | 0.0000 | 0.1200 |

## Uzbek Culture Results
| Condition | Examples | Grounded | Hallucination | Recall@k |
| --- | ---: | ---: | ---: | ---: |
| baseline | 25 | 1.0000 | 0.0000 | 0.2800 |
| chunk_small | 25 | 1.0000 | 0.0000 | 0.2800 |
| chunk_smaller | 25 | 1.0000 | 0.0000 | 0.2800 |

## Key Findings
- Uzbek history recall@k: baseline=0.1600, chunk_small=0.1600, chunk_smaller=0.1600
- Uzbek institutions recall@k: baseline=0.1200, chunk_small=0.1200, chunk_smaller=0.1200
- Improvements should be interpreted cautiously because the current generator/scorer remain heuristic.
