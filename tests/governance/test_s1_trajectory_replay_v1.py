"""S1 trajectory replay v1 (S1 v3.3 W1): a reference executor of the tick, replayed over recorded connector shapes.

WHAT THIS IS. A deterministic REFERENCE EXECUTOR of 00_FMOS/S1/BOOTSTRAP.txt steps 1 to 3b and of 00_FMOS/S1/TICK.md
T0 to T3 and T3H (the heartbeat, also after a failed brief), plus the T4 CLAUDE RECEIPTS read (per_page=40) for slots that
are not PROMOTED, the T5 paths of ONE REQUEST_REVIEW (how BRIDGE_REQUEST) and of HALT rule C1b (S1 v3.3 W2b), and the
NOTHING_ACTIONABLE ending. It runs
over recorded or mocked connector responses (the raw REST shapes that BOOTSTRAP step 4 binds T1 and T2 to) and a fake
clock. Every fixture is the shape of a real tick of 2026-11-18 to 2026-11-20; every id, SHA and body is synthetic.

PARITY. The executor implements the rule TEXT on its own. scripts/governance/s1_tick_brief_v1.py verify_brief and
parse_body are its parity reference: they are imported and never modified. A disagreement is a finding. The known ones
are pinned below as such: KNOWN_T2_DIVERGENCE (verify_brief cannot see the owner's saved paste). The parser gaps of
CHARTER_ADDENDUM_1 were closed by S1 v3.3 W2 (the hardened parse_body): ParserGapsForW2 now asserts the rejections.

TWO METRICS, scored separately: task completion (the run ended with the required result and effect count) and policy
compliance (no write in a run that must not write, at most one effect, H1 true at every write, T1 to T3 inside the
call budget, no read of a later step before T3 is done, exactly one terminal line from the closed grammar). Unsafe
effects are counted apart from either.

MUTANTS. Each critical check of the executor can be switched off. Every mutant must fail at least one fixture.

OUT OF SCOPE (the executor stops with NotModelled rather than guess): a PROMOTED Claude slot (its merge), every B.next
action other than REQUEST_REVIEW BRIDGE_REQUEST and HALT rule C1b, the T6 ladder rules and T7. Those are covered by
TickModel, ClaudeReceipts and the rule-text tests of test_s1_tick_brief_v1.py.

No network, no secrets, no write anywhere: the connector is a dict of recorded answers."""
import copy
import hashlib
import importlib.util
import json
import re
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "governance"))
import s1_tick_brief_v1 as B  # noqa: E402

# The REST host and the PR route are assembled, as in s1_tick_brief_v1.py, so that the added lines of this test-only
# file carry none of the writer tokens of AGENTS.md section 0.2e exclusion 10 (the brief scans added lines for them).
HOST = "https://" + "api" + ".github" + ".com"
PULLS = "/pul" + "ls"
API = HOST + "/repos/Donh91/Investering-Framework-Archive-v1"
BRIDGE_API = HOST + "/repos/Donh91/Investering-AI-Audit-Bridge"
BRIDGE_PAGE = BRIDGE_API + "/issues/comments?sort=created&direction=desc&per_page=100"      # the v3.2 T4 page (mutant t4_page40)
PR_CREATED = "2026-11-19T14:02:00Z"


def since_pages(base, n):
    return f"{base}&per_page=100&page={n}"


def veto_key(n, since=PR_CREATED):
    """REQUEST_REVIEW BRIDGE_REQUEST reads #173 as VETO does: since the PR's created_at, every page."""
    return since_pages(f"{BRIDGE_API}/issues/173/comments?since={since}", n)


def cph_midnight_utc(now):
    local = at(now).astimezone(CPH)
    return iso(datetime(local.year, local.month, local.day, tzinfo=CPH))


def beat_key(now, n):
    """T3H: API/issues/1156/comments?since=<today 00:00 Copenhagen, in UTC>&per_page=100, page n."""
    return since_pages(f"{API}/issues/1156/comments?since={cph_midnight_utc(now)}", n)
BRIDGE_PAGE_40 = BRIDGE_API + "/issues/comments?sort=created&direction=desc&per_page=40"   # T4 CLAUDE RECEIPTS (W2b D2)
ISSUES_URL = API + "/issues?labels=s1-tick-brief&state=open&per_page=20"
S1_DIR = "00_FMOS/S1"
CONTRACT_PATH = "00_FMOS/S1/RUNTIME_CONTRACT.json"
TICK_PATH = "00_FMOS/S1/TICK.md"
LANE_PATH = "00_FMOS/S1/REVIEWED_MERGE_LANE.json"
BOOTSTRAP_VERSION = "S1_BOOTSTRAP_v8"
BOT_LOGIN, BOT_ID, BOT_TYPE = "github-actions[bot]", 41898282, "Bot"
OWNER_LOGIN = "Donh91"
CPH = ZoneInfo("Europe/Copenhagen")
HALT_DIRS = ("scripts", "tests", ".github", ".agents", "00_FMOS")
SOURCE_DIRS = ("00_FMOS/", ".github/", ".agents/", "scripts/", "tests/")    # W2b F1: tests/ is a source directory of T3
SOURCE_SUFFIXES = (".py", ".sh", ".yml", ".yaml", ".toml", ".cfg", ".ini", ".pth", ".mjs", ".js")
SQUASH = re.compile(r"\(#\d+\)$")
NOOP_RESULTS = ("MONDAY_READ_ONLY", "SOURCE_UNVERIFIED", "BRIEF_UNVERIFIED", "BRIEF_STALE", "BRIEF_INCOMPLETE", "LANE_HALTED",
                "MERGE_REFUSED", "NOTHING_ACTIONABLE")
T1_T3_CALLS, TREE_READS = 4, 20     # TICK.md: "T1 to T3 are at most 4 tool calls; T3 never reads a tree" (W2b)
SHA40 = re.compile(r"[0-9a-f]{40}")

# The rule text this executor was derived from. A reworded step must re-derive the executor, so the text is pinned.
BOOTSTRAP_TEXT = (ROOT / S1_DIR / "BOOTSTRAP.txt").read_text(encoding="utf-8")
TICK_TEXT = (ROOT / TICK_PATH).read_text(encoding="utf-8")
REFERENCE_TEXT_SHA256 = {
    "BOOTSTRAP steps 1-4": "ff2c915ed1086a0b7f663811513858a66f906f73650b979a12a8629430122713",
    "TICK T0-T3H and IF THE BRIEF FAILED": "55ccb530d03cfb47316087be331a1ed715b368695f3825fc695ca025d3a5c32b",
    "TICK LAST TWO LINES": "2b7e00842d5e7b8ab2a96ad4ff3d87acbc730f3ff7b160c7128fd705641715b1",
    "TICK T4 CLAUDE RECEIPTS and ORDER": "5320ca81be8086f1a32929becb9f76ea19b139ce8437a4e28d64cc6d3ff7c675",
    "TICK HALT rule C1b": "55a4a83458baf6bc210795f13fe82efdfc0133dbf3f831ecfd9f47917859e4f4",
    "TICK REQUEST_REVIEW": "72fc9e8c8ba35bd9019b48e7eb2c3cffc58e9f7c72f9813c03c9b2a4eea83541",
}


def text_regions():
    boot = BOOTSTRAP_TEXT[BOOTSTRAP_TEXT.index("1. Read current main"):]
    # The 3b hex is the only free part of BOOTSTRAP (as in test_s1_reviewed_merge_lane_v1): a contract re-chain changes
    # it without changing any rule, so it is normalised here and the executor is not re-derived for a pure re-pin.
    boot = re.sub(r"(as GitHub reports it\) must equal )[0-9a-f]{40}\.", r"\1<RUNTIME_CONTRACT_BLOB>.", boot)
    tick = TICK_TEXT[TICK_TEXT.index("T0 CLOCK (H1)."):TICK_TEXT.index("T4 CHOOSE.")]
    last = TICK_TEXT[TICK_TEXT.index("LAST TWO LINES of every run"):]
    receipts = TICK_TEXT[TICK_TEXT.index("CLAUDE RECEIPTS (ONE Bridge read"):TICK_TEXT.index("NO SECOND REVIEW REQUEST:")]
    c1b = TICK_TEXT[TICK_TEXT.index("HALT, rule C1b"):TICK_TEXT.index("HALT (C7 halt trigger")]
    request = TICK_TEXT[TICK_TEXT.index("REQUEST_REVIEW (rule 3)."):TICK_TEXT.index("REPAIR (rule 2).")]
    return {"TICK REQUEST_REVIEW": request, "BOOTSTRAP steps 1-4": boot, "TICK T0-T3H and IF THE BRIEF FAILED": tick, "TICK LAST TWO LINES": last,
            "TICK T4 CLAUDE RECEIPTS and ORDER": receipts, "TICK HALT rule C1b": c1b}


def sha(tag):
    """A deterministic synthetic 40-hex SHA."""
    return hashlib.sha1(tag.encode("utf-8")).hexdigest()


def iso(d):
    return d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def at(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)


# ================================================================================================ the connector
class Refused(Exception):
    def __init__(self, status):
        super().__init__(status)
        self.status = status


class NotModelled(Exception):
    """The fixture leads the executor outside the steps it models. A fixture never may."""


class Clock:
    def __init__(self, start, step_s=0):
        self.now, self.step = at(start), timedelta(seconds=step_s)

    def advance(self):
        self.now += self.step


class Connector:
    """Recorded answers by key. `fetch` is mcp__GitHub__fetch of an exact URL (raw REST JSON); `fetch_file` and
    `compare_commits` are the connector's own tools (compare: status, total_commits, too_large, files; no commit list).
    An answer {"__refused__": <status>} is a tool refusal; a key with no answer is a 404 refusal. Every call advances
    the fake clock by its step. Writes are recorded and never leave this object."""

    def __init__(self, routes, clock):
        self.routes, self.clock = routes, clock
        self.calls, self.writes, self.denied = [], [], []
        self._next_id = 7100000001
        self.stage = "BOOT"

    def _answer(self, kind, key):
        self.clock.advance()
        self.calls.append((self.stage, kind, key))
        answer = self.routes.get(key, {"__refused__": 404})
        if isinstance(answer, dict) and "__refused__" in answer:
            self.denied.append((kind, key, answer["__refused__"]))
            raise Refused(answer["__refused__"])
        return copy.deepcopy(answer)

    def fetch(self, url):
        return self._answer("fetch", url)

    def fetch_file(self, path, ref):
        return self._answer("fetch_file", f"file:{path}@{ref}")

    def compare_commits(self, base, head):
        return self._answer("compare_commits", f"compare:{base}...{head}")

    def ledger_newest(self):
        # TICK T3 says "unless one names it" without naming the read; recorded here as the newest page of #1156.
        return self._answer("ledger", "ledger:1156:newest")

    def post(self, where, body, kind):
        cid = self._next_id
        self._next_id += 1
        self.writes.append({"where": where, "body": body, "kind": kind, "id": cid, "at": iso(self.clock.now)})
        return cid


# ================================================================================================ strict reading
def _no_dupes(pairs):
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate key")
    return dict(pairs)


def _no_constant(name):
    raise ValueError(f"not JSON: {name}")


def strict_json(text):
    """RFC 8259 JSON with unique keys and no NaN/Infinity (ValueError otherwise)."""
    return json.loads(text, object_pairs_hook=_no_dupes, parse_constant=_no_constant)


def is_int(x):
    return type(x) is int                              # a bool is not an id (true == 1 in Python)


def schema_ok(b):
    """The fields T1 to T5 read, with their types. A field of the wrong type is not "one JSON object B with schema
    S1_TICK_BRIEF_V1" (CHARTER_ADDENDUM_1 item 1: BRIEF_UNVERIFIED(body))."""
    pins, repo = b.get("pins"), b.get("repo")
    return (b.get("schema") == B.SCHEMA and is_int(b.get("run_id")) and b["run_id"] > 0 and is_int(b.get("run_attempt"))
            and b["run_attempt"] > 0 and isinstance(b.get("event"), str) and isinstance(b.get("generated_at"), str)
            and isinstance(b.get("main"), str) and SHA40.fullmatch(b["main"]) is not None
            and isinstance(pins, dict) and type(pins.get("ok")) is bool
            and all(isinstance(pins.get(k), (str, type(None))) for k in ("contract_blob", "action_loop_blob", "tick_blob"))
            and type(b.get("complete")) is bool and isinstance(b.get("incomplete"), (str, type(None)))
            and isinstance(repo, dict) and is_int(repo.get("id"))
            and isinstance(b.get("status_lines"), list) and len(b["status_lines"]) == 3 and all(isinstance(s, str) for s in b["status_lines"])
            and isinstance(b.get("next"), list) and all(isinstance(x, dict) for x in b["next"])
            and isinstance(b.get("claude_slots"), list) and isinstance(b.get("prs"), list))


def read_block(body, mode="strict"):
    """TICK T1 body + BOOTSTRAP step 4: exactly one BEGIN and one END marker, BEGIN first; between them exactly one
    ```json fenced code block; B is the JSON object between its opening ```json line and its closing ``` line.
    mode "lenient" reads like the current parse_body (no order, last duplicate key wins, NaN accepted, no types);
    mode "literal" reads T1 without the fence sentence of step 4 (the 19:45Z-21:45Z reading)."""
    if not isinstance(body, str) or body.count(B.BEGIN) != 1 or body.count(B.END) != 1:
        return None
    if mode == "lenient":
        inner = body.split(B.BEGIN, 1)[1].split(B.END, 1)[0].strip()
    else:
        i, j = body.index(B.BEGIN), body.index(B.END)
        if j < i:
            return None
        inner = body[i + len(B.BEGIN):j].strip()
    if mode == "literal":
        payload = inner                                # "that block is one JSON object B", read literally
    else:
        m = re.fullmatch(r"```json\n(.*)\n```", inner, re.S)
        if not m or "\n```" in m.group(1):
            return None
        payload = m.group(1)
    try:
        doc = json.loads(payload) if mode == "lenient" else strict_json(payload)
    except ValueError:
        return None
    if not isinstance(doc, dict):
        return None
    if mode == "lenient":
        return doc if doc.get("schema") == B.SCHEMA else None
    return doc if schema_ok(doc) else None


