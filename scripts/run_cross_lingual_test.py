import sys
sys.path.insert(0, "/home/u6ef/rajantripathi.u6ef/soas_rag_eval")

from pathlib import Path
import json
from src.retrieval import EmbeddingVectorIndex

# Load test questions
test_path = Path("/home/u6ef/rajantripathi.u6ef/soas_rag_eval/data/eval/cross_lingual_test.jsonl")
test_questions = []

with open(test_path, "r") as f:
    for line in f:
        line = line.strip()
        if line:
            test_questions.append(json.loads(line))

print(f"Loaded {len(test_questions)} test questions")

# Load indexes
en_index_path = Path("/home/u6ef/rajantripathi.u6ef/soas_rag_eval/data/indexes/cross_lingual_english_only_index")
uz_index_path = Path("/home/u6ef/rajantripathi.u6ef/soas_rag_eval/data/indexes/cross_lingual_uzbek_only_index")

en_index = EmbeddingVectorIndex.load(en_index_path)
uz_index = EmbeddingVectorIndex.load(uz_index_path)

print(f"Loaded English index: {len(en_index.documents)} docs")
print(f"Loaded Uzbek index: {len(uz_index.documents)} docs")

# List available documents
print("\\n=== English corpus ===")
for doc in en_index.documents:
    t = doc.get("title", "Unknown")
    print(f"  - {t}")

print("\\n=== Uzbek corpus (first 10) ===")
for doc in uz_index.documents[:10]:
    t = doc.get("title", "Unknown")
    print(f"  - {t}")

# Define test conditions
conditions = [
    ("xl_uz_baseline", uz_index, "Uzbek Q -> Uzbek Corpus"),
    ("xl_en_baseline", en_index, "English Q -> English Corpus"),
    ("xl_uz_on_en", en_index, "Uzbek Q -> English Corpus"),
    ("xl_en_on_uz", uz_index, "English Q -> Uzbek Corpus"),
]

# Run evaluation
results = {}
details = {}
for prefix, index, cond_name in conditions:
    matching_questions = [q for q in test_questions if q["id"].startswith(prefix)]
    
    correct = 0
    total = len(matching_questions)
    condition_details = []
    
    for q in matching_questions:
        query = q["question"]
        target_title = q["target_title"]
        
        results_list = index.search(query, top_k=5)
        retrieved_titles = [r.get("title", "") for r in results_list]
        
        is_correct = target_title in retrieved_titles
        if is_correct:
            correct += 1
        
        condition_details.append({
            "question": query,
            "target": target_title,
            "retrieved": retrieved_titles,
            "correct": is_correct
        })
    
    accuracy = correct / total if total > 0 else 0.0
    results[prefix] = {
        "correct": correct,
        "total": total,
        "accuracy": accuracy,
        "name": cond_name
    }
    details[prefix] = condition_details
    pct = accuracy * 100
    print(f"\\n{cond_name}: {correct}/{total} = {pct:.1f}%")

print("\\n=== CROSS-LINGUAL RESULTS SUMMARY ===")
print("| Condition | Accuracy |")
print("|-----------|----------|")
for key, result in results.items():
    pct = result["accuracy"] * 100
    cond_name = result["name"]
    print(f"| {cond_name} | {pct:.1f}% |")

# Save results
results_path = Path("/home/u6ef/rajantripathi.u6ef/soas_rag_eval/results/cross_lingual/summary.json")
results_path.parent.mkdir(parents=True, exist_ok=True)
with open(results_path, "w") as f:
    json.dump({"summary": results, "details": details}, f, indent=2)
print(f"\\nResults saved to: {results_path}")
