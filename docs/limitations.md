# Limitations

## Evaluation Scope
- The benchmark is manually curated and still moderate in size even after expansion to `manual_eval_v4`.
- The public repository exposes only a small sample of the evaluation data.

## Metrics
- The current pipeline emphasizes retrieval recall and heuristic grounding-oriented metrics.
- A stronger model-backed judge or human evaluation layer would strengthen future analysis.

## Corpus Coverage
- Uzbek coverage improved substantially after supplementation, but this does not imply full coverage of Uzbek institutional, legal, and historical knowledge.
- English history and institutions remained relatively weaker under the final setup, showing that source asymmetry still matters.

## Public Repository Constraints
- Full raw datasets, processed corpora, indexes, and HPC run directories are intentionally excluded from git.
- The public repository is therefore a lightweight benchmark and reporting bundle rather than a full archival snapshot of cluster storage.
