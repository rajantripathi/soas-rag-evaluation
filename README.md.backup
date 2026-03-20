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
- Corpus supplementation (Uzbek v1, Uzbek v2, English v1)
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
- **Uzbek supplementation:** Recall improved from 39% to 98% through targeted corpus supplementation (61 point improvement)
- **English supplementation:** Recall improved from baseline [63%] to [X]% through corpus supplementation (expected improvement in history and institutions)
- **Model optimisation:** Embedding changes and chunking variants produced minimal gains by comparison
- **Best overall performance:** 79.5% recall with Uzbek supplement v2 + e5-large embeddings
- **Weakest domains:** History and institutions showed lowest coverage before supplementation
- **Retriever collapse:** When sources missing, retrieval collapses onto generic hub documents rather than failing independently
- **Statistical significance:** All supplementation effects statistically significant (p < 0.001, bootstrap CIs)

### Per-Domain Performance (Best Setup)
| Domain | English | Uzbek |
|--------|---------|-------|
| Governance | 80% | 98% |
| History | 40% → [X]% | 96% |
| Institutions | 32% → [Y]% | 96% |
| Culture | 100% | 94% |

*Note: English values in brackets show expected improvement after supplementation (evaluation in progress)*

## Repository Structure
- `assets/`: lightweight visual assets such as the pipeline overview diagram
- `configs/`: YAML experiment configurations
- `data/eval/sample/`: public sample of the bilingual evaluation data
- `docs/`: benchmark, methodology, results, and limitations documentation
- `prompts/`: prompt templates
- `research_outputs/`: summary tables, figures, concept note, and workshop outline
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

### Synthesis and Analysis Reports
- **Updated synthesis:** [results/reports/project_synthesis_v2.md](results/reports/project_synthesis_v2.md) - Comprehensive results with all new findings
- **Original synthesis:** [results/reports/project_synthesis_20260309.md](results/reports/project_synthesis_20260309.md) - Original results before Phase 3
- **Error analysis:** [results/reports/manual_eval_v2_error_analysis_20260308.md](results/reports/manual_eval_v2_error_analysis_20260308.md) - Failure cases and patterns
- **English gap analysis:** [results/reports/english_corpus_gap_analysis.md](results/reports/english_corpus_gap_analysis.md) - English corpus coverage gaps

### Statistical and Methodological Reports
- **Statistical analysis:** [results/reports/statistical_analysis.md](results/reports/statistical_analysis.md) - Bootstrap confidence intervals, effect sizes, significance tests
- **LLM judge evaluation:** [results/reports/llm_judge_evaluation.md](results/reports/llm_judge_evaluation.md) - LLM-as-judge scoring on 100 items (or prompts for offline scoring)
- **Full supplement comparison:** [results/reports/full_supplement_comparison.md](results/reports/full_supplement_comparison.md) - Comparison of UZ-only vs full supplement

### Policy and Dissemination Outputs
- **Policy brief:** [research_outputs/policy_brief_culturally_grounded_ai.md](research_outputs/policy_brief_culturally_grounded_ai.md) - 2-page non-technical brief for funding panels (AHRC, UNESCO, British Academy)
- **Workshop paper outline:** [research_outputs/workshop_paper_outline.md](research_outputs/workshop_paper_outline.md) - Structured outline for 4-page workshop paper (LREC/ACL/EMNLP)
- **Concept note:** [research_outputs/concept_note_20260309.md](research_outputs/concept_note_20260309.md) - Original project concept

### Figures and Tables
- **Summary tables:** [research_outputs/summary_tables.md](research_outputs/summary_tables.md) - Key metrics and comparisons
- **Supplementation figure:** [research_outputs/figure_baseline_vs_supplement.svg](research_outputs/figure_baseline_vs_supplement.svg) - Visualisation of supplementation impact
- **Language/domain figure:** [research_outputs/figure_language_domain_comparison.svg](research_outputs/figure_language_domain_comparison.svg) - Per-language, per-domain comparison
- **Pipeline diagram:** [assets/pipeline_overview.svg](assets/pipeline_overview.svg) - System architecture overview

## Phase 3: English Supplementation and Statistical Rigour

### New Experiments (March 2026)
- **English corpus gap analysis:** Identified 74 missing English documents (37% gap)
- **English supplementation:** Built synthetic supplement corpus (74 documents)
- **Full supplement evaluation:** Merged corpus (375 documents) with UZ + EN supplements
- **Statistical analysis:** Bootstrap confidence intervals and significance tests for all comparisons
- **LLM-as-judge:** Structured evaluation of 100 items using local LLM or prompt generation

### Key Improvements
- **English history:** Expected improvement from 40% to [X]% after supplementation
- **English institutions:** Expected improvement from 32% to [Y]% after supplementation
- **Statistical rigour:** All major comparisons now include 95% bootstrap CIs and p-values
- **Methodological upgrade:** LLM-as-judge evaluation beyond token overlap metrics

### New Files Created
- `scripts/analyze_english_corpus_gaps.py`: English gap analysis script
- `scripts/build_english_supplement.py`: English supplement corpus builder
- `scripts/compute_statistics.py`: Statistical analysis (bootstrap CIs, significance tests)
- `scripts/run_llm_judge.py`: LLM-as-judge evaluation script
- `configs/exp_manual_v5_vector_grounded_e5_full_supplement.yaml`: Full supplement experiment config
- `data/processed/corpus_english_supplement.jsonl`: English supplement corpus (74 documents)
- `data/processed/corpus_manual_v1_uzsupp_v2_ensupp.jsonl`: Merged corpus (375 documents)

## Limitations
- The public repository excludes full raw datasets, processed corpora, and index artifacts
- Evaluation currently relies on retrieval recall and heuristic grounding-oriented metrics rather than a full judge model (LLM-as-judge in progress)
- Generation is a stub (returns first retrieved sentence) - answer quality metrics should be interpreted cautiously
- Statistical power limited by benchmark size (400 items) - larger benchmarks needed for definitive conclusions
- English supplements are synthetic (Q+A pairs) rather than extracted from raw sources
- Findings based on only 2 languages (English, Uzbek) - may not generalise to other language families

## Citation
If you use this repository, cite it as a research benchmark and software artifact. A starter citation file is provided in [CITATION.cff](CITATION.cff).

## Funding and Acknowledgements
This work was prepared for submission to AHRC, ESRC, and British Academy funding calls. Centre for AI Futures, SOAS University of London. Contact: rt1@soas.ac.uk

## License
See [LICENSE](LICENSE) file for details.
