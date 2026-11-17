import unittest
from scripts.research.maeve_opportunity_match_v1 import match_entries

def row(i, day, action="NONE", **kw):
    base = dict(id=i, asset="BTC", timeframe="1h", era="synthetic-v1",
                decision_at=f"2025-01-{day:02d}T12:00:00Z",
                features_available_at=f"2025-01-{day:02d}T12:00:00Z",
                eligibility="ELIGIBLE", ledger_coverage="COMPLETE", action=action)
    base.update(kw)
    return base

class MatchEntriesTest(unittest.TestCase):
    def test_same_era_prior_only_and_order_invariant(self):
        rows = [row("a", 2), row("e", 5, "ENTRY"), row("b", 6),
                row("other", 4, era="synthetic-v2")]
        result = match_entries(rows)
        self.assertEqual(result["matched"], [{"entry_id":"e","control_id":"a"}])
        self.assertEqual(result, match_entries(list(reversed(rows))))
    def test_unknown_incomplete_future_and_active_actions_are_not_none(self):
        rows = [row("unknown", 1, eligibility="UNKNOWN"),
                row("incomplete", 2, ledger_coverage="INCOMPLETE"),
                row("futurefeature", 3, features_available_at="2025-01-05T12:00:00Z"),
                row("dca", 4, "DCA"), row("e", 5, "ENTRY"), row("later", 6)]
        result = match_entries(rows)
        self.assertEqual(result["matched"], [])
        self.assertEqual(result["unmatched_entry_ids"], ["e"])
        self.assertEqual(result["excluded_rows"], 4)
    def test_future_append_does_not_change_existing_match(self):
        rows = [row("a", 1), row("e", 2, "ENTRY")]
        self.assertEqual(match_entries(rows)["matched"],
                         match_entries(rows + [row("later", 3)])["matched"])
    def test_duplicate_and_outcome_rejected(self):
        with self.assertRaises(ValueError):
            match_entries([row("a", 1), row("b", 1)])
        with self.assertRaises(ValueError):
            match_entries([row("a", 1, future_pnl=1)])
    def test_window_and_reuse_explicit(self):
        rows = [row("a", 1), row("e", 2, "ENTRY"), row("f", 3, "ENTRY")]
        self.assertEqual(match_entries(rows)["control_reuse"], {"a": 2})
        self.assertEqual(match_entries(rows, max_prior_days=1)["unmatched_entry_ids"], ["f"])
    def test_no_cross_asset_or_hour(self):
        rows = [row("a", 1, asset="ETH"),
                row("b", 2, decision_at="2025-01-02T13:00:00Z"),
                row("e", 3, "ENTRY")]
        self.assertEqual(match_entries(rows)["matched"], [])
