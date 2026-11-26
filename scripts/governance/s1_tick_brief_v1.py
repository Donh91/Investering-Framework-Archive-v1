"""S1_TICK_BRIEF_V1: GitHub prepares the S1 tick; S1 verifies the brief and acts.

Read-only towards the repository. The build half reads GitHub natively with the job token (contents, actions and
pull-requests read) and never executes or imports code from a pull-request head; the publish half holds issues:write
and only writes the one brief issue. The brief is evidence, never authority: 00_FMOS/S1/TICK.md says which facts S1
re-reads natively before it acts, and a missing, stale or unauthentic brief is a NOOP, never a full census.

Layout: pure functions first (tested with fixtures in tests/governance/test_s1_tick_brief_v1.py), then the GitHub
reader, then the two command-line entry points `build` and `publish`.

AGENTS.md section 0.2i: the build also decides. S1_DECISION_V1 = s1_decision_v1.decide(brief) is published as its own
block above the brief (render_issue), and the job `execute` (its own module: this file never merges and never
imports it) acts on it only when the switch on main reads LIVE.
"""
from __future__ import annotations

import base64
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
import time
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
import s1_decision_v1 as decision_v1  # noqa: E402  (pure functions: S1_DECISION_V1, AGENTS.md section 0.2i)

SCHEMA = "S1_TICK_BRIEF_V1"
REPO = "Donh91/Investering-Framework-Archive-v1"
OWNER_LOGIN = "Donh91"
OWNER_ISSUE = 1156
BRIEF_LABEL = "s1-tick-brief"
BRIEF_TITLE = "S1 tick brief (machine-written by .github/workflows/s1-tick-brief.yml; do not edit)"
WORKFLOW_PATH = ".github/workflows/s1-tick-brief.yml"
EXECUTOR_WORKFLOW_PATH = ".github/workflows/s1-executor.yml"   # fix round 6 (F2): the executor is its own workflow
ACTIONS_BOT = {"login": "github-actions[bot]", "id": 41898282, "type": "Bot"}
CODEX_BOT_LOGIN = "chatgpt-codex-connector[bot]"
TASK_ID = "6ae5fd466b48819187abc224ec0f1c5f"
BEGIN, END = "<!-- S1_TICK_BRIEF_V1 BEGIN -->", "<!-- S1_TICK_BRIEF_V1 END -->"
MAX_BODY = 60000                      # GitHub refuses an issue body above 65536 characters
MAX_AGE_MINUTES = 45                  # TICK.md: an older brief is BRIEF_STALE
FALLBACK_DUE_MINUTES = 55             # a workflow_run (fallback) trigger builds only when NO brief was generated since the
                                      # previous hourly slot: at most one extra build, and only after a missed cron
MAX_API_CALLS = 300                   # hard cap per build. The job token's 1,000 requests an hour are shared by EVERY
                                      # workflow of the repository; one build an hour under this cap leaves them room
RETRY_AFTER_MAX_SECONDS = 60          # a rate-limit answer is retried once, and only when it asks for at most this wait
CRON_RECENT_MINUTES = 50              # a cron run of this workflow this recent: the fallback does not build
BUILD_RECENT_MINUTES = 60             # any run that reached build this recently: the fallback does not build
COALESCE_MINUTES = 5                  # an older fallback run this young and still running decides; a newer one stops
JOBS_READS_PER_DUE = 3                # jobs lists read per due check to find a started build
DUE_API_CALLS = 5                     # run list, brief issue, and at most JOBS_READS_PER_DUE jobs lists
PUBLISH_API_CALLS = 25                # label read, label create, issue create or update, lock, closing extra issues
READBACK_API_CALLS = 2                # the one issue read after publish (S1_BRIEF_DIGEST_V1), a retry included
RUN_EVENTS = ("schedule", "workflow_dispatch", "workflow_run", "push")
FALLBACK_EVENTS = ("workflow_run", "push")   # these two only build after a missed cron; schedule and manual runs always build
CODEX_LIMIT_HOURS = 24                # a Codex usage-limit answer this recent, with no newer Codex answer: unavailable
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
VERDICT_SCHEMA = "S1_BRIEF_VERDICT_V1"   # B.verdict, SHADOW (S1 v3.3 W2): published, and S1 still runs T1 to T3 itself
DIGEST_TOKEN = "S1_BRIEF_DIGEST_V1"      # printed by publish after reading the issue back (R2-7)
T3_TREE_DIRS = ("scripts", "tests", ".github", ".agents", "00_FMOS")   # the entries TICK T3 C1b compares, in its order
C1B_WINDOW = 100                      # first-parent commits read back from B.main (one commits page, as TICK T3 C1b)
C1B_PAGES = 3                         # fix round 6 (liveness): commit pages one build may read to REACH a known anchor; a range
                                      # gap only when the anchor is lost or more than C1B_PAGES * C1B_WINDOW commits back
C1B_SEARCH_READS = 20                 # tree reads inside one differing segment; past it the segment's last commit is named
C1B_MAX_CALLS = 110                   # the C1b part's own share of MAX_API_CALLS (it runs before the PR depth reads).
                                      # Fix round 6 (F1): enough for EVERY shape of a C1B_WINDOW chain: 1 issues + 1 run +
                                      # 1 commits read + at most C1B_WINDOW + 1 distinct root trees (every key c1b_scan
                                      # reads is the base tree or a chain commit's tree, memoised) = 104 <= 110
C1B_MAX_GAPS = 16                     # fix round 6: more open history gaps than this is surfaced (C1b:gaps_overflow), never cut
# Fix round 6 (S4): the owner's decision whether an open C1b history gap or open segment also fences the legacy live
# ChatGPT lane (TICK.md v3.3 reads B.next and B.claude_slots). True: while any is open, B.next carries no MERGE entry
# and no Claude slot is ready (HALT, RECONCILE, REPAIR and review requests stay). Without it this head would widen
# that lane: a scan that main ends incomplete (the C1b budget) is a complete brief with an open segment here.
C1B_FENCES_LEGACY_LANE = True
MERGE_ACTIONS = ("MERGE", "MERGE_IF_CLAUDE_APPROVE")
SQUASH_SUBJECT = re.compile(r"\(#\d+\)$")   # TICK T3: a squash merge is a one-parent commit whose subject ends (#<n>)
S1_FILES = "00_FMOS/S1"
SWITCH = "00_FMOS/S1/REVIEWED_MERGE_LANE.json"
CONTRACT_FILE = "00_FMOS/S1/RUNTIME_CONTRACT.json"
POLICY_FILE = "00_FMOS/S1_REQUIRED_PR_JOBS_POLICY_V1.json"
ISOLATION_FILE = "00_FMOS/S1_WORKFLOW_ISOLATION_V1.json"
BINDINGS_FILE = "00_FMOS/S1/EVIDENCE_BINDINGS.md"
PRIVACY_PREFIX = "S1_NATIVE_PRIVACY" + "_SCAN_STEP_V1"     # split: this file must never contain the gate marker itself
SITE_PREFIX = "05_CYCLE_NAVIGATOR/site/"
# The files that produce the privacy gate's result. When main changed one of them after a PR's merge-base, that PR's
# gate ran old code: only a branch update lets the current gate run (rule 2c, owner route).
GATE_FILES = (".github/workflows/data-architecture-gate.yml", "scripts/governance/s1_native_privacy_scan_step_v1.py",
              "scripts/governance/s1_diff_scan_v1.py", "scripts/governance/s1_site_public_readback_v1.py")
OWNER_UPDATE_NEXT = "OWNER_BRANCH_UPDATE"
# S1 v3.3 W5, rule 2c: who updates a branch that must take main. S1's connector has no update-branch call (Route 1 of
# STEWARD_STATES.md) and Route 2 is not part of TICK.md, so an entry "BRANCH_UPDATE" without `by` can only end as a
# skip, every tick, in front of every other entry. "OWNER": the entry carries by=OWNER (one S1_ITEM_v1 per head, then
# the owner or ChatGPT updates the branch). Any other value restores the entry without `by`; flip it only together
# with a reviewed TICK.md change that gives S1 a route.
S1_BRANCH_UPDATE_ROUTE = "OWNER"
# The named receipts of an S1 action on #1156 (ACTION_LOOP RECEIPTS) and the action word each one proves. Closed set:
# B.ledger.last_action carries the word, never text of the comment.
S1_ACTION_RECEIPTS = {"S1_LANE_MERGE_v1": "MERGE", "S1_LANE_HALTED": "LANE_HALTED", "S1_PACKAGE_PR_v1": "PACKAGE",
                      "S1_PACKAGE_FAILED": "PACKAGE", "S1_PACKAGE_SKIPPED": "PACKAGE", "S1_OP_DONE_v1": "RECONCILE"}
S1_ACTION_WORDS = ("ANSWER", "REPAIR", "REQUEST_REVIEW", "MERGE", "PACKAGE", "REENABLE", "STEWARD")
CONTRACT_ANY = re.compile(r"\bcontract=[0-9a-f]{8}\b")   # anywhere: a heartbeat and a short receipt carry it mid-line
# The Codex connector's own usage-limit answer, at the START of its comment ("You have reached your Codex usage limits
# for code reviews. ..."; read from this repository on 2026-11-26). A sentence such as "I can't review the lockfile"
# is not one (review finding P1-A).
LIMIT_RE = re.compile(r"(?i)\A\s*You have reached your Codex usage limits?\b")
CODEX_FEED_HOURS = 72                 # how far back the repository-wide read of Codex's own activity goes (read_codex_feed)
# AGENTS.md section 0.2i. An Actions-bot ledger post proves nothing by its identity (every workflow of the repository
# posts as that bot): an executor post names its run, and that run is read and checked (executor_post).
OP_INTENTS = ("S1_LANE_MERGE_INTENT_v1", "S1_OP_INTENT_v1")
EXECUTOR_RUN = re.compile(r"(?m)^executor: GITHUB run=(\d{1,20})[ \t]*$")
EXECUTOR_EVENTS = ("workflow_run",)   # fix round 6 (F2): an executor run is a workflow_run of s1-executor.yml
RUN_POST_SLACK_SECONDS = 120          # an executor post was created between its run's creation and end, give or take this
SETTLE_RUN_READS = 4                  # run reads per build (and per executor run) to judge Actions-bot outcome posts
SETTLE_MERGE_READS = 4                # PR reads per build (and per executor run): the native proof behind a merge receipt (A10)
# What marks a PR as written by an AI or by automation (review_gate: such a PR never merges unreviewed). Best effort:
# an AI that writes as the owner account, on a branch with another name and with no trailer, is not detectable.
AI_BRANCH = re.compile(r"(?i)^(?:claude|codex|chatgpt|gpt|openai|copilot|grok|gemini|cursor|devin|agents?|ai|bots?|automation|auto|dependabot|renovate)[/_-]")
AI_TRAILER = re.compile(r"(?im)^\s*co-authored-by:[^\n]*\b(?:claude|codex|chatgpt|openai|anthropic|copilot|gemini|grok|cursor|devin)\b"
                        r"|^\s*claude-session:|noreply@anthropic\.com")
AI_BODY = re.compile(r"(?i)generated with \[?claude code|claude\.ai/code|chatgpt\.com/(?:codex|s/)")
# Owner decision 2026-11-25 (review route). A Claude receipt never passes a head Claude wrote: these marks say it did.
CLAUDE_BRANCH = re.compile(r"(?i)^claude[/_-]")
CLAUDE_TRAILER = re.compile(r"(?im)^\s*co-authored-by:[^\n]*\b(?:claude|anthropic)\b|^\s*claude-session:|noreply@anthropic\.com")
CLAUDE_BODY = re.compile(r"(?i)generated with \[?claude code|claude\.ai/code")
INDEPENDENCE = ("INDEPENDENT_DETACHED", "SELF_AUTHORED_DESIGN")   # CLAUDE.md receipt values; anything else is no route (b) receipt
RECALL_READS_PER_BUILD = 3            # merged PRs with a pending Codex recall whose review state one build reads (four reads each)

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


class StopReading(RuntimeError):
    """The build must stop calling the API. The brief that results is INCOMPLETE with `reason`, never a partial brief
    that reads as complete."""
    reason = "stopped"


class ApiBudget(StopReading):
    reason = "api_budget"


class RateLimited(StopReading):
    reason = "rate_limited"


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


def is_s1_author(row):
    """Who may have written an S1 ledger post on #1156: the owner account (S1 as the ChatGPT task) or the Actions bot
    (the executor job of this workflow, AGENTS.md section 0.2i). Every use of this is fail closed: a post that counts
    can only stop a merge (a halt, an open intent, an attempted head) or suppress a duplicate (a receipt, a heartbeat),
    never start one. SETTLING an intent is the one ledger rule that unblocks something, and identity is not enough for
    it: open_intents() accepts the owner account, or an Actions-bot post that is proven to be the executor's."""
    return login(row) == OWNER_LOGIN or is_actions_bot((row or {}).get("user"))


def is_s1_unedited(row):
    return is_s1_author(row) and bool(row.get("created_at")) and row.get("created_at") == row.get("updated_at")


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
        if is_s1_author(c) and HALT_RE.search(str(c.get("body") or "")):
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
        if is_s1_author(c) and first_line_token(c.get("body")) == "S1_LANE_MERGE_v1":
            out.append({"id": c["id"], "created_at": c["created_at"]})
    return out


def executor_run(body):
    """The run id an executor post names on its own `executor: GITHUB run=<id>` line (the first such line), or None."""
    m = EXECUTOR_RUN.search(str(body or ""))
    return int(m.group(1)) if m else None


def executor_post(c, run_of, now):
    """Is this ledger post proven to be the work of the executor job? All must hold: the Actions bot wrote it and
    never edited it; it names its run; `run_of(id)` (GET actions/runs/<id>, read by the caller) is that run, a run of
    the EXECUTOR workflow file (fix round 6, F2: s1-executor.yml) on main of this repository, started by workflow_run
    (a completed brief run); and the post was created
    while that run existed. Anything unread or unreadable: not proven. What this does NOT prove: a workflow on main
    that deliberately names a run of this workflow while that run is in progress passes (only the owner merges
    workflow code, AGENTS.md section 0.2e exclusion 1)."""
    if run_of is None or not isinstance(c, dict) or not is_actions_bot(c.get("user")) or not is_s1_unedited(c):
        return False
    rid = executor_run(c.get("body"))
    if rid is None:
        return False
    run = run_of(rid)
    try:
        if not isinstance(run, dict) or run.get("id") != rid or run.get("path") != EXECUTOR_WORKFLOW_PATH or run.get("head_branch") != "main" \
                or run.get("event") not in EXECUTOR_EVENTS or (run.get("repository") or {}).get("full_name") != REPO \
                or (run.get("head_repository") or {}).get("full_name") != REPO:
            return False
        slack = timedelta(seconds=RUN_POST_SLACK_SECONDS)
        end = stamp(run["updated_at"]) if run.get("status") == "completed" else now
        return stamp(run["created_at"]) - slack <= stamp(c["created_at"]) <= end + slack
    except (ValueError, KeyError, TypeError):
        return False


class RunReader:
    """`run_of` for executor_post(): GET actions/runs/<id>, memoised and capped. A run that does not exist, or a read
    that GitHub answers with any other HTTP error, reads as None (not proven, fail closed: a post that names an odd
    run id must never be able to stop the build); past the cap nothing more is read (None again). A rate limit or the
    API cap still stops the reads (StopReading). `docs` is the record a snapshot keeps."""

    def __init__(self, gh, max_reads=SETTLE_RUN_READS):
        self.gh, self.max_reads, self.docs = gh, max_reads, {}

    def __call__(self, run_id):
        key = str(int(run_id))
        if key not in self.docs:
            if len(self.docs) >= self.max_reads:
                return None
            try:
                self.docs[key] = self.gh.get(f"actions/runs/{key}")
            except urllib.error.HTTPError:
                self.docs[key] = None
        return self.docs[key]


class MergeReader:
    """`merge_of` for settles(): GET pulls/<n>, memoised and capped like RunReader; keeps only the fields the native
    merge proof needs. A missing PR or any other HTTP error reads as None (not proven: the intent stays open)."""

    def __init__(self, gh, max_reads=SETTLE_MERGE_READS):
        self.gh, self.max_reads, self.docs = gh, max_reads, {}

    def __call__(self, pr):
        key = str(int(pr))
        if key not in self.docs:
            if len(self.docs) >= self.max_reads:
                return None
            try:
                doc = self.gh.get(f"pulls/{key}")
                self.docs[key] = {"number": doc.get("number"), "merged": doc.get("merged"), "merge_commit_sha": doc.get("merge_commit_sha"),
                                  "head_sha": (doc.get("head") or {}).get("sha"), "merged_at": doc.get("merged_at"),
                                  "merged_by": (doc.get("merged_by") or {}).get("login") if isinstance(doc.get("merged_by"), dict) else None,
                                  "state": doc.get("state")} if isinstance(doc, dict) else None
            except urllib.error.HTTPError:
                self.docs[key] = None
        return self.docs[key]


class LogReader:
    """`log_of` for open_intents() (fix round 5, P1-05): the log text of the `execute` job of one run of this workflow
    (GET actions/runs/<id>/jobs, then the job's log), memoised and capped like RunReader. A run with no completed
    execute job, or any HTTP error, reads as None (not proven)."""

    def __init__(self, gh, max_reads=2):
        self.gh, self.max_reads, self.docs = gh, max_reads, {}

    def __call__(self, run_id):
        key = str(int(run_id))
        if key not in self.docs:
            if len(self.docs) >= self.max_reads:
                return None
            self.docs[key] = None
            try:
                jobs, ok = self.gh.pages(f"actions/runs/{key}/jobs", {"filter": "latest"}, key="jobs", max_pages=1)
                job = [j for j in jobs or [] if isinstance(j, dict) and j.get("name") == "execute" and j.get("status") == "completed"
                       and j.get("run_id") in (None, int(key))]
                if ok and len(job) == 1 and isinstance(job[0].get("id"), int):
                    text = self.gh.text(f"actions/jobs/{job[0]['id']}/logs")
                    self.docs[key] = text if isinstance(text, str) else None
            except (urllib.error.HTTPError, ValueError):          # an expired or oversized log: not proven
                self.docs[key] = None
        return self.docs[key]


def logged_write(log_of, run_id, token, comment_id):
    """Did the execute job of run `run_id` itself write ledger post `comment_id` of kind `token`? Its own finish line
    (S1_EXECUTOR_V1 ... writes=<n>:<token>#<id>,...) in that job's log says so. Unread: False."""
    if log_of is None or run_id is None or type(comment_id) is not int:
        return False
    text = log_of(run_id)
    want = re.compile(rf"S1_EXECUTOR_V1 mode=LIVE decision=\S+ action=\S+ result=[^\n]*? writes=\d+:\S*{re.escape(token)}#{comment_id}(?![0-9])")
    return isinstance(text, str) and want.search(text) is not None


def native_outcome(it, merge_of, run_of):
    """Fix round 5 (#173/7188234670 P1-05): what native state says about executor intent `it` NOW, as an outcome that
    can settle it: ABSENT (the PR is not merged) or FOREIGN (merged, but at another head, by another actor or outside
    the intent's window), and only after the intent's OWN run has ended (a merge call of a running job may still land).
    None: unproven, or merged by the Actions bot at this head inside the window (that is this intent's merge)."""
    if merge_of is None or run_of is None:
        return None
    rid = executor_run((it.get("row") or {}).get("body"))
    run = run_of(rid) if rid is not None else None
    if not isinstance(run, dict) or run.get("id") != rid or run.get("status") != "completed":
        return None
    native = merge_of(it["pr"])
    if not isinstance(native, dict):
        return None
    if native.get("merged") is False:
        return "ABSENT"
    if native.get("merged") is not True:
        return None
    try:
        merged_at, at = stamp(native.get("merged_at")), stamp(it["created_at"])
    except (ValueError, KeyError, TypeError):
        return None
    mine = native.get("head_sha") == it["head"] and native.get("merged_by") == ACTIONS_BOT["login"] \
        and at - timedelta(seconds=5) <= merged_at <= at + timedelta(minutes=15)
    return None if mine else "FOREIGN"


HALT_FIRST = re.compile(r"^S1_LANE_HALTED PR=(\d{1,10}) head=([0-9a-f]{40})\b")
LOG_PROOFS_PER_READ = 2               # executor intents whose run log one open_intents() call reads for the induction floor


def settles(c, it, merge_of=None, run_of=None):
    """Does this post READ as the outcome of intent `it`? Who wrote it is open_intents()'s question.

    An EXECUTOR merge intent (the Actions bot wrote it and it names its run: `it["exact"]`) is settled only by an outcome
    bound to it exactly (ChatGPT finding A10 / #5): an S1_LANE_MERGE_v1 whose `intent:`, `pr:` and `head:` are this
    intent's id, PR and head AND whose `merge:` commit is the PR's native merge_commit_sha with the PR natively merged
    at that head (`merge_of`, GET pulls/<n>; unread: not settled); an S1_LANE_HALTED whose first line names this PR and
    head and whose `intent:` is this id; or an S1_OP_DONE_v1 whose `intent:` is this id, result ABSENT or FOREIGN, and
    evidence names this PR. A stale or other-head outcome of the same PR never settles it.

    LEGACY intents (the owner account's ChatGPT lane, which names no executor run) keep the reading the live lane has
    always had: an S1_OP_DONE_v1 that cites the id anywhere, or an S1_LANE_MERGE_v1 or S1_LANE_HALTED that names the
    PR. They are quarantined, not migrated: open_intents() marks them `legacy`, and the executor posts no new one."""
    token, body = first_line_token(c.get("body")), str(c.get("body") or "")
    if it.get("exact"):
        f = fields(body)
        if (f.get("intent") or "").strip() != str(it["id"]):
            return False
        if token == "S1_OP_DONE_v1":
            result = (f.get("result") or "").strip()
            if result == "OWNER_SETTLED":                        # the owner's explicit manual settlement of exactly this intent id
                return is_owner_unedited(c)
            # fix round 5 (P1-05): the outcome must also be TRUE natively, after the intent's own run ended: a forged or
            # early ABSENT (another workflow naming a running executor run) can then only ever say what is true
            return result in ("ABSENT", "FOREIGN") and re.match(rf"pr={it['pr']}(?!\d)", (f.get("evidence") or "").strip()) is not None \
                and native_outcome(it, merge_of, run_of) == result
        if token == "S1_LANE_HALTED":
            m = HALT_FIRST.match(body.splitlines()[0] if body else "")
            return bool(m) and int(m.group(1)) == it["pr"] and m.group(2) == it["head"]
        if token == "S1_LANE_MERGE_v1":
            merge = (f.get("merge") or "").strip()
            if (f.get("pr") or "").strip() != str(it["pr"]) or (f.get("head") or "").strip() != it["head"] or not SHA40.fullmatch(merge) or merge_of is None:
                return False
            native = merge_of(it["pr"])
            return isinstance(native, dict) and native.get("merged") is True and native.get("merge_commit_sha") == merge and native.get("head_sha") == it["head"]
        return False
    if token == "S1_OP_DONE_v1":
        return re.search(rf"(?<!\d){it['id']}(?!\d)", body) is not None
    if token in ("S1_LANE_MERGE_v1", "S1_LANE_HALTED") and it["kind"] == "S1_LANE_MERGE_INTENT_v1" and it["pr"] is not None:
        return re.search(rf"(?<!\d){it['pr']}(?!\d)", fields(body).get("pr", "") or body.splitlines()[0]) is not None
    return False


