#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils import ensure_dir, read_jsonl, write_jsonl


ORIGINAL_FIELDS = (
    "id",
    "language",
    "domain",
    "question",
    "gold_answer",
    "cultural_specificity",
    "answerable",
    "source_doc_ids",
)

LANGUAGES = ("en", "uz")
DOMAINS = ("governance", "history", "institutions", "culture")
DIFFICULTY_ORDER = {"hard": 0, "medium": 1, "easy": 2}
VALID_DIFFICULTIES = set(DIFFICULTY_ORDER)
VALID_QUALITY_FLAGS = {
    None,
    "domain_misclassification",
    "question_quality",
    "gold_answer_quality",
}

# Derived from the Stage 1 audit outputs.
SEED_QUALITY_FLAGS = {
    "en_20": "domain_misclassification",
    "en_62": "domain_misclassification",
    "uz_82": "domain_misclassification",
    "uz_83": "domain_misclassification",
    "uz_78": "domain_misclassification",
    "uz_89": "domain_misclassification",
    "uz_71": "domain_misclassification",
    "en_61": "domain_misclassification",
    "uz_93": "question_quality",
    "uz_92": "question_quality",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Enrich manual_eval_v4 with resolved source titles, heuristic difficulty labels, and Stage 1 quality flags."
    )
    parser.add_argument(
        "--input",
        default="data/eval/manual_eval_v4.jsonl",
        help="Path to the 400-item manual_eval_v4 JSONL dataset.",
    )
    parser.add_argument(
        "--corpus",
        default="data/processed/corpus_manual_v1_uzsupp_v2.jsonl",
        help="Path to the enriched manual corpus JSONL used for source title resolution.",
    )
    parser.add_argument(
        "--output",
        default="data/eval/manual_eval_v5.jsonl",
        help="Path to write the enriched manual_eval_v5 JSONL dataset.",
    )
    return parser


def load_required_rows(path: Path, label: str) -> list[dict[str, Any]]:
    if not path.exists():
        raise SystemExit(f"{label} not found: {path}")
    return read_jsonl(path)


def build_title_lookup(corpus_rows: list[dict[str, Any]]) -> dict[str, str]:
    from src.datasets import detect_id, detect_title

    title_lookup: dict[str, str] = {}
    seen_ids: set[str] = set()
    for row in corpus_rows:
        doc_id = detect_id(row, fallback="")
        if not doc_id:
            continue
        if doc_id in seen_ids:
            raise ValueError(f"Duplicate corpus doc_id detected: {doc_id}")
        seen_ids.add(doc_id)
        title = detect_title(row)
        if title:
            title_lookup[doc_id] = title
    return title_lookup


def resolve_source_title(item: dict[str, Any], title_lookup: dict[str, str]) -> str | None:
    source_doc_ids = item.get("source_doc_ids") or []
    if not source_doc_ids:
        return None
    return title_lookup.get(str(source_doc_ids[0]))


def classify_difficulty(item: dict[str, Any]) -> str:
    question = item["question"].lower()
    gold_words = len(item["gold_answer"].split())
    domain = item["domain"]

    if domain == "history":
        return "hard"

    reasoning_keywords_en = ["why", "how important", "how is", "what role"]
    reasoning_keywords_uz = [
        "tarixiy",
        "tarixda",
        "qanday bog'liq",
        "nima uchun",
        "qanday ahamiyatga",
    ]
    if any(keyword in question for keyword in reasoning_keywords_en + reasoning_keywords_uz):
        return "hard"

    if gold_words <= 20:
        return "easy"

    return "medium"


def build_flagged_doc_lookup(items: list[dict[str, Any]]) -> dict[tuple[str, ...], str]:
    items_by_id = {item["id"]: item for item in items}
    flagged_doc_ids: dict[tuple[str, ...], str] = {}
    for item_id, flag in SEED_QUALITY_FLAGS.items():
        row = items_by_id.get(item_id)
        if row is None:
            raise ValueError(f"Flagged seed item not found in dataset: {item_id}")
        key = tuple(str(doc_id) for doc_id in row["source_doc_ids"])
        existing = flagged_doc_ids.get(key)
        if existing is not None and existing != flag:
            raise ValueError(f"Conflicting quality flags for source_doc_ids {key}: {existing} vs {flag}")
        flagged_doc_ids[key] = flag
    return flagged_doc_ids


