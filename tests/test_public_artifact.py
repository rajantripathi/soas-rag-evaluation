"""Dependency-free checks of the public scoring contract and release data."""
import json
from collections import Counter
from pathlib import Path
import unittest

from scripts.compute_retrieval_recall import (
    load_jsonl, score_recall, validate_dataset_rows,
)

ROOT = Path(__file__).resolve().parents[1]


class RetrievalScoringTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            dict(id='a', language='en', domain='history', question='A?', source_doc_ids=['x', 'y']),
            dict(id='b', language='uz', domain='culture', question='B?', source_doc_ids=['z']),
        ]

    def test_rank_cutoff_and_any_source_hit(self):
        predictions = {'a': ['irrelevant', 'y'], 'b': ['z']}
        self.assertEqual(score_recall(self.rows, predictions, 1)['recall'], 0.5)
        self.assertEqual(score_recall(self.rows, predictions, 2)['recall'], 1.0)

    def test_missing_prediction_counts_as_miss_and_slices_remain_visible(self):
        result = score_recall(self.rows, {'a': ['x', 'x']}, 3)
        self.assertEqual(result['hits'], 1)
        self.assertEqual(result['missing_predictions'], 1)
        self.assertEqual(result['by_language']['uz']['recall'], 0)
        self.assertEqual(result['by_domain']['history']['recall'], 1)

    def test_invalid_cutoff_and_duplicate_rows_rejected(self):
        with self.assertRaises(ValueError):
            score_recall(self.rows, {}, 0)
        with self.assertRaises(ValueError):
            validate_dataset_rows([self.rows[0], self.rows[0]])


class PublicReleaseTests(unittest.TestCase):
    def test_release_shape_balance_and_preview(self):
        rows = load_jsonl(ROOT / 'hf_dataset/manual_eval_v5_retrieval_only.jsonl')
        preview = load_jsonl(ROOT / 'hf_dataset/manual_eval_v5_sample.jsonl')
        validate_dataset_rows(rows)
        self.assertEqual(len(rows), 400)
        self.assertEqual(len(preview), 30)
        counts = Counter((row['language'], row['domain']) for row in rows)
        self.assertEqual(counts, Counter({(language, domain): 50
            for language in ('en', 'uz')
            for domain in ('governance', 'history', 'institutions', 'culture')}))
        allowed = {'id', 'language', 'domain', 'question', 'source_doc_ids',
                   'answerable', 'cultural_specificity', 'source_title', 'difficulty', 'quality_flag'}
        for row in rows:
            self.assertEqual(set(row), allowed)
            self.assertTrue(row['source_doc_ids'])
            self.assertTrue(all(isinstance(value, str) for value in row['source_doc_ids']))
        by_id = {row['id']: row for row in rows}
        for row in preview:
            self.assertEqual(row, by_id[row['id']])


if __name__ == '__main__':
    unittest.main()
