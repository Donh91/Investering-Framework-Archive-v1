"""Negative controls for original S1 native UI owner-attestation candidate."""
import copy
import json
from pathlib import Path
import unittest

from scripts.governance.s1_owner_ui_attestation_v1 import (
    CONTRACT, REPO, classify_native_ui_comment,
)

H = "a" * 40
P = "b" * 40
DECISION = "APPROVE_STAGED_S"
ID = 123456

def native_fixture():
    return {
        "id": ID,
        "html_url": f"https://github.com/{REPO}/pull/2089#issuecomment-{ID}",
        "user": {"login": "Donh91", "type": "User"},
        "author_association": "OWNER",
        "performed_via_github_app": None,
        "created_at": "2026-11-12T12:00:00Z",
        "updated_at": "2026-11-12T12:00:00Z",
        "body": (
            "S1_OWNER_UI_RELEASE_ATTESTATION_v1\n"
            f"repo={REPO}\n"
            "pr=2089\n"
            f"head={H}\n"
            f"policy_blob={P}\n"
            f"decision={DECISION}"
        ),
    }

def check(rec, **kwargs):
    return classify_native_ui_comment(
        rec,
        pr_number=kwargs.get("pr_number", 2089),
        head_sha=kwargs.get("head_sha", H),
        policy_blob_sha=kwargs.get("policy_blob_sha", P),
        decision=kwargs.get("decision", DECISION),
    )

class NativeUI(unittest.TestCase):
    def test_ui_looking_comment_is_never_authorization(self):
        got = check(native_fixture())
        self.assertEqual(got["contract"], CONTRACT)
        self.assertTrue(got["status"].startswith("UI_COMMENT_CANDIDATE"))
        self.assertFalse(got["authorized"])
        self.assertFalse(got["externally_authenticated"])
        self.assertEqual(len(got["body_sha256"]), 64)

    def test_real_observed_chatgpt_app_comment_must_not_authorize(self):
        x = native_fixture()
        x["performed_via_github_app"] = {"slug": "chatgpt-codex-connector"}
        self.assertEqual(check(x)["reason"], "APP_AUTHORED_OR_UNVERIFIED")
        del x["performed_via_github_app"]
        self.assertEqual(check(x)["reason"], "APP_AUTHORED_OR_UNVERIFIED")

    def test_other_author_or_bad_login(self):
        x = native_fixture(); x["user"]["login"] = "other"
        self.assertEqual(check(x)["reason"], "OWNER_IDENTITY_NOT_PROVEN")
        x = native_fixture(); x["author_association"] = "NONE"
        self.assertEqual(check(x)["reason"], "OWNER_IDENTITY_NOT_PROVEN")

    def test_wrong_requested_head_and_policy_sha_are_rejected(self):
        self.assertEqual(check(native_fixture(), head_sha="c"*40)["reason"],
                         "OWNER_DECISION_SCOPE_OR_EXACT_HEAD_MISMATCH")
        self.assertEqual(check(native_fixture(), policy_blob_sha="d"*40)["reason"],
                         "OWNER_DECISION_SCOPE_OR_EXACT_HEAD_MISMATCH")

    def test_body_cannot_change_variant_or_add_freeform_approval(self):
        x = native_fixture()
        x["body"] += "\nAPPROVE EVERYTHING"
        self.assertEqual(check(x)["reason"], "OWNER_DECISION_SCOPE_OR_EXACT_HEAD_MISMATCH")
        x = native_fixture(); x["body"] = x["body"].replace("STAGED_S", "HIGH_IMPACT")
        self.assertEqual(check(x)["reason"], "OWNER_DECISION_SCOPE_OR_EXACT_HEAD_MISMATCH")

    def test_bounded_issue_location_can_be_used(self):
        x = native_fixture()
        x["html_url"] = f"https://github.com/{REPO}/issues/1156#issuecomment-{ID}"
        self.assertTrue(check(x)["status"].startswith("UI_COMMENT_CANDIDATE"))

    def test_external_repository_or_wrong_comment_id_rejected(self):
        x = native_fixture(); x["html_url"] = f"https://github.com/other/repo/issues/1156#issuecomment-{ID}"
        self.assertEqual(check(x)["reason"], "COMMENT_LOCATION_UNVERIFIED")
        x = native_fixture(); x["html_url"] += "0"
        self.assertEqual(check(x)["reason"], "COMMENT_LOCATION_UNVERIFIED")

    def test_missing_or_reversed_native_timestamps_rejected(self):
        x = native_fixture(); x["updated_at"] = "2026-11-12T11:00:00Z"
        self.assertEqual(check(x)["reason"], "COMMENT_CLOCK_UNVERIFIED")
        x = native_fixture(); del x["updated_at"]
        self.assertEqual(check(x)["reason"], "COMMENT_CLOCK_UNVERIFIED")

    def test_malformed_json_never_authorizes(self):
        for x in (None, [], "ok", {}, {"performed_via_github_app": None}):
            with self.subTest(x=x):
                self.assertFalse(check(x)["authorized"])

    def test_ui_comment_from_api_shape_roundtrip_is_a_candidate_only(self):
        obj = json.loads(json.dumps(native_fixture()))
        self.assertTrue(check(obj)["status"].startswith("UI_COMMENT_CANDIDATE"))
        self.assertFalse(check(obj)["externally_authenticated"])

class RequiredJobsManifest(unittest.TestCase):
    def test_main_target_manifest_has_unique_native_workflow_job_tuples(self):
        root = Path(__file__).resolve().parents[2]
        manifest = json.loads(
            (root/"00_FMOS/S1_REQUIRED_PR_JOBS_POLICY_V1.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["contract"], "S1_REQUIRED_PR_JOBS_POLICY_V1")
        self.assertEqual(set(manifest["classes"]), {"DOCS_ONLY", "LOW_CODE"})
        for cls, jobs in manifest["classes"].items():
            with self.subTest(cls=cls):
                self.assertGreaterEqual(len(jobs), 2)
                ids = []
                for job in jobs:
                    self.assertEqual(job["event"], "pull_request")
                    self.assertGreater(job["executed_test_steps_min"], 0)
                    path = job["workflow_path"]
                    self.assertTrue(path.startswith(".github/workflows/"))
                    workflow = (root/path).read_text(encoding="utf-8")
                    self.assertIn("pull_request:", workflow)
                    self.assertIn("  " + job["job_id"] + ":", workflow)
                    ids.append((path, job["job_id"]))
                self.assertEqual(len(ids), len(set(ids)))
