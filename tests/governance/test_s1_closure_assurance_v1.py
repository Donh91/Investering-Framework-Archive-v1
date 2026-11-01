"""Adversarial contract tests. No GitHub, provider or production writes."""
import copy
import json
import unittest
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schemas" / "S1_CLOSURE_ASSURANCE_V1.schema.json"

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:
    Draft202012Validator = None
    FormatChecker = None


def sample():
    return {
        "contract": "S1_CLOSURE_ASSURANCE_V1",
        "case_id": "Archive#1156",
        "case_kind": "INCIDENT",
        "original_owner": "existing S1",
        "original_url": "https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156",
        "status": "ACTIONABLE",
        "priority": "P0",
        "evidence_fingerprint": "source-sha-12345678",
        "last_material_progress_utc": "2026-11-01T20:00:00Z",
        "next_action": "Reproduce source fault with original receipts",
        "acceptance_criterion": "Exact-head CI and natural source readback",
        "source_refs": ["main@abc123"],
        "authority": "OWNER_GOVERNED",
    }


@unittest.skipUnless(Draft202012Validator is not None, "jsonschema dependency unavailable")
class ClosureAssuranceSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text()), format_checker=FormatChecker())
        cls.validator.check_schema(cls.validator.schema)

    def valid(self, receipt):
        return not list(self.validator.iter_errors(receipt))

    def test_actionable_valid(self):
        self.assertTrue(self.valid(sample()))

    def test_blocked_requires_trigger(self):
        item = sample()
        item["status"] = "BLOCKED_WITH_TRIGGER"
        self.assertFalse(self.valid(item))
        item["blocker"] = {"type": "EXTERNAL", "reactivation_trigger": "Vault credential becomes authorized", "trigger_owner": "Vault owner"}
        self.assertTrue(self.valid(item))

    def test_closure_requires_proof(self):
        item = sample()
        item["status"] = "CLOSED_VERIFIED"
        self.assertFalse(self.valid(item))
        item["closure_proof"] = {"disposition": "MERGED_AND_VERIFIED", "proof_refs": ["main@123"], "verified_at_utc": "2026-11-01T21:00:00Z"}
        self.assertTrue(self.valid(item))

    def test_strategist_cannot_claim_merge_authority(self):
        item = sample()
        item["case_kind"] = "STRATEGIST_PROPOSAL"
        item["strategy"] = {"hypothesis": "Improves original source coverage", "falsification": "Compare against frozen control", "expected_user_value": "More complete source recall"}
        self.assertFalse(self.valid(item))
        item["authority"] = "ADVISORY_ONLY"
        self.assertTrue(self.valid(item))

    def test_missing_owner_rejected(self):
        item = sample()
        del item["original_owner"]
        self.assertFalse(self.valid(item))

    def test_unknown_status_rejected(self):
        item = sample()
        item["status"] = "HOLD_FOREVER"
        self.assertFalse(self.valid(item))

    def test_unexpected_privileged_field_rejected(self):
        item = sample()
        item["auto_merge"] = True
        self.assertFalse(self.valid(item))

    def test_stalled_requires_distinct_reactivation(self):
        item = sample()
        item["status"] = "PROCESS_STALLED"
        self.assertFalse(self.valid(item))


if __name__ == "__main__":
    unittest.main()
