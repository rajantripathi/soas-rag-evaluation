# Results

## Main Result
Across the full experiment sequence, corpus supplementation produced the largest gains in retrieval quality.

## Representative Comparisons
On `manual_eval_v2`:

- baseline vector recall@k: `0.5100`
- supplement v1 recall@k: `0.7150`
- supplement v2 recall@k: `0.8050`

Uzbek recall improved from `0.3900` in the baseline vector setup to `0.9800` under supplement v2.

On `manual_eval_v4` with the best-performing setup:

- overall recall@k: `0.7950`
- English recall@k: `0.6300`
- Uzbek recall@k: `0.9600`

## Interpretation
- Chunking changes had minimal impact on the hardest Uzbek domains.
- Embedding changes were measurable but modest.
- Hybrid retrieval did not improve beyond the final vector setup.
- Adding the right culturally grounded documents produced the strongest improvements.

The main takeaway is that retrieval quality improved most when the corpus actually contained the relevant local source material.
