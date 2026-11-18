"""S1_TICK_BRIEF_V1: GitHub prepares the S1 tick; S1 verifies the brief and acts.

Read-only towards the repository. The build half reads GitHub natively with the job token (contents, actions and
pull-requests read) and never executes or imports code from a pull-request head; the publish half holds issues:write
and only writes the one brief issue. The brief is evidence, never authority: 00_FMOS/S1/TICK.md says which facts S1
re-reads natively before it acts, and a missing, stale or unauthentic brief is a NOOP, never a full census.

Layout: pure functions first (tested with fixtures in tests/governance/test_s1_tick_brief_v1.py), then the GitHub
reader, then the two command-line entry points `build` and `publish`.
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.dont_write_bytecode = True
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import check_codex_review_finality as codex_finality  # noqa: E402  (same directory, pinned with this file)
import s1_native_job_identity_v1 as job_identity  # noqa: E402  (its redirect handler: no bearer token across hosts)

SCHEMA = "S1_TICK_BRIEF_V1"
REPO = "Donh91/Investering-Framework-Archive-v1"
OWNER_LOGIN = "Donh91"
OWNER_ISSUE = 1156
BRIEF_LABEL = "s1-tick-brief"
BRIEF_TITLE = "S1 tick brief (machine-written by .github/workflows/s1-tick-brief.yml; do not edit)"
WORKFLOW_PATH = ".github/workflows/s1-tick-brief.yml"
ACTIONS_BOT = {"login": "github-actions[bot]", "id": 41898282, "type": "Bot"}
CODEX_BOT_LOGIN = "chatgpt-codex-connector[bot]"
TASK_ID = "6ae5fd466b48819187abc224ec0f1c5f"
BEGIN, END = "<!-- S1_TICK_BRIEF_V1 BEGIN -->", "<!-- S1_TICK_BRIEF_V1 END -->"
MAX_BODY = 60000                      # GitHub refuses an issue body above 65536 characters
MAX_AGE_MINUTES = 45                  # TICK.md: an older brief is BRIEF_STALE
MAX_PATHS_PER_PR = 60
MAX_DEPTH_PRS = 15                    # same-repository non-draft PRs read in depth per run (API budget), most recently updated
                                      # first; any PR left unread makes the brief complete=false and is listed NOT_READ:depth_cap
BINARY_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".woff", ".woff2", ".ttf", ".parquet", ".zip", ".gz")
DATA_SUFFIXES = (".json", ".jsonl", ".ndjson", ".csv", ".tsv", ".parquet", ".db", ".sqlite", ".log")
RECORD_NAME = re.compile(r"(?i)ledger|receipt|journal|histor|episode|registry|manifest|audit|\bLOG\b|_log\b|changelog")
ADDRESS_RE = re.compile(r"(?i)@codex\b[^\n]{0,24}\b(?:address|fix|resolve|repair)\b")
HALT_RE = re.compile(r"(?m)^\W{0,8}S1_LANE_HALTED\b")
FAST_RISKS = ("LOW", "MEDIUM")        # a HIGH merge entry carries high_evidence=true: S1 proves HIGH EVIDENCE itself
FAILED_CONCLUSIONS = ("failure", "timed_out", "startup_failure", "cancelled")
SHA40 = re.compile(r"[0-9a-f]{40}")
S1_FILES = "00_FMOS/S1"
SWITCH = "00_FMOS/S1/REVIEWED_MERGE_LANE.json"
CONTRACT_FILE = "00_FMOS/S1/RUNTIME_CONTRACT.json"
POLICY_FILE = "00_FMOS/S1_REQUIRED_PR_JOBS_POLICY_V1.json"
ISOLATION_FILE = "00_FMOS/S1_WORKFLOW_ISOLATION_V1.json"
BINDINGS_FILE = "00_FMOS/S1/EVIDENCE_BINDINGS.md"
PRIVACY_PREFIX = "S1_NATIVE_PRIVACY" + "_SCAN_STEP_V1"     # split: this file must never contain the gate marker itself
SITE_PREFIX = "05_CYCLE_NAVIGATOR/site/"

# AGENTS.md section 0.2e exclusions 10 and 11, matched on ADDED lines of the diff. Tokens are assembled so that this
# file's own text does not carry them.
WRITER_TOKENS = [r"\bgit\b[^\n|;&]{0,80}?\b(?:push|commit|tag|branch|merge)\b", r"""['"]git['"]\s*,\s*(?:['"][^'"]*['"]\s*,\s*)*['"](?:push|commit|tag|branch|merge)['"]""", r"(?<![\w.-])gh\s", r"api\.github\.com", r"/pulls\b",
                 r"/merges\b", r"/git/refs", r"GITHUB" + r"_TOKEN", r"GH" + r"_TOKEN", r"\.git/", r"core\.hooksPath",
                 r"\bgit\s+config\b", r"\bGIT_[A-Z_]+\s*=", r"persist-credentials"]
FORGERY_TOKENS = [PRIVACY_PREFIX, "GITHUB" + "_STEP_SUMMARY", "GITHUB" + "_OUTPUT", "GITHUB" + "_EVENT_PATH",
                  "full-repository-tests" + ".xml", "junit" + "xml"]
_WRITER_RE = re.compile("|".join(WRITER_TOKENS))
_FORGERY_RE = re.compile("|".join(re.escape(t) for t in FORGERY_TOKENS))
TEXT_SUFFIXES = (".py", ".md", ".json", ".yml", ".yaml", ".txt", ".mjs", ".js", ".ts", ".html", ".css", ".csv", ".toml",
                 ".cfg", ".ini", ".sh", ".jsonl", ".sql", ".rs", ".tsx", ".jsx", ".xml", ".svg")
INSTALLED_TOP_LEVEL = frozenset({"pytest", "yaml", "pandas", "numpy", "jsonschema", "sklearn", "rfc3339_validator", "pip",
                                 "setuptools", "requests", "scipy", "_pytest", "pluggy", "iniconfig", "packaging"})


# ----------------------------------------------------------------------------------------------- small helpers
def stamp(value):
    """An aware UTC datetime from a GitHub timestamp; raises ValueError on anything else (callers fail closed)."""
    if not isinstance(value, str) or not value:
        raise ValueError("TIMESTAMP_MISSING")
    d = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if d.tzinfo is None:
        raise ValueError("TIMESTAMP_UNAWARE")
    return d.astimezone(timezone.utc)


def iso(d):
    return d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def login(row):
    user = (row or {}).get("user") or {}
    return user.get("login") if isinstance(user, dict) else None


def is_owner_unedited(row):
    """The framework's behavioural authenticity idiom for S1 and Claude posts: owner account, never edited."""
    return login(row) == OWNER_LOGIN and bool(row.get("created_at")) and row.get("created_at") == row.get("updated_at")


def is_actions_bot(user):
    return isinstance(user, dict) and all(user.get(k) == v for k, v in ACTIONS_BOT.items())


def fields(body):
    """`key: value` and `key=value` lines of a receipt, first occurrence wins (a later line never overrides)."""
    out = {}
    for line in str(body or "").splitlines():
        m = re.match(r"^\s*(?:[-*]\s+)?([A-Za-z_][A-Za-z0-9_ ]{0,40}?)\s*[:=]\s*(.*?)\s*$", line)
        if m and m.group(1).strip().lower() not in out:
            out[m.group(1).strip().lower()] = m.group(2)
    return out


def first_line_token(body):
    for line in str(body or "").splitlines():
        if line.strip():
            return line.strip().split()[0]
    return ""


def has_line(body, token):
    return any(line.strip().startswith(token) for line in str(body or "").splitlines())


# ----------------------------------------------------------------------------------------------- pins
def pin_check(switch, contract, actual, bootstrap_text):
    """LANE INTEGRITY plus the S1 chain, at the brief's main. `actual` maps every pinned path to its blob or tree SHA."""
    mismatch = []
    pins = switch.get("pins") if isinstance(switch, dict) else None
    if not isinstance(pins, dict) or not pins:
        mismatch.append("switch:pins_missing")
        pins = {}
    for path, want in sorted(pins.items()):
        if actual.get(path) != want:
            mismatch.append(f"pins:{path}")
    chain = {"action_loop_blob": contract.get("action_loop_path"), "lane_switch_blob": contract.get("lane_switch_path"),
             "tick_blob": contract.get("tick_path")}
    for key, path in chain.items():
        if not path or actual.get(path) != contract.get(key):
            mismatch.append(f"contract:{key}")
    for path, want in sorted((contract.get("rubric_blobs") or {}).items()):
        if actual.get(path) != want:
            mismatch.append(f"contract:rubric:{path}")
    m = re.search(r"must equal ([0-9a-f]{40})\.", bootstrap_text or "")
    if not m or m.group(1) != actual.get(CONTRACT_FILE):
        mismatch.append("bootstrap:3b")
    return {"ok": not mismatch, "mismatch": mismatch[:10], "paths": sorted(pins), "contract_blob": actual.get(CONTRACT_FILE),
            "action_loop_blob": actual.get(contract.get("action_loop_path") or ""),
            "tick_blob": actual.get(contract.get("tick_path") or ""),
            "switch_blob": actual.get(contract.get("lane_switch_path") or "")}


