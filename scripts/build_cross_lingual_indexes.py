#!/usr/bin/env python3
"""Build indexes for cross-lingual experiments."""

import json
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def build_index(corpus_file: str, index_name: str):
    """Build a single index."""
    from src.rag.index import DocumentIndex
    
    print(f"Building {index_name}...")
    
    docs = []
    with open(corpus_file) as f:
        for line in f:
            if line.strip():
                docs.append(json.loads(line))
    
    index = DocumentIndex(
        index_name=index_name,
        model_name="intfloat/multilingual-e5-large"
    )
    index.build(docs)
    print(f"  Done: {len(docs)} documents indexed")

def main():
    base = Path("/home/u6ef/rajantripathi.u6ef/soas_rag_eval")
    data_dir = base / "data"
    
    builds = [
        ("processed/corpus_english_only.jsonl", "indexes/cross_lingual_english_only_index"),
        ("processed/corpus_uzbek_only.jsonl", "indexes/cross_lingual_uzbek_only_index"),
    ]
    
    for corpus_rel, index_rel in builds:
        corpus_file = data_dir / corpus_rel
        index_path = data_dir / index_rel
        build_index(str(corpus_file), str(index_path))

if __name__ == "__main__":
    main()
