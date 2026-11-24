"""D3 advisory repeated-repair assessment; never a writer or closure authority.

The existing incident/operational-memory owner must independently authenticate
all native receipts and completeness before use. No I/O, retry, scheduler,
registry promotion, or production closure is performed here.
"""
from dataclasses import dataclass
from datetime import datetime
import re

SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
OUTCOMES = {"FAILED", "ACTION_READBACK", "UNKNOWN"}


@dataclass(frozen=True)
class Scope:
    repo_id: int
    pr: int
    head: str
    workflow: str
    job: str
    contract_blob: str
    method: str


@dataclass(frozen=True)
class Observation:
    scope: Scope
    receipt_id: int
    run_id: int
    attempt: int
    cause_sha256: str
    observed_at_utc: str
    outcome: str


@dataclass(frozen=True)
class Assessment:
    state: str
    consecutive_failed_attempts: int
    receipt_ids: tuple = ()

    @property
    def release_authorized(self):
        return False

    @property
    def verified_closure(self):
        return False


def posint(x):
    return type(x) is int and x > 0


def sha(x, pattern):
    return isinstance(x, str) and pattern.fullmatch(x) is not None


def valid_scope(s):
    return (isinstance(s, Scope) and posint(s.repo_id) and posint(s.pr)
            and sha(s.head, SHA40) and sha(s.contract_blob, SHA40)
            and isinstance(s.workflow, str) and s.workflow.startswith(".github/workflows/")
            and isinstance(s.job, str) and bool(s.job)
            and isinstance(s.method, str) and bool(s.method))


def utc(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("UTC_Z_REQUIRED")
    return datetime.fromisoformat(value[:-1] + "+00:00")


def assess(scope, observations, *, as_of_utc, history_complete):
    """Assess only the exact scope; two distinct failed attempts trigger a hold candidate.

    A cause digest represents a normalized, independently verified failure
    signature, excluding changing run/attempt IDs. Observation IDs and native
    run attempts are deduplicated separately. No cross-head or cross-method
    suppression; a changed cause resets the consecutive-failure sequence.
    """
    unknown = Assessment("EVIDENCE_UNPROVEN", 0)
    if (not valid_scope(scope) or history_complete is not True
            or not isinstance(observations, list) or len(observations) > 100):
        return unknown
    try:
        now = utc(as_of_utc)
        by_receipt, by_attempt = {}, {}
        for row in observations:
            if (not isinstance(row, Observation) or not valid_scope(row.scope)
                    or not all(posint(v) for v in (row.receipt_id, row.run_id, row.attempt))
                    or not sha(row.cause_sha256, SHA256) or row.outcome not in OUTCOMES):
                return unknown
            time = utc(row.observed_at_utc)
            if time > now:
                return unknown
            if row.receipt_id in by_receipt and by_receipt[row.receipt_id] != row:
                return unknown
            by_receipt[row.receipt_id] = row
            if row.scope != scope:
                continue
            key = (row.run_id, row.attempt)
            if key in by_attempt and by_attempt[key] != row:
                return unknown
            by_attempt[key] = row
        rows = sorted(by_attempt.values(), key=lambda r: utc(r.observed_at_utc))
    except (ValueError, TypeError, OverflowError):
        return unknown
    # Equal observation times across distinct attempts do not prove causal order.
    if len({utc(r.observed_at_utc) for r in rows}) != len(rows):
        return unknown
    if not rows:
        return Assessment("NO_ATTEMPT_EVIDENCE", 0)
    last = rows[-1]
    if last.outcome == "UNKNOWN":
        return unknown
    if last.outcome == "ACTION_READBACK":
        return Assessment("ROUTE_EXISTING_CLOSURE_OWNER", 0, (last.receipt_id,))
    failures = []
    for row in reversed(rows):
        if row.outcome != "FAILED" or row.cause_sha256 != last.cause_sha256:
            break
        failures.append(row.receipt_id)
    count = len(failures)
    return Assessment("PROCESS_STALLED_CANDIDATE" if count >= 2 else "SINGLE_FAILURE_OBSERVED",
                      count, tuple(reversed(failures)))
