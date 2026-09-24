from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.learning.t8_multi_ping_delay_cost import (
    attach_outcome,
    materialize_packet,
    scan,
)


def packet(*, snapshot="DPI-T8-001", freeze="2026-09-24T08:00:00Z", block=True):
    row = {
        "contract": "ACCEPTED_DATA_PING_PACKET_v1",
        "snapshot_id": snapshot,
        "freeze_utc": freeze,
        "acceptance_status": "ACCEPTED",
        "source_health": {"data_ping": "PASS"},
        "market_metrics": {},
        "framework_interpretation": "SHADOW",
        "authority": {"portfolio_action": False},
    }
    if block:
        row["MULTI_PING_AGGREGATION"] = {
            "window_runs": 3,
            "latest_ping_state": "PREPARE",
            "aggregated_state": "WAIT",
            "state_flip_reduced": True,
            "delay_minutes": 15,
            "data_quality": "COMPLETE",
            "authority": "FORWARD_TEST_ONLY",
            "dependency_to_latest_ping": "PARTIALLY_DEPENDENT",
            "redundancy_class": "PARTIALLY_REDUNDANT",
            "unique_information_gain": None,
        }
    return row


class T8MultiPingDelayCostTests(unittest.TestCase):
    def write(self, root: Path, value: dict, name="packet.json") -> Path:
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(value), encoding="utf-8")
        return p

    def test_explicit_block_freezes_immutable_source_row(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            p = self.write(root, packet())
            out = root / "rows"
            result = materialize_packet(p, out, root)
            self.assertEqual(result["status"], "SOURCE_ROW_FROZEN")
            source = json.loads(Path(result["source_row_path"]).read_text())
            self.assertEqual(source["benchmark"], "LATEST_PING_ONLY")
            self.assertEqual(source["latest_ping_state"], "PREPARE")
            self.assertEqual(source["aggregation_state"], "WAIT")
            self.assertEqual(source["dependency_to_latest_ping"], "PARTIALLY_DEPENDENT")
            self.assertEqual(source["redundancy_class"], "PARTIALLY_REDUNDANT")
            self.assertIsNone(source["eventual_framework_state"])
            self.assertIsNone(source["false_flip_count"])
            self.assertIsNone(source["delay_cost"])
            self.assertEqual(source["delay_cost_status"], "UNRESOLVED_NO_REGISTERED_COST_FUNCTION")
            self.assertTrue(source["right_censored"])
            self.assertFalse(source["authority"]["portfolio_action"])
            before = Path(result["source_row_path"]).read_bytes()
            again = materialize_packet(p, out, root)
            self.assertEqual(again["source_row_sha256"], result["source_row_sha256"])
            self.assertEqual(before, Path(result["source_row_path"]).read_bytes())

    def test_packet_without_explicit_block_is_noop(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            p = self.write(root, packet(block=False))
            result = materialize_packet(p, root / "rows", root)
            self.assertEqual(result["status"], "NOOP_NO_MULTI_PING_BLOCK")
            self.assertFalse((root / "rows/source_rows").exists())

    def test_nonaccepted_or_wrong_authority_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            bad = packet()
            bad["acceptance_status"] = "REJECTED"
            with self.assertRaisesRegex(ValueError, "accepted_status_required"):
                materialize_packet(self.write(root, bad), root / "rows", root)
            bad = packet(snapshot="DPI-T8-002")
            bad["MULTI_PING_AGGREGATION"]["authority"] = "CONSENSUS"
            with self.assertRaisesRegex(ValueError, "FORWARD_TEST_ONLY"):
                materialize_packet(self.write(root, bad, "bad2.json"), root / "rows", root)

    def test_window_must_be_three_or_four_runs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            bad = packet()
            bad["MULTI_PING_AGGREGATION"]["window_runs"] = 2
            with self.assertRaisesRegex(ValueError, "window_runs_must_be_3_or_4"):
                materialize_packet(self.write(root, bad), root / "rows", root)

    def test_missing_dependency_and_redundancy_remain_unknown(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            row = packet()
            row["MULTI_PING_AGGREGATION"].pop("dependency_to_latest_ping")
            row["MULTI_PING_AGGREGATION"].pop("redundancy_class")
            result = materialize_packet(self.write(root, row), root / "rows", root)
            source = json.loads(Path(result["source_row_path"]).read_text())
            self.assertEqual(source["dependency_to_latest_ping"], "UNKNOWN")
            self.assertEqual(source["redundancy_class"], "UNKNOWN")
            self.assertIsNone(source["unique_information_gain"])

    def test_later_outcome_is_append_only_and_measures_baseline_vs_aggregation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = materialize_packet(self.write(root, packet()), root / "rows", root)
            source_path = Path(result["source_row_path"])
            before = source_path.read_bytes()
            outcome = attach_outcome(
                source_path,
                "WAIT",
                "2026-09-24T10:00:00Z",
                "research/framework_state/example.json",
                "e" * 64,
                root / "rows",
            )
            self.assertEqual(before, source_path.read_bytes())
            row = json.loads(Path(outcome["path"]).read_text())
            self.assertEqual(row["false_flip_count"]["latest_ping_only"], 1)
            self.assertEqual(row["false_flip_count"]["multi_ping_aggregation"], 0)
            self.assertEqual(row["false_flip_reduction"], 1)
            self.assertEqual(row["delay_minutes"], 15.0)
            self.assertIsNone(row["delay_cost"])
            self.assertEqual(row["delay_cost_status"], "UNRESOLVED_NO_REGISTERED_COST_FUNCTION")
            self.assertFalse(row["right_censored"])
            self.assertFalse(row["source_row_rewritten"])

    def test_outcome_cannot_precede_or_equal_source_freeze(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = materialize_packet(self.write(root, packet()), root / "rows", root)
            for stamp in ("2026-09-24T07:59:59Z", "2026-09-24T08:00:00Z"):
                with self.assertRaisesRegex(ValueError, "outcome_must_be_after_source_freeze"):
                    attach_outcome(
                        Path(result["source_row_path"]),
                        "WAIT",
                        stamp,
                        "evidence.json",
                        "f" * 64,
                        root / "rows",
                    )

    def test_scan_is_idempotent_and_does_not_reconstruct_historical_chat(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            accepted = root / "accepted"
            self.write(accepted, packet(snapshot="one"), "one.json")
            self.write(accepted, packet(snapshot="two", block=False), "two.json")
            out = root / "rows"
            first = scan(accepted, out, root)
            second = scan(accepted, out, root)
            self.assertEqual(first["source_rows_frozen_or_verified"], 1)
            self.assertEqual(second["source_rows_frozen_or_verified"], 1)
            self.assertEqual(len(list((out / "source_rows").glob("*.json"))), 1)
            self.assertEqual(first["no_multi_ping_block"], 1)
            self.assertEqual(first["errors"], [])


if __name__ == "__main__":
    unittest.main()