# ----------------------------------------------------------------------------------------------- #1156 ledger
def lane_halts(comments):
    """S1_LANE_HALTED posts on #1156 by the owner account, oldest first. An EDITED halt still counts: section 0.2e
    lane state 3 has no unedited condition, and ignoring an edited halt would fail open."""
    out = []
    for c in comments:
        if login(c) == OWNER_LOGIN and HALT_RE.search(str(c.get("body") or "")):
            f = fields(c.get("body"))
            out.append({"id": c["id"], "created_at": c["created_at"], "run": (f.get("run") or "").strip() or None,
                        "body": str(c.get("body") or "")})
    return sorted(out, key=lambda h: h["id"])


def standing_halt(halts, clears_halt):
    """Section 0.2e lane state 3: a halt newer than the last enable. Comment ids grow with time, and a re-enable names
    the newest halt in clears_halt, so every halt with a larger id is standing (clears_halt null: every halt is)."""
    floor = clears_halt if isinstance(clears_halt, int) and not isinstance(clears_halt, bool) else 0
    standing = [h for h in halts if h["id"] > floor]
    return standing[-1]["id"] if standing else None


def lane_merges(comments):
    out = []
    for c in comments:
        # edited receipts count too: this list only ever makes the halt trigger MORE likely (fail closed)
        if login(c) == OWNER_LOGIN and first_line_token(c.get("body")) == "S1_LANE_MERGE_v1":
            out.append({"id": c["id"], "created_at": c["created_at"]})
    return out


def open_intents(comments, now, settle_minutes=60):
    """A cheap SIGNAL for RECONCILE (EVIDENCE_BINDINGS B3), never the reconciliation itself: authentic v3 intents
    (they carry loop=) with no later outcome that names their PR or cites their id."""
    intents = []
    for c in comments:
        token = first_line_token(c.get("body"))
        if not is_owner_unedited(c) or token not in ("S1_LANE_MERGE_INTENT_v1", "S1_OP_INTENT_v1"):
            continue
        f = fields(c.get("body"))
        if "loop" not in f:
            continue                                   # a legacy intent: S1 decides case (i) natively, not this signal
        pr = re.search(r"\d+", f.get("pr", ""))
        intents.append({"id": c["id"], "kind": token, "pr": int(pr.group(0)) if pr else None, "created_at": c["created_at"]})
    out = []
    for it in intents:
        settled = False
        for c in comments:
            if c.get("id", 0) <= it["id"] or not is_owner_unedited(c):
                continue
            token, body = first_line_token(c.get("body")), str(c.get("body") or "")
            f = fields(body)
            if token == "S1_OP_DONE_v1" and re.search(rf"(?<!\d){it['id']}(?!\d)", body):
                settled = True
            elif token in ("S1_LANE_MERGE_v1", "S1_LANE_HALTED") and it["kind"] == "S1_LANE_MERGE_INTENT_v1" and it["pr"] is not None \
                    and re.search(rf"(?<!\d){it['pr']}(?!\d)", f.get("pr", "") or body.splitlines()[0]):
                settled = True
        if not settled:
            age = (now - stamp(it["created_at"])).total_seconds() / 60
            out.append({"id": it["id"], "kind": it["kind"], "pr": it["pr"], "age_min": int(age), "due": age > settle_minutes})
    return out


# ----------------------------------------------------------------------------------------------- main health
def main_health(runs, complete, now, merges, halts, params):
    """Section 0.2e lane state 4 and the halt trigger, ROUTE 1 semantics (the workflow's own run list)."""
    path, fresh_hours = params["workflow_path"], params["fresh_hours"]
    if not complete:
        return {"status": "NOT_PROVEN", "reason": "TOOL_CANNOT_READ"}
    kept = [r for r in runs if r.get("path") == path and r.get("event") == "schedule" and r.get("head_branch") == "main"
            and ((r.get("head_repository") or {}).get("full_name") == REPO)]
    done = [r for r in kept if r.get("status") == "completed"]
    out = {"status": "NOT_PROVEN", "reason": "main_health_stale", "run_id": None, "unhalted_failed_runs": []}
    try:
        if merges:
            first_merge = min(stamp(m["created_at"]) for m in merges) - timedelta(minutes=60)   # receipt follows merge
            named = " ".join(h["body"] for h in halts)
            for r in done:
                if r.get("conclusion") in FAILED_CONCLUSIONS and stamp(r["updated_at"]) > first_merge \
                        and not re.search(rf"(?<!\d){r['id']}(?!\d)", named):
                    out["unhalted_failed_runs"].append(r["id"])
        if not done:
            return out
        newest = max(done, key=lambda r: stamp(r["updated_at"]))
        age_h = (now - stamp(newest["updated_at"])).total_seconds() / 3600
    except (ValueError, KeyError, TypeError):
        return {"status": "NOT_PROVEN", "reason": "main_health_unreadable"}
    out.update(run_id=newest["id"], conclusion=newest.get("conclusion"), updated_at=newest["updated_at"], age_h=round(age_h, 2))
    if newest.get("conclusion") != "success":
        out.update(status="FAIL", reason="main_health_failed")
    elif age_h > fresh_hours or age_h < 0:
        out.update(status="NOT_PROVEN", reason="main_health_stale")
    else:
        out.update(status="PASS", reason=None)
    if out["unhalted_failed_runs"]:
        out.update(status="FAIL", reason="unhalted_failed_run")
    return out


def lane_state(switch, pins, halt_id, health):
    reasons = []
    if not (isinstance(switch, dict) and switch.get("contract") == "S1_REVIEWED_MERGE_LANE_v1" and switch.get("state") == "ON"):
        reasons.append("switch")
    reasons += [m for m in pins["mismatch"]][:3]
    if halt_id is not None:
        reasons.append(f"halt c={halt_id}")
    if health.get("status") != "PASS":
        reasons.append(f"main_health:{health.get('reason')}")
    mm = switch.get("max_merges_per_tick") if isinstance(switch, dict) else None
    mm = mm if isinstance(mm, int) and not isinstance(mm, bool) and 1 <= mm <= 3 else 1
    return {"state": "OFF" if reasons else "ON", "off_reasons": reasons, "max_merges_per_tick": mm,
            "steward_state": switch.get("steward_state") if isinstance(switch, dict) else None}


def ruleset_census(read1, read2, complete):
    """Section 0.2c F3: two identical complete reads of the ruleset list."""
    key = lambda rows: sorted([r.get("id"), r.get("target"), r.get("enforcement"), r.get("updated_at")] for r in rows)
    try:
        a, b = key(read1), key(read2)
    except (TypeError, AttributeError):
        return {"stable": False, "census": None}
    return {"stable": bool(complete) and a == b, "census": a, "active": sum(1 for r in a if r[2] == "active")}


# ----------------------------------------------------------------------------------------------- CI identity (B4)
def ci_tuples(head, repo_id, runs, runs_complete, jobs_by_run, tuples):
    """EVIDENCE_BINDINGS B4: workflow path + job + latest attempt + head SHA + executed must-run steps."""
    out = {}
    for t in tuples:
        name = t["job"]
        if not runs_complete:
            out[name] = {"s": "NOT_PROVEN", "why": "runs_unreadable"}
            continue
        kept = [r for r in runs if r.get("path") == t["workflow_path"] and r.get("head_sha") == head
                and r.get("event") == t["event"] and (r.get("repository") or {}).get("id") == repo_id
                and (r.get("head_repository") or {}).get("id") == repo_id]
        if not kept:
            out[name] = {"s": "MISSING", "why": "no_run"}
            continue
        run = max(kept, key=lambda r: r.get("run_number") or 0)
        rec = {"run": run["id"], "att": run.get("run_attempt")}
        if run.get("status") != "completed":
            out[name] = dict(rec, s="PENDING", why="run_in_progress")
            continue
        jobs = jobs_by_run.get(run["id"])
        if jobs is None:
            out[name] = dict(rec, s="NOT_PROVEN", why="jobs_unreadable")
            continue
        match = [j for j in jobs if j.get("name") == name and j.get("run_attempt") == run.get("run_attempt")]
        if len(match) != 1:
            out[name] = dict(rec, s="MISSING" if not match else "NOT_PROVEN", why="job_not_in_latest_attempt" if not match else "job_ambiguous")
            continue
        job = match[0]
        rec["job"] = job.get("id")
        if job.get("status") != "completed":
            out[name] = dict(rec, s="PENDING", why="job_in_progress")
        elif job.get("conclusion") != "success" or job.get("head_sha") != head:
            out[name] = dict(rec, s="FAIL", why=f"job:{job.get('conclusion')}" if job.get("head_sha") == head else "job_other_sha")
        else:
            steps = {s.get("name"): s.get("conclusion") for s in job.get("steps") or []}
            bad = [s for s in t["must_run_steps"] if steps.get(s) != "success"]
            out[name] = dict(rec, s="NOT_PROVEN", why="step_not_run") if bad else dict(rec, s="PASS")
    return out


