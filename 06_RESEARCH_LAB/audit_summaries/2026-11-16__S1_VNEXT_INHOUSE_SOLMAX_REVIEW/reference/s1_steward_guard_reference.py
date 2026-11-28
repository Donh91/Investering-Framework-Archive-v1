"""S1 Steward vNext: pure, READ-ONLY adversarial reference rules.

NOT RELEASE CODE. Outputs are advisory and NEVER authorize GitHub mutation,
merge, owner approval, Vault access, paid API calls, trading or scheduling.
The caller must establish provenance using native APIs, not user-supplied JSON.
Designed for detached Claude review before integration into existing S1 v2.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import re
from typing import Any, Mapping, Sequence

SHA40 = re.compile(r"^[0-9a-f]{40}$")
REPO = "Donh91/Investering-Framework-Archive-v1"
HEALTH_PATH = ".github/workflows/automation-production-health.yml"
S1_TASK = "6ae5fd466b48819187abc224ec0f1c5f"


@dataclass(frozen=True)
class Finding:
    disposition: str
    code: str
    details: tuple[str, ...] = ()
    # No method in this file returns production authorization.
    authorized: bool = False

    def __post_init__(self) -> None:
        if self.authorized:
            raise ValueError("Reference guard cannot grant authority")


def _sha40(value: Any) -> bool:
    return isinstance(value, str) and SHA40.fullmatch(value) is not None


def _str(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _utc(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, OverflowError):
        return None
    if dt.tzinfo is None:
        return None
    try:
        return dt.astimezone(timezone.utc)
    except (OverflowError, ValueError):
        return None


def _looks_native_run(run: Mapping[str, Any]) -> bool:
    """Schema check, not native-authenticity proof."""
    return (
        isinstance(run.get("id"), int)
        and not isinstance(run.get("id"), bool)
        and run["id"] > 0
        and isinstance(run.get("path"), str)
        and isinstance(run.get("event"), str)
        and isinstance(run.get("head_branch"), str)
        and run.get("status") in ("completed", "queued", "in_progress", "requested", "waiting", "pending")
        and _utc(run.get("created_at")) is not None
    )


def admit_workflow_run(run: Mapping[str, Any], *, repo: str = REPO) -> Finding:
    """Prevent fork branch `main` being mistaken for local production.

    A result must still be corroborated against the native repository API.
    Do not infer provenance from a comment's JSON.
    """
    if not isinstance(run, Mapping) or not repo:
        return Finding("HOLD", "INPUT_INVALID")
    if run.get("head_branch") != "main":
        return Finding("HOLD", "NOT_DEFAULT_BRANCH")
    event = run.get("event")
    if event == "workflow_run":
        hr = run.get("head_repository")
        if not isinstance(hr, Mapping) or hr.get("full_name") != repo:
            return Finding("HOLD", "FOREIGN_OR_MISSING_HEAD_REPOSITORY")
        return Finding("ADVISORY_CANDIDATE", "SAME_REPOSITORY_WORKFLOW_RUN")
    if event in ("schedule", "workflow_dispatch", "repository_dispatch"):
        return Finding("ADVISORY_CANDIDATE", "REPO_SCOPED_EVENT")
    return Finding("HOLD", "EVENT_NOT_PRODUCTION")


def latest_scheduled_health(
    pages: Sequence[Sequence[Mapping[str, Any]]],
    *,
    observed_at: datetime,
    exhausted: bool,
    expected_repo: str = REPO,
    max_age_hours: int = 26,
) -> Finding:
    """Offline reducer for repo-wide /actions/runs pagination.

    The *adapter* must fetch the repo-scoped endpoint natively and paginate
    until exhausted or older than the 26-hour lookback. This reducer rejects
    unproven pagination and mismatched path/event/branch. No network calls.
    """
    if observed_at.tzinfo is None or not expected_repo or max_age_hours <= 0:
        return Finding("HOLD", "INVALID_TIME_OR_SCOPE")
    now = observed_at.astimezone(timezone.utc)
    cutoff = now - timedelta(hours=max_age_hours)
    runs = [r for page in pages for r in page]
    if not runs:
        return Finding("HOLD", "NO_RUNS")
    if any(not isinstance(r, Mapping) or not _looks_native_run(r) for r in runs):
        return Finding("HOLD", "MALFORMED_RUN_PAGE")
    timestamps = [_utc(r["created_at"]) for r in runs]
    if any(t is None or t > now + timedelta(minutes=5) for t in timestamps):
        return Finding("HOLD", "INVALID_RUN_CLOCK")
    if any(timestamps[i] < timestamps[i + 1] for i in range(len(timestamps) - 1)):
        return Finding("HOLD", "PAGES_NOT_NEWEST_FIRST")
    ids = [r["id"] for r in runs]
    if len(ids) != len(set(ids)):
        return Finding("HOLD", "DUPLICATED_RUN_PAGE")
    # If the adapter does not exhaust the list, the oldest scanned record
    # must cross the lookback boundary; otherwise a newer matching run may
    # have been omitted by a truncated search.
    if not exhausted and timestamps[-1] > cutoff:
        return Finding("HOLD", "PAGINATION_NOT_PROVEN")
    # The native API is repo scoped, but workflow path and event still need
    # exact matching. 'workflow_run' from a fork is NOT a scheduled main run.
    matches = [
        r for r in runs
        if r.get("path") == HEALTH_PATH
        and r.get("event") == "schedule"
        and r.get("head_branch") == "main"
    ]
    if not matches:
        return Finding("HOLD", "NO_SCHEDULED_MAIN_HEALTH_RUN")
    most_recent = matches[0]
    completed = _utc(most_recent.get("updated_at"))
    if most_recent.get("status") != "completed":
        return Finding("HOLD", "LATEST_HEALTH_NOT_TERMINAL", (str(most_recent["id"]),))
    if most_recent.get("conclusion") != "success":
        return Finding("HOLD", "LATEST_HEALTH_NOT_SUCCESS", (str(most_recent["id"]),))
    if completed is None or completed < cutoff or completed > now + timedelta(minutes=5):
        return Finding("HOLD", "HEALTH_FINISH_NOT_FRESH", (str(most_recent["id"]),))
    return Finding("ADVISORY_CANDIDATE", "SCHEDULED_HEALTH_SUCCESS", (str(most_recent["id"]),))


def independent_review_candidate(
    *,
    head: str,
    author_roles: Sequence[str],
    review: Mapping[str, Any],
    native_identity_attested: bool,
    native_head_attested: bool,
) -> Finding:
    """Guard an *evidence candidate* without making a review authoritative.

    native_identity_attested and native_head_attested are adapter facts. When
    a caller sources them from untrusted comments, the result is meaningless.
    The separate GitHub protection/recovery checks are still mandatory.
    """
    if not _sha40(head) or not native_identity_attested or not native_head_attested:
        return Finding("HOLD", "UNBOUND_NATIVE_REVIEW_PROVENANCE")
    if not isinstance(review, Mapping):
        return Finding("HOLD", "INVALID_REVIEW")
    if review.get("head_sha") != head or review.get("verdict") != "APPROVE":
        return Finding("HOLD", "STALE_OR_NON_APPROVED_REVIEW")
    if review.get("is_edited") is not False:
        return Finding("HOLD", "REVIEW_MUTABLE_OR_UNKNOWN")
    roles = {_str(r).upper() for r in author_roles}
    reviewer = review.get("reviewer")
    if reviewer == "S1_SPECIALIST":
        # A self-run rubric is a useful preflight, not independent review.
        return Finding("HOLD", "SPECIALIST_SELF_CHECK_NOT_INDEPENDENT")
    if reviewer == "CODEX":
        if "CODEX" in roles or "UNKNOWN" in roles:
            return Finding("HOLD", "CODEX_AUTHOR_OR_UNKNOWN")
        if not review.get("app_identity_verified"):
            return Finding("HOLD", "CODEX_APP_IDENTITY_MISSING")
        if review.get("unresolved_findings") is not False:
            return Finding("HOLD", "CODEX_FINDINGS_UNRESOLVED")
        return Finding("ADVISORY_CANDIDATE", "INDEPENDENT_CODEX_EVIDENCE")
    if reviewer == "CLAUDE":
        if "CLAUDE" in roles or "UNKNOWN" in roles:
            return Finding("HOLD", "CLAUDE_AUTHOR_OR_UNKNOWN")
        if review.get("independence") != "INDEPENDENT_DETACHED":
            return Finding("HOLD", "CLAUDE_NOT_DETACHED")
        if not all(_str(review.get(k)) for k in ("request_id", "report_path")):
            return Finding("HOLD", "CLAUDE_REQUEST_OR_REPORT_MISSING")
        if not _sha40(review.get("report_blob")) or not _sha40(review.get("bridge_commit")):
            return Finding("HOLD", "CLAUDE_REPORT_UNBOUND")
        if review.get("lane_eligible") != "YES":
            return Finding("HOLD", "CLAUDE_LANE_NOT_ASSERTED")
        return Finding("ADVISORY_CANDIDATE", "INDEPENDENT_CLAUDE_EVIDENCE")
    return Finding("HOLD", "UNKNOWN_REVIEW_KIND")


@dataclass(frozen=True)
class WorkItem:
    key: str
    head_sha: str
    priority: int  # lower is more urgent, frozen by governed classification
    current_state: str
    risk: str
    new_evidence: bool
    has_other_writer: bool = False
    actionable: bool = False
    native_source_verified: bool = False
    blocker_fingerprint: str = ""


def shortlist_work(items: Sequence[WorkItem], *, max_deep: int = 3) -> tuple[WorkItem, ...]:
    """Cheap delta-screen before deeper reads. Does not close or mutate work."""
    if max_deep < 1 or max_deep > 3:
        raise ValueError("Bounded maximum is 1-3")
    seen: set[str] = set()
    eligible: list[WorkItem] = []
    for it in items:
        if it.key in seen:
            continue
        seen.add(it.key)
        if (
            not it.native_source_verified or not _sha40(it.head_sha)
            or not it.actionable or not it.new_evidence
            or it.has_other_writer or it.current_state in {"MERGED", "CLOSED_VERIFIED"}
        ):
            continue
        eligible.append(it)
    eligible.sort(key=lambda x: (x.priority, x.key))
    return tuple(eligible[:max_deep])


def disposition_suggestion(
    *,
    proposed: str,
    risk: str,
    age_days: int,
    signals: Sequence[Mapping[str, Any]],
    owner_decision_verified: bool = False,
) -> Finding:
    """Never close on elapsed time or self-attested counter/comment alone."""
    if proposed != "CLOSED_NOISE":
        return Finding("ADVISORY_CANDIDATE", "NONDESTRUCTIVE_DISPOSITION")
    if risk in ("HIGH", "HIGH_IMPACT", "EXTREME", "UNKNOWN"):
        return Finding("HOLD", "HIGH_RISK_CLOSE_OWNER_REQUIRED")
    # For LOW/MEDIUM, autonomous close is NOT proposed by this guard until
    # independent objective native proof is present. Age/park count is never
    # a closure signal. Owner's authenticated decision can be submitted for
    # real platform release checks, but this module cannot authenticate it.
    if owner_decision_verified:
        return Finding("ADVISORY_CANDIDATE", "OWNER_CLOSE_DECISION_FOR_PLATFORM_RECHECK")
    allowed = {"DUPLICATE_PROVEN", "SUPERSEDED_BLOBS_PROVEN", "PREMISE_FALSIFIED_PROVEN"}
    strong = [s for s in signals if (
        isinstance(s, Mapping) and s.get("kind") in allowed
        and s.get("native_objective_proof") is True
        and _str(s.get("source_url")).startswith("https://github.com/")
        and _sha40(s.get("source_sha"))
        and s.get("independent_origin") is True
    )]
    if not strong:
        return Finding("HOLD", "NO_INDEPENDENT_OBJECTIVE_CLOSURE_PROOF")
    # Still require a separately authenticated closer. A URL, flags and hashes
    # in JSON can be forged; this reference cannot grant close permission.
    return Finding("HOLD", "OBJECTIVE_PROOF_REQUIRES_NATIVE_CLOSER")


def operation_key(*, repo: str, work_id: str, head: str, action: str, contract_blob: str) -> str:
    """Deterministic identity. Never a credential, lock, or commit signature."""
    if not repo or not work_id or action not in {"REQUEST_REVIEW", "REPAIR", "MERGE", "RECONCILE"}:
        raise ValueError("Invalid operation identity")
    if not _sha40(head) or not _sha40(contract_blob):
        raise ValueError("Cannot key a mutable or unverified source")
    payload = json.dumps([repo, work_id, head, action, contract_blob], separators=(",", ":"))
    return sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ObservedOperation:
    key: str
    intent_exists: bool
    write_attempted: bool
    native_result_exists: bool
    readback_matches: bool
    current_head_matches: bool
    native_authenticity_verified: bool


def reconcile_operation(op: ObservedOperation) -> Finding:
    """Re-read before retry; never interpret missing receipt as no write."""
    if not re.fullmatch(r"[0-9a-f]{64}", op.key):
        return Finding("HOLD", "INVALID_OPERATION_KEY")
    if not op.native_authenticity_verified:
        return Finding("HOLD", "NO_NATIVE_PROVENANCE")
    if op.native_result_exists and op.readback_matches:
        return Finding("ADVISORY_CANDIDATE", "OPERATION_ALREADY_APPLIED")
    if op.native_result_exists and not op.readback_matches:
        return Finding("HOLD", "HALT_RESULT_READBACK_MISMATCH")
    if op.write_attempted and not op.native_result_exists:
        return Finding("HOLD", "AMBIGUOUS_WRITE_RECONCILE_REQUIRED")
    if op.intent_exists and not op.current_head_matches:
        return Finding("HOLD", "SOURCE_DRIFT_RESTART")
    if not op.intent_exists:
        return Finding("ADVISORY_CANDIDATE", "NEW_ACTION_MAY_BE_PREFLIGHTED")
    return Finding("ADVISORY_CANDIDATE", "INTENT_EXISTS_NO_WRITE_YET")


def classify_scheduled_run(run: Mapping[str, Any], *, task_id: str = S1_TASK) -> Finding:
    """Diagnose task scheduler telemetry, not Github code health."""
    if run.get("task_id") != task_id:
        return Finding("HOLD", "WRONG_TASK_ID")
    scheduled = _utc(run.get("scheduled_for"))
    started = _utc(run.get("started_at"))
    ended = _utc(run.get("completed_at"))
    if not scheduled or not started:
        return Finding("HOLD", "RUN_CLOCK_UNVERIFIED")
    if started < scheduled - timedelta(minutes=5) or (ended and ended < started):
        return Finding("HOLD", "NONMONOTONIC_RUN_CLOCK")
    delay_seconds = max(0, int((started - scheduled).total_seconds()))
    if run.get("recorded_status") == "completed" and ended is None:
        return Finding("HOLD", "COMPLETION_WITHOUT_CLOCK")
    if run.get("recorded_status") == "in_progress" and ended is not None:
        return Finding("HOLD", "RUN_STATUS_CLOCK_MISMATCH")
    if delay_seconds > 15 * 60:
        return Finding("HOLD", "SCHEDULE_DISPATCH_DELAY", (str(delay_seconds),))
    if run.get("recorded_status") == "failed":
        return Finding("HOLD", "SCHEDULER_TASK_FAILED", (str(delay_seconds),))
    if run.get("recorded_status") != "completed":
        return Finding("HOLD", "RUN_NOT_FINISHED", (str(delay_seconds),))
    return Finding("ADVISORY_CANDIDATE", "RUN_COMPLETED_ON_SCHEDULE", (str(delay_seconds),))


def verified_closure_classification(e: Mapping[str, Any]) -> Finding:
    """No S1 closure credit from summaries, comments or interactive merges.

    A caller must supply native-verified facts. All outputs are ADVISORY.
    Consumer proof is distinct from merge readback and is never inferred.
    """
    exact = ("task_id", "run_id", "original_repo", "pr_number", "head_sha", "merge_commit_sha")
    if any(not e.get(k) for k in exact):
        return Finding("HOLD", "IDENTITY_OR_SOURCE_MISSING")
    if e.get("task_id") != S1_TASK:
        return Finding("HOLD", "NOT_SOLE_S1")
    if not _sha40(e.get("head_sha")) or not _sha40(e.get("merge_commit_sha")):
        return Finding("HOLD", "INVALID_MERGE_SHA")
    if e.get("route") not in {"DIRECT_SCHEDULED", "SCHEDULED_DELEGATED"}:
        return Finding("HOLD", "NOT_UNATTENDED_S1")
    if e.get("native_task_event_verified") is not True or e.get("native_merge_verified") is not True:
        return Finding("HOLD", "TASK_OR_MERGE_NOT_NATIVE_VERIFIED")
    if e.get("one_parent_squash") is not True or e.get("exact_head_readback") is not True:
        return Finding("HOLD", "MERGE_READBACK_NOT_PROVEN")
    if e.get("route") == "SCHEDULED_DELEGATED" and not all(e.get(k) is True for k in (
        "distinct_receiver_verified", "receiver_job_executed", "artifact_digest_bound", "s1_consumed_result"
    )):
        return Finding("HOLD", "DELEGATED_CHAIN_UNPROVEN")
    if e.get("natural_consumer_verified") is True:
        return Finding("ADVISORY_CANDIDATE", "S1_MERGE_AND_CONSUMER_CANDIDATE")
    return Finding("ADVISORY_CANDIDATE", "S1_MERGE_ONLY_CONSUMER_UNPROVEN")
