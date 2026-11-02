"""Adversarial tests for original CN pre-freeze daily issuance recovery."""
from __future__ import annotations

import copy
import math
from datetime import datetime, timezone
from pathlib import Path

import pytest

from scripts.cycle_navigator import build_weekly_cycle_navigator as builder
from scripts.cycle_navigator.daily_path_recovery import recover_daily_path, _source_gate
from scripts.cycle_navigator.daily_price_journey import CONTRACT, validate_daily_path, daily_path_issue_summary


ISSUED = datetime(2026, 11, 9, 9, 30, tzinfo=timezone.utc)
WEEK = "2026-W46"


def _points(base):
    return [{"day": day, "low": base-10, "expected_close": base + day,
             "high": base+15} for day in range(1, 8)]


def _asset(status, base):
    return {"status": status, "reason": "No defensible daily temporal path" if status == "UNAVAILABLE" else "Source-qualified conditional path",
            "points": [] if status == "UNAVAILABLE" else _points(base)}


def _value(btc="UNAVAILABLE", eth="UNAVAILABLE"):
    path = {"contract": CONTRACT, "forecast_week": WEEK,
            "BTC": _asset(btc, 100), "ETH": _asset(eth, 200)}
    return {"issue_number": 34, "base_case_this_week": "Cautious base case, uncalibrated.",
            "market_state": "MIXED", "forecast_freeze": {
                "btc_range_low": 80, "btc_range_high": 130,
                "eth_range_low": 180, "eth_range_high": 230,
                "intraday_map": {"day_1_2": "Uncertain", "day_3_4": "Possible retest", "day_5_7": "Repair uncertain"},
                "bull_bear_scale": {"horizons": {}}, "market_structure_analysis": {},
                "daily_price_path": path}}


def _context():
    return {"weekly_envelope_quote": {"BTC": "USDT", "ETH": "USDT"},
            "master_monday_pointer": {"iso_year": 2026, "iso_week": 45, "status": "READY"},
            "master_monday_machine_package": {"api_status": "success", "created_at_utc": "2026-11-09T09:00:00Z"},
            "completed_week_hourly_capture": {
                "iso_year": 2026, "iso_week": 45, "readiness": "READY",
                "generated_at_utc": "2026-11-09T08:10:00Z",
                "source_capture_paths": ["immutable/2026-W45.json"],
                "hourly_gap_diagnostics": {"observed_hours": 168, "missing_hour_count": 0},
                "hourly_sequence": {
                    "first_hour_utc": "2026-11-02T00:00:00Z",
                    "last_hour_utc": "2026-11-08T23:00:00Z",
                    "btc": {"week_range": {"open": 100, "close": 102, "low": 90, "high": 115},
                            "max_abs_return_1h_pct": 1.3, "max_range_1h_pct": 2.4, "up_hours": 80, "down_hours": 88},
                    "eth": {"week_range": {"open": 200, "close": 202, "low": 190, "high": 215},
                            "max_abs_return_1h_pct": 2.3, "max_range_1h_pct": 3.4, "up_hours": 85, "down_hours": 83},
                    "spot_flow_readback": {"BTC": {"quote_unit": "USDT", "semantics": "RETAINED_SPOT_EXCHANGE"},
                                           "ETH": {"quote_unit": "USDT", "semantics": "RETAINED_SPOT_EXCHANGE"}}}}}


def _proposal(btc="PUBLISHED", eth="PUBLISHED"):
    return {"contract": CONTRACT, "forecast_week": WEEK,
            "BTC": _asset(btc, 100), "ETH": _asset(eth, 200)}


def _run(value, context=None, request=None, issued=ISSUED, budget_check=None,
         cost_receipt_path=None, primary_unaccounted_cost_usd=0.0):
    return recover_daily_path(value, _context() if context is None else context,
                              year=2026, week=46, model="gpt-6-sol", issued_at=issued, request=request,
                              budget_check=budget_check or (lambda: {"status": "PASS", "remaining_usd_before": 40.0, "test_injection": True}),
                              cost_receipt_path=cost_receipt_path,
                              primary_unaccounted_cost_usd=primary_unaccounted_cost_usd)