def privacy_line(log_text, head):
    """Section 0.2e gate (b): EXACTLY ONE marker line in the isolated job's log, for this head."""
    if log_text is None:
        return {"result": None, "why": "log_unreadable"}
    lines = []
    for raw in log_text.splitlines():
        at = raw.find(PRIVACY_PREFIX)
        # a log line is "<timestamp> <text>"; the marker must START the text (a quoted or echoed marker never counts)
        if at >= 0 and re.fullmatch(r"(?:﻿)?(?:\d{4}-\d{2}-\d{2}T[0-9:.]+Z )?", raw[:at]):
            lines.append(raw[at:].strip())
    if len(lines) != 1:
        return {"result": None, "why": f"marker_lines={len(lines)}"}
    m = re.match(re.escape(PRIVACY_PREFIX) + r" result=([A-Z_]+) head=([0-9a-f]{40})(?:\s|$)", lines[0])
    if not m or m.group(2) != head:
        return {"result": None, "why": "marker_other_head_or_shape"}
    return {"result": m.group(1), "why": None}


def checks_summary(check_runs, statuses, complete):
    """Gate (c): every check run and status on the head is success, neutral or skipped; none pending or failed."""
    if not complete:
        return {"green": False, "why": "checks_unreadable"}
    latest = {}
    for c in check_runs:                                   # the newest run of each (app, name) is the one that counts
        key = ((c.get("app") or {}).get("slug"), c.get("name"))
        if key not in latest or (c.get("id") or 0) > (latest[key].get("id") or 0):
            latest[key] = c
    pending = [c["name"] for c in latest.values() if c.get("status") != "completed"]
    failed = [c["name"] for c in latest.values() if c.get("status") == "completed"
              and c.get("conclusion") not in ("success", "neutral", "skipped")]
    newest_status = {}
    for s in sorted(statuses, key=lambda s: s.get("id") or 0):
        newest_status[s.get("context")] = s.get("state")
    pending += [k for k, v in newest_status.items() if v == "pending"]
    failed += [k for k, v in newest_status.items() if v in ("failure", "error")]
    return {"green": not pending and not failed, "n": len(latest) + len(newest_status), "pending": sorted(pending)[:5],
            "failed": sorted(failed)[:5]}


# ----------------------------------------------------------------------------------------------- lane paths
def _governance(path, policy):
    return path in set(policy.get("governance_exact_paths") or []) or any(path.startswith(p) for p in policy.get("governance_prefixes") or [])


def path_exclusions(files, files_complete, policy, gate_isolation_live, isolation):
    """AGENTS.md section 0.2e exclusions that are a function of the diff: 1, 2, 3, 7, 10 and 11. The judgment exclusions
    (4 custody, 5 money, 6 privacy, 8 Round 3, 9 unclear) stay with the reviewer's lane_eligible line and with S1.
    Returns (reasons, risk_floor). Any reason makes the PR OWNER_GATED."""
    reasons = []
    add = lambda rule, path: reasons.append(f"x{rule}:{path}")
    if not files_complete:
        return ["x9:file_list_incomplete"], "UNCLEAR"
    required = set(policy.get("required_job_executed_paths") or [])
    required_dirs = {str(Path(p).parent) for p in required}
    stdlib = set(getattr(sys, "stdlib_module_names", ())) | INSTALLED_TOP_LEVEL
    code = False
    for f in files:
        names = [f.get("filename")] + ([f["previous_filename"]] if f.get("previous_filename") else [])
        status = f.get("status")
        for p in names:
            if not isinstance(p, str) or not p:
                add(9, "unreadable_path")
                continue
            base, parts = p.rsplit("/", 1)[-1], p.split("/")
            if _governance(p, policy) or (p in required and not gate_isolation_live):
                add(1, p)
            elif p.startswith("07_PROMPTS_AND_AGENTS/") or "__canonical." in base or "BOUNDARY" in p or "AUTHORITY" in p:
                add(1, p)
            if any(p.startswith(x) for x in ("scripts/health/", "scripts/data_governance/", "scripts/data_storage/",
                                              "tests/data_governance/", "tests/data_storage/", "research/data_governance/")) \
                    or base == "conftest.py" or p in ("pytest.ini", "pyproject.toml", "setup.cfg", "tox.ini") \
                    or base.startswith("requirements") or base in ("sitecustomize.py", "usercustomize.py") or base.endswith(".pth") \
                    or (len(parts) == 1 and base.endswith(".py")) \
                    or (base == "__init__.py" and parts[0] in ("tests", "scripts")):
                add(2, p)
            elif base.endswith(".py") and status in ("added", "renamed", "copied") and p == f.get("filename") \
                    and (base[:-3] in stdlib or str(Path(p).parent) in required_dirs):
                add(2, p)
            if p.endswith((".py", ".mjs", ".js", ".ts", ".sh", ".rs")) and not p.startswith("tests/") and "/tests/" not in p \
                    and not base.startswith("test_") and ".test." not in base:
                code = True
        p = f.get("filename") or ""
        outside = not (p.startswith("scripts/") or p.startswith("tests/"))
        prev = f.get("previous_filename") or ""
        if (status == "removed" and outside) or (status == "renamed" and prev and not (prev.startswith("scripts/") or prev.startswith("tests/"))) \
                or (status == "modified" and outside and (f.get("deletions") or 0) > 0
                    and ((f.get("additions") or 0) == 0
                         or ((p.endswith(DATA_SUFFIXES) or RECORD_NAME.search(p)) and (f.get("deletions") or 0) > (f.get("additions") or 0)))):
            add(7, prev or p)
        elif status == "modified" and outside and f.get("patch") is None and (p.lower().endswith(DATA_SUFFIXES + (".gz", ".zip", ".parquet")) or RECORD_NAME.search(p)):
            add(7, p)                                          # a replaced binary record: its line counts say nothing
        patch = f.get("patch")
        if patch is None:
            # GitHub omits the patch of a large or binary file. Only a known binary type is let through (the judgment
            # rule covers it); every other file with no readable patch is unclear, whatever its suffix.
            if status != "removed" and not p.lower().endswith(BINARY_SUFFIXES) and not (status == "renamed" and (f.get("changes") or 0) == 0):
                add(11, f"{p}:no_patch")
        else:
            added = "\n".join(line[1:] for line in patch.splitlines() if line.startswith("+") and not line.startswith("+++"))
            if _WRITER_RE.search(added):
                add(10, p)
            if _FORGERY_RE.search(added):
                add(11, p)
    if isolation is None:
        reasons.append("x3:isolation_not_derived")
    else:
        for p in isolation.get("owner_gated") or []:
            add(3, p)
    paths = [f.get("filename") or "" for f in files]
    if reasons:
        floor = "OWNER_GATED"
    elif (isolation or {}).get("high_floor") or any(p.startswith(SITE_PREFIX) for p in paths) \
            or any(p.startswith(("data/", "02_DATA_PING/", "03_DAILY_CAPTURE_LOGS/")) or p.endswith((".jsonl", ".csv", ".parquet")) for p in paths):
        floor = "HIGH"
    elif code:
        floor = "MEDIUM"
    else:
        floor = "LOW"
    return sorted(set(reasons)), floor


# ----------------------------------------------------------------------------------------------- reviews and writers
def head_commit_time(commits, head):
    for c in commits:
        if c.get("sha") == head:
            return stamp(((c.get("commit") or {}).get("committer") or {}).get("date"))
    raise ValueError("HEAD_COMMIT_NOT_IN_LIST")


def authorship(pr, commits, commits_complete, comments):
    ref = ((pr.get("head") or {}).get("ref") or "")
    if not commits_complete or len(commits) > 250:
        return {"s1": True, "codex": True, "why": "commit_list_incomplete"}
    s1 = ref.startswith("s1/") or any(f"S1-Authored-By: {TASK_ID}" in ((c.get("commit") or {}).get("message") or "") for c in commits)
    codex = ref.startswith("codex/") or login(pr) == CODEX_BOT_LOGIN \
        or any(((c.get("author") or {}).get("login") == CODEX_BOT_LOGIN) or ((c.get("committer") or {}).get("login") == CODEX_BOT_LOGIN) for c in commits)
    # REVIEW_ADMISSION: "@codex address" answered by Codex makes the head CODEX_AUTHORED (its commits may carry another
    # login). Fail closed: ANY "@codex address" request on the PR counts, answered or not, and an unreadable comment
    # list counts too.
    if comments is None or any(not codex_finality.is_codex(c) and ADDRESS_RE.search(str(c.get("body") or "")) for c in comments) \
            or any((c.get("performed_via_github_app") or {}).get("slug") == "chatgpt-codex-connector" for c in commits) \
            or (pr.get("performed_via_github_app") or {}).get("slug") == "chatgpt-codex-connector" \
            or re.search(r"(?i)\bcodex\b.{0,40}\b(created|authored|addressed|implemented)\b", str(pr.get("body") or "")):
        codex = True
    body = str(pr.get("body") or "")
    package = bool(re.search(r"(?i)implements bridge package|claude-authored package", body))
    return {"s1": s1, "codex": codex, "claude_package": package}


