#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils import ensure_dir, read_jsonl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write a research-style report combining corpus supplement findings with manual_eval_v4 results."
    )
    parser.add_argument("--baseline-v2-run", required=True)
    parser.add_argument("--supplement-v1-run", required=True)
    parser.add_argument("--supplement-v2-run", required=True)
    parser.add_argument("--manual-v4-run", required=True)
    parser.add_argument("--output", default="results/reports/manual_eval_v4_research_report_20260309.md")
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


def write_table(handle, title: str, labels_to_rows: dict[str, list[dict]], language: str | None = None, domain: str | None = None) -> None:
    handle.write(f"## {title}\n")
    handle.write("| Condition | Recall@k |\n")
    handle.write("| --- | ---: |\n")
    for label, rows in labels_to_rows.items():
        handle.write(f"| {label} | {avg_recall(rows, language=language, domain=domain):.4f} |\n")
    handle.write("\n")


def main() -> int:
    args = build_parser().parse_args()
    baseline_v2 = load_rows(args.baseline_v2_run)
    supplement_v1 = load_rows(args.supplement_v1_run)
    supplement_v2 = load_rows(args.supplement_v2_run)
    manual_v4 = load_rows(args.manual_v4_run)

    output = Path(args.output)
    ensure_dir(output.parent)

    with output.open("w", encoding="utf-8") as handle:
        handle.write("# Culturally Grounded Multilingual RAG Evaluation: Corpus Coverage Report\n\n")
        handle.write("## Setup\n")
        handle.write("- Retrieval model: `intfloat/multilingual-e5-large`\n")
        handle.write("- Prompting: grounded prompt\n")
        handle.write("- Best corpus condition: expanded Uzbek supplement v2\n")
        handle.write("- `manual_eval_v4` size: 400 items, balanced as 50 items per language-domain cell\n")
        handle.write("- `manual_eval_v4` preserves all `manual_eval_v2` items and adds one deterministic alternate phrasing per original item\n\n")

        handle.write("## Baseline vs Supplement Comparison on manual_eval_v2\n")
        write_table(
            handle,
            "Overall Recall on manual_eval_v2",
            {
                "baseline corpus": baseline_v2,
                "supplement v1": supplement_v1,
                "supplement v2": supplement_v2,
            },
        )
        write_table(
            handle,
            "Uzbek Domain Recall on manual_eval_v2",
            {
                "baseline_history": [row for row in baseline_v2 if row["language"] == "uz" and row["domain"] == "history"],
                "supplement_v1_history": [row for row in supplement_v1 if row["language"] == "uz" and row["domain"] == "history"],
                "supplement_v2_history": [row for row in supplement_v2 if row["language"] == "uz" and row["domain"] == "history"],
                "baseline_institutions": [row for row in baseline_v2 if row["language"] == "uz" and row["domain"] == "institutions"],
                "supplement_v1_institutions": [row for row in supplement_v1 if row["language"] == "uz" and row["domain"] == "institutions"],
                "supplement_v2_institutions": [row for row in supplement_v2 if row["language"] == "uz" and row["domain"] == "institutions"],
                "baseline_culture": [row for row in baseline_v2 if row["language"] == "uz" and row["domain"] == "culture"],
                "supplement_v1_culture": [row for row in supplement_v1 if row["language"] == "uz" and row["domain"] == "culture"],
                "supplement_v2_culture": [row for row in supplement_v2 if row["language"] == "uz" and row["domain"] == "culture"],
            },
        )

        handle.write("## manual_eval_v4 Results with Best Setup\n")
        write_table(handle, "Overall Recall on manual_eval_v4", {"supplement v2 + manual_eval_v4": manual_v4})
        write_table(handle, "English Recall on manual_eval_v4", {"supplement v2 + manual_eval_v4": manual_v4}, language="en")
        write_table(handle, "Uzbek Recall on manual_eval_v4", {"supplement v2 + manual_eval_v4": manual_v4}, language="uz")
        for domain in ["governance", "history", "institutions", "culture"]:
            write_table(
                handle,
                f"Domain Recall on manual_eval_v4: {domain}",
                {"english": [row for row in manual_v4 if row["language"] == "en" and row["domain"] == domain],
                 "uzbek": [row for row in manual_v4 if row["language"] == "uz" and row["domain"] == domain]},
            )

        handle.write("## Analysis\n")
        handle.write("- Baseline versus supplement runs show that corpus coverage, not prompt choice or chunk size alone, is the dominant bottleneck for culturally grounded Uzbek retrieval.\n")
        handle.write("- Targeted cultural knowledge sources improve retrieval most when they add the exact local entities, institutions, and historical subjects that the baseline corpus does not contain.\n")
        handle.write("- Supplement v1 demonstrated that a small curated corpus patch can resolve hard Uzbek history and institutions gaps.\n")
        handle.write("- Supplement v2 showed that a more general structured-source expansion from Uzbek Wikipedia can extend those gains to culture while preserving English performance.\n")
        handle.write("- This implies that knowledge representation in AI systems is partly a corpus design problem: if culturally specific knowledge is absent or weakly represented, retrieval quality will systematically underperform for those communities.\n")
        handle.write("- For culturally grounded AI systems, reproducible local supplements are a practical mechanism for improving grounding without destabilizing the rest of the pipeline.\n")

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
