import unittest
from datetime import datetime, timezone
from scripts.daily_capture.c5_context import fred_from_payload, session_close, window_aggregates, valid_seal


class C5ContextTests(unittest.TestCase):
    def test_fred_current_and_gap_and_late(self):
        payload = b"DATE,VIXCLS,VXVCLS\n2026-11-23,18,20\n2026-11-24,19,20\n2026-11-25,21,20\n2026-11-26,.,.\n2026-11-27,22,20\n"
        capture = "2026-11-28T08:00:00Z"
        cutoff = "2026-11-28T08:00:01Z"
        result = fred_from_payload(payload, "gh-123-1", capture, cutoff)
        self.assertEqual(result["status"], "AVAILABLE")
        self.assertEqual(result["term_structure_class"], "INVERTED")
        self.assertEqual(result["vix_3m_ratio"], 1.1)
        self.assertFalse(result["scoring_allowed"])
        self.assertTrue(valid_seal(result))
        self.assertNotIn("rows", result)
        self.assertEqual(fred_from_payload(payload.replace(b"22,20", b".,20"), "gh-123-1", capture, cutoff)["reason"], "FRED_MATCHED_SESSION_GAP")
        self.assertEqual(fred_from_payload(payload, "gh-123-1", cutoff, capture)["status"], "UNAVAILABLE")
        self.assertEqual(fred_from_payload(payload, "gh-123-1", capture, cutoff, "CONSERVATIVE_RELEASE_LAG")["scoring_allowed"], False)

    def test_dst(self):
        from datetime import date
        self.assertEqual(session_close(date(2026, 11, 27)).hour, 21)
        self.assertEqual(session_close(date(2026, 7, 10)).hour, 20)

    def test_liquidation_dedup_and_missing_coverage(self):
        end = datetime(2026, 11, 28, 12, tzinfo=timezone.utc)
        event = {"event_id":"one", "event_timestamp_ms":int(end.timestamp()*1000), "inst_id":"BTC-USDT-SWAP",
                 "pos_side":"long","notional_usd":3000,"notional_method":"OKX_CONTRACT_UNIT_NORMALIZATION_v1","source_payload_sha256":"a"*64}
        captures = [{"observed_at_utc":end.isoformat(), "lane1_liquidations":{"BTC":{"status":"PASS"}}}]
        result = window_aggregates([event, dict(event)], captures, end, "BTC", 24, 28)
        self.assertEqual(result["long_notional_usd"],3000)
        self.assertEqual(result["pressure_class"],"UNAVAILABLE")
        self.assertEqual(window_aggregates([event], [], end, "BTC", 24, 28)["status"],"UNAVAILABLE")
        with self.assertRaises(ValueError):
            window_aggregates([event, dict(event,notional_usd=5000)], captures, end, "BTC", 24, 28)