def codex_review(head, pr, commits, commits_complete, comments, reviews, inline, complete, now, silent_hours):
    """REVIEW_ADMISSION (i) through the repository's own finality rule, plus the request state rule 3 needs."""
    out = {"status": "NONE", "requested_after_head": False}
    if not complete:
        return {"status": "NOT_PROVEN", "why": "review_reads_incomplete"}
    try:
        head_time = head_commit_time(commits, head) if commits_complete else None
        requests = [codex_finality.effective_request_time(c) for c in comments
                    if not codex_finality.is_codex(c) and re.search(r"(?mi)^\s*@codex\s+review\b", str(c.get("body") or ""))]
        after = [r for r in requests if head_time is not None and r > head_time]
        if after:
            last = max(after)
            out.update(requested_after_head=True, request_age_h=round((now - last).total_seconds() / 3600, 1))
            answers = [c for c in comments if codex_finality.is_codex(c) and stamp(c.get("updated_at") or c.get("created_at")) > last]
            if any(re.search(r"(?i)usage limit|reached your .*limit|can(?:'|no)t review|unable to review", str(c.get("body") or "")) for c in answers):
                out["status"] = "UNAVAILABLE"
            elif out["request_age_h"] > silent_hours:
                out["status"] = "SILENT"
            else:
                out["status"] = "REQUESTED"
        decision = codex_finality.decision(head, comments, reviews, inline)
    except (ValueError, KeyError, TypeError):
        return {"status": "NOT_PROVEN", "why": "review_unreadable"}
    if decision.get("technical_review_accepted") is True:
        if head_time is None or stamp(decision["review_requested_at"]) <= head_time:
            out.update(status="NOT_PROVEN", why="request_not_after_head_commit")
        else:
            out.update(status="FINAL", requested_at=decision["review_requested_at"])
    elif decision.get("status") in ("UNRESOLVED_CODEX_FINDINGS", "LATER_MATERIAL_REVIEW_FINDINGS", "CURRENT_HEAD_INLINE_FINDING"):
        out.update(status="FINDINGS", why=decision["status"])
    return out


def changes_requested(reviews, head):
    """A native CHANGES_REQUESTED on the head voids every review kind. The newest non-comment review per user counts."""
    newest = {}
    for r in sorted(reviews, key=lambda r: r.get("id") or 0):
        if r.get("commit_id") == head and r.get("state") in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED"):
            newest[login(r)] = r.get("state")
    return any(v == "CHANGES_REQUESTED" for v in newest.values())


def concurrent_writer(commits, commits_complete, comments, head, now, quiet_minutes):
    """H7 / B2: an unanswered '@codex address' request, or a commit under quiet_minutes old."""
    if not commits_complete:
        return "commit_list_incomplete"
    try:
        if (now - head_commit_time(commits, head)).total_seconds() < quiet_minutes * 60:
            return "recent_commit"
        asks = [stamp(c["created_at"]) for c in comments
                if not codex_finality.is_codex(c) and ADDRESS_RE.search(str(c.get("body") or ""))]
        if asks:
            last = max(asks)
            by_codex = lambda c: CODEX_BOT_LOGIN in ((c.get("author") or {}).get("login"), (c.get("committer") or {}).get("login"))
            answered = any(codex_finality.is_codex(c) and stamp(c["created_at"]) > last for c in comments) \
                or any(by_codex(c) and stamp(((c.get("commit") or {}).get("committer") or {}).get("date")) > last for c in commits)
            if not answered:
                return "codex_address_open"
    except (ValueError, KeyError, TypeError):
        return "writer_state_unreadable"
    return None


def newest_item(comments):
    """The newest authentic S1_ITEM_v1 on the PR (a display hint for S1's own S1_ITEM_v1; counters are never trusted)."""
    for c in sorted(comments, key=lambda c: c.get("id") or 0, reverse=True):
        if is_owner_unedited(c) and first_line_token(c.get("body")) == "S1_ITEM_v1" and re.search(r"(?m)^\s*contract=[0-9a-f]{8}\b", str(c.get("body"))):
            f = fields(c.get("body"))
            return {"c": c["id"], "state": f.get("state"), "attempt": f.get("attempt"), "risk": f.get("risk"), "kind": f.get("kind"),
                    "due": f.get("due"), "park_count": f.get("park_count")}
    return None


def claude_review(head, bridge_comments):
    """ACTION_LOOP C5 for a CLAUDE_REVIEW_v1 on Bridge #173, as far as comments alone decide it. The workflow cannot
    read the private Bridge, so the brief never carries this; S1 does this read itself. Kept here as the reference
    implementation of the comment checks (tests, and offline dry runs against recorded Bridge comments)."""
    mine = []
    for c in bridge_comments:
        if first_line_token(c.get("body")) != "CLAUDE_REVIEW_v1":
            continue
        f = fields(c.get("body"))
        if f.get("head_sha") == head:
            mine.append((c, f))
    if not mine:
        return {"status": "NONE"}
    c, f = max(mine, key=lambda cf: cf[0].get("id") or 0)          # the NEWEST one for H decides, whatever it says
    why = None
    if not is_owner_unedited(c):
        why = "not_owner_or_edited"
    elif f.get("verdict") != "APPROVE":
        why = f"verdict:{f.get('verdict')}"
    elif f.get("lane_eligible") != "YES":
        why = "lane_eligible_not_yes"
    elif not SHA40.fullmatch(f.get("report_blob") or "") or not SHA40.fullmatch(f.get("bridge_commit") or "") or not f.get("report"):
        why = "report_binding_missing"
    else:
        m = re.search(r"\d{6,}", f.get("request") or "")
        req = next((r for r in bridge_comments if m and r.get("id") == int(m.group(0))), None)
        rf = fields(req.get("body")) if req else {}
        if not req or first_line_token(req.get("body")) != "S1_REVIEW_REQUEST_v1" or head not in str(req.get("body")) \
                or not is_owner_unedited(req) or stamp(req["created_at"]) >= stamp(c["created_at"]) or not rf:
            why = "no_prior_exact_head_request"
    out = {"status": "APPROVE" if why is None else "INADMISSIBLE", "c": c.get("id"), "independence": f.get("independence")}
    if why:
        out["why"] = why
    else:
        out.update(report=f["report"], report_blob=f["report_blob"], bridge_commit=f["bridge_commit"],
                   body_sha256=hashlib.sha256(str(c.get("body")).encode()).hexdigest())
    return out


