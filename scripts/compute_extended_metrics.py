#!/usr/bin/env python3
"""Extended retrieval metrics: nDCG@k, MRR@k, MAP@k, Precision@k.

Computes standard IR metrics beyond Recall@k for all experiment conditions.
Operates on existing predictions.jsonl files -- no re-running of retrieval needed.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compute extended retrieval metrics.")
    p.add_argument("--results-dir", default="results", help="Base results directory")
    p.add_argument("--eval-file", default="data/eval/manual_eval_v5.jsonl")
    p.add_argument("--output", default="results/q1_experiments/extended_metrics.json")
    p.add_argument("--top-k", type=int, nargs="+", default=[1, 3, 5, 10, 20, 50, 100])
    return p.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# ---------------------------------------------------------------------------
# Metric implementations
# ---------------------------------------------------------------------------

def recall_at_k(relevant: set[str], retrieved: list[str], k: int) -> float:
    if not relevant:
        return 0.0
    return len(relevant & set(retrieved[:k])) / len(relevant)


def precision_at_k(relevant: set[str], retrieved: list[str], k: int) -> float:
    if k == 0:
        return 0.0
    return len(relevant & set(retrieved[:k])) / k


def ndcg_at_k(relevant: set[str], retrieved: list[str], k: int) -> float:
    """nDCG@k with binary relevance."""
    dcg = 0.0
    for i, doc_id in enumerate(retrieved[:k]):
        if doc_id in relevant:
            dcg += 1.0 / np.log2(i + 2)  # i+2 because rank is 1-indexed
    # Ideal DCG: all relevant docs at top ranks
    ideal_count = min(len(relevant), k)
    idcg = sum(1.0 / np.log2(i + 2) for i in range(ideal_count))
    if idcg == 0:
        return 0.0
    return dcg / idcg


def mrr_at_k(relevant: set[str], retrieved: list[str], k: int) -> float:
    """Mean Reciprocal Rank@k."""
    for i, doc_id in enumerate(retrieved[:k]):
        if doc_id in relevant:
            return 1.0 / (i + 1)
    return 0.0


def average_precision(relevant: set[str], retrieved: list[str]) -> float:
    """Average Precision (for MAP)."""
    if not relevant:
        return 0.0
    hits = 0
    sum_precision = 0.0
    for i, doc_id in enumerate(retrieved):
        if doc_id in relevant:
            hits += 1
            sum_precision += hits / (i + 1)
    return sum_precision / len(relevant)


# ---------------------------------------------------------------------------
# Main computation
# ---------------------------------------------------------------------------

def compute_metrics_for_condition(
    predictions: list[dict[str, Any]],
    eval_data: dict[str, dict[str, Any]],
    k_values: list[int],
) -> dict[str, Any]:
    """Compute all metrics for one experiment condition."""
    # Group predictions by ID
    pred_by_id = {p["id"]: p for p in predictions}

    # Collect per-item metric values
    metric_values: dict[str, list[float]] = defaultdict(list)
    stratified: dict[str, dict[str, list[float]]] = {
        "en": defaultdict(list),
        "uz": defaultdict(list),
    }

    # Also stratify by cultural specificity
    cultural_strata: dict[str, dict[str, list[float]]] = {
        "unknown": defaultdict(list),
        "low": defaultdict(list),
        "medium": defaultdict(list),
        "high": defaultdict(list),
    }

    # And by domain
    domain_strata: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    for item_id, eval_item in eval_data.items():
        pred = pred_by_id.get(item_id)
        if pred is None:
            continue

        relevant_ids = set(eval_item.get("source_doc_ids", []))
        # Get retrieved doc IDs from contexts
        # Handle both field names: 'contexts' (old format) and 'retrieved_contexts' (current format)
        contexts = pred.get("retrieved_contexts") or pred.get("contexts", [])
        retrieved_ids = [str(c.get("doc_id", "")) for c in contexts]
        language = eval_item.get("language", "unknown")
        specificity = eval_item.get("cultural_specificity", "unknown")
        domain = eval_item.get("domain", "unknown")

        for k in k_values:
            r = recall_at_k(relevant_ids, retrieved_ids, k)
            p = precision_at_k(relevant_ids, retrieved_ids, k)
            ndcg = ndcg_at_k(relevant_ids, retrieved_ids, k)
            mrr = mrr_at_k(relevant_ids, retrieved_ids, k)

            metric_values[f"recall@{k}"].append(r)
            metric_values[f"precision@{k}"].append(p)
            metric_values[f"ndcg@{k}"].append(ndcg)
            metric_values[f"mrr@{k}"].append(mrr)

            stratified[language][f"recall@{k}"].append(r)
            stratified[language][f"ndcg@{k}"].append(ndcg)
            stratified[language][f"mrr@{k}"].append(mrr)

            cultural_strata[specificity][f"recall@{k}"].append(r)
            cultural_strata[specificity][f"ndcg@{k}"].append(ndcg)

            domain_strata[domain][f"recall@{k}"].append(r)
            domain_strata[domain][f"ndcg@{k}"].append(ndcg)

        # MAP@100 (or whatever the max k is)
        ap = average_precision(relevant_ids, retrieved_ids)
        metric_values["map"].append(ap)
        stratified[language]["map"].append(ap)

    # Aggregate
    results: dict[str, Any] = {"overall": {}, "by_language": {}, "by_specificity": {}, "by_domain": {}}

    for metric_name, values in metric_values.items():
        arr = np.array(values)
        results["overall"][metric_name] = {
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr)),
            "count": len(values),
        }

    for lang, metrics in stratified.items():
        results["by_language"][lang] = {}
        for metric_name, values in metrics.items():
            arr = np.array(values)
            results["by_language"][lang][metric_name] = {
                "mean": float(np.mean(arr)),
                "count": len(values),
            }

    for spec, metrics in cultural_strata.items():
        results["by_specificity"][spec] = {}
        for metric_name, values in metrics.items():
            if values:
                arr = np.array(values)
                results["by_specificity"][spec][metric_name] = {
                    "mean": float(np.mean(arr)),
                    "count": len(values),
                }

    for domain, metrics in domain_strata.items():
        results["by_domain"][domain] = {}
        for metric_name, values in metrics.items():
            if values:
                arr = np.array(values)
                results["by_domain"][domain][metric_name] = {
                    "mean": float(np.mean(arr)),
                    "count": len(values),
                }

    return results


def find_experiment_dirs(results_dir: Path) -> dict[str, Path]:
    """Find all experiment directories with predictions.jsonl."""
    experiments = {}
    for d in sorted(results_dir.iterdir()):
        if not d.is_dir():
            continue
        pred_file = d / "predictions.jsonl"
        if pred_file.exists():
            # Use directory name as condition name
            experiments[d.name] = d
    return experiments


def main() -> int:
    args = parse_args()
    results_dir = Path(args.results_dir)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load eval data
    eval_rows = load_jsonl(Path(args.eval_file))
    eval_data = {row["id"]: row for row in eval_rows}
    print(f"Loaded {len(eval_data)} eval items from {args.eval_file}")

    # Find all experiment conditions
    experiments = find_experiment_dirs(results_dir)
    print(f"Found {len(experiments)} experiment conditions")

    all_results = {}
    for cond_name, cond_dir in experiments.items():
        print(f"  Processing: {cond_name}")
        predictions = load_jsonl(cond_dir / "predictions.jsonl")
        if not predictions:
            print(f"    Skipping (no predictions)")
            continue
        metrics = compute_metrics_for_condition(predictions, eval_data, args.top_k)
        all_results[cond_name] = metrics

    # Save results
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {output_path}")

    # Print summary table
    print("\n" + "=" * 80)
    print("SUMMARY: Key Metrics Across Conditions")
    print("=" * 80)
    print(f"{'Condition':<40} {'Recall@10':>10} {'nDCG@10':>10} {'MRR@10':>10} {'MAP':>10}")
    print("-" * 80)
    for cond_name, metrics in sorted(all_results.items()):
        overall = metrics.get("overall", {})
        r10 = overall.get("recall@10", {}).get("mean", 0.0)
        n10 = overall.get("ndcg@10", {}).get("mean", 0.0)
        m10 = overall.get("mrr@10", {}).get("mean", 0.0)
        map_val = overall.get("map", {}).get("mean", 0.0)
        print(f"{cond_name:<40} {r10:>10.3f} {n10:>10.3f} {m10:>10.3f} {map_val:>10.3f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