def assign_quality_flag(item: dict[str, Any], flagged_doc_ids: dict[tuple[str, ...], str]) -> str | None:
    if item["id"] in SEED_QUALITY_FLAGS:
        return SEED_QUALITY_FLAGS[item["id"]]
    return flagged_doc_ids.get(tuple(str(doc_id) for doc_id in item["source_doc_ids"]))


def enrich_items(items: list[dict[str, Any]], title_lookup: dict[str, str]) -> tuple[list[dict[str, Any]], dict[str, dict[str, int]]]:
    flagged_doc_ids = build_flagged_doc_lookup(items)
    resolution_counts = {language: {"resolved": 0, "total": 0} for language in LANGUAGES}
    difficulty_counts: Counter[str] = Counter()
    quality_counts: Counter[str | None] = Counter()

    enriched: list[dict[str, Any]] = []
    for item in items:
        language = item["language"]
        resolution_counts[language]["total"] += 1
        source_title = resolve_source_title(item, title_lookup)
        if source_title is not None:
            resolution_counts[language]["resolved"] += 1

        difficulty = classify_difficulty(item)
        difficulty_counts[difficulty] += 1

        quality_flag = assign_quality_flag(item, flagged_doc_ids)
        quality_counts[quality_flag] += 1

        enriched_item = dict(item)
        enriched_item["source_title"] = source_title
        enriched_item["difficulty"] = difficulty
        enriched_item["quality_flag"] = quality_flag
        enriched.append(enriched_item)

    return enriched, {
        "resolution_counts": resolution_counts,
        "difficulty_counts": dict(difficulty_counts),
        "quality_counts": {("clean" if key is None else key): value for key, value in quality_counts.items()},
    }


def validate_input_rows(items: list[dict[str, Any]]) -> None:
    if len(items) != 400:
        raise ValueError(f"Expected 400 items in manual_eval_v4, found {len(items)}")
    for item in items:
        missing = [field for field in ORIGINAL_FIELDS if field not in item]
        if missing:
            raise ValueError(f"Row {item.get('id')} missing required fields: {missing}")


def validate_output_rows(original_rows: list[dict[str, Any]], enriched_rows: list[dict[str, Any]]) -> dict[str, Any]:
    if len(enriched_rows) != 400:
        raise ValueError(f"Expected 400 output items, found {len(enriched_rows)}")

    original_by_id = {row["id"]: row for row in original_rows}
    enriched_by_id = {row["id"]: row for row in enriched_rows}

    if len(original_by_id) != len(original_rows) or len(enriched_by_id) != len(enriched_rows):
        raise ValueError("Duplicate item IDs detected")

    warnings: list[str] = []

    language_counts: Counter[str] = Counter()
    domain_counts: Counter[tuple[str, str]] = Counter()
    difficulty_counts: Counter[tuple[str, str]] = Counter()
    quality_counts: Counter[str | None] = Counter()
    resolution_counts = {language: {"resolved": 0, "total": 0} for language in LANGUAGES}

    for item_id, enriched in enriched_by_id.items():
        original = original_by_id.get(item_id)
        if original is None:
            raise ValueError(f"Unexpected output row id: {item_id}")

        for field in ORIGINAL_FIELDS:
            if enriched[field] != original[field]:
                raise ValueError(f"Field {field} changed for row {item_id}")

        for field in ("source_title", "difficulty", "quality_flag"):
            if field not in enriched:
                raise ValueError(f"Row {item_id} missing derived field: {field}")

        if enriched["difficulty"] not in VALID_DIFFICULTIES:
            raise ValueError(f"Invalid difficulty for row {item_id}: {enriched['difficulty']}")
        if enriched["quality_flag"] not in VALID_QUALITY_FLAGS:
            raise ValueError(f"Invalid quality_flag for row {item_id}: {enriched['quality_flag']}")

        language = enriched["language"]
        domain = enriched["domain"]
        if language not in LANGUAGES:
            raise ValueError(f"Invalid language for row {item_id}: {language}")
        if domain not in DOMAINS:
            raise ValueError(f"Invalid domain for row {item_id}: {domain}")

        language_counts[language] += 1
        domain_counts[(language, domain)] += 1
        difficulty_counts[(language, enriched["difficulty"])] += 1
        quality_counts[enriched["quality_flag"]] += 1
        resolution_counts[language]["total"] += 1
        if enriched["source_title"] is not None:
            resolution_counts[language]["resolved"] += 1

    for language in LANGUAGES:
        if language_counts[language] != 200:
            raise ValueError(f"Expected 200 {language} items, found {language_counts[language]}")
        for domain in DOMAINS:
            if domain_counts[(language, domain)] != 50:
                raise ValueError(
                    f"Expected 50 rows for {(language, domain)}, found {domain_counts[(language, domain)]}"
                )

    if resolution_counts["en"]["resolved"] != 200 or resolution_counts["uz"]["resolved"] != 200:
        warnings.append("Some source titles could not be resolved from the corpus.")

    return {
        "language_counts": dict(language_counts),
        "domain_counts": dict(domain_counts),
        "difficulty_counts": dict(difficulty_counts),
        "quality_counts": {("clean" if key is None else key): value for key, value in quality_counts.items()},
        "resolution_counts": resolution_counts,
        "warnings": warnings,
    }


