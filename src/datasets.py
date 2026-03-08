from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from datasets import Dataset, DatasetDict, IterableDataset, IterableDatasetDict
from datasets import load_dataset, load_from_disk

from src.utils import ensure_dir


DATASET_SPECS = [
    {
        "name": "miracl/miracl",
        "config_name": "en",
        "local_dir": "miracl_en",
        "language": "en",
        "kind": "qa",
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
    for key in ("text", "contents", "context", "document", "body", "article", "passage_text"):
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
    for key in ("doc_id", "docid", "id", "idx", "passage_id", "example_id"):
        value = example.get(key)
        if isinstance(value, (str, int)):
            return str(value)
    return fallback


def detect_question(example: dict[str, Any]) -> str:
    for key in ("question", "query", "input", "prompt"):
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
