"""Recompute title-masking metrics and check frozen baseline ranks (stdlib only)."""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verify(directory):
    payload = json.loads((directory / 'metrics.json').read_text())
    predictions = [json.loads(line) for line in (directory / 'predictions.jsonl').read_text().splitlines()]
    labels = {q['id']: q for q in map(json.loads, (ROOT / 'research_outputs/reproducible_pilot/evaluation_labels.jsonl').read_text().splitlines())}
    expected_ids = set(labels) - set(payload['provenance']['excluded_question_ids'])
    for variant in payload['variants']:
        for method in payload['methods']:
            rows = [p for p in predictions if p['passage_variant'] == variant and p['method'] == method]
            assert {p['id'] for p in rows} == expected_ids, 'Incomplete predictions'
    for row in predictions:
        label = labels[row['id']]
        assert row['source_doc_ids'] == label['source_doc_ids']
        assert row['language'] == label['language']
        assert row['questions'] == ('alternate' if label['variant'] else 'original')
        assert len(row['retrieved_doc_ids']) == len(set(row['retrieved_doc_ids'])) == 5
    keys = [(p['language'], p['method'], p['passage_variant'], p['id']) for p in predictions]
    assert len(keys) == len(set(keys)), 'Duplicate predictions'
    for cell in payload['results']:
        rows = [p for p in predictions if p['language'] == cell['language'] and p['method'] == cell['method']
                and p['passage_variant'] == cell['variant'] and p['questions'] == cell['questions']]
        assert len(rows) == cell['n']
        for k in (1, 3, 5):
            hits = sum(bool(set(p['source_doc_ids']) & set(p['retrieved_doc_ids'][:k])) for p in rows)
            assert round(100 * hits / len(rows), 1) == cell[f'hit@{k}'], (cell, k)
    for interval in payload['title_masking_drop']:
        rows = [p for p in predictions if p['language'] == interval['language'] and p['method'] == interval['method'] and p['questions'] == 'original']
        hit = lambda p: int(bool(set(p['source_doc_ids']) & set(p['retrieved_doc_ids'][:3])))
        a = {p['id']: hit(p) for p in rows if p['passage_variant'] == 'title_prefix'}
        b = {p['id']: hit(p) for p in rows if p['passage_variant'] == 'title_masked'}
        delta = [a[q] - b[q] for q in a]
        n = len(delta)
        assert interval['n'] == n
        assert interval['drop_pp'] == round(100 * sum(delta) / n, 1)
        config = payload['provenance']['config']
        rng = random.Random(config['bootstrap_seed'])
        samples = sorted(sum(delta[rng.randrange(n)] for _ in range(n)) / n for _ in range(config['bootstrap_resamples']))
        expected = [round(100 * samples[int(0.025 * len(samples))], 1), round(100 * samples[int(0.975 * len(samples)) - 1], 1)]
        assert interval['ci95_pp'] == expected
    if not payload['approximate']:
        for language in ('en', 'uz'):
            for method in payload['methods']:
                baseline = [json.loads(line) for line in (ROOT / 'research_outputs/reproducible_pilot' /
                            f'predictions_{language}_{method}.jsonl').read_text().splitlines()]
                expected = {p['id']: p['retrieved_doc_ids'] for p in baseline if p['condition'] == 'full'}
                actual = {p['id']: p['retrieved_doc_ids'] for p in predictions if p['language'] == language
                          and p['method'] == method and p['passage_variant'] == 'title_prefix'}
                assert expected == actual, f'Frozen baseline ranks differ: {language} {method}'
    print(f"Verified {len(payload['results']) * 3} metric cells and frozen baseline ranks.")


if __name__ == '__main__':
    verify(ROOT / 'research_outputs/title_masking/frozen')
