from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from scripts.intraday_execution.intraday_execution_research import asset_features
from scripts.intraday_execution import shadow_direction_confidence as sdc


def test_asset_features_accepts_hourly_rows_as_timestamp_row_tuples():
    start = datetime(2026, 8, 24, 0, 0, tzinfo=timezone.utc)
    pairs = []
    for index in range(6):
        row = {
            "btc_close": str(100 + index),
            "btc_high": str(101 + index),
            "btc_low": str(99 + index),
            "btc_quote_volume": "200" if index == 5 else "100",
            "btc_volume": "1",
            "btc_return_1h_pct": "1.0",
            "btc_taker_buy_quote_share": "0.55",
            "btc_oi_change_1h_pct": "0.2",
            "btc_funding_event_rate": "0.0001",
        }
        pairs.append((start + timedelta(hours=index), row))

    features = asset_features("btc", pairs)

    assert features["close"] == 105.0
    assert features["rolling_relative_quote_volume"] == 2.0
    assert features["return_4h_pct"] == (105.0 / 101.0 - 1.0) * 100.0


def test_shadow_direction_uses_no_edge_when_evidence_is_split():
    votes = [
        {"family": "a", "direction": "UP", "value": 1.0},
        {"family": "b", "direction": "UP", "value": 1.0},
        {"family": "c", "direction": "DOWN", "value": -1.0},
        {"family": "d", "direction": "DOWN", "value": -1.0},
    ]
    result = sdc.summarize_votes(votes, {"minimum_direction_families": 4, "minimum_vote_margin": 2})
    assert result["direction"] == "NO_EDGE"
    assert result["evidence_agreement_pct"] == 50.0


def test_shadow_direction_freezes_direction_without_calling_agreement_probability():
    obs = {
        "btc": {
            "return_1h_pct": 0.2,
            "return_4h_pct": 0.8,
            "vwap_deviation_pct": 0.4,
            "momentum_acceleration_1h_vs_prior3h_pp": 0.1,
            "taker_buy_quote_share": 0.56,
            "taker_buy_share_delta_vs_prior3h": 0.02,
        },
        "eth": {
            "return_1h_pct": 0.3,
            "return_4h_pct": 0.9,
            "vwap_deviation_pct": 0.5,
            "momentum_acceleration_1h_vs_prior3h_pp": 0.2,
            "taker_buy_quote_share": 0.57,
            "taker_buy_share_delta_vs_prior3h": 0.03,
        },
        "ethbtc": {"return_1h_pct": 0.1},
        "breadth": {"advance_ratio": 0.7},
    }
    summary = sdc.summarize_votes(
        sdc.build_votes("ETH", obs),
        {"minimum_direction_families": 4, "minimum_vote_margin": 2},
    )
    assert summary["direction"] == "UP"
    assert summary["evidence_agreement_pct"] == 100.0
    assert "calibrated_probability" not in summary


def test_calibration_hides_numeric_probability_during_warmup(tmp_path, monkeypatch):
    outcomes = tmp_path / "outcomes"
    calibration_path = tmp_path / "calibration.json"
    monkeypatch.setattr(sdc, "OUTCOMES", outcomes)
    monkeypatch.setattr(sdc, "CALIBRATION", calibration_path)

    start = datetime(2026, 8, 1, tzinfo=timezone.utc)
    for index in range(5):
        issued = start + timedelta(hours=index)
        sdc.write_json(
            outcomes / f"{index}.json",
            {
                "contract": "INTRADAY_DIRECTION_OUTCOME_v1",
                "status": "MATURED",
                "result": "HIT",
                "issued_at_utc": sdc.iso(issued),
                "source_price_observation_utc": sdc.iso(issued),
                "target": "BTC",
                "horizon_hours": 1,
                "actual_direction": "UP",
                "calibration_group": "BTC:1H:UP:6_of_6",
                "votes": [{"family": "return_1h", "direction": "UP"}],
                "brier_score": None,
            },
        )

    summary = sdc.build_calibration_summary(
        {
            "minimum_independent_calibration_samples": 20,
            "strong_calibration_samples": 50,
            "high_assurance_minimum_independent_samples": 300,
            "high_assurance_wilson_floor": 0.97,
        },
        start + timedelta(days=1),
    )
    group = summary["groups"]["BTC:1H:UP:6_of_6"]
    assert group["independent_count"] == 5
    assert group["maturity"] == "WARMUP"
    assert group["display_probability"] is None


