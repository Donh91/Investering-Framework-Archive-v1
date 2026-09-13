"""Descriptive T11 sidecar. Never rescores or modifies the source ledgers."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path

from scripts.learning import outcome_maturation_engine as owner


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def explain(forecast, outcome):
    row = {key: 'NOT_EVALUABLE' for key in (
        'DIRECTION', 'MAGNITUDE', 'TIMING', 'SEQUENCE', 'STATE_OR_PHASE',
        'ACTION_TRANSLATION', 'PRIMARY_FAILURE_CLASS')}
    row.update(TARGET_RESULT=outcome.get('result'), outcome_status=outcome.get('status'),
               scientific_score_eligible=outcome.get('scientific_score_eligible'),
               scientific_skill_claim=False)
    if outcome.get('status') == 'CENSORED':
        row.update(TARGET_RESULT='CENSORED', reason='CENSORED_NOT_PREDICTION_FAILURE')
        return row
    if not forecast or outcome.get('forecast_sha256') != owner.sha(forecast):
        row['reason'] = 'FORECAST_BINDING_UNAVAILABLE'
        return row
    try:
        owner.validate_forecast(forecast)
        if owner.legacy_unit_ambiguous(forecast):
            raise ValueError('legacy_units')
        start, end = outcome.get('start_value'), outcome.get('end_value')
        if (outcome.get('status') != 'MATURED' or
                not all(finite(v) for v in (start, end, forecast.get('start_value'))) or
                start <= 0 or start != forecast['start_value']):
            raise ValueError('invalid_observation')
        if owner.classify(forecast, start, end) != outcome.get('result'):
            raise ValueError('result_conflict')
    except (ValueError, TypeError, KeyError, OverflowError):
        row['reason'] = 'OWNER_CONTRACT_OR_RESULT_CONFLICT'
        return row
    if forecast['direction'] not in ('UP', 'DOWN'):
        row['reason'] = 'RANGE_DIRECTION_DECOMPOSITION_NOT_DEFINED'
        return row
    if not finite(forecast.get('threshold_pct')):
        row['reason'] = 'INVALID_THRESHOLD'
        return row
    signed_move = (end / start - 1) * (1 if forecast['direction'] == 'UP' else -1)
    if not math.isfinite(signed_move):
        row['reason'] = 'NONFINITE_DERIVED_MOVE'
        return row
    row['DIRECTION'] = 'CORRECT' if signed_move > 0 else 'WRONG' if signed_move < 0 else 'NOT_EVALUABLE'
    row['MAGNITUDE'] = 'SUFFICIENT' if outcome['result'] == 'HIT' else 'INSUFFICIENT'
    if outcome['result'] == 'MISS':
        row['PRIMARY_FAILURE_CLASS'] = 'DIRECTION' if signed_move < 0 else 'MAGNITUDE'
    row['reason'] = 'DESCRIPTIVE_FROZEN_DIRECTIONAL_TARGET_ONLY'
    return row


def build_report(forecast_root, outcome_root):
    sources, forecasts, outcomes = [], defaultdict(dict), []
    for root, contracts in ((forecast_root, {'FROZEN_FORECAST_v1'}),
                            (outcome_root, {'MATURED_OUTCOME_v2', 'MATURED_OUTCOME_v3'})):
        if not root.is_dir():
            raise ValueError('source_root_missing')
        for path in sorted(root.rglob('*.json')):
            raw = path.read_bytes()
            value = json.loads(raw)  # Malformed evidence must not silently disappear.
            binding = {'path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
            sources.append(binding)
            if value.get('contract') not in contracts:
                continue
            if root == forecast_root:
                forecasts[value.get('forecast_id')][owner.sha(value)] = value
            else:
                outcomes.append((binding, value))
    rows = []
    for binding, outcome in outcomes:
        versions = forecasts.get(outcome.get('forecast_id'), {})
        forecast = versions.get(outcome.get('forecast_sha256'))
        rows.append({'outcome_source': binding, 'forecast_id': outcome.get('forecast_id'),
                     'forecast_sha256': outcome.get('forecast_sha256'),
                     'original_result': outcome.get('result'), **explain(forecast, outcome)})
    return {'contract': 'FORECAST_ERROR_TAXONOMY_READOUT_v1',
            'authority': 'DESCRIPTIVE_ONLY_NO_SCORING_OR_PROMOTION',
            'source_manifest': sources, 'outcome_count': len(rows),
            'original_result_counts': dict(sorted(Counter(str(r['original_result']) for r in rows).items())),
            'failure_class_counts': dict(sorted(Counter(r['PRIMARY_FAILURE_CLASS'] for r in rows).items())),
            'rows': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--forecast-root', type=Path, required=True)
    parser.add_argument('--outcome-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    for root in (args.forecast_root, args.outcome_root):
        if args.output.resolve().is_relative_to(root.resolve()):
            raise SystemExit('output_must_be_outside_source_roots')
    report = build_report(args.forecast_root, args.outcome_root)
    data = (json.dumps(report, sort_keys=True, indent=2) + '\n').encode()
    if args.output.exists():
        if args.output.read_bytes() != data:
            raise SystemExit('immutable_report_conflict')
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('xb') as handle:
            handle.write(data)
    print(json.dumps({k: report[k] for k in ('outcome_count', 'original_result_counts', 'failure_class_counts')}))


if __name__ == '__main__':
    main()
