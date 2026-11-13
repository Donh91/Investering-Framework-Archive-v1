"""Adversarial no-network tests of owner-only Astra High one-shot API lane."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.api_agent import manual_astra_task2_high_v1 as m

HEAD = "a" * 40
ENV = {
    "GITHUB_SHA": HEAD, "GITHUB_ACTOR": "Donh91",
    "GITHUB_REF": "refs/heads/main",
    "GITHUB_RUN_ID": "43419999999",
    "GITHUB_REPOSITORY": "Donh91/Investering-Framework-Archive-v1",
    "GITHUB_TOKEN": "INERT_SYNTHETIC_TEST",
    "OPENAI_API_KEY": "INERT_SYNTHETIC_TEST",
    "ASTRA_OWNER_CONFIRM": m.OWNER_CONFIRM,
}

class AstraOneShotTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root = Path(self.t.name)
        for source in m.SOURCE_FILES:
            f = self.root / source
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("Synthetic, public-only research fixture " + source, encoding="utf-8")
        self.out = self.root / "out"
        self.root_patch = patch.object(m, "ROOT", self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        self.env_patch = patch.dict(os.environ, ENV)
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)

    def test_public_source_manifest_and_cost_ceiling(self):
        p, manifest = m.build_payload()
        self.assertEqual(p["model"], "gpt-6-astra")
        self.assertEqual(p["reasoning"]["effort"], "high")
        self.assertTrue(p["background"] and p["store"])
        self.assertEqual(p["max_output_tokens"], 50000)
        self.assertLessEqual(manifest["worst_case_token_estimate_usd"], 5.0)
        self.assertEqual(len(manifest["source_files"]), len(m.SOURCE_FILES))
        self.assertEqual(manifest["source_main_sha"], HEAD)
        self.assertFalse(manifest["private_source"])
        self.assertEqual(manifest["paid_attempts_allowed"], 1)

    def test_second_prepare_fails_without_overwrite(self):
        m.prepare(self.out)
        with self.assertRaisesRegex(ValueError, "ONE_USE_RECORD_ALREADY_EXISTS"):
            m.prepare(self.out)

    def test_owner_and_branch_required(self):
        m.prepare(self.out)
        with patch.dict(os.environ, {"GITHUB_ACTOR": "not-owner"}):
            with self.assertRaisesRegex(ValueError, "OWNER_MAIN_GATE_FAILED"):
                m.reserve(self.out)
        with patch.dict(os.environ, {"ASTRA_OWNER_CONFIRM": "wrong"}):
            with self.assertRaisesRegex(ValueError, "EXPLICIT_OWNER_CONFIRMATION"):
                m.reserve(self.out)
        self.assertFalse((self.out / "claim.json").exists())

    def test_existing_claim_stops_billing(self):
        with patch.object(m, "http_json", return_value={"artifacts": [{"name": m.CLAIM_ARTIFACT, "expired": False}]}):
            with self.assertRaisesRegex(ValueError, "PAID_CLAIM_ALREADY_EXISTS"):
                m.check_claim_artifacts("inert", ENV["GITHUB_REPOSITORY"])

    def test_model_access_checked_before_paid_claim(self):
        m.prepare(self.out)
        def mock_http(method, url, **kwargs):
            if "api.github.com" in url:
                return {"artifacts": []}
            return {"id": "no-such-model"}
        with patch.object(m, "http_json", side_effect=mock_http):
            with self.assertRaisesRegex(ValueError, "ASTRA_MODEL_NOT_AVAILABLE"):
                m.reserve(self.out)
        self.assertFalse((self.out / "claim.json").exists())

    def _prepare_and_claim(self):
        m.prepare(self.out)
        def mocked(method, url, **kwargs):
            if "api.github.com" in url: return {"artifacts": []}
            if "/models/" in url: return {"id": m.MODEL}
            raise AssertionError("unexpected request")
        with patch.object(m, "http_json", side_effect=mocked):
            m.reserve(self.out)

    def test_exactly_one_paid_post_and_no_retry(self):
        self._prepare_and_claim()
        count = []
        def mocked(method, url, **kwargs):
            count.append((method, url))
            return {"id": "resp_SYNTHETIC123456", "model": m.MODEL, "status": "in_progress"}
        with patch.object(m, "http_json", side_effect=mocked):
            m.submit(self.out)
            with self.assertRaisesRegex(ValueError, "ONE_USE_RECORD_ALREADY_EXISTS"):
                m.submit(self.out)
        self.assertEqual([x for x in count if x[0] == "POST"], [("POST", m.API + "/responses")])
        self.assertEqual(m.read(self.out / "attempt.json")["attempt_count"], 1)
        self.assertEqual(m.read(self.out / "response_handle.json")["response_id"], "resp_SYNTHETIC123456")

    def test_ambiguous_post_never_resubmitted(self):
        self._prepare_and_claim()
        with patch.object(m, "http_json", side_effect=TimeoutError("synthetic")):
            with self.assertRaises(TimeoutError):
                m.submit(self.out)
        self.assertTrue((self.out / "attempt.json").exists())
        self.assertFalse((self.out / "response_handle.json").exists())
        with self.assertRaisesRegex(ValueError, "ONE_USE_RECORD_ALREADY_EXISTS"):
            m.submit(self.out)

    def test_get_only_completion_and_usage_receipt(self):
        self._prepare_and_claim()
        with patch.object(m, "http_json", return_value={"id": "resp_SYNTHETIC123456", "model": m.MODEL, "status": "in_progress"}):
            m.submit(self.out)
        completed = {
            "id": "resp_SYNTHETIC123456",
            "model": m.MODEL, "status": "completed",
            "output": [{"content": [{"type": "output_text", "text": "PUBLIC-ONLY ASTRA RESEARCH DRAFT; NO VERIFIED EDGE"}]}],
            "usage": {"input_tokens": 2000, "output_tokens": 8000}
        }
        with patch.object(m, "http_json", return_value=completed) as call:
            status = m.collect(self.out)
            self.assertEqual(call.call_args[0][0], "GET")
        self.assertEqual(status, 0)
        receipt = m.read(self.out / "receipt.json")
        self.assertEqual(receipt["estimated_cost_usd"], 0.42)
        self.assertTrue(receipt["claude_audit_due"])
        self.assertFalse(receipt["scientific_edge_verified"])
        self.assertIn("NO VERIFIED EDGE", (self.out / "research_output.md").read_text())

    def test_mismatched_response_id_fails_closed(self):
        self._prepare_and_claim()
        with patch.object(m, "http_json", return_value={"id": "resp_SYNTHETIC123456", "model": m.MODEL, "status": "in_progress"}):
            m.submit(self.out)
        with patch.object(m, "http_json", return_value={"id": "resp_OTHER", "status": "completed"}):
            with self.assertRaisesRegex(ValueError, "RETRIEVED_RESPONSE_ID_OR_MODEL_MISMATCH"):
                m.collect(self.out)

    def test_oversize_source_does_not_construct_api_payload(self):
        source = self.root / m.SOURCE_FILES[0]
        source.write_text("A"*50001)
        with self.assertRaisesRegex(ValueError, "SOURCE_OVERSIZE"):
            m.build_payload()

    def test_private_path_traversal_is_rejected(self):
        with patch.object(m, "SOURCE_FILES", ("../../restricted.dat",)):
            with self.assertRaisesRegex(ValueError, "PUBLIC_ALLOWLIST_FILE_MISSING_OR_UNSAFE"):
                m.build_payload()

if __name__ == "__main__":
    unittest.main()
