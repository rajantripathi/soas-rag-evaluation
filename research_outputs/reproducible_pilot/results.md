# Reproducible coverage diagnostic results

New local experiment on frozen Wikipedia revisions. Not a reproduction of the historical corpus or an unseen-source evaluation. Primary analysis uses original questions; intervals condition on the frozen corpus and seed-42 removal.

| Language | Method | Condition | Questions | Source availability | Hit@3 | Hit@3 given availability |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| en | bm25 | full | 100 | 100.0% | 99.0% | 99.0% |
| en | bm25 | removed_42 | 100 | 50.0% | 49.0% | 98.0% |
| en | bm25 | removed_43 | 100 | 50.0% | 49.0% | 98.0% |
| en | bm25 | removed_44 | 100 | 50.0% | 49.0% | 98.0% |
| en | bm25 | removed_45 | 100 | 50.0% | 50.0% | 100.0% |
| en | bm25 | removed_46 | 100 | 50.0% | 49.0% | 98.0% |
| en | e5_prefixed | full | 100 | 100.0% | 100.0% | 100.0% |
| en | e5_prefixed | removed_42 | 100 | 50.0% | 50.0% | 100.0% |
| en | e5_prefixed | removed_43 | 100 | 50.0% | 50.0% | 100.0% |
| en | e5_prefixed | removed_44 | 100 | 50.0% | 50.0% | 100.0% |
| en | e5_prefixed | removed_45 | 100 | 50.0% | 50.0% | 100.0% |
| en | e5_prefixed | removed_46 | 100 | 50.0% | 50.0% | 100.0% |
| en | e5_unprefixed | full | 100 | 100.0% | 100.0% | 100.0% |
| en | e5_unprefixed | removed_42 | 100 | 50.0% | 50.0% | 100.0% |
| en | e5_unprefixed | removed_43 | 100 | 50.0% | 50.0% | 100.0% |
| en | e5_unprefixed | removed_44 | 100 | 50.0% | 50.0% | 100.0% |
| en | e5_unprefixed | removed_45 | 100 | 50.0% | 50.0% | 100.0% |
| en | e5_unprefixed | removed_46 | 100 | 50.0% | 50.0% | 100.0% |
| uz | bm25 | full | 96 | 100.0% | 92.7% | 92.7% |
| uz | bm25 | removed_42 | 96 | 50.0% | 47.9% | 95.8% |
| uz | bm25 | removed_43 | 96 | 50.0% | 46.9% | 93.8% |
| uz | bm25 | removed_44 | 96 | 50.0% | 45.8% | 91.7% |
| uz | bm25 | removed_45 | 96 | 50.0% | 49.0% | 97.9% |
| uz | bm25 | removed_46 | 96 | 50.0% | 49.0% | 97.9% |
| uz | e5_prefixed | full | 96 | 100.0% | 100.0% | 100.0% |
| uz | e5_prefixed | removed_42 | 96 | 50.0% | 50.0% | 100.0% |
| uz | e5_prefixed | removed_43 | 96 | 50.0% | 50.0% | 100.0% |
| uz | e5_prefixed | removed_44 | 96 | 50.0% | 50.0% | 100.0% |
| uz | e5_prefixed | removed_45 | 96 | 50.0% | 50.0% | 100.0% |
| uz | e5_prefixed | removed_46 | 96 | 50.0% | 50.0% | 100.0% |
| uz | e5_unprefixed | full | 96 | 100.0% | 100.0% | 100.0% |
| uz | e5_unprefixed | removed_42 | 96 | 50.0% | 50.0% | 100.0% |
| uz | e5_unprefixed | removed_43 | 96 | 50.0% | 50.0% | 100.0% |
| uz | e5_unprefixed | removed_44 | 96 | 50.0% | 50.0% | 100.0% |
| uz | e5_unprefixed | removed_45 | 96 | 50.0% | 50.0% | 100.0% |
| uz | e5_unprefixed | removed_46 | 96 | 50.0% | 50.0% | 100.0% |

## Paired differences at k=3 (full minus seed-42 reduced corpus)

| Language | Method | Difference | 95% source-bootstrap interval |
| --- | --- | ---: | --- |
| en | bm25 | 50.0 pp | [40.0, 60.0] pp |
| en | e5_prefixed | 50.0 pp | [40.0, 60.0] pp |
| en | e5_unprefixed | 50.0 pp | [40.0, 60.0] pp |
| uz | bm25 | 44.8 pp | [34.4, 55.2] pp |
| uz | e5_prefixed | 50.0 pp | [39.6, 60.4] pp |
| uz | e5_unprefixed | 50.0 pp | [39.6, 60.4] pp |

All cutoffs, variant and unflagged sensitivity results are in `metrics.json`. Unflagged is not equivalent to independently validated. Background articles were sampled once; bootstrap intervals do not account for background-corpus selection. Source restoration uses the full frozen condition.