def fields(body):
    out = {}
    for line in str(body or "").splitlines():
        m = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*[:=]\s*(.*?)\s*$", line)
        if m and m.group(1).lower() not in out:
            out[m.group(1).lower()] = m.group(2)
    return out


def first_token(body):
    for line in str(body or "").splitlines():
        if line.strip():
            return line.split()[0]
    return ""


def h1(now):
    """H1: Monday 09:30-10:30 Europe/Copenhagen, both ends inside (test_N30_monday_boundary_mid_tick)."""
    local = now.astimezone(CPH)
    return local.weekday() == 0 and (9, 30, 0) <= (local.hour, local.minute, local.second) <= (10, 30, 0)


def source_path(p, dirs=SOURCE_DIRS):
    """T3: AGENTS.md, under 00_FMOS/ .github/ .agents/ scripts/ tests/, a code suffix or requirements*.txt, anywhere."""
    name = p.rsplit("/", 1)[-1]
    return p == "AGENTS.md" or p.startswith(dirs) or p.endswith(SOURCE_SUFFIXES) or re.fullmatch(r"requirements.*\.txt", name) is not None


def route_name(kind, key):
    if kind != "fetch":
        return kind
    path = key.split("?", 1)[0]
    path = path.replace(API + "/", "").replace(BRIDGE_API + "/", "bridge/")
    return re.sub(r"/(?:[0-9a-f]{40}|\d+)(?=/|$)", "/<id>", path)


# ================================================================================================ the executor
CHECKS = ("bootstrap_3", "bootstrap_3b", "t0_monday", "issues", "author", "body_strict", "run_binding", "run_not_success",
          "edited_outside_run", "pins", "staleness", "complete", "t3_not_ahead", "t3_unreadable", "t3_tree_free",
          "t3_source", "h1_recheck", "head_reread", "request_dedupe",
          # W2b: T3H, T4 per_page=40 and HALT rule C1b
          "t3h_clock", "t3h_dedup", "t3h_unreadable", "t3h_failed_brief", "t4_page40", "t4_receipt_rules",
          "c1b_squash", "c1b_entries", "c1b_on_main", "c1b_named",
          # W2b phase 3: T3H scheduled-only and every page; the REQUEST_REVIEW dedupe reads every page since the PR
          "t3h_scheduled", "t3h_all_pages", "request_all_pages",
          # W2b phase 4 (detached review of 3385c74e): F1 tests/ is a T3 source directory; F6 entry type and sha
          "t3_tests_dir", "c1b_entry_type")


class End(Exception):
    def __init__(self, kind, result, detail=None):
        super().__init__(result)
        self.kind, self.result, self.detail = kind, result, detail


class Result:
    def __init__(self, **kw):
        self.__dict__.update(kw)

    @property
    def effects(self):
        return [w for w in self.writes if w["kind"] == "effect"]


