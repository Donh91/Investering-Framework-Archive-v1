import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "research" / "memes_alpha"))

from core import (  # noqa: E402
    build_public_manifest,
    cadence_due,
    canonical_identity,
    choose_cadence,
    classify_transfer,
    convergence_events,
    cross_chain_snapshot,
    make_event,
    solana_risk_features,
    stable_hash,
    validate_public_payload,
)


class MemesAlphaCoreTests(unittest.TestCase):
    def test_intentional_buy_requires_wallet_initiated_capital_and_swap(self):
        self.assertEqual(classify_transfer({"direction": "IN", "wallet_initiated": True, "capital_committed": True, "swap_proven": True}), "INTENTIONAL_BUY")
        self.assertEqual(classify_transfer({"direction": "IN", "wallet_initiated": False, "capital_committed": False, "swap_proven": False}), "PASSIVE_RECEIPT")
        self.assertEqual(classify_transfer({"direction": "IN", "airdrop": True}), "DUST_OR_SPAM")

    def test_user_origin_is_preserved(self):
        event = make_event(chain_id="ethereum", identity="0x" + "1" * 40, wallet_ref="0x" + "2" * 40,
                           origin="USER_SUPPLIED", observed_at="2026-09-12T00:00:00Z", source_refs=["fixture"],
                           observation={"direction": "IN", "wallet_initiated": True, "capital_committed": True, "swap_proven": True})
        self.assertEqual(event["origin"], "USER_SUPPLIED")
        self.assertEqual(event["event_class"], "INTENTIONAL_BUY")

    def test_convergence_exactly_once(self):
        asset = "0x" + "3" * 40
        events = []
        qualified = set()
        for idx in (1, 2):
            wallet = "0x" + str(idx) * 40
            e = make_event(chain_id="ethereum", identity=asset, wallet_ref=wallet, origin="AUTONOMOUS_DISCOVERY",
                           observed_at=f"2026-09-12T0{idx}:00:00Z", source_refs=["fixture"],
                           observation={"direction": "IN", "wallet_initiated": True, "capital_committed": True, "swap_proven": True})
            events.append(e)
            qualified.add(e["wallet_identity_hash"])
        convergence = convergence_events(events + events, qualified)
        self.assertEqual(len(convergence), 1)
        self.assertEqual(convergence[0]["qualified_wallet_count"], 2)

    def test_solana_exact_mint_and_cluster_risk(self):
        with self.assertRaises(ValueError):
            solana_risk_features(exact_mint_verified=False, top10_concentration=0.1, linked_fresh_wallet_cluster=False, paid_boost=False, creator_verified=None)
        result = solana_risk_features(exact_mint_verified=True, top10_concentration=0.1, linked_fresh_wallet_cluster=True, paid_boost=True, creator_verified=True)
        self.assertEqual(result["distribution_state"], "CLUSTER_RISK")
        self.assertFalse(result["paid_boost_counts_as_independent_alpha"])

    def test_cross_chain_requires_identity_and_no_hindsight(self):
        with self.assertRaises(ValueError):
            cross_chain_snapshot([{"identity_verified": False}])
        with self.assertRaises(ValueError):
            cross_chain_snapshot([{
                "identity_verified": True, "chain_id": "solana", "asset_identity_hash": stable_hash("a"),
                "frozen_discovery_features": {"future_return": 5.0},
            }])

    def test_public_manifest_rejects_private_identifiers(self):
        manifest = build_public_manifest(private_manifest_hash=stable_hash("m"), seed_hash=stable_hash("s"), case_count=2,
                                         event_counts={"INTENTIONAL_BUY": 1}, chain_coverage={"solana": "PASS"}, health="PASS", reason_codes=[])
        validate_public_payload(manifest)
        with self.assertRaises(ValueError):
            validate_public_payload({"wallet_address": "0x" + "a" * 40})
        with self.assertRaises(ValueError):
            validate_public_payload({"leak": "0x" + "a" * 40})

    def test_adaptive_cadence_and_noop_due_logic(self):
        self.assertEqual(choose_cadence(high_value_event=False, qualified_case_count=0, source_degraded=False), "COLD")
        self.assertEqual(choose_cadence(high_value_event=False, qualified_case_count=1, source_degraded=False), "WATCH")
        self.assertEqual(choose_cadence(high_value_event=True, qualified_case_count=1, source_degraded=False), "HOT")
        now = datetime(2026, 9, 12, 12, tzinfo=timezone.utc)
        self.assertFalse(cadence_due("2026-09-12T11:30:00Z", "HOT", now))
        self.assertTrue(cadence_due("2026-09-12T10:30:00Z", "HOT", now))

    def test_no_trade_authority_key_can_enter_manifest(self):
        with self.assertRaises(ValueError):
            validate_public_payload({"position_size": "10%"})


if __name__ == "__main__":
    unittest.main()
