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
    assert value["lookahead_guard"] == "BAR_END_ON_OR_BEFORE_EVENT"


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
