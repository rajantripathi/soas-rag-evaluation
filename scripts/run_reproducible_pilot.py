"""Frozen Wikipedia coverage diagnostic: acquire, run, and report locally."""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PUBLIC = ROOT / 'research_outputs/reproducible_pilot'
CACHE = ROOT / 'data/reproducible_pilot'
DATA = ROOT / 'hf_dataset/manual_eval_v5_retrieval_only.jsonl'
CONFIG_PATH = ROOT / 'configs/reproducible_pilot.json'
CONFIG = json.loads(CONFIG_PATH.read_text())
MODEL = CONFIG['model_id']


def digest(data):
    return hashlib.sha256(data if isinstance(data, bytes) else json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + '\n')
    temporary.replace(path)


def rows():
    return [json.loads(line) for line in DATA.read_text().splitlines() if line.strip()]


def git_commit():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()


def api(language, params):
    import requests
    url = f'https://{language}.wikipedia.org/w/api.php'
    for attempt in range(6):
        try:
            response = requests.get(url, params={'format': 'json', 'formatversion': 2, 'maxlag': 5, **params},
                                    headers={'User-Agent': 'EN-UZ-ResearchPilot/1.0 (https://github.com/rajantripathi/soas-rag-evaluation)'}, timeout=60)
            response.raise_for_status()
            payload = response.json()
            if 'error' in payload:
                raise RuntimeError(str(payload['error']))
            return payload
        except (requests.RequestException, ValueError, RuntimeError):
            if attempt == 5:
                raise
            time.sleep(min(2 ** attempt, 20))


def fetch_page(language, *, title=None, page_id=None, revision_id=None):
    import mwparserfromhell
    params = {'action': 'query', 'prop': 'revisions', 'rvprop': 'ids|timestamp|content', 'rvslots': 'main'}
    if revision_id is not None:
        params['revids'] = str(revision_id)
    elif page_id is not None:
        params['pageids'] = str(page_id)
        params['redirects'] = 1
    else:
        params['titles'] = title
        params['redirects'] = 1
    payload = api(language, params)
    pages = payload.get('query', {}).get('pages', [])
    if len(pages) != 1 or pages[0].get('missing') or not pages[0].get('revisions'):
        return None
    return parse_page(language, pages[0], payload.get('query', {}).get('redirects', []))


def parse_page(language, page, redirects=None):
    import mwparserfromhell
    if page.get('ns') != 0 or not page.get('revisions'):
        return None
    rev = page['revisions'][0]
    raw = rev['slots']['main']['content']
    if raw.lstrip().lower().startswith('#redirect'):
        return None
    clean = ' '.join(mwparserfromhell.parse(raw).strip_code(normalize=True, collapse=True).split())
    if len(clean) < 100:
        return None
    return dict(language=language, page_id=page['pageid'], revision_id=rev['revid'],
                title=page['title'], revision_timestamp=rev['timestamp'],
                url=f"https://{language}.wikipedia.org/w/index.php?oldid={rev['revid']}",
                retrieved_at=datetime.now(timezone.utc).isoformat(),
                raw_sha256=digest(raw.encode()), text_sha256=digest(clean.encode()), text=clean,
                redirects=redirects or [])


