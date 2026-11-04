"""No-network, no-POST regressions for generic stored Sol collector."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.api_agent import s1_sol_background_collect as c

HEAD = "a" * 40
RID = "resp_proven54321"
RUN = "41830814618"
CLAIM_ID = 101

def fixture(path: Path):
    context = json.dumps({"contract": "S1_SOL_MAX_PATCH_CONTEXT_v1",
        "source_head": HEAD, "repo": c.REPO, "original_pr": c.PR}).encode()
    handle = {"response_id": RID, "source_head": HEAD,
        "context_sha256": hashlib.sha256(context).hexdigest(),
        "reservation_claim_id": CLAIM_ID, "model": c.MODEL,
        "reasoning_effort": "max", "state": "in_progress"}
    reservation = {"claim_id": CLAIM_ID, "model": c.MODEL,
        "effort": "max", "source_head": HEAD, "status": "RESERVED"}
    (path / "context.json").write_bytes(context)
    (path / "response_handle.json").write_text(json.dumps(handle))
    (path / "reservation.json").write_text(json.dumps(reservation))
    return handle, reservation

def native(resource):
    if resource == "actions/runs/" + RUN:
        return {"id": int(RUN), "event": "pull_request",
                "name": "Framework Learning Supervisor", "head_sha": HEAD}
    if resource == "issues/comments/" + str(CLAIM_ID):
        return {"user": {"login": "github-actions[bot]"},
                "body": f"{c.CLAIM_PREFIX} HEAD={HEAD} {c.CLAIM_TAIL}"}
    raise AssertionError("unexpected native endpoint " + resource)

class DummyResponse:
    status = 200
    def __init__(self, body): self.body = body
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, *args): return json.dumps(self.body).encode()

class CollectorTests(unittest.TestCase):
    def test_proven_native_run_and_claim_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture(root)
            handle = c.verify_native_artifact(root, RUN, read_native=native)
            self.assertEqual(handle["response_id"], RID)
            self.assertEqual(handle["source_head"], HEAD)
            self.assertEqual(handle["claim_id"], CLAIM_ID)

    def test_github_run_origin_mismatch_blocks_before_provider(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture(root)
            with self.assertRaisesRegex(ValueError, "ORIGIN_GITHUB_RUN_INVALID"):
                c.verify_native_artifact(root, RUN, read_native=lambda resource: {
                    **native(resource), "head_sha": "b"*40} if resource.startswith("actions/") else native(resource))

    def test_native_claim_actor_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture(root)
            def evil(resource):
                data = native(resource)
                return {**data, "user": {"login": "Donh91"}} if resource.startswith("issues/") else data
            with self.assertRaisesRegex(ValueError, "NATIVE_PAYMENT_CLAIM"):
                c.verify_native_artifact(root, RUN, read_native=evil)

    def test_cross_source_replay_changes_context_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture(root)
            (root / "context.json").write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "CONTEXT_DRIFT"):
                c.verify_native_artifact(root, RUN, read_native=native)

    def test_bad_origin_run_is_no_native_read(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture(root)
            with self.assertRaisesRegex(ValueError, "INVALID_ORIGIN_RUN"):
                c.verify_native_artifact(root, "41830;echo bad", read_native=lambda x: self.fail("network"))

    def test_provider_get_is_one_request_without_post(self):
        methods = []
        def fake(req, timeout):
            methods.append((req.get_method(), req.full_url))
            return DummyResponse({"id": RID, "status": "completed",
                                  "usage": {"input_tokens": 100, "output_tokens": 200},
                                  "output": []})
        status, obj = c.retrieve_once({"response_id": RID}, "test-key", request=fake)
        self.assertEqual((status, obj["status"]), (200, "completed"))
        self.assertEqual(methods, [("GET", "https://api.openai.com/v1/responses/" + RID)])

    def test_empty_key_no_provider_call(self):
        called = []
        with self.assertRaisesRegex(ValueError, "OPENAI_API_KEY_MISSING"):
            c.retrieve_once({"response_id": RID}, "", request=lambda *args: called.append(args))
        self.assertEqual(called, [])

    def test_404_is_unknown_billing_not_zero(self):
        result = c.interpret({"response_id": RID}, 404, {})
        self.assertEqual(result["state"], "EXPIRED_OR_NOT_STORED")
        self.assertEqual(result["provider_billing"], "NOT_RECONCILED")
        self.assertFalse(result["paid_post_performed"])

    def test_pending_does_not_relaunch(self):
        result = c.interpret({"response_id": RID}, 200,
                             {"id": RID, "status": "in_progress"})
        self.assertEqual(result["state"], "PENDING_COLLECT")
        self.assertFalse(result["automatic_source_application"])

    def test_completed_reports_usage_not_billing(self):
        response = {"id": RID, "status": "completed",
                    "usage": {"input_tokens": 120, "output_tokens": 240,
                              "output_tokens_details": {"reasoning_tokens": 200}}}
        result = c.interpret({"response_id": RID}, 200, response)
        self.assertEqual(result["state"], "COMPLETED")
        self.assertEqual(result["usage"]["reasoning_tokens"], 200)
        self.assertEqual(result["provider_billing"], "NOT_RECONCILED")

    def test_unknown_id_blocks_result(self):
        result = c.interpret({"response_id": RID}, 200,
                             {"id": "resp_other12345", "status": "completed"})
        self.assertEqual(result["state"], "PROVIDER_OR_ID_MISMATCH")

    def test_429_is_retryable_without_post(self):
        self.assertEqual(c.interpret({"response_id": RID}, 429, {})["state"], "RETRYABLE_GET_ONLY")

    def test_collect_dispatch_cannot_run_production_writer(self):
        workflow = Path(".github/workflows/framework-learning-supervisor.yml").read_text()
        self.assertIn("sol-max-collect:", workflow)
        self.assertIn("inputs.sol_collect_run_id != ''", workflow)
        self.assertIn("inputs.sol_collect_run_id == ''", workflow)
        self.assertIn("actions/download-artifact@v4", workflow)
        self.assertIn("ref: main", workflow)

    def test_response_handle_uploaded_before_any_validation(self):
        workflow = Path(".github/workflows/framework-learning-supervisor.yml").read_text()
        call = workflow.index("s1_sol_max_patch_execution.py call --head")
        persist = workflow.index("name: Persist original paid response handle immediately")
        validate = workflow.index("name: Validate generated patch and run original regression suite")
        self.assertLess(call, persist)
        self.assertLess(persist, validate)
        self.assertIn("--submit-only", workflow[call:persist])
        self.assertIn("hashFiles('runtime/s1-sol-max/proposal.json') != ''", workflow)

    def test_output_remains_non_authoritative_even_if_completed(self):
        self.assertFalse(c.interpret({"response_id": RID}, 200,
                         {"id": RID, "status": "completed"})["automatic_source_application"])

if __name__ == "__main__":
    unittest.main()
