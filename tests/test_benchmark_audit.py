import hashlib
import json
from pathlib import Path
import unittest
from scripts.audit_public_benchmark import audit, render


class BenchmarkAuditTests(unittest.TestCase):
    def row(self, id, language, question, targets):
        return dict(id=id, language=language, question=question, source_doc_ids=targets,
                    quality_flag=None, source_title=None, domain='history')

    def test_targets_are_language_scoped_and_paraphrases_are_grouped(self):
        rows = [self.row('a', 'en', 'First?', ['1']), self.row('b', 'en', 'Other?', ['1']),
                self.row('c', 'uz', 'First?', ['1'])]
        report = audit(rows)
        self.assertEqual(report['language_scoped_source_targets'], 2)
        self.assertEqual(report['by_language']['en']['rows_per_target_distribution'], {2: 1})
        self.assertEqual(report['duplicate_question_rows'], 0)

    def test_overlapping_multi_target_schema_is_rejected(self):
        with self.assertRaises(ValueError):
            audit([self.row('a', 'en', 'A?', ['1', '2'])])

    def test_checked_in_audit_matches_release_bytes(self):
        root = Path(__file__).resolve().parents[1]
        name = "hf_dataset/manual_eval_v5_retrieval_only.jsonl"
        data = (root / name).read_bytes()
        report = audit([json.loads(line) for line in data.decode("utf-8").splitlines()])
        report.update(input=name, sha256=hashlib.sha256(data).hexdigest())
        self.assertEqual(render(report), (root / "research_outputs/public_benchmark_structure.md").read_text())

    def test_duplicate_ids_rejected(self):
        row = self.row('a', 'en', 'A?', ['1'])
        with self.assertRaises(ValueError):
            audit([row, row])


if __name__ == '__main__':
    unittest.main()