def acquire(background_count):
    PUBLIC.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    manifest_path = PUBLIC / 'source_manifest.json'
    if manifest_path.exists():
        manifest = read(manifest_path)
        # Reconstruct exact revisions in bounded API batches; never resample.
        pending = defaultdict(list)
        for doc in manifest['documents']:
            cached = CACHE / 'articles' / f"{doc['language']}_{doc['page_id']}.json"
            if cached.exists():
                stored = read(cached)
                if stored['raw_sha256'] == doc['raw_sha256'] and digest(stored['text'].encode()) == doc['text_sha256']:
                    continue
            pending[doc['language']].append(doc)
        for language, missing in pending.items():
            for start in range(0, len(missing), 50):
                batch = missing[start:start+50]
                payload = api(language, {'action': 'query', 'prop': 'revisions',
                                        'revids': '|'.join(str(d['revision_id']) for d in batch),
                                        'rvprop': 'ids|timestamp|content', 'rvslots': 'main'})
                fetched = {}
                for page in payload.get('query', {}).get('pages', []):
                    parsed = parse_page(language, page)
                    if parsed:
                        fetched[parsed['revision_id']] = parsed
                for doc in batch:
                    value = fetched.get(doc['revision_id'])
                    if not value or value['page_id'] != doc['page_id'] or value['raw_sha256'] != doc['raw_sha256'] or value['text_sha256'] != doc['text_sha256']:
                        raise RuntimeError(f"Frozen revision unavailable or parser mismatch: {doc['url']}")
                    write(CACHE / 'articles' / f"{language}_{doc['page_id']}.json", value)
                print(f'Reconstructed {language}: {min(start+50,len(missing))}/{len(missing)}', flush=True)
        print('Frozen source manifest reconstructed', flush=True)
        return
    targets = {}
    for row in rows():
        if '_v4_' not in row['id']:
            targets[(row['language'], row['source_doc_ids'][0])] = row
    mappings = []
    documents = {}
    for (language, legacy), row in sorted(targets.items()):
        checkpoint = CACHE / 'target_resolution' / f"{digest([language, legacy])}.json"
        if checkpoint.exists():
            record = read(checkpoint)
        else:
            fetched = fetch_page(language, page_id=int(legacy)) if language == 'uz' else fetch_page(language, title=legacy)
            # Uzbek page IDs are checked against the stored title, including redirects.
            title_matches = fetched and (language != 'uz' or row['source_title'] == fetched['title'] or
                                        any(r.get('from') == row['source_title'] for r in fetched['redirects']))
            record = dict(language=language, legacy_id=legacy, status='resolved' if title_matches else 'unresolved',
                          requested_title=row['source_title'] or legacy,
                          page_id=fetched['page_id'] if title_matches else None,
                          reason=None if title_matches else 'missing_short_nonarticle_or_title_mismatch')
            if title_matches:
                write(CACHE / 'articles' / f"{language}_{fetched['page_id']}.json", fetched)
            write(checkpoint, record)
        mappings.append(record)
        if record['status'] == 'resolved':
            key = (language, record['page_id'])
            documents[key] = read(CACHE / 'articles' / f'{language}_{key[1]}.json')
        if len(mappings) % 25 == 0:
            print(f'Resolved target attempts: {len(mappings)}/{len(targets)}', flush=True)
    write(PUBLIC / 'target_mapping.json', mappings)
    counts = {language: sum(m['language'] == language and m['status'] == 'resolved' for m in mappings) for language in ('en', 'uz')}
    print('Resolved original targets:', counts, flush=True)
    if min(counts.values()) < CONFIG['minimum_resolved_targets_per_language']:
        raise RuntimeError('Below predeclared 90-target-per-language gate; mapping audit saved, no bilingual experiment run.')
    target_keys = set(documents)
    for language in ('en', 'uz'):
        pool_path = CACHE / f'background_selection_{language}.json'
        pool = read(pool_path) if pool_path.exists() else []
        existing = set(pool)
        while len(pool) < background_count:
            payload = api(language, {'action': 'query', 'generator': 'random', 'grnnamespace': 0,
                                     'grnfilterredir': 'nonredirects', 'grnlimit': 50,
                                     'prop': 'revisions', 'rvprop': 'ids|timestamp|content', 'rvslots': 'main'})
            for candidate in payload.get('query', {}).get('pages', []):
                pid = candidate['pageid']
                if pid in existing or (language, pid) in target_keys:
                    continue
                fetched = parse_page(language, candidate)
                if not fetched or fetched['page_id'] != pid:
                    continue
                write(CACHE / 'articles' / f'{language}_{pid}.json', fetched)
                pool.append(pid)
                existing.add(pid)
                write(pool_path, pool)
                if len(pool) % 100 == 0:
                    print(f'{language}: {len(pool)}/{background_count} background articles', flush=True)
                if len(pool) == background_count:
                    break
        for pid in pool[:background_count]:
            documents[(language, pid)] = read(CACHE / 'articles' / f'{language}_{pid}.json')
    public_docs = []
    for key, doc in sorted(documents.items()):
        public_docs.append({**{k: v for k, v in doc.items() if k != 'text'}, 'role': 'target' if key in target_keys else 'background'})
    manifest = dict(dataset_sha256=digest(DATA.read_bytes()), background_per_language=background_count,
                    selection='Wikipedia random main-namespace nonredirect pages; fixed once in this manifest, not seeded resampling',
                    parser_version=importlib.metadata.version('mwparserfromhell'), documents=public_docs)
    write(manifest_path, manifest)
    print('Frozen manifest written', flush=True)


