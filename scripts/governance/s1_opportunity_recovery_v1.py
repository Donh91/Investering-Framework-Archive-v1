"""S1 v4.3 deterministic opportunity/research reactivation advisor.

Pure read-only functions, not permission to dispatch, edit GitHub or merge.
Caller must authenticate every input against current original owner records.
"""
from hashlib import sha256
import json
from urllib.parse import urlparse
import re

ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "RESEARCH": 4}
MATERIAL = frozenset((
    "head", "executed_ci", "binding_review", "policy", "source_receipt",
    "owner_conflict", "runner_recovered", "matured_prospective_window",
    "native_ack",
))
TERMINAL = frozenset((
    "CLOSED_VERIFIED", "REJECTED_WITH_EVIDENCE",
    "SUPERSEDED_VERIFIED", "ADOPTED_VERIFIED",
))
VALID_STATES = TERMINAL | frozenset((
    "DISCOVERED", "ACTIONABLE", "IN_PROGRESS", "BLOCKED_WITH_TRIGGER",
    "READY_FOR_TEST", "IN_VALIDATION", "VERIFICATION", "PROCESS_STALLED",
))


class AdvisoryInputError(ValueError):
    pass


def _url(value):
    if not isinstance(value, str):
        return False
    u = urlparse(value)
    parts = u.path.strip("/").split("/")
    return (u.scheme == "https" and u.netloc == "github.com"
            and len(parts) == 4 and parts[0] == "Donh91"
            and parts[2] in ("issues", "pull") and parts[3].isdigit())


def _check(item):
    if not isinstance(item, dict):
        raise AdvisoryInputError("case must be a dict")
    for key in ("case_id", "original_url", "owner", "evidence_fingerprint",
                "priority", "status", "authority"):
        if not item.get(key):
            raise AdvisoryInputError("missing provenance field " + key)
    if not _url(item["original_url"]):
        raise AdvisoryInputError("noncanonical owner URL")
    if item["priority"] not in ORDER:
        raise AdvisoryInputError("unknown priority")
    if item["status"] not in VALID_STATES:
        raise AdvisoryInputError("unknown lifecycle state")
    if item["authority"] not in ("ADVISORY_ONLY", "READ_ONLY", "OWNER_GOVERNED"):
        raise AdvisoryInputError("authority escalation")
    if len(item["evidence_fingerprint"]) < 8:
        raise AdvisoryInputError("insufficient fingerprint")


def reactivated(item):
    """Never reactivate unchanged blockers by elapsed time or new comments."""
    _check(item)
    change = item.get("material_trigger")
    if not isinstance(change, dict) or change.get("kind") not in MATERIAL:
        return False
    before, after = change.get("previous"), change.get("current")
    evidence_url = change.get("native_evidence_url")
    native_run = False
    if change.get("kind") == "executed_ci" and isinstance(evidence_url, str):
        parsed = urlparse(evidence_url)
        native_run = (parsed.scheme == "https" and parsed.netloc == "github.com"
                      and re.fullmatch(r"/Donh91/[A-Za-z0-9_.-]+/actions/runs/[1-9][0-9]*(?:/job/[1-9][0-9]*)?", parsed.path) is not None)
    return (isinstance(before, str) and isinstance(after, str)
            and len(before) >= 8 and len(after) >= 8 and before != after
            and (_url(evidence_url) or native_run))


def select_cases_isolated(cases, maximum=3):
    """Keep malformed candidate telemetry local; preserve strict legacy API.

    Invalid rows are reported, never silently admitted or granted authority.
    Existing callers can migrate without changing select_cases' exception API.
    """
    if not isinstance(cases, list):
        raise AdvisoryInputError("case list required")
    good, invalid = [], []
    for index, item in enumerate(cases):
        try:
            select_cases([item], maximum=maximum)
        except (AdvisoryInputError, TypeError, ValueError) as exc:
            invalid.append({"input_index": index, "disposition": "INTERNAL_REPAIRABLE",
                            "reason": str(exc), "other_prs_may_continue": True})
        else:
            good.append(item)
    return {"selected": select_cases(good, maximum=maximum),
            "invalid_cases": invalid, "release_authority": False}


