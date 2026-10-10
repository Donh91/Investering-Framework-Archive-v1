from __future__ import annotations

import importlib.util
import hashlib
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "learning" / "action_compass_exit_calibration.py"
SPEC = importlib.util.spec_from_file_location("action_compass_exit_calibration", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class ProtectionCalibrationTests(unittest.TestCase):
    def write_case(
        self,
        root: Path,
        *,
        projection_source: str = "MACHINE_PACKAGE",
        policy: str = "2026-09-25_DECISION_INTEGRITY_V3_2",
        data_quality: str = "OK",
        pullback: str = "HIGH",
        distribution: str = "WARNING",
    ) -> Path:
        freeze_rel = Path("04_MARKET_LEARNING/handlekompas/official/daily/2026/09/27/CMP-test.json")
        freeze_path = root / freeze_rel
        freeze_path.parent.mkdir(parents=True, exist_ok=True)
        freeze = {
            "contract": "OFFICIAL_DAILY_COMPASS_v1",
            "schema_version": 3,
            "decision_policy_version": policy,
            "compass_id": "CMP-test",
            "compass_sha256": "a" * 64,
            "source_bindings": {
                "cycle_navigator": {"decision_projection_source": projection_source}
            },
            "protection_tracker": {
                "contract": "COMPASS_PROTECTION_TRACKER_v1",
                "pullback_risk_state": pullback,
                "pullback_class": "DEFENSIVE_PULLBACK",
                "distribution_risk": distribution,
                "eta_window": "24-72h",
                "confidence_quality": "MEDIUM",
                "decisive_public_drivers": ["BREADTH_DIVERGENCE", "LIQUIDITY_DETERIORATION"],
                "invalidation": "Typed recovery evidence clears the warning.",
                "data_quality": data_quality,
                "reentry_state": "WAIT_FOR_FLUSH",
            },
        }
        # Use the real producer's self-excluding canonical freeze digest rather
        # than a dummy SHA so integrity validation is exercised by every test.
        freeze.pop("compass_sha256")
        expected_digest = hashlib.sha256(
            (json.dumps(freeze, sort_keys=True, separators=(",", ":"),
                        ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
        ).hexdigest()
        freeze["compass_sha256"] = expected_digest
        freeze_path.write_text(json.dumps(freeze), encoding="utf-8")

        outcome_root = root / "04_MARKET_LEARNING/handlekompas/official/outcomes"
        outcome_path = outcome_root / "2026/09/27/CMP-test_72h.json"
        outcome_path.parent.mkdir(parents=True, exist_ok=True)
        outcome = {
            "contract": "OFFICIAL_DAILY_COMPASS_OUTCOME_v1",
            "compass_id": "CMP-test",
            "compass_sha256": expected_digest,
            "forecast_path": freeze_rel.as_posix(),
            "horizon": "72h",
            "realized": {
                "btc_return_pct": -8.0,
                "btc_mfe_pct": 3.0,
                "btc_mae_pct": -12.0,
                "eth_return_pct": 6.0,
                "eth_mfe_pct": 11.0,
                "eth_mae_pct": -5.0,
            },
        }
        outcome_path.write_text(json.dumps(outcome), encoding="utf-8")
        return outcome_root

    def test_modern_official_outcomes_make_typed_protection_accountable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outcome_root = self.write_case(root)
            report = MODULE.build_report(root, outcome_root, "2026-09-30T00:00:00Z")
            self.assertEqual(report["contract"], "ACTION_COMPASS_PROTECTION_CALIBRATION_v2")
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["source_outcome_count"], 1)
            self.assertEqual(report["eligible_series_row_count"], 2)
            self.assertEqual(report["warning_series_row_count"], 2)
            self.assertEqual(len(report["cohorts"]), 2)
            btc = next(row for row in report["cohorts"] if row["series_id"] == "BTC_USDT_MARK_PRICE")
            self.assertEqual(btc["pullback_risk_state"], "HIGH")
            self.assertEqual(btc["distribution_risk"], "WARNING")
            self.assertEqual(btc["confidence_quality"], "MEDIUM")
            self.assertEqual(btc["eta_windows_observed"], ["24-72h"])
            self.assertEqual(btc["median_max_upside_after_signal_pct"], 3.0)
            self.assertEqual(btc["median_max_drawdown_after_signal_pct"], -12.0)
            self.assertEqual(btc["median_full_exit_capital_preserved_reference_pct"], 8.0)
            self.assertEqual(btc["median_full_exit_terminal_upside_foregone_reference_pct"], 0.0)
            self.assertFalse(report["promotion_readiness"]["automatic_promotion"])
            self.assertTrue(report["interpretation_boundary"]["descriptive_only"])

    def test_changed_freeze_payload_cannot_pass_claimed_hash_pair(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outcome_root = self.write_case(root, pullback="BUILDING", distribution="UNKNOWN")
            forecast = next((root / "04_MARKET_LEARNING/handlekompas/official/daily").rglob("*.json"))
            modified = json.loads(forecast.read_text(encoding="utf-8"))
            modified["protection_tracker"]["pullback_risk_state"] = "HIGH"
            # The outcome and freeze still claim precisely the same old SHA.
            # Tampering must be rejected before any risk state is counted.
            forecast.write_text(json.dumps(modified), encoding="utf-8")
            report = MODULE.build_report(root, outcome_root, "2026-10-10T00:00:00Z")
            self.assertEqual(report["source_outcome_count"], 1)
            self.assertEqual(report["eligible_series_row_count"], 0)
            self.assertEqual(report["warning_series_row_count"], 0)
            self.assertEqual(report["nonwarning_downside_context"], [])
            self.assertEqual(report["excluded_outcome_counts"]["FORECAST_PAYLOAD_HASH_MISMATCH"], 1)

    def test_equal_but_fabricated_freeze_and_outcome_digests_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outcome_root = self.write_case(root)
            forecast = next((root / "04_MARKET_LEARNING/handlekompas/official/daily").rglob("*.json"))
            outcome = next(outcome_root.rglob("*.json"))
            freeze_data = json.loads(forecast.read_text(encoding="utf-8"))
            outcome_data = json.loads(outcome.read_text(encoding="utf-8"))
            freeze_data["compass_sha256"] = "f" * 64
            outcome_data["compass_sha256"] = "f" * 64
            forecast.write_text(json.dumps(freeze_data), encoding="utf-8")
            outcome.write_text(json.dumps(outcome_data), encoding="utf-8")
            report = MODULE.build_report(root, outcome_root, "2026-10-10T00:00:00Z")
            self.assertEqual(report["eligible_series_row_count"], 0)
            self.assertEqual(report["excluded_outcome_counts"]["FORECAST_PAYLOAD_HASH_MISMATCH"], 1)

    def test_nonfinite_payload_with_null_or_missing_hashes_is_rejected(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            for declaration in (None, "MISSING", "f" * 64):
                with self.subTest(value=value, declaration=declaration), tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    outcome_root = self.write_case(root)
                    forecast = next((root / "04_MARKET_LEARNING/handlekompas/official/daily").rglob("*.json"))
                    outcome = next(outcome_root.rglob("*.json"))
                    freeze_data = json.loads(forecast.read_text(encoding="utf-8"))
                    outcome_data = json.loads(outcome.read_text(encoding="utf-8"))
                    freeze_data["nonfinite_probe"] = value
                    for payload in (freeze_data, outcome_data):
                        if declaration == "MISSING":
                            payload.pop("compass_sha256", None)
                        else:
                            payload["compass_sha256"] = declaration
                    forecast.write_text(json.dumps(freeze_data), encoding="utf-8")
                    outcome.write_text(json.dumps(outcome_data), encoding="utf-8")
                    report = MODULE.build_report(root, outcome_root, "2026-10-10T00:00:00Z")
                    self.assertEqual(report["eligible_series_row_count"], 0)
                    self.assertEqual(report["warning_series_row_count"], 0)
                    self.assertEqual(report["excluded_outcome_counts"]["FORECAST_PAYLOAD_HASH_MISMATCH"], 1)

    def test_genuine_canonical_freeze_payload_is_admitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outcome_root = self.write_case(root, pullback="BUILDING", distribution="UNKNOWN")
            freeze = next((root / "04_MARKET_LEARNING/handlekompas/official/daily").rglob("*.json"))
            raw = json.loads(freeze.read_text(encoding="utf-8"))
            self.assertEqual(MODULE.frozen_compass_digest(raw), raw["compass_sha256"])
            report = MODULE.build_report(root, outcome_root, "2026-10-10T00:00:00Z")
            self.assertEqual(report["eligible_series_row_count"], 2)
            self.assertEqual(report["warning_series_row_count"], 0)
            self.assertEqual(len(report["nonwarning_downside_context"]), 2)

    def test_compatibility_addendum_is_not_learned_as_prospective_machine_projection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outcome_root = self.write_case(root, projection_source="HASH_BOUND_COMPATIBILITY_ADDENDUM")
            report = MODULE.build_report(root, outcome_root, "2026-09-30T00:00:00Z")
            self.assertEqual(report["status"], "NO_ELIGIBLE_MATURED_ROWS")
            self.assertEqual(report["eligible_series_row_count"], 0)
            self.assertEqual(
                report["excluded_outcome_counts"]["PROJECTION_NOT_PROSPECTIVE_MACHINE_PACKAGE"],
                1,
            )

    def test_pre_repair_policy_and_degraded_protection_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outcome_root = self.write_case(root, policy="2026-09-24_LEGACY")
            report = MODULE.build_report(root, outcome_root, "2026-09-30T00:00:00Z")
            self.assertEqual(report["eligible_series_row_count"], 0)
            self.assertEqual(report["excluded_outcome_counts"]["UNREGISTERED_DECISION_POLICY"], 1)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outcome_root = self.write_case(root, data_quality="DEGRADED")
            report = MODULE.build_report(root, outcome_root, "2026-09-30T00:00:00Z")
            self.assertEqual(report["eligible_series_row_count"], 0)
            self.assertEqual(report["excluded_outcome_counts"]["PROTECTION_DATA_QUALITY_NOT_OK"], 1)

    def test_current_v4_policy_and_pullback_warning_are_eligible_with_unknown_distribution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outcome_root = self.write_case(
                root,
                policy="2026-09-30_DIRECTION_ACTION_SEPARATION_V4_0",
                pullback="ELEVATED",
                distribution="UNKNOWN",
            )
            report = MODULE.build_report(root, outcome_root, "2026-10-06T00:00:00Z")
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["eligible_series_row_count"], 2)
            self.assertEqual(report["warning_series_row_count"], 2)
            self.assertEqual(
                report["prospective_source_gate"]["registered_decision_policies"],
                [
                    "2026-09-25_DECISION_INTEGRITY_V3_2",
                    "2026-09-30_DIRECTION_ACTION_SEPARATION_V4_0",
                ],
            )

    def test_building_watch_with_unknown_distribution_is_calibrated_not_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outcome_root = self.write_case(
                root,
                policy="2026-09-30_DIRECTION_ACTION_SEPARATION_V4_0",
                pullback="BUILDING",
                distribution="UNKNOWN",
            )
            report = MODULE.build_report(root, outcome_root, "2026-10-06T17:00:00Z")
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["eligible_series_row_count"], 2)
            self.assertEqual(report["warning_series_row_count"], 0)
            self.assertIn("NO_MATURED_TYPED_WARNING_OUTCOMES", report["promotion_readiness"]["blockers"])

    def test_nonwarning_drawdown_is_visible_without_hindsight_sell_or_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outcome_root = self.write_case(
                root,
                policy="2026-09-30_DIRECTION_ACTION_SEPARATION_V4_0",
                pullback="BUILDING",
                distribution="UNKNOWN",
            )
            report = MODULE.build_report(root, outcome_root, "2026-10-09T17:00:00Z")
            self.assertEqual(report["warning_series_row_count"], 0)
            context = report["nonwarning_downside_context"]
            self.assertEqual(len(context), 2)
            btc = next(row for row in context if row["series_id"] == "BTC_USDT_MARK_PRICE")
            self.assertEqual(btc["horizon"], "72h")
            self.assertEqual(btc["series_row_count"], 1)
            self.assertEqual(btc["distinct_compass_freeze_count"], 1)
            self.assertEqual(btc["mae_observed_row_count"], 1)
            self.assertEqual(btc["worst_observed_mae_pct"], -12.0)
            self.assertIsNone(btc["independent_adverse_event_count"])
            self.assertEqual(btc["warning_classification"], "NO_TYPED_WARNING_IN_FROZEN_COMPASS")
            self.assertTrue(report["interpretation_boundary"]["nonwarning_downside_context_is_descriptive"])
            self.assertFalse(report["interpretation_boundary"]["market_rule_change"])
            self.assertFalse(report["promotion_readiness"]["automatic_promotion"])

    def test_warning_event_not_reclassified_as_nonwarning_gap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outcome_root = self.write_case(root, pullback="HIGH", distribution="WARNING")
            report = MODULE.build_report(root, outcome_root, "2026-10-09T17:00:00Z")
            self.assertEqual(report["warning_series_row_count"], 2)
            self.assertEqual(report["nonwarning_downside_context"], [])

    def test_nonwarning_absent_mae_does_not_become_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outcome_root = self.write_case(root, pullback="BUILDING", distribution="UNKNOWN")
            outcome_path = next(outcome_root.rglob("*.json"))
            item = json.loads(outcome_path.read_text())
            item["realized"]["btc_mae_pct"] = None
            outcome_path.write_text(json.dumps(item))
            report = MODULE.build_report(root, outcome_root, "2026-10-09T17:00:00Z")
            btc = next(row for row in report["nonwarning_downside_context"] if row["series_id"] == "BTC_USDT_MARK_PRICE")
            self.assertIsNone(btc["median_observed_mae_pct"])
            self.assertIsNone(btc["worst_observed_mae_pct"])
            self.assertEqual(btc["mae_missing_row_count"], 1)
            self.assertEqual(btc["mae_observed_row_count"], 0)

    def test_normal_typed_state_is_calibrated_without_being_called_a_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outcome_root = self.write_case(root, pullback="NORMAL", distribution="NONE")
            report = MODULE.build_report(root, outcome_root, "2026-09-30T00:00:00Z")
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["eligible_series_row_count"], 2)
            self.assertEqual(report["warning_series_row_count"], 0)
            self.assertIn("NO_MATURED_TYPED_WARNING_OUTCOMES", report["promotion_readiness"]["blockers"])

    def test_empty_repository_is_explicit_not_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = MODULE.build_report(root, root / "missing", "2026-09-30T00:00:00Z")
            self.assertEqual(report["status"], "NO_ELIGIBLE_MATURED_ROWS")
            self.assertEqual(report["source_outcome_count"], 0)
            self.assertEqual(report["cohorts"], [])
            self.assertIn(
                "NO_ELIGIBLE_PROSPECTIVE_TYPED_PROTECTION_OUTCOMES",
                report["promotion_readiness"]["blockers"],
            )


if __name__ == "__main__":
    unittest.main()
