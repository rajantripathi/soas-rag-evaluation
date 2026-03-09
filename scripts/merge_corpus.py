#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from src.utils import ensure_dir, read_jsonl, write_jsonl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Merge one or more normalized corpus JSONL files without overwriting base doc_ids.")
    parser.add_argument("--base-corpus", required=True)
    parser.add_argument("--supplement", action="append", required=True, help="Supplementary corpus JSONL file. Repeat for multiple files.")
    parser.add_argument("--output", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    merged = []
    seen: set[str] = set()

    for row in read_jsonl(args.base_corpus):
        merged.append(row)
        seen.add(row["doc_id"])

    for supplement_path in args.supplement:
        for row in read_jsonl(supplement_path):
            if row["doc_id"] in seen:
                continue
            merged.append(row)
            seen.add(row["doc_id"])

    ensure_dir(Path(args.output).parent)
    write_jsonl(args.output, merged)
    print(args.output)
    print(len(merged))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
