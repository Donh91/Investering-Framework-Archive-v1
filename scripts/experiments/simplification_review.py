#!/usr/bin/env python3
"""Read-only alias and outcome review; never changes lifecycle state."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from experiment_lifecycle_scientific_admission import semantic_spec


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def review(registry, candidates, high_observation_min=None):
    if high_observation_min is not None and (type(high_observation_min) is not int or high_observation_min < 1):
        raise ValueError('positive observation review threshold required')
    groups = defaultdict(list)
    rows = []
    registry_variants = defaultdict(list)
    for row in registry['candidates']:
        registry_variants[row['candidate_id']].append(row)
    for cid, variants in sorted(registry_variants.items()):
        keys = set().union(*(r.keys() for r in variants))
        row = {k: variants[0].get(k) if all(r.get(k) == variants[0].get(k) for r in variants) else 'UNKNOWN' for k in keys}
        source = candidates.get(cid)
        item = {k: row.get(k, 'UNKNOWN') for k in ('candidate_id', 'state', 'observation_count', 'matured_outcome_count', 'kind')}
        item['forecast_count'] = len(row['forecast_ids']) if isinstance(row.get('forecast_ids'), list) else 'UNKNOWN'
        item['recommendation'] = 'NEEDS_MORE_OUTCOMES'
        item['flags'] = ['REPEATED_REGISTRY_ID_REVIEW'] if len(variants) > 1 else []
        item['registry_variants'] = [{'sha256': digest(r), 'created_at_utc': r.get('created_at_utc', 'UNKNOWN')} for r in variants]
        if source is None or source.get('spec') is None:
            item.update(source_status='UNAVAILABLE' if source is None else 'CONFLICTING_SPECIFICATIONS', recommendation='WAIT_FOR_DATA')
            if source is not None:
                item['source_provenance'] = source['source_variants']
                item['flags'].append('CONFLICTING_FROZEN_SOURCE_NO_ALIAS_INFERENCE')
        else:
            spec = source['spec']
            # Reuse owner path/parameter normalization. Preserve hypothesis,
            # falsifier and unit semantics as separate identity dimensions.
            identity = {'mechanical': semantic_spec(spec), 'hypothesis': spec.get('hypothesis'),
                        'falsifier': spec.get('falsifier'), 'unit_contract': spec.get('target_unit_contract_version')}
            item.update(source_status='BOUND', source_sha256=digest(source),
                        source_provenance=source.get('source_variants', source.get('source', {})),
                        target_metric_path=spec.get('target_metric_path'),
                        normalized_spec=identity['mechanical'], review_group=digest(identity))
            # Incomplete identities are never grouped by null equality.
            if all(spec.get(k) is not None for k in ('kind', 'hypothesis', 'falsifier', 'horizon_days')):
                groups[item['review_group']].append(cid)
            else:
                item['flags'].append('INCOMPLETE_IDENTITY_NO_ALIAS_INFERENCE')
        if row.get('state') in {'DATA_BLOCKED', 'WAITING_FOR_DATA'}:
            item['recommendation'] = 'WAIT_FOR_DATA'
        elif 'MAPPING' in str(row.get('state', '')):
            item['recommendation'] = 'WAIT_FOR_MAPPING'
        elif 'QUARANTINED' in str(row.get('state', '')):
            item['recommendation'] = 'WAIT_FOR_MAPPING'
            item['flags'].append('OWNER_QUARANTINE_PRESERVED_NO_REQUALIFICATION')
        zero = row.get('state') == 'INCUBATING' and row.get('matured_outcome_count') == 0 and item['forecast_count'] == 0
        if zero:
            item['flags'].append('ZERO_FORECAST_ZERO_OUTCOME_INCUBATION')
            n = row.get('observation_count')
            if high_observation_min is not None and type(n) is int and n >= high_observation_min:
                item['flags'].append('HIGH_OBSERVATION_REVIEW_ONLY')
        rows.append(item)
    aliases = []
    by_id = {r['candidate_id']: r for r in rows}
    for key, ids in sorted(groups.items()):
        if len(ids) < 2:
            continue
        ids.sort()
        inconclusive = [i for i in ids if by_id[i]['state'] == 'MATURED_INCONCLUSIVE']
        aliases.append({'review_group': key, 'candidate_ids': ids,
                        'recommendation': 'MERGE_REVIEW', 'automatic_merge': False,
                        'repeated_matured_inconclusive_ids': inconclusive if len(inconclusive) > 1 else []})
        for cid in ids:
            by_id[cid]['flags'].append('ALIAS_REVIEW_NOT_DUPLICATE_VERDICT')
    return {'contract': 'EXPERIMENT_SIMPLIFICATION_REVIEW_v1',
            'authority': 'SHADOW_ONLY_NO_MUTATION_NO_RETIREMENT_NO_PROMOTION_NO_WEIGHT',
            'source_registry_sha256': digest(registry), 'source_generated_at_utc': registry.get('generated_at_utc', 'UNKNOWN'),
            'candidate_count': len(rows), 'source_registry_row_count': len(registry['candidates']), 'high_observation_review_min': high_observation_min if high_observation_min is not None else 'UNSPECIFIED',
            'threshold_semantics': 'EXPLICIT_REVIEW_FILTER_ONLY_NOT_MARKET_OR_LIFECYCLE_RULE',
            'alias_groups': aliases, 'candidates': sorted(rows, key=lambda r: r['candidate_id'])}


def load_candidates(root):
    variants = defaultdict(list)
    for path in sorted(root.rglob('*.json')):
        raw = path.read_bytes()
        obj = json.loads(raw)
        if obj.get('contract') == 'EXPERIMENT_CANDIDATE_v1':
            variants[obj['candidate_id']].append((path, raw, obj))
    candidates = {}
    for cid, items in variants.items():
        specs = {digest(o['spec']) for _, _, o in items}
        provenance = [{'path': p.relative_to(root).as_posix(), 'bytes': len(raw),
                       'sha256': hashlib.sha256(raw).hexdigest(), 'provenance': o.get('source', {})}
                      for p, raw, o in items]
        candidates[cid] = {'spec': items[0][2]['spec'] if len(specs) == 1 else None,
                           'source_variants': provenance}
    return candidates


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--registry', type=Path, required=True)
    p.add_argument('--candidate-root', type=Path, required=True)
    p.add_argument('--high-observation-min', type=int)
    args = p.parse_args()
    candidates = load_candidates(args.candidate_root)
    print(json.dumps(review(json.loads(args.registry.read_text()), candidates, args.high_observation_min), sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
