"""Offline replay of explicitly normalized evidence. No network or write authority."""
import hashlib
import json
from datetime import datetime
from simulator import decide

def utc(value):
    if not isinstance(value, str):
        raise ValueError("timestamp")
    t = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if t.utcoffset() is None:
        raise ValueError("timezone")
    return t

def replay(raw, expected_sha256, decision_at):
    """Hash binding proves bytes, not source authenticity or first availability."""
    unknown = {"status": "UNKNOWN", "decision": None, "comparable": False}
    try:
        if type(raw) is not bytes or hashlib.sha256(raw).hexdigest() != expected_sha256:
            return dict(unknown, reason="hash")
        def unique(pairs):
            out = {}
            for k, v in pairs:
                if k in out:
                    raise ValueError("duplicate key")
                out[k] = v
            return out
        row = json.loads(raw, object_pairs_hook=unique)
        if type(row) is not dict or row.get("schema") != "S1_REPLAY_FIXTURE_v1":
            return dict(unknown, reason="schema")
        if row.get("kind") != "SYNTHETIC":
            return dict(unknown, reason="historical_authentication_not_implemented")
        cutoff = utc(decision_at)
        if not utc(row["observed_at"]) <= utc(row["available_at"]) <= cutoff:
            return dict(unknown, reason="future_evidence")
        if type(row.get("evidence")) is not dict:
            return dict(unknown, reason="evidence")
        result = decide(row["evidence"])
        return {"status": "SYNTHETIC", "decision": result.decision.value,
                "reason": result.reason, "comparable": False}
    except (ValueError, TypeError, KeyError, OverflowError, RecursionError):
        return dict(unknown, reason="malformed")
