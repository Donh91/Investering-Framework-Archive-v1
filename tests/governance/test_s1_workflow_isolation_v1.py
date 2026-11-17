"""S1 workflow isolation guard (AGENTS.md section 0.2e exclusions 1 and 3, section 0.2f "isolate instead of exclude").

00_FMOS/S1_WORKFLOW_ISOLATION_V1.json is S1's machine-readable view of the workflows. This test keeps it consistent with a
derivation from .github/workflows, so S1 never has to parse YAML at runtime:
- secret_jobs: every job that receives a secret (secrets.* in the job, secrets: inherit, or secrets.* at workflow level);
- secret_job_executed_paths: the files those jobs execute (workflow tokens plus the local import closure, the same
  derivation as s1_standing_policy_v1 uses for required_job_executed_paths). Exclusion 3 includes at least these files (a lower bound; AGENTS.md keeps the judgment rule too);
- pr_write_jobs: jobs that can run on pull_request with a write-scoped token (or the default token). Shrink-only debt;
- secret_on_pr_jobs: jobs that receive a secret and can run on pull_request. Shrink-only debt;
- gate_isolation: LIVE only when the privacy scan and the execution-truth check run in their own isolated jobs.
Adding a new secret-on-PR or write-on-PR job fails here until the frozen debt sets below are raised, which is a
.github + tests/governance change and therefore owner-gated.
"""
import ast
import json
import re
from pathlib import PurePosixPath
import unittest
from pathlib import Path

import yaml

from scripts.governance import s1_standing_policy_v1 as sp

ROOT = Path(__file__).resolve().parents[2]
WF = ROOT / ".github" / "workflows"
ISOLATION = ROOT / "00_FMOS" / "S1_WORKFLOW_ISOLATION_V1.json"
NOT_PR_MARKERS = ("github.ref == 'refs/heads/main'", "github.event_name != 'pull_request'",
                  "github.event_name == 'schedule'", "github.event_name == 'workflow_dispatch'",
                  "github.event_name == 'push'")
PRIVACY = "scripts/governance/s1_native_privacy_scan_step_v1.py"
TRUTH = "scripts/governance/check_test_execution_truth.py"
FROZEN_PR_WRITE_DEBT = frozenset(["adaptive-gap-validation-gate.yml:validate", "compass-event-refresh.yml:validate", "compass-outcomes.yml:validate", "daily-compass.yml:validate", "framework-learning-supervisor.yml:fmos-mission-loop-audit", "framework-learning-supervisor.yml:s1-v43-terra-max-review", "framework-learning-supervisor.yml:senior-repair-audit", "framework-learning-supervisor.yml:sol-max-elite-submit", "framework-learning-supervisor.yml:sol-max-implementation-patch", "framework-learning-supervisor.yml:temp-sol-pr-review", "framework-learning-supervisor.yml:validate", "native-market-recovery.yml:validate", "owner-bound-daily-director-manual.yml:astra-realdata-task2-v2", "provider-budget-readback.yml:validate-pr", "shadow-compass-v2.yml:validate", "situation-room-daily-static.yml:validate"])
FROZEN_SECRET_ON_PR_DEBT = frozenset(["api-agent-gateway-gate.yml:gateway-gate", "framework-learning-supervisor.yml:fmos-mission-loop-audit", "framework-learning-supervisor.yml:s1-v43-terra-max-review", "framework-learning-supervisor.yml:senior-repair-audit", "framework-learning-supervisor.yml:sol-max-elite-collect", "framework-learning-supervisor.yml:sol-max-elite-submit", "framework-learning-supervisor.yml:sol-max-implementation-patch", "framework-learning-supervisor.yml:sol-max-response-probe", "framework-learning-supervisor.yml:temp-sol-pr-review", "owner-bound-daily-director-manual.yml:astra-realdata-task2-v2"])


def workflows():
    for path in sorted(WF.glob("*.y*ml")):
        text = path.read_text(encoding="utf-8")
        yield path.name, text, yaml.safe_load(text) or {}


def triggers(doc):
    on = doc.get(True, doc.get("on"))
    if isinstance(on, str):
        return {on}
    if isinstance(on, list):
        return set(on)
    return set(on or {})


def can_run_on_pr(doc, job):
    if not triggers(doc) & {"pull_request", "pull_request_target"}:
        return False
    cond = str(job.get("if", ""))
    return not any(marker in cond for marker in NOT_PR_MARKERS)


