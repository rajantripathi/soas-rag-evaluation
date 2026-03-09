#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


METRICS = [
    "grounded_answer_score",
    "hallucination_rate",
    "unsupported_claim_rate",
    "retrieval_recall_at_k",
]


def summarize(rows: list[dict]) -> dict[str, float]:
    total = len(rows)
    output: dict[str, float] = {"examples": total}
    for metric in METRICS:
        output[metric] = round(sum(float(row.get(metric, 0.0)) for row in rows) / max(total, 1), 4)
    return output


def load_rows(run_dir: Path) -> list[dict]:
    predictions = run_dir / "predictions.jsonl"
    with predictions.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a concise manual_eval_v2 comparison report.")
    parser.add_argument("--none-run", required=True, help="Run directory for the no-retrieval condition.")
    parser.add_argument("--vector-run", required=True, help="Run directory for the vector condition.")
    parser.add_argument(
        "--vector-grounded-run",
        required=True,
        help="Run directory for the vector + grounded prompt condition.",
    )
    parser.add_argument(
        "--output",
        default="results/reports/manual_eval_v2_comparison_20260308.md",
        help="Markdown output path.",
    )
    return parser


def write_table(handle, title: str, section: str, summary: dict[str, dict]) -> None:
    handle.write(f"## {title}\n")
    handle.write("| Run | Examples | Grounded | Hallucination | Unsupported | Recall@k |\n")
    handle.write("| --- | ---: | ---: | ---: | ---: | ---: |\n")
    for run_name in ["none", "vector", "vector_grounded"]:
        row = summary[run_name][section]
        handle.write(
            "| {run} | {examples} | {grounded:.4f} | {hallucination:.4f} | {unsupported:.4f} | {recall:.4f} |\n".format(
                run=run_name,
                examples=row["examples"],
                grounded=row["grounded_answer_score"],
                hallucination=row["hallucination_rate"],
                unsupported=row["unsupported_claim_rate"],
                recall=row["retrieval_recall_at_k"],
            )
        )
    handle.write("\n")


def main() -> int:
    args = build_parser().parse_args()
    runs = {
        "none": Path(args.none_run),
        "vector": Path(args.vector_run),
        "vector_grounded": Path(args.vector_grounded_run),
    }

    summary: dict[str, dict[str, dict]] = {}
    for name, run_dir in runs.items():
        rows = load_rows(run_dir)
        summary[name] = {
            "overall": summarize(rows),
            "en": summarize([row for row in rows if row["language"] == "en"]),
            "uz": summarize([row for row in rows if row["language"] == "uz"]),
            "run_dir": {"path": str(run_dir)},
        }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        handle.write("# Manual Eval v2 Comparison\n\n")
        handle.write("## Experiment Setup\n")
        handle.write("- Evaluation file: data/eval/manual_eval_v2.jsonl\n")
        handle.write("- Total examples: 200\n")
        handle.write("- Language balance: 100 English, 100 Uzbek\n")
        handle.write("- Domain balance per language: 25 governance, 25 history, 25 institutions, 25 culture\n")
        handle.write("- Fixed parameters: same corpus, same index, same stub generator, same retrieval backend, same top_k\n")
        handle.write("- Conditions: none, vector, vector plus grounded prompt\n\n")

        write_table(handle, "Overall Results", "overall", summary)
        write_table(handle, "English Results", "en", summary)
        write_table(handle, "Uzbek Results", "uz", summary)

        handle.write("## Comparison Summary\n")
        handle.write("- The no-retrieval baseline uses the stub fallback text, so recall stays at zero and hallucination stays maximal.\n")
        handle.write("- Vector retrieval materially improves grounding by returning the intended source document for most items.\n")
        handle.write("- The grounded prompt variant is strongest in this stub setup because it trims the answer to the first retrieved sentence.\n\n")

        handle.write("## Caveats\n")
        handle.write("- Results come from a deterministic stub generator and heuristic metrics rather than a model-backed judge.\n")
        handle.write("- The benchmark is manually curated and still relatively small despite expansion to 200 items.\n")
        handle.write("- English coverage depends on TyDi English plus the MIRACL raw-file workaround rather than a broader production corpus.\n\n")

        handle.write("## Recommended Next Steps\n")
        handle.write("- Add a stronger generation backend and rerun the same comparison.\n")
        handle.write("- Add Slurm templates for repeatable manual_eval_v2 comparison jobs.\n")
        handle.write("- Expand culturally grounded English and Uzbek corpora beyond the current staged sources.\n")

    print(output_path)
    for name in ["none", "vector", "vector_grounded"]:
        print(name, summary[name])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
