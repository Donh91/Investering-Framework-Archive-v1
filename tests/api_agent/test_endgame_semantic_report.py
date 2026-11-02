"""Positive and mutation-negative tests for fail-closed API completion reports."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from scripts.api_agent.endgame_semantic_report import report

WORK = "M3_KOMPAS_PIT_NOWCAST_ISSUANCE_PROOF_20261028"
NOW = 1793214000


def digest(value):
    return hashlib.sha256((json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()).hexdigest()


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "live").mkdir()
        self.context = {"contract": "TERRA_ENDGAME_PROGRESS_PACKET_v1", "work_id": WORK,
                        "exact_original_main_sha": "a" * 40}
        self.manifest = {"work_id": WORK, "main_sha": "a" * 40}
        self.output = {"status": "READY", "summary": "UNTRUSTED_PROSE", "forecast_candidates": []}
        self.prompt = b"bounded"
        self.receipt = {"contract": "API_AGENT_RECEIPT_v3", "task": "TERRA_XHIGH_ENDGAME_PROGRESS_V1",
                        "model": "gpt-6.1-terra", "reasoning_effort": "xhigh", "status": "PASS",
                        "attempt_count": 1, "response_id": "resp_123", "created_unix": NOW - 10,
                        "estimated_cost_usd": 0.111377, "authority": {"merge": False},
                        "context_hash": digest(self.context), "output_hash": digest(self.output),
                        "prompt_hash": hashlib.sha256(self.prompt).hexdigest()}
        self.write()

    def write(self):
        for name, value in (("context.json", self.context), ("manifest.json", self.manifest),
                            ("live/receipt.json", self.receipt), ("live/output.json", self.output)):
            (self.root / name).write_text(json.dumps(value))
        (self.root / "prompt.txt").write_bytes(self.prompt)

    def run_report(self, attempt=1):
        return report(self.root, WORK, "40732341444", attempt, now=NOW)

    def test_ready_requires_review_and_does_not_leak_model_text(self):
        s = self.run_report()
        self.assertIn("substantive_status=READY; disposition=REVIEW_REQUIRED", s)
        self.assertIn("code_status=NOT_IMPLEMENTED_BY_MODEL", s)
        self.assertNotIn("UNTRUSTED_PROSE", s)

    def test_degraded_and_blocked_are_not_success(self):
        for state, decision in (("DEGRADED", "FIX_REQUIRED"), ("BLOCKED", "SOURCE_REQUIRED")):
            self.output["status"] = state
            self.receipt["output_hash"] = digest(self.output)
            self.write()
            self.assertIn(f"substantive_status={state}; disposition={decision}", self.run_report())

    def test_mutated_output_hash_fails_closed(self):
        self.output["status"] = "DEGRADED"
        self.write()
        self.assertIn("substantive_status=UNVERIFIED", self.run_report())

    def test_mismatched_work_even_with_matching_hash_fails_closed(self):
        self.context["work_id"] = "OTHER_VALID_WORK_ID_20261028"
        self.receipt["context_hash"] = digest(self.context)
        self.write()
        self.assertIn("EVIDENCE_MISSING_OR_MISMATCHED", self.run_report())

    def test_missing_and_corrupt_receipt_fail_closed(self):
        (self.root / "live/receipt.json").unlink()
        self.assertIn("gateway_status=UNVERIFIED", self.run_report())
        (self.root / "live/receipt.json").write_text("{broken")
        self.assertIn("gateway_status=UNVERIFIED", self.run_report())

    def test_stale_receipt_and_second_attempt_fail_closed(self):
        self.receipt["created_unix"] = NOW - 4000
        self.write()
        self.assertIn("substantive_status=UNVERIFIED", self.run_report())
        self.assertIn("substantive_status=UNVERIFIED", self.run_report(attempt=2))

    def test_authority_and_forecast_mutations_fail_closed(self):
        self.receipt["authority"]["merge"] = True
        self.write()
        self.assertIn("gateway_status=UNVERIFIED", self.run_report())
        self.receipt["authority"]["merge"] = False
        self.output["forecast_candidates"] = [{"direction": "UP"}]
        self.receipt["output_hash"] = digest(self.output)
        self.write()
        self.assertIn("gateway_status=UNVERIFIED", self.run_report())

    def test_prompt_hash_and_future_receipt_fail_closed(self):
        self.prompt = b"tampered"
        self.write()
        self.assertIn("gateway_status=UNVERIFIED", self.run_report())
        self.receipt["prompt_hash"] = hashlib.sha256(self.prompt).hexdigest()
        self.receipt["created_unix"] = NOW + 5
        self.write()
        self.assertIn("gateway_status=UNVERIFIED", self.run_report())
