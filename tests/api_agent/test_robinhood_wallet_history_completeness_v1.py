from __future__ import annotations

import unittest

from scripts.api_agent.robinhood_wallet_history_completeness_v1 import (
    audit_robinhood_wallet_history,
)


WALLET = "0x" + "aa" * 20


def fake_fetcher(pages):
    calls = []
    def fetch(endpoint_path, *, api_key=None, query=None, allow_public_fallback=True):
        q = dict(query or {})
        calls.append((endpoint_path, q))
        key = (endpoint_path.split("/")[-1], tuple(sorted(q.items())))
        payload = pages[key]
        return payload, {
            "status": "PASS",
            "transport": "PUBLIC_CHAIN_FALLBACK",
            "authenticated": False,
            "fallback_used": True,
        }
    fetch.calls = calls
    return fetch


class RobinhoodWalletHistoryCompletenessTests(unittest.TestCase):
    def test_follows_next_page_params_and_completes_at_window_start(self):
        pages = {}
        for surface in ("transactions", "token-transfers"):
            pages[(surface, ())] = {
                "items": [
                    {"hash":"0x1","timestamp":"2026-10-06T10:00:00Z"},
                    {"hash":"0x2","timestamp":"2026-10-05T10:00:00Z"},
                ],
                "next_page_params":{"block_number":10,"index":2,"items_count":50},
            }
            pages[(surface, (("block_number",10),("index",2),("items_count",50)))] = {
                "items":[
                    {"hash":"0x3","timestamp":"2026-09-29T10:00:00Z"},
                ],
                "next_page_params":{"block_number":5,"index":1,"items_count":50},
            }
        fetch=fake_fetcher(pages)
        r=audit_robinhood_wallet_history(
            WALLET,
            history_start_utc="2026-10-01T00:00:00Z",
            cutoff_utc="2026-10-06T12:00:00Z",
            max_pages_per_endpoint=5,
            fetcher=fetch,
        )
        self.assertEqual(r["coverage_state"],"COMPLETE_WINDOW")
        self.assertTrue(r["negative_activity_claim_admissible"])
        self.assertEqual(r["surfaces"]["transactions"]["completion_basis"],"REACHED_WINDOW_START")
        self.assertEqual(r["surfaces"]["transactions"]["pages_fetched"],2)
        self.assertIn(("block_number",10), tuple(sorted(fetch.calls[1][1].items())))

    def test_exhausted_empty_history_is_complete_not_truncated(self):
        pages={}
        for surface in ("transactions","token-transfers"):
            pages[(surface,())]={"items":[],"next_page_params":None}
        r=audit_robinhood_wallet_history(
            WALLET,history_start_utc="2026-09-01T00:00:00Z",
            cutoff_utc="2026-10-01T00:00:00Z",fetcher=fake_fetcher(pages)
        )
        self.assertEqual(r["coverage_state"],"COMPLETE_WINDOW")
        self.assertTrue(r["negative_activity_claim_admissible"])
        self.assertEqual(r["surfaces"]["transactions"]["completion_basis"],"PAGINATION_EXHAUSTED")

    def test_page_cap_is_unknown_not_no_activity(self):
        pages={}
        for surface in ("transactions","token-transfers"):
            pages[(surface,())]={
                "items":[{"hash":"0x1","timestamp":"2026-10-06T10:00:00Z"}],
                "next_page_params":{"block_number":10,"index":1}
            }
        r=audit_robinhood_wallet_history(
            WALLET,history_start_utc="2026-09-01T00:00:00Z",
            cutoff_utc="2026-10-06T12:00:00Z",max_pages_per_endpoint=1,
            fetcher=fake_fetcher(pages)
        )
        self.assertEqual(r["coverage_state"],"TRUNCATED_PAGE_CAP")
        self.assertFalse(r["negative_activity_claim_admissible"])
        self.assertEqual(r["downstream_incomplete_state"],"UNKNOWN")

    def test_missing_timestamp_fails_closed(self):
        pages={}
        for surface in ("transactions","token-transfers"):
            pages[(surface,())]={"items":[{"hash":"0x1"}],"next_page_params":None}
        r=audit_robinhood_wallet_history(
            WALLET,history_start_utc="2026-09-01T00:00:00Z",
            cutoff_utc="2026-10-01T00:00:00Z",fetcher=fake_fetcher(pages)
        )
        self.assertEqual(r["coverage_state"],"DATA_INSUFFICIENT")
        self.assertFalse(r["negative_activity_claim_admissible"])

    def test_repeated_cursor_is_data_conflict(self):
        pages={}
        for surface in ("transactions","token-transfers"):
            pages[(surface,())]={
                "items":[{"hash":"0x1","timestamp":"2026-10-06T10:00:00Z"}],
                "next_page_params":{"block_number":10,"index":1}
            }
            pages[(surface,(("block_number",10),("index",1)))]={
                "items":[{"hash":"0x2","timestamp":"2026-10-05T10:00:00Z"}],
                "next_page_params":{"block_number":10,"index":1}
            }
        r=audit_robinhood_wallet_history(
            WALLET,history_start_utc="2026-09-01T00:00:00Z",
            cutoff_utc="2026-10-06T12:00:00Z",max_pages_per_endpoint=5,
            fetcher=fake_fetcher(pages)
        )
        self.assertEqual(r["coverage_state"],"DATA_CONFLICT")

    def test_pagination_time_reversal_fails_closed(self):
        pages={}
        for surface in ("transactions","token-transfers"):
            pages[(surface,())]={
                "items":[{"hash":"0x1","timestamp":"2026-10-05T10:00:00Z"}],
                "next_page_params":{"block_number":10,"index":1}
            }
            pages[(surface,(("block_number",10),("index",1)))]={
                "items":[{"hash":"0x2","timestamp":"2026-10-06T10:00:00Z"}],
                "next_page_params":None
            }
        r=audit_robinhood_wallet_history(
            WALLET,history_start_utc="2026-09-01T00:00:00Z",
            cutoff_utc="2026-10-06T12:00:00Z",fetcher=fake_fetcher(pages)
        )
        self.assertEqual(r["coverage_state"],"DATA_CONFLICT")

    def test_source_failure_is_not_negative_evidence(self):
        def fail(*args,**kwargs):
            raise RuntimeError("boom")
        r=audit_robinhood_wallet_history(
            WALLET,history_start_utc="2026-09-01T00:00:00Z",
            cutoff_utc="2026-10-01T00:00:00Z",fetcher=fail
        )
        self.assertEqual(r["coverage_state"],"SOURCE_ERROR")
        self.assertFalse(r["negative_activity_claim_admissible"])


if __name__=="__main__":
    unittest.main()
