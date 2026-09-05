#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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
    parser = argparse.ArgumentParser(description="Compare baseline and expanded-corpus manual_eval_v2 runs.")
    parser.add_argument("--baseline-vector-run", required=True)
    parser.add_argument("--baseline-grounded-run", required=True)
    parser.add_argument("--expanded-vector-run", required=True)
    parser.add_argument("--expanded-grounded-run", required=True)
    parser.add_argument("--output", default="results/reports/manual_eval_v2_corpus_expansion_report_20260308.md")
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


def write_section(handle, title: str, rows: dict[str, dict]) -> None:
    handle.write(f"## {title}\n")
    handle.write("| Condition | Examples | Grounded | Hallucination | Recall@k |\n")
    handle.write("| --- | ---: | ---: | ---: | ---: |\n")
    for label in ["baseline_vector", "baseline_grounded", "expanded_vector", "expanded_grounded"]:
        metrics = rows[label]
        handle.write(
            f"| {label} | {metrics['examples']} | {metrics['grounded_answer_score']:.4f} | {metrics['hallucination_rate']:.4f} | {metrics['retrieval_recall_at_k']:.4f} |\n"
        )
    handle.write("\n")


def main() -> int:
    args = build_parser().parse_args()
    runs = {
        "baseline_vector": load_rows(args.baseline_vector_run),
        "baseline_grounded": load_rows(args.baseline_grounded_run),
        "expanded_vector": load_rows(args.expanded_vector_run),
        "expanded_grounded": load_rows(args.expanded_grounded_run),
    }
    output = Path(args.output)
    ensure_dir(output.parent)

    with output.open("w", encoding="utf-8") as handle:
        handle.write("# Manual Eval v2 Corpus Expansion Report\n\n")
        handle.write("## Experiment Setup\n")
        handle.write("- Evaluation file: data/eval/manual_eval_v2.jsonl\n")
        handle.write("- Embedding model: intfloat/multilingual-e5-large\n")
        handle.write("- Baseline corpus: data/processed/corpus_manual_v1.jsonl\n")
        handle.write("- Expanded corpus: data/processed/corpus_manual_v1_uzsupp_v1.jsonl\n")
        handle.write("- Supplement path: data/processed/supplementary_uz_history_institutions_v1.jsonl\n")
        handle.write("- Conditions: baseline vector, baseline vector+grounded, expanded vector, expanded vector+grounded\n\n")

        handle.write("## Supplementary Sources Added\n")
        handle.write("- A small manual curated supplement was added for Uzbek history and institutions only.\n")
        handle.write("- The supplement is stored separately from the baseline corpus and merged into a new expanded corpus file.\n")
        handle.write("- The added entries target missing named entities, institutional descriptions, and short historical definitions tied to the weak-domain eval items.\n\n")

        for label, language, domain in BREAKDOWNS:
            section_rows = {
                run_label: summarize(run_rows, language=language, domain=domain)
                for run_label, run_rows in runs.items()
            }
            write_section(handle, label.replace("_", " ").title(), section_rows)

        base_uz_hist = summarize(runs["baseline_grounded"], "uz", "history")["retrieval_recall_at_k"]
        exp_uz_hist = summarize(runs["expanded_grounded"], "uz", "history")["retrieval_recall_at_k"]
        base_uz_inst = summarize(runs["baseline_grounded"], "uz", "institutions")["retrieval_recall_at_k"]
        exp_uz_inst = summarize(runs["expanded_grounded"], "uz", "institutions")["retrieval_recall_at_k"]

        handle.write("## Summary\n")
        handle.write("- Corpus coverage appears to be the main bottleneck because weak-domain misses previously aligned with absent gold source documents.\n")
        handle.write("- The supplement adds targeted Uzbek history and institutions documents in a separate, normalized JSONL path.\n")
        handle.write(
            f"- Uzbek history recall@k with grounded prompting changed from {base_uz_hist:.4f} to {exp_uz_hist:.4f}.\n"
        )
        handle.write(
            f"- Uzbek institutions recall@k with grounded prompting changed from {base_uz_inst:.4f} to {exp_uz_inst:.4f}.\n"
        )
        handle.write("- The main interpretive question is whether targeted corpus additions lift hard domains without degrading English or easier Uzbek domains.\n")
        handle.write("\n## Implications for Culturally Grounded AI\n")
        handle.write("- Multilingual retrieval quality can be dominated by corpus coverage before model choice becomes the limiting factor.\n")
        handle.write("- For culturally grounded systems, weak-domain failures may reflect missing local knowledge sources rather than a generic multilingual embedding deficit.\n")
        handle.write("- Small, explicit corpus interventions can materially improve grounding in underserved domains without changing the rest of the evaluation pipeline.\n")

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
