#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import csv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils import ensure_dir, utc_timestamp


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize all metrics.csv files under results/.")
    parser.add_argument("--results-dir", default="results", help="Results root directory.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    results_dir = Path(args.results_dir)
    metric_files = sorted(results_dir.glob("eval_*/metrics.csv"))
    rows = []
    for metric_file in metric_files:
        with metric_file.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            rows.extend(reader)

    reports_dir = ensure_dir(results_dir / "reports")
    report_path = reports_dir / f"progress_{utc_timestamp()}.md"
    with report_path.open("w", encoding="utf-8") as handle:
        handle.write("# Progress Report\n\n")
        if not rows:
            handle.write("- No completed runs found.\n")
        else:
            for row in rows:
                handle.write(
                    "- run_dir: {run_dir}, examples: {examples}, grounded_answer_score: {grounded_answer_score}, "
                    "hallucination_rate: {hallucination_rate}, unsupported_claim_rate: {unsupported_claim_rate}, "
                    "retrieval_recall_at_k: {retrieval_recall_at_k}\n".format(**row)
                )
    print(f"Wrote report to {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
