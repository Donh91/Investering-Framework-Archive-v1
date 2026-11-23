"""Pure S1 incident classifier for authenticated native-run observations.

No GitHub reads, background work, scheduling, code writes, permission changes
or merge decisions. Caller must independently authenticate *every* input row.
A green GitHub job by itself is NEVER a source/consumer recovery receipt.
"""
from __future__ import annotations

from datetime import datetime, timezone
import re
import json
import hashlib
from urllib.parse import urlparse

_SHA = re.compile(r"^[0-9a-f]{40}$")
_RUN_PATH = re.compile(r"^/Donh91/[A-Za-z0-9_.-]+/actions/runs/([1-9][0-9]*)$")
_CRITICAL = frozenset({"INTEGRITY", "SECURITY", "PRIVACY", "CUSTODY", "FALSE_PASS"})
_TRANSIENT = frozenset({"TRANSPORT", "RATE_LIMIT", "UPSTREAM_UNAVAILABLE"})
_OTHER = frozenset({"SEMANTIC", "SOURCE_MISSING", "TEST_FAILURE"})
_CLASSES = _CRITICAL | _TRANSIENT | _OTHER
_ALLOWED_EVENTS = frozenset({"schedule", "workflow_dispatch", "push", "workflow_run"})


class IncidentEvidenceError(ValueError):
    """Malformed, conflicting or future-dated incident evidence."""


def _utc(value: object) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise IncidentEvidenceError("UTC_Z_REQUIRED")
    try:
        result = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise IncidentEvidenceError("INVALID_UTC") from exc
    if result.utcoffset().total_seconds() != 0:
        raise IncidentEvidenceError("NOT_UTC")
    return result.astimezone(timezone.utc)


def _checked(row: object, now: datetime) -> dict:
    if not isinstance(row, dict):
        raise IncidentEvidenceError("ROW_OBJECT_REQUIRED")
    key = row.get("incident_key")
    if not isinstance(key, str) or not re.fullmatch(r"[a-zA-Z0-9_.:/-]{8,140}", key):
        raise IncidentEvidenceError("INCIDENT_ID_INVALID")
    url = row.get("native_run_url")
    if not isinstance(url, str):
        raise IncidentEvidenceError("NATIVE_RUN_URL_REQUIRED")
    p = urlparse(url)
    m = _RUN_PATH.fullmatch(p.path)
    if p.scheme != "https" or p.netloc != "github.com" or p.params or p.query or p.fragment or not m:
        raise IncidentEvidenceError("NATIVE_RUN_URL_INVALID")
    if type(row.get("run_id")) is not int or int(m.group(1)) != row["run_id"]:
        raise IncidentEvidenceError("NATIVE_RUN_ID_MISMATCH")
    if row.get("event") not in _ALLOWED_EVENTS:
        raise IncidentEvidenceError("RUN_EVENT_INVALID")
    if row.get("result") not in {"FAILURE", "SUCCESS"}:
        raise IncidentEvidenceError("RUN_RESULT_INVALID")
    failure_class = row.get("failure_class")
    if row["result"] == "FAILURE" and failure_class not in _CLASSES:
        raise IncidentEvidenceError("FAILURE_CLASS_REQUIRED")
    if row["result"] == "SUCCESS" and failure_class is not None:
        raise IncidentEvidenceError("SUCCESS_WITH_FAILURE_CLASS")
    if not isinstance(row.get("source_sha"), str) or not _SHA.fullmatch(row["source_sha"]):
        raise IncidentEvidenceError("EXACT_SOURCE_SHA_REQUIRED")
    if type(row.get("consumer_receipt_verified")) is not bool:
        raise IncidentEvidenceError("EXPLICIT_CONSUMER_RECEIPT_REQUIRED")
    if row["result"] == "FAILURE" and row["consumer_receipt_verified"]:
        raise IncidentEvidenceError("FAILED_RUN_CANNOT_HAVE_RECOVERY_RECEIPT")
    t = _utc(row.get("observed_at_utc"))
    if t > now:
        raise IncidentEvidenceError("FUTURE_EVIDENCE")
    return {**row, "_time": t}


_HEALTH_SOURCE = "research/architecture_health/LATEST_AUTOMATION_HEALTH.json"
_HEALTH_WORKFLOW = ".github/workflows/automation-production-health.yml"
_HEALTH_REPO = "Donh91/Investering-Framework-Archive-v1"
_HEALTH_MARKER = "AUTOMATION_HEALTH_RED_ORIGIN_v1"
_HEALTH_FIELDS = frozenset({
    "repo", "run_id", "run_attempt", "run_event", "source_main",
    "source_path", "source_blob", "history_path", "history_blob",
    "source_generated_at_utc", "status",
})


def _git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()


