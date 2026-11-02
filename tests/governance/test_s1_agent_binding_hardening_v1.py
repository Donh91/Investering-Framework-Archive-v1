"""Checks for strict timestamp and reproducible request binding."""
import unittest
from tests.governance.test_s1_agent_handoff_receipts_v1 import chain
from scripts.governance.s1_agent_handoff_receipts_v1 import validate_chain, ReceiptError


class RequestBindingHardeningTests(unittest.TestCase):
    def test_repeat_same_binding_same_digest(self):
        first = validate_chain(chain())
        second = validate_chain(chain())
        self.assertEqual(first["request_binding_sha256"], second["request_binding_sha256"])
        self.assertEqual(len(first["request_binding_sha256"]), 64)

    def test_different_request_changes_digest(self):
        a = chain()
        b = chain()
        for event in b:
            event["request_id"] = "req-20261102-002"
        self.assertNotEqual(
            validate_chain(a)["request_binding_sha256"],
            validate_chain(b)["request_binding_sha256"])

    def test_short_request_id_rejected(self):
        entries = chain()
        for event in entries:
            event["request_id"] = "x"
        with self.assertRaises(ReceiptError):
            validate_chain(entries)

    def test_typed_source_fingerprint(self):
        entries = chain()
        for event in entries:
            event["source_fingerprint"] = "short"
        with self.assertRaises(ReceiptError):
            validate_chain(entries)

    def test_no_space_in_utc_timestamp(self):
        entries = chain()
        entries[0]["at_utc"] = "2026-11-02 10:00:00Z"
        with self.assertRaises(ReceiptError):
            validate_chain(entries)


if __name__ == "__main__":
    unittest.main()