def open_intents(comments, now, settle_minutes=60, run_of=None, merge_of=None, log_of=None):
    """A cheap SIGNAL for RECONCILE (EVIDENCE_BINDINGS B3), never the reconciliation itself: authentic v3 intents
    (they carry loop=) with no later outcome that names their PR or cites their id.

    WHO may settle an intent. A settled intent unblocks the lane (C9) and ends its readback, so this is the one ledger
    rule that can start something, and the identity of the Actions bot is not enough for it (about 30 workflows of this
    repository hold issues: write and post as that bot). An intent is settled by a never-edited outcome post of the
    owner account, or by a never-edited outcome post that executor_post() proves to be the executor job's. `run_of`
    is the caller's run reader (RunReader, or a snapshot's record of it); None: no Actions-bot post settles anything.

    Bounded reads. An executor merge intent whose run is proven was posted by a run that had itself found no open
    merge intent (the executor's verify_merge), and an owner post that settles an executor merge intent closes it and
    every older one. So executor merge intents OLDER than the newest such intent are not examined again; intents the
    owner account posted are always examined (an owner post settles them at no read).

    Fix round 5 (#173/7188234670 P1-05): "posted by a run that had itself found no open merge intent" is proven only by
    that run's OWN execute log naming the intent as one of its writes (logged_write, `log_of`; at most
    LOG_PROOFS_PER_READ logs per call). A bot post that only names a run, which any workflow with issues: write can
    make, never closes older intents. No proof: every executor intent is examined (fail closed: an unproven one stays
    open and holds the lane, C9)."""
    rows = [c for c in comments if isinstance(c, dict)]
    intents = []
    for c in rows:
        token = first_line_token(c.get("body"))
        if not is_s1_unedited(c) or token not in OP_INTENTS:
            continue
        f = fields(c.get("body"))
        if "loop" not in f:
            continue                                   # a legacy intent: S1 decides case (i) natively, not this signal
        pr = re.search(r"\d+", f.get("pr", ""))
        head = (f.get("head") or "").strip()
        bot = is_actions_bot(c.get("user"))
        exact = bot and token == "S1_LANE_MERGE_INTENT_v1" and executor_run(c.get("body")) is not None and bool(pr) and bool(SHA40.fullmatch(head))
        intents.append({"id": c["id"], "kind": token, "pr": int(pr.group(0)) if pr else None, "created_at": c["created_at"],
                        "bot": bot, "row": c, "head": head, "exact": exact})
    memo = {}

    def outcomes(it):                                  # lazy: the native merge proofs are read only for the intents examined
        if it["id"] not in memo:
            memo[it["id"]] = [c for c in rows if c.get("id", 0) > it["id"] and settles(c, it, merge_of, run_of)]
        return memo[it["id"]]
    by_owner = lambda it: any(is_owner_unedited(c) for c in outcomes(it))
    executor_merge = [it for it in intents if it["bot"] and it["kind"] == "S1_LANE_MERGE_INTENT_v1"]
    floor, proofs = 0, 0
    for it in sorted(executor_merge, key=lambda i: i["id"], reverse=True):
        if by_owner(it):
            floor = it["id"]
            break
        if proofs < LOG_PROOFS_PER_READ and executor_post(it["row"], run_of, now):
            proofs += 1
            if logged_write(log_of, executor_run(it["row"].get("body")), "S1_LANE_MERGE_INTENT_v1", it["id"]):
                floor = it["id"]
                break
    out = []
    for it in intents:
        if it["bot"] and it["kind"] == "S1_LANE_MERGE_INTENT_v1" and it["id"] < floor:
            continue                                   # closed by induction (docstring): never read again
        if by_owner(it) or any(executor_post(c, run_of, now) for c in outcomes(it)):
            continue
        age = (now - stamp(it["created_at"])).total_seconds() / 60
        out.append(dict({"id": it["id"], "kind": it["kind"], "pr": it["pr"], "age_min": int(age), "due": age > settle_minutes},
                        **({} if it["exact"] else {"legacy": True})))
    return out


def _pr_head(body):
    f = fields(body)
    pr, head = re.search(r"\d+", f.get("pr", "")), (f.get("head") or "").strip()
    return (int(pr.group(0)), head, f) if pr and SHA40.fullmatch(head) else (None, None, f)


def fallback_candidates(comments):
    """{(PR, head): [post, ...]} of the S1_FALLBACK_CANDIDATE_v1 receipts an S1 author posted on #1156, oldest first
    (edited or not: the count only ever parks a head; the executor itself relies only on a PROVEN one)."""
    out = {}
    for c in sorted((c for c in comments if isinstance(c, dict)), key=lambda c: c.get("id") or 0):
        if is_s1_author(c) and first_line_token(c.get("body")) == "S1_FALLBACK_CANDIDATE_v1":
            pr, head, _f = _pr_head(c.get("body"))
            if pr is not None:
                out.setdefault((pr, head), []).append(c)
    return out


def p01_named(comments, reviews, inline=()):
    """Route (c) only: True when a conversation comment, a review summary or (fix round 5, P1-11) an inline review
    comment of the PR names P0 or P1 (any author, any time, resolved or not); None when any list was not read. Routes
    (a) and (b) do not use it: there a reviewer has read the head, and for them only an unresolved review THREAD
    blocks (C6)."""
    if comments is None or reviews is None or inline is None:
        return None
    return any(re.search(r"(?i)\bP[01]\b", str(r.get("body") or "")) for r in list(comments) + list(reviews) + list(inline) if isinstance(r, dict))


def fallback_mismatch(posts):
    """True when the candidate receipts of ONE (PR, head) do not all carry the same evidence hash: two runs disagreed
    about that head. A candidate with no evidence line counts as a value of its own."""
    return len({(fields(c.get("body")).get("evidence") or "").strip() for c in posts}) > 1


def recalls(comments):
    """Every fallback merge an S1 author recorded on #1156, oldest first (owner decision 2026-11-25): an
    S1_CODEX_RECALL_PENDING_v1, or an S1_LANE_MERGE_v1 whose review reads FALLBACK(...), by PR and head. A pending post
    counts edited or not (it only adds caution). Whether a recall is still PENDING is decided by Codex's own review
    state of that head, read natively (recall_status), never by a receipt: `cleared` only says that a clear receipt of
    an S1 author exists, and it is used for one thing, to keep the executor from posting a second one (review finding
    P2-D: any workflow with issues: write, and anything that writes as the owner account, can post such a receipt)."""
    pending, cleared = {}, set()
    for c in sorted((c for c in comments if isinstance(c, dict)), key=lambda c: c.get("id") or 0):
        if not is_s1_author(c):
            continue
        token = first_line_token(c.get("body"))
        pr, head, f = _pr_head(c.get("body"))
        if pr is None:
            continue
        if token == "S1_CODEX_RECALL_PENDING_v1" or (token == "S1_LANE_MERGE_v1" and str(f.get("review") or "").startswith("FALLBACK(")):
            pending.setdefault((pr, head), {"c": c["id"], "pr": pr, "head": head, "merge": (f.get("merge") or "").strip() or None})
        elif token == "S1_CODEX_RECALL_CLEARED_v1":
            cleared.add((pr, head))
    return [dict(v, cleared=k in cleared) for k, v in pending.items()]


def unverified_receipts(comments):
    """Route (b) merges whose Claude receipt nobody has checked against the private Bridge (P1-C): every
    S1_LANE_MERGE_v1 of an S1 author, posted by an executor run, whose review reads exactly CLAUDE. The workflow
    cannot read the Bridge, so nothing in GitHub Actions can clear this. It is cleared by a never-edited post of the
    OWNER account on #1156, S1_CLAUDE_RECEIPT_VERIFIED_v1, that names the PR, the head and a 40-hex report_blob,
    which must be the blob the merge receipt recorded when it recorded one."""
    merged, verified = {}, set()
    for c in sorted((c for c in comments if isinstance(c, dict)), key=lambda c: c.get("id") or 0):
        token = first_line_token(c.get("body"))
        pr, head, f = _pr_head(c.get("body"))
        if pr is None:
            continue
        blob = (f.get("report_blob") or "").strip()
        if token == "S1_LANE_MERGE_v1" and is_s1_author(c) and (f.get("review") or "").strip() == "CLAUDE" and executor_run(c.get("body")) is not None:
            merged.setdefault((pr, head), {"c": c["id"], "pr": pr, "head": head, "report_blob": blob if SHA40.fullmatch(blob) else None})
        elif token == "S1_CLAUDE_RECEIPT_VERIFIED_v1" and is_owner_unedited(c) and SHA40.fullmatch(blob):
            verified.add((pr, head, blob))
    return [v for (pr, head), v in merged.items()
            if not any(k[0] == pr and k[1] == head and v["report_blob"] in (None, k[2]) for k in verified)]


EXECUTOR_WATCH_RUNS = 3              # earlier runs whose jobs one build reads to find the newest published one
EXECUTOR_STALE_HOURS = 3             # a newest published run older than this: the executor is not running


def read_executor_watch(gh, current_run):
    """Fix round 4 (ChatGPT #8): the watchdog's native reads. Fix round 6 (F2): the executor is its own workflow, so the
    newest completed runs of s1-executor.yml on main (one list read), and for at most EXECUTOR_WATCH_RUNS of them,
    newest first, the jobs and the execute job's log, until one whose execute job ran and had a decision (a run whose
    job was skipped, or whose health line reads NO_DECISION, had nothing to execute)."""
    doc = gh.get(f"actions/workflows/{Path(EXECUTOR_WORKFLOW_PATH).name}/runs", {"branch": "main", "status": "completed", "per_page": 30})
    runs = sorted((r for r in (doc.get("workflow_runs") or []) if isinstance(r, dict) and r.get("event") in EXECUTOR_EVENTS
                   and r.get("status") == "completed" and r.get("conclusion") != "skipped" and isinstance(r.get("id"), int)),
                  key=lambda r: r["id"], reverse=True)
    seen = []
    for r in runs[:EXECUTOR_WATCH_RUNS]:
        jobs, ok = gh.pages(f"actions/runs/{r['id']}/jobs", {"filter": "latest"}, key="jobs", max_pages=1)
        names = {j.get("name"): j.get("conclusion") for j in jobs or [] if isinstance(j, dict)}
        # "publish": whether the brief run of this executor run published the brief it acted on ("success": it had a
        # decision; "none": its job was skipped, or its health line reads NO_DECISION)
        seen.append({"run": r["id"], "at": r.get("created_at"), "publish": "none", "execute": names.get("execute"), "complete": bool(ok)})
        if names.get("execute") in (None, "skipped"):
            continue
        # fix round 5 (#173/7188234670 P1-08): the job conclusion is not the executor's health (an UNVERIFIED run exits
        # 0). The ONE health line of that job's own log is read.
        job = [j for j in jobs or [] if isinstance(j, dict) and j.get("name") == "execute" and j.get("status") == "completed" and isinstance(j.get("id"), int)]
        text = gh.text(f"actions/jobs/{job[0]['id']}/logs") if len(job) == 1 else None
        seen[-1]["health"] = health_of_log(text)
        if seen[-1]["health"] != "UNVERIFIED" or not no_decision_log(text):
            seen[-1]["publish"] = "success"
            break
    return {"runs": seen, "listed": len(runs)}


def no_decision_log(text):
    """The one health line of an executor log reads result NO_DECISION(...): its brief run published nothing new."""
    found = HEALTH_LINE.findall(text) if isinstance(text, str) else []
    try:
        return len(found) == 1 and str(json.loads(found[0]).get("result") or "").startswith("NO_DECISION(")
    except (ValueError, AttributeError):
        return False


HEALTH_LINE = re.compile(r"S1_EXECUTOR_HEALTH (\{[^\n]*\})")
HEALTH_STATES = ("OK", "HELD", "UNVERIFIED", "DEGRADED", "AMBIGUOUS")


def health_of_log(text):
    """The state of the ONE S1_EXECUTOR_HEALTH line of an execute job's log: "NOHEALTH" when there is none (a crash
    before the handler, a cancelled or killed job), "MANY" when there are several, "UNREAD" when it does not parse."""
    if not isinstance(text, str):
        return "UNREAD"
    found = HEALTH_LINE.findall(text)
    if not found:
        return "NOHEALTH"
    if len(found) > 1:
        return "MANY"
    try:
        state = json.loads(found[0]).get("state")
    except (ValueError, AttributeError):
        return "UNREAD"
    return state if state in HEALTH_STATES else "UNREAD"


def executor_watch(doc, mode, now):
    """The executor's health as GitHub itself records it, independent of ChatGPT and of the executor's own report:
    OFF (the switch says OFF), OK (the newest run that published a decision ran its execute job to success), FAILED
    (that job failed, was cancelled or timed out: DEGRADED, AMBIGUOUS or a crash), MISSING (it did not run), STALE (the
    newest published run is older than EXECUTOR_STALE_HOURS), NONE (no published run among those read) or UNREAD."""
    if mode == "OFF":
        return {"state": "OFF"}
    runs = doc.get("runs") if isinstance(doc, dict) else None
    if not isinstance(runs, list) or not all(isinstance(r, dict) and r.get("complete") for r in runs):
        return {"state": "UNREAD"}
    first = next((r for r in runs if r.get("publish") == "success"), None)
    if first is None:
        return {"state": "NONE" if doc.get("listed") else "UNREAD"}
    try:
        age = (now - stamp(first.get("at"))).total_seconds() / 3600
    except (ValueError, TypeError):
        return {"state": "UNREAD", "run": first.get("run")}
    state = {"success": "OK", "skipped": "MISSING", None: "MISSING"}.get(first.get("execute"), "FAILED")
    health = first.get("health")
    if state in ("OK", "FAILED"):
        # fix round 5 (P1-08): OK only when the job succeeded AND its own health line reads OK or HELD; any other line
        # (UNVERIFIED, DEGRADED, AMBIGUOUS), no line, several lines or an unread log is that state, never OK
        state = health if health not in ("OK", "HELD") else ("OK" if state == "OK" else "FAILED")
        state = state if isinstance(state, str) else "UNREAD"
    if age > EXECUTOR_STALE_HOURS:
        state = "STALE"
    return {"state": state, "run": first.get("run"), "execute": first.get("execute"), "health": health, "age_h": round(age, 1)}


