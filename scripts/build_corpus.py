#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.soas_datasets import (
    DATASET_SPECS,
    detect_answer,
    detect_id,
    detect_language,
    detect_question,
    detect_text,
    detect_title,
    iter_examples,
    iter_miracl_raw_documents,
    load_saved_dataset,
)
from src.utils import ensure_dir, load_config, write_jsonl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Normalize fetched datasets into a smoke corpus and eval set.")
    parser.add_argument("--config", default="configs/exp_smoke.yaml", help="Path to YAML config.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config = load_config(args.config)
    raw_root = Path(config["paths"]["raw_data_dir"])
    processed_dir = ensure_dir(Path(config["paths"]["processed_data_dir"]))
    eval_dir = ensure_dir(Path(config["paths"]["eval_data_dir"]))
    max_docs = int(config["dataset"].get("smoke_max_docs", 120))
    max_eval = int(config["dataset"].get("smoke_max_eval", 50))
    generate_eval = bool(config["dataset"].get("generate_eval", True))
    max_docs_per_source = config["dataset"].get("max_docs_per_source")
    allowed_languages = config["dataset"].get("allowed_languages", {})
    corpus_filename = config["paths"].get("corpus_file", "corpus_smoke.jsonl")
    eval_filename = config["paths"].get("eval_file", "smoke_eval.jsonl")

    corpus_rows = []
    eval_rows = []
    source_doc_counts: dict[str, int] = {}

    for spec in DATASET_SPECS:
        dataset_path = raw_root / spec["local_dir"]
        if not dataset_path.exists():
            continue
        source_count = source_doc_counts.get(spec["local_dir"], 0)
        if spec.get("fetch_strategy") == "miracl_raw":
            for example in iter_miracl_raw_documents(dataset_path):
                if max_docs_per_source is not None and source_count >= int(max_docs_per_source):
                    break
                text = example.get("text", "").strip()
                if not text:
                    continue
                title = example.get("title", "").strip()
                doc_id = str(example.get("docid") or title or f"{spec['local_dir']}_{len(corpus_rows)}")
                corpus_rows.append(
                    {
                        "doc_id": doc_id,
                        "chunk_id": f"{doc_id}::0",
                        "source": spec["name"],
                        "language": spec["language"],
                        "title": title,
                        "text": text,
                        "metadata": {
                            "dataset_dir": spec["local_dir"],
                            "fetch_strategy": "miracl_raw",
                        },
                    }
                )
                source_count += 1
                source_doc_counts[spec["local_dir"]] = source_count
                if len(corpus_rows) >= max_docs:
                    break
            if len(corpus_rows) >= max_docs and (len(eval_rows) >= max_eval or not generate_eval):
                break
            continue
        dataset_obj = load_saved_dataset(dataset_path)
        for split_name, example in iter_examples(dataset_obj):
            default_lang = spec["language"]
            language = detect_language(example, default_lang)
            source_allowed_languages = allowed_languages.get(spec["local_dir"]) or allowed_languages.get(spec["name"])
            if source_allowed_languages and language not in source_allowed_languages:
                continue

            text = detect_text(example)
            if text and len(corpus_rows) < max_docs:
                if max_docs_per_source is not None and source_count >= int(max_docs_per_source):
                    break
                doc_id = detect_id(example, f"{spec['local_dir']}_{split_name}_{len(corpus_rows)}")
                corpus_rows.append(
                    {
                        "doc_id": doc_id,
                        "chunk_id": f"{doc_id}::0",
                        "source": spec["name"],
                        "language": language,
                        "title": detect_title(example),
                        "text": text,
                        "metadata": {
                            "split": split_name,
                            "dataset_dir": spec["local_dir"],
                        },
                    }
                )
                source_count += 1
                source_doc_counts[spec["local_dir"]] = source_count

            question = detect_question(example)
            answer = detect_answer(example)
            if generate_eval and question and answer and len(eval_rows) < max_eval:
                source_doc_id = detect_id(example, f"{spec['local_dir']}_{split_name}_{len(eval_rows)}")
                eval_rows.append(
                    {
                        "id": f"{spec['local_dir']}_{split_name}_{len(eval_rows)}",
                        "language": language,
                        "domain": spec["name"],
                        "question": question,
                        "gold_answer": answer,
                        "source_doc_ids": [source_doc_id],
                        "answerable": True,
                        "cultural_specificity": "unknown",
                    }
                )

        if len(corpus_rows) >= max_docs and (len(eval_rows) >= max_eval or not generate_eval):
            break

    if not corpus_rows:
        raise SystemExit("No corpus documents were built from fetched datasets.")

    if generate_eval and not eval_rows:
        eval_rows = [
            {
                "id": f"synthetic_{idx}",
                "language": row["language"],
                "domain": row["source"],
                "question": f"What is this passage about: {row['title'] or row['doc_id']}?",
                "gold_answer": row["text"].split(".")[0].strip(),
                "source_doc_ids": [row["doc_id"]],
                "answerable": True,
                "cultural_specificity": "unknown",
            }
            for idx, row in enumerate(corpus_rows[:max_eval])
        ]

    corpus_path = processed_dir / corpus_filename
    write_jsonl(corpus_path, corpus_rows)
    print(f"Wrote corpus: {corpus_path}")
    if generate_eval:
        eval_path = eval_dir / eval_filename
        write_jsonl(eval_path, eval_rows)
        print(f"Wrote eval set: {eval_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
