#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from scipy import stats

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils import ensure_dir, read_jsonl, write_jsonl


def build_parser():
    """Build argument parser."""
    parser = argparse.ArgumentParser(description="Compute statistical significance for experiment comparisons.")
    parser.add_argument("--results-dir", default="results", help="Base results directory")
    parser.add_argument("--eval-file", default="data/eval/manual_eval_v5.jsonl")
    parser.add_argument("--output", default="results/reports/statistical_analysis.md")
    parser.add_argument("--n-resamples", type=int, default=1000, help="Number of bootstrap resamples")
    parser.add_argument("--ci", type=float, default=0.95, help="Confidence interval level")
    return parser


def bootstrap_recall(predictions: List[Dict], n_resamples: int = 1000, ci: float = 0.95) -> Tuple[float, float, float]:
    """Compute bootstrap confidence interval for recall@k."""
    recalls = [p.get("retrieval_recall_at_k", 0.0) for p in predictions]

    # Bootstrap resampling
    np.random.seed(42)
    boot_means = []
    for _ in range(n_resamples):
        sample = np.random.choice(recalls, size=len(recalls), replace=True)
        boot_means.append(np.mean(sample))

    # Compute CI
    alpha = 1 - ci
    lower = np.percentile(boot_means, 100 * alpha / 2)
    upper = np.percentile(boot_means, 100 * (1 - alpha / 2))
    mean = np.mean(recalls)

    return mean, lower, upper


def compute_effect_size(recalls_a: List[float], recalls_b: List[float]) -> float:
    """Compute Cohen's d for difference in proportions."""
    mean_a = np.mean(recalls_a)
    mean_b = np.mean(recalls_b)
    pooled_std = np.sqrt((np.std(recalls_a) ** 2 + np.std(recalls_b) ** 2) / 2)

    if pooled_std == 0:
        return 0.0

    return abs(mean_b - mean_a) / pooled_std


def mcnemar_test_exact(pred_a: List[Dict], pred_b: List[Dict], gold_ids: List[str]) -> Tuple[float, float]:
    """Compute McNemar's test for paired binary comparisons."""
    # Build alignment by ID
    pred_a_by_id = {p["id"]: p for p in pred_a}
    pred_b_by_id = {p["id"]: p for p in pred_b}

    # Count contingency table
    # a = both correct, b = A correct B wrong, c = A wrong B correct, d = both wrong
    a = b = c = d = 0

    for gid in gold_ids:
        pa = pred_a_by_id.get(gid, {})
        pb = pred_b_by_id.get(gid, {})

        ra = pa.get("retrieval_recall_at_k", 0.0)
        rb = pb.get("retrieval_recall_at_k", 0.0)

        if ra >= 1.0 and rb >= 1.0:
            a += 1
        elif ra >= 1.0 and rb < 1.0:
            b += 1
        elif ra < 1.0 and rb >= 1.0:
            c += 1
        else:
            d += 1

    # McNemar's test (with continuity correction)
    if b + c == 0:
        return 1.0, 0.0  # No difference, p=1.0

    # Use an exact binomial test for the discordant pairs.
    p_value = stats.binomtest(min(b, c), n=b + c, p=0.5).pvalue

    # Effect size (difference in proportions)
    diff = (b - c) / (a + b + c + d) if (a + b + c + d) > 0 else 0.0

    return p_value, diff


def load_experiment_results(results_dir: Path, condition_name: str) -> List[Dict]:
    """Load predictions from experiment results directory."""
    # Try to find the most recent matching directory
    matching_dirs = sorted([d for d in results_dir.glob(f"*{condition_name}*") if d.is_dir()])

    if not matching_dirs:
        return []

    latest_dir = matching_dirs[-1]
    predictions_file = latest_dir / "predictions.jsonl"

    if not predictions_file.exists():
        return []

    return read_jsonl(predictions_file)