def recall_window(items, now, n=RECALL_READS_PER_BUILD):
    """Which pending recalls ONE build reads: n of them, starting one further every hour. A recall that never clears
    (a head Codex does not review, a finding nobody resolves) can therefore not starve the ones behind it: with more
    than n pending, every one is still read in n of every len(items) hours."""
    if not items:
        return []
    start = (int(now.timestamp()) // 3600) % len(items)
    return (items[start:] + items[:start])[:n]


def recall_publish(items, cap=10):
    """The recalls a brief publishes, at most `cap` (ChatGPT audit A23): every item THIS build read first (recall_window
    reads RECALL_READS_PER_BUILD < cap of them), then the unread ones, oldest first. Publication used to be the oldest
    ten, so with more than ten pending the read ones beyond the tenth never reached the decision or the executor: they
    could never be requested again or cleared. The count of pending recalls is published separately and is never cut."""
    read = [i for i in items if i.get("codex") != "NOT_READ"]
    return (read + [i for i in items if i.get("codex") == "NOT_READ"])[:cap]


def read_recall(gh, n):
    """The review state of one merged PR with a pending recall: its comments, reviews, inline comments and commits."""
    c, c1 = gh.pages(f"issues/{n}/comments", max_pages=10)
    r, c2 = gh.pages(f"pulls/{n}/reviews", max_pages=10)
    i, c3 = gh.pages(f"pulls/{n}/comments", max_pages=10)
    k, c4 = gh.pages(f"pulls/{n}/commits", max_pages=3)
    return {"comments": c, "reviews": r, "inline": i, "commits": k, "complete": bool(c1 and c2 and c3), "commits_complete": bool(c4)}


def recall_status(head, read, now, silent_hours):
    """Codex's state for one recalled head, from read_recall(): FINAL clears the recall, FINDINGS is the owner's."""
    if not isinstance(read, dict):
        return "NOT_READ"
    return codex_review(head, {}, read.get("commits") or [], bool(read.get("commits_complete")), read.get("comments") or [], read.get("reviews") or [],
                        read.get("inline") or [], bool(read.get("complete")), now, silent_hours).get("status")


def attempted_heads(comments):
    """(PR, head) of every merge intent an S1 author ever posted on #1156, settled or not, edited or not. One merge
    attempt per PR head, ever (AGENTS.md section 0.2i: a refused merge is never retried): such a head is the owner's
    to merge, and a new commit is a new head. This list only ever stops a merge."""
    out = set()
    for c in comments:
        if isinstance(c, dict) and is_s1_author(c) and first_line_token(c.get("body")) == "S1_LANE_MERGE_INTENT_v1":
            f = fields(c.get("body"))
            pr, head = re.search(r"\d+", f.get("pr", "")), (f.get("head") or "").strip()
            if pr and SHA40.fullmatch(head):
                out.add((int(pr.group(0)), head))
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


def health_window_ok(runs, complete):
    """Fix round 6 (S3): did one read return main health's required window, ROUTE 1's newest page of runs? A list that is
    either a full page (100 runs: the newest 100, as pages(max_pages=1) reads it) or a short page that pages() found
    consistent (its total_count and ids). Empty, malformed or a short inconsistent page: not read."""
    return isinstance(runs, list) and bool(runs) and (len(runs) >= 100 or complete is True)


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
                or (status not in ("added", "removed", "renamed") and outside and (f.get("deletions") or 0) > 0
                    and ((f.get("additions") or 0) == 0
                         or ((p.endswith(DATA_SUFFIXES) or RECORD_NAME.search(p)) and (f.get("deletions") or 0) > (f.get("additions") or 0)))):
            add(7, prev or p)
        elif status not in ("added", "removed", "renamed") and outside and f.get("patch") is None and (p.lower().endswith(DATA_SUFFIXES + (".gz", ".zip", ".parquet")) or RECORD_NAME.search(p)):
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


def ai_authored(pr, commits, commits_complete, author):
    """AGENTS.md section 0.2i: is this PR marked as written by an AI or by automation? By authorship() (S1, Codex, a
    Bridge package), by its branch name, by a commit trailer or by its body; an unreadable commit list reads as yes.
    The branch name itself is never published, only this fact (B.prs[].thin.ai)."""
    if not commits_complete or len(commits) > 250 or not isinstance(author, dict):
        return True
    if author.get("s1") is not False or author.get("codex") is not False or author.get("claude_package") is not False:
        return True
    ref, body = str((pr.get("head") or {}).get("ref") or ""), str(pr.get("body") or "")
    return bool(AI_BRANCH.match(ref) or AI_BODY.search(body)
                or any(AI_TRAILER.search(str((c.get("commit") or {}).get("message") or "")) for c in commits))


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
            if any(LIMIT_RE.search(str(c.get("body") or "")) for c in answers):
                out["status"] = "UNAVAILABLE"
            elif out["request_age_h"] > silent_hours:
                out["status"] = "SILENT"
            else:
                out["status"] = "REQUESTED"
            # Section 0.2i route (c): a status is evidence that Codex is unavailable only when it rests on a request of
            # the OWNER account that was never edited. Anyone can comment on a public repository, and Codex is not known
            # to answer accounts it does not serve, so silence after an outsider's request proves nothing (P1-A).
            mine = [codex_finality.effective_request_time(c) for c in comments
                    if is_owner_unedited(c) and re.search(r"(?mi)^\s*@codex\s+review\b", str(c.get("body") or ""))]
            mine = [r for r in mine if r > head_time]
            if mine and out["status"] in ("UNAVAILABLE", "SILENT"):
                asked = max(mine)
                said = [(stamp(c.get("updated_at") or c.get("created_at")), c) for c in comments if codex_finality.is_codex(c)]
                said = [(at, c) for at, c in said if at > asked]
                limits = [at for at, c in said if LIMIT_RE.search(str(c.get("body") or ""))]
                # an answer is a Codex comment, a Codex PR review or a Codex inline comment after the request
                other = [stamp(r["submitted_at"]) for r in reviews if codex_finality.is_codex(r) and r.get("submitted_at")] \
                    + [stamp(r.get("updated_at") or r["created_at"]) for r in inline if codex_finality.is_codex(r)]
                if out["status"] == "UNAVAILABLE" and limits:
                    out["offline"] = {"signal": "UNAVAILABLE", "at": iso(max(limits)), "request_at": iso(asked)}
                elif out["status"] == "SILENT" and (now - asked).total_seconds() > silent_hours * 3600 and not said and not any(t > asked for t in other):
                    out["offline"] = {"signal": "SILENT", "at": iso(asked), "request_at": iso(asked)}
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


def claude_written(pr, commits, commits_complete):
    """Is this head marked as written by Claude (branch name, commit trailer, body)? An unreadable commit list: yes."""
    if not commits_complete or len(commits) > 250:
        return True
    return bool(CLAUDE_BRANCH.match(str((pr.get("head") or {}).get("ref") or "")) or CLAUDE_BODY.search(str(pr.get("body") or ""))
                or any(CLAUDE_TRAILER.search(str((c.get("commit") or {}).get("message") or "")) for c in commits))


def claude_receipt(head, comments):
    """Route (b) of the review gate, read natively: a CLAUDE_REVIEW_v1 for exactly this head among the PR's OWN
    comments (the workflow cannot read the private Bridge, so a receipt counts only once it stands on the PR), by the
    owner account, with the same rules as receipt_state(): APPROVE needs a never-edited, solicited, non-PROACTIVE
    receipt with no newer refusal; a REQUEST_CHANGES or BLOCK is a VETO until a newer admissible APPROVE."""
    if comments is None:
        return "NOT_PROVEN"
    try:
        state = receipt_state(head, comments)
        return "VETO" if state["veto"] else "APPROVE" if claude_receipt_fields(head, comments) is not None else "NONE"
    except (ValueError, KeyError, TypeError, AttributeError):
        return "NOT_PROVEN"


def claude_receipt_fields(head, comments):
    """The ONE receipt route (b) accepts for this head, as the fields the merge receipt records, or None (P1-C). On top
    of receipt_state()'s approval it must be complete on the PR itself: the request it names is a real comment there,
    an S1_REVIEW_REQUEST_v1 for this head by the owner account, never edited and older than the receipt; the receipt
    carries `report`, a 40-hex `report_blob` and a 40-hex `bridge_commit`; it says `lane_eligible: YES`; and it states
    its `independence`. What this does NOT prove: who wrote it (the owner account did), or that the report exists in
    the private Bridge (the workflow cannot read it). Hence the unverified-receipt flag (unverified_receipts)."""
    state = receipt_state(head, comments)
    f = state.get("fields") if isinstance(state.get("fields"), dict) else {}
    if state["veto"] or not state["approved"] or not state["page_complete"]:
        return None
    if (f.get("lane_eligible") or "").strip() != "YES" or (f.get("independence") or "").strip() not in INDEPENDENCE:
        return None                                              # fix round 4 (#12): a known independence value, not any text
    rid, row = cited_request(f, comments)
    if rid is None or row is None:
        return None
    # fix round 5 (#173/7188234670 P1-10): the receipt is bound by its own comment id, body hash, update time and
    # independence, and the request by its body hash, so the final look notices a receipt replaced under the same blobs
    c = state.get("comment") if isinstance(state.get("comment"), dict) else {}
    return {"request": rid, "request_sha256": hashlib.sha256(str(row.get("body") or "").encode()).hexdigest()[:16],
            "receipt": c.get("id"), "receipt_sha256": hashlib.sha256(str(c.get("body") or "").encode()).hexdigest()[:16],
            "receipt_updated_at": c.get("updated_at"), "independence": (f.get("independence") or "").strip(),
            "report_blob": (f.get("report_blob") or "").strip(), "bridge_commit": (f.get("bridge_commit") or "").strip()}


def changes_requested(reviews):
    """A native CHANGES_REQUESTED voids every review kind, on whatever commit it was made. As on GitHub itself it
    stands until the same reviewer approves or the review is dismissed: a new push never lifts it. Each reviewer's
    newest non-comment review counts, over every commit of the PR."""
    newest = {}
    for r in sorted(reviews, key=lambda r: r.get("id") or 0):
        if r.get("state") in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED"):
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


ITEM_KINDS = ("FIX", "TEST", "DOCS", "RESEARCH")     # every other kind, or none, reads as DIRECTION (STEWARD_STATES.md)
ITEM_RISKS = ("LOW", "MEDIUM", "HIGH", "HIGH_IMPACT", "EXTREME")


def newest_item(comments):
    """The newest authentic S1_ITEM_v1 on the PR (a display hint for S1's own S1_ITEM_v1; counters are never trusted).
    kind and risk are NOT the newest item's: they are the strongest over EVERY authentic item, because both are "only
    ever raised" (a later item saying kind FIX never lowers an earlier DIRECTION). An unknown kind is DIRECTION; an
    unknown risk is UNCLEAR, above every class."""
    items = [fields(c.get("body")) | {"_c": c} for c in sorted(comments, key=lambda c: c.get("id") or 0, reverse=True)
             if is_owner_unedited(c) and first_line_token(c.get("body")) == "S1_ITEM_v1" and re.search(r"(?m)^\s*contract=[0-9a-f]{8}\b", str(c.get("body")))]
    if not items:
        return None
    f, c = items[0], items[0]["_c"]
    kinds = [(i.get("kind") or "").strip().upper() for i in items]
    risks = [(i.get("risk") or "").strip().upper() for i in items]
    kind = "DIRECTION" if any(k not in ITEM_KINDS for k in kinds) else kinds[0]
    risk = "UNCLEAR" if any(r not in ITEM_RISKS for r in risks) else max(risks, key=ITEM_RISKS.index)
    return {"c": c["id"], "state": f.get("state"), "attempt": f.get("attempt"), "risk": risk, "kind": kind,
            "due": f.get("due"), "park_count": f.get("park_count"), "at": c.get("created_at"),
            "owner_update": OWNER_UPDATE_NEXT in str(f.get("next") or "")}


def codex_availability(comment_lists, now, hours=CODEX_LIMIT_HOURS):
    """Is Codex known to be unavailable? The NEWEST Codex comment over every PR read in this run decides: a usage-limit
    answer younger than `hours` means unavailable. Anything unreadable leaves it available (the per-PR rules still
    apply, and a request that Codex cannot serve costs one comment, never a gate)."""
    newest = None
    for comments in comment_lists:
        for c in comments or []:
            try:
                if codex_finality.is_codex(c):
                    at = stamp(c.get("updated_at") or c.get("created_at"))
                    if newest is None or at > newest[0]:
                        newest = (at, c)
            except (ValueError, TypeError):
                continue
    if newest and LIMIT_RE.search(str(newest[1].get("body") or "")) and 0 <= (now - newest[0]).total_seconds() <= hours * 3600:
        return {"available": False, "why": "usage_limit", "at": iso(newest[0])}
    return {"available": True}


def read_codex_feed(gh, now, hours=CODEX_FEED_HOURS):
    """Codex's own activity in the WHOLE repository over the last `hours`, newest first: its issue and PR conversation
    comments and its inline review comments (two list reads; neither is limited to open PRs or to the PRs a build reads
    in depth). `complete` is False when either list did not end inside its pages."""
    since = iso(now - timedelta(hours=hours))
    rows, c1 = gh.pages("issues/comments", {"since": since, "sort": "created", "direction": "desc"}, max_pages=5)
    inline, c2 = gh.pages("pulls/comments", {"since": since, "sort": "created", "direction": "desc"}, max_pages=5)
    slim = lambda r: {"id": r.get("id"), "user": r.get("user"), "created_at": r.get("created_at"), "updated_at": r.get("updated_at"),
                      "body": str(r.get("body") or "")[:160]}
    return {"since": since, "comments": [slim(r) for r in rows if isinstance(r, dict) and codex_finality.is_codex(r)],
            "inline": [slim(r) for r in inline if isinstance(r, dict) and codex_finality.is_codex(r)], "complete": bool(c1 and c2)}


def codex_activity(feed, prs):
    """Everything Codex is known to have posted: the repository-wide feed (read_codex_feed) plus the comments, reviews
    and inline comments of the PRs that were read in depth. {"complete": the feed was read whole, "since", "items":
    [{"at", "limit", "c", "kind"}] newest first}; `limit` marks a usage-limit answer."""
    items = {}

    def add(kind, r, when):
        try:
            if isinstance(r, dict) and codex_finality.is_codex(r) and when:
                items[(kind, r.get("id"))] = {"at": stamp(when), "c": r.get("id"), "kind": kind,
                                              "limit": kind == "comment" and bool(LIMIT_RE.search(str(r.get("body") or "")))}
        except (ValueError, TypeError):
            pass
    feed = feed if isinstance(feed, dict) else {}
    for r in feed.get("comments") or []:
        add("comment", r, r.get("updated_at") or r.get("created_at"))
    for r in feed.get("inline") or []:
        add("inline", r, r.get("updated_at") or r.get("created_at"))
    for d in (prs or {}).values() if isinstance(prs, dict) else []:
        if isinstance(d, dict):
            for r in d.get("comments") or []:
                add("comment", r, r.get("updated_at") or r.get("created_at"))
            for r in d.get("inline") or []:
                add("inline", r, r.get("updated_at") or r.get("created_at"))
            for r in d.get("reviews") or []:
                add("review", r, r.get("submitted_at"))
    return {"complete": feed.get("complete") is True, "since": feed.get("since"),
            "items": sorted(items.values(), key=lambda a: (a["at"], str(a["c"])), reverse=True)}


def offline_signal(cx, activity, now, hours=CODEX_LIMIT_HOURS):
    """Section 0.2i route (c): is Codex DEMONSTRABLY unavailable for this head? The signal, or None (P1-A, P3-F).
    UNAVAILABLE  the owner asked about this head, Codex answered with its usage-limit sentence (codex_review), and
                 Codex's newest activity anywhere in the repository is still a usage-limit answer;
    SILENT       the owner asked about this head, Codex answered nothing on this PR (no comment, review or inline
                 comment) for more than the silent budget, and Codex has posted nothing anywhere in the repository
                 since the request;
    LIMIT        nobody asked about this head, and Codex's newest activity anywhere in the repository is a usage-limit
                 answer at most `hours` old.
    None         everything else: the repository-wide read is incomplete, the evidence is older than that read, the
                 request was not the owner's or was edited, or Codex has done anything else since."""
    try:
        if not isinstance(cx, dict) or not isinstance(activity, dict) or activity.get("complete") is not True:
            return None
        since, items = stamp(activity["since"]), activity.get("items") or []
        status = cx.get("status")
        ev = cx.get("offline") if isinstance(cx.get("offline"), dict) else {}
        if status in ("UNAVAILABLE", "SILENT") and ev.get("signal") == status:
            at = stamp(ev["at"])
            if at < since:
                return None                                      # older than the repository-wide read: what Codex did since is unknown
            if status == "UNAVAILABLE":                          # fix round 5 (P1-11): the newest limit answer is at most `hours` old
                return status if items and items[0]["limit"] and 0 <= (now - items[0]["at"]).total_seconds() <= hours * 3600 else None
            return status if not any(a["at"] > at for a in items) else None
        if status == "NONE" and items and items[0]["limit"] and 0 <= (now - items[0]["at"]).total_seconds() <= hours * 3600:
            return "LIMIT"
        return None
    except (ValueError, KeyError, TypeError):
        return None


def request_for(head, row):
    """Is this Bridge comment an S1_REVIEW_REQUEST_v1 for exactly `head`? The head is the VALUE of the request's own
    head (or head_sha) field. A head that only appears somewhere in the text never counts."""
    if not isinstance(row, dict) or first_line_token(row.get("body")) != "S1_REVIEW_REQUEST_v1":
        return False
    f = fields(row.get("body"))
    return head in ((f.get("head") or "").strip(), (f.get("head_sha") or "").strip())


def receipts_for(head, page):
    """Every CLAUDE_REVIEW_v1 on the page whose head_sha field is exactly `head`, oldest first, as (comment, fields)."""
    out = [(c, fields(c.get("body"))) for c in page if first_line_token(c.get("body")) == "CLAUDE_REVIEW_v1"]
    return sorted(((c, f) for c, f in out if (f.get("head_sha") or "").strip() == head), key=lambda cf: cf[0].get("id") or 0)


def cited_request(f, page):
    """(id named by the receipt's request field, the row with that id on the page or None)."""
    m = re.search(r"\d{6,}", f.get("request") or "")
    return (int(m.group(0)) if m else None), next((r for r in page if m and r.get("id") == int(m.group(0))), None)


def receipt_state(head, page):
    """TICK.md T4 for one head and ONE page of Bridge comments, with the same parser F4 uses:
    veto      a REQUEST_CHANGES or BLOCK by the owner account (edited or not) that no NEWER admissible APPROVE follows.
              An APPROVE that is itself not approved here (edited, unsolicited, PROACTIVE, another author) never
              cancels a refusal. Blocks every merge route;
    approved  an unedited, solicited, non-PROACTIVE APPROVE by the owner account with no newer refusal;
    page_complete  the page itself shows the request row (for this head, by the owner account, unedited, older than
                   the receipt) and the three binding fields. Only then may a review request be suppressed."""
    rows = receipts_for(head, page)
    out = {"veto": False, "approved": False, "page_complete": False, "fields": None}
    good = None
    for c, f in rows:
        if f.get("verdict") in ("REQUEST_CHANGES", "BLOCK"):
            if login(c) == OWNER_LOGIN:                          # the same author rule as an approval: the owner account
                good = None                                      # a newer refusal voids every older approval
                out["veto"] = True
            continue
        rid, row = cited_request(f, page)
        if f.get("verdict") == "APPROVE" and is_owner_unedited(c) and "PROACTIVE" not in str(c.get("body")) and rid \
                and (row is None or request_for(head, row)):
            try:
                complete = bool(row is not None and is_owner_unedited(row) and stamp(row["created_at"]) < stamp(c["created_at"])
                                and f.get("report") and SHA40.fullmatch(f.get("report_blob") or "") and SHA40.fullmatch(f.get("bridge_commit") or ""))
            except (ValueError, KeyError, TypeError):
                complete = False
            good = (f, complete, c)
            # fix round 4 (ChatGPT #173/7186140947 finding 02): only a COMPLETE, eligible, independent APPROVE lifts an
            # older refusal. An approval that lacks its request row, a blob, lane_eligible: YES or a known independence
            # is a candidate at most, never the authority that ends a veto.
            if complete and (f.get("lane_eligible") or "").strip() == "YES" and (f.get("independence") or "").strip() in INDEPENDENCE:
                out["veto"] = False
    if good:
        out.update(approved=True, page_complete=good[1], fields=good[0], comment=good[2])
    return out


def claude_review(head, bridge_comments):
    """ACTION_LOOP C5 for a CLAUDE_REVIEW_v1 on Bridge #173, as far as comments alone decide it. The workflow cannot
    read the private Bridge, so the brief never carries this; S1 does this read itself. Kept here as the reference
    implementation of the comment checks (tests, and offline dry runs against recorded Bridge comments)."""
    mine = receipts_for(head, bridge_comments)
    if not mine:
        return {"status": "NONE"}
    c, f = mine[-1]                                              # the NEWEST one for H decides, whatever it says
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
        _rid, req = cited_request(f, bridge_comments)
        if not req or not request_for(head, req) or not is_owner_unedited(req) or stamp(req["created_at"]) >= stamp(c["created_at"]):
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
    e = {"n": n, "head": head, "open": []}
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
        e["unreadable"] = True                                   # never ranked, never merged; the other PRs are unaffected
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
    e["thin"] = decision_v1.entry_facts(pr, files, fc, ctx.get("push_filters"))   # section 0.2i: judgment as data
    e["thin"]["bot"] = (pr.get("user") or {}).get("type") != "User"                # a PR a bot opened: never self-merged
    if data.get("isolation"):
        e["isolation"] = {k: (data["isolation"].get(k) or [])[:6] for k in ("owner_gated", "high_floor") if data["isolation"].get(k)}
    cmp_ = data.get("compare") or {}
    main_changed = set(cmp_.get("main_changed_paths") or [])
    e["behind"] = cmp_.get("behind_by")
    overlap = sorted(main_changed & set(paths)) if cmp_.get("complete") else None
    # A17: did main change a privacy- or CI-gate file AFTER this head's privacy-scan run was created? data["gate_drift"]
    # is that list, read from git at the base SHA the run recorded. When the run names no base, the merge-base decides
    # (older, so never less strict). 
    gate_files = set(GATE_FILES) | {t["workflow_path"] for t in ctx["tuples"]}
    drift = data.get("gate_drift")
    if drift is None:
        drift = sorted(main_changed & gate_files) if cmp_.get("complete") else []    # unreadable: C2:compare_unreadable already blocks
    if drift:
        e["gate_stale"] = sorted(drift)
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
    e["thin"]["ai"] = ai_authored(pr, commits, cc, e["author"])                   # section 0.2i: never merged unreviewed
    e["thin"]["claude"] = claude_receipt(head, comments if rc else None)          # review route (b)
    e["thin"]["claude_written"] = claude_written(pr, commits, cc)
    e["thin"]["data_route"] = decision_v1.data_route(pr, files, fc, commits, cc, ctx.get("allowlist"))[0]   # addendum c: route (c) scope
    e["thin"]["p01_named"] = p01_named(comments if rc else None, reviews if rc else None, (data.get("inline") or []) if rc else None)   # route (c): PARK on a P0/P1 anybody wrote
    e["writer"] = concurrent_writer(commits, cc, comments, head, ctx["now"], ctx["quiet_minutes"]) if rc else "comments_unreadable"
    cx = codex_review(head, pr, commits, cc, comments, reviews, data.get("inline") or [], rc, ctx["now"], ctx["budgets"]["codex_silent_hours"])
    if e["author"].get("codex") and cx.get("status") == "FINAL":
        cx = {"status": "INADMISSIBLE", "why": "codex_authored_head"}
    threads = data.get("threads")
    p01 = None if threads is None else sum(1 for t in threads if not t.get("resolved") and re.search(r"(?i)\bP[01]\b", t.get("first_body") or ""))
    e["review"] = {"codex": cx, "changes_requested": changes_requested(reviews) if rc else None,
                   "unresolved_p0p1": p01 if p01 is not None else "NOT_PROVEN", "claude": "S1_READS_BRIDGE"}
    e["item"] = newest_item(comments) if rc else None
    try:                                                         # the owner route of rule 2c is announced once per head
        e["owner_update_noted"] = bool(e["item"] and e["item"].pop("owner_update", False) and cc
                                       and stamp(e["item"].pop("at", None)) > head_commit_time(commits, head))
    except (ValueError, KeyError, TypeError):
        e["owner_update_noted"] = False
    if e["item"]:
        e["item"].pop("owner_update", None)
        e["item"].pop("at", None)
    # ONE REQUEST PER HEAD (EVIDENCE_BINDINGS B2): an address request posted at this head, answered or not, is the only one
    try:
        e["address_at_head"] = (not rc or not cc) or any(
            not codex_finality.is_codex(c) and ADDRESS_RE.search(str(c.get("body") or "")) and stamp(c["created_at"]) > head_commit_time(commits, head)
            for c in comments)
    except (ValueError, KeyError, TypeError):
        e["address_at_head"] = True
    # shrinking files the automatic exclusion 7 does not decide: S1 judges them (TICK F2)
    e["shrinks"] = [[f.get("filename"), f.get("additions") or 0, f.get("deletions") or 0] for f in files
                    if f.get("status") not in ("added", "removed", "renamed") and not str(f.get("filename") or "").startswith(("scripts/", "tests/"))
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
    if e.get("gate_stale"):
        gate("C3:gate_drift")                                    # an old green result never proves the current gate
    if e["review"]["changes_requested"] is not False:
        gate("C5:changes_requested" if e["review"]["changes_requested"] else "C5:reviews_unreadable")
    if p01 != 0:
        gate("C6:unresolved_p0p1" if p01 else "C6:threads_unreadable")
    return e


# ----------------------------------------------------------------------------------------------- ranking
def owner_update_route(e):
    """Rule 2c, owner route: the reason this branch must take main while S1 is not the one to do it, else None.
    gate_stale: main changed a privacy- or CI-gate file after this head's privacy-scan run. Whatever that run said, it
    does not prove the current gate, and no code fix on the branch can change that: the branch must take main so the
    current gate runs. ci_missing (S1 v3.3 W5): a required job never ran on this head (for example a PR opened by a
    workflow, whose runs wait for approval with no job), the PR is behind main, main changed none of its files, and
    S1 has no branch-update route (S1_BRANCH_UPDATE_ROUTE). S1 cannot update a branch; the owner or ChatGPT does."""
    if e.get("skip") or (e.get("behind") or 0) <= 0:
        return None
    if e.get("gate_stale"):
        return "gate_stale"
    if S1_BRANCH_UPDATE_ROUTE == "OWNER" and (e.get("ci") or {}).get("state") == "MISSING" and e.get("main_overlap") == [] \
            and not any(g.startswith("C1:") for g in e.get("open") or []):
        return "ci_missing"
    return None


def claude_slots(entries, lane):
    """Every PR for which an exact-head CLAUDE_REVIEW_v1 APPROVE would be the review (the brief cannot read the private
    Bridge; S1 reads Bridge #173 once per tick and matches these heads). ready: no open gate and the lane is ON, so
    the approval makes the PR a rule 4 candidate; not ready: the approval only means no review request is posted.
    high_evidence is the same flag a MERGE entry carries (risk floor above MEDIUM: S1 proves HIGH EVIDENCE itself)."""
    out = []
    for e in entries:
        if e.get("skip") or e["ci"]["state"] != "GREEN" or e["review"]["codex"]["status"] in ("FINAL", "FINDINGS") \
                or any(g.startswith("C1:") for g in e["open"]):
            continue
        out.append({"pr": e["n"], "head": e["head"], "ready": not e["open"] and lane["state"] == "ON",
                    "high_evidence": e["lane"]["risk_floor"] not in FAST_RISKS})
    return out


def next_actions(entries, lane, health, intents, codex_ok=True, max_n=6, c1b_halt=None, fence_merges=False):
    """The ranked list. Entry 0 is THE one next ladder action; the rest are fallbacks if S1's native re-read fails.
    Order: the C1b halt (B.c1b.halt), the C7 halt trigger, RECONCILE signal, rule 4 (review proven by the brief), rule 4
    (review on the Bridge, S1 reads it), rule 2, rule 3. Inside a class: fewest open gates, then the lowest PR number
    (ACTION_LOOP CANDIDATE ORDER). A C1b halt is never the brief's own halt: S1 re-reads the commit, its parent and
    both trees natively and only then posts the S1_LANE_HALTED of C1b."""
    out = []
    if c1b_halt_ok(c1b_halt):
        out.append({"action": "HALT", "rule": "C1b", "source": "C1B", "commit": c1b_halt["commit"], "parent": c1b_halt["parent"],
                    "entries": list(c1b_halt["entries"]), "verify": ["commit", "parent", "trees"],
                    "why": "a commit on main that is not a squash merge changed scripts, tests, .github, .agents or 00_FMOS"})
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
                other = review_request_kind(e, codex_ok)
                merge_b.append((key, dict(base, action="MERGE_IF_CLAUDE_APPROVE", rule="4", review="CLAUDE_REVIEW_v1 on Bridge #173",
                                           risk_floor=e["lane"]["risk_floor"], high_evidence=high, otherwise=other,
                                           verify=["head", "checks", "claude_review", "lane_pins", "rulesets", "halts"] + (["high_evidence"] if high else []))))
                continue
        if any(g.startswith("C1:") for g in gates):
            continue                                            # H7: never write to a branch another writer works on
        route = owner_update_route(e)
        if route:                                                # no code fix helps and Codex is not the route
            if not e.get("owner_update_noted"):
                detail = {"gate_stale": e["gate_stale"][:3]} if route == "gate_stale" else \
                    {"missing": sorted(k for k, t in e["ci"]["tuples"].items() if t["s"] == "MISSING")}
                repair.append((key, dict(base, action="REPAIR", rule="2c", how="BRANCH_UPDATE", by="OWNER", reason=route,
                                         verify=["head", "no_owner_update_item"], **detail)))
            continue
        gated = not e["lane"]["eligible"]                        # rule 2: for an OWNER_GATED PR S1 does (c) only
        # one "@codex address" per head, however it was answered; and none at all while Codex is out of quota (the
        # single request of this head would be spent on a Codex that cannot answer)
        asked = e.get("address_at_head", True) or not codex_ok
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
            kind = review_request_kind(e, codex_ok)
            if kind and cx["status"] != "FINAL" and (lane["state"] != "ON" or gates):
                review.append((key, dict(base, action="REQUEST_REVIEW", rule="3", how=kind, verify=["head", "no_request_for_head"])))
    for group in (merge_a, merge_b, repair, review):
        out += [x for _k, x in sorted(group, key=lambda kx: kx[0])]
    if fence_merges:
        # fix round 7 (R6-SH3): the C1b fence removes merge entries BEFORE the rank and the cut, so the legal non-merge
        # actions (HALT, RECONCILE, REPAIR, REQUEST_REVIEW) surface instead of being cut behind fenced merges
        out = [x for x in out if x.get("action") not in MERGE_ACTIONS]
    for rank, x in enumerate(out[:max_n], 1):
        x["rank"] = rank
    return out[:max_n]


MAX_BUILDS = 999                      # B.next[].builds stops counting here


def entry_key(x):
    """What makes two B.next entries of two briefs the same piece of work: the action and how it is done, on the same
    PR head (or commit, or run, or intents). A new head is new work."""
    if not isinstance(x, dict):
        return None
    what = x.get("pr") if x.get("pr") is not None else x.get("commit") or x.get("run") or ",".join(str(i) for i in x.get("intents") or [])
    return f"{x.get('action')}:{x.get('how') or x.get('rule') or '-'}:{what}:{str(x.get('head') or '-')[:12]}"


def next_builds(brief):
    """{entry_key: builds} of a published brief's B.next (S1 v3.3 W5). A counter only: never an anchor, never authority."""
    out = {}
    for x in ((brief.get("ranked") or brief.get("next") or []) if isinstance(brief, dict) else []):
        key, n = entry_key(x), x.get("builds") if isinstance(x, dict) else None
        if key:
            out[key] = int(n) if isinstance(n, int) and 0 < n <= MAX_BUILDS else 1      # JSON true is 1, as a missing count is
    return out


def count_builds(entries, previous):
    """B.next[].builds: in how many briefs in a row this entry has been ranked, this one included (1: new in this
    brief). The owner, the daily summary and the acceptance record read it: an entry S1 can take alone that stays ranked
    brief after brief is work S1 did not do. S1 itself never reads it. `previous` is next_builds() of the brief this
    build read as its predecessor ({} when it read none: the count restarts at 1, never higher than the truth)."""
    for x in entries:
        x["builds"] = min((previous or {}).get(entry_key(x), 0) + 1, MAX_BUILDS)
    return entries


def review_request_kind(e, codex_ok=True):
    """Rule 3: (i) '@codex review' once per head when Codex may review it; (ii) the Bridge request when Codex is
    inadmissible, unavailable or silent past its budget. None while a Codex request is still inside its budget.
    codex_ok false (Codex is known to be out of quota): never a Codex request, and no waiting for one."""
    cx = e["review"]["codex"]
    if cx["status"] == "FINAL":
        return None
    if e["author"].get("codex") or cx["status"] in ("UNAVAILABLE", "SILENT", "INADMISSIBLE", "FINDINGS") or not codex_ok:
        return "BRIDGE_REQUEST"
    if cx["status"] == "NONE" and not cx.get("requested_after_head"):
        return "CODEX_REVIEW"
    return None


# ----------------------------------------------------------------------------------------------- owner lines
CPH = ZoneInfo("Europe/Copenhagen")


def status_lines(entries, lane, merges, now, c1b=None):
    """The three STATUS LINES of OWNER_VISIBILITY.md as far as the brief can state them. What it cannot prove
    (the WAITING_ONLY_FOR_OWNER set needs the review and HIGH EVIDENCE) is written UNKNOWN, never guessed. `c1b` is
    B.c1b: its gap (history the C1b halt test never scanned) is an owner entry, C1B_GAP(window=<n>)."""
    first = []
    for r in lane["off_reasons"]:
        first.append("LANE_OFF(" + (r if r.startswith(("halt", "pins:")) else "switch" if r == "switch" else "main_health" if r.startswith("main_health") else r) + ")")
    gated = [e for e in entries if not e.get("skip") and not e["lane"]["eligible"]]
    forks = [e for e in entries if e.get("skip") == "B1:fork_head"]
    if any(e["ci"]["state"] == "GREEN" for e in gated):
        first.append("UNKNOWN (waiting_set_needs_review_and_high_evidence)")
    update = [e["n"] for e in entries if owner_update_route(e)]
    if update:
        first.append("BRANCH_UPDATE(" + " ".join(f"#{n}" for n in update) + ")")
    gap = (c1b or {}).get("gap")
    if isinstance(gap, dict) and gap.get("from_unknown") is True:    # W5: history the C1b test never scanned
        first.append(f"C1B_GAP(window={gap.get('window')})")
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


def of_this_task(body):
    """The ACTION_LOOP WORK RULE idiom for a post of this task: the task id, or a contract=<8> line."""
    return TASK_ID in str(body or "") or CONTRACT_ANY.search(str(body or "")) is not None


def heartbeats(comments):
    """The S1_HEARTBEAT_v1 posts of #1156 exactly as TICK T3H counts them for its de-duplication (W5: T3H relies on
    B.ledger.last_heartbeat_at, so both must agree): by the owner account, first token S1_HEARTBEAT_v1, of this task.
    An EDITED heartbeat still counts, as in T3H (it was posted; ignoring it would post a second one the same day); a
    heartbeat-shaped post of another thread never does."""
    return [c for c in comments if is_s1_author(c) and c.get("created_at")
            and first_line_token(c.get("body")) == "S1_HEARTBEAT_v1" and of_this_task(c.get("body"))]


def s1_actions(comments):
    """The authentic receipts of an S1 action on #1156, as (created_at, action word, comment id), oldest first. A
    named receipt of S1_ACTION_RECEIPTS, or a short receipt whose `action` field is one of S1_ACTION_WORDS; owner
    account, never edited, with a contract=<8> line. A heartbeat, an intent and an S1_ITEM_v1 are not actions."""
    out = []
    for c in comments:
        if not is_s1_unedited(c) or not CONTRACT_ANY.search(str(c.get("body") or "")):
            continue
        token = first_line_token(c.get("body"))
        word = S1_ACTION_RECEIPTS.get(token)
        if word is None and token in S1_ACTION_WORDS:
            word = token
        if word is None:
            action = str(fields(c.get("body")).get("action") or "").strip().upper()
            word = action if action in S1_ACTION_WORDS else None
        if word is None:
            continue
        try:
            out.append((stamp(c["created_at"]), word, c["id"]))
        except (ValueError, KeyError):
            continue
    return sorted(out, key=lambda r: (r[0], r[2]))


def heartbeat_due(comments, now):
    """ACTION_LOOP HEARTBEAT: one S1_HEARTBEAT_v1 per Copenhagen day, from the first tick at or after 08:45."""
    local = now.astimezone(CPH)
    if (local.hour, local.minute) < (8, 45):
        return False
    return not any(stamp(c["created_at"]).astimezone(CPH).date() == local.date() for c in heartbeats(comments))


def ledger_hint(comments, intents, ledger_ok, now=None):
    """B.ledger (S1 v3.3 W2b, D4), HINT ONLY: the newest heartbeat and the open intents, from the #1156 comments this
    build already read. S1 never acts on it: F5 still reads the newest comments; this fills the heartbeat's fields
    without guesswork, and TICK T3H reads #1156 only for the minutes after ledger_read_at. W5: last_action is the
    newest authentic S1 action receipt (word, time, comment id; null: the ledger holds none) and actions_24h counts
    them over the 24 hours before `now`. A run that ended NOOP writes nothing, so the ledger never proves ticks_24h.
    An unread ledger is read=false and states nothing (count null)."""
    if not ledger_ok:
        return {"read": False, "last_heartbeat_at": None, "open_intents": {"count": None, "ids": []},
                "last_action": None, "actions_24h": None}
    actions = s1_actions(comments)
    last = {"at": iso(actions[-1][0]), "action": actions[-1][1], "id": actions[-1][2]} if actions else None
    recent = None if now is None else sum(1 for at, _w, _i in actions if timedelta(0) <= now - at <= timedelta(hours=24))
    newest = None
    for c in heartbeats(comments):
        try:
            at = stamp(c["created_at"])
        except (ValueError, KeyError):
            continue
        if newest is None or at > newest:
            newest = at
    return {"read": True, "last_heartbeat_at": iso(newest) if newest else None,
            "open_intents": {"count": len(intents), "ids": [i["id"] for i in intents][:10]},
            "last_action": last, "actions_24h": recent}


# ----------------------------------------------------------------------------------------------- C1b (producer)
class C1bFail(Exception):
    """The C1b part cannot finish: B.c1b is published with the carried anchor and the brief is complete=false with
    the reason C1b:<why>. Never a partial range that reads as checked."""

    def __init__(self, why):
        super().__init__(why)
        self.why = why


def c1b_subject(row):
    return str(((row or {}).get("commit") or {}).get("message") or "").split("\n", 1)[0]


def c1b_parents(row):
    return [p.get("sha") for p in (row or {}).get("parents") or [] if isinstance(p, dict) and isinstance(p.get("sha"), str)]


def c1b_tree_key(row, sha):
    """What GET /git/trees/<key> is read with: the commit's root tree SHA when the commit list states it (two commits
    with one root tree then cost one read), else the commit SHA itself (GitHub resolves a commit to its tree)."""
    tree = (((row or {}).get("commit") or {}).get("tree") or {}).get("sha")
    return tree if isinstance(tree, str) and SHA40.fullmatch(tree) else sha


def c1b_entries(doc):
    """The scripts, tests, .github, .agents and 00_FMOS entries of ONE non-recursive root tree, as "<type>:<sha>" (a
    missing name is None). Anything that is not a complete tree listing raises C1bFail("tree_read")."""
    if not isinstance(doc, dict) or doc.get("truncated") or not isinstance(doc.get("tree"), list):
        raise C1bFail("tree_read")
    rows = {e.get("path"): f"{e.get('type')}:{e.get('sha')}" for e in doc["tree"] if isinstance(e, dict)}
    return tuple(rows.get(d) for d in T3_TREE_DIRS)


def c1b_walk(main_sha, commits, known, window=C1B_WINDOW):
    """main's first-parent chain back from main_sha, by parents[0], until a known point (checked by an earlier brief).
    Returns (chain oldest first as (sha, parents, subject, tree_key), base sha, reached). Not reached: the chain stops
    at `window` commits, at a commit the page does not hold, or at a root commit; `base` is then where it stopped."""
    by_sha = {c.get("sha"): c for c in commits if isinstance(c, dict)}
    chain, cur, reached = [], main_sha, False
    while True:
        if cur in known:
            reached = True
            break
        row = by_sha.get(cur)
        parents = c1b_parents(row)
        if len(chain) >= window or row is None or not parents:
            break
        chain.append((cur, parents, c1b_subject(row), c1b_tree_key(row, cur)))
        cur = parents[0]
    chain.reverse()
    return chain, cur, reached


def c1b_scan(chain, base, base_key, entries_of, search_reads=C1B_SEARCH_READS, unproven=None, progress=None):
    """TICK T3 C1b on a first-parent chain (oldest first): segments from the base to the parent of the first squash
    merge, from each squash merge to the parent of the next, and from the last squash merge to the end (no squash
    merge: base to end). A segment whose start and end entries differ was changed by a commit that is not a squash
    merge: the first commit of that segment whose entries differ from its parent's is the halt, with parent its
    parents[0]. Past `search_reads` tree reads in the segment the halt names the segment's last commit and, as its
    parent, the segment's START (capped: S1's HALT step compares the trees of parent and commit, and those two are
    the pair proven to differ). Returns None or {commit, parent, entries, capped}.

    Fix round 6 (#173/7194396829 S5, F1): `progress` (a dict) records how far the step-by-step proof got WHILE the scan
    runs: progress["proven"] is the largest chain index k such that every commit chain[0..k] is proven (a squash merge,
    a commit whose entries equal its parent's, or the halt commit itself), -1 for none. A read that fails or a budget
    that runs out mid-scan leaves it where the proof stopped. It never moves past a capped (unproven) segment or an
    unread commit, even when a later segment is read and proven."""
    progress = progress if progress is not None else {}
    progress["proven"] = -1
    keys = [base_key] + [c[3] for c in chain]                   # keys[k] is the tree of chain[k]'s first parent
    squash = [k for k, (_s, parents, subject, _t) in enumerate(chain) if len(parents) == 1 and SQUASH_SUBJECT.search(subject)]
    segments, anchor, start = [], (base, base_key), 0            # anchor: (commit sha, tree key) of the segment start
    for k in squash:
        segments.append((anchor, list(range(start, k)), k))     # k: the squash merge that ends this segment
        anchor, start = (chain[k][0], chain[k][3]), k + 1
    segments.append((anchor, list(range(start, len(chain))), None))
    differ = lambda a, b: [d for d, x, y in zip(T3_TREE_DIRS, a, b) if x != y]
    contiguous = True                                           # every commit before the current one is proven
    for (anchor_sha, anchor_key), idx, after in segments:
        if idx:
            # ChatGPT audit A24: equal START and END entries no longer skip a segment. A code change that a later commit of
            # the same segment undid (A -> B -> A) was on main in between, so the first `search_reads` commits of every
            # segment are read one by one. Past that cap a segment with equal ends is still not proven clean (stated limit).
            same_ends = entries_of(anchor_key) == entries_of(chain[idx[-1]][3])
            for n, k in enumerate(idx):
                if n >= search_reads and same_ends:
                    # fix round 4 (#7 / 7186140947-08): past the cap a segment with equal ends is UNPROVEN, never clean. It is
                    # recorded (the caller keeps checked_through at the proven point, and the decision merges nothing)
                    if unproven is not None:                     # fix round 5 (P1-07): and where the proof stopped
                        unproven.append({"from": anchor_sha, "to": chain[idx[-1]][0], "unread": len(idx) - n, "proven": chain[idx[n - 1]][0]})
                    contiguous = False                           # fix round 6 (S5): the proof stops here for good in this scan
                    break
                if n >= search_reads:
                    last = chain[idx[-1]]
                    if contiguous:
                        progress["proven"] = idx[-1]             # the halt covers its segment: the next scan starts after it
                    return {"commit": last[0], "parent": anchor_sha, "entries": differ(entries_of(anchor_key), entries_of(last[3])), "capped": True}
                sha, parents, _subject, key = chain[k]
                names = differ(entries_of(keys[k]), entries_of(key))
                if names:
                    if contiguous:
                        progress["proven"] = k
                    return {"commit": sha, "parent": parents[0], "entries": names, "capped": False}
                if contiguous:
                    progress["proven"] = k
        if after is not None and contiguous:
            progress["proven"] = after                          # a squash merge may change code (TICK T3)
    return None


def c1b_halt_ok(halt):
    return isinstance(halt, dict) and isinstance(halt.get("commit"), str) and SHA40.fullmatch(halt["commit"]) is not None \
        and isinstance(halt.get("parent"), str) and SHA40.fullmatch(halt["parent"]) is not None \
        and isinstance(halt.get("entries"), list) and all(e in T3_TREE_DIRS for e in halt["entries"])


def previous_brief(issues):
    """The published brief of the one label read: (issue, brief) or (None, why). Same issue rules as TICK T1."""
    if not isinstance(issues, list):
        return None, "issues_unreadable"
    rows = [i for i in issues if isinstance(i, dict) and "pull_request" not in i]
    if len(rows) != 1:
        return None, f"issues={len(rows)}"
    if not is_actions_bot(rows[0].get("user")):
        return None, "author"
    brief = parse_body(rows[0].get("body"))
    return (rows[0], brief) if brief is not None else (None, "body")


ANCHOR_WAITS = (10, 20, 30)            # fix round 7: seconds between re-reads of a predecessor run that has not completed yet
def _sleep(seconds):
    time.sleep(seconds)                 # through the module attribute: a test that replaces time.sleep replaces this too


def brief_tuple(issue):
    """Fix round 7 (R6-SH2): the EXACT identity of one published brief issue: issue number, run id, run attempt, the
    sha256 of the exact brief block bytes, and the brief generation (0 for a brief from before fix round 7). publish()
    replaces the published brief only when the new brief carried exactly this tuple. None when it does not parse."""
    brief = parse_body((issue or {}).get("body")) if isinstance(issue, dict) else None
    if brief is None or not _is_id(issue.get("number")):
        return None
    gen = brief.get("generation", 0)
    return {"issue": issue["number"], "run_id": brief["run_id"], "run_attempt": brief["run_attempt"],
            "sha256": brief_digest(issue.get("body")), "generation": gen if type(gen) is int and gen >= 0 else -1}


TUPLE_KEYS = ("issue", "run_id", "run_attempt", "sha256", "generation")


def tuple_ok(t):
    return isinstance(t, dict) and _is_id(t.get("issue")) and _is_id(t.get("run_id")) and _is_id(t.get("run_attempt")) \
        and isinstance(t.get("sha256"), str) and re.fullmatch(r"[0-9a-f]{64}", t["sha256"]) is not None \
        and type(t.get("generation")) is int and t["generation"] >= 0


def duplicate_briefs(issues):
    """Fix round 7 (R6-SH2): more than one labelled Actions-bot issue whose body parses: [(issue, brief)] by number,
    else []. Their gaps are ALL carried (conservatively) and publish() closes an extra one only once every gap and halt
    of it is proven in the surviving brief."""
    if not isinstance(issues, list):
        return []
    rows = sorted((i for i in issues if isinstance(i, dict) and "pull_request" not in i and is_actions_bot(i.get("user"))
                   and _is_id(i.get("number"))), key=lambda i: i["number"])
    if len(rows) < 2 or len(rows) != len([i for i in issues if isinstance(i, dict) and "pull_request" not in i]):
        return []
    pairs = [(i, parse_body(i.get("body"))) for i in rows]
    return pairs if all(b is not None for _i, b in pairs) else []


def carried_halt(issues):
    """The c1b.halt of a published brief body even when its run binding fails (F2): run_not_success, edited_outside_run
    or an unreadable run. Bot authorship is the floor (the T1 author rule): a body not written by github-actions[bot]
    is never read, because HALT rule C1b compares the entry's parent with its commit and a forged parent (an old
    ancestor) could make S1 post a false S1_LANE_HALTED. Never used for the anchor. The first labelled bot issue whose
    body parses and carries a valid halt."""
    if not isinstance(issues, list):
        return None
    # fix round 8: in the issue-number order publish() and duplicate_briefs() use (the canonical issue first). A string
    # order put issue 10000 before 9999, so the canonical issue's halt was replaced by the extra's and then lost
    for i in sorted((i for i in issues if isinstance(i, dict) and "pull_request" not in i and is_actions_bot(i.get("user"))),
                    key=lambda i: (0, i["number"], "") if _is_id(i.get("number")) else (1, 0, str(i.get("number")))):
        c = (parse_body(i.get("body")) or {}).get("c1b")
        if isinstance(c, dict) and c1b_halt_ok(c.get("halt")):
            return c["halt"]
    return None


def previous_anchor(issue, brief, run, now):
    """The checked point the previous brief proves: (known, halt, why). The brief counts only when its run is a run of
    this workflow on main at brief.main, successful when completed, whose window holds generated_at, and the issue was
    not edited after that run (TICK T2 edited_outside_run). known is [c1b.checked_through] when the brief has a c1b
    block (null there: nothing known), else [brief.main] (a brief from before W2b, which has no c1b block). The halt
    returned here is the bound one; read_c1b carries the previous halt even when the binding fails (carried_halt)."""
    try:
        made, edited = stamp(brief.get("generated_at")), stamp(issue.get("updated_at"))
        if not isinstance(run, dict) or run.get("id") != brief.get("run_id") or run.get("path") != WORKFLOW_PATH \
                or (run.get("repository") or {}).get("full_name") != REPO or run.get("head_branch") != "main" \
                or (run.get("head_repository") or {}).get("full_name") != REPO \
                or run.get("head_sha") != brief.get("main") or run.get("run_attempt") != brief.get("run_attempt") \
                or run.get("event") not in RUN_EVENTS or run.get("event") != brief.get("event"):
            return [], None, "run_binding"
        # fix round 7 (R6-SH2): only a COMPLETED, successful run anchors (read_c1b re-reads an in-progress one first)
        if run.get("status") != "completed":
            return [], None, "run_in_progress"
        if run.get("conclusion") != "success":
            return [], None, "run_not_success"
        end = stamp(run.get("updated_at"))
        if not stamp(run.get("run_started_at")) <= made <= edited <= end:
            return [], None, "edited_outside_run"
    except (ValueError, TypeError, AttributeError):
        return [], None, "timestamps"
    if "c1b" not in brief:
        return [brief["main"]], None, None
    c = brief.get("c1b") if isinstance(brief.get("c1b"), dict) else {}
    point = _sha_or_none(c.get("checked_through"))
    return ([point] if point else []), (c.get("halt") if c1b_halt_ok(c.get("halt")) else None), (None if point else "no_checked_through")


GAP_ACCEPTED = "S1_C1B_GAP_ACCEPTED_v1"   # the owner's explicit disposition of ONE carried history gap (fix round 5)
GAP_KEYS = ("id", "kind", "from", "to", "from_unknown", "reason", "window", "detected_at", "state")
GAP_UNBOUNDED = ("", "-", "unbounded")    # the `from:` of an acceptance of a gap with no known start


# Fix round 6 (#173/7194141485 S1, S2; #173/7194396829 S5; ChatGPT kit b6c810a1): the C1b history ledger.
#   checked_through  the scan frontier: every first-parent commit up to it was proven by a scan (a squash merge, a commit
#                    whose entries equal its parent's, or a halt) OR lies in one of the listed gaps. It only ever stops at
#                    the contiguous proven point: never past a capped segment, an unread commit, a budget stop or a halt.
#   open             this build's own unproven rest, (checked_through, B.main]: resumed by the next build from
#                    checked_through (automatic, no state beyond the anchor; the next scan covers it exactly once).
#   gaps             EVERY range no scan can prove (history before the window when the anchor was lost or not reached),
#                    one item per range, each with its exact from/to, reason and detection time. Carried by every brief.
#                    A gap leaves the ledger only by an exact owner disposition (gap_acceptance); a read failure never
#                    removes, shrinks or merges one. prev names the brief this build carried them from: publish()
#                    replaces the published brief only with a brief that carried exactly that one.
def c1b_gap(frm, to, reason, window, detected_at):
    return {"id": f"{frm or '-'}..{to}", "kind": "RANGE", "from": frm, "to": to, "from_unknown": True,
            "reason": str(reason)[:80], "window": window, "detected_at": detected_at, "state": "UNVERIFIED"}


def gap_ok(g):
    """Is this one well-formed gap item (as c1b_gap writes it)?"""
    try:
        return isinstance(g, dict) and set(g) == set(GAP_KEYS) and g["kind"] == "RANGE" and g["from_unknown"] is True \
            and isinstance(g["to"], str) and SHA40.fullmatch(g["to"]) is not None \
            and (g["from"] is None or (isinstance(g["from"], str) and SHA40.fullmatch(g["from"]) is not None)) \
            and g["id"] == f"{g['from'] or '-'}..{g['to']}" and isinstance(g["reason"], str) and type(g["window"]) is int \
            and g["state"] == "UNVERIFIED" and isinstance(stamp(g["detected_at"]), datetime)
    except (ValueError, TypeError, AttributeError):
        return False


def gap_detection(g):
    """Fix round 8 (R7-SH1): the exact identity of ONE detection of ONE gap: its range id AND its detection time (the
    pair gap_action_id hashes). Two items with the same range and another detected_at are two detections."""
    return (g["id"], g["detected_at"])


def add_gap(gaps, g, exact=False):
    """A NEW detection of this build (exact False): one item per range, a range already in the ledger keeps its first
    unresolved item and its detection time (a range found again every tick is not a new gap each tick). Carrying items
    of published briefs (exact True, fix round 8, R7-SH1): one item per exact detection, so two detections of one range
    from two issue histories are never coalesced (each keeps its own action id and needs its own owner disposition)."""
    key = gap_detection if exact else (lambda x: x["id"])
    if not any(key(x) == key(g) for x in gaps):
        gaps.append(g)


def carried_gaps(prev, now):
    """EVERY history gap of the previous brief, one by one. A gap item that does not validate, a gaps field that is not a
    list, and the single gap of a brief from before this ledger (B.c1b.gap, fix round 5) are carried conservatively: as
    an UNBOUNDED gap (no known start) to the commit they name, else to that brief's main, detected when that brief was
    made. A capped segment of a fix round 5 brief is not a gap: its scan resumes from checked_through."""
    c = prev.get("c1b") if isinstance(prev, dict) and isinstance(prev.get("c1b"), dict) else {}
    try:
        made = iso(stamp(prev.get("generated_at")))
    except (ValueError, TypeError, AttributeError):
        made = iso(now)
    fallback = _sha_or_none(prev.get("main")) if isinstance(prev, dict) else None
    out = []

    def unbounded(item, reason):
        to = (_sha_or_none(item.get("to")) if isinstance(item, dict) else None) or fallback
        if to is None:
            raise C1bFail("gaps_unreadable")                    # nothing to name: this build carries nothing (publish keeps the old brief)
        add_gap(out, c1b_gap(None, to, reason, C1B_WINDOW, made), exact=True)

    if "gaps" in c:
        for g in c["gaps"] if isinstance(c["gaps"], list) else [None]:
            if gap_ok(g):
                add_gap(out, {k: g[k] for k in GAP_KEYS}, exact=True)   # fix round 8: by exact detection, never by range
            else:
                unbounded(g, "C1b:gap_unreadable")
    else:
        legacy = c.get("gap")
        if isinstance(legacy, dict) and legacy.get("from_unknown") is True \
                and not str(legacy.get("reason") or "").startswith("C1b:capped_equal_ends"):
            unbounded(legacy, str(legacy.get("reason") or "C1b:range"))
    return out


def cleared_record(gap, cid):
    """Fix round 8 (R7-SH1): B.c1b.cleared item of ONE owner disposition: the range id, the exact detection (its
    detected_at and gap_action_id) and the acceptance comment id. preserved() counts only such a complete record."""
    return {"id": gap["id"], "detected_at": gap["detected_at"], "gap": gap_action_id(gap), "by": f"owner:{cid}", "comment": cid}


def cleared_ok(x):
    """Is this a complete fix-round-8 cleared record? A legacy record (range id and by only) is ambiguous: it names no
    detection, so it never counts as the disposition of any detection (fail closed)."""
    return isinstance(x, dict) and isinstance(x.get("id"), str) and isinstance(x.get("detected_at"), str) \
        and isinstance(x.get("gap"), str) and _is_id(x.get("comment")) and x.get("by") == f"owner:{x['comment']}" \
        and x["gap"] == gap_action_id(x)


def gap_action_id(gap):
    """Fix round 7 (R6-SH4, owner addendum g): the stable action id of ONE detection of ONE gap: the range id AND its
    detection time (a range found again later is a new detection with a new id). C1B- and 12 hex."""
    return "C1B-" + hashlib.sha256(f"{gap['id']}|{gap['detected_at']}".encode("utf-8")).hexdigest()[:12]


def gap_accept_body(gap):
    """The exact never-edited comment the owner account posts on #1156 to dispose of this gap detection (what ChatGPT
    posts when the owner sends GO <action id>)."""
    return f"{GAP_ACCEPTED}\ngap: {gap_action_id(gap)}\nfrom: {gap['from'] or '-'}\nto: {gap['to']}"


GAP_NATIVE_QUERY = ("query($ids:[ID!]!){nodes(ids:$ids){... on IssueComment{databaseId lastEditedAt includesCreatedEdit "
                    "author{login} issue{number}}}}")
GAP_NATIVE_READS = 20                 # acceptance candidates whose native edit record one build reads (ONE GraphQL call)


def native_edit_ok(row):
    """Fix round 7 (R6-SH4): GitHub's own edit record of this comment (GraphQL IssueComment, attached by collect() as
    row["native_edit"]) proves it was never edited: lastEditedAt null and includesCreatedEdit false, for this positive
    comment id, by the owner account, on #1156. Missing or unreadable: not proven (fail closed). Residual: every agent
    writes as the same owner account, so this proves the comment unedited, not which agent of the owner account wrote it."""
    n = row.get("native_edit") if isinstance(row, dict) else None
    return isinstance(n, dict) and _is_id(row.get("id")) and n.get("databaseId") == row["id"] and n.get("lastEditedAt") is None \
        and "lastEditedAt" in n and n.get("includesCreatedEdit") is False and n.get("author") == OWNER_LOGIN and n.get("issue") == OWNER_ISSUE


def gap_acceptance(gap, ledger):
    """The id of the owner's disposition of exactly this gap detection, or None. Fix round 7 (R6-SH4): an
    S1_C1B_GAP_ACCEPTED_v1 by the owner account on #1156 with a positive comment id, never edited by GitHub's own record
    (native_edit_ok; the REST created_at == updated_at check still applies too), whose fields are each present exactly
    once and name exactly this detection: gap: is gap_action_id(gap) (range AND detection time), to: is the gap's to and
    from: is the gap's from ("-" or "unbounded" only for a gap with no known start), created at or after the gap was
    detected. `ledger` None: unread, nothing is accepted."""
    if ledger is None:
        return None
    for x in ledger:
        if not isinstance(x, dict) or not is_owner_unedited(x) or first_line_token(x.get("body")) != GAP_ACCEPTED \
                or not native_edit_ok(x):
            continue
        keys = [m.group(1).strip().lower() for m in (re.match(r"^\s*(?:[-*]\s+)?([A-Za-z_][A-Za-z0-9_ ]{0,40}?)\s*[:=]\s*(.*?)\s*$", ln)
                                                       for ln in str(x.get("body")).splitlines()) if m]
        if any(keys.count(k) != 1 for k in ("gap", "from", "to")):
            continue                                             # a missing or a repeated field: not exact
        f = fields(x.get("body"))
        to, frm, gid = (f.get("to") or "").strip(), (f.get("from") or "").strip(), (f.get("gap") or "").strip()
        if gid != gap_action_id(gap) or to != gap["to"] or (frm != gap["from"] if gap["from"] else frm.lower() not in GAP_UNBOUNDED):
            continue
        try:
            if stamp(x.get("created_at")) < stamp(gap["detected_at"]):
                continue
        except (ValueError, TypeError):
            continue
        return x["id"]
    return None


def read_gap_native(gh, comments, limit=GAP_NATIVE_READS):
    """Fix round 7 (R6-SH4): attach GitHub's native edit record to the newest `limit` owner S1_C1B_GAP_ACCEPTED_v1
    comments (ONE read-only GraphQL call). A failed read attaches nothing (no acceptance counts)."""
    rows = [c for c in comments or [] if isinstance(c, dict) and login(c) == OWNER_LOGIN and _is_id(c.get("id"))
            and first_line_token(c.get("body")) == GAP_ACCEPTED and isinstance(c.get("node_id"), str)][-limit:]
    if not rows:
        return 0
    doc = gh.graphql(GAP_NATIVE_QUERY, {"ids": [c["node_id"] for c in rows]})
    nodes = ((doc or {}).get("data") or doc or {}).get("nodes") if isinstance(doc, dict) else None
    by_id = {n.get("databaseId"): n for n in nodes or [] if isinstance(n, dict)}
    for c in rows:
        n = by_id.get(c["id"])
        if isinstance(n, dict) and "lastEditedAt" in n:
            c["native_edit"] = {"databaseId": n.get("databaseId"), "lastEditedAt": n.get("lastEditedAt"),
                                "includesCreatedEdit": n.get("includesCreatedEdit"),
                                "author": (n.get("author") or {}).get("login"), "issue": (n.get("issue") or {}).get("number")}
    return len(rows)


def gap_summary(gaps, opn, carried=0):
    """B.c1b.gap as TICK.md v3.3 T3H reads it (c1b_gap=window=<n>) and as main's brief had it: set while any gap or an
    open segment exists. window: the commits it covers (C1B_WINDOW for a range of unknown length)."""
    if gaps:
        return {"from_unknown": True, "window": sum(g["window"] for g in gaps), "reason": gaps[0]["reason"], "to": gaps[0]["to"],
                "carried": carried > 0, "count": len(gaps)}
    if opn:
        return {"from_unknown": True, "window": opn["unread"], "reason": opn["reason"], "to": opn["to"], "carried": False, "count": 0}
    return None


def c1b_frontier(out, chain, base, progress, reason):
    """checked_through at the contiguous proven point of this scan, and the open rest (checked_through, B.main]."""
    p = progress.get("proven", -1) if isinstance(progress, dict) else -1
    ct = chain[p][0] if p >= 0 else base
    out["checked_through"] = ct
    out["open"] = None if ct == chain[-1][0] else {"from": ct, "to": chain[-1][0], "reason": reason, "unread": len(chain) - 1 - p}


def read_c1b(gh, main_sha, ledger, now, max_calls=C1B_MAX_CALLS):
    """B.c1b (S1 v3.3 W2b, D1): the TICK T3 C1b halt test, run by the producer on main's first-parent history from the
    previous brief's checked_through up to B.main, on its own share of the call budget.

    Fail closed: no usable previous brief, or a checked_through the first-parent walk of the newest C1B_WINDOW commits
    does not reach, scans that window, records the range before it as a gap and is complete=false (C1b:range). An
    unreadable read is complete=false (C1b:<why>); the budget is not (the open segment blocks every merge and the next
    build resumes it). A halt of the previous brief that no S1_LANE_HALTED on #1156 names yet is carried until one does
    (`ledger` None: unread, always carried). Fix round 6: the previous brief's gaps are carried one by one before any
    other read, and B.c1b.prev is set only once the previous brief was read AND its anchor judged: every failure before
    that leaves prev None, and publish() then keeps the published brief.
    Returns {checked_through, from, halt, gap, gaps, open, cleared, prev, carry, complete, reason, stop}."""
    out = {"checked_through": None, "from": None, "halt": None, "gap": None, "gaps": [], "open": None, "cleared": [], "prev": None,
           "carry": None, "complete": False, "reason": None, "stop": None, "carried": 0}
    first = gh.calls
    progress, chain, base, reached, range_reason = {"proven": -1}, None, None, False, None

    def get(path, params=None):
        if gh.calls - first >= max_calls:
            raise C1bFail("budget")
        return gh.get(path, params)

    try:
        try:
            issues = get("issues", {"labels": BRIEF_LABEL, "state": "open", "per_page": 20})
        except (C1bFail, StopReading):
            raise
        except Exception:                                        # noqa: BLE001
            raise C1bFail("issues_unreadable")
        issue, prev = previous_brief(issues)
        known, why = [], prev if issue is None else None
        if why == "issues_unreadable":
            raise C1bFail(why)
        # W5: the previous build could not read ITS predecessor (carry UNKNOWN): whatever it carried is unknown, and so
        # is this build's own carry. Fail closed: no anchor of that brief is used, the window is scanned, the brief is
        # complete=false (C1b:carry_unknown) and the range before the window is a gap.
        carry_unknown = issue is not None and isinstance(prev.get("c1b"), dict) and prev["c1b"].get("carry") == "UNKNOWN"
        out["prev_next"] = next_builds(prev) if issue is not None else {}   # W5: B.next[].builds counts on from here
        out["prev_log"] = prev.get("decision_log") if issue is not None and isinstance(prev.get("decision_log"), list) else None
        dups = duplicate_briefs(issues) if issue is None else []
        if issue is not None or dups:
            # fix round 6 (S1, S2): every gap of the previous brief, carried first and one by one; only an exact owner
            # disposition removes one (the cleared list says which, and by which comment). Fix round 7: with duplicate
            # brief issues, the gaps of EVERY one of them (no anchor is taken from any). Fix round 8 (R7-SH1): the union
            # is by exact detection (range id AND detected_at): the same range detected in two issue histories stays two
            # items, each disposed of only by its own acceptance; the cleared record names the exact detection and the
            # acceptance comment, so no clearance is ever read as another detection's
            carried = []
            for _i, b in (dups or [(issue, prev)]):
                for g in carried_gaps(b, now):
                    add_gap(carried, g, exact=True)
            for g in carried:
                cid = gap_acceptance(g, ledger)
                if cid is None:
                    out["gaps"].append(g)
                else:
                    out["cleared"].append(cleared_record(g, cid))
            out["carried"] = len(out["gaps"])
        prev_halt = carried_halt(issues)                         # F2: carried whatever the binding; never the anchor
        if prev_halt is not None:
            named = ledger is not None and any(prev_halt["commit"] in h["body"] for h in lane_halts(ledger))
            out["halt"] = None if named else prev_halt
        if issue is not None:
            try:
                run = get(f"actions/runs/{int(prev.get('run_id'))}")
            except (C1bFail, StopReading):
                raise
            except Exception:                                    # noqa: BLE001  (unproven: no anchor is carried)
                raise C1bFail("run_unreadable")
            known, _bound_halt, why = previous_anchor(issue, prev, run, now)
            for wait in ANCHOR_WAITS:                            # fix round 7: completion lags the job end by seconds
                if why != "run_in_progress":
                    break
                _sleep(wait)
                try:
                    run = get(f"actions/runs/{int(prev.get('run_id'))}")
                except (C1bFail, StopReading):
                    raise
                except Exception:                                # noqa: BLE001
                    raise C1bFail("run_unreadable")
                known, _bound_halt, why = previous_anchor(issue, prev, run, now)
            if why == "run_in_progress":
                raise C1bFail("anchor_pending")                  # never an anchor, never a replacement (prev stays None)
            if carry_unknown:
                known, why = [], "carry_unknown"
                out["carry"] = "UNKNOWN"                         # until this build's own scan reaches B.main
            out["prev"] = brief_tuple(issue)                     # fix round 7 (R6-SH2): the exact tuple publish() compares
        elif dups:
            out["prev"] = dict(brief_tuple(dups[0][0]), absorbed=[brief_tuple(i) for i, _b in dups[1:]])
        out["checked_through"] = known[0] if known else None    # carried when this build cannot finish
        if main_sha in known:
            out.update(checked_through=main_sha, complete=True)
            out["from"] = main_sha
            return c1b_done(out)
        try:
            commits = get("commits", {"sha": main_sha, "per_page": C1B_WINDOW})
        except (C1bFail, StopReading):
            raise
        except Exception:                                        # noqa: BLE001
            raise C1bFail("commits_unreadable")
        if not isinstance(commits, list):
            raise C1bFail("commits_unreadable")
        # fix round 6 (liveness): a known anchor that the first page does not reach is followed back page by page (at most
        # C1B_PAGES, each read from the commit where the walk stopped), so a backlog or a resumed scan never turns into a
        # gap; the scan of the longer chain is bounded by the budget (an open segment, resumed). No anchor: one page.
        rows, pages, limit = list(commits), 1, C1B_WINDOW * (C1B_PAGES if known else 1)
        while True:
            walked, base, reached = c1b_walk(main_sha, rows, known, limit)
            if reached or not known or pages >= C1B_PAGES or len(walked) >= limit or not walked \
                    or any(isinstance(c, dict) and c.get("sha") == base for c in rows):
                break
            try:
                more = get("commits", {"sha": base, "per_page": C1B_WINDOW})
            except (C1bFail, StopReading):
                raise
            except Exception:                                    # noqa: BLE001  (a transient read: no gap, the next build retries)
                raise C1bFail("commits_unreadable")
            if not isinstance(more, list) or not more:
                raise C1bFail("commits_unreadable")
            rows, pages = rows + more, pages + 1
        commits = rows
        if not walked:
            raise C1bFail("commits_unreadable")                  # B.main itself is not on the page: nothing was scanned
        chain = walked
        out["from"] = base
        if not reached:
            # F3, fix round 6 (S5): the history before the window is a gap of its own (from the anchor when there is one),
            # whatever the scan of the window finds; it is orthogonal to the window's own open segment
            range_reason = "C1b:carry_unknown" if carry_unknown else "C1b:range" + ("" if known else f":no_anchor:{why or 'none'}")
            add_gap(out["gaps"], c1b_gap(known[0] if known else None, base, range_reason, C1B_WINDOW, iso(now)))
            out["carry"] = None                                  # the window is read: this build's own scan is what it carries
        cache = {}

        def entries_of(key):
            if key not in cache:
                try:
                    doc = get(f"git/trees/{key}")
                except (C1bFail, StopReading):
                    raise
                except Exception:                                # noqa: BLE001
                    raise C1bFail("tree_read")
                cache[key] = c1b_entries(doc)
            return cache[key]

        base_row = next((c for c in commits if isinstance(c, dict) and c.get("sha") == base), None)
        unproven = []
        halt = c1b_scan(chain, base, c1b_tree_key(base_row, base), entries_of, unproven=unproven, progress=progress)
        # fix round 7 (R6-SH3, liveness): a segment capped at C1B_SEARCH_READS is resumed IN THIS BUILD from the proven
        # point while the C1b budget lasts (each pass proves up to C1B_SEARCH_READS more commits, or stops at a halt or a
        # budget stop exactly as before), so one build proves about C1B_MAX_CALLS commits, not C1B_SEARCH_READS. A load
        # above that stays an open segment whose unread count the owner line shows (C1B_GAP(window=<unread>)).
        while halt is None and unproven and gh.calls - first < max_calls and 0 <= progress["proven"] < len(chain) - 1:
            p = progress["proven"]
            sub, more, sub_progress = chain[p + 1:], [], {"proven": -1}
            try:
                halt = c1b_scan(sub, chain[p][0], chain[p][3], entries_of, unproven=more, progress=sub_progress)
            finally:
                if sub_progress["proven"] >= 0:
                    progress["proven"] = p + 1 + sub_progress["proven"]
            unproven[:] = more
            if progress["proven"] == p:
                break                                            # no step forward: never loop
        if out["halt"] is None and halt is not None:
            out["halt"] = halt                                   # an older unnamed halt of the previous brief stays first
        elif halt is not None and out["halt"] != halt:
            # fix round 6: a halt this brief cannot carry (an older one is first) is never checkpointed over: the proof
            # stops before it, so the next scan finds it again once the older halt is named
            at = {c[0]: k for k, c in enumerate(chain)}
            progress["proven"] = min(progress["proven"], at.get(halt["parent"], -1))
        # fix round 5 (P1-07), fix round 6 (S5): checked_through stops where the step-by-step proof stopped (a capped
        # segment, a halt), also after the window fallback; the rest of the window is this brief's open segment
        c1b_frontier(out, chain, base, progress, "C1b:halt" if halt is not None else "C1b:capped_equal_ends" if unproven else "C1b:unproven")
        out.update(complete=reached, carry=None, reason=range_reason)
        return c1b_done(out)
    except C1bFail as exc:
        if chain is not None:                                    # fix round 6 (F1): the scan stopped: keep its contiguous proof
            c1b_frontier(out, chain, base, progress, f"C1b:{exc.why}")
        if exc.why == "budget" and chain is not None:
            # the C1b budget is bounded progress, never a stall: the open segment blocks every merge, the next build resumes
            out.update(complete=reached, carry=None, reason=range_reason)
            return c1b_done(out)
        out.update(complete=False, reason=f"C1b:{exc.why}")
        if exc.why == "issues_unreadable":
            # W5: this build never saw the previous brief, so it cannot carry that brief's halt or anchor. It says so:
            # publish() never lets such a brief replace a published one, and the next build fails closed on it.
            out["carry"] = "UNKNOWN"
    except StopReading as exc:
        if chain is not None:
            c1b_frontier(out, chain, base, progress, f"C1b:{exc.reason}")
        out.update(complete=False, reason=f"C1b:{exc.reason}", stop=exc.reason)
    except Exception as exc:                                     # noqa: BLE001
        out.update(complete=False, reason=f"C1b:unreadable:{type(exc).__name__}", prev=None)
    return c1b_done(out)


def c1b_done(out):
    """The summary (B.c1b.gap) and the bound on the ledger: more gaps than C1B_MAX_GAPS is surfaced, never cut."""
    out["gap"] = gap_summary(out["gaps"], out["open"], out.get("carried", 0))
    if len(out["gaps"]) > C1B_MAX_GAPS and out.get("complete"):
        out.update(complete=False, reason="C1b:gaps_overflow")
    return out


def c1b_fence(block):
    """Why the C1b state forbids every merge now (empty: it does not): open gaps, an open segment, an unknown carry."""
    out = []
    if block.get("gaps"):
        out.append(f"gaps={len(block['gaps'])}")
    if isinstance(block.get("open"), dict):
        out.append(f"open:{block['open']['reason']}")
    if block.get("carry") == "UNKNOWN":
        out.append("carry_unknown")
    return out


def c1b_block(snap_c1b, now=None):
    """B.c1b and the brief's C1b incomplete reason (None when complete) from collect()'s record. A record in the shape
    of fix round 5 (one `gap`, no `gaps`) is migrated as carried_gaps() migrates a brief: one unbounded gap."""
    c = snap_c1b if isinstance(snap_c1b, dict) else {}
    raw = c.get("gaps") if isinstance(c.get("gaps"), list) else []
    gaps = [{k: g[k] for k in GAP_KEYS} for g in raw if gap_ok(g)]
    bad = len(gaps) != len(raw) or ("gaps" in c and not isinstance(c.get("gaps"), list))
    legacy = c.get("gap")
    if "gaps" not in c and isinstance(legacy, dict) and legacy.get("from_unknown") is True \
            and not str(legacy.get("reason") or "").startswith("C1b:capped_equal_ends"):
        to = _sha_or_none(legacy.get("to")) or _sha_or_none(c.get("checked_through"))
        if to is None:
            bad = True
        else:
            gaps.append(c1b_gap(None, to, str(legacy.get("reason") or "C1b:range"), C1B_WINDOW, iso(now or datetime.now(timezone.utc))))
    o = c.get("open")
    opn = {"from": o["from"], "to": o["to"], "reason": str(o["reason"])[:60], "unread": o["unread"]} \
        if isinstance(o, dict) and _sha_or_none(o.get("from")) and _sha_or_none(o.get("to")) and type(o.get("unread")) is int and o.get("reason") else None
    bad = bad or (o is not None and opn is None)
    prev = c.get("prev")
    if tuple_ok(prev):
        absorbed = prev.get("absorbed")
        prev = dict({k: prev[k] for k in TUPLE_KEYS},
                    **({"absorbed": [{k: a[k] for k in TUPLE_KEYS} for a in absorbed]} if isinstance(absorbed, list)
                       and all(tuple_ok(a) for a in absorbed) else {}))
        bad = bad or (absorbed is not None and "absorbed" not in prev)
    else:
        bad = bad or prev is not None
        prev = None
    # fix round 8 (R7-SH1): a complete record keeps its exact detection and comment id; anything else keeps only the
    # legacy id/by (which preserved() never counts as a disposition)
    cleared = [{k: x[k] for k in ("id", "detected_at", "gap", "by", "comment")} if cleared_ok(x) else
               {"id": str(x.get("id"))[:90], "by": str(x.get("by"))[:40]}
               for x in (c.get("cleared") or []) if isinstance(x, dict)][:2 * C1B_MAX_GAPS]
    block = {"checked_through": _sha_or_none(c.get("checked_through")), "from": _sha_or_none(c.get("from")),
             "halt": c["halt"] if c1b_halt_ok(c.get("halt")) else None,
             "gap": gap_summary(gaps, opn, c.get("carried") if type(c.get("carried")) is int else 0),   # TICK T3H reads it (heartbeat)
             "gaps": gaps,                                        # fix round 6: the ledger, one item per unproven range
             "open": opn,                                         # fix round 6: this build's unproven rest, resumed next build
             "cleared": cleared,                                  # fix round 6: gaps of the previous brief the owner disposed of
             "prev": prev,                                        # fix round 6: the brief this build carried (publish() checks it)
             "carry": "UNKNOWN" if c.get("carry") == "UNKNOWN" else None}   # W5: this build never read its predecessor
    # fix round 7 (owner addendum g, SHADOW record only): one stable action id per gap detection and the exact reply the
    # owner sends; GO <id> lets ChatGPT post gap_accept_body(gap) as the owner account. No expiry or receipt yet (pre-LIVE)
    block["owner_actions"] = [{"id": gap_action_id(g), "gap": g["id"], "reply": f"GO {gap_action_id(g)}"} for g in gaps]
    block["fence"] = c1b_fence(block)                            # fix round 6 (S4): non-empty: no merge by any lane
    reason = c.get("reason")
    if bad:
        reason = "C1b:record_invalid"
    if c.get("complete") is True and not reason:
        return block, None
    reason = str(reason or "C1b:not_read")
    block["fence"].append("incomplete")                          # and an incomplete C1b part fences too (S1 also stops at T2)
    return block, reason if reason.startswith("C1b:") else "C1b:" + reason


# ----------------------------------------------------------------------------------------------- the verdict (shadow)
def _sha_or_none(value):
    return value if isinstance(value, str) and SHA40.fullmatch(value) else None


def brief_verdict(main_sha, contract, actual, bootstrap_text, pins, trees):
    """B.verdict, SHADOW (S1 v3.3 W2, charter A01/A02): the checks of BOOTSTRAP steps 3 and 3b and of the TICK T2 pins
    clause that the producer can decide at B.main, computed here on their own (not copied from pin_check), plus the
    tree SHAs at B.main that T3 C1b compares. S1 ignores this field until a reviewed TICK change promotes it.

    The producer cannot decide T1 (which issue carries the label, and its author) or T2's run binding (its own run is
    still running), and it cannot decide T3 (M is read by S1 later): those are "S1_DECIDES". The 3b value of the
    owner's saved paste is S1's own independent cross-check; the producer compares with BOOTSTRAP.txt AT B.main only.
    `actual` maps paths to blob SHAs at B.main; `trees` maps "" (the root) and each T3_TREE_DIRS entry to a tree SHA."""
    contract = contract if isinstance(contract, dict) else {}
    actual = actual if isinstance(actual, dict) else {}
    pins = pins if isinstance(pins, dict) else {}
    trees = trees if isinstance(trees, dict) else {}
    blob = lambda path: _sha_or_none(actual.get(path)) if isinstance(path, str) and path else None
    step3, step3b, t2, basis = [], [], [], []
    for key, path_key in (("action_loop_blob", "action_loop_path"), ("tick_blob", "tick_path"), ("lane_switch_blob", "lane_switch_path")):
        want = _sha_or_none(contract.get(key))
        if want is None or blob(contract.get(path_key)) != want:
            step3.append(f"3:{key}")
    rubric = contract.get("rubric_blobs")
    if not isinstance(rubric, dict):                            # D5: missing or not a map is unverifiable, never "none to check"
        step3.append("3:rubric_blobs")
    else:
        for path, want in sorted(rubric.items()):
            if _sha_or_none(want) is None or blob(path) != want:
                step3.append(f"3:rubric:{path}")
    stated = re.search(r"bootstrap_version must be (S1_BOOTSTRAP_v\d+)\.", bootstrap_text or "")
    if not stated or contract.get("bootstrap_version") != stated.group(1):
        step3.append("3:bootstrap_version")
    contract_blob = blob(CONTRACT_FILE)
    pasted = re.search(r"must equal ([0-9a-f]{40})\.", bootstrap_text or "")
    bootstrap_3b = pasted.group(1) if pasted else None
    if contract_blob is None or contract_blob != bootstrap_3b:
        step3b.append("3b:bootstrap_text")
    if pins.get("ok") is not True:
        t2.append("pins:ok")
    if contract_blob is None or pins.get("contract_blob") != contract_blob or pins.get("contract_blob") != bootstrap_3b:
        t2.append("pins:contract_blob")
    for key in ("action_loop_blob", "tick_blob"):
        if _sha_or_none(pins.get(key)) is None or pins.get(key) != contract.get(key):
            t2.append(f"pins:{key}")
    basis_trees = {name: _sha_or_none(trees.get(name)) for name in T3_TREE_DIRS}
    root_tree = _sha_or_none(trees.get(""))
    basis = (["t3_basis:root"] if root_tree is None else []) + [f"t3_basis:{n}" for n, v in basis_trees.items() if v is None]
    source = "SOURCE_UNVERIFIED(3)" if step3 else "SOURCE_UNVERIFIED(3b)" if step3b else "OK"
    return {"schema": VERDICT_SCHEMA, "shadow": True, "main": main_sha, "source": source, "t1": "S1_DECIDES",
            "t2": "BRIEF_UNVERIFIED(pins)" if t2 else "OK", "t2_scope": "pins", "t3": "S1_DECIDES",
            "reasons": (step3 + step3b + t2 + basis)[:16], "contract_blob": contract_blob, "bootstrap_3b": bootstrap_3b,
            "t3_basis": {"root_tree": root_tree, "trees": basis_trees}}


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
    runs = snap.get("executor_runs") if isinstance(snap.get("executor_runs"), dict) else {}
    proofs = snap.get("merge_proofs") if isinstance(snap.get("merge_proofs"), dict) else {}
    logs = snap.get("executor_logs") if isinstance(snap.get("executor_logs"), dict) else {}
    intents = open_intents(comments, now, params["op_settle_minutes"], lambda rid: runs.get(str(rid)), lambda n: proofs.get(str(n)),
                           lambda rid: logs.get(str(rid))) if ledger_ok else []
    attempted = attempted_heads(comments) if ledger_ok else set()
    candidates = fallback_candidates(comments) if ledger_ok else None
    recall_items = [dict(item, codex=recall_status(item["head"], (snap.get("recall_reads") or {}).get(str(item["pr"])), now, snap["budgets"]["codex_silent_hours"]))
                    for item in (recalls(comments) if ledger_ok else [])]
    # P2-D: PENDING is "this build did not read Codex's completed review of that head". A clear receipt decides nothing;
    # an item drops out of the brief only when it is FINAL natively AND its clear receipt is already posted.
    recall_pending = [i for i in recall_items if i["codex"] != "FINAL"]
    recall_shown = recall_publish(recall_items)                  # fix round 4 (#11): a FINAL one stays listed, cleared or not (label repair)
    unverified = unverified_receipts(comments) if ledger_ok else []
    c1b, c1b_reason = c1b_block(snap.get("c1b"), now)
    repo_id = (snap.get("repo") or {}).get("id")
    ctx = {"repo_id": repo_id, "main_sha": snap["main_sha"], "policy": snap["policy"], "tuples": params["required_job_tuples"],
           "gate_isolation_live": snap.get("gate_isolation") == "LIVE", "now": now, "budgets": snap["budgets"],
           "quiet_minutes": params["foreign_commit_quiet_minutes"], "push_filters": snap.get("push_filters"),
           "allowlist": decision_v1.fallback_allowlist(switch)}
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
            if (entries[-1].get("n"), entries[-1].get("head")) in attempted:
                entries[-1]["attempted"] = True                  # section 0.2i: one executor merge attempt per PR head, ever
            if isinstance(entries[-1].get("thin"), dict):        # the fallback's candidate receipts for this exact head (unknown ledger: None)
                mine = None if candidates is None else candidates.get((entries[-1].get("n"), entries[-1].get("head")), [])
                entries[-1]["thin"]["fallback_candidates"] = None if mine is None else len(mine)
                entries[-1]["thin"]["fallback_mismatch"] = None if mine is None else fallback_mismatch(mine)
    rules = ruleset_census(snap.get("rulesets_1") or [], snap.get("rulesets_2") or [], bool(snap.get("rulesets_complete")))
    pulls_ok = bool(snap.get("pulls_complete"))
    codex = codex_availability([d.get("comments") for d in (snap.get("pr") or {}).values() if isinstance(d, dict)], now)
    activity = codex_activity(snap.get("codex_feed"), snap.get("pr"))
    newest = activity["items"][0] if activity["items"] else None
    limit = {"c": newest["c"], "at": iso(newest["at"]), "kind": newest["kind"]} if activity["complete"] and newest and newest["limit"] else None
    for e in entries:                                            # route (c): is Codex demonstrably unavailable for this head?
        if isinstance(e.get("thin"), dict):
            e["thin"]["codex_offline"] = offline_signal((e.get("review") or {}).get("codex"), activity, now)
    # complete=false is for data that was truly NOT READ. Main moving while the brief is built is not such a case:
    # the brief describes exactly snap["main_sha"], and S1's drift rule (TICK T3) covers main after it.
    unread = ([c1b_reason] if c1b_reason else []) + ([] if pulls_ok else ["pulls_unreadable"]) + ([] if ledger_ok else ["ledger_unreadable"]) \
        + ([] if identity_ok else ["repository_identity"]) + [str(x) for x in (snap.get("errors") or [])] \
        + (["depth_cap"] if any(e.get("skip") == "NOT_READ:depth_cap" for e in entries) else [])
    brief = {
        "schema": SCHEMA, "run_id": snap["run"]["id"], "run_attempt": snap["run"]["attempt"], "event": snap["run"]["event"],
        "generation": brief_generation(c1b),                    # fix round 7 (R6-SH1): monotonic, publish() never goes back
        "generated_at": iso(now), "max_age_minutes": MAX_AGE_MINUTES,
        "repo": {"full_name": (snap.get("repo") or {}).get("full_name"), "id": repo_id, "identity": identity_ok},
        "main": snap["main_sha"], "pins": pins,
        "lane": dict(lane, halt=halt_id, health=health, halts_seen=len(halts), lane_merges_seen=len(merges)),
        "rulesets": rules, "main_protected": snap.get("main_protected"),
        "open_intents": intents[:5],
        "status_lines": status_lines(entries, lane, merges, now, c1b) if pulls_ok and ledger_ok else
        ["OWNER APPROVAL REQUIRED: UNKNOWN (brief_incomplete)", "HIGH_IMPACT BLOCKED: UNKNOWN", "DISPOSITIONS TODAY: UNKNOWN"],
        "heartbeat_due": heartbeat_due(comments, now) if ledger_ok else False,
        "prs": entries, "drafts": drafts,
        "next": c1b_fenced_next(count_builds(next_actions(entries, lane, health, intents, codex["available"], c1b_halt=c1b["halt"],
                                                          fence_merges=bool(C1B_FENCES_LEGACY_LANE and c1b.get("fence"))),
                                             (snap.get("c1b") or {}).get("prev_next") if isinstance(snap.get("c1b"), dict) else None), c1b)
        if pulls_ok and identity_ok else [],
        "claude_slots": c1b_fenced_slots(claude_slots(entries, lane), c1b) if pulls_ok and identity_ok else [],
        "codex": codex,
        "complete": not unread, "incomplete": unread[0] if unread else None, "unread": unread[:8],
        "errors": (snap.get("errors") or [])[:8],
        # A15: a PR that could not be read is listed here and carries unreadable=true; it does not make the brief
        # incomplete. Only global evidence does (the pulls list, the ledger, identity, the API cap, the depth cap).
        "pr_errors": (snap.get("pr_errors") or [])[:8], "unreadable": [e["n"] for e in entries if e.get("unreadable")],
        "ledger_read_at": snap.get("ledger_read_at") or iso(now),
        "main_moved_during_build": bool(snap.get("main_moved")), "timing": snap.get("timing") or {},
        "not_in_brief": ["rule 1 ANSWER", "rule 5 PACKAGE", "rule 5b REENABLE", "rule 6 STEWARD", "HIGH EVIDENCE",
                         "CLAUDE_REVIEW_v1 (private Bridge)", "exclusions 4,5,6,8,9, the judgment half of 3 and 7 (see shrinks)"],
        "c1b": c1b,                                              # D1: the T3 C1b halt test, done here (TICK T3 reads it)
        "ledger": ledger_hint(comments, intents, ledger_ok, now),   # D4: hint only
        "verdict": brief_verdict(snap["main_sha"], contract, snap["pins_actual"], snap.get("bootstrap_text"), pins, snap.get("trees_actual")),
        "thin": decision_v1.thin_config(switch),                 # section 0.2i: executor mode and review policy of the switch
        "recall": {"pending": len(recall_pending) if ledger_ok else None, "items": recall_shown},   # merges that wait for Codex's revisit
        "codex_evidence": limit,                                 # Codex's newest activity in the repository, when it is a usage-limit answer
        "claude_receipts": {"unverified": len(unverified) if ledger_ok else None, "items": unverified[:10]},   # route (b) merges, receipt not checked against the Bridge
        "executor_watch": executor_watch(snap.get("executor_watch"), decision_v1.thin_config(switch)["executor"], now),   # GitHub's own record of the executor job
    }
    if brief["thin"]["executor"] == "LIVE":
        # The executor job is the ONE actor. The legacy ChatGPT procedure (TICK.md v3.3) acts only on B.next and
        # B.claude_slots, so both are empty for it; the same ranked list is published as B.ranked.
        brief["ranked"], brief["next"], brief["claude_slots"] = brief["next"], [], []
    return log_decision(brief, (snap.get("c1b") or {}).get("prev_log") if isinstance(snap.get("c1b"), dict) else None)


def brief_generation(c1b):
    """Fix round 7 (R6-SH1): the predecessor's generation + 1 (1 when this build carried no brief: the first one, or a
    build whose predecessor read failed, which publish() then never lets replace a published brief)."""
    prev = c1b.get("prev") if isinstance(c1b, dict) else None
    return (prev["generation"] + 1) if tuple_ok(prev) else 1


def c1b_fenced_next(entries, c1b):
    """Fix round 6 (S4): while B.c1b.fence is set (an open gap or segment), B.next holds no merge entry for the legacy
    lane; HALT, RECONCILE, REPAIR and review requests keep their rank (C1B_FENCES_LEGACY_LANE)."""
    if not (C1B_FENCES_LEGACY_LANE and c1b.get("fence")):
        return entries
    return [e for e in entries if e.get("action") not in MERGE_ACTIONS]


def c1b_fenced_slots(slots, c1b):
    """Fix round 6 (S4): while B.c1b.fence is set no Claude slot is ready (TICK.md v3.3 promotes only a ready slot to a
    merge entry). A slot stays listed, so an approval still means that no review request is posted."""
    if not (C1B_FENCES_LEGACY_LANE and c1b.get("fence")):
        return slots
    return [dict(x, ready=False) for x in slots]


DECISION_LOG_MAX = 24                 # B.decision_log: the newest decisions, one line each (the shadow record)
MAX_DECISION_BLOCK = 4000             # the decision block is small by construction; MAX_BODY + this stays under GitHub's limit
RENDER_HARD_LIMIT = 65000 - MAX_DECISION_BLOCK   # fix round 8 (R7-SH2): a brief block above this is never publishable (publish refuses > 65000)


def decision_log_entry(d):
    """One line of B.decision_log: what the decision was, without any text of a PR (short ids only)."""
    return {"d": d.get("id"), "at": d.get("generated_at"), "m": str(d.get("main") or "")[:12], "x": d.get("executor"),
            "a": d.get("action"), "n": d.get("pr"), "h": str(d.get("head") or "")[:12] or None, "r": str(d.get("result"))[:120]}


def log_decision(brief, prev_log):
    """B.decision_log: the carried log of the previous published brief plus this brief's own decision. The decision
    itself is NOT a field of the brief: it is decision_v1.decide(brief), a pure function of the published brief, and
    render_issue() writes it as its own block above the brief. `prev_log` None: unknown or none, the log restarts."""
    d = decision_v1.decide({k: v for k, v in brief.items() if k != "decision_log"})
    log = [x for x in (prev_log or []) if isinstance(x, dict) and x.get("d") != d.get("id")][-(DECISION_LOG_MAX - 1):]
    brief["decision_log"] = log + [decision_log_entry(d)]
    return brief


def decision_of(body):
    """The S1_DECISION_V1 of an issue body, or None: the body holds one valid brief and one valid decision block, and
    that decision IS decision_v1.decide(brief) for the brief in the same body (a decision block that the brief does
    not produce is never used: not published, not executed, not reported)."""
    brief, d = parse_body(body), decision_v1.parse_decision(body)
    if brief is None or d is None or not decision_v1.same_decision(d, decision_v1.decide(brief)):
        return None
    return d


def render_issue(brief):
    """(issue body, decision): the decision block first, then the brief block of render(). The decision is computed
    from the brief AS PUBLISHED (after any shrink), so publish(), the executor and any reader can recompute it from the
    body alone and must get the same object."""
    d = None
    for _ in range(3):
        text = render(brief)
        published = parse_body(text)
        if published is None:
            raise SystemExit("RENDER_REFUSED: the brief does not parse")
        d = decision_v1.decide(published)
        want, log = decision_log_entry(d), published.get("decision_log") or []
        if log and log[-1] == want:
            break
        brief = dict(brief, decision_log=list(brief.get("decision_log") or [])[:-1] + [want])   # the shrink changed it
    # After three passes the newest LOG line may still describe the decision of the pass before (a log line that moves
    # the body across a shrink limit twice). The decision block itself is always decide(published): never a wrong action.
    top = decision_v1.render_decision(d)
    if len(top) > MAX_DECISION_BLOCK:                            # only the three owner lines can be long: cut them, keep the action
        d = dict(d, status_lines=[x[:300] for x in d["status_lines"]], skipped=d["skipped"][:3], advice=[])
        d["print"] = d["status_lines"] + d["print"][3:]
        top = decision_v1.render_decision(d)
    return top + text, d


def render(brief):
    """The issue body: one JSON block between two markers. Shrinks deterministically below MAX_BODY; a brief that
    still does not fit is published with next=[] and complete=false (S1 then has no candidate from it). Fix round 8
    (R7-SH2): every level keeps the generation and the WHOLE c1b block (gaps, open, fence, cleared, owner_actions and
    the exact prev tuple publish() compares), so the shrunk brief can replace its predecessor; when even the last level
    does not fit, the build fails visibly (RENDER_REFUSED) and the published brief stays: a gap is never dropped."""
    def dump(b):
        return (f"{SCHEMA} run_id={b['run_id']} generated_at={b['generated_at']} main={b['main']}\n\n"
                "Machine-written every tick by `.github/workflows/s1-tick-brief.yml`. Evidence only, never authority: "
                "`00_FMOS/S1/TICK.md` says what S1 re-reads before it acts. Do not edit; an edit makes the brief unverifiable.\n\n"
                f"{BEGIN}\n```json\n{json.dumps(b, separators=(',', ':'), sort_keys=True).replace('<', chr(92) + 'u003c').replace('`', chr(92) + 'u0060')}\n```\n{END}\n")
    body = dump(brief)
    if len(body) <= MAX_BODY:
        return body
    b = json.loads(json.dumps(brief))
    ranked = {x.get("pr") for x in (b.get("ranked") or b["next"])}   # section 0.2i: while the executor is LIVE the list is B.ranked
    for e in b["prs"]:                                         # 1: drop detail of PRs that are not ranked
        if e["n"] not in ranked:
            for k in ("paths", "isolation", "item", "author", "thin"):   # without its paths a PR is never decided: its section 0.2i facts go too
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
    if "generation" in brief:
        b["generation"] = brief["generation"]                   # fix round 8 (R7-SH2): publish() needs it at every level
    for key in ("verdict", "c1b", "ledger"):                   # small and bounded in size: kept at every shrink level
        if key in brief:
            b[key] = brief[key]
    b.update(next=[], claude_slots=[], complete=False, incomplete="brief_too_large", errors=["brief_too_large"], shrunk=3, prs=[], drafts=[], lane={"state": "OFF", "off_reasons": ["brief_too_large"]},
             status_lines=["OWNER APPROVAL REQUIRED: UNKNOWN (brief_too_large)", "HIGH_IMPACT BLOCKED: UNKNOWN", "DISPOSITIONS TODAY: UNKNOWN"], heartbeat_due=False)
    for key in ("thin", "decision_log", "recall", "codex_evidence", "claude_receipts"):   # section 0.2i: a brief that ranks nothing decides NOOP
        if key in brief:
            b[key] = brief[key]
    body = dump(b)
    if len(body) > RENDER_HARD_LIMIT:
        # fix round 8 (R7-SH2): never cut the C1b ledger to fit. A level-3 brief above the shrink target but under the
        # hard limit is still published (it fits GitHub with its decision block); above the hard limit the build fails
        # visibly, the published brief stays (S1 reads it as BRIEF_STALE) and nothing is lost
        gaps = (brief.get("c1b") or {}).get("gaps") if isinstance(brief.get("c1b"), dict) else None
        raise SystemExit(f"RENDER_REFUSED: brief_too_large even at shrink level 3 (bytes={len(body)} max={RENDER_HARD_LIMIT} "
                         f"c1b_gaps={len(gaps) if isinstance(gaps, list) else '-'}); the C1b ledger is never cut, the published brief is kept")
    return body


def _unique_pairs(pairs):
    """object_pairs_hook: a key repeated in ANY object, top-level or nested, makes the body invalid (the duplicate
    would otherwise silently win, and a reader that keeps the first one would see a different brief)."""
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate key {key!r}")
        out[key] = value
    return out


def _no_constant(name):
    raise ValueError(f"not JSON: {name}")                    # NaN, Infinity and -Infinity are not RFC 8259 JSON


def strict_loads(text):
    """RFC 8259 JSON with unique keys at every level and no NaN or Infinity; ValueError otherwise."""
    return json.loads(text, object_pairs_hook=_unique_pairs, parse_constant=_no_constant)


def _is_id(value):
    return type(value) is int and value > 0                    # a bool is not an id (True == 1 in Python)


def brief_schema_ok(b):
    """The fields T1 to T5 read, with their types (CHARTER_ADDENDUM_1: a wrong type is BRIEF_UNVERIFIED(body)). The
    reference is schema_ok of tests/governance/test_s1_trajectory_replay_v1.py; the SHA fields are also 40-hex here."""
    pins, repo, lines = b.get("pins"), b.get("repo"), b.get("status_lines")
    sha_or_null = lambda v: v is None or (isinstance(v, str) and SHA40.fullmatch(v) is not None)
    return (b.get("schema") == SCHEMA and _is_id(b.get("run_id")) and _is_id(b.get("run_attempt"))
            and isinstance(b.get("event"), str) and isinstance(b.get("generated_at"), str)
            and isinstance(b.get("main"), str) and SHA40.fullmatch(b["main"]) is not None
            and isinstance(pins, dict) and type(pins.get("ok")) is bool
            and all(sha_or_null(pins.get(k)) for k in ("contract_blob", "action_loop_blob", "tick_blob"))
            and type(b.get("complete")) is bool and isinstance(b.get("incomplete"), (str, type(None)))
            and isinstance(repo, dict) and type(repo.get("id")) is int
            and isinstance(lines, list) and len(lines) == 3 and all(isinstance(x, str) for x in lines)
            and isinstance(b.get("next"), list) and all(isinstance(x, dict) for x in b["next"])
            and isinstance(b.get("claude_slots"), list) and isinstance(b.get("prs"), list))


def brief_block(body):
    """The exact JSON text of the one block (the bytes between the opening ```json line and the closing ``` line), or
    None: exactly one BEGIN and one END marker, BEGIN before END, and between them exactly one ```json fence."""
    text = str(body or "")
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        return None
    i, j = text.index(BEGIN), text.index(END)
    if j < i:
        return None
    m = re.fullmatch(r"```json\n(.*)\n```", text[i + len(BEGIN):j].strip(), re.S)
    if not m or "\n```" in m.group(1):
        return None
    return m.group(1)


def parse_body(body):
    """The inverse of render(): exactly one ordered marker pair around one ```json block holding one strict JSON object
    (unique keys at every level, no NaN or Infinity) that passes brief_schema_ok; anything else is None."""
    block = brief_block(body)
    if block is None:
        return None
    try:
        doc = strict_loads(block)
    except (ValueError, RecursionError):
        return None
    return doc if isinstance(doc, dict) and brief_schema_ok(doc) else None


def brief_digest(body):
    """S1_BRIEF_DIGEST_V1: sha256 of the UTF-8 bytes of the block text, or None when the body has no block."""
    block = brief_block(body)
    return None if block is None else hashlib.sha256(block.encode("utf-8")).hexdigest()


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
    if run.get("path") != WORKFLOW_PATH or run.get("event") not in RUN_EVENTS or run.get("event") != brief.get("event") \
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
    if (brief.get("pins") or {}).get("ok") is not True:        # the order of TICK.md T2: pins, then age, then completeness
        return bad("pins")
    age = (now - made).total_seconds() / 60
    if age > max_age or age < -2:
        return (None, f"BRIEF_STALE(age_min={int(age)})")
    if brief.get("complete") is not True:                      # truly unread data: the tick is a NOOP with this reason
        return (None, f"BRIEF_INCOMPLETE({brief.get('incomplete') or 'unknown'})")
    return brief, "OK"


def brief_is_old(issues, now, minutes=FALLBACK_DUE_MINUTES):
    """No brief by the Actions bot younger than `minutes` is published. Age and author decide, nothing else: a brief
    that is incomplete or whose pins are off is retried by the hourly cron run, never by every trigger completion (that
    would spend the repository's hourly API quota on a state a rebuild cannot change). Anything unreadable is old."""
    if not isinstance(issues, list):
        return True
    rows = [i for i in issues if isinstance(i, dict) and "pull_request" not in i]
    if len(rows) != 1 or not is_actions_bot(rows[0].get("user")):
        return True
    brief = parse_body(rows[0].get("body"))
    try:
        age = (now - stamp(brief["generated_at"])).total_seconds() / 60
    except (ValueError, KeyError, TypeError):
        return True
    return not 0 <= age < minutes


def build_started(jobs):
    """A11/A13: did this run start the build job? From its jobs list: a `build` job that was not skipped. A build that
    failed or was cancelled counts too (it spent the API calls); a run whose jobs cannot be read counts as started."""
    if not isinstance(jobs, list):
        return True
    return any(isinstance(j, dict) and j.get("name") == "build" and j.get("conclusion") != "skipped" for j in jobs)


def cooldown_candidates(runs, now, self_run_id, limit=JOBS_READS_PER_DUE):
    """The fallback runs (workflow_run, push) of the last BUILD_RECENT_MINUTES whose jobs are worth reading, longest
    first: a run that built lasts minutes, a run that was not due ends after its short due job. At most `limit`."""
    rows = []
    for run in runs:
        try:
            if run.get("id") == self_run_id or run.get("event") not in FALLBACK_EVENTS:
                continue
            created = stamp(run.get("created_at"))
            if (now - created).total_seconds() / 60 >= BUILD_RECENT_MINUTES:
                continue
            end = stamp(run.get("updated_at")) if run.get("status") == "completed" else now
            rows.append(((end - created).total_seconds(), run.get("id")))
        except (ValueError, TypeError, AttributeError):
            rows.append((float("inf"), run.get("id") if isinstance(run, dict) else None))
    return [rid for _d, rid in sorted(rows, key=lambda x: -x[0])[:limit]]


def recent_build(runs, now, self_run_id, jobs_of=None):
    """True when another run of this workflow makes a fallback build redundant:
    - a cron run created in the last CRON_RECENT_MINUTES, or a cron or manual run in the last BUILD_RECENT_MINUTES
      (they always build);
    - an OLDER fallback run that is still running and was created less than COALESCE_MINUTES ago (A12: it decides;
      this one stops after the one call that read the run list);
    - a fallback run of the last BUILD_RECENT_MINUTES whose jobs list shows a started build (jobs_of(run id), at most
      JOBS_READS_PER_DUE reads). An unreadable row or jobs list counts as a build."""
    for run in runs:
        try:
            if run.get("id") == self_run_id:
                continue
            if run.get("status") == "completed" and run.get("conclusion") == "cancelled":
                continue                                         # fix round 7: replaced while pending in the run group; it built nothing
            age = (now - stamp(run.get("created_at"))).total_seconds() / 60
            if age < CRON_RECENT_MINUTES and run.get("event") == "schedule":
                return True
            if age < BUILD_RECENT_MINUTES and run.get("event") not in FALLBACK_EVENTS:
                return True
            if 0 <= age < COALESCE_MINUTES and run.get("status") != "completed" and isinstance(self_run_id, int) \
                    and isinstance(run.get("id"), int) and run["id"] < self_run_id:
                return True
        except (ValueError, TypeError, AttributeError):
            return True
    if jobs_of is None:
        return False
    return any(build_started(jobs_of(rid)) for rid in cooldown_candidates(runs, now, self_run_id))


def fallback_due(issues, now, runs=None, self_run_id=None, minutes=FALLBACK_DUE_MINUTES, jobs_of=None):
    """The workflow_run and push triggers are a freshness fallback for a MISSED cron event, not a second schedule (a
    push to main still happens when GitHub fires no scheduled workflow at all). A fallback run builds only
    when the published brief is older than `minutes` AND the run list of this workflow shows no recent cron run and no
    recent build. The run list must be readable: without it the fallback never builds (the cron still does), because
    the job token's hourly quota is shared by every workflow of the repository."""
    if not isinstance(runs, list) or recent_build(runs, now, self_run_id):
        return False
    if not brief_is_old(issues, now, minutes):
        return False                                             # the usual case: two calls, no jobs read
    return not recent_build(runs, now, self_run_id, jobs_of or (lambda rid: None))


CODE_DRIFT_PREFIXES = ("00_FMOS/", ".github/", ".agents/", "scripts/", "tests/", "07_PROMPTS_AND_AGENTS/",
                       "01_CORE_FRAMEWORK/governance/")
CODE_DRIFT_SUFFIXES = (".py", ".sh", ".yml", ".yaml", ".toml", ".cfg", ".ini", ".pth", ".mjs", ".js")


def code_drift_path(path):
    """The path rule of TICK.md T3 (source_changed), as code: AGENTS.md, a path under a governance prefix or a pin
    directory of the lane switch, an executable or config suffix anywhere, or a requirements*.txt anywhere."""
    if not isinstance(path, str) or not path:
        return True                                              # unreadable path: treat as code
    name = path.rsplit("/", 1)[-1]
    return (path == "AGENTS.md" or path.startswith(CODE_DRIFT_PREFIXES) or path.endswith(CODE_DRIFT_SUFFIXES)
            or (name.startswith("requirements") and name.endswith(".txt")))


def code_drift_due(issues, drift, head):
    """True when the published brief describes a main whose code differs from `head`: a squash merge of code since the
    brief makes every S1 tick end BRIEF_STALE(source_changed) until the next build, so the push that brought it builds
    now. Only native evidence decides: the brief's own B.main and drift(B.main, head) -> (relation, paths), read from
    git (never the push payload, never the REST compare). Unreadable drift is due (fail toward a fresh brief); a brief
    that is already at or past `head` is not; no single bot brief is left to the existing rule (brief_is_old)."""
    if not isinstance(head, str) or not SHA40.fullmatch(head) or not isinstance(issues, list):
        return False
    rows = [i for i in issues if isinstance(i, dict) and "pull_request" not in i]
    if len(rows) != 1 or not is_actions_bot(rows[0].get("user")):
        return False
    brief = parse_body(rows[0].get("body"))
    base = (brief or {}).get("main")
    if not isinstance(base, str) or not SHA40.fullmatch(base) or base == head:
        return False
    try:
        relation, paths = drift(base, head)
    except Exception:                                            # noqa: BLE001
        return True
    if relation == "behind":
        return False                                             # a newer brief already covers this push (re-asked after the wait)
    if relation != "ahead" or not isinstance(paths, list) or len(paths) >= DRIFT_MAX_FILES:
        return True                                              # unknown, diverged, or beyond T3's caps: rebuild
    return any(code_drift_path(p) for p in paths)


CHECKOUT_ROOT = Path(__file__).resolve().parents[2]  # the checkout this script runs from (workspace in due, main/ in build)
DRIFT_MAX_COMMITS, DRIFT_MAX_FILES = 100, 300       # TICK.md T3: beyond these the drift is unreadable (BRIEF_STALE)


def git_drift(root, base, head):
    """(relation, paths) of base -> head for code_drift_due: relation from a commits-only graph (ahead, behind or
    unknown), paths from the two trees (depth 1, no file cap). Anything unreadable is (unknown, None)."""
    graph_dir = Path(str(root) + ".due-graph")
    try:
        url = git(root, "remote", "get-url", "origin")
        graph_dir.mkdir(parents=True, exist_ok=True)
        git(graph_dir, "init", "--quiet", "--bare")
        if "origin" not in git(graph_dir, "remote").split():
            git(graph_dir, "remote", "add", "origin", url)
        have = fetch_commits(graph_dir, [base, head], "--filter=tree:0")
    except (subprocess.CalledProcessError, OSError):
        return "unknown", None
    if not {base, head} <= have:
        return "unknown", None
    if on_main(graph_dir, head, base):
        return "behind", None
    if not on_main(graph_dir, base, head):
        return "unknown", None
    try:
        if int(git(graph_dir, "rev-list", "--count", f"{base}..{head}")) > DRIFT_MAX_COMMITS:
            return "too_large", None
    except (subprocess.CalledProcessError, ValueError):
        return "unknown", None
    if not {base, head} <= fetch_commits(root, [base, head], "--depth=1"):
        return "unknown", None
    return "ahead", changed_between(root, base, head)


# ----------------------------------------------------------------------------------------------- GitHub reader
def rate_limited(exc):
    """Is this HTTP error a primary or secondary rate limit? 429 always; 403 with Retry-After, with no remaining quota,
    or with GitHub's secondary-rate-limit text in the body. A plain 403 (a permission) is not."""
    if exc.code == 429:
        return True
    if exc.code != 403:
        return False
    headers = exc.headers or {}
    if headers.get("Retry-After") or str(headers.get("x-ratelimit-remaining")) == "0":
        return True
    try:
        body = exc.read(4096).decode("utf-8", "replace").lower()
    except Exception:                                            # noqa: BLE001
        body = ""
    return "secondary rate limit" in body or "rate limit exceeded" in body


class GitHub:
    """Minimal REST reader. GET only, except graphql() (a read query sent by POST) and the two issue writes of publish."""

    def __init__(self, token, repo=REPO, base="https://api.github.com", budget=MAX_API_CALLS):
        self.token, self.repo, self.base, self.calls, self.budget = token, repo, base, 0, budget

    def _request(self, method, url, data=None, accept="application/vnd.github+json"):
        req = urllib.request.Request(url, method=method, data=None if data is None else json.dumps(data).encode())
        req.add_header("Accept", accept)
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        req.add_header("User-Agent", "s1-tick-brief")
        if self.token:
            req.add_header("Authorization", f"Bearer {self.token}")
        for attempt in (1, 2):                                   # one retry of a read that failed in transport or with a 5xx
            self.calls += 1                                      # EVERY HTTP attempt counts toward the cap, a retry included
            if self.calls > self.budget:
                raise ApiBudget("API_BUDGET_EXHAUSTED")
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    return resp.read(), resp.headers
            except urllib.error.HTTPError as exc:
                if rate_limited(exc):
                    # a primary or secondary rate limit: ONE bounded retry when GitHub names a short wait, then stop
                    wait = str((exc.headers or {}).get("Retry-After") or "")
                    if method == "GET" and attempt == 1 and wait.isdigit() and int(wait) <= RETRY_AFTER_MAX_SECONDS:
                        time.sleep(int(wait))
                        continue
                    raise RateLimited(f"HTTP_{exc.code}") from exc
                if method != "GET" or exc.code < 500 or attempt == 2:
                    raise
            except (urllib.error.URLError, TimeoutError):
                if method != "GET" or attempt == 2:
                    raise
            time.sleep(2)

    def remaining(self):
        """API calls this client may still make under its cap (fix round 5, D04: the merge reserve)."""
        return self.budget - self.calls

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
            raise ApiBudget("API_BUDGET_EXHAUSTED")
        req = urllib.request.Request(self.url(path), method="GET")
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("User-Agent", "s1-tick-brief")
        if self.token:
            req.add_header("Authorization", f"Bearer {self.token}")
        try:
            with urllib.request.build_opener(job_identity._SafeGithubLogRedirect()).open(req, timeout=60) as resp:
                raw = resp.read(8 * 1024 * 1024 + 1)
        except urllib.error.HTTPError as exc:
            if rate_limited(exc):                                # the log read stops the build like every other read
                raise RateLimited(f"HTTP_{exc.code}") from exc
            raise
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
reviewThreads(first:100,after:$c){pageInfo{hasNextPage endCursor} nodes{isResolved comments(first:100){totalCount nodes{body}}}}}}}"""
THREAD_COMMENTS_MAX = 100              # replies of one review thread read in one query; a longer thread is unread (None)


def read_threads(gh, number):
    """Every review thread of the PR with EVERY reply's body joined (`first_body` keeps its old name), or None when
    anything is unread. Fix round 5 (#173/7190895883 D01): a thread whose replies GitHub reports beyond those returned
    (totalCount), a missing or non-boolean isResolved, or a node of another shape is unread: never "no P0/P1"."""
    owner, name = gh.repo.split("/")
    out, cursor = [], None
    for _ in range(5):
        data = gh.graphql(THREADS_QUERY, {"o": owner, "r": name, "n": number, "c": cursor})
        t = data["repository"]["pullRequest"]["reviewThreads"]
        for node in t["nodes"]:
            comments = (node or {}).get("comments") if isinstance(node, dict) else None
            rows = comments.get("nodes") if isinstance(comments, dict) else None
            if not isinstance(node, dict) or type(node.get("isResolved")) is not bool or not isinstance(rows, list) \
                    or type(comments.get("totalCount")) is not int or comments["totalCount"] != len(rows) or len(rows) > THREAD_COMMENTS_MAX \
                    or not all(isinstance(c, dict) for c in rows):
                return None
            out.append({"resolved": node["isResolved"], "first_body": "\n".join(str(c.get("body") or "") for c in rows), "replies": len(rows)})
        if not t["pageInfo"]["hasNextPage"]:
            return out
        cursor = t["pageInfo"]["endCursor"]
    return None


GIT_ENV = None                         # set by main(): the job token reaches git through the process environment only


def token_git_env(token, base=None):
    """The environment for git: the token as an HTTP header for github.com, passed per process and never written to
    the checkout's configuration (the checkout step does not persist a credential)."""
    env = dict(os.environ if base is None else base)
    env["GIT_TERMINAL_PROMPT"] = "0"
    if token:
        n = int(env.get("GIT_CONFIG_COUNT") or 0)
        cred = base64.b64encode(f"x-access-token:{token}".encode()).decode()
        env.update({"GIT_CONFIG_COUNT": str(n + 1), f"GIT_CONFIG_KEY_{n}": "http.https://github.com/.extraheader",
                    f"GIT_CONFIG_VALUE_{n}": f"AUTHORIZATION: basic {cred}"})
    return env


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True, env=GIT_ENV).stdout.strip()


