from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.learning.t6_rotation_survival import operate


def packet(ethbtc: float, delta: float, *, breadth=0.5, btc_d=55.0, deployment=None, btc_etf=None, eth_etf=None, stamp="2026-09-09T01:00:00Z"):
    return {
        "contract": "AUTO_MARKET_STATE_PACKET_v1",
        "generated_at_utc": stamp,
        "normalized_state": {
            "scalar_values": {
                "ethbtc": ethbtc,
                "breadth_advance_ratio": breadth,
                "btc_dominance_pct": btc_d,
                "btc_etf_musd": btc_etf,
                "eth_etf_musd": eth_etf,
            },
            "entry_signal_reference": {} if deployment is None else {"state": deployment},
        },
        "deltas_since_prior_auto_packet": {"ethbtc": {"absolute": delta}},
    }


def cadence(level=0.03):
    return {
        "cadence_contract": "ADAPTIVE_ROTATION_CADENCE_v1",
        "authority": "OPERATIONAL_SAMPLING_ONLY_NON_BINDING",
        "registered_ethbtc_level_read_only": level,
    }


class T6RotationSurvivalTests(unittest.TestCase):
    def test_first_cross_freezes_immutable_baseline_with_missing_axes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = operate(packet(0.0301, 0.0002, deployment=None, btc_etf=None, eth_etf=None), cadence(), root)
            self.assertEqual(result["event"], "FIRST_CROSS_FROZEN")
            seq = result["active_sequence_id"]
            baseline = json.loads((root / "sequences" / seq / "BASELINE.json").read_text())
            self.assertEqual(baseline["benchmark"], "FIRST_ETHBTC_CROSS")
            self.assertTrue(baseline["right_censored"])
            self.assertFalse(baseline["axes_at_freeze"]["deployment"]["available"])
            self.assertFalse(baseline["axes_at_freeze"]["flow"]["available"])
            self.assertIsNone(baseline["delay_cost"])
            self.assertIsNone(baseline["failure_outcome"])
            self.assertFalse(baseline["authority"]["portfolio_action"])

    def test_missing_prior_delta_cannot_create_retrospective_cross(self):
        with tempfile.TemporaryDirectory() as td:
            p = packet(0.031, 0.0)
            p["deltas_since_prior_auto_packet"] = {}
            result = operate(p, cadence(), Path(td))
            self.assertEqual(result["event"], "NO_ELIGIBLE_FIRST_CROSS")
            self.assertIsNone(result["active_sequence_id"])

    def test_active_sequence_appends_observation_without_rewriting_baseline(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first = operate(packet(0.0301, 0.0002), cadence(), root)
            seq = first["active_sequence_id"]
            baseline_path = root / "sequences" / seq / "BASELINE.json"
            before = baseline_path.read_bytes()
            later = packet(0.0304, 0.0003, stamp="2026-09-10T01:00:00Z")
            result = operate(later, cadence(), root)
            self.assertEqual(result["event"], "ACTIVE_SEQUENCE_OBSERVATION")
            self.assertEqual(before, baseline_path.read_bytes())

    def test_reversal_closes_state_without_manufacturing_outcome(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first = operate(packet(0.0301, 0.0002), cadence(), root)
            seq = first["active_sequence_id"]
            result = operate(packet(0.0298, -0.0003, stamp="2026-09-10T01:00:00Z"), cadence(), root)
            self.assertEqual(result["event"], "ETHBTC_REVERSAL_OBSERVED")
            state = json.loads((root / "STATE.json").read_text())
            self.assertIsNone(state["active_sequence_id"])
            baseline = json.loads((root / "sequences" / seq / "BASELINE.json").read_text())
            self.assertIsNone(baseline["failure_outcome"])
            self.assertIsNone(baseline["exit_side_outcome"])

    def test_cadence_authority_must_remain_non_binding(self):
        with tempfile.TemporaryDirectory() as td:
            bad = cadence()
            bad["authority"] = "MARKET_RULE"
            with self.assertRaises(ValueError):
                operate(packet(0.0301, 0.0002), bad, Path(td))


if __name__ == "__main__":
    unittest.main()
