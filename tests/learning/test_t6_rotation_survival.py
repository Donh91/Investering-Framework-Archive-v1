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


    def test_identical_replay_after_reversal_preserves_immutable_observation_and_state(self):
        """Production failure: old reversal recomputed from already-closed STATE."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            operate(packet(0.0301, 0.0002), cadence(), root)
            reversal = packet(0.02963, -0.00047, stamp="2026-09-10T01:00:00Z")
            first = operate(reversal, cadence(), root)
            frozen = (root / "observations" / Path(first["observation_path"]).name).read_bytes()
            state_before = (root / "STATE.json").read_bytes()
            latest_before = (root / "LATEST.json").read_bytes()
            self.assertEqual(first["event"], "ETHBTC_REVERSAL_OBSERVED")
            self.assertEqual(operate(reversal, cadence(), root), first)
            self.assertEqual((root / "STATE.json").read_bytes(), state_before)
            self.assertEqual((root / "LATEST.json").read_bytes(), latest_before)
            self.assertEqual((root / "observations" / Path(first["observation_path"]).name).read_bytes(), frozen)

    def test_replay_changed_cadence_cannot_silently_reuse_original_observation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            sample = packet(0.0301, 0.0002)
            operate(sample, cadence(), root)
            state_before = (root / "STATE.json").read_bytes()
            with self.assertRaisesRegex(ValueError, "immutable_conflict"):
                operate(sample, cadence(0.0298), root)
            self.assertEqual((root / "STATE.json").read_bytes(), state_before)

    def test_replay_corrupt_frozen_object_fails_closed_without_state_change(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            sample = packet(0.0301, 0.0002)
            result = operate(sample, cadence(), root)
            observation_path = Path(result["observation_path"])
            frozen = json.loads(observation_path.read_text())
            frozen["current_ethbtc"] = 0.09999
            observation_path.write_text(json.dumps(frozen))
            state_before = (root / "STATE.json").read_bytes()
            with self.assertRaisesRegex(ValueError, "immutable_conflict"):
                operate(sample, cadence(), root)
            self.assertEqual((root / "STATE.json").read_bytes(), state_before)

    def test_replay_missing_latest_pointer_is_never_inferred_or_regenerated(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            sample = packet(0.0301, 0.0002)
            operate(sample, cadence(), root)
            (root / "LATEST.json").unlink()
            state_before = (root / "STATE.json").read_bytes()
            with self.assertRaisesRegex(ValueError, "t6_replay_latest_pointer_missing"):
                operate(sample, cadence(), root)
            self.assertEqual((root / "STATE.json").read_bytes(), state_before)

    def test_valid_replay_preserves_all_supported_nonreversal_states(self):
        for mode in ("no_cross", "first_cross", "active"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                sample = packet(0.029, 0.0) if mode == "no_cross" else packet(0.0301, 0.0002)
                result = operate(sample, cadence(), root)
                if mode == "active":
                    sample = packet(0.0304, 0.0003, stamp="2026-09-10T01:00:00Z")
                    result = operate(sample, cadence(), root)
                before = {p: p.read_bytes() for p in root.rglob("*.json")}
                self.assertEqual(operate(sample, cadence(), root), result)
                self.assertEqual({p: p.read_bytes() for p in root.rglob("*.json")}, before)

    def test_replay_rejects_corrupted_consequential_latest_fields(self):
        for field, value in (("event", "NO_ELIGIBLE_FIRST_CROSS"),
                             ("active_sequence_id", None),
                             ("authority", {"binding": True})):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                sample = packet(0.0301, 0.0002)
                operate(sample, cadence(), root)
                latest_path = root / "LATEST.json"
                latest = json.loads(latest_path.read_text())
                latest[field] = value
                latest_path.write_text(json.dumps(latest))
                before = {p: p.read_bytes() for p in root.rglob("*.json")}
                with self.assertRaisesRegex(ValueError, "t6_replay_latest_pointer_mismatch"):
                    operate(sample, cadence(), root)
                self.assertEqual({p: p.read_bytes() for p in root.rglob("*.json")}, before)

    def test_replay_rejects_state_that_disagrees_with_frozen_event(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            sample = packet(0.0301, 0.0002)
            operate(sample, cadence(), root)
            state_path = root / "STATE.json"
            state = json.loads(state_path.read_text())
            state["active_sequence_id"] = None
            state_path.write_text(json.dumps(state))
            before = {p: p.read_bytes() for p in root.rglob("*.json")}
            with self.assertRaisesRegex(ValueError, "t6_replay_state_mismatch"):
                operate(sample, cadence(), root)
            self.assertEqual({p: p.read_bytes() for p in root.rglob("*.json")}, before)

    def test_stale_older_source_replay_does_not_rewind_newer_latest(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            old = packet(0.0301, 0.0002)
            operate(old, cadence(), root)
            later = packet(0.0304, 0.0003, stamp="2026-09-10T01:00:00Z")
            operate(later, cadence(), root)
            state_before = (root / "STATE.json").read_bytes()
            latest_before = (root / "LATEST.json").read_bytes()
            with self.assertRaisesRegex(ValueError, "t6_replay_latest_pointer_mismatch"):
                operate(old, cadence(), root)
            self.assertEqual((root / "STATE.json").read_bytes(), state_before)
            self.assertEqual((root / "LATEST.json").read_bytes(), latest_before)


if __name__ == "__main__":
    unittest.main()
