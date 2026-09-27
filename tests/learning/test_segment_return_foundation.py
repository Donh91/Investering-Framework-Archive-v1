from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.learning import segment_return_foundation as foundation


def snapshot(ts: str, rows: list[dict]) -> dict:
    return {
        "contract": foundation.SOURCE_CONTRACT,
        "retrieval_timestamp": ts,
        "freeze_timestamp": ts,
        "universe": {
            "membership_hash": ts[:10].replace("-", ""),
        },
        "constituents": rows,
    }


def row(asset_id: str, rank: int, price: float, market_cap: float) -> dict:
    return {
        "asset_id": asset_id,
        "filtered_rank": rank,
        "price_usd": price,
        "market_cap_usd": market_cap,
    }


class SegmentReturnFoundationTests(unittest.TestCase):
    def write_snapshot(self, root: Path, day: str, value: dict) -> None:
        path = root / day / "owner_snapshot.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_freezes_prior_rank_membership_before_measuring_next_price(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "breadth"
            self.write_snapshot(
                root,
                "2026-09-26",
                snapshot(
                    "2026-09-26T10:00:00Z",
                    [
                        row("bitcoin", 1, 100.0, 1000.0),
                        row("ethereum", 2, 50.0, 500.0),
                        row("alpha", 3, 10.0, 100.0),
                        row("beta", 26, 20.0, 50.0),
                        row("gamma", 51, 40.0, 10.0),
                    ],
                ),
            )
            self.write_snapshot(
                root,
                "2026-09-27",
                snapshot(
                    "2026-09-27T10:00:00Z",
                    [
                        row("bitcoin", 1, 110.0, 1100.0),
                        row("ethereum", 2, 45.0, 450.0),
                        # alpha moved to rank 90, but belongs to prior day's 3-25 cohort.
                        row("alpha", 90, 12.0, 120.0),
                        row("beta", 20, 22.0, 55.0),
                        row("gamma", 40, 36.0, 9.0),
                    ],
                ),
            )
            rows, lineage = foundation.build_rows(root)
            self.assertEqual(len(rows), 1)
            value = rows[0]
            self.assertAlmostEqual(value["BTC"], 0.10)
            self.assertAlmostEqual(value["ETH"], -0.10)
            self.assertAlmostEqual(value["RANK_3_25"], 0.20)
            self.assertAlmostEqual(value["RANK_26_50"], 0.10)
            self.assertAlmostEqual(value["RANK_51_100"], -0.10)
            self.assertIsNone(value["MICROCAPS"])
            self.assertTrue(value["consecutive_calendar_day"])
            self.assertEqual(value["bucket_diagnostics"]["RANK_3_25"]["cohort_count"], 1)
            self.assertEqual(value["bucket_diagnostics"]["RANK_3_25"]["matched_count"], 1)
            self.assertEqual(len(lineage), 1)

    def test_missing_current_constituent_reduces_coverage_without_lookahead_fill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "breadth"
            self.write_snapshot(
                root,
                "2026-09-26",
                snapshot(
                    "2026-09-26T10:00:00Z",
                    [
                        row("bitcoin", 1, 100.0, 1000.0),
                        row("ethereum", 2, 50.0, 500.0),
                        row("alpha", 3, 10.0, 100.0),
                        row("delta", 4, 5.0, 90.0),
                    ],
                ),
            )
            self.write_snapshot(
                root,
                "2026-09-27",
                snapshot(
                    "2026-09-27T10:00:00Z",
                    [
                        row("bitcoin", 1, 101.0, 1010.0),
                        row("ethereum", 2, 51.0, 510.0),
                        row("alpha", 3, 11.0, 110.0),
                    ],
                ),
            )
            rows, _ = foundation.build_rows(root)
            diag = rows[0]["bucket_diagnostics"]["RANK_3_25"]
            self.assertEqual(diag["cohort_count"], 2)
            self.assertEqual(diag["matched_count"], 1)
            self.assertEqual(diag["matched_fraction"], 0.5)
            self.assertAlmostEqual(rows[0]["RANK_3_25"], 0.10)

    def test_report_is_explicitly_not_a_governed_del_owner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "breadth"
            self.write_snapshot(
                root,
                "2026-09-26",
                snapshot(
                    "2026-09-26T10:00:00Z",
                    [row("bitcoin", 1, 100.0, 1000.0), row("ethereum", 2, 50.0, 500.0)],
                ),
            )
            self.write_snapshot(
                root,
                "2026-09-27",
                snapshot(
                    "2026-09-27T10:00:00Z",
                    [row("bitcoin", 1, 101.0, 1010.0), row("ethereum", 2, 51.0, 510.0)],
                ),
            )
            csv_path = Path(tmp) / "foundation.csv"
            report = foundation.build_report(root, csv_path, "2026-09-27T12:00:00Z")
            self.assertEqual(report["contract"], "SEGMENT_RETURN_RESEARCH_FOUNDATION_v1")
            self.assertEqual(report["status"], "RESEARCH_ONLY_NOT_DEL_OWNER")
            self.assertFalse(report["del_activation"]["satisfies_required_owner_contract"])
            self.assertEqual(
                report["del_activation"]["required_contract"],
                "GOVERNED_SEGMENT_RETURN_SERIES_v1",
            )
            self.assertIn(
                "CANONICAL_MARKET_CAP_BUCKET_TAXONOMY_MISSING",
                report["del_activation"]["blockers"],
            )
            self.assertIn("MICROCAP_RETURN_OWNER_MISSING", report["del_activation"]["blockers"])
            self.assertFalse(report["rank_proxy_semantics"]["canonical_market_cap_band_mapping"])
            self.assertFalse(report["authority"]["del_activation"])
            self.assertTrue(csv_path.exists())
            header = csv_path.read_text(encoding="utf-8").splitlines()[0]
            self.assertEqual(
                header,
                "date,BTC,ETH,RANK_3_25,RANK_26_50,RANK_51_100,MICROCAPS",
            )

    def test_invalid_snapshot_is_ignored_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "breadth"
            bad = root / "2026-09-26" / "owner_snapshot.json"
            bad.parent.mkdir(parents=True, exist_ok=True)
            bad.write_text(json.dumps({"contract": "WRONG", "constituents": []}), encoding="utf-8")
            rows, lineage = foundation.build_rows(root)
            self.assertEqual(rows, [])
            self.assertEqual(lineage, [])


if __name__ == "__main__":
    unittest.main()
