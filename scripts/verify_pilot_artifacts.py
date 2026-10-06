"""Independently recompute saved pilot metrics with the standalone public scorer."""
from collections import defaultdict
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.compute_retrieval_recall import score_recall


def verify(directory):
    directory=Path(directory)
    labels={r['id']:r for r in [json.loads(x) for x in (directory/'evaluation_labels.jsonl').read_text().splitlines()]}
    groups=defaultdict(dict)
    for path in directory.glob('predictions_*.jsonl'):
        for line in path.read_text().splitlines():
            p=json.loads(line)
            key=(p['language'],p['method'],p['condition'])
            if p['id'] in groups[key]: raise ValueError('Duplicate prediction')
            groups[key][p['id']]=p['retrieved_doc_ids']
    metrics=json.loads((directory/'metrics.json').read_text())
    if not metrics: raise ValueError('No metrics')
    for expected in metrics:
        selected=[r for r in labels.values() if r['language']==expected['language'] and
                  (r['variant'] if expected['subset']=='variants' else not r['variant']) and
                  (expected['subset']!='unflagged_original' or not r['quality_flag'])]
        predictions=groups[(expected['language'],expected['method'],expected['condition'])]
        actual=score_recall(selected,predictions,expected['k'])
        assert actual['missing_predictions']==0
        assert actual['rows']==expected['rows'] and actual['hits']==expected['hits']
        assert abs(actual['recall']-expected['hit_rate'])<1e-12
    print(f'Independently verified {len(metrics)} metric cells using the standalone scorer')


if __name__=='__main__': verify(ROOT/'research_outputs/reproducible_pilot')
