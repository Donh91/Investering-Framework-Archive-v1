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
from datetime import datetime, timedelta, timezone
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
# agree, and a merge that is flagged for Codex to revisit. (c) applies only when Codex is DEMONSTRABLY unavailable, by
# evidence read natively, by the build and again by the executor:
#   UNAVAILABLE  someone asked "@codex review" after this head's last commit and Codex answered with a usage limit;
#   SILENT       someone asked after this head's last commit and Codex did not answer within 24 hours;
#   LIMIT        nobody asked Codex about this head, and Codex's NEWEST comment on any open PR the build read is a
#                usage-limit answer that is at most 24 hours old (Codex itself says it has no usage).
# No repository variable can switch the fallback on. A request that is pending inside its 24 hours is never "offline".
RECALL_POLICY = "CODEX_CLAUDE_OR_OFFLINE_RECALL"
CODEX_OFFLINE_STATES = ("UNAVAILABLE", "SILENT")
FALLBACK_MIN_GAP_MINUTES = 50              # the second run starts at least this long after the first run's candidate receipt
FALLBACK_MAX_AGE_HOURS = 24                # an older candidate has expired: the count starts again
FALLBACK_MAX_CANDIDATES = 3                # candidate receipts per PR head, ever; then the head is parked for the owner
RECALL_LABEL = "codex-recall-pending"      # on every PR merged by the fallback, until Codex's completed review of that head
REVIEW_ROUTE = re.compile(r"CODEX|CLAUDE|FALLBACK\((?:UNAVAILABLE|SILENT|LIMIT)\)|NONE\(policy=NATIVE_GATES\)")
EXECUTOR_ACTIONS = ("MERGE", "HALT")       # what the executor may do; a heartbeat is observability, never the action
MERGE_RISKS = ("LOW", "MEDIUM")            # HIGH, HIGH_IMPACT, EXTREME, unclear and OWNER_GATED are never executor merges
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
    return {"executor": mode if isinstance(mode, str) and mode in EXECUTOR_MODES else "OFF",
            "review_policy": policy if isinstance(policy, str) and policy in REVIEW_POLICIES else "CODEX_FINAL_REQUIRED"}


def effective_mode(config_mode, hold):
    """The switch on main is the authority; the owner's repository variable S1_EXECUTOR_HOLD can only restrict it.
    ANY non-empty value holds: "1", "true", "off", "0", "no" and "false" all turn a LIVE or SHADOW executor OFF. The
    variable is a kill switch, so no word in it can mean "run"; only deleting it, or leaving it empty, releases the hold."""
    mode = config_mode if config_mode in EXECUTOR_MODES else "OFF"
    held = hold is not None and str(hold).strip() != ""
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
    # the diff itself, for the fallback route only (review_route): which lists the ADDED lines of non-document files match
    diff_x = set()
    for f in files or []:
        if not str(f.get("filename") or "").lower().endswith(DOC_SUFFIXES):
            added = "\n".join(line[1:] for line in str(f.get("patch") or "").splitlines() if line.startswith("+") and not line.startswith("+++"))
            forms = word_forms(added)                             # the word lists of a path AND the strong identifiers of a body (send_transaction)
            diff_x |= {code for code in BODY_LISTS if JUDGMENT[code].search(forms) or BODY_PATTERNS[code].search(forms)}
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
    return {"x": sorted(set(x))[:8], "x_n": len(set(x)), "risk": risk,
            "direction": bool(removed_code or DIRECTION_WORDS.search(title_forms) or any(DIRECTION_WORDS.search(word_forms(p)) for p in paths)),
            "hold_labels": held[:3],
            "docs_only": bool(files_complete and paths and all(doc_path(p) for p in paths)),
            "diff_x": sorted(diff_x) if files_complete else ["unknown"],
            "push": push_trigger_matches(paths, push_filters)[:4] if files_complete else ["unknown"],
            "title_sha256": sha16(title)}