def select_cases(cases, maximum=3):
    """Recommend max 3 original cases for *fresh release preflight* only."""
    if type(maximum) is not int or not 1 <= maximum <= 3:
        raise AdvisoryInputError("maximum must be 1-3")
    selected = {}
    for item in cases:
        _check(item)
        if item["status"] in TERMINAL or item.get("active_head_editor"):
            continue
        if item.get("safety_gate") == "FAILED":
            continue
        if item["status"] in ("BLOCKED_WITH_TRIGGER", "PROCESS_STALLED") and not reactivated(item):
            continue
        impact, effort = item.get("impact", 3), item.get("effort", 3)
        if (type(impact) is not int or type(effort) is not int
                or not 1 <= impact <= 5 or not 1 <= effort <= 5):
            raise AdvisoryInputError("invalid score components")
        # Hard P0 precedence, no score can bypass active source/integrity risk.
        rank = (ORDER[item["priority"]],
                0 if item.get("ready_for_preflight") is True else 1,
                -impact, effort, item["case_id"])
        # A permalink, query string or trailing slash cannot create a second case.
        identity = urlparse(item["original_url"]).path.rstrip("/")
        if identity not in selected or rank < selected[identity][0]:
            selected[identity] = (rank, item)
    result = sorted(selected.values(), key=lambda v: v[0])[:maximum]
    return [{
        "case_id": item["case_id"],
        "original_url": item["original_url"],
        "evidence_fingerprint": item["evidence_fingerprint"],
        "decision": "VERIFY_CURRENT_GATES",
        "release_authority": False,
        "trigger": "MATERIAL" if item["status"] in
                   ("BLOCKED_WITH_TRIGGER", "PROCESS_STALLED") else "ACTIVE",
    } for _, item in result]


def strategic_question(item, brief, *, source_root=None, now=None):
    """Correlate offline advice only after the existing source reader accepts it.

    A supplied CURRENT label is not verification. source_root is a local checkout;
    this boundary performs no network access, dispatch or file writes.
    """
    _check(item)
    needs_advice = any(item.get(k) is True for k in (
        "ambiguous_owner", "cross_domain_conflict",
        "competing_implementation", "research_decision_unknown",
    ))
    if not needs_advice:
        return {"state": "NOT_NEEDED", "release_authority": False}
    if not isinstance(brief, dict) or brief.get("contract") != "FRAMEWORK_STRATEGIST_BRIEF_v1":
        return {"state": "SOURCE_UNAVAILABLE", "release_authority": False}
    if (not isinstance(brief.get("authority"), dict)
            or brief["authority"].get("type") != "ADVISORY_ONLY"):
        raise AdvisoryInputError("Strategist cannot escalate authority")
    if brief.get("input_status") != "CURRENT" or not brief.get("intent_sha256"):
        return {"state": "STALE_BRIEF", "release_authority": False}
    if source_root is None or now is None:
        return {"state": "SOURCE_UNVERIFIED", "release_authority": False}
    from pathlib import Path
    from scripts.framework_intelligence.framework_learning_supervisor import read_strategist_advisory
    root = Path(source_root)
    verified = read_strategist_advisory(root, now)
    if verified.get("status") != "ADVISORY_PREVIOUS_EVIDENCE":
        state = "SOURCE_UNAVAILABLE" if verified.get("status") == "UNAVAILABLE" else "SOURCE_UNVERIFIED"
        return {"state": state, "reason": verified.get("status"),
                "release_authority": False}
    try:
        raw = (root / verified["reference"]).read_bytes()
        if (sha256(raw).hexdigest() != verified.get("source_sha256")
                or json.loads(raw) != brief):
            return {"state": "SOURCE_UNVERIFIED", "reason": "BRIEF_CHANGED",
                    "release_authority": False}
    except (OSError, ValueError, UnicodeDecodeError):
        return {"state": "SOURCE_UNAVAILABLE", "release_authority": False}
    bound = {
        "case": item["evidence_fingerprint"],
        "intent": brief["intent_sha256"],
        "generated": brief.get("generated_at_utc"),
        "source_sha256": verified["source_sha256"],
    }
    matches = []
    for proposal in brief.get("proposals", []):
        if not isinstance(proposal, dict):
            continue
        if (proposal.get("id") == item.get("strategist_proposal_id")
                or proposal.get("evidence_fingerprint") == item["evidence_fingerprint"]):
            if isinstance(proposal.get("id"), str) and len(matches) < 3:
                matches.append(proposal["id"])
    return {
        "matched_existing_proposal_ids": sorted(set(matches)),
        "state": "READ_EXISTING_BRIEF",
        "brief_binding_sha256": sha256(json.dumps(
            bound, sort_keys=True, separators=(",", ":")
        ).encode()).hexdigest(),
        "question": "Owner, falsifier, alternatives, bounded next action?",
        "authority": "ADVISORY_ONLY",
        "release_authority": False,
    }
