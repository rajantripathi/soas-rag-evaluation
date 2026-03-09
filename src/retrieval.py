from __future__ import annotations

import math
import pickle
import re
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np


TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text or "")]


class SimpleVectorIndex:
    def __init__(self, documents: list[dict[str, Any]]) -> None:
        self.documents = documents
        self.doc_vectors: list[dict[str, float]] = []
        self.idf: dict[str, float] = {}

    def build(self) -> None:
        doc_freq: Counter[str] = Counter()
        tokenized_docs: list[list[str]] = []
        for document in self.documents:
            tokens = tokenize(document.get("text", ""))
            tokenized_docs.append(tokens)
            doc_freq.update(set(tokens))

        total_docs = max(len(tokenized_docs), 1)
        self.idf = {
            term: math.log((1 + total_docs) / (1 + freq)) + 1.0
            for term, freq in doc_freq.items()
        }
        self.doc_vectors = [self._vectorize_tokens(tokens) for tokens in tokenized_docs]

    def _vectorize_tokens(self, tokens: list[str]) -> dict[str, float]:
        counts = Counter(tokens)
        total = max(sum(counts.values()), 1)
        return {
            term: (count / total) * self.idf.get(term, 1.0)
            for term, count in counts.items()
        }

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        query_vector = self._vectorize_tokens(tokenize(query))
        scored: list[tuple[float, dict[str, Any]]] = []
        for vector, document in zip(self.doc_vectors, self.documents):
            score = cosine_similarity(query_vector, vector)
            if score > 0:
                scored.append((score, document))
        scored.sort(key=lambda item: item[0], reverse=True)
        results = []
        for rank, (score, document) in enumerate(scored[:top_k], start=1):
            result = dict(document)
            result["score"] = round(score, 6)
            result["rank"] = rank
            results.append(result)
        return results

    def save(self, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        with (output_dir / "index.pkl").open("wb") as handle:
            pickle.dump(
                {
                    "documents": self.documents,
                    "doc_vectors": self.doc_vectors,
                    "idf": self.idf,
                },
                handle,
            )

    @classmethod
    def load(cls, output_dir: Path) -> "SimpleVectorIndex":
        with (output_dir / "index.pkl").open("rb") as handle:
            payload = pickle.load(handle)
        index = cls(payload["documents"])
        index.doc_vectors = payload["doc_vectors"]
        index.idf = payload["idf"]
        return index


class BM25Index:
    def __init__(self, documents: list[dict[str, Any]], k1: float = 1.5, b: float = 0.75) -> None:
        self.documents = documents
        self.k1 = k1
        self.b = b
        self.doc_tokens: list[list[str]] = []
        self.doc_term_freqs: list[Counter[str]] = []
        self.doc_lengths: list[int] = []
        self.avg_doc_length: float = 0.0
        self.idf: dict[str, float] = {}

    def build(self) -> None:
        doc_freq: Counter[str] = Counter()
        for document in self.documents:
            tokens = tokenize(document.get("text", ""))
            term_freqs = Counter(tokens)
            self.doc_tokens.append(tokens)
            self.doc_term_freqs.append(term_freqs)
            self.doc_lengths.append(len(tokens))
            doc_freq.update(term_freqs.keys())

        total_docs = max(len(self.documents), 1)
        self.avg_doc_length = sum(self.doc_lengths) / total_docs if self.doc_lengths else 0.0
        self.idf = {
            term: math.log(1.0 + ((total_docs - freq + 0.5) / (freq + 0.5)))
            for term, freq in doc_freq.items()
        }

    def _score(self, query_tokens: list[str], idx: int) -> float:
        if not query_tokens:
            return 0.0
        score = 0.0
        doc_length = self.doc_lengths[idx] if self.doc_lengths else 0
        norm = self.k1 * (1.0 - self.b + self.b * (doc_length / (self.avg_doc_length or 1.0)))
        term_freqs = self.doc_term_freqs[idx]
        for term in query_tokens:
            freq = term_freqs.get(term, 0)
            if freq <= 0:
                continue
            numerator = freq * (self.k1 + 1.0)
            denominator = freq + norm
            score += self.idf.get(term, 0.0) * (numerator / (denominator or 1.0))
        return score

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        query_tokens = tokenize(query)
        scored: list[tuple[float, dict[str, Any]]] = []
        for idx, document in enumerate(self.documents):
            score = self._score(query_tokens, idx)
            if score > 0:
                scored.append((score, document))
        scored.sort(key=lambda item: item[0], reverse=True)
        results = []
        for rank, (score, document) in enumerate(scored[:top_k], start=1):
            result = dict(document)
            result["score"] = round(score, 6)
            result["rank"] = rank
            results.append(result)
        return results

    def save(self, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        with (output_dir / "index.pkl").open("wb") as handle:
            pickle.dump(
                {
                    "documents": self.documents,
                    "k1": self.k1,
                    "b": self.b,
                    "doc_tokens": self.doc_tokens,
                    "doc_term_freqs": self.doc_term_freqs,
                    "doc_lengths": self.doc_lengths,
                    "avg_doc_length": self.avg_doc_length,
                    "idf": self.idf,
                },
                handle,
            )

    @classmethod
    def load(cls, output_dir: Path) -> "BM25Index":
        with (output_dir / "index.pkl").open("rb") as handle:
            payload = pickle.load(handle)
        index = cls(payload["documents"], k1=payload["k1"], b=payload["b"])
        index.doc_tokens = payload["doc_tokens"]
        index.doc_term_freqs = payload["doc_term_freqs"]
        index.doc_lengths = payload["doc_lengths"]
        index.avg_doc_length = payload["avg_doc_length"]
        index.idf = payload["idf"]
        return index


class EmbeddingVectorIndex:
    def __init__(self, documents: list[dict[str, Any]], model_name: str) -> None:
        self.documents = documents
        self.model_name = model_name
        self.doc_embeddings: np.ndarray | None = None
        self._model = None
        self._doc_id_to_idx: dict[str, int] = {
            str(document["doc_id"]): idx for idx, document in enumerate(documents)
        }

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name, local_files_only=True)
        return self._model

    def build(self) -> None:
        model = self._load_model()
        texts = [document.get("text", "") for document in self.documents]
        self.doc_embeddings = np.asarray(
            model.encode(texts, normalize_embeddings=True, show_progress_bar=False),
            dtype=np.float32,
        )

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        if self.doc_embeddings is None or len(self.documents) == 0:
            return []
        query_embedding = self.encode_query(query)
        scores = self.doc_embeddings @ query_embedding
        ranked_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for rank, idx in enumerate(ranked_indices, start=1):
            result = dict(self.documents[int(idx)])
            result["score"] = round(float(scores[int(idx)]), 6)
            result["rank"] = rank
            results.append(result)
        return results

    def encode_query(self, query: str) -> np.ndarray:
        model = self._load_model()
        return np.asarray(
            model.encode([query], normalize_embeddings=True, show_progress_bar=False)[0],
            dtype=np.float32,
        )

    def score_doc_ids(self, query_embedding: np.ndarray, doc_ids: list[str]) -> list[tuple[float, dict[str, Any]]]:
        if self.doc_embeddings is None:
            return []
        scored: list[tuple[float, dict[str, Any]]] = []
        for doc_id in doc_ids:
            idx = self._doc_id_to_idx.get(str(doc_id))
            if idx is None:
                continue
            score = float(self.doc_embeddings[idx] @ query_embedding)
            scored.append((score, self.documents[idx]))
        scored.sort(key=lambda item: item[0], reverse=True)
        return scored

    def save(self, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        with (output_dir / "index.pkl").open("wb") as handle:
            pickle.dump(
                {
                    "documents": self.documents,
                    "doc_embeddings": self.doc_embeddings,
                    "model_name": self.model_name,
                },
                handle,
            )

    @classmethod
    def load(cls, output_dir: Path) -> "EmbeddingVectorIndex":
        with (output_dir / "index.pkl").open("rb") as handle:
            payload = pickle.load(handle)
        index = cls(payload["documents"], payload["model_name"])
        index.doc_embeddings = payload["doc_embeddings"]
        return index


class HybridIndex:
    def __init__(
        self,
        documents: list[dict[str, Any]],
        model_name: str,
        bm25_k1: float = 1.5,
        bm25_b: float = 0.75,
    ) -> None:
        self.documents = documents
        self.model_name = model_name
        self.bm25_k1 = bm25_k1
        self.bm25_b = bm25_b
        self.bm25 = BM25Index(documents, k1=bm25_k1, b=bm25_b)
        self.embedding = EmbeddingVectorIndex(documents, model_name=model_name)

    def build(self) -> None:
        self.bm25.build()
        self.embedding.build()

    @classmethod
    def from_components(cls, bm25: BM25Index, embedding: EmbeddingVectorIndex) -> "HybridIndex":
        index = cls(bm25.documents, model_name=embedding.model_name, bm25_k1=bm25.k1, bm25_b=bm25.b)
        index.bm25 = bm25
        index.embedding = embedding
        return index

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        bm25_results = self.bm25.search(query, top_k=top_k)
        vector_results = self.embedding.search(query, top_k=top_k)
        merged_doc_ids: list[str] = []
        seen: set[str] = set()
        for result in bm25_results + vector_results:
            doc_id = str(result["doc_id"])
            if doc_id in seen:
                continue
            seen.add(doc_id)
            merged_doc_ids.append(doc_id)

        if not merged_doc_ids:
            return []

        query_embedding = self.embedding.encode_query(query)
        reranked = self.embedding.score_doc_ids(query_embedding, merged_doc_ids)[:top_k]
        results = []
        for rank, (score, document) in enumerate(reranked, start=1):
            result = dict(document)
            result["score"] = round(score, 6)
            result["rank"] = rank
            results.append(result)
        return results

    def save(self, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        with (output_dir / "index.pkl").open("wb") as handle:
            pickle.dump(
                {
                    "documents": self.documents,
                    "model_name": self.model_name,
                    "bm25_k1": self.bm25_k1,
                    "bm25_b": self.bm25_b,
                    "bm25_doc_tokens": self.bm25.doc_tokens,
                    "bm25_doc_term_freqs": self.bm25.doc_term_freqs,
                    "bm25_doc_lengths": self.bm25.doc_lengths,
                    "bm25_avg_doc_length": self.bm25.avg_doc_length,
                    "bm25_idf": self.bm25.idf,
                    "doc_embeddings": self.embedding.doc_embeddings,
                },
                handle,
            )

    @classmethod
    def load(cls, output_dir: Path) -> "HybridIndex":
        with (output_dir / "index.pkl").open("rb") as handle:
            payload = pickle.load(handle)
        index = cls(
            payload["documents"],
            model_name=payload["model_name"],
            bm25_k1=payload["bm25_k1"],
            bm25_b=payload["bm25_b"],
        )
        index.bm25.doc_tokens = payload["bm25_doc_tokens"]
        index.bm25.doc_term_freqs = payload["bm25_doc_term_freqs"]
        index.bm25.doc_lengths = payload["bm25_doc_lengths"]
        index.bm25.avg_doc_length = payload["bm25_avg_doc_length"]
        index.bm25.idf = payload["bm25_idf"]
        index.embedding.doc_embeddings = payload["doc_embeddings"]
        return index


def build_index(documents: list[dict[str, Any]], backend: str, model_name: str | None = None):
    if backend == "simple_vector":
        index = SimpleVectorIndex(documents)
    elif backend == "bm25":
        index = BM25Index(documents)
    elif backend == "embedding":
        if not model_name:
            raise ValueError("Embedding backend requires retrieval.model_name")
        index = EmbeddingVectorIndex(documents, model_name=model_name)
    elif backend == "hybrid":
        if not model_name:
            raise ValueError("Hybrid backend requires retrieval.model_name")
        index = HybridIndex(documents, model_name=model_name)
    else:
        raise ValueError(f"Unsupported retrieval backend: {backend}")
    index.build()
    return index


def load_index(output_dir: Path, backend: str):
    if backend == "simple_vector":
        return SimpleVectorIndex.load(output_dir)
    if backend == "bm25":
        return BM25Index.load(output_dir)
    if backend == "embedding":
        return EmbeddingVectorIndex.load(output_dir)
    if backend == "hybrid":
        return HybridIndex.load(output_dir)
    raise ValueError(f"Unsupported retrieval backend: {backend}")


def cosine_similarity(left: dict[str, float], right: dict[str, float]) -> float:
    numerator = 0.0
    for key, value in left.items():
        numerator += value * right.get(key, 0.0)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)
