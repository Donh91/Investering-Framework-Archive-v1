from __future__ import annotations

import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.learning.shadow_compass_v2 import (
    FORECAST_CONTRACT,
    INPUT_CONTRACT,
    MODEL_OUTPUT_CONTRACT,
    build_forecast,
    build_input,
    validate_model_output,
)


class ShadowCompassV2Tests(unittest.TestCase):
    def auto_state(self):
        return {
            "contract": "AUTO_MARKET_STATE_PACKET_v1",
            "packet_sha256": "auto-sha",
            "packet_generated_at_utc": "2026-09-30T19:09:59Z",
            "source_snapshot": {"exact_commit_sha": "source-sha"},
            "validation_status": "PASS",
            "decision_context_status": "PASS",
            "blockers": [],
            "optional_degraded_lanes": [],
            "missingness_policy": "MISSING_IS_UNKNOWN_DEGRADED_OR_UNAVAILABLE_NEVER_BEARISH",
            "source_health": {"hourly_market": {"status": "PASS"}},
            "deltas_since_prior_auto_packet": {
                "btc_usdt": {"pct": -1.0},
                "eth_usdt": {"pct": -1.5},
                "ethbtc": {"pct": -0.5},
            },
            "normalized_state": {
                "live_market": {"btc_usdt": 83000.0, "eth_usdt": 2660.0, "ethbtc": 0.032, "observation_open_utc": "2026-09-30T19:00:00Z"},
                "spot_hourly": {
                    "observation_open_utc": "2026-09-30T19:00:00Z",
                    "BTCUSDT": {"return_1h_pct": -0.4, "taker_buy_quote_share": 0.42},
                    "ETHUSDT": {"return_1h_pct": -0.7, "taker_buy_quote_share": 0.40},
                    "ETHBTC": {"return_1h_pct": -0.2},
                },
                "microstructure": {
                    "retrieval_timestamp": "2026-09-30T19:05:00Z",
                    "source": "BINANCE_SPOT_MARKET_DATA_ONLY",
                    "symbols": {
                        "BTCUSDT": {"midpoint": 83010.0, "vwap": 83020.0, "spread_bps": 0.01, "depth20_quote_notional_imbalance": 0.2, "taker_quote_imbalance": -0.1, "trade_count": 1000},
                        "ETHUSDT": {"midpoint": 2661.0, "vwap": 2662.0, "spread_bps": 0.04, "depth20_quote_notional_imbalance": -0.2, "taker_quote_imbalance": -0.3, "trade_count": 1000},
                    },
                },
                "derivatives": {
                    "hourly": {"btc_open_interest": 2_700_000.0, "eth_open_interest": 5_500_000.0, "btc_oi_change_1h_pct": 1.0, "eth_oi_change_1h_pct": 2.0},
                    "live_anchor": {},
                },
                "current_breadth": {"advance_ratio": 0.35, "advancers": 35, "decliners": 63, "observed_at_utc": "2026-09-30T19:05:00Z"},
                "breadth": {"aggregate": {"equal_weight_mean_return_24h_pct": -1.0, "median_return_24h_pct": -0.8}},
                "btc_dominance": {"value_pct": 58.6},
                "settled_etf": {"btc_reported_total_musd": 60.0, "eth_reported_total_musd": -5.0},
                "stablecoin_liquidity": {"total_usd": 300_000_000_000.0, "change_7d_pct": 1.0},
                "macro_risk": {},
                "sentiment": {},
                "altseason_context": {},
                "entry_signal_reference": {"state": "WAIT"},
            },
        }

    def cn(self):
        return {
            "issue_number": 28,
            "base_case_this_week": "Consolidation with retest risk.",
            "base_case_2_3_weeks": "Selective recovery if breadth improves.",
            "decision_projection": {
                "contract": "CYCLE_NAVIGATOR_DECISION_PROJECTION_v1",
                "next_1_3d": {"direction": "MIXED", "summary": "Mixed."},
                "next_5_7d": {"direction": "SIDEWAYS", "summary": "Consolidation."},
                "next_2_3w": {"direction": "SIDEWAYS", "summary": "Consolidation."},
                "weeks_4_8": {"direction": "UNAVAILABLE"},
                "protection": {"pullback_risk_state": "BUILDING"},
            },
        }

    def input_value(self):
        return build_input(
            self.auto_state(),
            auto_pointer={"packet_path": "x", "packet_sha256": "auto-sha"},
            auto_packet_path=Path("04_MARKET_LEARNING/entry_signals/auto_market_state/runs/test.json"),
            cn_package=self.cn(),
            cn_binding={
                "status": "PASS", "issue_number": 28, "iso_week": 40, "iso_year": 2026,
                "decision_projection_source": "MACHINE_PACKAGE",
                "machine_package": {"content_sha256": "cn-sha"},
            },
            issued_at=datetime(2026, 9, 30, 20, 30, tzinfo=timezone.utc),
        )

    def model_output(self):
        row = {
            "direction": "DOWN",
            "expected_path": "retest -> reassess",
            "supporting_evidence": ["BTC and ETH both weak"],
            "contradicting_evidence": ["BTC ETF flow positive"],
            "missing_evidence": [],
            "pullback_risk": "BUILDING",
            "transmission_state": "DETERIORATING",
            "confidence": "MEDIUM",
            "falsification_conditions": ["BTC and ETH reclaim while breadth improves"],
        }
        return {
            "contract": MODEL_OUTPUT_CONTRACT,
            "horizons": {"12h": dict(row), "72h": dict(row), "168h": {**row, "direction": "MIXED"}},
            "cross_horizon_summary": "Tactical weakness inside unresolved weekly structure.",
            "global_missing_evidence": [],
        }

    def test_input_is_compact_shadow_context_not_official_answer_key(self):
        value = self.input_value()
        self.assertEqual(value["contract"], INPUT_CONTRACT)
        self.assertEqual(value["market"]["spot_hourly"]["BTCUSDT"]["return_1h_pct"], -0.4)
        self.assertEqual(value["market"]["microstructure"]["symbols"]["ETHUSDT"]["taker_quote_imbalance"], -0.3)
        self.assertEqual(value["structural_prior"]["authority"], "CYCLE_NAVIGATOR_CONTEXT_NOT_ANSWER_KEY")
        self.assertNotIn("official_compass", value)
        self.assertEqual(value["source_bindings"]["auto_market_state"]["packet_sha256"], "auto-sha")

    def test_model_output_requires_falsification_and_controlled_horizons(self):
        value = self.model_output()
        validate_model_output(value)
        broken = self.model_output()
        broken["horizons"]["12h"]["falsification_conditions"] = []
        with self.assertRaisesRegex(ValueError, "falsification_missing"):
            validate_model_output(broken)

    def test_forecast_remains_shadow_only_with_zero_execution_authority(self):
        input_value = self.input_value()
        model_output = self.model_output()
        forecast = build_forecast(
            input_value,
            model_output,
            {"usage": {"input_tokens": 1000, "output_tokens": 500, "total_tokens": 1500}},
            model="gpt-6.1-sol",
        )
        self.assertEqual(forecast["contract"], FORECAST_CONTRACT)
        self.assertEqual(forecast["model_id"], "gpt-6.1-sol")
        self.assertFalse(forecast["authority"]["portfolio_execution"])
        self.assertFalse(forecast["authority"]["official_compass_override"])
        self.assertFalse(forecast["authority"]["automatic_promotion"])
        self.assertEqual(forecast["usage"]["total_tokens"], 1500)


if __name__ == "__main__":
    unittest.main()
