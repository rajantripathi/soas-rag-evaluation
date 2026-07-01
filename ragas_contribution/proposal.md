# Proposal: English-Uzbek Retrieval Evaluation Benchmark for RAGAS

## Summary

This proposal contributes a small, inspectable English-Uzbek retrieval evaluation benchmark for culturally grounded RAG systems. The benchmark focuses on whether a retriever returns the intended supporting source document for questions about governance, history, institutions, and culture.

In this benchmark setting, targeted Uzbek source curation improved Uzbek retrieval recall from 39% to 98% without changing the underlying model. The repository results suggest that corpus coverage and source quality had a larger observed effect than embedding-model variation for this evaluation set.

## Motivation

Most RAG evaluation examples are centered on English or high-resource settings. This makes it difficult to test whether evaluation workflows expose failures caused by missing local source material, uneven language coverage, or culturally specific evidence requirements.

English-Uzbek is a useful case study because the benchmark pairs a high-resource language with a lower-resource Central Asian language and keeps the evaluation target concrete: can the system retrieve the relevant source document for a culturally grounded question?

## Contribution Scope

The proposed RAGAS contribution would add release-ready retrieval benchmark material rather than expanding RAGAS into a dataset-hosting project. A suitable scope is:

- a compact English-Uzbek evaluation sample
- documentation for the retrieval-only public schema
- an example showing how to adapt rows into RAGAS-style retrieval workflows
- guidance on which RAGAS metrics are appropriate once retrieved contexts and generated answers are available

The full project repository remains the source of methodology, result tables, and reproducibility notes.

## Benchmark Structure

The public retrieval-only `manual_eval_v5` data contains 400 evaluation items balanced across English and Uzbek, with four domains per language: governance, history, institutions, and culture.

Current fields are:

- `id`
- `language`
- `domain`
- `question`
- `source_doc_ids`
- `answerable`
- `cultural_specificity`
- `source_title`
- `difficulty`
- `quality_flag`

The benchmark uses `source_doc_ids` as the auditable retrieval target. It does not require renaming fields for retrieval evaluation; an adapter can map `question` to `user_input`, keep `source_doc_ids` in metadata, and accept externally supplied retrieved passages as `retrieved_contexts` when available.

## How This Supports RAGAS

The benchmark can support several RAG evaluation tasks:

- Retrieval: check whether retrieved document IDs match `source_doc_ids`.
- Grounding: inspect whether generated answers are supported by retrieved contexts once those contexts are supplied externally.
- Faithfulness: evaluate answers against retrieved contexts once real generated answers are supplied.
- Answer quality: compare generated answers against separately cleared references when available.

The benchmark is most directly useful for retrieval and source-coverage evaluation. It should not be presented as a complete generative answer-quality benchmark because the public Hugging Face release intentionally excludes answer text, source text, retrieved contexts, and generated answers.

## Reproducibility

Users can inspect the public dataset files and run the local sample adapter:

```bash
python ragas_contribution/minimal_example.py --limit 5
```

The public repository includes:

- `hf_dataset/manual_eval_v5_retrieval_only.jsonl`
- `hf_dataset/manual_eval_v5_sample.jsonl`
- `hf_dataset/README.md`
- `docs/dataset_card_v5.md`
- `docs/results.md`
- `results/reports/statistical_analysis.md`
- `results/reports/manual_eval_v5_validation.md`

Full reruns require the excluded raw corpora, processed indexes, run outputs, and Isambard-AI environment described in the repository documentation.

## Results Summary

Validated retrieval-side results in the repository include:

- English baseline recall: 63%.
- Uzbek baseline recall: 39%.
- Uzbek recall after targeted corpus supplementation: 98%.
- English supplementation: retracted due to synthetic leakage and not reportable.

These results should be described as specific to this English-Uzbek benchmark and its experimental setup. They do not justify a broader conclusion about corpus coverage versus model choice outside this setting.

## Limitations

- The benchmark has 400 items and should be treated as moderate in size.
- It covers only English and Uzbek.
- Results are retrieval-side results, not full end-to-end answer-quality results.
- Public reruns are limited by excluded raw corpora, indexes, and HPC artifacts.
- Some `source_title` values could not be resolved from the supplied corpus.
- The English supplementation attempt was retracted and should not be used as evidence.
- Quality flags remain in the dataset for transparency rather than being removed.

## Affiliations

- SOAS University of London
- American University of Technology, Uzbekistan

## Proposed RAGAS PR Shape

Suggested PR title:

> Add English-Uzbek low-resource RAG retrieval evaluation example

Suggested PR summary:

> This PR adds a compact English-Uzbek culturally grounded retrieval evaluation example. It demonstrates how low-resource RAG evaluation can separate retrieval failures caused by missing source coverage from downstream generation behavior. The dataset material is scoped as an example and adapter pattern rather than a broad benchmark claim.

## Current External Trail

- Hugging Face dataset: https://huggingface.co/datasets/Rajan2026/soas-english-uzbek-rag-evaluation
- Open RAGAS PR: https://github.com/vibrantlabsai/ragas/pull/2795
- LangChain issue: https://github.com/langchain-ai/langchain/issues/38572

TODO: Adapt the contribution format if RAGAS maintainers request a different location, sample size, or metric framing.