def removal_ids(target_ids, seed):
    values = sorted(target_ids)
    random.Random(seed).shuffle(values)
    return set(values[:len(values) // 2])


def rank(scores, ids, excluded=(), k=5):
    # Stable document-ID tie break; missing sources cannot be returned.
    return [ids[i] for i in sorted((i for i in range(len(ids)) if ids[i] not in excluded),
                                  key=lambda i: (-float(scores[i]), ids[i]))[:k]]


def prepare_model():
    from huggingface_hub import model_info, snapshot_download
    lock_path = PUBLIC / 'model_lock.json'
    lock = read(lock_path) if lock_path.exists() else {'model_id': MODEL, 'revision': model_info(MODEL).sha}
    write(lock_path, lock)
    return snapshot_download(repo_id=lock['model_id'], revision=lock['revision'], allow_patterns=['*.json', '*.txt', 'model.safetensors', 'pytorch_model.bin', 'sentencepiece.bpe.model', 'tokenizer.model', '1_Pooling/*']), lock


def run():
    os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
    import numpy as np
    import torch
    from sentence_transformers import SentenceTransformer
    from src.retrieval import BM25Index, tokenize
    torch.set_num_threads(CONFIG['torch_threads'])
    model_path, model_lock = prepare_model()
    model = SentenceTransformer(model_path, device=CONFIG['device'])
    model.max_seq_length = CONFIG['model_max_tokens']
    model.eval()
    manifest = read(PUBLIC / 'source_manifest.json')
    if manifest['dataset_sha256'] != digest(DATA.read_bytes()):
        raise ValueError('Dataset differs from frozen source manifest')
    mapping = read(PUBLIC / 'target_mapping.json')
    resolved = {(m['language'], m['legacy_id']): f"{m['language']}:{m['page_id']}" for m in mapping if m['status'] == 'resolved'}
    examples = [{**r, 'canonical_target': resolved[(r['language'], r['source_doc_ids'][0])]} for r in rows()
                if (r['language'], r['source_doc_ids'][0]) in resolved]
    # Export canonical labels separately; preserve published dataset bytes.
    labels = [{'id': r['id'], 'language': r['language'], 'domain': r['domain'], 'question': r['question'],
               'source_doc_ids': [r['canonical_target']], 'variant': '_v4_' in r['id'], 'quality_flag': r['quality_flag']} for r in examples]
    label_path = PUBLIC / 'evaluation_labels.jsonl'
    label_path.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in labels))
    passages = []
    for doc in manifest['documents']:
        cached = read(CACHE / 'articles' / f"{doc['language']}_{doc['page_id']}.json")
        if digest(cached['text'].encode()) != doc['text_sha256']:
            raise ValueError('Article hash mismatch')
        text = doc['title'] + '. ' + cached['text']
        tokens = model.tokenizer.encode(text, add_special_tokens=False)[:CONFIG['passage_tokens']]
        text = model.tokenizer.decode(tokens, skip_special_tokens=True)
        passages.append({'doc_id': f"{doc['language']}:{doc['page_id']}", 'language': doc['language'], 'text': text})
    write(PUBLIC / 'passage_manifest.json', [{'doc_id': p['doc_id'], 'text_sha256': digest(p['text'].encode())} for p in passages])
    base_metadata = dict(git_commit=git_commit(), protocol=CONFIG, config_sha256=digest(CONFIG_PATH.read_bytes()), runner_sha256=digest(Path(__file__).read_bytes()), dataset_sha256=digest(DATA.read_bytes()),
                         source_manifest_sha256=digest((PUBLIC/'source_manifest.json').read_bytes()),
                         target_mapping_sha256=digest((PUBLIC/'target_mapping.json').read_bytes()),
                         model=model_lock, device='cpu', batch_size=8, max_tokens=480,
                         cutoff_primary=3, cutoffs=[1,3,5], seeds=list(range(42,47)),
                         packages={p: importlib.metadata.version(p) for p in ['numpy','torch','sentence-transformers','transformers','mwparserfromhell']})
    write(PUBLIC / 'run_manifest.json', base_metadata)

    def encode(texts, prefix, kind):
        encoded = []
        for start in range(0, len(texts), 8):
            batch = [prefix + t for t in texts[start:start+8]]
            key = digest([batch, model_lock, CONFIG['model_max_tokens'], base_metadata['packages']])
            path = CACHE / 'embeddings' / f'{key}.npy'
            if path.exists():
                values = np.load(path, allow_pickle=False)
            else:
                values = model.encode(batch, batch_size=8, normalize_embeddings=True, show_progress_bar=False, convert_to_numpy=True)
                path.parent.mkdir(parents=True, exist_ok=True)
                np.save(path, values, allow_pickle=False)
            encoded.append(values)
            if start % 200 == 0:
                print(f'{kind}: {start}/{len(texts)} encoded', flush=True)
        return np.vstack(encoded)

    all_predictions = []
    for language in ('en','uz'):
        docs = [p for p in passages if p['language'] == language]
        questions = [r for r in examples if r['language'] == language]
        ids = [p['doc_id'] for p in docs]
        targets = {q['canonical_target'] for q in questions}
        masks = {'full': set(), **{f'removed_{seed}': removal_ids(targets,seed) for seed in range(42,47)}}
        write(PUBLIC / f'conditions_{language}.json', {k: sorted(v) for k,v in masks.items()})
        for method in ('bm25', 'e5_prefixed', 'e5_unprefixed'):
            output_path = PUBLIC / f'predictions_{language}_{method}.jsonl'
            if method == 'bm25':
                # Corpus removal changes lexical IDF and average length: rebuild
                # BM25 per condition, rather than merely masking full-corpus scores.
                score_arrays = {}
                for condition, excluded in masks.items():
                    available = [d for d in docs if d['doc_id'] not in excluded]
                    index = BM25Index(available); index.build()
                    condition_ids = [d['doc_id'] for d in available]
                    score_arrays[condition] = (condition_ids, [[index._score(tokenize(q['question']), i) for i in range(len(available))] for q in questions])
            else:
                prefix = method == 'e5_prefixed'
                doc_vectors = encode([d['text'] for d in docs], 'passage: ' if prefix else '', f'{language}/{method}/docs')
                query_vectors = encode([q['question'] for q in questions], 'query: ' if prefix else '', f'{language}/{method}/queries')
                scores = query_vectors @ doc_vectors.T
                score_arrays = {condition: (ids, scores) for condition in masks}
            output = []
            for condition, excluded in masks.items():
                condition_ids, scores = score_arrays[condition]
                for q, values in zip(questions, scores):
                    output.append(dict(id=q['id'], language=language, domain=q['domain'], variant='_v4_' in q['id'],
                                       source_group=q['canonical_target'], quality_flag=q['quality_flag'], method=method, condition=condition,
                                       target_available=q['canonical_target'] not in excluded,
                                       retrieved_doc_ids=rank(values, condition_ids, excluded)))
            output_path.write_text(''.join(json.dumps(p,ensure_ascii=False)+'\n' for p in output))
            all_predictions.extend(output)
            print(f'Finished {language}/{method}: {len(output)} predictions', flush=True)
    print('All retrieval runs complete', flush=True)