def _fake(proposal, calls):
    def answer(model, payload):
        calls.append((model, payload))
        return copy.deepcopy(proposal), {"id": "resp_synthetic", "usage": {"input_tokens": 200, "output_tokens": 100}}
    return answer


def test_initial_7_of_7_for_both_assets_has_zero_extra_api_calls():
    calls = []
    original = _value("PUBLISHED", "PUBLISHED")
    output, receipt = _run(copy.deepcopy(original), request=_fake(_proposal(), calls))
    assert output == original
    assert receipt["attempt_count"] == 0 and calls == []
    assert receipt["status"] == "NOT_REQUIRED"


def test_first_0_of_7_and_second_7_of_7_is_valid_and_freezes_once():
    calls = []
    value = _value()
    original_bounds = {key: value["forecast_freeze"][key] for key in ("btc_range_low", "btc_range_high", "eth_range_low", "eth_range_high")}
    out, receipt = _run(value, request=_fake(_proposal(), calls))
    assert len(calls) == 1
    assert receipt["attempt_count"] == 1
    assert receipt["status"] == "PARTIAL_OR_FULL_RECOVERY"
    assert receipt["issued_at_utc"] == "2026-11-09T09:30:00Z"
    assert len(receipt["source_context_sha256"]) == 64
    assert len(receipt["original_daily_path_sha256"]) == 64
    assert receipt["source_clock_and_quote"]["quote"]["BTC"] == "USDT"
    assert receipt["response_id"] == "resp_synthetic"
    assert {key: out["forecast_freeze"][key] for key in original_bounds} == original_bounds
    path = validate_daily_path(out["forecast_freeze"]["daily_price_path"], out["forecast_freeze"], 2026, 46)
    assert all(len(path[a]["points"]) == 7 for a in ("BTC", "ETH"))
    assert daily_path_issue_summary(path, out["forecast_freeze"], 2026, 46)["status"] == "PUBLISHED_BOTH"


def test_btc_recovers_but_eth_honestly_abstains():
    calls = []
    out, receipt = _run(_value(), request=_fake(_proposal(eth="UNAVAILABLE"), calls))
    path = out["forecast_freeze"]["daily_price_path"]
    assert path["BTC"]["status"] == "PUBLISHED"
    assert path["ETH"]["status"] == "UNAVAILABLE"
    assert "REASSESSMENT_ABSTAINED" in receipt["per_asset_reason"]["ETH"]
    assert len(calls) == 1
    assert daily_path_issue_summary(path, out["forecast_freeze"], 2026, 46)["status"] == "PARTIAL"


def test_already_published_asset_cannot_be_overwritten_on_other_asset_retry():
    original = _value("PUBLISHED", "UNAVAILABLE")
    other = _proposal()
    other["BTC"]["points"][0]["expected_close"] = 115
    out, _ = _run(original, request=_fake(other, []))
    assert out["forecast_freeze"]["daily_price_path"]["BTC"]["points"][0]["expected_close"] == 101
    assert out["forecast_freeze"]["daily_price_path"]["ETH"]["status"] == "PUBLISHED"


@pytest.mark.parametrize("bad", [
    "wrong_week", "reversed_days", "missing_day", "duplicate_day", "outside_week",
    "negative", "zero", "nan", "infinite", "string_price", "boolean_price", "inverted_range"])
def test_invalid_second_attempt_must_not_publish_fabricated_path(bad):
    proposal = _proposal(eth="UNAVAILABLE")
    btc = proposal["BTC"]
    if bad == "wrong_week":
        proposal["forecast_week"] = "2026-W45"
    elif bad == "reversed_days":
        btc["points"].reverse()
    elif bad == "missing_day":
        btc["points"].pop()
    elif bad == "duplicate_day":
        btc["points"][2]["day"] = 2
    elif bad == "outside_week":
        btc["points"][0]["high"] = 135
    elif bad == "negative":
        btc["points"][0]["low"] = -1
    elif bad == "zero":
        btc["points"][0]["low"] = 0
    elif bad == "nan":
        btc["points"][0]["expected_close"] = float("nan")
    elif bad == "infinite":
        btc["points"][0]["high"] = math.inf
    elif bad == "string_price":
        btc["points"][0]["low"] = "90"
    elif bad == "boolean_price":
        btc["points"][0]["low"] = True
    elif bad == "inverted_range":
        btc["points"][0]["low"] = 125
    out, receipt = _run(_value(), request=_fake(proposal, []))
    assert out["forecast_freeze"]["daily_price_path"]["BTC"]["status"] == "UNAVAILABLE"
    assert receipt["attempt_count"] == 1
    assert receipt["status"] != "PARTIAL_OR_FULL_RECOVERY"


