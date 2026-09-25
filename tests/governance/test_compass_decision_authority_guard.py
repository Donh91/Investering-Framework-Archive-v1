"""Permanent Compass decision-authority regression guard."""
from __future__ import annotations

import itertools
import unittest
from datetime import datetime, timezone

from scripts.data_ping.native_handlekompas import (
    action_context,
    capitalization_ladder,
    sell_assessment,
)

NOW = datetime(2026, 9, 25, 8, 0, tzinfo=timezone.utc)


def packet(*, breadth: float, ethbtc: float, entry_state: str) -> dict:
    stamp = "2026-09-25T08:00:00Z"
    return {
        "contract": "AUTO_MARKET_STATE_PACKET_v1",
        "packet_generated_at_utc": stamp,
        "packet_sha256": "guard-packet",
        "validation_status": "PASS",
        "decision_context_status": "PASS",
        "blockers": [],
        "normalized_state": {
            "live_market": {"ethbtc": ethbtc},
            "breadth": {"aggregate": {"advance_ratio": breadth}},
            "entry_signal_reference": {"state": entry_state},
        },
        "source_health": {
            "hourly_market": {
                "status": "PASS",
                "freshness": {
                    "status": "PASS",
                    "pointer_freshness": {"status": "PASS", "timestamp": stamp, "max_age_seconds": 10800},
                    "retrieval_freshness": {"status": "PASS", "timestamp": stamp, "max_age_seconds": 10800},
                    "session_coverage_freshness": {"status": "PASS", "timestamp": stamp, "max_age_seconds": 10800},
                    "source_observation_freshness": {"status": "PASS", "timestamp": stamp, "max_age_seconds": 10800},
                },
            }
        },
    }


class CompassDecisionAuthorityGuardTest(unittest.TestCase):
    def test_retired_proxy_grid_can_never_change_action(self):
        for breadth, ethbtc, entry_state in itertools.product(
            (0.10, 0.39, 0.50, 0.90),
            (0.0200, 0.0299, 0.0301, 0.0500),
            ("WAIT", "LEGACY_PATTERN_OBSERVED_FORWARD_ONLY_NOT_PROMOTION_READY", "GRADUATED_ALTCOIN_TOPUP_ACTIVE"),
        ):
            with self.subTest(breadth=breadth, ethbtc=ethbtc, entry_state=entry_state):
                action = action_context(
                    packet(breadth=breadth, ethbtc=ethbtc, entry_state=entry_state),
                    as_of=NOW,
                )
                self.assertEqual(action["NOW"], "HOLD_WAIT")
                self.assertEqual(action["proxy_authority"]["top100_breadth_action_weight"], 0)
                self.assertEqual(action["proxy_authority"]["ethbtc_0_03_gate_action_weight"], 0)
                self.assertFalse(action["proxy_authority"]["legacy_entry_observer_action_authority"])

    def test_meme_rung_cannot_inherit_microcap_authority(self):
        state = packet(breadth=0.90, ethbtc=0.05, entry_state="WAIT")
        ladder = capitalization_ladder(
            state,
            {"NOW": "GRADUATED_TOPUP_ACTIVE"},
            {"directional_state": "BULLISH"},
            as_of=NOW,
        )
        self.assertEqual(ladder[-2]["segment"], "MICROCAPS")
        self.assertEqual(ladder[-1]["segment"], "MEMES")
        self.assertEqual(ladder[-1]["status"], "UNAVAILABLE")
        self.assertEqual(ladder[-1]["action"], "UNAVAILABLE")
        self.assertEqual(ladder[-1]["direction"], "UNAVAILABLE")
        self.assertIn("MICROCAPS cannot be used as a proxy", ladder[-1]["reason"])

    def test_degraded_meme_rung_keeps_owner_specific_trigger(self):
        state = packet(breadth=0.10, ethbtc=0.02, entry_state="WAIT")
        state["validation_status"] = "FAIL"
        ladder = capitalization_ladder(
            state,
            {"NOW": "HOLD_WAIT_DATA_DEGRADED"},
            {"directional_state": "UNAVAILABLE"},
            as_of=NOW,
        )
        meme = ladder[-1]
        self.assertEqual(meme["segment"], "MEMES")
        self.assertEqual(meme["status"], "UNAVAILABLE")
        self.assertEqual(meme["upgrade_trigger"]["type"], "GOVERNED_MEME_DECISION_OWNER")
        self.assertNotEqual(meme["upgrade_trigger"]["type"], "ACTION_STATE")

    def test_protection_risk_cannot_silently_become_sell_authority(self):
        state = packet(breadth=0.10, ethbtc=0.02, entry_state="WAIT")
        protection = {
            "pullback_risk_state": "CONFIRMED",
            "distribution_risk": "CONFIRMED",
        }
        sell = sell_assessment(state, protection, as_of=NOW)
        self.assertEqual(sell["state"], "UNAVAILABLE")
        self.assertFalse(sell["authority"]["portfolio_execution"])
        self.assertFalse(sell["authority"]["new_sell_rule"])
        self.assertFalse(sell["authority"]["automatic_action"])
        self.assertFalse(sell["authority"]["protection_is_sell_authority"])


if __name__ == "__main__":
    unittest.main()
