"""S1 C1/C2: read-only native GitHub required-job identity proof, SHADOW ONLY.

Authored for original S1 #1156 / draft #2092. The workflow path and YAML job
identifier must BOTH match the main policy for the same exact pull-request HEAD.
A success-looking check name, self-attested JSON or bot comment is NOT proof.
This module cannot authorize or execute a merge.
"""
from __future__ import annotations

import base64
import json
import os
import re
from urllib.parse import quote
from urllib.request import Request, urlopen

SHA40 = re.compile(r"^[0-9a-f]{40}$")
PATH = "00_FMOS/S1_REQUIRED_PR_JOBS_POLICY_V1.json"
MAX_PAGES = 10


class GithubNativeRead:
    """Read-only GitHub REST transport; response content is never logged."""
    def __init__(self, token=None):
        self.token = token if token is not None else os.environ.get("GITHUB_TOKEN", "")

    def __call__(self, route):
        if not route.startswith("/") or ".." in route:
            raise ValueError("UNSAFE_GITHUB_ROUTE")
        headers = {"Accept": "application/vnd.github+json",
                   "X-GitHub-Api-Version": "2022-11-28",
                   "User-Agent": "S1-native-job-identity-v1"}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        req = Request("https://api.github.com" + route, headers=headers, method="GET")
        with urlopen(req, timeout=20) as resp:
            return json.load(resp)


def _hold(reason, **extra):
    return {"contract": "S1_NATIVE_REQUIRED_JOB_IDENTITY_V1",
            "status": "HOLD", "reason": reason,
            "authorized": False, "externally_authenticated": False, **extra}


def _page_all(read, root, collection, max_count=1000):
    records = []
    expected_total = None
    for page in range(1, MAX_PAGES + 1):
        suffix = "&" if "?" in root else "?"
        result = read(root + suffix + "per_page=100&page=" + str(page))
        if not isinstance(result, dict) or type(result.get("total_count")) is not int:
            raise ValueError("NATIVE_PAGINATION_UNVERIFIED")
        if expected_total is None:
            expected_total = result["total_count"]
        if result["total_count"] != expected_total or expected_total > max_count:
            raise ValueError("NATIVE_PAGINATION_UNVERIFIED")
        chunk = result.get(collection)
        if not isinstance(chunk, list) or len(chunk) > 100:
            raise ValueError("NATIVE_PAGINATION_UNVERIFIED")
        records += chunk
        if len(records) >= expected_total:
            if len(records) != expected_total:
                raise ValueError("NATIVE_PAGINATION_UNVERIFIED")
            return records
        if len(chunk) != 100:
            raise ValueError("NATIVE_PAGINATION_UNVERIFIED")
    raise ValueError("NATIVE_PAGINATION_UNVERIFIED")


def _page_files(read, root, expected_count):
    if type(expected_count) is not int or not 0 < expected_count <= 3000:
        raise ValueError("PR_FILES_COUNT_UNVERIFIED")
    files = []
    for page in range(1, 31):
        chunk = read(root + "?per_page=100&page=" + str(page))
        if not isinstance(chunk, list) or len(chunk) > 100:
            raise ValueError("PR_FILES_PAGINATION_UNVERIFIED")
        files.extend(chunk)
        if len(files) >= expected_count:
            if len(files) != expected_count:
                raise ValueError("PR_FILES_PAGINATION_UNVERIFIED")
            return files
        if len(chunk) != 100:
            raise ValueError("PR_FILES_PAGINATION_UNVERIFIED")
    raise ValueError("PR_FILES_PAGINATION_UNVERIFIED")


