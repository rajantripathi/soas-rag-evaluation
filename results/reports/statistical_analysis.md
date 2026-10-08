# Historical retrieval results: statistical correction

The historical significance tests, confidence intervals and standardised effect sizes previously reported here are withdrawn pending verification against the original paired predictions. The reported Uzbek Cohen’s d did not match the checked-in formula. Earlier versions remain available in Git history; they should not be cited as verified statistical evidence.

### Overall Recall@k Across Conditions

| Phase | Condition | Corpus | Retrieval | Overall | EN | UZ |
|-------|-----------|---------|-----------|--------|-----|-----|
| v2 | Baseline (no retrieval) | baseline | no_retrieval | 0.0% | 0.0% | 0.0% |
| v2 | Vector baseline | baseline | simple_vector | 49.0% | 61.0% | 37.0% |
| v2 | e5-large | baseline | multilingual_e5_large | 51.0% | 63.0% | 39.0% |
| v2 | UZ supplement v1 | baseline_plus_manual_uzbek | multilingual_e5_large | 71.5% | 63.0% | 80.0% |
| v2 | UZ supplement v2 | baseline_plus_structured_uzbek | multilingual_e5_large | 80.5% | 63.0% | 98.0% |
| v4 | Best vector | supplement_v2 | multilingual_e5_large | 79.5% | 63.0% | 96.0% |
| v4 | BM25 only | supplement_v2 | bm25 | 67.0% | 62.0% | 72.0% |
| v4 | Hybrid | supplement_v2 | bm25_plus_multilingual_e5_large | 79.5% | 63.0% | 96.0% |

## Interpretation

These percentages are retained as historical descriptive reports. Uzbek supplementation added known evaluation-linked source material; the 39% to 98% change does not establish performance on unseen sources. The v2 and v4 populations differ, and alternate phrasings share source targets.

For current auditable evidence, see the [frozen pilot](../../research_outputs/reproducible_pilot/README.md) and [statistical provenance guidance](../../docs/reviewer_guide.md#statistical-provenance). Its source-group intervals are conditional on the fixed corpus and question set, not population-level language comparisons.
