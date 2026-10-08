"""Between-language differences for the title-masking runs (standard library only).

For every retriever and passage variant this computes, on original questions at k=3:

* the English minus Uzbek Hit@3 difference, with an unpaired bootstrap that
  resamples source groups independently within each language;
* the difference in masking drops (Uzbek drop minus English drop, where each
  drop is paired within question between ``title_prefix`` and ``title_masked``),
  bootstrapped the same way.

Intervals are descriptive, unadjusted for the number of comparisons, and
conditional on the frozen corpus and question set.

    python scripts/analyze_title_masking_gaps.py          # write language_gaps.json
    python scripts/analyze_title_masking_gaps.py --check  # recompute and compare (CI)
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'research_outputs/title_masking'
RUNS = ('frozen', 'frozen_retrievers')
OUT = BASE / 'language_gaps.json'
K = 3


def percentile_interval(samples):
    samples = sorted(samples)
    n = len(samples)
    return [round(samples[int(0.025 * n)], 1), round(samples[int(0.975 * n) - 1], 1)]


def unpaired_gap(a, b, resamples, seed):
    rng = random.Random(seed)
    stats = []
    for _ in range(resamples):
        ra = [a[rng.randrange(len(a))] for _ in a]
        rb = [b[rng.randrange(len(b))] for _ in b]
        stats.append(100 * (sum(ra) / len(ra) - sum(rb) / len(rb)))
    return percentile_interval(stats)


def load_hits():
    """Return {(run, method, language, variant): {question_id: hit}} and the bootstrap config."""
    hits, config = {}, None
    for run in RUNS:
        directory = BASE / run
        if not (directory / 'metrics.json').exists():
            continue
        payload = json.loads((directory / 'metrics.json').read_text())
        if payload['approximate']:
            continue
        config = config or payload['provenance']['config']
        for line in (directory / 'predictions.jsonl').read_text().splitlines():
            p = json.loads(line)
            if p['questions'] != 'original':
                continue
            key = (run, p['method'], p['language'], p['passage_variant'])
            hits.setdefault(key, {})[p['id']] = int(bool(set(p['source_doc_ids']) & set(p['retrieved_doc_ids'][:K])))
    return hits, config


def analyse():
    hits, config = load_hits()
    resamples, seed = config['bootstrap_resamples'], config['bootstrap_seed']
    rows = []
    combos = sorted({(run, method, variant) for run, method, _, variant in hits})
    for run, method, variant in combos:
        en, uz = hits[(run, method, 'en', variant)], hits[(run, method, 'uz', variant)]
        a, b = [en[q] for q in sorted(en)], [uz[q] for q in sorted(uz)]
        rows.append(dict(run=run, method=method, variant=variant, measure='en_minus_uz_hit@3', n_en=len(a), n_uz=len(b),
                         value_pp=round(100 * (sum(a) / len(a) - sum(b) / len(b)), 1),
                         ci95_pp=unpaired_gap(a, b, resamples, seed)))
    for run, method in sorted({(run, method) for run, method, _ in combos}):
        drops = {}
        for language in ('en', 'uz'):
            before, after = hits[(run, method, language, 'title_prefix')], hits[(run, method, language, 'title_masked')]
            drops[language] = [before[q] - after[q] for q in sorted(before)]
        rows.append(dict(run=run, method=method, variant='title_prefix_to_title_masked', measure='uz_drop_minus_en_drop',
                         n_en=len(drops['en']), n_uz=len(drops['uz']),
                         value_pp=round(100 * (sum(drops['uz']) / len(drops['uz']) - sum(drops['en']) / len(drops['en'])), 1),
                         ci95_pp=unpaired_gap(drops['uz'], drops['en'], resamples, seed)))
    return dict(k=K, resamples=resamples, seed=seed,
                note='Descriptive unpaired source-group bootstrap; unadjusted for multiple comparisons; conditional on the frozen corpus.',
                rows=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true', help='Recompute and compare with the committed file')
    args = parser.parse_args()
    result = analyse()
    if args.check:
        committed = json.loads(OUT.read_text())
        assert committed == result, 'language_gaps.json does not match a fresh recomputation'
        print(f"Verified {len(result['rows'])} between-language rows.")
        return
    OUT.write_text(json.dumps(result, indent=2) + '\n')
    for r in result['rows']:
        print(r['run'], r['method'], r['variant'], r['measure'], r['value_pp'], r['ci95_pp'])


if __name__ == '__main__':
    main()
