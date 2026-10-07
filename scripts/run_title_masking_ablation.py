"""Title-masking ablation for the frozen-corpus retrieval pilot.

Most benchmark questions name their source article ("Toshkent nima?" ->
"Toshkent"). This script measures how much of the complete-corpus source hit
rate depends on that overlap by re-scoring the same questions against three
passage representations:

* ``title_prefix``  - the pilot protocol: "<title>. <lead text>"
* ``no_prefix``     - lead text only; the title still occurs naturally in the text
* ``title_masked``  - lead text with every occurrence of the article's own title
                      removed (case-insensitive, apostrophe-variant tolerant)

Masking is applied to every candidate article, target and background alike.
All runs use the complete corpus (no source removal).

Two corpus sources are supported:

* frozen (default): the pilot's hash-checked revision cache under
  ``data/reproducible_pilot/articles`` (run ``run_reproducible_pilot.py acquire``
  first). Results are written to ``research_outputs/title_masking/frozen``.
* ``--corpus FILE``: a JSONL corpus with fields doc_id, language, title, text,
  role (for example from ``prepare_snapshot_corpus.py``). Results are labelled
  approximate and written to ``research_outputs/title_masking/<name>``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PILOT = ROOT / 'research_outputs/reproducible_pilot'
CACHE = ROOT / 'data/reproducible_pilot'
CONFIG = json.loads((ROOT / 'configs/reproducible_pilot.json').read_text())
VARIANTS = ('title_prefix', 'no_prefix', 'title_masked')
METHODS = ('bm25', 'e5_prefixed')
CUTOFFS = (1, 3, 5)
APOSTROPHES = "ʻʼ'‘’`ʹ"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def norm(text: str) -> str:
    text = re.sub(f'[{APOSTROPHES}]', "'", text.lower())
    return ' '.join(re.sub(r'[^\w\']+', ' ', text).split())


def title_pattern(title: str) -> re.Pattern:
    """Match the title, and its form without a parenthetical disambiguator."""
    forms = {title, re.sub(r'\s*\(.*?\)\s*$', '', title)}
    alternatives = []
    for form in sorted((f for f in forms if f.strip()), key=len, reverse=True):
        parts = [re.escape(p) for p in re.split(r'\s+', form.strip())]
        escaped = r'\s+'.join(parts)
        escaped = re.sub('|'.join(re.escape(re.escape(a)) for a in APOSTROPHES), f'[{APOSTROPHES}]', escaped)
        alternatives.append(escaped)
    return re.compile('|'.join(alternatives), re.IGNORECASE)


def mask_title(title: str, text: str) -> str:
    return ' '.join(title_pattern(title).sub(' ', text).split())


def load_frozen_corpus() -> list[dict]:
    manifest = json.loads((PILOT / 'source_manifest.json').read_text())
    corpus = []
    for doc in manifest['documents']:
        path = CACHE / 'articles' / f"{doc['language']}_{doc['page_id']}.json"
        if not path.exists():
            raise SystemExit(f'Missing frozen article {path}. Run: python scripts/run_reproducible_pilot.py acquire')
        cached = json.loads(path.read_text())
        if sha(cached['text']) != doc['text_sha256']:
            raise SystemExit(f'Hash mismatch for {path}')
        corpus.append(dict(doc_id=f"{doc['language']}:{doc['page_id']}", language=doc['language'],
                           title=doc['title'], text=cached['text'], role=doc['role']))
    return corpus


def build_passages(corpus, variant, tokenizer):
    out = []
    for doc in corpus:
        if variant == 'title_prefix':
            text = doc['title'] + '. ' + doc['text']
        elif variant == 'no_prefix':
            text = doc['text']
        else:
            text = mask_title(doc['title'], doc['text'])
        tokens = tokenizer.encode(text, add_special_tokens=False)[:CONFIG['passage_tokens']]
        out.append(dict(doc_id=doc['doc_id'], language=doc['language'],
                        text=tokenizer.decode(tokens, skip_special_tokens=True)))
    return out


def rank(scores, ids, k=5):
    return [ids[i] for i in sorted(range(len(ids)), key=lambda i: (-float(scores[i]), ids[i]))[:k]]


def bootstrap_drop(a, b, resamples, seed):
    """Paired source-group bootstrap for mean(a) - mean(b); one question per source."""
    rng = random.Random(seed)
    n = len(a)
    diffs = []
    for _ in range(resamples):
        idx = [rng.randrange(n) for _ in range(n)]
        diffs.append(sum(a[i] - b[i] for i in idx) / n)
    diffs.sort()
    return [100 * diffs[int(0.025 * resamples)], 100 * diffs[int(0.975 * resamples) - 1]]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--corpus', type=Path, help='JSONL corpus; omit to use the frozen pilot cache')
    parser.add_argument('--name', default=None, help='Output folder name (default: frozen or corpus stem)')
    parser.add_argument('--note', default='', help='Provenance note recorded with approximate runs')
    args = parser.parse_args()

    os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
    import numpy as np
    import torch
    from sentence_transformers import SentenceTransformer
    from huggingface_hub import snapshot_download
    from src.retrieval import BM25Index, tokenize

    torch.set_num_threads(CONFIG['torch_threads'])
    lock = json.loads((PILOT / 'model_lock.json').read_text())
    model_path = snapshot_download(repo_id=lock['model_id'], revision=lock['revision'],
                                   allow_patterns=['*.json', '*.txt', 'model.safetensors', 'sentencepiece.bpe.model',
                                                   'tokenizer.model', '1_Pooling/*'])
    model = SentenceTransformer(model_path, device='cpu')
    model.max_seq_length = CONFIG['model_max_tokens']

    if args.corpus:
        corpus = [json.loads(l) for l in args.corpus.read_text().splitlines() if l.strip()]
        approximate, name = True, args.name or args.corpus.stem
    else:
        corpus = load_frozen_corpus()
        approximate, name = False, args.name or 'frozen'
    out_dir = ROOT / 'research_outputs/title_masking' / name
    out_dir.mkdir(parents=True, exist_ok=True)

    labels = [json.loads(l) for l in (PILOT / 'evaluation_labels.jsonl').read_text().splitlines() if l.strip()]
    corpus_ids = {d['doc_id'] for d in corpus}
    titles = {d['doc_id']: d['title'] for d in corpus}

    results, per_question = [], {}
    leakage = {}
    for language in CONFIG['languages']:
        docs = [d for d in corpus if d['language'] == language]
        questions = [q for q in labels if q['language'] == language and q['source_doc_ids'][0] in corpus_ids]
        originals = [q for q in questions if not q['variant']]
        leakage[language] = dict(
            original_questions=len(originals),
            title_in_question=sum(norm(titles[q['source_doc_ids'][0]]) in norm(q['question']) for q in originals),
            targets_in_corpus=len({q['source_doc_ids'][0] for q in originals}),
            candidates=len(docs), background=sum(d['role'] == 'background' for d in docs))
        for variant in VARIANTS:
            passages = build_passages(docs, variant, model.tokenizer)
            ids = [p['doc_id'] for p in passages]
            for method in METHODS:
                if method == 'bm25':
                    index = BM25Index(passages); index.build()
                    score_rows = [[index._score(tokenize(q['question']), i) for i in range(len(ids))] for q in questions]
                else:
                    dv = model.encode(['passage: ' + p['text'] for p in passages], batch_size=8,
                                      normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)
                    qv = model.encode(['query: ' + q['question'] for q in questions], batch_size=8,
                                      normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)
                    score_rows = qv @ dv.T
                for q, scores in zip(questions, score_rows):
                    top = rank(scores, ids)
                    gold = q['source_doc_ids'][0]
                    per_question[(language, variant, method, q['id'])] = {k: int(gold in top[:k]) for k in CUTOFFS}
                for subset, rows in (('original', originals), ('alternate', [q for q in questions if q['variant']])):
                    if not rows:
                        continue
                    hits = {k: sum(per_question[(language, variant, method, q['id'])][k] for q in rows) for k in CUTOFFS}
                    results.append(dict(language=language, variant=variant, method=method, questions=subset, n=len(rows),
                                        **{f'hit@{k}': round(100 * hits[k] / len(rows), 1) for k in CUTOFFS}))
                print(f'{language} {variant} {method} done', flush=True)

    intervals = []
    for language in CONFIG['languages']:
        originals = [q for q in labels if q['language'] == language and not q['variant'] and q['source_doc_ids'][0] in corpus_ids]
        for method in METHODS:
            a = [per_question[(language, 'title_prefix', method, q['id'])][3] for q in originals]
            b = [per_question[(language, 'title_masked', method, q['id'])][3] for q in originals]
            intervals.append(dict(language=language, method=method, k=3, n=len(a),
                                  drop_pp=round(100 * (sum(a) - sum(b)) / len(a), 1),
                                  ci95_pp=[round(x, 1) for x in bootstrap_drop(a, b, CONFIG['bootstrap_resamples'], CONFIG['bootstrap_seed'])]))

    payload = dict(approximate=approximate, note=args.note, corpus_sha256=sha(json.dumps(corpus, sort_keys=True, ensure_ascii=False)),
                   model=lock, variants=VARIANTS, methods=METHODS, leakage=leakage, results=results, title_masking_drop=intervals)
    (out_dir / 'metrics.json').write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n')

    lines = [f'# Title-masking ablation ({name})', '']
    if approximate:
        lines += ['**Approximate run.** The corpus is not the hash-checked frozen pilot corpus. ' + args.note, '']
    lines += ['Complete corpus, original questions. Hit@k in percent.', '',
              '| Language | Method | Variant | n | Hit@1 | Hit@3 | Hit@5 |', '| --- | --- | --- | ---: | ---: | ---: | ---: |']
    for r in results:
        if r['questions'] == 'original':
            lines.append(f"| {r['language']} | {r['method']} | {r['variant']} | {r['n']} | {r['hit@1']} | {r['hit@3']} | {r['hit@5']} |")
    lines += ['', 'Drop in Hit@3 from title_prefix to title_masked (source-group paired bootstrap, 95% interval):', '',
              '| Language | Method | n | Drop (pp) | 95% interval (pp) |', '| --- | --- | ---: | ---: | --- |']
    for r in intervals:
        lines.append(f"| {r['language']} | {r['method']} | {r['n']} | {r['drop_pp']} | [{r['ci95_pp'][0]}, {r['ci95_pp'][1]}] |")
    lines += ['', 'Question-title overlap (original questions whose text contains the target article title):', '']
    for language, s in leakage.items():
        lines.append(f"- {language}: {s['title_in_question']}/{s['original_questions']} questions; "
                     f"{s['candidates']} candidates ({s['background']} background)")
    lines += ['', 'Alternate-phrasing results are in `metrics.json`.']
    (out_dir / 'results.md').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
