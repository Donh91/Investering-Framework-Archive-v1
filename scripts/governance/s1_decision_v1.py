"""S1_DECISION_V1: the ONE next action of the S1 lane, decided in GitHub Actions (AGENTS.md section 0.2i).

Pure functions only: no network, no file read, no subprocess, no clock of its own (every caller passes `now`). The
builder (s1_tick_brief_v1.py) calls decide() on the brief it built from native reads and publishes the result as its own
small block at the top of the brief issue; the executor (s1_executor_v1.py) re-reads the facts natively and performs
the action only when the switch on main reads LIVE. The same decide() serves the shadow phase, the executor, the
read-only observer (00_FMOS/S1/OBSERVER_BOOTSTRAP.txt) and the offline replay.

What moved here from the text a language model used to execute (00_FMOS/S1/TICK.md v3.3):
  T0 CLOCK            monday_window(), clock_gate()
  T4 CHOOSE / ORDER   decide(): HALT, then MERGE (LOW before MEDIUM, lowest PR), else NOOP; one action
  T5 F2 judgment      entry_facts(): exclusions 4, 5, 6, 8, 9 as word lists on paths, title and body (best effort,
                      never a proof), the risk class, direction, hold labels, the documentation-only fact
  T5 F4 review        review_gate(): the GitHub-native review policy of the switch; code never merges unreviewed
  T5 F5 lane / rules  lane_gates()
  T3H HEARTBEAT       heartbeat block of the decision; body by heartbeat_body()
  F6/F7 receipts      intent_body(), merge_receipt_body(), halt_body(), op_done_body()
  C10 readback        readback_verdict()
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

SCHEMA = "S1_DECISION_V1"
BEGIN, END = "<!-- S1_DECISION_V1 BEGIN -->", "<!-- S1_DECISION_V1 END -->"
OBSERVER_VERSION = "S1_OBSERVER_v10"       # the read-only ChatGPT task text this decision format serves
MAX_AGE_MINUTES = 45                       # a decision older than this is never acted on and never reported as current
EXECUTE_MAX_AGE_MINUTES = 20               # the executor runs in the build's own workflow run: an older decision is a re-run
EXECUTOR_MODES = ("OFF", "SHADOW", "LIVE")
REVIEW_POLICIES = ("CODEX_FINAL_REQUIRED", "CODEX_CLAUDE_OR_OFFLINE_RECALL", "NATIVE_GATES")
NO_REVIEW_STATES = ("NONE", "UNAVAILABLE", "SILENT", "INADMISSIBLE")   # codex_review(): read completely, and no completed review
# Owner decision 2026-11-25 (review route, Codex recall). The gate passes on (a) the completed Codex review of the exact
# head, (b) a Claude exact-head APPROVE receipt, or (c) the Codex-offline fallback: two independent executor runs that
# agree, and a merge that is flagged for Codex to revisit. (c) merges class LOW only, and it applies only when Codex is
# DEMONSTRABLY unavailable, by evidence read natively, by the build and again by the executor
# (s1_tick_brief_v1.offline_signal; fix round 3). Only a never-edited "@codex review" of the OWNER account after this
# head's last commit counts as a request, and Codex's own activity is read for the whole repository:
#   UNAVAILABLE  the owner asked, Codex answered with its usage-limit sentence, and Codex's newest activity anywhere in
#                the repository is still a usage-limit answer;
#   SILENT       the owner asked, Codex answered nothing on the PR within 24 hours, and Codex has posted nothing anywhere
#                in the repository since the request;
#   LIMIT        nobody asked Codex about this head, and Codex's NEWEST activity anywhere in the repository is a
#                usage-limit answer that is at most 24 hours old (Codex itself says it has no usage).
# No repository variable can switch the fallback on. A request that is pending inside its 24 hours is never "offline".
RECALL_POLICY = "CODEX_CLAUDE_OR_OFFLINE_RECALL"
FALLBACK_MIN_GAP_MINUTES = 50              # the second run starts at least this long after the first run's candidate receipt
FALLBACK_MAX_AGE_HOURS = 24                # an older candidate has expired: the count starts again
FALLBACK_MAX_CANDIDATES = 3                # candidate receipts per PR head, ever; then the head is parked for the owner
RECALL_LABEL = "codex-recall-pending"      # on every PR merged by the fallback, until Codex's completed review of that head
OFFLINE_SIGNALS = ("UNAVAILABLE", "SILENT", "LIMIT")      # s1_tick_brief_v1.offline_signal
REVIEW_ROUTE = re.compile(r"CODEX|CLAUDE|FALLBACK\((?:UNAVAILABLE|SILENT|LIMIT)\)|NONE\(policy=NATIVE_GATES\)")
EXECUTOR_ACTIONS = ("MERGE", "HALT")       # what the executor may do; a heartbeat is observability, never the action
MERGE_RISKS = ("LOW", "MEDIUM")            # HIGH_IMPACT, EXTREME, unclear and OWNER_GATED are never executor merges; HIGH only as
                                           # repository automation's allowlisted stored data (owner addendum c, data_admitted)
RISK_ORDER = ("LOW", "MEDIUM", "HIGH", "HIGH_IMPACT", "EXTREME", "UNCLEAR", "OWNER_GATED")
# The owner's label veto. Names are compared without case, spaces, "_" and "-" (label_key): HIGH_IMPACT, "high impact"
# and High-Impact are one label. Every "risk:" label other than low and medium holds as well (hold_label).
HOLD_LABELS = ("s1-hold", "hold", "on-hold", "do-not-merge", "dnm", "owner-gated", "high-impact", "wip", "draft", "blocked", "P0",
               "priority: high", "priority: critical", "priority: urgent", "risk: high", "auto-trading", "wontfix", "invalid", "duplicate")
TITLE_HOLD = re.compile(r"(?i)^[\s\[\(]*(draft|wip|do[ _-]?not[ _-]?merge|dnm|hold)(?![A-Za-z])")   # a title that says "not yet"
# gates that are the executor's own policy: a PR that only these hold is finished work that waits for the owner's merge
OWNER_ROUTE_GATES = ("C2:judgment:", "C2:risk:", "C2:push_trigger:", "C2:shrinks:", "C5:strategist", "C5:bot_authored", "C5:s1_authored",
                     "C5:codex_authored", "C5:ai_authored", "C5:review_required", "C5:codex_final_required", "C9:attempted_head",
                     "C5:claude_authored", "C5:fallback_parked:")
ORIGIN_WINDOW_MINUTES = 15                 # EVIDENCE_BINDINGS s1_origin_window_minutes: merged_at within this of the intent
CPH = ZoneInfo("Europe/Copenhagen")
SHA40 = re.compile(r"[0-9a-f]{40}")
TASK_ID = "6ae5fd466b48819187abc224ec0f1c5f"
OWNER_ISSUE = 1156
DOC_SUFFIXES = (".md", ".txt", ".rst")
DOCS_ONLY_SUFFIXES = (".md", ".rst")       # the only files a PR may change to merge with no completed review (review_gate)
# AGENTS.md section 0.2c D5 and the manifest's science_gated_prefixes: a research, market or forecast publication
# under these prefixes needs its science owner's gate "regardless of .md suffix". It is never a plain document.
SCIENCE_GATED_PREFIXES = ("04_MARKET_LEARNING/", "04_RESEARCH_LAB/", "05_CYCLE_NAVIGATOR/", "06_RESEARCH_LAB/", "research/")
MANIFEST_NAME = re.compile(r"(?i)^(?:requirements|constraints)[^/]*\.txt$")       # a dependency list is code, not a document
AGENT_FILE = re.compile(r"(?i)^(?:agents|claude|gemini|skill|copilot-instructions)\.md$|prompt|instruction|bootstrap")
DATA_SUFFIXES = (".json", ".jsonl", ".ndjson", ".csv", ".tsv", ".parquet", ".db", ".sqlite", ".log")
BINARY_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".woff", ".woff2", ".ttf", ".parquet", ".zip", ".gz")
RECORD_NAME = re.compile(r"(?i)ledger|receipt|journal|histor|episode|registry|manifest|audit|\bLOG\b|_log\b|changelog")
DATA_PREFIXES = ("data/", "02_DATA_PING/", "03_DAILY_CAPTURE_LOGS/", "03_WEEKLY_OPERATIONS/", "09_SOURCE_QA/", "08_SOURCE_MATERIAL/")
SITE_PREFIX = "05_CYCLE_NAVIGATOR/site/"

# AGENTS.md section 0.2e exclusions 4, 5, 6 and 8, which a reviewer or S1 used to judge. Here they are word lists
# matched on every changed path, every previous_filename, the PR title and the PR body. A match is OWNER_GATED; the lists
# err toward the owner (a market word such as "trade" in a research note costs an owner click, never a merge).
# BEST EFFORT, NEVER A PROOF: a list sees names and prose, not what a diff does, and a synonym it does not hold passes.
# The control for code is therefore the review (review_gate): no policy merges a code change that nobody reviewed.
# Two kinds of entry. A STEM matches anywhere, also inside one lower-case word (autotrader, swapexecutor). A WORD
# (_words) matches between separators: "_", "-", ".", "/", digits, a space, and a camelCase boundary, because every
# text is matched in two forms (word_forms): as written, and with a space at each camelCase boundary (TradeExecutor,
# githubToken and placeOrder hold the words trade, token and order).
_W = r"(?<![A-Za-z])"                       # word start that treats _ - . / and digits as separators
_E = r"(?![A-Za-z])"
_CAMEL = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")


def _words(*alternatives):
    return _W + "(?:" + "|".join(alternatives) + ")" + _E


def word_forms(text):
    """`text` as written, and again with a space at every camelCase boundary."""
    t = str(text or "")
    return t + "\n" + _CAMEL.sub(" ", t)


JUDGMENT = {
    # exclusion 4: credentials, custody, recovery, repository settings (and the usual names of key and credential files)
    "x4": re.compile(r"(?i)secret|credential|passw(?:or)?d|passphrase|api[_ -]?key|private[_ -]?key|signing[_ -]?key|key[_ -]?pair|key[_ -]?store"
                     r"|mnemonic|seed[_ -]?phrase|oauth|bearer|vault|recover|backup|ruleset|branch[_ -]?protect|repo(?:sitory)?[_ -]?settings|custody"
                     r"|\.env(?![A-Za-z0-9])|\.envrc|\.pem(?![A-Za-z0-9])|\.key(?![A-Za-z0-9])|\.p12|\.pfx|\.jks|\.kdbx"
                     r"|id_(?:rsa|dsa|ecdsa|ed25519)|\.netrc|\.npmrc|\.pypirc|\.htpasswd|authorized_keys|known_hosts|"
                     + _words("tokens?", "seal(?:ed|s)?", "sign(?:s|ed|er|ers|ing|ature|atures)?", "seeds?", "auth", "jwt", "cookies?")),
    # exclusion 5: money, trading, order execution, paid APIs
    "x5": re.compile(r"(?i)trading|trader|wallet|payment|spend|budget|billing|cost[_ -]?(?:cap|guard)|api[_ -]?agent|withdraw|deposit|broker|leverage"
                     r"|swap|executor|sniper|money|slippage|"
                     + _words("trad(?:e|es|ed)", "(?<!in )orders?", "funds?", "capital", "paid", "transfers?",
                              "exec(?:s|ute|utes|uted|uting|ution|utions|utable)?", "snip(?:e|es|ed|ing)", "buy(?:s|ing|er|ers)?",
                              "sell(?:s|ing|er|ers)?")),
    # exclusion 6: the public/private boundary
    "x6": re.compile(r"(?i)privat|privacy|public|publish|publication|redact|restricted|personal|" + _words("bridge", "pii")),
    # exclusion 8: Round 3
    "x8": re.compile(r"(?i)round[_ -]?3|round[_ -]?three|" + r"(?<![A-Za-z0-9])r3(?![A-Za-z0-9])"),
}
# The PR BODY (fix round 2). The title and every path get the four word lists above. A body is prose, and most bodies of
# this repository restate the hard lines ("no paid API", "no live trading", "public-safe"): the word lists matched 280 of
# 283 merged PRs on their body alone. So the body is matched with its own, narrower patterns: a positive-action phrase
# ("enables live trading", "places orders"), a strong identifier (send_transaction, private key, .env) or Round 3, and
# never inside a sentence that negates or disclaims it ("no ...", "not ...", "never ...", "without ...", "... unchanged").
# The public/private list (x6) is not matched on the body at all. Best effort, like every list here.
_ACT = (r"(?:enabl\w+|activat\w+|turn\w*\W+on|switch\w*\W+on|go(?:es|ing)?\W+live|start\w*|begin\w*|plac\w+|execut\w+|submit\w+|send\w*|broadcast\w*"
        r"|sign\w*|mov\w+|transfer\w*|withdraw\w*|deposit\w*|spend\w*|pay\w*|rais\w+|increas\w+|buy\w*|sell\w*)")
_OBJ = r"(?:trading|trades?|orders?|swaps?|funds?|money|transactions?|payments?|wallets?|spend(?:ing)?\W+caps?|budgets?|paid\W+apis?)"
BODY_PATTERNS = {
    "x4": re.compile(r"(?i)private[_ -]?keys?|secret[_ -]?keys?|signing[_ -]?keys?|seed[_ -]?phrases?|mnemonic|key[_ -]?pairs?|api[_ -]?keys?|access[_ -]?tokens?"
                     r"|bearer[_ -]?tokens?|passw(?:or)?ds?|credentials?|\.env(?![A-Za-z0-9])|\.pem(?![A-Za-z0-9])|id_(?:rsa|dsa|ecdsa|ed25519)"),
    "x5": re.compile(r"(?i)" + _W + _ACT + r"\W+(?:\w+\W+){0,4}?" + _OBJ + _E
                     + r"|live\W+(?:trading|orders?|execution|funds?|money)|real\W+(?:funds|money)|auto\W?trading|order\W+execution|fund\W+movement"
                     r"|send[_ ]?(?:raw[_ ]?)?transaction|sign[_ ]?transaction|(?:place|create|submit|cancel)[_ ]?orders?|execute[_ ]?(?:trade|swap|order)s?"),
    "x8": JUDGMENT["x8"],
}
BODY_LISTS = tuple(BODY_PATTERNS)
_SENTENCE_END = re.compile(r"[.;!?](?=\s|$)|\n")           # a full stop ends a sentence only before a space: ".env" and "a.py" stay whole
_NEGATION = re.compile(r"(?i)" + _W + r"(?:no|not|never|without|non|none|neither|nor|cannot|zero)" + _E + r"|n't")
_DISCLAIMER = re.compile(r"(?i)" + _W + r"(?:unchanged|untouched|unaffected|excluded|forbidden|prohibited|firewall)" + _E + r"|out\W+of\W+scope")


def body_hits(body):
    """The lists a PR body matches (see BODY_PATTERNS): sentence by sentence, in both word forms, skipping a match that
    a negation precedes in its sentence and every sentence that disclaims ("... unchanged", "out of scope")."""
    hits = set()
    for sentence in _SENTENCE_END.split(str(body or "")):
        if _DISCLAIMER.search(sentence):
            continue
        for form in word_forms(sentence).split("\n"):
            for code, rx in BODY_PATTERNS.items():
                if code not in hits and any(not _NEGATION.search(form[:m.start()]) for m in rx.finditer(form)):
                    hits.add(code)
    return sorted(hits)


# Owner addendum c (2026-11-26): route (c) merges only repository automation's DATA PRs on a positive allowlist.
FALLBACK_AUTHOR = {"login": "github-actions[bot]", "id": 41898282, "type": "Bot"}   # the platform identity of a GITHUB_TOKEN PR
ALLOWLIST_FORBIDDEN = (".github/", ".agents/", "00_FMOS/", "01_CORE_FRAMEWORK/", "07_PROMPTS_AND_AGENTS/", "scripts/", "tests/", "schemas/", SITE_PREFIX)
DATA_STATUSES = ("added", "modified")                     # never removed, renamed, copied or a status this code does not know
MAX_DATA_COMMITS = 5
# Secret SHAPES in a data PR's added lines (a data file holds no names to read, so a word list would park every real
# snapshot, ChatGPT #3 / addendum c): a PEM private key block, and the fixed prefixes of common live tokens. The native
# privacy-scan job (C3) stays the primary credential gate; this only parks.
SECRET_SHAPE = re.compile(r"-----BEGIN [A-Z ]{0,20}PRIVATE KEY-----|(?<![A-Za-z0-9])(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}"
                          r"|sk-[A-Za-z0-9_-]{30,}|AKIA[0-9A-Z]{16}|xox[abprs]-[A-Za-z0-9-]{20,})")
HARD_LINE_LISTS = ("x4", "x5", "x8")                       # credentials and custody, money and trading, Round 3

NAMED_HIGH = re.compile(r"(?i)high[_ -]?impact|" + _W + r"extreme" + _E + r"|owner[_ -]?gated")
DIRECTION_WORDS = re.compile(r"(?i)roadmap|priorit|master[_ -]?plan|" + _W + r"mission" + _E + r"|strateg|deprecat|" + _W + r"remov(?:e|es|ed|al|ing)" + _E
                             + r"|sunset|retire|" + _W + r"new[_ -]?(?:program|producer|consumer)" + _E)
CODE_SUFFIXES = (".py", ".mjs", ".js", ".ts", ".sh", ".rs")


# ----------------------------------------------------------------------------------------------- small helpers
def stamp(value):
    if not isinstance(value, str) or not value:
        raise ValueError("TIMESTAMP_MISSING")
    d = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if d.tzinfo is None:
        raise ValueError("TIMESTAMP_UNAWARE")
    return d.astimezone(timezone.utc)


def iso(d):
    return d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha16(text):
    return hashlib.sha256(str(text).encode("utf-8")).hexdigest()[:16]


def risk_max(*classes):
    """The highest of the given classes; an unknown class reads as UNCLEAR (never as LOW)."""
    best = 0
    for c in classes:
        if c is None:
            continue
        c = str(c).strip().upper()
        best = max(best, RISK_ORDER.index(c) if c in RISK_ORDER else RISK_ORDER.index("UNCLEAR"))
    return RISK_ORDER[best]


# ----------------------------------------------------------------------------------------------- the switch
def thin_config(switch):
    """The two standing decisions of section 0.2i, from the lane switch on main. Missing, unknown or unparsable reads as
    the strictest value: executor OFF and a completed Codex review required."""
    s = switch if isinstance(switch, dict) else {}
    mode, policy = s.get("executor"), s.get("review_policy")
    # fix round 5 (#173/7188234670 P1-02, P1-11; 7191289605 N02): route (c) has its OWN switch, OFF unless it reads
    # exactly "ON". It ships OFF and stays OFF at LIVE until the route (c) pre-LIVE gates of section 0.2i hold.
    return {"executor": mode if isinstance(mode, str) and mode in EXECUTOR_MODES else "OFF",
            "review_policy": policy if isinstance(policy, str) and policy in REVIEW_POLICIES else "CODEX_FINAL_REQUIRED",
            "fallback_route": "ON" if s.get("fallback_route") == "ON" else "OFF"}


def effective_mode(config_mode, hold):
    """The switch on main is the authority; the owner's repository variable S1_EXECUTOR_HOLD can only restrict it.
    ANY non-empty value holds: "1", "true", "off", "0", "no" and "false" all turn a LIVE or SHADOW executor OFF. The
    variable is a kill switch, so no word in it can mean "run"; only deleting it, or leaving it empty, releases the hold."""
    mode = config_mode if config_mode in EXECUTOR_MODES else "OFF"
    held = hold is not None and str(hold) != ""                # fix round 5 (P1-09): whitespace is a non-empty value and holds
    return "OFF" if held else mode


# ----------------------------------------------------------------------------------------------- clock (H1)
def monday_window(now):
    """(start, end) in UTC of the Monday 09:30-10:30 Europe/Copenhagen window that contains `now`, or else the next one
    after it. DST-safe: the local wall clock decides."""
    local = now.astimezone(CPH)
    day = local.date() - timedelta(days=local.weekday())          # Monday of this ISO week
    for week in (0, 1):
        d = day + timedelta(days=7 * week)
        start = datetime(d.year, d.month, d.day, 9, 30, tzinfo=CPH)
        end = datetime(d.year, d.month, d.day, 10, 30, tzinfo=CPH)
        if now.astimezone(timezone.utc) <= end.astimezone(timezone.utc):
            return start.astimezone(timezone.utc), end.astimezone(timezone.utc)
    raise AssertionError("unreachable")


def in_monday_window(now):
    start, end = monday_window(now)
    return start <= now.astimezone(timezone.utc) <= end


def expires_at(generated, max_age=MAX_AGE_MINUTES):
    """The last moment a decision may be acted on: its age limit, cut at the start of the next Monday window."""
    start, end = monday_window(generated)
    limit = generated + timedelta(minutes=max_age)
    if generated < start < limit:
        return start
    return limit


def clock_gate(now, generated_at, expires, max_age=MAX_AGE_MINUTES):
    """None when a write may happen at `now`, else the NOOP result. Checked again before EVERY write (B9 CLOCK)."""
    if not isinstance(now, datetime) or now.tzinfo is None:
        return "BRIEF_STALE(clock)"
    if in_monday_window(now):
        return "MONDAY_READ_ONLY"
    try:
        made, until = stamp(generated_at), stamp(expires)
    except ValueError:
        return "BRIEF_UNVERIFIED(timestamps)"
    age = (now - made).total_seconds() / 60
    if age < -2 or age > max_age or now > until:
        return f"BRIEF_STALE(age_min={int(age)})"
    return None


# ----------------------------------------------------------------------------------------------- push triggers
def filter_regex(pattern):
    """A GitHub Actions path filter pattern as a compiled regex, or None when it cannot be translated (the caller then
    treats the pattern as matching everything). * is any run without '/', ** is any run, **/ also matches nothing,
    ? and + repeat the preceding character, [] is a character class."""
    out, i, n = [], 0, len(pattern)
    try:
        while i < n:
            c = pattern[i]
            if c == "*":
                if pattern[i:i + 3] == "**/":
                    out.append("(?:.*/)?")
                    i += 3
                elif pattern[i:i + 2] == "**":
                    out.append(".*")
                    i += 2
                else:
                    out.append("[^/]*")
                    i += 1
            elif c in "?+":
                if not out:
                    return None
                out.append(c)
                i += 1
            elif c == "[":
                j = pattern.index("]", i + 1)
                body = pattern[i + 1:j]
                if not body or "[" in body or "\\" in body:
                    return None
                out.append("[" + body.replace("^", "\\^") + "]")
                i = j + 1
            elif c == "\\":
                if i + 1 >= n:
                    return None
                out.append(re.escape(pattern[i + 1]))
                i += 2
            else:
                out.append(re.escape(c))
                i += 1
        return re.compile("".join(out))
    except (ValueError, re.error):
        return None


def push_trigger_matches(paths, filters, self_workflow="s1-tick-brief.yml"):
    """Which workflows a push of these paths to main would start, by their `on.push` filters at main. A merge made with
    the workflow token starts NONE of them (GitHub never starts a workflow from an event of GITHUB_TOKEN, except
    workflow_dispatch and repository_dispatch), so such a PR is not an executor merge: the owner route merges it and the
    workflows run. Fail closed: unreadable filters, a push trigger with no paths filter, an untranslatable pattern and
    every negated pattern count as a match. `filters` is [{"workflow": name, "paths": [..] or None,
    "paths_ignore": [..] or None}]; this workflow's own push trigger (a brief rebuild) is not needed after its own merge."""
    if not isinstance(filters, list):
        return ["unknown"]
    hit = []
    for f in filters:
        if not isinstance(f, dict) or not isinstance(f.get("workflow"), str):
            return ["unknown"]
        name = f["workflow"]
        if name == self_workflow:
            continue
        pats, ignore = f.get("paths"), f.get("paths_ignore")
        if pats is None:
            # no paths filter: every push starts it, unless paths-ignore covers EVERY changed path
            covered = isinstance(ignore, list) and bool(paths) and all(
                any((rx := filter_regex(str(p))) is not None and rx.fullmatch(path) for p in ignore if not str(p).startswith("!"))
                for path in paths)
            if not covered:
                hit.append(name)
            continue
        if not isinstance(pats, list):
            hit.append(name)
            continue
        matched = False
        for p in pats:
            p = str(p)
            if p.startswith("!"):
                continue                                         # a negation only ever removes matches: ignored, fail closed
            rx = filter_regex(p)
            if rx is None or any(rx.fullmatch(path) for path in paths):
                matched = True
                break
        if matched:
            hit.append(name)
    return sorted(set(hit))


