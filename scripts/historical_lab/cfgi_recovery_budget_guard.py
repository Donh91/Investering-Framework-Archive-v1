#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from cfgi_targeted_backfill import candidate_events, select_events

ROOT = Path('06_RESEARCH_LAB/historical_altseason_pullback_v1')
LEDGER = Path('00_ARCHIVE_CONTROL/research_runtime/HISTORICAL_ALTSEASON_CFGI_PAID_ATTEMPT_LEDGER.json')
RESERVATION = Path('00_ARCHIVE_CONTROL/research_runtime/HISTORICAL_ALTSEASON_CFGI_PAID_RESERVATION.json')


def main() -> None:
    cfg = json.loads((ROOT / 'config.json').read_text())
    catalog = json.loads((ROOT / 'artifacts/EPISODE_CATALOG.json').read_text())
    ledger = json.loads(LEDGER.read_text())
    reservation = json.loads(RESERVATION.read_text())

    assert ledger['contract'] == 'HISTORICAL_ALTSEASON_CFGI_PAID_ATTEMPT_LEDGER_v1'
    assert ledger['input_fingerprint_sha256'] == reservation['input_fingerprint_sha256']
    attempts = ledger.get('attempts') or []
    prior_actual = sum(int(x.get('actual_credits_used_from_headers') or 0) for x in attempts)
    assert prior_actual == int(ledger['cumulative_actual_credits_used'])
    assert int(ledger['owner_authorized_recovery_attempts']) == 1
    assert ledger['automatic_retry_after_failure'] is False

    ccfg = cfg['cfgi']
    hard_cap = int(ccfg['expected_credit_hard_cap'])
    reserve = int(ccfg['minimum_credits_reserve'])
    last_remaining = next((int(x['final_credits_remaining']) for x in reversed(attempts) if x.get('final_credits_remaining') is not None), None)
    assert last_remaining is not None

    events = candidate_events(catalog)
    selected, _intervals, expected_current = select_events(events, ccfg, last_remaining)
    assert selected, 'no selected recovery events'
    assert len(selected) == int(reservation['candidate_event_count'])

    projected_cumulative = prior_actual + int(expected_current)
    projected_remaining = last_remaining - int(expected_current)
    blockers = []
    if projected_cumulative > hard_cap:
        blockers.append('CUMULATIVE_HARD_CAP_EXCEEDED')
    if projected_remaining < reserve:
        blockers.append('PROJECTED_RESERVE_BREACH')

    out = {
        'contract': 'HISTORICAL_ALTSEASON_CFGI_RECOVERY_BUDGET_GUARD_v1',
        'input_fingerprint_sha256': reservation['input_fingerprint_sha256'],
        'prior_actual_credits_used': prior_actual,
        'expected_current_worst_case_credits': int(expected_current),
        'projected_cumulative_credits': projected_cumulative,
        'hard_cap_credits': hard_cap,
        'last_known_credits_remaining': last_remaining,
        'projected_credits_remaining': projected_remaining,
        'minimum_reserve_credits': reserve,
        'selected_event_count': len(selected),
        'recovery_attempts_authorized': 1,
        'blockers': blockers,
        'status': 'PASS' if not blockers else 'FAIL',
    }
    print(json.dumps(out, sort_keys=True))
    if blockers:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
