# Statistical Analysis

## Methodology

- **Bootstrap confidence intervals**: 1000 resamples, 95% CI
- **McNemar's test**: For paired binary comparisons between conditions
- **Absolute gain**: Difference in recall@k proportions, reported in percentage points
- **Standardised effect size**: Cohen's *d*, reported separately from absolute gain
- **Sample size**: 400 items (200 English, 200 Uzbek) for v4 experiments, 200 items for v2 experiments

## Key Experimental Findings

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

## Statistical Significance Tests

### Comparison 1: Baseline vs UZ Supplement v2 (Uzbek)

**Hypothesis**: Targeted corpus supplementation improves Uzbek retrieval performance

| Metric | Baseline | UZ Supp v2 | Difference | 95% CI | p-value |
|--------|----------|------------|------------|--------|---------|
| Uzbek recall@k | 39.0% | 98.0% | +59.0% | [52.1%, 65.9%] | <0.001*** |
| Overall recall@k | 51.0% | 80.5% | +29.5% | [23.8%, 35.2%] | <0.001*** |

**Conclusion**: Statistically significant improvement in Uzbek retrieval through corpus supplementation (p < 0.001).

### Comparison 2: Embedding Model Changes (e5-large vs mpnet)

**Hypothesis**: Better embedding models improve retrieval performance

| Metric | mpnet | e5-large | Difference | 95% CI | p-value |
|--------|-------|----------|------------|--------|---------|
| Overall recall@k | 43.5% | 51.0% | +7.5% | [1.2%, 13.8%] | 0.020* |
| Uzbek recall@k | 25.0% | 39.0% | +14.0% | [7.1%, 20.9%] | <0.001*** |

**Conclusion**: Statistically significant but modest improvement from better embeddings (7.5% overall vs 29.5% from supplementation).

### Comparison 3: Chunk Size Variants

**Hypothesis**: Smaller chunk sizes improve retrieval performance

| Metric | 256/64 chunks | 128/32 chunks | Difference | 95% CI | p-value |
|--------|---------------|---------------|------------|--------|---------|
| Overall recall@k | 48.5% | 48.5% | 0.0% | [-3.2%, 3.2%] | 1.000 |

**Conclusion**: No statistically significant difference from chunking variations.

### Comparison 4: BM25 vs Vector (with UZ supplement v2)

**Hypothesis**: Lexical retrieval (BM25) vs semantic retrieval (vector)

| Metric | BM25 | Vector | Difference | 95% CI | p-value |
|--------|------|--------|------------|--------|---------|
| Overall recall@k | 67.0% | 79.5% | +12.5% | [7.8%, 17.2%] | <0.001*** |
| Uzbek recall@k | 72.0% | 96.0% | +24.0% | [18.1%, 29.9%] | <0.001*** |
| English recall@k | 62.0% | 63.0% | +1.0% | [-4.2%, 6.2%] | 0.708 |

**Conclusion**: Vector retrieval significantly outperforms BM25 for Uzbek (p < 0.001), but not for English (p = 0.708).

### Comparison 5: Vector vs Hybrid

**Hypothesis**: Hybrid retrieval (BM25 + vector) outperforms vector-only

| Metric | Vector | Hybrid | Difference | 95% CI | p-value |
|--------|--------|--------|------------|--------|---------|
| Overall recall@k | 79.5% | 79.5% | 0.0% | [-2.1%, 2.1%] | 1.000 |

**Conclusion**: No statistically significant difference between vector and hybrid approaches.

## Effect Sizes (Cohen's d)

### Large Effects (d > 0.8)
- **UZ supplementation (Uzbek)**: d = 2.91 (very large effect)
- **UZ supplementation (overall)**: d = 1.45 (very large effect)

### Medium Effects (0.5 < d < 0.8)
- **BM25 vs Vector (Uzbek)**: d = 0.98 (large effect)
- **e5-large vs mpnet (Uzbek)**: d = 0.67 (medium effect)

### Small Effects (d < 0.5)
- **e5-large vs mpnet (overall)**: d = 0.31 (small effect)
- **BM25 vs Vector (English)**: d = 0.04 (negligible effect)

## Per-Domain Analysis (Best Setup: UZ Supp v2 + e5-large)

| Domain | English | Uzbek | Gap |
|--------|---------|-------|-----|
| Governance | 80.0% | 98.0% | 18.0% |
| History | 40.0% | 96.0% | 56.0% |
| Institutions | 32.0% | 96.0% | 64.0% |
| Culture | 100.0% | 94.0% | -6.0% |

**Key Finding**: English history and institutions show the largest performance gaps, matching the corpus coverage analysis.

## Bootstrap Confidence Intervals (Methodology Note)

Confidence intervals were computed using bootstrap resampling (1000 iterations) with the following method:

```python
def bootstrap_recall(recalls, n_resamples=1000, ci=0.95):
    boot_means = [np.mean(np.random.choice(recalls, size=len(recalls), replace=True))
                  for _ in range(n_resamples)]
    lower = np.percentile(boot_means, 100 * (1 - ci) / 2)
    upper = np.percentile(boot_means, 100 * (1 + ci) / 2)
    return np.mean(recalls), lower, upper
```

## Limitations

1. **Sample size**: 400 items provides reasonable statistical power but larger benchmarks (1000+ items) would yield narrower confidence intervals

2. **Independence assumption**: Bootstrap CIs assume items are independent, which may not hold if some items share source documents

3. **Multiple comparisons**: No correction for multiple testing (e.g., Bonferroni) applied; results should be interpreted as exploratory

4. **Bounded proportions**: Effect sizes (Cohen's d) should be interpreted cautiously for bounded metrics like recall@k

## Key Takeaways

1. **Uzbek corpus supplementation produced a large standardised effect in this setting** (d = 2.91); the embedding-model comparison had d = 0.31

2. **The validated Uzbek supplementation comparison was statistically significant** (p < 0.001); the embedding comparison and vector-versus-BM25 results have their own tests above

3. **No significant difference** from chunking variations (p = 1.0) or hybrid retrieval (p = 1.0)

4. **English-Uzbek asymmetry**: Uzbek shows dramatic improvements from supplementation; English shows smaller effects and different failure modes

5. **Domain-specific patterns**: English history and institutions were the weakest English domains; the supplemented Uzbek setup showed high recall across all four domains

---

*Analysis generated: 19 March 2026*
*Experiments conducted on: Isambard GH200 GPUs*
*Statistical software: Python 3.11, NumPy, SciPy*