def test_calibration_exposes_conservative_estimate_after_minimum_sample(tmp_path, monkeypatch):
    outcomes = tmp_path / "outcomes"
    calibration_path = tmp_path / "calibration.json"
    monkeypatch.setattr(sdc, "OUTCOMES", outcomes)
    monkeypatch.setattr(sdc, "CALIBRATION", calibration_path)

    start = datetime(2026, 8, 1, tzinfo=timezone.utc)
    for index in range(20):
        issued = start + timedelta(hours=index)
        sdc.write_json(
            outcomes / f"{index}.json",
            {
                "contract": "INTRADAY_DIRECTION_OUTCOME_v1",
                "status": "MATURED",
                "result": "HIT",
                "issued_at_utc": sdc.iso(issued),
                "source_price_observation_utc": sdc.iso(issued),
                "target": "BTC",
                "horizon_hours": 1,
                "actual_direction": "UP",
                "calibration_group": "BTC:1H:UP:6_of_6",
                "votes": [{"family": "return_1h", "direction": "UP"}],
                "brier_score": None,
            },
        )

    summary = sdc.build_calibration_summary(
        {
            "minimum_independent_calibration_samples": 20,
            "strong_calibration_samples": 50,
            "high_assurance_minimum_independent_samples": 300,
            "high_assurance_wilson_floor": 0.97,
        },
        start + timedelta(days=2),
    )
    group = summary["groups"]["BTC:1H:UP:6_of_6"]
    assert group["maturity"] == "EARLY_CALIBRATION"
    assert group["empirical_hit_rate"] == 1.0
    assert group["display_probability"] < 1.0
    assert group["display_probability"] == round(21 / 22, 6)


def test_horizon_freeze_is_anchored_to_generic_source_observation_and_fails_closed_on_short_span():
    observed = datetime(2026, 8, 30, 10, 0, tzinfo=timezone.utc)
    now = observed + timedelta(minutes=40)
    obs = {"price_observation_utc": sdc.iso(observed)}
    cfg = {"minimum_remaining_fraction_of_horizon": 0.5}

    one_hour = sdc._horizon_eligibility(obs, now, 1, cfg)
    four_hour = sdc._horizon_eligibility(obs, now, 4, cfg)

    assert one_hour["status"] == "INSUFFICIENT_REMAINING_FORWARD_SPAN"
    assert one_hour["due_at_utc"] == sdc.iso(observed + timedelta(hours=1))
    assert four_hour["status"] == "ELIGIBLE"
    assert four_hour["due_at_utc"] == sdc.iso(observed + timedelta(hours=4))


def test_hourly_owner_timestamp_is_candle_open_and_forecast_starts_at_observable_close():
    candle_open = datetime(2026, 8, 30, 10, 0, tzinfo=timezone.utc)
    observable_close = candle_open + timedelta(hours=1)
    now = observable_close + timedelta(minutes=10)
    obs = {
        "price_observation_utc": sdc.iso(candle_open),
        "hourly_sequence_run_id": "HOURLY_SEQUENCE_TEST",
    }
    cfg = {"minimum_remaining_fraction_of_horizon": 0.5}

    assert sdc._source_price_observation_time(obs) == observable_close
    one_hour = sdc._horizon_eligibility(obs, now, 1, cfg)
    assert one_hour["status"] == "ELIGIBLE"
    assert one_hour["source_cutoff_utc"] == sdc.iso(observable_close)
    assert one_hour["due_at_utc"] == sdc.iso(observable_close + timedelta(hours=1))
    assert one_hour["remaining_forward_hours_at_issue"] == round(50 / 60, 6)


def _write_prediction_fixture(predictions, issued, source_close, due, *, direction="UP"):
    sdc.write_json(
        predictions / "prediction.json",
        {
            "contract": "INTRADAY_DIRECTION_PREDICTION_v1",
            "issued_at_utc": sdc.iso(issued),
            "source_candle_open_utc": sdc.iso(source_close - timedelta(hours=1)),
            "source_price_observation_utc": sdc.iso(source_close),
            "horizons": {
                "1H": {
                    "horizon_hours": 1,
                    "due_at_utc": sdc.iso(due),
                    "targets": {
                        "BTC": {
                            "direction": direction,
                            "start_value": 100.0,
                            "calibration_key": "6_of_6",
                            "votes": [{"family": "return_1h", "direction": direction}],
                            "frozen_calibrated_probability_pct": None,
                        }
                    },
                }
            },
        },
    )


