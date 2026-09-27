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


def raw_row(asset_id: str, price: float) -> dict:
    return {
        "id": asset_id,
        "symbol": asset_id[:5],
        "name": asset_id,
        "market_cap": 1.0,
        "current_price": price,
        "price_change_percentage_24h": 0.0,
    }


class SegmentReturnFoundationTests(unittest.TestCase):
    def write_snapshot(self, root: Path, day: str, value: dict, raw_rows: list[dict] | None = None) -> None:
        path = root / day / "owner_snapshot.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")
        if raw_rows is not None:
            path.with_name("raw_source_payload.json").write_text(json.dumps(raw_rows), encoding="utf-8")

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
                        row("alpha", 90, 12.0, 120.0),
                        row("beta", 20, 22.0, 55.0),
                        row("gamma", 40, 36.0, 9.0),
                    ],
                ),
            )
            rows, lineage = foundation.build_rows(root)
            self.assertEqual(len(rows), 1)
            value = rows[0]
            self.assertTrue(value["daily_interval_eligible"])
            self.assertEqual(value["interval_hours"], 24.0)
            self.assertAlmostEqual(value["BTC"], 0.10)
            self.assertAlmostEqual(value["ETH"], -0.10)
            self.assertAlmostEqual(value["RANK_3_25"], 0.20)
            self.assertAlmostEqual(value["RANK_26_50"], 0.10)
            self.assertAlmostEqual(value["RANK_51_100"], -0.10)
            self.assertIsNone(value["MICROCAPS"])
            self.assertEqual(value["bucket_diagnostics"]["RANK_3_25"]["cohort_count"], 1)
            self.assertEqual(value["bucket_diagnostics"]["RANK_3_25"]["matched_count"], 1)
            self.assertTrue(value["bucket_diagnostics"]["RANK_3_25"]["complete_price_coverage"])
            self.assertEqual(len(lineage), 1)

    def test_raw_top150_fallback_preserves_frozen_member_that_leaves_owner_top100(self) -> None:
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
                raw_rows=[
                    raw_row("bitcoin", 101.0),
                    raw_row("ethereum", 51.0),
                    raw_row("alpha", 11.0),
                    raw_row("delta", 4.0),
                ],
            )
            rows, _ = foundation.build_rows(root)
            diag = rows[0]["bucket_diagnostics"]["RANK_3_25"]
            self.assertEqual(diag["cohort_count"], 2)
            self.assertEqual(diag["matched_count"], 2)
            self.assertEqual(diag["matched_fraction"], 1.0)
            self.assertTrue(diag["complete_price_coverage"])
            self.assertEqual(diag["raw_top150_fallback_asset_ids"], ["delta"])
            self.assertEqual(diag["missing_asset_ids"], [])
            self.assertAlmostEqual(rows[0]["RANK_3_25"], -0.05)

    def test_missing_even_from_raw_payload_makes_bucket_unavailable_not_survivor_average(self) -> None:
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
                raw_rows=[
                    raw_row("bitcoin", 101.0),
                    raw_row("ethereum", 51.0),
                    raw_row("alpha", 11.0),
                ],
            )
            rows, _ = foundation.build_rows(root)
            diag = rows[0]["bucket_diagnostics"]["RANK_3_25"]
            self.assertFalse(diag["complete_price_coverage"])
            self.assertEqual(diag["matched_count"], 1)
            self.assertEqual(diag["missing_asset_ids"], ["delta"])
            self.assertIsNone(rows[0]["RANK_3_25"])
            self.assertIsNone(rows[0]["raw_point_to_point_returns"]["RANK_3_25"])

    def test_irregular_timestamp_gap_is_retained_for_lineage_but_excluded_from_daily_series(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "breadth"
            self.write_snapshot(
                root,
                "2026-09-26",
                snapshot(
                    "2026-09-26T00:00:00Z",
                    [
                        row("bitcoin", 1, 100.0, 1000.0),
                        row("ethereum", 2, 50.0, 500.0),
                        row("alpha", 3, 10.0, 100.0),
                    ],
                ),
            )
            self.write_snapshot(
                root,
                "2026-09-27",
                snapshot(
                    "2026-09-27T10:42:00Z",
                    [
                        row("bitcoin", 1, 110.0, 1100.0),
                        row("ethereum", 2, 55.0, 550.0),
                        row("alpha", 3, 12.0, 120.0),
                    ],
                ),
            )
            rows, lineage = foundation.build_rows(root)
            self.assertEqual(rows[0]["interval_hours"], 34.7)
            self.assertFalse(rows[0]["daily_interval_eligible"])
            self.assertIsNone(rows[0]["BTC"])
            self.assertIsNone(rows[0]["ETH"])
            self.assertIsNone(rows[0]["RANK_3_25"])
            self.assertAlmostEqual(rows[0]["raw_point_to_point_returns"]["BTC"], 0.10)
            self.assertAlmostEqual(rows[0]["raw_point_to_point_returns"]["RANK_3_25"], 0.20)
            self.assertFalse(lineage[0]["daily_interval_eligible"])

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
            self.assertFalse(report["survivor_only_bucket_average_allowed"])
            self.assertTrue(report["raw_top150_dropout_price_fallback"])
            self.assertEqual(report["daily_interval_policy"]["minimum_hours"], 21.0)
            self.assertEqual(report["daily_interval_policy"]["maximum_hours"], 27.0)
            self.assertTrue(csv_path.exists())
            header = csv_path.read_text(encoding="utf-8").splitlines()[0]
            self.assertEqual(
                header,
                "date,prior_date,interval_hours,daily_interval_eligible,BTC,ETH,RANK_3_25,RANK_26_50,RANK_51_100,MICROCAPS",
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
