#!/usr/bin/env python3
"""Kompas Task2 #1596: fail-closed shadow science, not forecasts or trades.

Risk evidence stays with original #1553. This cannot discover market events,
certify vendor first-known, change a risk policy or promote a challenger.
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from math import isfinite

CONTRACT = "TASK2_WAVE_B_SHADOW_SCIENCE_GATES_v1"
ALLOWED_MODELS = {"ORIGINAL", "B1", "PERSISTENCE", "MOMENTUM", "VOLATILITY"}


def utc(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("UTC_Z_TIMESTAMP_REQUIRED")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("INVALID_TIMESTAMP") from exc
    if dt.utcoffset() != timedelta(0):
        raise ValueError("UTC_TIMESTAMP_REQUIRED")
    return dt.astimezone(timezone.utc)


def _is_sha(value):
    return (isinstance(value, str) and len(value) == 40
            and all(c in "0123456789abcdef" for c in value))


def _finite_positive(value):
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not isfinite(value) or value <= 0):
        raise ValueError("INVALID_POSITIVE_PRICE")
    return float(value)


def _range(raw):
    lo = _finite_positive(raw["low"])
    hi = _finite_positive(raw["high"])
    if lo >= hi:
        raise ValueError("INVERTED_FORECAST_RANGE")
    return lo, hi


def score_weekly_pair(packet):
    """Descriptive paired extrema only; never a proper probability score.

    Caller must bind original source to Git objects and genuine provider-time
    evidence externally. Any unknown temporal/currency/coverage gate abstains.
    """
    asset = packet["asset"]
    week = packet["target_week"]
    if asset not in {"BTC", "ETH"} or not isinstance(week, str) or not week:
        raise ValueError("INVALID_ASSET_OR_WEEK")
    original = packet["original"]
    models = packet["models"]
    if (not isinstance(models, dict) or "ORIGINAL" not in models
            or set(models) - ALLOWED_MODELS):
        raise ValueError("INVALID_MODEL_SET")
    if not isinstance(original, dict):
        raise ValueError("MISSING_ORIGINAL_CUSTODY")
    issue = utc(original["issue_utc"])
    begin = utc(packet["target_start_utc"])
    end = utc(packet["target_end_utc"])
    if (issue >= end or end <= begin or end - begin != timedelta(days=7)
            or issue < begin - timedelta(days=1)
            or any(x.minute or x.second or x.microsecond for x in (begin, end))):
        raise ValueError("ORIGINAL_TARGET_CLOCK_INVALID")
    # Weekly original is often issued MONDAY AFTER the target week starts.
    # Score only completed hour-close outcomes STRICTLY AFTER issue,
    # never the hours before the genuine source freeze.
    first_eligible_close = max(
        begin + timedelta(hours=1),
        issue.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1),
    )
    if first_eligible_close > end:
        raise ValueError("NO_PROSPECTIVE_COMPLETE_HOUR")
    if not _is_sha(original.get("immutable_sha")):
        return {"status": "ORIGINAL_FREEZE_NOT_VERIFIED", "scores": {}, "contract": CONTRACT}
    if original.get("vendor_first_known_utc") is None:
        return {"status": "PIT_UNVERIFIED", "scores": {}, "contract": CONTRACT}
    if utc(original["vendor_first_known_utc"]) > issue:
        return {"status": "ORIGINAL_LOOKAHEAD", "scores": {}, "contract": CONTRACT}
    outcome = packet.get("outcome")
    if not outcome or utc(outcome["matured_at_utc"]) < end:
        return {"status": "NOT_MATURED", "scores": {}, "contract": CONTRACT}
    if original.get("quote") != outcome.get("quote") or original.get("quote") not in {"USD", "USDT"}:
        return {"status": "QUOTE_INCOMPARABLE", "scores": {}, "contract": CONTRACT}
    observed_low = _finite_positive(outcome["low"])
    observed_high = _finite_positive(outcome["high"])
    if observed_high < observed_low:
        raise ValueError("INVALID_OUTCOME_EXTREMA")
    anchor_meta = packet.get("anchor_source", {})
    if (not _is_sha(anchor_meta.get("immutable_sha"))
            or anchor_meta.get("quote") != original["quote"]
            or not anchor_meta.get("first_known_utc")
            or utc(anchor_meta["first_known_utc"]) > issue):
        return {"status": "ANCHOR_PIT_UNVERIFIED", "scores": {}, "contract": CONTRACT}
    observation_meta = outcome.get("source", {})
    expected_bars = int((end - first_eligible_close).total_seconds() // 3600) + 1
    if (not _is_sha(observation_meta.get("immutable_sha"))
            or observation_meta.get("closed_hour_count") != expected_bars
            or observation_meta.get("first_closed_utc") != first_eligible_close.strftime("%Y-%m-%dT%H:%M:%SZ")
            or observation_meta.get("last_closed_utc") != packet["target_end_utc"]):
        return {"status": "OUTCOME_COVERAGE_UNVERIFIED", "scores": {}, "contract": CONTRACT}
    anchor = _finite_positive(packet["preissue_anchor_price"])
    scores = {}
    for name, candidate in models.items():
        if candidate.get("quote") != original["quote"]:
            return {"status": "CHALLENGER_QUOTE_INCOMPARABLE", "scores": {}, "contract": CONTRACT}
        if not _is_sha(candidate.get("immutable_sha")):
            return {"status": "CHALLENGER_NOT_FROZEN", "scores": {}, "contract": CONTRACT}
        candidate_issue = utc(candidate["issue_utc"])
        if candidate_issue > issue or candidate_issue >= begin:
            return {"status": "CHALLENGER_ISSUED_TOO_LATE", "scores": {}, "contract": CONTRACT}
        first_known = candidate.get("vendor_first_known_utc")
        if first_known is None or utc(first_known) > candidate_issue:
            return {"status": "CHALLENGER_PIT_UNVERIFIED", "scores": {}, "contract": CONTRACT}
        lo, hi = _range(candidate)
        width = (hi - lo) / anchor
        misses = (max(0.0, lo - observed_low) + max(0.0, observed_high - hi)) / anchor
        overlap = max(0.0, min(hi, observed_high) - max(lo, observed_low))
        union = max(hi, observed_high) - min(lo, observed_low)
        scores[name] = {
            "joint_extrema_contained": lo <= observed_low and hi >= observed_high,
            "width_over_preissue_anchor": round(width, 8),
            "two_tail_miss_over_anchor": round(misses, 8),
            "overlap_over_union": round(overlap / union, 8),
            "probabilistic_interval_score": None,
        }
    return {
        "status": "DESCRIPTIVE_PAIRED_SCORE_ONLY", "scores": scores, "contract": CONTRACT,
        "independent_event_families": None, "statistical_edge_admitted": False,
        "production_model_change": False, "execution_or_investor_utility": False,
        "asset": asset, "target_week": week,
        "issue_utc": original["issue_utc"],
        "postfreeze_first_eligible_closed_hour_utc": first_eligible_close.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "postfreeze_eligible_completed_hours": expected_bars,
    }


def audit_pullback_episode(packet):
    """Require the original complete pre-anchor decision grid.

    Each accepted delivered pre-event 4/5+ warning has a legal source clock.
    Controls and pullbacks use the same clocks; 3/5 is never called 4/5.
    """
    kind = packet["kind"]
    if (kind not in {"PULLBACK", "CONTROL"} or not packet.get("episode_id")
            or not packet.get("family_id")):
        raise ValueError("INVALID_EPISODE_IDENTITY")
    anchor = utc(packet["anchor_utc"])
    slots = packet["slots"]
    if not isinstance(slots, list) or not slots:
        raise ValueError("MISSING_NO_WARNING_DENOMINATOR")
    expected = [anchor - timedelta(hours=n) for n in range(len(slots), 0, -1)]
    if [utc(s["decision_utc"]) for s in slots] != expected:
        raise ValueError("INCOMPLETE_OR_NONCONTIGUOUS_DECISION_GRID")
    allowed = {"RECORDED", "ABSTAIN", "NOT_ISSUED", "SOURCE_MISSING"}
    qualifying = []
    emitted = []
    uncertified = 0
    missing = 0
    risk3_count = 0
    for slot in slots:
        status = slot["status"]
        if status not in allowed:
            raise ValueError("INVALID_DECISION_STATUS")
        if status != "RECORDED":
            missing += 1
            if slot.get("severity") is not None or slot.get("delivered_utc") is not None:
                raise ValueError("NON_ISSUED_WARNING_FABRICATION")
            continue
        level = slot["severity"]
        if type(level) is not int or not 0 <= level <= 5:
            raise ValueError("INVALID_SEVERITY")
        issued = utc(slot["decision_utc"])
        first = slot.get("source_first_known_utc")
        if first is None or utc(first) > issued:
            uncertified += 1
            continue
        risk3_count += level == 3
        if level < 4:
            continue
        emitted.append(issued)
        delivery = slot.get("delivered_utc")
        if delivery is not None:
            delivery_clock = utc(delivery)
            if delivery_clock < issued:
                raise ValueError("DELIVERY_BEFORE_ISSUANCE")
            if delivery_clock < anchor:
                qualifying.append(delivery_clock)
    lead = (anchor - min(qualifying)).total_seconds() / 3600 if qualifying else None
    return {
        "contract": CONTRACT, "episode_id": packet["episode_id"],
        "family_id": packet["family_id"], "classification": "RETROSPECTIVE_DEVELOPMENT_ONLY",
        "kind": kind, "expected_decision_slots": len(slots),
        "explicit_non_recorded_slots": missing, "uncertified_recorded_slots": uncertified,
        "source_legal_risk3_slots": risk3_count, "issued_high_risk_slots": len(emitted),
        "pre_anchor_delivered_high_risk": bool(qualifying),
        "lead_hours_from_first_proven_delivery": lead,
        "pullback_without_delivered_high_risk": kind == "PULLBACK" and not qualifying,
        "control_with_delivered_high_risk": kind == "CONTROL" and bool(qualifying),
        "independent_shock_n": None, "risk_policy_change": False,
        "trading_or_exit_authority": False,
    }
