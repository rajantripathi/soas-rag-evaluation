# Technical Architecture

## Purpose

This repository implements a bilingual RAG evaluation pipeline for culturally grounded retrieval in English and Uzbek. The system is designed to answer a specific methodological question:

> When retrieval fails for culturally grounded multilingual questions, is the main bottleneck the retrieval model or the availability of the right source documents?

The validated result is that targeted Uzbek corpus supplementation improved retrieval recall much more than retriever or embedding changes.

## Main Components

| Component | Location | Responsibility |
| --- | --- | --- |
| Dataset and corpus builders | `scripts/fetch_datasets.py`, `scripts/build_corpus.py`, supplement builders | Stage raw datasets, normalize documents, and build corpus JSONL files |
| Evaluation data | `data/eval/`, `hf_dataset/`, full cluster artifacts | Store internal QA examples and public retrieval-only question/source-target rows |
| Retrieval backends | `src/retrieval.py` | Implement TF-IDF-style vector retrieval, BM25, embedding retrieval, and hybrid retrieval |
| Evaluation runner | `src/orchestration.py`, `scripts/run_eval.py` | Run retrieval, generation stub, scoring, and metric aggregation |
| Metrics | `src/evaluation.py`, `scripts/compute_statistics.py` | Compute Recall@k, grounding heuristics, hallucination heuristics, CIs, and effect sizes |
| Reporting | `scripts/report_*.py`, `scripts/generate_research_outputs.py` | Produce tables, figures, synthesis reports, and paper artifacts |
| Cluster execution | `slurm/` | Run build, evaluation, aggregation, and optional judge workflows on Isambard |

## Data Model

### Corpus Record

```json
{
  "doc_id": "source_document_id",
  "chunk_id": "source_document_id::0",
  "source": "dataset_or_supplement_name",
  "language": "en_or_uz",
  "title": "document_title",
  "text": "document_text",
  "metadata": {}
}
```

### Evaluation Record

```json
{
  "id": "benchmark_item_id",
  "language": "en_or_uz",
  "domain": "governance_history_institutions_or_culture",
  "question": "culturally_grounded_question",
  "gold_answer": "reference_answer",
  "source_doc_ids": ["gold_source_document_id"],
  "answerable": true,
  "cultural_specificity": "unknown_low_medium_or_high"
}
```

The v5 benchmark enrichment adds `source_title`, `difficulty`, and `quality_flag` fields so quality issues remain auditable instead of being silently removed.

The public Hugging Face release uses a retrieval-only subset of this schema. It keeps `question`, `source_doc_ids`, and audit fields, but excludes `gold_answer`, retrieved contexts, source text, excerpts, and generated answers.

## Retrieval Architecture

The pipeline supports four retrieval modes:

| Backend | Implementation | Role in experiments |
| --- | --- | --- |
| `simple_vector` | Local TF-IDF-style sparse vectors | Lightweight baseline and smoke tests |
| `embedding` | SentenceTransformers embeddings | Main semantic retrieval path |
| `bm25` | Local BM25 implementation | Lexical retrieval comparison |
| `hybrid` | BM25 candidate union reranked by embedding similarity | Tests whether lexical plus semantic retrieval improves recall |

Hybrid retrieval first collects candidates from BM25 and embedding retrieval, removes duplicate document IDs, then reranks the merged candidates with the embedding model.

## Evaluation Architecture

The evaluation runner performs the following loop:

1. Load an experiment config.
2. Load the evaluation examples.
3. Load the configured retrieval index.
4. Retrieve top-k contexts for each question.
5. Generate a lightweight answer from retrieved context.
6. Score retrieval and grounding metrics.
7. Write per-example predictions, aggregate metrics, and run metadata.

The primary metric is:

```text
retrieval_recall_at_k = 1 if any retrieved doc_id appears in source_doc_ids else 0
```

This is intentionally strict. It asks whether the retriever found the intended source document, not merely whether it found a vaguely related passage.

## Experiment Matrix

The repository includes configurations for:

- no-retrieval baseline
- baseline vector retrieval
- chunking variants
- embedding model comparisons
- Uzbek supplement v1
- structured Uzbek supplement v2
- BM25 retrieval
- hybrid retrieval

The strongest validated result is the Uzbek supplement v2 improvement:

- Uzbek baseline recall: `0.3900`
- Uzbek recall after supplement v2: `0.9800`
- Cohen's d: `2.91`

## Reproducibility Controls

| Control | Implementation |
| --- | --- |
| Config hashes | Each run records a hash of the active config |
| Git commit logging | Evaluation logs include the current Git commit |
| Timestamped run directories | Outputs are written under timestamped `results/eval_*` directories |
| Fixed configs | Experiment settings live in `configs/` |
| Small public sample | `hf_dataset/manual_eval_v5_sample.jsonl` preserves a shareable retrieval-only benchmark sample |
| Large artifact exclusion | Raw corpora, processed corpora, indexes, and full run directories remain outside Git |

## Known Technical Boundaries

- The generator is a controlled stub, so this is primarily a retrieval evaluation project.
- Public Git does not contain full raw datasets, indexes, or complete cluster run directories.
- English supplementation results were retracted because the attempted supplement leaked gold-answer text.
- LLM-as-judge infrastructure exists, but it is not part of the validated headline result.
