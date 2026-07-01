from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


REQUIRED_DATASET_FIELDS = {"id", "source_doc_ids", "language", "domain", "question"}
PREDICTION_FIELD = "retrieved_doc_ids"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSONL row") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: expected a JSON object")
            rows.append(row)
    return rows


def load_hf_dataset(dataset_name: str, split: str) -> list[dict[str, Any]]:
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise RuntimeError(
            "Loading from Hugging Face requires the `datasets` package. "
            "Install project dependencies or use --data with a local JSONL file."
        ) from exc

    dataset = load_dataset(dataset_name, split=split)
    return [dict(row) for row in dataset]


def require_string_list(value: Any, field_name: str, row_id: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{row_id}: `{field_name}` must be a list")
    return [str(item) for item in value]


def validate_dataset_rows(rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("No dataset rows loaded")

    seen_ids: set[str] = set()
    for index, row in enumerate(rows, start=1):
        row_id = str(row.get("id", f"row_{index}"))
        missing = sorted(REQUIRED_DATASET_FIELDS.difference(row))
        if missing:
            raise ValueError(f"{row_id}: missing dataset fields {missing}")
        if row_id in seen_ids:
            raise ValueError(f"{row_id}: duplicate dataset id")
        seen_ids.add(row_id)
        require_string_list(row["source_doc_ids"], "source_doc_ids", row_id)


def load_predictions(path: Path) -> dict[str, list[str]]:
    predictions: dict[str, list[str]] = {}
    for row in load_jsonl(path):
        row_id = str(row.get("id", ""))
        if not row_id:
            raise ValueError(f"{path}: prediction row is missing `id`")
        if row_id in predictions:
            raise ValueError(f"{path}: duplicate prediction id `{row_id}`")
        if PREDICTION_FIELD not in row:
            raise ValueError(
                f"{path}: prediction row `{row_id}` is missing `{PREDICTION_FIELD}`"
            )
        predictions[row_id] = require_string_list(
            row[PREDICTION_FIELD],
            PREDICTION_FIELD,
            row_id,
        )
    return predictions


def build_oracle_predictions(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    return {
        str(row["id"]): require_string_list(
            row["source_doc_ids"],
            "source_doc_ids",
            str(row["id"]),
        )
        for row in rows
    }


def score_recall(
    rows: list[dict[str, Any]],
    predictions: dict[str, list[str]],
    k: int,
) -> dict[str, Any]:
    if k <= 0:
        raise ValueError("--k must be greater than zero")

    total = len(rows)
    hits = 0
    missing_predictions = 0
    by_language_total: Counter[str] = Counter()
    by_language_hits: Counter[str] = Counter()
    by_domain_total: Counter[str] = Counter()
    by_domain_hits: Counter[str] = Counter()

    for row in rows:
        row_id = str(row["id"])
        language = str(row["language"])
        domain = str(row["domain"])
        source_ids = set(
            require_string_list(row["source_doc_ids"], "source_doc_ids", row_id)
        )
        retrieved = predictions.get(row_id)
        if retrieved is None:
            missing_predictions += 1
            retrieved = []
        retrieved_at_k = retrieved[:k]
        hit = bool(source_ids.intersection(retrieved_at_k))

        hits += int(hit)
        by_language_total[language] += 1
        by_language_hits[language] += int(hit)
        by_domain_total[domain] += 1
        by_domain_hits[domain] += int(hit)

    return {
        "k": k,
        "rows": total,
        "hits": hits,
        "recall": hits / total if total else 0.0,
        "missing_predictions": missing_predictions,
        "by_language": summarize_slices(by_language_total, by_language_hits),
        "by_domain": summarize_slices(by_domain_total, by_domain_hits),
    }


def summarize_slices(
    totals: Counter[str],
    hits: Counter[str],
) -> dict[str, dict[str, float | int]]:
    summary: dict[str, dict[str, float | int]] = {}
    for key in sorted(totals):
        total = totals[key]
        hit_count = hits[key]
        summary[key] = {
            "rows": total,
            "hits": hit_count,
            "recall": hit_count / total if total else 0.0,
        }
    return summary


def print_text_report(metrics: dict[str, Any], oracle_check: bool) -> None:
    label = "Oracle evaluator check" if oracle_check else "Retrieval evaluation"
    print(label)
    print(f"Rows scored: {metrics['rows']}")
    print(
        f"Recall@{metrics['k']}: {metrics['recall']:.4f} "
        f"({metrics['hits']}/{metrics['rows']})"
    )
    print(f"Missing predictions: {metrics['missing_predictions']}")

    print("By language:")
    for language, values in metrics["by_language"].items():
        print(
            f"  {language}: {values['recall']:.4f} "
            f"({values['hits']}/{values['rows']})"
        )

    print("By domain:")
    for domain, values in metrics["by_domain"].items():
        print(
            f"  {domain}: {values['recall']:.4f} "
            f"({values['hits']}/{values['rows']})"
        )

    if oracle_check:
        print(
            "Note: --oracle-check uses source_doc_ids as retrieved_doc_ids. "
            "It validates evaluator wiring; it is not a model result."
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Compute retrieval recall@k for the SOAS English-Uzbek retrieval-only "
            "benchmark. Prediction JSONL rows must contain `id` and `retrieved_doc_ids`."
        )
    )
    parser.add_argument(
        "--data",
        default="hf_dataset/manual_eval_v5_retrieval_only.jsonl",
        help="Local retrieval-only JSONL file. Ignored when --hf-dataset is set.",
    )
    parser.add_argument(
        "--hf-dataset",
        default=None,
        help=(
            "Optional Hugging Face dataset id, for example "
            "Rajan2026/soas-english-uzbek-rag-evaluation."
        ),
    )
    parser.add_argument("--split", default="train", help="Hugging Face split to load.")
    parser.add_argument(
        "--predictions",
        default=None,
        help=(
            "Prediction JSONL with rows shaped as "
            "{'id': str, 'retrieved_doc_ids': list[str]}."
        ),
    )
    parser.add_argument(
        "--oracle-check",
        action="store_true",
        help="Use source_doc_ids as retrieved_doc_ids to validate evaluator wiring.",
    )
    parser.add_argument("--k", type=int, default=5, help="Recall cutoff.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    if bool(args.predictions) == args.oracle_check:
        parser.error("Provide exactly one of --predictions or --oracle-check")

    rows = (
        load_hf_dataset(args.hf_dataset, args.split)
        if args.hf_dataset
        else load_jsonl(Path(args.data))
    )
    validate_dataset_rows(rows)

    predictions = (
        build_oracle_predictions(rows)
        if args.oracle_check
        else load_predictions(Path(args.predictions))
    )
    metrics = score_recall(rows, predictions, args.k)

    if args.json:
        print(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print_text_report(metrics, args.oracle_check)


if __name__ == "__main__":
    main()
