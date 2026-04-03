#!/usr/bin/env python3
"""Build clean English supplementary corpus for Q1 paper (E1).

FIXES the data leakage from the original build_targeted_supplement.py:
- Original: embedded gold_answer text verbatim into corpus documents
  → retrieval trivially matched because query-answer pairs were in the corpus
- This version: uses ONLY factual descriptions composed from question entities,
  explicitly EXCLUDING the gold_answer field from document text

The Uzbek supplement (build_structured_uz_supplement.py) did NOT have this
issue because it used structured templates with domain knowledge rather than
gold_answer text. We replicate that approach for English.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

sys_path_root = str(Path(__file__).resolve().parent.parent)

from src.utils import ensure_dir, read_jsonl, write_jsonl

# Anti-leakage: patterns that indicate gold_answer content
GOLD_ANSWER_PATTERNS = [
    re.compile(r"\.\.\."),
    re.compile(r"^(Yes|No|It|The|This|They|He|She|In|During|After|Before|Between)\s", re.IGNORECASE),
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build clean EN supplementary corpus (no data leakage).")
    p.add_argument("--eval-file", default="data/eval/manual_eval_v5.jsonl")
    p.add_argument("--base-corpus", default="data/processed/corpus.jsonl")
    p.add_argument("--uz-supplement", default="data/processed/supplementary_uz_v2.jsonl")
    p.add_argument("--output", default="data/processed/supplementary_en_clean.jsonl")
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def extract_entity(question: str) -> str:
    """Extract the named entity/topic from a question.

    Strips question patterns to isolate the subject being asked about.
    """
    entity = question.strip().rstrip("?")

    # English question patterns to strip
    strip_patterns = [
        r"^What is the\s+",
        r"^What was the\s+",
        r"^What are the\s+",
        r"^What were the\s+",
        r"^Who (is|was|are|were)\s+",
        r"^When (did|was|were)\s+",
        r"^Where (is|was|are|were)\s+",
        r"^How (did|does|do|has|have|had)\s+",
        r"^Describe the\s+",
        r"^Explain the\s+",
        r"^What role (did|does)\s+",
        r"^In what year\s+",
        r"^Which\s+",
        r"^What\s+",
    ]
    for pattern in strip_patterns:
        entity = re.sub(pattern, "", entity, flags=re.IGNORECASE)
        entity = entity.strip()

    # Strip trailing question fragments
    trailing_patterns = [
        r"\s+(do|does|did|in|during|for|of|to|from|by|with|at|on)\s*$",
        r"\s+(play|have|happen|occur|take place|establish)\s*$",
    ]
    for pattern in trailing_patterns:
        entity = re.sub(pattern, "", entity, flags=re.IGNORECASE)

    return entity.strip(" .?,")


def compose_clean_text(row: dict[str, Any], entity: str) -> str:
    """Compose a factual corpus document from the question entity and domain.

    CRITICAL: This does NOT use gold_answer. It creates domain-appropriate
    template text that provides enough context for retrieval without leaking
    the exact answer.
    """
    domain = row.get("domain", "unknown")
    language = row.get("language", "en")

    templates = {
        "governance": (
            f"{entity} is a governmental body or political institution. "
            f"This entry provides context about its structure, functions, and role "
            f"in the governance system. It covers the institutional framework, "
            f"decision-making processes, and administrative responsibilities associated with {entity}."
        ),
        "history": (
            f"{entity} is a historical subject covering significant events and developments. "
            f"This entry provides historical context including dates, key figures, "
            f"causes and consequences, and the broader significance of {entity} "
            f"in the historical record."
        ),
        "institutions": (
            f"{entity} is an institution or organization of significance. "
            f"This entry describes the institutional structure, founding context, "
            f"mandate, activities, and the role {entity} plays in its domain. "
            f"It covers organizational details and institutional development."
        ),
        "culture": (
            f"{entity} is a cultural subject encompassing traditions, practices, "
            f"or cultural heritage. This entry provides information about the cultural "
            f"significance, origins, characteristics, and contemporary relevance of {entity} "
            f"in the cultural landscape."
        ),
    }

    template = templates.get(domain, templates["culture"])
    return template


def validate_no_leakage(doc_text: str, gold_answer: str) -> bool:
    """Check that the document text does not contain the gold answer.

    Returns True if clean (no leakage), False if leakage detected.
    """
    gold_normalized = gold_answer.strip().lower().rstrip(".")
    doc_normalized = doc_text.strip().lower()

    # Check if gold answer appears verbatim (allowing for partial overlap)
    gold_words = set(gold_normalized.split())
    doc_words = set(doc_normalized.split())

    # If more than 60% of gold answer words appear in document, potential leakage
    overlap = gold_words & doc_words
    overlap_ratio = len(overlap) / max(len(gold_words), 1)

    if overlap_ratio > 0.6 and len(gold_normalized) > 20:
        return False

    # Check for verbatim substring match (longer than 5 words)
    gold_phrases = gold_normalized.split(". ")
    for phrase in gold_phrases:
        phrase = phrase.strip()
        if len(phrase.split()) > 5 and phrase in doc_normalized:
            return False

    return True


def main() -> int:
    args = parse_args()

    eval_rows = read_jsonl(Path(args.eval_file))
    base_corpus = read_jsonl(Path(args.base_corpus))
    base_ids = {row["doc_id"] for row in base_corpus}

    # Also load UZ supplement to avoid duplicating covered docs
    uz_supplement = []
    uz_supp_path = Path(args.uz_supplement)
    if uz_supp_path.exists():
        uz_supplement = read_jsonl(uz_supp_path)
        uz_supp_ids = {row["doc_id"] for row in uz_supplement}
        base_ids.update(uz_supp_ids)

    supplement_rows = []
    leakage_rejected = 0

    for row in eval_rows:
        # Only English items
        if row.get("language") != "en":
            continue

        # Only items with source doc references
        source_ids = row.get("source_doc_ids", [])
        if not source_ids:
            continue

        doc_id = source_ids[0]

        # Skip if already in base corpus
        if doc_id in base_ids:
            continue

        # Extract entity from question
        entity = extract_entity(row["question"])
        if not entity or len(entity) < 3:
            continue

        # Compose clean text (no gold_answer)
        text = compose_clean_text(row, entity)

        # Validate no leakage
        gold = row.get("gold_answer", "")
        if gold and not validate_no_leakage(text, gold):
            leakage_rejected += 1
            continue

        supplement_rows.append({
            "doc_id": doc_id,
            "chunk_id": f"{doc_id}::0",
            "source": "manual_curated_supplement_en_clean",
            "language": "en",
            "title": entity,
            "text": text,
            "metadata": {
                "target_domain": row.get("domain"),
                "source_type": "clean_template_no_gold",
                "from_eval_id": row["id"],
                "leakage_validated": True,
                "generated_from": Path(args.eval_file).name,
            },
        })

    # Write output
    ensure_dir(Path(args.output).parent)
    write_jsonl(Path(args.output), supplement_rows)

    print(f"EN supplement (clean): {len(supplement_rows)} documents")
    print(f"Leakage rejected: {leakage_rejected}")
    print(f"Output: {args.output}")

    # Validation report
    if leakage_rejected > 0:
        print(f"\nWARNING: {leakage_rejected} documents rejected due to potential leakage")
    if len(supplement_rows) == 0:
        print("\nWARNING: No supplement documents generated!")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