def fetch_commits(repo, shas, *options):
    """One fetch for every SHA; when that fails, one fetch per SHA. Returns the SHAs that were fetched."""
    shas = list(dict.fromkeys(s for s in shas if isinstance(s, str) and SHA40.fullmatch(s)))
    if not shas:
        return set()
    try:
        git(repo, "fetch", "--quiet", "--no-tags", *options, "origin", *shas)
        return set(shas)
    except subprocess.CalledProcessError:
        got = set()
        for sha in shas:
            try:
                git(repo, "fetch", "--quiet", "--no-tags", *options, "origin", sha)
                got.add(sha)
            except subprocess.CalledProcessError:
                pass
        return got


def read_graph(root, graph_dir, main_sha, heads):
    """{head: {base, behind_by}} from git COMMIT objects alone: one commits-only fetch (no trees, no blobs) of main's
    and every head's history into a scratch repository. The REST compare lists at most 300 files and 250 commits, which
    made every PR far behind a busy main unreadable; a merge-base needs neither. A head that is missing, has no single
    merge-base with main, or cannot be counted is absent from the result (the caller reads that as NOT PROVEN)."""
    out = {}
    try:
        url = git(root, "remote", "get-url", "origin")
        Path(graph_dir).mkdir(parents=True, exist_ok=True)
        git(graph_dir, "init", "--quiet", "--bare")
        if "origin" not in git(graph_dir, "remote").split():
            git(graph_dir, "remote", "add", "origin", url)
        have = fetch_commits(graph_dir, [main_sha, *heads], "--filter=tree:0")
    except (subprocess.CalledProcessError, OSError):
        return out
    if main_sha not in have:
        return out
    for head in heads:
        if head not in have:
            continue
        try:
            bases = git(graph_dir, "merge-base", "--all", main_sha, head).split()
            if len(bases) != 1 or not SHA40.fullmatch(bases[0]):
                continue
            out[head] = {"base": bases[0], "behind_by": int(git(graph_dir, "rev-list", "--count", f"{head}..{main_sha}"))}
        except (subprocess.CalledProcessError, ValueError):
            continue
    return out


