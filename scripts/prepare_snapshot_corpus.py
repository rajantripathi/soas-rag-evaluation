"""Build an approximate pilot corpus from a Wikipedia dump snapshot.

Use this only when the frozen revisions cannot be fetched (for example when the
Wikipedia API rate-limits a cloud host). It maps the pilot's frozen page IDs
to article text in a snapshot such as Hugging Face ``wikimedia/wikipedia``
(``20231101.uz``, ``20231101.en``). Text and revisions differ from the frozen
corpus, so downstream results must be labelled approximate.

* Targets: kept only when the page ID exists in the snapshot. Questions whose
  target is missing are dropped by the ablation script.
* Background: frozen background pages found in the snapshot are kept; missing
  ones are replaced by a seeded random sample of other snapshot pages
  (main-namespace text of at least 100 characters, excluding all frozen IDs)
  so each language keeps the frozen background size.

Example::

    python scripts/prepare_snapshot_corpus.py \
        --snapshot uz=wikisnap/uz.parquet \
        --snapshot en=wikisnap/en_rows.json --snapshot en=wikisnap/en_shard.parquet \
        --out data/title_masking/snapshot_20231101.jsonl
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'research_outputs/reproducible_pilot/source_manifest.json'


def load_rows(path: Path):
    if path.suffix == '.parquet':
        import pyarrow.parquet as pq
        table = pq.read_table(path, columns=['id', 'title', 'text'])
        return zip(table['id'].to_pylist(), table['title'].to_pylist(), table['text'].to_pylist())
    return ((r['id'], r['title'], r['text']) for r in json.loads(path.read_text()))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--snapshot', action='append', required=True, help='LANG=PATH (parquet or JSON list); repeatable')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    pools = defaultdict(dict)
    inputs = []
    for spec in args.snapshot:
        language, path = spec.split('=', 1)
        if language not in ('en', 'uz'):
            parser.error('Snapshot language must be en or uz')
        source = Path(path)
        h = hashlib.sha256()
        with source.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                h.update(chunk)
        inputs.append(dict(language=language, filename=source.name, sha256=h.hexdigest()))
        for page_id, title, text in load_rows(source):
            text = ' '.join((text or '').split())
            if len(text) >= 100:
                previous = pools[language].get(str(page_id))
                if previous is not None and previous != (title, text):
                    raise ValueError(f'Conflicting snapshot rows: {language}:{page_id}')
                pools[language][str(page_id)] = (title, text)

    manifest = json.loads(MANIFEST.read_text())
    frozen_ids = defaultdict(set)
    for doc in manifest['documents']:
        frozen_ids[doc['language']].add(str(doc['page_id']))

    corpus, report = [], {}
    for language in sorted(pools):
        pool = pools[language]
        docs = [d for d in manifest['documents'] if d['language'] == language]
        kept_targets = kept_background = 0
        for doc in docs:
            hit = pool.get(str(doc['page_id']))
            if not hit:
                continue
            # Keep the frozen title: it is what the benchmark questions were written against.
            corpus.append(dict(doc_id=f"{language}:{doc['page_id']}", language=language, title=doc['title'],
                               text=hit[1], role=doc['role'], source='frozen_id', snapshot_title=hit[0]))
            kept_targets += doc['role'] == 'target'
            kept_background += doc['role'] == 'background'
        need = manifest['background_per_language'] - kept_background
        candidates = sorted(pid for pid in pool if pid not in frozen_ids[language])
        if len(candidates) < need:
            raise ValueError(f'Insufficient background candidates for {language}: {len(candidates)} < {need}')
        fill = random.Random(args.seed).sample(candidates, need)
        for pid in fill:
            corpus.append(dict(doc_id=f'{language}:{pid}', language=language, title=pool[pid][0], text=pool[pid][1],
                               role='background', source='snapshot_fill'))
        report[language] = dict(targets=kept_targets, of_targets=sum(d['role'] == 'target' for d in docs),
                                background_frozen=kept_background, background_fill=len(fill))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(''.join(json.dumps(d, ensure_ascii=False) + '\n' for d in corpus))
    provenance = dict(inputs=inputs, seed=args.seed, counts=report,
        corpus_sha256=hashlib.sha256(args.out.read_bytes()).hexdigest(),
        note='Sampling is from the supplied files only, not necessarily all Wikipedia. Frozen-ID rows retain frozen titles; snapshot_title records differences.')
    args.out.with_suffix('.provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