def test_outcome_uses_exact_due_owner_candle_not_a_later_current_price(tmp_path, monkeypatch):
    predictions = tmp_path / "predictions"
    outcomes = tmp_path / "outcomes"
    hourly = tmp_path / "hourly"
    monkeypatch.setattr(sdc, "PREDICTIONS", predictions)
    monkeypatch.setattr(sdc, "OUTCOMES", outcomes)
    monkeypatch.setattr(sdc, "HOURLY_ROOT", hourly)

    source_close = datetime(2026, 8, 30, 11, 0, tzinfo=timezone.utc)
    due = source_close + timedelta(hours=1)
    issued = source_close + timedelta(minutes=10)
    _write_prediction_fixture(predictions, issued, source_close, due)

    path = hourly / "2026/08/2026-08-30.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "timestamp_utc,btc_close,spot_status\n"
        f"{sdc.iso(due - timedelta(hours=1))},101.0,PASS\n"
    )

    # Current price deliberately points the opposite way. It must never be used.
    obs = {
        "price_observation_utc": sdc.iso(datetime(2026, 8, 30, 12, 0, tzinfo=timezone.utc)),
        "hourly_sequence_run_id": "HOURLY_SEQUENCE_LATER",
        "btc": {"close": 50.0},
    }
    counts = sdc.mature_predictions(
        obs,
        {"max_outcome_evidence_lag_hours": 1.5},
        datetime(2026, 8, 30, 13, 5, tzinfo=timezone.utc),
    )

    assert counts["matured"] == 1
    result = next(outcomes.rglob("*.json"))
    row = sdc.read_json(result)
    assert row["result"] == "HIT"
    assert row["end_value"] == 101.0
    assert row["evidence_observation_utc"] == sdc.iso(due)
    assert row["evidence_horizon_error_hours"] == 0.0
    assert row["evidence_semantics"] == "EXACT_DUE_CLOSED_1H_OWNER_CANDLE"


def test_missing_exact_due_candle_is_censored_instead_of_using_later_price(tmp_path, monkeypatch):
    predictions = tmp_path / "predictions"
    outcomes = tmp_path / "outcomes"
    hourly = tmp_path / "hourly"
    monkeypatch.setattr(sdc, "PREDICTIONS", predictions)
    monkeypatch.setattr(sdc, "OUTCOMES", outcomes)
    monkeypatch.setattr(sdc, "HOURLY_ROOT", hourly)

    source_close = datetime(2026, 8, 30, 10, 0, tzinfo=timezone.utc)
    due = source_close + timedelta(hours=1)
    issued = source_close + timedelta(minutes=5)
    _write_prediction_fixture(predictions, issued, source_close, due)

    obs = {
        "price_observation_utc": sdc.iso(datetime(2026, 8, 30, 13, 0, tzinfo=timezone.utc)),
        "hourly_sequence_run_id": "HOURLY_SEQUENCE_LATER",
        "btc": {"close": 150.0},
    }
    counts = sdc.mature_predictions(
        obs,
        {"max_outcome_evidence_lag_hours": 1.5},
        datetime(2026, 8, 30, 14, 5, tzinfo=timezone.utc),
    )

    assert counts["censored"] == 1
    result = next(outcomes.rglob("*.json"))
    row = sdc.read_json(result)
    assert row["status"] == "CENSORED"
    assert row["reason"] == "EXACT_DUE_OWNER_CANDLE_MISSING_AFTER_GRACE"
    assert row["substitute_later_price_forbidden"] is True


def test_market_cap_transmission_marks_microcap_unavailable(tmp_path, monkeypatch):
    breadth_path = tmp_path / "breadth.json"
    sdc.write_json(
        breadth_path,
        {
            "constituents": [
                {"filtered_rank": 3, "change_24h_pct": 1.0},
                {"filtered_rank": 4, "change_24h_pct": 2.0},
                {"filtered_rank": 26, "change_24h_pct": -1.0},
                {"filtered_rank": 27, "change_24h_pct": -2.0},
                {"filtered_rank": 51, "change_24h_pct": 0.5},
                {"filtered_rank": 52, "change_24h_pct": -0.5},
            ]
        },
    )
    monkeypatch.setattr(sdc, "BREADTH", breadth_path)
    transmission = sdc.build_market_cap_transmission()
    assert transmission["large_cap_proxy"]["direction"] == "UP"
    assert transmission["mid_cap_proxy"]["direction"] == "DOWN"
    assert transmission["small_cap_proxy"]["direction"] == "NO_EDGE"
    assert transmission["microcap"]["direction"] == "NO_EDGE"
    assert transmission["microcap"]["reason"] == "CURRENT_BREADTH_OWNER_STOPS_AT_TOP100"


