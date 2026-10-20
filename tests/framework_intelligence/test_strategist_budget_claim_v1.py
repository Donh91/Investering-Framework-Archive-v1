"""Regression: concurrent Strategist questions cannot overspend a shared lane."""
import base64
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from scripts.framework_intelligence.strategist_budget_claim_v1 import (
    CAP_USD, CONTRACT, MODEL, TASK, canonical, claim_month, max_liability, prepare_payload,
)
MONTH = datetime.now(timezone.utc).strftime("%Y-%m")


class BudgetClaimTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.runtime = self.root / "runtime"
        self.runtime.mkdir()
        def save(path, payload):
            fp = self.root / path
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text(json.dumps(payload))
        save("research/api_agent/API_TASK_REGISTRY_v1.json", {"tasks": {
            TASK: {"model": MODEL, "max_attempts": 1, "max_output_tokens": 5400,
                   "governed_instruction": "Bounded"}}})
        save("research/api_agent/API_INTELLIGENCE_POLICY_v2.json", {
            "monthly_hard_stop_usd": 40, "global_reserve_usd": 4,
            "lane_caps_usd": {TASK: CAP_USD}})
        (self.runtime / "prompt.txt").write_text("Read-only.")
        (self.runtime / "context.json").write_text('{"source":[]}')
        (self.runtime / "plan.json").write_text(json.dumps({
            "run_allowed": True, "max_api_calls": 1, "material_fingerprint": "b"*64}))

    def test_worst_case_includes_output_tokens(self):
        amount = max_liability(self.root, self.runtime)
        self.assertGreaterEqual(amount, 0.054)
        self.assertLessEqual(amount, 0.15)
        (self.runtime / "context.json").write_text("x"*12002)
        with self.assertRaisesRegex(ValueError, "unbounded"):
            max_liability(self.root, self.runtime)

    def test_new_questions_consume_same_monthly_cap(self):
        month = {}
        for n, digit in enumerate("abcdef", 1):
            month = claim_month(month, month=MONTH, fingerprint=digit*64,
                                run_id=str(n), liability_usd=0.11)
        self.assertEqual(len(month["entries"]), 6)
        with self.assertRaisesRegex(ValueError, "insufficient"):
            claim_month(month, month=MONTH, fingerprint="0"*64,
                        run_id="7", liability_usd=0.11)
        with self.assertRaisesRegex(ValueError, "already_claimed"):
            claim_month(month, month=MONTH, fingerprint="a"*64,
                        run_id="8", liability_usd=0.11)

    def test_existing_ledger_requires_expected_blob_sha(self):
        original = claim_month({}, month=MONTH, fingerprint="a"*64,
                               run_id="1", liability_usd=0.11)
        raw = canonical(original)
        blob_sha = hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        remote = {"sha": blob_sha, "content": base64.b64encode(raw).decode()}
        claim = prepare_payload(self.root, self.runtime, remote, month=MONTH, run_id="2")
        self.assertEqual(claim["request"]["sha"], blob_sha)
        self.assertIn("b"*64, json.loads(base64.b64decode(claim["request"]["content"]))["entries"])
        remote["sha"] = "f"*40
        with self.assertRaisesRegex(ValueError, "sha_mismatch"):
            prepare_payload(self.root, self.runtime, remote, month=MONTH, run_id="3")

    def test_untrusted_ledger_and_budget_policy_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "untrusted_existing"):
            claim_month({"contract": CONTRACT, "month": MONTH}, month=MONTH,
                        fingerprint="c"*64, run_id="4", liability_usd=0.1)
        path = self.root/"research/api_agent/API_TASK_REGISTRY_v1.json"
        cfg = json.loads(path.read_text())
        cfg["tasks"][TASK]["max_attempts"] = 2
        path.write_text(json.dumps(cfg))
        with self.assertRaisesRegex(ValueError, "budget_policy"):
            max_liability(self.root, self.runtime)


if __name__ == "__main__":
    unittest.main()