def on_main(graph_dir, sha, main_sha):
    """Is `sha` an ancestor of main_sha? From the commits-only graph repository; anything unreadable is no."""
    return ancestry(graph_dir, sha, main_sha) is True


def ancestry(graph_dir, sha, main_sha):
    """Fix round 5 (D06): True (an ancestor), False (git PROVED it is not: exit 1) or None (anything else: unknown)."""
    try:
        git(graph_dir, "merge-base", "--is-ancestor", sha, main_sha)
        return True
    except subprocess.CalledProcessError as exc:
        return False if exc.returncode == 1 else None
    except OSError:
        return None


def changed_between(root, base, main_sha):
    """Every path main changed after `base`, from the two trees (no file or commit cap). None when unreadable."""
    try:
        return [n for n in git(root, "diff", "--name-only", "--no-renames", "-z", base, main_sha).split("\0") if n]
    except subprocess.CalledProcessError:
        return None


def root_trees(root):
    """{"": the root tree SHA of HEAD, and each T3_TREE_DIRS name: its tree SHA in that root tree (the non-recursive
    entries GET /git/trees/<sha> lists, which TICK T3 C1b compares)}. A name that is not a tree there is None."""
    out = dict.fromkeys(("", *T3_TREE_DIRS))
    try:
        out[""] = git(root, "rev-parse", "HEAD^{tree}")
        for row in git(root, "ls-tree", "-z", "HEAD").split("\0"):
            meta, _tab, name = row.partition("\t")
            parts = meta.split()
            if name in T3_TREE_DIRS and len(parts) == 3 and parts[1] == "tree":
                out[name] = parts[2]
    except (subprocess.CalledProcessError, OSError):
        pass
    return out


