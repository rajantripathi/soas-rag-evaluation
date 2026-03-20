import sys
sys.path.insert(0, "/home/u6ef/rajantripathi.u6ef/soas_rag_eval")

from pathlib import Path
import json
from src.retrieval import EmbeddingVectorIndex
import numpy as np

# Load test questions
test_path = Path("/home/u6ef/rajantripathi.u6ef/soas_rag_eval/data/eval/cross_lingual_robust_test.jsonl")
test_questions = []

with open(test_path, "r") as f:
    for line in f:
        if line.strip():
            test_questions.append(json.loads(line))

print("Loaded {} test questions".format(len(test_questions)))

# Load indexes
en_index_path = Path("/home/u6ef/rajantripathi.u6ef/soas_rag_eval/data/indexes/cross_lingual_english_robust_index")
uz_index_path = Path("/home/u6ef/rajantripathi.u6ef/soas_rag_eval/data/indexes/cross_lingual_uzbek_only_index")

en_index = EmbeddingVectorIndex.load(en_index_path)
uz_index = EmbeddingVectorIndex.load(uz_index_path)

print("Loaded English index: {} docs".format(len(en_index.documents)))
print("Loaded Uzbek index: {} docs".format(len(uz_index.documents)))

# Define test conditions
conditions = [
    ("uz_base", uz_index, "Uzbek Q -> Uzbek Corpus"),
    ("en_base", en_index, "English Q -> English Corpus"),
    ("uz_on_en", en_index, "Uzbek Q -> English Corpus"),
    ("en_on_uz", uz_index, "English Q -> Uzbek Corpus"),
]

# Run evaluation
results = {}
by_domain = {}
by_qtype = {}
details = {}

for prefix, index, cond_name in conditions:
    matching_questions = [q for q in test_questions if q["id"].startswith(prefix)]
    
    correct = 0
    total = len(matching_questions)
    condition_details = []
    
    for q in matching_questions:
        query = q["q"]
        target_title = q["tt"]
        domain = q["d"]
        qtype = q["qt"]
        
        results_list = index.search(query, top_k=5)
        retrieved_titles = [r.get("title", "") for r in results_list]
        
        is_correct = target_title in retrieved_titles
        if is_correct:
            correct += 1
        
        # Track by domain and question type
        key = (prefix, domain)
        if key not in by_domain:
            by_domain[key] = [0, 0]
        by_domain[key][0] += is_correct
        by_domain[key][1] += 1
        
        key2 = (prefix, qtype)
        if key2 not in by_qtype:
            by_qtype[key2] = [0, 0]
        by_qtype[key2][0] += is_correct
        by_qtype[key2][1] += 1
        
        condition_details.append({
            "id": q["id"],
            "question": query,
            "target": target_title,
            "retrieved": retrieved_titles,
            "correct": is_correct,
            "domain": domain,
            "qtype": qtype
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
    print("{}: {}/{} = {:.1f}%".format(cond_name, correct, total, pct))

# Calculate 95% confidence intervals using Wilson score interval
def wilson_interval(correct, total, confidence=0.95):
    if total == 0:
        return (0, 0)
    from math import sqrt
    z = 1.96  # 95% confidence
    p = correct / total
    denominator = 1 + z**2 / total
    center = (p + z**2 / (2 * total)) / denominator
    margin = z * sqrt(p * (1 - p) / total + z**2 / (4 * total**2)) / denominator
    return (max(0, center - margin), min(1, center + margin))

print("\n=== RESULTS WITH 95% CONFIDENCE INTERVALS ===")
print("| Condition | Accuracy | 95% CI |")
print("|-----------|----------|--------|")
for key, result in results.items():
    acc = result["accuracy"]
    ci_low, ci_high = wilson_interval(result["correct"], result["total"])
    print("| {} | {:.1f}% | [{:.1f}%, {:.1f}%] |".format(
        result["name"], acc * 100, ci_low * 100, ci_high * 100))

print("\n=== BY DOMAIN (Cross-lingual only) ===")
print("| Domain | UZ->EN | EN->UZ |")
print("|--------|--------|--------|")
domains = set([k[1] for k in by_domain.keys()])
for d in sorted(domains):
    uz_en = by_domain.get(("uz_on_en", d), [0, 0])
    en_uz = by_domain.get(("en_on_uz", d), [0, 0])
    uz_acc = uz_en[0] / uz_en[1] * 100 if uz_en[1] > 0 else 0
    en_acc = en_uz[0] / en_uz[1] * 100 if en_uz[1] > 0 else 0
    print("| {} | {}/{} ({:.0f}%) | {}/{} ({:.0f}%) |".format(
        d, uz_en[0], uz_en[1], uz_acc, en_uz[0], en_uz[1], en_acc))

print("\n=== BY QUESTION TYPE (Cross-lingual only) ===")
print("| Type | UZ->EN | EN->UZ |")
print("|------|--------|--------|")
qtypes = set([k[1] for k in by_qtype.keys()])
for qt in sorted(qtypes):
    uz_en = by_qtype.get(("uz_on_en", qt), [0, 0])
    en_uz = by_qtype.get(("en_on_uz", qt), [0, 0])
    uz_acc = uz_en[0] / uz_en[1] * 100 if uz_en[1] > 0 else 0
    en_acc = en_uz[0] / en_uz[1] * 100 if en_uz[1] > 0 else 0
    print("| {} | {}/{} ({:.0f}%) | {}/{} ({:.0f}%) |".format(
        qt, uz_en[0], uz_en[1], uz_acc, en_uz[0], en_uz[1], en_acc))

# Save results
results_path = Path("/home/u6ef/rajantripathi.u6ef/soas_rag_eval/results/cross_lingual/robust_summary.json")
results_path.parent.mkdir(parents=True, exist_ok=True)

output = {
    "summary": results,
    "confidence_intervals": {
        key: {
            "accuracy": result["accuracy"],
            "correct": result["correct"],
            "total": result["total"],
            "ci_95_low": wilson_interval(result["correct"], result["total"])[0],
            "ci_95_high": wilson_interval(result["correct"], result["total"])[1]
        }
        for key, result in results.items()
    },
    "by_domain": {str(k): v for k, v in by_domain.items()},
    "by_qtype": {str(k): v for k, v in by_qtype.items()},
    "details": details
}

with open(results_path, "w") as f:
    json.dump(output, f, indent=2)

print("\nResults saved to: {}".format(results_path))
