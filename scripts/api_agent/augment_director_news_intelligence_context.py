"""Read-only, fail-closed verified news context for the existing Daily Director.

News is context, never market-state, forecast-scoring, portfolio or execution
authority. The only producer remains the current Situation Room daily owner.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_OWNER_POINTER = Path("03_DAILY_CAPTURE_LOGS/catalyst_overlay/situation_room/LATEST.json")
AUTHORITY = "RESEARCH_ONLY_NON_CANONICAL"
CONTRACT = "DIRECTOR_NEWS_INTELLIGENCE_CONTEXT_v1"


def _instant(value):
    if not isinstance(value, str):
        return None
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return result.astimezone(timezone.utc) if result.tzinfo else None
    except (ValueError, OverflowError):
        return None


def _blocked(reason, *, status="UNAVAILABLE"):
    return {
        "contract": CONTRACT, "status": status, "reason": reason,
        "authority": AUTHORITY, "verified_count": 0, "verified_context": [],
        "event_fingerprint": None, "news_only_review_eligible": False,
        "canonical_effect": False, "market_state_effect": False,
        "portfolio_effect": False, "execution_authority": False,
    }


def news_intelligence(pointer_path=DEFAULT_OWNER_POINTER, *, now=None):
    """Return a bounded context and its exact source paths for provenance.

    Never infer zero events from a missing/failed source. Never use a historical
    event as a new event, and never read paths escaping the trusted owner root.
    """
    pointer_path = Path(pointer_path)
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("news_as_of_must_be_timezone_aware")
    now = now.astimezone(timezone.utc)
    if not pointer_path.is_file():
        return _blocked("NEWS_OWNER_POINTER_MISSING"), []
    try:
        pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
        key = pointer.get("path")
        if not isinstance(key, str) or not key:
            return _blocked("NEWS_OWNER_ROW_PATH_MISSING", status="BLOCKED_INVALID_POINTER"), [pointer_path]
        raw = Path(key)
        row_path = (raw if raw.is_absolute() else Path.cwd() / raw).resolve()
        if not row_path.is_relative_to(pointer_path.resolve().parent):
            return _blocked("NEWS_OWNER_ROW_OUTSIDE_OWNER_ROOT", status="BLOCKED_INVALID_POINTER"), [pointer_path]
        if not row_path.is_file():
            return _blocked("NEWS_OWNER_ROW_MISSING"), [pointer_path]
        raw_bytes = row_path.read_bytes()
        row = json.loads(raw_bytes)
    except (ValueError, OSError, TypeError, json.JSONDecodeError):
        return _blocked("NEWS_OWNER_READ_FAILED", status="BLOCKED_INVALID_POINTER"), [pointer_path]

    paths = [pointer_path, row_path]
    if (pointer.get("contract") != "SITUATION_ROOM_DAILY_OWNER_LATEST_POINTER_v1"
        or row.get("contract") != "SITUATION_ROOM_DAILY_OWNER_v1"
        or row.get("authority") != AUTHORITY
        or row.get("run_id") != pointer.get("run_id")
        or row.get("observation_date_utc") != pointer.get("observation_date_utc")
        or row.get("canonical_effect") is not False
        or row.get("market_state_effect") is not False
        or row.get("portfolio_effect") is not False):
        return _blocked("NEWS_OWNER_BINDING_OR_AUTHORITY_MISMATCH", status="BLOCKED_INVALID_OWNER"), paths

    detection = _instant(row.get("detection_time_utc"))
    if detection is None or detection > now:
        return _blocked("NEWS_OWNER_DETECTION_TIME_INVALID", status="BLOCKED_INVALID_OWNER"), paths
    age_hours = (now - detection).total_seconds() / 3600
    coverage = row.get("source_coverage") if isinstance(row.get("source_coverage"), dict) else {}
    receipts = coverage.get("receipts") if isinstance(coverage.get("receipts"), list) else []
    failed = sorted({str(x.get("source_id") or "UNKNOWN") for x in receipts
                     if isinstance(x, dict) and x.get("status") != "PASS"})
    primary_pass = coverage.get("primary_pass")
    primary_total = coverage.get("primary_total")
    healthy = (row.get("run_status") == "PASS" and not failed and
               isinstance(primary_pass, int) and primary_pass >= 3 and
               isinstance(primary_total, int) and primary_pass == primary_total)
    coverage_status = "PASS" if healthy else "DEGRADED"
    status = "STALE" if age_hours > 36 else ("READY" if healthy else "DEGRADED_SOURCE_COVERAGE")

    verified = []
    seen = set()
    for event in row.get("events", []):
        if not isinstance(event, dict) or event.get("verification_status") != "PRIMARY_SOURCE_VERIFIED":
            continue
        evidences = event.get("source_receipts")
        if not isinstance(evidences, list) or not any(
            isinstance(x, dict) and x.get("status") == "PASS" and x.get("role") == "PRIMARY"
            for x in evidences
        ):
            continue
        instant = _instant(event.get("event_time_utc"))
        if instant is None or instant > now:
            continue
        eid = event.get("event_id")
        family = event.get("event_family_id")
        url = next((x.get("url") for x in evidences if isinstance(x, dict) and
                    x.get("status") == "PASS" and x.get("role") == "PRIMARY"), None)
        if not isinstance(eid, str) or not eid or not isinstance(url, str) or not url:
            continue
        if eid in seen:
            continue
        seen.add(eid)
        verified.append({
            "event_id": eid, "event_family_id": family,
            "title": str(event.get("title") or "")[:300],
            "event_time_utc": event.get("event_time_utc"),
            "classification": event.get("classification"),
            "source_url": url, "verification_status": "PRIMARY_SOURCE_VERIFIED",
        })
    verified.sort(key=lambda x: (str(x["event_time_utc"]), x["event_id"]))
    fingerprint = (hashlib.sha256(json.dumps(sorted(x["event_id"] for x in verified),
                                   separators=(",", ":")).encode()).hexdigest()
                   if verified else None)
    eligible = bool(fingerprint and age_hours <= 24 and status != "STALE")
    return {
        "contract": CONTRACT, "status": status, "authority": AUTHORITY,
        "source_owner_status": row.get("run_status"),
        "source_daily_result": row.get("daily_result"),
        "source_run_id": row.get("run_id"),
        "source_row_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "observation_date_utc": row.get("observation_date_utc"),
        "detected_at_utc": row.get("detection_time_utc"),
        "source_age_hours": round(age_hours, 3),
        "source_coverage_status": coverage_status,
        "failed_sources": failed, "primary_pass": primary_pass, "primary_total": primary_total,
        "unverified_count": len(row.get("current_unverified_discoveries") or []),
        "verified_count": len(verified), "verified_context": verified[:12],
        "event_fingerprint": fingerprint,
        "news_only_review_eligible": eligible,
        "instruction": ("Use verified news only as source-attributed research context. "
                        "DEGRADED/STALE means unknown coverage, never no news. "
                        "Do not infer causal price attribution or change trading permissions."),
        "canonical_effect": False, "market_state_effect": False,
        "portfolio_effect": False, "execution_authority": False,
    }, paths