def report():
    import numpy as np
    predictions = []
    for path in sorted(PUBLIC.glob('predictions_*.jsonl')):
        predictions.extend(json.loads(line) for line in path.read_text().splitlines())
    labels = {r['id']: r for r in [json.loads(line) for line in (PUBLIC/'evaluation_labels.jsonl').read_text().splitlines()]}
    expected = {(r['id'],method,condition) for r in labels.values() for method in ('bm25','e5_prefixed','e5_unprefixed')
                for condition in ('full',*[f'removed_{s}' for s in range(42,47)])}
    actual = [(p['id'],p['method'],p['condition']) for p in predictions]
    if set(actual) != expected or len(actual) != len(expected):
        raise ValueError('Missing or duplicate predictions')
    manifest = read(PUBLIC/'source_manifest.json')
    known_ids = {f"{d['language']}:{d['page_id']}" for d in manifest['documents']}
    masks = {language: read(PUBLIC/f'conditions_{language}.json') for language in ('en','uz')}
    for p in predictions:
        label = labels[p['id']]
        if p['language'] != label['language'] or p['domain'] != label['domain'] or p['variant'] != label['variant'] or p['quality_flag'] != label['quality_flag'] or p['source_group'] != label['source_doc_ids'][0]:
            raise ValueError('Prediction metadata differs from frozen labels')
        excluded = set(masks[p['language']][p['condition']])
        if p['target_available'] != (p['source_group'] not in excluded):
            raise ValueError('Incorrect availability annotation')
        ranked = p['retrieved_doc_ids']
        if len(ranked) != len(set(ranked)) or len(ranked) > 5 or any(d not in known_ids or d in excluded or not d.startswith(p['language']+':') for d in ranked):
            raise ValueError('Invalid, removed, duplicate, or cross-language retrieved ID')
    metrics = []
    for subset in ('original','variants','unflagged_original'):
        selected = [p for p in predictions if (p['variant'] if subset=='variants' else not p['variant'])
                    and (subset!='unflagged_original' or not p['quality_flag'])]
        groups = defaultdict(list)
        for p in selected:
            groups[(p['language'],p['method'],p['condition'])].append(p)
        for (lang,method,condition), items in sorted(groups.items()):
            availability = sum(p['target_available'] for p in items)
            for k in (1,3,5):
                hits = sum(p['source_group'] in p['retrieved_doc_ids'][:k] for p in items)
                if hits > availability:
                    raise ValueError('Hit rate exceeds source availability')
                metrics.append(dict(subset=subset, language=lang, method=method, condition=condition, k=k,
                                    rows=len(items), hits=hits, available=availability, hit_rate=hits/len(items),
                                    availability=availability/len(items), conditional_hit_rate=hits/availability if availability else None))
    write(PUBLIC/'metrics.json', metrics)
    intervals=[]
    # Each language is resampled separately, preserving source groups and pairing.
    for lang in ('en','uz'):
        for method in ('bm25','e5_prefixed','e5_unprefixed'):
            paired=defaultdict(dict)
            for p in predictions:
                if p['language']==lang and p['method']==method and not p['variant'] and p['condition'] in ('full','removed_42'):
                    paired[p['source_group']].setdefault(p['condition'],[]).append(float(p['source_group'] in p['retrieved_doc_ids'][:3]))
            diffs=np.array([np.mean(v['full'])-np.mean(v['removed_42']) for v in paired.values()])
            rng=np.random.default_rng(42)
            boot=rng.choice(diffs,size=(10000,len(diffs)),replace=True).mean(axis=1)
            intervals.append(dict(language=lang,method=method,comparison='full minus removed_42',source_groups=len(diffs),
                                  difference=float(diffs.mean()),lower=float(np.quantile(boot,.025)),upper=float(np.quantile(boot,.975))))
    write(PUBLIC/'paired_intervals.json',intervals)
    lines=['# Reproducible coverage diagnostic results','',
           'New local experiment on frozen Wikipedia revisions. Not a reproduction of the historical corpus or an unseen-source evaluation. Primary analysis uses original questions; intervals condition on the frozen corpus and seed-42 removal.', '',
           '| Language | Method | Condition | Questions | Source availability | Hit@3 | Hit@3 given availability |',
           '| --- | --- | --- | ---: | ---: | ---: | ---: |']
    for m in metrics:
        if m['subset']=='original' and m['k']==3:
            conditional='N/A' if m['conditional_hit_rate'] is None else f"{m['conditional_hit_rate']:.1%}"
            lines.append(f"| {m['language']} | {m['method']} | {m['condition']} | {m['rows']} | {m['availability']:.1%} | {m['hit_rate']:.1%} | {conditional} |")
    lines+=['','## Paired differences at k=3 (full minus seed-42 reduced corpus)','',
            '| Language | Method | Difference | 95% source-bootstrap interval |','| --- | --- | ---: | --- |']
    for v in intervals:
        lines.append(f"| {v['language']} | {v['method']} | {100*v['difference']:.1f} pp | [{100*v['lower']:.1f}, {100*v['upper']:.1f}] pp |")
    lines+=['','All cutoffs, variant and unflagged sensitivity results are in `metrics.json`. Unflagged is not equivalent to independently validated. Background articles were sampled once; bootstrap intervals do not account for background-corpus selection. Source restoration uses the full frozen condition.','']
    (PUBLIC/'results.md').write_text('\n'.join(lines))
    print('Reports regenerated from checked predictions',flush=True)


def main():
    global CACHE
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=['acquire','model','run','report'])
    parser.add_argument('--background-count',type=int,default=CONFIG['background_per_language'])
    parser.add_argument('--cache-dir', type=Path, default=CACHE, help='Local source and embedding cache; never published.')
    args=parser.parse_args()
    CACHE=args.cache_dir
    if args.stage=='acquire': acquire(args.background_count)
    elif args.stage=='model': prepare_model()
    elif args.stage=='run': run()
    else: report()


if __name__=='__main__': main()
