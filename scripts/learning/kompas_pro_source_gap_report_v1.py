"""Read-only 14-horizon source-gap diagnostics for the EXISTING Kompas Pro.

No price model, source admission, provider-first-known assertion, new issuer,
market decision, action, schedule, API expense or historical rewriting.
Outputs reason codes and owners only. A plausible source-shaped row is NOT
independent proof of an issued numerical forecast.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
from typing import Any, Mapping

from scripts.learning.kompas_pro_horizon_readback_v2 import HORIZON_IDS

CONTRACT = "KOMPAS_PRO_SOURCE_GAP_REPORT_v1"
OFFICIAL = {"H1_3D": "NEXT_1_3D", "H5_7D": "NEXT_5_7D", "H2_3W": "NEXT_2_3W"}
VALID_DIRECTION = {"UP", "DOWN", "MIXED", "SIDEWAYS", "LEAN_BULLISH", "LEAN_BEARISH"}
OWNER_ISSUE = {
    "NOW": 1827, "H0_12H": 1827, "H24H": 1516, "H1_3D": 1516,
    "H5_7D": 1593, "H8_14D": 1516, "H15_21D": 1516, "H2_3W": 1516,
    "H21_30D": 1516, "H4_8W": 1516, "H1_3M": 1516,
    "H3_6M": 1516, "H6_9M": 1516, "H9_12M": 1516,
}


def utc(value: Any) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("EXACT_UTC_REQUIRED")
    try:
        d = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        raise ValueError("UTC_INVALID") from None
    if d.tzinfo is None:
        raise ValueError("UTC_INVALID")
    return d.astimezone(timezone.utc)


def _official_valid(pointer: Mapping, official: Mapping, now: datetime) -> bool:
    if (pointer.get("contract") != "OFFICIAL_DAILY_COMPASS_LATEST_POINTER_v1"
            or official.get("contract") != "OFFICIAL_DAILY_COMPASS_v1"
            or official.get("data_status") != "OK"
            or pointer.get("compass_id") != official.get("compass_id")
            or pointer.get("compass_sha256") != official.get("compass_sha256")
            or pointer.get("issued_at_utc") != official.get("issued_at_utc")):
        return False
    try:
        age = now - utc(official.get("issued_at_utc"))
    except ValueError:
        return False
    return timedelta(0) <= age <= timedelta(hours=3)


def _strategic_valid(pointer: Mapping, anchor: Mapping, now: datetime) -> bool:
    if (pointer.get("contract") != "STRATEGIC_COMPASS_LATEST_POINTER_v1"
            or anchor.get("contract") != "STRATEGIC_COMPASS_ANCHOR_v1"
            or pointer.get("anchor_id") != anchor.get("anchor_id")
            or pointer.get("anchor_sha256") != anchor.get("anchor_sha256")
            or pointer.get("issued_at_utc") != anchor.get("issued_at_utc")):
        return False
    try:
        age = now - utc(anchor.get("issued_at_utc"))
    except ValueError:
        return False
    return timedelta(0) <= age <= timedelta(days=8)


def build_report(
    ledger: Mapping, official_pointer: Mapping, official: Mapping,
    strategic_pointer: Mapping, strategic_anchor: Mapping, weekly_freeze: Mapping,
    *, as_of_utc: str,
) -> dict[str, Any]:
    """Describe actual current evidence availability without ever emitting a price.

    Freshness and matching internal identities are necessary but NOT sufficient
    proof of provider custody, independent issuance, scientific edge or delivery.
    The output is useful for gap-routing, not publication or portfolio actions.
    """
    now = utc(as_of_utc)
    horizon_rows = ledger.get("horizons") if isinstance(ledger, Mapping) else None
    if (not isinstance(ledger, Mapping) or ledger.get("contract") != "KOMPAS_PRO_INTERNAL_HORIZON_IMPLEMENTATION_LEDGER_v2"
            or not isinstance(horizon_rows, list)
            or [r.get("id") for r in horizon_rows] != list(HORIZON_IDS)):
        raise ValueError("CANONICAL_14_HORIZON_LEDGER_REQUIRED")
    if not all(isinstance(x, Mapping) for x in
               (official_pointer, official, strategic_pointer, strategic_anchor, weekly_freeze)):
        raise ValueError("SOURCE_OBJECT_REQUIRED")
    valid_official = _official_valid(official_pointer, official, now)
    valid_strategic = _strategic_valid(strategic_pointer, strategic_anchor, now)
    path = weekly_freeze.get("daily_price_path") or {}
    asset = path.get("BTC") or {}
    if not isinstance(asset, Mapping):
        asset = {}
    points = asset.get("points")
    seven_source_rows = (path.get("contract") == "CN_FROZEN_DAILY_PRICE_PATH_v1"
                         and isinstance(points, list) and len(points) == 7
                         and asset.get("status") == "PUBLISHED")
    rows = []
    for item in horizon_rows:
        h = item["id"]
        reason = ["NO_ADMITTED_ORIGINAL_NUMERIC_PRICE_ISSUE"]
        direction = "UNAVAILABLE"
        lane = "NONE"
        context = "UNAVAILABLE"
        if h in ("NOW", "H0_12H"):
            if valid_official and official.get("market_now", {}).get("directional_state") in ("BEARISH", "BULLISH", "NEUTRAL"):
                lane, context = "OFFICIAL_OBSERVATION", "OBSERVED_NOT_PREDICTIVE"
            else:
                reason.append("OFFICIAL_OBSERVATION_UNAVAILABLE_OR_EXPIRED")
            if h == "H0_12H":
                reason.append("TWELVE_HOUR_NOWCAST_IS_NOT_PROSPECTIVE_FORECAST")
        elif h in OFFICIAL:
            state = official.get("horizons", {}).get(OFFICIAL[h], {}) if valid_official else {}
            if state.get("expected_direction") in VALID_DIRECTION:
                direction, lane, context = state["expected_direction"], "OFFICIAL_DIRECTION", "QUALITATIVE_ONLY"
            else:
                reason.append("OFFICIAL_DIRECTION_UNAVAILABLE_OR_EXPIRED")
            if h == "H5_7D":
                # Original Monday W45 was 0/7. Seven syntactically present
                # rows still require original issuance/quote/clock attestation.
                if seven_source_rows:
                    reason.append("SEVEN_DAILY_ROWS_PRESENT_BUT_ISSUANCE_UNATTESTED")
                else:
                    reason.append("ORIGINAL_WEEKLY_SEVEN_DAY_PATH_MISSING")
                reason.append("WEEKLY_FORECAST_NOT_ROLLING_FIVE_TO_SEVEN_DAYS")
        elif h == "H21_30D":
            state = strategic_anchor.get("strategic_21_30d", {}) if valid_strategic else {}
            if state.get("btc_direction") in {"UP", "DOWN", "MIXED"}:
                direction, lane, context = state["btc_direction"], "STRATEGIC_CONTEXT", "NONBINDING_QUALITATIVE"
            else:
                reason.append("STRATEGIC_ANCHOR_MISSING_OR_NOT_CURRENT")
        elif h == "H4_8W":
            state = strategic_anchor.get("cycle_4_8w", {}) if valid_strategic else {}
            if state.get("direction") in {"UP", "DOWN", "MIXED"}:
                direction, lane, context = state["direction"], "CYCLE_CONTEXT", "NONBINDING_QUALITATIVE"
            else:
                reason.append("CYCLE_4_8W_DIRECTION_NOT_SUPPORTED")
        elif h in ("H8_14D", "H15_21D"):
            reason.append("FOURTEEN_TWENTYONE_DAY_PREFLIGHT_RESEARCH_ONLY")
            reason.append("SOURCE_ADMISSION_ORIGINAL_ISSUANCE_AND_MATURATION_NEEDED")
        elif h in ("H1_3M", "H3_6M", "H6_9M", "H9_12M"):
            reason.append("LONG_RANGE_SCENARIOS_NOT_ORIGINAL_ISSUED")
            reason.append("MULTIMONTH_MATURATION_AND_BASELINES_REQUIRED")
        else:
            reason.append("PROSPECTIVE_PRICE_ISSUER_NOT_CONNECTED")
        rows.append({
            "horizon_id": h, "source_context": context, "direction": direction,
            "direction_authority": lane, "price_status": "NOT_ADMITTED",
            "numeric_low": None, "numeric_expected": None, "numeric_high": None,
            "reason_codes": reason, "owner_issue": OWNER_ISSUE[h],
            "source_receipt_is_independent_proof": False,
        })
    return {
        "contract": CONTRACT, "as_of_utc": as_of_utc, "mode": "READ_ONLY_DIAGNOSTIC",
        "source_ids_consistent_and_current": {"official": valid_official, "strategic": valid_strategic},
        "weekly_source_row_count": 7 if seven_source_rows else 0,
        "week_is_not_a_rolling_forecast": True,
        "rows": rows, "automated_forecast_issued": False,
        "price_model_added": False, "source_admitted": False,
        "scientific_edge_proven": False, "portfolio_authority": False,
    }


def _load(root: Path, rel: str) -> dict:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="14-horizon source gaps, no forecast generation")
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--as-of-utc", required=True, help="Explicit readback UTC timestamp")
    args = parser.parse_args()
    root = args.repo.resolve()
    ledger = _load(root, "07_PROMPTS_AND_AGENTS/action_compass/KOMPAS_PRO_HORIZON_IMPLEMENTATION_LEDGER_v2.json")
    op = _load(root, "04_MARKET_LEARNING/handlekompas/official/LATEST_COMPASS.json")
    off = _load(root, op["compass_path"])
    sp = _load(root, "04_MARKET_LEARNING/handlekompas/strategic/LATEST_STRATEGIC_COMPASS.json")
    strategic = _load(root, sp["anchor_path"])
    # Follow existing current CN delivery pointer, never hardcode W45 or
    # synthesize last week from calendar time. Confine paths to weekly owner.
    wp = _load(root, "05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json")
    week_dir = wp.get("week_dir")
    if (wp.get("contract") != "CYCLE_NAVIGATOR_DELIVERY_POINTER_v1"
            or not isinstance(week_dir, str)
            or not re.fullmatch(r"05_CYCLE_NAVIGATOR/weekly/20[0-9]{2}/W[0-9]{2}", week_dir)):
        raise ValueError("WEEKLY_OWNER_POINTER_INVALID")
    weekly = _load(root, week_dir + "/CYCLE_NAVIGATOR_FORECAST_FREEZE.json")
    report = build_report(ledger, op, off, sp, strategic, weekly, as_of_utc=args.as_of_utc)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
