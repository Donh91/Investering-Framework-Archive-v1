"""Adversarial negative controls for public receipt shape."""
import unittest

from public_receipt import CONTRACT, PublicReceiptError, dumps_receipt, validate_receipt


GOOD = {
    "contract": CONTRACT,
    "request_alias": "request_83de9175be2981f210fe44f3",
    "disclosure_state": "METADATA_ONLY",
    "evidence_alias": "evidence_73bb4ed075bd913fcab6e128",
    "research_lane": "PRIVATE_SOURCE_HEALTH",
}


class PublicReceiptTests(unittest.TestCase):
    def test_positive_exact_shape(self):
        self.assertEqual(validate_receipt(GOOD)["research_lane"], "PRIVATE_SOURCE_HEALTH")
        self.assertIn('"contract"', dumps_receipt(GOOD))

    def test_reject_raw_market_value(self):
        for k, v in (("price", 80000), ("win_rate", .88), ("raw_sha256", "d" * 64),
                     ("source_timestamp", "2026-10-30T12:00:00Z"), ("comment", "secret"),
                     ("aggregate_count", 12), ("relative_outperformance", True)):
            with self.subTest(key=k), self.assertRaises(PublicReceiptError):
                validate_receipt({**GOOD, k: v})

    def test_reject_nonopaque_identifiers(self):
        for alias in ("btc_price_80000", "a", "2026-w43", "UP", "x" * 81,
                      "test/../../secrets", "evidence%20btc", "ea31f7-funding:0.02"):
            with self.subTest(alias=alias), self.assertRaises(PublicReceiptError):
                validate_receipt({**GOOD, "evidence_alias": alias})

    def test_reject_round3_or_scoring_promotion(self):
        for lane in ("ROUND3_SCORING", "PRIVATE_HYPOTHESIS", "LIVE_TRADING", "PUBLIC_ONLY\nprice=80000"):
            with self.subTest(lane=lane), self.assertRaises(PublicReceiptError):
                validate_receipt({**GOOD, "research_lane": lane})

    def test_reject_one_bit_verdict_or_confidence(self):
        for status in ("BETTER_THAN_BASELINE", "APPROVED", "EDGE_CONFIRMED", "HELD", "REJECTED"):
            with self.subTest(status=status), self.assertRaises(PublicReceiptError):
                validate_receipt({**GOOD, "disclosure_state": status})

    def test_reject_missing_field_and_non_string(self):
        without = dict(GOOD)
        without.pop("evidence_alias")
        with self.assertRaises(PublicReceiptError):
            validate_receipt(without)
        with self.assertRaises(PublicReceiptError):
            validate_receipt({**GOOD, "request_alias": 123456})
        with self.assertRaises(PublicReceiptError):
            validate_receipt(None)


if __name__ == "__main__":
    unittest.main()
