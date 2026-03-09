#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.retrieval import build_index
from src.utils import ensure_dir, load_config, read_jsonl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a smoke vector index from normalized corpus JSONL.")
    parser.add_argument("--config", default="configs/exp_smoke.yaml", help="Path to YAML config.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config = load_config(args.config)
    corpus_filename = config["paths"].get("corpus_file", "corpus_smoke.jsonl")
    index_name = config["paths"].get("index_name", "smoke_index")
    corpus_path = Path(config["paths"]["processed_data_dir"]) / corpus_filename
    index_dir = ensure_dir(Path(config["paths"]["index_dir"]) / index_name)
    documents = read_jsonl(corpus_path)
    backend = config["retrieval"]["backend"]
    model_name = config["retrieval"].get("model_name")
    index = build_index(documents, backend=backend, model_name=model_name)
    index.save(index_dir)
    with (index_dir / "metadata.json").open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "index_type": backend,
                "documents": len(documents),
                "retrieval_backend": backend,
                "model_name": model_name,
            },
            handle,
            indent=2,
        )
    print(f"Wrote index to {index_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