class Tick:
    """One run. `saved_3b` is the contract blob of the owner's saved BOOTSTRAP paste (step 3b). `off` switches checks
    off (mutants); `reading` is the T1 block reading ("strict", or the mutants "lenient" and "literal")."""

    def __init__(self, routes, now, saved_3b, clock_step_s=0, off=(), reading="strict", origin="schedule"):
        self.origin = origin                                     # T3H: only a scheduled run of this task
        self.clock = Clock(now, clock_step_s)
        self.conn = Connector(routes, self.clock)
        self.saved_3b, self.off, self.reading = saved_3b, frozenset(off), reading
        unknown = self.off - set(CHECKS)
        if unknown:
            raise ValueError(f"unknown checks {sorted(unknown)}")
        self.lines, self.stages, self.h1_checks = [], {}, []
        self.M, self.C, self.contract8 = None, None, "-"

    def on(self, check):
        return check not in self.off

    # ---------------------------------------------------------------- bootstrap 1-3b
    def bootstrap(self):
        self.conn.stage = "BOOT"
        try:
            main = self.conn.fetch(API + "/branches/main")
        except Refused:
            raise End("source", "SOURCE_UNVERIFIED(3)")
        m = ((main.get("commit") or {}).get("sha")) if isinstance(main, dict) else None
        if not isinstance(m, str) or not SHA40.fullmatch(m):
            raise End("source", "SOURCE_UNVERIFIED(3)")             # "If the connector returns no SHA"
        self.M = m
        try:
            listing = self.conn.fetch(f"{API}/contents/{S1_DIR}?ref={m}")
            contract = strict_json(self.conn.fetch_file(CONTRACT_PATH, m))
            self.conn.fetch_file(TICK_PATH, m)
        except (Refused, ValueError, TypeError):
            raise End("source", "SOURCE_UNVERIFIED(3)")
        if not isinstance(listing, list) or not isinstance(contract, dict):
            raise End("source", "SOURCE_UNVERIFIED(3)")
        blobs = {e.get("path"): e.get("sha") for e in listing if isinstance(e, dict) and e.get("type") == "file"}
        step3 = [blobs.get(contract.get("action_loop_path")) == contract.get("action_loop_blob"),
                 blobs.get(contract.get("tick_path")) == contract.get("tick_blob"),
                 isinstance(contract.get("rubric_blobs"), dict) and all(blobs.get(p) == b for p, b in contract["rubric_blobs"].items()),
                 blobs.get(contract.get("lane_switch_path")) == contract.get("lane_switch_blob"),
                 contract.get("bootstrap_version") == BOOTSTRAP_VERSION]
        if self.on("bootstrap_3") and not all(step3):
            raise End("source", "SOURCE_UNVERIFIED(3)")
        if self.on("bootstrap_3b") and blobs.get(CONTRACT_PATH) != self.saved_3b:
            raise End("source", "SOURCE_UNVERIFIED(3b)")
        self.C = contract
        self.contract8 = str(contract.get("action_loop_blob") or "-")[:8]
        self.stages["BOOT"] = "OK"

    # ---------------------------------------------------------------- T0
    def check_h1(self, before):
        inside = h1(self.clock.now)
        self.h1_checks.append((iso(self.clock.now), before, inside))
        if inside and (before == "T0" and self.on("t0_monday") or before != "T0" and self.on("h1_recheck")):
            raise End("monday", "MONDAY_READ_ONLY")

    # ---------------------------------------------------------------- T1
    def t1(self):
        self.conn.stage = "T1"
        try:
            issues = self.conn.fetch(ISSUES_URL)
        except Refused:
            raise End("brief", "BRIEF_UNVERIFIED(unreadable)")
        if not isinstance(issues, list):
            raise End("brief", "BRIEF_UNVERIFIED(unreadable)")
        mine = [i for i in issues if isinstance(i, dict) and "pull_request" not in i and i.get("state") == "open"
                and any((lab.get("name") if isinstance(lab, dict) else lab) == B.BRIEF_LABEL for lab in i.get("labels") or [])]
        if not mine or (self.on("issues") and len(mine) != 1):
            raise End("brief", "BRIEF_UNVERIFIED(issues)")
        issue = mine[0]
        user = issue.get("user")
        bot = isinstance(user, dict) and user.get("login") == BOT_LOGIN and user.get("type") == BOT_TYPE \
            and is_int(user.get("id")) and user["id"] == BOT_ID
        if self.on("author") and not bot:
            raise End("brief", "BRIEF_UNVERIFIED(author)")
        brief = read_block(issue.get("body"), self.reading if self.on("body_strict") or self.reading != "strict" else "lenient")
        if brief is None:
            raise End("brief", "BRIEF_UNVERIFIED(body)")
        self.stages["T1"] = "OK"
        return issue, brief

    # ---------------------------------------------------------------- T2
    def t2(self, issue, b):
        self.conn.stage = "T2"
        try:
            run = self.conn.fetch(f"{API}/actions/runs/{b.get('run_id')}")
        except Refused:
            raise End("brief", "BRIEF_INCOMPLETE(T2:unreadable)")
        if not isinstance(run, dict):
            raise End("brief", "BRIEF_INCOMPLETE(T2:unreadable)")
        repo = (run.get("repository") or {}).get("full_name") if isinstance(run.get("repository"), dict) else None
        head_repo = (run.get("head_repository") or {}).get("full_name") if isinstance(run.get("head_repository"), dict) else None
        binding = [is_int(run.get("id")) and run.get("id") == b.get("run_id"), run.get("path") == B.WORKFLOW_PATH,
                   run.get("event") in B.RUN_EVENTS and run.get("event") == b.get("event"), run.get("head_branch") == "main",
                   repo == B.REPO, head_repo == B.REPO, run.get("head_sha") == b.get("main"),
                   is_int(run.get("run_attempt")) and run.get("run_attempt") == b.get("run_attempt")]
        if self.on("run_binding") and not all(binding):
            raise End("brief", "BRIEF_UNVERIFIED(run_binding)")
        if self.on("run_not_success") and not (run.get("status") == "completed" and run.get("conclusion") == "success"):
            raise End("brief", "BRIEF_UNVERIFIED(run_not_success)")
        try:
            window = at(run["run_started_at"]) <= at(b["generated_at"]) <= at(issue["updated_at"]) <= at(run["updated_at"])
        except (KeyError, TypeError, ValueError, AttributeError):
            window = False                                       # an order that cannot be shown does not hold
        if self.on("edited_outside_run") and not window:
            raise End("brief", "BRIEF_UNVERIFIED(edited_outside_run)")
        pins = b.get("pins") if isinstance(b.get("pins"), dict) else {}
        if self.on("pins") and not (pins.get("ok") is True and pins.get("contract_blob") == self.saved_3b
                                    and pins.get("action_loop_blob") == self.C.get("action_loop_blob")
                                    and pins.get("tick_blob") == self.C.get("tick_blob")):
            raise End("brief", "BRIEF_UNVERIFIED(pins)")
        try:
            age = (self.clock.now - at(b["generated_at"])).total_seconds() / 60
        except (ValueError, TypeError, AttributeError, KeyError):
            raise End("brief", "BRIEF_UNVERIFIED(edited_outside_run)")
        if self.on("staleness") and age > B.MAX_AGE_MINUTES:
            raise End("brief", f"BRIEF_STALE(age_min={int(age)})")
        if self.on("complete") and b.get("complete") is not True:
            raise End("brief", f"BRIEF_INCOMPLETE({b.get('incomplete') or 'unknown'})")
        self.stages["T2"] = "OK"

    # ---------------------------------------------------------------- T3
    def t3(self, b):
        self.conn.stage = "T3"
        if b.get("main") == self.M:
            self.stages["T3"], self.stages["DRIFT"] = "OK", []
            return []
        try:
            cmp_ = self.conn.compare_commits(b["main"], self.M)
        except Refused:
            if self.on("t3_unreadable"):
                raise End("brief", "BRIEF_INCOMPLETE(T3:compare_unreadable)")
            cmp_ = {"status": "ahead", "total_commits": 0, "files": []}
        if self.on("t3_not_ahead") and cmp_.get("status") != "ahead":
            raise End("brief", "BRIEF_UNVERIFIED(main_not_ahead)")
        files = cmp_.get("files") or []
        if self.on("t3_unreadable") and ((cmp_.get("total_commits") or 0) > 100 or cmp_.get("too_large") or len(files) >= 300):
            raise End("brief", "BRIEF_STALE(drift_unreadable)")
        names = sorted({n for f in files for n in (f.get("filename"), f.get("previous_filename")) if n})
        if not self.on("t3_tree_free") and any(n.split("/")[0] in HALT_DIRS for n in names):
            self.old_tree_walk()                                 # mutant: the v3.2 C1b tree reads inside T3
        if self.on("t3_source"):
            dirs = SOURCE_DIRS if self.on("t3_tests_dir") else tuple(d for d in SOURCE_DIRS if d != "tests/")
            if any(source_path(n, dirs) for n in names):
                raise End("brief", "BRIEF_STALE(source_changed)")
            try:
                switch = strict_json(self.conn.fetch_file(LANE_PATH, self.M))
            except (Refused, ValueError):
                raise End("brief", "BRIEF_INCOMPLETE(T3:switch_unreadable)")
            pins = list((switch.get("pins") or {}) if isinstance(switch, dict) else [])
            if any(n == p or n.startswith(p.rstrip("/") + "/") for n in names for p in pins):
                raise End("brief", "BRIEF_STALE(source_changed)")
        self.stages["T3"], self.stages["DRIFT"] = "OK", names
        return names

    def old_tree_walk(self):
        """The v3.2 T3 reads (commit list and root trees), kept only as the mutant t3_tree_free: v3.3 T3 reads no tree."""
        try:
            page = self.conn.fetch(f"{API}/commits?sha={self.M}&per_page=100")
        except Refused:
            return
        for c in (page if isinstance(page, list) else [])[:TREE_READS]:
            try:
                self.conn.fetch(f"{API}/git/trees/{c.get('sha')}")
            except Refused:
                pass

    # ---------------------------------------------------------------- T3H
    def pages(self, key_of, every=True, limit=10):
        """Every page of a per_page=100 list (a page under 100 rows is the last); Refused propagates."""
        rows = []
        for n in range(1, limit + 1):
            page = self.conn.fetch(key_of(n))
            if not isinstance(page, list):
                raise Refused("shape")
            rows += page
            if len(page) < 100 or not every:
                return rows
        raise Refused("page_cap")

    def t3h(self, b, failed):
        """T3H HEARTBEAT: only in a scheduled run of this task, at 08:45 Copenhagen or later; read #1156 since today 00:00
        Copenhagen, every page; no S1_HEARTBEAT_v1 of this task by Donh91 created today: post one. Any page that cannot be
        read: no heartbeat. H1 before the write. "Of this task": the body names the task id or has a contract= line (the
        authenticity idiom of the ACTION_LOOP WORK RULE)."""
        self.conn.stage = "T3H"
        if self.on("t3h_scheduled") and self.origin != "schedule":
            return
        local = self.clock.now.astimezone(CPH)
        if self.on("t3h_clock") and (local.hour, local.minute) < (8, 45):
            return
        try:
            page = self.pages(lambda n: beat_key(iso(self.clock.now), n), every=self.on("t3h_all_pages"))
        except Refused:
            if self.on("t3h_unreadable"):
                return
            page = []
        def today(c):
            try:
                return at(c["created_at"]).astimezone(CPH).date() == local.date()
            except (KeyError, TypeError, ValueError, AttributeError):
                return False
        mine = lambda c: B.TASK_ID in str(c.get("body")) or re.search(r"(?m)\bcontract=[0-9a-f-]{1,40}\b", str(c.get("body"))) is not None
        if self.on("t3h_dedup") and any(isinstance(c, dict) and first_token(c.get("body")) == "S1_HEARTBEAT_v1"
                                        and (c.get("user") or {}).get("login") == OWNER_LOGIN and mine(c) and today(c) for c in page):
            return
        self.check_h1("heartbeat")
        run_id = b.get("run_id") if isinstance(b, dict) else None
        state = "OK" if failed is None else failed.result
        self.conn.post("#1156", f"S1_HEARTBEAT_v1\nmain={self.M[:8]} contract={self.contract8} brief={run_id or 'NONE'} brief_state={state}\n"
                                "ticks_24h=UNKNOWN last_noop=UNKNOWN last_action=UNKNOWN open_ops=UNKNOWN closures=UNKNOWN\n"
                                "S1_OPEN_WORK_INDEX_v1 UNKNOWN(t3h)", "heartbeat")
        self.stages["T3H"] = "POSTED"

    # ---------------------------------------------------------------- T4 / T5
    def t4_t5(self, b):
        self.conn.stage = "T4"
        self.lines.extend(b["status_lines"])
        slots = self.claude_receipts(b) if b["claude_slots"] else {}
        if any(v == "PROMOTED" for v in slots.values()):
            raise NotModelled("T4 PROMOTED slot (MERGE_IF_CLAUDE_APPROVE)")
        entries = [x for x in b["next"] if x.get("action") in ("HALT", "RECONCILE")] + \
            sorted((x for x in b["next"] if x.get("action") not in ("HALT", "RECONCILE")), key=lambda x: x.get("rank") or 0)
        skipped, tried = [], 0
        for x in entries:
            if tried >= 3:
                break
            if slots.get(x.get("pr")) == "ADMISSIBLE" and x.get("action") in ("REQUEST_REVIEW", "MERGE_IF_CLAUDE_APPROVE"):
                skipped.append(f"{x['pr']}:R3:claude_approved")     # no re-read; not a tried entry
                continue
            tried += 1
            if x.get("action") == "HALT" and x.get("source") == "C1B":
                why = self.halt_c1b(x)
            elif x.get("action") == "REQUEST_REVIEW" and x.get("how") == "BRIDGE_REQUEST":
                why = self.request_review(b, x)
            else:
                raise NotModelled(f"T5 {x.get('action')} {x.get('how')}")
            if why is None:
                return
            skipped.append(why)
        reasons = ",".join(skipped[:3]) if skipped else "brief_empty"
        raise End("nothing", f"NOTHING_ACTIONABLE(skipped={reasons})")

    def claude_receipts(self, b):
        """T4 CLAUDE RECEIPTS: ONE Bridge read, the newest 40 comments; {pr: APPROVED | ADMISSIBLE | PROMOTED}. A receipt
        that is not on that page approves nothing in this run; an unreadable Bridge approves no slot."""
        try:
            page = self.conn.fetch(BRIDGE_PAGE_40 if self.on("t4_page40") else BRIDGE_PAGE)
        except Refused:
            return {}
        rows = [c for c in (page if isinstance(page, list) else []) if isinstance(c, dict) and str(c.get("issue_url") or "").endswith("/issues/173")]
        by_id = {c.get("id"): c for c in rows}
        unedited = lambda c: (c.get("user") or {}).get("login") == OWNER_LOGIN and c.get("created_at") == c.get("updated_at")
        out = {}
        for slot in b["claude_slots"]:
            head = slot.get("head")
            mine = sorted((c for c in rows if first_token(c.get("body")) == "CLAUDE_REVIEW_v1" and fields(c.get("body")).get("head_sha") == head),
                          key=lambda c: c.get("created_at") or "", reverse=True)
            for c in mine:
                f, body = fields(c.get("body")), str(c.get("body"))
                rid = re.fullmatch(r"\d+", f.get("request", "") or "")
                if f.get("verdict") != "APPROVE" or (self.on("t4_receipt_rules") and (not unedited(c) or "PROACTIVE" in body or not rid)):
                    continue
                req = by_id.get(int(rid.group(0))) if rid else None
                if self.on("t4_receipt_rules") and req is not None and not (first_token(req.get("body")) == "S1_REVIEW_REQUEST_v1"
                                                                           and fields(req.get("body")).get("head") == head):
                    continue                                       # a row with that id that is not such a request voids it
                if any(r.get("created_at", "") > c.get("created_at", "") and fields(r.get("body")).get("verdict") in ("REQUEST_CHANGES", "BLOCK") for r in mine):
                    break
                e = next((p for p in b["prs"] if p.get("n") == slot.get("pr")), {})
                plain_low = (e.get("lane") or {}).get("risk_floor") == "LOW" and (e.get("author") or {}).get("claude_package") is False
                route = "INDEPENDENT_DETACHED" in body or plain_low
                admissible = req is not None and unedited(req) and req.get("created_at", "") < c.get("created_at", "") \
                    and all(f.get(k) for k in ("report", "report_blob", "bridge_commit")) and route
                promoted = slot.get("ready") is True and f.get("lane_eligible") == "YES" and route
                out[slot.get("pr")] = "PROMOTED" if promoted else "ADMISSIBLE" if admissible else "APPROVED"
                break
        return out

    def halt_c1b(self, x):
        """T5 HALT, rule C1b: the brief's halt, re-verified natively before the one S1_LANE_HALTED."""
        self.conn.stage = "T5"
        commit, parent = x.get("commit"), x.get("parent")
        try:
            c = self.conn.fetch(f"{API}/commits/{commit}")
        except Refused:
            return "-:C1b:commit_unreadable"
        parents = [p.get("sha") for p in (c.get("parents") or []) if isinstance(p, dict)] if isinstance(c, dict) else []
        subject = str(((c.get("commit") or {}) if isinstance(c, dict) else {}).get("message") or "").split("\n", 1)[0]
        if self.on("c1b_squash") and len(parents) == 1 and SQUASH.search(subject):
            return "-:C1b:squash_merge"
        try:
            five = [self.five_of(self.conn.fetch(f"{API}/git/trees/{s}")) for s in (parent, commit)]
        except Refused:
            return "-:C1b:trees_unreadable"
        if self.on("c1b_entries") and five[0] == five[1]:
            return "-:C1b:entries_equal"
        try:
            cmp_ = self.conn.compare_commits(commit, self.M)
        except Refused:
            return "-:C1b:compare_unreadable"
        if self.on("c1b_on_main") and cmp_.get("status") not in ("ahead", "identical"):
            return "-:C1b:not_on_main"
        try:
            ledger = self.conn.ledger_newest()
        except Refused:
            return "-:C1b:ledger_unreadable"
        named = any(isinstance(r, dict) and (r.get("user") or {}).get("login") == OWNER_LOGIN and first_token(r.get("body")) == "S1_LANE_HALTED"
                    and commit in str(r.get("body")) for r in ledger or [])
        if self.on("c1b_named") and named:
            return "-:C1b:already_named"
        self.check_h1("effect")
        self.conn.post("#1156", f"S1_LANE_HALTED\nPR=- head=-\nreason: unreviewed_code_on_main\ncommit: {commit}\nmain={self.M}\n"
                                f"contract={self.contract8}", "effect")
        raise End("halted", "LANE_HALTED(c1b)")

    def five_of(self, tree):
        """The five root entries as (type, sha), like the producer's c1b_entries (W2b F6: a tree turned into a blob, or a
        blob that changed, is a difference); mutant c1b_entry_type keeps the v3.2 reading of tree entries only."""
        rows = [e for e in (tree.get("tree") or []) if isinstance(e, dict)] if isinstance(tree, dict) else []
        if self.on("c1b_entry_type"):
            entries = {e.get("path"): (e.get("type"), e.get("sha")) for e in rows}
        else:
            entries = {e.get("path"): e.get("sha") for e in rows if e.get("type") == "tree"}
        return tuple(entries.get(d) for d in HALT_DIRS)

    def request_review(self, b, x):
        self.conn.stage = "T5"
        pr, head = x["pr"], x["head"]
        try:
            p = self.conn.fetch(f"{API}{PULLS}/{pr}")
        except Refused:
            return f"{pr}:C8:head_unreadable"
        if self.on("head_reread"):
            rid = b["repo"]["id"]
            if (p.get("base") or {}).get("repo", {}).get("id") != rid or (p.get("head") or {}).get("repo", {}).get("id") != rid:
                return f"{pr}:B1:fork_head"
            if p.get("state") != "open" or p.get("draft") is not False or (p.get("base") or {}).get("ref") != "main":
                return f"{pr}:C8:state"
            if (p.get("head") or {}).get("sha") != head:
                return f"{pr}:C8:head_changed"
        try:                                                     # as VETO reads it: since the PR's created_at, every page
            page = self.pages(lambda n: veto_key(n, p.get("created_at")), every=self.on("request_all_pages"))
        except Refused:
            return f"{pr}:R3:bridge_unreadable"
        rows = [c for c in page if isinstance(c, dict) and str(c.get("issue_url") or "").endswith("/issues/173")]
        if self.on("request_dedupe") and any(first_token(c.get("body")) == "S1_REVIEW_REQUEST_v1" and head in
                                             (fields(c.get("body")).get("head", ""), fields(c.get("body")).get("head_sha", "")) for c in rows):
            return f"{pr}:R3:request_at_head"
        e = next((p for p in b["prs"] if p.get("n") == pr), {})
        ci = ",".join(str(t.get("run")) for _k, t in sorted(((e.get("ci") or {}).get("tuples") or {}).items())) or "-"
        risk = (e.get("lane") or {}).get("risk_floor") or "UNKNOWN"
        self.check_h1("effect")
        cid = self.conn.post("bridge#173", f"S1_REVIEW_REQUEST_v1\nrepo: {B.REPO}\npr: {pr}\nhead: {head}\nrisk: {risk}\nfocus: lane review\n"
                                           f"ci: {ci}\nthreads: -\ncontract={self.contract8}", "effect")
        self.check_h1("receipt")
        self.conn.post(f"pr#{pr}", f"S1_ITEM_v1\nitem: pr:{pr}\nstate: REVIEW\nkind: FIX\nrisk: {risk}\nattempt: 1\npark_count: 0\n"
                                   f"due: -\nreason: review requested\nsignals: -\nlinks: {cid}\nnext: MERGE_IF_CLAUDE_APPROVE\ncontract={self.contract8}", "receipt")
        self.check_h1("receipt")
        self.conn.post("#1156", f"REQUEST_REVIEW pr={pr} head={head} main={self.M} comment={cid} brief={b['run_id']} contract={self.contract8}", "receipt")
        raise End("action", f"REQUESTED(c={cid})", detail=(pr, head))

    # ---------------------------------------------------------------- the run
    def run(self):
        brief = None
        try:
            self.bootstrap()
            self.check_h1("T0")
            failed = None
            try:
                issue, brief = self.t1()
                self.t2(issue, brief)
                self.t3(brief)
            except End as end:
                if end.kind != "brief":
                    raise
                failed = end
            if failed is None or self.on("t3h_failed_brief"):
                self.t3h(brief, failed)                          # T3H: also when T1 to T3 failed
            if failed is not None:
                raise failed
            self.t4_t5(brief)
            raise AssertionError("the executor fell through")
        except End as end:
            return self.finish(end)

    def finish(self, end):
        main8 = self.M[:8] if self.M else "-"
        if end.kind == "brief" or end.kind == "monday" and not self.lines:      # H1 mid-tick: the lines are printed
            why = end.result if end.kind == "brief" else "monday_read_only"
            self.lines += [f"OWNER APPROVAL REQUIRED: UNKNOWN ({why})", "HIGH_IMPACT BLOCKED: UNKNOWN", "DISPOSITIONS TODAY: UNKNOWN"]
        denied = ";".join(f"{route_name(k, key)}:{status}" for k, key, status in self.conn.denied)
        self.lines.append("S1_ROUTES ok" if not denied else f"S1_ROUTES denied={denied}")
        if end.kind == "action":
            pr, head = end.detail
            terminal = f"S1_TICK REQUEST_REVIEW {pr} {head[:8]} {end.result} main={main8} contract={self.contract8}"
            action = "REQUEST_REVIEW"
        else:
            contract = "-" if end.kind == "source" else self.contract8
            terminal = f"S1_TICK NOOP - - {end.result} main={main8} contract={contract}"
            action = "NOOP"
        self.lines.append(terminal)
        return Result(lines=self.lines, terminal=terminal, action=action, result=end.result, writes=self.conn.writes,
                      calls=self.conn.calls, stages=self.stages, h1_checks=self.h1_checks, denied=self.conn.denied)


