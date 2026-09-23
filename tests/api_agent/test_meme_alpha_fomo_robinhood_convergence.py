from __future__ import annotations

import copy
import unittest
from datetime import datetime, timedelta, timezone

from scripts.api_agent import meme_alpha_fomo_robinhood_convergence as c
from scripts.api_agent import meme_alpha_fomo_robinhood_observer as o

TOKEN = "0x71e52e7cd3c13b278cd05e80c9a63b843cbed960"
OTHER = "0x" + "f" * 40
BASE = datetime(2026, 9, 22, 12, 0, tzinfo=timezone.utc)


def receipt(index: int, entity: str, minutes: int = 0, seconds: int = 0, token: str = TOKEN):
    ts = (BASE + timedelta(minutes=minutes, seconds=seconds)).isoformat().replace("+00:00", "Z")
    raw = {
        "wallet_address": "0x" + format(index, "040x"),
        "contract": token,
        "chain": "robinhood",
        "chain_id": 4663,
        "side": "buy",
        "kind": "swap",
        "self_initiated": True,
        "observed_at_utc": ts,
        "source_event_timestamp_utc": ts,
        "source": "fixture",
        "source_health": "PASS",
        "transaction_hash": "0x" + format(index, "064x"),
        "log_index": 0,
        "provenance_evidence_refs": [f"fixture:prov:{index}"],
        "provenance_independently_reproduced": True,
        "economic_entity_id": entity,
        "independence_state": "CONFIRMED",
        "liquidity_usd": 25000,
        "market_data_health": "PASS",
        "market_data_health_evidence_refs": [f"fixture:market:{index}"],
        "sellable": True,
        "prospective_admission_state": "PASS",
        "prospective_admission_evidence_ref": f"fixture:prospective:{index}",
    }
    return o.build_receipt(raw, {"handle": "fixture"}, retrieved_at=ts)


def batch(rows):
    return {"contract": "FOMO_ROBINHOOD_OBSERVER_BATCH_v1", "receipts": rows}


class ConvergenceTests(unittest.TestCase):
    def pair(self):
        return [receipt(1, "entity-A"), receipt(2, "entity-B", 12)]

    def assert_no(self, rows):
        out = c.aggregate(batch(rows))
        self.assertEqual(out["eligible_convergence_count"], 0)
        self.assertEqual(out["promotion_counter_increment"], 0)
        return out

    def test_valid_pair_and_zero_counter(self):
        out = c.aggregate(batch(self.pair()))
        self.assertEqual(out["eligible_convergence_count"], 1)
        self.assertEqual(out["unique_chain_token_count"], 1)
        self.assertEqual(out["promotion_counter_increment"], 0)
        self.assertEqual(out["eligible_convergences"][0]["qualifying_window_minutes"], [15, 30, 60, 180])
        self.assertEqual(out["eligible_convergences"][0]["promotion_counter_increment"], 0)

    def test_identity_tamper_rejected(self):
        for field, value in [
            ("token_ca", OTHER),
            ("wallet_address", "0x" + "e" * 40),
            ("observed_at_utc_exact", "2026-09-22T12:01:00Z"),
            ("source_event_timestamp_or_UNKNOWN", "2026-09-22T11:59:00Z"),
        ]:
            rows = self.pair()
            old = rows[0]["observation_id"]
            rows[0][field] = value
            self.assertNotEqual(o.observation_id(rows[0]), old)
            self.assert_no(rows)

        rows = self.pair()
        old = rows[0]["observation_id"]
        rows[0]["source_locator"]["log_index"] = 1
        self.assertNotEqual(o.observation_id(rows[0]), old)
        self.assert_no(rows)

    def test_entity_collapse(self):
        self.assert_no([receipt(1, "entity-A"), receipt(2, "entity-A", 5)])

    def test_frozen_windows(self):
        out = c.aggregate(batch(self.pair()))
        self.assertEqual(out["evaluated_window_minutes"], [15, 30, 60, 180])
        self.assertEqual(len({v["eligible_convergences"][0]["convergence_id"] for v in out["window_results"]}), 1)
        for minutes in c.FROZEN_WINDOWS:
            self.assertEqual(
                c.aggregate(batch([receipt(1, "A"), receipt(2, "B", minutes)]), window_minutes=minutes)["eligible_convergence_count"],
                1,
            )
            self.assertEqual(
                c.aggregate(batch([receipt(1, "A"), receipt(2, "B", minutes, 1)]), window_minutes=minutes)["eligible_convergence_count"],
                0,
            )

    def test_duplicate_conflict_and_replay(self):
        rows = self.pair()
        out = c.aggregate(batch(rows + [copy.deepcopy(rows[0])]))
        self.assertEqual(out["eligible_convergence_count"], 1)
        self.assertEqual(out["duplicate_receipt_count"], 1)
        conflicting = copy.deepcopy(rows[0])
        conflicting["economic_entity_id_or_PENDING"] = "entity-C"
        out = self.assert_no(rows + [conflicting])
        self.assertEqual(out["rejected_or_pending_receipt_count"], 2)
        first = c.aggregate(batch(rows))
        second = c.aggregate(batch(list(reversed(rows))))
        self.assertEqual(first, second)

    def test_required_gates_rechecked(self):
        for field, value in [
            ("independence_state", "PENDING"),
            ("source_health", "UNKNOWN"),
            ("market_data_health", "UNKNOWN"),
            ("market_data_health_evidence_refs", []),
            ("prospective_admission_state", "PENDING"),
            ("prospective_admission_evidence_ref", ""),
            ("sellability_state", "UNKNOWN"),
            ("provenance_independently_reproduced", False),
        ]:
            rows = self.pair()
            rows[0][field] = value
            self.assert_no(rows)

    def test_two_tokens_two_discoveries(self):
        rows = self.pair() + [receipt(3, "C", token=OTHER), receipt(4, "D", 12, token=OTHER)]
        out = c.aggregate(batch(rows))
        self.assertEqual(out["eligible_convergence_count"], 2)
        self.assertEqual(out["unique_chain_token_count"], 2)
        self.assertEqual(out["promotion_counter_increment"], 0)


if __name__ == "__main__":
    unittest.main()