# ----------------------------------------------------------------------------------------------- per-PR facts
def path_risk(path):
    """REVIEW_ADMISSION.md RISK CLASS as a function of one path. LOW: documentation and tests only. HIGH: stored data,
    ledgers and receipts, site and public output. Everything else is MEDIUM (code and configuration)."""
    p = str(path or "")
    base = p.rsplit("/", 1)[-1]
    low = p.lower()
    if p.startswith("tests/") or "/tests/" in p or base.startswith("test_"):
        return "LOW"
    if p.startswith(SITE_PREFIX) or p.startswith(DATA_PREFIXES) or base.startswith("LATEST_") or RECORD_NAME.search(base):
        return "HIGH"                                            # a file NAMED as a record; a directory name decides nothing
    if low.endswith(DOC_SUFFIXES) and not MANIFEST_NAME.match(base):
        return "LOW"
    if low.endswith(DATA_SUFFIXES) and not p.startswith("scripts/"):
        return "HIGH"
    return "MEDIUM"


def label_key(name):
    """A label name without case, spaces, "_" and "-"."""
    return re.sub(r"[\s_\-]+", "", str(name or "").lower())


HOLD_KEYS = frozenset(label_key(name) for name in HOLD_LABELS)


def hold_label(name):
    key = label_key(name)
    return key in HOLD_KEYS or (key.startswith("risk:") and key not in ("risk:low", "risk:medium"))