def review_route(e, policy):
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
    if cx == "REQUESTED":
        return None, "C5:codex_review_pending"
    if recall and thin.get("claude") not in ("NONE", "APPROVE"):
        return None, "C5:claude_veto" if thin.get("claude") == "VETO" else "C5:review_unreadable"   # a Claude refusal blocks every route
    if cx == "FINAL":
        return ("CODEX", None) if author.get("codex") is False else (None, "C5:codex_authored")   # Codex never reviews its own head
    if cx not in NO_REVIEW_STATES:
        return None, "C5:review_unreadable"                       # NOT_PROVEN, missing, or a status this code does not know
    if recall:
        if thin.get("claude") == "APPROVE":                       # (b): never Claude's review of a head Claude wrote
            return ("CLAUDE", None) if thin.get("claude_written") is False else (None, "C5:claude_authored")
        offline = cx if cx in CODEX_OFFLINE_STATES else "LIMIT" if cx == "NONE" and thin.get("codex_limit") is True else None
        if offline is None:
            return None, "C5:codex_review_required"               # (c) needs proof that Codex is unavailable: ask Codex
        if author.get("s1") is not False:
            return None, "C5:s1_authored"                         # automation's own work is never merged by automation's own runs alone
        if author.get("codex") is not False:
            return None, "C5:codex_authored"                      # Codex could never clear the recall of a head it wrote
        if thin.get("bot") is not False:
            return None, "C5:bot_authored"
        if thin.get("diff_x") != []:
            return None, "C5:fallback_parked:diff_words"          # the diff itself holds a credential, money or Round 3 word: uncertain, PARK
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


def review_gate(e, policy):
    return review_route(e, policy)[1]


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
                "claude": "NOT_PROVEN", "claude_written": True, "diff_x": ["unknown"], "fallback_candidates": None, "fallback_mismatch": True,
                "codex_limit": False, "p01_named": True}
    if "paths" not in e:
        gates.append("C2:paths_not_in_brief")
    for x in (thin.get("x") or [])[:2]:
        gates.append(f"C2:judgment:{x}")
    if e.get("shrinks"):
        gates.append("C2:shrinks:" + str(e["shrinks"][0][0]))
    if thin.get("push"):
        gates.append("C2:push_trigger:" + str(thin["push"][0]))
    item = e.get("item") if isinstance(e.get("item"), dict) else {}
    risk = risk_max(lane.get("risk_floor"), thin.get("risk"), item.get("risk"))
    if risk not in MERGE_RISKS:
        gates.append(f"C2:risk:{risk}")
    if thin.get("direction") or item.get("kind") == "DIRECTION":
        gates.append("C5:strategist")
    if e.get("mergeable") in ("dirty", "blocked"):
        gates.append(f"C2:mergeable:{e.get('mergeable')}")
    review = review_gate(e, cfg["review_policy"])
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


def lane_gates(brief):
    """The lane-level checks (C7, C8). Any reason: no merge in this decision, whatever the PRs look like."""
    out = []
    lane = brief.get("lane") if isinstance(brief.get("lane"), dict) else {}
    if lane.get("state") != "ON":
        out += [f"C7:{r}" for r in (lane.get("off_reasons") or ["lane_off"])][:3]
    rules = brief.get("rulesets") if isinstance(brief.get("rulesets"), dict) else {}
    if rules.get("stable") is not True:
        out.append("C8:ruleset_census")
    elif rules.get("active") != 0 or brief.get("main_protected") is not False:
        # an active rule or a protected branch: compliance and bypass evidence cannot be proven with the job token
        out.append("C8:ruleset_unproven")
    if not isinstance(brief.get("repo"), dict) or brief["repo"].get("identity") is not True:
        out.append("B1:repository_identity")
    return out


# ----------------------------------------------------------------------------------------------- the decision
def _noop(base, result, skipped=()):
    d = dict(base, action="NOOP", result=result, pr=None, head=None, merge=None, halt=None, skipped=list(skipped)[:6])
    return d


