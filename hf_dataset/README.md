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
  - central-asia
  - culturally-grounded
  - benchmark
license: cc-by-4.0
pretty_name: SOAS English-Uzbek RAG Evaluation (Retrieval-Only)
size_categories:
  - n<1K
configs:
  - config_name: default
    data_files:
      - split: train
        path: "manual_eval_v5_retrieval_only.jsonl"
      - split: preview
        path: "manual_eval_v5_sample.jsonl"
---

# When Corpus Coverage Matters More Than Model Choice: An English-Uzbek Low-Resource RAG Evaluation Dataset

## Dataset Summary

This folder documents a bilingual English-Uzbek retrieval evaluation benchmark for culturally grounded RAG systems. The 400-row public pilot release is retrieval-only: it contains questions and source-document targets, but it intentionally excludes answer, context, excerpt, and source-text fields.

This is a pilot benchmark with documented quality flags, template-generated examples, and domain mismatches. The rows are published for transparency and diagnostic retrieval experiments; they should not be treated as 400 equally clean QA items. Some known mismatches were identified after the initial flagging pass, so the current `quality_flag` field should be treated as useful but not exhaustive.

The full QA version remains pending license and source-clearance review. `gold_answer` and `reference_answer` fields are not included in the public pilot release because earlier review found source-derived answer text that needs manual clearance before publication.

The benchmark is designed to test whether a RAG pipeline retrieves the relevant supporting source document. In this benchmark setting, targeted Uzbek source curation produced an observed improvement in Uzbek retrieval recall from 39% to 98% without changing the underlying model. The result should be interpreted as evidence from this evaluation set, not as evidence for all low-resource RAG systems.

## Languages

- English (`en`)
- Uzbek (`uz`)

## Task

Primary task: RAG retrieval evaluation.

The core evaluation question is whether retrieved document IDs include the item-level `source_doc_ids`.

This public pilot release does not support answer correctness, faithfulness, or reference-answer metrics by itself because `gold_answer`, `reference_answer`, retrieved contexts, generated answers, source text, and excerpts are intentionally excluded.

## Intended Uses

- Evaluate retrieval recall for culturally grounded English and Uzbek questions.
- Compare corpus coverage interventions against retrieval or embedding changes.
- Analyze retrieval behavior by language and domain.
- Build examples for RAGAS-style multilingual evaluation.
- Audit whether source coverage is sufficient before optimizing model choices.

## Out-of-Scope Uses

- Do not use the dataset to claim general Uzbek QA competence.
- Do not use this retrieval-only pilot release as a generated-answer quality benchmark.
- Do not compute answer correctness, faithfulness, or reference-answer metrics from these files alone.
- Do not cite the retracted English supplementation results as evidence.
- Do not treat the English and Uzbek halves as parallel translations.
- Do not generalize the findings to all low-resource languages without further evaluation.

## Dataset Structure

Current files:

- `manual_eval_v5_retrieval_only.jsonl`: 400-row retrieval-only public pilot release.
- `manual_eval_v5_sample.jsonl`: 30-row public preview sample with the same retrieval-only field set.
- `dataset_info.json`: auxiliary draft metadata for release planning. It is not a Hugging Face-generated `dataset_infos.json` file.

Not included in this branch:

- `manual_eval_v5.jsonl`: internal full QA dataset file with `gold_answer`. It is withheld from the public branch pending license/source-clearance review.

No custom loading script is required. The retrieval-only dataset can be loaded with the standard JSON loader:

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
- The dataset card, retrieval-only JSONL file, and preview JSONL file are the public dataset materials in this branch.

The retrieval-only dataset is balanced across English and Uzbek:

| Language | Items |
| --- | ---: |
| English | 200 |
| Uzbek | 200 |

The retrieval-only dataset is also balanced across four domains per language:

| Domain | English | Uzbek |
| --- | ---: | ---: |
| governance | 50 | 50 |
| history | 50 | 50 |
| institutions | 50 | 50 |
| culture | 50 | 50 |

