"""S1 merge-transaction kernel: executable specification. Pure, stdlib only, no I/O.

plan_step() is the whole decision procedure. tick() turns its decisions into
native-call REQUESTS; the caller (fake or real) performs each one and sends the
result back, or throws NativeError. Inputs are evidence, never authority.
"""
import hashlib
from collections import namedtuple

S1_LOGIN = "Donh91"      # shared with the owner: a login NEVER proves attribution
LEDGER = 1156            # the S1 ledger issue
SETTLE_S = 3600          # B3 op_settle_minutes: a younger intent may belong to a live run
WINDOW_S = 900           # B3 s1_origin_window_minutes
DEADLINE_S = 300         # the merging run sends its merge within this of its intent
STEP_CAP = 32

INTENT, MERGE_RCPT, HALTED = "S1_LANE_MERGE_INTENT_v1", "S1_LANE_MERGE_v1", "S1_LANE_HALTED"
OP_DONE, ITEM, CLOSURE = "S1_OP_DONE_v1", "S1_ITEM_v1", "S1_CLOSURE_v1"
OWNER_NOTE = "OWNER_MERGE_NOTE_v1"   # proposed marker: "a merge of this PR was not S1's"
RECEIPT_ORDER = (ITEM, CLOSURE, MERGE_RCPT)   # the ledger receipt is the commit record: last

(POST_INTENT, MERGE, READBACK, POST_RECEIPTS, RECONCILE_OWN, RECONCILE_FOREIGN,
 HALT_UNKNOWN, ABANDON, NOOP) = (
    "POST_INTENT", "MERGE", "READBACK", "POST_RECEIPTS", "RECONCILE_OWN",
    "RECONCILE_FOREIGN", "HALT_UNKNOWN", "ABANDON", "NOOP")
OWN, FOREIGN, UNKNOWN, ABSENT, NEED = "OWN", "FOREIGN", "UNKNOWN", "ABSENT", "NEED"

Action = namedtuple("Action", "kind reason args")


class NativeError(Exception):
    """A native call failed or its response was lost. It says nothing about the effect."""
    def __init__(self, status):
        super().__init__(status)
        self.status = status


def act(kind, reason, **args):
    return Action(kind, reason, args)


# ---------------------------------------------------------------- key
def _sha40(name, v):
    if type(v) is not str or len(v) != 40 or any(ch not in "0123456789abcdef" for ch in v):
        raise ValueError(name + ": 40 lowercase hex characters required")
    return v


def _posint(name, v):
    if type(v) is not int or v <= 0:
        raise ValueError(name + ": positive int required")
    return v


def idempotency_key(repo_id, pr, head, base_main, loop_blob):
    """sha256 over labelled, newline-terminated fields: fixed order, decimal ints,
    fixed-length hex, so no two different bindings share an encoding."""
    text = "S1_TXN_KEY_v1\nrepo_id=%d\npr=%d\nhead=%s\nbase_main=%s\nloop_blob=%s\n" % (
        _posint("repo_id", repo_id), _posint("pr", pr), _sha40("head", head),
        _sha40("base_main", base_main), _sha40("loop_blob", loop_blob))
    return hashlib.sha256(text.encode("ascii")).hexdigest()


# ---------------------------------------------------------------- ledger records
def render(kind, **fields):
    return "\n".join([kind] + ["%s: %s" % kv for kv in fields.items()])


def parse(comment):
    lines = str(comment.get("body", "")).split("\n")
    return lines[0], dict(ln.split(": ", 1) for ln in lines[1:] if ": " in ln)


def intent_of(comment):
    """The intent record of an AUTHENTIC intent comment (unedited, key recomputes), else None."""
    kind, f = parse(comment)
    if kind != INTENT or comment.get("author") != S1_LOGIN:
        return None
    if comment.get("created_at") != comment.get("updated_at"):
        return None
    try:
        rec = dict(id=comment["id"], created_at=comment["created_at"], repo_id=int(f["repo_id"]),
                   pr=int(f["pr"]), head=f["head"], base_main=f["main"], loop_blob=f["loop"])
        if idempotency_key(*(rec[k] for k in ("repo_id", "pr", "head", "base_main", "loop_blob"))) != f["key"]:
            return None
    except (KeyError, ValueError, TypeError):
        return None
    return dict(rec, key=f["key"])


def intents(ledger):
    return sorted(filter(None, map(intent_of, ledger)), key=lambda i: i["id"])


def is_open(ledger, intent):
    """B3 OPEN: no later merge receipt or halt for the PR, no S1_OP_DONE_v1 citing the intent."""
    for c in ledger:
        if c["id"] <= intent["id"] or c.get("author") != S1_LOGIN:
            continue
        kind, f = parse(c)
        if kind in (MERGE_RCPT, HALTED) and f.get("pr") == str(intent["pr"]):
            return False
        if kind == OP_DONE and f.get("intent") == str(intent["id"]):
            return False
    return True


def open_intents(ledger):
    return [i for i in intents(ledger) if is_open(ledger, i)]


