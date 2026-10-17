"""Deterministic public-safe weekly SHADOW handoff to existing research owners.

Reads only existing public Archive pointers. Does NOT scan, price, backtest,
dispatch models, access secrets, place paper/live orders, or promote signals.
Data from private repos require a separately accepted value-free receipt.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

CONTRACT = "SHADOW_CROSS_DOMAIN_WEEKLY_REVIEW_v1"
AUTHORITY = "RESEARCH_ONLY_NON_CANONICAL"
# Explicit allowlist; never follow path strings found in untrusted JSON.
PUBLIC_SOURCES = {
    "COMPASS": (
        ("04_MARKET_LEARNING/handlekompas/shadow_v2/LATEST.json",
         "SHADOW_COMPASS_V2_LATEST_POINTER_v1"),
        ("research/framework_memory/action_compass_calibration/LATEST_EXIT_WARNING_CALIBRATION.json",
         "ACTION_COMPASS_PROTECTION_CALIBRATION_v2"),
        ("research/framework_memory/edge_compound_governor/LATEST.json",
         "EDGE_COMPOUND_GOVERNOR_v1"),
    ),
    "AUTO_TRADING": (
        ("research/experiment_lifecycle/weekly_adjudication/LATEST.json",
         "UNIFIED_EXPERIMENTAL_LIFECYCLE_ADJUDICATION_v1"),
        ("research/experiment_lifecycle/SEQUENTIAL_RESEARCH_QUEUE_v1.json",
         "SEQUENTIAL_RESEARCH_QUEUE_v1"),
    ),
}
LANE_IDS = ("COMPASS", "AUTO_TRADING", "ALPHA_LAB")
MAX_SOURCE_BYTES = 1_000_000
MAX_SOURCE_AGE_DAYS = 8
DETERMINISTIC_ONLY = {
    "external_llm_calls": 0,
    "incremental_paid_api_usd": 0,
    "incremental_provider_calls": 0,
    "new_schedulers": 0,
    "automatic_execution": False,
    "automatic_market_rule_change": False,
    "automatic_model_promotion": False,
    "wallet_signing": False,
}


def _clock(value):
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.astimezone(timezone.utc) if parsed.utcoffset() is not None else None
    except (ValueError, OverflowError):
        return None


def _no_nan(value):
    raise ValueError("nonfinite JSON")


def _read(root: Path, rel: str, expected: str, now: datetime):
    out = {
        "path": rel, "expected_contract": expected,
        "sha256": None, "source_status": "MISSING",
        "source_at_utc": None,
    }
    p = root / rel
    try:
        if not p.is_file() or not p.resolve().is_relative_to(root.resolve()):
            return out, None
        raw = p.read_bytes()
        if len(raw) > MAX_SOURCE_BYTES:
            out["source_status"] = "SOURCE_TOO_LARGE"
            return out, None
        out["sha256"] = hashlib.sha256(raw).hexdigest()
        data = json.loads(raw, parse_constant=_no_nan)
        if not isinstance(data, dict) or data.get("contract") != expected:
            out["source_status"] = "CONTRACT_MISMATCH"
            return out, None
        authority = data.get("authority")
        if isinstance(authority, dict):
            if any(authority.get(k) is True for k in
                   ("portfolio_execution", "automatic_promotion", "canonical_promotion",
                    "market_state_change", "sell", "trim")):
                out["source_status"] = "AUTHORITY_CONFLICT"
                return out, None
        elif authority not in (None, AUTHORITY, "RESEARCH_ONLY_NO_PORTFOLIO_OR_PRODUCTION_AUTHORITY"):
            out["source_status"] = "AUTHORITY_CONFLICT"
            return out, None
        for key in ("portfolio_execution", "automatic_market_rule_change",
                    "automatic_promotion", "canonical_effect"):
            if data.get(key) is True:
                out["source_status"] = "AUTHORITY_CONFLICT"
                return out, None
        stamp = data.get("generated_at_utc") or data.get("issued_at_utc")
        if stamp is None:
            out["source_status"] = "VALID_UNDATED_POLICY"
            return out, data
        dt = _clock(stamp)
        if dt is None:
            out["source_status"] = "INVALID_SOURCE_CLOCK"
            return out, None
        out["source_at_utc"] = dt.isoformat().replace("+00:00", "Z")
        delta = (now - dt).total_seconds()
        if delta < -300:
            out["source_status"] = "FUTURE_SOURCE_CLOCK"
            return out, None
        if delta > MAX_SOURCE_AGE_DAYS * 86400:
            out["source_status"] = "STALE"
            return out, None
        out["source_status"] = "CURRENT_CONTRACT_VALID"
        return out, data
    except (OSError, UnicodeError, ValueError, TypeError):
        out["source_status"] = "UNREADABLE_OR_INVALID_JSON"
        return out, None


def _nonnegative_int(value):
    return value if type(value) is int and value >= 0 else None


def build(root: Path, now: datetime) -> dict:
    if now.utcoffset() is None:
        raise ValueError("timezone-aware UTC required")
    now = now.astimezone(timezone.utc)
    week = now.strftime("%G-W%V")
    lanes = []
    for lane_id in ("COMPASS", "AUTO_TRADING"):
        evidence, admitted = [], {}
        for rel, contract in PUBLIC_SOURCES[lane_id]:
            source, data = _read(root, rel, contract, now)
            evidence.append(source)
            if data is not None and source["source_status"] in (
                "CURRENT_CONTRACT_VALID", "VALID_UNDATED_POLICY"
            ):
                admitted[contract] = data
        source_ok = all(e["source_status"] in (
            "CURRENT_CONTRACT_VALID", "VALID_UNDATED_POLICY"
        ) for e in evidence)
        if lane_id == "COMPASS":
            calibration = admitted.get("ACTION_COMPASS_PROTECTION_CALIBRATION_v2", {})
            governor = admitted.get("EDGE_COMPOUND_GOVERNOR_v1", {})
            semantic = governor.get("semantic_state") or {}
            metrics = {
                "calibration_eligible_rows_not_independent_forecasts":
                    _nonnegative_int(calibration.get("eligible_series_row_count")),
                "calibration_warning_rows_not_proven_alerts":
                    _nonnegative_int(calibration.get("warning_series_row_count")),
                "economic_action_edge": (
                    "NOT_ESTABLISHED" if semantic.get("economic_action_edge_claim") ==
                    "NOT_ESTABLISHED" else "UNKNOWN_OR_UNADMITTED"
                ),
                "qualified_buy_sell_net_return": None,
            }
            review = "WATCH_MATURATION_AND_DELIVERED_AFTER_COST_OUTCOMES"
            owner = "Official Compass / EDGE #1530 / risk-to-action #1553"
        else:
            adjudication = admitted.get("UNIFIED_EXPERIMENTAL_LIFECYCLE_ADJUDICATION_v1", {})
            queue = admitted.get("SEQUENTIAL_RESEARCH_QUEUE_v1", {})
            count = (adjudication.get("summary") or {}).get("candidate_count")
            # Candidate count is emphatically NOT the proposal-time trial denominator.
            metrics = {
                "research_candidate_count_NOT_GLOBAL_TRIAL_DENOMINATOR":
                    _nonnegative_int(count),
                "global_proposal_time_trial_denominator": None,
                "verified_paper_trade_net_return": None,
                "research_queue_shadow_only": queue.get("status") == "ACTIVE_SHADOW_ONLY"
                if queue else None,
            }
            review = "REPAIR_GLOBAL_TRIAL_DENOMINATOR_BEFORE_BROAD_SEARCH"
            owner = "AUTO_TRADING #1557 / Experiment Lifecycle"
        lanes.append({
            "lane_id": lane_id,
            "owner": owner,
            "source_status": "SOURCE_OBSERVED" if source_ok else "SOURCE_INCOMPLETE",
            "scientific_edge": "UNPROVEN",
            "review_question": review,
            "metrics": metrics,
            "public_source_evidence": evidence,
            "independent_review_complete": False,
            "paper_or_live_trading_authorized": False,
        })
    lanes.append({
        "lane_id": "ALPHA_LAB",
        "owner": "Meme-Alpha-Lab domain owners / Archive #1340",
        "source_status": "PRIVATE_REPO_SOURCE_NOT_IMPORTED",
        "scientific_edge": "UNPROVEN",
        "review_question": "AWAIT_AUTHENTICATED_PUBLIC_SAFE_CROSS_REPO_OWNER_RECEIPT",
        "metrics": {
            "prospective_tradable_edge": None,
            "private_wallet_data_ingested": False,
        },
        "public_source_evidence": [],
        "independent_review_complete": False,
        "paper_or_live_trading_authorized": False,
    })
    out = {
        "contract": CONTRACT,
        "week": week,
        "generated_at_utc": now.isoformat().replace("+00:00", "Z"),
        "authority": AUTHORITY,
        "lanes": lanes,
        "summary": {
            "lane_count": len(lanes),
            "qualified_live_trading_strategies": 0,
            "profitability_claim": "NONE_VERIFIED",
            "supervisor_advisory_only": True,
            "private_source_boundaries_preserved": True,
            "no_promotion_without_independent_review": True,
        },
        "cost_and_execution": dict(DETERMINISTIC_ONLY),
        "anti_double_counting": "SHARED_MARKET_OUTCOMES_AND_CROSS_REPO_DERIVATIVES_ARE_NOT_INDEPENDENT_TRIALS",
    }
    validate(out)
    return out


def validate(review: dict) -> bool:
    if not isinstance(review, dict) or review.get("contract") != CONTRACT:
        raise ValueError("cross-domain contract invalid")
    if review.get("authority") != AUTHORITY or not _clock(review.get("generated_at_utc")):
        raise ValueError("cross-domain authority/clock invalid")
    if review.get("week") != _clock(review["generated_at_utc"]).strftime("%G-W%V"):
        raise ValueError("cross-domain ISO week invalid")
    if review.get("cost_and_execution") != DETERMINISTIC_ONLY:
        raise ValueError("cross-domain spend/execution ceiling violated")
    summary = review.get("summary", {})
    if not isinstance(summary, dict) or summary.get("lane_count") != 3:
        raise ValueError("cross-domain summary invalid")
    if (summary.get("qualified_live_trading_strategies") != 0 or
        summary.get("profitability_claim") != "NONE_VERIFIED" or
        summary.get("supervisor_advisory_only") is not True or
        summary.get("private_source_boundaries_preserved") is not True or
        summary.get("no_promotion_without_independent_review") is not True):
        raise ValueError("cross-domain scientific firewalls invalid")
    lanes = review.get("lanes")
    if not isinstance(lanes, list) or [x.get("lane_id") for x in lanes if isinstance(x, dict)] != list(LANE_IDS):
        raise ValueError("cross-domain lane ownership invalid")
    for lane in lanes:
        if lane.get("scientific_edge") != "UNPROVEN" or lane.get("paper_or_live_trading_authorized") is not False:
            raise ValueError("cross-domain trading edge/authority leak")
        if lane.get("independent_review_complete") is not False:
            raise ValueError("cross-domain forged independent acceptance")
        if lane.get("source_status") not in (
            "SOURCE_OBSERVED", "SOURCE_INCOMPLETE", "PRIVATE_REPO_SOURCE_NOT_IMPORTED"
        ):
            raise ValueError("cross-domain evidence state invalid")
        evidence = lane.get("public_source_evidence")
        expected = PUBLIC_SOURCES.get(lane["lane_id"], ())
        if not isinstance(evidence, list) or len(evidence) != len(expected):
            raise ValueError("cross-domain evidence count invalid")
        for entry, (path, contract) in zip(evidence, expected):
            if entry.get("path") != path or entry.get("expected_contract") != contract:
                raise ValueError("cross-domain unapproved source path")
            if entry.get("sha256") is not None and (
                not isinstance(entry["sha256"], str) or len(entry["sha256"]) != 64 or
                any(c not in "0123456789abcdef" for c in entry["sha256"])
            ):
                raise ValueError("cross-domain invalid source digest")
        metrics = lane.get("metrics")
        if not isinstance(metrics, dict):
            raise ValueError("cross-domain metrics invalid")
        if lane["lane_id"] == "COMPASS":
            if metrics.get("qualified_buy_sell_net_return") is not None:
                raise ValueError("no verified executable Compass ROI source")
            for k in ("calibration_eligible_rows_not_independent_forecasts",
                      "calibration_warning_rows_not_proven_alerts"):
                if metrics.get(k) is not None and _nonnegative_int(metrics[k]) is None:
                    raise ValueError("calibration count invalid")
        if lane["lane_id"] == "AUTO_TRADING":
            if metrics.get("global_proposal_time_trial_denominator") is not None or (
                metrics.get("verified_paper_trade_net_return") is not None
            ):
                raise ValueError("auto trading evidence not independently admitted")
            count = metrics.get("research_candidate_count_NOT_GLOBAL_TRIAL_DENOMINATOR")
            if count is not None and _nonnegative_int(count) is None:
                raise ValueError("experimental candidate count invalid")
        if lane["lane_id"] == "ALPHA_LAB":
            if lane["source_status"] != "PRIVATE_REPO_SOURCE_NOT_IMPORTED":
                raise ValueError("private data boundary invalid")
            if lane["metrics"].get("private_wallet_data_ingested") is not False:
                raise ValueError("private wallet data leak")
    return True
