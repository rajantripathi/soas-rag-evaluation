import json
import os

markers = ["Part of a series on", "Main Page", "vte", "Contents"]
items = [json.loads(l) for l in open("data/eval/manual_eval_v5.jsonl")]

flagged = []
for item in items:
    for m in markers:
        if m.lower() in item["gold_answer"].lower():
            flagged.append({
                "id": item["id"],
                "marker": m,
                "preview": item["gold_answer"][:80]
            })
            break

print("Found {} items with Wikipedia navigation artefacts:".format(len(flagged)))
for f in flagged[:10]:
    print("  {}: {} -> {}".format(f["id"], f["marker"], f["preview"]))
if len(flagged) > 10:
    print("  ... and {} more".format(len(flagged) - 10))

os.makedirs("results", exist_ok=True)
with open("results/gold_answer_quality_flags.json", "w") as f:
    json.dump(flagged, f, indent=2)

print("\nSaved to results/gold_answer_quality_flags.json")