@pytest.mark.parametrize("bad", ["future_capture", "future_mm", "target_week_rows", "wrong_completed_week",
                                   "missing_lineage", "missing_hours", "not_ready", "wrong_clock", "missing_quote", "wrong_first_hour"])
def test_source_and_clock_guard_fail_closed_without_extra_spend(bad):
    context = _context()
    cap = context["completed_week_hourly_capture"]
    if bad == "future_capture":
        cap["generated_at_utc"] = "2026-11-09T12:00:00Z"
    elif bad == "future_mm":
        context["master_monday_machine_package"]["created_at_utc"] = "2026-11-09T12:00:00Z"
    elif bad == "target_week_rows":
        cap["hourly_sequence"]["last_hour_utc"] = "2026-11-09T02:00:00Z"
    elif bad == "wrong_completed_week":
        cap["iso_week"] = 44
    elif bad == "missing_lineage":
        cap["source_capture_paths"] = []
    elif bad == "missing_hours":
        cap["hourly_gap_diagnostics"]["observed_hours"] = 165
    elif bad == "not_ready":
        cap["readiness"] = "DEGRADED"
    elif bad == "wrong_clock":
        cap["generated_at_utc"] = "bad-clock"
    elif bad == "missing_quote":
        cap["hourly_sequence"]["spot_flow_readback"] = {}
    elif bad == "wrong_first_hour":
        cap["hourly_sequence"]["first_hour_utc"] = "2026-11-03T00:00:00Z"
    calls = []
    out, receipt = _run(_value(), context=context, request=_fake(_proposal(), calls))
    assert receipt["attempt_count"] == 0 and calls == []
    assert receipt["status"] == "SKIPPED_SOURCE_GUARD"
    assert out["forecast_freeze"]["daily_price_path"]["BTC"]["status"] == "UNAVAILABLE"


@pytest.mark.parametrize("bad", ["unbound_weekly_quote", "cross_quote", "first_close_passed", "before_week_start"])
def test_weekly_quote_or_prospective_clock_rejects_without_api_call(bad):
    from datetime import timedelta
    context = _context()
    issued = ISSUED
    if bad == "unbound_weekly_quote":
        del context["weekly_envelope_quote"]
    elif bad == "cross_quote":
        context["weekly_envelope_quote"]["BTC"] = "USD"
        context["weekly_envelope_quote"]["ETH"] = "USD"
    elif bad == "first_close_passed":
        issued = datetime(2026, 11, 10, 0, 0, tzinfo=timezone.utc)
    else:
        issued = datetime(2026, 11, 8, 23, 59, tzinfo=timezone.utc)
    calls = []
    _, receipt = _run(_value(), context=context, issued=issued, request=_fake(_proposal(), calls))
    assert receipt["attempt_count"] == 0 and not calls
    assert receipt["status"] == "SKIPPED_SOURCE_GUARD"


def test_monthly_cost_guard_blocks_even_injected_request():
    calls = []
    _, receipt = _run(_value(), request=_fake(_proposal(), calls),
                      budget_check=lambda: {"status": "BLOCKED"})
    assert receipt["status"] == "SKIPPED_BUDGET_OR_OPERATOR_GUARD"
    assert receipt["attempt_count"] == 0 and calls == []


def test_budget_readback_unavailable_fails_closed_without_paid_request(monkeypatch):
    from scripts.cycle_navigator import daily_path_recovery as repair
    import subprocess
    monkeypatch.setattr(repair.subprocess, "run", lambda *args, **kwargs:
                        subprocess.CompletedProcess(args, 1, stdout='{"status":"BLOCKED","remaining_usd":0}', stderr=""))
    calls = []
    _, receipt = _run(_value(), request=_fake(_proposal(), calls), budget_check=repair._budget_guard)
    assert receipt["attempt_count"] == 0 and calls == []
    assert receipt["status"] == "SKIPPED_BUDGET_OR_OPERATOR_GUARD"