def doc_path(path):
    """Is this path a plain document: Markdown or reStructuredText of class LOW, in no dot-directory, under no
    science-gated prefix (section 0.2c D5: genuinely documentation-only, NON-scientific), and not a file that
    instructs an agent (AGENTS.md, a prompt, a bootstrap text)? Everything else needs a review (review_gate)."""
    p = str(path or "")
    return (p.lower().endswith(DOCS_ONLY_SUFFIXES) and path_risk(p) == "LOW" and not any(part.startswith(".") for part in p.split("/"))
            and not p.startswith(SCIENCE_GATED_PREFIXES) and not AGENT_FILE.search(p.rsplit("/", 1)[-1]))


def entry_facts(pr, files, files_complete, push_filters):
    """The facts about one PR that TICK F2 left to judgment, as data: the judgment exclusions (x4 custody, x5 money,
    x6 privacy, x8 Round 3, x9 a class named HIGH_IMPACT or a binary file) on paths, title and body, the path risk
    class, a direction signal, hold labels and a hold title, whether the PR changes documents only, and the
    push-triggered workflows a token merge would not start. Title and body are never published: only the title's hash,
    so the executor notices a retitled PR."""
    pr = pr if isinstance(pr, dict) else {}
    title, body = str(pr.get("title") or ""), str(pr.get("body") or "")
    labels = sorted({str(l.get("name")) for l in pr.get("labels") or [] if isinstance(l, dict) and l.get("name")})
    paths, removed_code, binary = [], False, []
    for f in files or []:
        for p in (f.get("filename"), f.get("previous_filename")):
            if isinstance(p, str) and p:
                paths.append(p)
        name = str(f.get("filename") or "")
        if f.get("status") in ("removed", "renamed") and str(f.get("previous_filename") or name).endswith(CODE_SUFFIXES):
            removed_code = True
        if name.lower().endswith(BINARY_SUFFIXES) and f.get("status") != "removed":
            binary.append(name)
    x, title_forms, body_forms = [f"{code}:body" for code in body_hits(body)], word_forms(title), word_forms(body)
    # fix round 4 (ChatGPT #3 / 7186140947 #4): the hard lines hold on EVERY route, not only on the fallback. The ADDED
    # lines of every file that is not prose (.md, .rst) are read for the credential, money and Round 3 lists; a hit is a
    # judgment gate (the owner's route), whatever the review. A PR that is repository automation's allowlisted data is
    # read for secret shapes instead (data_route), because its data carries those words by nature.
    # fix round 5 (#173/7188234670 P1-04): the REMOVED lines are read too (a deleted guard names what it guarded), and a
    # file whose patch GitHub did not return is "patch_unread", never an empty diff. Still a word list on changed lines:
    # it does not see what a diff does (a changed number, a context line), so it is a net, never the proof (section 0.2i).
    diff_x = set()
    for f in files or []:
        name = str(f.get("filename") or "").lower()
        if name.endswith((".md", ".rst")):
            continue
        patch = f.get("patch")
        if not isinstance(patch, str):
            if not name.endswith(BINARY_SUFFIXES) and (f.get("additions") or 0) + (f.get("deletions") or 0) > 0:
                diff_x.add("patch_unread")
            continue
        changed = "\n".join(line[1:] for line in patch.splitlines() if line[:1] in ("+", "-") and not line.startswith(("+++", "---")))
        forms = word_forms(changed)
        diff_x |= {code for code in HARD_LINE_LISTS if JUDGMENT[code].search(forms) or (code in BODY_PATTERNS and BODY_PATTERNS[code].search(forms))}
    for code, rx in JUDGMENT.items():
        if rx.search(title_forms):
            x.append(f"{code}:title")
        x += [f"{code}:{p}" for p in paths if rx.search(word_forms(p))]
    if NAMED_HIGH.search(title_forms) or NAMED_HIGH.search(body_forms):
        x.append("x9:named_high_impact")
    x += [f"x9:binary:{p}" for p in binary]
    if not files_complete:
        x.append("x9:file_list_incomplete")
    risk = risk_max(*[path_risk(p) for p in paths]) if paths and files_complete else "UNCLEAR"
    held = [l[:40] for l in labels if hold_label(l)]
    named = TITLE_HOLD.search(title)
    if named:
        held.append("title:" + re.sub(r"[ _-]+", "-", named.group(1).lower()))
    return {"x": sorted(set(x))[:8], "x_n": len(set(x)), "risk": risk, "diff_x": sorted(diff_x) if files_complete else ["unknown"],
            "direction": bool(removed_code or DIRECTION_WORDS.search(title_forms) or any(DIRECTION_WORDS.search(word_forms(p)) for p in paths)),
            "hold_labels": held[:3],
            "docs_only": bool(files_complete and paths and all(doc_path(p) for p in paths)),
            "push": push_trigger_matches(paths, push_filters)[:4] if files_complete else ["unknown"],
            "title_sha256": sha16(title)}


def _literal_prefix(rx):
    """The literal start of an anchored allowlist pattern: up to its first regex metacharacter, with "\\." read as "."."""
    out, i = [], 1
    while i < len(rx):
        ch = rx[i]
        if ch == "\\" and i + 1 < len(rx) and rx[i + 1] in "./-_":
            out.append(rx[i + 1])
            i += 2
            continue
        if ch in "\\[](){}.*+?|^$":
            break
        out.append(ch)
        i += 1
    return "".join(out)


