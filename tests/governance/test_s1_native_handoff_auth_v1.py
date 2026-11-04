"""Non-network positive and adversarial regression tests for S1 G1 proof."""
import hashlib
import json
import unittest

from scripts.governance.s1_agent_handoff_receipts_v1 import validate_chain
from scripts.governance.s1_native_handoff_auth_v1 import authenticate_native_chain

REPO = "Donh91/Investering-Framework-Archive-v1"
STATES = ("REQUESTED", "ACKNOWLEDGED", "ACCEPTED", "RESULT_DELIVERED")
TIMES = tuple(f"2026-11-04T15:0{i}:00Z" for i in range(4))


def fixture():
    common = {
        "request_id": "req-20261104-g1-native-00001",
        "source_head": "a" * 40,
        "source_fingerprint": "f" * 64,
        "sender": "S1",
        "recipient": "Codex",
        "original_url": f"https://github.com/{REPO}/issues/1156",
    }
    chain = [
        dict(
            common, state=state, actor=("S1" if i == 0 else "Codex"),
            at_utc=TIMES[i],
            native_event_url=f"https://github.com/{REPO}/issues/1156#issuecomment-{100+i}",
        )
        for i, state in enumerate(STATES)
    ]
    chain[-1]["result_url"] = f"https://github.com/{REPO}/actions/runs/42"
    binding = validate_chain(chain)["request_binding_sha256"]
    artifact_content = {
        "contract": "S1_RECIPIENT_RESULT_v1",
        "request_id": common["request_id"],
        "source_head": common["source_head"],
        "source_fingerprint": common["source_fingerprint"],
        "request_binding_sha256": binding,
        "workflow_run_id": 42,
        "workflow_job_id": 77,
    }
    artifact_bytes = json.dumps(artifact_content, sort_keys=True).encode()
    native = {}
    for i, event in enumerate(chain):
        body = {
            "contract": "S1_HANDOFF_NATIVE_V1",
            "request_id": event["request_id"],
            "source_head": event["source_head"],
            "source_fingerprint": event["source_fingerprint"],
            "request_binding_sha256": binding,
            "state": event["state"],
        }
        if i == 3:
            body.update(
                workflow_run_id=42, workflow_job_id=77, artifact_id=333,
                receiver_head_sha="b" * 40,
                artifact_sha256=hashlib.sha256(artifact_bytes).hexdigest(),
            )
        native[f"/repos/{REPO}/issues/comments/{100+i}"] = {
            "id": 100 + i,
            "html_url": event["native_event_url"],
            "user": {"login": ("Donh91" if i == 0 else "codex[bot]")},
            "created_at": TIMES[i],
            "body": json.dumps(body),
        }
    native[f"/repos/{REPO}/actions/runs/42"] = {
        "id": 42,
        "head_sha": "b" * 40,
        "repository": {"full_name": REPO},
        "actor": {"login": "codex[bot]"},
        "event": "workflow_dispatch",
        "status": "completed",
        "conclusion": "success",
    }
    native[f"/repos/{REPO}/actions/jobs/77"] = {
        "id": 77,
        "run_id": 42,
        "status": "completed",
        "conclusion": "success",
        "steps": [
            {"name": "Set up job", "status": "completed", "conclusion": "success"},
            {"name": "Run bounded implementation", "status": "completed", "conclusion": "success"},
            {"name": "Run bounded tests", "status": "completed", "conclusion": "success"},
        ],
    }
    native[f"/repos/{REPO}/actions/runs/42/artifacts"] = {
        "artifacts": [{
            "id": 333,
            "workflow_run": {"id": 42},
            "expired": False,
        }],
    }
    return chain, binding, native, artifact_bytes


def evaluate(chain=None, binding=None, native=None, artifact=None, required=None):
    base_chain, base_binding, base_native, base_artifact = fixture()
    return authenticate_native_chain(
        base_chain if chain is None else chain,
        expected_source_head="a" * 40,
        expected_binding_sha256=base_binding if binding is None else binding,
        origin_repo=REPO, recipient_repo=REPO,
        sender_login="Donh91", recipient_login="codex[bot]",
        native_get=lambda path: (base_native if native is None else native)[path],
        artifact_bytes_get=lambda _repo, _id: base_artifact if artifact is None else artifact,
        required_execution_steps=(("Run bounded implementation", "Run bounded tests") if required is None else required),
    )


