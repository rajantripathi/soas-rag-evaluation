#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

import numpy as np
from scipy.stats import spearmanr

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils import ensure_dir, read_jsonl, write_jsonl


def build_parser():
    """Build argument parser."""
    parser = argparse.ArgumentParser(description="Analyse LLM-as-judge evaluation results.")
    parser.add_argument("--scores", default="results/eval_llm_judge/scores.jsonl", help="Path to judge scores")
    parser.add_argument("--output", default="results/reports/llm_judge_evaluation.md", help="Output report path")
    return parser


def compute_statistics(scores: List[Dict]) -> Dict:
    """Compute statistics on judge scores."""
    # Filter valid scores
    valid = [s for s in scores if s["judge_scores"].get("retrieval_relevance") is not None]

    if not valid:
        return {}

    stats = {}

    # Overall means
    for dim in ["retrieval_relevance", "answer_faithfulness", "answer_correctness", "cultural_grounding"]:
        values = [s["judge_scores"][dim] for s in valid]
        stats[f"{dim}_overall"] = {
            "mean": np.mean(values),
            "std": np.std(values),
            "min": np.min(values),
            "max": np.max(values),
        }

    # Per-language means
    for lang in ["en", "uz"]:
        lang_scores = [s for s in valid if s.get("language") == lang]
        if lang_scores:
            for dim in ["retrieval_relevance", "answer_faithfulness", "answer_correctness", "cultural_grounding"]:
                values = [s["judge_scores"][dim] for s in lang_scores]
                stats[f"{dim}_{lang}"] = {
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "count": len(values),
                }

    # Per-domain means
    for domain in ["governance", "history", "institutions", "culture"]:
        domain_scores = [s for s in valid if s.get("domain") == domain]
        if domain_scores:
            for dim in ["retrieval_relevance", "answer_faithfulness", "answer_correctness", "cultural_grounding"]:
                values = [s["judge_scores"][dim] for s in domain_scores]
                stats[f"{dim}_{domain}"] = {
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "count": len(domain_scores),
                }

    # Correlation between retrieval_relevance and recall@k
    recall_values = [s.get("retrieval_recall_at_k", 0) for s in valid]
    retrieval_rel = [s["judge_scores"]["retrieval_relevance"] for s in valid]

    if len(recall_values) > 1 and len(retrieval_rel) > 1:
        corr, p_value = spearmanr(recall_values, retrieval_rel)
        stats["recall_retrieval_relevance_correlation"] = {
            "correlation": corr,
            "p_value": p_value,
            "n": len(valid),
        }

    # Interesting edge cases
    # 1. High recall but low cultural grounding
    high_recall_low_culture = [
        s for s in valid
        if s.get("retrieval_recall_at_k", 0) >= 1.0 and s["judge_scores"]["cultural_grounding"] < 3
    ]

    # 2. Low recall but high correctness (model knew answer without retrieval)
    low_recall_high_correct = [
        s for s in valid
        if s.get("retrieval_recall_at_k", 0) < 1.0 and s["judge_scores"]["answer_correctness"] >= 4
    ]

    stats["edge_cases"] = {
        "high_recall_low_culture": len(high_recall_low_culture),
        "low_recall_high_correct": len(low_recall_high_correct),
        "high_recall_low_culture_items": [s["id"] for s in high_recall_low_culture],
        "low_recall_high_correct_items": [s["id"] for s in low_recall_high_correct],
    }

    return stats


