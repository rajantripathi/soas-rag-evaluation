---
language:
  - en
  - uz
task_categories:
  - text-retrieval
tags:
  - retrieval-augmented-generation
  - rag-evaluation
  - multilingual
  - low-resource
  - uzbek
license: other
pretty_name: When Corpus Coverage Matters More Than Model Choice
---

# When Corpus Coverage Matters More Than Model Choice: An English-Uzbek Low-Resource RAG Evaluation Dataset

## Dataset Summary

This folder documents a bilingual English-Uzbek retrieval evaluation benchmark for culturally grounded RAG systems. The 400-row public release candidate is retrieval-only: it contains questions and source-document targets, but it intentionally excludes answer, context, excerpt, and source-text fields.

The full QA version remains pending license and source-clearance review. `gold_answer` and `reference_answer` fields are not included in the release candidate because earlier review found source-derived answer text that needs manual clearance before publication.

The benchmark is designed to test whether a RAG pipeline retrieves the relevant supporting source document. In this benchmark setting, targeted Uzbek source curation produced an observed improvement in Uzbek retrieval recall from 39% to 98% without changing the underlying model. The result should be interpreted as evidence from this evaluation set, not as evidence for all low-resource RAG systems.

## Retrieval-Only Release Scope

This is a retrieval-only dataset release candidate. It supports retrieval recall and source-document matching by comparing retrieved document IDs against `source_doc_ids`.

It does not include answer text, reference-answer text, source text, retrieved contexts, or excerpts. This version therefore does not support answer correctness, faithfulness, or reference-answer metrics. The full QA version remains pending licence and source-clearance review.

## Languages

- English (`en`)
- Uzbek (`uz`)

## Task

Primary task: RAG retrieval evaluation.

The core evaluation question is whether retrieved document IDs include the item-level `source_doc_ids`.

This release candidate does not support answer correctness, faithfulness, or reference-answer metrics by itself because `gold_answer`, `reference_answer`, retrieved contexts, generated answers, source text, and excerpts are intentionally excluded.

## Intended Uses

- Evaluate retrieval recall for culturally grounded English and Uzbek questions.
- Compare corpus coverage interventions against retrieval or embedding changes.
- Analyze retrieval behavior by language and domain.
- Build examples for RAGAS-style multilingual evaluation.
- Audit whether source coverage is sufficient before optimizing model choices.

## Out-of-Scope Uses

- Do not use the dataset to claim general Uzbek QA competence.
- Do not use this retrieval-only release candidate as a generated-answer quality benchmark.
- Do not compute answer correctness, faithfulness, or reference-answer metrics from these files alone.
- Do not cite the retracted English supplementation results as evidence.
- Do not treat the English and Uzbek halves as parallel translations.
- Do not generalize the findings to all low-resource languages without further evaluation.

## Dataset Structure

Current files:

- `manual_eval_v5_retrieval_only.jsonl`: 400-row retrieval-only public release candidate.
- `manual_eval_v5_sample.jsonl`: 30-row public preview sample with the same retrieval-only field set.
- `dataset_info.json`: auxiliary draft metadata for release planning. It is not a Hugging Face-generated `dataset_infos.json` file.

Not included in this branch:

- `manual_eval_v5.jsonl`: internal full QA dataset file with `gold_answer`. It is withheld from the public release candidate pending license/source-clearance review.

No custom loading script is required. The retrieval-only candidate can be loaded with the standard JSON loader:

```python
from datasets import load_dataset

dataset = load_dataset(
    "json",
    data_files={
        "train": "manual_eval_v5_retrieval_only.jsonl",
        "preview": "manual_eval_v5_sample.jsonl",
    },
)
```

Auxiliary metadata:

- `dataset_info.json` is auxiliary draft release metadata for review and upload planning.
- It is not a Hugging Face-generated `dataset_infos.json` file.
- The dataset card, retrieval-only JSONL candidate, and preview JSONL file are the public dataset materials in this branch.

The retrieval-only candidate is balanced across English and Uzbek:

| Language | Items |
| --- | ---: |
| English | 200 |
| Uzbek | 200 |

The retrieval-only candidate is also balanced across four domains per language:

| Domain | English | Uzbek |
| --- | ---: | ---: |
| governance | 50 | 50 |
| history | 50 | 50 |
| institutions | 50 | 50 |
| culture | 50 | 50 |

## Dataset Fields

The retrieval-only release candidate contains exactly these fields:

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Stable item identifier. |
| `language` | string | `en` or `uz`. |
| `domain` | string | `governance`, `history`, `institutions`, or `culture`. |
| `question` | string | Evaluation question. |
| `source_doc_ids` | list[string] | Intended source document identifiers for retrieval recall. |
| `answerable` | boolean | Whether the item is considered answerable. |
| `cultural_specificity` | string | Cultural-specificity label retained from the benchmark. |
| `source_title` | string or null | Human-readable title resolved from the source document identifier where available. |
| `difficulty` | string | Deterministic heuristic label: `easy`, `medium`, or `hard`. |
| `quality_flag` | string or null | Audit-derived flag such as `domain_misclassification` or `question_quality`. |

Excluded fields:

- `gold_answer`
- `reference_answer`
- `answer`
- `context`
- `excerpt`
- `source_text`
- `source_document`

The full QA release may include answer/reference fields after clearance. This retrieval-only candidate intentionally omits them.

No `split` field is present in the data rows. For Hugging Face loading, treat `manual_eval_v5_retrieval_only.jsonl` as the main split and `manual_eval_v5_sample.jsonl` as a preview split.

