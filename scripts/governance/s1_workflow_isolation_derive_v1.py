#!/usr/bin/env python3
"""S1 workflow isolation derivation (AGENTS.md section 0.2e exclusion 3, section 0.2g privileged execution closure).

Derives, for the repository tree at a given root, which workflow jobs are privileged and which files they execute or
name. It only PARSES the tree (yaml, ast, regex): it never imports or executes a file of the tree it analyses, and it
uses no network.

The six path lists (PATH_LIST_KEYS) are derived live, at the PR head and at main, and S1 uses their union: a path that
either tree lists stays lane-excluded, so a PR cannot un-list a file by deleting the edge that makes it secret-run.
They are no longer enumerated in 00_FMOS/S1_WORKFLOW_ISOLATION_V1.json; that file keeps the job-level lists.

- secret_jobs: every job that receives a secret (secrets.* in the job, secrets: inherit, or secrets.* at workflow level);
- secret_job_executed_paths: the files those jobs execute (workflow tokens plus the local import closure, the same
  derivation as s1_standing_policy_v1 uses for required_job_executed_paths);
- writer_jobs, token_ref_jobs: the privileged jobs that are not secret jobs (a write-scoped token, the default token
  counts; or a step that names the workflow token); writer_job_executed_paths: what those jobs execute;
- secret_job_named_files, writer_job_named_files: every non-code file path that the steps of such a job name, from the
  workflow text alone, whether or not the file exists;
- unresolved_edge_paths, writer_unresolved_edge_paths: files with a dynamic load, an exec or eval, a shell source or a
  subprocess command that no literal resolves (also a Python file that does not parse). The closure behind such an
  edge is UNKNOWN;
- the closure follows Python imports, sys.path edits, literal repository paths in code, literal dynamic loads and the
  steps of local composite actions (uses: ./path); a reusable workflow call is not followed, it is listed in
  action_refs;
- NOT covered: build tools that hide the command (a Makefile target, an npm script), code fetched at run time, and data
  files that code opens by a computed name.

Fail closed: a missing workflow directory, or a workflow file that cannot be read or parsed or is not a mapping of
jobs, raises DerivationError (the CLI exits 2). Nothing is ever read as an empty closure.

CLI:
  s1_workflow_isolation_derive_v1.py --root <dir> [--json]
  s1_workflow_isolation_derive_v1.py --root <head dir> --base-root <main dir> --changed <file, one path per line>
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

import yaml

try:
    from scripts.governance import s1_standing_policy_v1 as sp
except ImportError:                                    # run as a file (also with python -I): load the sibling module
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import s1_standing_policy_v1 as sp

NOT_PR_MARKERS = ("github.ref == 'refs/heads/main'", "github.event_name != 'pull_request'",
                  "github.event_name == 'schedule'", "github.event_name == 'workflow_dispatch'",
                  "github.event_name == 'push'")
PRIVACY = "scripts/governance/s1_native_privacy_scan_step_v1.py"
TRUTH = "scripts/governance/check_test_execution_truth.py"
CONFIG_SUFFIXES = (".json", ".yml", ".yaml", ".toml", ".ini", ".cfg", ".txt")
DYNAMIC_LOADERS = frozenset({"import_module", "__import__", "exec", "eval", "execfile", "run_path", "run_module",
                             "spec_from_file_location", "load_source", "SourceFileLoader"})
TOKEN_REFS = ("github.token", "GITHUB_TOKEN")
SUBPROCESS_CALLS = frozenset({"run", "call", "check_call", "check_output", "Popen", "system", "popen", "execv", "execve",
                              "execvp", "execl", "spawnv", "spawnl"})
SUBPROCESS_OWNERS = frozenset({"subprocess", "os", "sp"})
# A shell line that sources, evaluates or runs a script whose name is a variable or a command substitution.
SHELL_UNKNOWN = re.compile(
    r"(?m)^[ \t]*(?:(?:source|\.)[ \t]+[\"']?[$`]"
    r"|eval[ \t]"
    r"|(?:bash|sh|python3?|node)[ \t]+(?:-[A-Za-z]+[ \t]+)*[\"']?\$[A-Za-z_{(@*0-9])")

OWNER_GATED_KEYS = ("secret_job_executed_paths", "secret_job_named_files", "unresolved_edge_paths")
HIGH_FLOOR_KEYS = ("writer_job_executed_paths", "writer_job_named_files", "writer_unresolved_edge_paths")
# The path lists that are derived live per tree and are not enumerated in 00_FMOS/S1_WORKFLOW_ISOLATION_V1.json.
PATH_LIST_KEYS = ("secret_job_executed_paths", "writer_job_executed_paths", "secret_job_named_files",
                  "writer_job_named_files", "unresolved_edge_paths", "writer_unresolved_edge_paths")


class DerivationError(ValueError):
    """The tree cannot be derived. The caller must treat every path as OWNER_GATED (never as an empty closure)."""


# ---------------------------------------------------------------- pure functions of a parsed workflow
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


def names_token(job):
    text = json.dumps(job, default=str)
    return any(ref in text for ref in TOKEN_REFS)


def _has_literal(node):
    return any(isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value.strip() for n in ast.walk(node))


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


def run_lines(job):
    return [str(s.get("run", "")) for s in (job.get("steps") or []) if "run" in s]


def runs_script(job, script):
    """True when a run line executes script (a py_compile syntax check does not execute it)."""
    commands = [cmd for run in run_lines(job) for cmd in run.replace("\\\n", " ").splitlines()]
    return any(script in cmd and "py_compile" not in cmd for cmd in commands)


SITE_BUILD = "scripts/governance/s1_site_public_readback_v1.py"
SITE_ARTIFACT = {"name": "s1-site-public-${{ github.run_id }}-${{ github.run_attempt }}",
                 "path": "${{ runner.temp }}/s1-site-public"}


def isolated_site_build_job(doc):
    """The one job that runs the PR-controlled Pages build for the privacy job: no secret, no write scope, no
    persisted checkout credential, no dependency, and its only output is the artifact of this run and attempt."""
    job = (doc.get("jobs") or {}).get("site-public-build")
    if not job:
        return False
    steps = job.get("steps") or []
    checkout = [s.get("with") or {} for s in steps if s.get("uses") == "actions/checkout@v4"]
    upload = [s.get("with") or {} for s in steps if s.get("uses") == "actions/upload-artifact@v4"]
    runs = run_lines(job)
    return (not receives_secret(doc, job) and not write_scoped(doc, job) and not names_token(job)
            and not job.get("needs") and not job.get("permissions")
            and [s.get("uses") for s in steps if "uses" in s] == ["actions/checkout@v4", "actions/setup-node@v4",
                                                                  "actions/upload-artifact@v4"]
            and len(checkout) == 1 and checkout[0].get("persist-credentials") is False
            and len(runs) == 1 and runs[0].startswith(f"python3 -I {SITE_BUILD} build ")
            and len(upload) == 1 and {k: upload[0].get(k) for k in SITE_ARTIFACT} == SITE_ARTIFACT)


def isolated_privacy_job(doc):
    """The privacy job runs no PR-controlled step. Since fix 4 it reads one artifact (bytes) from site-public-build:
    it needs that job only for the artifact and runs whatever its outcome (always()); nothing else was added."""
    job = (doc.get("jobs") or {}).get("privacy-scan")
    if not job:
        return False
    steps = job.get("steps") or []
    uses = [s.get("uses") for s in steps if "uses" in s]
    runs = run_lines(job)
    mode = [s.get("env", {}).get("S1_PRIVACY_SCAN_MODE") for s in steps if "run" in s]
    staged = [s.get("env", {}).get("S1_SITE_PUBLIC_READBACK_DIR") for s in steps if "run" in s]
    download = [s.get("with") or {} for s in steps if s.get("uses") == "actions/download-artifact@v4"]
    return (list(doc["jobs"])[0] == "privacy-scan"
            and uses == ["actions/checkout@v4", "actions/setup-python@v5", "actions/download-artifact@v4"]
            and runs == [f"python -I {PRIVACY}"] and mode == ["enforce"]
            and job.get("needs") == "site-public-build" and str(job.get("if", "")).startswith("always() && ")
            and download == [SITE_ARTIFACT] and staged == [SITE_ARTIFACT["path"]]
            and isolated_site_build_job(doc))


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


# ---------------------------------------------------------------- one tree
class Tree:
    """The derivation for one repository tree. Every cache lives on the instance, so two roots never share one and a
    tree that changes between two derive(root) calls is read again."""

    def __init__(self, root: Path | str):
        self.root = Path(root)
        self.wf = self.root / ".github" / "workflows"
        self._edges: dict[str, tuple[set[str], bool]] = {}
        self._imports: dict[str, set[str]] = {}
        self._seed_tokens: dict[str, frozenset[str]] = {}
        self._workflows: list[tuple[str, str, dict]] | None = None

    def workflows(self):
        """(file name, text, parsed mapping) of every workflow. Fail closed on anything that is not a readable
        mapping whose jobs are mappings."""
        if self._workflows is None:
            if not self.wf.is_dir():
                raise DerivationError(f"no workflow directory at {self.wf}: the tree cannot be derived")
            out = []
            for path in sorted(self.wf.glob("*.y*ml")):
                try:
                    text = path.read_text(encoding="utf-8")
                    doc = yaml.safe_load(text) or {}
                except (yaml.YAMLError, OSError, UnicodeDecodeError) as exc:
                    reason = " ".join(str(exc).split())[:300]
                    raise DerivationError(f"unparsable workflow .github/workflows/{path.name}: {reason}") from exc
                jobs = doc.get("jobs") if isinstance(doc, dict) else None
                if not isinstance(doc, dict) or not isinstance(jobs or {}, dict) or not all(
                        isinstance(job, dict) for job in (jobs or {}).values()):
                    raise DerivationError(f"unparsable workflow .github/workflows/{path.name}: not a mapping of jobs")
                out.append((path.name, text, doc))
            self._workflows = out
        return iter(self._workflows)

    def file_text(self, rel):
        try:
            return (self.root / rel).read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            return ""

    def dynamic_edges(self, rel):
        """(resolved local targets, unresolved) for the dynamic loads of a code file.

        Python: a literal module name that is no repository file is the standard library or an installed package:
        resolved, nothing to follow. A literal file name is resolved against the file's own directory and its ancestors.
        exec, eval, a load whose target no literal names, and a subprocess or os.system call whose command holds no
        literal at all are UNKNOWN (N20). A loader imported under another name (from importlib import import_module as x)
        is followed by its real name. Shell: source, eval or an interpreter run on a variable is UNKNOWN.
        UNKNOWN means the caller must not treat the closure as complete."""
        root = self.root
        if rel.endswith(".sh"):
            return set(), bool(SHELL_UNKNOWN.search(self.file_text(rel)))
        if not rel.endswith(".py"):
            return set(), False
        try:
            tree = ast.parse(self.file_text(rel))
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
                        if (root / cand).is_file():
                            targets.add(cand)
                            found = True
                elif re.fullmatch(r"[A-Za-z_][\w.]*", lit):
                    found = True                           # a literal module name
                    for base in bases:
                        cand = (base / (lit.replace(".", "/") + ".py")).as_posix()
                        cand = cand[2:] if cand.startswith("./") else cand
                        if (root / cand).is_file():
                            targets.add(cand)
            if name in ("import_module", "__import__", "run_module") and not any(
                    isinstance(a, ast.Constant) and isinstance(a.value, str) for a in node.args[:1]):
                found = False                              # the module name itself is computed
            if not found:
                unresolved = True
        return targets, unresolved

    def expanded_steps(self, job):
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
                path = self.root / uses[2:] / name
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

    def step_text_is_unknown(self, job):
        """A run line of the job itself that sources, evaluates or runs a computed script, or an unreadable local action."""
        for step in self.expanded_steps(job):
            if step.get("s1_unknown_local_action") or SHELL_UNKNOWN.search(str(step.get("run", ""))):
                return True
        return False

    def file_edges(self, rel):
        """Every file that rel loads (memoised on this tree): (targets, has an unresolved dynamic edge)."""
        if rel not in self._edges:
            targets, unknown = self.dynamic_edges(rel)
            self._edges[rel] = (targets | self.import_edges(rel), unknown)
        return self._edges[rel]

    def full_closure(self, job):
        """Files a job executes: the v2 closure (imports, sys.path edits, literal paths) over the job's steps and the
        steps of its local composite actions, plus literal dynamic loads.
        Returns (code paths, files with an unresolved dynamic edge)."""
        closure = set(self.job_executed_paths({"steps": self.expanded_steps(job)}))
        unresolved = set()
        frontier = set(closure)
        seen = set()
        while frontier:
            new = set()
            for rel in frontier:
                seen.add(rel)
                edges, unknown = self.file_edges(rel)
                if unknown:
                    unresolved.add(rel)
                new |= edges - closure
            new = {p for p in new if not p.startswith(".github/")}
            closure |= new
            frontier = new - seen
        return closure, unresolved

    def named_files(self, job):
        """Non-code file paths that a job's steps name, from the workflow text alone (existence is not checked)."""
        step_text = json.dumps(self.expanded_steps(job), default=str).replace("\\n", "\n")
        found = set()
        for token in sp._TOKEN.findall(step_text):
            token = token.rstrip(".")
            token = token[2:] if token.startswith("./") else token
            if ("/" in token and token.endswith(CONFIG_SUFFIXES) and not token.startswith(("/", "-", ".github/"))
                    and ".." not in token.split("/")):
                found.add(token)
        return found

    def _seed_token(self, token):
        """The files one workflow token names (memoised on this tree: the same directory is named by many jobs)."""
        if token not in self._seed_tokens:
            root, found = self.root, set()
            cand = root / token
            if "/" in token and cand.is_file():
                if token.endswith(sp._CODE_SUFFIXES):
                    found.add(token)
            elif "/" in token and cand.is_dir():
                found |= {p.relative_to(root).as_posix() for p in cand.rglob("*") if p.is_file() and p.suffix in sp._CODE_SUFFIXES}
            elif "." in token and "/" not in token and (root / (token.replace(".", "/") + ".py")).is_file():
                found.add(token.replace(".", "/") + ".py")
            self._seed_tokens[token] = frozenset(found)
        return self._seed_tokens[token]

    def job_seed(self, text):
        """Files a job runs, imports or reads as config: code files named or under a named directory, and config files
        named explicitly. Data under a directory the job writes or reads in bulk is data, not code (not followed)."""
        found = set()
        for token in sp._TOKEN.findall(text):
            token = token.rstrip(".")
            if not token or token.startswith(("/", "-", ".github")) or ".." in token.split("/"):
                continue
            found |= self._seed_token(token)
        return found

    def imports_via_sys_path(self, rel):
        """A file that edits sys.path may import from any ancestor directory (R2 P1-1, e.g. lib.evidence_io)."""
        root = self.root
        if not rel.endswith(".py"):
            return set()
        try:
            text = (root / rel).read_text(encoding="utf-8")
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
                        if (root / cand).is_file():
                            found.add(cand)
        return found

    def import_edges(self, rel):
        """Local imports of rel (memoised on this tree; the v2 derivation, unchanged)."""
        if rel not in self._imports:
            self._imports[rel] = sp._local_imports(self.root, rel) | self.imports_via_sys_path(rel)
        return self._imports[rel]

    def job_executed_paths(self, job):
        text = json.dumps(job.get("steps") or [], default=str).replace("\\n", "\n")
        closure = self.job_seed(text)
        frontier = set(closure)
        while frontier:
            new = set()
            for rel in frontier:
                new |= self.import_edges(rel) - closure
            closure |= new
            frontier = new
        return {p for p in closure if not p.startswith(".github/")}

    def derive(self) -> dict:
        secret_jobs, executed, pr_write, secret_on_pr = [], set(), [], []
        writer_jobs, token_ref_jobs, writer_paths, config_paths, unresolved = [], [], set(), set(), set()
        writer_config, writer_unresolved, unknown_step_jobs = set(), set(), []
        artifact_edges, action_refs, persisted = [], set(), []
        gate = {"privacy": False, "truth": False}
        for name, text, doc in self.workflows():
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
                    executed |= self.job_executed_paths(job)
                    closure, unknown = self.full_closure(job)
                    executed |= closure
                    config_paths |= self.named_files(job)
                    unresolved |= unknown
                    if can_run_on_pr(doc, job):
                        secret_on_pr.append(key)
                elif write or token:
                    (writer_jobs if write else token_ref_jobs).append(key)
                    closure, unknown = self.full_closure(job)
                    writer_paths |= closure
                    writer_config |= self.named_files(job)
                    writer_unresolved |= unknown
                if (secret or write or token) and self.step_text_is_unknown(job):
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


