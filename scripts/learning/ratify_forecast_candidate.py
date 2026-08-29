from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timedelta, timezone
from pathlib import Path

UNIT_CONTRACT_VERSION = "FORECAST_TARGET_UNITS_v2"
LINEAGE_CONTRACT = "DATA_PING_LEARNING_LINEAGE_v1"


def canon(v): return (json.dumps(v, sort_keys=True, separators=(',', ':')) + '\n').encode()
def digest(v): return hashlib.sha256(canon(v)).hexdigest()
def load(p): return json.loads(p.read_text())
def at_path(v, path):
    cur = v
    for part in path.split('.'):
        if not isinstance(cur, dict): return None
        cur = cur.get(part)
    return cur


def normalize_target(candidate, start):
    direction = candidate.get('direction')
    mode = candidate.get('target_mode')
    if direction in {'UP', 'DOWN'}:
        if mode == 'PCT_MOVE':
            pct = candidate.get('threshold_pct')
            if not isinstance(pct, (int, float)) or float(pct) <= 0:
                raise SystemExit('PCT_THRESHOLD_REQUIRED')
            return {'target_mode': mode, 'threshold_pct': float(pct), 'target_value': None,
                    'range_lower_pct': None, 'range_upper_pct': None}
        if mode == 'ABSOLUTE_VALUE':
            target = candidate.get('target_value')
            if not isinstance(target, (int, float)):
                raise SystemExit('ABSOLUTE_TARGET_REQUIRED')
            target = float(target)
            if direction == 'UP':
                if target <= float(start): raise SystemExit('UP_TARGET_MUST_EXCEED_START')
                pct = (target / float(start) - 1.0) * 100.0
            else:
                if target >= float(start): raise SystemExit('DOWN_TARGET_MUST_BE_BELOW_START')
                pct = (1.0 - target / float(start)) * 100.0
            return {'target_mode': mode, 'threshold_pct': pct, 'target_value': target,
                    'range_lower_pct': None, 'range_upper_pct': None}
        raise SystemExit('EXPLICIT_DIRECTIONAL_TARGET_MODE_REQUIRED')
    if direction == 'RANGE':
        if mode != 'ABSOLUTE_RANGE':
            raise SystemExit('ABSOLUTE_RANGE_MODE_REQUIRED')
        low, high = candidate.get('range_low'), candidate.get('range_high')
        if not isinstance(low, (int, float)) or not isinstance(high, (int, float)) or float(low) >= float(high):
            raise SystemExit('VALID_RANGE_BOUNDS_REQUIRED')
        return {'target_mode': mode, 'threshold_pct': None, 'target_value': None,
                'range_lower_pct': (float(low) / float(start) - 1.0) * 100.0,
                'range_upper_pct': (float(high) / float(start) - 1.0) * 100.0,
                'range_lower_value': float(low), 'range_upper_value': float(high)}
    raise SystemExit('INVALID_DIRECTION')


def validate_data_ping_lineage(candidate, receipt_path):
    lineage = candidate.get('data_ping_lineage')
    if lineage is None:
        if receipt_path is not None:
            raise SystemExit('ORPHAN_ACTION_COMPASS_RECEIPT')
        return None
    if not isinstance(lineage, dict) or lineage.get('contract') != LINEAGE_CONTRACT:
        raise SystemExit('INVALID_DATA_PING_LINEAGE')
    if receipt_path is None:
        raise SystemExit('ACTION_COMPASS_RECEIPT_REQUIRED')
    receipt = load(receipt_path)
    packet_hash = lineage.get('accepted_packet_sha256')
    if not isinstance(packet_hash, str) or len(packet_hash) != 64 or any(ch not in '0123456789abcdef' for ch in packet_hash):
        raise SystemExit('INVALID_ACCEPTED_PACKET_SHA256')
    expected = {
        'accepted_packet_identity': 'DPI-' + packet_hash[:24],
        'action_compass_receipt_id': receipt.get('receipt_id'),
        'action_compass_receipt_sha256': digest(receipt),
        'accepted_packet_path': receipt.get('source_reference'),
        'canonical_repository': receipt.get('canonical_repository'),
        'canonical_commit_sha': receipt.get('canonical_commit_sha'),
        'owner_contract': receipt.get('owner_contract'),
    }
    if receipt.get('contract') != 'THREE_HORIZON_ACTION_COMPASS_RECEIPT_v1_1':
        raise SystemExit('WRONG_ACTION_COMPASS_RECEIPT_CONTRACT')
    if receipt.get('input_binding_status') != 'VERIFIED_REPO_FILE':
        raise SystemExit('ACTION_COMPASS_INPUT_NOT_VERIFIED_REPO_FILE')
    if receipt.get('input_packet_sha256') != packet_hash:
        raise SystemExit('ACTION_COMPASS_PACKET_HASH_MISMATCH')
    if receipt.get('portfolio_execution') is not False:
        raise SystemExit('PORTFOLIO_EXECUTION_MUST_REMAIN_FALSE')
    commit = receipt.get('canonical_commit_sha')
    if not isinstance(commit, str) or len(commit) != 40:
        raise SystemExit('INVALID_CANONICAL_COMMIT_SHA')
    for key, expected_value in expected.items():
        if lineage.get(key) != expected_value:
            raise SystemExit('DATA_PING_LINEAGE_MISMATCH:' + key)
    return dict(lineage)