def decide(brief, now=None):
    """S1_DECISION_V1 from one S1_TICK_BRIEF_V1 (a dict as build_brief() returns it). Total: any missing or malformed
    part of the brief ends in a NOOP with its reason, never in an exception and never in an action."""
    b = brief if isinstance(brief, dict) else {}
    pins = b.get("pins") if isinstance(b.get("pins"), dict) else {}
    cfg = b.get("thin") if isinstance(b.get("thin"), dict) else {}
    cfg = {"executor": cfg.get("executor") if cfg.get("executor") in EXECUTOR_MODES else "OFF",
           "review_policy": cfg.get("review_policy") if cfg.get("review_policy") in REVIEW_POLICIES else "CODEX_FINAL_REQUIRED"}
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
            "main": main, "contract_blob": pins.get("contract_blob"), "pins_ok": pins.get("ok") is True,
            "observer": OBSERVER_VERSION, "executor": cfg["executor"], "review_policy": cfg["review_policy"],
            "heartbeat": {"due": False}, "advice": [], "status_lines": list(lines), "contract": contract8, "recall": {"pending": None}}

    def done(d):
        pr, h8 = (d["pr"] if d["pr"] is not None else "-"), (d["head"][:8] if d.get("head") else "-")
        # A decision is never a merge: the line the observer prints is always NOOP with what was DECIDED (ACTION_LOOP
        # RECEIPTS: never claim a merge you did not read back). The executor's own run prints the outcome.
        d["tick"] = f"S1_TICK NOOP {pr} {h8} {d['result']} main={(main or '-')[:8]} contract={contract8}"
        d["print"] = observer_print(d, b.get("ledger"))
        return d

    if made is None or main is None or not isinstance(b.get("run_id"), int) or isinstance(b.get("run_id"), bool):
        return done(_noop(base, "BRIEF_UNVERIFIED(body)"))
    if pins.get("ok") is not True:
        why = (pins.get("mismatch") or ["pins"])[0] if isinstance(pins.get("mismatch"), list) else "pins"
        step = "3b" if why == "bootstrap:3b" else "3"
        return done(_noop(base, f"SOURCE_UNVERIFIED({step})", [f"lane:pins:{why}"]))
    if b.get("complete") is not True:
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
    base["recall"] = {"pending": recall.get("pending") if type(recall.get("pending")) is int else None}
    if (b.get("codex") or {}).get("available") is True:           # Codex answers again: ask it to review each pending merged head
        base["advice"] += [{"action": "REQUEST_REVIEW", "pr": i["pr"], "head": i["head"], "how": "CODEX_RECALL"}
                           for i in items if i.get("codex") in ("NONE", "SILENT", "UNAVAILABLE")][:3]
    notes = []
    if base["recall"]["pending"] != 0:
        notes.append(f"CODEX_RECALL_PENDING({base['recall']['pending'] if base['recall']['pending'] is not None else 'UNKNOWN'}): "
                     + (" ".join(f"#{i['pr']}" for i in items[:6]) or "-"))
    findings = [i for i in items if i.get("codex") == "FINDINGS"]
    if findings:
        notes.append("CODEX_RECALL_FINDINGS: " + " ".join(f"#{i['pr']} {i['head'][:8]}" for i in findings[:4]) + " (revert or fix required)")
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
    intent_prs = {i.get("pr") for i in intents if isinstance(i, dict)}
    if any(isinstance(i, dict) and i.get("kind") == "S1_LANE_MERGE_INTENT_v1" for i in intents):
        skipped.append("lane:C9:open_merge_intent")              # one merge at a time: the readback settles it first
    entries = [e for e in (b.get("prs") or []) if isinstance(e, dict) and isinstance(e.get("n"), int)]
    ranked = []
    for e in entries:
        gates = pr_gates(e, cfg, intent_prs)
        ranked.append(((RISK_ORDER.index(pr_risk(e)), len(gates), e["n"]), e, gates))
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
        merge = {"pr": e["n"], "sha": e["head"], "merge_method": "squash", "risk": pr_risk(e),
                 "review": review_route(e, cfg["review_policy"])[0],
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
    if not (isinstance(d.get("result"), str) and isinstance(d.get("tick"), str) and d["tick"].startswith("S1_TICK NOOP ")):
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
    if d["action"] == "MERGE":
        m = d.get("merge")
        if not (isinstance(m, dict) and isinstance(m.get("review"), str) and REVIEW_ROUTE.fullmatch(m["review"])):
            return False
        return (isinstance(m, dict) and type(m.get("pr")) is int and m.get("pr") == d.get("pr") and isinstance(m.get("sha"), str)
                and SHA40.fullmatch(m["sha"]) is not None and m["sha"] == d.get("head") and m.get("merge_method") == "squash"
                and m.get("risk") in MERGE_RISKS and d.get("halt") is None and d.get("pins_ok") is True and d.get("main") is not None)
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
    return (f"{SCHEMA} id={decision.get('id')} generated_at={decision.get('generated_at')} main={decision.get('main')} "
            f"action={decision.get('action')}\n\n{BEGIN}\n```json\n{text}\n```\n{END}\n\n")


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
        f"risk: {m['risk']}", f"review: {m['review']}", f"contract={decision['contract']}", f"task: {TASK_ID}"])