# ----------------------------------------------------------------------------------------------- one PR
def pr_entry(pr, data, ctx):
    """Everything the brief says about one open non-draft PR. `data` holds the raw reads; a missing read is recorded,
    never guessed. ctx: repo_id, main_sha, policy, tuples, gate_isolation_live, now, budgets, quiet_minutes."""
    head, n = (pr.get("head") or {}).get("sha"), pr.get("number")
    e = {"n": n, "head": head, "ref": (pr.get("head") or {}).get("ref"), "open": []}
    gate = e["open"].append
    head_repo = (pr.get("head") or {}).get("repo") or {}
    if (pr.get("base") or {}).get("ref") != "main" or ((pr.get("base") or {}).get("repo") or {}).get("id") != ctx["repo_id"]:
        e["skip"] = "B1:base_not_main"
        return e
    if head_repo.get("id") != ctx["repo_id"]:
        e["skip"] = "B1:fork_head"
        return e
    if not isinstance(head, str) or not SHA40.fullmatch(head) or data.get("error"):
        e["skip"] = f"NOT_READ:{data.get('error') or 'head'}"
        return e
    d1, d2 = data.get("detail") or {}, data.get("detail2") or {}
    if (d1.get("head") or {}).get("sha") != head or (d2.get("head") or {}).get("sha") != head or d1.get("state") != "open" \
            or d2.get("state") != "open" or d1.get("draft") or d2.get("draft"):
        e["skip"] = "C2:head_moved_or_state"                   # a head that moved while the brief was built is never ranked
        return e
    files, fc = data.get("files") or [], bool(data.get("files_complete")) and len(data.get("files") or []) == d2.get("changed_files")
    e["files"] = d2.get("changed_files")
    paths = sorted({f.get("filename") or "" for f in files} | {f["previous_filename"] for f in files if f.get("previous_filename")})
    if len(paths) <= MAX_PATHS_PER_PR and fc:
        e["paths"] = paths
    else:
        e["paths_omitted"] = len(paths)
    e["paths_sha256"] = hashlib.sha256("\n".join(paths).encode()).hexdigest()[:16]
    reasons, floor = path_exclusions(files, fc, ctx["policy"], ctx["gate_isolation_live"], data.get("isolation"))
    e["lane"] = {"eligible": not reasons, "x": reasons[:6], "risk_floor": floor}
    if data.get("isolation"):
        e["isolation"] = {k: (data["isolation"].get(k) or [])[:6] for k in ("owner_gated", "high_floor") if data["isolation"].get(k)}
    cmp_ = data.get("compare") or {}
    main_changed = set(cmp_.get("main_changed_paths") or [])
    e["behind"] = cmp_.get("behind_by")
    overlap = sorted(main_changed & set(paths)) if cmp_.get("complete") else None
    e["main_overlap"] = overlap[:5] if overlap is not None else "NOT_PROVEN"
    e["mergeable"] = d2.get("mergeable_state") if d2.get("mergeable") is not None else "UNKNOWN"
    tuples = ci_tuples(head, ctx["repo_id"], data.get("runs") or [], bool(data.get("runs_complete")), data.get("jobs") or {}, ctx["tuples"])
    priv = privacy_line(data.get("privacy_log"), head) if tuples.get("privacy-scan", {}).get("s") == "PASS" else {"result": None, "why": "job_not_pass"}
    checks = checks_summary(data.get("check_runs") or [], data.get("statuses") or [], bool(data.get("checks_complete")))
    e["ci"] = {"tuples": tuples, "privacy": priv["result"] or f"NONE({priv['why']})", "checks": checks}
    states = {t["s"] for t in tuples.values()}
    if "FAIL" in states or checks.get("failed"):
        ci = "FAIL"
    elif "MISSING" in states:
        ci = "MISSING"
    elif states - {"PASS"} or not checks["green"]:
        ci = "PENDING" if ("PENDING" in states or checks.get("pending")) else "NOT_PROVEN"
    else:
        ci = "GREEN"
    e["ci"]["state"] = ci
    comments, reviews = data.get("comments") or [], data.get("reviews") or []
    rc = bool(data.get("review_reads_complete"))
    commits, cc = data.get("commits") or [], bool(data.get("commits_complete"))
    e["author"] = authorship(pr, commits, cc, comments if rc else None)
    e["writer"] = concurrent_writer(commits, cc, comments, head, ctx["now"], ctx["quiet_minutes"]) if rc else "comments_unreadable"
    cx = codex_review(head, pr, commits, cc, comments, reviews, data.get("inline") or [], rc, ctx["now"], ctx["budgets"]["codex_silent_hours"])
    if e["author"].get("codex") and cx.get("status") == "FINAL":
        cx = {"status": "INADMISSIBLE", "why": "codex_authored_head"}
    threads = data.get("threads")
    p01 = None if threads is None else sum(1 for t in threads if not t.get("resolved") and re.search(r"(?i)\bP[01]\b", t.get("first_body") or ""))
    e["review"] = {"codex": cx, "changes_requested": changes_requested(reviews, head) if rc else None,
                   "unresolved_p0p1": p01 if p01 is not None else "NOT_PROVEN", "claude": "S1_READS_BRIDGE"}
    e["item"] = newest_item(comments) if rc else None
    # ONE REQUEST PER HEAD (EVIDENCE_BINDINGS B2): an address request posted at this head, answered or not, is the only one
    try:
        e["address_at_head"] = (not rc or not cc) or any(
            not codex_finality.is_codex(c) and ADDRESS_RE.search(str(c.get("body") or "")) and stamp(c["created_at"]) > head_commit_time(commits, head)
            for c in comments)
    except (ValueError, KeyError, TypeError):
        e["address_at_head"] = True
    # shrinking files the automatic exclusion 7 does not decide: S1 judges them (TICK F2)
    e["shrinks"] = [[f.get("filename"), f.get("additions") or 0, f.get("deletions") or 0] for f in files
                    if f.get("status") == "modified" and not str(f.get("filename") or "").startswith(("scripts/", "tests/"))
                    and (f.get("deletions") or 0) > (f.get("additions") or 0)]
    if len(e["shrinks"]) > 20 or "paths" not in e:               # S1 cannot judge what it cannot see: unclear, OWNER_GATED
        e["shrinks"] = e["shrinks"][:20]
        if e["lane"]["eligible"]:
            e["lane"] = {"eligible": False, "x": ["x7:shrinks_not_listed"], "risk_floor": "OWNER_GATED"}
    # ---- open gates of the reviewed-merge lane, in checklist order
    if e["writer"]:
        gate(f"C1:{e['writer']}")
    if not e["lane"]["eligible"]:
        gate("C2:owner_gated")
    if overlap is None:
        gate("C2:compare_unreadable")
    elif overlap:
        gate("C2:needs_branch_update")
    if ci != "GREEN":
        gate(f"C4:ci_{ci.lower()}")
    elif priv["result"] != "NO_RESTRICTED_CONTENT":
        gate(f"C3:privacy_line:{priv['result'] or priv['why']}")
    if e["review"]["changes_requested"] is not False:
        gate("C5:changes_requested" if e["review"]["changes_requested"] else "C5:reviews_unreadable")
    if p01 != 0:
        gate("C6:unresolved_p0p1" if p01 else "C6:threads_unreadable")
    return e


# ----------------------------------------------------------------------------------------------- ranking
def next_actions(entries, lane, health, intents, max_n=6):
    """The ranked list. Entry 0 is THE one next ladder action; the rest are fallbacks if S1's native re-read fails.
    Order: halt trigger, RECONCILE signal, rule 4 (review proven by the brief), rule 4 (review on the Bridge, S1 reads
    it), rule 2, rule 3. Inside a class: fewest open gates, then the lowest PR number (ACTION_LOOP CANDIDATE ORDER)."""
    out = []
    for run in (health.get("unhalted_failed_runs") or [])[:1]:
        out.append({"action": "HALT", "rule": "C7", "run": run, "verify": ["run"], "why": "failed main-health run after a lane merge, no halt names it"})
    due = [i for i in intents if i["due"]]
    if due:
        out.append({"action": "RECONCILE", "rule": "B3", "intents": [i["id"] for i in due[:3]], "verify": ["intent"], "why": "open intent older than the settle time"})
    merge_a, merge_b, repair, review = [], [], [], []
    for e in entries:
        if e.get("skip") or e.get("draft"):
            continue
        gates, ci, cx = e["open"], e["ci"]["state"], e["review"]["codex"]
        base = {"pr": e["n"], "head": e["head"]}
        high = e["lane"]["risk_floor"] not in FAST_RISKS          # HIGH: after every LOW and MEDIUM merge of its class
        key = (high, len(gates), e["n"])
        if not gates and lane["state"] == "ON":
            if cx["status"] == "FINAL":
                merge_a.append((key, dict(base, action="MERGE", rule="4", review="CODEX", risk_floor=e["lane"]["risk_floor"], high_evidence=high,
                                           verify=["head", "checks", "codex_review", "lane_pins", "rulesets", "halts"] + (["high_evidence"] if high else []))))
                continue
            if cx["status"] != "FINDINGS":
                other = review_request_kind(e)
                merge_b.append((key, dict(base, action="MERGE_IF_CLAUDE_APPROVE", rule="4", review="CLAUDE_REVIEW_v1 on Bridge #173",
                                           risk_floor=e["lane"]["risk_floor"], high_evidence=high, otherwise=other,
                                           verify=["head", "checks", "claude_review", "lane_pins", "rulesets", "halts"] + (["high_evidence"] if high else []))))
                continue
        if any(g.startswith("C1:") for g in gates):
            continue                                            # H7: never write to a branch another writer works on
        gated = not e["lane"]["eligible"]                        # rule 2: for an OWNER_GATED PR S1 does (c) only
        asked = e.get("address_at_head", True)                   # one "@codex address" per head, however it was answered
        if ci == "FAIL" and (gated or asked):
            continue
        if ci == "FAIL":
            failed = sorted(k for k, t in e["ci"]["tuples"].items() if t["s"] == "FAIL") + e["ci"]["checks"].get("failed", [])
            repair.append((key, dict(base, action="REPAIR", rule="2a", how="CODEX_ADDRESS", job=(failed or ["?"])[0], verify=["head", "no_open_address"])))
        elif ci == "MISSING" or "C2:needs_branch_update" in gates:
            if e["main_overlap"] == "NOT_PROVEN":
                continue
            if e["main_overlap"] and (gated or asked):
                continue
            if e["main_overlap"]:
                repair.append((key, dict(base, action="REPAIR", rule="2d", how="CODEX_ADDRESS_MERGE_MAIN", paths=e["main_overlap"], verify=["head", "no_open_address"])))
            elif (e.get("behind") or 0) > 0:
                repair.append((key, dict(base, action="REPAIR", rule="2c", how="BRANCH_UPDATE", missing=sorted(k for k, t in e["ci"]["tuples"].items() if t["s"] == "MISSING"),
                                         verify=["head"])))
        elif ci == "GREEN" and cx["status"] == "FINDINGS" and not gated and not asked and not e["author"].get("s1"):
            repair.append((key, dict(base, action="REPAIR", rule="2b", how="CODEX_ADDRESS", job="the unresolved Codex review findings", verify=["head", "no_open_address"])))
        elif ci == "GREEN":
            kind = review_request_kind(e)
            if kind and cx["status"] != "FINAL" and (lane["state"] != "ON" or gates):
                review.append((key, dict(base, action="REQUEST_REVIEW", rule="3", how=kind, verify=["head", "no_request_for_head"])))
    for group in (merge_a, merge_b, repair, review):
        out += [x for _k, x in sorted(group, key=lambda kx: kx[0])]
    for rank, x in enumerate(out[:max_n], 1):
        x["rank"] = rank
    return out[:max_n]


def review_request_kind(e):
    """Rule 3: (i) '@codex review' once per head when Codex may review it; (ii) the Bridge request when Codex is
    inadmissible, unavailable or silent past its budget. None while a Codex request is still inside its budget."""
    cx = e["review"]["codex"]
    if cx["status"] == "FINAL":
        return None
    if e["author"].get("codex") or cx["status"] in ("UNAVAILABLE", "SILENT", "INADMISSIBLE", "FINDINGS"):
        return "BRIDGE_REQUEST"
    if cx["status"] == "NONE" and not cx.get("requested_after_head"):
        return "CODEX_REVIEW"
    return None


# ----------------------------------------------------------------------------------------------- owner lines
CPH = ZoneInfo("Europe/Copenhagen")


