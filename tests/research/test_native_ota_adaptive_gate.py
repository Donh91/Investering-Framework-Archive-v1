from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT / "scripts/research"
sys.path.insert(0, str(SCRIPT_DIR))
MODULE_PATH = SCRIPT_DIR / "native_ota_adaptive_gate.py"
spec = importlib.util.spec_from_file_location("native_ota_adaptive_gate", MODULE_PATH)
assert spec and spec.loader
gate = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = gate
spec.loader.exec_module(gate)

UTC = timezone.utc


def policy() -> dict:
    return {
        "contract": "NATIVE_OTA_ADAPTIVE_POLICY_v1",
        "source_policy": "READ_EXISTING_GITHUB_OWNERS_ONLY_NO_NEW_MARKET_SOURCE_CALLS",
        "cadence": {
            "max_full_runs_per_iso_week": 2,
            "minimum_hours_between_full_runs": 72
        },
        "adaptive_gate": {
            "run_score_threshold": 3.0,
            "breadth_support_reference_read_only": 0.50,
            "breadth_material_delta_abs": 0.15,
            "initial_attention_weights": {
                "settled_transition": 1.25,
                "classified_new_information": 1.10,
                "classified_evidential": 1.00,
                "breadth_regime_change": 1.00,
                "breadth_material_delta": 0.90,
                "research_novelty": 0.80,
                "framework_data_gap": 0.70
            },
            "attention_weight_bounds": [0.75, 1.25],
            "novel_signal_step": 0.05,
            "repeated_signal_step": -0.05
        },
        "self_development_scope": [
            "ADAPTIVE_CADENCE", "RESEARCH_ATTENTION_PRIORITY",
            "REDUNDANCY_DAMPING", "NOVELTY_WEIGHTING"
        ],
        "immutable_guards": {
            "canonical_state_change": False,
            "market_rule_change": False,
            "threshold_change": False,
            "portfolio_execution": False,
            "experiment_promotion": False,
            "automatic_weight_change_to_market_model": False,
            "new_market_source_calls": False
        }
    }


def write_policy(root: Path, payload: dict | None = None) -> None:
    path = root / gate.POLICY_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload or policy()))


def write_breadth(root: Path, value: float) -> None:
    path = root / "03_DAILY_CAPTURE_LOGS/breadth_rich/LATEST.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"aggregate": {"advance_ratio": value}}))


def preview(new_info: int = 0, evidential: int = 0, gaps: int = 0) -> dict:
    return {
        "classification_counts": {
            "NEW_INFORMATION": new_info,
            "EVIDENTIAL": evidential,
            "CONTEXT_ONLY": 0
        },
        "gap_accounting": {
            "framework_data_gaps": [f"gap-{i}" for i in range(gaps)]
        }
    }


class AdaptiveOtaGateTests(unittest.TestCase):
    def test_policy_fails_closed_on_threshold_authority_breach(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            broken = policy()
            broken["immutable_guards"]["threshold_change"] = True
            write_policy(root, broken)
            with self.assertRaises(RuntimeError):
                gate.load_policy(root)

    def test_material_novel_signals_can_promote_adaptive_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_policy(root)
            write_breadth(root, 0.54)
            state = root / gate.STATE_PATH
            state.parent.mkdir(parents=True, exist_ok=True)
            state.write_text(json.dumps({
                "latest_breadth_advance_ratio": 0.34,
                "active_signal_signature": [],
                "attention_weights": policy()["adaptive_gate"]["initial_attention_weights"]
            }))
            now = datetime(2026, 9, 9, 20, 45, tzinfo=UTC)
            with mock.patch.object(gate.ota, "build_report", return_value=(preview(new_info=1), False)):
                result = gate.evaluate(root, now)
            self.assertTrue(result["run_full_ota"])
            self.assertIn("breadth_regime_change", result["active_signal_signature"])
            self.assertIn("breadth_material_delta", result["active_signal_signature"])
            self.assertFalse(result["thresholds_changed"])
            self.assertFalse(result["canonical_effect"])

    def test_repeated_signature_is_damped_not_market_thresholds(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_policy(root)
            write_breadth(root, 0.54)
            state = root / gate.STATE_PATH
            state.parent.mkdir(parents=True, exist_ok=True)
            state.write_text(json.dumps({
                "latest_breadth_advance_ratio": 0.54,
                "active_signal_signature": ["classified_new_information"],
                "attention_weights": policy()["adaptive_gate"]["initial_attention_weights"]
            }))
            now = datetime(2026, 9, 9, 20, 45, tzinfo=UTC)
            with mock.patch.object(gate.ota, "build_report", return_value=(preview(new_info=1), False)):
                result = gate.evaluate(root, now)
            self.assertEqual(result["learning_update"], "DAMP_REPEATED_SIGNATURE")
            self.assertLess(
                result["attention_weights_next"]["classified_new_information"],
                result["attention_weights_used"]["classified_new_information"]
            )
            self.assertFalse(result["portfolio_rules_changed"])

    def test_weekly_cap_blocks_extra_full_ota(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_policy(root)
            write_breadth(root, 0.54)
            report_dir = root / "04_MARKET_LEARNING/ota_native/2026/09/08"
            report_dir.mkdir(parents=True, exist_ok=True)
            for i, hour in enumerate((10, 14)):
                (report_dir / f"{hour:02d}0000_NATIVE_OTA_READBACK.json").write_text(json.dumps({
                    "mode": "FULL_FIXED_OR_MANUAL",
                    "generated_at_utc": f"2026-09-08T{hour:02d}:00:00Z"
                }))
            now = datetime(2026, 9, 9, 20, 45, tzinfo=UTC)
            with mock.patch.object(gate.ota, "build_report", return_value=(preview(new_info=2, evidential=2), True)):
                result = gate.evaluate(root, now)
            self.assertFalse(result["run_full_ota"])
            self.assertIn("WEEKLY_FULL_RUN_CAP_REACHED", result["blockers"])

    def test_persist_keeps_learning_state_separate_from_market_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_policy(root)
            write_breadth(root, 0.34)
            now = datetime(2026, 9, 9, 20, 45, tzinfo=UTC)
            with mock.patch.object(gate.ota, "build_report", return_value=(preview(), False)):
                result = gate.evaluate(root, now)
            path = gate.persist(root, result)
            self.assertTrue(path.exists())
            state = json.loads((root / gate.STATE_PATH).read_text())
            self.assertIn("attention_weights", state)
            self.assertFalse(state["canonical_effect"])
            self.assertFalse(state["thresholds_changed"])


if __name__ == "__main__":
    unittest.main()
