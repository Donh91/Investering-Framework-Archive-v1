"""S1 ROOT decision envelope: deliberately SHADOW, never write authority."""
from __future__ import annotations
import re
import hashlib
import json

SCHEMA = "S1_ROOT_VERDICT_V1"
SHA = re.compile(r"[0-9a-f]{40}\Z")
REQUIRED = {"privacy-scan", "gate", "storage-health", "test", "execution-truth"}
ACTIONS = {"HALT", "RECONCILE", "MERGE", "MERGE_IF_CLAUDE_APPROVE", "REPAIR", "REQUEST_REVIEW"}

def obj(x):
    return x if isinstance(x, dict) else {}

def sha(x):
    return isinstance(x, str) and SHA.fullmatch(x) is not None

def positive(x):
    return type(x) is int and x > 0

def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()

def build_root_verdict(brief):
    """Derive bounded, public-only evidence. Never accept a rank as authorization.

    No free text, private receipt data or PR content is serialized. Unknown is FAIL.
    The public producer cannot authenticate its own future publication or private
    vetoes; the shadow verdict therefore always authorizes NONE.
    """
    b = obj(brief)
    pins, p, lane, rules = (obj(b.get(k)) for k in ("pins", "verdict", "lane", "rulesets"))
    repo = obj(b.get("repo"))
    candidates = b.get("next")
    c = obj(candidates[0]) if isinstance(candidates, list) and candidates else {}
    kind = c.get("action")
    kind = kind if isinstance(kind, str) and kind in ACTIONS else "NONE"
    n = c.get("pr")
    h = c.get("head")
    prs = b.get("prs")
    matches = [e for e in prs if isinstance(e, dict) and e.get("n") == n and e.get("head") == h] if isinstance(prs, list) and positive(n) and sha(h) else []
    e = matches[0] if len(matches) == 1 else {}
    ci, review, elane = (obj(e.get(k)) for k in ("ci", "review", "lane"))
    tuples = obj(ci.get("tuples"))
    gates = {}
    def check(name, ok, reason):
        gates[name] = {"state": "PASS" if ok is True else "FAIL", "reason": "OK" if ok is True else reason}
    check("binding", bool(sha(b.get("main")) and positive(b.get("run_id")) and positive(b.get("run_attempt")) and repo.get("identity") is True), "BINDING_UNPROVEN")
    check("complete", b.get("complete") is True, "BRIEF_INCOMPLETE")
    check("pins", bool(pins.get("ok") is True and p.get("source") == "OK" and p.get("t2") == "OK" and p.get("main") == b.get("main") and sha(pins.get("contract_blob")) and pins.get("contract_blob") == p.get("contract_blob") == p.get("bootstrap_3b")), "PINS_UNPROVEN")
    check("drift", b.get("main_moved_during_build") is False, "MAIN_MOVED_OR_UNKNOWN")
    check("candidate", bool(kind != "NONE" and len(matches) == 1 and not e.get("skip") and e.get("unreadable") is not True and e.get("open") == []), "NO_UNAMBIGUOUS_CLEAR_CANDIDATE")
    check("lane", bool(lane.get("state") == "ON" and "halt" in lane and lane["halt"] is None and elane.get("eligible") is True and e.get("writer", "UNKNOWN") is None and not e.get("shrinks") and isinstance(e.get("paths"), list) and bool(e["paths"]) and elane.get("risk_floor") == "LOW" and obj(e.get("item")).get("risk", "LOW") == "LOW"), "LANE_OR_OWNER_GATE")
    check("rulesets", bool(rules.get("stable") is True and isinstance(rules.get("census"), list)), "RULESETS_UNPROVEN")
    check("ci", bool(ci.get("state") == "GREEN" and set(tuples) == REQUIRED and all(obj(t).get("s") == "PASS" and positive(obj(t).get("job")) for t in tuples.values()) and obj(ci.get("checks")).get("green") is True), "CI_TUPLES_UNPROVEN")
    check("privacy", bool(ci.get("privacy") == "NO_RESTRICTED_CONTENT" and not e.get("gate_stale") and e.get("main_overlap") == []), "PRIVACY_OR_GATE_DRIFT")
    check("public_review", bool(review.get("changes_requested") is False and type(review.get("unresolved_p0p1")) is int and review["unresolved_p0p1"] == 0), "REVIEW_OR_THREADS_UNPROVEN")
    check("no_intents", b.get("open_intents") == [], "INTENT_PENDING_OR_UNKNOWN")
    # These cannot be established by this public build, by design.
    for name, reason in (
        ("publication_authenticity", "PUBLISHED_RUN_NOT_YET_COMPLETE"),
        ("private_approval_and_veto", "PRIVATE_REVIEW_NOT_READABLE_BY_PUBLIC_PRODUCER"),
        ("owner_presence_and_judgment", "OWNER_AND_JUDGMENT_NOT_DELEGATED"),
        ("live_preconditions", "LIVE_RECHECK_REQUIRED"),
        ("merge_readback", "POST_ACTION_READBACK_REQUIRED"),
        ("execution_authority", "SHADOW_NO_CUTOVER"),
    ):
        check(name, False, reason)
    out = {"schema": SCHEMA, "mode": "SHADOW", "main": b.get("main") if sha(b.get("main")) else None,
           "run_id": b.get("run_id") if positive(b.get("run_id")) else None,
           "run_attempt": b.get("run_attempt") if positive(b.get("run_attempt")) else None,
           "candidate": {"kind": kind, "pr": n if positive(n) else None, "head": h if sha(h) else None},
           "next_action": "NONE", "preconditions": gates}
    out["evidence_sha256"] = digest(out)
    return out

def force_none(verdict):
    """Body shrink must never preserve a misleading actionable candidate."""
    v = obj(verdict)
    out = {k: v[k] for k in ("schema", "mode", "main", "run_id", "run_attempt") if k in v}
    out.update(candidate={"kind": "NONE", "pr": None, "head": None}, next_action="NONE",
               preconditions={"complete": {"state": "FAIL", "reason": "BRIEF_TOO_LARGE"},
                              "execution_authority": {"state": "FAIL", "reason": "SHADOW_NO_CUTOVER"}})
    out["evidence_sha256"] = digest(out)
    return out
