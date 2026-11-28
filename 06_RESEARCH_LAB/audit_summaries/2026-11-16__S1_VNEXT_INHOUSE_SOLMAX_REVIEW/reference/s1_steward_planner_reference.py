"""READ-ONLY S1 Steward vNext decision planner, not a GitHub executor.

This is a falsifiable challenger to Claude's v2 state transitions. No network,
secrets, writes, grants, model calls, paid API, or merge authority.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from hashlib import sha256
import json
from typing import Sequence, Mapping

VALID_STATES = frozenset({"DISCOVERED", "TRIAGED", "BUILD", "TEST", "REVIEW", "RELEASE", "OBSERVE", "BLOCKED", "PARKED", "CLOSED_VERIFIED", "CLOSED_NOISE", "OWNER_ACTION"})
RISK = {"LOW":0, "MEDIUM":1, "HIGH":2, "HIGH_IMPACT":3, "EXTREME":4, "UNKNOWN":5}

@dataclass(frozen=True)
class Case:
    item_id: str
    state: str
    risk: str
    source_fingerprint: str
    priority: int
    actionable: bool
    evidence_changed: bool
    touched_by_other_writer: bool
    privacy_proven: bool
    exact_head_ci_proven: bool
    independent_review_proven: bool
    lane_eligible: bool
    owner_present_required: bool
    tests_executed: bool
    due_time: datetime | None = None
    attempts: int = 0
    active_incident: bool = False
    source_authority_proven: bool = False
    natural_consumer_proven: bool = False
    merge_readback_proven: bool = False
    reviewer_available: bool = True
    native_tool_available: bool = True
    changed_files: tuple[str, ...] = ()
    blocker: str = ""

@dataclass(frozen=True)
class Plan:
    action: str
    item_id: str
    reason: str
    fingerprint: str
    owner_card: Mapping[str, str] | None = None
    authorized: bool = False
    def __post_init__(self):
        if self.authorized:
            raise ValueError("planner cannot authorize execution")


def fingerprint_case(case: Case, *, main_sha: str, policy_blob: str) -> str:
    # A value to deduplicate identical observations. Not a proof of origin.
    payload = (case.item_id, case.state, case.risk, case.source_fingerprint,
        case.privacy_proven, case.exact_head_ci_proven,
        case.independent_review_proven, case.lane_eligible,
        case.owner_present_required, case.native_tool_available,
        case.blocker, main_sha, policy_blob)
    return sha256(json.dumps(payload,separators=(",", ":")).encode()).hexdigest()


def owner_action_card(case: Case, *, head: str, exact_main: str,
                      missing: Sequence[str], recovery: str) -> dict[str, str]:
    """A nonbinding concise card, never an owner approval token."""
    return {
        "kind":"S1_OWNER_DECISION_CARD_v1",
        "pr":case.item_id,
        "head":head,
        "main_at_assessment":exact_main,
        "risk":case.risk,
        "release_readiness": "GATES_NOT_PROVEN" if missing else "ADVISORY_ALL_CHECKS_PROVEN",
        "missing_gates": ", ".join(missing) if missing else "none observed",
        "recovery_state":recovery,
        "owner_action":"Review exact HEAD and press native GitHub squash merge only if all fresh gates prove PASS",
        "s1_action":"WAIT_FOR_NATIVE_OWNER_DECISION",
        "expires":"At any HEAD, main, policy, CI or recovery change; never a reusable approval",
    }


def decide_case(case: Case, *, head: str, main: str, policy_blob: str) -> Plan:
    """A pure action suggestion, not an instruction to tools or an approval."""
    if case.state not in VALID_STATES or case.risk not in RISK:
        return Plan("HOLD", case.item_id, "UNKNOWN_STATE_OR_RISK", "")
    fp = fingerprint_case(case, main_sha=main,policy_blob=policy_blob)
    if not case.source_authority_proven:
        return Plan("HOLD", case.item_id, "SOURCE_NOT_AUTHENTICATED", fp)
    if case.touched_by_other_writer:
        return Plan("HOLD", case.item_id, "OTHER_WRITER_LEASE", fp)
    if case.state in {"CLOSED_VERIFIED", "CLOSED_NOISE"}:
        return Plan("NOOP", case.item_id, "TERMINAL_NO_NEW_ACTION", fp)
    if case.state == "OBSERVE":
        if case.natural_consumer_proven and case.merge_readback_proven:
            return Plan("ADVISORY_CLOSE_PROOF", case.item_id, "CONSUMER_AND_MERGE_NATIVE_EVIDENCE_REQUIRED", fp)
        return Plan("OBSERVE", case.item_id, "NATURAL_CONSUMER_NOT_PROVEN", fp)
    if case.owner_present_required or case.risk in {"EXTREME", "UNKNOWN"}:
        missing=[]
        if not case.tests_executed:missing.append("native_tests")
        if not case.exact_head_ci_proven:missing.append("exact_head_ci")
        if not case.privacy_proven:missing.append("privacy")
        if not case.independent_review_proven:missing.append("independent_review")
        card=owner_action_card(case,head=head, exact_main=main,missing=missing,recovery="NOT_IN_INPUT")
        return Plan("OWNER_CARD", case.item_id, "OWNER_PRESENT_MERGE", fp, card)
    if case.state in {"DISCOVERED", "TRIAGED", "BUILD"}:
        if not case.actionable or not case.evidence_changed:
            return Plan("BLOCKED_WITH_TRIGGER",case.item_id,"NO_NEW_ACTIONABLE_EVIDENCE",fp)
        if not case.native_tool_available:
            return Plan("BLOCKED_WITH_TRIGGER",case.item_id,"EXECUTOR_TOOL_NOT_VERIFIED",fp)
        return Plan("REPAIR_OR_REQUEST_CODEX",case.item_id,"ORIGINAL_SOURCE_BRANCH_ONLY",fp)
    if case.state == "TEST":
        if not case.tests_executed or not case.exact_head_ci_proven:
            return Plan("RUN_TESTS_OR_DIAGNOSE",case.item_id,"TEST_COVERAGE_NOT_PROVEN",fp)
        return Plan("REQUEST_INDEPENDENT_REVIEW",case.item_id,"TESTS_COMPLETE",fp)
    if case.state == "REVIEW":
        if not case.independent_review_proven:
            if not case.reviewer_available:
                return Plan("BLOCKED_WITH_TRIGGER",case.item_id,"INDEPENDENT_REVIEWER_UNAVAILABLE_OWNER_FALLBACK",fp)
            return Plan("REQUEST_INDEPENDENT_REVIEW",case.item_id,"EXACT_HEAD_REVIEW_MISSING",fp)
        if not case.privacy_proven or not case.exact_head_ci_proven:
            return Plan("BLOCKED_WITH_TRIGGER",case.item_id,"OTHER_GATES_NOT_PROVEN",fp)
        return Plan("PREFLIGHT_RELEASE",case.item_id,"REVIEW_PRESENT_NO_MERGE_PERMISSION",fp)
    if case.state == "RELEASE":
        if not all((case.privacy_proven,case.exact_head_ci_proven,case.tests_executed,
                    case.independent_review_proven,case.lane_eligible)):
            return Plan("BLOCKED_WITH_TRIGGER",case.item_id,"RELEASE_GATES_INCOMPLETE",fp)
        return Plan("PREFLIGHT_RELEASE",case.item_id,"FRESH_NATIVE_PLATFORM_AND_VAULT_GATE_STILL_REQUIRED",fp)
    # PARKED and BLOCKED are NEVER closed merely because the time budget ran out.
    if case.state in {"BLOCKED", "PARKED"}:
        if case.evidence_changed and case.actionable:
            return Plan("RETRIAGE",case.item_id,"TRIGGER_CHANGED",fp)
        return Plan("NOOP",case.item_id,"UNCHANGED_BLOCKER",fp)
    return Plan("HOLD",case.item_id,"STATE_REQUIRES_OWNER_POLICY",fp)


def plan_tick(cases: Sequence[Case], *, head_by_item: Mapping[str,str], main: str,
              policy_blob: str, monday_readonly: bool, max_deep: int = 3) -> tuple[Plan, ...]:
    if monday_readonly:
        return (Plan("NOOP", "*", "MONDAY_READ_ONLY", ""),)
    if max_deep not in (1,2,3): raise ValueError("max_deep must be 1..3")
    prioritized=sorted(cases, key=lambda c:(not c.active_incident,c.priority,c.item_id))
    seen=set(); results=[]
    for c in prioritized:
        if c.item_id in seen: continue
        seen.add(c.item_id)
        head=head_by_item.get(c.item_id, "")
        plan=decide_case(c,head=head,main=main,policy_blob=policy_blob)
        if plan.action == "NOOP" and plan.reason == "UNCHANGED_BLOCKER": continue
        results.append(plan)
        if len(results)>=max_deep:break
    return tuple(results)