def build_frozen(c, r, b, baseline_path, target, lineage, frozen_at):
    candidate = c['candidate']; horizon = int(candidate['horizon_days']); metric = candidate['metric_path']
    start = at_path(b, metric); baseline_hash = digest(b)
    forecast_id = 'ff_' + hashlib.sha256(canon({'candidate': c['candidate_id'], 'ratification': r, 'baseline': baseline_hash})).hexdigest()[:24]
    frozen = {
        'contract': 'FROZEN_FORECAST_v1',
        'unit_contract_version': UNIT_CONTRACT_VERSION,
        'forecast_id': forecast_id,
        'candidate_id': c['candidate_id'],
        'frozen_at_utc': frozen_at.isoformat().replace('+00:00', 'Z'),
        'outcome_due_utc': (frozen_at + timedelta(days=horizon)).isoformat().replace('+00:00', 'Z'),
        'horizon_days': horizon,
        'metric_path': metric,
        'direction': candidate['direction'],
        'start_value': start,
        'target_mode': target['target_mode'],
        'threshold_pct': target.get('threshold_pct'),
        'target_value': target.get('target_value'),
        'range_lower_pct': target.get('range_lower_pct'),
        'range_upper_pct': target.get('range_upper_pct'),
        'range_lower_value': target.get('range_lower_value'),
        'range_upper_value': target.get('range_upper_value'),
        'rationale': candidate.get('rationale'),
        'model': c.get('model'),
        'task': c.get('task'),
        'prompt_sha256': c.get('prompt_sha256'),
        'context_sha256': c.get('context_sha256'),
        'source_output_sha256': c.get('source_output_sha256'),
        'candidate_sha256': digest(c),
        'ratification_sha256': digest(r),
        'baseline_evidence_path': str(baseline_path),
        'baseline_evidence_sha256': baseline_hash,
        'authority': {'portfolio_action': False, 'model_weight_change': False, 'canonical_promotion': False},
    }
    if lineage is not None:
        frozen['data_ping_lineage'] = lineage
    return frozen


def main():
    ap = argparse.ArgumentParser();ap.add_argument('--candidate', type=Path, required=True);ap.add_argument('--ratification', type=Path, required=True);ap.add_argument('--baseline-evidence', type=Path, required=True);ap.add_argument('--output-root', type=Path, required=True);ap.add_argument('--action-compass-receipt', type=Path);a = ap.parse_args()
    c = load(a.candidate);r = load(a.ratification);b = load(a.baseline_evidence)
    if c.get('contract') != 'FORECAST_CANDIDATE_v1' or c.get('ratification_status') != 'PENDING': raise SystemExit('CANDIDATE_NOT_PENDING')
    if r.get('contract') != 'FORECAST_RATIFICATION_PACKET_v1' or r.get('decision') != 'RATIFY': raise SystemExit('RATIFICATION_REQUIRED')
    if r.get('candidate_id') != c.get('candidate_id'): raise SystemExit('CANDIDATE_ID_MISMATCH')
    if r.get('authority') not in {'CHATGPT_FRAMEWORK_OWNER', 'EXPLICIT_USER_MANDATE'}: raise SystemExit('INVALID_RATIFICATION_AUTHORITY')
    candidate = c['candidate'];metric = candidate['metric_path'];start = at_path(b, metric)
    if not isinstance(start, (int, float)): raise SystemExit('BASELINE_METRIC_UNAVAILABLE')
    target = normalize_target(candidate, float(start))
    lineage = validate_data_ping_lineage(c, a.action_compass_receipt)
    baseline_hash = digest(b)
    forecast_id = 'ff_' + hashlib.sha256(canon({'candidate': c['candidate_id'], 'ratification': r, 'baseline': baseline_hash})).hexdigest()[:24]
    out = a.output_root / f"{forecast_id}.json"; out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        existing = load(out)
        try:
            frozen_at = datetime.fromisoformat(existing['frozen_at_utc'].replace('Z', '+00:00'))
        except Exception as exc:
            raise SystemExit('FORECAST_ID_COLLISION') from exc
        expected = build_frozen(c, r, b, a.baseline_evidence, target, lineage, frozen_at)
        if canon(existing) != canon(expected):
            raise SystemExit('FORECAST_ID_COLLISION')
        print(json.dumps({'status': 'DUPLICATE_NOOP', 'forecast_id': forecast_id, 'path': str(out)}, sort_keys=True)); return
    frozen = build_frozen(c, r, b, a.baseline_evidence, target, lineage, datetime.now(timezone.utc))
    out.write_bytes(canon(frozen));print(json.dumps({'status': 'FROZEN', 'forecast_id': frozen['forecast_id'], 'path': str(out)}, sort_keys=True))
if __name__ == '__main__': main()
