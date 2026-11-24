"""D2 shadow diagnostic for one required workflow/job at an exact PR head.

No I/O, permissions, retries or release authority. Complete native inputs must be
independently authenticated. An advisory diagnosis never replaces required CI.
"""
from dataclasses import dataclass
import re

SHA = re.compile(r"[0-9a-f]{40}\Z")


@dataclass(frozen=True)
class Diagnosis:
    state: str
    route: str
    run_id: int | None = None
    attempt: int | None = None
    job_id: int | None = None
    failed_steps: tuple = ()
    head: str | None = None
    workflow_path: str | None = None
    job_name: str | None = None
    repo_id: int | None = None

    @property
    def release_authorized(self):
        return False

    @property
    def fingerprint(self):
        return (self.repo_id, self.head, self.workflow_path, self.job_name, self.state,
                self.run_id, self.attempt, self.job_id, self.failed_steps)


def positive_int(value):
    return type(value) is int and value > 0


def diagnose(*, head, repo_id, workflow_path, job_name, must_run_steps,
             runs, runs_complete, jobs_by_run, jobs_complete, gate_stale=False):
    """Never infer code failure, approval reason or permission from conclusion alone."""
    def result(state, route, run=None, job=None, failed=()):
        return Diagnosis(state, route, (run or {}).get("id"),
                         (run or {}).get("run_attempt"), (job or {}).get("id"), tuple(failed),
                         head if isinstance(head, str) else None,
                         workflow_path if isinstance(workflow_path, str) else None,
                         job_name if isinstance(job_name, str) else None,
                         repo_id if positive_int(repo_id) else None)

    unknown = lambda: result("EVIDENCE_UNPROVEN", "READ_NATIVE_EVIDENCE")
    if (not isinstance(head, str) or not SHA.fullmatch(head) or not positive_int(repo_id)
            or not isinstance(workflow_path, str) or not workflow_path.startswith(".github/workflows/")
            or not isinstance(job_name, str) or not job_name
            or not isinstance(must_run_steps, (tuple, list)) or not must_run_steps
            or not all(isinstance(s, str) and s for s in must_run_steps)
            or len(set(must_run_steps)) != len(must_run_steps)
            or runs_complete is not True or not isinstance(runs, list)
            or not isinstance(jobs_by_run, dict) or not isinstance(jobs_complete, dict)
            or type(gate_stale) is not bool):
        return unknown()
    kept = []
    for r in runs:
        if not isinstance(r, dict):
            return unknown()
        if r.get("path") != workflow_path:
            if not isinstance(r.get("path"), str):
                return unknown()
            continue
        if r.get("head_sha") != head or r.get("event") != "pull_request":
            if not r.get("head_sha") or not r.get("event"):
                return unknown()
            continue
        for field in ("repository", "head_repository"):
            if not isinstance(r.get(field), dict) or not positive_int(r[field].get("id")):
                return unknown()
        if any(r[k]["id"] != repo_id for k in ("repository", "head_repository")):
            continue
        if not all(positive_int(r.get(k)) for k in ("id", "run_number", "run_attempt")):
            return unknown()
        kept.append(r)
    if not kept:
        return result("NO_BOUND_RUN", "DIAGNOSE_TRIGGER")
    # Same workflow run_number must not point to multiple run identities.
    if (len({(r["run_number"], r["id"]) for r in kept}) != len({r["run_number"] for r in kept})
            or len({(r["run_number"], r["id"]) for r in kept}) != len({r["id"] for r in kept})):
        return unknown()
    latest = max(kept, key=lambda r: (r["run_number"], r["run_attempt"]))
    if sum((r["run_number"], r["run_attempt"]) == (latest["run_number"], latest["run_attempt"]) for r in kept) != 1:
        return unknown()
    rid, att = latest["id"], latest["run_attempt"]
    status, conclusion = latest.get("status"), latest.get("conclusion")
    if status in ("queued", "in_progress", "waiting", "requested", "pending"):
        return result("RUN_PENDING", "WAIT_FOR_NATIVE_COMPLETION", latest)
    if status != "completed" or not isinstance(conclusion, str):
        return unknown()
    key = (rid, att)
    if jobs_complete.get(key) is not True or not isinstance(jobs_by_run.get(key), list):
        return result("JOBS_UNPROVEN", "READ_NATIVE_EVIDENCE", latest)
    jobs = jobs_by_run[key]
    if any(not isinstance(j, dict) or j.get("run_id") != rid or j.get("run_attempt") != att
           or j.get("head_sha") != head or not positive_int(j.get("id"))
           or not isinstance(j.get("name"), str) for j in jobs):
        return result("JOB_BINDING_UNPROVEN", "READ_NATIVE_EVIDENCE", latest)
    if len({j["id"] for j in jobs}) != len(jobs):
        return result("JOB_BINDING_UNPROVEN", "READ_NATIVE_EVIDENCE", latest)
    if conclusion == "action_required":
        return result("ACTION_REQUIRED_NO_JOBS" if not jobs else "ACTION_REQUIRED",
                      "INSPECT_NATIVE_APPROVAL_OR_POLICY", latest)
    if conclusion in ("startup_failure", "timed_out", "cancelled", "stale"):
        return result("RUN_INTERRUPTED", "DIAGNOSE_INFRA_OR_CANCELLATION", latest)
    matches = [j for j in jobs if j["name"] == job_name]
    if len(matches) != 1:
        return result("JOB_ABSENT" if not matches else "JOB_AMBIGUOUS",
                      "DIAGNOSE_JOB_SELECTION" if not matches else "READ_NATIVE_EVIDENCE", latest)
    job = matches[0]
    if job.get("status") != "completed":
        return result("JOB_NOT_COMPLETED", "READ_NATIVE_EVIDENCE", latest, job)
    jc = job.get("conclusion")
    if jc == "action_required":
        return result("ACTION_REQUIRED", "INSPECT_NATIVE_APPROVAL_OR_POLICY", latest, job)
    if jc in ("startup_failure", "timed_out", "cancelled", "stale"):
        return result("JOB_INTERRUPTED", "DIAGNOSE_INFRA_OR_CANCELLATION", latest, job)
    steps = job.get("steps")
    if (not isinstance(steps, list) or any(not isinstance(s, dict) or not isinstance(s.get("name"), str) for s in steps)
            or any(sum(s["name"] == n for s in steps) > 1 for n in must_run_steps)):
        return result("STEPS_UNPROVEN", "READ_NATIVE_EVIDENCE", latest, job)
    failed = tuple(sorted(s["name"] for s in steps if s.get("conclusion") == "failure"))
    if jc == "failure":
        return result("EXECUTED_STEP_FAILURE" if failed else "JOB_FAILURE_UNATTRIBUTED",
                      "INSPECT_FAILED_STEP_LOG" if failed else "INSPECT_NATIVE_JOB_LOG", latest, job, failed)
    if jc != "success" or conclusion != "success":
        return result("NON_SUCCESS", "DIAGNOSE_NATIVE_CONCLUSION", latest, job)
    by_name = {s["name"]: s for s in steps}
    if any(by_name.get(n, {}).get("status") != "completed" or by_name.get(n, {}).get("conclusion") != "success"
           for n in must_run_steps):
        return result("REQUIRED_STEP_NOT_PROVEN", "DIAGNOSE_JOB_SELECTION", latest, job)
    if gate_stale:
        return result("GATE_STALE", "ASSESS_OWNER_BRANCH_UPDATE", latest, job)
    return result("REQUIRED_JOB_EVIDENCE_PASS", "CONTINUE_EXISTING_GATES", latest, job)