def test_rounding_cannot_display_99_without_high_assurance():
    group = {"display_probability": 101 / 102, "maturity": "CALIBRATED", "independent_count": 100, "wilson_lower_95": 0.96}
    summary = {"groups": {"BTC:1H:UP:6_of_6": group}}
    view = sdc._calibration_view(summary, "BTC", 1, {"direction": "UP", "calibration_key": "6_of_6"})
    assert view["calibrated_probability"] is None


def test_high_assurance_requires_independent_samples_and_wilson_floor():
    start = datetime(2026, 8, 1, tzinfo=timezone.utc)
    rows = [{"status": "MATURED", "result": "HIT", "issued_at_utc": sdc.iso(start + timedelta(hours=i)), "source_price_observation_utc": sdc.iso(start + timedelta(hours=i)), "target": "BTC", "horizon_hours": 1, "actual_direction": "UP", "calibration_group": "BTC:1H:UP:6_of_6", "votes": [], "brier_score": None} for i in range(300)]
    cfg = {"minimum_independent_calibration_samples": 20, "strong_calibration_samples": 50, "high_assurance_minimum_independent_samples": 300, "high_assurance_wilson_floor": 0.97}
    early = sdc.calibration_summary_from_rows(rows[:100], cfg, start + timedelta(days=20))["groups"]["BTC:1H:UP:6_of_6"]
    assert early["maturity"] == "CALIBRATED"
    assert early["display_probability"] is None
    mature = sdc.calibration_summary_from_rows(rows, cfg, start + timedelta(days=20))["groups"]["BTC:1H:UP:6_of_6"]
    assert mature["maturity"] == "HIGH_ASSURANCE_99_ELIGIBLE"
    assert mature["independent_count"] == 300
    assert mature["wilson_lower_95"] >= 0.97
    blocked = sdc.calibration_summary_from_rows(rows, {**cfg, "high_assurance_wilson_floor": 0.999}, start + timedelta(days=20))["groups"]["BTC:1H:UP:6_of_6"]
    assert blocked["maturity"] == "CALIBRATED_STRONG"
    assert blocked["display_probability"] is None


def test_future_due_candle_cannot_mature_before_actual_clock(tmp_path, monkeypatch):
    monkeypatch.setattr(sdc, "PREDICTIONS", tmp_path / "predictions")
    monkeypatch.setattr(sdc, "OUTCOMES", tmp_path / "outcomes")
    monkeypatch.setattr(sdc, "HOURLY_ROOT", tmp_path / "hourly")
    source_close = datetime(2026, 8, 31, 10, tzinfo=timezone.utc)
    due = source_close + timedelta(hours=1)
    _write_prediction_fixture(sdc.PREDICTIONS, source_close + timedelta(minutes=10), source_close, due)
    path = sdc.HOURLY_ROOT / "2026/08/2026-08-31.csv"
    path.parent.mkdir(parents=True)
    path.write_text("timestamp_utc,btc_close,spot_status\n2026-08-31T10:00:00Z,101,PASS\n")
    # A future-labelled source and an already-present fixture cannot advance UTC.
    obs = {"price_observation_utc": sdc.iso(due), "hourly_sequence_run_id": "fixture"}
    counts = sdc.mature_predictions(obs, {}, source_close + timedelta(minutes=30))
    assert counts == {"matured": 0, "censored": 0, "abstained": 0, "pending": 1}
    assert not sdc.OUTCOMES.exists()


def test_stale_source_cannot_display_long_horizon_as_eligible():
    close = datetime(2026, 8, 31, 10, tzinfo=timezone.utc)
    obs = {"price_close_observation_utc": sdc.iso(close)}
    result = sdc._horizon_eligibility(obs, close + timedelta(hours=2), 24, {})
    assert result["status"] == "SOURCE_TOO_STALE"


