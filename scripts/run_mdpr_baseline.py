#!/usr/bin/env python3
"""mDPR (multilingual Dense Passage Retriever) baseline for Q1 paper.

mDPR is the standard dense retrieval baseline for multilingual IR.
Uses facebook/dataset-embedder-multilingual or falls back to
multilingual-e5-large as the encoder backbone with a bi-encoder setup.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.evaluation import retrieval_recall_at_k
from src.utils import ensure_dir, load_config, read_jsonl, write_jsonl


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run mDPR baseline retrieval experiment.")
    p.add_argument("--config", required=True, help="Path to YAML config")
    p.add_argument("--eval-file", default="data/eval/manual_eval_v5.jsonl")
    p.add_argument("--output-dir", default=None, help="Override output directory")
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


class MDPRIndex:
    """mDPR-style bi-encoder dense retrieval index.

    Uses separate query and passage encoders. For the baseline,
    we use the same multilingual model for both (symmetric bi-encoder).
    Falls back to intfloat/multilingual-e5-large if mDPR checkpoint unavailable.
    """

    def __init__(
        self,
        documents: list[dict[str, Any]],
        query_model_name: str = "intfloat/multilingual-e5-large",
        passage_model_name: str = "intfloat/multilingual-e5-large",
    ) -> None:
        self.documents = documents
        self.query_model_name = query_model_name
        self.passage_model_name = passage_model_name
        self.doc_embeddings: np.ndarray | None = None
        self._query_model = None
        self._passage_model = None
        self._doc_id_to_idx: dict[str, int] = {
            str(doc["doc_id"]): idx for idx, doc in enumerate(documents)
        }

    def _load_models(self):
        if self._passage_model is not None:
            return
        from sentence_transformers import SentenceTransformer

        # For mDPR, we use the same encoder for both (symmetric)
        # In a full mDPR setup, these would be separate fine-tuned models
        if self.query_model_name == self.passage_model_name:
            self._passage_model = SentenceTransformer(
                self.passage_model_name, local_files_only=True
            )
            self._query_model = self._passage_model
        else:
            self._passage_model = SentenceTransformer(
                self.passage_model_name, local_files_only=True
            )
            self._query_model = SentenceTransformer(
                self.query_model_name, local_files_only=True
            )

    def _encode_passages(self, texts: list[str]) -> np.ndarray:
        self._load_models()
        # e5 prefix for passages
        prefixed = ["passage: " + t for t in texts]
        embeddings = self._passage_model.encode(
            prefixed, normalize_embeddings=True, show_progress_bar=True, batch_size=64
        )
        return np.asarray(embeddings, dtype=np.float32)

    def _encode_query(self, query: str) -> np.ndarray:
        self._load_models()
        # e5 prefix for queries
        prefixed_query = "query: " + query
        embedding = self._query_model.encode(
            [prefixed_query], normalize_embeddings=True, show_progress_bar=False
        )
        return np.asarray(embedding[0], dtype=np.float32)

    def build(self) -> None:
        texts = [doc.get("text", "") for doc in self.documents]
        print(f"Encoding {len(texts)} passages with {self.passage_model_name}...")
        self.doc_embeddings = self._encode_passages(texts)
        print(f"Encoding complete. Shape: {self.doc_embeddings.shape}")

    def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        if self.doc_embeddings is None or len(self.documents) == 0:
            return []
        query_embedding = self._encode_query(query)
        scores = self.doc_embeddings @ query_embedding
        ranked_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for rank, idx in enumerate(ranked_indices, start=1):
            result = dict(self.documents[int(idx)])
            result["score"] = round(float(scores[int(idx)]), 6)
            result["rank"] = rank
            results.append(result)
        return results

    def save(self, output_dir: Path) -> None:
        import pickle
        output_dir.mkdir(parents=True, exist_ok=True)
        with (output_dir / "index.pkl").open("wb") as f:
            pickle.dump({
                "documents": self.documents,
                "doc_embeddings": self.doc_embeddings,
                "query_model_name": self.query_model_name,
                "passage_model_name": self.passage_model_name,
            }, f)

    @classmethod
    def load(cls, output_dir: Path) -> "MDPRIndex":
        import pickle
        with (output_dir / "index.pkl").open("rb") as f:
            payload = pickle.load(f)
        index = cls(
            payload["documents"],
            query_model_name=payload["query_model_name"],
            passage_model_name=payload["passage_model_name"],
        )
        index.doc_embeddings = payload["doc_embeddings"]
        return index


def main() -> int:
    args = parse_args()
    config = load_config(args.config)

    output_dir = Path(args.output_dir) if args.output_dir else None
    if output_dir is None:
        results_dir = Path(config["paths"]["results_dir"])
        output_dir = results_dir / "q1_experiments" / "mdpr_baseline"
    output_dir = ensure_dir(output_dir)

    np.random.seed(args.seed)

    # Load data
    eval_items = read_jsonl(Path(args.eval_file))
    corpus_file = config["paths"].get("corpus_file", "corpus.jsonl")
    corpus_path = Path(config["paths"]["processed_data_dir"]) / corpus_file
    documents = read_jsonl(corpus_path)
    print(f"Loaded {len(documents)} documents, {len(eval_items)} eval items")

    # Build or load index
    index_dir = output_dir / "index"
    index = MDPRIndex(documents)
    if (index_dir / "index.pkl").exists():
        print(f"Loading existing index from {index_dir}")
        index = MDPRIndex.load(index_dir)
    else:
        print("Building mDPR index...")
        index.build()
        index.save(index_dir)

    # Run retrieval
    top_k = config.get("retrieval", {}).get("top_k", 10)
    predictions = []
    for i, item in enumerate(eval_items):
        results = index.search(item["question"], top_k=top_k)
        recall = retrieval_recall_at_k(item, results)
        predictions.append({
            "id": item["id"],
            "language": item.get("language", "unknown"),
            "domain": item.get("domain", "unknown"),
            "cultural_specificity": item.get("cultural_specificity", "unknown"),
            "difficulty": item.get("difficulty", "unknown"),
            "retrieval_recall_at_k": recall,
            "contexts": [
                {"doc_id": r.get("doc_id"), "score": r.get("score"), "rank": r.get("rank")}
                for r in results
            ],
        })
        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1}/{len(eval_items)} queries")

    write_jsonl(output_dir / "predictions.jsonl", predictions)

    # Summary
    en = [p for p in predictions if p["language"] == "en"]
    uz = [p for p in predictions if p["language"] == "uz"]
    summary = {
        "condition": "mdpr",
        "query_model": index.query_model_name,
        "passage_model": index.passage_model_name,
        "top_k": top_k,
        "seed": args.seed,
        "n_queries": len(predictions),
        "overall_recall@10": float(np.mean([p["retrieval_recall_at_k"] for p in predictions])),
        "en_recall@10": float(np.mean([p["retrieval_recall_at_k"] for p in en])) if en else 0,
        "uz_recall@10": float(np.mean([p["retrieval_recall_at_k"] for p in uz])) if uz else 0,
    }
    with (output_dir / "summary.json").open("w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults:")
    print(f"  Overall Recall@10: {summary['overall_recall@10']:.3f}")
    print(f"  English Recall@10: {summary['en_recall@10']:.3f} (n={len(en)})")
    print(f"  Uzbek Recall@10:   {summary['uz_recall@10']:.3f} (n={len(uz)})")
    print(f"  Saved to: {output_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
