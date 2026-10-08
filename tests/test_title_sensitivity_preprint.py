import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import analyze_title_masking_gaps as gaps  # noqa: E402
import write_title_sensitivity_manuscript as manuscript  # noqa: E402


class TitleSensitivityPreprintTests(unittest.TestCase):
    def test_language_gaps_match_predictions(self):
        committed = json.loads(gaps.OUT.read_text())
        self.assertEqual(committed, gaps.analyse())

    def test_unpaired_gap_is_deterministic_and_degenerate_at_ceiling(self):
        self.assertEqual(gaps.unpaired_gap([1] * 10, [1] * 8, 200, 42), [0.0, 0.0])
        a, b = [1, 0, 1, 1], [0, 0, 1, 0]
        self.assertEqual(gaps.unpaired_gap(a, b, 500, 42), gaps.unpaired_gap(a, b, 500, 42))

    def test_manuscript_matches_metrics(self):
        frozen, extra, methods, cells, drops, gap = manuscript.collect()
        fresh = manuscript.write(frozen, extra, methods, cells, drops, gap, manuscript.passage_stats(), save=False)
        self.assertEqual(manuscript.PAPER.read_text(), fresh)
        self.assertNotIn('—', fresh, 'No em dashes in the manuscript')
        self.assertIn('79.2%', fresh)


if __name__ == '__main__':
    unittest.main()