def lane_halted(ledger):
    return any(parse(c)[0] == HALTED and c.get("author") == S1_LOGIN for c in ledger)


def owner_marker(ledger, intent):
    return any(parse(c)[0] == OWNER_NOTE and parse(c)[1].get("pr") == str(intent["pr"]) for c in ledger)


# ---------------------------------------------------------------- classification
def classify(obs, intent):
    """(OWN | FOREIGN | UNKNOWN | ABSENT | NEED, why) from native observations only.
    OWN means 'this intent's operation, natively verified'. It is NOT proof that S1
    pressed the button: only the merging run's own success response supports S1_RUN."""
    pr = obs.get("pr")
    if pr is None:
        return NEED, "pr"
    if type(pr) is not dict or pr.get("number") != intent["pr"] or type(pr.get("merged")) is not bool:
        return UNKNOWN, "pr_malformed"
    if not pr["merged"]:
        return ABSENT, "not_merged" if pr.get("head") == intent["head"] else "HEAD_CHANGED"
    if pr.get("merged_by") != S1_LOGIN:
        return FOREIGN, "other_actor"
    if pr.get("head") != intent["head"]:
        return FOREIGN, "other_head"
    t = pr.get("merged_at")
    if type(t) is not int:
        return UNKNOWN, "merged_at_unreadable"
    if t < intent["created_at"]:
        return FOREIGN, "before_intent"
    if t > intent["created_at"] + WINDOW_S:
        return FOREIGN, "after_window"
    c = obs.get("commit")
    if c is None:
        return NEED, "commit"
    if type(c) is not dict or type(c.get("parents")) is not list:
        return UNKNOWN, "commit_malformed"
    if len(c["parents"]) != 1:
        return FOREIGN, "not_squash"
    if t == intent["created_at"]:
        return UNKNOWN, "same_second_as_intent"
    if not str(c.get("subject", "")).endswith("(#%d)" % intent["pr"]):
        return UNKNOWN, "subject"
    for need in ("on_main", "rule_suite", "head_blobs"):
        if obs.get(need) is None:
            return NEED, need
    if obs["on_main"] not in ("ahead", "identical"):
        return UNKNOWN, "not_on_main"
    if obs["rule_suite"] != "pass":
        return UNKNOWN, "bypass"
    if not obs["head_blobs"] or c.get("files") != obs["head_blobs"]:
        return UNKNOWN, "blob_mismatch"
    return OWN, "verified"


# ---------------------------------------------------------------- the state machine
def plan_step(obs, intent):
    """Next action from (observed state, oldest OPEN intent or None). Pure and total.
    obs: ledger, now, optional cand/pr/commit/on_main/rule_suite/head_blobs/pr_comments,
    and run = what THIS run did (intent_id, merge, posted); a crash loses run."""
    led, run, now = obs["ledger"], obs.get("run") or {}, obs["now"]
    if intent is None:
        cand = obs.get("cand")
        if cand is None:
            return act(NOOP, "no_candidate")
        if "intent_id" in run:
            return act(NOOP, "intent_not_durable")
        if lane_halted(led):
            return act(NOOP, "lane_halted")
        b = {k: cand[k] for k in ("repo_id", "pr", "head", "base_main", "loop_blob")}
        key = idempotency_key(**b)
        if any(i["key"] == key for i in intents(led)):
            return act(NOOP, "key_spent")
        pr = obs.get("pr")
        if pr is None:
            return act(READBACK, "pr", need="pr")
        if type(pr) is not dict or pr.get("state") != "open" or pr.get("merged") is not False:
            return act(NOOP, "pr_not_open")
        if pr.get("head") != cand["head"]:
            return act(NOOP, "head_changed")
        return act(POST_INTENT, "qualified", key=key, **b)

    mine = run.get("intent_id") == intent["id"]
    dup = any(i["key"] == intent["key"] and i["id"] < intent["id"] for i in intents(led))
    if mine and "merge" not in run:
        if dup:
            return act(ABANDON, "DUPLICATE")
        if lane_halted(led):
            return act(ABANDON, "lane_halted")
        if now - intent["created_at"] > DEADLINE_S:
            return act(ABANDON, "deadline")
        return act(MERGE, "one_attempt", pr=intent["pr"], sha=intent["head"], method="squash")
    if mine and run["merge"] != "OK":
        return act(NOOP, "MERGE_REFUSED(%s)" % run["merge"])   # no retry, no other write
    if not mine:
        if now - intent["created_at"] < SETTLE_S:
            return act(NOOP, "intent_young")
        if dup:
            return act(ABANDON, "DUPLICATE")

    cls, why = classify(obs, intent)
    if cls == NEED:
        return act(READBACK, why, need=why)
    if mine and cls in (ABSENT, FOREIGN):
        cls, why = UNKNOWN, "response_contradicts_native:" + why
    if cls == OWN and not mine and owner_marker(led, intent):
        cls, why = UNKNOWN, "owner_marker"    # same login, no success response of ours: unprovable
    if cls == ABSENT:
        return act(ABANDON, why)
    if cls == FOREIGN:
        return act(RECONCILE_FOREIGN, why)
    if cls == UNKNOWN:
        return act(HALT_UNKNOWN, why, halt="readback" if mine else "reconcile_readback")
    posted = set(run.get("posted", ()))
    if not mine:
        if obs.get("pr_comments") is None:
            return act(READBACK, "pr_comments", need="pr_comments")
        posted |= {parse(c)[0] for c in obs["pr_comments"]
                   if c.get("author") == S1_LOGIN and parse(c)[1].get("key") == intent["key"]}
    for r in RECEIPT_ORDER:
        if r not in posted:
            return act(POST_RECEIPTS if mine else RECONCILE_OWN, r, receipt=r,
                       origin="S1_RUN" if mine else "UNKNOWN")
    return act(NOOP, "settled")