def write_scoped(doc, job):
    perms = job.get("permissions", doc.get("permissions"))
    if perms is None:
        return True                                    # default token: treated as write (fail closed)
    if isinstance(perms, str):
        return perms != "read-all"
    return any(str(v) == "write" for v in perms.values())


def receives_secret(doc, job):
    top = {k: v for k, v in doc.items() if k != "jobs"}
    return "secrets." in json.dumps(job, default=str) or job.get("secrets") == "inherit" or "secrets." in json.dumps(top, default=str)


CONFIG_SUFFIXES = (".json", ".yml", ".yaml", ".toml", ".ini", ".cfg", ".txt")


def job_seed(text):
    """Files a job runs, imports or reads as config: code files named or under a named directory, and config files
    named explicitly. Data under a directory the job writes or reads in bulk is data, not code (not followed)."""
    found = set()
    for token in sp._TOKEN.findall(text):
        token = token.rstrip(".")
        if not token or token.startswith(("/", "-", ".github")) or ".." in token.split("/"):
            continue
        cand = ROOT / token
        if "/" in token and cand.is_file():
            if token.endswith(sp._CODE_SUFFIXES):
                found.add(token)
        elif "/" in token and cand.is_dir():
            found |= {p.relative_to(ROOT).as_posix() for p in cand.rglob("*") if p.is_file() and p.suffix in sp._CODE_SUFFIXES}
        elif "." in token and "/" not in token and (ROOT / (token.replace(".", "/") + ".py")).is_file():
            found.add(token.replace(".", "/") + ".py")
    return found


def imports_via_sys_path(rel):
    """A file that edits sys.path may import from any ancestor directory (R2 P1-1, e.g. lib.evidence_io)."""
    if not rel.endswith(".py"):
        return set()
    try:
        text = (ROOT / rel).read_text(encoding="utf-8")
        tree = ast.parse(text)
    except (SyntaxError, UnicodeDecodeError, OSError):
        return set()
    if "sys.path" not in text:
        return set()
    found = set()
    ancestors = list(PurePosixPath(rel).parents)
    # R3 N1: sys.path targets built from literal path chains, e.g. Path(__file__).resolve().parents[1] / "lib",
    # ROOT / "scripts" / "research" with ROOT = Path(__file__).resolve().parents[2], or .parent / "learning".
    chain = r"((?:\s*/\s*[\"'][^\"']+[\"'])+)"
    segs = lambda c: re.findall(r"[\"']([^\"']+)[\"']", c)
    roots = {var: int(k) for var, k in re.findall(r"(\w+)\s*=\s*Path\(__file__\)(?:\.resolve\(\))?\.parents\[(\d+)\]", text)}
    for var in re.findall(r"(\w+)\s*=\s*Path\(__file__\)(?:\.resolve\(\))?\.parent\b(?!s)", text):
        roots[var] = 0
    for k, c in re.findall(r"parents\[(\d+)\]" + chain, text):
        if int(k) < len(ancestors):
            ancestors.append(ancestors[int(k)].joinpath(*segs(c)))
    for c in re.findall(r"\.parent\b(?!s)" + chain, text):
        ancestors.append(PurePosixPath(rel).parent.joinpath(*segs(c)))
    base_list = list(PurePosixPath(rel).parents)
    for var, k in roots.items():
        if k < len(base_list):
            ancestors.append(base_list[k])
            for c in re.findall(r"\b" + re.escape(var) + chain, text):
                ancestors.append(base_list[k].joinpath(*segs(c)))
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            names = [node.module] + [f"{node.module}.{a.name}" for a in node.names]
        for name in names:
            for base in ancestors:
                target = base.joinpath(*name.split("."))
                for cand in (target.as_posix() + ".py", (target / "__init__.py").as_posix()):
                    if (ROOT / cand).is_file():
                        found.add(cand)
    return found


def job_executed_paths(job):
    text = json.dumps(job.get("steps") or [], default=str).replace("\\n", "\n")
    closure = job_seed(text)
    frontier = set(closure)
    while frontier:
        new = set()
        for rel in frontier:
            new |= (sp._local_imports(ROOT, rel) | imports_via_sys_path(rel)) - closure
        closure |= new
        frontier = new
    return {p for p in closure if not p.startswith(".github/")}


