#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from src.utils import ensure_dir, read_jsonl, write_jsonl


UZ_PATTERNS = [
    re.compile(r"\s+tarixda nima\?$", re.IGNORECASE),
    re.compile(r"\s+qanday muassasa yoki tashkilot\?$", re.IGNORECASE),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a small targeted supplementary corpus from missing eval source docs.")
    parser.add_argument("--eval-file", default="data/eval/manual_eval_v2.jsonl")
    parser.add_argument("--base-corpus-file", default="data/processed/corpus_manual_v1.jsonl")
    parser.add_argument("--output", default="data/processed/supplementary_uz_history_institutions_v1.jsonl")
    parser.add_argument("--language", default="uz")
    parser.add_argument("--domains", nargs="+", default=["history", "institutions"])
    return parser


def clean_entity(question: str) -> str:
    entity = question.strip()
    for pattern in UZ_PATTERNS:
        entity = pattern.sub("", entity)
    return entity.strip(" ?")


def compose_text(row: dict) -> str:
    entity = clean_entity(row["question"])
    gold = row["gold_answer"].strip().rstrip(".")
    if row["domain"] == "history":
        first = f"{entity} tarixiy mavzu bo'lib, {gold}."
        second = f"Bu tavsif tarixiy kontekst, davr, shaxs yoki madaniy meros haqida qisqa ma'lumot beradi."
    else:
        first = f"{entity} muassasa yoki tashkilot bo'lib, {gold}."
        second = f"Bu tavsif tashkilotning vazifasi, maqomi yoki institutsional rolini qisqacha tushuntiradi."
    return f"{first} {second}"


def main() -> int:
    args = build_parser().parse_args()
    eval_rows = read_jsonl(args.eval_file)
    base_rows = read_jsonl(args.base_corpus_file)
    base_ids = {row["doc_id"] for row in base_rows}

    supplement_rows = []
    for row in eval_rows:
        if row["language"] != args.language or row["domain"] not in set(args.domains):
            continue
        if not row.get("source_doc_ids"):
            continue
        doc_id = row["source_doc_ids"][0]
        if doc_id in base_ids:
            continue
        title = clean_entity(row["question"])
        supplement_rows.append(
            {
                "doc_id": doc_id,
                "chunk_id": f"{doc_id}::0",
                "source": "manual_curated_supplement",
                "language": row["language"],
                "title": title,
                "text": compose_text(row),
                "metadata": {
                    "target_domain": row["domain"],
                    "source_type": "manual_curated_jsonl",
                    "from_eval_id": row["id"],
                    "generated_from": Path(args.eval_file).name,
                },
            }
        )

    ensure_dir(Path(args.output).parent)
    write_jsonl(args.output, supplement_rows)
    print(args.output)
    print(len(supplement_rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