def fallback_allowlist(switch):
    """Owner addendum c: the fixed, reviewed POSITIVE allowlist of route (c), from the lane switch on main (so a reviewed
    PR is the only way to change it, and the pins and the switch blob bind it). [(head_ref regex, [(path regex,
    statuses)])], or None when it is missing or ANY part is malformed: route (c) then merges nothing (fail closed).
    Every path pattern is anchored, ends in .json, starts with a literal directory outside code, tests, workflows,
    governance, agent instructions, schemas and the site, and allows only "added" and/or "modified"."""
    doc = switch.get("fallback_data_allowlist") if isinstance(switch, dict) else None
    if not isinstance(doc, dict) or doc.get("author") != FALLBACK_AUTHOR["login"] or not isinstance(doc.get("entries"), list) or not doc["entries"]:
        return None
    out = []
    try:
        for entry in doc["entries"]:
            if not isinstance(entry, dict) or not isinstance(entry.get("paths"), list) or not entry["paths"]:
                return None
            ref = entry.get("head_ref")
            if not (isinstance(ref, str) and ref.startswith("^") and ref.endswith("$") and "/" in _literal_prefix(ref)):
                return None
            rows = []
            for row in entry["paths"]:
                rx, statuses = (row.get("path"), row.get("status")) if isinstance(row, dict) else (None, None)
                prefix = _literal_prefix(rx) if isinstance(rx, str) else ""
                if not (isinstance(rx, str) and rx.startswith("^") and rx.endswith(r"\.json$") and "/" in prefix and ".." not in prefix
                        and not prefix.startswith(ALLOWLIST_FORBIDDEN) and not prefix.startswith(".") and isinstance(statuses, list) and statuses
                        and all(x in DATA_STATUSES for x in statuses)):
                    return None
                rows.append((re.compile(rx), tuple(statuses)))
            ref_rx = re.compile(ref)
            # fix round 5 (P1-01): a path pattern that names the snapshot's week binds it to the head branch's week
            if any("week" in rx.groupindex for rx, _s in rows) and "week" not in ref_rx.groupindex:
                return None
            out.append((ref_rx, rows))
    except re.error:
        return None
    return out


def iso_week_ok(value):
    """Is `value` a real ISO week, YYYY-Www (W01 to W52 or W53 when that year has one)?"""
    m = re.fullmatch(r"([0-9]{4})-W([0-9]{2})", str(value or ""))
    if not m:
        return False
    try:
        return date.fromisocalendar(int(m.group(1)), int(m.group(2)), 1).isocalendar()[1] == int(m.group(2))
    except ValueError:
        return False


def _automation(user):
    return isinstance(user, dict) and all(user.get(k) == v for k, v in FALLBACK_AUTHOR.items())


def data_route(pr, files, files_complete, commits, commits_complete, allowlist):
    """Owner addendum c: is this PR repository automation's DATA PR on the positive allowlist? (True, None) or (False,
    why). All must hold: the PR was opened by github-actions[bot] (login, id and type: the identity GitHub gives a
    GITHUB_TOKEN PR); at most MAX_DATA_COMMITS commits, none a merge, none whose GitHub author or committer is an account
    other than that bot (a person who pushes to the branch is linked to their account); the head branch matches an
    entry; and EVERY changed file matches a path pattern of that entry with an allowed status, has no previous name,
    and is a stored-data file outside every code, test, workflow, governance and config location (checked again here,
    whatever the allowlist says). Anything unread or unknown: False."""
    if not allowlist:
        return False, "no_allowlist"
    pr = pr if isinstance(pr, dict) else {}
    if not _automation(pr.get("user")):
        return False, "author"
    if not files_complete or not files:
        return False, "files"
    if not commits_complete or not commits or len(commits) > MAX_DATA_COMMITS:
        return False, "commits"
    for c in commits:
        if not isinstance(c, dict) or len(c.get("parents") or []) != 1:
            return False, "commits"
        # fix round 5 (#173/7188234670 P1-02): an author or committer GitHub did not link to an account (null) is UNKNOWN,
        # never the bot. Even a linked one is matched by e-mail, not authenticated: that is why route (c) has its own
        # switch, OFF until writer provenance is proven (section 0.2i, route (c) gates). Anything unproven: False.
        if not all(_automation(who) for who in (c.get("author"), c.get("committer"))):
            return False, "commit_identity"
    ref = str(((pr.get("head") or {}).get("ref")) or "")
    for ref_rx, rows in allowlist:
        mref = ref_rx.fullmatch(ref)
        if not mref:
            continue
        week = mref.groupdict().get("week")
        if week is not None and not iso_week_ok(week):
            return False, "week"
        # fix round 5 (P1-01): EXACTLY the entry's files: one file per path row and one row per file (LATEST-only, a
        # weekly file alone, two weekly files or a duplicate row never qualify), and a weekly file of the head's week
        if len(files) != len(rows):
            return False, "path_set"
        used = set()
        for f in files:
            name = f.get("filename") if isinstance(f, dict) else None
            if not isinstance(name, str) or f.get("previous_filename") or name.startswith(ALLOWLIST_FORBIDDEN) \
                    or not name.lower().endswith(".json") or path_risk(name) != "HIGH":
                return False, "path"
            hits = [i for i, (rx, statuses) in enumerate(rows) if rx.fullmatch(name) and f.get("status") in statuses]
            if len(hits) != 1 or hits[0] in used:
                return False, "path_set" if hits else "path"
            used.add(hits[0])
            named = rows[hits[0]][0].fullmatch(name).groupdict().get("week")
            if named is not None and named != week:
                return False, "week"
            if not isinstance(f.get("patch"), str) or SECRET_SHAPE.search(f["patch"]):
                return False, "secret_shape"                     # no readable patch, or a secret's shape in it: never unreviewed data
        return True, None                                        # as many files as rows, each on its own row: exactly the entry
    return False, "head_ref"


def data_admitted(e):
    """Owner addendum c names stored-data snapshots (#2314) as route (c) merges; REVIEW_ADMISSION.md RISK CLASS calls a
    change to stored data HIGH. Such a PR is admitted at class HIGH, and ONLY then: the brief's data_route fact is True,
    the class is exactly HIGH (never HIGH_IMPACT, EXTREME, UNCLEAR or OWNER_GATED, from whatever source), and the
    automatic lane floor is LOW or MEDIUM (no producer path, no site, no exclusion). Every other HIGH stays a C2:risk gate."""
    thin = e.get("thin") if isinstance(e.get("thin"), dict) else {}
    return thin.get("data_route") is True and pr_risk(e) == "HIGH" and (e.get("lane") or {}).get("risk_floor") in MERGE_RISKS


def merge_risk_ok(risk, data_ok):
    return risk in MERGE_RISKS or (risk == "HIGH" and data_ok is True)


def data_fallback(e, route):
    """Fix round 5 (#173/7188234670 P1-03, owner addendum d): the HIGH stored-data admission and the data PR's
    exemption from the changed-line word lists hold ONLY on route (c) itself. A data PR on route (a) or (b) is HIGH
    like any other stored data: C2:risk, the owner's merge."""
    return isinstance(route, str) and route.startswith("FALLBACK(") and data_admitted(e)


def review_route(e, policy, fallback="OFF"):
    """Gate (d) as the switch states it. Returns (route, None) when the review gate passes, else (None, gate).
    Routes: CODEX (the completed Codex review of a head Codex did not write), CLAUDE (a Claude exact-head APPROVE
    receipt, RECALL_POLICY only), FALLBACK(<state>) (the Codex-offline fallback, RECALL_POLICY only) and
    NONE(policy=NATIVE_GATES) (a plain document nobody marked as AI- or bot-written). Findings and an unanswered request
    block under every policy. Every fact is read fail closed: a missing or unknown value is the blocking one."""
    cx = ((e.get("review") or {}).get("codex") or {}).get("status")
    author = e.get("author") if isinstance(e.get("author"), dict) else {}
    thin = e.get("thin") if isinstance(e.get("thin"), dict) else {}
    recall = policy == RECALL_POLICY
    if cx == "FINDINGS":
        return None, "C5:codex_findings"
    if recall and thin.get("claude") not in ("NONE", "APPROVE"):
        return None, "C5:claude_veto" if thin.get("claude") == "VETO" else "C5:review_unreadable"   # a Claude refusal blocks every route
    if cx == "FINAL":
        return ("CODEX", None) if author.get("codex") is False else (None, "C5:codex_authored")   # Codex never reviews its own head
    if recall and thin.get("claude") == "APPROVE" and (cx in NO_REVIEW_STATES or cx == "REQUESTED"):
        # (b), owner decision B (2026-11-26): a Claude exact-head APPROVE counts AT ONCE, also while a Codex request is
        # pending. Never Claude's review of a head Claude wrote, and never S1's own head (S1 writes as the owner account,
        # the account the receipt is checked against, P1-C). Findings, a Claude veto and a native CHANGES_REQUESTED
        # (C5, the brief's gate list) still block.
        if author.get("s1") is not False:
            return None, "C5:s1_authored"
        return ("CLAUDE", None) if thin.get("claude_written") is False else (None, "C5:claude_authored")
    if cx == "REQUESTED":
        return None, "C5:codex_review_pending"
    if cx not in NO_REVIEW_STATES:
        return None, "C5:review_unreadable"                       # NOT_PROVEN, missing, or a status this code does not know
    if recall:
        offline = thin.get("codex_offline")                       # (c): the builder's signal, which must fit this head's Codex state
        if offline not in OFFLINE_SIGNALS or cx != ("NONE" if offline == "LIMIT" else offline):
            return None, "C5:codex_review_required"               # (c) needs proof that Codex is unavailable: ask Codex
        if thin.get("data_route") is not True:
            return None, "C5:fallback_parked:not_data"            # addendum c: (c) merges ONLY automation's allowlisted data PRs; code needs (a) or (b)
        if fallback != "ON":
            return None, "C5:fallback_parked:route_off"           # fix round 5: route (c) has its own switch, OFF until its pre-LIVE gates hold
        if author.get("s1") is not False:
            return None, "C5:s1_authored"                         # S1's own work is never merged by automation's own runs alone
        if author.get("codex") is not False:
            return None, "C5:codex_authored"                      # Codex could never clear the recall of a head it wrote
        if thin.get("p01_named") is not False:
            return None, "C5:fallback_parked:p0p1_comment"        # someone wrote P0 or P1 on the PR and no reviewer has read the head: PARK
        if thin.get("fallback_mismatch") is not False:
            return None, "C5:fallback_parked:mismatch"            # two runs derived different evidence for this head, or unknown: PARK
        n = thin.get("fallback_candidates")
        if type(n) is not int or n >= FALLBACK_MAX_CANDIDATES:
            return None, "C5:fallback_parked:candidates"          # candidates used up without a merge, or the count is unknown: PARK
        return f"FALLBACK({offline})", None
    if policy != "NATIVE_GATES":
        return None, "C5:codex_final_required"
    if author.get("s1") is not False:
        return None, "C5:s1_authored"
    if author.get("codex") is not False:
        return None, "C5:codex_authored"
    if author.get("claude_package") is not False or thin.get("ai") is not False:
        return None, "C5:ai_authored"
    if thin.get("bot") is not False:
        return None, "C5:bot_authored"
    if thin.get("docs_only") is not True:
        return None, "C5:review_required"
    return "NONE(policy=NATIVE_GATES)", None


def review_gate(e, policy, fallback="OFF"):
    return review_route(e, policy, fallback)[1]


