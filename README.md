# SOAS RAG Evaluation — English-Uzbek Retrieval Pilot

<!-- badges-start -->
![License](https://img.shields.io/badge/license-MIT-blue.svg)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21067667.svg)](https://doi.org/10.5281/zenodo.21067667)
![Python](https://img.shields.io/badge/python-3.10-blue.svg)
![Last Commit](https://img.shields.io/github/last-commit/rajantripathi/soas-rag-evaluation)
<!-- badges-end -->

## Hugging Face Dataset

The 400-row pilot bilingual retrieval benchmark is available on Hugging Face:

[![HF Dataset](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Dataset-blue)](https://huggingface.co/datasets/Rajan2026/soas-english-uzbek-rag-evaluation)

```python
from datasets import load_dataset

ds = load_dataset("Rajan2026/soas-english-uzbek-rag-evaluation")
print(ds)
```

License: CC-BY-4.0.

Dataset DOI: [10.5281/zenodo.21067667](https://doi.org/10.5281/zenodo.21067667).

> **Pilot benchmark:** The 400 rows are published for transparent retrieval research, but they are not all equally clean. Template-generated questions and domain mismatches are documented through `quality_flag` metadata and the [dataset quality audit](research_outputs/dataset_quality_audit_20260309.md). Treat flagged rows as diagnostic cases, and do not use this release as a polished general-purpose QA benchmark. The current flags are known to be incomplete and will be expanded in a later cleaned release.

## Public Research Assets

- [Industry brief](docs/industry_brief.md): concise engineering framing for AI teams evaluating multilingual RAG.
- [Retrieval-only dataset card](hf_dataset/README.md): public schema, intended uses, limitations, and citation.
- [Recall@k evaluator](scripts/compute_retrieval_recall.py): minimal scorer for retrieved document IDs against `source_doc_ids`.

Evaluator smoke check:

```bash
python scripts/compute_retrieval_recall.py --oracle-check --k 5
```

The smoke check validates scorer wiring by using `source_doc_ids` as retrieved IDs. It is not a model result.

> **Headline result:** In this English-Uzbek evaluation setting, Uzbek retrieval recall improved from **39% to 98%** after targeted corpus supplementation: an absolute gain of **59 percentage points** (*p* < 0.001; Cohen's *d* = **2.91**).

## TL;DR

| Metric | English | Uzbek (before) | Uzbek (after corpus supplementation) |
|---|---|---|---|
| Retrieval Recall | 63% | 39% | **98%** |
| Effect Size (Cohen's d) | — | baseline | **2.91** |

The 59-percentage-point gain from corpus supplementation was approximately 7.9 times the 7.5-point gain observed from embedding-model variation. This comparison concerns absolute recall gains, not a ratio of Cohen's *d* values, and it does not compare different generation LLMs.

## What is in this repo

- Bilingual evaluation harness (English + Uzbek) for RAG retrieval quality
- Reproducible methodology with corpus supplementation pipeline
- Public retrieval-only benchmark files and quality-audit notes
- Scripts to compute Recall@k and effect-size statistics

## Technical Architecture

Architecture and reproducibility notes are documented separately:

- [`docs/architecture_blueprints.md`](docs/architecture_blueprints.md): pipeline, Isambard execution topology, evaluation control plane, and publication data flow
- [`docs/technical_architecture.md`](docs/technical_architecture.md): components, data model, retrieval backends, evaluation loop, and reproducibility controls
- [`docs/isambard_reproducibility.md`](docs/isambard_reproducibility.md): historical execution environment and cluster rehydration guidance
- [`docs/technical_q_and_a.md`](docs/technical_q_and_a.md): technical discussion notes, limitations, and claims to avoid

## Local Smoke Workflow

Environment bootstrap:

```bash
bash scripts/check_env.sh
bash scripts/bootstrap_env.sh
source .venv/bin/activate
```

Smoke path:

```bash
python scripts/fetch_datasets.py --config configs/base.yaml
python scripts/build_corpus.py --config configs/exp_smoke.yaml
python scripts/build_index.py --config configs/exp_smoke.yaml
python scripts/run_eval.py --config configs/exp_smoke.yaml
```

Research-output regeneration:

```bash
python scripts/generate_research_outputs.py
```

This smoke workflow validates the public code path; it does not reproduce the historical Isambard-AI experiment from the public repository alone. The reported run also requires the source corpora and indexes that are intentionally excluded. See the [historical reproducibility notes](docs/isambard_reproducibility.md).

## Citation

Dataset DOI: [10.5281/zenodo.21067667](https://doi.org/10.5281/zenodo.21067667)

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

Author affiliations: (1) AI² Lab, American University of Technology, Uzbekistan; (2) Centre for AI Futures, SOAS University of London.

This repository is a research artifact maintained by the author. It does not represent an official institutional position of SOAS University of London or the American University of Technology.

## Benchmark Design

### Languages and Domains
- **Languages:** English and Uzbek
- **Domains:** governance, history, institutions, culture

### Evaluation Sets
- `manual_eval_v1`: Initial 200-item set (100 EN, 100 UZ)
- `manual_eval_v2`: 200-item set used for the validated supplementation comparison and error analysis
- `manual_eval_v4`: Expanded 400-item set used for robustness analysis
- `manual_eval_v5`: Enriched schema with difficulty, quality_flag, source_title (400 items)

### Internal Core Schema (v5)

The internal evaluation schema includes reference-answer fields for QA analysis. The public Hugging Face dataset is retrieval-only and intentionally excludes answer text to reduce leakage and source-clearance risk.

- `id`: Unique identifier
- `language`: "en" or "uz"
- `domain`: "governance", "history", "institutions", "culture"
- `question`: Culturally grounded question
- `gold_answer`: Internal reference answer, excluded from the public retrieval-only Hugging Face dataset
- `source_doc_ids`: Wikipedia article IDs for gold sources
- `answerable`: Boolean flag
- `cultural_specificity`: "unknown", "low", "medium", "high"
- `source_title`: Resolved Wikipedia title (v5 enrichment)
- `difficulty`: "easy", "medium", "hard" (v5 enrichment)
- `quality_flag`: Domain-specific quality issues (v5 enrichment)

### Retrieval Settings Studied
- No retrieval baseline
- Vector retrieval (TF-IDF, sentence embeddings)
- Chunking variants (256/64, 128/32)
- Embedding comparison (mpnet, multilingual-e5-large)
- Corpus supplementation (Uzbek v1, Uzbek v2)
- BM25 and hybrid retrieval

## Dataset Versions

| Version | Size | Key Features | Use Case |
|---------|------|--------------|----------|
| v1 | 200 items | Initial balanced set | Baseline experiments |
| v2 | 200 items | Quality audit, failure taxonomy | Error analysis |
| v4 | 400 items | Expanded evaluation set | Robustness analysis |
| v5 | 400 items | Enriched schema (difficulty, quality_flag, source_title) | Public pilot release |

## Key Findings

### Core Result
**In this evaluation setting, corpus supplementation produced substantially larger retrieval gains than embedding-model variation.**

### Detailed Findings
- **Uzbek supplementation:** Recall improved from 39% to 98% through targeted corpus supplementation (59 percentage point improvement, p < 0.001, Cohen's d = 2.91)
- **Embedding-model comparison:** The observed overall recall difference was 7.5 percentage points (Cohen's d = 0.31). The 59-point supplementation gain was approximately 7.9 times this absolute difference; the Cohen's *d* values are reported separately and are not used to form that ratio.
- **English baseline:** 63% recall at baseline, with a 37% gap identified in history and institutions domains. English supplementation was attempted but results were retracted due to data leakage.
- **Expanded v4 setup:** 79.5% overall recall with Uzbek supplement v2 + e5-large embeddings; the separate 200-item v2 phase reached 80.5%
- **Weakest domains:** History and institutions showed lowest coverage before supplementation
- **Retriever collapse:** When sources missing, retrieval collapses onto generic hub documents rather than failing independently
- **Statistical significance:** The validated Uzbek supplement v2 comparison was statistically significant (*p* < 0.001)

### Per-Domain Performance (Best Setup: Uzbek supplement v2 + e5-large)
| Domain | English | Uzbek |
|--------|---------|-------|
| Governance | 80% | 98% |
| History | 40% | 96% |
| Institutions | 32% | 96% |
| Culture | 100% | 94% |

## Repository Structure
- `assets/`: lightweight visual assets such as the pipeline overview diagram
- `configs/`: YAML experiment configurations
- `docs/`: benchmark, methodology, results, and limitations documentation
- `hf_dataset/`: public retrieval-only Hugging Face dataset card and JSONL files
- `prompts/`: prompt templates
- `research_outputs/`: summary tables, figures, concept note, and workshop paper
- `results/reports/`: synthesis reports retained in-repo
- `scripts/`: CLI entrypoints and lightweight report generators
- `slurm/`: Slurm templates for cluster execution
- `src/`: retrieval, evaluation, orchestration, and dataset modules

Large HPC artifacts such as raw datasets, processed corpora, indexes, and full experiment run directories are intentionally excluded from version control.
The internal full-QA datasets and answer-bearing prediction files are also excluded pending source and licence clearance.

## Research Outputs

### Workshop Paper
- **Workshop paper:** [research_outputs/workshop_paper_2026/paper_final.md](research_outputs/workshop_paper_2026/paper_final.md) - 4-page workshop paper based on validated Uzbek supplementation results

### Synthesis and Analysis Reports
- **Updated synthesis:** [results/reports/project_synthesis_v2.md](results/reports/project_synthesis_v2.md) - Comprehensive results with corrected English status
- **Original synthesis:** [results/reports/project_synthesis_20260309.md](results/reports/project_synthesis_20260309.md) - Original validated results
- **Error analysis:** [results/reports/manual_eval_v2_error_analysis_20260308.md](results/reports/manual_eval_v2_error_analysis_20260308.md) - Retrieval-side failure cases with answer and source excerpts removed
- **English gap analysis:** [results/reports/english_corpus_gap_analysis.md](results/reports/english_corpus_gap_analysis.md) - English corpus coverage gaps (baseline only)

### Statistical and Methodological Reports
- **Statistical analysis:** [results/reports/statistical_analysis.md](results/reports/statistical_analysis.md) - Bootstrap confidence intervals, effect sizes, significance tests

### Policy and Research Framing
- **Policy brief:** [research_outputs/policy_brief_culturally_grounded_ai.md](research_outputs/policy_brief_culturally_grounded_ai.md) - non-technical interpretation of the validated retrieval findings
- **Workshop outline:** [research_outputs/workshop_outline_20260309.md](research_outputs/workshop_outline_20260309.md) - Structured outline for workshop papers
- **Concept note:** [research_outputs/concept_note_20260309.md](research_outputs/concept_note_20260309.md) - Original project concept

### Audit and Quality Outputs
- **Audit summary:** [research_outputs/audit_summary_20260309.md](research_outputs/audit_summary_20260309.md) - Dataset quality audit
- **Failure taxonomy:** [research_outputs/failure_taxonomy_20260309.md](research_outputs/failure_taxonomy_20260309.md) - Systematic failure classification
- **V5 enrichment spec:** [research_outputs/v5_enrichment_spec_20260309.md](research_outputs/v5_enrichment_spec_20260309.md) - Dataset version 5 schema additions

### Figures and Tables
- **Summary tables:** [research_outputs/summary_tables.md](research_outputs/summary_tables.md) - Key metrics and comparisons
- **Supplementation figure:** [research_outputs/figure_baseline_vs_supplement.svg](research_outputs/figure_baseline_vs_supplement.svg) - Visualisation of supplementation impact
- **Language/domain figure:** [research_outputs/figure_language_domain_comparison.svg](research_outputs/figure_language_domain_comparison.svg) - Per-language, per-domain comparison
- **Pipeline diagram:** [assets/pipeline_overview.svg](assets/pipeline_overview.svg) - System architecture overview

## Methodological Notes

### Retraction: English Supplement Invalid (March 2026)

An initial English supplementation attempt was conducted but results have been retracted. The synthetic documents used contained gold_answer text from the evaluation set, introducing data leakage. Results claiming 100% English recall are invalid. The Uzbek supplementation results (39% to 98%) remain valid. English results are therefore reported at baseline only.

### Validated Results
The following results are validated and reported:
- Uzbek supplementation v2: 59 percentage point improvement (39% to 98%, d = 2.91)
- Embedding model comparison: 7.5 percentage point improvement (d = 0.31)
- Chunking variations: no significant difference (p = 1.000)
- Hybrid vs vector retrieval: no significant difference (p = 1.000)

### Not Attempted
The following experiments were not attempted:
- Cross-lingual retrieval (English questions on Uzbek corpus, or vice versa)
- LLM-as-judge evaluation (infrastructure exists but not executed)
- Human evaluation

## Limitations
- This is a pilot benchmark with documented template artifacts, domain mismatches, and incomplete quality flags; the 400 rows should not be treated as equally clean
- The public repository excludes full raw datasets, processed corpora, and index artifacts
- The validated results concern retrieval recall, not generated-answer quality
- No human evaluation or LLM-as-judge evaluation has been completed
- Generation is a stub that returns the first retrieved sentence; heuristic answer-oriented metrics are not part of the headline claim
- Statistical power limited by benchmark size (400 items) - larger benchmarks would yield narrower confidence intervals
- English was not successfully supplemented (baseline results only)
- Findings based on only 2 languages (English, Uzbek) - may not generalise to other language families

## Citation
If you use this repository, cite it as a research benchmark and software artifact. A starter citation file is provided in [CITATION.cff](CITATION.cff).

## Acknowledgements
The computations reported in this repository used the Isambard-AI supercomputer under project u6ef. This historical acknowledgement does not imply current or future access to Isambard-AI.

## License
Code is released under the [MIT License](LICENSE). The public dataset is released under CC BY 4.0, as recorded in its [dataset card](hf_dataset/README.md) and DOI metadata.