def status_lines(entries, lane, merges, now):
    """The three STATUS LINES of OWNER_VISIBILITY.md as far as the brief can state them. What it cannot prove
    (the WAITING_ONLY_FOR_OWNER set needs the review and HIGH EVIDENCE) is written UNKNOWN, never guessed."""
    first = []
    for r in lane["off_reasons"]:
        first.append("LANE_OFF(" + (r if r.startswith(("halt", "pins:")) else "switch" if r == "switch" else "main_health" if r.startswith("main_health") else r) + ")")
    gated = [e for e in entries if not e.get("skip") and not e["lane"]["eligible"]]
    forks = [e for e in entries if e.get("skip") == "B1:fork_head"]
    if any(e["ci"]["state"] == "GREEN" for e in gated):
        first.append("UNKNOWN (waiting_set_needs_review_and_high_evidence)")
    second = []
    for e in gated:
        missing = next((g for g in e["open"] if g != "C2:owner_gated"), "review_or_high_evidence_not_in_brief")
        second.append(f"#{e['n']} {e['head'][:8]} ({missing})")
    second += [f"#{e['n']} {str(e['head'])[:8]} (fork_head)" for e in forks]
    today = now.astimezone(CPH).date()
    merged = sum(1 for m in merges if stamp(m["created_at"]).astimezone(CPH).date() == today)
    return ["OWNER APPROVAL REQUIRED: " + (" ; ".join(first) if first else "NONE"),
            "HIGH_IMPACT BLOCKED: " + (" ; ".join(second) if second else "NONE"),
            f"DISPOSITIONS TODAY: merged={merged} parked=UNKNOWN closed=UNKNOWN handed_off=UNKNOWN owner=UNKNOWN"]


def heartbeat_due(comments, now):
    """ACTION_LOOP HEARTBEAT: one S1_HEARTBEAT_v1 per Copenhagen day, from the first tick at or after 08:45."""
    local = now.astimezone(CPH)
    if (local.hour, local.minute) < (8, 45):
        return False
    return not any(is_owner_unedited(c) and first_line_token(c.get("body")) == "S1_HEARTBEAT_v1"
                   and stamp(c["created_at"]).astimezone(CPH).date() == local.date() for c in comments)


# ----------------------------------------------------------------------------------------------- the brief
def build_brief(snap):
    now = stamp(snap["now"])
    params = snap["bindings"]
    switch, contract = snap["switch"], snap["contract"]
    pins = pin_check(switch, contract, snap["pins_actual"], snap.get("bootstrap_text"))
    comments = snap.get("issue_comments") or []
    ledger_ok = bool(snap.get("issue_comments_complete"))
    halts, merges = lane_halts(comments), lane_merges(comments)
    health = main_health(snap.get("health_runs") or [], bool(snap.get("health_runs_complete")), now, merges, halts, params["main_health"])
    halt_id = standing_halt(halts, switch.get("clears_halt") if isinstance(switch, dict) else None)
    lane = lane_state(switch, pins, halt_id, health)
    if not ledger_ok:
        lane["state"] = "OFF"
        lane["off_reasons"].append("ledger_unreadable")
    intents = open_intents(comments, now, params["op_settle_minutes"]) if ledger_ok else []
    repo_id = (snap.get("repo") or {}).get("id")
    ctx = {"repo_id": repo_id, "main_sha": snap["main_sha"], "policy": snap["policy"], "tuples": params["required_job_tuples"],
           "gate_isolation_live": snap.get("gate_isolation") == "LIVE", "now": now, "budgets": snap["budgets"],
           "quiet_minutes": params["foreign_commit_quiet_minutes"]}
    entries, drafts = [], []
    identity_ok = (snap.get("repo") or {}).get("full_name") == REPO and (snap.get("repo") or {}).get("fork") is False and isinstance(repo_id, int)
    for pr in sorted(snap.get("pulls") or [], key=lambda p: p.get("number") or 0):
        if pr.get("draft"):
            drafts.append(pr.get("number"))
        elif not identity_ok:
            entries.append({"n": pr.get("number"), "head": (pr.get("head") or {}).get("sha"), "skip": "B1:repository_identity", "open": []})
        elif ((pr.get("head") or {}).get("repo") or {}).get("id") != repo_id:
            entries.append({"n": pr.get("number"), "head": (pr.get("head") or {}).get("sha"), "skip": "B1:fork_head", "open": []})
        elif pr.get("number") not in (snap.get("pr") or {}):
            entries.append({"n": pr.get("number"), "head": (pr.get("head") or {}).get("sha"), "skip": "NOT_READ:depth_cap", "open": []})
        else:
            entries.append(pr_entry(pr, snap["pr"][pr["number"]], ctx))
    rules = ruleset_census(snap.get("rulesets_1") or [], snap.get("rulesets_2") or [], bool(snap.get("rulesets_complete")))
    pulls_ok = bool(snap.get("pulls_complete"))
    brief = {
        "schema": SCHEMA, "run_id": snap["run"]["id"], "run_attempt": snap["run"]["attempt"], "event": snap["run"]["event"],
        "generated_at": iso(now), "max_age_minutes": MAX_AGE_MINUTES,
        "repo": {"full_name": (snap.get("repo") or {}).get("full_name"), "id": repo_id, "identity": identity_ok},
        "main": snap["main_sha"], "pins": pins,
        "lane": dict(lane, halt=halt_id, health=health, halts_seen=len(halts), lane_merges_seen=len(merges)),
        "rulesets": rules, "main_protected": snap.get("main_protected"),
        "open_intents": intents[:5],
        "status_lines": status_lines(entries, lane, merges, now) if pulls_ok and ledger_ok else
        ["OWNER APPROVAL REQUIRED: UNKNOWN (brief_incomplete)", "HIGH_IMPACT BLOCKED: UNKNOWN", "DISPOSITIONS TODAY: UNKNOWN"],
        "heartbeat_due": heartbeat_due(comments, now) if ledger_ok else False,
        "prs": entries, "drafts": drafts,
        "next": next_actions(entries, lane, health, intents) if pulls_ok and identity_ok else [],
        "complete": pulls_ok and ledger_ok and identity_ok and not snap.get("errors") and not any(e.get("skip") == "NOT_READ:depth_cap" for e in entries),
        "errors": (snap.get("errors") or [])[:8],
        "not_in_brief": ["rule 1 ANSWER", "rule 5 PACKAGE", "rule 5b REENABLE", "rule 6 STEWARD", "HIGH EVIDENCE",
                         "CLAUDE_REVIEW_v1 (private Bridge)", "exclusions 4,5,6,8,9, the judgment half of 3 and 7 (see shrinks)"],
    }
    return brief


def render(brief):
    """The issue body: one JSON block between two markers. Shrinks deterministically below MAX_BODY; a brief that
    still does not fit is published with next=[] and complete=false (S1 then has no candidate from it)."""
    def dump(b):
        return (f"{SCHEMA} run_id={b['run_id']} generated_at={b['generated_at']} main={b['main']}\n\n"
                "Machine-written every tick by `.github/workflows/s1-tick-brief.yml`. Evidence only, never authority: "
                "`00_FMOS/S1/TICK.md` says what S1 re-reads before it acts. Do not edit; an edit makes the brief unverifiable.\n\n"
                f"{BEGIN}\n```json\n{json.dumps(b, separators=(',', ':'), sort_keys=True).replace('<', chr(92) + 'u003c').replace('`', chr(92) + 'u0060')}\n```\n{END}\n")
    body = dump(brief)
    if len(body) <= MAX_BODY:
        return body
    b = json.loads(json.dumps(brief))
    ranked = {x.get("pr") for x in b["next"]}
    for e in b["prs"]:                                         # 1: drop detail of PRs that are not ranked
        if e["n"] not in ranked:
            for k in ("paths", "isolation", "item", "author"):
                e.pop(k, None)
            if "ci" in e:
                e["ci"] = {"state": e["ci"]["state"], "privacy": e["ci"]["privacy"]}
    b["shrunk"] = 1
    body = dump(b)
    if len(body) <= MAX_BODY:
        return body
    for e in b["prs"]:                                         # 2: drop path lists everywhere (paths_sha256 stays)
        if "paths" in e:
            e["paths_omitted"] = len(e.pop("paths"))
    b["shrunk"] = 2
    body = dump(b)
    if len(body) <= MAX_BODY:
        return body
    b = {k: brief[k] for k in ("schema", "run_id", "run_attempt", "event", "generated_at", "max_age_minutes", "repo", "main", "pins")}
    b.update(next=[], complete=False, errors=["brief_too_large"], shrunk=3, prs=[], drafts=[], lane={"state": "OFF", "off_reasons": ["brief_too_large"]},
             status_lines=["OWNER APPROVAL REQUIRED: UNKNOWN (brief_too_large)", "HIGH_IMPACT BLOCKED: UNKNOWN", "DISPOSITIONS TODAY: UNKNOWN"], heartbeat_due=False)
    return dump(b)


def parse_body(body):
    """The inverse of render(): exactly one marker pair and one JSON object with the schema; anything else is None."""
    text = str(body or "")
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        return None
    inner = text.split(BEGIN, 1)[1].split(END, 1)[0].strip()
    m = re.fullmatch(r"```json\n(.*)\n```", inner, re.S)
    if not m:
        return None
    try:
        doc = json.loads(m.group(1))
    except json.JSONDecodeError:
        return None
    return doc if isinstance(doc, dict) and doc.get("schema") == SCHEMA else None


