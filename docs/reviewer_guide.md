# Evidence and reviewer guide

This repository documents an English–Uzbek retrieval pilot. It investigates whether missing source material limits retrieval in culturally specific domains. The public release supports inspection and reuse of the retrieval evaluator; it is not a complete archive of the historical compute environment.

## Evidence map

| Question | Evidence | Interpretation |
| --- | --- | --- |
| Where does 39% → 98% come from? | [v2 supplementation report](../results/reports/manual_eval_v2_uz_supplement_v2_report_20260309.md) | 100 Uzbek questions within a 200-item bilingual evaluation; same e5-large retriever, changed corpus |
| What happened on the expanded set? | [v4 research report](../results/reports/manual_eval_v4_research_report_20260309.md) | 400 items; 96% Uzbek, 63% English, 79.5% overall |
| How do embeddings compare? | [Embedding report](../results/reports/manual_eval_v2_embedding_report_20260308.md) | Compare like populations: 14-point Uzbek gain or 7.5-point overall gain |
| What is publicly released? | [Dataset card](../hf_dataset/README.md) | v5 retrieval-only metadata, 400 rows and a 30-row preview; no answer references |
| How clean are the questions? | [Quality audit](../research_outputs/dataset_quality_audit_20260309.md) | Known template artifacts, domain mismatches, and incomplete flags |
| What can be reproduced? | [Reproducibility notes](isambard_reproducibility.md) | Local scoring is available; historical runs require excluded corpora and artifacts |

## What the supplementation experiment establishes

The structured Uzbek supplement was built by finding evaluation-linked sources absent from the baseline corpus. This is a targeted coverage-repair experiment. It demonstrates retrieval changes after adding those sources, but does not estimate performance on unseen questions or sources. A held-out evaluation, with corpus decisions fixed before inspecting test targets, is needed for that claim.

The original configurations inherit `top_k: 3` from `configs/base.yaml`. The metric counts a question as a hit when any gold source document appears among the retrieved documents. The repository calls this Recall@k; it is a question-level source hit rate, not fractional recall across all relevant documents.

The 98% result belongs to v2 (100 Uzbek items); the expanded v4 result is 96% (200 Uzbek items). The v5 public dataset adds metadata to the expanded release. These phases should be cited separately.

## Statistical provenance

The [historical statistical report](../results/reports/statistical_analysis.md) contains confidence intervals, p-values, and Cohen's d values. These are retained as historical reported figures, not newly verified statistics.

There is an unresolved discrepancy between the reported Uzbek Cohen's d of 2.91 and the population-standard-deviation formula in `scripts/compute_statistics.py`. For binary item scores with means 0.39 and 0.98, that formula yields:

```text
(0.98 - 0.39) / sqrt((0.39 * 0.61 + 0.98 * 0.02) / 2) ≈ 1.64
```

This arithmetic check does not establish a replacement inferential analysis. The paired prediction files and exact run mapping are not included in the public release, so the reported paired tests and confidence intervals cannot be independently reconstructed here. The current statistics script also does not emit the historical report's complete set of comparisons or effect-size table.

Until the original aligned predictions and analysis provenance are recovered, use the descriptive recall results as the headline. Treat the historical inferential statistics as requiring verification. Shared sources, targeted curation, and multiple comparisons also limit statistical interpretation.

The earlier “7.9×” comparison divided a 59-point Uzbek-only supplementation gain by a 7.5-point bilingual embedding gain. That comparison mixes populations. The descriptive gains are 59 versus 14 points for Uzbek, or 29.5 versus 7.5 points overall; neither comparison establishes a universal advantage across tasks.

## Excluded conclusions

- English supplementation results were retracted because synthetic documents included reference-answer text.
- Stub-generated answers and heuristic grounding scores do not establish answer quality.
- The repository does not establish independent human validation, cross-lingual retrieval performance, or general performance across low-resource languages.
- The working paper and policy brief are research outputs in this repository; no publication or funding status is inferred from their filenames.

## Public checks

From the repository root, with Python 3.10 or later:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/compute_retrieval_recall.py --oracle-check --k 3
```

The tests check scoring behavior, the public dataset's shape and balance, preview consistency, and exclusion of answer-bearing fields. These checks do not validate linguistic quality or reproduce model experiments. The oracle check must not be reported as model performance.