def pr_gates(e, cfg, intent_prs=()):
    """Every open gate of one PR for an executor merge, in checklist order (empty: the PR qualifies). The first block
    is the brief's own gate list (C1 writer, C2 owner_gated / overlap, C3 privacy, C4 CI, C5 changes requested, C6
    P0/P1); the rest are the checks S1 used to make itself."""
    if e.get("skip"):
        return [str(e["skip"])]
    gates = list(e.get("open") or [])
    thin = e.get("thin") if isinstance(e.get("thin"), dict) else None
    lane = e.get("lane") or {}
    if thin is None:
        gates.append("C2:facts_not_in_brief")
        thin = {"x": [], "risk": "UNCLEAR", "direction": True, "hold_labels": [], "push": ["unknown"], "docs_only": False, "ai": True,
                "claude": "NOT_PROVEN", "claude_written": True, "data_route": False, "diff_x": ["unknown"], "fallback_candidates": None, "fallback_mismatch": True,
                "codex_offline": None, "p01_named": True}
    if "paths" not in e:
        gates.append("C2:paths_not_in_brief")
    route, review = review_route(e, cfg["review_policy"], cfg.get("fallback_route", "OFF"))
    for x in (thin.get("x") or [])[:2]:
        gates.append(f"C2:judgment:{x}")
    if thin.get("diff_x") != [] and not data_fallback(e, route):
        gates.append(f"C2:judgment:diff:{(thin.get('diff_x') or ['unknown'])[0]}")   # fix round 4: the hard lines hold on every route
    if e.get("shrinks"):
        gates.append("C2:shrinks:" + str(e["shrinks"][0][0]))
    if thin.get("push"):
        gates.append("C2:push_trigger:" + str(thin["push"][0]))
    item = e.get("item") if isinstance(e.get("item"), dict) else {}
    risk = risk_max(lane.get("risk_floor"), thin.get("risk"), item.get("risk"))
    # a data PR that only route (c) can admit, with no route yet, shows its review gate (what route (c) still needs), not
    # the HIGH class it would be admitted at; on a reviewed route (a) or (b) its HIGH class IS the gate (P1-03)
    no_route_yet = route is None and data_admitted(e)
    if not merge_risk_ok(risk, data_fallback(e, route) or no_route_yet):
        gates.append(f"C2:risk:{risk}")
    if thin.get("direction") or item.get("kind") == "DIRECTION":
        gates.append("C5:strategist")
    if e.get("mergeable") in ("dirty", "blocked"):
        gates.append(f"C2:mergeable:{e.get('mergeable')}")
    if review:
        gates.append(review)
    for label in thin.get("hold_labels") or []:
        gates.append(f"C5:hold_label:{label}")
    if e.get("n") in intent_prs:
        gates.append("C9:open_intent")
    if e.get("attempted"):
        gates.append("C9:attempted_head")                         # one merge attempt per PR head, ever: a refused merge is the owner's
    return gates


def pr_risk(e):
    thin = e.get("thin") if isinstance(e.get("thin"), dict) else {}
    item = e.get("item") if isinstance(e.get("item"), dict) else {}
    return risk_max((e.get("lane") or {}).get("risk_floor"), thin.get("risk") or "UNCLEAR", item.get("risk"))


# Fix round 5 (#173/7188234670 P1-08): which gates say "this could not be READ or proven", as opposed to "this was
# read and it blocks". A decision whose NOOP rests on any of them is UNVERIFIED, never a verified "nothing to do", and
# the executor's health line says so. Exact gate codes (the reason vocabulary of this file and of the brief), not
# fragments of a result text; a gate that is not listed is a verified block.
UNVERIFIED_GATES = ("C1:comments_unreadable", "C2:compare_unreadable", "C2:facts_not_in_brief", "C2:paths_not_in_brief",
                    "C2:judgment:x9:file_list_incomplete", "C2:judgment:diff:unknown", "C2:judgment:diff:patch_unread",
                    "C2:push_trigger:unknown", "C2:risk:UNCLEAR", "C4:ci_not_proven", "C5:reviews_unreadable", "C5:review_unreadable",
                    "C6:threads_unreadable", "C7:ledger_unreadable", "C8:ruleset_census", "B1:repository_identity", "C1b:",
                    "pins:", "NOT_READ:")
# Fix round 6 (#173/7194141485 S3): the LANE gates (C7, C8) are typed the other way round: a lane gate is a verified block
# ONLY when it is one of these, read and proven; every other C7 or C8 reason (an unread main-health window, a protection
# flag that is not a real bool, an unstable ruleset census, any reason a later change adds) is UNVERIFIED by default.
VERIFIED_LANE_GATES = ("C7:switch", "C7:main_health:main_health_failed", "C7:main_health:unhalted_failed_run",
                       "C8:ruleset_active", "C8:main_protected")


def unverified_gate(gate):
    """Is this gate (bare, or as a skipped entry "<n>:<gate>" / "lane:<gate>") an unread or unproven fact?"""
    code = str(gate or "")
    head, sep, rest = code.partition(":")
    if sep and (head == "lane" or head.isdigit()):
        code = rest
    if code.startswith("NOT_READ:depth_cap"):
        return False                                            # outside the depth window: coverage, stated per brief (N03)
    if code.startswith("C3:privacy_line:"):
        return code[len("C3:privacy_line:"):][:1].islower()    # a reason (log_unreadable, marker_lines=0), not a scan result
    if code.startswith(("C7:", "C8:")):
        return not (code in VERIFIED_LANE_GATES or code.startswith("C7:halt c="))   # a standing halt the ledger shows
    return code.startswith(UNVERIFIED_GATES)


def lane_gates(brief):
    """The lane-level checks (C7, C8). Any reason: no merge in this decision, whatever the PRs look like."""
    out = []
    lane = brief.get("lane") if isinstance(brief.get("lane"), dict) else {}
    if lane.get("state") != "ON":
        out += [f"C7:{r}" for r in (lane.get("off_reasons") or ["lane_off"])][:3]
    rules = brief.get("rulesets") if isinstance(brief.get("rulesets"), dict) else {}
    active, protected = rules.get("active"), brief.get("main_protected")
    # an active rule or a protected branch: compliance and bypass evidence cannot be proven with the job token. Fix round 6
    # (S3): a proven active rule or a proven protected main is a verified block; a census that is not stable, a count
    # that is not an integer, or a protection flag that is not a real bool is unread (UNVERIFIED), never "proven"
    if rules.get("stable") is not True or type(active) is not int:
        out.append("C8:ruleset_census")
    elif active != 0:
        out.append("C8:ruleset_active")
    elif protected is True:
        out.append("C8:main_protected")
    elif protected is not False:
        out.append("C8:protection_unreadable")
    if not isinstance(brief.get("repo"), dict) or brief["repo"].get("identity") is not True:
        out.append("B1:repository_identity")
    return out


# ----------------------------------------------------------------------------------------------- the decision
def _noop(base, result, skipped=()):
    d = dict(base, action="NOOP", result=result, pr=None, head=None, merge=None, halt=None, skipped=list(skipped)[:6])
    return d


def decide(brief, now=None):
    """S1_DECISION_V1 from one S1_TICK_BRIEF_V1 (a dict as build_brief() returns it). Total: any missing or malformed
    part of the brief ends in a NOOP with its reason, never in an exception and never in an action.

    Fix round 5 (#173/7191289605 N07): totality is ENFORCED here, not only claimed. Any exception inside the rules (a
    nested value of a shape the rules did not expect) is the NOOP BRIEF_UNVERIFIED(decide:<type>), so the publish job
    still publishes the brief the live ChatGPT lane reads, and no malformed shape can become an action."""
    try:
        return _decide(brief, now)
    except Exception as exc:                                    # noqa: BLE001  (a defect or a malformed brief: never an action)
        d = _decide(None, None)
        d["result"] = f"BRIEF_UNVERIFIED(decide:{type(exc).__name__})"
        d["tick"] = f"S1_TICK NOOP - - {d['result']} main=- contract=-"
        d["tick"] = d["tick"] if d.get("executor") == "LIVE" else shadow_tick(d["tick"])
        d["print"] = observer_print(d)
        return d


