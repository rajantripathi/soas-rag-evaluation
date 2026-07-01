# Industry Brief: Multilingual RAG Evaluation Before Model Tuning

## Executive Summary

This project is a compact English-Uzbek retrieval benchmark for culturally grounded RAG systems. It is designed to test a practical engineering question: did retrieval fail because the model is weak, or because the source corpus does not contain the right evidence?

In this benchmark setting, targeted Uzbek source curation improved retrieval recall from 39% to 98% without changing the underlying model. The result is evidence for this dataset and setup, not a universal claim about all low-resource languages.

## Why It Matters for AI Teams

Many RAG teams tune embeddings, prompts, and rerankers before checking whether the required source material is actually present and retrievable. That creates wasted iteration cycles and can hide coverage gaps in multilingual deployments.

This benchmark separates source-coverage failure from downstream generation quality. The public release is retrieval-only, so teams can inspect question, language, domain, and source-document target fields without inheriting answer-text leakage risk.

## Public Assets

- GitHub repository: https://github.com/rajantripathi/soas-rag-evaluation
- Hugging Face dataset: https://huggingface.co/datasets/Rajan2026/soas-english-uzbek-rag-evaluation
- Dataset DOI: https://doi.org/10.5281/zenodo.21067667
- RAGAS contribution PR: https://github.com/vibrantlabsai/ragas/pull/2795
- LangChain cookbook proposal: https://github.com/langchain-ai/langchain/issues/38572

## What the Benchmark Provides

- 400 retrieval-evaluation rows across English and Uzbek.
- Four domains per language: governance, history, institutions, and culture.
- Source-document targets through `source_doc_ids`.
- Retrieval-only Hugging Face release under CC-BY-4.0.
- Repository code under MIT.
- Reproducibility notes, reports, and statistical analysis in the source repository.

## How an Engineering Team Can Reuse It

1. Load the retrieval-only dataset from Hugging Face.
2. Run each question through a retriever.
3. Save retrieved document identifiers as `retrieved_doc_ids`.
4. Compute recall@k by checking whether retrieved identifiers match `source_doc_ids`.
5. Slice results by language and domain before changing embeddings or prompts.

Prediction JSONL schema:

```json
{"id": "uz_00", "retrieved_doc_ids": ["793", "1031", "1482"]}
```

Evaluator smoke check:

```bash
python scripts/compute_retrieval_recall.py --oracle-check --k 5
```

The smoke check uses ground-truth source IDs as retrieved IDs. It validates evaluator wiring only; it is not a model result.

## Claims to Make

- In this English-Uzbek benchmark setting, targeted Uzbek corpus supplementation improved retrieval recall from 39% to 98%.
- The observed corpus-coverage effect was larger than embedding-model variation in this setup.
- Retrieval-only evaluation is useful for diagnosing source coverage before optimizing generation.

## Claims to Avoid

- Do not claim this proves corpus coverage always dominates model choice.
- Do not claim the dataset measures generated-answer quality by itself.
- Do not cite the retracted English supplementation result as valid evidence.
- Do not describe the English and Uzbek halves as parallel translations.

## Positioning

This is best presented as an applied AI evaluation artifact: small enough to inspect, structured enough to reuse, and scoped carefully enough to be credible for industry review.
