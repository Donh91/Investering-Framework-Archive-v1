import json
import unittest

from scripts.api_agent import meme_alpha_eth_blockscout_provenance as p


TOKEN = "0x" + "a" * 40
OTHER = "0x" + "b" * 40
CREATOR = "0x" + "c" * 40
TX = "0x" + "d" * 64


def getter_for(address=None, *, verified=True, is_contract=True, is_scam=False, creator=CREATOR, tx=TX, returned_tx=TX, tx_status="ok", fail=False):
    address = address or TOKEN

    def getter(url, timeout=20):
        if fail:
            raise OSError("source unavailable")
        if "/addresses/" in url:
            return 200, {
                "hash": address,
                "is_contract": is_contract,
                "is_verified": verified,
                "is_scam": is_scam,
                "creator_address_hash": creator,
                "creation_transaction_hash": tx,
            }
        if "/transactions/" in url:
            return 200, {"hash": returned_tx, "status": tx_status}
        raise AssertionError(url)

    return getter


class EthBlockscoutProvenanceTests(unittest.TestCase):
    def produce(self, **kwargs):
        getter = kwargs.pop("getter", getter_for())
        return p.produce(f"eth:{TOKEN}", TOKEN, frozen_payload_ref="runtime/moonshot/evidence/frozen.json", getter=getter, api_key="fixture-secret", **kwargs)

    def test_exact_good_fixture_produces_one_p_receipt(self):
        evidence, frozen = self.produce()
        self.assertEqual(evidence["status"], "PASS")
        self.assertEqual(len(evidence["receipts"]), 1)
        receipt = evidence["receipts"][0]
        self.assertEqual(receipt["family"], "P")
        self.assertEqual(receipt["source_contract"], p.SOURCE_CONTRACT)
        self.assertTrue(receipt["deterministic"])
        self.assertFalse(receipt["llm_generated"])
        self.assertEqual(frozen["returned_address"], TOKEN)
        self.assertEqual(frozen["creation_status"], "success")

    def test_wrong_returned_ca_produces_no_receipt(self):
        evidence, _ = self.produce(getter=getter_for(address=OTHER))
        self.assertEqual(evidence["status"], "UNKNOWN")
        self.assertEqual(evidence["receipts"], [])

    def test_wrong_candidate_id_fails_closed_before_source_call(self):
        def forbidden(*args, **kwargs):
            raise AssertionError("source must not be called")
        evidence, frozen = p.produce("eth:wrong", TOKEN, frozen_payload_ref="frozen.json", getter=forbidden)
        self.assertEqual(evidence["status"], "UNKNOWN")
        self.assertEqual(evidence["receipts"], [])
        self.assertEqual(frozen["source_health"]["reason"], "IDENTITY_BINDING_INVALID")

    def test_unverified_contract_produces_no_receipt(self):
        evidence, _ = self.produce(getter=getter_for(verified=False))
        self.assertEqual(evidence["receipts"], [])

    def test_missing_or_failed_creation_transaction_produces_no_receipt(self):
        for getter in (getter_for(tx=None), getter_for(tx_status="error"), getter_for(returned_tx="0x" + "e" * 64)):
            with self.subTest(getter=getter):
                evidence, _ = self.produce(getter=getter)
                self.assertEqual(evidence["receipts"], [])

    def test_missing_creator_produces_no_receipt(self):
        evidence, _ = self.produce(getter=getter_for(creator=None))
        self.assertEqual(evidence["receipts"], [])

    def test_scam_flag_produces_no_receipt(self):
        evidence, _ = self.produce(getter=getter_for(is_scam=True))
        self.assertEqual(evidence["receipts"], [])

    def test_source_error_is_degraded_and_produces_no_receipt(self):
        evidence, frozen = self.produce(getter=getter_for(fail=True))
        self.assertEqual(evidence["status"], "DEGRADED")
        self.assertEqual(evidence["receipts"], [])
        self.assertEqual(frozen["source_health"]["status"], "DEGRADED")

    def test_credentials_are_never_persisted(self):
        evidence, frozen = self.produce()
        serialized = json.dumps({"evidence": evidence, "frozen": frozen}, sort_keys=True)
        self.assertNotIn("fixture-secret", serialized)
        self.assertNotIn("apikey", serialized.lower())

    def test_authority_is_alert_gate_only(self):
        evidence, _ = self.produce()
        self.assertEqual(evidence["authority"], "alert_gate_only")
        self.assertFalse(evidence["portfolio_action"])
        self.assertFalse(evidence["automatic_trading"])


if __name__ == "__main__":
    unittest.main()
