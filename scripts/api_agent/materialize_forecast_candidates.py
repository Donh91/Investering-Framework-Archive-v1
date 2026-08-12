from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

TARGET_MODES = {'PCT_MOVE', 'ABSOLUTE_VALUE', 'ABSOLUTE_RANGE'}


def canon(v): return (json.dumps(v, sort_keys=True, separators=(',', ':')) + '\n').encode()

def load_json(path: Path):
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def existing_candidate_ids(pending_root: Path) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    if not pending_root.exists():
        return found
    for path in sorted(pending_root.rglob('*.json')):
        row = load_json(path)
        if not isinstance(row, dict):
            continue
        candidate_id = str(row.get('candidate_id') or '').strip()
        if not candidate_id:
            continue
        found.setdefault(candidate_id, []).append(str(path))
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--receipt', type=Path, required=True)
    ap.add_argument('--pending-root', type=Path, required=True)
    a = ap.parse_args()

    out = json.loads(a.output.read_text())
    receipt = json.loads(a.receipt.read_text())
    now = datetime.now(timezone.utc)
    existing = existing_candidate_ids(a.pending_root)
    created: list[str] = []
    already_present: list[str] = []

    for i, candidate in enumerate(out.get('forecast_candidates', []), 1):
        if candidate.get('target_mode') not in TARGET_MODES:
            raise SystemExit('FORECAST_CANDIDATE_TARGET_MODE_REQUIRED')
        candidate_id = hashlib.sha256(canon({'receipt': receipt.get('output_hash'), 'index': i, 'candidate': candidate})).hexdigest()[:24]
        if candidate_id in existing:
            already_present.append(candidate_id)
            continue

        material = {
            'contract': 'FORECAST_CANDIDATE_v1',
            'authority': 'UNRATIFIED_RESEARCH_ONLY',
            'candidate_id': candidate_id,
            'created_at_utc': now.isoformat().replace('+00:00', 'Z'),
            'model': receipt.get('model'),
            'task': receipt.get('task'),
            'prompt_sha256': receipt.get('prompt_hash'),
            'context_sha256': receipt.get('context_hash'),
            'source_output_sha256': receipt.get('output_hash'),
            'candidate': candidate,
            'ratification_status': 'PENDING',
            'self_promotion_allowed': False,
        }
        path = a.pending_root / f'{now:%Y/%m/%d}' / f'{candidate_id}.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = canon(material)
        path.write_bytes(payload)
        if path.read_bytes() != payload:
            raise RuntimeError('forecast_candidate_readback_mismatch')
        existing[candidate_id] = [str(path)]
        created.append(str(path))

    print(json.dumps({
        'status': 'PASS',
        'candidate_count': len(created),
        'created_count': len(created),
        'existing_candidate_count': len(already_present),
        'existing_candidate_ids': sorted(already_present),
        'paths': created,
        'idempotent_across_pending_tree': True,
    }, sort_keys=True))


if __name__ == '__main__':
    main()