# ---------------------------------------------------------------- public API
def derive(root: Path | str) -> dict:
    """The derivation of the tree at root. Raises DerivationError when the workflows cannot be read."""
    return Tree(root).derive()


def lane_classification(changed_paths: Iterable[str], derivations: Sequence[Mapping[str, Any]]) -> dict:
    """Which changed paths are lane-excluded (owner_gated) or risk HIGH at least (high_floor).

    derivations: derive(main tree) and derive(PR head tree). The UNION decides, so a head that deletes the edge that
    makes a file secret-run does not un-list that file. Pass every changed path and every previous_filename."""
    derivations = list(derivations)
    if not derivations:
        raise DerivationError("no derivation given: every changed path is OWNER_GATED")
    owner, high = set(), set()
    for d in derivations:
        missing = [k for k in PATH_LIST_KEYS if not isinstance(d.get(k) if isinstance(d, Mapping) else None, list)]
        if missing:
            raise DerivationError(f"a derivation lacks {missing}: pass derive(root), not the pinned isolation file")
        for key in OWNER_GATED_KEYS:
            owner |= set(d[key])
        for key in HIGH_FLOOR_KEYS:
            high |= set(d[key])
    changed = set()
    for path in changed_paths:
        path = str(path).strip()
        path = path[2:] if path.startswith("./") else path
        if path:
            changed.add(path)
    return {"owner_gated": sorted(changed & owner), "high_floor": sorted((changed & high) - owner)}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", required=True, help="the tree to derive (with --changed: the PR head tree)")
    parser.add_argument("--base-root", help="the main tree (required with --changed)")
    parser.add_argument("--changed", help="a file with one changed path per line (also every previous_filename)")
    parser.add_argument("--json", action="store_true", help="print the whole derivation as JSON")
    args = parser.parse_args(argv)
    try:
        if args.changed:
            if not args.base_root:
                raise DerivationError("--changed needs --base-root: the classification is the union of main and head")
            try:
                changed = Path(args.changed).read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeDecodeError) as exc:
                raise DerivationError(f"cannot read --changed {args.changed}: {exc}") from exc
            result = lane_classification(changed, [derive(args.base_root), derive(args.root)])
            print(json.dumps(result, indent=2))
            return 0
        derived = derive(args.root)
    except DerivationError as exc:
        print(f"DERIVATION_FAILED (fail closed, treat every path as OWNER_GATED): {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(derived, indent=2))
    else:
        for key, value in derived.items():
            print(f"{key}: {value if isinstance(value, str) else len(value)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
