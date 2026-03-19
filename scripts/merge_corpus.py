#!/usr/bin/env python3
import argparse
from pathlib import Path

import sys
sys.path.insert(0, '/home/u6ef/rajantripathi.u6ef/soas_rag_eval')

from src.utils import ensure_dir, read_jsonl, write_jsonl


def build_parser():
    """Build argument parser."""
    parser = argparse.ArgumentParser(description="Merge base corpus with supplement corpus.")
    parser.add_argument("--base-corpus", default="data/processed/corpus_manual_v1_uzsupp_v2.jsonl")
    parser.add_argument("--supplement", default="data/processed/corpus_english_supplement.jsonl")
    parser.add_argument("--output", default="data/processed/corpus_manual_v1_uzsupp_v2_ensupp.jsonl")
    return parser


def main():
    """Main function."""
    args = build_parser().parse_args()

    # Load corpora
    base_rows = read_jsonl(args.base_corpus)
    supplement_rows = read_jsonl(args.supplement)

    # Merge
    merged_rows = base_rows + supplement_rows

    # Write merged corpus
    ensure_dir(Path(args.output).parent)
    write_jsonl(args.output, merged_rows)

    # Print statistics
    print("Merged corpus created: {}".format(args.output))
    print("Base corpus documents: {}".format(len(base_rows)))
    print("Supplement documents: {}".format(len(supplement_rows)))
    print("Total merged documents: {}".format(len(merged_rows)))
    print("\nCorpus breakdown by source:")
    source_counts = {}
    for row in merged_rows:
        source = row.get("source", "unknown")
        source_counts[source] = source_counts.get(source, 0) + 1

    for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
        print("  {}: {} documents".format(source, count))

    return 0


if __name__ == "__main__":
    sys.exit(main())
