# Retrieval Methodology

## Pipeline
The repository implements a config-driven experimental pipeline used historically on Isambard-AI:

1. inspect environment
2. stage datasets on-cluster
3. normalize corpora
4. build indexes
5. run evaluations
6. score and summarize results

All major scripts expose CLI arguments and write timestamped outputs.

## Retrieval Conditions
The experiment sequence included:

- no retrieval baseline
- vector retrieval
- chunking comparisons
- multilingual embedding comparisons
- corpus supplementation
- BM25 lexical retrieval
- hybrid lexical plus vector retrieval

## Retrieval Scoring
Primary retrieval analysis used `retrieval_recall_at_k` based on whether the intended source document appeared among retrieved contexts.

Exploratory heuristic metrics included:

- grounded answer score
- hallucination rate
- unsupported claim rate

These heuristics use a first-sentence generation stub and are not evidence of end-to-end answer quality. No human evaluation or LLM-as-judge evaluation has been completed.

## Corpus Intervention Strategy
The core methodological contribution was to compare model-side changes against corpus-side interventions:

- baseline corpus
- targeted Uzbek supplement v1
- structured Uzbek supplement v2

This allowed the project to test whether retrieval failure came from model weakness or missing knowledge sources.
