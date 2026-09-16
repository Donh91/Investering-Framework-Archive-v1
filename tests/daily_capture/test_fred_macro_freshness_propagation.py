import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.daily_capture.build_capture_index import latest_fred_values


class FredMacroFreshnessPropagationTests(unittest.TestCase):
    def _write_series(self, root: Path, series: str, rows: list[tuple[str, str]]) -> None:
        payload_root = root / "raw" / "source_payloads"
        payload_root.mkdir(parents=True, exist_ok=True)
        path = payload_root / f"run-1__{series}.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["DATE", series])
            writer.writerows(rows)

    def test_mixed_owner_freshness_survives_compaction(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows = {
                "DGS2": [("2026-09-07", "3.10")],
                "DGS10": [("2026-09-07", "4.20")],
                "VIXCLS": [("2026-09-07", "18.5")],
                "DTWEXBGS": [("2026-08-25", "118.2")],
            }
            for series, payload_rows in rows.items():
                self._write_series(root, series, payload_rows)

            retrieval = "2026-09-08T06:13:00Z"
            health_rows = [
                {
                    "series": "DGS2",
                    "status": "PASS",
                    "source_timestamp": "2026-09-07T00:00:00Z",
                    "retrieval_timestamp": retrieval,
                    "freshness_seconds": 108780,
                    "stale_after_seconds": 604800,
                },
                {
                    "series": "DGS10",
                    "status": "PASS",
                    "source_timestamp": "2026-09-07T00:00:00Z",
                    "retrieval_timestamp": retrieval,
                    "freshness_seconds": 108780,
                    "stale_after_seconds": 604800,
                },
                {
                    "series": "VIXCLS",
                    "status": "PASS",
                    "source_timestamp": "2026-09-07T00:00:00Z",
                    "retrieval_timestamp": retrieval,
                    "freshness_seconds": 108780,
                    "stale_after_seconds": 604800,
                },
                {
                    "series": "DTWEXBGS",
                    "status": "STALE",
                    "source_timestamp": "2026-08-25T00:00:00Z",
                    "retrieval_timestamp": retrieval,
                    "freshness_seconds": 1222380,
                    "stale_after_seconds": 864000,
                },
            ]
            (root / "source_health.json").write_text(
                json.dumps({"status": "STALE", "series": health_rows}), encoding="utf-8"
            )

            values = latest_fred_values(root)
            self.assertEqual(values["DGS2"]["status"], "PASS")
            self.assertEqual(values["DGS10"]["status"], "PASS")
            self.assertEqual(values["VIXCLS"]["status"], "PASS")
            self.assertEqual(values["DTWEXBGS"]["status"], "STALE")
            self.assertEqual(values["DTWEXBGS"]["value"], 118.2)
            for series in rows:
                self.assertIn("source_timestamp", values[series])
                self.assertEqual(values[series]["retrieval_timestamp"], retrieval)
                self.assertIsInstance(values[series]["freshness_seconds"], int)
                self.assertIsInstance(values[series]["stale_after_seconds"], int)

    def test_missing_owner_health_keeps_value_without_inferred_freshness(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_series(root, "DGS10", [("2026-09-07", "4.20")])
            values = latest_fred_values(root)
            self.assertEqual(values["DGS10"], {"value": 4.2, "date": "2026-09-07"})
            self.assertNotIn("status", values["DGS10"])

    def test_ambiguous_or_invalid_health_never_manufactures_quality(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_series(root, "DGS10", [("2026-09-07", "4.20")])
            duplicate = {
                "series": "DGS10",
                "status": "PASS",
                "source_timestamp": "2026-09-07T00:00:00Z",
                "retrieval_timestamp": "2026-09-08T06:13:00Z",
                "freshness_seconds": 100,
                "stale_after_seconds": 604800,
            }
            (root / "source_health.json").write_text(
                json.dumps({"series": [duplicate, dict(duplicate, status="STALE")]}), encoding="utf-8"
            )
            values = latest_fred_values(root)
            self.assertEqual(values["DGS10"]["value"], 4.2)
            self.assertNotIn("status", values["DGS10"])

    def test_latest_usable_numeric_observation_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_series(
                root,
                "DGS2",
                [("2026-09-05", "3.0"), ("2026-09-06", "."), ("2026-09-07", "3.1")],
            )
            values = latest_fred_values(root)
            self.assertEqual(values["DGS2"]["date"], "2026-09-07")
            self.assertEqual(values["DGS2"]["value"], 3.1)


if __name__ == "__main__":
    unittest.main()
