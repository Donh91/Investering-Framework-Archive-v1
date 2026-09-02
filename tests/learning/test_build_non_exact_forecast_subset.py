from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.learning.build_non_exact_forecast_subset import build_subset


class NonExactForecastSubsetTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.forecasts = self.root / "forecasts"
        self.output = self.root / "subset"
        self.forecasts.mkdir()
        self.addCleanup(self.tmp.cleanup)

    def write(self, relative: str, value: dict) -> Path:
        path = self.forecasts / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, sort_keys=True) + "\n")
        return path

    def test_exact_forecast_is_excluded(self):
        self.write("exact.json", {
            "contract": "FROZEN_FORECAST_v1",
            "forecast_id": "exact",
            "settlement_contract_version": "FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1",
        })
        result = build_subset(self.forecasts, self.output)
        self.assertEqual(result["excluded_exact_forecasts"], 1)
        self.assertEqual(result["copied_non_exact_forecasts"], 0)
        self.assertFalse((self.output / "exact.json").exists())

    def test_legacy_forecast_is_copied_byte_identically(self):
        source = self.write("2026/09/legacy.json", {
            "contract": "FROZEN_FORECAST_v1",
            "forecast_id": "legacy",
        })
        before = source.read_bytes()
        result = build_subset(self.forecasts, self.output)
        destination = self.output / "2026/09/legacy.json"
        self.assertEqual(result["copied_non_exact_forecasts"], 1)
        self.assertEqual(destination.read_bytes(), before)

    def test_non_forecast_json_is_skipped(self):
        self.write("metadata.json", {"contract": "OTHER"})
        result = build_subset(self.forecasts, self.output)
        self.assertEqual(result["skipped_non_forecast_json"], 1)
        self.assertFalse((self.output / "metadata.json").exists())

    def test_malformed_json_fails_closed(self):
        path = self.forecasts / "bad.json"
        path.write_text("{")
        with self.assertRaises(json.JSONDecodeError):
            build_subset(self.forecasts, self.output)


if __name__ == "__main__":
    unittest.main()
