#!/usr/bin/env python3
"""Run cross-lingual RAG evaluation to measure cultural bias."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.retrieval import EmbeddingVectorIndex, load_index
from src.utils import read_jsonl


def load_questions(eval_file, target_language):
    questions = []
    for item in read_jsonl(eval_file):
        if item.get("language") == target_language:
            questions.append(item)
    return questions


def run_evaluation(index_path, questions, top_k=5):
    # Load index using the module function
    index = load_index(Path(index_path), backend="embedding")
    
    results = {"total": len(questions), "correct": 0, "results": []}
    
    for qa in questions:
        query = qa.get("question", qa.get("query", ""))
        gold_ids = set(qa.get("source_doc_ids", [qa.get("source_title", "")]))
        
        # Use search method
        hits = index.search(query, top_k=top_k)
        
        # Extract doc_ids from results
        retrieved_ids = set()
        for hit in hits:
            if "doc_id" in hit:
                retrieved_ids.add(hit["doc_id"])
            elif "source" in hit:
                retrieved_ids.add(hit["source"])
        
        is_correct = bool(gold_ids & retrieved_ids)
        if is_correct:
            results["correct"] += 1
        
        results["results"].append({
            "id": qa.get("id"),
            "question": query[:100],
            "language": qa.get("language"),
            "correct": is_correct,
            "gold_docs": list(gold_ids),
            "retrieved_docs": list(retrieved_ids)[:3]
        })
    
    results["accuracy"] = results["correct"] / results["total"] if results["total"] > 0 else 0
    return results


def main():
    base = Path("/home/u6ef/rajantripathi.u6ef/soas_rag_eval")
    data_dir = base / "data"
    output_dir = base / "results" / "cross_lingual"
    output_dir.mkdir(exist_ok=True, parents=True)
    
    eval_file = data_dir / "eval" / "manual_eval_v5.jsonl"
    
    experiments = [
        ("cross_lingual_english_only_index", "uz", "uzbek_questions_on_english_corpus"),
        ("cross_lingual_uzbek_only_index", "en", "english_questions_on_uzbek_corpus"),
    ]
    
    all_results = {}
    
    for index_name, lang, exp_name in experiments:
        print("=" * 60)
        print("Experiment: " + exp_name)
        print("=" * 60)
        
        index_path = str(data_dir / "indexes" / index_name)
        questions = load_questions(str(eval_file), lang)
        
        print("Index: " + index_path)
        print("Questions: {} ({})".format(len(questions), lang))
        
        results = run_evaluation(index_path, questions)
        
        print()
        print("Results:")
        print("  Accuracy: {:.1%}".format(results["accuracy"]))
        print("  Correct: {}/{}".format(results["correct"], results["total"]))
        
        output_file = output_dir / "{}.json".format(exp_name)
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print("  Saved: " + str(output_file))
        
        all_results[exp_name] = {
            "accuracy": results["accuracy"],
            "correct": results["correct"],
            "total": results["total"]
        }
    
    print()
    print("=" * 60)
    print("CROSS-LINGUAL EVALUATION SUMMARY")
    print("=" * 60)
    print()
    print("Cultural Bias Analysis:")
    for exp_name, metrics in all_results.items():
        print("  " + exp_name + ":")
        print("    Accuracy: {:.1%} ({}/{})".format(
            metrics["accuracy"], metrics["correct"], metrics["total"]))
    
    summary_file = output_dir / "cross_lingual_summary.json"
    with open(summary_file, "w") as f:
        json.dump(all_results, f, indent=2)
    print()
    print("Summary saved: " + str(summary_file))


if __name__ == "__main__":
    main()
