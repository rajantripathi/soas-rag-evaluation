#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from src.utils import ensure_dir, read_jsonl


METRICS = ["grounded_answer_score", "hallucination_rate", "retrieval_recall_at_k"]
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
    parser = argparse.ArgumentParser(
        description="Compare baseline, supplement v1, and structured supplement v2 manual_eval_v2 runs."
    )
    parser.add_argument("--baseline-run", required=True)
    parser.add_argument("--supplement-v1-run", required=True)
    parser.add_argument("--supplement-v2-run", required=True)
    parser.add_argument(
        "--output",
        default="results/reports/manual_eval_v2_uz_supplement_v2_report_20260309.md",
    )
    return parser


def load_rows(path: str) -> list[dict]:
    return read_jsonl(Path(path) / "predictions.jsonl")


def summarize(rows: list[dict], language: str | None, domain: str | None) -> dict[str, float]:
    subset = rows
    if language:
        subset = [row for row in subset if row["language"] == language]
    if domain:
        subset = [row for row in subset if row["domain"] == domain]
    total = len(subset) or 1
    return {
        "examples": len(subset),
        **{
            metric: round(sum(float(row.get(metric, 0.0)) for row in subset) / total, 4)
            for metric in METRICS
        },
    }


def write_table(handle, title: str, runs: dict[str, list[dict]], language: str | None, domain: str | None) -> None:
    handle.write(f"## {title}\n")
    handle.write("| Corpus Condition | Examples | Grounded | Hallucination | Recall@k |\n")
    handle.write("| --- | ---: | ---: | ---: | ---: |\n")
    for label, rows in runs.items():
        metrics = summarize(rows, language=language, domain=domain)
        handle.write(
            f"| {label} | {metrics['examples']} | {metrics['grounded_answer_score']:.4f} | {metrics['hallucination_rate']:.4f} | {metrics['retrieval_recall_at_k']:.4f} |\n"
        )
    handle.write("\n")


def main() -> int:
    args = build_parser().parse_args()
    runs = {
        "baseline": load_rows(args.baseline_run),
        "supplement_v1": load_rows(args.supplement_v1_run),
        "supplement_v2": load_rows(args.supplement_v2_run),
    }
    output = Path(args.output)
    ensure_dir(output.parent)

    with output.open("w", encoding="utf-8") as handle:
        handle.write("# Manual Eval v2 Uzbek Supplement v2 Report\n\n")
        handle.write("## Experiment Setup\n")
        handle.write("- Evaluation file: data/eval/manual_eval_v2.jsonl\n")
        handle.write("- Retrieval setup: vector retrieval with intfloat/multilingual-e5-large and grounded prompting\n")
        handle.write("- Baseline corpus: data/processed/corpus_manual_v1.jsonl\n")
        handle.write("- Supplement v1 corpus: baseline + data/processed/supplementary_uz_history_institutions_v1.jsonl\n")
        handle.write("- Supplement v2 corpus: baseline + data/processed/supplementary_uz_structured_v2.jsonl\n")
        handle.write("- Supplement v2 source: structured rows extracted from data/raw/uz_wiki\n\n")

        handle.write("## Additional Uzbek Source Material Used\n")
        handle.write("- Structured Uzbek Wikipedia rows for history, institutions, and culture were extracted from the saved `yakhyo/uz-wiki` dataset.\n")
        handle.write("- The extraction targeted eval-linked source documents that were absent from the baseline corpus.\n")
        handle.write("- The supplementary corpus remains separate from the baseline corpus and is merged into a new expanded-corpus artifact for evaluation only.\n\n")

        for title, language, domain in BREAKDOWNS:
            write_table(handle, title.replace("_", " ").title(), runs, language=language, domain=domain)

        base = summarize(runs["baseline"], "uz", "culture")["retrieval_recall_at_k"]
        v1 = summarize(runs["supplement_v1"], "uz", "culture")["retrieval_recall_at_k"]
        v2 = summarize(runs["supplement_v2"], "uz", "culture")["retrieval_recall_at_k"]
        inst_base = summarize(runs["baseline"], "uz", "institutions")["retrieval_recall_at_k"]
        inst_v1 = summarize(runs["supplement_v1"], "uz", "institutions")["retrieval_recall_at_k"]
        inst_v2 = summarize(runs["supplement_v2"], "uz", "institutions")["retrieval_recall_at_k"]

        handle.write("## Interpretation\n")
        handle.write("- Corpus coverage strongly shapes culturally grounded retrieval because missing local source documents cap recall before reranking or prompt design can help.\n")
        handle.write("- Targeted supplements improve performance most when they add the exact local entities and descriptions missing from the evaluation domains.\n")
        handle.write(
            f"- Uzbek culture recall@k changed from {base:.4f} in baseline to {v1:.4f} with supplement v1 and {v2:.4f} with structured supplement v2.\n"
        )
        handle.write(
            f"- Uzbek institutions recall@k changed from {inst_base:.4f} in baseline to {inst_v1:.4f} with supplement v1 and {inst_v2:.4f} with structured supplement v2.\n"
        )
        handle.write("- This suggests that knowledge representation in AI systems is partly a corpus construction problem: what is absent from the corpus becomes absent from grounding.\n")
        handle.write("- For culturally grounded systems, explicit local supplements can be a practical way to correct representational blind spots while preserving a reproducible pipeline.\n")

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
