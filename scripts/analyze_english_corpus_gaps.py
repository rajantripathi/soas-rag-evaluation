#!/usr/bin/env python3
import argparse
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils import ensure_dir, read_jsonl


def build_parser():
    """Build argument parser."""
    parser = argparse.ArgumentParser(description="Analyze English corpus coverage gaps by domain.")
    parser.add_argument("--eval-file", default="data/eval/manual_eval_v5.jsonl")
    parser.add_argument("--corpus-file", default="data/processed/corpus_manual_v1_uzsupp_v2.jsonl")
    parser.add_argument(
        "--output",
        default="results/reports/english_corpus_gap_analysis.md",
    )
    return parser


def analyze_english_gaps(eval_rows, corpus_ids):
    """Analyze English items by domain for corpus coverage gaps."""
    english_items = [row for row in eval_rows if row["language"] == "en"]

    domains = ["governance", "history", "institutions", "culture"]
    summary = {}

    for domain in domains:
        domain_items = [row for row in english_items if row["domain"] == domain]

        # Check which items have their source document in the corpus
        present = []
        missing = []

        for item in domain_items:
            source_doc_ids = item.get("source_doc_ids", [])
            if source_doc_ids and source_doc_ids[0] in corpus_ids:
                present.append(item)
            else:
                missing.append(item)

        summary[domain] = {
            "total": len(domain_items),
            "present": len(present),
            "missing": len(missing),
            "present_items": present,
            "missing_items": missing,
            "coverage_pct": (len(present) / len(domain_items) * 100) if domain_items else 0.0,
        }

    return summary


def write_report(path, summary):
    """Generate markdown report with gap analysis findings."""
    ensure_dir(path.parent)

    with path.open("w", encoding="utf-8") as handle:
        handle.write("# English Corpus Gap Analysis\n\n")
        handle.write("## Overview\n\n")
        handle.write("This analysis identifies missing English source documents in the current corpus, ")
        handle.write("following the same methodology used for Uzbek gap analysis. ")
        handle.write("The goal is to identify which English domains need supplementation.\n\n")

        # Overall summary
        total_en = sum(s["total"] for s in summary.values())
        total_present = sum(s["present"] for s in summary.values())
        total_missing = sum(s["missing"] for s in summary.values())

        handle.write("**Total English items:** {}\n".format(total_en))
        handle.write("**Items with source in corpus:** {} ({:.1f}%)\n".format(total_present, total_present/total_en*100))
        handle.write("**Items with missing source:** {} ({:.1f}%)\n\n".format(total_missing, total_missing/total_en*100))

        # Per-domain breakdown table
        handle.write("## Coverage by Domain\n\n")
        handle.write("| Domain | Total | Present | Missing | Coverage % |\n")
        handle.write("| --- | ---: | ---: | ---: | ---: |\n")

        for domain in ["governance", "history", "institutions", "culture"]:
            stats = summary[domain]
            handle.write(
                "| {} | {} | {} | {} | {:.1f}% |\n".format(
                    domain.capitalize(), stats['total'], stats['present'],
                    stats['missing'], stats['coverage_pct']
                )
            )
        handle.write("\n")

        # Detailed missing items by domain
        handle.write("## Missing Source Documents by Domain\n\n")

        for domain in ["governance", "history", "institutions", "culture"]:
            stats = summary[domain]
            if stats['missing_items']:
                handle.write("### {}\n\n".format(domain.capitalize()))
                handle.write("**Missing count:** {} of {} ({:.1f}%)\n\n".format(
                    stats['missing'], stats['total'], stats['missing']/stats['total']*100
                ))

                # List missing items with source titles
                for item in stats['missing_items'][:10]:  # Show first 10
                    source_title = item.get('source_title', item.get('source_doc_ids', ['unknown'])[0])
                    handle.write("- **{}** (`{}`): {}...\n".format(
                        item['id'], source_title, item['question'][:80]
                    ))

                if len(stats['missing_items']) > 10:
                    handle.write("- ... and {} more\n".format(len(stats['missing_items']) - 10))
                handle.write("\n")

        # Findings and recommendations
        handle.write("## Key Findings\n\n")

        # Identify weakest domain
        sorted_domains = sorted(summary.items(), key=lambda x: x[1]['coverage_pct'])
        weakest_domain = sorted_domains[0]

        handle.write("1. **Weakest domain:** {} with only {:.1f}% coverage\n".format(
            weakest_domain[0].capitalize(), weakest_domain[1]['coverage_pct']
        ))

        # Count how many domains have <70% coverage
        weak_domains = [d for d, s in summary.items() if s['coverage_pct'] < 70.0]
        if weak_domains:
            handle.write("2. **Domains needing attention:** {} (all below 70% coverage)\n".format(
                ', '.join(weak_domains).capitalize()
            ))

        handle.write("3. **Total supplementation needed:** {} English documents\n\n".format(total_missing))

        handle.write("## Recommendations\n\n")
        handle.write("Based on this analysis, the following supplementation strategy is recommended:\n\n")

        for domain in ["governance", "history", "institutions", "culture"]:
            stats = summary[domain]
            if stats['missing'] > 0:
                handle.write("### {}\n\n".format(domain.capitalize()))
                handle.write("- **Priority:** {}\n".format('High' if stats['coverage_pct'] < 70 else 'Medium'))
                handle.write("- **Documents needed:** {}\n".format(stats['missing']))
                handle.write("- **Source strategy:** Search MIRACL and TyDi QA English corpora for matching Wikipedia titles\n\n")

        handle.write("## Next Steps\n\n")
        handle.write("1. Extract missing English documents from existing raw datasets (MIRACL, TyDi QA)\n")
        handle.write("2. For documents not found in raw datasets, flag for manual curation\n")
        handle.write("3. Build English supplement corpus and merge with existing corpus\n")
        handle.write("4. Re-run evaluation to measure English recall improvement\n\n")


def main():
    """Main function."""
    args = build_parser().parse_args()

    # Load data
    eval_rows = read_jsonl(args.eval_file)
    corpus_rows = read_jsonl(args.corpus_file)

    # Build set of corpus doc_ids
    corpus_ids = {row["doc_id"] for row in corpus_rows}

    # Analyze gaps
    summary = analyze_english_gaps(eval_rows, corpus_ids)

    # Write report
    write_report(Path(args.output), summary)

    # Print summary
    print("English gap analysis complete.")
    print("Total English items: {}".format(sum(s['total'] for s in summary.values())))
    print("Items with source in corpus: {}".format(sum(s['present'] for s in summary.values())))
    print("Items with missing source: {}".format(sum(s['missing'] for s in summary.values())))
    print("\nReport written to: {}".format(args.output))

    return 0


if __name__ == "__main__":
    sys.exit(main())