def test_branch_or_local_run_has_no_production_context(monkeypatch):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    assert sdc.production_context() is None
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_REPOSITORY", sdc.REPOSITORY)
    monkeypatch.setenv("GITHUB_REF", "refs/heads/agent/task-fixture")
    monkeypatch.setenv("GITHUB_EVENT_NAME", "workflow_dispatch")
    monkeypatch.setenv("GITHUB_RUN_ID", "123")
    assert sdc.production_context() is None


@pytest.mark.parametrize("asset", ["btc", "eth", "ethbtc"])
@pytest.mark.parametrize("invalid_close", [None, True, float("nan"), float("inf"), -float("inf"), 0, -1, "100"])
def test_prediction_writer_rejects_invalid_price_before_creating_any_row(tmp_path, monkeypatch, asset, invalid_close):
    monkeypatch.setattr(sdc, "PREDICTIONS", tmp_path / "predictions")
    now = datetime(2026, 8, 31, 10, 15, tzinfo=timezone.utc)
    obs = {key: {"close": 100.0} for key in ("btc", "eth", "ethbtc")}
    obs.update(price_observation_utc="2026-08-31T09:00:00Z", hourly_sequence_run_id="fixture")
    obs[asset]["close"] = invalid_close
    result = sdc.write_prediction(obs, {}, now, {}, {}, registration={"receipt_sha256": "fixture"}, context={"run_id": "fixture"})
    assert result == ("INVALID_SOURCE_PRICE_NO_PREDICTION", None)
    assert not sdc.PREDICTIONS.exists()


