"""Option C: daily log-only proposals; never owner authority or a write gateway.

Interactive operator independently authenticates native log and direct user GO,
rechecks all review gates, reserves intent before posting, reads back and receipts.
GitHub comments cannot authenticate human presence; no scheduled consumer.
"""
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

SCHEMA = "S1_OWNER_REVIEW_BATCH_v1"
MAX_TARGETS = 3
SHA = re.compile(r"[0-9a-f]{40}")


def clock(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("UTC required")
    return datetime.fromisoformat(value[:-1] + "+00:00")


def z(at):
    if not isinstance(at, datetime) or at.utcoffset() is None:
        raise ValueError("aware clock required")
    return at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def daily_slot(value):
    try:
        return clock(value).astimezone(ZoneInfo("Europe/Copenhagen")).hour == 20
    except (ValueError, TypeError):
        return False


def proposal(*, targets, main, contract, run, attempt, generated_at, now):
    if (not daily_slot(generated_at) or not SHA.fullmatch(str(main))
            or not SHA.fullmatch(str(contract)) or type(run) is not int or run <= 0
            or type(attempt) is not int or attempt <= 0 or not isinstance(targets, (tuple, list))
            or not 1 <= len(targets) <= MAX_TARGETS):
        raise ValueError("invalid proposal identity")
    issued, source = clock(z(now)), clock(generated_at)
    if not source <= issued <= source+timedelta(minutes=45):
        raise ValueError("stale proposal source")
    rows, seen = [], set()
    for pr, head in targets:
        if type(pr) is not int or pr <= 0 or pr in seen or not isinstance(head, str) or not SHA.fullmatch(head):
            raise ValueError("invalid or duplicate target")
        seen.add(pr)
        rows.append({"pr": pr, "head": head})
    body = {"contract": SCHEMA, "mode": "SHADOW", "authority": "PROPOSAL_ONLY",
            "main": main, "runtime_contract": contract, "run": run, "attempt": attempt,
            "brief_generated_at": generated_at, "local_day": source.astimezone(ZoneInfo("Europe/Copenhagen")).date().isoformat(),
            "issued_at": z(issued), "expires_at": z(issued+timedelta(hours=24)), "targets": rows}
    return {**body, "batch": hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()}


def select_go(batch, command, *, now, current_heads, consumed):
    """Pure validation only. consumed is COMPLETE native intent census or None.
    An unsettled intent consumes (PR, full head) forever. No atomic-lock claim.
    Native origin, actual user role and live recheck remain operator obligations.
    """
    if not isinstance(batch, dict) or not isinstance(command, str) or consumed is None or not isinstance(current_heads, dict):
        raise ValueError("missing input")
    try:
        rebuilt = proposal(targets=[(r["pr"], r["head"]) for r in batch["targets"]],
                           main=batch["main"], contract=batch["runtime_contract"], run=batch["run"],
                           attempt=batch["attempt"], generated_at=batch["brief_generated_at"], now=clock(batch["issued_at"]))
        if rebuilt != batch:
            raise ValueError("proposal mismatch")
        at = clock(z(now))
        if not clock(batch["issued_at"]) <= at < clock(batch["expires_at"]):
            raise ValueError("expired or future proposal")
        match = re.fullmatch(r"GO review((?: #[1-9][0-9]*){1,3}) batch=([0-9a-f]{64})", command)
        if match is None or match.group(2) != batch["batch"]:
            raise ValueError("GO not bound to batch")
        ids = [int(x[1:]) for x in match.group(1).split()]
        heads = {r["pr"]: r["head"] for r in batch["targets"]}
        if len(ids) != len(set(ids)) or any(p not in heads or current_heads.get(p) != heads[p] or (p,heads[p]) in consumed for p in ids):
            raise ValueError("stale, unlisted or consumed target")
        return [(p, heads[p]) for p in ids]
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError("malformed proposal") from exc


def receipt_fields(batch, pr, head, *, intent_id, request_id):
    if (not any(r == {"pr": pr, "head": head} for r in batch["targets"])
            or type(intent_id) is not int or intent_id <= 0
            or type(request_id) is not int or request_id <= 0 or intent_id == request_id):
        raise ValueError("invalid receipt")
    return {"contract": "S1_OWNER_REVIEW_RECEIPT_v1", "batch": batch["batch"],
            "pr": pr, "head": head, "intent": intent_id, "request": request_id,
            "review_authority": False, "merge_authority": False}