class NativeHandoffTests(unittest.TestCase):
    def blocked(self, result):
        self.assertEqual(result["status"], "UNKNOWN_OR_BLOCKED")
        self.assertFalse(result["authenticated_delivery"])
        self.assertFalse(result["actual_job_execution_proven"])
        self.assertFalse(result["result_artifact_verified"])
        self.assertFalse(result["release_authorized"])

    def test_complete_native_chain_no_merge_authority(self):
        result = evaluate()
        self.assertEqual(result["status"], "OBSERVED_EXECUTION_NOT_RELEASE")
        self.assertTrue(result["authenticated_delivery"])
        self.assertTrue(result["actual_job_execution_proven"])
        self.assertTrue(result["result_artifact_verified"])
        self.assertFalse(result["release_authorized"])

    def test_code_ready_is_not_recipient_ack(self):
        chain, *_ = fixture()
        self.blocked(evaluate(chain=chain[:1]))

    def test_real_ack_without_job_evidence(self):
        chain, *_ = fixture()
        for end in (2, 3):
            with self.subTest(end=end):
                result = evaluate(chain=chain[:end])
                self.assertEqual(result["status"], "NATIVE_RECIPIENT_ACK_ONLY")
                self.assertTrue(result["authenticated_delivery"])
                self.assertFalse(result["actual_job_execution_proven"])
                self.assertFalse(result["release_authorized"])

    def test_forged_sender_or_recipient_comment(self):
        for idx in (0, 1, 3):
            with self.subTest(idx=idx):
                chain, binding, db, artifact = fixture()
                db[f"/repos/{REPO}/issues/comments/{100+idx}"]["user"]["login"] = "untrusted[bot]"
                self.blocked(evaluate(native=db))

    def test_native_comment_wrong_work_id_or_source(self):
        for field, value in (
            ("request_id", "req-other-20261104"), ("source_head", "c" * 40),
            ("source_fingerprint", "0" * 64), ("request_binding_sha256", "0" * 64),
        ):
            with self.subTest(field=field):
                chain, binding, db, artifact = fixture()
                key = f"/repos/{REPO}/issues/comments/101"
                body = json.loads(db[key]["body"])
                body[field] = value
                db[key]["body"] = json.dumps(body)
                self.blocked(evaluate(native=db))

    def test_native_comment_wrong_time(self):
        chain, binding, db, artifact = fixture()
        db[f"/repos/{REPO}/issues/comments/101"]["created_at"] = "2026-11-04T14:01:00Z"
        self.blocked(evaluate(native=db))

    def test_fake_github_lookalike(self):
        chain, binding, db, artifact = fixture()
        chain[1]["native_event_url"] = (
            f"https://github.com.attacker.invalid/{REPO}/issues/1156#issuecomment-101")
        self.blocked(evaluate(chain=chain))

    def test_wrong_request_binding(self):
        self.blocked(evaluate(binding="0" * 64))

    def test_wrong_run_actor_or_source_head(self):
        for field, value in (("head_sha", "c" * 40), ("actor", {"login": "Donh91"})):
            with self.subTest(field=field):
                chain, binding, db, artifact = fixture()
                db[f"/repos/{REPO}/actions/runs/42"][field] = value
                self.blocked(evaluate(native=db))

    def test_wrong_run_job_relationship(self):
        chain, binding, db, artifact = fixture()
        db[f"/repos/{REPO}/actions/jobs/77"]["run_id"] = 999
        self.blocked(evaluate(native=db))

    def test_failed_cancelled_queued_or_skipped_job(self):
        for state, conclusion in (
            ("queued", None), ("completed", "failure"),
            ("completed", "cancelled"), ("completed", "skipped"),
        ):
            with self.subTest(state=state, conclusion=conclusion):
                chain, binding, db, artifact = fixture()
                db[f"/repos/{REPO}/actions/jobs/77"].update(
                    status=state, conclusion=conclusion)
                self.blocked(evaluate(native=db))

    def test_zero_substantive_executed_steps(self):
        chain, binding, db, artifact = fixture()
        db[f"/repos/{REPO}/actions/jobs/77"]["steps"] = [
            {"name": "Checkout", "status": "completed", "conclusion": "success"},
            {"name": "Set up job", "status": "completed", "conclusion": "success"},
        ]
        self.blocked(evaluate(native=db))

    def test_checkout_only_even_if_success_must_not_prove_execution(self):
        chain, binding, db, artifact = fixture()
        db[f"/repos/{REPO}/actions/jobs/77"]["steps"] = [
            {"name": "Set up job", "status": "completed", "conclusion": "success"},
            {"name": "Run actions/checkout@v4", "status": "completed", "conclusion": "success"},
            {"name": "Run actions/setup-python@v5", "status": "completed", "conclusion": "success"},
        ]
        self.blocked(evaluate(native=db))

    def test_two_required_steps_must_both_execute(self):
        for name in ("Run bounded implementation", "Run bounded tests"):
            chain, binding, db, artifact = fixture()
            for row in db[f"/repos/{REPO}/actions/jobs/77"]["steps"]:
                if row["name"] == name:
                    row["conclusion"] = "skipped"
            with self.subTest(name=name):
                self.blocked(evaluate(native=db))

    def test_untrusted_or_setup_step_manifest_must_be_rejected(self):
        for required in (
            [], ["Run bounded tests"], ["Run bounded tests", "Run bounded tests"],
            ["Run actions/checkout@v4", "Run bounded tests"],
            ["Set up job", "Run bounded tests"],
            ["Run actions/setup-python@v5", "Run bounded tests"],
        ):
            with self.subTest(required=required):
                self.blocked(evaluate(required=required))

    def test_wrong_or_expired_artifact(self):
        for field, value in (("workflow_run", {"id": 999}), ("expired", True)):
            with self.subTest(field=field):
                chain, binding, db, artifact = fixture()
                db[f"/repos/{REPO}/actions/runs/42/artifacts"]["artifacts"][0][field] = value
                self.blocked(evaluate(native=db))

    def test_tampered_result_bytes(self):
        self.blocked(evaluate(artifact=b'{"fake":true}'))

    def test_wrong_artifact_request_id_even_if_digest_matches(self):
        chain, binding, db, raw = fixture()
        payload = json.loads(raw)
        payload["request_id"] = "req-20261104-other"
        changed = json.dumps(payload, sort_keys=True).encode()
        key = f"/repos/{REPO}/issues/comments/103"
        body = json.loads(db[key]["body"])
        body["artifact_sha256"] = hashlib.sha256(changed).hexdigest()
        db[key]["body"] = json.dumps(body)
        self.blocked(evaluate(native=db, artifact=changed))

    def test_unavailable_native_job_fails_closed(self):
        chain, binding, db, artifact = fixture()
        del db[f"/repos/{REPO}/actions/jobs/77"]
        self.blocked(evaluate(native=db))


if __name__ == "__main__":
    unittest.main()
