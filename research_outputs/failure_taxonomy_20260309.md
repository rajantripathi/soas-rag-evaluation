# Failure Taxonomy

This taxonomy is based on the "Vector Retrieval Failures" section of `results/reports/manual_eval_v2_error_analysis_20260308.md`, cross-checked against the Isambard baseline corpus (`data/processed/corpus_manual_v1.jsonl`) and the supplemented corpus (`data/processed/corpus_manual_v1_uzsupp_v2.jsonl`).

## Case-Level Classification

| id | language | domain | failure_type | confidence | notes |
|----|----------|--------|--------------|------------|-------|
| en_83 | en | history | corpus_gap | high | The labeled source document `Geological history of oxygen` is absent from the baseline index. This is a hard retrieval impossibility, not a ranking miss. |
| en_61 | en | governance | domain_misclassification | high | The source document exists in the baseline corpus, but the question asks "What place, state, or political entity is List of battleships of the United States Navy?" The entity is a list article, not a polity. Secondary issue: retrieval_confusion after a bad template assignment. |
| uz_93 | uz | institutions | question_quality | high | The question "Institut qanday muassasa yoki tashkilot?" is semantically underspecified and collapses to a bare generic noun. Secondary issue: the gold document `14516` (`Institut`) is also absent from the baseline corpus. |
| uz_42 | uz | institutions | corpus_gap | medium | The baseline corpus does not contain gold doc `1887`. In the supplemented corpus this resolves to `Oʻzbekistondagi universitetlar`, so the item was impossible under the baseline index. Secondary issue: plural list-style entity phrasing may further weaken retrieval. |
| uz_58 | uz | culture | corpus_gap | high | The baseline corpus does not contain gold doc `2198` (`Microsoft Windows`). The query itself is straightforward. |
| uz_71 | uz | institutions | domain_misclassification | high | The question "Munavvarqori Abdurashidxon oʻgʻli qanday muassasa yoki tashkilot?" assigns a person to the institutions domain. Secondary issue: gold doc `2826` was absent from the baseline corpus. |
| uz_78 | uz | institutions | domain_misclassification | high | `Coldplay` is a music group, not an institution. Secondary issue: gold doc `4080` was absent from the baseline corpus. |
| uz_80 | uz | institutions | corpus_gap | high | Gold doc `5309` (`Oʻzbekiston milliy teleradiokompaniyasi`) is absent from the baseline corpus. The question itself is institution-shaped and materially answerable if the source is present. |
| uz_82 | uz | institutions | domain_misclassification | high | The question "1477 qanday muassasa yoki tashkilot?" applies an institution template to a year article. Secondary issue: gold doc `8090` was absent from the baseline corpus. |
| uz_83 | uz | institutions | domain_misclassification | high | The question "1917 qanday muassasa yoki tashkilot?" applies an institution template to a year article. Secondary issue: gold doc `8855` was absent from the baseline corpus. |
| uz_89 | uz | institutions | domain_misclassification | high | `Gmail` is an email service, not an institution or formal body. Secondary issue: gold doc `13959` was absent from the baseline corpus. |
| uz_92 | uz | institutions | corpus_gap | medium | The baseline corpus does not contain gold doc `14515` (`Universitet`). Secondary issue: the question is generic and inherits the same template weakness as `uz_93`, but the primary blocker in the baseline run is corpus absence. |

## Failure Distribution

| failure_type | english | uzbek | total |
|--------------|---------|-------|-------|
| corpus_gap | 1 | 4 | 5 |
| domain_misclassification | 1 | 5 | 6 |
| question_quality | 0 | 1 | 1 |
| entity_mismatch | 0 | 0 | 0 |
| retriever_confusion | 0 | 0 | 0 |

## Retriever Degeneration

All 10 Uzbek retrieval failures in the report retrieved at least one of the same three baseline-corpus documents: `1790`, `1570`, or `1798`. In the baseline corpus these resolve to `Muallif`, `Samarqand viloyati`, and `Astronomiya`.

This is a dense-retrieval degeneration pattern rather than 10 independent failures. When the intended source document is absent from the index, embedding similarity collapses toward a small set of semantically broad, high-density hub passages. These hubs are long, generic articles that are "close enough" to many unrelated queries, so the retriever keeps returning them as fallback neighbors.

That matters analytically because it masks a single root cause as apparent query diversity. The Uzbek misses look heterogeneous on the surface, but the dominant underlying mechanism is corpus absence in the baseline index.

Quantification:

- Uzbek retrieval failures in the report: `10`
- Uzbek failures retrieving at least one of hub docs `1790`, `1570`, or `1798`: `10`
- Share affected: `100%`

## Recommendations

| what to fix | affected items | estimated effort |
|-------------|----------------|------------------|
| Add explicit corpus-presence checks to error-analysis reports so impossible cases are separated from ranking errors before manual interpretation. | `en_83`, `uz_42`, `uz_58`, `uz_80`, `uz_92`, plus any future baseline runs with absent gold docs | low |
| Remove or relabel items where the benchmark domain template is obviously wrong for the entity type. | `en_61`, `uz_71`, `uz_78`, `uz_82`, `uz_83`, `uz_89` | medium |
| Rewrite generic institution-template questions that collapse to bare nouns and are not meaningful retrieval probes. | `uz_93`; review `uz_92` as a secondary case | low |
| Surface human-readable titles for Uzbek source IDs in audit outputs and future dataset versions so failures are interpretable without Isambard corpus access. | all Uzbek failures in this table; especially opaque IDs `1887`, `5309`, `8090`, `8855`, `13959` | medium |
| Track hub-document frequency in retrieval diagnostics to detect dense-retrieval collapse automatically. | all Uzbek failures in the baseline run; likely reusable for future dense-retrieval experiments | low |
