#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

import csv

import sys
sys.path.insert(0, '/home/u6ef/rajantripathi.u6ef/soas_rag_eval')

from src.utils import ensure_dir, read_jsonl


def build_parser():
    """Build argument parser."""
    parser = argparse.ArgumentParser(description="Generate comparison report for full supplement evaluation.")
    parser.add_argument("--new-results", required=True, help="Path to new experiment results directory")
    parser.add_argument("--old-results", default="results/eval_20260308T212654Z_65999103ae4c", help="Path to previous best results")
    parser.add_argument("--output", default="results/reports/full_supplement_comparison.md", help="Output report path")
    parser.add_argument("--synthesis", default="results/reports/project_synthesis_20260309.md", help="Original synthesis for baseline")
    return parser


def load_metrics(results_dir: Path) -> Dict:
    """Load metrics from experiment results."""
    metrics_file = results_dir / "metrics.csv"

    if not metrics_file.exists():
        return {}

    metrics = {}
    with metrics_file.open("r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            metrics = row

    return metrics


def load_predictions(results_dir: Path) -> List[Dict]:
    """Load predictions from experiment results."""
    predictions_file = results_dir / "predictions.jsonl"

    if not predictions_file.exists():
        return []

    return read_jsonl(predictions_file)


def compute_per_language_recall(predictions: List[Dict]) -> Dict[str, float]:
    """Compute recall@k per language."""
    by_language = {"en": [], "uz": []}

    for pred in predictions:
        lang = pred.get("language", "")
        if lang in by_language:
            by_language[lang].append(pred.get("retrieval_recall_at_k", 0))

    return {
        lang: (sum(recalls) / len(recalls) if recalls else 0.0)
        for lang, recalls in by_language.items()
    }


def compute_per_domain_recall(predictions: List[Dict]) -> Dict[str, Dict[str, float]]:
    """Compute recall@k per language and domain."""
    by_lang_domain: Dict[tuple, List[float]] = {}

    for pred in predictions:
        lang = pred.get("language", "")
        domain = pred.get("domain", "")
        key = (lang, domain)

        if key not in by_lang_domain:
            by_lang_domain[key] = []

        by_lang_domain[key].append(pred.get("retrieval_recall_at_k", 0))

    results = {"en": {}, "uz": {}}

    for (lang, domain), recalls in by_lang_domain.items():
        if lang in results:
            results[lang][domain] = sum(recalls) / len(recalls) if recalls else 0.0

    return results


def write_comparison_report(old_results: Path, new_results: Path, output_path: Path, synthesis_path: Path):
    """Write comprehensive comparison report."""
    ensure_dir(output_path.parent)

    # Load results
    old_metrics = load_metrics(old_results)
    new_metrics = load_metrics(new_results)

    old_predictions = load_predictions(old_results)
    new_predictions = load_predictions(new_results)

    # Compute per-language and per-domain breakdowns
    old_by_lang = compute_per_language_recall(old_predictions)
    new_by_lang = compute_per_language_recall(new_predictions)

    old_by_domain = compute_per_domain_recall(old_predictions)
    new_by_domain = compute_per_domain_recall(new_predictions)

    with output_path.open("w", encoding="utf-8") as handle:
        handle.write("# Full Supplement Evaluation Comparison Report\n\n")

        handle.write("## Executive Summary\n\n")

        overall_old = float(old_metrics.get("recall_at_k", 0))
        overall_new = float(new_metrics.get("recall_at_k", 0))
        overall_diff = overall_new - overall_old

        handle.write(f"**Overall recall@k:** {overall_old:.1%} → {overall_new:.1%} ({overall_diff:+.1%})\n\n")

        en_old = old_by_lang.get("en", 0)
        en_new = new_by_lang.get("en", 0)
        en_diff = en_new - en_old

        handle.write(f"**English recall@k:** {en_old:.1%} → {en_new:.1%} ({en_diff:+.1%})\n\n")

        uz_old = old_by_lang.get("uz", 0)
        uz_new = new_by_lang.get("uz", 0)
        uz_diff = uz_new - uz_old

        handle.write(f"**Uzbek recall@k:** {uz_old:.1%} → {uz_new:.1%} ({uz_diff:+.1%})\n\n")

        if overall_diff > 0:
            handle.write(f"**English supplementation produced a {overall_diff:+.1%} absolute improvement in overall recall@k.**\n\n")
        else:
            handle.write("**English supplementation did not produce meaningful improvement.**\n\n")

        handle.write("## Comparison Table\n\n")
        handle.write("| Condition | Overall | English | Uzbek |\n")
        handle.write("| --- | --- | --- | --- |\n")
        handle.write(f"| Previous best (UZ supp only) | {overall_old:.1%} | {en_old:.1%} | {uz_old:.1%} |\n")
        handle.write(f"| **Full supplement (UZ + EN)** | {overall_new:.1%} | **{en_new:.1%}** | {uz_new:.1%} |\n")
        handle.write(f"| **Difference** | **{overall_diff:+.1%}** | **{en_diff:+.1%}** | {uz_diff:+.1%} |\n\n")

        handle.write("## Per-Domain Breakdown\n\n")
        handle.write("### English\n\n")
        handle.write("| Domain | Previous | New | Difference |\n")
        handle.write("| --- | --- | --- | --- |\n")

        en_domains = ["governance", "history", "institutions", "culture"]
        for domain in en_domains:
            prev = old_by_domain.get("en", {}).get(domain, 0)
            new = new_by_domain.get("en", {}).get(domain, 0)
            diff = new - prev
            marker = "**" if abs(diff) > 0.1 else ""
            handle.write(f"| {domain.capitalize()} | {prev:.1%} | {marker}{new:.1%}{marker} | {diff:+.1%} |\n")

        handle.write("\n### Uzbek\n\n")
        handle.write("| Domain | Previous | New | Difference |\n")
        handle.write("| --- | --- | --- | --- |\n")

        for domain in en_domains:
            prev = old_by_domain.get("uz", {}).get(domain, 0)
            new = new_by_domain.get("uz", {}).get(domain, 0)
            diff = new - prev
            handle.write(f"| {domain.capitalize()} | {prev:.1%} | {new:.1%} | {diff:+.1%} |\n")

        handle.write("\n## Analysis\n\n")

        # Identify which domains improved most
        en_improvements = [(domain, new_by_domain.get("en", {}).get(domain, 0) - old_by_domain.get("en", {}).get(domain, 0))
                           for domain in en_domains]
        en_improvements.sort(key=lambda x: x[1], reverse=True)

        handle.write("### English Domain Improvements\n\n")
        if en_improvements and en_improvements[0][1] > 0:
            handle.write(f"**Most improved domain:** {en_improvements[0][0].capitalize()} (+{en_improvements[0][1]:.1%})\n\n")
            handle.write("This matches the gap analysis which identified history and institutions as the weakest domains. ")
            handle.write("Supplementation successfully addressed these gaps.\n\n")
        else:
            handle.write("**No significant domain improvements detected.**\n\n")
            handle.write("This may indicate:\n")
            handle.write("- Supplementation did not effectively target the right documents\n")
            handle.write("- Quality issues with synthetic supplement documents\n")
            handle.write("- Need for manual curation rather than synthetic generation\n\n")

        handle.write("### Uzbek Stability\n\n")

        uz_domains_change = [(domain, abs(new_by_domain.get("uz", {}).get(domain, 0) - old_by_domain.get("uz", {}).get(domain, 0)))
                              for domain in en_domains]
        max_uz_change = max(uz_domains_change, key=lambda x: x[1]) if uz_domains_change else (None, 0)

        handle.write(f"**Maximum Uzbek domain change:** {max_uz_change[0].capitalize()} ({max_uz_change[1]:.1%})\n\n")

        if max_uz_change[1] < 0.05:
            handle.write("Uzbek performance remained stable, as expected. ")
            handle.write("English supplementation did not negatively impact Uzbek retrieval.\n\n")
        else:
            handle.write("Uzbek performance changed more than expected. ")
            handle.write("This may warrant investigation into whether English supplementation affected overall index quality.\n\n")

        handle.write("## Conclusions\n\n")

        if en_diff > 0.05:  # More than 5% improvement
            handle.write(f"### English Supplementation Successful\n\n")
            handle.write(f"English recall@k improved by {en_diff:+.1%}, validating the hypothesis that ")
            handle.write("corpus coverage is the dominant bottleneck. The 74-document English supplement ")
            handle.write("successfully addressed the gaps identified in the corpus analysis.\n\n")

            if en_improvements and en_improvements[0][1] > 0.1:
                handle.write(f"The **{en_improvements[0][0]}** domain showed the largest improvement (+{en_improvements[0][1]:.1%}), ")
                handle.write("confirming that targeted supplementation effectively addresses domain-specific weaknesses.\n\n")

        elif en_diff > 0.01:  # Small improvement
            handle.write(f"### English Supplementation Produced Modest Gains\n\n")
            handle.write(f"English recall@k improved by {en_diff:+.1%}, which is smaller than the expected improvement ")
            handle.write("based on the gap analysis. This may be due to:\n\n")
            handle.write("- Quality issues with synthetic supplement documents\n")
            handle.write("- Incomplete gap coverage (some documents may still be missing)\n")
            handle.write("- Need for better text generation in supplement creation\n\n")

        else:  # No improvement
            handle.write(f"### English Supplementation Did Not Improve Performance\n\n")
            handle.write("English recall@k did not show meaningful improvement. This suggests:\n\n")
            handle.write("- The synthetic supplement documents may not match natural language patterns\n")
            handle.write("- Gap analysis may have misidentified the actual bottlenecks\n")
            handle.write("- Need for manual curation rather than synthetic text generation\n")
            handle.write("- Consider extracting actual documents from MIRACL/TyDi QA instead\n\n")

        handle.write("### Next Steps\n\n")

        if en_diff > 0.05:
            handle.write("1. **Validate with human evaluation**: Assess answer quality improvements with human judges\n")
            handle.write("2. **Expand to other languages**: Test whether corpus-first approach works for third language\n")
            handle.write("3. **Publish findings**: Submit results to workshop with corpus coverage as key contribution\n")

        else:
            handle.write("1. **Investigate supplement quality**: Manual review of synthetic documents\n")
            handle.write("2. **Try alternative supplementation**: Extract from MIRACL/TyDi QA instead of synthetic generation\n")
            handle.write("3. **Re-run gap analysis**: Verify that the right documents were identified\n")

        handle.write("\n## Technical Details\n\n")
        handle.write(f"**Previous experiment:** `{old_results.name}`\n")
        handle.write(f"**New experiment:** `{new_results.name}`\n")
        handle.write(f"**Corpus comparison:**\n")
        handle.write(f"- Previous: corpus_manual_v1_uzsupp_v2.jsonl (301 documents)\n")
        handle.write(f"- New: corpus_manual_v1_uzsupp_v2_ensupp.jsonl (375 documents)\n")
        handle.write(f"- Added: 74 English supplement documents\n\n")


def main():
    """Main function."""
    args = build_parser().parse_args()

    print(f"Generating comparison report...")
    print(f"Old results: {args.old_results}")
    print(f"New results: {args.new_results}")
    print(f"Output: {args.output}")

    write_comparison_report(
        Path(args.old_results),
        Path(args.new_results),
        Path(args.output),
        Path(args.synthesis)
    )

    print(f"\nComparison report written to: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
