from __future__ import annotations

import csv
import importlib.util
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts/research/copper_gold_slow_cycle_event_study.py"
SPEC = importlib.util.spec_from_file_location("copper_gold_slow_cycle_event_study", MODULE_PATH)
study = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = study
assert SPEC.loader is not None
SPEC.loader.exec_module(study)


def test_state_join_never_uses_future_bar():
    rows = [
        {"bar_end_day": date(2020, 2, 29), "bar_end_period": "2020-02", "bar_end_timestamp": "2020-02-29T23:59:59Z", "regime_state": "EXPANSION", "macd_histogram": 0.1, "rsi_14_wilder": 60.0},
        {"bar_end_day": date(2020, 4, 30), "bar_end_period": "2020-04", "bar_end_timestamp": "2020-04-30T23:59:59Z", "regime_state": "TURNING_NEGATIVE", "macd_histogram": -0.1, "rsi_14_wilder": 45.0},
    ]
    value = study.latest_settled_state(rows, date(2020, 3, 15))
    assert value["bar_end_period"] == "2020-02"
    assert value["lookahead_guard"] == "KNOWLEDGE_AVAILABLE_ON_OR_BEFORE_EVENT_EOD"


def test_forward_metrics_require_matured_horizon():
    start = date(2020, 1, 1)
    prices = [(start + timedelta(days=offset), 100.0 - offset / 10) for offset in range(241)]
    value = study.forward_metrics(prices, 0)
    assert value["return_60d_pct"] == pytest.approx(-6.0)
    assert value["max_drawdown_240d_pct"] == pytest.approx(-24.0)
    assert value["return_365d_pct"] is None


def test_peak_labels_reclaim_as_mid_cycle_and_cluster_candidates():
    start = date(2020, 1, 1)
    prices = []
    for offset in range(900):
        if offset <= 400:
            price = 100.0 + offset
        elif offset <= 550:
            price = 500.0 - (offset - 400) * 1.5
        else:
            price = 275.0 + (offset - 550) * 2.0
        prices.append((start + timedelta(days=offset), price))
    peaks = study.objective_peak_episodes(prices)
    assert peaks[0]["event_day"] == start + timedelta(days=400)
    assert peaks[0]["outcome_label"] == "MID_CYCLE_RECLAIMED_WITHIN_365D"


def test_pre_btc_copper_gold_events_are_not_mapped_to_first_btc_day():
    rows = [{"bar_end_day": date(1990, 1, 31), "bar_end_period": "1990-01", "regime_state": "TURNING_NEGATIVE"}]
    start = date(2010, 7, 18)
    btc = [(start + timedelta(days=offset), 100.0 + offset) for offset in range(400)]
    assert study.signal_events(rows, "TURNING_NEGATIVE", btc) == []


def test_btc_loader_accepts_coinmetrics_time_and_rejects_duplicates():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "btc.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["time", "PriceUSD"])
            writer.writerow(["2020-01-01", "100"])
            writer.writerow(["2020-01-02", "101"])
        assert study.load_btc(path) == [(date(2020, 1, 1), 100.0), (date(2020, 1, 2), 101.0)]
        with path.open("a", newline="", encoding="utf-8") as handle:
            csv.writer(handle).writerow(["2020-01-02", "102"])
        with pytest.raises(ValueError, match="btc_duplicate_date"):
            study.load_btc(path)


def test_state_join_uses_knowledge_time_not_bar_end():
    rows = [
        {
            "bar_end_day": date(2020, 2, 29),
            "bar_end_period": "2020-02",
            "bar_end_timestamp": "2020-02-29T23:59:59Z",
            "knowledge_at": study.parse_utc("2020-03-04T00:00:00Z"),
            "knowledge_time_status": "OWNER_RECORDED_WORKBOOK_UPDATED_ON",
            "regime_state": "EXPANSION",
            "macd_histogram": 0.1,
            "rsi_14_wilder": 60.0,
        },
        {
            "bar_end_day": date(2020, 4, 30),
            "bar_end_period": "2020-04",
            "bar_end_timestamp": "2020-04-30T23:59:59Z",
            "knowledge_at": study.parse_utc("2020-05-05T00:00:00Z"),
            "knowledge_time_status": "OWNER_RECORDED_WORKBOOK_UPDATED_ON",
            "regime_state": "TURNING_NEGATIVE",
            "macd_histogram": -0.1,
            "rsi_14_wilder": 45.0,
        },
    ]
    assert study.latest_settled_state(rows, date(2020, 3, 3)) is None
    value = study.latest_settled_state(rows, date(2020, 3, 4))
    assert value["bar_end_period"] == "2020-02"
    assert value["knowledge_available_at_utc"] == "2020-03-04T00:00:00Z"


def test_signal_event_enters_at_first_btc_eod_after_knowledge_time():
    start = date(2020, 1, 1)
    btc = [(start + timedelta(days=i), 100.0 + i) for i in range(400)]
    rows = [{
        "bar_end_day": date(2020, 2, 29),
        "bar_end_period": "2020-02",
        "bar_end_timestamp": "2020-02-29T23:59:59Z",
        "knowledge_at": study.parse_utc("2020-03-04T00:00:00Z"),
        "knowledge_time_status": "OWNER_RECORDED_WORKBOOK_UPDATED_ON",
        "regime_state": "TURNING_NEGATIVE",
    }]
    events = study.signal_events(rows, "TURNING_NEGATIVE", btc)
    assert len(events) == 1
    assert events[0]["event_date"] == "2020-03-04"
    assert events[0]["source_knowledge_available_at_utc"] == "2020-03-04T00:00:00Z"


def test_publication_evidence_and_fallback_are_explicit():
    with tempfile.TemporaryDirectory() as tmp:
        revisions = Path(tmp) / "revisions"
        revisions.mkdir()
        (revisions / "receipt.json").write_text(
            """{
              "coverage": {"last_period": "2020-02"},
              "source": {"workbook_updated_on": "March 04, 2020"}
            }""",
            encoding="utf-8",
        )
        evidence = study.load_publication_evidence(revisions)
        exact = {
            "bar_end_period": "2020-02",
            "bar_end_timestamp": "2020-02-29T23:59:59Z",
        }
        study.annotate_feature_knowledge(exact, evidence, 86401)
        assert exact["knowledge_at"] == study.parse_utc("2020-03-04T00:00:00Z")
        assert exact["knowledge_time_status"] == "OWNER_RECORDED_WORKBOOK_UPDATED_ON"

        fallback = {
            "bar_end_period": "2020-04",
            "bar_end_timestamp": "2020-04-30T23:59:59Z",
        }
        study.annotate_feature_knowledge(fallback, evidence, 86401)
        assert fallback["knowledge_at"] == study.parse_utc("2020-05-02T00:00:00Z")
        assert fallback["knowledge_time_status"] == "EXPLICIT_PUBLICATION_LAG_LOWER_BOUND"

        with pytest.raises(ValueError, match="publication_lag_lower_bound_seconds_required"):
            study.annotate_feature_knowledge(dict(fallback), evidence, None)