def verify_brief(issues, run, now, repo_id=None, max_age=MAX_AGE_MINUTES):
    """The authenticity checks of 00_FMOS/S1/TICK.md step T2, as code (the reference for the rule text; S1 does the
    same checks by reading). `issues` is the answer to the one label read; `run` is GET /actions/runs/<run_id>.
    Returns (brief or None, reason). reason is OK, or BRIEF_UNVERIFIED(<why>) / BRIEF_STALE(<why>)."""
    bad = lambda why: (None, f"BRIEF_UNVERIFIED({why})")
    if not isinstance(issues, list):
        return bad("unreadable")
    mine = [i for i in issues if isinstance(i, dict) and "pull_request" not in i and i.get("state") == "open"
            and any((l.get("name") if isinstance(l, dict) else l) == BRIEF_LABEL for l in i.get("labels") or [])]
    if len(mine) != 1:
        return bad(f"issues={len(mine)}")
    issue = mine[0]
    if not is_actions_bot(issue.get("user")):
        return bad("author")
    brief = parse_body(issue.get("body"))
    if brief is None:
        return bad("body")
    if not isinstance(run, dict) or run.get("id") != brief.get("run_id"):
        return bad("run_id")
    if run.get("path") != WORKFLOW_PATH or run.get("event") not in ("schedule", "workflow_dispatch") or run.get("event") != brief.get("event") \
            or run.get("head_branch") != "main" or (run.get("repository") or {}).get("full_name") != REPO \
            or (run.get("head_repository") or {}).get("full_name") != REPO or run.get("head_sha") != brief.get("main") \
            or run.get("run_attempt") != brief.get("run_attempt"):
        return bad("run_binding")
    if repo_id is not None and ((run.get("repository") or {}).get("id") != repo_id or (brief.get("repo") or {}).get("id") != repo_id):
        return bad("repo_id")
    if run.get("status") != "completed" or run.get("conclusion") != "success":
        return bad("run_not_success")
    try:
        started, ended = stamp(run.get("run_started_at")), stamp(run.get("updated_at"))
        edited, made = stamp(issue.get("updated_at")), stamp(brief.get("generated_at"))
    except ValueError:
        return bad("timestamps")
    # the body was last written INSIDE the run: any later edit (by anyone) moves updated_at past the run's end
    if not (started <= made <= edited <= ended):
        return bad("edited_outside_run")
    age = (now - made).total_seconds() / 60
    if age > max_age or age < -2:
        return (None, f"BRIEF_STALE(age_min={int(age)})")
    if (brief.get("pins") or {}).get("ok") is not True:
        return bad("pins")
    return brief, "OK"


# ----------------------------------------------------------------------------------------------- GitHub reader
class GitHub:
    """Minimal REST reader. GET only, except graphql() (a read query sent by POST) and the two issue writes of publish."""

    def __init__(self, token, repo=REPO, base="https://api.github.com", budget=700):
        self.token, self.repo, self.base, self.calls, self.budget = token, repo, base, 0, budget

    def _request(self, method, url, data=None, accept="application/vnd.github+json"):
        self.calls += 1
        if self.calls > self.budget:
            raise RuntimeError("API_BUDGET_EXHAUSTED")
        req = urllib.request.Request(url, method=method, data=None if data is None else json.dumps(data).encode())
        req.add_header("Accept", accept)
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        req.add_header("User-Agent", "s1-tick-brief")
        if self.token:
            req.add_header("Authorization", f"Bearer {self.token}")
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read(), resp.headers

    def url(self, path, params=None):
        root = path if path.startswith("https://") else f"{self.base}/repos/{self.repo}{'/' if path and not path.startswith('/') else ''}{path}"
        return root + ("?" + urllib.parse.urlencode(params) if params else "")

    def get(self, path, params=None):
        raw, _h = self._request("GET", self.url(path, params))
        return json.loads(raw)

    def text(self, path):
        """A job log. GitHub answers with a redirect to its log storage: only GitHub's own storage hosts are followed
        and the bearer token is never sent to the second host (the repository's own handler)."""
        self.calls += 1
        if self.calls > self.budget:
            raise RuntimeError("API_BUDGET_EXHAUSTED")
        req = urllib.request.Request(self.url(path), method="GET")
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("User-Agent", "s1-tick-brief")
        if self.token:
            req.add_header("Authorization", f"Bearer {self.token}")
        with urllib.request.build_opener(job_identity._SafeGithubLogRedirect()).open(req, timeout=60) as resp:
            raw = resp.read(8 * 1024 * 1024 + 1)
        if len(raw) > 8 * 1024 * 1024:
            raise ValueError("JOB_LOG_SIZE_UNVERIFIED")
        return raw.decode("utf-8", "replace")

    def pages(self, path, params=None, key=None, max_pages=30):
        """Every page, per_page=100. Returns (rows, complete). complete is False when max_pages was hit, when a keyed
        list's total_count moved or does not match, or when an id repeats."""
        rows, total, params = [], None, dict(params or {}, per_page=100)
        for page in range(1, max_pages + 1):
            doc = self.get(path, dict(params, page=page))
            batch = doc.get(key) if key else doc
            if not isinstance(batch, list):
                return rows, False
            if key:
                if total is not None and doc.get("total_count") != total:
                    return rows, False
                total = doc.get("total_count")
            rows += batch
            if len(batch) < 100:
                ids = [r.get("id") for r in rows if isinstance(r, dict) and "id" in r]
                ok = len(ids) == len(set(ids)) and (total is None or (total == len(rows) and total < 1000))
                return rows, ok
        return rows, False

    def graphql(self, query, variables):
        raw, _h = self._request("POST", "https://api.github.com/graphql", {"query": query, "variables": variables})
        doc = json.loads(raw)
        if doc.get("errors"):
            raise RuntimeError("GRAPHQL_ERROR")
        return doc["data"]


THREADS_QUERY = """query($o:String!,$r:String!,$n:Int!,$c:String){repository(owner:$o,name:$r){pullRequest(number:$n){
reviewThreads(first:100,after:$c){pageInfo{hasNextPage endCursor} nodes{isResolved comments(first:30){nodes{body}}}}}}}"""


def read_threads(gh, number):
    owner, name = gh.repo.split("/")
    out, cursor = [], None
    for _ in range(5):
        data = gh.graphql(THREADS_QUERY, {"o": owner, "r": name, "n": number, "c": cursor})
        t = data["repository"]["pullRequest"]["reviewThreads"]
        out += [{"resolved": n["isResolved"], "first_body": "\n".join((c.get("body") or "") for c in n["comments"]["nodes"] or [])} for n in t["nodes"]]
        if not t["pageInfo"]["hasNextPage"]:
            return out
        cursor = t["pageInfo"]["endCursor"]
    return None


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout.strip()


def parse_json_block(text, contract):
    for m in re.finditer(r"```json\n(.*?)\n```", text, re.S):
        try:
            doc = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(doc, dict) and doc.get("contract") == contract:
            return doc
    raise ValueError(f"PARAMETER_BLOCK_MISSING:{contract}")


def read_pr(gh, pr, ctx, snap_errors, derive_isolation):
    """All native reads for one PR. Any failed read is recorded on the entry; the entry is then never ranked."""
    n, head = pr["number"], pr["head"]["sha"]
    d = {}
    try:
        d["detail"] = gh.get(f"pulls/{n}")
        d["files"], d["files_complete"] = gh.pages(f"pulls/{n}/files", max_pages=31)
        d["commits"], d["commits_complete"] = gh.pages(f"pulls/{n}/commits", max_pages=3)
        comments, c1 = gh.pages(f"issues/{n}/comments", max_pages=10)
        reviews, c2 = gh.pages(f"pulls/{n}/reviews", max_pages=10)
        inline, c3 = gh.pages(f"pulls/{n}/comments", max_pages=10)
        d.update(comments=comments, reviews=reviews, inline=inline, review_reads_complete=c1 and c2 and c3)
        try:
            d["threads"] = read_threads(gh, n)
        except Exception:                                        # noqa: BLE001  (unreadable threads are NOT_PROVEN)
            d["threads"] = None
        cmp_ = gh.get(f"compare/{ctx['main_sha']}...{head}")
        base = (cmp_.get("merge_base_commit") or {}).get("sha")
        d["compare"] = {"behind_by": cmp_.get("behind_by"), "complete": False, "main_changed_paths": []}
        if base and cmp_.get("behind_by") == 0:
            d["compare"]["complete"] = True
        elif base:
            back = gh.get(f"compare/{base}...{ctx['main_sha']}")
            names = [f.get("filename") for f in back.get("files") or []] + [f.get("previous_filename") for f in back.get("files") or [] if f.get("previous_filename")]
            # GitHub lists at most 300 files on a compare; a longer list is incomplete and the overlap is NOT PROVEN
            d["compare"].update(main_changed_paths=names, complete=len(back.get("files") or []) < 300 and back.get("status") in ("ahead", "identical"))
        runs, rc = gh.pages("actions/runs", {"head_sha": head, "event": "pull_request"}, key="workflow_runs", max_pages=5)
        d["runs"], d["runs_complete"], d["jobs"] = runs, rc, {}
        wanted = {t["workflow_path"] for t in ctx["tuples"]}
        for path in wanted:
            kept = [r for r in runs if r.get("path") == path and r.get("head_sha") == head]
            if kept:
                run = max(kept, key=lambda r: r.get("run_number") or 0)
                jobs, jc = gh.pages(f"actions/runs/{run['id']}/jobs", {"filter": "latest"}, key="jobs", max_pages=3)
                d["jobs"][run["id"]] = jobs if jc else None
        priv = [j for jobs in d["jobs"].values() if jobs for j in jobs if j.get("name") == "privacy-scan" and j.get("conclusion") == "success"]
        d["privacy_log"] = None
        if len(priv) == 1:
            try:
                d["privacy_log"] = gh.text(f"actions/jobs/{priv[0]['id']}/logs")
            except Exception:                                    # noqa: BLE001
                d["privacy_log"] = None
        checks, k1 = gh.pages(f"commits/{head}/check-runs", key="check_runs", max_pages=5)
        statuses, k2 = gh.pages(f"commits/{head}/statuses", max_pages=3)
        d.update(check_runs=checks, statuses=statuses, checks_complete=k1 and k2)
        d["isolation"] = derive_isolation(head, [f.get("filename") for f in d["files"]] + [f["previous_filename"] for f in d["files"] if f.get("previous_filename")])
        d["detail2"] = gh.get(f"pulls/{n}")                    # the second head read, AFTER every other read of this PR
    except Exception as exc:                                     # noqa: BLE001
        d["error"] = type(exc).__name__
        snap_errors.append(f"pr{n}:{type(exc).__name__}")
    return d


