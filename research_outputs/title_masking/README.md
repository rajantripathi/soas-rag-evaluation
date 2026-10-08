# Title-masking sensitivity analysis

The frozen-corpus run shows that retrieval scores are sensitive to article-title evidence. It uses all 100 English and 96 Uzbek resolved targets, the original 2,000 background articles, and hash-checked article text. All baseline top-five rankings reproduce the published pilot exactly. This is a diagnostic on a target-aware pilot, not an estimate of an intrinsic English–Uzbek retrieval gap.

## Frozen results

Original questions, complete corpus, Hit@3 (%):

| Retriever | Language | Title prefix | No added prefix | Title masked | Masked fixed window |
| --- | --- | ---: | ---: | ---: | ---: |
| E5-small | English | 100.0 | 100.0 | 92.0 | 93.0 |
| E5-small | Uzbek | 100.0 | 95.8 | 79.2 | 79.2 |
| BM25 | English | 99.0 | 98.0 | 75.0 | 75.0 |
| BM25 | Uzbek | 92.7 | 90.6 | 40.6 | 40.6 |

For E5, the masked English–Uzbek difference is **12.8 percentage points** (13.8 with the fixed-window control). The within-language drops from the title-prefix baseline are 8.0 points for English [95% paired bootstrap interval: 3.0, 14.0] and 20.8 for Uzbek [13.5, 29.2]. These intervals describe each drop conditional on the fixed evaluation set; they are not intervals or significance tests for the between-language difference.

See [all results](frozen/results.md), [machine-readable metrics and provenance](frozen/metrics.json), [ranked predictions](frozen/predictions.jsonl), and [passage hashes and token lengths](frozen/passage_audit.jsonl). Alternate phrasings are reported separately and are not treated as independent sources.

## Protocol and interpretation

The four representations are applied to every candidate, including background articles:

- `title_prefix`: title + ". " + article lead, truncated to 480 model tokens, as in the pilot.
- `no_prefix`: article lead without the added title, truncated to 480 tokens.
- `title_masked`: remove the article title and its undisambiguated form from the lead, then truncate to 480 tokens.
- `title_masked_fixed_window`: first select the same 480-token lead window used by `no_prefix`, then mask it without drawing in later text.

Matching is case-insensitive and tolerates Uzbek apostrophe variants. Unicode word boundaries prevent deleting `Art` from `Earth` or `2` from `2026`; inflected forms such as `Toshkentda` remain intact. The script does not perform morphological analysis, remove synonyms or guarantee removal of all entity clues. The pinned E5 model uses query/passage prefixes; BM25 uses the same passages with k1=1.5 and b=0.75.

89/100 English and 96/96 Uzbek original questions contain the normalised target title. Natural entity mentions are legitimate retrieval evidence: removing them changes the information available to the retriever. This analysis therefore supports a claim about sensitivity to title evidence, not proof of leakage, general language capability, or the superiority of a proposed paper narrative.

Article length, subject mix, question construction, morphology and tokenizer behaviour remain possible explanations for the different drops. Full-article word counts do not establish an article-length cause when the model sees a truncated passage. The fixed-window control addresses replenishment with later text; it does not resolve the other confounds. Native-speaker questions and a held-out, independently selected corpus remain necessary for broader claims.

## Reproduce and verify

Use the pilot experiment dependencies and acquire its frozen revision cache first (see the [pilot instructions](../reproducible_pilot/README.md)):

```bash
python scripts/run_reproducible_pilot.py acquire
python scripts/run_title_masking_ablation.py
python scripts/verify_title_masking.py
```

For an existing cache, add `--cache-dir /path/to/data/reproducible_pilot`. Source text stays local. The standalone verifier requires only Python's standard library and checks all 96 metric cells, the paired bootstrap intervals, complete prediction coverage and exact baseline rankings. CI runs this verification without downloading a model.

## Earlier substitute-corpus experiment

The files in `snapshot_20231101/` are retained as an **exploratory legacy run**, produced with PR commit `af8085e`. They used 2023 snapshot text, 82 English and 96 Uzbek targets, and replacement backgrounds (including English fill sampled from one shard). The original matcher also removed substrings inside words, and masking before truncation admitted later text. Consequently the earlier 91.5% versus 68.8% result is not the result of the corrected frozen protocol and should not be used as the paper's headline. Corpus and masking changes occurred together; their separate contributions have not been isolated.

The approximate helper remains available for new experiments:

```bash
# Parquet input additionally requires pyarrow.
python scripts/prepare_snapshot_corpus.py \
    --snapshot uz=uz.parquet --snapshot en=en_rows.json --snapshot en=en_shard.parquet \
    --out data/title_masking/snapshot_20231101.jsonl
python scripts/run_title_masking_ablation.py \
    --corpus data/title_masking/snapshot_20231101.jsonl --name snapshot_corrected --note "Describe snapshot revision and shard selection"
```

The helper records input hashes and sampling provenance alongside the local corpus. Sampling is from the supplied files, not necessarily all Wikipedia. Frozen-ID rows retain their frozen title and record the snapshot title separately. The historical snapshot run does not have ranked predictions or a complete input manifest, so its aggregate figures cannot be independently verified from the checked-in artifacts alone.
