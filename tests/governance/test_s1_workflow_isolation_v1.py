"""S1 workflow isolation guard (AGENTS.md section 0.2e exclusions 1 and 3, section 0.2f "isolate instead of exclude").

The derivation lives in scripts/governance/s1_workflow_isolation_derive_v1.py (its docstring describes every list).
It is computed live: here for this tree, and by S1 at the PR head and at main (the union) for lane eligibility.

00_FMOS/S1_WORKFLOW_ISOLATION_V1.json is the pinned job-level view. This test keeps it EQUAL to the derivation for
every key it carries:
- secret_jobs, writer_jobs, token_ref_jobs: the privileged jobs;
- pr_write_jobs: jobs that can run on pull_request with a write-scoped token (or the default token). Shrink-only debt;
- secret_on_pr_jobs: jobs that receive a secret and can run on pull_request. Shrink-only debt;
- gate_isolation: LIVE only when the privacy scan and the execution-truth check run in their own isolated jobs;
- unknown_step_jobs, privileged_artifact_edges: shrink-only debt; action_refs: frozen;
- pr_persisted_write_credential_jobs: always a subset of pr_write_jobs.
These change only when .github/ changes, which is owner-gated anyway.

The six path lists (derive.PATH_LIST_KEYS: what secret and writer jobs execute, the non-code files they name, and
the files with an unresolved dynamic edge) are NOT in the file. They are derived at the head, so a PR that adds a
file which a secret job runs needs no edit of the pinned file (the Archive #2188 case); the path is still
lane-excluded, because S1 classifies with lane_classification over the derivations of main and of the head.

Unchanged and checked against the live derivation of this tree: adding a secret-on-PR or write-on-PR job, an
unresolved dynamic edge in privileged code, an unknown step, a privileged artifact input or an action reference fails
here until the frozen debt sets below are raised, which is a .github + tests/governance change and therefore
owner-gated.
"""
import json
import re
import unittest
from pathlib import Path

import yaml

from scripts.governance import s1_workflow_isolation_derive_v1 as derivation
from scripts.governance.s1_workflow_isolation_derive_v1 import (  # noqa: F401  (names other tests import from here)
    CONFIG_SUFFIXES, DYNAMIC_LOADERS, NOT_PR_MARKERS, PATH_LIST_KEYS, PRIVACY, SHELL_UNKNOWN, SUBPROCESS_CALLS,
    SUBPROCESS_OWNERS, TOKEN_REFS, TRUTH, artifact_inputs, can_run_on_pr, isolated_privacy_job, isolated_truth_job,
    names_token, persists_checkout_credential, receives_secret, run_lines, runs_script, triggers, write_scoped)

