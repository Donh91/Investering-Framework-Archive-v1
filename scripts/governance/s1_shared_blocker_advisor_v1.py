"""Read-only shared-blocker clustering for the existing S1 owner lanes.

Never creates PRs, reroutes domain owners or labels a blocker resolved.
Input records and source links require authenticated native verification by S1.
"""
from collections import defaultdict
from urllib.parse import urlparse


def _original(url):
    if not isinstance(url, str):
        return None
    parsed = urlparse(url)
    path = parsed.path.strip("/").split("/")
    if parsed.scheme != "https" or parsed.netloc != "github.com":
        return None
    if len(path) != 4 or path[0] != "Donh91":
        return None
    if path[2] not in ("issues", "pull") or not path[3].isdigit():
        return None
    return "/".join(path)


def cluster_blockers(cases, limit=3):
    """Suggest one bounded repair owner per shared evidence-bound blocker."""
    if not isinstance(cases, list) or type(limit) is not int or not 1 <= limit <= 3:
        raise ValueError("invalid original-case input or limit")
    groups = defaultdict(dict)
    for item in cases:
        if not isinstance(item, dict):
            continue
        original = _original(item.get("original_url"))
        upstream = _original(item.get("blocker_owner_url"))
        fingerprint = item.get("blocker_fingerprint")
        if (not original or not upstream or not isinstance(fingerprint, str)
                or len(fingerprint) < 8 or not item.get("original_owner")
                or item.get("blocker_resolved") is True):
            continue
        # One original case counted once, never duplicate by query/fragment.
        groups[(upstream, fingerprint)][original] = item
    ranked = sorted(
        ((key, unique) for key, unique in groups.items() if len(unique) >= 2),
        key=lambda entry: (-len(entry[1]), entry[0][0], entry[0][1]),
    )
    result = []
    for (upstream, fingerprint), unique in ranked[:limit]:
        result.append({
            "upstream_owner": "https://github.com/" + upstream,
            "blocker_fingerprint": fingerprint,
            "dependent_originals": ["https://github.com/" + name for name in sorted(unique)],
            "affected_original_count": len(unique),
            "suggested_action": "INSPECT_ORIGINAL_UPSTREAM_DEFECT_ONCE",
            "source_gates_verified": False,
            "autoroute_or_merge_allowed": False,
            "new_issue_or_pr_created": False,
        })
    return result
