from __future__ import annotations

import copy
import unittest

from scripts.api_agent import meme_alpha_fomo_robinhood_observer as o

W1 = "0x0a6ebed0155edb4b21d92ad02897a626cd90119e"
TOKEN = "0x71e52e7cd3c13b278cd05e80c9a63b843cbed960"
RETRIEVED = "2026-09-22T12:01:00Z"


def activity() -> dict:
    return {
        "wallet_address": W1,
        "contract": TOKEN,
        "side": "buy",
        "kind": "swap",
        "self_initiated": True,
        "observed_at_utc": "2026-09-22T12:00:00Z",
        "source_event_timestamp_utc": "2026-09-22T11:59:58Z",
        "source": "fixture-chain-provider",
        "source_health": "PASS",
        "chain": "robinhood",
        "chain_id": 4663,
        "transaction_hash": "0x" + "a" * 64,
        "log_index": 0,
        "provenance_evidence_refs": ["fixture:independent-reproduction"],
        "provenance_independently_reproduced": True,
        "economic_entity_id": "entity-A",
        "independence_state": "CONFIRMED",
        "liquidity_usd": 25000,
        "market_data_health": "PASS",
        "market_data_health_evidence_refs": ["fixture:market-integrity"],
        "sellable": True,
        "prospective_admission_state": "PASS",
        "prospective_admission_evidence_ref": "fixture:prospective",
    }


class ObserverTests(unittest.TestCase):
    def receipt(self, row=None):
        return o.build_receipt(activity() if row is None else row, {"handle": "fixture"}, retrieved_at=RETRIEVED)

    def test_valid_receipt_and_legacy_identity(self):
        row = activity()
        before = copy.deepcopy(row)
        receipt = self.receipt(row)
        self.assertEqual(receipt["state"], "PROVENANCE_PASS")
        self.assertEqual(receipt["observation_id"], o.observation_id(receipt))
        legacy = {
            "wallet_address": W1,
            "token_ca": TOKEN,
            "observed_at_utc_exact": "2026-09-22T12:00:00Z",
            "source_event_timestamp_utc": "2026-09-22T11:59:58Z",
            "source_tx": row["transaction_hash"],
            "source_log_index": 0,
        }
        expected = "FOMO-RH-" + o.hashlib.sha256(o.canon(legacy)).hexdigest()[:20]
        self.assertEqual(receipt["observation_id"], expected)
        self.assertEqual(row, before)
        self.assertFalse(receipt["promotion_counter_eligible"])

    def test_raw_classify_separate_from_receipt_only_gates(self):
        row = activity()
        for key in (
            "observed_at_utc",
            "source_event_timestamp_utc",
            "transaction_hash",
            "log_index",
            "prospective_admission_state",
            "prospective_admission_evidence_ref",
        ):
            del row[key]
        self.assertEqual(o.classify(row), "PROVENANCE_PASS")
        self.assertEqual(self.receipt(row)["state"], "TIMESTAMP_MISSING")

    def test_fail_closed_gates(self):
        cases = [
            ("self_initiated", False, "PROVENANCE_PENDING"),
            ("provenance_independently_reproduced", False, "PROVENANCE_PENDING"),
            ("provenance_evidence_refs", [], "PROVENANCE_PENDING"),
            ("independence_state", "PENDING", "ENTITY_PENDING"),
            ("source_health", "UNKNOWN", "DEGRADED"),
            ("market_data_health", "UNKNOWN", "MARKET_HEALTH_PENDING"),
            ("market_data_health_evidence_refs", [], "MARKET_HEALTH_PENDING"),
            ("liquidity_usd", None, "MARKET_HEALTH_PENDING"),
            ("sellable", False, "SELLABILITY_PENDING"),
            ("prospective_admission_state", "PENDING", "PROVENANCE_PENDING"),
            ("prospective_admission_evidence_ref", "", "PROVENANCE_PENDING"),
        ]
        for field, value, expected in cases:
            with self.subTest(field=field):
                row = activity()
                row[field] = value
                self.assertEqual(self.receipt(row)["state"], expected)

    def test_market_health_not_inferred_from_liquidity(self):
        row = activity()
        del row["market_data_health"]
        self.assertEqual(self.receipt(row)["state"], "MARKET_HEALTH_PENDING")

    def test_seeded_reject(self):
        for kind in o.REJECT_KINDS:
            row = activity()
            row["kind"] = kind
            self.assertEqual(self.receipt(row)["state"], "PROVENANCE_REJECT")

    def test_locator_and_timestamp_fail_closed(self):
        row = activity()
        row["transaction_hash"] = "0x123"
        self.assertEqual(self.receipt(row)["state"], "PROVENANCE_PENDING")
        row = activity()
        row["observed_at_utc"] = "2026-09-22"
        self.assertEqual(self.receipt(row)["state"], "TIMESTAMP_MISSING")
        self.assertIsNone(o.iso_exact(True))
        self.assertIsNone(o.iso_exact(float("nan")))
        self.assertIsNotNone(o.iso_exact("2026-09-22T12:00Z"))

    def test_historical_not_backfilled(self):
        row = activity()
        row["observed_at_utc"] = "2020-01-01T12:00:00Z"
        row["source_event_timestamp_utc"] = "2020-01-01T11:59:58Z"
        del row["prospective_admission_state"]
        del row["prospective_admission_evidence_ref"]
        self.assertEqual(self.receipt(row)["state"], "PROVENANCE_PENDING")


if __name__ == "__main__":
    unittest.main()