## Upstream Provenance

The source repository documents or references the following upstream source families that need final per-source confirmation before upload:

- MIRACL / MIRACL corpus material.
- TyDi QA material, if it is present in the released rows.
- Uzbek Wikipedia-derived material, including `yakhyo/uz-wiki`, if it is present in the released rows.
- Targeted and structured Uzbek enrichment corpus material used in this repository.

The public retrieval-only files contain evaluation questions and source identifiers. They do not include reference answers, source text, the full raw corpora, processed indexes, or complete HPC run outputs.

TODO: Confirm per-record upstream provenance before Hugging Face upload.

TODO: Confirm whether TyDi QA-derived material is present in the public retrieval-only rows.

TODO: Confirm whether Uzbek Wikipedia-derived metadata is present and whether share-alike dataset-content terms are required.

## Attribution and Source Notes

Users should cite this dataset and respect the terms of the upstream sources used to construct or enrich the benchmark. The source repository software licence and the dataset-content licence may differ.

`source_doc_ids` and `source_title` are retrieval target metadata. They are not source text. They still need provenance review because they may identify upstream source documents.

The retrieval-only candidate has 200 unique source document IDs and 163 unique non-null source titles. `source_title` is unresolved for 74 rows. Some resolved titles are short or ambiguous, for example `-1`, `1477`, `1917`, `1972`, `Din`, and `Bosh Sahifa`. These values are retained for retrieval traceability but should be reviewed before final publication.

## Evaluation Methodology

Primary metric: retrieval recall@k.

An item is counted as retrieved when at least one retrieved document ID matches `source_doc_ids`. This isolates retrieval and source-coverage behavior from downstream generation.

The repository reports bootstrap confidence intervals, paired comparisons, and effect sizes in the checked-in reports. The public dataset card does not introduce new evaluation results.

This release candidate does not provide answer references. Users who want answer correctness, faithfulness, or reference-answer metrics need a separately cleared QA release or their own approved reference answers.

## Results Summary

Validated retrieval-side results from the repository:

| Setting | Retrieval Recall | Status |
| --- | ---: | --- |
| English baseline | 63% | Valid baseline |
| Uzbek baseline | 39% | Valid baseline |
| Uzbek after corpus supplementation | 98% | Validated curation result |
| English supplementation | Retracted | Invalid due to synthetic leakage |

Careful interpretation:

- On this English-Uzbek evaluation set, corpus coverage and curation had a larger observed effect than embedding-model variation.
- The validated Uzbek supplementation effect was 59 percentage points, from 39% to 98%.
- The result is retrieval-side evidence; it does not establish final generated-answer quality.

## Ethical Considerations

- Culturally grounded benchmarks can expose language and source-coverage gaps that are hidden by English-only evaluation.
- The dataset should be used to improve coverage and evaluation quality, not to rank cultures or languages.
- Uzbek examples should not be treated as a complete representation of Uzbek knowledge, institutions, or culture.
- Quality flags are retained to make known issues visible rather than silently removing difficult items.

## Release Risk Review

TODO: Confirm dataset-content licence compatibility before upload. The retrieval-only candidate excludes source-derived reference answers, but the source corpora, source-document identifiers, and source titles still need release review.

TODO: Review long `gold_answer` values before any future full QA Hugging Face upload. The prepared internal full QA dataset includes some extended source-derived excerpts rather than short answer spans.

TODO: Confirm that all included records come from public or release-cleared sources and do not include private Isambard paths, credentials, or non-public notes.

No obvious personal private data, credentials, or local filesystem paths were added by the release-preparation files.

## Limitations

- The benchmark has 400 items and is moderate in size.
- It covers only English and Uzbek.
- This is a retrieval-only release candidate.
- It does not support answer correctness, faithfulness, or reference-answer metrics by itself.
- The full QA JSONL with answer/reference fields is not included pending source-clearance review.
- Full raw corpora, processed indexes, and HPC execution artifacts are not included in this release folder.
- `source_title` resolution is incomplete for 74 rows.
- Some `source_title` values are ambiguous and need final provenance review.
- Difficulty labels are deterministic heuristics, not human difficulty judgments.
- English supplementation was retracted due to data leakage; English performance should be reported only at the valid baseline.
- Cross-lingual retrieval was not evaluated.
- Human evaluation and LLM-as-judge evaluation are not completed.

## Dataset Content Licence

TODO: Add final dataset-content licence before upload. The source repository currently includes an MIT software licence for repository code, but the dataset-content licence should be confirmed separately because source materials may carry their own terms.

Recommended conservative directions to review:

- Use a share-alike dataset-content licence such as CC BY-SA 4.0 if Uzbek Wikipedia-derived metadata is confirmed in the released dataset.
- Document mixed provenance if the public candidate combines sources with different attribution or redistribution terms.
- Use a more permissive dataset-content licence only if the retained questions and source metadata are confirmed to be compatible with that choice.

Do not treat this draft dataset card as legal advice or final clearance.

## Citation

TODO: Add exact citation after the technical report or dataset release is finalized.

Starter repository citation metadata is available in `CITATION.cff` in the source repository.

TODO: Add upstream-source attribution notes after provenance confirmation.

## Contact and Maintainers

TODO: Add final Hugging Face dataset URL after upload.
TODO: Confirm final dataset repository ID before upload.

Maintainer: Rajan Prasad Tripathi.

Affiliations:

- SOAS University of London
- American University of Technology, Uzbekistan

Source repository: `https://github.com/rajantripathi/soas-rag-evaluation`
