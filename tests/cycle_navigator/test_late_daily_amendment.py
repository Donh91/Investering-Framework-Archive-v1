"""Real W45 original freeze readback, synthetic one-shot supplement tests."""
import copy
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from scripts.cycle_navigator.issue_late_daily_amendment import issue_once
from scripts.cycle_navigator.daily_price_journey import CONTRACT

ROOT = Path(__file__).resolve().parents[2]
ISSUED = datetime(2026, 11, 2, 10, 30, tzinfo=timezone.utc)


def response():
    def asset(base, low, high):
        return {"status": "PUBLISHED", "reason": "Synthetic uncalibrated conditional path",
                "points": [{"day": i, "low": low, "expected_close": base + i,
                            "high": high} for i in range(1, 8)]}
    return {"contract": CONTRACT, "forecast_week": "2026-W45",
            "BTC": asset(78000, 77000, 80000),
            "ETH": asset(2300, 2200, 2400)}


def make_request(calls, result=None):
    def invoke(model, payload):
        calls.append(payload)
        return copy.deepcopy(result or response()), {
            "id": "resp_synthetic_w45",
            "usage": {"input_tokens": 1000, "output_tokens": 1000}}
    return invoke


def invoke(tmp_path, calls, *, issued=ISSUED, result=None, budget=None):
    return issue_once(ROOT, year=2026, week=45, model="gpt-6-sol",
                      issued_at=issued, output=tmp_path / "w45-late.json",
                      request=make_request(calls, result),
                      budget_check=budget or (lambda: {"status": "PASS"}))


def test_read_original_frozen_W45_and_append_only_distinct_7of7(tmp_path):
    frozen = ROOT / "05_CYCLE_NAVIGATOR/weekly/2026/W45/CYCLE_NAVIGATOR_FORECAST_FREEZE.json"
    before = frozen.read_bytes()
    calls = []
    output = invoke(tmp_path, calls)
    assert len(calls) == 1
    assert output["status"] == "SUPPLEMENTAL_SEVEN_DAY_CANDIDATE"
    assert output["forecast_week"] == "2026-W45"
    assert output["original_freeze_changed"] is False
    assert output["original_issuer_replacement"] is False
    assert output["eligible_for_official_scoring"] is False
    assert output["site_publishing_authority"] is False
    assert output["original_weekly_envelope_quote_verified"] is False
    assert all(len(output["daily_path"][asset]["points"]) == 7 for asset in ("BTC", "ETH"))
    assert frozen.read_bytes() == before
    assert json.loads((tmp_path / "w45-late.json").read_text())["supplement_sha256"] == output["supplement_sha256"]


def test_no_duplicate_or_overwrite_of_supplement(tmp_path):
    invoke(tmp_path, [])
    with pytest.raises(ValueError, match="SUPPLEMENT_OUTPUT_ALREADY_EXISTS"):
        invoke(tmp_path, [])


def test_no_seven_outcomes_if_first_monday_close_occurred(tmp_path):
    calls = []
    result = invoke(tmp_path, calls, issued=datetime(2026, 11, 3, 0, 0, tzinfo=timezone.utc))
    assert result["status"] == "SUPPLEMENTAL_UNAVAILABLE"
    assert not calls
    assert result["recovery_receipt"]["source_gate"] == "SEVEN_DAY_PROSPECTIVE_WINDOW_CLOSED_OR_NOT_STARTED"


def test_cost_failure_cannot_spend_or_produce_claimed_path(tmp_path):
    calls = []
    result = invoke(tmp_path, calls, budget=lambda: {"status": "BLOCKED"})
    assert result["status"] == "SUPPLEMENTAL_UNAVAILABLE" and calls == []
    assert result["recovery_receipt"]["attempt_count"] == 0


def test_invalid_candidate_rejects_only_bad_asset(tmp_path):
    calls = []
    candidate = response()
    candidate["BTC"]["points"][3]["expected_close"] = 100000
    result = invoke(tmp_path, calls, result=candidate)
    assert len(calls) == 1
    assert result["daily_path"]["BTC"]["status"] == "UNAVAILABLE"
    assert result["daily_path"]["ETH"]["status"] == "PUBLISHED"


def test_W45_only_and_no_backfill_other_weeks(tmp_path):
    with pytest.raises(ValueError, match="LATE_ISSUE_ONE_WEEK_ONLY"):
        issue_once(ROOT, year=2026, week=44, model="gpt-6-sol", issued_at=ISSUED,
                   output=tmp_path / "wrong.json", request=make_request([]),
                   budget_check=lambda: {"status": "PASS"})