def _decide(brief, now=None):
    b = brief if isinstance(brief, dict) else {}
    pins = b.get("pins") if isinstance(b.get("pins"), dict) else {}
    cfg = b.get("thin") if isinstance(b.get("thin"), dict) else {}
    cfg = {"executor": cfg.get("executor") if cfg.get("executor") in EXECUTOR_MODES else "OFF",
           "review_policy": cfg.get("review_policy") if cfg.get("review_policy") in REVIEW_POLICIES else "CODEX_FINAL_REQUIRED",
           "fallback_route": "ON" if cfg.get("fallback_route") == "ON" else "OFF"}
    main = b.get("main") if isinstance(b.get("main"), str) and SHA40.fullmatch(b.get("main") or "") else None
    contract8 = str(pins.get("action_loop_blob") or "")[:8] or "-"
    try:
        made = stamp(b.get("generated_at"))
    except ValueError:
        made = None
    now = now if isinstance(now, datetime) and now.tzinfo is not None else made
    lines = b.get("status_lines")
    if not (isinstance(lines, list) and len(lines) == 3 and all(isinstance(x, str) for x in lines)):
        lines = ["OWNER APPROVAL REQUIRED: UNKNOWN (brief_unreadable)", "HIGH_IMPACT BLOCKED: UNKNOWN", "DISPOSITIONS TODAY: UNKNOWN"]
    base = {"schema": SCHEMA, "id": f"{b.get('run_id')}.{b.get('run_attempt')}", "run_id": b.get("run_id"), "run_attempt": b.get("run_attempt"),
            "generated_at": iso(made) if made else None, "expires_at": iso(expires_at(made)) if made else None,
            "main": main, "contract_blob": pins.get("contract_blob") if SHA40.fullmatch(str(pins.get("contract_blob") or "")) else None,
            "pins_ok": pins.get("ok") is True,
            "observer": OBSERVER_VERSION, "executor": cfg["executor"], "review_policy": cfg["review_policy"],
            "heartbeat": {"due": False}, "advice": [], "status_lines": list(lines), "contract": contract8, "recall": {"pending": None},
            "unverified": []}

    def done(d):
        pr, h8 = (d["pr"] if d["pr"] is not None else "-"), (d["head"][:8] if d.get("head") else "-")
        # A decision is never a merge: the line the observer prints is always NOOP with what was DECIDED (ACTION_LOOP
        # RECEIPTS: never claim a merge you did not read back). The executor's own run prints the outcome.
        d["tick"] = f"S1_TICK NOOP {pr} {h8} {d['result']} main={(main or '-')[:8]} contract={contract8}"
        if cfg["executor"] != "LIVE":
            d["tick"] = shadow_tick(d["tick"])                   # fix round 6 (F3): never a ready-made S1_TICK line in SHADOW
        d["print"] = observer_print(d, b.get("ledger"))
        return d

    if made is None or main is None or not isinstance(b.get("run_id"), int) or isinstance(b.get("run_id"), bool):
        return done(_noop(base, "BRIEF_UNVERIFIED(body)"))
    if pins.get("ok") is not True:
        why = (pins.get("mismatch") or ["pins"])[0] if isinstance(pins.get("mismatch"), list) else "pins"
        step = "3b" if why == "bootstrap:3b" else "3"
        return done(_noop(base, f"SOURCE_UNVERIFIED({step})", [f"lane:pins:{why}"]))
    # ChatGPT audit A22: PRs beyond the build's depth (NOT_READ:depth_cap) are per-PR unknowns, not global ones. Such a
    # PR is never a candidate (it carries `skip`), and nothing it holds can change the lane: halts and intents are on
    # #1156, main is read, C1b reads main's history. So a brief whose ONLY unread item is depth_cap still decides over
    # the PRs it read in full. Every other unread item (ledger, pulls, identity, C1b, errors, brief_too_large) is global.
    depth_only = b.get("complete") is False and b.get("unread") == ["depth_cap"] and b.get("incomplete") == "depth_cap"
    if b.get("complete") is not True and not depth_only:
        return done(_noop(base, f"BRIEF_INCOMPLETE({b.get('incomplete') or 'unknown'})"))
    if in_monday_window(now) or in_monday_window(made):
        return done(_noop(base, "MONDAY_READ_ONLY"))
    ledger = b.get("ledger") if isinstance(b.get("ledger"), dict) else {}
    base["heartbeat"] = {"due": b.get("heartbeat_due") is True and ledger.get("read") is True}
    base["advice"] = [{k: x.get(k) for k in ("action", "pr", "head", "how", "reason") if x.get(k) is not None}
                      for x in (b.get("ranked") or b.get("next") or []) if isinstance(x, dict) and x.get("action") in ("REQUEST_REVIEW", "REPAIR")][:3]
    # Codex recall (owner decision 2026-11-25): every fallback merge waits for Codex's completed review of its head.
    recall = b.get("recall") if isinstance(b.get("recall"), dict) else {}
    items = [i for i in (recall.get("items") or []) if isinstance(i, dict) and type(i.get("pr")) is int and SHA40.fullmatch(str(i.get("head") or ""))]
    base["recall"] = {"pending": recall.get("pending") if type(recall.get("pending")) is int and recall["pending"] >= 0 else None}   # fix round 6: a negative count is unread
    if (b.get("codex") or {}).get("available") is True:           # Codex answers again: ask it to review each pending merged head
        base["advice"] += [{"action": "REQUEST_REVIEW", "pr": i["pr"], "head": i["head"], "how": "CODEX_RECALL"}
                           for i in items if i.get("codex") in ("NONE", "SILENT", "UNAVAILABLE")][:3]
    notes = []
    waiting = [i for i in items if i.get("codex") != "FINAL"]    # P2-D: pending by Codex's native state; "?" = not read in this build
    if base["recall"]["pending"] != 0:
        notes.append(f"CODEX_RECALL_PENDING({base['recall']['pending'] if base['recall']['pending'] is not None else 'UNKNOWN'}): "
                     + (" ".join(f"#{i['pr']}" + ("?" if i.get("codex") == "NOT_READ" else "") for i in waiting[:6]) or "-"))
    findings = [i for i in items if i.get("codex") == "FINDINGS"]
    if findings:
        notes.append("CODEX_RECALL_FINDINGS: " + " ".join(f"#{i['pr']} {i['head'][:8]}" for i in findings[:4]) + " (revert or fix required)")
    # route (b) merges whose receipt nobody checked against the Bridge (P1-C): the owner's line only, until the owner clears it
    receipts = b.get("claude_receipts") if isinstance(b.get("claude_receipts"), dict) else {}
    if receipts.get("unverified") != 0:
        loose = [i for i in (receipts.get("items") or []) if isinstance(i, dict) and type(i.get("pr")) is int]
        notes.append(f"CLAUDE_RECEIPT_UNVERIFIED({receipts['unverified'] if type(receipts.get('unverified')) is int else 'UNKNOWN'}): "
                     + (" ".join(f"#{i['pr']}" for i in loose[:6]) or "-"))
    watch = b.get("executor_watch") if isinstance(b.get("executor_watch"), dict) else {}
    if cfg["executor"] != "OFF" and watch.get("state") != "OK":   # fix round 4 (#8): a missing or degraded executor is on the owner's line
        notes.append(f"EXECUTOR_{watch.get('state') if isinstance(watch.get('state'), str) and watch.get('state').isalpha() else 'UNKNOWN'}"
                     f"(run={watch.get('run') if type(watch.get('run')) is int else '-'})")
    if notes:
        first = base["status_lines"][0]
        base["status_lines"] = [first + " ; " + " ; ".join(notes)] + base["status_lines"][1:]

    # 1. HALT: a commit on main that is not a squash merge and changed code (C1b), then a failed main-health run after
    #    a lane merge (C7). A halt is the decision's action; nothing merges in a decision that halts.
    c1b = b.get("c1b") if isinstance(b.get("c1b"), dict) else {}
    halt = c1b.get("halt") if isinstance(c1b.get("halt"), dict) else None
    lane = b.get("lane") if isinstance(b.get("lane"), dict) else {}
    health = lane.get("health") if isinstance(lane.get("health"), dict) else {}
    if halt and SHA40.fullmatch(str(halt.get("commit") or "")) and SHA40.fullmatch(str(halt.get("parent") or "")):
        d = dict(base, action="HALT", result=f"DECIDED_HALT(c1b,executor={cfg['executor']})", pr=None, head=None, merge=None, skipped=[],
                 halt={"source": "C1B", "commit": halt["commit"], "parent": halt["parent"], "entries": list(halt.get("entries") or [])[:5]})
        return done(d)
    failed = [r for r in (health.get("unhalted_failed_runs") or []) if isinstance(r, int) and not isinstance(r, bool)]
    if failed:
        d = dict(base, action="HALT", result=f"DECIDED_HALT(main_health,executor={cfg['executor']})", pr=None, head=None, merge=None, skipped=[],
                 halt={"source": "C7", "run": failed[0]})
        return done(d)

    # 2. MERGE: the lane, then every PR in rank order (LOW before MEDIUM, then the lowest number); the first that has
    #    no open gate is the ONE merge of this decision.
    skipped = [f"lane:{g}" for g in lane_gates(b)]
    intents = b.get("open_intents") if isinstance(b.get("open_intents"), list) else []
    if ledger.get("read") is not True:
        skipped.append("lane:C7:ledger_unreadable")
    if ("gaps" in c1b and (not isinstance(c1b["gaps"], list) or c1b["gaps"])) \
            or ("gaps" not in c1b and isinstance(c1b.get("gap"), dict) and c1b["gap"].get("from_unknown") is True):
        skipped.append("lane:C1b:history_gap")                  # fix round 4: history this brief did not prove clean: no merge now
    if c1b.get("open") is not None or c1b.get("checked_through") != b.get("main") or c1b.get("fence"):
        skipped.append("lane:C1b:open_segment")                 # fix round 6: the scan has not proven B.main yet (it resumes next build)
    intent_prs = {i.get("pr") for i in intents if isinstance(i, dict)}
    if any(isinstance(i, dict) and i.get("kind") == "S1_LANE_MERGE_INTENT_v1" for i in intents):
        skipped.append("lane:C9:open_merge_intent")              # one merge at a time: the readback settles it first
    entries = [e for e in (b.get("prs") or []) if isinstance(e, dict) and isinstance(e.get("n"), int)]
    ranked, unverified = [], [s for s in skipped if unverified_gate(s)]
    for e in entries:
        gates = pr_gates(e, cfg, intent_prs)
        ranked.append(((RISK_ORDER.index(pr_risk(e)), len(gates), e["n"]), e, gates))
        unverified += [f"{e['n']}:{g}" for g in gates if unverified_gate(g)][:1]
    base["unverified"] = sorted(set(unverified))[:6]
    ranked.sort(key=lambda r: r[0])
    chosen, owner_route = None, []
    for _key, e, gates in ranked:
        if gates:
            if not e.get("skip") or not str(e.get("skip")).startswith("NOT_READ"):
                skipped.append(f"{e['n']}:{gates[0]}")
            if not e.get("skip") and all(g.startswith(OWNER_ROUTE_GATES) for g in gates) and isinstance(e.get("head"), str):
                owner_route.append(f"#{e['n']} {e['head'][:8]} (owner_merge:{gates[0][:60]})")
            continue
        if chosen is None and not skipped_lane(skipped):
            chosen = e
    if owner_route:
        # finished work the executor may not merge (its policy, not a failed gate): the owner's first line names it
        first = base["status_lines"][0]
        head, sep, rest = first.partition(": ")
        shown = ([] if rest.strip() in ("NONE", "") else [rest]) + owner_route[:5]
        base["status_lines"] = [f"{head}{sep}{' ; '.join(shown)}"] + base["status_lines"][1:]
    if chosen is not None:
        e = chosen
        ci = (e.get("ci") or {}).get("tuples") or {}
        route = review_route(e, cfg["review_policy"], cfg["fallback_route"])[0]
        merge = {"pr": e["n"], "sha": e["head"], "merge_method": "squash", "risk": pr_risk(e), "data": data_fallback(e, route),
                 "review": route,
                 "files": e.get("files"), "paths_sha256": e.get("paths_sha256"), "title_sha256": (e.get("thin") or {}).get("title_sha256"),
                 "ci": {name: [t.get("run"), t.get("att"), t.get("job")] for name, t in sorted(ci.items())},
                 "health_run": health.get("run_id")}
        d = dict(base, action="MERGE", result=f"DECIDED_MERGE(executor={cfg['executor']})", pr=e["n"], head=e["head"], merge=merge, halt=None,
                 skipped=[s for s in skipped if not s.startswith(f"{e['n']}:")][:6])
        return done(d)
    reasons = ";".join(skipped[:3]) if skipped else "brief_empty"
    return done(_noop(base, f"NOTHING_ACTIONABLE(skipped={reasons})", skipped))


def skipped_lane(skipped):
    return any(s.startswith("lane:") for s in skipped)


SHADOW_TICK = "SHADOW_RECORD_NOT_A_TICK"


def shadow_tick(tick):
    """Fix round 6 (#2337 F3): outside LIVE the decision block is a record of what the executor WOULD do, published in the
    issue that the live ChatGPT lane (TICK.md v3.3) reads. It carries no S1_TICK line a reader could copy: the same
    fields, under a token that is not one (TICK.md's NOOP results and its S1_TICK line are S1's own, from its own reads)."""
    return SHADOW_TICK + " " + str(tick)[len("S1_TICK "):] if str(tick).startswith("S1_TICK ") else str(tick)