def verify_health_red_origin(
    comment_body: str,
    *,
    author_login: str,
    created_at: str,
    updated_at: str,
    native_run: dict,
    source_bytes: bytes,
    history_bytes: bytes,
    current_main_source_blob: str,
    source_main: str,
) -> dict:
    """Fail-closed offline admission predicate for a *trusted* native readback.

    Inputs must be independently fetched and authenticated by the caller using
    GitHub's native read APIs; this helper does not fetch, grant authority or
    substitute a fabricated issue body for a bot comment. It consumes exactly
    the fields emitted by the real health producer in the current workflow.
    """
    def reject(why: str) -> None:
        raise IncidentEvidenceError("INCIDENT_ORIGIN_UNVERIFIED:" + why)

    if author_login != "github-actions[bot]" or not created_at or created_at != updated_at:
        reject("NOT_UNEDITED_ACTIONS_BOT_COMMENT")
    if not isinstance(comment_body, str):
        reject("COMMENT_MISSING")
    lines = comment_body.strip().splitlines()
    if not lines or lines[0] != _HEALTH_MARKER:
        reject("ORIGIN_MARKER_INVALID")
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if ": " not in line:
            reject("FIELD_SEPARATOR_INVALID")
        key, value = line.split(": ", 1)
        if key not in _HEALTH_FIELDS or key in fields or not value:
            reject("FIELD_DUPLICATE_UNKNOWN_OR_EMPTY")
        fields[key] = value
    if fields.keys() != _HEALTH_FIELDS:
        reject("ORIGIN_FIELDS_MISSING")
    if fields["repo"] != _HEALTH_REPO or fields["source_path"] != _HEALTH_SOURCE:
        reject("WRONG_REPOSITORY_OR_SOURCE")
    if fields["run_event"] != "schedule" or fields["status"] != "RED":
        reject("NOT_SCHEDULED_RED")
    if not re.fullmatch(r"[1-9][0-9]*", fields["run_id"]) or not re.fullmatch(r"[1-9][0-9]*", fields["run_attempt"]):
        reject("INVALID_RUN_OR_ATTEMPT")
    run_id, attempt = int(fields["run_id"]), int(fields["run_attempt"])
    expected_history_path = f"research/architecture_health/history/{run_id}-attempt-{attempt}.json"
    if fields["history_path"] != expected_history_path:
        reject("HISTORY_PATH_MISMATCH")
    for key in ("source_main", "source_blob", "history_blob"):
        if not re.fullmatch(r"[0-9a-f]{40}", fields[key]):
            reject("INVALID_GIT_SHA")
    if source_main != fields["source_main"]:
        reject("SOURCE_COMMIT_NOT_READ_BACK")
    if (not isinstance(source_bytes, bytes) or not isinstance(history_bytes, bytes)
        or _git_blob_sha(source_bytes) != fields["source_blob"]
        or current_main_source_blob != fields["source_blob"]
        or _git_blob_sha(history_bytes) != fields["history_blob"]):
        reject("SOURCE_OR_HISTORY_BLOB_MISMATCH")
    if not isinstance(native_run, dict):
        reject("NATIVE_RUN_MISSING")
    nr = native_run.get("repository")
    if (type(native_run.get("id")) is not int or native_run["id"] != run_id
        or type(native_run.get("run_attempt")) is not int or native_run["run_attempt"] != attempt
        or native_run.get("event") != "schedule"
        or native_run.get("head_branch") != "main"
        or native_run.get("status") != "completed"
        or native_run.get("conclusion") != "success"
        or native_run.get("name") != "Automation Production Health"
        or not isinstance(native_run.get("path"), str)
        or _HEALTH_WORKFLOW not in native_run["path"]
        or not isinstance(nr, dict) or nr.get("full_name") != _HEALTH_REPO):
        reject("NATIVE_RUN_IDENTITY_MISMATCH")
    try:
        report = json.loads(source_bytes)
        history = json.loads(history_bytes)
    except (ValueError, TypeError):
        reject("JSON_UNREADABLE")
    if not isinstance(report, dict) or not isinstance(history, dict):
        reject("NON_OBJECT_SOURCE")
    if (report.get("repository") != _HEALTH_REPO
        or report.get("status") != "RED"
        or type(report.get("red_count")) is not int or report["red_count"] <= 0
        or report.get("generated_at_utc") != fields["source_generated_at_utc"]):
        reject("REPORT_RED_OR_TIMESTAMP_INVALID")
    try:
        _utc(fields["source_generated_at_utc"])
    except IncidentEvidenceError:
        reject("SOURCE_TIMESTAMP_INVALID")
    from scripts.health.automation_health_resolution import (
        HISTORY_CONTRACT, canonical_hash,
    )
    if (history.get("contract") != HISTORY_CONTRACT
        or type(history.get("run_id")) is not int or history["run_id"] != run_id
        or type(history.get("run_attempt")) is not int or history["run_attempt"] != attempt
        or history.get("run_event") != "schedule"
        or history.get("status") != "RED"
        or type(history.get("red_count")) is not int
        or history["red_count"] != report["red_count"]
        or history.get("generated_at_utc") != report["generated_at_utc"]
        or history.get("source_path") != _HEALTH_SOURCE
        or history.get("source_sha256") != hashlib.sha256(source_bytes).hexdigest()
        or history.get("receipt_sha256") != canonical_hash({
            k: v for k, v in history.items() if k != "receipt_sha256"
        })):
        reject("HISTORY_NOT_BOUND_TO_NATIVE_RUN_AND_SOURCE")
    return {
        "contract": "S1_HEALTH_ORIGIN_ADVISORY_v1",
        "status": "ORIGIN_CANDIDATE_VERIFIED_FROM_SUPPLIED_GITHUB_READBACK",
        "source_main": source_main,
        "source_blob": fields["source_blob"],
        "run_id": run_id,
        "run_attempt": attempt,
        "incident_evidence_key": f"{_HEALTH_REPO}:{run_id}:{attempt}",
        "original_consumer_verified": False,
        "incident_closed": False,
        "merge_authorized": False,
    }


