"""Synthetic positives/negative controls for research-only public forecast intake."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "scripts/research/public_forecast_intake_gate_v1.py"
spec = importlib.util.spec_from_file_location("public_forecast_intake_gate_v1", PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def valid():
    return {
        "case_id": "synthetic-1", "authority": "RESEARCH_ONLY",
        "source_uri": "https://example.org/claim",
        "claim_type": "conditional", "asset": "BTC",
        "source_issued_at_utc": "2026-11-16T08:00:00Z",
        "first_machine_observed_at_utc": "2026-11-16T08:01:00Z",
        "frozen_at_utc": "2026-11-16T08:02:00Z",
        "outcome_window_start_utc": "2026-11-16T08:03:00Z",
        "source_content_sha256": "a" * 64,
        "original_source_receipt_ref": "sha256:fake-self-declared-does-not-prove-first-known"
    }

class PublicForecastGateTests(unittest.TestCase):
    def test_syntactically_complete_is_never_scientific_proof(self):
        x = mod.audit_case(valid())
        self.assertEqual(x["status"], "STRUCTURAL_ONLY_INDEPENDENT_PROOF_UNVERIFIED")
        self.assertFalse(x["scientific_admitted"])
        self.assertFalse(x["scorable"])

    def test_missing_first_observation_censors(self):
        c = valid()
        c["first_machine_observed_at_utc"] = None
        self.assertEqual(mod.audit_case(c)["status"], "CONTEXT_ONLY_MISSING_PROOF")

    def test_after_outcome_freeze_rejected(self):
        c = valid()
        c["frozen_at_utc"] = "2026-11-16T08:04:00Z"
        self.assertIn("NONCAUSAL_CLOCK_ORDER", mod.audit_case(c)["problems"])

    def test_seen_before_original_issue_rejected(self):
        c = valid()
        c["first_machine_observed_at_utc"] = "2026-11-16T07:59:00Z"
        self.assertIn("NONCAUSAL_CLOCK_ORDER", mod.audit_case(c)["problems"])

    def test_wrong_timezone_rejected(self):
        c = valid()
        c["source_issued_at_utc"] = "2026-11-16T10:00:00+02:00"
        self.assertEqual(mod.audit_case(c)["status"], "REJECTED_SCHEMA")

    def test_insecure_uri_rejected(self):
        c = valid()
        c["source_uri"] = "http://example.org/claim"
        self.assertIn("SOURCE_URI_NOT_HTTPS", mod.audit_case(c)["problems"])

    def test_invalid_digest_rejected(self):
        c = valid()
        c["source_content_sha256"] = "a"
        self.assertIn("MALFORMED_SOURCE_HASH", mod.audit_case(c)["problems"])

    def test_authority_escalation_rejected(self):
        c = valid()
        c["authority"] = "OFFICIAL_COMPASS"
        self.assertIn("AUTHORITY_NOT_RESEARCH_ONLY", mod.audit_case(c)["problems"])

    def test_duplicate_case_rejected(self):
        c = valid()
        with self.assertRaisesRegex(ValueError, "DUPLICATE_CASE_ID"):
            mod.audit_manifest({"contract": mod.CONTRACT, "cases": [c, c]})

    def test_unhashable_json_values_fail_closed(self):
        c = valid()
        c["authority"] = ["RESEARCH_ONLY"]
        c["claim_type"] = {"target": "BTC"}
        self.assertEqual(mod.audit_case(c)["status"], "REJECTED_SCHEMA")

    def test_non_string_duplicate_key_is_rejected_not_crash(self):
        c = valid()
        c["case_id"] = {"bad": "id"}
        result = mod.audit_manifest({"contract": mod.CONTRACT, "cases": [c]})
        self.assertEqual(result["rows"][0]["status"], "REJECTED_SCHEMA")

    def test_no_manifest_can_claim_score_or_promotion(self):
        m = {"contract": mod.CONTRACT, "cases": [valid()]}
        result = mod.audit_manifest(m)
        self.assertEqual(result["scientific_admitted_count"], 0)
        self.assertEqual(result["forecast_scores_created"], 0)

    def test_real_research_cases_remain_non_scorable(self):
        path = ROOT / "06_RESEARCH_LAB/audit_summaries/2026-11-16__public_forecast_cases_v1.json"
        x = mod.audit_manifest(json.loads(path.read_text(encoding="utf-8")))
        self.assertEqual(x["row_count"], 4)
        self.assertTrue(all(not row["scorable"] for row in x["rows"]))
        self.assertTrue(all(not row["scientific_admitted"] for row in x["rows"]))

if __name__ == "__main__":
    unittest.main()