def observer_print(d, ledger=None):
    """D.print: the exact lines the read-only observer prints, in order (the three owner lines, what the executor last
    did according to the ledger the brief read, S1_ROUTES, and the S1_TICK line last)."""
    last = (ledger or {}).get("last_action") if isinstance(ledger, dict) else None
    did = f"{last.get('action')}@{last.get('at')}(c={last.get('id')})" if isinstance(last, dict) else "NONE"
    pending = (d.get("recall") or {}).get("pending")
    return list(d["status_lines"]) + [f"S1_EXECUTOR mode={d['executor']} last_action={did} recall_pending={pending if pending is not None else 'UNKNOWN'}",
                                      "S1_ROUTES ok", d["tick"]]


# ----------------------------------------------------------------------------------------------- the block
def decision_schema_ok(d):
    sha_or_null = lambda v: v is None or (isinstance(v, str) and SHA40.fullmatch(v) is not None)
    if not isinstance(d, dict) or d.get("schema") != SCHEMA or d.get("action") not in ("NOOP", "MERGE", "HALT"):
        return False
    want = "S1_TICK NOOP " if d.get("executor") == "LIVE" else SHADOW_TICK + " NOOP "
    if not (isinstance(d.get("result"), str) and isinstance(d.get("tick"), str) and d["tick"].startswith(want)):
        return False
    if d["result"].startswith("DECIDED_") != (d["action"] != "NOOP") or (d["action"] != "NOOP" and not d["result"].startswith(f"DECIDED_{d['action']}(")):
        return False
    lines = d.get("status_lines")
    if not (isinstance(lines, list) and len(lines) == 3 and all(isinstance(x, str) for x in lines)):
        return False
    if not (sha_or_null(d.get("main")) and sha_or_null(d.get("head")) and sha_or_null(d.get("contract_blob")) and type(d.get("pins_ok")) is bool):
        return False
    if d.get("executor") not in EXECUTOR_MODES or d.get("review_policy") not in REVIEW_POLICIES:
        return False
    if not isinstance(d.get("heartbeat"), dict) or type(d["heartbeat"].get("due")) is not bool or not isinstance(d.get("skipped"), list):
        return False
    out = d.get("print")
    if not (isinstance(out, list) and len(out) == 6 and all(isinstance(x, str) for x in out) and out[:3] == lines
            and out[3].startswith("S1_EXECUTOR ") and out[4] == "S1_ROUTES ok" and out[5] == d["tick"]):
        return False
    recall = d.get("recall")
    if not isinstance(recall, dict) or not (recall.get("pending") is None or (type(recall.get("pending")) is int and recall["pending"] >= 0)):
        return False
    if not (isinstance(d.get("unverified"), list) and all(isinstance(x, str) for x in d["unverified"])):
        return False
    if d["action"] == "MERGE":
        m = d.get("merge")
        if not (isinstance(m, dict) and isinstance(m.get("review"), str) and REVIEW_ROUTE.fullmatch(m["review"])):
            return False
        return (isinstance(m, dict) and type(m.get("pr")) is int and m.get("pr") == d.get("pr") and isinstance(m.get("sha"), str)
                and SHA40.fullmatch(m["sha"]) is not None and m["sha"] == d.get("head") and m.get("merge_method") == "squash"
                and merge_risk_ok(m.get("risk"), m.get("data")) and (m.get("data") is not True or m["review"].startswith("FALLBACK("))
                and d.get("halt") is None and d.get("pins_ok") is True and d.get("main") is not None)
    if d["action"] == "HALT":
        h = d.get("halt")
        if not isinstance(h, dict) or d.get("merge") is not None or d.get("pr") is not None:
            return False
        if h.get("source") == "C1B":
            return SHA40.fullmatch(str(h.get("commit") or "")) is not None and SHA40.fullmatch(str(h.get("parent") or "")) is not None
        return h.get("source") == "C7" and type(h.get("run")) is int
    return d.get("merge") is None and d.get("halt") is None and d.get("pr") is None and d.get("head") is None


def same_decision(a, b):
    """Two decisions are the same object apart from the three owner lines, the skipped list and the advice, which
    render_issue() may cut to keep the block small."""
    cut = ("status_lines", "skipped", "advice", "print")
    strip = lambda d: {k: v for k, v in d.items() if k not in cut} if isinstance(d, dict) else None
    return strip(a) is not None and strip(a) == strip(b)


def _unique_pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate key {key!r}")
        out[key] = value
    return out


def _no_constant(name):
    raise ValueError(f"not JSON: {name}")


def render_decision(decision):
    """The decision's own block, placed FIRST in the brief issue body so that a reader needs only the top of it."""
    text = json.dumps(decision, separators=(",", ":"), sort_keys=True).replace("<", "\\u003c").replace("`", "\\u0060")
    note = "" if decision.get("executor") == "LIVE" else \
        ("\n\nSHADOW RECORD ONLY (fix round 6, F3): what the GitHub executor WOULD do. Not the S1 tick and never an "
         "instruction: S1 (00_FMOS/S1/TICK.md) reads only the S1_TICK_BRIEF_V1 block below and acts on its own reads.")
    return (f"{SCHEMA} id={decision.get('id')} generated_at={decision.get('generated_at')} main={decision.get('main')} "
            f"action={decision.get('action')}{note}\n\n{BEGIN}\n```json\n{text}\n```\n{END}\n\n")


def decision_block(body):
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


def parse_decision(body):
    """The inverse of render_decision(): one marker pair, one fenced strict JSON object (unique keys, no NaN) that
    passes decision_schema_ok. Anything else is None."""
    block = decision_block(body)
    if block is None:
        return None
    try:
        doc = json.loads(block, object_pairs_hook=_unique_pairs, parse_constant=_no_constant)
    except (ValueError, RecursionError):
        return None
    return doc if decision_schema_ok(doc) else None


# ----------------------------------------------------------------------------------------------- comment bodies
def intent_body(decision, repo_id, loop_blob, run_id):
    m = decision["merge"]
    return "\n".join([
        "S1_LANE_MERGE_INTENT_v1", f"pr: {m['pr']}", f"head: {m['sha']}", f"main: {decision['main']}", f"repo_id={repo_id}",
        f"loop={loop_blob}", f"brief={decision['run_id']}", f"decision={decision['id']}", f"executor: GITHUB run={run_id}",
        f"risk: {m['risk']}", f"review: {m['review']}", f"paths_sha256: {m.get('paths_sha256')}", f"contract={decision['contract']}", f"task: {TASK_ID}"])


def merge_receipt_body(decision, repo_id, intent_id, readback, run_id, privacy_run, reconciled=False, claude=None, health_run=None):
    m = decision["merge"] if isinstance(decision.get("merge"), dict) else {}
    ci = " ".join(f"ci={name}@{v[0]}.{v[1]}" for name, v in sorted((m.get("ci") or {}).items()) if isinstance(v, list) and len(v) >= 2)
    c = claude or {}
    receipt = [] if m.get("review") != "CLAUDE" else [                 # route (b): what was accepted, and that nobody checked it against the Bridge
        f"claude_request: {c.get('request', 'unavailable')}", f"claude_request_sha256: {c.get('request_sha256', 'unavailable')}",
        f"claude_receipt_id: {c.get('receipt', 'unavailable')}", f"claude_receipt_sha256: {c.get('receipt_sha256', 'unavailable')}",
        f"claude_independence: {c.get('independence', 'unavailable')}", f"report_blob: {c.get('report_blob', 'unavailable')}",
        f"bridge_commit: {c.get('bridge_commit', 'unavailable')}", "claude_receipt: UNVERIFIED"]
    # fix round 5 (#173/7190895883 D03): four mains, each what it is (the decision's, the one the final look verified,
    # the squash commit's actual parent, main after the merge), and a reconciled receipt claims nothing it did not read
    rules = "rules: UNVERIFIED(reconciled)" if reconciled else "rules: no_active_ruleset_and_main_unprotected(final_look)"
    health = "main_health=UNVERIFIED(reconciled)" if reconciled else f"main_health=final_look run={health_run if health_run is not None else 'unavailable'}"
    return "\n".join([
        "S1_LANE_MERGE_v1" + (" reconciled" if reconciled else ""), f"pr: {readback['pr']}", f"head: {readback['head']}",
        f"merge: {readback['merge_commit']}", f"review: {m.get('review', 'unavailable')}",
        # fix round 4 (#173/7186140947 finding 06): a receipt never claims more than was verified
        f"privacy=NO_RESTRICTED_CONTENT run={privacy_run}" if privacy_run is not None else "privacy=UNVERIFIED run=unavailable", ci or "ci=unavailable",
        f"decision_main: {decision.get('main')}", f"verified_main: {readback.get('verified_main') or 'UNVERIFIED'}",
        f"merge_parent: {readback.get('merge_parent') or 'UNVERIFIED'}", f"main_after: {readback['main_after']}",
        f"blob_match: {readback['paths']} paths", f"delta_match: {readback.get('delta') or 'UNVERIFIED'}",
        rules, f"repo_id={repo_id}", f"intent: {intent_id}",
        health, f"brief={decision.get('run_id')}", f"decision={decision.get('id')}",
        "merge_execution_origin: " + ("UNKNOWN" if reconciled else f"S1_GITHUB_EXECUTOR run={run_id}"),
        f"executor: GITHUB run={run_id if run_id is not None else '-'}",
        f"item: pr:{readback['pr']} state: MERGED", "closure: OBSERVING", f"contract={decision.get('contract')}", f"task: {TASK_ID}"] + receipt)


def fallback_evidence(pr, head, risk, files, paths_sha256, title_sha256, body, ci, policy=None):
    """What one fallback run derived about the PR, from ITS OWN native reads, as one hash. Two runs agree when the hashes
    are equal: the same head, the same file set, title and body, the same risk class, the same CI runs and jobs, and
    (ChatGPT audit A09) the same policy epoch: the RUNTIME_CONTRACT blob and the review policy the run verified, so a
    candidate of an older contract or policy never counts for a newer one. Main is not part of it: a data-only move of
    main is allowed, a code move stops each run (no_code_drift). The Codex-offline signal is not part of it either:
    every run has to prove that for itself, and the signal may differ."""
    doc = {"pr": pr, "head": head, "risk": risk, "files": files, "paths_sha256": paths_sha256, "title_sha256": title_sha256,
           "body_sha256": sha16(body), "ci": ci, "policy": policy}
    return hashlib.sha256(json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:32]


def candidate_body(decision, evidence, offline, n, run_id):
    m = decision["merge"]
    return "\n".join(["S1_FALLBACK_CANDIDATE_v1", f"pr: {m['pr']}", f"head: {m['sha']}", f"main: {decision['main']}", f"evidence: {evidence}",
                      f"risk: {m['risk']}", f"offline: {offline}", f"candidate_n: {n}", f"decision={decision['id']}",
                      f"executor: GITHUB run={run_id}", f"contract={decision['contract']}", f"task: {TASK_ID}"])


