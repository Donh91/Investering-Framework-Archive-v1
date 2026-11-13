"""Fail-closed source-binding tests for native required-job identity, S1 #1156."""
import base64
import copy
import hashlib
import json
import unittest
from scripts.governance.s1_native_job_identity_v1 import verify_native_required_jobs

REPO = "Donh91/Investering-Framework-Archive-v1"
HEAD = "a" * 40
MAIN = "b" * 40
PATH1 = ".github/workflows/data-architecture-gate.yml"
PATH2 = ".github/workflows/storage-health-gate.yml"
ROOT = "/repos/" + REPO


def build_fixture():
    policy = {"contract": "S1_REQUIRED_PR_JOBS_POLICY_V1",
              "lane_state": "SHADOW", "review_optional_classes": [],
              "classes": {"DOCS_ONLY": [
                  {"workflow_path": PATH1, "job_id": "gate", "event": "pull_request",
                   "executed_test_steps_min": 1},
                  {"workflow_path": PATH2, "job_id": "storage-health", "event": "pull_request",
                   "executed_test_steps_min": 1}]}}
    raw = json.dumps(policy).encode()
    sha = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    urls = {
        ROOT + "/branches/main": {"commit": {"sha": MAIN}},
        ROOT + "/contents/00_FMOS/S1_REQUIRED_PR_JOBS_POLICY_V1.json?ref=" + MAIN:
            {"encoding": "base64", "content": base64.b64encode(raw).decode(), "sha": sha},
        ROOT + "/pulls/9": {"head": {"sha": HEAD}, "state": "open",
                             "draft": False, "changed_files": 1},
        ROOT + "/pulls/9/files?per_page=100&page=1":
            [{"filename": "README.md", "status": "modified"}],
        ROOT + "/actions/runs?head_sha=" + HEAD + "&event=pull_request&per_page=100&page=1":
            {"total_count": 2, "workflow_runs": [
                {"path": PATH1, "head_sha": HEAD, "event": "pull_request",
                 "id": 123, "run_attempt": 1, "status": "completed", "conclusion": "success"},
                {"path": PATH2, "head_sha": HEAD, "event": "pull_request",
                 "id": 124, "run_attempt": 1, "status": "completed", "conclusion": "success"}]},
    }
    for rid, name in ((123, "gate"), (124, "storage-health")):
        urls[ROOT + f"/actions/runs/{rid}/jobs?per_page=100&page=1"] = {
            "total_count": 1, "jobs": [
                {"id": rid + 1000, "run_id": rid, "head_sha": HEAD, "name": name,
                 "status": "completed", "conclusion": "success", "steps": [
                    {"name": "Execute tests", "status": "completed", "conclusion": "success",
                     "started_at": "2026-11-13T18:00:00Z",
                     "completed_at": "2026-11-13T18:01:00Z"}]}]}
    return urls


def verify(urls):
    def native_get(path):
        return copy.deepcopy(urls[path])
    return verify_native_required_jobs(native_get, REPO, 9, HEAD, "DOCS_ONLY")