def read_push_filters(root):
    """[{workflow, paths, paths_ignore}] for every workflow file at `root` whose push trigger can fire on main (section
    0.2i: a merge made with the workflow token starts none of them, so decision_v1.push_trigger_matches keeps such a PR
    for the owner route). None when the parser or any workflow file cannot be read: every PR then reads as a match."""
    try:
        import yaml
    except ImportError:
        return None
    out = []
    try:
        files = sorted(p for p in (Path(root) / ".github" / "workflows").iterdir() if p.suffix in (".yml", ".yaml"))
        for path in files:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(doc, dict):
                return None
            on = doc.get(True, doc.get("on"))                    # YAML 1.1 reads the key `on` as the boolean true
            on = {on: None} if isinstance(on, str) else {k: None for k in on} if isinstance(on, list) else on
            if not isinstance(on, dict):
                return None
            if "push" not in on:
                continue
            push = on["push"] if isinstance(on["push"], dict) else {}
            branches = push.get("branches")
            if "tags" in push and "branches" not in push and "branches-ignore" not in push:
                continue                                         # tags only: a branch push never starts it
            if isinstance(branches, list) and branches and "branches-ignore" not in push \
                    and not any(str(b) == "main" or any(ch in str(b) for ch in "*?+[!") for b in branches):
                continue                                         # provably other branches only
            out.append({"workflow": path.name, "paths": push.get("paths"), "paths_ignore": push.get("paths-ignore")})
    except Exception:                                            # noqa: BLE001  (unreadable: fail closed)
        return None
    return out


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
        except StopReading:
            raise
        except Exception:                                        # noqa: BLE001  (unreadable threads are NOT_PROVEN)
            d["threads"] = None
        # The PR's own changed set is the files list above (complete only with changed_files equality, pr_entry). What
        # main changed since the merge-base comes from git objects: the graph gives the base, two trees give the paths.
        g = (ctx.get("graph") or {}).get(head)
        d["compare"] = {"behind_by": g["behind_by"] if g else None, "complete": False, "main_changed_paths": []}
        if g and g["base"] == ctx["main_sha"] and g["behind_by"] == 0:
            d["compare"]["complete"] = True
        elif g:
            names = ctx["main_changed"](g["base"])
            if names is not None:
                d["compare"].update(main_changed_paths=names, complete=True)
        runs, rc = gh.pages("actions/runs", {"head_sha": head, "event": "pull_request"}, key="workflow_runs", max_pages=5)
        d["runs"], d["runs_complete"], d["jobs"] = runs, rc, {}
        wanted = {t["workflow_path"] for t in ctx["tuples"]}
        for path in wanted:
            kept = [r for r in runs if r.get("path") == path and r.get("head_sha") == head]
            if kept:
                run = max(kept, key=lambda r: r.get("run_number") or 0)
                jobs, jc = gh.pages(f"actions/runs/{run['id']}/jobs", {"filter": "latest"}, key="jobs", max_pages=3)
                d["jobs"][run["id"]] = jobs if jc else None
        gate_path = next((t["workflow_path"] for t in ctx["tuples"] if t["job"] == "privacy-scan"), None)
        gate_runs = [r for r in runs if r.get("path") == gate_path and r.get("head_sha") == head]
        if gate_runs:
            newest = max(gate_runs, key=lambda r: r.get("run_number") or 0)
            base_at_run = next(((p.get("base") or {}).get("sha") for p in newest.get("pull_requests") or [] if p.get("number") == n), None)
            if isinstance(base_at_run, str) and SHA40.fullmatch(base_at_run):
                d["gate_drift"] = ctx["gate_drift"](base_at_run)  # None when that tree cannot be read: the merge-base decides
        priv = [j for jobs in d["jobs"].values() if jobs for j in jobs if j.get("name") == "privacy-scan" and j.get("conclusion") == "success"]
        d["privacy_log"] = None
        if len(priv) == 1:
            try:
                d["privacy_log"] = gh.text(f"actions/jobs/{priv[0]['id']}/logs")
            except StopReading:
                raise
            except Exception:                                    # noqa: BLE001
                d["privacy_log"] = None
        checks, k1 = gh.pages(f"commits/{head}/check-runs", key="check_runs", max_pages=5)
        statuses, k2 = gh.pages(f"commits/{head}/statuses", max_pages=3)
        d.update(check_runs=checks, statuses=statuses, checks_complete=k1 and k2)
        changed = [f.get("filename") for f in d["files"]] + [f["previous_filename"] for f in d["files"] if f.get("previous_filename")]
        # The derivation of a head costs a checkout and about 20 s. It can only ADD exclusion 3 reasons, so a PR that
        # another diff exclusion already makes OWNER_GATED is not derived (same lane result, no redundant read).
        already, _floor = path_exclusions(d["files"], bool(d["files_complete"]), ctx["policy"], ctx["gate_isolation_live"], {"owner_gated": [], "high_floor": []})
        d["isolation"] = {"owner_gated": [], "high_floor": [], "not_derived": "already_owner_gated"} if already else derive_isolation(head, changed)
        d["detail2"] = gh.get(f"pulls/{n}")                    # the second head read, AFTER every other read of this PR
    except StopReading:
        raise                                                    # the cap or a rate limit: collect() stops every further read
    except Exception as exc:                                     # noqa: BLE001
        d["error"] = type(exc).__name__
        snap_errors.append(f"pr{n}:{type(exc).__name__}")       # recorded per PR (brief.pr_errors): NOT a global error
    return d


