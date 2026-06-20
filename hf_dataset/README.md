---
language:
  - en
  - uz
task_categories:
  - question-answering
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

This folder documents a bilingual English-Uzbek retrieval evaluation benchmark for culturally grounded RAG systems. The full 400-item dataset is prepared but is not included in this public branch while license and source-clearance review is pending.

The current public JSONL file is a preview sample only. It contains questions and source-document metadata, but it deliberately omits `gold_answer` values because some reference-answer text is source-derived and needs manual clearance before public dataset release.

The benchmark is designed to test whether a RAG pipeline retrieves the relevant supporting source document. In this benchmark setting, targeted Uzbek source curation produced an observed improvement in Uzbek retrieval recall from 39% to 98% without changing the underlying model. The result should be interpreted as evidence from this evaluation set, not as evidence for all low-resource RAG systems.

## Languages

- English (`en`)
- Uzbek (`uz`)

## Task

Primary task: RAG retrieval evaluation.

The core evaluation question is whether the retrieved document IDs include the item-level `source_doc_ids`. The dataset can also support grounding, faithfulness, and answer-quality evaluation when users supply retrieved contexts and generated answers from their own RAG systems.

## Intended Uses

- Evaluate retrieval recall for culturally grounded English and Uzbek questions.
- Compare corpus coverage interventions against retrieval or embedding changes.
- Analyze retrieval behavior by language and domain.
- Build examples for RAGAS-style multilingual evaluation.
- Audit whether source coverage is sufficient before optimizing model choices.

## Out-of-Scope Uses

- Do not use the dataset to claim general Uzbek QA competence.
- Do not use it as a full generative answer-quality benchmark without additional generated answers and human or metric-based answer evaluation.
- Do not cite the retracted English supplementation results as evidence.
- Do not treat the English and Uzbek halves as parallel translations.
- Do not generalize the findings to all low-resource languages without further evaluation.

## Dataset Structure

Current files:

- `manual_eval_v5_sample.jsonl`: 30-item public preview sample with `gold_answer` omitted.
- `dataset_info.json`: auxiliary draft metadata for release planning.

Not included in this branch:

- `manual_eval_v5.jsonl`: full 400-item dataset file. It is withheld from the public branch pending license/source-clearance review.

No custom loading script is required for the current preview file. It can be loaded with the standard JSON loader:

```python
from datasets import load_dataset

dataset = load_dataset(
    "json",
    data_files={"preview": "manual_eval_v5_sample.jsonl"},
)
```

Auxiliary metadata:

- `dataset_info.json` is auxiliary draft release metadata for review and upload planning.
- It is not a Hugging Face-generated `dataset_infos.json` file.
- The dataset card and preview JSONL file are the only public dataset materials in this branch.

The prepared full benchmark is balanced across English and Uzbek, but the full JSONL is under release review and is not included here:

| Language | Items |
| --- | ---: |
| English | 200 |
| Uzbek | 200 |

The prepared full benchmark is also balanced across four domains per language:

| Domain | English | Uzbek |
| --- | ---: | ---: |
| governance | 50 | 50 |
| history | 50 | 50 |
| institutions | 50 | 50 |
| culture | 50 | 50 |

## Preview Fields

The current public preview preserves the non-answer metadata fields from the existing repository schema:

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

The full release is expected to include `gold_answer` after clearance. The preview intentionally omits it.

No `split` field is present in the preview data. For Hugging Face loading, treat the current file as a `preview` split.

## Data Sources

The repository documents source staging from:

- MIRACL English raw corpus material.
- TyDi QA primary task material.
- Uzbek Wikipedia material through `yakhyo/uz-wiki`.
- Targeted and structured Uzbek source enrichment used for the validated supplementation experiment.

The public preview file contains evaluation questions and source identifiers. It does not include reference answers, the full raw corpora, processed indexes, or complete HPC run outputs.

## Evaluation Methodology

Primary metric: retrieval recall@k.

An item is counted as retrieved when at least one retrieved document ID matches `source_doc_ids`. This isolates retrieval and source-coverage behavior from downstream generation.

The repository reports bootstrap confidence intervals, paired comparisons, and effect sizes in the checked-in reports. The public dataset card does not introduce new evaluation results and does not claim that the full dataset has been released.

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

TODO: Confirm dataset-license compatibility before upload. The JSONL files include reference-answer text derived from source corpora, and the release license should be compatible with those sources.

TODO: Review long `gold_answer` values before public Hugging Face upload. The current preview omits `gold_answer`, but the prepared full dataset includes some extended source-derived excerpts rather than short answer spans.

TODO: Confirm that all included records come from public or release-cleared sources and do not include private Isambard paths, credentials, or non-public notes.

No obvious personal private data, credentials, or local filesystem paths were added by the release-preparation files.

## Limitations

- The benchmark has 400 items and is moderate in size.
- It covers only English and Uzbek.
- The full 400-row JSONL is not included in this branch pending source-clearance review.
- Full raw corpora, processed indexes, and HPC execution artifacts are not included in this release folder.
- `source_title` resolution is incomplete for some English items.
- Difficulty labels are deterministic heuristics, not human difficulty judgments.
- English supplementation was retracted due to data leakage; English performance should be reported only at the valid baseline.
- Cross-lingual retrieval was not evaluated.
- Human evaluation and LLM-as-judge evaluation are not completed.

## Licensing

TODO: Add final dataset license before upload. The source repository currently includes an MIT software license, but the dataset release license should be confirmed separately because source materials may carry their own terms.

## Citation

TODO: Add exact citation after the technical report or dataset release is finalized.

Starter repository citation metadata is available in `CITATION.cff` in the source repository.

## Contact and Maintainers

TODO: Add final Hugging Face dataset URL after upload.
TODO: Confirm final dataset repository ID before upload.

Maintainer: Rajan Prasad Tripathi.

Affiliations:

- SOAS University of London
- American University of Technology, Uzbekistan

Source repository: `https://github.com/rajantripathi/soas-rag-evaluation`
