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

class FrozenAcquisitionTests(unittest.TestCase):
    def test_reconstruction_requests_exact_revision_and_checks_hashes(self):
        from scripts import run_reproducible_pilot as pilot
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp);public=base/'public';cache=base/'cache'
            doc=dict(language='en',page_id=7,revision_id=900,raw_sha256='raw',text_sha256=digest(b'text'),url='https://example.org/?oldid=900')
            write(public/'source_manifest.json',{'documents':[doc]})
            with patch.object(pilot,'PUBLIC',public),patch.object(pilot,'CACHE',cache),patch.object(pilot,'api',return_value={'query':{'pages':[{}]}}) as fetch,patch.object(pilot,'parse_page',return_value={**doc,'text':'text'}):
                pilot.acquire(1000)
                self.assertEqual(fetch.call_args.args[0], 'en')
                self.assertEqual(fetch.call_args.args[1]['revids'], '900')
                self.assertEqual(json.loads((cache/'articles/en_7.json').read_text())['text'],'text')

    def test_changed_revision_content_is_not_silently_accepted(self):
        from scripts import run_reproducible_pilot as pilot
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp);public=base/'public';cache=base/'cache'
            doc=dict(language='en',page_id=7,revision_id=900,raw_sha256='expected',text_sha256='expected',url='https://example.org/?oldid=900')
            write(public/'source_manifest.json',{'documents':[doc]})
            with patch.object(pilot,'PUBLIC',public),patch.object(pilot,'CACHE',cache),patch.object(pilot,'api',return_value={'query':{'pages':[{}]}}),patch.object(pilot,'parse_page',return_value={**doc,'raw_sha256':'changed'}):
                with self.assertRaisesRegex(RuntimeError,'Frozen revision unavailable'):
                    pilot.acquire(1000)


if __name__ == '__main__':
    unittest.main()