def collect(gh, root, head_root, now, run):
    """The snapshot for build_brief(): native reads at one main SHA. `root` is the checkout of that SHA."""
    errors = []
    main_sha = git(root, "rev-parse", "HEAD")
    pr_errors = []
    snap = {"now": iso(now), "run": run, "main_sha": main_sha, "errors": errors, "pr_errors": pr_errors}
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
    snap["trees_actual"] = root_trees(root)                      # B.verdict.t3_basis: the trees TICK T3 C1b compares, at B.main
    snap["push_filters"] = read_push_filters(root)               # section 0.2i: main's push-triggered workflows (files only)
    clock, timing = time.monotonic(), {}
    snap["timing"] = timing
    snap["repo"] = gh.get("")
    branch = gh.get("branches/main")
    snap["main_protected"] = branch.get("protected")
    # The brief is built against ONE pinned SHA, the checked-out main_sha (M0), and says so in `main`. Main moving
    # meanwhile is expected (data writers commit every few minutes) and is NOT an error: nothing below reads "current
    # main", and S1 applies the drift rule to the commits after M0 (TICK T3).
    snap["main_moved"] = (branch.get("commit") or {}).get("sha") != main_sha
    snap["ledger_read_at"] = iso(datetime.now(timezone.utc))   # BEFORE the read: a halt posted from now on is S1's to see (TICK F5)
    snap["issue_comments"], snap["issue_comments_complete"] = gh.pages(f"issues/{OWNER_ISSUE}/comments", max_pages=120)
    # section 0.2i: the runs that Actions-bot outcome posts name (none while the ledger holds no such post; at most
    # SETTLE_RUN_READS). build_brief() repeats the same pure computation over this record.
    reader, merges, logs = RunReader(gh), MergeReader(gh), LogReader(gh)
    if snap["issue_comments_complete"]:
        try:
            open_intents(snap["issue_comments"], stamp(snap["now"]), 0, reader, merges, logs)   # the same `now` build_brief() uses
        except StopReading as exc:
            errors.append(exc.reason)
    snap["executor_runs"], snap["merge_proofs"], snap["executor_logs"] = reader.docs, merges.docs, logs.docs
    try:                                                         # the executor watchdog (fix round 4, #8): fail soft, UNREAD
        snap["executor_watch"] = read_executor_watch(gh, (snap.get("run") or {}).get("id"))
    except StopReading as exc:
        errors.append(exc.reason)
        snap["executor_watch"] = None
    except (urllib.error.HTTPError, OSError, ValueError, KeyError, TypeError, AttributeError):
        snap["executor_watch"] = None
    # Codex's own activity in the whole repository (route (c): is Codex demonstrably unavailable?). Fail soft: an
    # unreadable feed is an incomplete one, and an incomplete one is never an offline signal.
    try:
        snap["codex_feed"] = read_codex_feed(gh, stamp(snap["now"]))
    except StopReading as exc:
        errors.append(exc.reason)
        snap["codex_feed"] = {"complete": False}
    except (urllib.error.HTTPError, OSError, ValueError):
        snap["codex_feed"] = {"complete": False}
    # Codex recall: the review state of the merged PRs whose recall is pending (none while the ledger holds no fallback merge)
    snap["recall_reads"] = {}
    if snap["issue_comments_complete"]:
        for item in recall_window(recalls(snap["issue_comments"]), stamp(snap["now"])):
            try:
                snap["recall_reads"][str(item["pr"])] = read_recall(gh, item["pr"])
            except StopReading as exc:
                errors.append(exc.reason)
                break
            except urllib.error.HTTPError:
                continue                                         # a receipt that names an unreadable PR: its state stays NOT_READ
    snap["health_runs"] = gh.pages(f"actions/workflows/{Path(snap['bindings']['main_health']['workflow_path']).name}/runs",
                                   {"event": "schedule", "branch": "main"}, key="workflow_runs", max_pages=1)
    snap["health_runs"], health_complete = snap["health_runs"]
    snap["health_runs_complete"] = health_window_ok(snap["health_runs"], health_complete)   # ROUTE 1: the newest 100 runs only (fix round 6: proven as that scope)
    r1, c1 = gh.pages("rulesets", {"includes_parents": "true"}, max_pages=2)
    r2, c2 = gh.pages("rulesets", {"includes_parents": "true"}, max_pages=2)
    snap.update(rulesets_1=r1, rulesets_2=r2, rulesets_complete=c1 and c2)
    snap["pulls"], snap["pulls_complete"] = gh.pages("pulls", {"state": "open", "sort": "created", "direction": "asc"}, max_pages=5)
    if snap["issue_comments_complete"]:
        try:                                                     # fix round 7 (R6-SH4): native edit records, fail closed
            read_gap_native(gh, snap["issue_comments"])
        except StopReading as exc:
            errors.append(exc.reason)
        except (urllib.error.HTTPError, OSError, ValueError, KeyError, TypeError, AttributeError, RuntimeError):
            pass
    # D1: the C1b halt test, before the PR depth reads and on its own share of the cap (the PRs cannot starve it)
    snap["c1b"] = read_c1b(gh, main_sha, snap["issue_comments"] if snap["issue_comments_complete"] else None, now)
    timing["base_s"] = round(time.monotonic() - clock)
    import s1_workflow_isolation_derive_v1 as iso_mod            # main's code only; it parses, it never executes a head
    main_derivation = iso_mod.derive(Path(root))

    def derive_isolation(head, changed):
        started = time.monotonic()
        try:
            if head not in fetched:
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
        finally:
            timing["derive_s"] = round(timing.get("derive_s", 0) + time.monotonic() - started)
            timing["derive_n"] = timing.get("derive_n", 0) + 1

    same_repo = [p for p in snap["pulls"] if not p.get("draft") and ((p.get("head") or {}).get("repo") or {}).get("id") == snap["repo"].get("id")]
    chosen = sorted(same_repo, key=lambda p: str(p.get("updated_at") or ""), reverse=True)[:MAX_DEPTH_PRS]
    heads = [(p.get("head") or {}).get("sha") for p in chosen]
    clock = time.monotonic()
    graph_dir = Path(str(head_root) + ".graph")
    graph = read_graph(root, graph_dir, main_sha, [h for h in heads if isinstance(h, str) and SHA40.fullmatch(h)])
    # one fetch brings the tree of every merge-base and every head (depth 1: one commit each)
    fetched = fetch_commits(root, sorted({g["base"] for g in graph.values()} - {main_sha}) + heads, "--depth=1")
    timing["git_s"] = round(time.monotonic() - clock)
    cache = {}

    def main_changed(base):
        if base not in cache:                                    # per run: PRs that share a merge-base share the diff
            cache[base] = changed_between(root, base, main_sha) if base in fetched else None
        return cache[base]

    gate_files = set(GATE_FILES) | {t["workflow_path"] for t in snap["bindings"]["required_job_tuples"]}

    def gate_drift(base_at_run):
        """Gate files main changed after the base SHA a privacy run recorded (one more depth-1 fetch per distinct base)."""
        if base_at_run == main_sha:
            return []
        if not on_main(graph_dir, base_at_run, main_sha):
            return None                                          # not a commit of main: unverified, the merge-base decides
        if base_at_run not in fetched:
            fetched.update(fetch_commits(root, [base_at_run], "--depth=1"))
        names = main_changed(base_at_run)
        return None if names is None else sorted(set(names) & gate_files)

    ctx = {"main_sha": main_sha, "tuples": snap["bindings"]["required_job_tuples"], "graph": graph, "main_changed": main_changed, "gate_drift": gate_drift,
           "policy": snap["policy"], "gate_isolation_live": snap.get("gate_isolation") == "LIVE"}
    snap["pr"] = {}
    clock = time.monotonic()
    stopped = snap["c1b"].get("stop")                           # the cap or a rate limit hit inside C1b: no further call
    if stopped:
        errors.insert(0, stopped)
    for pr in chosen:
        if stopped is None:
            try:
                snap["pr"][pr["number"]] = read_pr(gh, pr, ctx, pr_errors, derive_isolation)
                continue
            except StopReading as exc:                           # api_budget or rate_limited: no further API call in this build
                stopped = exc.reason
                errors.insert(0, stopped)
        snap["pr"][pr["number"]] = {"error": stopped}            # this PR and every later one: NOT_READ, never ranked
    timing["prs_s"] = round(time.monotonic() - clock)
    return snap


