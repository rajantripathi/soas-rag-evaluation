from __future__ import annotations

import math
import pickle
import re
from collections import Counter
from pathlib import Path
from typing import Any


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


def cosine_similarity(left: dict[str, float], right: dict[str, float]) -> float:
    numerator = 0.0
    for key, value in left.items():
        numerator += value * right.get(key, 0.0)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)
