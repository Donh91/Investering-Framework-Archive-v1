from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.api_agent.build_owner_bound_director_context import build_context


class EnrichedLearningTests(unittest.TestCase):
    def test_metric_deltas_are_explicit(self) -> None:
        previous = {"contract": "DAILY_RAW_CAPTURE_INDEX_v2", "captured_at_utc": "2026-08-01T00:00:00Z", "run_id": "a", "owners": [{"owner_id": "binance_spot", "status": "PASS"}], "market_metrics": {"spot": {"BTCUSDT": {"close": 100.0}}}}
        latest = {"contract": "DAILY_RAW_CAPTURE_INDEX_v2", "captured_at_utc": "2026-08-01T04:00:00Z", "run_id": "b", "owners": [{"owner_id": "binance_spot", "status": "PASS"}], "market_metrics": {"spot": {"BTCUSDT": {"close": 102.0}}}}
        context = build_context([(Path("a.json"), previous), (Path("b.json"), latest)])
        row = next(x for x in context["metric_deltas"] if x["metric"] == "spot.BTCUSDT.close")
        self.assertEqual(row["absolute_change"], 2.0)
        self.assertEqual(row["percentage_change"], 2.0)
        self.assertFalse(context["canonical_data_ping"])

    def test_missing_previous_stays_unknown(self) -> None:
        latest = {"contract": "DAILY_RAW_CAPTURE_INDEX_v2", "captured_at_utc": "2026-08-01T04:00:00Z", "run_id": "b", "owners": [], "market_metrics": {"breadth": {"advancers": 61}}}
        context = build_context([(Path("b.json"), latest)])
        row = next(x for x in context["metric_deltas"] if x["metric"] == "breadth.advancers")
        self.assertIsNone(row["previous"])
        self.assertNotIn("absolute_change", row)


if __name__ == "__main__":
    unittest.main()
