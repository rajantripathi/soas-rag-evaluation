# Culturally Grounded Multilingual RAG Evaluation

## Overview
This repository presents a reproducible bilingual retrieval benchmark for culturally grounded question answering in English and Uzbek. It packages a conservative RAG evaluation pipeline, balanced manual evaluation sets, experiment configurations, and research-facing summaries designed for collaborators, workshop submission, and future corpus expansion work.

## Why This Benchmark Matters
Multilingual AI systems are often evaluated on generic benchmarks that underrepresent local institutional, historical, and cultural knowledge. This project asks a more specific question: when retrieval fails on culturally grounded queries, is the main bottleneck model choice or knowledge source coverage?

The experiments consistently point to the same answer: corpus coverage of culturally grounded sources matters more than chunking, embedding swaps, or hybrid retrieval design.

## Benchmark Design

### Languages and Domains
- **Languages:** English and Uzbek
- **Domains:** governance, history, institutions, culture

### Evaluation Sets
- `manual_eval_v1`: Initial 200-item set (100 EN, 100 UZ)
- `manual_eval_v2`: Quality audit, failure taxonomy
- `manual_eval_v4`: Uzbek supplement v2, 400 items
- `manual_eval_v5`: Enriched schema with difficulty, quality_flag, source_title (400 items)

### Core Schema (v5)
- `id`: Unique identifier
- `language`: "en" or "uz"
- `domain`: "governance", "history", "institutions", "culture"
- `question`: Culturally grounded question
- `gold_answer`: Reference answer
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
| v4 | 400 items | Uzbek supplement v2 | Current best performance |
| v5 | 400 items | Enriched schema (difficulty, quality_flag, source_title) | Final experiments, publication |

## Key Findings

### Core Result
**Corpus coverage dominates model choice for culturally grounded multilingual retrieval.**

### Detailed Findings
- **Uzbek supplementation:** Recall improved from 39% to 98% through targeted corpus supplementation (59 percentage point improvement, p < 0.001, Cohen's d = 2.91)
- **Model optimisation:** Embedding changes produced only a 7.5 percentage point gain (Cohen's d = 0.31). The corpus supplementation effect is 7.9 times larger than the model effect.
- **English baseline:** 63% recall at baseline, with a 37% gap identified in history and institutions domains. English supplementation was attempted but results were retracted due to data leakage.
- **Best overall performance:** 79.5% recall with Uzbek supplement v2 + e5-large embeddings
- **Weakest domains:** History and institutions showed lowest coverage before supplementation
- **Retriever collapse:** When sources missing, retrieval collapses onto generic hub documents rather than failing independently
- **Statistical significance:** All supplementation effects statistically significant (bootstrap CIs, p < 0.001)

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
- `data/eval/sample/`: public sample of the bilingual evaluation data
- `docs/`: benchmark, methodology, results, and limitations documentation
- `prompts/`: prompt templates
- `research_outputs/`: summary tables, figures, concept note, and workshop paper
- `results/reports/`: synthesis reports retained in-repo
- `scripts/`: CLI entrypoints and lightweight report generators
- `slurm/`: Slurm templates for cluster execution
- `src/`: retrieval, evaluation, orchestration, and dataset modules

Large HPC artifacts such as raw datasets, processed corpora, indexes, and full experiment run directories are intentionally excluded from version control.

## Quickstart
Environment bootstrap on Isambard:

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

## Research Outputs

### Workshop Paper
- **Workshop paper:** [research_outputs/workshop_paper_2026/paper_final.md](research_outputs/workshop_paper_2026/paper_final.md) - 4-page workshop paper based on validated Uzbek supplementation results

### Synthesis and Analysis Reports
- **Updated synthesis:** [results/reports/project_synthesis_v2.md](results/reports/project_synthesis_v2.md) - Comprehensive results with corrected English status
- **Original synthesis:** [results/reports/project_synthesis_20260309.md](results/reports/project_synthesis_20260309.md) - Original validated results
- **Error analysis:** [results/reports/manual_eval_v2_error_analysis_20260308.md](results/reports/manual_eval_v2_error_analysis_20260308.md) - Failure cases and patterns
- **English gap analysis:** [results/reports/english_corpus_gap_analysis.md](results/reports/english_corpus_gap_analysis.md) - English corpus coverage gaps (baseline only)

### Statistical and Methodological Reports
- **Statistical analysis:** [results/reports/statistical_analysis.md](results/reports/statistical_analysis.md) - Bootstrap confidence intervals, effect sizes, significance tests

### Policy and Dissemination Outputs
- **Policy brief:** [research_outputs/policy_brief_culturally_grounded_ai.md](research_outputs/policy_brief_culturally_grounded_ai.md) - 2-page non-technical brief for funding panels (AHRC, UNESCO, British Academy)
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
- The public repository excludes full raw datasets, processed corpora, and index artifacts
- Evaluation currently relies on retrieval recall and heuristic grounding-oriented metrics
- Generation is a stub (returns first retrieved sentence), so answer quality metrics should be interpreted cautiously
- Statistical power limited by benchmark size (400 items) - larger benchmarks would yield narrower confidence intervals
- English was not successfully supplemented (baseline results only)
- Findings based on only 2 languages (English, Uzbek) - may not generalise to other language families

## Citation
If you use this repository, cite it as a research benchmark and software artifact. A starter citation file is provided in [CITATION.cff](CITATION.cff).

## Funding and Acknowledgements
This work used the Isambard-AI supercomputer under the u6ef project. Centre for AI Futures, SOAS University of London. Contact: rt1@soas.ac.uk

## License
See [LICENSE](LICENSE) file for details.
