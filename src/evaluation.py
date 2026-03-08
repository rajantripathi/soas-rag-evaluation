from __future__ import annotations

from typing import Any

from src.retrieval import tokenize


def overlap_ratio(left: str, right: str) -> float:
    left_tokens = set(tokenize(left))
    right_tokens = set(tokenize(right))
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens)


def score_example(
    example: dict[str, Any],
    answer: str,
    contexts: list[dict[str, Any]],
) -> dict[str, float]:
    gold = example.get("gold_answer", "")
    context_text = " ".join(item.get("text", "") for item in contexts)
    answer_overlap = overlap_ratio(answer, gold) if gold else 0.0
    context_overlap = overlap_ratio(answer, context_text) if context_text else 0.0
    unsupported = 1.0 if answer and context_text and context_overlap < 0.25 else 0.0
    hallucination = 1.0 if answer and not contexts else unsupported
    grounded_score = round(max(answer_overlap, context_overlap), 4)
    return {
        "grounded_answer_score": grounded_score,
        "hallucination_rate": hallucination,
        "unsupported_claim_rate": unsupported,
    }


def retrieval_recall_at_k(example: dict[str, Any], contexts: list[dict[str, Any]]) -> float:
    gold_doc_ids = set(example.get("source_doc_ids", []))
    if not gold_doc_ids:
        return 0.0
    retrieved_ids = {context.get("doc_id") for context in contexts}
    return 1.0 if gold_doc_ids & retrieved_ids else 0.0
