from __future__ import annotations

from typing import Any


def generate_answer(
    question: str,
    contexts: list[dict[str, Any]],
    mode: str = "stub",
    prompt_style: str = "baseline",
) -> str:
    if mode != "stub":
        raise ValueError(f"Unsupported generation mode for smoke path: {mode}")

    if contexts:
        top_text = contexts[0].get("text", "").strip()
        if prompt_style == "grounded":
            if top_text:
                return top_text.split(".")[0].strip() + "."
            return "Insufficient evidence in retrieved context."
        if top_text:
            return top_text[:240].strip()
    return f"No retrieved evidence available for: {question}"
