# Title-masking ablation

Most pilot questions name their source article: all 96 resolved Uzbek original questions and 71 of the 82 English questions in the approximate run contain the target title (for example "Toshkent nima?" for *Toshkent*). The near-ceiling complete-corpus Hit@3 in the frozen pilot may therefore reflect title matching rather than retrieval of content.

This ablation re-scores the same questions against three passage representations, applied to every candidate article (targets and background):

| Variant | Passage |
| --- | --- |
| `title_prefix` | "<title>. <lead text>" (the pilot protocol) |
| `no_prefix` | lead text only; the title still occurs naturally |
| `title_masked` | lead text with every occurrence of the article's own title removed |

All runs use the complete corpus, the pinned multilingual-e5-small revision with retrieval prefixes, and the repository BM25 (k1=1.5, b=0.75), with 480-token passages as in the pilot.

## Approximate run: `snapshot_20231101/`

The frozen revisions could not be fetched from the run environment (Wikipedia API rate limit), so this run uses article text from the Hugging Face `wikimedia/wikipedia` 20231101 snapshots matched to the frozen page IDs. It covers all 96 Uzbek targets and 82 of 100 English targets; missing background pages were replaced by a seeded random sample. Under the original `title_prefix` protocol, it closely reproduces the frozen pilot (E5 Hit@3 100.0% in both languages; BM25 98.8% English and 91.7% Uzbek, against 99.0% and 92.7% frozen).

Headline (original questions, Hit@3):

| Language | Retriever | Title prefix | Title masked | Drop, pp [95% interval] |
| --- | --- | ---: | ---: | --- |
| English | E5-small | 100.0% | 91.5% | 8.5 [3.7, 14.6] |
| English | BM25 | 98.8% | 81.7% | 17.1 [9.8, 25.6] |
| Uzbek | E5-small | 100.0% | 68.8% | 31.2 [21.9, 40.6] |
| Uzbek | BM25 | 91.7% | 28.1% | 63.5 [54.2, 72.9] |

Interpretation limits:

- The run is approximate: text, revisions and part of the background differ from the frozen corpus. Rerun on the frozen cache (below) before citing figures.
- Uzbek target articles are much shorter than English ones (median about 516 against 3,500 words; 15% of Uzbek targets have under 100 words), so masking removes proportionally more Uzbek content. The language difference after masking is partly an article-length effect, not only a model effect.
- Masking removes exact title strings only. Inflected forms keep their suffixes (for example "Toshkentda" becomes "da"), synonyms and partial names remain, so this is a conservative test of title reliance.
- Intervals are paired source-group bootstraps conditional on this corpus; they are descriptive, as in the pilot.

## Reproduce

Exact version, on the frozen hash-checked cache (after `python scripts/run_reproducible_pilot.py acquire`):

```bash
python scripts/run_title_masking_ablation.py
```

Approximate version, from local snapshot files:

```bash
python scripts/prepare_snapshot_corpus.py \
    --snapshot uz=uz.parquet --snapshot en=en_rows.json --snapshot en=en_shard.parquet \
    --out data/title_masking/snapshot_20231101.jsonl
python scripts/run_title_masking_ablation.py \
    --corpus data/title_masking/snapshot_20231101.jsonl --name snapshot_20231101 --note "..."
```

Snapshot article text stays under ignored `data/` and is not redistributed.