def test_negative_missing_key_and_transport_error_keep_original_abstention():
    for fake in (lambda m,p: (_ for _ in ()).throw(TimeoutError("network")),
                 lambda m,p: ({"contract": CONTRACT, "forecast_week": WEEK, "BTC": {}},
                               {"usage": {}, "id": "invalid"})):
        out, receipt = _run(_value(), request=fake)
        assert out["forecast_freeze"]["daily_price_path"]["BTC"]["status"] == "UNAVAILABLE"
        assert receipt["attempt_count"] == 1


def test_operator_cost_guard_prevents_second_call(monkeypatch):
    monkeypatch.setenv("CN_DAILY_RECOVERY_ENABLED", "0")
    calls = []
    _, receipt = _run(_value(), request=_fake(_proposal(), calls))
    assert receipt["attempt_count"] == 0 and calls == []


def test_retry_transport_failure_never_automatically_reissues():
    calls = []
    def failed(model, payload):
        calls.append(payload)
        raise RuntimeError("API_RATE_LIMIT")
    out, receipt = _run(_value(), request=failed)
    assert len(calls) == 1
    assert receipt["status"] == "UNAVAILABLE_AFTER_RECOVERY_ERROR"
    assert out["forecast_freeze"]["daily_price_path"]["BTC"]["status"] == "UNAVAILABLE"


def test_source_manifest_holds_attempt_and_canonical_scoring_is_untouched():
    src = Path(builder.__file__).read_text()
    assert '"daily_path_recovery": daily_recovery_receipt' in src
    assert "source_manifest_sha256" in src
    assert "CYCLE_NAVIGATOR_SCORECARD_v1" in src
    assert "value[\"evaluation\"]" in src
    assert "existing_forecast_freeze_refuses_reissue" in src
    assert "daily_path_recovery" in src
    assert 'daily_path_issue_summary(freeze.get("daily_price_path")' in src


def test_legacy_original_semantic_call_remains_one_and_workflow_not_extended():
    src = Path(builder.__file__).read_text()
    assert src.count("value, raw = call_openai(args.model, prompt, context, args.max_output_tokens)") == 1
    workflow = (Path(builder.__file__).parents[2] / ".github/workflows/cycle-navigator-weekly-publication.yml").read_text()
    assert "group: framework-main-writer" in workflow
    assert "Enforce monthly API cost guard" in workflow

def test_production_never_makes_extra_paid_call_even_if_env_and_budget_allow(monkeypatch, tmp_path):
    from scripts.cycle_navigator import daily_path_recovery as repair
    called = []
    monkeypatch.setenv("CN_DAILY_RECOVERY_ENABLED", "1")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(repair.urllib.request, "urlopen", lambda *a, **k: called.append(1))
    reservation = tmp_path / "must-not-create-paid-reservation.json"
    original = _value()
    out, receipt = _run(copy.deepcopy(original), cost_receipt_path=reservation,
                        budget_check=lambda: {"status": "PASS", "remaining_usd_before": 100.0})
    assert out == original
    assert receipt["attempt_count"] == 0 and called == []
    assert receipt["status"] == "SKIPPED_PAID_RECOVERY_DISABLED"
    assert receipt["budget_error_code"] == "PAID_SEMANTIC_RECOVERY_NOT_AUTHORIZED"
    assert not reservation.exists()


def test_source_input_size_guard_never_calls_paid_api(monkeypatch):
    from scripts.cycle_navigator import daily_path_recovery as repair
    calls = []
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(repair.urllib.request, "urlopen", lambda req, timeout=180: calls.append(req))
    with pytest.raises(RuntimeError, match="RECOVERY_INPUT_SIZE_EXCEEDED"):
        repair._one_request("test-model", {"very_large_payload": "x" * (repair.MAX_RECOVERY_INPUT_BYTES + 1)})
    assert calls == []


def test_no_real_api_request_without_durable_cost_reservation(monkeypatch):
    from scripts.cycle_navigator import daily_path_recovery as repair
    called = []
    monkeypatch.setattr(repair.urllib.request, "urlopen", lambda *a, **k: called.append(1))
    _, receipt = _run(_value(), cost_receipt_path=None)
    assert receipt["attempt_count"] == 0 and called == []
    assert receipt["status"] == "SKIPPED_PAID_RECOVERY_DISABLED"
    assert receipt["budget_error_code"] == "PAID_SEMANTIC_RECOVERY_NOT_AUTHORIZED"


