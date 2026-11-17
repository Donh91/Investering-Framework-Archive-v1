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

v3 privileged execution closure (Astra S1 vNext fix 6, negative tests N19 and N20). A job is PRIVILEGED when it
receives a secret, holds a write-scoped token (the default token counts) or names the workflow token in a step:
- writer_jobs, token_ref_jobs: the privileged jobs that are not secret jobs by the rule above;
- writer_job_executed_paths: what those jobs execute. A lower bound: S1 classes a changed path listed here HIGH at least;
- secret_job_named_files: every non-code file path that the steps of a secret job name (config, registry, prompt,
  state). Exclusion 3 "reads as config". Derived from the workflow text alone, whether or not the file exists, so a
  data writer that creates such a file on main never changes this list;
- the closure follows Python imports, sys.path edits and literal repository paths in code (shell sourcing and
  subprocess targets; these three are the v2 derivation, unchanged) and, new in v3, the targets of dynamic loads that
  a literal names, also when the literal is a bare file name next to the loading file;
- unresolved_edge_paths (secret-run files) and writer_unresolved_edge_paths (writer-run files): files with a dynamic
  load, an exec or eval, a shell source or a subprocess command that no literal resolves. unknown_step_jobs: privileged
  jobs whose own steps do the same, or that use a local action this test cannot read. The closure behind such an edge is
  UNKNOWN, so each list is shrink-only debt: a new unresolved edge in privileged code fails here;
- writer_job_named_files: the non-code files a writer or token job names (config that can redirect a writer);
- local composite actions (uses: ./path) are expanded into the steps of the job that uses them; a reusable workflow
  call is not followed, it is frozen in action_refs (none exists today);
- NOT covered, stated so that nobody reads the lists as complete: build tools that hide the command (a Makefile target,
  an npm script), code fetched at run time, and data files that code opens by a computed name;
- privileged_artifact_edges: privileged jobs that download an artifact or restore a cache. Shrink-only debt;
- action_refs: every action a workflow uses. Frozen: a new or re-pointed action fails here;
- pr_persisted_write_credential_jobs: jobs on pull_request whose checkout keeps a write-scoped credential on disk.
  Always a subset of pr_write_jobs, so the existing shrink-only debt covers it.
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
DYNAMIC_LOADERS = frozenset({"import_module", "__import__", "exec", "eval", "execfile", "run_path", "run_module",
                             "spec_from_file_location", "load_source", "SourceFileLoader"})
TOKEN_REFS = ("github.token", "GITHUB_TOKEN")
FROZEN_UNRESOLVED_EDGE_DEBT = frozenset(["06_RESEARCH_LAB/alpha_lab/tools/test_alpha_proof_supervisor_v2.py", "scripts/api_agent/fmos_mission_loop_audit_dispatch.py", "scripts/api_agent/mcp_provider_automation.py", "scripts/api_agent/s1_sol_max_patch_execution.py", "scripts/cycle_navigator/build_internal_precision.py", "scripts/learning/mature_exact_settlement_forecasts.py", "scripts/orchestration/verify_durable_readback.py", "scripts/research/manual_astra_maeve_task2_20261117.py", "scripts/research/w45_thursday_selftest_outcomes.py", "tests/api_agent/test_api_intelligence_v2.py", "tests/api_agent/test_owner_global_api_budget_cap.py", "tests/framework_intelligence/test_operational_memory_fail_to_codex_intake_v1.py", "tests/research/test_manual_astra_research_program_20261116.py"])
FROZEN_WRITER_UNRESOLVED_EDGE_DEBT = frozenset(["06_RESEARCH_LAB/audit_summaries/code_audit_20260831/reproduce.py", "scripts/daily_capture/rich_breadth_recovery_watchdog.py", "scripts/document_ingestion/anydoc_ingest.py", "scripts/evidence_lifecycle/audit_lifecycle_store.py", "scripts/evidence_lifecycle/write_ethbtc_persistence_receipt.py", "scripts/experiments/strategy_factor_leakage_e1_production.py", "scripts/pdf_ingestion/pdf_ingest.py", "scripts/research/shadow_mutation_probe.py", "scripts/research/shadow_session_telemetry.py", "scripts/research/validate_research_governance_integration.py", "scripts/skill_quality_gate/run_eval.py", "tests/api_agent/test_adaptive_evidence_gap.py", "tests/experiments/test_scientific_admission_lifecycle.py", "tests/learning/test_action_compass_accountability.py", "tests/learning/test_audit_lifecycle_timestamps.py", "tests/learning/test_compass_outcomes.py", "tests/learning/test_data_ping_learning_closure.py", "tests/learning/test_forecast_error_taxonomy.py", "tests/security/test_cre_shadow_guard.py"])
FROZEN_UNKNOWN_STEP_JOB_DEBT = frozenset()
FROZEN_PRIVILEGED_ARTIFACT_DEBT = frozenset(["alpha-proof-supervisor.yml:adjudicate <- download-artifact,gh-run-download", "cfgi-v3-launch-receipt-publish.yml:publish <- download-artifact", "cowork-historical-altseason-bundle-receipt.yml:publish <- gh-run-download", "framework-learning-operations.yml:operate <- download-artifact", "framework-learning-supervisor.yml:sol-max-collect <- download-artifact", "framework-learning-supervisor.yml:sol-max-elite-collect <- gh-run-download", "historical-altseason-cfgi-publish.yml:publish <- download-artifact", "historical-altseason-cfgi-terminal-publish.yml:publish <- gh-run-download", "historical-altseason-free-publish.yml:publish <- download-artifact", "research-lab-sol-dispatch.yml:research-lab-sol-collect <- gh-run-download", "weekly-api-calibration-shadow.yml:publish <- download-artifact"])
FROZEN_ACTION_REFS = frozenset(["./.github/actions/intraday-execution", "actions/cache@v4", "actions/checkout@v4", "actions/checkout@v6", "actions/configure-pages@v5", "actions/deploy-pages@v4", "actions/download-artifact@v4", "actions/setup-node@v4", "actions/setup-python@v5", "actions/upload-artifact@v4", "actions/upload-pages-artifact@v4", "dtolnay/rust-toolchain@stable"])


