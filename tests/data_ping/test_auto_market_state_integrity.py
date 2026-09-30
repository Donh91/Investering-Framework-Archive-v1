from __future__ import annotations

import unittest

from scripts.data_ping.auto_market_state import etf, select_current_breadth, stablecoin


class AutoMarketStateIntegrityTests(unittest.TestCase):
    def test_freshest_same_family_breadth_point_wins_without_double_vote(self):
        rich = {
            "retrieved_at_utc": "2026-09-30T14:59:03Z",
            "aggregate": {
                "advance_ratio": 0.33,
                "advancers": 33,
                "decliners": 65,
                "flat": 2,
                "constituent_count": 100,
            },
            "universe": {"membership_hash": "rich-hash", "constituent_count": 100},
        }
        live = {
            "advancers": 74,
            "decliners": 24,
            "flat": 2,
            "constituent_count": 100,
            "membership_hash": "live-hash",
            "observation": {"retrieval_timestamp_utc": "2026-09-30T17:59:20Z"},
            "evidence_semantics": {"evidence_role": "PROXY_ONLY"},
        }
        out = select_current_breadth(rich, live)
        self.assertIsNotNone(out)
        self.assertEqual(out["source"], "LIVE_ANCHOR_BREADTH_REFERENCE")
        self.assertAlmostEqual(out["advance_ratio"], 0.74)
        self.assertEqual(out["advancers"], 74)
        self.assertEqual(out["selection_semantics"], "FRESHEST_SAME_FAMILY_POINT_ONLY_NO_DOUBLE_VOTE")
        self.assertFalse(out["temporal_comparison"]["independent_vote"])
        self.assertTrue(out["temporal_comparison"]["same_upstream_family"])
        self.assertEqual(out["temporal_comparison"]["older_source"], "RICH_BREADTH_OWNER")
        self.assertEqual(out["temporal_comparison"]["newer_source"], "LIVE_ANCHOR_BREADTH_REFERENCE")

    def test_timestamped_rich_breadth_beats_untimestamped_live_reference(self):
        rich = {
            "retrieved_at_utc": "2026-09-30T14:59:03Z",
            "aggregate": {"advance_ratio": 0.42, "advancers": 42, "decliners": 56, "constituent_count": 100},
        }
        live = {"advancers": 80, "decliners": 18, "constituent_count": 100}
        out = select_current_breadth(rich, live)
        self.assertEqual(out["source"], "RICH_BREADTH_OWNER")
        self.assertAlmostEqual(out["advance_ratio"], 0.42)

    def test_stablecoin_normalization_preserves_source_and_retrieval_time(self):
        out, health = stablecoin({
            "contract": "DEFILLAMA_STABLECOIN_LIQUIDITY_OWNER_v1_1",
            "global": {
                "total_usd": 300_000_000_000.0,
                "change_1d_pct": 0.1,
                "change_7d_pct": 1.0,
                "change_30d_pct": 2.0,
                "timestamp": 1790726400,
            },
            "retrieved_at_utc": "2026-09-30T11:13:52Z",
            "evidence_semantics": {"evidence_role": "SUPPLY_LIQUIDITY", "deployment_confirmation": "NOT_ESTABLISHED"},
            "authority": {"binding": False, "canonical_acceptance": False, "state_change": False, "portfolio_action": False},
        })
        self.assertEqual(health["status"], "PASS")
        self.assertEqual(out["retrieved_at_utc"], "2026-09-30T11:13:52Z")
        self.assertIsNotNone(out["source_timestamp"])

    def test_etf_normalization_preserves_retrieval_time(self):
        out, health = etf({
            "contract": "DAILY_SETTLED_ETF_CALIBRATION_v2",
            "session_date": "2026-09-29",
            "retrieved_at_utc": "2026-09-30T12:27:59Z",
            "rows": [
                {"asset": "BTC", "session_final": True, "total_parity": True, "reported_total": 66.2},
                {"asset": "ETH", "session_final": True, "total_parity": True, "reported_total": -2.8},
            ],
        })
        self.assertEqual(health["status"], "PASS")
        self.assertEqual(out["retrieved_at_utc"], "2026-09-30T12:27:59Z")
        self.assertEqual(out["btc_reported_total_musd"], 66.2)
        self.assertEqual(out["eth_reported_total_musd"], -2.8)


if __name__ == "__main__":
    unittest.main()