# ----------------------------------------------------------------------------------------------- publish
def keep_published(gh, issue, brief, now):
    """Is the published body a real brief of this workflow, so that an older one must not replace it? All must hold:
    its generated_at is not in the future and not after the issue's updated_at; its run_id is a run of this workflow
    in this repository (ONE read); and that run's window contains generated_at. Anything else, or an unreadable run,
    is overwritten."""
    try:
        made = stamp(brief.get("generated_at"))
        if made > now or made > stamp(issue.get("updated_at")):
            return False
        run = gh.get(f"actions/runs/{int(brief.get('run_id'))}")
        if run.get("path") != WORKFLOW_PATH or (run.get("repository") or {}).get("full_name") != REPO:
            return False
        end = stamp(run.get("updated_at")) if run.get("status") == "completed" else now
        return stamp(run.get("run_started_at")) <= made <= end
    except Exception:                                            # noqa: BLE001  (not provable: overwrite)
        return False


def publish(gh, body, now=None, result=None):
    """Write the one brief issue. Finds it by label; creates the label and the issue on the first run. More than one
    open labelled issue by the Actions bot is repaired by closing the newer ones (never deleted), and only once their
    ledger is proven carried (fix round 7). Returns the issue number. Fix round 8: `result` (a dict, optional) is set
    to {"state": "WRITTEN"|"SKIPPED", "reason": ...}: a skip keeps the published brief and is never reported as a write."""
    result = {} if result is None else result
    result.update(state="SKIPPED", reason="not_reached")
    if parse_body(body) is None or len(body) > 65000:
        raise SystemExit("PUBLISH_REFUSED: body is not one valid brief")
    if decision_v1.BEGIN in body and decision_of(body) is None:
        raise SystemExit("PUBLISH_REFUSED: the S1_DECISION_V1 block is not the decision of this brief")
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
        result.update(state="WRITTEN", reason="created")
        try:
            gh._request("PUT", gh.url(f"issues/{number}/lock"), {"lock_reason": "resolved"})
        except urllib.error.HTTPError:
            pass                                                 # an unlocked issue still works; a comment only makes one brief unverifiable
        return number
    # Fix round 7 (R6-SH1, R6-SH2): an exact compare-and-swap on the ONE serialized writer. The workflow runs build and
    # publish in ONE job of ONE concurrency group (cancel-in-progress false), so no other publish of this code runs
    # between this build's read of the published brief and the write below; this check is the second fence (a rerun,
    # an old-code run during rollout, a manual edit). The new brief replaces the published one only when its build
    # carried EXACTLY the published brief: the same issue number, run id, run attempt, sha256 of the exact block bytes
    # and generation, and the new generation is that generation + 1. Anything else keeps the published brief (S1 reads
    # it as BRIEF_STALE until the next build, which resumes from it): no build ever replaces a newer brief.
    current, new = parse_body(mine[0].get("body")), parse_body(body)
    carried = ((new or {}).get("c1b") or {}).get("prev") if isinstance((new or {}).get("c1b"), dict) else None
    have = brief_tuple(mine[0])
    want = {k: carried.get(k) for k in TUPLE_KEYS} if isinstance(carried, dict) else None
    # a published body that is not a brief (have None) carries no ledger this build could have carried: replaced (F1)
    if have is not None and (want != have or new.get("generation") != have["generation"] + 1):
        print(f"S1_TICK_BRIEF_PUBLISH_SKIPPED c1b_predecessor_not_carried published={json.dumps(have, sort_keys=True)} "
              f"carried={json.dumps(want, sort_keys=True)} generation={(new or {}).get('generation')}")
        result.update(reason="c1b_predecessor_not_carried")
        return mine[0]["number"]
    extras = mine[1:]
    absorbed = carried.get("absorbed") if isinstance(carried, dict) and isinstance(carried.get("absorbed"), list) else []
    keep = []
    for extra in extras:
        # an extra brief issue is closed only once THIS build carried exactly it (its tuple) and every gap and the halt
        # of it is in the brief written below; otherwise it stays open (two issues: S1 reads BRIEF_UNVERIFIED, fenced)
        t = brief_tuple(extra)
        if t is None or t not in absorbed or not preserved(parse_body(extra.get("body")), new):
            keep.append(extra["number"])
    # W5: a build that could not read the previous brief (c1b.carry UNKNOWN) carried nothing. It never replaces a
    # published brief that still holds a C1b halt: that halt exists nowhere else until S1 has posted it. The older
    # brief stays (S1 reads it as BRIEF_STALE), and the next build reads it and carries the halt as usual.
    if isinstance((new or {}).get("c1b"), dict) and new["c1b"].get("carry") == "UNKNOWN" \
            and isinstance((current or {}).get("c1b"), dict) and c1b_halt_ok(current["c1b"].get("halt")):
        print(f"S1_TICK_BRIEF_PUBLISH_SKIPPED carried_halt_kept run={current.get('run_id')} halt={current['c1b']['halt']['commit']}")
        result.update(reason="carried_halt_kept")
        return mine[0]["number"]
    try:
        if current is not None and stamp(current.get("generated_at")) > stamp(new.get("generated_at")) \
                and keep_published(gh, mine[0], current, now or datetime.now(timezone.utc)):
            print(f"S1_TICK_BRIEF_PUBLISH_SKIPPED newer_brief_published run={current.get('run_id')}")
            result.update(reason="newer_brief_published")
            return mine[0]["number"]
    except (ValueError, TypeError):
        pass                                                     # an unreadable current brief is replaced
    gh._request("PATCH", gh.url(f"issues/{mine[0]['number']}"), {"body": body})
    result.update(state="WRITTEN", reason="replaced")
    for extra in extras:
        if extra["number"] in keep:
            print(f"S1_TICK_BRIEF_DUPLICATE_KEPT issue={extra['number']} reason=ledger_not_proven_preserved")
        else:
            gh._request("PATCH", gh.url(f"issues/{extra['number']}"), {"state": "closed", "state_reason": "not_planned"})
    return mine[0]["number"]


def preserved(old, new):
    """Fix round 7 (R6-SH2), fix round 8 (R7-SH1): is every gap DETECTION and the halt of brief `old` in brief `new`?
    A gap is kept only by its exact detection (the same range id AND detected_at in new.c1b.gaps) or by a complete
    cleared record of exactly that detection (cleared_ok, the same range, detected_at and action id). Another detection
    of the same range, or a legacy cleared record that names the range only, never counts. A halt by the same commit."""
    if not isinstance(old, dict) or not isinstance(new, dict):
        return False
    nc = new.get("c1b") if isinstance(new.get("c1b"), dict) else {}
    have = {gap_detection(g) for g in nc.get("gaps") or [] if isinstance(g, dict) and isinstance(g.get("id"), str)
                                                     and isinstance(g.get("detected_at"), str)} | \
        {gap_detection(x) for x in nc.get("cleared") or [] if cleared_ok(x)}
    try:
        gaps = carried_gaps(old, datetime.now(timezone.utc))
    except C1bFail:
        return False
    if any(gap_detection(g) not in have for g in gaps):
        return False
    oc = old.get("c1b") if isinstance(old.get("c1b"), dict) else {}
    halt = oc.get("halt") if c1b_halt_ok(oc.get("halt")) else None
    return halt is None or (c1b_halt_ok(nc.get("halt")) and nc["halt"].get("commit") == halt.get("commit"))


def readback_line(gh, number, body):
    """R2-7, SHADOW: read the brief issue back after the write and print S1_BRIEF_DIGEST_V1 over the exact block bytes
    GitHub now serves. readback is MATCH (the served block is byte-identical to the one this run wrote), SUPERSEDED
    (the served brief is another run's: publish kept a newer brief, or a later build wrote after this one), MISMATCH
    (this run's brief, other bytes) or UNREADABLE. ONE read, on its own budget READBACK_API_CALLS, with the publish
    token (issues: write includes read). A failure is reported, never raised: in shadow the line is evidence only and
    the publish result is unchanged."""
    mine, want = parse_body(body), brief_digest(body)
    try:
        served = gh.get(f"issues/{int(number)}")
        served = served.get("body") if isinstance(served, dict) else None
    except Exception:                                            # noqa: BLE001  (unreadable is a state, not an error)
        served = None
    block = brief_block(served) if isinstance(served, str) else None
    got = None if block is None else hashlib.sha256(block.encode("utf-8")).hexdigest()
    if got is None:
        state = "UNREADABLE"
    elif got == want:
        state = "MATCH"
    else:
        try:
            other = strict_loads(block)
        except (ValueError, RecursionError):
            other = None
        same_run = isinstance(other, dict) and other.get("run_id") == (mine or {}).get("run_id") \
            and other.get("run_attempt") == (mine or {}).get("run_attempt")
        state = "MISMATCH" if same_run or not isinstance(other, dict) else "SUPERSEDED"
    return (f"{DIGEST_TOKEN} issue={number} run={(mine or {}).get('run_id')} main={(mine or {}).get('main')} "
            f"sha256={got or '-'} bytes={len(block.encode('utf-8')) if block is not None else '-'} expected_sha256={want} readback={state}")


def main(argv):
    global GIT_ENV
    mode = argv[1] if len(argv) > 1 else ""
    token = os.environ.get("GITHUB" + "_TOKEN", "")
    repo = os.environ.get("GITHUB_REPOSITORY", REPO)
    if repo != REPO:
        raise SystemExit(f"REFUSED: repository {repo} is not {REPO}")
    if mode == "due":
        # prints true or false. Only a workflow_run event can be "not due". An unreadable issue list reads as an old
        # brief; an unreadable RUN list means no fallback build (the hourly cron still builds).
        due = True
        if os.environ.get("GITHUB_EVENT_NAME") in FALLBACK_EVENTS:
            # ONE call when the run list already says no; TWO when the brief is fresh (the usual case); at most
            # DUE_API_CALLS when the brief is old and the jobs of up to three earlier runs must be read
            gh = GitHub(token, budget=DUE_API_CALLS)
            now = datetime.now(timezone.utc)
            run_id = os.environ.get("GITHUB_RUN_ID", "")
            run_id = int(run_id) if run_id.isdigit() else None
            try:
                runs = gh.get(f"actions/workflows/{Path(WORKFLOW_PATH).name}/runs", {"per_page": 100}).get("workflow_runs")
            except Exception:                                    # noqa: BLE001
                runs = None
            due = False
            issues, issues_read = None, False
            if isinstance(runs, list) and not recent_build(runs, now, run_id):
                try:
                    issues = gh.get("issues", {"labels": BRIEF_LABEL, "state": "open", "per_page": 20})
                except Exception:                                # noqa: BLE001
                    issues = None
                issues_read = True
                def jobs_of(rid):
                    try:
                        return gh.get(f"actions/runs/{rid}/jobs", {"per_page": 30}).get("jobs")
                    except Exception:                            # noqa: BLE001  (unreadable: counted as a started build)
                        return None
                due = fallback_due(issues, now, runs, run_id, jobs_of=jobs_of)
            if not due and os.environ.get("GITHUB_EVENT_NAME") == "push":
                # D1, independent of recent_build (a cron run of the last hour must not hide a code push): a push is a
                # squash merge or an owner push (data bots push with the job token, which starts no workflow); when
                # it changed code since the published brief, the brief is stale for S1 now. Git reads only for the
                # drift (no REST quota); at most one more REST read (the brief issue), within DUE_API_CALLS.
                if not issues_read:
                    try:
                        issues = gh.get("issues", {"labels": BRIEF_LABEL, "state": "open", "per_page": 20})
                    except Exception:                            # noqa: BLE001
                        issues = None
                GIT_ENV = token_git_env(token)
                due = code_drift_due(issues, lambda base, head: git_drift(CHECKOUT_ROOT, base, head),
                                     os.environ.get("GITHUB_SHA", ""))
        print("true" if due else "false")
        return 0
    if mode == "build":
        root, head_root, out = argv[2], argv[3], Path(argv[4])
        run = {"id": int(os.environ["GITHUB_RUN_ID"]), "attempt": int(os.environ["GITHUB_RUN_ATTEMPT"]), "event": os.environ["GITHUB_EVENT_NAME"]}
        GIT_ENV = token_git_env(token)
        gh = GitHub(token)
        snap = collect(gh, root, head_root, datetime.now(timezone.utc), run)
        brief = build_brief(snap)
        brief["api_calls"] = gh.calls
        brief["generated_at"] = iso(datetime.now(timezone.utc))  # the end of the reads: the age S1 measures starts here
        log_decision(brief, (snap.get("c1b") or {}).get("prev_log") if isinstance(snap.get("c1b"), dict) else None)
        body, _decision = render_issue(brief)
        out.write_text(body, encoding="utf-8")
        print(f"S1_TICK_BRIEF_BUILD run={run['id']} main={brief['main']} prs={len(brief['prs'])} next={len(brief['next'])} "
              f"complete={brief['complete']} calls={gh.calls} bytes={len(body)}")
        d = decision_v1.parse_decision(body) or {}
        print(f"S1_DECISION_V1 id={d.get('id')} executor={d.get('executor')} action={d.get('action')} pr={d.get('pr')} "
              f"head={d.get('head')} result={d.get('result')}")
        return 0
    if mode == "publish":
        body = Path(argv[2]).read_text(encoding="utf-8")
        brief = parse_body(body)
        if brief is None or str(brief.get("run_id")) != os.environ.get("GITHUB_RUN_ID") or brief.get("main") != os.environ.get("GITHUB_SHA"):
            raise SystemExit("PUBLISH_REFUSED: the brief does not belong to this run")
        if decision_of(body) is None:                            # section 0.2i: every published body carries its decision
            raise SystemExit("PUBLISH_REFUSED: the S1_DECISION_V1 block is missing or is not the decision of this brief")
        outcome = {}
        number = publish(GitHub(token, budget=PUBLISH_API_CALLS), body, result=outcome)
        # fix round 8: a skipped publish is never reported as published (the readback line below then says SUPERSEDED)
        if outcome.get("state") == "WRITTEN":
            print(f"S1_TICK_BRIEF_PUBLISHED issue={number} run={brief['run_id']} result=WRITTEN reason={outcome.get('reason')}")
        else:
            print(f"S1_TICK_BRIEF_NOT_PUBLISHED issue={number} run={brief['run_id']} result=SKIPPED reason={outcome.get('reason')}")
        print(readback_line(GitHub(token, budget=READBACK_API_CALLS), number, body))
        return 0
    raise SystemExit("usage: s1_tick_brief_v1.py due | build <main checkout> <head worktree dir> <out file> | publish <brief file>")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
