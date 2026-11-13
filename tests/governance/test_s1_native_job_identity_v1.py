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
              "governance_exact_paths": ["AGENTS.md", "CLAUDE.md"],
              "governance_prefixes": [".github/", ".agents/", "00_FMOS/",
                                      "00_ARCHIVE_CONTROL/", "01_CORE_FRAMEWORK/governance/",
                                      "scripts/governance/s1_", "tests/governance/test_s1_",
                                      "research/api_agent/", "private/", "secrets/", "vault/"],
              "required_job_executed_paths": [
                  "scripts/data_governance/storage_health_gate.py",
                  "tests/data_governance/test_storage_health_gate.py"],
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
        ROOT + "/pulls/9": {"head": {"sha": HEAD}, "base": {"ref": "main"}, "state": "open",
                             "draft": False, "changed_files": 1},
        ROOT + "/pulls/9/files?per_page=100&page=1":
            [{"filename": "README.md", "status": "modified"}],
        ROOT + "/actions/runs?head_sha=" + HEAD + "&event=pull_request&per_page=100&page=1":
            {"total_count": 2, "workflow_runs": [
                {"path": PATH1, "head_sha": HEAD, "event": "pull_request",
                 "id": 123, "run_attempt": 1, "status": "completed", "conclusion": "success",
                 "pull_requests": [{"number": 9, "base": {"ref": "main"}}]},
                {"path": PATH2, "head_sha": HEAD, "event": "pull_request",
                 "id": 124, "run_attempt": 1, "status": "completed", "conclusion": "success",
                 "pull_requests": [{"number": 9, "base": {"ref": "main"}}]}]},
    }
    for rid, name in ((123, "gate"), (124, "storage-health")):
        urls[ROOT + f"/actions/runs/{rid}/attempts/1/jobs?per_page=100&page=1"] = {
            "total_count": 1, "jobs": [
                {"id": rid + 1000, "run_id": rid, "head_sha": HEAD, "name": name,
                 "status": "completed", "conclusion": "success", "steps": [
                    {"name": "Execute tests", "status": "completed", "conclusion": "success",
                     "started_at": "2026-11-13T18:00:00Z",
                     "completed_at": "2026-11-13T18:01:00Z"}]}]}
    for path, jobid in ((PATH1, "gate"), (PATH2, "storage-health")):
        # The source on current main and original PR HEAD must match.
        yaml = ("name: Native test\non: pull_request\njobs:\n  " + jobid +
                ":\n    runs-on: ubuntu-latest\n    steps:\n      - run: python -m unittest\n").encode()
        blob = hashlib.sha1(b"blob " + str(len(yaml)).encode() + b"\0" + yaml).hexdigest()
        for ref in (MAIN, HEAD):
            urls[ROOT + "/contents/" + path + "?ref=" + ref] = {
                "encoding": "base64", "sha": blob, "content": base64.b64encode(yaml).decode()}
    runs = urls[ROOT + "/actions/runs?head_sha=" + HEAD +
                "&event=pull_request&per_page=100&page=1"]["workflow_runs"]
    for run in runs:
        urls[ROOT + "/actions/runs/" + str(run["id"])] = copy.deepcopy(run)
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
        x[ROOT + "/actions/runs/123/attempts/1/jobs?per_page=100&page=1"]["jobs"][0]["name"] = "gate-alias"
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
        x[ROOT + "/actions/runs/123/attempts/1/jobs?per_page=100&page=1"]["jobs"][0]["head_sha"] = "c" * 40
        self.assertEqual(verify(x)["reason"], "WORKFLOW_JOB_ID_UNVERIFIED")

    def test_skipped_job_fails_closed(self):
        x = build_fixture()
        x[ROOT + "/actions/runs/123/attempts/1/jobs?per_page=100&page=1"]["jobs"][0]["conclusion"] = "skipped"
        self.assertEqual(verify(x)["reason"], "REQUIRED_JOB_NOT_SUCCESS")

    def test_unexecuted_test_step_fails_closed(self):
        x = build_fixture()
        x[ROOT + "/actions/runs/123/attempts/1/jobs?per_page=100&page=1"]["jobs"][0]["steps"][0]["conclusion"] = "skipped"
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
        x[ROOT + "/actions/runs/123/attempts/1/jobs?per_page=100&page=1"]["total_count"] = 3
        self.assertEqual(verify(x)["reason"], "NATIVE_INPUT_UNAVAILABLE_OR_INCONSISTENT")

    def test_later_failed_run_blocks_older_green(self):
        x = build_fixture()
        r = x[ROOT + "/actions/runs?head_sha=" + HEAD + "&event=pull_request&per_page=100&page=1"]
        r["workflow_runs"].append({"path": PATH1, "head_sha": HEAD, "event": "pull_request",
                                   "id": 125, "run_attempt": 1,
                                   "status": "completed", "conclusion": "failure",
                                   "pull_requests": [{"number": 9, "base": {"ref": "main"}}]})
        r["total_count"] = 3
        self.assertEqual(verify(x)["reason"], "REQUIRED_WORKFLOW_NOT_SUCCESS")

    def test_missing_file_page_fails_closed(self):
        x = build_fixture()
        x[ROOT + "/pulls/9"]["changed_files"] = 2
        self.assertEqual(verify(x)["reason"], "NATIVE_INPUT_UNAVAILABLE_OR_INCONSISTENT")

    def test_duplicate_pr_filenames_are_not_a_complete_census(self):
        x = build_fixture()
        x[ROOT + "/pulls/9"]["changed_files"] = 2
        x[ROOT + "/pulls/9/files?per_page=100&page=1"] = [
            {"filename": "README.md", "status": "modified"},
            {"filename": "README.md", "status": "modified"}]
        self.assertEqual(verify(x)["reason"], "NATIVE_INPUT_UNAVAILABLE_OR_INCONSISTENT")

    def test_run_for_other_pr_cannot_satisfy_original_pr(self):
        x = build_fixture()
        route = ROOT + "/actions/runs?head_sha=" + HEAD + "&event=pull_request&per_page=100&page=1"
        x[route]["workflow_runs"][0]["pull_requests"] = [
            {"number": 10, "base": {"ref": "feature"}}]
        self.assertEqual(verify(x)["reason"], "PR_RUN_ASSOCIATION_UNVERIFIED")

    def test_yaml_display_name_alias_cannot_impersonate_job_id(self):
        x = build_fixture()
        # The YAML contains both gate and a decoy that displays as gate.
        yaml = b"jobs:\n  gate:\n    runs-on: ubuntu-latest\n  decoy:\n    name: gate\n    runs-on: ubuntu-latest\n"
        blob = hashlib.sha1(b"blob " + str(len(yaml)).encode() + b"\0" + yaml).hexdigest()
        for ref in (HEAD, MAIN):
            x[ROOT + "/contents/" + PATH1 + "?ref=" + ref] = {
                "encoding": "base64", "sha": blob, "content": base64.b64encode(yaml).decode()}
        self.assertEqual(verify(x)["reason"], "WORKFLOW_YAML_JOB_ID_UNVERIFIED")

    def test_attempt_rerun_after_job_read_fails_closed(self):
        x = build_fixture()
        x[ROOT + "/actions/runs/123"]["run_attempt"] = 2
        x[ROOT + "/actions/runs/123"]["conclusion"] = "failure"
        self.assertEqual(verify(x)["reason"], "NATIVE_RUN_ATTEMPT_DRIFT")

    def test_latest_run_census_rechecked_again_after_job_reads(self):
        x = build_fixture()
        route = ROOT + "/actions/runs?head_sha=" + HEAD + "&event=pull_request&per_page=100&page=1"
        count = [0]
        def reader(path):
            if path == route:
                count[0] += 1
                if count[0] > 1:
                    altered = copy.deepcopy(x[path])
                    altered["workflow_runs"][0]["run_attempt"] = 2
                    altered["workflow_runs"][0]["conclusion"] = "failure"
                    return altered
            return copy.deepcopy(x[path])
        self.assertEqual(verify_native_required_jobs(reader, REPO, 9, HEAD, "DOCS_ONLY")["reason"],
                         "NATIVE_RUN_CENSUS_DRIFT")

    def test_pr_workflow_source_mismatch_fails_closed(self):
        x = build_fixture()
        path = ROOT + "/contents/" + PATH1 + "?ref=" + HEAD
        yaml = b"jobs:\n  gate:\n    name: injected\n"
        blob = hashlib.sha1(b"blob " + str(len(yaml)).encode() + b"\0" + yaml).hexdigest()
        x[path] = {"encoding": "base64", "sha": blob,
                   "content": base64.b64encode(yaml).decode()}
        self.assertEqual(verify(x)["reason"], "WORKFLOW_YAML_JOB_ID_UNVERIFIED")

    def test_workflow_source_change_in_docs_lane_fails_closed(self):
        x = build_fixture()
        x[ROOT + "/pulls/9/files?per_page=100&page=1"][0]["filename"] = PATH1
        self.assertEqual(verify(x)["reason"], "REQUIRED_WORKFLOW_SOURCE_CHANGED_BY_PR")

    def test_policy_source_change_in_docs_lane_fails_closed(self):
        x = build_fixture()
        x[ROOT + "/pulls/9/files?per_page=100&page=1"][0]["filename"] = (
            "00_FMOS/S1_REQUIRED_PR_JOBS_POLICY_V1.json")
        self.assertEqual(verify(x)["reason"], "REQUIRED_WORKFLOW_SOURCE_CHANGED_BY_PR")

    def test_verifier_self_change_in_docs_lane_fails_closed(self):
        x = build_fixture()
        x[ROOT + "/pulls/9/files?per_page=100&page=1"][0]["filename"] = (
            "scripts/governance/s1_native_job_identity_v1.py")
        self.assertEqual(verify(x)["reason"], "REQUIRED_WORKFLOW_SOURCE_CHANGED_BY_PR")

    def test_renamed_workflow_source_into_docs_is_blocked(self):
        x = build_fixture()
        x[ROOT + "/pulls/9/files?per_page=100&page=1"][0].update(
            {"filename": "docs/harmless.md", "previous_filename": PATH2,
             "status": "renamed"})
        self.assertEqual(verify(x)["reason"], "REQUIRED_WORKFLOW_SOURCE_CHANGED_BY_PR")

    def test_exact_agents_policy_cannot_pass_as_docs(self):
        x = build_fixture()
        x[ROOT + "/pulls/9/files?per_page=100&page=1"][0]["filename"] = "AGENTS.md"
        self.assertEqual(verify(x)["reason"], "REQUIRED_WORKFLOW_SOURCE_CHANGED_BY_PR")

    def test_governance_canonical_directory_cannot_pass_as_docs(self):
        x = build_fixture()
        x[ROOT + "/pulls/9/files?per_page=100&page=1"][0]["filename"] = (
            "01_CORE_FRAMEWORK/governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md")
        self.assertEqual(verify(x)["reason"], "REQUIRED_WORKFLOW_SOURCE_CHANGED_BY_PR")

    def test_required_job_implemented_file_cannot_pass_as_low_code(self):
        x = build_fixture()
        x[ROOT + "/pulls/9/files?per_page=100&page=1"][0]["filename"] = (
            "scripts/data_governance/storage_health_gate.py")
        self.assertEqual(verify_native_required_jobs(
            lambda path: copy.deepcopy(x[path]), REPO, 9, HEAD, "LOW_CODE")["reason"],
            "POLICY_REQUIRED_JOBS_UNVERIFIED" if False else "REQUIRED_WORKFLOW_SOURCE_CHANGED_BY_PR")

    def test_renamed_policy_file_into_docs_rejected(self):
        x = build_fixture()
        x[ROOT + "/pulls/9/files?per_page=100&page=1"][0].update({
            "filename": "docs/renamed.md", "previous_filename": "AGENTS.md", "status": "renamed"})
        self.assertEqual(verify(x)["reason"], "REQUIRED_WORKFLOW_SOURCE_CHANGED_BY_PR")

    def test_forced_high_class_not_applicable(self):
        self.assertEqual(verify_native_required_jobs(lambda p: {}, REPO, 9, HEAD, "HIGH")["reason"],
                         "INVALID_INPUT")


if __name__ == "__main__":
    unittest.main()
