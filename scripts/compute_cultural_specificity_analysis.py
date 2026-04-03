#!/usr/bin/env python3
"""Cultural specificity analysis: CRG and CSS metrics.

Implements:
  - CRG (Cultural Retrieval Gap): How much supplementation helps at each specificity level
  - CSS (Cultural Sensitivity Score): How much a system degrades on culturally specific queries

Produces stratified analysis and publication-ready tables.
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
    p = argparse.ArgumentParser(description="Compute cultural specificity analysis (CRG, CSS).")
    p.add_argument("--results-dir", default="results", help="Base results directory")
    p.add_argument("--eval-file", default="data/eval/manual_eval_v5.jsonl")
    p.add_argument("--output-dir", default="results/q1_experiments")
    p.add_argument("--n-resamples", type=int, default=10000, help="Bootstrap resamples")
    return p.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# ---------------------------------------------------------------------------
# Core metrics
# ---------------------------------------------------------------------------

def recall_at_k_for_item(pred: dict, eval_item: dict, k: int = 10) -> float:
    """Binary recall@k for a single item."""
    gold_ids = set(eval_item.get("source_doc_ids", []))
    if not gold_ids:
        return 0.0
    contexts = pred.get("contexts", [])
    retrieved_ids = {str(c.get("doc_id", "")) for c in contexts[:k]}
    return 1.0 if gold_ids & retrieved_ids else 0.0


def compute_crg(
    baseline_preds: dict[str, dict],
    supplemented_preds: dict[str, dict],
    eval_data: dict[str, dict],
    specificity_levels: list[str] = None,
    k: int = 10,
) -> dict[str, dict[str, float]]:
    """Cultural Retrieval Gap: Recall(baseline, s) - Recall(supplemented, s) per specificity level.

    Higher CRG means supplementation helped more for that specificity level.
    """
    if specificity_levels is None:
        specificity_levels = ["unknown", "low", "medium", "high"]

    crg_results = {}
    for level in specificity_levels:
        # Filter items by specificity level
        items_at_level = {
            item_id: item
            for item_id, item in eval_data.items()
            if item.get("cultural_specificity") == level
        }

        if not items_at_level:
            continue

        baseline_recalls = []
        supplemented_recalls = []

        for item_id, eval_item in items_at_level.items():
            b_pred = baseline_preds.get(item_id)
            s_pred = supplemented_preds.get(item_id)
            if b_pred is None or s_pred is None:
                continue

            baseline_recalls.append(recall_at_k_for_item(b_pred, eval_item, k))
            supplemented_recalls.append(recall_at_k_for_item(s_pred, eval_item, k))

        if not baseline_recalls:
            continue

        baseline_mean = np.mean(baseline_recalls)
        supplemented_mean = np.mean(supplemented_recalls)
        gap = supplemented_mean - baseline_mean  # Positive = supplementation helped

        crg_results[level] = {
            "baseline_recall": float(baseline_mean),
            "supplemented_recall": float(supplemented_mean),
            "crg": float(gap),
            "n_items": len(baseline_recalls),
        }

    return crg_results


def compute_css(
    predictions: dict[str, dict],
    eval_data: dict[str, dict],
    k: int = 10,
) -> float:
    """Cultural Sensitivity Score: 1 - Recall(high_specificity) / Recall(low_specificity).

    CSS -> 0: System handles cultural queries as well as generic ones.
    CSS -> 1: System fails on culturally specific queries.
    """
    low_items = {
        item_id: item
        for item_id, item in eval_data.items()
        if item.get("cultural_specificity") == "low"
    }
    high_items = {
        item_id: item
        for item_id, item in eval_data.items()
        if item.get("cultural_specificity") == "high"
    }

    low_recalls = []
    for item_id, eval_item in low_items.items():
        pred = predictions.get(item_id)
        if pred:
            low_recalls.append(recall_at_k_for_item(pred, eval_item, k))

    high_recalls = []
    for item_id, eval_item in high_items.items():
        pred = predictions.get(item_id)
        if pred:
            high_recalls.append(recall_at_k_for_item(pred, eval_item, k))

    if not low_recalls or not high_recalls:
        return float("nan")

    low_mean = np.mean(low_recalls)
    high_mean = np.mean(high_recalls)

    if low_mean == 0:
        return float("nan")

    return float(1.0 - (high_mean / low_mean))


def bootstrap_ci(
    values: list[float],
    n_resamples: int = 10000,
    ci: float = 0.95,
) -> tuple[float, float, float]:
    """Bootstrap confidence interval."""
    arr = np.array(values)
    np.random.seed(42)
    boot_means = []
    for _ in range(n_resamples):
        sample = np.random.choice(arr, size=len(arr), replace=True)
        boot_means.append(np.mean(sample))
    alpha = 1 - ci
    return float(np.mean(arr)), float(np.percentile(boot_means, 100 * alpha / 2)), float(np.percentile(boot_means, 100 * (1 - alpha / 2)))


# ---------------------------------------------------------------------------
# Experiment discovery
# ---------------------------------------------------------------------------

def find_condition(results_dir: Path, pattern: str) -> Path | None:
    """Find the latest experiment directory matching a pattern."""
    matches = sorted([d for d in results_dir.glob(f"*{pattern}*") if d.is_dir()])
    if not matches:
        return None
    return matches[-1]


def load_predictions(condition_dir: Path) -> dict[str, dict]:
    """Load predictions indexed by item ID."""
    pred_file = condition_dir / "predictions.jsonl"
    if not pred_file.exists():
        return {}
    preds = load_jsonl(pred_file)
    return {p["id"]: p for p in preds}


def main() -> int:
    args = parse_args()
    results_dir = Path(args.results_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load eval data
    eval_rows = load_jsonl(Path(args.eval_file))
    eval_data = {row["id"]: row for row in eval_rows}
    print(f"Loaded {len(eval_data)} eval items")

    # Print specificity distribution
    spec_dist = defaultdict(int)
    for item in eval_data.values():
        spec_dist[item.get("cultural_specificity", "unknown")] += 1
    print(f"Cultural specificity distribution: {dict(spec_dist)}")

    # Discover experiment conditions
    conditions = {}
    for d in sorted(results_dir.iterdir()):
        if not d.is_dir() or d.name == "q1_experiments" or d.name == "reports":
            continue
        pred_file = d / "predictions.jsonl"
        if pred_file.exists():
            conditions[d.name] = load_predictions(d)

    print(f"Found {len(conditions)} conditions: {list(conditions.keys())}")

    # 1. Compute CSS for every condition
    css_results = {}
    for cond_name, preds in conditions.items():
        css = compute_css(preds, eval_data, k=10)
        css_results[cond_name] = css

    # 2. Compute CRG for baseline vs each supplemented condition
    # Identify baseline and supplemented conditions
    baseline_name = None
    supplement_names = []
    for cond_name in conditions:
        if "baseline" in cond_name.lower() or cond_name == next(iter(conditions)):
            baseline_name = cond_name
        elif "supp" in cond_name.lower():
            supplement_names.append(cond_name)

    crg_all = {}
    if baseline_name and supplement_names:
        baseline_preds = conditions[baseline_name]
        for supp_name in supplement_names:
            supp_preds = conditions[supp_name]
            crg = compute_crg(baseline_preds, supp_preds, eval_data)
            crg_all[f"{baseline_name}_vs_{supp_name}"] = crg

    # 3. Stratified recall by specificity level for every condition
    stratified_recall = {}
    specificity_levels = ["unknown", "low", "medium", "high"]
    for cond_name, preds in conditions.items():
        stratified_recall[cond_name] = {}
        for level in specificity_levels:
            level_items = {
                item_id: item
                for item_id, item in eval_data.items()
                if item.get("cultural_specificity") == level
            }
            recalls = []
            for item_id, eval_item in level_items.items():
                pred = preds.get(item_id)
                if pred:
                    recalls.append(recall_at_k_for_item(pred, eval_item, k=10))
            if recalls:
                mean, lower, upper = bootstrap_ci(recalls, args.n_resamples)
                stratified_recall[cond_name][level] = {
                    "recall@10": float(mean),
                    "ci_lower": float(lower),
                    "ci_upper": float(upper),
                    "n": len(recalls),
                }

    # Save results
    output = {
        "css_by_condition": css_results,
        "crg_comparisons": crg_all,
        "stratified_recall": stratified_recall,
        "specificity_distribution": dict(spec_dist),
    }

    output_file = output_dir / "cultural_specificity_analysis.json"
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {output_file}")

    # Print CRG table
    print("\n" + "=" * 80)
    print("CULTURAL RETRIEVAL GAP (CRG) by Specificity Level")
    print("=" * 80)
    for comparison, crg in crg_all.items():
        print(f"\n  {comparison}")
        print(f"  {'Level':<12} {'Baseline':>10} {'Supplemented':>12} {'CRG':>8} {'N':>5}")
        print(f"  {'-' * 50}")
        for level in specificity_levels:
            if level in crg:
                r = crg[level]
                print(f"  {level:<12} {r['baseline_recall']:>10.3f} {r['supplemented_recall']:>12.3f} {r['crg']:>+8.3f} {r['n_items']:>5}")

    # Print CSS table
    print("\n" + "=" * 80)
    print("CULTURAL SENSITIVITY SCORE (CSS) by Condition")
    print("CSS = 1 - Recall(high_specificity)/Recall(low_specificity)")
    print("CSS -> 0: system handles cultural queries well")
    print("CSS -> 1: system fails on cultural queries")
    print("=" * 80)
    print(f"{'Condition':<50} {'CSS':>8}")
    print("-" * 60)
    for cond_name, css in sorted(css_results.items()):
        if np.isnan(css):
            print(f"{cond_name:<50} {'N/A':>8}")
        else:
            print(f"{cond_name:<50} {css:>8.3f}")

    # Print stratified recall table
    print("\n" + "=" * 80)
    print("RECALL@10 by Cultural Specificity Level")
    print("=" * 80)
    header = f"{'Condition':<40}" + "".join(f"  {level:>10}" for level in specificity_levels)
    print(header)
    print("-" * (40 + 12 * len(specificity_levels)))
    for cond_name, levels in sorted(stratified_recall.items()):
        row = f"{cond_name:<40}"
        for level in specificity_levels:
            if level in levels:
                row += f"  {levels[level]['recall@10']:>10.3f}"
            else:
                row += f"  {'N/A':>10}"
        print(row)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
