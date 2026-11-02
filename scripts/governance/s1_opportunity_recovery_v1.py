"""S1 v4.3 deterministic opportunity/research reactivation advisor.

Pure read-only functions, not permission to dispatch, edit GitHub or merge.
Caller must authenticate every input against current original owner records.
"""
from hashlib import sha256
import json
from urllib.parse import urlparse

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


class AdvisoryInputError(ValueError):
    pass


def _url(value):
    if not isinstance(value, str):
        return False
    u = urlparse(value)
    return u.scheme == "https" and u.netloc == "github.com" and u.path.startswith("/Donh91/")


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
    return (isinstance(before, str) and isinstance(after, str)
            and len(before) >= 8 and len(after) >= 8 and before != after
            and _url(change.get("native_evidence_url")))


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
        identity = item["original_url"]
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


def strategic_question(item, brief):
    """Use only existing Strategist advisory, not an LLM/API dispatch."""
    _check(item)
    needs_advice = any(item.get(k) is True for k in (
        "ambiguous_owner", "cross_domain_conflict",
        "competing_implementation", "research_decision_unknown",
    ))
    if not needs_advice:
        return {"state": "NOT_NEEDED", "release_authority": False}
    if not isinstance(brief, dict) or brief.get("contract") != "FRAMEWORK_STRATEGIST_BRIEF_v1":
        return {"state": "SOURCE_UNAVAILABLE", "release_authority": False}
    if brief.get("authority", {}).get("type") != "ADVISORY_ONLY":
        raise AdvisoryInputError("Strategist cannot escalate authority")
    if brief.get("input_status") != "CURRENT" or not brief.get("intent_sha256"):
        return {"state": "STALE_BRIEF", "release_authority": False}
    bound = {
        "case": item["evidence_fingerprint"],
        "intent": brief["intent_sha256"],
        "generated": brief.get("generated_at_utc"),
    }
    return {
        "state": "READ_EXISTING_BRIEF",
        "brief_binding_sha256": sha256(json.dumps(
            bound, sort_keys=True, separators=(",", ":")
        ).encode()).hexdigest(),
        "question": "Owner, falsifier, alternatives, bounded next action?",
        "authority": "ADVISORY_ONLY",
        "release_authority": False,
    }
