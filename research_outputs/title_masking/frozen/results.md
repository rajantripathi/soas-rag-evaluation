# Title-masking ablation (frozen)

Complete corpus, original questions. Hit@k in percent.

| Language | Method | Variant | n | Hit@1 | Hit@3 | Hit@5 |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| en | bm25 | title_prefix | 100 | 98.0 | 99.0 | 99.0 |
| en | e5_prefixed | title_prefix | 100 | 100.0 | 100.0 | 100.0 |
| en | bm25 | no_prefix | 100 | 93.0 | 98.0 | 98.0 |
| en | e5_prefixed | no_prefix | 100 | 98.0 | 100.0 | 100.0 |
| en | bm25 | title_masked | 100 | 68.0 | 75.0 | 78.0 |
| en | e5_prefixed | title_masked | 100 | 90.0 | 92.0 | 94.0 |
| en | bm25 | title_masked_fixed_window | 100 | 68.0 | 75.0 | 78.0 |
| en | e5_prefixed | title_masked_fixed_window | 100 | 89.0 | 93.0 | 94.0 |
| uz | bm25 | title_prefix | 96 | 81.2 | 92.7 | 99.0 |
| uz | e5_prefixed | title_prefix | 96 | 93.8 | 100.0 | 100.0 |
| uz | bm25 | no_prefix | 96 | 75.0 | 90.6 | 94.8 |
| uz | e5_prefixed | no_prefix | 96 | 87.5 | 95.8 | 97.9 |
| uz | bm25 | title_masked | 96 | 25.0 | 40.6 | 42.7 |
| uz | e5_prefixed | title_masked | 96 | 61.5 | 79.2 | 81.2 |
| uz | bm25 | title_masked_fixed_window | 96 | 24.0 | 40.6 | 41.7 |
| uz | e5_prefixed | title_masked_fixed_window | 96 | 61.5 | 79.2 | 80.2 |

Drop in Hit@3 from title_prefix to title_masked (source-group paired bootstrap, 95% interval):

| Language | Method | n | Drop (pp) | 95% interval (pp) |
| --- | --- | ---: | ---: | --- |
| en | bm25 | 100 | 24.0 | [16.0, 33.0] |
| en | e5_prefixed | 100 | 8.0 | [3.0, 14.0] |
| uz | bm25 | 96 | 52.1 | [41.7, 61.5] |
| uz | e5_prefixed | 96 | 20.8 | [13.5, 29.2] |

Question-title overlap (original questions whose text contains the target article title):

- en: 89/100 questions; 1100 candidates (1000 background)
- uz: 96/96 questions; 1096 candidates (1000 background)

Alternate-phrasing results are in `metrics.json`.