ROOT = Path(__file__).resolve().parents[2]
WF = ROOT / ".github" / "workflows"
ISOLATION = ROOT / "00_FMOS" / "S1_WORKFLOW_ISOLATION_V1.json"
FROZEN_PR_WRITE_DEBT = frozenset(["adaptive-gap-validation-gate.yml:validate", "compass-event-refresh.yml:validate", "compass-outcomes.yml:validate", "daily-compass.yml:validate", "framework-learning-supervisor.yml:fmos-mission-loop-audit", "framework-learning-supervisor.yml:s1-v43-terra-max-review", "framework-learning-supervisor.yml:senior-repair-audit", "framework-learning-supervisor.yml:sol-max-elite-submit", "framework-learning-supervisor.yml:sol-max-implementation-patch", "framework-learning-supervisor.yml:temp-sol-pr-review", "framework-learning-supervisor.yml:validate", "native-market-recovery.yml:validate", "owner-bound-daily-director-manual.yml:astra-realdata-task2-v2", "provider-budget-readback.yml:validate-pr", "shadow-compass-v2.yml:validate", "situation-room-daily-static.yml:validate"])
FROZEN_SECRET_ON_PR_DEBT = frozenset(["api-agent-gateway-gate.yml:gateway-gate", "framework-learning-supervisor.yml:fmos-mission-loop-audit", "framework-learning-supervisor.yml:s1-v43-terra-max-review", "framework-learning-supervisor.yml:senior-repair-audit", "framework-learning-supervisor.yml:sol-max-elite-collect", "framework-learning-supervisor.yml:sol-max-elite-submit", "framework-learning-supervisor.yml:sol-max-implementation-patch", "framework-learning-supervisor.yml:sol-max-response-probe", "framework-learning-supervisor.yml:temp-sol-pr-review", "owner-bound-daily-director-manual.yml:astra-realdata-task2-v2"])
FROZEN_UNRESOLVED_EDGE_DEBT = frozenset(["06_RESEARCH_LAB/alpha_lab/tools/test_alpha_proof_supervisor_v2.py", "scripts/api_agent/fmos_mission_loop_audit_dispatch.py", "scripts/api_agent/mcp_provider_automation.py", "scripts/api_agent/s1_sol_max_patch_execution.py", "scripts/cycle_navigator/build_internal_precision.py", "scripts/learning/mature_exact_settlement_forecasts.py", "scripts/orchestration/verify_durable_readback.py", "scripts/research/manual_astra_maeve_task2_20261117.py", "scripts/research/w45_thursday_selftest_outcomes.py", "tests/api_agent/test_api_intelligence_v2.py", "tests/api_agent/test_owner_global_api_budget_cap.py", "tests/framework_intelligence/test_operational_memory_fail_to_codex_intake_v1.py", "tests/research/test_manual_astra_research_program_20261116.py"])
FROZEN_WRITER_UNRESOLVED_EDGE_DEBT = frozenset(["06_RESEARCH_LAB/audit_summaries/code_audit_20260831/reproduce.py", "scripts/daily_capture/rich_breadth_recovery_watchdog.py", "scripts/document_ingestion/anydoc_ingest.py", "scripts/evidence_lifecycle/audit_lifecycle_store.py", "scripts/evidence_lifecycle/write_ethbtc_persistence_receipt.py", "scripts/experiments/strategy_factor_leakage_e1_production.py", "scripts/pdf_ingestion/pdf_ingest.py", "scripts/research/shadow_mutation_probe.py", "scripts/research/shadow_session_telemetry.py", "scripts/research/validate_research_governance_integration.py", "scripts/skill_quality_gate/run_eval.py", "tests/api_agent/test_adaptive_evidence_gap.py", "tests/experiments/test_scientific_admission_lifecycle.py", "tests/learning/test_action_compass_accountability.py", "tests/learning/test_audit_lifecycle_timestamps.py", "tests/learning/test_compass_outcomes.py", "tests/learning/test_data_ping_learning_closure.py", "tests/learning/test_forecast_error_taxonomy.py", "tests/security/test_cre_shadow_guard.py"])
FROZEN_UNKNOWN_STEP_JOB_DEBT = frozenset()
FROZEN_PRIVILEGED_ARTIFACT_DEBT = frozenset(["alpha-proof-supervisor.yml:adjudicate <- download-artifact,gh-run-download", "cfgi-v3-launch-receipt-publish.yml:publish <- download-artifact", "cowork-historical-altseason-bundle-receipt.yml:publish <- gh-run-download", "framework-learning-operations.yml:operate <- download-artifact", "framework-learning-supervisor.yml:sol-max-collect <- download-artifact", "framework-learning-supervisor.yml:sol-max-elite-collect <- gh-run-download", "historical-altseason-cfgi-publish.yml:publish <- download-artifact", "historical-altseason-cfgi-terminal-publish.yml:publish <- gh-run-download", "historical-altseason-free-publish.yml:publish <- download-artifact", "research-lab-sol-dispatch.yml:research-lab-sol-collect <- gh-run-download", "weekly-api-calibration-shadow.yml:publish <- download-artifact"])
FROZEN_ACTION_REFS = frozenset(["./.github/actions/intraday-execution", "actions/cache@v4", "actions/checkout@v4", "actions/checkout@v6", "actions/configure-pages@v5", "actions/deploy-pages@v4", "actions/download-artifact@v4", "actions/setup-node@v4", "actions/setup-python@v5", "actions/upload-artifact@v4", "actions/upload-pages-artifact@v4", "dtolnay/rust-toolchain@stable"])


def workflows():
    """(file name, text, parsed mapping) of every workflow of ROOT (read at call time, so a fixture may repoint ROOT)."""
    return derivation.Tree(ROOT).workflows()


def derive(root=None):
    """The live derivation of ROOT (or of root)."""
    return derivation.derive(ROOT if root is None else root)


# No key of the pinned file is a lower bound any more: every key it carries equals the derivation, and the six path
# lists are derived live (PATH_LIST_KEYS). Kept because tools read this name.
LOWER_BOUND_KEYS = ()
_REAL_ROOT = ROOT
_REAL = {}


