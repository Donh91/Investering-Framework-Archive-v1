"""Read-only resume census for the EXISTING Research Lab queue.

No extra owner, queue, scheduler, researcher or automatic scientific admission.
This is a compatibility/triage view over an authenticated checked-in source.
"""
import re
from urllib.parse import urlparse

SOURCE_CONTRACT = "RESEARCH_LAB_EXTERNAL_SPECIALIST_DISSECTION_QUEUE_V1"
SHA40 = re.compile(r"^[0-9a-f]{40}$")


class ResearchQueueError(ValueError):
    pass


def _github_original(value):
    if not isinstance(value, str):
        return False
    u = urlparse(value)
    return (u.scheme == "https" and u.netloc == "github.com"
            and u.path.startswith("/Donh91/")
            and ("/issues/" in u.path or "/pull/" in u.path))


def census(queue, source_blob_sha):
    """One row per existing research lane, no invented positive result.

    All state changes require live source/owner evidence outside this module.
    The caller must authenticate the queue blob and linked PR/issue states.
    """
    if not isinstance(source_blob_sha, str) or not SHA40.fullmatch(source_blob_sha):
        raise ResearchQueueError("authenticated queue blob SHA required")
    if (not isinstance(queue, dict)
            or queue.get("contract") != SOURCE_CONTRACT
            or queue.get("authority") != "RESEARCH_ONLY"):
        raise ResearchQueueError("unexpected research authority")
    if not isinstance(queue.get("transversal", []), list) or not isinstance(queue.get("lanes", []), list):
        raise ResearchQueueError("invalid original queue sections")
    items = queue.get("transversal", []) + queue.get("lanes", [])
    if not items or len(items) > 100:
        raise ResearchQueueError("missing or unbounded original research lanes")
    output = []
    seen = set()
    for item in items:
        if not isinstance(item, dict) or not item.get("id") or not item.get("owner"):
            raise ResearchQueueError("original research ID and owner required")
        name = item["id"]
        if name in seen:
            raise ResearchQueueError("duplicate research claim identity")
        seen.add(name)
        current = item.get("state", "UNKNOWN")
        if not isinstance(current, str):
            raise ResearchQueueError("invalid original research state")
        original = item.get("execution_issue")
        if not _github_original(original):
            original = None
        followup = item.get("next_action")
        # Retain negative scientific history even if an old record has
        # no next action. Missing follow-up must never erase falsification.
        if any(token in current for token in ("REJECTED", "FALSIFIED", "KILLED")):
            disposition = ("RETAIN_NEGATIVE_LEARNING" if original is not None
                           else "RETAIN_NEGATIVE_LEARNING_OWNER_LINK_REQUIRED")
        elif not isinstance(followup, str) or len(followup.strip()) < 10:
            disposition = "OWNER_MUST_DEFINE_NEXT_ACTION"
        elif original is None:
            disposition = "ORIGINAL_OWNER_LINK_REQUIRED"
        elif current == "MERGED_CAPABILITY_ACTIVE":
            disposition = "EXISTING_MERGE_FOLLOWUP_NOT_AUTO_CLOSED"
        elif any(token in current for token in (
                "PENDING", "WAITING", "PARTIAL", "INCONCLUSIVE", "BLOCKED")):
            disposition = "AWAIT_EXPLICIT_MATERIAL_TRIGGER"
        else:
            disposition = "EXISTING_OWNER_REVIEW_CANDIDATE"
        output.append({
            "claim_id": name,
            "owner": item["owner"],
            "source_state": current,
            "original_issue": original,
            "next_action": followup or None,
            "disposition": disposition,
            "automatically_promoted": False,
            "auto_dispatch": False,
            "science_admitted": False,
        })
    return {
        "contract": "S1_EXISTING_RESEARCH_RECOVERY_READOUT_V1",
        "queue_blob_sha": source_blob_sha,
        "count": len(output),
        "items": output,
        "actual_github_states_checked": False,
        "new_source_events_authenticated": False,
    }