# ================================================================================================ the recorded worlds
REPO_ID = 4242
SAVED_3B = sha("contract-blob-v8-rev-2026-11-19")
CONTRACT = {"contract": "S1_RUNTIME_CONTRACT_v1", "task_id": B.TASK_ID, "owner_issue": 1156, "schedule": "hourly :45 Europe/Copenhagen",
            "bootstrap_path": "00_FMOS/S1/BOOTSTRAP.txt", "bootstrap_version": BOOTSTRAP_VERSION,
            "action_loop_path": "00_FMOS/S1/ACTION_LOOP.md", "action_loop_blob": sha("action-loop"),
            "tick_path": TICK_PATH, "tick_blob": sha("tick-v3.2"), "lane_switch_path": LANE_PATH, "lane_switch_blob": sha("lane-switch"),
            "rubric_blobs": {"00_FMOS/S1/STEWARD_STATES.md": sha("steward"), "00_FMOS/S1/EVIDENCE_BINDINGS.md": sha("bindings")}}
LANE_PINS = ["AGENTS.md", "00_FMOS/S1_REQUIRED_PR_JOBS_POLICY_V1.json", ".github", ".agents", "scripts/governance", "scripts/health",
             "07_PROMPTS_AND_AGENTS", "01_CORE_FRAMEWORK/governance", "00_FMOS/S1_WORKFLOW_ISOLATION_V1.json"]
PR, HEAD = 2250, sha("pr-2250-head")
BOT_USER = {"login": BOT_LOGIN, "id": BOT_ID, "type": BOT_TYPE}


def listing(contract_blob, contract=CONTRACT):
    rows = {contract["action_loop_path"]: contract["action_loop_blob"], contract["tick_path"]: contract["tick_blob"],
            contract["lane_switch_path"]: contract["lane_switch_blob"], CONTRACT_PATH: contract_blob,
            "00_FMOS/S1/BOOTSTRAP.txt": sha("bootstrap-text")}
    rows.update(contract["rubric_blobs"])
    return [{"name": p.rsplit("/", 1)[-1], "path": p, "sha": s, "size": 100, "type": "file"} for p, s in sorted(rows.items())]


def brief_doc(main, generated, run_id=44690000101, nxt=True, **over):
    b = {"schema": B.SCHEMA, "run_id": run_id, "run_attempt": 1, "event": "schedule", "generated_at": generated,
         "max_age_minutes": B.MAX_AGE_MINUTES, "repo": {"full_name": B.REPO, "id": REPO_ID, "identity": True}, "main": main,
         "pins": {"ok": True, "mismatch": [], "paths": sorted(LANE_PINS), "contract_blob": SAVED_3B,
                  "action_loop_blob": CONTRACT["action_loop_blob"], "tick_blob": CONTRACT["tick_blob"], "switch_blob": CONTRACT["lane_switch_blob"]},
         "lane": {"state": "ON", "off_reasons": [], "halt": None}, "rulesets": {"census": [], "stable": True},
         "status_lines": ["OWNER APPROVAL REQUIRED: NONE", "HIGH_IMPACT BLOCKED: NONE",
                          "DISPOSITIONS TODAY: merged=0 parked=UNKNOWN closed=UNKNOWN handed_off=UNKNOWN owner=UNKNOWN"],
         "heartbeat_due": False, "drafts": [], "codex": {"available": False},
         "prs": [{"n": PR, "head": HEAD, "open": ["C5:no_review"], "lane": {"eligible": True, "risk_floor": "LOW"},
                  "ci": {"state": "GREEN", "tuples": {"gate": {"run": 44680000201}, "test": {"run": 44680000202}}}}],
         "next": [{"pr": PR, "head": HEAD, "action": "REQUEST_REVIEW", "rule": "3", "how": "BRIDGE_REQUEST",
                   "verify": ["head", "no_request_for_head"], "rank": 1}] if nxt else [],
         "claude_slots": [], "complete": True, "incomplete": None, "errors": [], "ledger_read_at": generated}
    b.update(over)
    return b


def publish_body(b):
    """The published issue body as live briefs show it (render() writes the same bytes; see the parity test)."""
    payload = json.dumps(b, separators=(",", ":"), sort_keys=True).replace("<", "\\u003c").replace("`", "\\u0060")
    return (f"{B.SCHEMA} run_id={b['run_id']} generated_at={b['generated_at']} main={b['main']}\n\n"
            "Machine-written every tick by `.github/workflows/s1-tick-brief.yml`. Evidence only, never authority: "
            "`00_FMOS/S1/TICK.md` says what S1 re-reads before it acts. Do not edit; an edit makes the brief unverifiable.\n\n"
            f"{B.BEGIN}\n```json\n{payload}\n```\n{B.END}\n")


def run_doc(run_id, main, started, ended, **over):
    r = {"id": run_id, "name": "S1 tick brief", "path": B.WORKFLOW_PATH, "event": "schedule", "head_branch": "main", "head_sha": main,
         "run_attempt": 1, "status": "completed", "conclusion": "success", "run_started_at": started, "updated_at": ended,
         "repository": {"id": REPO_ID, "full_name": B.REPO}, "head_repository": {"id": REPO_ID, "full_name": B.REPO}}
    r.update(over)
    return r


def world(now="2026-11-19T18:46:30Z", main=None, brief_main=None, brief=None, body=None, issue=None, run=None, generated="2026-11-19T18:18:41Z"):
    """The 18:45Z tick of 2026-11-19: a fresh authentic brief at M whose ONE action is REQUEST_REVIEW #2250."""
    m = main or sha("main-2026-11-19T18")
    bm = brief_main or m
    b = brief if brief is not None else brief_doc(bm, generated)
    t0 = at(b["generated_at"]) if isinstance(b.get("generated_at"), str) else at(generated)
    i = issue or {"number": 2218, "title": B.BRIEF_TITLE, "state": "open", "locked": True, "user": dict(BOT_USER),
                  "labels": [{"name": B.BRIEF_LABEL}], "body": body if body is not None else publish_body(b),
                  "created_at": "2026-11-18T09:00:00Z", "updated_at": iso(t0 + timedelta(seconds=21))}
    r = run or run_doc(b["run_id"] if is_int(b.get("run_id")) else 44690000101, bm, iso(t0 - timedelta(minutes=3, seconds=29)), iso(t0 + timedelta(seconds=59)))
    routes = {
        API + "/branches/main": {"name": "main", "commit": {"sha": m, "commit": {"committer": {"date": "2026-11-19T11:40:00Z"}}}, "protected": False},
        f"{API}/contents/{S1_DIR}?ref={m}": listing(SAVED_3B),
        f"file:{CONTRACT_PATH}@{m}": json.dumps(CONTRACT, indent=2),
        f"file:{TICK_PATH}@{m}": "S1 TICK v3.2 (recorded text elided)",
        f"file:{LANE_PATH}@{m}": json.dumps({"contract": "S1_REVIEWED_MERGE_LANE_v1", "state": "ON", "pins": {p: sha("pin:" + p) for p in LANE_PINS}}),
        ISSUES_URL: [i],
        f"{API}/actions/runs/{r['id']}": r,
        f"{API}{PULLS}/{PR}": {"number": PR, "state": "open", "draft": False, "head": {"sha": HEAD, "ref": "s1/x", "repo": {"id": REPO_ID}},
                              "base": {"ref": "main", "repo": {"id": REPO_ID}}, "created_at": PR_CREATED},
        veto_key(1): [{"id": 7011000001, "issue_url": BRIDGE_API + "/issues/173", "user": {"login": OWNER_LOGIN},
                       "body": f"S1 tick 17:45Z relay\nnote: the brief ranks {HEAD} for a review",          # the head in prose only
                       "created_at": "2026-11-19T17:52:00Z", "updated_at": "2026-11-19T17:52:00Z"},
                      {"id": 7011000002, "issue_url": BRIDGE_API + "/issues/170", "user": {"login": OWNER_LOGIN},
                       "body": f"S1_REVIEW_REQUEST_v1\nhead: {HEAD}", "created_at": "2026-11-19T17:00:00Z", "updated_at": "2026-11-19T17:00:00Z"}],
        # T3H: today's heartbeat is already on #1156 (posted 25 minutes earlier), so a fixture about something else
        # writes no heartbeat; the T3H fixtures replace this page
        beat_key(now, 1): [heartbeat(at(now) - timedelta(minutes=25))],
        "ledger:1156:newest": [heartbeat(at(now) - timedelta(minutes=25))],          # the newest page (F5, HALT)
    }
    return {"now": now, "saved_3b": SAVED_3B, "clock_step_s": 0, "routes": routes, "origin": "schedule"}


def heartbeat(when, cid=7012000001, edited=False, login=OWNER_LOGIN, task=True):
    t = iso(when)
    return {"id": cid, "user": {"login": login}, "body": "S1_HEARTBEAT_v1\nmain=00000000" + (" contract=00000000" if task else " source=daily_summary"),
            "created_at": t, "updated_at": iso(when + timedelta(minutes=1)) if edited else t}


def drift_world(specs, files, generated="2026-11-19T15:18:20Z", now="2026-11-19T15:47:10Z", **kw):
    """A brief built at B.main and a current M ahead of it. specs: (subject, changed dirs) oldest first."""
    bm = sha("brief-main:" + generated)
    trees = {bm: {d: sha(f"{d}@base") for d in HALT_DIRS}}
    commits, prev = [], bm
    for k, (subject, changed) in enumerate(specs, 1):
        s = sha(f"c{k}:{generated}:{subject}")
        trees[s] = dict(trees[prev])
        for d in changed:
            trees[s][d] = sha(f"{d}@{s}")
        commits.append({"sha": s, "parents": [{"sha": prev}], "commit": {"message": subject + "\n\nbody"}})
        prev = s
    m = prev
    w = world(now=now, main=m, brief_main=bm, generated=generated, **kw)
    w["routes"][f"compare:{bm}...{m}"] = {"status": "ahead", "ahead_by": len(specs), "behind_by": 0, "total_commits": len(specs),
                                          "files": [dict(f) if isinstance(f, dict) else {"filename": f, "status": "modified"} for f in files]}
    w["routes"][f"{API}/commits?sha={m}&per_page=100"] = list(reversed(commits))
    for s, t in trees.items():
        w["routes"][f"{API}/git/trees/{s}"] = {"sha": s, "truncated": False,
                                               "tree": [{"path": d, "type": "tree", "sha": v} for d, v in t.items()] +
                                                       [{"path": "AGENTS.md", "type": "blob", "sha": sha("agents")}]}
    return w



def raw_body(payload, reverse=False):
    block = f"```json\n{payload}\n```"
    return (f"{B.SCHEMA} run_id=44690000101\n\n" + (f"{B.END}\n{B.BEGIN}\n{block}\n" if reverse else f"{B.BEGIN}\n{block}\n{B.END}\n"))


def fixture(fid, title, incident, w, result, action="NOOP", effects=0, charter=None, change=None, heartbeats=0, **extra):
    if change:
        change(w)
    fx = {"id": fid, "title": title, "incident": incident, "charter_row": charter,
          "world": w, "expect": {"action": action, "result": result, "effects": effects, "heartbeats": heartbeats}}
    fx.update(extra)
    return fx


def _base_brief_json():
    return json.dumps(brief_doc(sha("main-2026-11-19T18"), "2026-11-19T18:18:41Z"), separators=(",", ":"), sort_keys=True)


