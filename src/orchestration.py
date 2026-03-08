from __future__ import annotations

from pathlib import Path
from typing import Any

from src.evaluation import retrieval_recall_at_k, score_example
from src.generation import generate_answer
from src.retrieval import SimpleVectorIndex
from src.utils import (
    append_log,
    config_hash,
    ensure_dir,
    git_commit,
    make_run_dir,
    write_csv,
    write_jsonl,
)


def run_evaluation(
    config: dict[str, Any],
    eval_examples: list[dict[str, Any]],
    index: SimpleVectorIndex | None,
    results_root: Path,
) -> Path:
    run_dir = make_run_dir(results_root, "eval", config)
    log_path = ensure_dir(run_dir / "logs") / "run.log"
    append_log(log_path, f"config_hash={config_hash(config)} git_commit={git_commit()}")

    retrieval_mode = config["experiment"]["retrieval_mode"]
    prompt_style = config["experiment"]["prompt_style"]
    generation_mode = config["generation"]["backend"]
    top_k = int(config["retrieval"].get("top_k", 3))

    outputs: list[dict[str, Any]] = []
    aggregate = {
        "examples": 0,
        "grounded_answer_score": 0.0,
        "hallucination_rate": 0.0,
        "unsupported_claim_rate": 0.0,
        "retrieval_recall_at_k": 0.0,
    }

    for example in eval_examples:
        contexts = []
        if retrieval_mode == "vector" and index is not None:
            contexts = index.search(example["question"], top_k=top_k)
        answer = generate_answer(
            question=example["question"],
            contexts=contexts,
            mode=generation_mode,
            prompt_style=prompt_style,
        )
        metrics = score_example(example, answer, contexts)
        recall = retrieval_recall_at_k(example, contexts) if contexts else 0.0
        row = dict(example)
        row.update(
            {
                "prediction": answer,
                "retrieved_contexts": contexts,
                "retrieval_recall_at_k": recall,
                **metrics,
            }
        )
        outputs.append(row)
        aggregate["examples"] += 1
        for key in ("grounded_answer_score", "hallucination_rate", "unsupported_claim_rate"):
            aggregate[key] += metrics[key]
        aggregate["retrieval_recall_at_k"] += recall

    total = max(aggregate["examples"], 1)
    metric_row = {
        "run_dir": str(run_dir),
        "config_hash": config_hash(config),
        "git_commit": git_commit(),
        "examples": aggregate["examples"],
        "grounded_answer_score": round(aggregate["grounded_answer_score"] / total, 4),
        "hallucination_rate": round(aggregate["hallucination_rate"] / total, 4),
        "unsupported_claim_rate": round(aggregate["unsupported_claim_rate"] / total, 4),
        "retrieval_recall_at_k": round(aggregate["retrieval_recall_at_k"] / total, 4),
    }

    write_jsonl(run_dir / "predictions.jsonl", outputs)
    write_csv(run_dir / "metrics.csv", [metric_row])
    with (run_dir / "summary.md").open("w", encoding="utf-8") as handle:
        handle.write("# Smoke Evaluation Summary\n\n")
        for key, value in metric_row.items():
            handle.write(f"- {key}: {value}\n")
    append_log(log_path, f"wrote_results={run_dir}")
    return run_dir
