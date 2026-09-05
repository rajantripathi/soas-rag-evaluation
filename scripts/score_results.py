#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils import read_jsonl, write_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Rescore prediction JSONL into a flat CSV table.")
    parser.add_argument("predictions", help="Path to predictions.jsonl")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    rows = read_jsonl(Path(args.predictions))
    flat_rows = []
    for row in rows:
        flat_rows.append(
            {
                "id": row["id"],
                "language": row["language"],
                "grounded_answer_score": row["grounded_answer_score"],
                "hallucination_rate": row["hallucination_rate"],
                "unsupported_claim_rate": row["unsupported_claim_rate"],
                "retrieval_recall_at_k": row["retrieval_recall_at_k"],
            }
        )
    output_path = Path(args.predictions).with_suffix(".csv")
    write_csv(output_path, flat_rows)
    print(f"Wrote scored CSV to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