def write_report(output_path: Path, scores: List[Dict], stats: Dict):
    """Write analysis report."""
    ensure_dir(output_path.parent)

    with output_path.open("w", encoding="utf-8") as handle:
        handle.write("# LLM-as-Judge Evaluation Results\n\n")

        if not stats:
            handle.write("## No Valid Scores\n\n")
            handle.write("No valid LLM judge scores were obtained. ")
            handle.write("This may be due to:\n")
            handle.write("- Model loading failure\n")
            handle.write("- JSON parsing errors\n")
            handle.write("- Network or resource issues\n\n")
            handle.write("Check the log files for details.\n")
            return

        handle.write("## Overview\n\n")
        handle.write(f"Total items judged: {len(scores)}\n")
        handle.write(f"Valid scores: {len([s for s in scores if s['judge_scores'].get('retrieval_relevance') is not None])}\n")
        handle.write(f"Invalid scores: {len([s for s in scores if s['judge_scores'].get('retrieval_relevance') is None])}\n\n")

        handle.write("## Summary Table\n\n")
        handle.write("| Dimension | Overall | English | Uzbek |\n")
        handle.write("| --- | --- | --- | --- |\n")

        for dim in ["retrieval_relevance", "answer_faithfulness", "answer_correctness", "cultural_grounding"]:
            overall = stats.get(f"{dim}_overall", {}).get("mean", 0)
            en = stats.get(f"{dim}_en", {}).get("mean", 0)
            uz = stats.get(f"{dim}_uz", {}).get("mean", 0)
            handle.write(f"| {dim} | {overall:.2f} | {en:.2f} | {uz:.2f} |\n")

        handle.write("\n## Per-Domain Breakdown\n\n")
        handle.write("| Domain | Retrieval Relevance | Answer Faithfulness | Answer Correctness | Cultural Grounding |\n")
        handle.write("| --- | --- | --- | --- | --- |\n")

        for domain in ["governance", "history", "institutions", "culture"]:
            rel = stats.get(f"retrieval_relevance_{domain}", {}).get("mean", 0)
            faith = stats.get(f"answer_faithfulness_{domain}", {}).get("mean", 0)
            corr = stats.get(f"answer_correctness_{domain}", {}).get("mean", 0)
            cult = stats.get(f"cultural_grounding_{domain}", {}).get("mean", 0)
            handle.write(f"| {domain.capitalize()} | {rel:.2f} | {faith:.2f} | {corr:.2f} | {cult:.2f} |\n")

        handle.write("\n## Correlation Analysis\n\n")

        if "recall_retrieval_relevance_correlation" in stats:
            corr_stats = stats["recall_retrieval_relevance_correlation"]
            handle.write(f"**Spearman correlation between retrieval_relevance and recall@k:** ")
            handle.write(f"r = {corr_stats['correlation']:.3f}, p = {corr_stats['p_value']:.4f}\n\n")

            if corr_stats['p_value'] < 0.05:
                handle.write("The correlation is statistically significant, suggesting that ")
                handle.write("the LLM judge's assessment of retrieval relevance aligns with ")
                handle.write("the binary recall@k metric.\n\n")
            else:
                handle.write("The correlation is not statistically significant, suggesting that ")
                handle.write("the LLM judge's assessment captures different aspects of retrieval quality.\n\n")
        else:
            handle.write("Correlation analysis could not be computed.\n\n")

        handle.write("## Interesting Edge Cases\n\n")

        edge_cases = stats.get("edge_cases", {})
        high_recall_low_culture = edge_cases.get("high_recall_low_culture_items", [])
        low_recall_high_correct = edge_cases.get("low_recall_high_correct_items", [])

        if high_recall_low_culture:
            handle.write(f"### High Recall but Low Cultural Grounding ({edge_cases.get('high_recall_low_culture', 0)} items)\n\n")
            handle.write("These items had successful retrieval (recall@k >= 1.0) but low cultural grounding scores (< 3):\n\n")
            for item_id in high_recall_low_culture[:5]:
                handle.write(f"- `{item_id}`\n")
            if len(high_recall_low_culture) > 5:
                handle.write(f"- ... and {len(high_recall_low_culture) - 5} more\n")
            handle.write("\n")

        if low_recall_high_correct:
            handle.write(f"### Low Recall but High Answer Correctness ({edge_cases.get('low_recall_high_correct', 0)} items)\n\n")
            handle.write("These items had failed retrieval (recall@k < 1.0) but high answer correctness scores (>= 4):\n\n")
            for item_id in low_recall_high_correct[:5]:
                handle.write(f"- `{item_id}`\n")
            if len(low_recall_high_correct) > 5:
                handle.write(f"- ... and {len(low_recall_high_correct) - 5} more\n")
            handle.write("\n")

        handle.write("## Methodology\n\n")
        handle.write("### Judge Prompt\n\n")
        handle.write("The LLM judge was instructed to score each item on four dimensions from 1-5:\n\n")
        handle.write("- **retrieval_relevance**: Is the retrieved passage relevant to answering the question?\n")
        handle.write("- **answer_faithfulness**: Is the system answer grounded in the retrieved passage?\n")
        handle.write("- **answer_correctness**: Does the system answer convey the same information as the gold answer?\n")
        handle.write("- **cultural_grounding**: Does the answer appropriately reflect culturally specific knowledge?\n\n")

        handle.write("### Selection Strategy\n\n")
        handle.write("Items were selected to ensure:\n")
        handle.write("- Balanced representation: 50 English, 50 Uzbek\n")
        handle.write("- Stratified by domain: ~12-13 items per domain per language\n")
        handle.write("- Mix of success and failure cases based on recall@k\n")
        handle.write("- Random seed: 42 for reproducibility\n\n")

        handle.write("### Model\n\n")
        handle.write("**Model:** mistralai/Mistral-7B-Instruct-v0.3\n\n")
        handle.write("**Parameters:**\n")
        handle.write("- `max_new_tokens`: 256\n")
        handle.write("- `temperature`: 0.1 (near-deterministic)\n")
        handle.write("- `torch_dtype`: float16\n\n")

        handle.write("## Limitations\n\n")
        handle.write("1. **Stub generation**: System answers are first retrieved sentences, not full LLM generations. ")
        handle.write("This may affect faithfulness and correctness scores.\n\n")

        handle.write("2. **Single model**: Results may vary with different judge models. ")
        handle.write("Consider ensemble or multiple judges for robustness.\n\n")

        handle.write("3. **Sample size**: 100 items provides initial insights but larger samples would yield more reliable statistics.\n\n")

        handle.write("4. **Subjectivity**: Cultural grounding and relevance assessment have inherent subjectivity. ")
        handle.write("Human evaluation would provide ground truth for validating judge scores.\n\n")

        handle.write("## Next Steps\n\n")
        handle.write("1. **Human validation**: Compare LLM judge scores with human assessments on a subset of items\n")
        handle.write("2. **Error analysis**: Detailed qualitative analysis of edge cases identified above\n")
        handle.write("3. **Model comparison**: Test different judge models for robustness\n")
        handle.write("4. **Expand sample**: Judge all 400 items for more comprehensive analysis\n")


