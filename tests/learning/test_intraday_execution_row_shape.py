from __future__ import annotations

from datetime import datetime, timedelta, timezone

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