def recall_pending_body(decision, merge_commit, candidate_id, first_run, run_id):
    m = decision["merge"]
    return "\n".join(["S1_CODEX_RECALL_PENDING_v1", f"pr: {m['pr']}", f"head: {m['sha']}", f"merge: {merge_commit}", f"runs: {first_run},{run_id}",
                      f"candidate: {candidate_id}", f"label: {RECALL_LABEL}", f"review: {m['review']}",
                      "clears_on: the completed Codex review of this head", f"executor: GITHUB run={run_id}",
                      f"contract={decision['contract']}", f"task: {TASK_ID}"])


def recall_cleared_body(pr, head, requested_at, contract, run_id):
    return "\n".join(["S1_CODEX_RECALL_CLEARED_v1", f"pr: {pr}", f"head: {head}", f"codex_review_requested_at: {requested_at}",
                      "codex: FINAL", f"executor: GITHUB run={run_id}", f"contract={contract}", f"task: {TASK_ID}"])


def halt_body(reason, pr=None, head=None, commit=None, run=None, detail=None, contract="-", run_id=None, intent=None):
    lines = [f"S1_LANE_HALTED PR={pr if pr is not None else '-'} head={head or '-'}", f"reason: {reason}"]
    if intent is not None:
        lines.append(f"intent: {intent}")                      # the intent this halt is the outcome of (A10: exact settlement)
    if commit:
        lines.append(f"commit: {commit}")
    if run is not None:
        lines.append(f"run={run}")
    if detail:
        lines.append(f"detail: {detail}")
    lines += [f"executor: GITHUB run={run_id if run_id is not None else '-'}", f"contract={contract}", f"task: {TASK_ID}"]
    return "\n".join(lines)


def op_done_body(intent_id, result, evidence, contract="-", run_id=None):
    return "\n".join(["S1_OP_DONE_v1", f"intent: {intent_id}", f"result: {result}", f"evidence: {evidence}",
                      f"executor: GITHUB run={run_id if run_id is not None else '-'}", f"contract={contract}", f"task: {TASK_ID}"])


def heartbeat_body(decision, brief, ticks_24h, mode, run_id):
    ledger = brief.get("ledger") if isinstance(brief.get("ledger"), dict) else {}
    last = ledger.get("last_action") if isinstance(ledger.get("last_action"), dict) else None
    gap = ((brief.get("c1b") or {}).get("gap") or {}) if isinstance(brief.get("c1b"), dict) else {}
    return "\n".join([
        f"S1_HEARTBEAT_v1 main={str(decision.get('main') or '-')[:8]} contract={decision.get('contract')} "
        f"ticks_24h={ticks_24h if isinstance(ticks_24h, int) and not isinstance(ticks_24h, bool) else 'UNKNOWN'} last_noop=UNKNOWN "
        f"last_action={(last['action'] + '@' + last['at']) if last else 'NONE'} "
        f"open_ops={(ledger.get('open_intents') or {}).get('count') if ledger.get('read') else 'UNKNOWN'} closures=UNKNOWN",
        f"brief={decision.get('run_id')} brief_state=OK executor=GITHUB mode={mode} run={run_id}",
        f"decision: {decision.get('tick')}",
        f"c1b_gap={'window=' + str(gap.get('window')) if gap.get('from_unknown') is True else 'NONE'}",
        f"codex_recall_pending={(decision.get('recall') or {}).get('pending') if (decision.get('recall') or {}).get('pending') is not None else 'UNKNOWN'}",
        "S1_OPEN_WORK_INDEX_v1 UNKNOWN(not_built_by_the_executor)", f"task: {TASK_ID}"])


# ----------------------------------------------------------------------------------------------- C10 readback
def tree_entry(entry):
    """One path of a readback, in the tri-state of fix round 3 (ChatGPT audit READBACK_FALSE_MATCH): ("PRESENT", mode,
    type, sha), ("ABSENT",) when the commit was read and the path is proven not to be in it, or ("UNREADABLE",). Anything
    else (None, a bare SHA, a short tuple) is UNREADABLE: "absent" and "could not read" are never the same value."""
    if isinstance(entry, tuple) and entry == ("ABSENT",):
        return entry
    if (isinstance(entry, tuple) and len(entry) == 4 and entry[0] == "PRESENT" and isinstance(entry[1], str) and re.fullmatch(r"[0-7]{6}", entry[1])
            and entry[2] in ("blob", "tree", "commit") and isinstance(entry[3], str) and SHA40.fullmatch(entry[3])):
        return entry
    return ("UNREADABLE",)


def readback_verdict(pr, head, intent_at, merge_commit, blobs, ancestor_of_main, now, executor_login="github-actions[bot]",
                     window_minutes=ORIGIN_WINDOW_MINUTES, paths=None, changed=False):
    """ACTION_LOOP C10 / EVIDENCE_BINDINGS B3 for one merge intent, from native reads the caller made:
      pr             GET /pulls/<n>
      merge_commit   GET /commits/<merge_commit_sha> (parents, commit.message), or None
      blobs          [(path, entry at the merge commit, entry at the head)] for EVERY changed path; an entry is
                     tree_entry()'s ("PRESENT", mode, type, sha), ("ABSENT",) or ("UNREADABLE",)
      ancestor_of_main  True when the merge commit is an ancestor of, or equal to, current main
      paths          the exact path set the intent was made for; `blobs` must cover exactly that set
      changed        fix round 5 (N05): every path the squash commit changed against its parent, or None (unread);
                     False (the default) only for callers that do not check the delta
    Fix round 5 (D06): a proof that could not be READ is UNREADABLE, never MISMATCH: the merge commit that GitHub names
    but did not return, an ancestry that could not be computed (None), unread blobs. MISMATCH is proven only.
    Returns (state, why): ABSENT (not merged), FOREIGN (merged, but not this intent's operation), MATCH, MISMATCH
    (this intent's merge, and a C10 fact fails: the halt trigger), or UNREADABLE. MATCH needs every path read at both
    commits and equal in mode, type and SHA (a deletion is ABSENT at both). One unknown path, or a path set that is not
    the intent's, is UNREADABLE and never MATCH: the intent stays open and no receipt says "verified"."""
    if not isinstance(pr, dict) or not isinstance(pr.get("number"), int):
        return "UNREADABLE", "pr"
    if pr.get("merged") is False:
        return "ABSENT", "not_merged"
    if pr.get("merged") is not True:
        return "UNREADABLE", "merged_unknown"                     # a missing or odd field is not "not merged" (fix round 4, #10)
    try:
        merged_at, at = stamp(pr.get("merged_at")), stamp(intent_at)
    except ValueError:
        return "UNREADABLE", "timestamps"
    if (pr.get("head") or {}).get("sha") != head:
        return "FOREIGN", "other_head"
    if merged_at < at - timedelta(seconds=5) or merged_at > at + timedelta(minutes=window_minutes):
        return "FOREIGN", "outside_intent_window"
    if ((pr.get("merged_by") or {}).get("login")) != executor_login:
        return "FOREIGN", "other_actor"
    sha = pr.get("merge_commit_sha")
    if not isinstance(sha, str) or not SHA40.fullmatch(sha):
        return "UNREADABLE", "merge_commit_sha"
    if not isinstance(merge_commit, dict):
        return "UNREADABLE", "merge_commit_unreadable"
    if merge_commit.get("sha") != sha:
        return "MISMATCH", "merge_commit_other"
    parents = merge_commit.get("parents") or []
    subject = str(((merge_commit.get("commit") or {}).get("message")) or "").split("\n", 1)[0]
    if len(parents) != 1:
        return "MISMATCH", "parents"
    if not subject.endswith(f"(#{pr['number']})"):
        return "MISMATCH", "subject"
    if ancestor_of_main is None:
        return "UNREADABLE", "ancestry_unknown"
    if ancestor_of_main is not True:
        return "MISMATCH", "not_on_main"
    if not isinstance(blobs, list) or not blobs:
        return "UNREADABLE", "blobs_unreadable"
    try:
        listed = [row[0] for row in blobs]
        rows = [(row[0], tree_entry(row[1]), tree_entry(row[2])) for row in blobs]
    except (TypeError, IndexError):
        return "UNREADABLE", "blobs_shape"
    if paths is not None and (len(set(listed)) != len(listed) or set(listed) != set(paths)):
        return "UNREADABLE", "path_set"
    unknown = [path for path, a, b in rows if a == ("UNREADABLE",) or b == ("UNREADABLE",)]
    for path, merged_entry, head_entry in rows:
        if "UNREADABLE" not in (merged_entry[0], head_entry[0]) and merged_entry != head_entry:
            return "MISMATCH", f"blob:{path}"
    if unknown:
        return "UNREADABLE", f"path_unknown:{unknown[0]}"
    if changed is not False and paths is not None:
        # fix round 5 (N05): the reverse check. The squash commit changed EXACTLY the intent's path set: no other path
        if not isinstance(changed, list):
            return "UNREADABLE", "delta_unreadable"
        if set(changed) != set(paths):
            extra = sorted(set(changed) ^ set(paths))
            return "MISMATCH", f"delta:{extra[0] if extra else '-'}"
    return "MATCH", f"paths={len(rows)}"


# ----------------------------------------------------------------------------------------------- the observer
def observer_lines(issues, now, bot=None):
    """Reference implementation of 00_FMOS/S1/OBSERVER_BOOTSTRAP.txt (the read-only ChatGPT task): what it prints from
    the ONE read of the open issues labelled s1-tick-brief. It never writes. `bot` is the Actions bot identity."""
    bot = bot or {"login": "github-actions[bot]", "id": 41898282, "type": "Bot"}
    unknown = ["OWNER APPROVAL REQUIRED: UNKNOWN (observer)", "HIGH_IMPACT BLOCKED: UNKNOWN", "DISPOSITIONS TODAY: UNKNOWN"]
    end = lambda why: unknown + ["S1_ROUTES ok", f"S1_TICK NOOP - - {why} main=- contract=-"]
    if not isinstance(issues, list):
        return end("BRIEF_UNVERIFIED(unreadable)")
    rows = [i for i in issues if isinstance(i, dict) and "pull_request" not in i]
    if len(rows) != 1:
        return end(f"BRIEF_UNVERIFIED(issues={len(rows)})")
    user = rows[0].get("user")
    if not (isinstance(user, dict) and all(user.get(k) == v for k, v in bot.items())):
        return end("BRIEF_UNVERIFIED(author)")
    d = parse_decision(rows[0].get("body"))
    if d is None:
        return end("BRIEF_UNVERIFIED(body)")
    if d.get("observer") != OBSERVER_VERSION:
        return end("SOURCE_UNVERIFIED(observer_version)")
    try:
        age = (now - stamp(d.get("generated_at"))).total_seconds() / 60
    except ValueError:
        return end("BRIEF_UNVERIFIED(timestamps)")
    if age > MAX_AGE_MINUTES or age < -2:
        return end(f"BRIEF_STALE(age_min={int(age)})")
    return list(d["print"])