def merge_receipt_body(decision, repo_id, intent_id, readback, run_id, privacy_run, reconciled=False):
    m = decision["merge"] if isinstance(decision.get("merge"), dict) else {}
    ci = " ".join(f"ci={name}@{v[0]}.{v[1]}" for name, v in sorted((m.get("ci") or {}).items()) if isinstance(v, list) and len(v) >= 2)
    return "\n".join([
        "S1_LANE_MERGE_v1" + (" reconciled" if reconciled else ""), f"pr: {readback['pr']}", f"head: {readback['head']}",
        f"merge: {readback['merge_commit']}", f"review: {m.get('review', 'unavailable')}",
        f"privacy=NO_RESTRICTED_CONTENT run={privacy_run if privacy_run is not None else 'unavailable'}", ci or "ci=unavailable",
        f"main_before: {decision.get('main')}", f"main_after: {readback['main_after']}", f"blob_match: {readback['paths']} paths",
        "rules: no_active_ruleset_and_main_unprotected", f"repo_id={repo_id}", f"intent: {intent_id}",
        f"main_health=brief run={m.get('health_run', 'unavailable')}", f"brief={decision.get('run_id')}", f"decision={decision.get('id')}",
        "merge_execution_origin: " + ("UNKNOWN" if reconciled else f"S1_GITHUB_EXECUTOR run={run_id}"),
        f"executor: GITHUB run={run_id if run_id is not None else '-'}",
        f"item: pr:{readback['pr']} state: MERGED", "closure: OBSERVING", f"contract={decision.get('contract')}", f"task: {TASK_ID}"])


def fallback_evidence(pr, head, risk, files, paths_sha256, title_sha256, body, ci):
    """What one fallback run derived about the PR, from ITS OWN native reads, as one hash. Two runs agree when the hashes
    are equal: the same head, the same file set, title and body, the same risk class, the same CI runs and jobs. The
    Codex-offline signal is not part of it: every run has to prove that for itself, and the signal may differ."""
    doc = {"pr": pr, "head": head, "risk": risk, "files": files, "paths_sha256": paths_sha256, "title_sha256": title_sha256,
           "body_sha256": sha16(body), "ci": ci}
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


def halt_body(reason, pr=None, head=None, commit=None, run=None, detail=None, contract="-", run_id=None):
    lines = [f"S1_LANE_HALTED PR={pr if pr is not None else '-'} head={head or '-'}", f"reason: {reason}"]
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
def readback_verdict(pr, head, intent_at, merge_commit, blobs, ancestor_of_main, now, executor_login="github-actions[bot]",
                     window_minutes=ORIGIN_WINDOW_MINUTES):
    """ACTION_LOOP C10 / EVIDENCE_BINDINGS B3 for one merge intent, from native reads the caller made:
      pr             GET /pulls/<n>
      merge_commit   GET /commits/<merge_commit_sha> (parents, commit.message), or None
      blobs          [(path, blob at the merge commit or None, blob at the head or None)] for EVERY changed path
      ancestor_of_main  True when the merge commit is an ancestor of, or equal to, current main
    Returns (state, why): ABSENT (not merged), FOREIGN (merged, but not this intent's operation), MATCH, or MISMATCH
    (this intent's merge, and a C10 fact fails: the halt trigger)."""
    if not isinstance(pr, dict) or not isinstance(pr.get("number"), int):
        return "UNREADABLE", "pr"
    if pr.get("merged") is not True:
        return "ABSENT", "not_merged"
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
    if not isinstance(merge_commit, dict) or merge_commit.get("sha") != sha or not isinstance(sha, str) or not SHA40.fullmatch(sha):
        return "MISMATCH", "merge_commit_unreadable"
    parents = merge_commit.get("parents") or []
    subject = str(((merge_commit.get("commit") or {}).get("message")) or "").split("\n", 1)[0]
    if len(parents) != 1:
        return "MISMATCH", "parents"
    if not subject.endswith(f"(#{pr['number']})"):
        return "MISMATCH", "subject"
    if ancestor_of_main is not True:
        return "MISMATCH", "not_on_main"
    if not isinstance(blobs, list) or not blobs:
        return "MISMATCH", "blobs_unreadable"
    for path, merged_blob, head_blob in blobs:
        if merged_blob != head_blob:
            return "MISMATCH", f"blob:{path}"
    return "MATCH", f"paths={len(blobs)}"


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
