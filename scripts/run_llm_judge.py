#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Dict, List

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils import ensure_dir, read_jsonl, write_jsonl


def build_parser():
    """Build argument parser."""
    parser = argparse.ArgumentParser(description="Run LLM-as-judge evaluation on RAG predictions.")
    parser.add_argument("--predictions", required=True, help="Path to predictions.jsonl from best experiment run")
    parser.add_argument("--output", default="results/eval_llm_judge/scores.jsonl", help="Output path for judge scores")
    parser.add_argument("--model", default="mistralai/Mistral-7B-Instruct-v0.3", help="Model to use for judging")
    parser.add_argument("--n-items", type=int, default=100, help="Number of items to judge")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--max-new-tokens", type=int, default=256, help="Max tokens for judge response")
    parser.add_argument("--temperature", type=float, default=0.1, help="Temperature for sampling")
    return parser


def select_judgement_subset(predictions: List[Dict], n_items: int = 100, seed: int = 42) -> List[Dict]:
    """Select a stratified subset of items for judging."""
    random.seed(seed)

    # Group by language and domain
    by_lang_domain: Dict[tuple, List[Dict]] = {}
    for pred in predictions:
        key = (pred.get("language"), pred.get("domain"))
        if key not in by_lang_domain:
            by_lang_domain[key] = []
        by_lang_domain[key].append(pred)

    selected = []

    # Select roughly 12-13 items per domain per language (4 domains * 2 languages * 12.5 = 100)
    target_per_cell = n_items // 8

    for (lang, domain), items in by_lang_domain.items():
        # Ensure mix of success and failure cases
        success = [p for p in items if p.get("retrieval_recall_at_k", 0) >= 1.0]
        failure = [p for p in items if p.get("retrieval_recall_at_k", 0) < 1.0]

        n_success = min(len(success), target_per_cell // 2)
        n_failure = min(len(failure), target_per_cell - n_success)

        selected.extend(random.sample(success, n_success))
        selected.extend(random.sample(failure, n_failure))

    # If we don't have enough, add more from any category
    if len(selected) < n_items:
        remaining = [p for p in predictions if p not in selected]
        selected.extend(random.sample(remaining, min(n_items - len(selected), len(remaining))))

    random.shuffle(selected)
    return selected[:n_items]


def construct_judge_prompt(item: Dict) -> str:
    """Construct a judge prompt for an item."""

    question = item.get("question", "")
    language = item.get("language", "")
    domain = item.get("domain", "")
    gold_answer = item.get("gold_answer", "")

    # Get retrieved context (top passage)
    contexts = item.get("contexts", [])
    if contexts and len(contexts) > 0:
        top_context = contexts[0].get("text", "No context retrieved")
    else:
        top_context = "No context retrieved"

    # Get system prediction
    prediction = item.get("prediction", "")

    prompt = f"""You are evaluating a retrieval-augmented question answering system for culturally grounded queries.

Question: {question}
Language: {language}
Domain: {domain}
Gold answer: {gold_answer}
Retrieved context (top passage): {top_context}
System answer: {prediction}

Score each dimension from 1 to 5:

retrieval_relevance: Is the retrieved passage relevant to answering the question? (1=completely irrelevant, 5=perfectly relevant)
answer_faithfulness: Is the system answer grounded in the retrieved passage without adding unsupported claims? (1=fabricated, 5=fully grounded)
answer_correctness: Does the system answer convey the same information as the gold answer? (1=completely wrong, 5=fully correct)
cultural_grounding: Does the answer appropriately reflect culturally specific knowledge? (1=no cultural awareness, 5=strong cultural grounding)

Respond ONLY with a JSON object, no other text:
{{"retrieval_relevance": N, "answer_faithfulness": N, "answer_correctness": N, "cultural_grounding": N, "reasoning": "brief explanation"}}"""

    return prompt


def parse_judge_response(response: str) -> Dict:
    """Parse judge response from LLM output."""
    try:
        # Try to extract JSON from response
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()

        result = json.loads(response)

        # Validate scores are 1-5
        for key in ["retrieval_relevance", "answer_faithfulness", "answer_correctness", "cultural_grounding"]:
            if key in result:
                result[key] = max(1, min(5, int(result[key])))

        return result

    except Exception as e:
        # If parsing fails, return null scores
        return {
            "retrieval_relevance": None,
            "answer_faithfulness": None,
            "answer_correctness": None,
            "cultural_grounding": None,
            "reasoning": f"Parse error: {str(e)}",
            "raw_response": response
        }


def main():
    """Main function."""
    args = build_parser().parse_args()

    # Load predictions
    print(f"Loading predictions from {args.predictions}")
    predictions = read_jsonl(args.predictions)

    # Select subset for judging
    print(f"Selecting {args.n_items} items for judging")
    selected = select_judgement_subset(predictions, args.n_items, args.seed)

    print(f"Selected {len(selected)} items:")
    print(f"  English: {sum(1 for s in selected if s.get('language') == 'en')}")
    print(f"  Uzbek: {sum(1 for s in selected if s.get('language') == 'uz')}")
    for domain in ["governance", "history", "institutions", "culture"]:
        print(f"  {domain}: {sum(1 for s in selected if s.get('domain') == domain)}")

    # Try to load model
    try:
        print(f"Loading model: {args.model}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

        tokenizer = AutoTokenizer.from_pretrained(args.model)
        model = AutoModelForCausalLM.from_pretrained(
            args.model,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        print("Model loaded successfully")

    except Exception as e:
        print(f"ERROR: Failed to load model: {e}")
        print("\nFalling back to prompt generation mode...")
        print("Writing prompts to file for offline scoring...")

        # Generate prompts for offline scoring
        output_dir = Path(args.output).parent
        ensure_dir(output_dir)

        prompts_file = output_dir / "llm_judge_prompts.jsonl"
        prompts_data = []

        for item in selected:
            prompt_text = construct_judge_prompt(item)
            prompts_data.append({
                "id": item.get("id"),
                "language": item.get("language"),
                "domain": item.get("domain"),
                "prompt": prompt_text
            })

        write_jsonl(prompts_file, prompts_data)
        print(f"\nPrompts written to: {prompts_file}")
        print("You can use these prompts with any LLM for offline scoring.")

        # Write dummy Slurm script for running later
        slurm_script = output_dir / "run_llm_juge_later.sbatch"
        with slurm_script.open("w") as f:
            f.write("""#!/bin/bash
#SBATCH --job-name=llm_judge
#SBATCH --output=logs/llm_judge_%j.out
#SBATCH --error=logs/llm_judge_%j.err
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --gres=gpu:1

set -euo pipefail
mkdir -p logs results/eval_llm_judge
module load cray-python/3.11.7 || true
source .venv/bin/activate

python scripts/run_llm_judge.py \\
  --predictions """ + args.predictions + """ \\
  --output results/eval_llm_judge/scores.jsonl \\
  --model """ + args.model + """ \\
  --n-items """ + str(args.n_items) + """
""")

        print(f"\nSlurm script written to: {slurm_script}")
        print(f"Submit with: sbatch {slurm_script}")

        return 0

    # Run inference
    results = []

    for i, item in enumerate(selected):
        if (i + 1) % 10 == 0:
            print(f"Processing item {i+1}/{len(selected)}")

        prompt = construct_judge_prompt(item)

        # Tokenise
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

        # Generate
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=args.max_new_tokens,
                temperature=args.temperature,
                do_sample=args.temperature > 0,
                pad_token_id=tokenizer.eos_token_id
            )

        # Decode response
        response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)

        # Parse response
        scores = parse_judge_response(response)

        # Create result record
        result = {
            "id": item.get("id"),
            "language": item.get("language"),
            "domain": item.get("domain"),
            "question": item.get("question"),
            "gold_answer": item.get("gold_answer"),
            "prediction": item.get("prediction"),
            "retrieval_recall_at_k": item.get("retrieval_recall_at_k", 0),
            "judge_scores": scores,
            "raw_response": response if scores.get("retrieval_relevance") is None else None
        }

        results.append(result)

    # Write results
    output_path = Path(args.output)
    ensure_dir(output_path.parent)
    write_jsonl(output_path, results)

    print(f"\nResults written to: {args.output}")
    print(f"Judge {len(results)} items")

    # Print summary statistics
    valid_scores = [r for r in results if r["judge_scores"].get("retrieval_relevance") is not None]
    if valid_scores:
        print(f"\nValid scores: {len(valid_scores)}/{len(results)}")

        for dim in ["retrieval_relevance", "answer_faithfulness", "answer_correctness", "cultural_grounding"]:
            scores = [r["judge_scores"][dim] for r in valid_scores]
            mean = np.mean(scores)
            print(f"  {dim}: {mean:.2f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
