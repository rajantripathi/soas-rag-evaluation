#!/usr/bin/env python3
"""BGE-M3 baseline experiment for Q1 paper.

BGE-M3 (BAAI/bge-m3) is a multilingual embedding model specifically designed
for multilingual retrieval. This script runs retrieval with BGE-M3 on both
English and Uzbek queries and reports all standard IR metrics.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.retrieval import load_index
from src.evaluation import retrieval_recall_at_k
from src.utils import ensure_dir, load_config, read_jsonl, write_jsonl


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run BGE-M3 baseline retrieval experiment.")
    p.add_argument("--config", required=True, help="Path to YAML config")
    p.add_argument("--eval-file", default="data/eval/manual_eval_v5.jsonl")
    p.add_argument("--output-dir", default=None, help="Override output directory")
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


class BGE_M3_Index:
    """BGE-M3 dense retrieval index.

    Uses FlagEmbedding's BGE-M3 model for multilingual dense retrieval.
    Falls back to sentence-transformers if FlagEmbedding is not available.
    """

    def __init__(self, documents: list[dict[str, Any]], model_name: str = "BAAI/bge-m3") -> None:
        self.documents = documents
        self.model_name = model_name
        self.doc_embeddings: np.ndarray | None = None
        self._model = None
        self._doc_id_to_idx: dict[str, int] = {
            str(doc["doc_id"]): idx for idx, doc in enumerate(documents)
        }

    def _load_model(self):
        if self._model is not None:
            return self._model

        try:
            from FlagEmbedding import BGEM3FlagModel
            self._model = BGEM3FlagModel(
                self.model_name,
                use_fp16=True,
            )
        except ImportError:
            print("FlagEmbedding not available, falling back to sentence-transformers")
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def _encode(self, texts: list[str], is_query: bool = False) -> np.ndarray:
        model = self._load_model()

        # Try FlagEmbedding API first
        try:
            from FlagEmbedding import BGEM3FlagModel
            if isinstance(model, BGEM3FlagModel):
                output = model.encode(texts, return_dense=True, return_sparse=False, return_colbert_vecs=False)
                embeddings = output["dense_vecs"]
                norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
                return (embeddings / norms).astype(np.float32)
        except (ImportError, AttributeError, KeyError):
            pass

        # Fallback: sentence-transformers
        from sentence_transformers import SentenceTransformer
        if isinstance(model, SentenceTransformer):
            return np.asarray(
                model.encode(texts, normalize_embeddings=True, show_progress_bar=True),
                dtype=np.float32,
            )

        raise RuntimeError("Could not encode with any available model")

    def build(self) -> None:
        texts = [doc.get("text", "") for doc in self.documents]
        print(f"Encoding {len(texts)} documents with {self.model_name}...")
        self.doc_embeddings = self._encode(texts)
        print(f"Encoding complete. Shape: {self.doc_embeddings.shape}")

    def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        if self.doc_embeddings is None or len(self.documents) == 0:
            return []
        query_embedding = self._encode([query])[0]
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
        output_dir.mkdir(parents=True, exist_ok=True)
        with (output_dir / "index.pkl").open("wb") as f:
            import pickle
            pickle.dump({
                "documents": self.documents,
                "doc_embeddings": self.doc_embeddings,
                "model_name": self.model_name,
            }, f)

    @classmethod
    def load(cls, output_dir: Path) -> "BGE_M3_Index":
        import pickle
        with (output_dir / "index.pkl").open("rb") as f:
            payload = pickle.load(f)
        index = cls(payload["documents"], model_name=payload["model_name"])
        index.doc_embeddings = payload["doc_embeddings"]
        return index


def run_experiment(
    config: dict,
    eval_items: list[dict[str, Any]],
    corpus_path: Path,
    output_dir: Path,
    seed: int = 42,
) -> Path:
    """Run BGE-M3 retrieval experiment."""
    np.random.seed(seed)

    # Load corpus
    print(f"Loading corpus from {corpus_path}...")
    documents = read_jsonl(corpus_path)
    print(f"Loaded {len(documents)} documents")

    # Build or load index
    index_dir = output_dir / "index"
    index = BGE_M3_Index(documents)
    if (index_dir / "index.pkl").exists():
        print(f"Loading existing index from {index_dir}")
        index = BGE_M3_Index.load(index_dir)
    else:
        print("Building BGE-M3 index...")
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
            "contexts": [{"doc_id": r.get("doc_id"), "score": r.get("score"), "rank": r.get("rank")} for r in results],
        })
        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1}/{len(eval_items)} queries")

    # Save predictions
    predictions_file = output_dir / "predictions.jsonl"
    write_jsonl(predictions_file, predictions)

    # Compute summary
    en_preds = [p for p in predictions if p["language"] == "en"]
    uz_preds = [p for p in predictions if p["language"] == "uz"]
    overall_recall = np.mean([p["retrieval_recall_at_k"] for p in predictions])
    en_recall = np.mean([p["retrieval_recall_at_k"] for p in en_preds]) if en_preds else 0
    uz_recall = np.mean([p["retrieval_recall_at_k"] for p in uz_preds]) if uz_preds else 0

    summary = {
        "condition": "bge_m3",
        "model": "BAAI/bge-m3",
        "corpus": str(corpus_path),
        "top_k": top_k,
        "seed": seed,
        "n_queries": len(predictions),
        "overall_recall@10": float(overall_recall),
        "en_recall@10": float(en_recall),
        "uz_recall@10": float(uz_recall),
    }

    with (output_dir / "summary.json").open("w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults:")
    print(f"  Overall Recall@10: {overall_recall:.3f}")
    print(f"  English Recall@10: {en_recall:.3f} (n={len(en_preds)})")
    print(f"  Uzbek Recall@10:   {uz_recall:.3f} (n={len(uz_preds)})")
    print(f"  Saved to: {output_dir}")

    return output_dir


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    output_dir = Path(args.output_dir) if args.output_dir else None

    if output_dir is None:
        results_dir = Path(config["paths"]["results_dir"])
        output_dir = results_dir / "q1_experiments" / "bge_m3_baseline"

    output_dir = ensure_dir(output_dir)

    eval_items = read_jsonl(Path(args.eval_file))
    corpus_file = config["paths"].get("corpus_file", "corpus.jsonl")
    corpus_path = Path(config["paths"]["processed_data_dir"]) / corpus_file

    run_experiment(config, eval_items, corpus_path, output_dir, args.seed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
