#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

from src.utils import ensure_dir, read_jsonl, write_jsonl


EN_PREFIX_RE = re.compile(
    r"^(What is|What are|What does|How important is|How is|Why is|What kind of|What place, state, or political entity is|What institution, organization, or formal body is)\s+",
    re.IGNORECASE,
)
UZ_SUFFIXES = [
    " qanday muassasa yoki tashkilot?",
    " qanday institut, muassasa yoki tashkilot?",
    " tarixda nima?",
    " tarixiy jihatdan nima?",
    " siyosiy-geografik jihatdan nima?",
    " qaysi til?",
    " nima?",
]


TEMPLATES = {
    ("en", "governance"): [
        "How is {subject} described as a political or territorial entity?",
        "What kind of governed place or polity is {subject}?",
    ],
    ("en", "history"): [
        "How is {subject} situated in historical context?",
        "What historical subject or period does {subject} refer to?",
    ],
    ("en", "institutions"): [
        "How is {subject} described as an institution or formal organization?",
        "What type of institution or organized body is {subject}?",
    ],
    ("en", "culture"): [
        "How is {subject} described as a cultural or intellectual subject?",
        "What cultural concept, practice, or subject is {subject}?",
    ],
    ("uz", "governance"): [
        "{subject} qanday hudud, davlat yoki siyosiy birlik?",
        "{subject} siyosiy-geografik jihatdan nima?",
    ],
    ("uz", "history"): [
        "{subject} tarixiy jihatdan nima?",
        "{subject} tarixiy kontekstda nima?",
    ],
    ("uz", "institutions"): [
        "{subject} qanday institut, muassasa yoki tashkilot?",
        "{subject} institutsional jihatdan nima?",
    ],
    ("uz", "culture"): [
        "{subject} madaniy yoki ijtimoiy jihatdan nima?",
        "{subject} qanday madaniy tushuncha yoki mavzu?",
    ],
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Expand manual_eval_v2 to a balanced 400-item manual_eval_v4 set by adding deterministic alternate phrasings."
    )
    parser.add_argument("--input", default="data/eval/manual_eval_v2.jsonl")
    parser.add_argument("--corpus", default="data/processed/corpus_manual_v1_uzsupp_v2.jsonl")
    parser.add_argument("--output", default="data/eval/manual_eval_v4.jsonl")
    return parser


def normalize_language(value: str) -> str:
    return "en" if value == "english" else value


def infer_subject(row: dict, title_lookup: dict[str, str]) -> str:
    doc_ids = row.get("source_doc_ids", [])
    if doc_ids:
        doc_id = str(doc_ids[0])
        title = title_lookup.get(doc_id, "").strip()
        if title:
            return title
        if not doc_id.isdigit():
            return doc_id
    question = row["question"].strip()
    if row["language"] == "en":
        question = EN_PREFIX_RE.sub("", question)
        return question.rstrip("?").strip()
    lowered = question
    for suffix in UZ_SUFFIXES:
        if lowered.endswith(suffix):
            return lowered[: -len(suffix)].strip()
    return question.rstrip("?").strip()


def generate_variant_question(row: dict, subject: str, index: int) -> str:
    templates = TEMPLATES[(row["language"], row["domain"])]
    for offset in range(len(templates)):
        candidate = templates[(index + offset) % len(templates)].format(subject=subject).strip()
        if candidate != row["question"].strip():
            return candidate
    return f"{subject} nima?"


def validate_schema(rows: list[dict]) -> None:
    required = {
        "id",
        "language",
        "domain",
        "question",
        "gold_answer",
        "cultural_specificity",
        "answerable",
        "source_doc_ids",
    }
    for row in rows:
        missing = required - set(row)
        if missing:
            raise ValueError(f"Row {row.get('id')} missing fields: {sorted(missing)}")


def main() -> int:
    args = build_parser().parse_args()
    seed_rows = read_jsonl(args.input)
    corpus_rows = read_jsonl(args.corpus)
    title_lookup = {str(row["doc_id"]): row.get("title", "") for row in corpus_rows}

    output_rows = list(seed_rows)
    existing_ids = {row["id"] for row in seed_rows}

    grouped: dict[tuple[str, str], list[dict]] = {}
    for row in seed_rows:
        grouped.setdefault((row["language"], row["domain"]), []).append(row)

    for key, rows in grouped.items():
        rows = sorted(rows, key=lambda row: row["id"])
        for idx, row in enumerate(rows):
            subject = infer_subject(row, title_lookup)
            new_id = f"{key[0]}_{key[1]}_v4_{idx:02d}"
            if new_id in existing_ids:
                raise ValueError(f"Generated duplicate id: {new_id}")
            output_rows.append(
                {
                    "id": new_id,
                    "language": row["language"],
                    "domain": row["domain"],
                    "question": generate_variant_question(row, subject=subject, index=idx),
                    "gold_answer": row["gold_answer"],
                    "cultural_specificity": row["cultural_specificity"],
                    "answerable": row["answerable"],
                    "source_doc_ids": list(row["source_doc_ids"]),
                }
            )
            existing_ids.add(new_id)

    validate_schema(output_rows)
    counts = Counter((row["language"], row["domain"]) for row in output_rows)
    for language in ["en", "uz"]:
        for domain in ["governance", "history", "institutions", "culture"]:
            if counts[(language, domain)] != 50:
                raise ValueError(f"Expected 50 rows for {(language, domain)}, found {counts[(language, domain)]}")

    ensure_dir(Path(args.output).parent)
    write_jsonl(args.output, output_rows)
    print(args.output)
    print(len(output_rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
