#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.orchestration import run_evaluation
from src.retrieval import HybridIndex, load_index
from src.utils import ensure_dir, load_config, read_jsonl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a smoke evaluation with no-retrieval or vector retrieval.")
    parser.add_argument("--config", default="configs/exp_smoke.yaml", help="Path to YAML config.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config = load_config(args.config)
    eval_filename = config["paths"].get("eval_file", "smoke_eval.jsonl")
    index_name = config["paths"].get("index_name", "smoke_index")
    eval_examples = read_jsonl(Path(config["paths"]["eval_data_dir"]) / eval_filename)
    index = None
    if config["experiment"]["retrieval_mode"] == "vector":
        backend = config["retrieval"]["backend"]
        index_dir = Path(config["paths"]["index_dir"])
        if backend == "hybrid":
            vector_index_name = config["paths"]["vector_index_name"]
            lexical_index_name = config["paths"]["lexical_index_name"]
            vector_index = load_index(index_dir / vector_index_name, "embedding")
            lexical_index = load_index(index_dir / lexical_index_name, "bm25")
            index = HybridIndex.from_components(lexical_index, vector_index)
        else:
            index = load_index(index_dir / index_name, backend)
    results_root = ensure_dir(Path(config["paths"]["results_dir"]))
    run_dir = run_evaluation(config, eval_examples, index, results_root)
    print(f"Wrote evaluation run to {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
