#!/usr/bin/env python3
"""
Create language-specific corpora for cross-lingual RAG evaluation.
This enables studying cultural bias: how much does performance drop when
using the wrong language corpus?
"""

import json
import sys
from pathlib import Path

def main():
    base_dir = Path("/home/u6ef/rajantripathi.u6ef/soas_rag_eval")
    corpus_file = base_dir / "data" / "processed" / "corpus_manual_v1_uzsupp_v2.jsonl"
    output_dir = base_dir / "data" / "processed"
    
    en_output = output_dir / "corpus_english_only.jsonl"
    uz_output = output_dir / "corpus_uzbek_only.jsonl"
    
    en_docs = []
    uz_docs = []
    
    # Read and split corpus
    with open(corpus_file) as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            lang = obj.get("language", "unknown")
            if lang == "en":
                en_docs.append(obj)
            elif lang.startswith("uz"):
                uz_docs.append(obj)
    
    # Write English-only corpus
    with open(en_output, "w") as f:
        for doc in en_docs:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")
    
    # Write Uzbek-only corpus
    with open(uz_output, "w") as f:
        for doc in uz_docs:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")
    
    print("Cross-lingual corpora created:")
    print(f"  English-only: {en_output} ({len(en_docs)} docs)")
    print(f"  Uzbek-only: {uz_output} ({len(uz_docs)} docs)")
    print()
    print("Experiments enabled:")
    print("  1. English corpus → Uzbek questions (cultural mismatch)")
    print("  2. Uzbek corpus → English questions (cultural mismatch)")
    print("  3. Compare to baseline (mixed corpus)")

if __name__ == "__main__":
    main()
