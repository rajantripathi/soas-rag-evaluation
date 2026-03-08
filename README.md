# Culturally Grounded Multilingual RAG Evaluation

## Overview
This repository presents a reproducible bilingual retrieval benchmark for culturally grounded question answering in English and Uzbek. It packages a conservative RAG evaluation pipeline, balanced manual evaluation sets, experiment configurations, and research-facing summaries designed for collaborators, workshop submission, and future corpus expansion work.

## Why This Benchmark Matters
Multilingual AI systems are often evaluated on generic benchmarks that underrepresent local institutional, historical, and cultural knowledge. This project asks a more specific question: when retrieval fails on culturally grounded queries, is the main bottleneck model choice or knowledge source coverage?

The experiments consistently point to the same answer: corpus coverage of culturally grounded sources matters more than chunking, embedding swaps, or hybrid retrieval design.

## Benchmark Design
- Languages: English and Uzbek
- Domains: governance, history, institutions, culture
- Evaluation sets:
  - `manual_eval_v2`: 200 balanced items
  - `manual_eval_v4`: 400 balanced items
- Retrieval settings studied:
  - no retrieval baseline
  - vector retrieval
  - chunking variants
  - embedding comparison
  - corpus supplementation
  - BM25 and hybrid retrieval
- Core schema:
  - `id`
  - `language`
  - `domain`
  - `question`
  - `gold_answer`
  - `cultural_specificity`
  - `answerable`
  - `source_doc_ids`

## Key Findings
- Retrieval improved grounding substantially over the no-retrieval baseline.
- Smaller chunk sizes did not fix the hardest Uzbek failures.
- `intfloat/multilingual-e5-large` was the strongest tested embedding model, but embedding changes alone produced modest gains.
- BM25 and hybrid retrieval did not outperform the final vector setup.
- Targeted Uzbek corpus supplements produced the largest improvements by far.
- The main empirical contribution is that culturally grounded AI performance depended primarily on knowledge source coverage rather than model choice.

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
- Synthesis report: [results/reports/project_synthesis_20260309.md](results/reports/project_synthesis_20260309.md)
- Summary tables: [research_outputs/summary_tables.md](research_outputs/summary_tables.md)
- Corpus supplementation figure: [research_outputs/figure_baseline_vs_supplement.svg](research_outputs/figure_baseline_vs_supplement.svg)
- Language/domain figure: [research_outputs/figure_language_domain_comparison.svg](research_outputs/figure_language_domain_comparison.svg)
- Concept note: [research_outputs/concept_note_20260309.md](research_outputs/concept_note_20260309.md)
- Workshop outline: [research_outputs/workshop_outline_20260309.md](research_outputs/workshop_outline_20260309.md)
- Pipeline diagram: [assets/pipeline_overview.svg](assets/pipeline_overview.svg)

## Limitations
- The public repository excludes full raw datasets, processed corpora, and index artifacts.
- Evaluation currently relies on retrieval recall and heuristic grounding-oriented metrics rather than a full judge model.
- English source coverage remains thinner than Uzbek in some domains under the final supplemented setup.
- The public sample dataset is illustrative and not a replacement for the full benchmark used on Isambard.

## Citation
If you use this repository, cite it as a research benchmark and software artifact. A starter citation file is provided in [CITATION.cff](CITATION.cff).
