from __future__ import annotations

import importlib.util
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts" / "entry_signal" / "entry_signal_ledger.py"

spec = importlib.util.spec_from_file_location("entry_signal_ledger", MODULE_PATH)
ledger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ledger)


class EntrySignalMeasurementValidityTests(unittest.TestCase):
    def _market(self, eligible: bool):
        return {
            "ethbtc": 0.03147,
            "top100_advance_ratio": 0.70,
            "btc_return_24h_pct": 0.50,
            "eth_return_24h_pct": 0.79,
            "median_return_24h_pct": 0.34,
            "measurement_validity": {
                "independent_rotation_confirmation_eligible": eligible,
                "source_independence_eligible": eligible,
                "relative_breadth": {"outperforming_btc_share": 0.41},
            },
        }

    def test_legacy_pattern_fails_closed_until_explicit_canonical_promotion(self):
        state, checks, heat, observer_state = ledger.classify(self._market(False))
        self.assertEqual(state, "WAIT")
        self.assertEqual(
            set(checks),
            {
                "ethbtc_above_registered_0_0300",
                "top100_proxy_breadth_ge_50pct",
                "eth_outperforms_btc_24h",
            },
        )
        self.assertTrue(all(checks.values()))
        self.assertEqual(observer_state, "LEGACY_PATTERN_OBSERVED_FORWARD_ONLY_NOT_PROMOTION_READY")
        self.assertFalse(ledger.GRADUATED_DEPLOYMENT_PROMOTION["permits_active_state"])
        self.assertEqual(ledger.GRADUATED_DEPLOYMENT_PROMOTION["status"], "FORWARD_ONLY_NOT_PROMOTION_READY")
        self.assertEqual(heat, "NORMAL")

    def test_source_quality_upgrade_does_not_silently_restore_retired_breadth_gate(self):
        state, checks, _, observer_state = ledger.classify(self._market(True))
        self.assertEqual(state, "WAIT")
        self.assertTrue(all(checks.values()))
        self.assertEqual(observer_state, "LEGACY_PATTERN_OBSERVED_FORWARD_ONLY_NOT_PROMOTION_READY")

    def test_breadth_measurement_validity_exposes_relative_transmission_and_zero_weight(self):
        breadth = {
            "aggregate": {
                "constituent_count": 100,
                "advancers": 70,
                "advance_ratio": 0.70,
                "outperforming_btc_count": 41,
                "outperforming_eth_count": 33,
                "median_return_24h_pct": 0.34,
                "equal_weight_mean_return_24h_pct": 0.81,
            },
            "evidence_semantics": {
                "evidence_role": "PROXY_ONLY",
                "canonical_compatible": False,
                "canonical_large_cap_breadth": "UNCONFIRMED",
                "canonical_broad_alt_breadth": "UNCONFIRMED",
            },
            "observation": {"window_semantics": "SOURCE_REPORTED_ROLLING_24H_AT_RETRIEVAL"},
        }
        mv = ledger.measurement_validity_from_breadth(breadth)
        self.assertFalse(mv["source_independence_eligible"])
        self.assertEqual(mv["absolute_breadth_semantics"], "DESCRIPTIVE_PARTICIPATION_ZERO_EXECUTION_WEIGHT")
        self.assertEqual(mv["breadth_entry_permission"], "RETIRED_ZERO_WEIGHT")
        self.assertAlmostEqual(mv["relative_breadth"]["outperforming_btc_share"], 0.41)
        self.assertAlmostEqual(mv["relative_breadth"]["outperforming_eth_share"], 0.33)
        self.assertIn("overlapping rolling window", mv["rolling_window_confirmation_policy"])

    def test_bridge_cannot_present_learning_observer_as_action_authority(self):
        current = self._market(False)
        line = ledger.bridge_display_line(
            "WAIT", "LEGACY_PATTERN_OBSERVED_FORWARD_ONLY_NOT_PROMOTION_READY", "NORMAL", current
        )
        self.assertTrue(line.startswith("LEARNING OBSERVER:"))
        self.assertIn("canonical_action_authority=NONE", line)
        self.assertIn("promotion=FORWARD_ONLY_NOT_PROMOTION_READY", line)
        self.assertIn("outperforming_BTC=41%", line)
        self.assertNotIn("ENTRY/TOP-UP:", line)

    def test_relative_alpha_is_explicit_in_return_bundle(self):
        base = {
            "btc_usdt": 100.0,
            "eth_usdt": 100.0,
            "ethbtc": 0.03,
            "constituents": {"a": 100.0, "b": 100.0},
        }
        current = {
            "btc_usdt": 110.0,
            "eth_usdt": 105.0,
            "ethbtc": 0.031,
            "constituents": {"a": 104.0, "b": 102.0},
        }
        rb = ledger.return_bundle(base, current)
        self.assertAlmostEqual(rb["matched_top100_equal_weight_pct"], 3.0)
        self.assertAlmostEqual(rb["matched_top100_minus_btc_pp"], -7.0)
        self.assertAlmostEqual(rb["matched_top100_minus_eth_pp"], -2.0)

    def test_later_outcomes_do_not_define_historical_signal_validity(self):
        self.assertIn("must not retroactively invalidate", ledger.HISTORICAL_VALIDITY_POLICY)
        self.assertIn("contemporaneous evidence-role", ledger.HISTORICAL_VALIDITY_POLICY)

    def test_summary_excludes_unverified_legacy_horizons_without_rewriting_them(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            old_events, old_outcomes, old_summary = ledger.EVENTS, ledger.OUTCOMES, ledger.SUMMARY
            try:
                ledger.EVENTS = tmp / "events"
                ledger.OUTCOMES = tmp / "outcomes"
                ledger.SUMMARY = tmp / "summary.json"
                ledger.EVENTS.mkdir()
                ledger.OUTCOMES.mkdir()
                ledger.write_json(ledger.EVENTS / "event.json", {"event_type": "ACTIVATION", "event_id": "legacy"})
                legacy = {
                    "contract": "ENTRY_SIGNAL_OUTCOME_v1",
                    "horizons": {
                        "24h": {
                            "btc_return_since_signal_pct": 5.0,
                            "eth_return_since_signal_pct": 4.0,
                            "matched_top100_equal_weight_return_since_signal_pct": 1.0,
                        }
                    },
                }
                outcome_path = ledger.OUTCOMES / "legacy.json"
                ledger.write_json(outcome_path, legacy)
                before = outcome_path.read_bytes()
                ledger.build_summary(datetime(2026, 8, 30, tzinfo=timezone.utc))
                after = outcome_path.read_bytes()
                self.assertEqual(before, after)
                summary = ledger.read_json(ledger.SUMMARY)
                h = summary["horizons"]["24h"]
                self.assertIsNone(h["matched_top100_minus_btc_mean_pp"])
                self.assertIsNone(h["matched_top100_outperformed_btc_rate_pct"])
                self.assertEqual(h["matured_event_count"], 0)
                self.assertEqual(h["excluded_measurement_count"], 1)
                self.assertEqual(summary["promotion_authority"]["status"], "FORWARD_ONLY_NOT_PROMOTION_READY")
                self.assertIn("must not retroactively invalidate", summary["historical_validity_policy"])
            finally:
                ledger.EVENTS, ledger.OUTCOMES, ledger.SUMMARY = old_events, old_outcomes, old_summary


if __name__ == "__main__":
    unittest.main()
