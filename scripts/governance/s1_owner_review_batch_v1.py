"""Option C: bounded SHADOW plan and interactive-only reservation protocol.

No GitHub transport, authentication, or writes. A validated selection is NOT
owner authentication. An interactive operator must independently verify the
native executor log and current gates; scheduled callers cannot authorize.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

REPO_ID = 1289482022
MAX_TARGETS = 3
PLAN = "S1_OWNER_REVIEW_BATCH_PLAN_v1"
INTENT = "S1_OWNER_REVIEW_BATCH_INTENT_v1"
RECEIPT = "S1_OWNER_REVIEW_BATCH_RECEIPT_v1"
SHA = re.compile(r"[0-9a-f]{40}")
DAY = ZoneInfo("Europe/Copenhagen")


def _utc(at):
    if not isinstance(at, datetime) or at.utcoffset() is None:
        raise ValueError("timezone required")
    return at.astimezone(timezone.utc)


def _iso(at):
    return _utc(at).isoformat().replace("+00:00", "Z")


def _stamp(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("UTC required")
    return _utc(datetime.fromisoformat(value[:-1] + "+00:00"))


def _digest(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _targets(targets):
    result = []
    seen = set()
    for pr, head in targets:
        if type(pr) is not int or pr <= 0 or pr in seen or not isinstance(head, str) or not SHA.fullmatch(head):
            raise ValueError("invalid or duplicate target")
        seen.add(pr)
        result.append({"pr": pr, "head": head})
    if not 1 <= len(result) <= MAX_TARGETS:
        raise ValueError("invalid batch size")
    return result


def build_plan(targets, *, now, main, brief_run, brief_attempt, executor_run, executor_attempt):
    at = _utc(now)
    if not isinstance(main, str) or not SHA.fullmatch(main):
        raise ValueError("invalid main")
    ids = (brief_run, brief_attempt, executor_run, executor_attempt)
    if any(type(x) is not int or x <= 0 for x in ids):
        raise ValueError("native run identity required")
    result = {"contract": PLAN, "repository_id": REPO_ID, "main": main,
              "generated_at": _iso(at), "expires_at": _iso(at + timedelta(hours=24)),
              "owner_day": at.astimezone(DAY).date().isoformat(), "brief_run": brief_run,
              "brief_attempt": brief_attempt, "executor_run": executor_run,
              "executor_attempt": executor_attempt, "targets": _targets(targets),
              "authority": "SHADOW_PLAN_ONLY_NOT_OWNER_AUTHORIZATION"}
    return {**result, "plan_id": _digest(result)}


def validate_plan(plan, now):
    if not isinstance(plan, dict):
        raise ValueError("invalid plan")
    at = _stamp(plan["generated_at"])
    current = _utc(now)
    expected = build_plan([(r["pr"], r["head"]) for r in plan["targets"]], now=at,
                          main=plan["main"], brief_run=plan["brief_run"], brief_attempt=plan["brief_attempt"],
                          executor_run=plan["executor_run"], executor_attempt=plan["executor_attempt"])
    if plan != expected or not at <= current < _stamp(plan["expires_at"]):
        raise ValueError("invalid or expired plan")
    # A batch is daily; crossing local midnight closes the old offer even if
    # its absolute 24h ceiling has not elapsed.
    if current.astimezone(DAY).date().isoformat() != plan["owner_day"]:
        raise ValueError("owner day changed")
    return expected


def validate_selection(plan, message, current_heads, now):
    """Syntax + immutable binding only; never a human-presence authenticator."""
    validate_plan(plan, now)
    expected = "GO review " + " ".join("#"+str(r["pr"]) for r in plan["targets"])
    if message != expected or current_heads != {r["pr"]: r["head"] for r in plan["targets"]}:
        raise ValueError("selection or head mismatch")
    return {"selection_valid": True, "owner_authenticated": False,
            "write_authorized": False, "plan_id": plan["plan_id"]}


def intent_body(plan):
    # No trigger string in the owner ledger.
    return INTENT + "\n" + json.dumps(plan, sort_keys=True, separators=(",", ":"))


def _parse_intents(comments, complete):
    if not complete or not isinstance(comments, list):
        raise ValueError("ledger census incomplete")
    result = []
    ids = set()
    for c in comments:
        if not isinstance(c, dict):
            raise ValueError("malformed ledger row")
        body = c.get("body")
        if not isinstance(body, str):
            raise ValueError("unreadable ledger body")
        if not body.startswith(INTENT):
            continue
        # An ambiguous or edited reservation cannot become available again.
        if (not body.startswith(INTENT+"\n") or c.get("created_at") != c.get("updated_at")
                or type(c.get("id")) is not int or c["id"] in ids):
            raise ValueError("ambiguous reservation")
        plan = json.loads(body.split("\n", 1)[1])
        validate_plan(plan, _stamp(plan["generated_at"]))
        ids.add(c["id"])
        result.append((c["id"], plan))
    return result


def check_reservation(plan, comments, *, complete, own_intent_id=None):
    """Conservative one-use/day and one-use/head; any incomplete read stops."""
    target_keys = {(r["pr"], r["head"]) for r in plan["targets"]}
    own = []
    for cid, prior in _parse_intents(comments, complete):
        prior_keys = {(r["pr"], r["head"]) for r in prior["targets"]}
        if cid == own_intent_id:
            if prior != plan:
                raise ValueError("reservation mismatch")
            own.append(cid)
            continue
        if prior["owner_day"] == plan["owner_day"] or target_keys & prior_keys:
            raise ValueError("already reserved")
    if own_intent_id is not None and own != [own_intent_id]:
        raise ValueError("reservation missing")
    return True


def request_body(plan, pr, head, intent_id):
    if {"pr": pr, "head": head} not in plan["targets"] or type(intent_id) is not int or intent_id <= 0:
        raise ValueError("request outside reservation")
    return ("@codex review\n\nS1_OWNER_REVIEW_BATCH_COMMENT_v1\n"
            f"pr: {pr}\nhead: {head}\nplan: {plan['plan_id']}\nintent: {intent_id}\n"
            "origin: OWNER_INTERACTIVE")


def receipt_body(plan, pr, head, intent_id, request_id):
    request_body(plan, pr, head, intent_id)
    if type(request_id) is not int or request_id <= 0:
        raise ValueError("request ID missing")
    return (RECEIPT + "\n" + json.dumps({"plan_id": plan["plan_id"], "pr": pr, "head": head,
            "intent": intent_id, "request": request_id, "origin": "OWNER_INTERACTIVE",
            "codex_response_verified": False}, sort_keys=True, separators=(",", ":")))