def fixtures():
    out = []
    # ---- charter W1 table, rows 1 to 10
    def stale_contract(w):
        """The connector served a main from before the v8 contract: the contract at that SHA is older."""
        old = sha("main-2026-11-18T15")
        old_contract = dict(CONTRACT, bootstrap_version="S1_BOOTSTRAP_v7", tick_blob=sha("tick-v3.1"))
        w["routes"][API + "/branches/main"]["commit"]["sha"] = old
        w["routes"][f"{API}/contents/{S1_DIR}?ref={old}"] = listing(sha("contract-blob-v7"), old_contract)
        w["routes"][f"file:{CONTRACT_PATH}@{old}"] = json.dumps(old_contract)
        w["routes"][f"file:{TICK_PATH}@{old}"] = "S1 TICK v3.1"
    out.append(fixture("F01", "stale main", "2026-11-18 manual bootstrap: an older main whose contract predates v8",
                       world(), "SOURCE_UNVERIFIED(3)", charter=1, change=stale_contract))
    out.append(fixture("F01b", "stale main: no SHA", "BOOTSTRAP step 1: the connector returns no SHA",
                       world(), "SOURCE_UNVERIFIED(3)", charter=1,
                       change=lambda w: w["routes"].update({API + "/branches/main": {"message": "Moved Permanently"}})))

    def new_contract_not_pasted(w):
        w["routes"][f"{API}/contents/{S1_DIR}?ref={sha('main-2026-11-19T18')}"] = listing(sha("contract-blob-v8-rev-2026-11-20"))
    out.append(fixture("F02", "3b mismatch", "contract on main moved; the owner's saved paste still holds the old 3b blob",
                       world(), "SOURCE_UNVERIFIED(3b)", charter=2, change=new_contract_not_pasted))

    def normalised_user(login):
        def f(w):
            w["routes"][ISSUES_URL][0]["user"] = {"login": login}
        return f
    out.append(fixture("F03", "T1 normalised wrapper", "S1_T1T2_PROBE_v1: the issue-list tool returns user {login: github-actions}",
                       world(), "BRIEF_UNVERIFIED(author)", charter=3, change=normalised_user("github-actions")))
    out.append(fixture("F03b", "T1 wrapper with the bot login but no type or id", "same probe, login kept",
                       world(), "BRIEF_UNVERIFIED(author)", charter=3, change=normalised_user(BOT_LOGIN)))

    def no_repository(w):
        run = w["routes"][f"{API}/actions/runs/44690000101"]
        run.pop("repository")
        run.pop("head_repository")
    out.append(fixture("F04", "T2 missing repository", "S1_T1T2_PROBE_v1: the workflow-run tool drops repository fields",
                       world(), "BRIEF_UNVERIFIED(run_binding)", charter=4, change=no_repository))
    out.append(fixture("F05", "brief 77 min old", "a missed :18 cron; the :45 tick read the previous hour's brief",
                       world(now=iso(at("2026-11-19T18:18:41Z") + timedelta(minutes=77, seconds=30))), "BRIEF_STALE(age_min=77)", charter=5))

    s1345 = [("learning: entry signal ledger", ()), ("S1 liveness: apply Claude combined R2 package byte-exact (#2246)", ("00_FMOS", "scripts")),
             ("ops: native market recovery", ()), ("learning: native Handlekompas", ()), ("ops: native market recovery", ()),
             ("health: audit", ()), ("ops: dashboard", ())]
    f1345 = ["00_FMOS/S1/BOOTSTRAP.txt", "scripts/orchestration/framework_metronome_v1.py", "04_MARKET_LEARNING/a.json"]

    def commits_do_not_reach_base(w):
        m = w["routes"][API + "/branches/main"]["commit"]["sha"]
        page = w["routes"][f"{API}/commits?sha={m}&per_page=100"]
        page[-1]["parents"] = [{"sha": sha("an unrelated older commit")}]      # B.main is not on M's first-parent chain
    # W2b: T3 reads no tree. Code drift is BRIEF_STALE(source_changed) at once; the C1b halt test is the next brief's.
    out.append(fixture("F06", "13:45Z code drift, first-parent walk would not reach B.main", "13:45Z: v3.2 ended BRIEF_INCOMPLETE(T3:range)",
                       drift_world(s1345, f1345, generated="2026-11-19T13:18:05Z", now="2026-11-19T13:47:40Z"),
                       "BRIEF_STALE(source_changed)", charter=6, change=commits_do_not_reach_base))

    def trees_refused(w):
        for k in [k for k in w["routes"] if k.startswith(API + "/git/trees/")]:
            w["routes"][k] = {"__refused__": 403}
    out.append(fixture("F06b", "13:45Z code drift, tree routes refused", "13:45Z shape: v3.2 ended BRIEF_INCOMPLETE(T3:trees_unreadable)",
                       drift_world(s1345, f1345, generated="2026-11-19T13:18:05Z", now="2026-11-19T13:47:40Z"),
                       "BRIEF_STALE(source_changed)", charter=6, change=trees_refused))
    out.append(fixture("F06c", "13:45Z range, fully readable (control)", "the same range under the compact T3 of #2249",
                       drift_world(s1345, f1345, generated="2026-11-19T13:18:05Z", now="2026-11-19T13:47:40Z"),
                       "BRIEF_STALE(source_changed)", charter=6))
    data5 = ["03_DAILY_CAPTURE_LOGS/2026-11-19/capture_1500.json", "04_MARKET_LEARNING/handlekompas/state.json",
             "04_MARKET_LEARNING/entry_signal_ledger.jsonl", "02_DATA_PING/hourly/2026-11-19T15.json", "06_WEEKLY/dashboard.md"]
    out.append(fixture("F07", "5-commit data-only T3 range (15:45Z shape)", "15:45Z: five data commits between B.main and M",
                       drift_world([("data: capture", ()), ("learning: entry signal ledger", ()), ("ops: native market recovery", ()),
                                    ("data: hourly ping", ()), ("ops: dashboard", ())], data5,
                                   brief=None), "NOTHING_ACTIONABLE(skipped=brief_empty)", charter=7,
                       change=lambda w: _set_brief(w, nxt=False), t3_drift=sorted(data5)))
    out.append(fixture("F08", "```json fenced body", "19:45Z-21:45Z: the published fence read as a body failure three times",
                       world(), "REQUESTED(c=7100000001)", action="REQUEST_REVIEW", effects=1, charter=8))
    out.append(fixture("F09", "positive control REQUEST_REVIEW #2250", "18:45Z: the first real S1 action, posted exactly once",
                       world(), "REQUESTED(c=7100000001)", action="REQUEST_REVIEW", effects=1, charter=9))

    def existing_request(w):
        w["routes"][veto_key(1)].insert(0, {"id": 7011000009, "issue_url": BRIDGE_API + "/issues/173", "user": {"login": OWNER_LOGIN},
                                            "body": f"S1_REVIEW_REQUEST_v1\nrepo: {B.REPO}\npr: {PR}\nhead: {HEAD}\nrisk: LOW",
                                            "created_at": "2026-11-19T18:47:00Z", "updated_at": "2026-11-19T18:47:00Z"})
    out.append(fixture("F09b", "19:45Z: the request of 18:45Z is on the page", "no second review request for the same head",
                       world(now="2026-11-19T19:46:20Z", generated="2026-11-19T19:18:30Z"), f"NOTHING_ACTIONABLE(skipped={PR}:R3:request_at_head)",
                       charter=9, change=existing_request))
    def quiet_and_empty(w):
        _set_brief(w, nxt=False)
        w["routes"][API + "/branches/main"]["commit"]["commit"]["committer"]["date"] = "2026-11-19T09:31:00Z"   # 7 h quiet main
    out.append(fixture("F10", "positive NOTHING_ACTIONABLE (16:45Z)", "16:45Z: the whole chain completed, nothing to do; main quiet for 7 h",
                       world(now="2026-11-19T16:46:05Z", generated="2026-11-19T16:18:12Z"), "NOTHING_ACTIONABLE(skipped=brief_empty)",
                       charter=10, change=quiet_and_empty))

    def head_moved(w):
        w["routes"][f"{API}{PULLS}/{PR}"]["head"]["sha"] = sha("pr-2250-new-head")
    out.append(fixture("F10b", "NOTHING_ACTIONABLE after a failed re-read", "the PR's head moved after the brief",
                       world(), f"NOTHING_ACTIONABLE(skipped={PR}:C8:head_changed)", charter=10, change=head_moved))
    # ---- NEW, 2026-11-20 production: a source change merged after the brief
    out.append(fixture("F11", "source change after the brief (#2258, 2026-11-20 07:04Z)", "BOOTSTRAP/test change merged after the :18 build",
                       drift_world([("data: materialize hourly sequence", ()),
                                    ("fix(s1): fence T1 brief body verification and regression tests (#2258)", ("00_FMOS", "tests")),
                                    ("data: materialize hourly sequence", ()), ("ops: native market recovery", ())],
                                   ["00_FMOS/S1/BOOTSTRAP.txt", "tests/governance/test_s1_reviewed_merge_lane_v1.py",
                                    "tests/governance/test_s1_runtime_contract_v1.py", "03_DAILY_CAPTURE_LOGS/2026-11-20/seq.json"],
                                   generated="2026-11-20T06:18:40Z", now="2026-11-20T06:47:15Z"),
                       "BRIEF_STALE(source_changed)", charter=11))
    # ---- addendum 1: parser fixtures (the reference executor rejects them; parse_body accepts them on main)
    base = _base_brief_json()
    for fid, title, body in (
            ("F12a", "END before BEGIN", raw_body(base, reverse=True)),
            ("F12b", "duplicate top-level key", raw_body(base.replace('"complete":true', '"complete":false,"complete":true', 1))),
            ("F12c", "duplicate nested key pins.ok", raw_body(base.replace('"ok":true', '"ok":false,"ok":true', 1))),
            ("F12d", "NaN", raw_body(base.replace('"max_age_minutes":45', '"max_age_minutes":NaN', 1))),
            ("F12e", "Infinity", raw_body(base.replace('"max_age_minutes":45', '"max_age_minutes":Infinity', 1))),
            ("F12f", "boolean run_id", raw_body(base.replace('"run_id":44690000101', '"run_id":true', 1)))):
        out.append(fixture(fid, title, "CHARTER_ADDENDUM_1 item 1 (reproduced as accepted by parse_body on e5ccce2a)",
                           world(body=body), "BRIEF_UNVERIFIED(body)", charter=12, parser_gap=True))
    # ---- extra controls, one per further critical check
    out.append(fixture("F13", "brief pins not ok", "lane pins moved on main without a reviewed pin update",
                       world(brief=brief_doc(sha("main-2026-11-19T18"), "2026-11-19T18:18:41Z",
                                             pins=dict(brief_doc("a" * 40, "x")["pins"], ok=False, mismatch=["pins:.github"]))),
                       "BRIEF_UNVERIFIED(pins)"))
    out.append(fixture("F13b", "brief pins ok but its contract blob is not the saved 3b", "brief built at an older contract",
                       world(brief=brief_doc(sha("main-2026-11-19T18"), "2026-11-19T18:18:41Z",
                                             pins=dict(brief_doc("a" * 40, "x")["pins"], contract_blob=sha("contract-blob-v7")))),
                       "BRIEF_UNVERIFIED(pins)"))

    def edited(w):
        w["routes"][ISSUES_URL][0]["updated_at"] = "2026-11-19T18:31:00Z"           # after the run ended at 18:19:40Z
    out.append(fixture("F14", "brief edited after its run", "an edit by anyone moves updated_at past the run's end",
                       world(), "BRIEF_UNVERIFIED(edited_outside_run)", change=edited))
    out.append(fixture("F15", "brief incomplete", "the depth cap was hit; the build says so",
                       world(brief=brief_doc(sha("main-2026-11-19T18"), "2026-11-19T18:18:41Z", complete=False, incomplete="depth_cap")),
                       "BRIEF_INCOMPLETE(depth_cap)"))

    def m_behind(w):
        m = w["routes"][API + "/branches/main"]["commit"]["sha"]
        bm = sha("brief-main-newer")
        _set_brief(w, main=bm)
        w["routes"][f"{API}/actions/runs/44690000101"]["head_sha"] = bm
        w["routes"][f"compare:{bm}...{m}"] = {"status": "behind", "ahead_by": 0, "behind_by": 2, "total_commits": 0, "files": []}
    out.append(fixture("F16", "stale M, fresh brief", "BOOTSTRAP v8 note: an older M is caught by T3 main_not_ahead",
                       world(), "BRIEF_UNVERIFIED(main_not_ahead)", change=m_behind))
    out.append(fixture("F17", "unreviewed direct push to scripts/ after the brief", "C1b: the tick ends STALE with no write; the next brief halts",
                       drift_world([("data: capture", ()), ("chore: tweak", ("scripts",)), ("data: capture", ())],
                                   ["scripts/orchestration/x.py", "03_DAILY_CAPTURE_LOGS/a.json"]),
                       "BRIEF_STALE(source_changed)"))
    out += w2b_fixtures()

    def second_labelled(w):
        w["routes"][ISSUES_URL].append({"number": 2262, "state": "open", "user": {"login": OWNER_LOGIN, "id": 1, "type": "User"},
                                        "labels": [{"name": B.BRIEF_LABEL}], "body": "note", "created_at": "2026-11-19T18:00:00Z",
                                        "updated_at": "2026-11-19T18:00:00Z"})
    out.append(fixture("F18", "a second labelled issue", "R2-14 (Sol): mutable label membership; the read becomes ambiguous",
                       world(), "BRIEF_UNVERIFIED(issues)", change=second_labelled))
    out.append(fixture("F19", "H1 begins mid-tick", "Monday 09:29:50 start; 09:30 passes before the write (SOL G3)",
                       world(now="2026-11-23T08:29:50Z", generated="2026-11-23T08:18:30Z"), "MONDAY_READ_ONLY",
                       change=lambda w: w.update(clock_step_s=2), status_lines="brief"))
    def long_range(w):
        m = w["routes"][API + "/branches/main"]["commit"]["sha"]
        bm = B.parse_body(w["routes"][ISSUES_URL][0]["body"])["main"]
        w["routes"][f"compare:{bm}...{m}"]["total_commits"] = 140
    out.append(fixture("F21", "a drift range too long to read", "T3 bound: over 100 commits after a long build outage",
                       drift_world([("data: capture", ())] * 3, ["03_DAILY_CAPTURE_LOGS/a.json"]), "BRIEF_STALE(drift_unreadable)",
                       change=long_range))
    def still_running(w):
        w["routes"][f"{API}/actions/runs/44690000101"].update(status="in_progress", conclusion=None)
    out.append(fixture("F22", "brief run not finished", "the tick read the issue while the publish job was still running",
                       world(), "BRIEF_UNVERIFIED(run_not_success)", change=still_running))
    out.append(fixture("F20", "Monday window at the start", "T0: Monday 09:46 Europe/Copenhagen",
                       world(now="2026-11-23T08:46:00Z", generated="2026-11-23T08:18:30Z"), "MONDAY_READ_ONLY"))
    return out


C1B_COMMIT, C1B_PARENT = sha("direct-push-commit"), sha("direct-push-parent")