@pytest.mark.parametrize("first_issue_minutes", [15, 40])
def test_owner_runtime_freeze_retry_and_future_maturation_are_separate(tmp_path, monkeypatch, capsys, first_issue_minutes):
    import csv
    import json
    from pathlib import Path
    from scripts.intraday_execution import intraday_execution_research as research
    from scripts.intraday_execution.validate_direction_confidence import validate_repository

    repo = Path(__file__).resolve().parents[2]
    cfg = json.loads((repo / research.CONFIG).read_text())
    registry_path = Path("06_RESEARCH_LAB/forward_tests/2026-07-10__active-test-registry__canonical.md")
    registry_text = (repo / registry_path).read_text()
    monkeypatch.chdir(tmp_path)
    sdc.write_json(research.CONFIG, cfg)
    registry_path.parent.mkdir(parents=True)
    registry_path.write_text(registry_text)
    sdc.write_json(research.ENTRY, {
        "contract": "ENTRY_SIGNAL_LATEST_v1", "state": "WAIT",
        "promotion_authority": {"status": "FORWARD_ONLY_NOT_PROMOTION_READY", "permits_active_state": False},
        "measurement_validity": {"breadth_entry_permission": "RETIRED_ZERO_WEIGHT"},
        "authority": {"portfolio_execution": False, "canonical_market_state": False, "market_rule_change": False},
    })
    context = {"repository": sdc.REPOSITORY, "ref": "refs/heads/main", "event": "schedule", "run_id": "12345", "run_attempt": "1", "commit_sha": "a" * 40}
    # Synthetic Actions attestation only; the actual owner and validator run below.
    monkeypatch.setattr(sdc, "production_context", lambda: context)
    source_close = datetime(2026, 8, 31, 10, tzinfo=timezone.utc)
    clock = [source_close + timedelta(minutes=first_issue_minutes)]
    monkeypatch.setattr(research, "now_utc", lambda: clock[0])
    rows = []

    def append_candle(opened, close):
        row = {"timestamp_utc": sdc.iso(opened), "spot_status": "PASS", "ethbtc_close": "0.03", "ethbtc_high": "0.031", "ethbtc_return_1h_pct": "0.1"}
        for asset in ("btc", "eth"):
            for key, value in {"close": close, "high": close+1, "low": close-1, "volume": 1, "quote_volume": close, "return_1h_pct": 0.1, "taker_buy_quote_share": 0.6}.items():
                row[f"{asset}_{key}"] = str(value)
        rows.append(row)

    def publish_hourly(end):
        for day in {row["timestamp_utc"][:10] for row in rows}:
            stamp = datetime.fromisoformat(day)
            path = sdc.HOURLY_ROOT / f"{stamp:%Y/%m/%Y-%m-%d}.csv"
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(row for row in rows if row["timestamp_utc"].startswith(day))
        sdc.write_json(research.HOURLY_POINTER, {"status": "COMPLETE", "run_id": "fixture-hourly", "requested_hours": 26, "window_start_utc": sdc.iso(end-timedelta(hours=26)), "window_end_utc": sdc.iso(end)})

    for index in range(26):
        append_candle(source_close-timedelta(hours=26-index), 100.0)
    publish_hourly(source_close)
    legacy_path = research.OBS / "2026/08/31/20260831T090000Z.json"
    sdc.write_json(legacy_path, {"contract": "INTRADAY_EXECUTION_OBSERVATION_v1", "price_observation_utc": (source_close-timedelta(hours=1)).isoformat(), "research_state": "REGIME_NOT_ACTIVE"})
    legacy_bytes = legacy_path.read_bytes()

    research.main()
    capsys.readouterr()
    first = validate_repository(tmp_path, now=clock[0])
    assert first["prediction_rows_validated"] == 1
    assert first["outcome_rows_validated"] == 0
    assert sdc.REGISTRATION.exists()
    assert legacy_path.read_bytes() == legacy_bytes
    frozen = {path: path.read_bytes() for path in sdc.PREDICTIONS.rglob("*.json")}
    if first_issue_minutes > 30:
        latest = json.loads(research.LATEST.read_text())["shadow_direction_confidence"]
        assert all(target["direction"] == "NO_EDGE" and target["calibrated_probability"] is None for target in latest["horizons"]["1H"]["targets"].values())
        assert "1H BTC NO_EDGE(UNAVAILABLE)" in latest["data_ping_bridge"]["display_line"]
        assert all("1H" not in json.loads(raw)["horizons"] for raw in frozen.values())
    clock[0] += timedelta(minutes=5)
    research.main()
    capsys.readouterr()
    assert frozen == {path: path.read_bytes() for path in sdc.PREDICTIONS.rglob("*.json")}
    assert not sdc.OUTCOMES.exists()

    entry = json.loads(research.ENTRY.read_text())
    sdc.write_json(research.ENTRY, {**entry, "state": "GRADUATED_ALTCOIN_TOPUP_ACTIVE"})
    research.main()
    capsys.readouterr()
    latest = json.loads(research.LATEST.read_text())
    assert latest["adaptive_evidence"]["research_eligibility"]["eligible"] is False
    assert latest["shadow_direction_confidence"]["prediction_freeze"]["status"] == "RESEARCH_CONTEXT_INELIGIBLE_NO_PREDICTION"
    assert all(target["direction"] == "NO_EDGE" for horizon in latest["shadow_direction_confidence"]["horizons"].values() for target in horizon["targets"].values())
    assert legacy_path.read_bytes() == legacy_bytes
    sdc.write_json(research.ENTRY, entry)

    # Only advancing this explicitly synthetic clock and publishing the exact
    # next closed candle can produce a fixture outcome. This is not live evidence.
    append_candle(source_close, 101.0)
    publish_hourly(source_close+timedelta(hours=1))
    clock[0] = source_close+timedelta(hours=1, minutes=15)
    # A branch/local run must not append canonical outcomes or calibration,
    # even after a genuine prediction's due time has passed in the fixture.
    calibration_bytes = sdc.CALIBRATION.read_bytes()
    registration_bytes = sdc.REGISTRATION.read_bytes()
    monkeypatch.setattr(sdc, "production_context", lambda: None)
    research.main()
    capsys.readouterr()
    assert not sdc.OUTCOMES.exists()
    assert frozen == {path: path.read_bytes() for path in sdc.PREDICTIONS.rglob("*.json")}
    assert sdc.CALIBRATION.read_bytes() == calibration_bytes
    assert sdc.REGISTRATION.read_bytes() == registration_bytes
    monkeypatch.setattr(sdc, "production_context", lambda: context)
    research.main()
    capsys.readouterr()
    second = validate_repository(tmp_path, now=clock[0])
    assert second["prediction_rows_validated"] == 2
    assert second["outcome_rows_validated"] == (2 if first_issue_minutes <= 30 else 0)
    assert all(json.loads(path.read_text())["horizon_hours"] == 1 for path in sdc.OUTCOMES.rglob("*.json"))
    assert not research.EVENTS.exists()
    assert legacy_path.read_bytes() == legacy_bytes
