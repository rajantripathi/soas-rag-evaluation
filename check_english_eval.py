#!/usr/bin/env python3
import json

eval_rows = []
with open('data/eval/manual_eval_v5.jsonl', 'r') as f:
    for line in f:
        eval_rows.append(json.loads(line))

en_missing = [r for r in eval_rows if r['language'] == 'en' and not r.get('source_title')]
print('Total English items:', len([r for r in eval_rows if r['language'] == 'en']))
print('English items without source_title:', len(en_missing))
print()
print('Sample items with missing source:')
for r in en_missing[:5]:
    print("  {}: question='{}...' source_doc_ids={}".format(
        r['id'], r['question'][:60], r.get('source_doc_ids', [])
    ))
