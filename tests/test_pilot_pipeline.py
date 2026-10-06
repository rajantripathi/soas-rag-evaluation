"""Tiny synthetic report pipeline; no downloads or real model required."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import run_reproducible_pilot as pilot


@unittest.skipUnless(importlib.util.find_spec('numpy'), 'Install pilot dependencies for numerical integration tests')
class PipelineTests(unittest.TestCase):
    def fixture(self, directory):
        labels=[]; predictions=[]; docs=[]
        for language in ('en','uz'):
            docs += [dict(language=language,page_id=n) for n in (1,2,3)]
            masks={'full': [], **{f'removed_{s}':[f'{language}:1'] for s in range(42,47)}}
            pilot.write(directory/f'conditions_{language}.json',masks)
            for n in (1,2):
                for variant in (False,True):
                    id=f'{language}_{n}'+('_v4_0' if variant else '')
                    target=f'{language}:{n}'
                    labels.append(dict(id=id,language=language,domain='history',question='question',source_doc_ids=[target],variant=variant,quality_flag=None))
                    for method in ('bm25','e5_prefixed','e5_unprefixed'):
                        for condition,excluded in masks.items():
                            available=target not in excluded
                            predictions.append(dict(id=id,language=language,domain='history',variant=variant,
                                                    source_group=target,quality_flag=None,method=method,condition=condition,
                                                    target_available=available,retrieved_doc_ids=[target] if available else [f'{language}:3']))
        pilot.write(directory/'source_manifest.json',{'documents':docs})
        (directory/'evaluation_labels.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in labels))
        path=directory/'predictions_fixture.jsonl'
        path.write_text(''.join(json.dumps(r)+'\n' for r in predictions))
        return path,predictions

    def test_end_to_end_metrics_and_paired_intervals(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory=Path(temporary)
            self.fixture(directory)
            with patch.object(pilot,'PUBLIC',directory):
                pilot.report()
            from scripts.verify_pilot_artifacts import verify
            verify(directory)
            metrics=pilot.read(directory/'metrics.json')
            original=[m for m in metrics if m['subset']=='original' and m['k']==3]
            self.assertEqual(len(original),36)
            self.assertTrue(all(m['hit_rate']==(1 if m['condition']=='full' else .5) for m in original))
            self.assertTrue(all(m['conditional_hit_rate']==1 for m in original))
            self.assertTrue(all(r['difference']==.5 for r in pilot.read(directory/'paired_intervals.json')))

    def test_missing_predictions_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory=Path(temporary); path,values=self.fixture(directory)
            path.write_text(''.join(json.dumps(r)+'\n' for r in values[:-1]))
            with patch.object(pilot,'PUBLIC',directory), self.assertRaisesRegex(ValueError,'Missing or duplicate'):
                pilot.report()

    def test_removed_source_cannot_be_returned(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory=Path(temporary); path,values=self.fixture(directory)
            next(p for p in values if not p['target_available'])['retrieved_doc_ids']=['en:1']
            path.write_text(''.join(json.dumps(r)+'\n' for r in values))
            with patch.object(pilot,'PUBLIC',directory), self.assertRaisesRegex(ValueError,'Invalid, removed'):
                pilot.report()


if __name__=='__main__': unittest.main()