def row_selection_key(row: dict[str, Any]) -> tuple[int, int, int, str]:
    return (
        0 if row["source_title"] is not None else 1,
        0 if row["quality_flag"] is not None else 1,
        DIFFICULTY_ORDER[row["difficulty"]],
        row["id"],
    )


def choose_cell_rows(rows: list[dict[str, Any]], count: int) -> list[dict[str, Any]]:
    ordered = sorted(rows, key=row_selection_key)
    selected: list[dict[str, Any]] = []
    used_ids: set[str] = set()

    for difficulty in ("hard", "medium", "easy"):
        for row in ordered:
            if row["id"] in used_ids or row["difficulty"] != difficulty:
                continue
            selected.append(row)
            used_ids.add(row["id"])
            break
        if len(selected) == count:
            return selected

    for row in ordered:
        if row["id"] in used_ids:
            continue
        selected.append(row)
        used_ids.add(row["id"])
        if len(selected) == count:
            break

    if len(selected) != count:
        raise ValueError(f"Unable to select {count} rows from cell of size {len(rows)}")
    return selected


def drop_priority(row: dict[str, Any]) -> tuple[int, int, int, str]:
    return (
        0 if row["source_title"] is None else 1,
        0 if row["quality_flag"] is None else 1,
        0 if row["difficulty"] == "easy" else 1,
        row["id"],
    )


