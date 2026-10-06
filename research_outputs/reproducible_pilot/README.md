# Reproducible source-coverage diagnostic

This is a new local experiment on frozen Wikipedia revisions, separate from the historical Isambard runs. It measures designated-source retrieval after controlled removal and restoration. The target-aware corpus is not a held-out generalisation benchmark.

## Reproduce

Use Python 3.11. Create an isolated environment from the repository root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-pilot.lock.txt
python scripts/run_reproducible_pilot.py acquire
python scripts/run_reproducible_pilot.py model
python scripts/run_reproducible_pilot.py run
python scripts/run_reproducible_pilot.py report
python scripts/verify_pilot_artifacts.py
python scripts/write_pilot_manuscript.py
python scripts/build_pilot_paper.py
python -m unittest discover -s tests -v
```

`acquire` reuses the committed source manifest and fetches the exact revision IDs. It does not resample background articles when a manifest exists. Network access is needed for source and model acquisition; subsequent runs use cached source text and embeddings. If a revision is unavailable or content hashes differ, acquisition stops rather than substituting current content. Initial corpus creation samples nonredirect Wikipedia main-namespace pages once and freezes the result. The background sample is not claimed to be seed-reproducible without its manifest.

The experiment protocol is recorded in `configs/reproducible_pilot.json`. It uses CPU execution, four PyTorch threads, batches of eight, and one 480-token passage per article. Model inputs add `query: ` and `passage: ` only in the prefixed condition. The unprefixed condition is an implementation ablation. No generation or answer references are involved.

## Analysis

- Original questions are the primary analysis; alternate phrasings are a separate sensitivity analysis.
- Original benchmark IDs remain unchanged. `target_mapping.json` relates their source labels to language-scoped Wikipedia page IDs.
- Ambiguous, short, missing, nonarticle, or title-mismatched targets are excluded explicitly; at least 90 original targets must resolve per language.
- Each language has 1,000 background articles plus all resolved targets. Search is within language, not cross-lingual.
- Five source-removal masks use seeds 42–46. Each removes half the unique target pages while holding background articles fixed. All phrasings of a source share its availability.
- Dense embeddings are reused across source masks. BM25 statistics are rebuilt for each reduced corpus because IDF and document-length averages change.
- Source hit rates at 1, 3, and 5 accompany source availability and hit rate conditional on availability. Missing sources cannot be returned.
- Primary paired intervals use seed 42, k=3, and 10,000 source-group bootstrap resamples separately within each language. They condition on this corpus and removal mask, and do not measure background-sampling uncertainty.
- Quality flags are incomplete. The unflagged-original sensitivity subset is not described as a manually validated subset.

## Public artifacts

`source_manifest.json` contains article revision metadata and hashes, not article text. Source text and embeddings remain under ignored `data/reproducible_pilot/`. `model_lock.json` pins the model revision. `run_manifest.json` records versions, source hashes, protocol, runner hash, and Git commit.

Predictions contain IDs, rankings, and analysis metadata only. Prediction files contain multiple conditions; filter to one condition before passing them to the standalone evaluator. Use `evaluation_labels.jsonl` for the canonical source IDs, rather than the unchanged legacy labels. `report` checks complete prediction coverage, metadata consistency, source availability, and retrieved identifiers before generating metrics and intervals.

Wikipedia source material retains its upstream terms; the repository's MIT code licence and CC BY dataset label do not relicense downloaded article text. Reproduction retrieves source revisions from the upstream service. These small, target-aware candidate pools and automatic question templates limit interpretation to a diagnostic pilot.
