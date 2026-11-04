"""No-network tests for generic owner-bounded Sol MAX submit/GET semantics."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.api_agent import sol_max_elite_transport as m

HEAD = "a" * 40
MISSION = "S1-ELITE-EXECUTOR-20261104"
RUN = "41899900001"
ENV = {"GITHUB_RUN_ATTEMPT": "1", "GITHUB_RUN_ID": RUN,
       "GITHUB_ACTOR": "Donh91", "GITHUB_REPOSITORY": m.REPO}


def sample(root):
    original = json.loads(Path(m.BATCH).read_text())
    original["definitions"][0]["scope"] = ["scripts/example.py"]
    path = root / m.BATCH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(original))
    source = root / "scripts/example.py"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("def fix():\n    return 1\n")
    return original, path, source


def active(batch):
    obj = copy.deepcopy(batch)
    obj["dispatch_enabled"] = True
    obj["state"] = "OWNER_APPROVED_DISPATCH"
    obj["public_storage_consent_30_days"] = True
    obj["billing_liability_for_run_41870364609"] = "RECONCILED"
    obj["payment_policy"]["no_auto_paid_trigger_until_reconciled"] = False
    return obj


def native(claim, payload):
    def fetch(path):
        if path == "issues/comments/" + str(claim["id"]):
            return {"id": claim["id"], "body": claim["body"],
                    "user": {"login": "github-actions[bot]"}}
        if path == "actions/runs/" + RUN:
            return {"id": int(RUN), "event": "issue_comment",
                    "name": "Framework Learning Supervisor",
                    "head_sha": HEAD, "actor": {"login": "Donh91"}}
        raise AssertionError("unexpected native read " + path)
    return fetch


def paid_fixture(root):
    batch, _, _ = sample(root)
    packet = m.render_source(root, MISSION, HEAD)["packet"]
    payload = m.checked_request(packet)
    claim = {"status": "NATIVE_VERIFIED_PRE_HTTP", "id": 101,
             "mission": MISSION, "source_head": HEAD, "origin_run_id": RUN,
             "body": m.claim_body(MISSION, HEAD, m.digest(m.canonical(payload)))}
    return batch, packet, payload, claim


class FakeHTTP:
    status = 200

    def __init__(self, response):
        self.response = response

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, *args):
        return json.dumps(self.response).encode()


class EliteTransportTests(unittest.TestCase):
    def test_manifest_and_public_file_sha_are_bound(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, source = sample(root)
            result = m.render_source(root, MISSION, HEAD)
            self.assertEqual(result["context_sha256"],
                             m.digest(m.canonical(result["packet"])))
            self.assertEqual(result["packet"]["source_files"]["scripts/example.py"]["sha256"],
                             m.digest(source.read_bytes()))
            self.assertFalse(result["dispatch_enabled"])
            self.assertLess(result["cost_ceiling_usd"], 3)

    def test_missing_source_secret_traversal_and_bad_mission_reject(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            batch, path, source = sample(root)
            source.write_text("sk-proj-" + "A" * 28)
            with self.assertRaisesRegex(ValueError, "OVERSIZED_OR_SECRET"):
                m.render_source(root, MISSION, HEAD)
            source.write_text("ok")
            batch["definitions"][0]["scope"] = ["../secrets/token"]
            path.write_text(json.dumps(batch))
            with self.assertRaisesRegex(ValueError, "SOURCE_PATH_NOT_PUBLIC"):
                m.render_source(root, MISSION, HEAD)
            with self.assertRaisesRegex(ValueError, "INVALID_ELITE_MISSION_ID"):
                m.render_source(root, "bad", HEAD)

    def test_legacy_unknown_charge_and_no_consent_refuse_payment(self):
        with tempfile.TemporaryDirectory() as td:
            batch, _, payload, claim = paid_fixture(Path(td))
            with self.assertRaisesRegex(ValueError, "PAID_DISPATCH_STILL_GATED"):
                m.require_paid_authority(batch)
            admitted = active(batch)
            m.require_paid_authority(admitted)
            admitted["public_storage_consent_30_days"] = False
            with self.assertRaisesRegex(ValueError, "PAID_DISPATCH_STILL_GATED"):
                m.require_paid_authority(admitted)

    def test_request_model_scope_and_schema(self):
        with tempfile.TemporaryDirectory() as td:
            _, pkt, payload, _ = paid_fixture(Path(td))
            self.assertTrue(payload["background"])
            self.assertTrue(payload["store"])
            self.assertEqual(payload["model"], "gpt-6.1-sol")
            self.assertEqual(payload["reasoning"]["effort"], "max")
            self.assertEqual(payload["text"]["format"]["strict"], True)
            self.assertEqual(pkt["authority"], "PATCH_CANDIDATE_ONLY_NO_SOURCE_WRITE_NO_MERGE")

    def test_native_claim_and_run_must_match_exact_request(self):
        with tempfile.TemporaryDirectory() as td:
            _, _, payload, claim = paid_fixture(Path(td))
            m.verify_native_claim(claim, payload, native_reader=native(claim, payload), environment=ENV)
            bad = copy.deepcopy(claim)
            bad["body"] = bad["body"].replace("3.00", "4.00")
            with self.assertRaisesRegex(ValueError, "CLAIM_HASH_MISMATCH"):
                m.verify_native_claim(bad, payload, native_reader=native(bad, payload), environment=ENV)
            with self.assertRaisesRegex(ValueError, "CLAIM_OR_RUN_MISSING"):
                m.verify_native_claim(claim, payload, native_reader=native(claim, payload),
                                      environment={**ENV, "GITHUB_RUN_ATTEMPT": "2"})
            def fake_actor(resource):
                result = native(claim, payload)(resource)
                if resource.startswith("issues/"):
                    result["user"]["login"] = "attacker"
                return result
            with self.assertRaisesRegex(ValueError, "NOT_AUTHENTICATED"):
                m.verify_native_claim(claim, payload, native_reader=fake_actor, environment=ENV)

    def test_one_post_and_durable_handle_no_repeat(self):
        with tempfile.TemporaryDirectory() as td:
            batch, _, payload, claim = paid_fixture(Path(td))
            sends = []
            def post(req, timeout):
                sends.append(req.get_method())
                self.assertEqual(req.get_full_url(), "https://api.openai.com/v1/responses")
                return FakeHTTP({"id": "resp_unique1234", "status": "in_progress"})
            output = Path(td) / "paid"
            result = m.submit_one(active(batch), payload, claim, output, "fake-key",
                                  native_reader=native(claim, payload), environment=ENV, post=post)
            self.assertEqual(sends, ["POST"])
            self.assertEqual(result["response_id"], "resp_unique1234")
            self.assertEqual(json.loads((output / "attempt.json").read_text())["state"],
                             "SUBMITTED_GET_ONLY")
            with self.assertRaisesRegex(ValueError, "ALREADY_EXISTS_NO_SECOND_POST"):
                m.submit_one(active(batch), payload, claim, output, "fake-key",
                             native_reader=native(claim, payload), environment=ENV, post=post)
            self.assertEqual(len(sends), 1)

    def test_timeout_stays_unknown_liability_and_never_reposts(self):
        with tempfile.TemporaryDirectory() as td:
            batch, _, payload, claim = paid_fixture(Path(td))
            sends = []
            def fail(req, timeout):
                sends.append(req.get_method())
                raise TimeoutError("no response ID")
            output = Path(td) / "unknown"
            with self.assertRaises(TimeoutError):
                m.submit_one(active(batch), payload, claim, output, "fake-key",
                             native_reader=native(claim, payload), environment=ENV, post=fail)
            self.assertEqual(sends, ["POST"])
            self.assertEqual(json.loads((output / "attempt.json").read_text())["state"],
                             "POST_OUTCOME_UNKNOWN")
            with self.assertRaisesRegex(ValueError, "ALREADY_EXISTS_NO_SECOND_POST"):
                m.submit_one(active(batch), payload, claim, output, "fake-key",
                             native_reader=native(claim, payload), environment=ENV, post=fail)
            self.assertEqual(len(sends), 1)

    def test_get_only_never_submits_another_request(self):
        methods = []
        def get(req, timeout):
            methods.append(req.get_method())
            return FakeHTTP({"id": "resp_unique1234", "status": "completed", "usage": {
                "input_tokens": 100, "output_tokens": 200}})
        status, body = m.collect_one("resp_unique1234", "fake-key", get=get)
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "completed")
        self.assertEqual(methods, ["GET"])
        with self.assertRaisesRegex(ValueError, "VERIFIED_RESPONSE_ID"):
            m.collect_one("forged id", "fake-key", get=get)
        self.assertEqual(methods, ["GET"])

    def test_native_duplicate_claim_is_terminal_until_reconciled(self):
        body = m.claim_body(MISSION, HEAD, "f" * 64)
        with self.assertRaisesRegex(ValueError, "ALREADY_CLAIMED"):
            m.check_unspent_claim([{"body": body, "user": {"login": "github-actions[bot]"}}], MISSION)
        m.check_unspent_claim([{"body": body, "user": {"login": "third-party"}}], MISSION)


if __name__ == "__main__":
    unittest.main()