def main():
    """Main function."""
    args = build_parser().parse_args()

    # Load scores
    print(f"Loading scores from {args.scores}")
    scores = read_jsonl(args.scores)

    print(f"Loaded {len(scores)} scored items")

    # Compute statistics
    print("Computing statistics...")
    stats = compute_statistics(scores)

    # Write report
    print(f"Writing report to {args.output}")
    write_report(Path(args.output), scores, stats)

    # Print summary
    if stats:
        print("\nSummary Statistics:")
        for dim in ["retrieval_relevance", "answer_faithfulness", "answer_correctness", "cultural_grounding"]:
            overall = stats.get(f"{dim}_overall", {}).get("mean", 0)
            en = stats.get(f"{dim}_en", {}).get("mean", 0)
            uz = stats.get(f"{dim}_uz", {}).get("mean", 0)
            print(f"  {dim}: overall={overall:.2f}, en={en:.2f}, uz={uz:.2f}")

        if "recall_retrieval_relevance_correlation" in stats:
            corr = stats["recall_retrieval_relevance_correlation"]
            print(f"\nCorrelation (recall@k vs retrieval_relevance): r={corr['correlation']:.3f}, p={corr['p_value']:.4f}")

        edge = stats.get("edge_cases", {})
        print(f"\nEdge cases:")
        print(f"  High recall, low culture: {edge.get('high_recall_low_culture', 0)}")
        print(f"  Low recall, high correct: {edge.get('low_recall_high_correct', 0)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
