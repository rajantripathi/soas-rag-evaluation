#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


METRICS = ["grounded_answer_score", "hallucination_rate", "retrieval_recall_at_k"]


def load_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def summarize(rows: list[dict]) -> dict[str, float]:
    total = len(rows)
    return {
        "examples": total,
        **{metric: round(sum(float(r.get(metric, 0.0)) for r in rows) / max(total, 1), 4) for metric in METRICS},
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Report embedding comparison metrics for manual_eval_v2 runs.")
    parser.add_argument("--baseline-run", required=True)
    parser.add_argument("--e5-run", required=True)
    parser.add_argument("--mpnet-run", required=True)
    parser.add_argument("--output", default="results/reports/manual_eval_v2_embedding_report_20260308.md")
    return parser


def write_section(handle, title: str, breakdown: dict[str, dict], section: tuple[str, str] | str) -> None:
    handle.write(f"## {title}\n")
    handle.write("| Condition | Examples | Grounded | Hallucination | Recall@k |\n")
    handle.write("| --- | ---: | ---: | ---: | ---: |\n")
    for condition in ["baseline", "e5_large", "mpnet"]:
        row = breakdown[condition][section]
        handle.write(
            "| {condition} | {examples} | {grounded:.4f} | {hallucination:.4f} | {recall:.4f} |\n".format(
                condition=condition,
                examples=row["examples"],
                grounded=row["grounded_answer_score"],
                hallucination=row["hallucination_rate"],
                recall=row["retrieval_recall_at_k"],
            )
        )
    handle.write("\n")


def main() -> int:
    args = build_parser().parse_args()
    runs = {
        "baseline": Path(args.baseline_run),
        "e5_large": Path(args.e5_run),
        "mpnet": Path(args.mpnet_run),
    }
    breakdown: dict[str, dict] = {}
    for condition, run_dir in runs.items():
        rows = load_rows(run_dir / "predictions.jsonl")
        by_group: dict[tuple[str, str], list[dict]] = defaultdict(list)
        for row in rows:
            by_group[(row["language"], row["domain"])].append(row)
        breakdown[condition] = {
            "overall": summarize(rows),
            "en": summarize([r for r in rows if r["language"] == "en"]),
            "uz": summarize([r for r in rows if r["language"] == "uz"]),
        }
        for key, grouped in by_group.items():
            breakdown[condition][key] = summarize(grouped)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        handle.write("# Manual Eval v2 Embedding Comparison\n\n")
        handle.write("## Experiment Setup\n")
        handle.write("- Evaluation file: data/eval/manual_eval_v2.jsonl\n")
        handle.write("- Corpus and chunking: unchanged baseline corpus_manual_v1.jsonl\n")
        handle.write("- Retrieval mode: vector\n")
        handle.write("- Prompt style: grounded\n")
        handle.write("- Conditions: baseline simple_vector, intfloat/multilingual-e5-large, sentence-transformers/paraphrase-multilingual-mpnet-base-v2\n")
        handle.write("- All other parameters held fixed\n\n")

        write_section(handle, "Overall Results", breakdown, "overall")
        write_section(handle, "English Results", breakdown, "en")
        write_section(handle, "Uzbek Results", breakdown, "uz")

        for language, label in [("en", "English"), ("uz", "Uzbek")]:
            for domain in ["governance", "history", "institutions", "culture"]:
                write_section(handle, f"{label} {domain.title()} Results", breakdown, (language, domain))

        handle.write("## Key Findings\n")
        handle.write(
            "- Uzbek history recall@k: baseline={b:.4f}, e5_large={e5:.4f}, mpnet={mp:.4f}\n".format(
                b=breakdown["baseline"][("uz", "history")]["retrieval_recall_at_k"],
                e5=breakdown["e5_large"][("uz", "history")]["retrieval_recall_at_k"],
                mp=breakdown["mpnet"][("uz", "history")]["retrieval_recall_at_k"],
            )
        )
        handle.write(
            "- Uzbek institutions recall@k: baseline={b:.4f}, e5_large={e5:.4f}, mpnet={mp:.4f}\n".format(
                b=breakdown["baseline"][("uz", "institutions")]["retrieval_recall_at_k"],
                e5=breakdown["e5_large"][("uz", "institutions")]["retrieval_recall_at_k"],
                mp=breakdown["mpnet"][("uz", "institutions")]["retrieval_recall_at_k"],
            )
        )

    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
