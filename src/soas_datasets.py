from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any

from datasets import Dataset, DatasetDict, IterableDataset, IterableDatasetDict
from datasets import load_dataset, load_from_disk
from huggingface_hub import snapshot_download

from src.utils import ensure_dir


DATASET_SPECS = [
    {
        "name": "miracl/miracl",
        "config_name": "en",
        "local_dir": "miracl_en",
        "language": "en",
        "kind": "corpus",
        "fetch_strategy": "miracl_raw",
    },
    {
        "name": "tydiqa",
        "config_name": "primary_task",
        "local_dir": "tydiqa_primary_task",
        "language": "multi",
        "kind": "qa",
    },
    {
        "name": "yakhyo/uz-wiki",
        "config_name": None,
        "local_dir": "uz_wiki",
        "language": "uz",
        "kind": "corpus",
    },
]


def fetch_dataset(spec: dict[str, Any], raw_root: Path, force: bool = False) -> dict[str, Any]:
    target = raw_root / spec["local_dir"]
    if target.exists() and not force:
        return {
            "dataset": spec["name"],
            "config_name": spec["config_name"],
            "status": "skipped_existing",
            "output_dir": str(target),
        }

    ensure_dir(raw_root)
    if spec.get("fetch_strategy") == "miracl_raw":
        ensure_dir(target)
        snapshot_download(
            repo_id="miracl/miracl-corpus",
            repo_type="dataset",
            local_dir=str(target),
            allow_patterns=["miracl-corpus-v1.0-en/docs-0.jsonl.gz"],
        )
        snapshot_download(
            repo_id="miracl/miracl",
            repo_type="dataset",
            local_dir=str(target),
            allow_patterns=[
                "miracl-v1.0-en/topics/topics.miracl-v1.0-en-dev.tsv",
                "miracl-v1.0-en/topics/topics.miracl-v1.0-en-train.tsv",
                "miracl-v1.0-en/qrels/qrels.miracl-v1.0-en-dev.tsv",
                "miracl-v1.0-en/qrels/qrels.miracl-v1.0-en-train.tsv",
            ],
        )
        return {
            "dataset": spec["name"],
            "config_name": spec["config_name"],
            "status": "downloaded_raw",
            "output_dir": str(target),
        }
    dataset = load_dataset(spec["name"], spec["config_name"])
    dataset.save_to_disk(str(target))
    return {
        "dataset": spec["name"],
        "config_name": spec["config_name"],
        "status": "downloaded",
        "output_dir": str(target),
    }


def load_saved_dataset(path: Path) -> Dataset | DatasetDict | IterableDataset | IterableDatasetDict:
    return load_from_disk(str(path))


def iter_examples(dataset_obj: Any) -> Any:
    if isinstance(dataset_obj, DatasetDict):
        for split_name, split_ds in dataset_obj.items():
            for item in split_ds:
                yield split_name, item
        return
    if isinstance(dataset_obj, IterableDatasetDict):
        for split_name, split_ds in dataset_obj.items():
            for item in split_ds:
                yield split_name, item
        return
    for item in dataset_obj:
        yield "train", item


def detect_text(example: dict[str, Any]) -> str:
    for key in (
        "text",
        "contents",
        "context",
        "document",
        "body",
        "article",
        "passage_text",
        "document_plaintext",
    ):
        value = example.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def detect_title(example: dict[str, Any]) -> str:
    for key in ("title", "article_title", "document_title", "subject"):
        value = example.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def detect_id(example: dict[str, Any], fallback: str) -> str:
    for key in (
        "doc_id",
        "docid",
        "id",
        "idx",
        "passage_id",
        "example_id",
        "title",
        "document_title",
    ):
        value = example.get(key)
        if isinstance(value, (str, int)):
            return str(value)
    return fallback


def detect_question(example: dict[str, Any]) -> str:
    for key in ("question", "query", "input", "prompt", "question_text"):
        value = example.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def detect_answer(example: dict[str, Any]) -> str:
    answers = example.get("answers")
    if isinstance(answers, dict):
        text_values = answers.get("text")
        if isinstance(text_values, list) and text_values:
            return str(text_values[0]).strip()
    if isinstance(answers, list) and answers:
        first = answers[0]
        if isinstance(first, dict):
            text = first.get("text")
            if isinstance(text, str):
                return text.strip()
        if isinstance(first, str):
            return first.strip()
    for key in ("answer", "gold_answer", "target"):
        value = example.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    annotations = example.get("annotations")
    document_text = example.get("document_plaintext")
    if isinstance(annotations, dict) and isinstance(document_text, str):
        starts = annotations.get("minimal_answers_start_byte") or []
        ends = annotations.get("minimal_answers_end_byte") or []
        if starts and ends and starts[0] >= 0 and ends[0] > starts[0]:
            try:
                return document_text[starts[0] : ends[0]].strip()
            except Exception:
                return ""
    return ""


def detect_language(example: dict[str, Any], default: str) -> str:
    for key in ("language", "lang"):
        value = example.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return default


def write_manifest(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(records, handle, ensure_ascii=False, indent=2)


def iter_miracl_raw_documents(dataset_path: Path) -> Any:
    for gzip_path in sorted(dataset_path.glob("miracl-corpus-v1.0-en/docs-*.jsonl.gz")):
        with gzip.open(gzip_path, "rt", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                yield json.loads(line)
