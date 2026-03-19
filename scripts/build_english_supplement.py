#!/usr/bin/env python3
import argparse
import re
from pathlib import Path
from typing import Dict, List

import sys
sys.path.insert(0, '/home/u6ef/rajantripathi.u6ef/soas_rag_eval')

from src.utils import ensure_dir, read_jsonl, write_jsonl


# English question patterns to clean
EN_PATTERNS = [
    re.compile(r"\s+in historical context\?$", re.IGNORECASE),
    re.compile(r"\s+in institutional context\?$", re.IGNORECASE),
    re.compile(r"What place, state, or political entity is (.+)\?", re.IGNORECASE),
    re.compile(r"What institution, organization, or formal body is (.+)\?", re.IGNORECASE),
    re.compile(r"What is (.+)\?", re.IGNORECASE),
]


def build_parser():
    """Build argument parser."""
    parser = argparse.ArgumentParser(description="Build English supplementary corpus from missing eval source docs.")
    parser.add_argument("--eval-file", default="data/eval/manual_eval_v5.jsonl")
    parser.add_argument("--base-corpus-file", default="data/processed/corpus_manual_v1_uzsupp_v2.jsonl")
    parser.add_argument("--output", default="data/processed/corpus_english_supplement.jsonl")
    parser.add_argument("--language", default="en")
    parser.add_argument("--domains", nargs="+", default=["governance", "history", "institutions", "culture"])
    return parser


def clean_entity(question: str) -> str:
    """Extract the entity name from the question."""
    entity = question.strip()

    # Remove question patterns to extract entity
    for pattern in EN_PATTERNS:
        match = pattern.search(entity)
        if match:
            if match.groups():
                entity = match.group(1)
            else:
                entity = pattern.sub("", entity)
            break

    return entity.strip(" ?")


def compose_text(row: dict) -> str:
    """Compose synthetic document text from question and answer."""
    entity = clean_entity(row["question"])
    gold = row["gold_answer"].strip().rstrip(".")

    # Different composition patterns based on domain
    if row["domain"] == "history":
        first = "{} is a historical topic. {}".format(entity, gold)
        second = "This entry provides historical context about this subject, including its significance and historical development."
    elif row["domain"] == "institutions":
        first = "{} is an institution or organization. {}".format(entity, gold)
        second = "This entry describes the organization's purpose, structure, and role in its field or sector."
    elif row["domain"] == "governance":
        first = "{} relates to governance and political systems. {}".format(entity, gold)
        second = "This entry explains the political concept, system, or entity and its governance implications."
    else:  # culture
        first = "{} is a cultural topic. {}".format(entity, gold)
        second = "This entry explores the cultural significance and context of this subject."

    return "{} {} This document serves as a reference for queries about this topic.".format(first, second)


def main():
    """Main function."""
    args = build_parser().parse_args()
    eval_rows = read_jsonl(args.eval_file)
    base_rows = read_jsonl(args.base_corpus_file)
    base_ids = {row["doc_id"] for row in base_rows}
    wanted_domains = set(args.domains)

    supplement_rows = []
    missing_count = 0
    unresolvable = []

    for row in eval_rows:
        if row["language"] != args.language or row["domain"] not in wanted_domains:
            continue
        if not row.get("source_doc_ids"):
            missing_count += 1
            unresolvable.append(row["id"])
            continue

        doc_id = row["source_doc_ids"][0]
        if doc_id in base_ids:
            continue

        # Create synthetic supplement entry
        title = clean_entity(row["question"])
        if not title or title.lower() in ["what", "a", "an", "the"]:
            missing_count += 1
            unresolvable.append(row["id"])
            continue

        supplement_rows.append({
            "doc_id": doc_id,
            "chunk_id": "{}::0".format(doc_id),
            "source": "manual_curated_supplement",
            "language": row["language"],
            "title": title,
            "text": compose_text(row),
            "metadata": {
                "target_domain": row["domain"],
                "source_type": "manual_curated_jsonl",
                "from_eval_id": row["id"],
                "generated_from": Path(args.eval_file).name,
                "supplement_version": "en_v1",
                "synthetic": True,
            },
        })

    # Write supplement corpus
    ensure_dir(Path(args.output).parent)
    write_jsonl(args.output, supplement_rows)

    # Print statistics
    print("English supplement corpus created: {}".format(args.output))
    print("Total supplement documents: {}".format(len(supplement_rows)))
    print("Unresolvable items (no source_doc_ids): {}".format(missing_count))

    if unresolvable:
        print("Unresolvable item IDs: {}".format(", ".join(unresolvable[:10])))
        if len(unresolvable) > 10:
            print("  ... and {} more".format(len(unresolvable) - 10))

    # Per-domain breakdown
    print("\nPer-domain breakdown:")
    domain_counts = {}
    for row in supplement_rows:
        domain = row["metadata"]["target_domain"]
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

    for domain in ["governance", "history", "institutions", "culture"]:
        count = domain_counts.get(domain, 0)
        print("  {}: {} documents".format(domain.capitalize(), count))

    return 0


if __name__ == "__main__":
    sys.exit(main())
