# Retrieval Dataset Adapter Example

This example shows how the public English-Uzbek retrieval-only rows can be adapted for RAGAS-style retrieval workflows without changing the dataset schema.

## Local Data

Use the public retrieval-only sample first:

```bash
python ragas_contribution/minimal_example.py --input hf_dataset/manual_eval_v5_sample.jsonl --limit 5
```

Use the full retrieval-only release for inspection:

```bash
python ragas_contribution/minimal_example.py --input hf_dataset/manual_eval_v5_retrieval_only.jsonl --limit 5
```

The script validates required retrieval-only fields and prints preview records with the shape:

```json
{
  "user_input": "question text",
  "retrieved_contexts": [],
  "response": "",
  "metadata": {
    "id": "en_00",
    "language": "en",
    "domain": "culture",
    "source_doc_ids": ["Art Deco"],
    "source_title": "Art Deco",
    "difficulty": "medium",
    "quality_flag": null
  }
}
```

## Mapping to RAGAS Concepts

| Repository field | RAGAS-style use |
| --- | --- |
| `question` | `user_input` |
| `source_doc_ids` | retrieval target in metadata |
| `language`, `domain`, `difficulty`, `quality_flag` | analysis slices in metadata |
| retrieved passage text from a RAG system | `retrieved_contexts`, supplied externally |
| generated answer from a RAG system | `response`, supplied externally |

The public Hugging Face dataset contains questions and source identifiers. It does not contain reference answers, retrieved contexts, source text, or generated answers. Those fields must be supplied by a user's RAG pipeline or a separately cleared QA release before running context or answer metrics.

## Suggested Evaluation Flow

1. Load `hf_dataset/manual_eval_v5_retrieval_only.jsonl` or the Hugging Face dataset.
2. Run each `question` through a RAG pipeline.
3. Store retrieved document IDs as `retrieved_doc_ids`.
4. Compute retrieval recall by checking whether any retrieved document ID matches `source_doc_ids`.
5. Add retrieved contexts, responses, and references only if they are available from the user's pipeline or a cleared QA release.
6. Report retrieval-side results by language and domain.

## Metrics Fit

Appropriate when retrieved contexts, answers, and references are supplied externally:

- context relevance or context precision-style checks
- faithfulness checks against retrieved contexts
- answer correctness or semantic similarity checks against separately cleared references

Appropriate from repository fields alone:

- schema validation
- language/domain slicing
- retrieval-target preparation
- retrieval recall and source coverage analysis through `source_doc_ids`

Not supported by repository fields alone:

- final RAGAS scoring for a live model
- claims about generated answer quality
- cross-lingual retrieval results

## Scope

This script previews a field mapping; it does not execute RAGAS metrics. End-to-end answer evaluation requires retrieved contexts, generated answers, and suitable references supplied separately. See the [reviewer guide](../docs/reviewer_guide.md) for interpretation of the historical retrieval results.
