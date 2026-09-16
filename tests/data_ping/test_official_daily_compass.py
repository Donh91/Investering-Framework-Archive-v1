import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.data_ping.native_handlekompas import (
    CAPITALIZATION_ORDER,
    HORIZON_ORDER,
    OFFICIAL_AUTHORITY,
    build_official_compass,
    build_public_projection,
    write_official_compass,
)


class OfficialDailyCompassTest(unittest.TestCase):
    def auto(self, *, breadth=0.19, validation="PASS", decision="PASS", blockers=None, btc=75654.0, eth=2396.86, ethbtc=0.03168):
        return {
            "contract": "AUTO_MARKET_STATE_PACKET_v1",
            "packet_generated_at_utc": "2026-09-16T18:09:48Z",
            "packet_sha256": "packet-sha",
            "source_snapshot": {"exact_commit_sha": "source-commit"},
            "validation_status": validation,
            "decision_context_status": decision,
            "blockers": blockers or [],
            "optional_degraded_lanes": [],
            "deltas_since_prior_auto_packet": {
                "btc_usdt": {"pct": -0.3},
                "eth_usdt": {"pct": -0.7},
                "ethbtc": {"pct": -0.4},
            },
            "normalized_state": {
                "live_market": {"btc_usdt": btc, "eth_usdt": eth, "ethbtc": ethbtc, "observation_open_utc": "2026-09-16T18:00:00Z"},
                "breadth": {"aggregate": {"advance_ratio": breadth, "advancers": 19, "decliners": 78, "equal_weight_mean_return_24h_pct": -2.59}},
                "entry_signal_reference": {"state": "WAIT"},
                "btc_dominance": {"value_pct": 58.4},
                "settled_etf": {"btc_reported_total_musd": -100.0, "eth_reported_total_musd": 50.0},
                "stablecoin_liquidity": {"total_usd": 300_000_000_000.0},
                "derivatives": {},
                "sentiment": {"classification": "NEUTRAL"},
                "altseason_context": {"blockchaincenter_altcoin_season": {"horizons": {"90": {"published_score": 27}}}},
            },
            "source_health": {
                "hourly_market": {"status": "PASS"},
                "breadth": {"status": "PASS"},
                "btc_dominance": {"status": "PASS"},
                "settled_etf": {"status": "PASS"},
                "stablecoin_liquidity": {"status": "PASS"},
                "derivatives": {"status": "PASS"},
                "sentiment": {"status": "PASS"},
                "altseason_context": {"status": "PASS"},
                "entry_signal_reference": {"status": "PASS"},
            },
        }

    def cn(self):
        return {
            "issue_number": 26,
            "market_state": "Unresolved, volatile consolidation with elevated pullback risk.",
            "base_case_this_week": "W38 remains an unresolved, volatile consolidation with elevated pullback risk rather than a confirmed breakdown or broad risk expansion.",
        }

    def build(self, root, **kwargs):
        return build_official_compass(
            self.auto(**kwargs),
            packet_path=Path("04_MARKET_LEARNING/entry_signals/auto_market_state/runs/test.json"),
            cn_package=self.cn(),
            cn_binding={"status": "PASS"},
            repo_root=Path(root),
            issued_at=datetime(2026, 9, 16, 20, 17, tzinfo=timezone.utc),
            run_reason="SCHEDULED_DAILY",
        )

    def test_deterministic_same_input_same_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = self.build(tmp)
            b = self.build(tmp)
            self.assertEqual(a, b)
            self.assertEqual(a["compass_sha256"], b["compass_sha256"])

    def test_required_horizons_and_ladder_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.build(tmp)
            self.assertEqual(tuple(out["horizons"].keys()), HORIZON_ORDER)
            self.assertEqual(tuple(row["segment"] for row in out["capitalization_ladder"]), CAPITALIZATION_ORDER)
            self.assertEqual(out["authority"], OFFICIAL_AUTHORITY)
            self.assertFalse(out["authority"]["portfolio_execution"])

    def test_missing_values_remain_null_not_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.build(tmp, btc=None, eth=None, ethbtc=None)
            self.assertIsNone(out["market_reference"]["btc_usdt"])
            self.assertIsNone(out["market_reference"]["eth_usdt"])
            values = {row["feature_id"]: row["value"] for row in out["evidence_snapshot"]["selected_features"]}
            self.assertIsNone(values["btc_usdt"])
            self.assertIsNone(values["eth_usdt"])

    def test_degraded_state_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.build(tmp, validation="FAIL", decision="DEGRADED", blockers=["hourly_market"])
            self.assertEqual(out["data_status"], "DEGRADED")
            self.assertTrue(all(row["status"] == "UNAVAILABLE" for row in out["capitalization_ladder"]))
            self.assertTrue(all(out["horizons"][key]["expected_direction"] == "UNAVAILABLE" for key in HORIZON_ORDER))

    def test_public_projection_does_not_leak_internal_bindings_or_threshold_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.build(tmp)
            public = build_public_projection(out)
            self.assertNotIn("source_bindings", public)
            self.assertNotIn("evidence_snapshot", public)
            self.assertNotIn("native_action_contract", public)
            for row in public["capitalization_ladder"]:
                self.assertNotIn("upgrade_trigger", row)
                self.assertNotIn("deterioration_trigger", row)

    def test_scheduled_daily_freeze_is_single_and_immutable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "official"
            out = self.build(tmp)
            first = write_official_compass(out, root)
            second = write_official_compass(out, root)
            self.assertEqual(first["status"], "WRITTEN")
            self.assertEqual(second["status"], "EXISTING_DAILY_FREEZE")
            frozen = json.loads(Path(first["path"]).read_text())
            self.assertEqual(frozen["compass_sha256"], out["compass_sha256"])


if __name__ == "__main__":
    unittest.main()