def build_sample_dataset(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_cell: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_cell[(row["language"], row["domain"])].append(row)

    selected: list[dict[str, Any]] = []
    for language in LANGUAGES:
        for domain in DOMAINS:
            cell = by_cell[(language, domain)]
            selected.extend(choose_cell_rows(cell, count=4))

    sample = list(selected)
    while len(sample) > 30:
        candidates = sorted(sample, key=drop_priority)
        removed = False
        for candidate in candidates:
            remaining = [row for row in sample if row["id"] != candidate["id"]]
            flagged_count = sum(1 for row in remaining if row["quality_flag"] is not None)
            if flagged_count < 2:
                continue
            if len({row["difficulty"] for row in remaining}) < 2:
                continue
            sample = remaining
            removed = True
            break
        if not removed:
            raise ValueError("Unable to reduce sample to 30 rows while preserving constraints")

    sample_flagged = sum(1 for row in sample if row["quality_flag"] is not None)
    if sample_flagged < 2:
        raise ValueError("Sample dataset must contain at least 2 flagged items")
    if len({row["difficulty"] for row in sample}) < 2:
        raise ValueError("Sample dataset must include multiple difficulty levels")
    for language in LANGUAGES:
        for domain in DOMAINS:
            if not any(row["language"] == language and row["domain"] == domain for row in sample):
                raise ValueError(f"Sample dataset missing cell {(language, domain)}")

    return sorted(sample, key=lambda row: row["id"])


def format_markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def write_validation_report(path: Path, stats: dict[str, Any]) -> None:
    difficulty_rows = []
    for language in LANGUAGES:
        difficulty_rows.append(
            [
                language,
                str(stats["difficulty_counts"].get((language, "easy"), 0)),
                str(stats["difficulty_counts"].get((language, "medium"), 0)),
                str(stats["difficulty_counts"].get((language, "hard"), 0)),
            ]
        )

    quality_rows = [
        ["domain_misclassification", str(stats["quality_counts"].get("domain_misclassification", 0))],
        ["question_quality", str(stats["quality_counts"].get("question_quality", 0))],
        ["gold_answer_quality", str(stats["quality_counts"].get("gold_answer_quality", 0))],
        ["clean", str(stats["quality_counts"].get("clean", 0))],
    ]

    resolution_rows = []
    for language in LANGUAGES:
        resolved = stats["resolution_counts"][language]["resolved"]
        total = stats["resolution_counts"][language]["total"]
        resolution_rows.append([language, str(resolved), str(total)])

    domain_rows = []
    for language in LANGUAGES:
        domain_rows.append(
            [language] + [str(stats["domain_counts"].get((language, domain), 0)) for domain in DOMAINS]
        )

    warning_lines = stats["warnings"] or ["None"]

    with path.open("w", encoding="utf-8") as handle:
        handle.write("# manual_eval_v5 Validation Report\n\n")
        handle.write(f"- Dataset size: 400\n")
        handle.write(f"- Duplicate IDs: none\n\n")
        handle.write("## Language Distribution\n\n")
        handle.write(
            format_markdown_table(
                ["language", "count"],
                [[language, str(stats["language_counts"].get(language, 0))] for language in LANGUAGES],
            )
        )
        handle.write("\n\n## Domain Distribution\n\n")
        handle.write(format_markdown_table(["language", *DOMAINS], domain_rows))
        handle.write("\n\n## Difficulty Distribution\n\n")
        handle.write(format_markdown_table(["language", "easy", "medium", "hard"], difficulty_rows))
        handle.write("\n\n## Quality Flag Distribution\n\n")
        handle.write(format_markdown_table(["quality_flag", "count"], quality_rows))
        handle.write("\n\n## Source Title Resolution\n\n")
        handle.write(format_markdown_table(["language", "resolved", "total"], resolution_rows))
        handle.write("\n\n## Validation Warnings\n\n")
        for warning in warning_lines:
            handle.write(f"- {warning}\n")


def dataset_card_overview() -> str:
    return (
        "manual_eval_v5 is a deterministic enrichment of the 400-item bilingual retrieval benchmark for "
        "culturally grounded question answering in English and Uzbek. It preserves every v4 benchmark item "
        "exactly while adding human-readable source titles, a coarse difficulty heuristic, and auditable "
        "quality flags derived from the Stage 1 dataset audit."
    )


def write_dataset_card(path: Path, rows: list[dict[str, Any]], stats: dict[str, Any]) -> None:
    difficulty_counts = Counter(row["difficulty"] for row in rows)
    quality_counts = Counter(row["quality_flag"] for row in rows)
    total_resolved = sum(stats["resolution_counts"][language]["resolved"] for language in LANGUAGES)

    schema_rows = [
        ["id", "str", "Stable item identifier."],
        ["language", "str", "Benchmark language (`en` or `uz`)."],
        ["domain", "str", "Benchmark domain (`governance`, `history`, `institutions`, `culture`)."],
        ["question", "str", "Evaluation question text."],
        ["gold_answer", "str", "Reference answer text used for audit and downstream evaluation."],
        ["cultural_specificity", "str", "Manual cultural-specificity label retained from v4."],
        ["answerable", "bool", "Whether the item is considered answerable."],
        ["source_doc_ids", "list[str]", "Source document identifiers retained from v4."],
        ["source_title", "str | null", "Human-readable title resolved from the corpus using `source_doc_ids[0]`."],
        ["difficulty", "str", "Deterministic heuristic difficulty label: `easy`, `medium`, or `hard`."],
        ["quality_flag", "str | null", "Audit-derived label for known benchmark issues."],
    ]

    with path.open("w", encoding="utf-8") as handle:
        handle.write("# Internal QA Schema Note: manual_eval_v5\n\n")
        handle.write("## Overview\n\n")
        handle.write(dataset_card_overview() + "\n\n")
        handle.write("## Languages\n\n")
        handle.write("- English\n- Uzbek\n\n")
        handle.write("## Domains\n\n")
        handle.write("- governance\n- history\n- institutions\n- culture\n\n")
        handle.write("## Dataset Schema\n\n")
        handle.write(format_markdown_table(["field", "type", "description"], schema_rows))
        handle.write("\n\n## Difficulty Levels\n\n")
        handle.write("- `easy`: non-history items with gold answers of 20 words or fewer.\n")
        handle.write("- `medium`: items that are neither `easy` nor `hard` under the deterministic heuristic.\n")
        handle.write("- `hard`: all history items plus reasoning-oriented question forms.\n\n")
        handle.write(
            format_markdown_table(
                ["difficulty", "count"],
                [[label, str(difficulty_counts.get(label, 0))] for label in ("easy", "medium", "hard")],
            )
        )
        handle.write("\n\n## Quality Flags\n\n")
        handle.write(
            "Quality flags preserve known audit findings without mutating the benchmark content. "
            "Allowed values are `domain_misclassification`, `question_quality`, `gold_answer_quality`, and `null`.\n\n"
        )
        handle.write(
            format_markdown_table(
                ["quality_flag", "count"],
                [
                    ["domain_misclassification", str(quality_counts.get("domain_misclassification", 0))],
                    ["question_quality", str(quality_counts.get("question_quality", 0))],
                    ["gold_answer_quality", str(quality_counts.get("gold_answer_quality", 0))],
                    ["clean", str(quality_counts.get(None, 0))],
                ],
            )
        )
        handle.write("\n\n## Source Title Resolution\n\n")
        handle.write(
            f"Resolved titles: {total_resolved} / 400. Null values indicate that `source_doc_ids[0]` could not be "
            "matched to a titled row in the supplied corpus file.\n\n"
        )
        handle.write(
            format_markdown_table(
                ["language", "resolved", "total"],
                [
                    [
                        language,
                        str(stats["resolution_counts"][language]["resolved"]),
                        str(stats["resolution_counts"][language]["total"]),
                    ]
                    for language in LANGUAGES
                ],
            )
        )
        handle.write("\n\n## Changelog from v4\n\n")
        handle.write("- Added `source_title` resolved from the corpus.\n")
        handle.write("- Added deterministic `difficulty` labels.\n")
        handle.write("- Added audit-derived `quality_flag` labels.\n")
        handle.write("- Preserved all original v4 fields and values exactly.\n\n")
        handle.write("## Fields Excluded from v5\n\n")
        handle.write("- `evidence_text`: requires corpus-backed extraction and human verification; deferred to v6.\n")
        handle.write("- `source_url`: requires verified URL resolution for each source; deferred to v6.\n")
        handle.write(
            "- `pair_id`: the English and Uzbek halves are not parallel and do not support a meaningful 1:1 pairing in v5.\n\n"
        )
        handle.write("## Known Limitations\n\n")
        handle.write("- The benchmark remains manually curated and moderate in size.\n")
        handle.write("- Quality-flagged items are still present; the flag is documentation, not removal.\n")
        handle.write("- The difficulty heuristic is coarse and should not be treated as a human judgment label.\n")
        handle.write("- Source title coverage depends on the supplied corpus and may be incomplete.\n")
        handle.write("- Retrieval and answer-quality evaluation remain separable concerns when stub generation is used.\n\n")
        handle.write("## Publication Boundary\n\n")
        handle.write(
            "This document describes an internal schema only. The full QA rows and answer-bearing sample are "
            "excluded from the public branch pending source and license clearance. Use `hf_dataset/README.md` "
            "and the retrieval-only JSONL files for the public release.\n"
        )


def print_resolution_summary(stats: dict[str, dict[str, int]]) -> None:
    total_resolved = sum(stats[language]["resolved"] for language in LANGUAGES)
    total_items = sum(stats[language]["total"] for language in LANGUAGES)
    print("Source title resolution:")
    print(f"  English resolved: {stats['en']['resolved']} / {stats['en']['total']}")
    print(f"  Uzbek resolved: {stats['uz']['resolved']} / {stats['uz']['total']}")
    print(f"  Total resolved: {total_resolved} / {total_items}")


def print_difficulty_summary(counts: dict[str, int]) -> None:
    print("Difficulty distribution:")
    print(f"  easy:   {counts.get('easy', 0)}")
    print(f"  medium: {counts.get('medium', 0)}")
    print(f"  hard:   {counts.get('hard', 0)}")


def print_quality_summary(counts: dict[str, int]) -> None:
    print("Quality flags:")
    print(f"  domain_misclassification: {counts.get('domain_misclassification', 0)} items")
    print(f"  question_quality: {counts.get('question_quality', 0)} items")
    print(f"  gold_answer_quality: {counts.get('gold_answer_quality', 0)} items")
    print(f"  clean (null): {counts.get('clean', 0)} items")


def print_final_summary(stats: dict[str, Any], output_path: Path) -> None:
    total_resolved = sum(stats["resolution_counts"][language]["resolved"] for language in LANGUAGES)
    print("\n=== manual_eval_v5 build complete ===\n")
    print("Dataset size: 400")
    print(
        f"Language: en={stats['language_counts'].get('en', 0)} uz={stats['language_counts'].get('uz', 0)}"
    )
    print("Domains per language: governance=50 history=50 institutions=50 culture=50\n")
    print("Difficulty:")
    print(f"  easy:   {stats['difficulty_counts'].get(('en', 'easy'), 0) + stats['difficulty_counts'].get(('uz', 'easy'), 0)}")
    print(
        f"  medium: {stats['difficulty_counts'].get(('en', 'medium'), 0) + stats['difficulty_counts'].get(('uz', 'medium'), 0)}"
    )
    print(f"  hard:   {stats['difficulty_counts'].get(('en', 'hard'), 0) + stats['difficulty_counts'].get(('uz', 'hard'), 0)}\n")
    print(
        "Source title resolved: "
        f"{total_resolved} / 400 (en: {stats['resolution_counts']['en']['resolved']}/200, "
        f"uz: {stats['resolution_counts']['uz']['resolved']}/200)\n"
    )
    print("Quality flags:")
    print(f"  domain_misclassification: {stats['quality_counts'].get('domain_misclassification', 0)}")
    print(f"  question_quality: {stats['quality_counts'].get('question_quality', 0)}")
    print(f"  clean: {stats['quality_counts'].get('clean', 0)}\n")
    print("Files written:")
    print(f"  {output_path}")
    print("  data/eval/sample/manual_eval_v5_sample.jsonl")
    print("  results/reports/manual_eval_v5_validation.md")
    print("  docs/dataset_card_v5.md")


def main() -> int:
    args = build_parser().parse_args()

    input_path = Path(args.input)
    corpus_path = Path(args.corpus)
    output_path = Path(args.output)
    sample_path = Path("data/eval/sample/manual_eval_v5_sample.jsonl")
    validation_path = Path("results/reports/manual_eval_v5_validation.md")
    dataset_card_path = Path("docs/dataset_card_v5.md")

    input_rows = load_required_rows(input_path, "manual_eval_v4 dataset")
    corpus_rows = load_required_rows(corpus_path, "corpus dataset")

    validate_input_rows(input_rows)
    title_lookup = build_title_lookup(corpus_rows)
    enriched_rows, enrichment_stats = enrich_items(input_rows, title_lookup)

    print_resolution_summary(enrichment_stats["resolution_counts"])
    print_difficulty_summary(enrichment_stats["difficulty_counts"])
    print_quality_summary(enrichment_stats["quality_counts"])

    stats = validate_output_rows(input_rows, enriched_rows)
    sample_rows = build_sample_dataset(enriched_rows)

    ensure_dir(output_path.parent)
    ensure_dir(sample_path.parent)
    ensure_dir(validation_path.parent)
    ensure_dir(dataset_card_path.parent)

    write_jsonl(output_path, enriched_rows)
    write_jsonl(sample_path, sample_rows)
    write_validation_report(validation_path, stats)
    write_dataset_card(dataset_card_path, enriched_rows, stats)

    print_final_summary(stats, output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
