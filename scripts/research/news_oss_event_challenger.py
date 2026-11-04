#!/usr/bin/env python3
"""Offline, deterministic news-event identity and source-independence challenger.

Research only. No network, no write side effects, no live signal or event admission.
Original implementation inspired by publicly documented event-family ideas from
MIT-licensed Horizon/AIHOT, not copied from their source code.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

VALID_PRECISION = {"TIMESTAMP", "DATE_ONLY", "ASSUMED_UTC_FROM_SOURCE"}
ADMISSIBLE_VERIFICATION = {"PRIMARY_SOURCE_VERIFIED", "STRONG_INDEPENDENT_VERIFIED"}
TRACKING_KEYS = {"fbclid", "gclid", "mc_cid", "mc_eid"}


def _normalise(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(re.findall(r"\w+", value.casefold(), flags=re.UNICODE))


def _instant(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None  # Never silently invent UTC.
    return parsed.astimezone(timezone.utc)


def canonical_article_url(value: object) -> str | None:
    """Conservative URL equality. Only well-known tracking params are dropped."""
    if not isinstance(value, str) or not value:
        return None
    try:
        p = urlsplit(value)
    except ValueError:
        return None
    if p.scheme not in {"https", "http"} or not p.hostname:
        return None
    host = p.hostname.casefold()
    try:
        port = p.port
    except ValueError:
        return None
    if port:
        default = (p.scheme == "http" and port == 80) or (p.scheme == "https" and port == 443)
        if not default:
            host += f":{port}"
    params = sorted(
        (k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
        if k.casefold() not in TRACKING_KEYS and not k.casefold().startswith("utm_")
    )
    path = p.path or "/"
    if path != "/":
        path = path.rstrip("/")
    return urlunsplit((p.scheme, host, path, urlencode(params), ""))


def relation(left: dict[str, Any], right: dict[str, Any]) -> dict[str, str]:
    """Return comparison evidence, never a permission to merge a canonical ledger."""
    a, b = canonical_article_url(left.get("url")), canonical_article_url(right.get("url"))
    if a and b and a == b:
        return {"relation": "SAME_ARTICLE", "reason": "identical_canonical_url"}

    # Roundups and incomplete frames must not bridge unrelated event families.
    if left.get("scope") != "SINGLE_EVENT" or right.get("scope") != "SINGLE_EVENT":
        return {"relation": "REVIEW_REQUIRED", "reason": "scope_unresolved_or_composite"}

    keys = ("actor", "target")
    for k in keys:
        if not _normalise(left.get(k)) or not _normalise(right.get(k)):
            return {"relation": "REVIEW_REQUIRED", "reason": f"missing_{k}"}
    if any(_normalise(left[k]) != _normalise(right[k]) for k in keys):
        return {"relation": "DIFFERENT_EVENT", "reason": "actor_or_target_differs"}

    act_a, act_b = _normalise(left.get("action")), _normalise(right.get("action"))
    if not act_a or not act_b:
        return {"relation": "REVIEW_REQUIRED", "reason": "action_unresolved"}
    if left.get("event_time_precision") != "TIMESTAMP" or right.get("event_time_precision") != "TIMESTAMP":
        return {"relation": "REVIEW_REQUIRED", "reason": "exact_occurrence_time_unavailable"}

    t1 = _instant(left.get("event_time_utc"))
    t2 = _instant(right.get("event_time_utc"))
    if not t1 or not t2:
        return {"relation": "REVIEW_REQUIRED", "reason": "invalid_event_timestamp"}

    hours = abs((t1 - t2).total_seconds()) / 3600
    if act_a == act_b and hours <= 1:
        return {"relation": "POSSIBLE_SAME_OCCURRENCE", "reason": "frame_and_time_match_review_only"}
    if act_a != act_b and hours <= 24 * 7:
        return {"relation": "RELATED_DEVELOPMENT", "reason": "same_entity_different_action"}
    return {"relation": "DIFFERENT_EVENT", "reason": "action_or_time_differs"}


def first_known_source_census(rows: list[dict[str, Any]], cutoff_utc: str) -> dict[str, Any]:
    """Count independently eligible source groups WITHOUT verifying claims ourselves.

    A publisher group is an externally sourced provenance identity. Two URLs or
    distinct domains are not proof of two independent original reporters. Missing
    provenance or times cannot receive PIT/source-diversity credit.
    """
    cutoff = _instant(cutoff_utc)
    if cutoff is None:
        raise ValueError("asof_requires_timezone_aware_datetime")
    admitted: dict[str, int] = {}
    rejected: dict[str, int] = {}
    for r in rows:
        kind = _normalise(r.get("source_role"))
        if kind not in {"primary", "publisher"}:
            reason = "non_verifying_source_role"
        elif r.get("verification_status") not in ADMISSIBLE_VERIFICATION:
            reason = "unverified_claim"
        elif not isinstance(r.get("independent_publisher_group"), str) or not r.get("independent_publisher_group").strip():
            reason = "publisher_independence_unknown"
        else:
            first_known = _instant(r.get("first_known_utc"))
            retrieved = _instant(r.get("retrieval_end_utc"))
            if first_known is None or retrieved is None:
                reason = "pit_clock_unknown"
            elif max(first_known, retrieved) > cutoff:
                reason = "post_cutoff_first_known"
            else:
                reason = ""
        if reason:
            rejected[reason] = rejected.get(reason, 0) + 1
            continue
        key = r["independent_publisher_group"].strip().casefold()
        admitted[key] = admitted.get(key, 0) + 1
    return {
        "authority": "SHADOW_COMPARISON_ONLY",
        "independent_eligible_groups": len(admitted),
        "eligible_reports": sum(admitted.values()),
        "same_publisher_repeats": sum(n - 1 for n in admitted.values()),
        "excluded_reports": sum(rejected.values()),
        "excluded_by_reason": dict(sorted(rejected.items())),
        "no_truth_or_compass_promotion": True,
    }
