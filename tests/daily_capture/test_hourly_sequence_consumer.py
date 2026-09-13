import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.daily_capture.hourly_sequence_consumer import read_latest_complete_spot_row


FIELDS = ["timestamp_utc", "spot_status", "btc_close", "eth_close", "ethbtc_close"]


class HourlySequenceConsumerTests(unittest.TestCase):
    def write_pointer(
        self,
        root: Path,
        *,
        end: str,
        status: str = "COMPLETE",
        requested_hours: int = 26,
        spot_complete_hours: int = 26,
    ) -> Path:
        pointer = root / "LATEST.json"
        pointer.write_text(json.dumps({
            "contract": "HOURLY_SEQUENCE_LATEST_POINTER_v2_2",
            "status": status,
            "requested_hours": requested_hours,
            "spot_complete_hours": spot_complete_hours,
            "derivatives_oi_complete_hours": 25,
            "long_short_complete_hours": 26,
            "window_end_utc": end,
            "run_id": "fixture-run",
        }))
        return pointer

    def write_csv(self, root: Path, day: str, rows: list[dict[str, str]]) -> None:
        path = root / day[:4] / day[5:7] / f"{day}.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    def row(self, ts: str, **overrides) -> dict[str, str]:
        value = {
            "timestamp_utc": ts,
            "spot_status": "PASS",
            "btc_close": "78000",
            "eth_close": "2450",
            "ethbtc_close": "0.03141",
        }
        value.update(overrides)
        return value

    def test_midnight_boundary_reads_previous_utc_day(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pointer = self.write_pointer(root, end="2026-08-29T00:00:00Z")
            self.write_csv(root, "2026-08-28", [self.row("2026-08-28T23:00:00Z")])
            _, ts, row = read_latest_complete_spot_row(pointer, root)
            self.assertEqual(ts.isoformat(), "2026-08-28T23:00:00+00:00")
            self.assertEqual(row["btc_close"], "78000")

    def test_exclusive_boundary_never_consumes_boundary_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pointer = self.write_pointer(root, end="2026-08-29T12:00:00Z")
            self.write_csv(root, "2026-08-29", [
                self.row("2026-08-29T11:00:00Z", btc_close="77000"),
                self.row("2026-08-29T12:00:00Z", btc_close="99999"),
            ])
            _, ts, row = read_latest_complete_spot_row(pointer, root)
            self.assertEqual(ts.isoformat(), "2026-08-29T11:00:00+00:00")
            self.assertEqual(row["btc_close"], "77000")

    def test_missing_final_day_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pointer = self.write_pointer(root, end="2026-08-29T00:00:00Z")
            with self.assertRaisesRegex(RuntimeError, "hourly permanent CSV missing"):
                read_latest_complete_spot_row(pointer, root)

    def test_partial_pointer_with_complete_spot_is_usable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pointer = self.write_pointer(
                root,
                end="2026-08-29T00:00:00Z",
                status="PARTIAL",
                requested_hours=26,
                spot_complete_hours=26,
            )
            self.write_csv(root, "2026-08-28", [self.row("2026-08-28T23:00:00Z")])
            resolved, ts, row = read_latest_complete_spot_row(pointer, root)
            self.assertEqual(resolved["status"], "PARTIAL")
            self.assertEqual(resolved["derivatives_oi_complete_hours"], 25)
            self.assertEqual(ts.isoformat(), "2026-08-28T23:00:00+00:00")
            self.assertEqual(row["eth_close"], "2450")

    def test_partial_pointer_with_incomplete_spot_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pointer = self.write_pointer(
                root,
                end="2026-08-29T00:00:00Z",
                status="PARTIAL",
                requested_hours=26,
                spot_complete_hours=25,
            )
            with self.assertRaisesRegex(RuntimeError, "incomplete spot coverage"):
                read_latest_complete_spot_row(pointer, root)

    def test_failed_pointer_fails_closed_even_if_spot_counter_is_full(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pointer = self.write_pointer(
                root,
                end="2026-08-29T00:00:00Z",
                status="FAILED",
                requested_hours=26,
                spot_complete_hours=26,
            )
            with self.assertRaisesRegex(RuntimeError, "incomplete spot coverage"):
                read_latest_complete_spot_row(pointer, root)

    def test_partial_pointer_without_explicit_spot_counts_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pointer = root / "LATEST.json"
            pointer.write_text(json.dumps({
                "contract": "HOURLY_SEQUENCE_LATEST_POINTER_v2_2",
                "status": "PARTIAL",
                "window_end_utc": "2026-08-29T00:00:00Z",
            }))
            with self.assertRaisesRegex(RuntimeError, "incomplete spot coverage"):
                read_latest_complete_spot_row(pointer, root)

    def test_latest_pre_boundary_row_must_have_direct_closes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pointer = self.write_pointer(root, end="2026-08-29T00:00:00Z")
            self.write_csv(root, "2026-08-28", [self.row("2026-08-28T23:00:00Z", ethbtc_close="")])
            with self.assertRaisesRegex(RuntimeError, "missing direct spot close"):
                read_latest_complete_spot_row(pointer, root)


if __name__ == "__main__":
    unittest.main()
