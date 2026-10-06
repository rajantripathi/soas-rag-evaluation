import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts.run_reproducible_pilot import digest, git_commit, rank, removal_ids, write


class PilotTests(unittest.TestCase):
    def test_ranking_uses_stable_ids_and_excludes_removed_sources(self):
        self.assertEqual(rank([1, 1, 2], ['en:2', 'en:1', 'en:3'], {'en:3'}, 3), ['en:1', 'en:2'])

    def test_zero_scores_still_produce_ranked_candidates(self):
        self.assertEqual(rank([0,0], ['uz:2','uz:1'], k=1), ['uz:1'])

    def test_removal_is_source_based_repeatable_and_restorable(self):
        ids = {f'en:{n}' for n in range(100)}
        removed = removal_ids(ids, 42)
        self.assertEqual(len(removed), 50)
        self.assertEqual(removed, removal_ids(reversed(sorted(ids)), 42))
        self.assertNotEqual(removed, removal_ids(ids, 43))
        self.assertEqual((ids - removed) | removed, ids)

    def test_prefix_and_revision_change_cache_identity(self):
        self.assertNotEqual(digest(['query: hello','revision1']), digest(['hello','revision1']))
        self.assertNotEqual(digest(['query: hello','revision1']), digest(['query: hello','revision2']))

    def test_atomic_json_preserves_unicode(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'nested'/'test.json'
            write(path, {'title':'Oʻzbekiston'})
            self.assertEqual(json.loads(path.read_text()), {'title':'Oʻzbekiston'})
            self.assertFalse(path.with_suffix('.json.tmp').exists())

    def test_git_commit_uses_git_worktree_resolution(self):
        with patch('scripts.run_reproducible_pilot.subprocess.check_output', return_value='a'*40+'\n') as call:
            self.assertEqual(git_commit(), 'a'*40)
            self.assertEqual(call.call_args.args[0], ['git', 'rev-parse', 'HEAD'])


if __name__ == '__main__':
    unittest.main()
