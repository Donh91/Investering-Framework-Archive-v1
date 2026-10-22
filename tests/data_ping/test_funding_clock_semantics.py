import unittest
from pathlib import Path

from scripts.data_ping.native_handlekompas import evidence_snapshot


class FundingClockSemanticsTest(unittest.TestCase):
    def packet(self, *, settlement=1791849600000, captured="2026-10-12T22:57:02Z", capture_status="PASS"):
        commit = "a" * 40
        path = "03_DAILY_CAPTURE_LOGS/captures/original.json"
        health = {"status": "PASS", "target_path": "03_DAILY_CAPTURE_LOGS/captures/original.json",
                  "freshness": {"retrieval_freshness": {"status": capture_status, "timestamp": captured}},
                  "provenance": {"target": {"exact_commit_sha": commit, "exact_path": path,
                                            "git_blob_sha": "b" * 40}}}
        return {
            "packet_generated_at_utc": "2026-10-12T23:22:45Z",
            "source_snapshot": {"exact_commit_sha": commit},
            "source_health": {"derivatives": {"status": "PASS"}, "live_anchor": health},
            "normalized_state": {"derivatives": {"live_anchor": {
                symbol: {"funding": {"funding_rate": rate, "funding_time": settlement}}
                for symbol, rate in (("BTC-USDT-SWAP", 0.00002), ("ETH-USDT-SWAP", 0.00003))
            }}},
        }

    def funding(self, packet):
        rows = evidence_snapshot(packet, Path("original-packet.json"))["selected_features"]
        return {row["feature_id"]: row for row in rows if row["feature_id"] in ("btc_funding", "eth_funding")}

    def test_future_settlement_is_distinct_from_original_capture(self):
        for row in self.funding(self.packet()).values():
            self.assertIsNone(row["observed_at"])
            self.assertEqual(row["retrieved_at"], "2026-10-12T22:57:02Z")
            self.assertEqual(row["settlement_at_utc"], "2026-10-13T00:00:00Z")
            self.assertEqual(row["quote_clock_status"], "CAPTURE_ONLY_PROVIDER_FIRST_KNOWN_UNKNOWN")
            self.assertEqual(row["eligibility"], "ELIGIBLE_PRESENT")
        self.assertEqual(self.funding(self.packet())["btc_funding"]["value"], 0.00002)

    def test_missing_capture_cannot_inherit_settlement_or_packet_time(self):
        for row in self.funding(self.packet(captured=None)).values():
            self.assertIsNone(row["observed_at"])
            self.assertIsNone(row["retrieved_at"])
            self.assertEqual(row["quote_clock_status"], "UNKNOWN_NOT_PIT_ADMITTED")

    def test_after_packet_or_unverified_capture_is_not_admitted(self):
        for packet in (self.packet(captured="2026-10-12T23:23:00Z"),
                       self.packet(capture_status="FUTURE"),
                       self.packet(captured="2026-10-12T22:57:02+02:00"),
                       self.packet(captured="not-a-time")):
            for row in self.funding(packet).values():
                self.assertIsNone(row["observed_at"])
                self.assertIsNone(row["retrieved_at"])
                self.assertEqual(row["quote_clock_status"], "UNKNOWN_NOT_PIT_ADMITTED")

    def test_wrong_capture_binding_is_unknown(self):
        packet = self.packet()
        packet["source_health"]["live_anchor"]["provenance"]["target"]["exact_commit_sha"] = "c" * 40
        for row in self.funding(packet).values():
            self.assertIsNone(row["retrieved_at"])
            self.assertEqual(row["quote_clock_status"], "UNKNOWN_NOT_PIT_ADMITTED")

    def test_settlement_must_be_millisecond_epoch(self):
        for settlement in (1791849600, "1791849600", "bogus", None):
            for row in self.funding(self.packet(settlement=settlement)).values():
                self.assertIsNone(row["settlement_at_utc"])
                self.assertIsNone(row["observed_at"])

    def test_prior_settlement_still_does_not_prove_quote_observation(self):
        for row in self.funding(self.packet(settlement=1791810000000)).values():
            self.assertIsNone(row["observed_at"])
            self.assertEqual(row["retrieved_at"], "2026-10-12T22:57:02Z")
            self.assertEqual(row["quote_clock_status"], "CAPTURE_ONLY_PROVIDER_FIRST_KNOWN_UNKNOWN")


if __name__ == "__main__":
    unittest.main()
