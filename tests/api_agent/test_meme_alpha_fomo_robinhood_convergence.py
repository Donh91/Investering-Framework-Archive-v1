from __future__ import annotations

import unittest

from scripts.api_agent import meme_alpha_fomo_robinhood_convergence as c

TOKEN = "0x71e52e7cd3c13b278cd05e80c9a63b843cbed960"


def r(obs: str, wallet: str, entity: str, ts: str, **kw):
    row = {
        "contract": "FOMO_ROBINHOOD_OBSERVER_RECEIPT_v1",
        "observation_id": obs,
        "state": "PROVENANCE_PASS",
        "provenance_independently_reproduced": True,
        "sellability_state": "PASS",
        "economic_entity_id_or_PENDING": entity,
        "observed_at_utc_exact": ts,
        "token_ca": TOKEN,
        "wallet_address": wallet,
        "chain": "robinhood",
    }
    row.update(kw)
    return row


class ConvergenceTests(unittest.TestCase):
    def test_two_distinct_entities_freeze_one_eligible_convergence(self):
        batch = {"contract": "FOMO_ROBINHOOD_OBSERVER_BATCH_v1", "receipts": [
            r("a", "0x"+"1"*40, "entity-A", "2026-09-20T12:00:00Z"),
            r("b", "0x"+"2"*40, "entity-B", "2026-09-20T12:12:00Z"),
        ]}
        out = c.aggregate(batch, window_minutes=60)
        self.assertEqual(out["eligible_convergence_count"], 1)
        self.assertEqual(out["promotion_counter_increment"], 1)
        event = out["eligible_convergences"][0]
        self.assertEqual(event["state"], c.ELIGIBLE)
        self.assertEqual(event["independent_entity_count"], 2)
        self.assertFalse(event["authority"]["buy"])

    def test_two_wallets_same_entity_do_not_converge(self):
        batch = {"receipts": [
            r("a", "0x"+"1"*40, "entity-A", "2026-09-20T12:00:00Z"),
            r("b", "0x"+"2"*40, "entity-A", "2026-09-20T12:05:00Z"),
        ]}
        out = c.aggregate(batch)
        self.assertEqual(out["eligible_convergence_count"], 0)
        self.assertEqual(out["promotion_counter_increment"], 0)

    def test_seeded_or_pending_receipt_cannot_converge(self):
        bad = r("a", "0x"+"1"*40, "entity-A", "2026-09-20T12:00:00Z", state="PROVENANCE_REJECT")
        pending = r("b", "0x"+"2"*40, "entity-B", "2026-09-20T12:05:00Z", economic_entity_id_or_PENDING="PENDING")
        out = c.aggregate({"receipts": [bad, pending]})
        self.assertEqual(out["eligible_convergence_count"], 0)
        self.assertEqual(out["rejected_or_pending_receipt_count"], 2)

    def test_unreproduced_provenance_cannot_converge(self):
        batch = {"receipts": [
            r("a", "0x"+"1"*40, "entity-A", "2026-09-20T12:00:00Z", provenance_independently_reproduced=False),
            r("b", "0x"+"2"*40, "entity-B", "2026-09-20T12:05:00Z"),
        ]}
        self.assertEqual(c.aggregate(batch)["promotion_counter_increment"], 0)

    def test_outside_window_does_not_converge(self):
        batch = {"receipts": [
            r("a", "0x"+"1"*40, "entity-A", "2026-09-20T12:00:00Z"),
            r("b", "0x"+"2"*40, "entity-B", "2026-09-20T13:01:00Z"),
        ]}
        self.assertEqual(c.aggregate(batch, window_minutes=60)["promotion_counter_increment"], 0)

    def test_missing_exact_timestamp_fails_closed(self):
        batch = {"receipts": [
            r("a", "0x"+"1"*40, "entity-A", "UNKNOWN"),
            r("b", "0x"+"2"*40, "entity-B", "2026-09-20T12:05:00Z"),
        ]}
        self.assertEqual(c.aggregate(batch)["promotion_counter_increment"], 0)


if __name__ == "__main__":
    unittest.main()