def run_lines(job):
    return [str(s.get("run", "")) for s in (job.get("steps") or []) if "run" in s]


def runs_script(job, script):
    """True when a run line executes script (a py_compile syntax check does not execute it)."""
    commands = [cmd for run in run_lines(job) for cmd in run.replace("\\\n", " ").splitlines()]
    return any(script in cmd and "py_compile" not in cmd for cmd in commands)


def isolated_privacy_job(doc):
    job = (doc.get("jobs") or {}).get("privacy-scan")
    if not job:
        return False
    steps = job.get("steps") or []
    uses = [s.get("uses") for s in steps if "uses" in s]
    runs = run_lines(job)
    mode = [s.get("env", {}).get("S1_PRIVACY_SCAN_MODE") for s in steps if "run" in s]
    return (list(doc["jobs"])[0] == "privacy-scan" and uses == ["actions/checkout@v4", "actions/setup-python@v5"]
            and runs == [f"python -I {PRIVACY}"] and mode == ["enforce"] and not job.get("needs"))


def isolated_truth_job(doc):
    jobs = doc.get("jobs") or {}
    job = jobs.get("execution-truth")
    if not job:
        return False
    runs = run_lines(job)
    checkouts = [s.get("with", {}) for s in job.get("steps") or [] if s.get("uses") == "actions/checkout@v4"]
    others = [name for name, j in jobs.items() if name != "execution-truth" and runs_script(j, TRUTH)]
    return (job.get("needs") == "test" and len(runs) == 1 and runs[0].startswith(f"python -I gate/{TRUTH} ")
            and {"path": "gate", "ref": "${{ github.base_ref }}"} in [dict(c) for c in checkouts] and not others)


def derive():
    secret_jobs, executed, pr_write, secret_on_pr = [], set(), [], []
    gate = {"privacy": False, "truth": False}
    for name, text, doc in workflows():
        for jid, job in (doc.get("jobs") or {}).items():
            key = f"{name}:{jid}"
            if receives_secret(doc, job):
                secret_jobs.append(key)
                executed |= job_executed_paths(job)
                if can_run_on_pr(doc, job):
                    secret_on_pr.append(key)
            if can_run_on_pr(doc, job) and write_scoped(doc, job):
                pr_write.append(key)
        if name == "data-architecture-gate.yml":
            gate["privacy"] = isolated_privacy_job(doc)
        if name == "automation-production-health-gate.yml":
            gate["truth"] = isolated_truth_job(doc)
    return {"secret_jobs": sorted(secret_jobs), "secret_job_executed_paths": sorted(executed),
            "pr_write_jobs": sorted(pr_write), "secret_on_pr_jobs": sorted(secret_on_pr),
            "gate_isolation": "LIVE" if all(gate.values()) else "NOT_LIVE"}


class WorkflowIsolationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.derived = derive()
        cls.doc = json.loads(ISOLATION.read_text(encoding="utf-8"))

    def test_isolation_file_equals_the_derivation(self):
        self.assertEqual(self.doc["contract"], "S1_WORKFLOW_ISOLATION_V1")
        for key, value in self.derived.items():
            with self.subTest(key=key):
                if key == "secret_job_executed_paths":
                    # A lower bound of secret-run code: the file may list more, never less (R2 P2-2: a data file that
                    # appears on main never turns every PR red, because data files are not in the derivation).
                    self.assertLessEqual(set(value), set(self.doc[key]), "add the missing secret-run code paths")
                else:
                    self.assertEqual(self.doc[key], value, f"regenerate {key} in 00_FMOS/S1_WORKFLOW_ISOLATION_V1.json")
        for path in ("scripts/lib/evidence_io.py", "scripts/lib/metric_resolver.py", "scripts/lib/forecast_settlement_contract.py"):
            self.assertIn(path, self.doc["secret_job_executed_paths"])

    def test_debt_only_shrinks(self):
        self.assertLessEqual(set(self.derived["pr_write_jobs"]), FROZEN_PR_WRITE_DEBT,
                             "a new job can run on pull_request with a write token: isolate it instead")
        self.assertLessEqual(set(self.derived["secret_on_pr_jobs"]), FROZEN_SECRET_ON_PR_DEBT,
                             "a new job receives a secret on pull_request: isolate it instead")

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