def incident_triage(rows: list[dict], *, as_of_utc: str, threshold: int = 2) -> dict:
    """Classify one original incident from independently checked native receipts.

    The returned state is ONLY a candidate, never a verified external fact.
    Critical failures cannot self-resolve solely because a later run is green.
    Transient recovery needs a *subsequent natural scheduled* success with
    a separately verified consumer receipt; all such claims are rechecked by
    the real authorized S1 before writing/closing anything.
    """
    if not isinstance(rows, list) or not rows or len(rows) > 100:
        raise IncidentEvidenceError("BOUNDED_NONEMPTY_SERIES_REQUIRED")
    if type(threshold) is not int or not 2 <= threshold <= 4:
        raise IncidentEvidenceError("THRESHOLD_OUT_OF_BOUNDS")
    now = _utc(as_of_utc)
    checked = [_checked(row, now) for row in rows]
    keys = {row["incident_key"] for row in checked}
    repos = {row["native_run_url"].split("/")[4] for row in checked}
    if len(keys) != 1 or len(repos) != 1:
        raise IncidentEvidenceError("MIXED_INCIDENT_OR_REPOSITORY")
    unique = {}
    for row in checked:
        previous = unique.get(row["run_id"])
        if previous is not None and previous != row:
            raise IncidentEvidenceError("CONFLICTING_RUN_RECEIPTS")
        unique[row["run_id"]] = row
    history = sorted(unique.values(), key=lambda row: (row["_time"], row["run_id"]))
    latest = history[-1]
    failures = [row for row in history if row["result"] == "FAILURE"]
    critical = [row for row in failures if row["failure_class"] in _CRITICAL]
    streak = 0
    for row in reversed(history):
        if row["result"] != "FAILURE":
            break
        streak += 1
    if critical:
        decision, action = "INTEGRITY_HOLD", "INVESTIGATE_AND_REQUIRE_INDEPENDENT_RESOLUTION"
    elif not failures:
        decision, action = "NO_FAILURE_OBSERVED", "NO_REPAIR"
    elif latest["result"] == "SUCCESS":
        if latest["event"] == "schedule" and latest["consumer_receipt_verified"]:
            decision, action = "RECOVERY_CANDIDATE", "REVERIFY_NATIVE_CONSUMER_BEFORE_CLOSURE"
        else:
            decision, action = "RECOVERY_UNVERIFIED", "OBSERVE_NEXT_NATURAL_CONSUMER"
    elif latest["failure_class"] not in _TRANSIENT or streak >= threshold:
        decision, action = "REPAIR_CANDIDATE", "REPRODUCE_AND_REPAIR_EXISTING_OWNER"
    else:
        decision, action = "OBSERVE_TRANSIENT", "WAIT_FOR_NEXT_NATURAL_RUN"
    return {
        "contract": "S1_INCIDENT_TRIAGE_ADVISORY_v1",
        "incident_key": latest["incident_key"],
        "original_repository": next(iter(repos)),
        "decision": decision,
        "next_action": action,
        "latest_run_url": latest["native_run_url"],
        "latest_source_sha": latest["source_sha"],
        "failure_count": len(failures),
        "consecutive_failure_count": streak,
        "unique_runs": len(history),
        "critical_failure_ever_seen": bool(critical),
        "all_inputs_externally_authenticated": False,
        "incident_closed": False,
        "recovery_verified": False,
        "dispatch_authorized": False,
        "merge_authorized": False,
        "safety_policy_changed": False,
    }
