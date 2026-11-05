"""No-network original-run and owner-claim checks for GET-only Sol recovery."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.api_agent import api_gateway as gateway
from scripts.api_agent import research_lab_sol_recover_v1 as m
from scripts.api_agent import recoverable_responses_v1 as transport

RUN = "42000011122"
HEAD = "a" * 40
TRIGGER = "6640001122"
MISSION = "SOL61-MAX-CYCLE-RECOVERY-ALTSEASON-20261105"


def fixture(root):
    ctx = {"mission_id": MISSION, "authority": "ADVISORY_READ_ONLY",
           "private_data_included": False, "public_source_only": True}
    cfg = {"model": "gpt-6.1-sol", "reasoning_effort": "max",
           "max_attempts": 1, "max_output_tokens": 16000,
           "recoverable_background": True,
           "public_background_storage_authorized": True}
    registry = {"tasks": {"RESEARCH_LAB_SOL_ANALYSIS": cfg}}
    prompt = "research on public historical evidence only"
    (root / "output" / "transport").mkdir(parents=True, exist_ok=True)
    context_data = gateway.canonical_bytes(ctx)
    (root / "context.json").write_bytes(context_data)
    (root / "prompt.txt").write_text(prompt)
    (root / "effective_registry.json").write_text(json.dumps(registry))
    manifest = {"mission_id": MISSION, "comment_id": TRIGGER,
                "current_main_sha": HEAD,
                "context_sha256": gateway.sha256_bytes(context_data)}
    (root / "context_manifest.json").write_text(json.dumps(manifest))
    payload = gateway.build_request("RESEARCH_LAB_SOL_ANALYSIS", cfg, prompt, ctx)
    payload.update({"background": True, "store": True})
    sha = transport.digest(payload)
    (root / "output" / "transport" / "attempt.json").write_text(
        json.dumps({"contract": "RECOVERABLE_SOL_ATTEMPT_V1",
                    "state": "POST_OUTCOME_UNKNOWN",
                    "request_sha256": sha, "max_paid_posts": 1}))
    (root / "output" / "transport" / "response_handle.json").write_text(
        json.dumps({"contract": "RECOVERABLE_SOL_HANDLE_V1",
                    "state": "GET_ONLY", "request_sha256": sha,
                    "additional_posts_authorized": 0,
                    "response_id": "resp_valid1234"}))


def native(path):
    if path == "actions/runs/" + RUN:
        return {"id": int(RUN), "event": "issue_comment",
                "name": "Research Lab Sol Mission Dispatcher", "head_sha": HEAD,
                "actor": {"login": "Donh91"}}
    if path == "issues/comments/" + TRIGGER:
        return {"body": "[RESEARCH_LAB_SOL] mission=" + MISSION,
                "user": {"login": "Donh91"},
                "issue_url": "https://api.github.com/repos/" + m.REPO + "/issues/1476"}
    if path.startswith("issues/1476/comments?"):
        return [{"id": 19, "user": {"login": "github-actions[bot]"},
                 "body": m.CLAIM_PREFIX + " mission=" + MISSION + " head=" + HEAD +
                 " trigger=" + TRIGGER + " max_usd=3.00"}]
    raise AssertionError(path)


class RecoveryNativeTests(unittest.TestCase):
    def test_exact_native_proof_and_response_hash(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fixture(root)
            proof = m.verify_original(RUN, root, fetch=native)
            self.assertEqual(proof["status"], "AUTHENTICATED_ORIGIN_GET_ONLY")
            self.assertEqual(proof["additional_paid_posts"], 0)
            self.assertEqual(proof["claim_comment_id"], 19)

    def test_original_event_sha_may_precede_source_checkout_but_claim_stays_exact(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fixture(root)
            def event_before_checkout(path):
                row = native(path)
                if path == "actions/runs/" + RUN:
                    row["head_sha"] = "b" * 40
                return row
            proof = m.verify_original(RUN, root, fetch=event_before_checkout)
            self.assertEqual(proof["source_main_sha"], HEAD)
            self.assertEqual(proof["claim_comment_id"], 19)

    def test_forged_actor_or_missing_bot_claim_rejects(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fixture(root)
            def attacker(path):
                result = native(path)
                if path.startswith("issues/1476/comments?"):
                    result[0]["user"]["login"] = "attacker"
                return result
            with self.assertRaisesRegex(ValueError, "CLAIM_NOT_UNIQUE"):
                m.verify_original(RUN, root, fetch=attacker)

    def test_replaced_payload_or_non_public_context_rejects(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fixture(root)
            (root / "prompt.txt").write_text("forged replacement request")
            with self.assertRaisesRegex(ValueError, "API_REQUEST_HASH_MISMATCH"):
                m.verify_original(RUN, root, fetch=native)
            fixture(root)
            ctx=json.loads((root / "context.json").read_text())
            ctx["private_data_included"]=True
            (root / "context.json").write_text(json.dumps(ctx))
            with self.assertRaisesRegex(ValueError, "PUBLIC_SOURCE_OR_HANDLE_INVALID"):
                m.verify_original(RUN, root, fetch=native)

    def test_owner_collect_event_is_strict(self):
        with tempfile.TemporaryDirectory() as td:
            file=Path(td)/"event.json"
            event={"issue":{"number":1476},
                   "comment":{"body":"[RESEARCH_LAB_SOL_COLLECT] origin="+RUN,
                              "author_association":"OWNER",
                              "user":{"login":"Donh91"}}}
            file.write_text(json.dumps(event))
            env={"GITHUB_EVENT_NAME":"issue_comment","GITHUB_ACTOR":"Donh91",
                 "GITHUB_REPOSITORY":m.REPO,"GITHUB_RUN_ATTEMPT":"1"}
            with patch.dict(os.environ,env):
                self.assertEqual(m.parse_owner_collect(file),RUN)
                file.write_text(json.dumps({**event,"comment":{**event["comment"],
                    "body":"[RESEARCH_LAB_SOL_COLLECT] origin="+RUN+"\nunsafe"}}))
                with self.assertRaisesRegex(ValueError, "NOT_AUTHENTICATED"):
                    m.parse_owner_collect(file)
                file.write_text(json.dumps(event))
            with patch.dict(os.environ,{**env,"GITHUB_ACTOR":"imposter"}):
                with self.assertRaisesRegex(ValueError, "NOT_AUTHENTICATED"):
                    m.parse_owner_collect(file)


if __name__ == "__main__":
    unittest.main()
