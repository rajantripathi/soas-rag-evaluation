#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.retrieval import tokenize
from src.utils import load_config, read_jsonl, write_jsonl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Chunk a normalized corpus JSONL into smaller overlapping passages.")
    parser.add_argument("--config", required=True, help="Path to YAML config.")
    return parser


def make_chunks(text: str, chunk_size: int, overlap: int) -> list[str]:
    tokens = tokenize(text)
    if not tokens:
        return []
    step = max(chunk_size - overlap, 1)
    chunks: list[str] = []
    for start in range(0, len(tokens), step):
        window = tokens[start : start + chunk_size]
        if not window:
            break
        chunks.append(" ".join(window))
        if start + chunk_size >= len(tokens):
            break
    return chunks


def main() -> int:
    args = build_parser().parse_args()
    config = load_config(args.config)
    processed_dir = Path(config["paths"]["processed_data_dir"])
    source_file = processed_dir / config["paths"].get("source_corpus_file", "corpus_manual_v1.jsonl")
    output_file = processed_dir / config["paths"].get("corpus_file", "corpus_manual_chunked.jsonl")
    chunk_size = int(config["chunking"]["chunk_size"])
    overlap = int(config["chunking"]["overlap"])

    rows = read_jsonl(source_file)
    chunked_rows: list[dict] = []
    for row in rows:
        passages = make_chunks(row.get("text", ""), chunk_size=chunk_size, overlap=overlap)
        if not passages:
            continue
        for idx, passage in enumerate(passages):
            chunked = dict(row)
            chunked["chunk_id"] = f"{row['doc_id']}::{idx}"
            chunked["text"] = passage
            metadata = dict(row.get("metadata", {}))
            metadata.update(
                {
                    "source_corpus_file": source_file.name,
                    "chunk_size": chunk_size,
                    "overlap": overlap,
                }
            )
            chunked["metadata"] = metadata
            chunked_rows.append(chunked)

    write_jsonl(output_file, chunked_rows)
    print(output_file)
    print(len(chunked_rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