## Dataset Fields

The retrieval-only public release contains exactly these fields:

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

The full QA release may include answer/reference fields after clearance. This retrieval-only dataset intentionally omits them.

No `split` field is present in the data rows. For Hugging Face loading, treat `manual_eval_v5_retrieval_only.jsonl` as the main split and `manual_eval_v5_sample.jsonl` as a preview split.

## Data Sources

The repository documents source staging from:

- MIRACL English raw corpus material.
- TyDi QA primary task material.
- Uzbek Wikipedia material through `yakhyo/uz-wiki`.
- Targeted and structured Uzbek source enrichment used for the validated supplementation experiment.

The public retrieval-only files contain evaluation questions and source identifiers. They do not include reference answers, source text, the full raw corpora, processed indexes, or complete HPC run outputs.

## Evaluation Methodology

Primary metric: retrieval recall@k.

An item is counted as retrieved when at least one retrieved document ID matches `source_doc_ids`. This isolates retrieval and source-coverage behavior from downstream generation.

The repository reports bootstrap confidence intervals, paired comparisons, and effect sizes in the checked-in reports. The public dataset card does not introduce new evaluation results.

This public release does not provide answer references. Users who want answer correctness, faithfulness, or reference-answer metrics need a separately cleared QA release or their own approved reference answers.

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
- Because the flagging pass is incomplete, users should also consult the repository's dataset quality audit before defining a clean subset.

## Release Risk Review

TODO: Confirm dataset-license compatibility for any future expanded release. The retrieval-only dataset excludes source-derived reference answers, but the source corpora and source-document identifiers still need continuing release review.

TODO: Review long `gold_answer` values before any future full QA Hugging Face upload. The prepared internal full QA dataset includes some extended source-derived excerpts rather than short answer spans.

TODO: Confirm that all included records come from public or release-cleared sources and do not include private Isambard paths, credentials, or non-public notes.

No obvious personal private data, credentials, or local filesystem paths were added by the release-preparation files.

## Limitations

- The benchmark has 400 items and is moderate in size.
- It is a pilot benchmark: template-generated questions, domain mismatches, and uneven item quality remain.
- `quality_flag` documents known issues but is not yet exhaustive; unflagged does not necessarily mean manually validated.
- It covers only English and Uzbek.
- This is a retrieval-only pilot release.
- It does not support answer correctness, faithfulness, or reference-answer metrics by itself.
- The full QA JSONL with answer/reference fields is not included pending source-clearance review.
- Full raw corpora, processed indexes, and HPC execution artifacts are not included in this release folder.
- `source_title` resolution is incomplete for some English items.
- Difficulty labels are deterministic heuristics, not human difficulty judgments.
- English supplementation was retracted due to data leakage; English performance should be reported only at the valid baseline.
- Cross-lingual retrieval was not evaluated.
- Human evaluation and LLM-as-judge evaluation are not completed.

## Licensing

CC-BY-4.0 (dataset), MIT (code).

Dataset DOI: [10.5281/zenodo.21067667](https://doi.org/10.5281/zenodo.21067667)

## Citation

```bibtex
@dataset{tripathi_2026_soas_en_uz_rag,
  author       = {Tripathi, Rajan Prasad},
  title        = {SOAS English-Uzbek RAG Evaluation (Retrieval-Only)},
  year         = {2026},
  publisher    = {Zenodo},
  version      = {manual_eval_v5},
  doi          = {10.5281/zenodo.21067667},
  url          = {https://doi.org/10.5281/zenodo.21067667}
}
```

## Contact and Maintainers

Maintainer: Rajan Prasad Tripathi.

Affiliations: AUT AI² Lab, School of Digital Technologies, American University of Technology, Uzbekistan; Centre for AI Futures, SOAS University of London.

Hugging Face dataset: `https://huggingface.co/datasets/Rajan2026/soas-english-uzbek-rag-evaluation`
Source repository: `https://github.com/rajantripathi/soas-rag-evaluation`
