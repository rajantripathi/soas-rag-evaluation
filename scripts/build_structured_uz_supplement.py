#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from datasets import load_from_disk

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils import ensure_dir, read_jsonl, write_jsonl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a structured Uzbek supplementary corpus from raw uz_wiki rows referenced by eval items."
    )
    parser.add_argument("--eval-file", default="data/eval/manual_eval_v2.jsonl")
    parser.add_argument("--base-corpus-file", default="data/processed/corpus_manual_v1.jsonl")
    parser.add_argument("--raw-uz-wiki", default="data/raw/uz_wiki")
    parser.add_argument(
        "--domains",
        nargs="+",
        default=["history", "institutions", "culture"],
        help="Uzbek domains to include from the eval file.",
    )
    parser.add_argument("--language", default="uz")
    parser.add_argument(
        "--output",
        default="data/processed/supplementary_uz_structured_v2.jsonl",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=4000,
        help="Trim structured source text to a lead passage to keep indexing stable on cluster login nodes.",
    )
    return parser


def lead_passage(text: str, max_chars: int) -> str:
    cleaned = " ".join((text or "").split())
    if len(cleaned) <= max_chars:
        return cleaned
    clipped = cleaned[:max_chars]
    for marker in [". ", "! ", "? ", "; "]:
        idx = clipped.rfind(marker)
        if idx >= max_chars // 2:
            return clipped[: idx + 1].strip()
    return clipped.strip()


def main() -> int:
    args = build_parser().parse_args()
    eval_rows = read_jsonl(args.eval_file)
    base_rows = read_jsonl(args.base_corpus_file)
    base_ids = {row["doc_id"] for row in base_rows}
    wanted_domains = set(args.domains)

    target_ids: set[str] = set()
    target_metadata: dict[str, dict] = {}
    for row in eval_rows:
        if row["language"] != args.language or row["domain"] not in wanted_domains:
            continue
        if not row.get("source_doc_ids"):
            continue
        doc_id = str(row["source_doc_ids"][0])
        if doc_id in base_ids:
            continue
        target_ids.add(doc_id)
        target_metadata[doc_id] = {
            "target_domain": row["domain"],
            "from_eval_id": row["id"],
            "question": row["question"],
        }

    ds = load_from_disk(args.raw_uz_wiki)["train"]
    rows = []
    for item in ds:
        doc_id = str(item["id"])
        if doc_id not in target_ids:
            continue
        meta = target_metadata[doc_id]
        rows.append(
            {
                "doc_id": doc_id,
                "chunk_id": f"{doc_id}::0",
                "source": "uz_wiki_structured_supplement",
                "language": args.language,
                "title": str(item.get("title") or ""),
                "text": lead_passage(str(item.get("text") or ""), max_chars=args.max_chars),
                "metadata": {
                    "source_type": "uz_wiki_raw_saved_dataset",
                    "target_domain": meta["target_domain"],
                    "from_eval_id": meta["from_eval_id"],
                    "question": meta["question"],
                    "url": str(item.get("url") or ""),
                    "max_chars": args.max_chars,
                },
            }
        )

    rows.sort(key=lambda row: int(row["doc_id"]))
    ensure_dir(Path(args.output).parent)
    write_jsonl(args.output, rows)
    print(args.output)
    print(len(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
