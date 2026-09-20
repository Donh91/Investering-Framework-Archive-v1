from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.api_agent import meme_alpha_fomo_robinhood_observer as o

W1 = "0x0a6ebed0155edb4b21d92ad02897a626cd90119e"
W2 = "0x8f62a08537cede87d511aca6436274ab4ca080a3"
TOKEN = "0x71e52e7cd3c13b278cd05e80c9a63b843cbed960"


class ObserverTests(unittest.TestCase):
    def member(self, addr: str, handle: str) -> dict:
        return {"handle": handle, "evm_address": addr}

    def test_seeded_watch_style_overlap_is_rejected_and_never_counts(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cohort = root / "cohort.json"
            activity = root / "activity.json"
            output = root / "out.json"
            cohort.write_text(json.dumps({"members": [self.member(W1, "unipcs"), self.member(W2, "DumbCrayonEater")]}))
            activity.write_text(json.dumps({"rows": [
                {"wallet_address": W1, "contract": TOKEN, "side": "buy", "kind": "seed", "observed_at_utc": "2026-09-20T12:00:01Z"},
                {"wallet_address": W2, "contract": TOKEN, "side": "buy", "kind": "seeded", "observed_at_utc": "2026-09-20T12:00:02Z"},
            ]}))
            result = o.run(activity, cohort, output, retrieved_at="2026-09-20T12:00:05Z")
            self.assertEqual([r["state"] for r in result["receipts"]], ["PROVENANCE_REJECT", "PROVENANCE_REJECT"])
            self.assertEqual(result["promotion_counter_increment"], 0)
            self.assertTrue(all(not r["promotion_counter_eligible"] for r in result["receipts"]))

    def test_self_initiated_buy_fails_closed_until_entity_market_sellability(self) -> None:
        row = {
            "wallet_address": W1, "contract": TOKEN, "side": "buy", "kind": "swap",
            "self_initiated": True, "observed_at_utc": "2026-09-20T12:01:00Z"
        }
        member = self.member(W1, "unipcs")
        self.assertEqual(o.build_receipt(row, member, retrieved_at="2026-09-20T12:01:01Z")["state"], "ENTITY_PENDING")
        row["economic_entity_id"] = "entity-A"
        self.assertEqual(o.build_receipt(row, member, retrieved_at="2026-09-20T12:01:01Z")["state"], "MARKET_HEALTH_PENDING")
        row["liquidity_usd"] = 25000
        self.assertEqual(o.build_receipt(row, member, retrieved_at="2026-09-20T12:01:01Z")["state"], "SELLABILITY_PENDING")
        row["sellable"] = True
        self.assertEqual(o.build_receipt(row, member, retrieved_at="2026-09-20T12:01:01Z")["state"], "PROVENANCE_PASS")

    def test_date_only_or_missing_timestamp_cannot_create_lead_time(self) -> None:
        row = {"wallet_address": W1, "contract": TOKEN, "side": "buy", "kind": "swap", "self_initiated": True, "champion_first_seen_at": "2026-09-20T12:30:00Z"}
        receipt = o.build_receipt(row, self.member(W1, "unipcs"), retrieved_at="2026-09-20T12:31:00Z")
        self.assertIsNone(receipt["observed_at_utc_exact"])
        self.assertEqual(receipt["lead_time_minutes_or_NOT_COMPARABLE"], "NOT_COMPARABLE")

    def test_non_cohort_wallet_is_not_materialized(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cohort = root / "cohort.json"; activity = root / "activity.json"; output = root / "out.json"
            cohort.write_text(json.dumps({"members": [self.member(W1, "unipcs")]}))
            activity.write_text(json.dumps({"rows": [{"wallet_address": "0x" + "1"*40, "contract": TOKEN, "side": "buy", "kind": "swap", "observed_at_utc": "2026-09-20T12:00:00Z"}]}))
            result = o.run(activity, cohort, output, retrieved_at="2026-09-20T12:00:05Z")
            self.assertEqual(result["receipts"], [])


if __name__ == "__main__":
    unittest.main()
