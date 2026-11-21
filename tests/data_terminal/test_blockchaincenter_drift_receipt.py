"""Schema-drift canary: BlockchainCenter parser failures leave a machine-readable receipt."""
import hashlib
import json
import pathlib
import tempfile
import unittest

from tests.data_terminal.test_top100_breadth_owner_collector import (
    MODULE, blockchaincenter_payload, coinmarketcap_payload, payload,
)

RETRIEVAL = "2026-08-25T12:00:00Z"


class BlockchainCenterDriftReceiptTests(unittest.TestCase):
    def run_with(self, rotation_payload, **extra):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        out = pathlib.Path(tmp.name)
        owner = MODULE.run(payload(), out, RETRIEVAL, rotation_payload=rotation_payload,
                           coinmarketcap_payload=coinmarketcap_payload(), **extra)
        return out, owner

    def assert_receipt(self, raw, expected_code):
        out, owner = self.run_with(raw)
        self.assertEqual(owner["rotation_context"]["failure_state"], expected_code)
        receipt = json.loads((out / MODULE.BLOCKCHAINCENTER_DRIFT_RECEIPT).read_text())
        self.assertEqual(receipt["contract"], "BLOCKCHAINCENTER_SCHEMA_DRIFT_RECEIPT_v1")
        self.assertEqual(receipt["source"], "BlockchainCenter")
        self.assertEqual(receipt["error_code"], expected_code)
        self.assertEqual(receipt["raw_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(receipt["retrieved_at_utc"], RETRIEVAL)
        self.assertEqual(receipt["parser_contracts_tried"], list(MODULE.BLOCKCHAINCENTER_PARSER_CONTRACTS))
        top = json.loads((out / "receipt.json").read_text())
        self.assertEqual(top["rotation_context_drift_receipt"], MODULE.BLOCKCHAINCENTER_DRIFT_RECEIPT)
        manifest = json.loads((out / "artifact_manifest.json").read_text())
        self.assertIn(MODULE.BLOCKCHAINCENTER_DRIFT_RECEIPT, [row["path"] for row in manifest["members"]])
        self.assertEqual(MODULE.verify(out)["status"], "PASS")
        return out

    def test_schema_drift_writes_receipt(self):
        self.assert_receipt(b"<html><body>no props</body></html>", "BLOCKCHAINCENTER_SCHEMA_DRIFT")

    def test_reconciliation_fail_writes_receipt(self):
        self.assert_receipt(blockchaincenter_payload({"90": 99}), "BLOCKCHAINCENTER_RECONCILIATION_FAIL")

    def test_healthy_and_network_failures_write_no_receipt_and_rerun_clears_stale(self):
        out = self.assert_receipt(b"<html></html>", "BLOCKCHAINCENTER_SCHEMA_DRIFT")
        MODULE.run(payload(), out, RETRIEVAL, rotation_payload=blockchaincenter_payload(),
                   coinmarketcap_payload=coinmarketcap_payload())
        self.assertFalse((out / MODULE.BLOCKCHAINCENTER_DRIFT_RECEIPT).exists())
        self.assertNotIn("rotation_context_drift_receipt", json.loads((out / "receipt.json").read_text()))
        out2, owner = self.run_with(None, rotation_error={"failure_state": "SOURCE_HTTP_ERROR", "message": "x"})
        self.assertEqual(owner["rotation_context"]["failure_state"], "SOURCE_HTTP_ERROR")
        self.assertFalse((out2 / MODULE.BLOCKCHAINCENTER_DRIFT_RECEIPT).exists())


if __name__ == "__main__":
    unittest.main()