def collect(gh, root, head_root, now, run):
    """The snapshot for build_brief(): native reads at one main SHA. `root` is the checkout of that SHA."""
    errors = []
    main_sha = git(root, "rev-parse", "HEAD")
    snap = {"now": iso(now), "run": run, "main_sha": main_sha, "errors": errors}
    read = lambda rel: (Path(root) / rel).read_text(encoding="utf-8")
    snap["switch"], snap["contract"] = json.loads(read(SWITCH)), json.loads(read(CONTRACT_FILE))
    snap["policy"] = json.loads(read(POLICY_FILE))
    snap["gate_isolation"] = json.loads(read(ISOLATION_FILE)).get("gate_isolation")
    snap["bindings"] = parse_json_block(read(BINDINGS_FILE), "S1_EVIDENCE_BINDINGS_v1")
    snap["budgets"] = parse_json_block(read("00_FMOS/S1/STEWARD_STATES.md"), "S1_STEWARD_BUDGETS_v1")
    snap["bootstrap_text"] = read(snap["contract"]["bootstrap_path"])
    wanted = set(snap["switch"].get("pins") or {}) | {CONTRACT_FILE, snap["contract"].get("action_loop_path"), snap["contract"].get("lane_switch_path"),
                                                         snap["contract"].get("tick_path")} | set(snap["contract"].get("rubric_blobs") or {})
    snap["pins_actual"] = {}
    for path in sorted(p for p in wanted if p):
        try:
            snap["pins_actual"][path] = git(root, "rev-parse", f"HEAD:{path}")
        except subprocess.CalledProcessError:
            snap["pins_actual"][path] = None
    snap["repo"] = gh.get("")
    branch = gh.get("branches/main")
    snap["main_protected"] = branch.get("protected")
    if (branch.get("commit") or {}).get("sha") != main_sha:
        errors.append("main_moved_during_checkout")            # informational: S1 handles drift with the C1b compare
    snap["issue_comments"], snap["issue_comments_complete"] = gh.pages(f"issues/{OWNER_ISSUE}/comments", max_pages=120)
    snap["health_runs"], _ = gh.pages(f"actions/workflows/{Path(snap['bindings']['main_health']['workflow_path']).name}/runs",
                                      {"event": "schedule", "branch": "main"}, key="workflow_runs", max_pages=1)
    snap["health_runs_complete"] = bool(snap["health_runs"])   # ROUTE 1 reads the newest 100 runs of this workflow only
    r1, c1 = gh.pages("rulesets", {"includes_parents": "true"}, max_pages=2)
    r2, c2 = gh.pages("rulesets", {"includes_parents": "true"}, max_pages=2)
    snap.update(rulesets_1=r1, rulesets_2=r2, rulesets_complete=c1 and c2)
    snap["pulls"], snap["pulls_complete"] = gh.pages("pulls", {"state": "open", "sort": "created", "direction": "asc"}, max_pages=5)
    import s1_workflow_isolation_derive_v1 as iso_mod            # main's code only; it parses, it never executes a head
    main_derivation = iso_mod.derive(Path(root))

    def derive_isolation(head, changed):
        try:
            git(root, "fetch", "--quiet", "--no-tags", "--depth=1", "origin", head)
            if not (Path(head_root) / ".git").exists():
                git(root, "worktree", "add", "--quiet", "--detach", str(head_root), head)
            else:
                git(head_root, "checkout", "--quiet", "--detach", head)
            if git(head_root, "rev-parse", "HEAD") != head:
                return None
            return iso_mod.lane_classification(changed, [main_derivation, iso_mod.derive(Path(head_root))])
        except Exception:                                        # noqa: BLE001  (not derived: the PR reads OWNER_GATED)
            return None

    ctx = {"main_sha": main_sha, "tuples": snap["bindings"]["required_job_tuples"]}
    snap["pr"] = {}
    same_repo = [p for p in snap["pulls"] if not p.get("draft") and ((p.get("head") or {}).get("repo") or {}).get("id") == snap["repo"].get("id")]
    for pr in sorted(same_repo, key=lambda p: str(p.get("updated_at") or ""), reverse=True)[:MAX_DEPTH_PRS]:
        snap["pr"][pr["number"]] = read_pr(gh, pr, ctx, errors, derive_isolation)
    return snap


# ----------------------------------------------------------------------------------------------- publish
def publish(gh, body):
    """Write the one brief issue. Finds it by label; creates the label and the issue on the first run. More than one
    open labelled issue by the Actions bot is repaired by closing the newer ones (never deleted)."""
    if parse_body(body) is None or len(body) > 65000:
        raise SystemExit("PUBLISH_REFUSED: body is not one valid brief")
    issues = [i for i in gh.get("issues", {"labels": BRIEF_LABEL, "state": "open", "per_page": 20}) if "pull_request" not in i]
    mine = sorted((i for i in issues if is_actions_bot(i.get("user"))), key=lambda i: i["number"])
    foreign = [i["number"] for i in issues if not is_actions_bot(i.get("user"))]
    if foreign:
        raise SystemExit(f"PUBLISH_REFUSED: issue(s) {foreign} carry the label {BRIEF_LABEL} but are not by the Actions bot; S1 reads the brief as unverified until the owner removes the label there")
    if not mine:
        try:
            gh._request("POST", gh.url("labels"), {"name": BRIEF_LABEL, "color": "ededed", "description": "S1_TICK_BRIEF_V1 (machine-written)"})
        except urllib.error.HTTPError as exc:
            pass                                                 # exists already, or creating the issue creates it
        raw, _h = gh._request("POST", gh.url("issues"), {"title": BRIEF_TITLE, "body": body, "labels": [BRIEF_LABEL]})
        number = json.loads(raw)["number"]
        try:
            gh._request("PUT", gh.url(f"issues/{number}/lock"), {"lock_reason": "resolved"})
        except urllib.error.HTTPError:
            pass                                                 # an unlocked issue still works; a comment only makes one brief unverifiable
        return number
    for extra in mine[1:]:
        gh._request("PATCH", gh.url(f"issues/{extra['number']}"), {"state": "closed", "state_reason": "not_planned"})
    gh._request("PATCH", gh.url(f"issues/{mine[0]['number']}"), {"body": body})
    return mine[0]["number"]


def main(argv):
    mode = argv[1] if len(argv) > 1 else ""
    token = os.environ.get("GITHUB" + "_TOKEN", "")
    repo = os.environ.get("GITHUB_REPOSITORY", REPO)
    if repo != REPO:
        raise SystemExit(f"REFUSED: repository {repo} is not {REPO}")
    if mode == "build":
        root, head_root, out = argv[2], argv[3], Path(argv[4])
        run = {"id": int(os.environ["GITHUB_RUN_ID"]), "attempt": int(os.environ["GITHUB_RUN_ATTEMPT"]), "event": os.environ["GITHUB_EVENT_NAME"]}
        gh = GitHub(token)
        snap = collect(gh, root, head_root, datetime.now(timezone.utc), run)
        brief = build_brief(snap)
        brief["api_calls"] = gh.calls
        brief["generated_at"] = iso(datetime.now(timezone.utc))  # the end of the reads: the age S1 measures starts here
        body = render(brief)
        out.write_text(body, encoding="utf-8")
        print(f"S1_TICK_BRIEF_BUILD run={run['id']} main={brief['main']} prs={len(brief['prs'])} next={len(brief['next'])} "
              f"complete={brief['complete']} calls={gh.calls} bytes={len(body)}")
        return 0
    if mode == "publish":
        body = Path(argv[2]).read_text(encoding="utf-8")
        brief = parse_body(body)
        if brief is None or str(brief.get("run_id")) != os.environ.get("GITHUB_RUN_ID") or brief.get("main") != os.environ.get("GITHUB_SHA"):
            raise SystemExit("PUBLISH_REFUSED: the brief does not belong to this run")
        number = publish(GitHub(token, budget=20), body)
        print(f"S1_TICK_BRIEF_PUBLISHED issue={number} run={brief['run_id']}")
        return 0
    raise SystemExit("usage: s1_tick_brief_v1.py build <main checkout> <head worktree dir> <out file> | publish <brief file>")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