def test_existing_cost_reservation_prevents_double_paid_call(monkeypatch, tmp_path):
    from scripts.cycle_navigator import daily_path_recovery as repair
    called = []
    monkeypatch.setattr(repair.urllib.request, "urlopen", lambda *a, **k: called.append(1))
    path = tmp_path / "already-reserved.json"
    path.write_text('{"preexisting":true}')
    _, receipt = _run(_value(), cost_receipt_path=path)
    assert receipt["attempt_count"] == 0 and called == []
    assert receipt["budget_error_code"] == "PAID_SEMANTIC_RECOVERY_NOT_AUTHORIZED"
    assert path.read_text() == '{"preexisting":true}'


def test_first_model_pass_fails_closed_when_price_quote_mismatches():
    from scripts.cycle_navigator.daily_path_recovery import reject_unverified_initial_daily_quotes
    value = _value("PUBLISHED", "PUBLISHED")
    value["forecast_freeze"]["price_quote"] = {"BTC": "USD", "ETH": "USDT"}
    updated = reject_unverified_initial_daily_quotes(value, _context())
    path = updated["forecast_freeze"]["daily_price_path"]
    assert path["BTC"]["status"] == "UNAVAILABLE"
    assert path["BTC"]["points"] == []
    assert path["ETH"]["status"] == "PUBLISHED"
    assert path["ETH"]["points"][0]["expected_close"] == 201


def test_first_model_pass_all_verified_preserves_original_7of7():
    from scripts.cycle_navigator.daily_path_recovery import reject_unverified_initial_daily_quotes
    value = _value("PUBLISHED", "PUBLISHED")
    value["forecast_freeze"]["price_quote"] = {"BTC": "USDT", "ETH": "USDT"}
    original = copy.deepcopy(value)
    assert reject_unverified_initial_daily_quotes(value, _context()) == original


def test_first_model_pass_missing_quote_never_publishes():
    from scripts.cycle_navigator.daily_path_recovery import reject_unverified_initial_daily_quotes
    value = _value("PUBLISHED", "PUBLISHED")
    candidate = reject_unverified_initial_daily_quotes(value, _context())
    assert all(candidate["forecast_freeze"]["daily_price_path"][asset]["status"] == "UNAVAILABLE"
               for asset in ("BTC", "ETH"))


@pytest.mark.parametrize("primary_cost,remaining", [(0.20, 4.30), (0.0, 4.10), (float("nan"), 30.0)])
def test_extra_paid_request_includes_unrecorded_primary_cost(monkeypatch, tmp_path, primary_cost, remaining):
    from scripts.cycle_navigator import daily_path_recovery as repair
    called = []
    monkeypatch.setattr(repair.urllib.request, "urlopen", lambda *a, **k: called.append(1))
    reservation = tmp_path / "reserved-before-real-api.json"
    _, receipt = _run(_value(), cost_receipt_path=reservation,
                      budget_check=lambda: {"status":"PASS", "remaining_usd_before":remaining},
                      primary_unaccounted_cost_usd=primary_cost)
    assert receipt["status"] == "SKIPPED_PAID_RECOVERY_DISABLED"
    assert receipt["attempt_count"] == 0 and called == []
    assert not reservation.exists()


def test_semantic_retry_does_not_feed_model_its_old_abstention_rationale():
    from scripts.cycle_navigator.daily_path_recovery import _input_excerpt
    original = _value()
    original["forecast_freeze"]["daily_price_path"]["BTC"]["reason"] = "UNIQUE_OLD_REFUSAL_NOT_EVIDENCE"
    context = _context()
    src = {"quote": {"BTC": "USDT", "ETH": "USDT"}}
    payload = _input_excerpt(context, src, original, original["forecast_freeze"])
    assert "prior_abstentions" not in payload
    assert payload["prior_status"] == {"BTC": "UNAVAILABLE", "ETH": "UNAVAILABLE"}
    assert "UNIQUE_OLD_REFUSAL_NOT_EVIDENCE" not in __import__("json").dumps(payload)
