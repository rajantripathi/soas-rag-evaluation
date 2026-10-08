"""Run the frozen title-masking protocol with additional dense retrievers.

Re-uses the passage construction of ``run_title_masking_ablation.py`` so every
retriever sees byte-identical passages. On the frozen corpus the passage hashes
are checked against ``research_outputs/title_masking/frozen/passage_audit.jsonl``
before any model runs.

Retrievers and pinned revisions are listed in ``configs/title_masking_retrievers.json``.
Embeddings are cached under ``data/title_masking/embeddings`` so an interrupted run
resumes without re-encoding finished (retriever, language, variant) blocks.

Typical use, after ``python scripts/run_reproducible_pilot.py acquire``::

    python scripts/run_title_masking_retrievers.py                  # all retrievers, auto device
    python scripts/run_title_masking_retrievers.py --retrievers e5_base --device cpu
    python scripts/verify_title_masking.py

Outputs go to ``research_outputs/title_masking/frozen_retrievers`` (metrics.json,
predictions.jsonl, results.md).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_title_masking_ablation import (  # noqa: E402
    CACHE, CONFIG, CUTOFFS, PILOT, ROOT, VARIANTS, bootstrap_drop, build_passages, load_frozen_corpus, rank, sha,
)

RETRIEVER_CONFIG_PATH = ROOT / 'configs/title_masking_retrievers.json'
FROZEN_AUDIT = ROOT / 'research_outputs/title_masking/frozen/passage_audit.jsonl'
EMBED_CACHE = ROOT / 'data/title_masking/embeddings'


def pick_device(requested: str) -> str:
    import torch
    if requested != 'auto':
        return requested
    if torch.cuda.is_available():
        return 'cuda'
    if getattr(torch.backends, 'mps', None) and torch.backends.mps.is_available():
        return 'mps'
    return 'cpu'


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--retrievers', nargs='+', help='Subset of retriever names (default: all in the config)')
    parser.add_argument('--device', default='auto', help='auto, cpu, cuda or mps')
    parser.add_argument('--batch-size', type=int, default=16)
    parser.add_argument('--cache-dir', type=Path, default=CACHE, help='Frozen pilot cache')
    parser.add_argument('--corpus', type=Path, help='JSONL corpus for an approximate or smoke run')
    parser.add_argument('--limit-per-language', type=int, help='Smoke test: keep the first N targets and 2N background docs')
    parser.add_argument('--name', default=None, help='Output folder name (default: frozen_retrievers)')
    parser.add_argument('--note', default='')
    args = parser.parse_args()

    os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
    import importlib.metadata
    import numpy as np
    import torch
    from huggingface_hub import snapshot_download
    from sentence_transformers import SentenceTransformer
    from transformers import AutoTokenizer

    torch.set_num_threads(CONFIG['torch_threads'])
    device = pick_device(args.device)
    spec = json.loads(RETRIEVER_CONFIG_PATH.read_text())
    retrievers = spec['retrievers']
    if args.retrievers:
        unknown = set(args.retrievers) - {r['name'] for r in retrievers}
        if unknown:
            parser.error(f'Unknown retrievers: {sorted(unknown)}')
        retrievers = [r for r in retrievers if r['name'] in args.retrievers]

    # Passage tokenizer: the pinned E5-small tokenizer used by the frozen run.
    lock = json.loads((PILOT / 'model_lock.json').read_text())
    tok_path = snapshot_download(repo_id=lock['model_id'], revision=lock['revision'],
                                 allow_patterns=['*.json', '*.txt', 'sentencepiece.bpe.model', 'tokenizer.model'])
    tokenizer = AutoTokenizer.from_pretrained(tok_path)

    smoke = args.limit_per_language is not None
    if args.corpus:
        corpus = [json.loads(l) for l in args.corpus.read_text().splitlines() if l.strip()]
        approximate = True
    else:
        corpus = load_frozen_corpus(args.cache_dir)
        approximate = smoke
    labels = [json.loads(l) for l in (PILOT / 'evaluation_labels.jsonl').read_text().splitlines() if l.strip()]
    if smoke:
        keep = []
        for language in CONFIG['languages']:
            docs = [d for d in corpus if d['language'] == language]
            keep += [d for d in docs if d['role'] == 'target'][:args.limit_per_language]
            keep += [d for d in docs if d['role'] == 'background'][:2 * args.limit_per_language]
        corpus = keep
    name = args.name or ('frozen_retrievers' if not approximate else 'approximate_retrievers')
    if not re.fullmatch(r'[A-Za-z0-9_-]+', name):
        parser.error('--name must be a simple directory name')
    if len({d['doc_id'] for d in corpus}) != len(corpus):
        raise ValueError('Duplicate corpus IDs')
    corpus_ids = {d['doc_id'] for d in corpus}
    out_dir = ROOT / 'research_outputs/title_masking' / name
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build every passage once and, on the frozen corpus, prove identity with the audited run.
    passages = {}
    for language in CONFIG['languages']:
        docs = [d for d in corpus if d['language'] == language]
        for variant in VARIANTS:
            passages[(language, variant)] = build_passages(docs, variant, tokenizer)
    if not approximate:
        audit = {(r['doc_id'], r['variant']): r['text_sha256']
                 for r in map(json.loads, FROZEN_AUDIT.read_text().splitlines())}
        built = {(p['doc_id'], variant): sha(p['text']) for (language, variant), ps in passages.items() for p in ps}
        if built != audit:
            mismatched = sum(audit.get(k) != v for k, v in built.items())
            raise SystemExit(f'Passages differ from frozen audit ({mismatched} mismatches); refusing to run.')
        print(f'Passage identity check passed ({len(built)} passages).', flush=True)

    predictions, results, per_question, model_records = [], [], {}, []
    for retriever in retrievers:
        method = retriever['name']
        started = time.time()
        model = SentenceTransformer(retriever['model_id'], revision=retriever['revision'], device=device)
        model.max_seq_length = spec['max_seq_length']
        model.eval()

        def encode(texts, prefix, tag):
            key = sha(json.dumps([retriever['model_id'], retriever['revision'], prefix, spec['max_seq_length'],
                                  device, [sha(t) for t in texts]]))
            path = EMBED_CACHE / method / f'{key}.npy'
            if path.exists():
                return np.load(path, allow_pickle=False)
            values = model.encode([prefix + t for t in texts], batch_size=args.batch_size, normalize_embeddings=True,
                                  convert_to_numpy=True, show_progress_bar=False)
            path.parent.mkdir(parents=True, exist_ok=True)
            np.save(path, values, allow_pickle=False)
            print(f'  {method} {tag}: encoded {len(texts)} in {time.time() - started:.0f}s', flush=True)
            return values

        for language in CONFIG['languages']:
            questions = [q for q in labels if q['language'] == language and q['source_doc_ids'][0] in corpus_ids]
            originals = [q for q in questions if not q['variant']]
            qv = encode([q['question'] for q in questions], retriever['query_prefix'], f'{language}/queries')
            for variant in VARIANTS:
                ps = passages[(language, variant)]
                ids = [p['doc_id'] for p in ps]
                dv = encode([p['text'] for p in ps], retriever['passage_prefix'], f'{language}/{variant}')
                for q, scores in zip(questions, qv @ dv.T):
                    top = rank(scores, ids)
                    predictions.append(dict(id=q['id'], language=language, passage_variant=variant, method=method,
                                            questions='alternate' if q['variant'] else 'original',
                                            source_doc_ids=q['source_doc_ids'], retrieved_doc_ids=top))
                    per_question[(language, variant, method, q['id'])] = {k: int(q['source_doc_ids'][0] in top[:k]) for k in CUTOFFS}
                for subset, rows in (('original', originals), ('alternate', [q for q in questions if q['variant']])):
                    if rows:
                        hits = {k: sum(per_question[(language, variant, method, q['id'])][k] for q in rows) for k in CUTOFFS}
                        results.append(dict(language=language, variant=variant, method=method, questions=subset, n=len(rows),
                                            **{f'hit@{k}': round(100 * hits[k] / len(rows), 1) for k in CUTOFFS}))
        model_records.append(dict(**retriever, device=device, seconds=round(time.time() - started)))
        print(f'{method} done in {time.time() - started:.0f}s', flush=True)
        del model

    intervals = []
    methods = [r['name'] for r in retrievers]
    for language in CONFIG['languages']:
        originals = [q for q in labels if q['language'] == language and not q['variant'] and q['source_doc_ids'][0] in corpus_ids]
        for method in methods:
            a = [per_question[(language, 'title_prefix', method, q['id'])][3] for q in originals]
            b = [per_question[(language, 'title_masked', method, q['id'])][3] for q in originals]
            intervals.append(dict(language=language, method=method, k=3, n=len(a),
                                  drop_pp=round(100 * (sum(a) - sum(b)) / len(a), 1),
                                  ci95_pp=[round(x, 1) for x in bootstrap_drop(a, b, CONFIG['bootstrap_resamples'], CONFIG['bootstrap_seed'])]))

    payload = dict(protocol=spec['protocol'], approximate=approximate, baseline_ranks=False, note=args.note,
                   corpus_sha256=sha(json.dumps(corpus, sort_keys=True, ensure_ascii=False)),
                   retrievers=model_records, variants=VARIANTS, methods=methods, results=results, title_masking_drop=intervals,
                   provenance=dict(script_sha256=sha(Path(__file__).read_text()),
                                   retriever_config_sha256=sha(RETRIEVER_CONFIG_PATH.read_text()), config=CONFIG,
                                   passage_tokenizer=lock,
                                   labels_sha256=sha((PILOT / 'evaluation_labels.jsonl').read_text()),
                                   source_manifest_sha256=sha((PILOT / 'source_manifest.json').read_text()),
                                   packages={p: importlib.metadata.version(p) for p in ('numpy', 'torch', 'transformers', 'sentence-transformers')},
                                   excluded_question_ids=[q['id'] for q in labels if q['source_doc_ids'][0] not in corpus_ids]))
    (out_dir / 'predictions.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in predictions))
    (out_dir / 'metrics.json').write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n')

    lines = [f'# Title masking with additional retrievers ({name})', '']
    if approximate:
        lines += ['**Approximate or smoke run; not the frozen corpus.** ' + args.note, '']
    lines += ['Complete corpus, original questions, Hit@3 (%).' + ('' if approximate else ' Passages are identical to the frozen title-masking run.'), '',
              '| Retriever | Language | Title prefix | No added prefix | Title masked | Masked fixed window |',
              '| --- | --- | ---: | ---: | ---: | ---: |']
    for method in methods:
        for language in CONFIG['languages']:
            cells = {r['variant']: r['hit@3'] for r in results if r['method'] == method and r['language'] == language and r['questions'] == 'original'}
            lines.append(f"| {method} | {language} | " + ' | '.join(str(cells[v]) for v in VARIANTS) + ' |')
    lines += ['', 'Drop in Hit@3 from title prefix to title masked (paired source-group bootstrap, 95% interval):', '',
              '| Retriever | Language | n | Drop (pp) | 95% interval (pp) |', '| --- | --- | ---: | ---: | --- |']
    for r in intervals:
        lines.append(f"| {r['method']} | {r['language']} | {r['n']} | {r['drop_pp']} | [{r['ci95_pp'][0]}, {r['ci95_pp'][1]}] |")
    lines += ['', 'Model revisions, device and timings are in `metrics.json`.']
    (out_dir / 'results.md').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
