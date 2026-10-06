# Technical Q&A

Answers to common questions about the retrieval pipeline and its evaluation scope.

## What is the main technical contribution?

The main contribution is a controlled multilingual retrieval evaluation pipeline that compares corpus, retriever, embedding, and chunking interventions. In the validated Uzbek experiment, adding targeted source documents improved recall from 39% to 98%, a larger observed gain than the compared embedding or chunking changes.

## Why focus on retrieval recall instead of final answer quality?

The research question is about grounding. If the source document is absent from the retrieved context, a downstream generator cannot reliably ground the answer. Recall@k against `source_doc_ids` gives a direct, auditable test of whether the retriever found the intended evidence.

## Why is generation a stub?

The project intentionally separates retrieval quality from language-model fluency. A strong generator could hide retrieval failures by answering from parametric memory. The stub keeps the evaluation focused on retrieved evidence.

## What does corpus supplementation mean here?

Corpus supplementation means adding targeted culturally grounded documents that were missing or weakly represented in the baseline corpus. The Uzbek supplement v2 was structured to improve coverage of local entities, institutions, history, and culture without changing the overall retrieval pipeline.

## Why was the English supplement retracted?

The English supplement included text derived from gold answers, which created leakage from the evaluation set into the retrieval corpus. Those results were therefore invalidated. The Uzbek supplement result remains reported because it did not rely on that invalid English supplement.

## Why did hybrid retrieval not improve the final result?

Hybrid retrieval is useful when lexical matching recovers relevant candidates that semantic retrieval misses. In the final supplemented setup, vector retrieval already recovered most intended Uzbek sources, so BM25 did not add much new evidence.

## What are the main engineering strengths?

- Config-driven experiment design
- Reproducible run directories
- Multiple retriever implementations under a common interface
- Language and domain breakdowns
- Explicit leakage and quality-audit reporting
- Slurm templates for cluster execution
- Lightweight public repository with heavy artifacts excluded

## What are the main limitations?

- The full 400-row retrieval-only pilot benchmark is public; raw corpora, indexes, and answer-bearing internal material are not.
- The benchmark remains moderate in size.
- The primary validated result is retrieval-side, not full answer-generation quality.
- LLM-as-judge tooling exists but has not been executed; no human evaluation has been completed.
- Findings are based on English and Uzbek and should not be overgeneralized to all low-resource languages.

## Architecture and evidence

The pipeline builds corpora, indexes them with multiple retrievers, evaluates source-document retrieval, and reports language and domain metrics. See the [technical architecture](technical_architecture.md) for implementation details and the [reviewer guide](reviewer_guide.md) for evidence boundaries.
