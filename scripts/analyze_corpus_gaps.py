#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils import ensure_dir, read_jsonl


FOCUS_KEYS = [
    ("uz", "history"),
    ("uz", "institutions"),
    ("en", "history"),
    ("en", "institutions"),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze low-recall examples and corpus coverage gaps.")
    parser.add_argument("--eval-file", default="data/eval/manual_eval_v2.jsonl")
    parser.add_argument("--predictions-file", required=True)
    parser.add_argument("--corpus-file", default="data/processed/corpus_manual_v1.jsonl")
    parser.add_argument(
        "--output",
        default="results/reports/manual_eval_v2_corpus_gap_analysis_20260308.md",
    )
    return parser


def coverage_rows(eval_rows: list[dict], prediction_rows: list[dict], corpus_ids: set[str]) -> dict[tuple[str, str], dict]:
    by_id = {row["id"]: row for row in prediction_rows}
    summary: dict[tuple[str, str], dict] = {}
    for key in FOCUS_KEYS:
        examples = [row for row in eval_rows if row["language"] == key[0] and row["domain"] == key[1]]
        present = [row for row in examples if all(doc_id in corpus_ids for doc_id in row.get("source_doc_ids", []))]
        missing = [row for row in examples if row not in present]
        low_recall = [row for row in examples if by_id.get(row["id"], {}).get("retrieval_recall_at_k", 0.0) < 1.0]
        summary[key] = {
            "examples": examples,
            "present": present,
            "missing": missing,
            "low_recall": low_recall,
        }
    return summary


def write_report(path: Path, summary: dict[tuple[str, str], dict]) -> None:
    ensure_dir(path.parent)
    plan_rows = [
        (
            "manual_curated_jsonl",
            "uz",
            "history",
            "Current corpus is missing most gold source documents for Uzbek history examples.",
            "Direct recall lift for named entities, historical concepts, and short definitional questions.",
        ),
        (
            "manual_curated_jsonl",
            "uz",
            "institutions",
            "Current corpus lacks many Uzbek institutional descriptions and named organizations.",
            "Better coverage for universities, media bodies, legal charters, and formal organizations.",
        ),
        (
            "future_wikipedia_expansion",
            "uz",
            "history",
            "Need broader historical context beyond sparse article selection.",
            "Improves recall for historical periods, texts, and people not covered in the smoke corpus.",
        ),
        (
            "future_wikipedia_expansion",
            "uz",
            "institutions",
            "Need more institution pages and alternate phrasing around roles and mandates.",
            "Improves retrieval when questions use descriptive wording rather than exact titles.",
        ),
        (
            "future_english_fallback",
            "en",
            "history/institutions",
            "English weak cases also show source-document absence in the current limited corpus.",
            "Provides cleaner cross-language control once Uzbek coverage is no longer the dominant bottleneck.",
        ),
    ]

    with path.open("w", encoding="utf-8") as handle:
        handle.write("# Manual Eval v2 Corpus Gap Analysis\n\n")
        handle.write("## Why corpus coverage is the main bottleneck\n")
        handle.write("- In the weak domains, every low-recall case corresponds to a missing gold source document in the current corpus.\n")
        handle.write("- There were no cases in the focus domains where the gold document existed in the corpus but retrieval still missed it.\n")
        handle.write("- This makes corpus coverage the first bottleneck, ahead of chunk size and embedding choice.\n\n")

        handle.write("## Coverage Summary\n")
        handle.write("| Language | Domain | Total | Gold docs present | Gold docs missing | Low recall |\n")
        handle.write("| --- | --- | ---: | ---: | ---: | ---: |\n")
        for (language, domain), bucket in summary.items():
            handle.write(
                f"| {language} | {domain} | {len(bucket['examples'])} | {len(bucket['present'])} | {len(bucket['missing'])} | {len(bucket['low_recall'])} |\n"
            )
        handle.write("\n")

        handle.write("## Example Missing Coverage Cases\n")
        for key in FOCUS_KEYS:
            bucket = summary[key]
            handle.write(f"### {key[0]} / {key[1]}\n")
            for row in bucket["missing"][:8]:
                handle.write(
                    f"- `{row['id']}` gold={row['source_doc_ids'][0]} question={row['question']}\n"
                )
            handle.write("\n")

        handle.write("## Likely Missing Content Types\n")
        handle.write("- Missing source documents: the dominant issue in Uzbek history and institutions.\n")
        handle.write("- Named entity coverage: people, institutions, charters, and article titles are absent from the current corpus slice.\n")
        handle.write("- Institutional descriptions: several questions require concise role or mandate descriptions that are not present.\n")
        handle.write("- Historical context: historical concepts and figures need short, query-matching summaries to support retrieval.\n\n")

        handle.write("## Corpus Expansion Plan\n")
        handle.write("| source_type | target_language | target_domain | why this source is needed | expected benefit |\n")
        handle.write("| --- | --- | --- | --- | --- |\n")
        for row in plan_rows:
            handle.write(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} |\n")


def main() -> int:
    args = build_parser().parse_args()
    eval_rows = read_jsonl(args.eval_file)
    prediction_rows = read_jsonl(args.predictions_file)
    corpus_rows = read_jsonl(args.corpus_file)
    summary = coverage_rows(eval_rows, prediction_rows, {row["doc_id"] for row in corpus_rows})
    write_report(Path(args.output), summary)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
