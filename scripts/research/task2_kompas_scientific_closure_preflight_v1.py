#!/usr/bin/env python3
"""Public-only, read-only Kompas/CN source-clock and W46 daily miss diagnostic.

Research (Task2 #1596), not an original issuer, precision scorer, trading or
risk-classification authority. Never infer provider first-known from build time.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

CONTRACT = "TASK2_KOMPAS_SCIENTIFIC_CLOSURE_PREFLIGHT_V1"


def utc(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("UTC_Z_TIMESTAMP_REQUIRED")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.utcoffset() != timedelta(0):
        raise ValueError("UTC_REQUIRED")
    return result.astimezone(timezone.utc)


def numeric(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if not (-float("inf") < float(value) < float("inf")):
        return None
    return float(value)


def examine(cn: dict[str, Any], compass: dict[str, Any]) -> dict[str, Any]:
    if cn.get("schema") != "CN_PUBLIC_SNAPSHOT_V2":
        raise ValueError("CN_PUBLIC_CONTRACT_MISMATCH")
    if compass.get("contract") != "PUBLIC_COMPASS_PROJECTION_v1":
        raise ValueError("PUBLIC_COMPASS_CONTRACT_MISMATCH")
    live = cn.get("public_live_precision") or {}
    if live.get("contract") != "CN_PUBLIC_LIVE_PRICE_PRECISION_v1":
        raise ValueError("CN_LIVE_PRECISION_CONTRACT_MISMATCH")
    issue = utc(live["frozen_at_utc"])
    observed_through = utc(live["live_as_of_utc"]) if live.get("live_as_of_utc") else None
    declared = (live.get("price_quote_labels") or {}).get("forecast_model_declared") or {}
    actual_quote = (live.get("price_quote_labels") or {}).get("actual_native_spot") or {}
    native_quote_comparable = all(
        actual_quote.get(asset) == declared.get(asset) == "USDT"
        for asset in ("BTC", "ETH")
    )
    source_claims_eligible = (live.get("price_quote_labels") or {}).get("comparison_precision_eligible") is True

    full = compass.get("full_stack") or {}
    owner = full.get("official_freshness") or {}
    official_issued = utc(compass["issued_at_utc"])
    valid_until = utc(owner["valid_until_utc"]) if owner.get("valid_until_utc") else None
    life_seconds = int((valid_until-official_issued).total_seconds()) if valid_until else None
    if life_seconds is None:
        clock_status = "EXPIRY_CLOCK_UNAVAILABLE"
    elif life_seconds <= 0:
        clock_status = "ISSUED_AT_OR_AFTER_EXPIRY"
    elif life_seconds < 900:
        clock_status = "SHORT_REMAINING_VALIDITY_UNDER_15M"
    else:
        clock_status = "POSITIVE_REMAINING_VALIDITY"

    score = cn.get("public_scorecard") or {}
    claims = score.get("frozen_claim_precision") or {}
    ranges = score.get("price_range_precision") or {}
    paths = live.get("daily_price_path") or {}
    observations = live.get("daily_observations") or {}
    days = []
    for asset in ("BTC", "ETH"):
        entries = ((paths.get(asset) or {}).get("points") or [])
        by_day = {x.get("day"): x for x in entries}
        for observed in observations.get(asset, []):
            day = observed.get("day")
            expected = by_day.get(day)
            if expected is None:
                raise ValueError("ISSUED_DAILY_POINT_MISSING:" + asset + ":" + str(day))
            status = observed.get("status")
            if status not in {"COMPLETE", "LIVE", "GAP", "NOT_STARTED"}:
                raise ValueError("UNKNOWN_OBSERVATION_STATUS")
            actual_low = numeric(observed.get("low"))
            actual_high = numeric(observed.get("high"))
            actual_close = numeric(observed.get("close"))
            forecast_low = numeric(expected.get("low"))
            forecast_high = numeric(expected.get("high"))
            forecast_close = numeric(expected.get("expected_close"))
            if any(x is None or x <= 0 for x in (forecast_low, forecast_high, forecast_close)):
                raise ValueError("INVALID_FROZEN_FORECAST_POINT")
            date = utc(observed["date"] + "T00:00:00Z")
            original_day_contaminated = date < issue < date + timedelta(days=1)
            has_values = (status in {"LIVE", "COMPLETE"} and
                          actual_low is not None and actual_high is not None and
                          actual_close is not None and
                          0 < actual_low <= actual_close <= actual_high)
            low_breach_pct = (
                round(100 * max(0.0, forecast_low - actual_low) / forecast_low, 4)
                if has_values else None
            )
            high_breach_pct = (
                round(100 * max(0.0, actual_high - forecast_high) / forecast_high, 4)
                if has_values else None
            )
            close_error_pct = (
                round(100 * (actual_close - forecast_close) / forecast_close, 4)
                if has_values else None
            )
            days.append({
                "asset": asset, "day": day, "date": observed["date"],
                "status": status,
                "contains_preissue_hours_possible": original_day_contaminated,
                "observed_hour_count": observed.get("observed_hours"),
                "observed_at_utc": observed.get("as_of_utc"),
                "frozen_low": forecast_low, "frozen_high": forecast_high,
                "frozen_expected_close": forecast_close,
                "observed_low": actual_low if has_values else None,
                "observed_high": actual_high if has_values else None,
                "observed_close": actual_close if has_values else None,
                "low_breach_pct": low_breach_pct,
                "high_breach_pct": high_breach_pct,
                "close_error_pct": close_error_pct,
                "interpretation": ("PROVISIONAL_INTRADAY" if status == "LIVE"
                                   else "COMPLETED_CALENDAR_DAY_NOT_PIT_ADMITTED"
                                   if status == "COMPLETE" else "ABSTAIN"),
                "scientific_score_admitted": False,
            })
    return {
        "contract": CONTRACT, "authority": "PUBLIC_RESEARCH_DIAGNOSTIC_ONLY",
        "forecast_week": live.get("forecast_week"),
        "public_issue_number": live.get("public_issue_number"),
        "forecast_issued_at_utc": live["frozen_at_utc"],
        "observed_through_utc": observed_through.isoformat().replace("+00:00", "Z") if observed_through else None,
        "official": {
            "compass_id": compass.get("compass_id"),
            "issued_at_utc": compass.get("issued_at_utc"),
            "valid_until_utc": owner.get("valid_until_utc"),
            "remaining_validity_at_issue_seconds": life_seconds,
            "clock_status": clock_status,
            "native_data_health": (compass.get("public_data_health") or {}).get("native_data_health"),
            "first_provider_published_at": (compass.get("original_source_age_at_issue") or {}).get("provider_first_published_at_utc"),
            "first_user_delivered_at": (compass.get("original_source_age_at_issue") or {}).get("first_investor_delivery_at_utc"),
        },
        "source_comparison": {
            "same_native_and_declared_usdt": native_quote_comparable,
            "upstream_comparison_precision_eligible": source_claims_eligible,
            "scientific_pit_admitted": False,
        },
        "score_families_kept_separate": {
            "range_score": ranges.get("score"),
            "frozen_claim_score": claims.get("score"),
            "frozen_claim_scored_parameters": claims.get("scored_parameter_count"),
            "frozen_claim_coverage_pct": claims.get("parameter_coverage_pct"),
            "combined_accuracy": None,
        },
        "daily_diagnostics": days,
        "edge_proven": False,
        "action_authority": False,
        "notes": [
            "Calendar-day observations may include pre-issuance hours on the issuance Monday.",
            "Completed calendar day is not first-known/provider-PIT admission.",
            "Never score live/partial days as final, never relabel quote comparability as scientific eligibility.",
            "No portfolio or source threshold change; no new original forecast.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cn-public", type=Path, required=True)
    parser.add_argument("--compass-public", type=Path, required=True)
    args = parser.parse_args()
    cn = json.loads(args.cn_public.read_text(encoding="utf-8"))
    compass = json.loads(args.compass_public.read_text(encoding="utf-8"))
    print(json.dumps(examine(cn, compass), sort_keys=True, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
