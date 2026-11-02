"""Read-only S1 closure impact candidate metrics, not an evidence authority.

Never equate a scheduled run, issue comment, or green CI with a merge.
The caller must authenticate all claimed GitHub and task receipts independently.
"""
from datetime import datetime, timedelta, timezone
import re

_SHA = re.compile(r"^[0-9a-f]{40}$")


def _utc(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("UTC-Z timestamp required")
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError("invalid UTC calendar timestamp") from exc


def _sha(value):
    return isinstance(value, str) and _SHA.fullmatch(value) is not None


def closure_readout(records, as_of_utc, days=7):
    """Compute a deduplicated candidate denominator, not verified impact.

    Even a fully structured input requires external authentic GitHub proof.
    Emit caller-supplied candidate numbers only, never evidence-backed credit.
    """
    if not isinstance(records, list) or type(days) is not int or days not in (7, 28):
        raise ValueError("bounded records and fixed 7/28-day windows required")
    end = _utc(as_of_utc)
    start = end - timedelta(days=days)
    run_ids = set()
    merge_ids = set()
    candidate_merges = 0
    excluded = {"comment_only": 0, "other_actor": 0,
                "missing_main_readback": 0, "unqualified_merge_claim": 0}
    for row in records:
        if not isinstance(row, dict):
            raise ValueError("normalized receipt object required")
        event_time = _utc(row.get("observed_at_utc"))
        if not start <= event_time <= end:
            continue
        kind = row.get("kind")
        if kind == "S1_RUN":
            native_id = row.get("native_run_id")
            if isinstance(native_id, str) and native_id:
                run_ids.add(native_id)
            continue
        if kind != "MERGE":
            excluded["comment_only"] += 1
            continue
        if row.get("actual_actor") != "CHAT_S1":
            excluded["other_actor"] += 1
            continue
        fields = ("original_head", "merge_sha", "old_main_sha", "new_main_sha")
        if not all(_sha(row.get(f)) for f in fields):
            excluded["unqualified_merge_claim"] += 1
            continue
        if row.get("main_blob_readback") is not True:
            excluded["missing_main_readback"] += 1
            continue
        key = (row.get("repo"), row.get("pr"), row["merge_sha"])
        if key in merge_ids:
            continue
        if not isinstance(key[0], str) or type(key[1]) is not int:
            excluded["unqualified_merge_claim"] += 1
            continue
        merge_ids.add(key)
        candidate_merges += 1
    return {
        "contract": "S1_CLOSURE_CANDIDATE_IMPACT_v1",
        "window_days": days,
        "start_utc": start.isoformat().replace("+00:00", "Z"),
        "end_utc": end.isoformat().replace("+00:00", "Z"),
        "claimed_distinct_native_runs": len(run_ids),
        "claimed_s1_main_readback_merges": candidate_merges,
        "excluded": excluded,
        "externally_authenticated": False,
        "verified_production_impact": None,
        "success_rate": None,
        "notice": "CANDIDATES_ONLY_NATIVE_TASK_GITHUB_AND_PRODUCTION_VERIFICATION_REQUIRED",
    }
