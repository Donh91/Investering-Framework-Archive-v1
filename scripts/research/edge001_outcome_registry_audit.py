#!/usr/bin/env python3
"""Read-only EDGE-001 contract audit; never consumes warning data."""
import argparse
import hashlib
import importlib.util
import json
from datetime import datetime, timedelta
from pathlib import Path


def stamp(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def audit(root, registry_path, generator_path):
    spec = importlib.util.spec_from_file_location('edge_generator', generator_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    data = json.loads(registry_path.read_text())
    checks = []
    def check(name, valid, detail=None):
        checks.append({'check': name, 'status': 'PASS' if valid else 'FAIL', 'detail': detail})
    parent = root / module.PARENT
    source = root / module.SRC
    check('source_hash', data['source_sha256'] == hashlib.sha256(source.read_bytes()).hexdigest() == 'f3adc5716343c3a6e7dca812f4ca2d607abb5dd37495a7fa268ab41e5e889bd8')
    check('immutable_parent_v1', data['parent_v1_sha256'] == hashlib.sha256(parent.read_bytes()).hexdigest() == 'c8f8aa30502b909f016787161a661b2183f8ceef61c820cea00c53c5b70f71db')
    check('no_warning_join', data['framework_warning_data_joined'] is False)
    rows = module.load(source)
    ids = []
    for window in module.WINDOWS:
        primary = []
        for asset in module.GRIDS:
            tape = module.points(rows, window, asset)
            lane = data['windows'][window][asset]
            check(f'{window}/{asset}/hourly_continuity', all(b['t'] - a['t'] == timedelta(hours=1) for a, b in zip(tape, tape[1:]) if a['seg'] == b['seg']))
            check(f'{window}/{asset}/positive_unique_prices', all(p['v'] > 0 for p in tape) and len({p['t'] for p in tape}) == len(tape))
            for label in ('P1_fires', 'P2_fires'):
                ids.extend(f['fire_id'] for f in lane[label])
            for grid, cell in lane['grids'].items():
                ids.extend(e['episode_id'] for e in cell['episodes'])
                ids.extend(f['family_id'] for f in cell['families_14d'])
                # Reference extraction runs each segment independently; an open
                # threshold-crossed tail must be retained at EVERY segment end.
                segments = []
                for point in tape:
                    if not segments or segments[-1][-1]['seg'] != point['seg']:
                        segments.append([])
                    segments[-1].append(point)
                reference = []
                threshold = int(grid) / 100
                for segment in segments:
                    peak = segment[0]; cross = None; trough = None
                    for point in segment[1:]:
                        if cross is None:
                            if point['v'] > peak['v']: peak = point
                            elif point['v'] <= peak['v'] * (1 - threshold): cross = point; trough = point
                        elif point['v'] < trough['v']: trough = point
                        elif point['v'] >= trough['v'] * (1 + threshold):
                            reference.append((peak['t'], cross['t'], trough['t'], point['t'], False, None, peak['seg']))
                            peak = point; cross = None; trough = None
                    if cross is not None:
                        reference.append((peak['t'], cross['t'], trough['t'], None, True, segment[-1]['t'], peak['seg']))
                observed = [(stamp(e['peak_utc']), stamp(e['threshold_cross_utc']), stamp(e['trough_utc']), stamp(e['rebound_utc']) if e['rebound_utc'] else None, e['right_censored'], stamp(e['censor_utc']) if e['censor_utc'] else None, e['continuity_segment_id']) for e in cell['episodes']]
                check(f'{window}/{asset}/{grid}/all_episodes_and_censoring', observed == reference)
                check(f'{window}/{asset}/{grid}/censor_reason', all(not e['right_censored'] or e['censor_reason'] == 'CONTINUITY_SEGMENT_END_BEFORE_REBOUND' for e in cell['episodes']))
                groups = []
                for ep in sorted(cell['episodes'], key=lambda e: e['peak_utc']):
                    if groups and ep['continuity_segment_id'] == groups[-1][0]['continuity_segment_id'] and stamp(ep['peak_utc']) - max(stamp(e['trough_utc']) for e in groups[-1]) < timedelta(days=14):
                        groups[-1].append(ep)
                    else: groups.append([ep])
                check(f'{window}/{asset}/{grid}/trough_families', [set(f['episode_ids']) for f in cell['families_14d']] == [{e['episode_id'] for e in g} for g in groups])
                if int(grid) == module.PRIMARY[asset]: primary.extend(cell['families_14d'])
            ids.extend(c['control_id'] for c in lane.get('V_reversal_controls_primary10', []))
        # Independent graph connected components for overlap-only clusters.
        components = []
        remaining = {f['family_id']: f for f in primary}
        while remaining:
            first = remaining.pop(next(iter(remaining))); component = [first]
            changed = True
            while changed:
                changed = False
                for fid, candidate in list(remaining.items()):
                    if any(stamp(candidate['first_peak_utc']) <= stamp(f['family_end_trough_utc']) and stamp(f['first_peak_utc']) <= stamp(candidate['family_end_trough_utc']) for f in component):
                        component.append(remaining.pop(fid)); changed = True
            components.append(frozenset(f['family_id'] for f in component))
        clusters = data['windows'][window]['primary_cross_asset_clusters']
        ids.extend(c['cluster_id'] for c in clusters)
        check(f'{window}/overlap_only_transitive_clusters', set(components) == {frozenset(c['family_ids']) for c in clusters})
    check('global_id_uniqueness_including_fires_and_clusters', len(ids) == len(set(ids)), {'total': len(ids)})
    base = stamp('2020-01-01T00:00:00Z')
    def tape(values, segments=None):
        return [{'t': base + timedelta(hours=i), 'v': v, 'seg': segments[i] if segments else 'A'} for i, v in enumerate(values)]
    fixtures = [
        ('control_end_of_tape', tape([100, 94, 95]), 'CONTROL_CENSORED'),
        ('control_segment_gap', tape([100, 94, 95, 100], ['A', 'A', 'A', 'B']), 'CONTROL_CENSORED'),
        ('control_cross_at_p1_fire', tape([100, 89, 100]), None),
        ('control_valid_recovery', tape([100, 94, 100]), 'V_REVERSAL'),
        ('control_cross_after_fire', tape([100, 94, 89, 100]), None),
    ]
    for name, points, expected in fixtures:
        fires = module.comparator_fires(points, .05, 'FIXTURE', 'BTCUSDT', 'P1')
        controls = module.controls(points, fires, 'FIXTURE', 'BTCUSDT', .1)
        check(name, not controls if expected is None else len(controls) == 1 and controls[0]['control_status'] == expected, controls)
    failures = [c['check'] for c in checks if c['status'] == 'FAIL']
    return {'contract': 'EDGE001_OUTCOME_REGISTRY_AUDIT_v1', 'status': 'PASS' if not failures else 'FAIL', 'registry_sha256': hashlib.sha256(registry_path.read_bytes()).hexdigest(), 'checks': checks, 'failed_checks': failures, 'authority': 'RESEARCH_ONLY', 'framework_warning_data_joined': False, 'T2B_ready': not failures, 'claim_level': 'HYPOTHESIS', 'live_exit_rule': 'NONE'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo-root', type=Path, default=Path('.'))
    parser.add_argument('--registry', type=Path, required=True)
    parser.add_argument('--generator', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = audit(args.repo_root, args.registry, args.generator)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: report[k] for k in ('status', 'failed_checks', 'registry_sha256', 'T2B_ready')}))
    raise SystemExit(0 if report['status'] == 'PASS' else 1)