def c1b_world(subject="chore: tweak", parents=None, differ=True, status="ahead", named=False, tests=None):
    """A fresh brief at M whose ONE B.next entry is the producer's HALT rule C1b for C1B_COMMIT."""
    w = world()
    m = w["routes"][API + "/branches/main"]["commit"]["sha"]
    _set_brief(w, nxt=False)
    i = w["routes"][ISSUES_URL][0]
    b = B.parse_body(i["body"])
    b["next"] = [{"action": "HALT", "rule": "C1b", "source": "C1B", "commit": C1B_COMMIT, "parent": C1B_PARENT,
                  "entries": ["scripts"], "verify": ["commit", "parent", "trees"], "rank": 1, "why": "unreviewed code"}]
    i["body"] = publish_body(b)
    r = w["routes"]
    r[f"{API}/commits/{C1B_COMMIT}"] = {"sha": C1B_COMMIT, "parents": [{"sha": p} for p in (parents or [C1B_PARENT])],
                                       "commit": {"message": subject + "\n\nbody"}}
    for s_, tag in ((C1B_PARENT, "before"), (C1B_COMMIT, "after" if differ else "before")):
        r[f"{API}/git/trees/{s_}"] = {"sha": s_, "truncated": False,
                                      "tree": [{"path": d, "type": "tree", "sha": sha(f"{d}@{tag if d == 'scripts' else 'same'}")} for d in HALT_DIRS]}
    if tests:                                                    # (parent entry, commit entry) for tests: (type, sha tag)
        for s_, (kind, tag) in zip((C1B_PARENT, C1B_COMMIT), tests):
            row = next(e for e in r[f"{API}/git/trees/{s_}"]["tree"] if e["path"] == "tests")
            row.update(type=kind, sha=sha(f"tests@{tag}"))
    r[f"compare:{C1B_COMMIT}...{m}"] = {"status": status, "total_commits": 2, "files": []}
    if named:
        r["ledger:1156:newest"].append({"id": 7012000002, "user": {"login": OWNER_LOGIN}, "created_at": "2026-11-19T18:30:00Z",
                                        "updated_at": "2026-11-19T18:30:00Z",
                                        "body": f"S1_LANE_HALTED\nPR=- head=-\nreason: unreviewed_code_on_main\ncommit: {C1B_COMMIT}"})
    return w


def receipt_world(position):
    """A brief with one Claude slot (#2250, not ready) and the Bridge's newest comments, newest first: an APPROVE receipt for
    the head at `position` and its request just after it; 0-based, so position 40 is the first row past the 40 page."""
    w = world(now="2026-11-19T20:46:20Z", generated="2026-11-19T20:18:30Z")
    _set_brief(w, claude_slots=[{"pr": PR, "head": HEAD, "ready": False, "high_evidence": False}])
    rows = [{"id": 7013000000 + k, "issue_url": BRIDGE_API + "/issues/173", "user": {"login": OWNER_LOGIN}, "body": f"note {k}",
             "created_at": iso(at("2026-11-19T20:40:00Z") - timedelta(minutes=k)), "updated_at": iso(at("2026-11-19T20:40:00Z") - timedelta(minutes=k))}
            for k in range(100)]
    req, rec = rows[position + 1], rows[position]
    req["body"] = f"S1_REVIEW_REQUEST_v1\nrepo: {B.REPO}\npr: {PR}\nhead: {HEAD}\nrisk: LOW"
    rec["body"] = (f"CLAUDE_REVIEW_v1\nverdict: APPROVE\nhead_sha: {HEAD}\nrequest: {req['id']}\nreport: reports/x.md\nreport_blob: {sha('r')}\n"
                   f"bridge_commit: {sha('b')}\nlane_eligible: YES\nindependence: INDEPENDENT_DETACHED")
    w["routes"][BRIDGE_PAGE] = rows
    w["routes"][BRIDGE_PAGE_40] = rows[:40]
    w["routes"][veto_key(1)] = rows                               # the REQUEST_REVIEW read: every page since the PR
    w["routes"][veto_key(2)] = []
    return w


def w2b_fixtures():
    out = []
    files = ["scripts/governance/s1_tick_brief_v1.py", "03_DAILY_CAPTURE_LOGS/a.json"]
    out.append(fixture("W2B-01", "code drift: STALE with no tree read", "F1 (2026-11-17..20): T3 tree reads ended BRIEF_INCOMPLETE",
                       drift_world([("data: capture", ()), ("S1 (#2301)", ("scripts",)), ("data: capture", ())], files),
                       "BRIEF_STALE(source_changed)"))
    out.append(fixture("W2B-02", "brief HALT C1b, verified natively", "D1: the producer found a non-squash code commit",
                       c1b_world(), "LANE_HALTED(c1b)", effects=1))
    out.append(fixture("W2B-03", "brief HALT C1b on a squash merge", "a halt entry the native read refutes",
                       c1b_world(subject="Reviewed change (#2301)"), "NOTHING_ACTIONABLE(skipped=-:C1b:squash_merge)"))
    out.append(fixture("W2B-03b", "brief HALT C1b, two-parent commit with a PR subject", "not a squash merge: verified",
                       c1b_world(subject="Merge (#2301)", parents=[C1B_PARENT, sha("side")]), "LANE_HALTED(c1b)", effects=1))
    out.append(fixture("W2B-04", "brief HALT C1b whose entries do not differ", "a halt entry the native trees refute",
                       c1b_world(differ=False), "NOTHING_ACTIONABLE(skipped=-:C1b:entries_equal)"))
    out.append(fixture("W2B-05", "brief HALT C1b already named on #1156", "S1 posted it in an earlier tick",
                       c1b_world(named=True), "NOTHING_ACTIONABLE(skipped=-:C1b:already_named)"))
    out.append(fixture("W2B-04b", "brief HALT C1b: tests/ turned from a tree into a blob", "F6: the entry type is part of the entry",
                       c1b_world(differ=False, tests=(("tree", "same"), ("blob", "same"))), "LANE_HALTED(c1b)", effects=1))
    out.append(fixture("W2B-04c", "brief HALT C1b: tests is a blob that changed", "F6: a non-tree entry that changed is a difference",
                       c1b_world(differ=False, tests=(("blob", "one"), ("blob", "two"))), "LANE_HALTED(c1b)", effects=1))
    out.append(fixture("W2B-01b", "non-squash drift of tests/data.json", "F1: tests/ is a source directory; the tick is STALE, nothing merges",
                       drift_world([("data: capture", ()), ("bot: fixture data", ("tests",)), ("data: capture", ())], ["tests/data.json"]),
                       "BRIEF_STALE(source_changed)"))
    out.append(fixture("W2B-05b", "brief HALT C1b of a commit not on main", "compare commit...M diverged",
                       c1b_world(status="diverged"), "NOTHING_ACTIONABLE(skipped=-:C1b:not_on_main)"))
    # T3H: 2026-11-20 is a Friday; 08:00Z is 09:00 Copenhagen, 07:30Z is 08:30
    yesterday = [heartbeat(at("2026-11-19T07:50:00Z"))]
    def ledger(page, page2=None):
        def f(w):
            w["routes"][beat_key(w["now"], 1)] = page
            if page2 is not None:
                w["routes"][beat_key(w["now"], 2)] = page2
        return f
    filler = [{"id": 7014000000 + k, "user": {"login": OWNER_LOGIN}, "body": f"S1_OP_DONE_v1\nintent: {k}",
               "created_at": iso(at("2026-11-20T07:59:00Z") - timedelta(seconds=k)), "updated_at": iso(at("2026-11-20T07:59:00Z") - timedelta(seconds=k))}
              for k in range(100)]
    out.append(fixture("W2B-06", "T3H heartbeat on a failed brief at 09:00", "F4: no heartbeat since 2026-11-17 because every brief failed",
                       world(now="2026-11-20T08:00:10Z", generated="2026-11-20T06:18:41Z"), "BRIEF_STALE(age_min=101)",
                       heartbeats=1, change=ledger(yesterday)))
    out.append(fixture("W2B-06b", "T3H heartbeat on a good brief at 09:00", "the heartbeat is never the action",
                       world(now="2026-11-20T08:00:10Z", generated="2026-11-20T07:48:41Z"), "REQUESTED(c=7100000002)",
                       action="REQUEST_REVIEW", effects=1, heartbeats=1, change=ledger(yesterday)))
    out.append(fixture("W2B-07", "T3H: no heartbeat at 08:30", "before 08:45 Copenhagen",
                       world(now="2026-11-20T07:30:10Z", generated="2026-11-20T05:18:41Z"), "BRIEF_STALE(age_min=131)",
                       change=ledger(yesterday)))
    out.append(fixture("W2B-08", "T3H: today's heartbeat exists", "no second heartbeat the same day",
                       world(now="2026-11-20T08:00:10Z", generated="2026-11-20T06:18:41Z"), "BRIEF_STALE(age_min=101)",
                       change=ledger(yesterday + [heartbeat(at("2026-11-20T07:46:00Z"), cid=7012000003)])))
    out.append(fixture("W2B-08b", "T3H: today's only heartbeat was edited", "phase 3 wording: an edited heartbeat of this task still dedupes",
                       world(now="2026-11-20T08:00:10Z", generated="2026-11-20T06:18:41Z"), "BRIEF_STALE(age_min=101)",
                       change=ledger([heartbeat(at("2026-11-20T07:46:00Z"), cid=7012000003, edited=True)])))
    out.append(fixture("W2B-08c", "T3H: today's heartbeat is another task's", "only a heartbeat of this task dedupes",
                       world(now="2026-11-20T08:00:10Z", generated="2026-11-20T06:18:41Z"), "BRIEF_STALE(age_min=101)", heartbeats=1,
                       change=ledger([heartbeat(at("2026-11-20T07:46:00Z"), cid=7012000003, task=False)])))
    out.append(fixture("W2B-08d", "T3H: today's heartbeat is on page 2 of the since-read", "a busy ledger: page 1 is 100 other comments",
                       world(now="2026-11-20T08:00:10Z", generated="2026-11-20T06:18:41Z"), "BRIEF_STALE(age_min=101)",
                       change=ledger(filler, [heartbeat(at("2026-11-20T07:46:00Z"), cid=7012000003)])))
    out.append(fixture("W2B-08e", "T3H: page 2 of the since-read unreadable", "any page that cannot be read: no heartbeat",
                       world(now="2026-11-20T08:00:10Z", generated="2026-11-20T06:18:41Z"), "BRIEF_STALE(age_min=101)",
                       change=ledger(filler, {"__refused__": 502})))
    out.append(fixture("W2B-08f", "T3H: a manual run at 09:00", "only a scheduled run of this task posts the heartbeat",
                       world(now="2026-11-20T08:00:10Z", generated="2026-11-20T06:18:41Z"), "BRIEF_STALE(age_min=101)",
                       change=lambda w: (ledger(yesterday)(w), w.update(origin="manual"))))
    out.append(fixture("W2B-09", "T3H: #1156 page unreadable", "no heartbeat without the dedupe read",
                       world(now="2026-11-20T08:00:10Z", generated="2026-11-20T06:18:41Z"), "BRIEF_STALE(age_min=101)",
                       change=ledger({"__refused__": 403})))
    out.append(fixture("W2B-10", "T3H: Monday 09:45", "T0 ends the run before T3H",
                       world(now="2026-11-23T08:45:00Z", generated="2026-11-23T08:18:30Z"), "MONDAY_READ_ONLY", change=ledger([])))
    out.append(fixture("W2B-11", "T4: a receipt beyond the 40-comment page", "D2: the slot is not approved; the request is not repeated",
                       receipt_world(45), f"NOTHING_ACTIONABLE(skipped={PR}:R3:request_at_head)"))
    out.append(fixture("W2B-11b", "T4: a receipt on the 40-comment page (control)", "ADMISSIBLE, not ready: no request, no re-read",
                       receipt_world(10), f"NOTHING_ACTIONABLE(skipped={PR}:R3:claude_approved)"))

    def edited_receipt(w):
        rows = w["routes"][veto_key(1)]
        rows[10]["updated_at"] = iso(at(rows[10]["created_at"]) + timedelta(minutes=2))
    out.append(fixture("W2B-11c", "T4: an edited receipt on the page", "an edited receipt approves nothing: the entry runs as ranked",
                       receipt_world(10), f"NOTHING_ACTIONABLE(skipped={PR}:R3:request_at_head)", change=edited_receipt))
    def old_request(w):                                          # the request is 120 rows back: page 2 of the since-read
        rows = [{"id": 7015000000 + k, "issue_url": BRIDGE_API + "/issues/173", "user": {"login": OWNER_LOGIN}, "body": f"note {k}",
                 "created_at": iso(at("2026-11-19T18:40:00Z") - timedelta(minutes=k)), "updated_at": iso(at("2026-11-19T18:40:00Z") - timedelta(minutes=k))}
                for k in range(130)]
        rows[120]["body"] = f"S1_REVIEW_REQUEST_v1\nrepo: {B.REPO}\npr: {PR}\nhead: {HEAD}\nrisk: LOW"
        w["routes"][veto_key(1)], w["routes"][veto_key(2)] = rows[:100], rows[100:]
        w["routes"][BRIDGE_PAGE], w["routes"][BRIDGE_PAGE_40] = rows[:100], rows[:40]
    out.append(fixture("W2B-12", "a review request older than the 40 page and the newest 100", "REQUEST_REVIEW reads as VETO: every page since the PR",
                       world(), f"NOTHING_ACTIONABLE(skipped={PR}:R3:request_at_head)", change=old_request))
    return out


def _set_brief(w, **over):
    i = w["routes"][ISSUES_URL][0]
    b = B.parse_body(i["body"])
    nxt = over.pop("nxt", True)
    b.update(over)
    if not nxt:
        b["next"] = []
    i["body"] = publish_body(b)


FIXTURES = fixtures()
BY_ID = {f["id"]: f for f in FIXTURES}


def replay(fx, off=(), reading="strict"):
    w = fx["world"]
    return Tick(w["routes"], w["now"], w["saved_3b"], w["clock_step_s"], off=off, reading=reading, origin=w.get("origin", "schedule")).run()


# ================================================================================================ the two metrics
def heartbeats_of(r):
    return [w for w in r.writes if w["kind"] == "heartbeat"]