class NativeIdentityTests(unittest.TestCase):
    def test_all_exact_native_job_triplets_pass_advisory_only(self):
        result = verify(build_fixture())
        self.assertEqual(result["status"], "JOB_IDENTITY_PASS_ADVISORY")
        self.assertEqual({(x["workflow_path"], x["job_id"], x["head"])
                          for x in result["required_jobs"]},
                         {(PATH1, "gate", HEAD), (PATH2, "storage-health", HEAD)})
        self.assertFalse(result["authorized"])
        self.assertFalse(result["externally_authenticated"])
        self.assertFalse(result["test_commands_and_logs_verified"])

    def test_misnamed_green_check_not_job_identity(self):
        x = build_fixture()
        x[ROOT + "/actions/runs/123/jobs?per_page=100&page=1"]["jobs"][0]["name"] = "gate-alias"
        self.assertEqual(verify(x)["reason"], "WORKFLOW_JOB_ID_UNVERIFIED")

    def test_wrong_workflow_path_fails_closed(self):
        x = build_fixture()
        x[ROOT + "/actions/runs?head_sha=" + HEAD + "&event=pull_request&per_page=100&page=1"]["workflow_runs"][0]["path"] = PATH2
        self.assertEqual(verify(x)["reason"], "REQUIRED_WORKFLOW_MISSING")

    def test_stale_run_head_fails_closed(self):
        x = build_fixture()
        x[ROOT + "/actions/runs?head_sha=" + HEAD + "&event=pull_request&per_page=100&page=1"]["workflow_runs"][0]["head_sha"] = "c" * 40
        self.assertEqual(verify(x)["reason"], "REQUIRED_WORKFLOW_MISSING")

    def test_stale_native_job_head_fails_closed(self):
        x = build_fixture()
        x[ROOT + "/actions/runs/123/jobs?per_page=100&page=1"]["jobs"][0]["head_sha"] = "c" * 40
        self.assertEqual(verify(x)["reason"], "WORKFLOW_JOB_ID_UNVERIFIED")

    def test_skipped_job_fails_closed(self):
        x = build_fixture()
        x[ROOT + "/actions/runs/123/jobs?per_page=100&page=1"]["jobs"][0]["conclusion"] = "skipped"
        self.assertEqual(verify(x)["reason"], "REQUIRED_JOB_NOT_SUCCESS")

    def test_unexecuted_test_step_fails_closed(self):
        x = build_fixture()
        x[ROOT + "/actions/runs/123/jobs?per_page=100&page=1"]["jobs"][0]["steps"][0]["conclusion"] = "skipped"
        self.assertEqual(verify(x)["reason"], "REQUIRED_JOB_STEPS_UNVERIFIED")

    def test_missing_policy_git_blob_binding_fails_closed(self):
        x = build_fixture()
        x[ROOT + "/contents/00_FMOS/S1_REQUIRED_PR_JOBS_POLICY_V1.json?ref=" + MAIN]["sha"] = "0" * 40
        self.assertEqual(verify(x)["reason"], "POLICY_BLOB_UNVERIFIED")

    def test_main_source_drift_fails_closed(self):
        x = build_fixture()
        count = [0]
        def reader(path):
            if path == ROOT + "/branches/main":
                count[0] += 1
                return {"commit": {"sha": MAIN if count[0] == 1 else "c" * 40}}
            return copy.deepcopy(x[path])
        self.assertEqual(verify_native_required_jobs(reader, REPO, 9, HEAD, "DOCS_ONLY")["reason"],
                         "MAIN_DRIFT_RECHECK")

    def test_pr_head_drift_fails_closed(self):
        x = build_fixture()
        count = [0]
        def reader(path):
            if path == ROOT + "/pulls/9":
                count[0] += 1
                if count[0] > 1:
                    return {"head": {"sha": "c" * 40}}
            return copy.deepcopy(x[path])
        self.assertEqual(verify_native_required_jobs(reader, REPO, 9, HEAD, "DOCS_ONLY")["reason"],
                         "PR_HEAD_OR_STATE_DRIFT")

    def test_incomplete_job_pagination_fails_closed(self):
        x = build_fixture()
        x[ROOT + "/actions/runs/123/jobs?per_page=100&page=1"]["total_count"] = 3
        self.assertEqual(verify(x)["reason"], "NATIVE_INPUT_UNAVAILABLE_OR_INCONSISTENT")

    def test_later_failed_run_blocks_older_green(self):
        x = build_fixture()
        r = x[ROOT + "/actions/runs?head_sha=" + HEAD + "&event=pull_request&per_page=100&page=1"]
        r["workflow_runs"].append({"path": PATH1, "head_sha": HEAD, "event": "pull_request",
                                   "id": 125, "run_attempt": 1,
                                   "status": "completed", "conclusion": "failure"})
        r["total_count"] = 3
        self.assertEqual(verify(x)["reason"], "REQUIRED_WORKFLOW_NOT_SUCCESS")

    def test_missing_file_page_fails_closed(self):
        x = build_fixture()
        x[ROOT + "/pulls/9"]["changed_files"] = 2
        self.assertEqual(verify(x)["reason"], "NATIVE_INPUT_UNAVAILABLE_OR_INCONSISTENT")

    def test_forced_high_class_not_applicable(self):
        self.assertEqual(verify_native_required_jobs(lambda p: {}, REPO, 9, HEAD, "HIGH")["reason"],
                         "INVALID_INPUT")


if __name__ == "__main__":
    unittest.main()
