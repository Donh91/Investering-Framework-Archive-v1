"""Observe the legacy/current CN calibration split without blending score methods."""
import json
import math
import re
from datetime import date
from pathlib import Path

V2_LEDGER = Path('05_CYCLE_NAVIGATOR/forward_range_ledger/CN_FORWARD_RANGE_LEDGER_v2.jsonl')
PUBLIC_INDEX = Path('05_CYCLE_NAVIGATOR/public_series/CN_PUBLIC_SERIES_INDEX.json')


def inspect_routes(repo, legacy_verified_n):
    result = {
        'contract': 'CN_CALIBRATION_ROUTE_HEALTH_v1',
        'status': 'CURRENT_ROUTE_UNVERIFIED',
        'legacy_verified_row_n': legacy_verified_n,
        'v2_freeze_record_n': None,
        'v2_distinct_week_n': None,
        'current_public_scorecard': None,
        'score_method_conversion_performed': False,
        'scientific_admission': False,
        'canonical_effect': False,
    }
    try:
        rows = [json.loads(line) for line in (repo / V2_LEDGER).read_text().splitlines() if line.strip()]
        if not rows or any(not isinstance(r, dict) or r.get('contract') != 'CN_FORWARD_RANGE_FREEZE_v2' for r in rows):
            raise ValueError('INVALID_V2_FREEZE_RECORDS')
        result['v2_freeze_record_n'] = len(rows)
        result['v2_distinct_week_n'] = len({r['forecast_week'] for r in rows})
        pointer = json.loads((repo / PUBLIC_INDEX).read_text())['latest_completed_score']
        week, issue = pointer['forecast_week'], pointer['public_issue_number']
        if not isinstance(week, str) or not re.fullmatch(r'\d{4}-W\d{2}', week) or type(issue) is not int or issue < 1:
            raise ValueError('INVALID_PUBLIC_IDENTITY')
        year, w = int(week[:4]), int(week[-2:])
        date.fromisocalendar(year, w, 1)
        expected_path = Path(f'05_CYCLE_NAVIGATOR/public_scorecards/{year}/W{w:02d}/CN{issue}_PUBLIC_SCORECARD.json')
        if pointer.get('scorecard_path') != expected_path.as_posix():
            raise ValueError('PUBLIC_SCORECARD_PATH_MISMATCH')
        target = (repo / expected_path).resolve()
        if not target.is_relative_to(repo.resolve()):
            raise ValueError('PUBLIC_SCORECARD_PATH_ESCAPE')
        scorecard = json.loads(target.read_text())
        if (scorecard.get('contract') != 'CN_PUBLIC_WEEKLY_SCORECARD_v1' or
                scorecard.get('authority') != 'PUBLIC_FORECAST_ACCOUNTABILITY_ONLY_NO_PORTFOLIO_AUTHORITY' or
                scorecard.get('forecast_week') != week or scorecard.get('outcome_week') != week or
                scorecard.get('public_issue_number') != issue or scorecard.get('status') != 'FINAL_DUAL_TRACK'):
            raise ValueError('PUBLIC_SCORECARD_IDENTITY_MISMATCH')
        score = scorecard['price_range_precision']['score']
        if type(score) not in (int, float) or not math.isfinite(score) or not 0 <= score <= 100:
            raise ValueError('PUBLIC_SCORE_INVALID')
        if pointer.get('price_range_score') != score or not any(r.get('forecast_week') == week and r.get('public_issue_number') == issue for r in rows):
            raise ValueError('PUBLIC_SCORECARD_ROUTE_MISMATCH')
        result['current_public_scorecard'] = {'path': expected_path.as_posix(), 'week': week, 'public_issue': issue, 'price_range_score': score}
        result['status'] = ('LEGACY_LEDGER_EMPTY_NEWER_SCORECARD_PRESENT' if legacy_verified_n == 0 else 'DISTINCT_SCORE_METHODS_PRESENT')
        result['next_gate'] = 'RECOVER_MATCHED_LEGACY_COMPARATORS_WITHOUT_CONVERTING_PUBLIC_SCORES'
    except (OSError, ValueError, TypeError, KeyError, AttributeError, OverflowError):
        result['next_gate'] = 'VERIFY_CURRENT_PUBLIC_SCORECARD_ROUTE'
    return result