# ---------------------------------------------------------------- the driver
def _read(need, obs, pr):
    sha = (obs.get("pr") or {}).get("merge_commit_sha")
    return {"pr": ("get_pr", pr), "commit": ("get_commit", sha), "on_main": ("compare", sha, "main"),
            "rule_suite": ("rule_suite", sha), "head_blobs": ("pr_files", pr),
            "pr_comments": ("list_comments", pr)}[need]


def _post(a, obs, i):
    """(issue, body, ends_transaction) of a posting action."""
    ref = {"intent": i["id"], "key": i["key"]}
    if a.kind in (ABANDON, RECONCILE_FOREIGN):
        result = "FOREIGN" if a.kind == RECONCILE_FOREIGN else "ABSENT"
        return LEDGER, render(OP_DONE, result=result, reason=a.reason, **ref), True
    if a.kind == HALT_UNKNOWN:
        return LEDGER, render(HALTED, pr=i["pr"], head=i["head"], reason=a.args["halt"],
                              detail=a.reason, **ref), True
    sha, r = obs["pr"]["merge_commit_sha"], a.args["receipt"]
    if r == ITEM:
        return i["pr"], render(ITEM, item="pr:%d" % i["pr"], state="MERGED", merge=sha, **ref), False
    if r == CLOSURE:
        return i["pr"], render(CLOSURE, pr=i["pr"], merge=sha, state="OBSERVING", **ref), False
    parent = ((obs.get("commit") or {}).get("parents") or ["unavailable"])[0]
    return LEDGER, render(MERGE_RCPT, pr=i["pr"], head=i["head"], merge=sha, main_before=parent,
                          base_drift=parent != i["base_main"], merge_execution_origin=a.args["origin"],
                          reconciled=a.args["origin"] != "S1_RUN", **ref), True


def tick(cand=None):
    """One S1 run, at most one transaction step chain. Generator: yields (op, *args),
    receives the result (or NativeError); ("date",) is the server time of the last
    response and is not a call. Returns the final Action."""
    run = {}
    obs = {"cand": cand, "run": run}
    try:
        obs["ledger"] = yield ("list_comments", LEDGER)
        obs["now"] = yield ("date",)
        opened = open_intents(obs["ledger"])
        intent = opened[0] if opened else None
        for _ in range(STEP_CAP):
            a = plan_step(obs, intent)
            if a.kind == NOOP:
                return a
            if a.kind == READBACK:
                obs[a.args["need"]] = yield _read(a.args["need"], obs, (intent or cand)["pr"])
            elif a.kind == POST_INTENT:
                g = a.args
                c = yield ("post_comment", LEDGER, render(
                    INTENT, pr=g["pr"], head=g["head"], main=g["base_main"], repo_id=g["repo_id"],
                    loop=g["loop_blob"], key=g["key"]))
                run["intent_id"] = c["id"]
                obs["ledger"] = yield ("list_comments", LEDGER)     # durable? first with this key?
                obs["now"] = yield ("date",)
                intent = next((i for i in open_intents(obs["ledger"]) if i["id"] == c["id"]), None)
                obs["head_blobs"] = cand.get("head_blobs")
            elif a.kind == MERGE:
                run["merge"] = "sent"                               # the one attempt is spent
                try:
                    r = yield ("merge", a.args["pr"], a.args["sha"], a.args["method"])
                    run["merge"] = "OK" if type(r) is dict and r.get("merged") is True else "response"
                except NativeError as e:
                    run["merge"] = str(e.status)
                obs.pop("pr", None)                                 # stale: re-read natively
            else:
                issue, body, final = _post(a, obs, intent)
                yield ("post_comment", issue, body)
                if final:
                    return a
                run.setdefault("posted", []).append(a.args["receipt"])
        return act(NOOP, "step_cap")
    except NativeError as e:
        return act(NOOP, "native_error(%s)" % e.status)


# Planned native calls per path (measured by txn_sim.measure_call_counts and the tests).
CALL_BUDGET = {
    "ordinary_merge": 12,      # 7 reads + intent + merge + 3 receipts
    "noop_head_changed": 2, "noop_lane_halted": 1, "noop_intent_young": 1,
    "reconcile_own": 10, "reconcile_absent": 3, "reconcile_foreign": 3,
}
