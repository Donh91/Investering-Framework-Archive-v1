#!/usr/bin/env python3
"""Read-only historical vote-removal diagnostic for existing #1596 owner.
No forecast issuance, grading, model calls, dependencies, or live authority.
"""
import argparse
import json
import subprocess
from pathlib import Path

SNAPSHOT = '0e8c386b5a4ee57a5500cb3d02951c9e398b1b4f'
PREFIX = '04_MARKET_LEARNING/intraday_execution/'
SCORER = 'scripts/intraday_execution/shadow_direction_confidence.py'
CONFIG_BLOB = 'ec780123f36c36f192be604f2432f22fd964c07b'
SCORER_BLOB = '759623ed7be5f81869083bab35afd514e4640c32'
CASES = (
    ('2026/09/15/20260915T180730Z.json', 'efbf2df9b6df90f47a62b1172e62ab7bcfcec829', 'ad5af3b51fb93066bb0b05fd9b9af13b95017cac'),
    ('2026/09/16/20260916T011955Z.json', 'f93bc739ff13574fc4c55767ffeb647ecb1de517', '38147d78ef783db7b422c844027bebc383f1a350'),
)
GROUPS = {
    'price': ('return_1h', 'return_4h', 'session_vwap', 'momentum_acceleration'),
    'taker': ('taker_balance', 'taker_change'),
    'cross': ('ethbtc_1h', 'breadth_balance'),
}


def checked_blob(root, ref, path, expected):
    raw = subprocess.check_output(['git', '--no-replace-objects', 'show', f'{ref}:{path}'], cwd=root)
    actual = subprocess.check_output(['git', 'hash-object', '--stdin'], cwd=root, input=raw).decode().strip()
    if actual != expected:
        raise ValueError('BLOB_MISMATCH: ' + path)
    return raw


def replay(votes, minimum, margin):
    names = [v['family'] for v in votes]
    if len(names) != len(set(names)):
        raise ValueError('DUPLICATE_FAMILY')
    if any(v['direction'] not in ('UP', 'DOWN', 'FLAT', 'MISSING') for v in votes):
        raise ValueError('UNKNOWN_DIRECTION')
    up = sum(v['direction'] == 'UP' for v in votes)
    down = sum(v['direction'] == 'DOWN' for v in votes)
    n = up + down
    winner = max(up, down)
    direction = 'NO_EDGE' if n < minimum or up == down or abs(up-down) < margin else ('UP' if up > down else 'DOWN')
    return {'direction': direction, 'calibration_key': f'{winner}_of_{n}',
            'evidence_agreement_pct': round(winner/n*100, 2) if n else None}


def diagnose(target, cfg):
    votes = target['votes']
    args = (cfg['minimum_direction_families'], cfg['minimum_vote_margin'])
    baseline = replay(votes, *args)
    if any(target[k] != v for k, v in baseline.items()):
        raise ValueError('FROZEN_BASELINE_MISMATCH')
    return {'baseline': baseline, 'probability_at_issue': target['frozen_calibrated_probability_pct'],
            'interventions': {k: {'removed': sum(v['family'] in group for v in votes),
                                  **replay([v for v in votes if v['family'] not in group], *args)}
                              for k, group in GROUPS.items()}}


def run(root):
    rows = []
    for suffix, blob, producer in CASES:
        path = PREFIX + 'direction_predictions/' + suffix
        frozen = json.loads(checked_blob(root, SNAPSHOT, path, blob))
        if frozen['production_context']['commit_sha'] != producer:
            raise ValueError('PRODUCER_MISMATCH')
        checked_blob(root, producer, SCORER, SCORER_BLOB)
        cfg = json.loads(checked_blob(root, producer, PREFIX+'config.json', CONFIG_BLOB))['shadow_direction_confidence']
        for horizon, group in sorted(frozen['horizons'].items()):
            for asset, target in sorted(group['targets'].items()):
                rows.append({'path': path, 'blob': blob, 'producer': producer, 'horizon': horizon,
                             'asset': asset, **diagnose(target, cfg)})
    if len(rows) != 12:
        raise ValueError('ROSTER_MISMATCH')
    return {'status': 'HISTORICAL_VOTE_AGGREGATION_REPLAY_ONLY', 'rows': rows,
            'market_edge': 'UNTESTED', 'production_authority': False}


def self_test():
    def votes(*dirs):
        return [{'family': str(i), 'direction': d} for i, d in enumerate(dirs)]
    cases = [(('UP',)*6, 'UP'), (('UP',)*4+('DOWN',)*2, 'UP'),
             (('UP',)*4+('DOWN',)*4, 'NO_EDGE'), (('UP',)*3, 'NO_EDGE'),
             (('DOWN',)*4+('UP',)*2, 'DOWN'), (('MISSING',)*4, 'NO_EDGE')]
    for ds, expected in cases:
        assert replay(votes(*ds), 4, 2)['direction'] == expected
    for invalid in ([{'family':'a','direction':'UP'}]*2, [{'family':'a','direction':'OTHER'}]):
        try:
            replay(invalid, 4, 2)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid input accepted')
    assert replay(votes('UP','UP','UP','UP','DOWN','DOWN'),4,2)['evidence_agreement_pct'] == 66.67
    print('9/9 local self-test checks PASS (synthetic)')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
    else:
        print(json.dumps(run(args.root), indent=2, sort_keys=True))