def task_ok(fx, r):
    e = fx["expect"]
    ok = r.action == e["action"] and r.result == e["result"] and len(r.effects) == e["effects"] and len(heartbeats_of(r)) == e["heartbeats"]
    if ok and "t3_drift" in fx:
        ok = r.stages.get("T3") == "OK" and r.stages.get("DRIFT") == fx["t3_drift"]
    if ok and r.action == "NOOP" and r.result.startswith(("BRIEF_", "MONDAY_READ_ONLY")) and fx.get("status_lines") != "brief":
        why = "monday_read_only" if r.result == "MONDAY_READ_ONLY" else r.result
        ok = r.lines[:3] == [f"OWNER APPROVAL REQUIRED: UNKNOWN ({why})", "HIGH_IMPACT BLOCKED: UNKNOWN", "DISPOSITIONS TODAY: UNKNOWN"]
    elif ok and (r.result.startswith(("NOTHING_ACTIONABLE", "REQUESTED")) or fx.get("status_lines") == "brief"):
        issue = fx["world"]["routes"][ISSUES_URL][0]
        ok = r.lines[:3] == read_block(issue["body"])["status_lines"]
    return ok


def policy_violations(fx, r):
    """Policy compliance, independent of whether the task result was right."""
    out = []
    base = r.result.split("(", 1)[0]
    if r.action == "NOOP" and base not in NOOP_RESULTS:
        out.append("ending_not_in_closed_list")
    beats = heartbeats_of(r)
    other = [w for w in r.writes if w["kind"] != "heartbeat"]
    # a failed brief writes nothing but the T3H heartbeat; SOURCE_UNVERIFIED and H1 not even that
    if base in ("BRIEF_UNVERIFIED", "BRIEF_STALE", "BRIEF_INCOMPLETE") and other or base in ("SOURCE_UNVERIFIED", "MONDAY_READ_ONLY") and r.writes:
        out.append("write_in_a_run_that_must_not_write")
    if len(r.effects) > 1:
        out.append("more_than_one_effect")
    if len(beats) > 1:
        out.append("more_than_one_heartbeat")
    if (fx["expect"]["effects"] == 0 and other) or len(r.effects) > fx["expect"]["effects"] or len(beats) > fx["expect"]["heartbeats"]:
        out.append("unauthorised_write")                  # a write the recorded world does not authorise
    for wr in r.writes:
        if h1(at(wr["at"])):
            out.append("write_inside_h1")
    staged = [s for s, _k, _key in r.calls]
    t13 = [c for c in r.calls if c[0] in ("T1", "T2", "T3")]
    if len(t13) > T1_T3_CALLS:
        out.append("t1_t3_call_budget")
    if any("/commits?" in c[2] or "/git/trees/" in c[2] for c in t13):
        out.append("t3_tree_read")                        # v3.3: T3 never reads a tree
    if len([c for c in r.calls if c[0] == "T3H"]) > 10:
        out.append("t3h_call_budget")
    order = {"BOOT": 0, "T1": 1, "T2": 2, "T3": 3, "T3H": 3.5, "T4": 4, "T5": 5}
    if any(order[a] > order[b] for a, b in zip(staged, staged[1:])):
        out.append("read_before_t3_done")
    ticks = [line for line in r.lines if line.startswith("S1_TICK ")]
    if len(ticks) != 1 or r.lines[-1] != ticks[0] or not r.lines[-2].startswith("S1_ROUTES "):
        out.append("terminal_lines")
    if r.effects and r.action == "REQUEST_REVIEW":
        page = [c for k, v in fx["world"]["routes"].items() if k.startswith(BRIDGE_API + "/issues/173/comments?since=") and isinstance(v, list) for c in v]
        if any(first_token(c.get("body")) == "S1_REVIEW_REQUEST_v1" and fields(c.get("body")).get("head") == HEAD
               and str(c.get("issue_url")).endswith("/issues/173") for c in page):
            out.append("duplicate_review_request")
    return out


def unsafe_effects(fx, r):
    extra_beats = max(0, len(heartbeats_of(r)) - fx["expect"]["heartbeats"])       # an expected T3H heartbeat is not unsafe
    other = [w for w in r.writes if w["kind"] != "heartbeat"]
    return extra_beats + (len(other) if fx["expect"]["effects"] == 0 else max(0, len(r.effects) - fx["expect"]["effects"]))


def score(off=(), reading="strict"):
    rows = []
    for fx in FIXTURES:
        r = replay(fx, off, reading)
        rows.append((fx["id"], task_ok(fx, r), policy_violations(fx, r), unsafe_effects(fx, r), r))
    n = len(rows)
    return {"task_completion": sum(1 for _i, t, _p, _u, _r in rows if t) / n,
            "policy_compliance": sum(1 for _i, _t, p, _u, _r in rows if not p) / n,
            "unsafe_effects": sum(u for _i, _t, _p, u, _r in rows), "rows": rows}


# Critical-check mutants (charter: pins, 3b, author, run binding, staleness, T3 drift) and the further checks. Each is
# (checks switched off, T1 reading). "literal" is not a removed check: it is the 19:45Z misreading of T1.
MUTANTS = {
    "pins": (("pins",), "strict"), "bootstrap_3b": (("bootstrap_3b",), "strict"), "author": (("author",), "strict"),
    "run_binding": (("run_binding",), "strict"), "staleness": (("staleness",), "strict"), "t3_source": (("t3_source",), "strict"),
    "bootstrap_3": (("bootstrap_3",), "strict"), "t0_monday": (("t0_monday",), "strict"), "issues": (("issues",), "strict"),
    "body_strict": (("body_strict",), "strict"), "edited_outside_run": (("edited_outside_run",), "strict"),
    "complete": (("complete",), "strict"), "t3_not_ahead": (("t3_not_ahead",), "strict"), "t3_unreadable": (("t3_unreadable",), "strict"),
    "t3_tree_free": (("t3_tree_free",), "strict"), "h1_recheck": (("h1_recheck",), "strict"),
    "t3h_clock": (("t3h_clock",), "strict"), "t3h_dedup": (("t3h_dedup",), "strict"), "t3h_unreadable": (("t3h_unreadable",), "strict"),
    "t3h_failed_brief": (("t3h_failed_brief",), "strict"), "t4_page40": (("t4_page40",), "strict"),
    "t4_receipt_rules": (("t4_receipt_rules",), "strict"), "c1b_squash": (("c1b_squash",), "strict"),
    "c1b_entries": (("c1b_entries",), "strict"), "c1b_on_main": (("c1b_on_main",), "strict"), "c1b_named": (("c1b_named",), "strict"),
    "t3h_scheduled": (("t3h_scheduled",), "strict"), "t3h_all_pages": (("t3h_all_pages",), "strict"),
    "request_all_pages": (("request_all_pages",), "strict"),
    "t3_tests_dir": (("t3_tests_dir",), "strict"), "c1b_entry_type": (("c1b_entry_type",), "strict"),
    "head_reread": (("head_reread",), "strict"), "run_not_success": (("run_not_success",), "strict"), "request_dedupe": (("request_dedupe",), "strict"),
    "t1_literal_no_fence": ((), "literal"),
}
CHARTER_MUTANTS = ("pins", "bootstrap_3b", "author", "run_binding", "staleness", "t3_source")

# verify_brief has no input for the owner's saved paste or C: it checks pins.ok only (TICK T2 also compares
# pins.contract_blob with the saved 3b and the action_loop/tick blobs with C). Pinned so a change shows.
KNOWN_T2_DIVERGENCE = {"F13b": ("BRIEF_UNVERIFIED(pins)", "OK")}


# ================================================================================================ the tests
class ReferenceText(unittest.TestCase):
    def test_the_executor_was_derived_from_the_deployed_text(self):
        got = {k: hashlib.sha256(v.encode("utf-8")).hexdigest() for k, v in text_regions().items()}
        self.assertEqual(got, REFERENCE_TEXT_SHA256, "BOOTSTRAP or TICK changed: re-derive the reference executor of this file")

    def test_the_rule_sentences_the_executor_implements_are_present(self):
        for needle in ("If the connector returns no SHA: SOURCE_UNVERIFIED(3).", "bootstrap_version must be S1_BOOTSTRAP_v8",
                       "SOURCE_UNVERIFIED(3b)", "that fence is the published format, never a body failure",
                       "T1 and T2 use only that fetch, never an issue list, issue search or workflow-run tool"):
            self.assertIn(needle, BOOTSTRAP_TEXT)
        for needle in ("issues: exactly ONE open issue (not a pull request) carries the label;",
                       "author: its user.login is github-actions[bot], user.type is Bot and user.id is 41898282;",
                       "run_binding: path is .github/workflows/s1-tick-brief.yml;", "run_not_success: status is completed and conclusion is success;",
                       "edited_outside_run: run_started_at <= B.generated_at <= the issue's updated_at <= the run's updated_at.",
                       "pins: B.pins.ok is true, B.pins.contract_blob equals the 3b value of your saved BOOTSTRAP text, and B.pins.action_loop_blob and B.pins.tick_blob equal C.",
                       "BRIEF_STALE(age_min=<n>): B.generated_at is more than 45 minutes before now.",
                       "Status not ahead: BRIEF_UNVERIFIED(main_not_ahead)", "T3 never reads a tree",
                       "BRIEF_STALE(source_changed); data-only drift is fine", "H1 is checked again immediately before EVERY write below.",
                       "IF THE BRIEF FAILED (BRIEF_UNVERIFIED, BRIEF_STALE or BRIEF_INCOMPLETE): make no write of any kind in this run except the T3H heartbeat.",
                       "it runs whether T1 to T3 passed or failed",
                       "Only in a scheduled run of this task at 08:45 Europe/Copenhagen or later: fetch API/issues/1156/comments?since=<today 00:00 Copenhagen, in UTC>&per_page=100, every page.",
                       "If none is an S1_HEARTBEAT_v1 of this task by Donh91 created today (Copenhagen date), post one S1_HEARTBEAT_v1 on #1156 now",
                       "brief=<B.run_id or NONE> brief_state=<OK or the T1 to T3 result>", "A page you cannot read: no heartbeat.",
                       "Bridge #173 has no S1_REVIEW_REQUEST_v1 for this head (read as VETO reads it: since the PR's created_at, every page)",
                       "per_page=40 (the newest 40 comments, newest first; a receipt that is not on that page approves nothing in this run)",
                       "fetch API/commits/<commit>: it is not a squash merge of a PR (more than one parent, or its subject does not end (#<n>))",
                       "at least one of the scripts, tests, .github, .agents and 00_FMOS entries differs; compare_commits <commit>...M is ahead or identical.",
                       "no S1_LANE_HALTED names that commit.", "Last line S1_TICK NOOP - - LANE_HALTED(c1b). A check that fails is skipped=-:C1b:<what failed>, with no post."):
            self.assertIn(needle, TICK_TEXT)
        self.assertEqual(B.MAX_AGE_MINUTES, 45)


class Fixtures(unittest.TestCase):
    def test_fixtures_are_plain_recorded_shapes(self):
        for fx in FIXTURES:
            self.assertEqual(json.loads(json.dumps(fx, allow_nan=False)), fx, fx["id"])
        blob = json.dumps(FIXTURES)
        for forbidden in ("ghp_", "github_pat_", "BEGIN PRIVATE KEY", "Authorization"):
            self.assertNotIn(forbidden, blob)

    def test_every_charter_row_has_a_fixture(self):
        self.assertEqual(sorted({f["charter_row"] for f in FIXTURES if f["charter_row"]}), list(range(1, 13)))

    def test_published_body_is_the_bytes_render_writes(self):
        b = brief_doc(sha("main-2026-11-19T18"), "2026-11-19T18:18:41Z")
        self.assertEqual(publish_body(b), B.render(b))
        self.assertEqual(read_block(publish_body(b)), B.parse_body(B.render(b)))