def real_tree_derivation():
    """derive() of the real repository tree, computed once per process (tests never change that tree)."""
    if "derived" not in _REAL:
        _REAL["derived"] = derivation.derive(_REAL_ROOT)
    return _REAL["derived"]


def file_mismatches(doc, derived):
    """The equality rule of the pinned file: it carries exactly the derived keys other than the six path lists,
    each equal to the derivation. Returns the keys that break it (empty when the file is right)."""
    expected = {key: value for key, value in derived.items() if key not in PATH_LIST_KEYS}
    carried = {key: value for key, value in doc.items() if key not in ("contract", "rule")}
    absent = object()
    return sorted(key for key in set(expected) | set(carried) if expected.get(key, absent) != carried.get(key, absent))


class WorkflowIsolationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.derived = real_tree_derivation()
        cls.doc = json.loads(ISOLATION.read_text(encoding="utf-8"))

    def test_isolation_file_equals_the_derivation(self):
        self.assertEqual(self.doc["contract"], "S1_WORKFLOW_ISOLATION_V1")
        for key, value in self.derived.items():
            with self.subTest(key=key):
                if key in PATH_LIST_KEYS:
                    # Derived live at the PR head and at main, never enumerated here: a new file that a secret job
                    # runs changes the derivation, not this pinned file (Archive #2188).
                    self.assertNotIn(key, self.doc, f"{key} is derived live; remove it from the pinned file")
                else:
                    self.assertEqual(self.doc[key], value, f"regenerate {key} in 00_FMOS/S1_WORKFLOW_ISOLATION_V1.json")
        self.assertEqual(file_mismatches(self.doc, self.derived), [])
        self.assertEqual(set(self.doc), {"contract", "rule"} | (set(self.derived) - set(PATH_LIST_KEYS)))
        self.assertEqual(set(PATH_LIST_KEYS), set(derivation.OWNER_GATED_KEYS) | set(derivation.HIGH_FLOOR_KEYS))
        for path in ("scripts/lib/evidence_io.py", "scripts/lib/metric_resolver.py", "scripts/lib/forecast_settlement_contract.py"):
            self.assertIn(path, self.derived["secret_job_executed_paths"])

    def test_debt_only_shrinks(self):
        self.assertLessEqual(set(self.derived["pr_write_jobs"]), FROZEN_PR_WRITE_DEBT,
                             "a new job can run on pull_request with a write token: isolate it instead")
        self.assertLessEqual(set(self.derived["secret_on_pr_jobs"]), FROZEN_SECRET_ON_PR_DEBT,
                             "a new job receives a secret on pull_request: isolate it instead")

    def test_privileged_closure_debt_only_shrinks(self):
        # Astra fix 6: UNKNOWN means excluded. An unresolved dynamic edge in secret-run code, a privileged job that
        # takes an artifact or a cache, and every action reference are frozen: a new one fails here (owner-gated).
        self.assertLessEqual(set(self.derived["unresolved_edge_paths"]), FROZEN_UNRESOLVED_EDGE_DEBT,
                             "secret-run code gained a dynamic load that no literal resolves: its closure is UNKNOWN")
        self.assertLessEqual(set(self.derived["writer_unresolved_edge_paths"]), FROZEN_WRITER_UNRESOLVED_EDGE_DEBT,
                             "writer-run code gained a load or command that no literal resolves: its closure is UNKNOWN")
        self.assertLessEqual(set(self.derived["unknown_step_jobs"]), FROZEN_UNKNOWN_STEP_JOB_DEBT,
                             "a privileged job's own step sources, evaluates or runs a computed script")
        self.assertLessEqual(set(self.derived["privileged_artifact_edges"]), FROZEN_PRIVILEGED_ARTIFACT_DEBT,
                             "a privileged job takes a new artifact or cache: untrusted data may reach a token or secret")
        self.assertLessEqual(set(self.derived["action_refs"]), FROZEN_ACTION_REFS, "a new or re-pointed action reference")
        self.assertLessEqual(set(self.derived["pr_persisted_write_credential_jobs"]), set(self.derived["pr_write_jobs"]))
        for ref in self.derived["action_refs"]:
            if ref.startswith("./"):
                self.assertTrue(ref.startswith("./.github/"), "a local action outside .github is not lane-excluded")
        # every unresolved file is itself secret-run code, so exclusion 3 already owner-gates it
        self.assertLessEqual(set(self.derived["unresolved_edge_paths"]), set(self.derived["secret_job_executed_paths"]))

    def test_privileged_classes_are_disjoint_and_complete(self):
        secret, writer, token = (set(self.derived[k]) for k in ("secret_jobs", "writer_jobs", "token_ref_jobs"))
        self.assertFalse(secret & writer or secret & token or writer & token)
        every = {f"{name}:{jid}" for name, _, doc in workflows() for jid in (doc.get("jobs") or {})}
        for name, _, doc in workflows():
            for jid, job in (doc.get("jobs") or {}).items():
                key = f"{name}:{jid}"
                privileged = receives_secret(doc, job) or write_scoped(doc, job) or names_token(job)
                self.assertEqual(key in secret | writer | token, privileged, key)
        self.assertLessEqual(secret | writer | token, every)
        # a path that a secret job executes is exclusion 3 and is never listed again as writer-only code
        self.assertFalse(set(self.derived["writer_job_executed_paths"]) & set(self.derived["secret_job_executed_paths"]))

    def test_no_new_secret_job_checks_out_pr_code(self):
        # Pre-existing debt (FROZEN_SECRET_ON_PR_DEBT, e.g. framework-learning-supervisor.yml) checks out the PR head
        # with secrets; its executed files are exclusion-3 OWNER_GATED. No other secret job may do so.
        for name, text, doc in workflows():
            self.assertNotIn("pull_request_target", triggers(doc), name)
            for jid, job in (doc.get("jobs") or {}).items():
                if not receives_secret(doc, job) or f"{name}:{jid}" in FROZEN_SECRET_ON_PR_DEBT:
                    continue
                for step in job.get("steps") or []:
                    ref = str((step.get("with") or {}).get("ref", ""))
                    with self.subTest(job=f"{name}:{jid}"):
                        self.assertNotRegex(ref, r"head_ref|pull_request|refs/pull", "a secret job checks out PR code")

    def test_gate_isolation_is_live_and_gate_scripts_run_only_in_their_jobs(self):
        self.assertEqual(self.derived["gate_isolation"], "LIVE")
        for name, text, doc in workflows():
            for jid, job in (doc.get("jobs") or {}).items():
                if runs_script(job, PRIVACY):
                    self.assertEqual((name, jid), ("data-architecture-gate.yml", "privacy-scan"))
                if runs_script(job, TRUTH):
                    self.assertEqual((name, jid), ("automation-production-health-gate.yml", "execution-truth"))

    def test_the_2145_case_is_isolated(self):
        """#2145 changes build_data_consumer_index.py, which runs in framework-learning-operations.yml / operate."""
        self.assertNotIn("framework-learning-operations.yml:operate", self.derived["secret_jobs"])
        self.assertIn("framework-learning-operations.yml:receipt_sync", self.derived["secret_jobs"])
        self.assertNotIn("scripts/orchestration/build_data_consumer_index.py", self.derived["secret_job_executed_paths"])
        self.assertIn("scripts/experiments/sync_experiment_receipts.py", self.derived["secret_job_executed_paths"])
        doc = yaml.safe_load((WF / "framework-learning-operations.yml").read_text(encoding="utf-8"))
        job = doc["jobs"]["receipt_sync"]
        self.assertIn("refs/heads/main", job["if"])
        self.assertEqual(job.get("permissions"), {"contents": "read"})
        checkout = [s for s in job["steps"] if s.get("uses") == "actions/checkout@v4"]
        self.assertEqual([s.get("with", {}).get("ref") for s in checkout], ["main"])
        for line in run_lines(job):
            for call in re.findall(r"(?m)^\s*python3?\b[^\n]*", line):
                self.assertRegex(call, r"^\s*python3? -I\b", call)
        commits = [m for line in run_lines(doc["jobs"]["operate"]) for m in re.findall(r"(?m)^.*\bgit\b.*\bcommit\b.*$", line)]
        self.assertTrue(commits, "operate must still commit")
        for c in commits:
            self.assertIn("git -c core.hooksPath=/dev/null commit", c, "operate commits with hooks off (FMEA 15)")
        self.assertEqual([s for s in job["steps"] if "run" in s and "scripts/" in s["run"]
                          and "scripts/experiments/sync_experiment_receipts.py" not in s["run"]], [])


if __name__ == "__main__":
    unittest.main()
