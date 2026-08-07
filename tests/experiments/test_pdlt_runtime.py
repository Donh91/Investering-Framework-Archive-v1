from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


sidecar = load_module("pdlt_capture_sidecar", "scripts/experiments/pdlt_capture_sidecar.py")
census = load_module("pdlt_daily_census", "scripts/experiments/pdlt_daily_census.py")
deterministic = load_module("pdlt_deterministic_forecast", "scripts/experiments/pdlt_deterministic_forecast.py")
maturation = load_module("pdlt_maturation", "scripts/experiments/pdlt_maturation.py")
cost_guard = load_module("pdlt_cost_guard", "scripts/experiments/pdlt_cost_guard.py")
discovery = load_module("pdlt_discovery", "scripts/experiments/pdlt_discovery.py")

FIELDS = sidecar.FIELDS


def cfgi_row(symbol: str, timestamp: str, base: float) -> dict:
    return {
        "symbol": symbol,
        "timestamp": timestamp,
        "score": base,
        "classification": "TEST",
        "stale": False,
        "owner_status": "PASS",
        "components": {field: base + i for i, field in enumerate(FIELDS) if field != "score"},
    }


class PDLTRuntimeTests(unittest.TestCase):
    def test_sidecar_flattens_all_ten_cfgi_fields(self):
        snapshot = {"rows": [cfgi_row(s, "2026-08-07T20:00:00Z", 40 + i) for i, s in enumerate(("MARKET", "BTC", "ETH"))]}
        status, symbols, problems = sidecar.compact_cfgi(snapshot)
        self.assertEqual(status, "PASS")
        self.assertEqual(problems, [])
        self.assertEqual(set(symbols), {"MARKET", "BTC", "ETH"})
        self.assertEqual(set(symbols["MARKET"]["values"]), set(FIELDS))
        self.assertTrue(all(symbols["MARKET"]["values"][f] is not None for f in FIELDS))

    def test_sidecar_degrades_on_missing_field(self):
        row = cfgi_row("MARKET", "2026-08-07T20:00:00Z", 40)
        del row["components"]["orders"]
        snapshot = {"rows": [row, cfgi_row("BTC", "2026-08-07T20:00:00Z", 41), cfgi_row("ETH", "2026-08-07T20:00:00Z", 42)]}
        status, _, problems = sidecar.compact_cfgi(snapshot)
        self.assertEqual(status, "DEGRADED")
        self.assertTrue(any("orders" in p for p in problems))

    def test_cfgi_complete_accepts_only_full_three_symbol_sidecar(self):
        symbols = {}
        for i, s in enumerate(("MARKET", "BTC", "ETH")):
            symbols[s] = {"values": {field: 40 + i for field in FIELDS}}
        row = {"status": "PASS", "cfgi": {"symbols": symbols}}
        self.assertTrue(census.cfgi_complete(row))
        del symbols["ETH"]["values"]["orders"]
        self.assertFalse(census.cfgi_complete(row))

    def test_deterministic_b_fires_candidate_without_altering_a(self):
        model = {
            "contract": "PDLT_FROZEN_MODEL_v1",
            "baseline_probabilities": {
                "p_pullback_72h": 0.25,
                "p_heavy_pullback_7d": 0.15,
                "p_persistent_distribution_14d": 0.10,
            },
            "candidates": [{
                "candidate_id": "C1",
                "forward_eligible": True,
                "conditions": [{"symbol": "MARKET", "field": "orders", "operator": "<=", "threshold": -5.0}],
                "probabilities": {
                    "p_pullback_72h": 0.70,
                    "p_heavy_pullback_7d": 0.40,
                    "p_persistent_distribution_14d": 0.30,
                },
            }],
        }
        ctx = {"cutoff_utc": "2026-08-07T20:00:00Z", "cfgi": {"latest_deltas": {"MARKET": {"orders": -6.0}}}}
        value = deterministic.run(model, ctx)
        self.assertEqual(value["fired_candidates"], ["C1"])
        self.assertEqual(value["arm_a"]["p_pullback_72h"], 0.25)
        self.assertEqual(value["arm_b"]["p_pullback_72h"], 0.70)

    def test_cost_guard_counts_unique_current_and_historical_receipts(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            a = root / "a"; b = root / "b"
            a.mkdir(); b.mkdir()
            receipt = {"contract": "PDLT_OPENAI_RECEIPT_v1", "response_id": "r1", "estimated_cost_usd": 0.12}
            (a / "one.json").write_text(json.dumps(receipt))
            (b / "duplicate.json").write_text(json.dumps(receipt))
            (b / "two.json").write_text(json.dumps({"contract":"PDLT_OPENAI_RECEIPT_v1","response_id":"r2","estimated_cost_usd":0.20}))
            total, count = cost_guard.receipt_costs([a, b])
            self.assertAlmostEqual(total, 0.32)
            self.assertEqual(count, 2)

    def test_maturation_stats_compute_mae_mfe_and_first_breach(self):
        start_time = datetime(2026, 8, 1, tzinfo=timezone.utc)
        rows = []
        for i in range(1, 73):
            close = 100.0 - min(i, 10) * 0.25
            low = 96.5 if i == 12 else close - 0.2
            high = 103.0 if i == 20 else close + 0.2
            rows.append({
                "open_time": (start_time + timedelta(hours=i)).isoformat().replace("+00:00", "Z"),
                "dt": start_time + timedelta(hours=i),
                "low": low,
                "high": high,
                "close": close,
            })
        value = maturation.stats(rows, start_time, 72, 100.0, 3.0, False)
        self.assertIsNotNone(value)
        assert value is not None
        self.assertTrue(value["event"])
        self.assertGreaterEqual(value["mae_pct"], 3.0)
        self.assertGreaterEqual(value["mfe_pct"], 3.0)
        self.assertEqual(value["lead_time_hours"], 12.0)

    def test_quantile_is_deterministic(self):
        self.assertEqual(discovery.quantile([1.0, 2.0, 3.0, 4.0, 5.0], 0.5), 3.0)
        self.assertAlmostEqual(discovery.quantile([0.0, 10.0], 0.25), 2.5)


if __name__ == "__main__":
    unittest.main()
