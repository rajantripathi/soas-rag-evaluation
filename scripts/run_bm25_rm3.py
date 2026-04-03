#!/usr/bin/env python3
"""BM25+RM3 (pseudo-relevance feedback) baseline for Q1 paper.

RM3 expands the query using terms from top-retrieved documents,
then re-runs BM25 with the expanded query. This is a standard IR
baseline that often significantly outperforms vanilla BM25.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.evaluation import retrieval_recall_at_k
from src.utils import ensure_dir, load_config, read_jsonl, write_jsonl


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run BM25+RM3 baseline.")
    p.add_argument("--config", required=True, help="Path to YAML config")
    p.add_argument("--eval-file", default="data/eval/manual_eval_v5.jsonl")
    p.add_argument("--output-dir", default=None)
    p.add_argument("--fb-docs", type=int, default=10, help="Number of feedback documents")
    p.add_argument("--fb-terms", type=int, default=20, help="Number of feedback terms")
    p.add_argument("--original-query-weight", type=float, default=0.5, help="Weight for original query")
    return p.parse_args()


TOKEN_RE = __import__("re").compile(r"\w+", __import__("re").UNICODE)


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text or "")]


class BM25RM3Index:
    """BM25 with RM3 pseudo-relevance feedback expansion.

    Parameters:
        k1, b: BM25 parameters
        fb_docs: Number of top documents for feedback
        fb_terms: Number of expansion terms
        original_query_weight: Weight of original query vs expansion (0.5 = equal)
    """

    def __init__(
        self,
        documents: list[dict[str, Any]],
        k1: float = 1.5,
        b: float = 0.75,
        fb_docs: int = 10,
        fb_terms: int = 20,
        original_query_weight: float = 0.5,
    ) -> None:
        self.documents = documents
        self.k1 = k1
        self.b = b
        self.fb_docs = fb_docs
        self.fb_terms = fb_terms
        self.original_query_weight = original_query_weight

        self.doc_tokens: list[list[str]] = []
        self.doc_term_freqs: list[Counter] = []
        self.doc_lengths: list[int] = []
        self.avg_doc_length: float = 0.0
        self.idf: dict[str, float] = {}
        self.doc_count: int = 0

    def build(self) -> None:
        doc_freq: Counter = Counter()
        for doc in self.documents:
            tokens = tokenize(doc.get("text", ""))
            tf = Counter(tokens)
            self.doc_tokens.append(tokens)
            self.doc_term_freqs.append(tf)
            self.doc_lengths.append(len(tokens))
            doc_freq.update(tf.keys())

        self.doc_count = len(self.documents)
        self.avg_doc_length = (
            sum(self.doc_lengths) / self.doc_count if self.doc_count else 0.0
        )
        self.idf = {
            term: math.log(1.0 + ((self.doc_count - freq + 0.5) / (freq + 0.5)))
            for term, freq in doc_freq.items()
        }

    def _bm25_score(self, query_tokens: list[str], idx: int) -> float:
        if not query_tokens:
            return 0.0
        doc_length = self.doc_lengths[idx]
        norm = self.k1 * (1.0 - self.b + self.b * (doc_length / (self.avg_doc_length or 1.0)))
        score = 0.0
        tf = self.doc_term_freqs[idx]
        for term in query_tokens:
            freq = tf.get(term, 0)
            if freq <= 0:
                continue
            score += self.idf.get(term, 0.0) * (freq * (self.k1 + 1.0)) / (freq + norm)
        return score

    def _expand_query(self, query_tokens: list[str], top_docs: list[int]) -> list[tuple[str, float]]:
        """RM3 query expansion: extract top terms from feedback documents."""
        # Score terms by RM3 weight
        term_scores: Counter = Counter()
        for doc_idx in top_docs:
            tf = self.doc_term_freqs[doc_idx]
            doc_len = max(self.doc_lengths[doc_idx], 1)
            for term, freq in tf.items():
                # RM3 term weight: P(t|D) * IDF
                term_prob = freq / doc_len
                idf_weight = self.idf.get(term, 0.0)
                term_scores[term] += term_prob * idf_weight

        # Return top fb_terms
        return term_scores.most_common(self.fb_terms)

    def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        query_tokens = tokenize(query)

        # Step 1: Initial BM25 retrieval
        scored = []
        for idx in range(self.doc_count):
            score = self._bm25_score(query_tokens, idx)
            if score > 0:
                scored.append((score, idx))
        scored.sort(key=lambda x: x[0], reverse=True)

        if not scored:
            return []

        # Step 2: RM3 expansion
        feedback_docs = [idx for _, idx in scored[:self.fb_docs]]
        expansion_terms = self._expand_query(query_tokens, feedback_docs)

        # Step 3: Build expanded query vector
        # Combine original query + expansion
        expanded_query: dict[str, float] = {}
        w_orig = self.original_query_weight
        w_exp = 1.0 - w_orig

        for term in query_tokens:
            expanded_query[term] = expanded_query.get(term, 0.0) + w_orig / max(len(query_tokens), 1)

        for term, weight in expansion_terms:
            total_exp_weight = sum(w for _, w in expansion_terms) or 1.0
            expanded_query[term] = expanded_query.get(term, 0.0) + w_exp * (weight / total_exp_weight)

        # Step 4: Re-score with expanded query
        rescored = []
        for idx in range(self.doc_count):
            tf = self.doc_term_freqs[idx]
            doc_len = max(self.doc_lengths[idx], 1)
            score = 0.0
            for term, q_weight in expanded_query.items():
                freq = tf.get(term, 0)
                if freq <= 0:
                    continue
                doc_freq_norm = freq / doc_len
                score += q_weight * doc_freq_norm * self.idf.get(term, 0.0)
            if score > 0:
                rescored.append((score, idx))

        rescored.sort(key=lambda x: x[0], reverse=True)

        results = []
        for rank, (score, idx) in enumerate(rescored[:top_k], start=1):
            result = dict(self.documents[idx])
            result["score"] = round(score, 6)
            result["rank"] = rank
            results.append(result)
        return results


def main() -> int:
    args = parse_args()
    config = load_config(args.config)

    output_dir = Path(args.output_dir) if args.output_dir else None
    if output_dir is None:
        results_dir = Path(config["paths"]["results_dir"])
        output_dir = results_dir / "q1_experiments" / "bm25_rm3_baseline"
    output_dir = ensure_dir(output_dir)

    # Load data
    eval_items = read_jsonl(Path(args.eval_file))
    corpus_file = config["paths"].get("corpus_file", "corpus.jsonl")
    corpus_path = Path(config["paths"]["processed_data_dir"]) / corpus_file
    documents = read_jsonl(corpus_path)
    print(f"Loaded {len(documents)} documents, {len(eval_items)} eval items")

    # Build index
    index = BM25RM3Index(
        documents,
        fb_docs=args.fb_docs,
        fb_terms=args.fb_terms,
        original_query_weight=args.original_query_weight,
    )
    index.build()

    # Run retrieval
    top_k = config.get("retrieval", {}).get("top_k", 10)
    predictions = []
    for item in eval_items:
        results = index.search(item["question"], top_k=top_k)
        recall = retrieval_recall_at_k(item, results)
        predictions.append({
            "id": item["id"],
            "language": item.get("language", "unknown"),
            "domain": item.get("domain", "unknown"),
            "cultural_specificity": item.get("cultural_specificity", "unknown"),
            "difficulty": item.get("difficulty", "unknown"),
            "retrieval_recall_at_k": recall,
            "contexts": [{"doc_id": r.get("doc_id"), "score": r.get("score"), "rank": r.get("rank")} for r in results],
        })

    write_jsonl(output_dir / "predictions.jsonl", predictions)

    # Summary
    en = [p for p in predictions if p["language"] == "en"]
    uz = [p for p in predictions if p["language"] == "uz"]
    summary = {
        "condition": "bm25_rm3",
        "fb_docs": args.fb_docs,
        "fb_terms": args.fb_terms,
        "original_query_weight": args.original_query_weight,
        "overall_recall@10": float(np.mean([p["retrieval_recall_at_k"] for p in predictions])),
        "en_recall@10": float(np.mean([p["retrieval_recall_at_k"] for p in en])) if en else 0,
        "uz_recall@10": float(np.mean([p["retrieval_recall_at_k"] for p in uz])) if uz else 0,
    }
    with (output_dir / "summary.json").open("w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults:")
    print(f"  Overall: {summary['overall_recall@10']:.3f}")
    print(f"  English: {summary['en_recall@10']:.3f}")
    print(f"  Uzbek:   {summary['uz_recall@10']:.3f}")
    print(f"  Saved to: {output_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