def names_token(job):
    text = json.dumps(job, default=str)
    return any(ref in text for ref in TOKEN_REFS)


def file_text(rel):
    try:
        return (ROOT / rel).read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return ""


SUBPROCESS_CALLS = frozenset({"run", "call", "check_call", "check_output", "Popen", "system", "popen", "execv", "execve",
                              "execvp", "execl", "spawnv", "spawnl"})
SUBPROCESS_OWNERS = frozenset({"subprocess", "os", "sp"})
# A shell line that sources, evaluates or runs a script whose name is a variable or a command substitution.
SHELL_UNKNOWN = re.compile(
    r"(?m)^[ \t]*(?:(?:source|\.)[ \t]+[\"']?[$`]"
    r"|eval[ \t]"
    r"|(?:bash|sh|python3?|node)[ \t]+(?:-[A-Za-z]+[ \t]+)*[\"']?\$[A-Za-z_{(@*0-9])")


def _has_literal(node):
    return any(isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value.strip() for n in ast.walk(node))


def dynamic_edges(rel):
    """(resolved local targets, unresolved) for the dynamic loads of a code file.

    Python: a literal module name that is no repository file is the standard library or an installed package:
    resolved, nothing to follow. A literal file name is resolved against the file's own directory and its ancestors.
    exec, eval, a load whose target no literal names, and a subprocess or os.system call whose command holds no
    literal at all are UNKNOWN (N20). A loader imported under another name (from importlib import import_module as x)
    is followed by its real name. Shell: source, eval or an interpreter run on a variable is UNKNOWN.
    UNKNOWN means the caller must not treat the closure as complete."""
    if rel.endswith(".sh"):
        return set(), bool(SHELL_UNKNOWN.search(file_text(rel)))
    if not rel.endswith(".py"):
        return set(), False
    try:
        tree = ast.parse(file_text(rel))
    except SyntaxError:
        return set(), True
    targets, unresolved = set(), False
    bases = [PurePosixPath(rel).parent, *PurePosixPath(rel).parents]
    alias = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for a in node.names:
                if a.name in DYNAMIC_LOADERS or (node.module in ("subprocess", "os") and a.name in SUBPROCESS_CALLS):
                    alias[a.asname or a.name] = (node.module, a.name)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
        owner = getattr(getattr(func, "value", None), "id", None) if isinstance(func, ast.Attribute) else None
        if isinstance(func, ast.Name) and name in alias:
            owner, name = alias[name]
        if name in SUBPROCESS_CALLS and owner in SUBPROCESS_OWNERS:
            if not node.args or not _has_literal(node.args[0]):
                unresolved = True                      # the whole command is computed
            continue
        if name not in DYNAMIC_LOADERS:
            continue
        if isinstance(func, ast.Attribute) and name in ("exec", "eval"):
            continue                                   # a method such as cursor.exec(), not the builtin
        if name in ("exec", "eval", "execfile"):
            unresolved = True
            continue
        literals = [n.value for arg in [*node.args, *[k.value for k in node.keywords]] for n in ast.walk(arg)
                    if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        found = False
        for lit in literals:
            if lit.endswith(sp._CODE_SUFFIXES) and not lit.startswith("/") and ".." not in lit.split("/"):
                for base in bases:
                    cand = (base / lit).as_posix()
                    cand = cand[2:] if cand.startswith("./") else cand
                    if (ROOT / cand).is_file():
                        targets.add(cand)
                        found = True
            elif re.fullmatch(r"[A-Za-z_][\w.]*", lit):
                found = True                           # a literal module name
                for base in bases:
                    cand = (base / (lit.replace(".", "/") + ".py")).as_posix()
                    cand = cand[2:] if cand.startswith("./") else cand
                    if (ROOT / cand).is_file():
                        targets.add(cand)
        if name in ("import_module", "__import__", "run_module") and not any(
                isinstance(a, ast.Constant) and isinstance(a.value, str) for a in node.args[:1]):
            found = False                              # the module name itself is computed
        if not found:
            unresolved = True
    return targets, unresolved


def expanded_steps(job):
    """A job's steps with every local composite action (uses: ./path) replaced by that action's own steps, so code
    that a privileged job reaches only through a local action is in its closure. An action file that cannot be
    read or parsed yields a marker step, which the caller reports as an unknown edge."""
    out = []
    for step in job.get("steps") or []:
        uses = str(step.get("uses", ""))
        if not uses.startswith("./"):
            out.append(step)
            continue
        found = None
        for name in ("action.yml", "action.yaml"):
            path = ROOT / uses[2:] / name
            if path.is_file():
                try:
                    found = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                except (yaml.YAMLError, OSError, UnicodeDecodeError):
                    found = None
                break
        steps = ((found or {}).get("runs") or {}).get("steps") if isinstance(found, dict) else None
        if not isinstance(steps, list):
            out.append({"uses": uses, "s1_unknown_local_action": True})
        else:
            out.append({k: v for k, v in step.items() if k != "uses"} | {"s1_local_action": uses})
            out.extend(s for s in steps if isinstance(s, dict))
    return out


def step_text_is_unknown(job):
    """A run line of the job itself that sources, evaluates or runs a computed script, or an unreadable local action."""
    for step in expanded_steps(job):
        if step.get("s1_unknown_local_action") or SHELL_UNKNOWN.search(str(step.get("run", ""))):
            return True
    return False


_EDGES = {}


def file_edges(rel):
    """Every file that rel loads (memoised per ROOT): (targets, has an unresolved dynamic edge)."""
    key = (str(ROOT), rel)
    if key not in _EDGES:
        targets, unknown = dynamic_edges(rel)
        _EDGES[key] = (targets | import_edges(rel), unknown)
    return _EDGES[key]


def full_closure(job):
    """Files a job executes: the v2 closure (imports, sys.path edits, literal paths) over the job's steps and the
    steps of its local composite actions, plus literal dynamic loads.
    Returns (code paths, files with an unresolved dynamic edge)."""
    closure = set(job_executed_paths({"steps": expanded_steps(job)}))
    unresolved = set()
    frontier = set(closure)
    seen = set()
    while frontier:
        new = set()
        for rel in frontier:
            seen.add(rel)
            edges, unknown = file_edges(rel)
            if unknown:
                unresolved.add(rel)
            new |= edges - closure
        new = {p for p in new if not p.startswith(".github/")}
        closure |= new
        frontier = new - seen
    return closure, unresolved


def named_files(job):
    """Non-code file paths that a job's steps name, from the workflow text alone (existence is not checked)."""
    step_text = json.dumps(expanded_steps(job), default=str).replace("\\n", "\n")
    found = set()
    for token in sp._TOKEN.findall(step_text):
        token = token.rstrip(".")
        token = token[2:] if token.startswith("./") else token
        if ("/" in token and token.endswith(CONFIG_SUFFIXES) and not token.startswith(("/", "-", ".github/"))
                and ".." not in token.split("/")):
            found.add(token)
    return found


def artifact_inputs(job):
    kinds = set()
    for step in job.get("steps") or []:
        uses = str(step.get("uses", ""))
        if "download-artifact" in uses:
            kinds.add("download-artifact")
        if uses.startswith("actions/cache"):
            kinds.add("cache")
        if "gh run download" in str(step.get("run", "")):
            kinds.add("gh-run-download")
    return sorted(kinds)


def persists_checkout_credential(job):
    for step in job.get("steps") or []:
        if str(step.get("uses", "")).startswith("actions/checkout"):
            if str((step.get("with") or {}).get("persist-credentials", "true")).lower() != "false":
                return True
    return False


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


_IMPORTS = {}


def import_edges(rel):
    """Local imports of rel (memoised per ROOT; the v2 derivation, unchanged)."""
    key = (str(ROOT), rel)
    if key not in _IMPORTS:
        _IMPORTS[key] = sp._local_imports(ROOT, rel) | imports_via_sys_path(rel)
    return _IMPORTS[key]


def job_executed_paths(job):
    text = json.dumps(job.get("steps") or [], default=str).replace("\\n", "\n")
    closure = job_seed(text)
    frontier = set(closure)
    while frontier:
        new = set()
        for rel in frontier:
            new |= import_edges(rel) - closure
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
    writer_jobs, token_ref_jobs, writer_paths, config_paths, unresolved = [], [], set(), set(), set()
    writer_config, writer_unresolved, unknown_step_jobs = set(), set(), []
    artifact_edges, action_refs, persisted = [], set(), []
    gate = {"privacy": False, "truth": False}
    for name, text, doc in workflows():
        for jid, job in (doc.get("jobs") or {}).items():
            key = f"{name}:{jid}"
            secret, write, token = receives_secret(doc, job), write_scoped(doc, job), names_token(job)
            if job.get("uses"):
                action_refs.add(str(job["uses"]))      # a reusable workflow call: frozen, its jobs are not followed
            for step in job.get("steps") or []:
                if step.get("uses"):
                    action_refs.add(str(step["uses"]))
            if secret:
                secret_jobs.append(key)
                executed |= job_executed_paths(job)
                closure, unknown = full_closure(job)
                executed |= closure
                config_paths |= named_files(job)
                unresolved |= unknown
                if can_run_on_pr(doc, job):
                    secret_on_pr.append(key)
            elif write or token:
                (writer_jobs if write else token_ref_jobs).append(key)
                closure, unknown = full_closure(job)
                writer_paths |= closure
                writer_config |= named_files(job)
                writer_unresolved |= unknown
            if (secret or write or token) and step_text_is_unknown(job):
                unknown_step_jobs.append(key)
            if (secret or write or token) and artifact_inputs(job):
                artifact_edges.append(f"{key} <- {','.join(artifact_inputs(job))}")
            if can_run_on_pr(doc, job) and write_scoped(doc, job):
                pr_write.append(key)
                if persists_checkout_credential(job):
                    persisted.append(key)
        if name == "data-architecture-gate.yml":
            gate["privacy"] = isolated_privacy_job(doc)
        if name == "automation-production-health-gate.yml":
            gate["truth"] = isolated_truth_job(doc)
    return {"secret_jobs": sorted(secret_jobs), "secret_job_executed_paths": sorted(executed),
            "pr_write_jobs": sorted(pr_write), "secret_on_pr_jobs": sorted(secret_on_pr),
            "gate_isolation": "LIVE" if all(gate.values()) else "NOT_LIVE",
            "writer_jobs": sorted(writer_jobs), "token_ref_jobs": sorted(token_ref_jobs),
            "writer_job_executed_paths": sorted(writer_paths - executed),
            "secret_job_named_files": sorted(config_paths),
            "writer_job_named_files": sorted(writer_config - config_paths),
            "unresolved_edge_paths": sorted(unresolved),
            "writer_unresolved_edge_paths": sorted(writer_unresolved - unresolved),
            "unknown_step_jobs": sorted(unknown_step_jobs),
            "privileged_artifact_edges": sorted(artifact_edges),
            "action_refs": sorted(action_refs),
            "pr_persisted_write_credential_jobs": sorted(persisted)}


LOWER_BOUND_KEYS = ("secret_job_executed_paths", "writer_job_executed_paths")


class WorkflowIsolationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.derived = derive()
        cls.doc = json.loads(ISOLATION.read_text(encoding="utf-8"))

    def test_isolation_file_equals_the_derivation(self):
        self.assertEqual(self.doc["contract"], "S1_WORKFLOW_ISOLATION_V1")
        for key, value in self.derived.items():
            with self.subTest(key=key):
                if key in LOWER_BOUND_KEYS:
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
        self.assertLessEqual(set(self.derived["unresolved_edge_paths"]), set(self.doc["secret_job_executed_paths"]))

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
