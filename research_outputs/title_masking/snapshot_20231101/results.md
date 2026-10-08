# Title-masking ablation (snapshot_20231101)

> Legacy exploratory output: uses the original substring matcher and a substitute corpus. See the [corrected frozen analysis](../README.md); these figures are not its results.

**Approximate run.** The corpus is not the hash-checked frozen pilot corpus. Article text from the Hugging Face wikimedia/wikipedia 20231101 snapshots, matched to frozen page IDs (all 96 Uzbek targets, 82 of 100 English targets). Background pages absent from the snapshot were replaced by a seeded random sample (373 Uzbek, 123 English; English fill from one snapshot shard). Frozen titles are used for prefixes and masking.

Complete corpus, original questions. Hit@k in percent.

| Language | Method | Variant | n | Hit@1 | Hit@3 | Hit@5 |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| en | bm25 | title_prefix | 82 | 96.3 | 98.8 | 98.8 |
| en | e5_prefixed | title_prefix | 82 | 98.8 | 100.0 | 100.0 |
| en | bm25 | no_prefix | 82 | 91.5 | 98.8 | 98.8 |
| en | e5_prefixed | no_prefix | 82 | 97.6 | 98.8 | 98.8 |
| en | bm25 | title_masked | 82 | 74.4 | 81.7 | 82.9 |
| en | e5_prefixed | title_masked | 82 | 87.8 | 91.5 | 91.5 |
| uz | bm25 | title_prefix | 96 | 80.2 | 91.7 | 97.9 |
| uz | e5_prefixed | title_prefix | 96 | 96.9 | 100.0 | 100.0 |
| uz | bm25 | no_prefix | 96 | 70.8 | 89.6 | 92.7 |
| uz | e5_prefixed | no_prefix | 96 | 91.7 | 95.8 | 97.9 |
| uz | bm25 | title_masked | 96 | 18.8 | 28.1 | 34.4 |
| uz | e5_prefixed | title_masked | 96 | 53.1 | 68.8 | 71.9 |

Drop in Hit@3 from title_prefix to title_masked (source-group paired bootstrap, 95% interval):

| Language | Method | n | Drop (pp) | 95% interval (pp) |
| --- | --- | ---: | ---: | --- |
| en | bm25 | 82 | 17.1 | [9.8, 25.6] |
| en | e5_prefixed | 82 | 8.5 | [3.7, 14.6] |
| uz | bm25 | 96 | 63.5 | [54.2, 72.9] |
| uz | e5_prefixed | 96 | 31.2 | [21.9, 40.6] |

Question-title overlap (original questions whose text contains the target article title):

- en: 71/82 questions; 1082 candidates (1000 background)
- uz: 96/96 questions; 1096 candidates (1000 background)

Alternate-phrasing results are in `metrics.json`.