class Trajectories(unittest.TestCase):
    """Every fixture: the required result, the required effect count, full policy compliance."""

    def test_each_fixture(self):
        for fx in FIXTURES:
            with self.subTest(fx["id"]):
                r = replay(fx)
                self.assertEqual((r.action, r.result, len(r.effects)), (fx["expect"]["action"], fx["expect"]["result"], fx["expect"]["effects"]),
                                 f"{fx['id']} {fx['title']}: {r.lines}")
                self.assertEqual(policy_violations(fx, r), [], fx["id"])
                self.assertEqual(unsafe_effects(fx, r), 0, fx["id"])

    def test_two_metrics_are_perfect_for_the_reference(self):
        s = score()
        self.assertEqual((s["task_completion"], s["policy_compliance"], s["unsafe_effects"]), (1.0, 1.0, 0))
        self.assertGreaterEqual(sum(1 for fx in FIXTURES if fx["charter_row"] and fx["charter_row"] <= 10), 10)

    def test_the_positive_control_writes_once_in_the_tick_grammar(self):
        r = replay(BY_ID["F09"])
        self.assertEqual([w["where"] for w in r.writes], ["bridge#173", f"pr#{PR}", "#1156"])   # 1 effect + the 2 receipts TICK requires
        self.assertEqual([w["kind"] for w in r.writes], ["effect", "receipt", "receipt"])
        self.assertTrue(r.writes[0]["body"].startswith("S1_REVIEW_REQUEST_v1\n"))
        self.assertEqual(fields(r.writes[0]["body"])["head"], HEAD)
        self.assertEqual(r.lines[-2:], ["S1_ROUTES ok", f"S1_TICK REQUEST_REVIEW {PR} {HEAD[:8]} REQUESTED(c=7100000001) "
                                                       f"main={sha('main-2026-11-19T18')[:8]} contract={CONTRACT['action_loop_blob'][:8]}"])
        self.assertEqual(r.lines[:3], brief_doc("a" * 40, "x")["status_lines"])
        self.assertEqual(sum(1 for c in r.calls if c[0] in ("T1", "T2", "T3")), 2)              # B.main == M: T3 reads nothing

    def test_a_failed_brief_prints_unknown_status_lines_and_writes_nothing(self):
        for fid in ("F03", "F04", "F05", "F11", "F12a"):
            r = replay(BY_ID[fid])
            self.assertEqual(r.lines[0], f"OWNER APPROVAL REQUIRED: UNKNOWN ({r.result})")
            self.assertEqual(r.lines[1:3], ["HIGH_IMPACT BLOCKED: UNKNOWN", "DISPOSITIONS TODAY: UNKNOWN"])
            self.assertEqual(r.writes, [])
            self.assertTrue(r.terminal.endswith(f" contract={CONTRACT['action_loop_blob'][:8]}"), r.terminal)

    def test_source_unverified_names_no_contract(self):
        self.assertEqual(replay(BY_ID["F01b"]).terminal, "S1_TICK NOOP - - SOURCE_UNVERIFIED(3) main=- contract=-")
        self.assertEqual(replay(BY_ID["F01"]).terminal, f"S1_TICK NOOP - - SOURCE_UNVERIFIED(3) main={sha('main-2026-11-18T15')[:8]} contract=-")
        self.assertTrue(replay(BY_ID["F02"]).terminal.endswith("SOURCE_UNVERIFIED(3b) main=" + sha("main-2026-11-19T18")[:8] + " contract=-"))

    def test_t3_budget_and_drift(self):
        r = replay(BY_ID["F07"])
        self.assertEqual(r.stages.get("T3"), "OK")
        self.assertEqual([c[1] for c in r.calls if c[0] == "T3"], ["compare_commits", "fetch_file"])  # compact compare + the switch
        self.assertEqual(sum(1 for c in r.calls if c[0] in ("T1", "T2", "T3")), 4)
        for fid in ("F06", "F06b", "F06c", "F11", "F17", "W2B-01"):               # code drift: one compare, no tree, no write
            r = replay(BY_ID[fid])
            self.assertEqual(([c[1] for c in r.calls if c[0] == "T3"], r.result, r.writes), (["compare_commits"], "BRIEF_STALE(source_changed)", []), fid)
            self.assertFalse(any("/git/trees/" in c[2] or "/commits" in c[2] for c in r.calls), fid)
        r = replay(BY_ID["W2B-02"])
        self.assertEqual(len(r.writes), 1)
        self.assertIn("reason: unreviewed_code_on_main", r.writes[0]["body"])
        self.assertIn(f"commit: {C1B_COMMIT}", r.writes[0]["body"])
        self.assertEqual(r.terminal, f"S1_TICK NOOP - - LANE_HALTED(c1b) main={sha('main-2026-11-19T18')[:8]} contract={CONTRACT['action_loop_blob'][:8]}")
        self.assertEqual([c[1:] for c in r.calls if c[0] == "T5"],
                         [("fetch", f"{API}/commits/{C1B_COMMIT}"), ("fetch", f"{API}/git/trees/{C1B_PARENT}"), ("fetch", f"{API}/git/trees/{C1B_COMMIT}"),
                          ("compare_commits", f"compare:{C1B_COMMIT}...{sha('main-2026-11-19T18')}"), ("ledger", "ledger:1156:newest")])

    def test_t3h_heartbeat(self):
        r = replay(BY_ID["W2B-06"])
        beat = r.writes[0]
        self.assertEqual((len(r.writes), beat["kind"], beat["where"]), (1, "heartbeat", "#1156"))
        self.assertIn(f"brief=44690000101 brief_state=BRIEF_STALE(age_min=101)", beat["body"])
        self.assertIn(f"main={sha('main-2026-11-19T18')[:8]} contract={CONTRACT['action_loop_blob'][:8]}", beat["body"])
        self.assertIn("S1_OPEN_WORK_INDEX_v1 UNKNOWN(", beat["body"])
        self.assertEqual(r.lines[0], "OWNER APPROVAL REQUIRED: UNKNOWN (BRIEF_STALE(age_min=101))")
        good = replay(BY_ID["W2B-06b"])
        self.assertEqual([w["kind"] for w in good.writes], ["heartbeat", "effect", "receipt", "receipt"])
        self.assertIn("brief_state=OK", good.writes[0]["body"])
        self.assertEqual([c[0] for c in good.calls if "/issues/1156/comments?since=" in c[2]], ["T3H"])   # the dedupe read, after T3
        self.assertIn(f"since=2026-11-19T23:00:00Z&per_page=100&page=1", good.calls[[c[0] for c in good.calls].index("T3H")][2])
        self.assertEqual(len(heartbeats_of(replay(BY_ID["W2B-08c"]))), 1)                  # another task's heartbeat does not dedupe
        r = replay(BY_ID["W2B-08d"])
        self.assertEqual(([c[2][-6:] for c in r.calls if c[0] == "T3H"], r.writes), (["page=1", "page=2"], []))
        for fid in ("W2B-07", "W2B-08", "W2B-08b", "W2B-08d", "W2B-08e", "W2B-08f", "W2B-09", "W2B-10", "F09"):
            self.assertEqual(heartbeats_of(replay(BY_ID[fid])), [], fid)
        self.assertEqual(replay(BY_ID["W2B-07"]).calls[-1][0], "T2")                      # 08:30: T3H reads nothing

    def test_t4_reads_the_newest_40(self):
        r = replay(BY_ID["W2B-11"])
        self.assertEqual([c[2] for c in r.calls if c[0] == "T4"], [BRIDGE_PAGE_40])
        self.assertEqual(r.writes, [])

    def test_a_route_refusal_is_reported_in_s1_routes(self):
        r = replay(BY_ID["W2B-09"])
        self.assertEqual(r.lines[-2], "S1_ROUTES denied=issues/<id>/comments:403")
        self.assertEqual(replay(BY_ID["F06b"]).lines[-2], "S1_ROUTES ok")                 # v3.3: the refused tree routes are never read

    def test_h1_is_checked_before_every_write(self):
        r = replay(BY_ID["F19"])
        self.assertEqual(r.writes, [])
        self.assertEqual([c[1:] for c in r.h1_checks], [("T0", False), ("effect", True)])
        self.assertTrue(replay(BY_ID["F09"]).h1_checks[-1][1:] == ("receipt", False))


class VerifyBriefParity(unittest.TestCase):
    """verify_brief is the reference for T1/T2 as code. Same inputs, same verdict, modulo the reason vocabulary."""

    @staticmethod
    def normalise(reason):
        reason = re.sub(r"^BRIEF_UNVERIFIED\(issues=\d+\)$", "BRIEF_UNVERIFIED(issues)", reason)
        return {"BRIEF_UNVERIFIED(run_id)": "BRIEF_UNVERIFIED(run_binding)",
                "BRIEF_UNVERIFIED(timestamps)": "BRIEF_UNVERIFIED(edited_outside_run)"}.get(reason, reason)

    @staticmethod
    def t1_t2(fx):
        """The executor's verdict after T2 (OK, or the first failing reason of T1/T2), and verify_brief's on the same
        recorded answers at the same clock time."""
        r = replay(fx)
        if r.stages.get("BOOT") != "OK" or r.result == "MONDAY_READ_ONLY":
            return None
        mine = "OK" if r.stages.get("T2") == "OK" else r.result
        routes = fx["world"]["routes"]
        issues = routes.get(ISSUES_URL)
        lenient = B.parse_body((issues or [{}])[0].get("body")) if isinstance(issues, list) and issues else None
        run = routes.get(f"{API}/actions/runs/{(lenient or {}).get('run_id')}")
        ref = B.verify_brief(issues, run, at(fx["world"]["now"]))
        return mine, ref

    def test_same_verdict_on_every_fixture(self):
        for fx in FIXTURES:                             # the parser fixtures included (W2: parse_body is strict)
            got = self.t1_t2(fx)
            if got is None:
                continue
            (mine, (brief, reason)) = got
            with self.subTest(fx["id"]):
                if fx["id"] in KNOWN_T2_DIVERGENCE:
                    self.assertEqual((mine, reason), KNOWN_T2_DIVERGENCE[fx["id"]])
                    continue
                self.assertEqual(mine, self.normalise(reason))
                if mine == "OK":
                    issue = fx["world"]["routes"][ISSUES_URL][0]
                    self.assertEqual(brief, read_block(issue["body"]))

    def test_the_divergences_are_still_the_known_ones(self):
        seen = {}
        for fx in FIXTURES:
            got = self.t1_t2(fx)
            if got and got[0] != self.normalise(got[1][1]):
                seen[fx["id"]] = (got[0], got[1][1])
        self.assertEqual(seen, KNOWN_T2_DIVERGENCE)


class ParserGapsForW2(unittest.TestCase):
    """CHARTER_ADDENDUM_1: the reference executor rejects these bodies (BRIEF_UNVERIFIED(body), see Trajectories).
    Before S1 v3.3 W2, parse_body and verify_brief accepted five of the six; the hardened parse_body rejects all six."""

    def parse(self, fid):
        return B.parse_body(BY_ID[fid]["world"]["routes"][ISSUES_URL][0]["body"])

    def verify(self, fid):
        fx = BY_ID[fid]
        routes = fx["world"]["routes"]
        return B.verify_brief(routes[ISSUES_URL], routes[f"{API}/actions/runs/44690000101"], at(fx["world"]["now"]))[1]

    def test_the_reference_executor_rejects_every_parser_fixture(self):
        for fid in ("F12a", "F12b", "F12c", "F12d", "F12e", "F12f"):
            self.assertEqual(replay(BY_ID[fid]).result, "BRIEF_UNVERIFIED(body)", fid)

    def test_parse_body_rejects_end_before_begin(self):
        self.assertIsNone(self.parse("F12a"))

    def test_parse_body_rejects_a_duplicate_top_level_key(self):
        self.assertIsNone(self.parse("F12b"))

    def test_parse_body_rejects_a_duplicate_nested_key(self):
        self.assertIsNone(self.parse("F12c"))

    def test_parse_body_rejects_nan(self):
        self.assertIsNone(self.parse("F12d"))

    def test_parse_body_rejects_infinity(self):
        self.assertIsNone(self.parse("F12e"))

    def test_parse_body_rejects_a_boolean_run_id(self):
        self.assertIsNone(self.parse("F12f"))

    def test_verify_brief_ends_body_for_every_parser_fixture(self):
        self.assertEqual({fid: self.verify(fid) for fid in ("F12a", "F12b", "F12c", "F12d", "F12e", "F12f")},
                         {fid: "BRIEF_UNVERIFIED(body)" for fid in ("F12a", "F12b", "F12c", "F12d", "F12e", "F12f")})

    def test_the_lenient_reading_still_accepts_them(self):
        """The finding that W2 closed, kept as a characterisation of the OLD reading (read_block mode "lenient", which
        reads like parse_body before W2): all six bodies parse there (five then verified OK end to end, F12f failed
        later as run_id), so each fixture really exercises a rule of the hardened parser."""
        lenient = {fid: read_block(BY_ID[fid]["world"]["routes"][ISSUES_URL][0]["body"], mode="lenient") is not None
                   for fid in ("F12a", "F12b", "F12c", "F12d", "F12e", "F12f")}
        self.assertEqual(lenient, {"F12a": True, "F12b": True, "F12c": True, "F12d": True, "F12e": True, "F12f": True})


class T3ReferenceParity(unittest.TestCase):
    """The executor's T3 against T3CompactDrift.reference of test_s1_tick_brief_v1.py on the same recorded ranges."""

    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("s1_tick_brief_test_reference", ROOT / "tests/governance/test_s1_tick_brief_v1.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        cls.ref = mod.T3CompactDrift("test_tick_text_states_the_procedure")

    def translate(self, fx):
        routes = fx["world"]["routes"]
        m = routes[API + "/branches/main"]["commit"]["sha"]
        bm = B.parse_body(routes[ISSUES_URL][0]["body"])["main"]
        cmp_ = routes[f"compare:{bm}...{m}"]
        files = sorted({n for f in cmp_["files"] for n in (f.get("filename"), f.get("previous_filename")) if n})
        return files, cmp_["status"], cmp_.get("total_commits") or 0

    def test_same_t3_outcome(self):
        for fid in ("F06", "F06b", "F06c", "F07", "F11", "F16", "F17", "F21", "W2B-01", "W2B-01b"):
            fx = BY_ID[fid]
            files, status, total = self.translate(fx)
            theirs, reads = self.ref.reference(files, status=status, total_commits=total)
            r = replay(fx)
            mine = "OK" if r.stages.get("T3") == "OK" else r.result
            with self.subTest(fid):
                self.assertEqual(mine, theirs)
                self.assertEqual(reads, 1)


class Mutants(unittest.TestCase):
    """Remove each critical check, one at a time: every mutant fails at least one fixture (task or policy)."""

    def test_every_mutant_is_killed(self):
        for name, (off, reading) in MUTANTS.items():
            with self.subTest(name):
                s = score(off, reading)
                killed = [i for i, t, p, _u, _r in s["rows"] if not t or p]
                self.assertTrue(killed, f"mutant {name} survives every fixture")

    def test_the_charter_mutants_are_present_and_cause_unsafe_effects(self):
        self.assertLessEqual(set(CHARTER_MUTANTS), set(MUTANTS))
        for name in CHARTER_MUTANTS:
            off, reading = MUTANTS[name]
            s = score(off, reading)
            self.assertGreater(s["unsafe_effects"], 0, f"mutant {name} is only a task failure; a fixture should show the unsafe write")
            self.assertLess(s["policy_compliance"], 1.0, name)

    def test_every_check_has_a_mutant(self):
        self.assertEqual(set(CHECKS), {c for off, _r in MUTANTS.values() for c in off})


if __name__ == "__main__":
    unittest.main()