def verify_native_required_jobs(read, repo, pr_number, head, release_class):
    """Perform native GETs, not checks on a caller-fabricated evidence object.

    PASS proves the narrow path/job/HEAD identity and executed *named* steps,
    not the semantic correctness of tests or an authorization to release.
    An existing S1 operator must separately check job logs, exact source
    workflow commands, changes, privacy, reviews, native rules and recovery.
    """
    if (not isinstance(repo, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo)
            or type(pr_number) is not int or pr_number < 1
            or not isinstance(head, str) or not SHA40.fullmatch(head)
            or release_class not in ("DOCS_ONLY", "LOW_CODE")):
        return _hold("INVALID_INPUT")
    url = "/repos/" + repo
    try:
        main = read(url + "/branches/main")
        main_sha = main["commit"]["sha"]
        if not SHA40.fullmatch(main_sha):
            return _hold("MAIN_UNVERIFIED")
        pinned = read(url + "/contents/" + PATH + "?ref=" + main_sha)
        if pinned.get("encoding") != "base64" or not isinstance(pinned.get("content"), str):
            return _hold("POLICY_BLOB_UNVERIFIED")
        raw = base64.b64decode(pinned["content"], validate=False)
        # Exact Git blob verification is mandatory, not caller-supplied sha.
        import hashlib
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        if pinned.get("sha") != blob:
            return _hold("POLICY_BLOB_UNVERIFIED")
        policy = json.loads(raw)
        if policy.get("contract") != "S1_REQUIRED_PR_JOBS_POLICY_V1":
            return _hold("POLICY_CONTRACT_UNVERIFIED")
        # The current main is SHADOW. This probe does not activate a release.
        expected = policy["classes"][release_class]
        if not isinstance(expected, list) or not expected:
            return _hold("POLICY_REQUIRED_JOBS_UNVERIFIED")
        keys = set()
        for row in expected:
            if (not isinstance(row, dict)
                    or not isinstance(row.get("workflow_path"), str)
                    or not row["workflow_path"].startswith(".github/workflows/")
                    or not isinstance(row.get("job_id"), str) or not row["job_id"]
                    or row.get("event") != "pull_request"
                    or type(row.get("executed_test_steps_min")) is not int
                    or row["executed_test_steps_min"] < 1):
                return _hold("POLICY_REQUIRED_JOBS_UNVERIFIED")
            key = (row["workflow_path"], row["job_id"])
            if key in keys:
                return _hold("POLICY_DUPLICATE_JOB")
            keys.add(key)
        pr = read(url + "/pulls/" + str(pr_number))
        if pr["head"]["sha"] != head or pr.get("state") != "open" or pr.get("draft") is not False:
            return _hold("PR_HEAD_OR_STATE_DRIFT")
        files = _page_files(read, url + "/pulls/" + str(pr_number) + "/files", pr.get("changed_files"))
        if not all(isinstance(x, dict) and isinstance(x.get("filename"), str)
                   and isinstance(x.get("status"), str) for x in files):
            return _hold("PR_FILES_METADATA_UNVERIFIED")
        runs = _page_all(read, url + "/actions/runs?head_sha=" + head +
                         "&event=pull_request", "workflow_runs")
        proofs = []
        for item in expected:
            path, job_id = item["workflow_path"], item["job_id"]
            matching_runs = [x for x in runs if isinstance(x, dict)
                             and x.get("path") == path and x.get("head_sha") == head
                             and x.get("event") == "pull_request"
                             and type(x.get("id")) is int]
            if not matching_runs:
                return _hold("REQUIRED_WORKFLOW_MISSING", workflow_path=path, job_id=job_id)
            newest = max(matching_runs, key=lambda x: (x["id"], x.get("run_attempt", 0)))
            if newest.get("status") != "completed" or newest.get("conclusion") != "success":
                return _hold("REQUIRED_WORKFLOW_NOT_SUCCESS", workflow_path=path, job_id=job_id)
            rid = newest["id"]
            jobs = _page_all(read, url + "/actions/runs/" + str(rid) + "/jobs", "jobs")
            match = [x for x in jobs if isinstance(x, dict) and x.get("name") == job_id
                     and x.get("run_id") == rid and x.get("head_sha") == head
                     and type(x.get("id")) is int]
            if len(match) != 1:
                return _hold("WORKFLOW_JOB_ID_UNVERIFIED", workflow_path=path, job_id=job_id)
            job = match[0]
            if job.get("status") != "completed" or job.get("conclusion") != "success":
                return _hold("REQUIRED_JOB_NOT_SUCCESS", workflow_path=path, job_id=job_id)
            steps = job.get("steps")
            if not isinstance(steps, list):
                return _hold("REQUIRED_JOB_STEPS_UNVERIFIED", workflow_path=path, job_id=job_id)
            meaningful = [s for s in steps if isinstance(s, dict)
                          and isinstance(s.get("name"), str)
                          and not s["name"].startswith(("Run actions/", "Set up job", "Complete job"))
                          and s.get("status") == "completed" and s.get("conclusion") == "success"
                          and s.get("started_at") and s.get("completed_at")]
            if len(meaningful) < item["executed_test_steps_min"]:
                return _hold("REQUIRED_JOB_STEPS_UNVERIFIED", workflow_path=path, job_id=job_id)
            proofs.append({"workflow_path": path, "job_id": job_id, "head": head,
                           "run_id": rid, "native_job_id": job["id"],
                           "observed_named_steps": len(meaningful)})
        if read(url + "/pulls/" + str(pr_number))["head"]["sha"] != head:
            return _hold("PR_HEAD_OR_STATE_DRIFT")
        if read(url + "/branches/main")["commit"]["sha"] != main_sha:
            return _hold("MAIN_DRIFT_RECHECK")
        return {"contract": "S1_NATIVE_REQUIRED_JOB_IDENTITY_V1",
                "status": "JOB_IDENTITY_PASS_ADVISORY",
                "authorized": False, "externally_authenticated": False,
                "test_commands_and_logs_verified": False,
                "main_sha": main_sha, "policy_blob_sha": blob,
                "head": head, "required_jobs": proofs,
                "next_gate": "NATIVE_WORKFLOW_SOURCE_AND_JOB_LOGS_PLUS_REVIEW_PRIVACY_RULES_RECOVERY"}
    except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError):
        return _hold("NATIVE_INPUT_UNAVAILABLE_OR_INCONSISTENT")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--pr", required=True, type=int)
    ap.add_argument("--head", required=True)
    ap.add_argument("--class", dest="release_class", required=True,
                    choices=("DOCS_ONLY", "LOW_CODE"))
    opts = ap.parse_args()
    result = verify_native_required_jobs(
        GithubNativeRead(), opts.repo, opts.pr, opts.head, opts.release_class)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "JOB_IDENTITY_PASS_ADVISORY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
