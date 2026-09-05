#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils import ensure_dir, read_jsonl


BREAKDOWNS = [
    ("overall", None, None),
    ("en", "en", None),
    ("uz", "uz", None),
    ("en_governance", "en", "governance"),
    ("en_history", "en", "history"),
    ("en_institutions", "en", "institutions"),
    ("en_culture", "en", "culture"),
    ("uz_governance", "uz", "governance"),
    ("uz_history", "uz", "history"),
    ("uz_institutions", "uz", "institutions"),
    ("uz_culture", "uz", "culture"),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare vector, BM25, and hybrid retrieval on manual_eval_v4.")
    parser.add_argument("--vector-run", required=True)
    parser.add_argument("--bm25-run", required=True)
    parser.add_argument("--hybrid-run", required=True)
    parser.add_argument("--output", default="results/reports/manual_eval_v4_hybrid_report_20260309.md")
    return parser


def load_rows(run_dir: str) -> list[dict]:
    return read_jsonl(Path(run_dir) / "predictions.jsonl")


def avg_recall(rows: list[dict], language: str | None = None, domain: str | None = None) -> float:
    subset = rows
    if language:
        subset = [row for row in subset if row["language"] == language]
    if domain:
        subset = [row for row in subset if row["domain"] == domain]
    if not subset:
        return 0.0
    return round(sum(float(row["retrieval_recall_at_k"]) for row in subset) / len(subset), 4)


def write_table(handle, title: str, vector_rows: list[dict], bm25_rows: list[dict], hybrid_rows: list[dict], language: str | None, domain: str | None) -> None:
    handle.write(f"## {title}\n")
    handle.write("| System | Recall@k |\n")
    handle.write("| --- | ---: |\n")
    handle.write(f"| vector_only | {avg_recall(vector_rows, language=language, domain=domain):.4f} |\n")
    handle.write(f"| bm25_only | {avg_recall(bm25_rows, language=language, domain=domain):.4f} |\n")
    handle.write(f"| hybrid | {avg_recall(hybrid_rows, language=language, domain=domain):.4f} |\n\n")


def main() -> int:
    args = build_parser().parse_args()
    vector_rows = load_rows(args.vector_run)
    bm25_rows = load_rows(args.bm25_run)
    hybrid_rows = load_rows(args.hybrid_run)

    output = Path(args.output)
    ensure_dir(output.parent)
    with output.open("w", encoding="utf-8") as handle:
        handle.write("# manual_eval_v4 Hybrid Retrieval Report\n\n")
        handle.write("## Setup\n")
        handle.write("- Corpus: data/processed/corpus_manual_v1_uzsupp_v2.jsonl\n")
        handle.write("- Eval set: data/eval/manual_eval_v4.jsonl\n")
        handle.write("- Embedding model: intfloat/multilingual-e5-large\n")
        handle.write("- Prompting: grounded prompt\n")
        handle.write("- Hybrid strategy: retrieve top-k from BM25 and top-k from vector, merge candidates, rerank by vector similarity\n\n")
        for label, language, domain in BREAKDOWNS:
            write_table(handle, label.replace("_", " ").title(), vector_rows, bm25_rows, hybrid_rows, language, domain)
        handle.write("## Summary\n")
        handle.write("- Hybrid retrieval is useful only if lexical candidates recover relevant documents that vector retrieval misses.\n")
        handle.write("- The main question is whether hybrid improves Uzbek recall without degrading English retrieval.\n")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
