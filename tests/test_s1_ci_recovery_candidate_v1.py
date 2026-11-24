import unittest
from copy import deepcopy
from scripts.research.s1_ci_recovery_candidate_v1 import diagnose

HEAD = "7e03fd4b9650c40e658ba566361d9c63c1af15e0"
PATH = ".github/workflows/data-architecture-gate.yml"


def world():
    run = dict(id=45241495015, run_number=12, run_attempt=1, path=PATH, head_sha=HEAD,
               event="pull_request", repository={"id": 7}, head_repository={"id": 7},
               status="completed", conclusion="success")
    job = dict(id=101, run_id=run["id"], run_attempt=1, head_sha=HEAD, name="gate", status="completed",
               conclusion="success", steps=[dict(name="validate", status="completed", conclusion="success")])
    key = (run["id"], 1)
    return dict(head=HEAD, repo_id=7, workflow_path=PATH, job_name="gate", must_run_steps=["validate"],
                runs=[run], runs_complete=True, jobs_by_run={key: [job]}, jobs_complete={key: True})


class D2Test(unittest.TestCase):
    def check(self, w, expected):
        d = diagnose(**w)
        self.assertEqual(d.state, expected)
        self.assertIs(d.release_authorized, False)
        return d

    def test_pass_and_stale(self):
        w = world()
        self.check(w, "REQUIRED_JOB_EVIDENCE_PASS")
        self.check(w | {"gate_stale": True}, "GATE_STALE")

    def test_observed_2314_shape(self):
        w = world()
        w["runs"][0]["conclusion"] = "action_required"
        w["jobs_by_run"][(45241495015, 1)] = []
        d = self.check(w, "ACTION_REQUIRED_NO_JOBS")
        self.assertEqual(d.route, "INSPECT_NATIVE_APPROVAL_OR_POLICY")
        w["jobs_complete"][(45241495015, 1)] = False
        self.check(w, "JOBS_UNPROVEN")

    def test_wrong_or_missing_identity(self):
        for field, val in [("head_sha", "a"*40), ("event", "workflow_dispatch"),
                           ("repository", {"id": 8}), ("head_repository", {"id": 8})]:
            w = world(); w["runs"][0][field] = val
            with self.subTest(field=field): self.check(w, "NO_BOUND_RUN")
        for field in ("repository", "head_repository", "run_attempt", "path"):
            w = world(); del w["runs"][0][field]
            with self.subTest(field=field): self.check(w, "EVIDENCE_UNPROVEN")

    def test_latest_attempt_only(self):
        w = world(); newer = deepcopy(w["runs"][0]); newer["run_attempt"] = 2
        w["runs"].append(newer)
        self.check(w, "JOBS_UNPROVEN")
        w["jobs_complete"][(newer["id"], 2)] = True
        w["jobs_by_run"][(newer["id"], 2)] = w["jobs_by_run"][(newer["id"], 1)]
        self.check(w, "JOB_BINDING_UNPROVEN")

    def test_interruption_not_code_failure(self):
        for c in ("startup_failure", "cancelled", "timed_out", "stale"):
            w = world(); w["runs"][0]["conclusion"] = c
            with self.subTest(c=c): self.check(w, "RUN_INTERRUPTED")
        w = world(); w["runs"][0]["status"] = "queued"
        self.check(w, "RUN_PENDING")

    def test_failure_needs_log(self):
        w = world(); w["runs"][0]["conclusion"] = "failure"
        j = w["jobs_by_run"][(45241495015, 1)][0]; j["conclusion"] = "failure"
        self.check(w, "JOB_FAILURE_UNATTRIBUTED")
        j["steps"][0]["conclusion"] = "failure"
        d = self.check(w, "EXECUTED_STEP_FAILURE")
        self.assertEqual(d.failed_steps, ("validate",))
        self.assertEqual(d.route, "INSPECT_FAILED_STEP_LOG")

    def test_skipped_and_ambiguous(self):
        w = world(); jobs = w["jobs_by_run"][(45241495015, 1)]; j = jobs[0]
        j["steps"][0]["conclusion"] = "skipped"
        self.check(w, "REQUIRED_STEP_NOT_PROVEN")
        j["steps"][0]["conclusion"] = "success"; j["steps"].append(deepcopy(j["steps"][0]))
        self.check(w, "STEPS_UNPROVEN")
        j["steps"].pop(); jobs.append(dict(j, id=102))
        self.check(w, "JOB_AMBIGUOUS")

    def test_incomplete_and_duplicate(self):
        w = world(); self.check(w | {"runs_complete": False}, "EVIDENCE_UNPROVEN")
        self.check(w | {"must_run_steps": []}, "EVIDENCE_UNPROVEN")
        w["runs"].append(deepcopy(w["runs"][0])); self.check(w, "EVIDENCE_UNPROVEN")
        w = world(); w["jobs_by_run"][(45241495015, 1)] = []
        self.check(w, "JOB_ABSENT")


if __name__ == "__main__":
    unittest.main()