def main():
    """Main function."""
    args = build_parser().parse_args()

    # Load eval data
    eval_rows = read_jsonl(args.eval_file)
    gold_ids = [row["id"] for row in eval_rows]

    results_base = Path(args.results_dir)

    # Load experiment results (these will need to be adapted based on actual directory structure)
    experiments = {}
    exp_names = [
        "baseline",
        "vector_mpnet",
        "vector_e5",
        "uz_supp_v1",
        "uz_supp_v2",
    ]

    for exp_name in exp_names:
        predictions = load_experiment_results(results_base, exp_name)
        if predictions:
            experiments[exp_name] = predictions

    # Compute statistics for each condition
    stats_by_condition = {}

    for exp_name, predictions in experiments.items():
        # Overall
        mean, lower, upper = bootstrap_recall(predictions, args.n_resamples, args.ci)

        # Per-language
        en_preds = [p for p in predictions if p.get("language") == "en"]
        uz_preds = [p for p in predictions if p.get("language") == "uz"]

        en_mean, en_lower, en_upper = bootstrap_recall(en_preds, args.n_resamples, args.ci) if en_preds else (0, 0, 0)
        uz_mean, uz_lower, uz_upper = bootstrap_recall(uz_preds, args.n_resamples, args.ci) if uz_preds else (0, 0, 0)

        stats_by_condition[exp_name] = {
            "overall": (mean, lower, upper),
            "english": (en_mean, en_lower, en_upper),
            "uzbek": (uz_mean, uz_lower, uz_upper),
        }

    # Pairwise comparisons
    comparisons = []

    if "baseline" in experiments and "uz_supp_v2" in experiments:
        p_value, diff = mcnemar_test_exact(experiments["baseline"], experiments["uz_supp_v2"], gold_ids)
        comparisons.append({
            "condition_a": "Baseline",
            "condition_b": "UZ supp v2",
            "p_value": p_value,
            "difference": diff,
            "significant": p_value < 0.05,
        })

    # Write report
    ensure_dir(Path(args.output).parent)

    with Path(args.output).open("w", encoding="utf-8") as handle:
        handle.write("# Statistical Analysis\n\n")
        handle.write("## Methodology\n\n")
        handle.write("- Bootstrap confidence intervals: {} resamples, {:.0%} CI\n".format(args.n_resamples, args.ci))
        handle.write("- McNemar's test for paired binary comparisons\n")
        handle.write("- Cohen's d for effect sizes\n\n")

        handle.write("## Results by Condition\n\n")
        handle.write("| Condition | Overall | English | Uzbek |\n")
        handle.write("| --- | --- | --- | --- |\n")

        for exp_name in ["baseline", "vector_mpnet", "vector_e5", "uz_supp_v1", "uz_supp_v2"]:
            if exp_name not in stats_by_condition:
                continue

            stats = stats_by_condition[exp_name]
            overall = "{:.1%} [{:.1%}, {:.1%}]".format(*stats["overall"])
            english = "{:.1%} [{:.1%}, {:.1%}]".format(*stats["english"]) if stats["english"][0] > 0 else "N/A"
            uzbek = "{:.1%} [{:.1%}, {:.1%}]".format(*stats["uzbek"]) if stats["uzbek"][0] > 0 else "N/A"

            handle.write("| {} | {} | {} | {} |\n".format(exp_name.replace("_", " ").title(), overall, english, uzbek))

        handle.write("\n## Statistical Significance Tests\n\n")
        handle.write("| Condition A | Condition B | Difference | p-value | Significant |\n")
        handle.write("| --- | --- | --- | --- | --- |\n")

        for comp in comparisons:
            sig = "Yes" if comp["significant"] else "No"
            handle.write("| {} | {} | {:.1%} | {:.4f} | {} |\n".format(
                comp["condition_a"], comp["condition_b"], comp["difference"], comp["p_value"], sig
            ))

        handle.write("\n## Key Findings\n\n")

        if comparisons:
            for comp in comparisons:
                if comp["significant"]:
                    handle.write("- **{} vs {}**: Significant difference (p={:.4f}, {:.1%} absolute improvement)\n".format(
                        comp["condition_a"], comp["condition_b"], comp["p_value"], comp["difference"]
                    ))
                else:
                    handle.write("- **{} vs {}**: No significant difference (p={:.4f})\n".format(
                        comp["condition_a"], comp["condition_b"], comp["p_value"]
                    ))

        handle.write("\n## Limitations\n\n")
        handle.write("- Statistical power limited by sample size (400 items)\n")
        handle.write("- Bootstrap CIs assume independence of items\n")
        handle.write("- McNemar's test appropriate for paired binary comparisons\n")
        handle.write("- Effect sizes (Cohen's d) should be interpreted with caution for bounded proportions\n")

    print("Statistical analysis complete: {}".format(args.output))
    print("Analyzed {} conditions with {} comparisons".format(len(stats_by_condition), len(comparisons)))

    return 0


if __name__ == "__main__":
    sys.exit(main())
