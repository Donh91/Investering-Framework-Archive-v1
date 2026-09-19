#!/usr/bin/env python3
"""Event-driven Compass refresh admission.

This watcher does not create a forecast or trading signal. It decides whether
new canonical owner evidence is material enough to request a fresh Official
Compass between the two scheduled daily freezes.

Materiality reuses existing framework semantics:
- a change in accepted Compass action / directional state / capitalization ladder,
- a change in fail-closed data health,
- Entry Signal's existing HOT classification,
- a symmetric downside reuse of the same registered HOT magnitudes, for
  reassessment only (never as a buy/sell threshold).

A heat episode triggers once, then rearms after NORMAL. Action/health/ladder
changes are not suppressed by the heat episode. Same-source dispatches are
deduplicated. If required owner freshness is stale, this watcher requests a
fresh Hourly Sequence first and defers Compass materiality until the canonical
owner chain has rebuilt from fresh evidence.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
from typing import Any, Mapping

SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SCRIPTS_ROOT.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.data_ping import native_handlekompas as nh

AUTO_POINTER = Path("04_MARKET_LEARNING/entry_signals/auto_market_state/LATEST.json")
COMPASS_POINTER = Path("04_MARKET_LEARNING/handlekompas/official/LATEST_COMPASS.json")
ENTRY_LATEST = Path("04_MARKET_LEARNING/entry_signals/LATEST.json")
DEFAULT_ROOT = Path("04_MARKET_LEARNING/handlekompas/event_refresh")
CONTRACT = "COMPASS_EVENT_REFRESH_DECISION_v1"
PUBLIC_CONTRACT = "PUBLIC_COMPASS_EVENT_STATUS_v1"
STATE_CONTRACT = "COMPASS_EVENT_REFRESH_STATE_v1"
REQUEST_RETRY_SECONDS = 20 * 60
NON_PROTECTIVE_COOLDOWN_SECONDS = 3 * 60 * 60
SCHEDULE_PROXIMITY_SECONDS = 30 * 60
ACTION_RANK = {
    "HOLD_WAIT_DATA_DEGRADED": 0,
    "HOLD_DEFENSIVE_WAIT": 1,
    "HOLD_WAIT": 2,
    "PREPARE": 3,
    "GRADUATED_TOPUP_ACTIVE": 4,
}
LADDER_RANK = {"UNAVAILABLE": -1, "HARD_WAIT": 0, "WAIT": 1, "HOLD": 2, "PREPARE": 3, "DEPLOY": 4}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def parse_utc(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.utcoffset() is None:
        return None
    return dt.astimezone(timezone.utc)


def finite(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    out = float(value)
    return out if out == out and out not in (float("inf"), float("-inf")) else None


def heat_state(entry: Mapping[str, Any]) -> tuple[str, dict[str, Any]]:
    snap = entry.get("market_snapshot") if isinstance(entry.get("market_snapshot"), Mapping) else {}
    btc = finite(snap.get("btc_return_24h_pct"))
    eth = finite(snap.get("eth_return_24h_pct"))
    median = finite(snap.get("median_return_24h_pct"))
    existing_hot = str(entry.get("execution_temperature") or "NORMAL") == "HOT"

    # Existing owner magnitudes are +8% BTC, +12% ETH, +4% median Top-100.
    # Downside uses the same magnitudes symmetrically for refresh admission only.
    downside_hot = (
        (btc is not None and btc <= -8.0)
        or (eth is not None and eth <= -12.0)
        or (median is not None and median <= -4.0)
    )
    if downside_hot:
        state = "HOT_DOWNSIDE_REASSESSMENT"
    elif existing_hot:
        state = "HOT_UPSIDE_REASSESSMENT"
    else:
        state = "NORMAL"
    return state, {
        "btc_return_24h_pct": btc,
        "eth_return_24h_pct": eth,
        "median_return_24h_pct": median,
        "existing_entry_temperature": entry.get("execution_temperature"),
        "downside_semantics": "SYMMETRIC_REUSE_OF_EXISTING_HEAT_MAGNITUDES_EVENT_ONLY",
    }


def _ladder_status(rows: Any) -> list[tuple[str, str]]:
    if not isinstance(rows, list):
        return []
    out: list[tuple[str, str]] = []
    for row in rows:
        if isinstance(row, Mapping):
            out.append((str(row.get("segment") or ""), str(row.get("status") or "")))
    return out


def _age_seconds(now: datetime, value: Any) -> float | None:
    dt = parse_utc(value)
    if dt is None:
        return None
    age = (now - dt).total_seconds()
    return age if age >= 0 else None


def _ladder_more_defensive(previous: Any, current: Any) -> bool:
    prev = dict(_ladder_status(previous))
    cur = dict(_ladder_status(current))
    for segment, current_status in cur.items():
        previous_status = prev.get(segment)
        if previous_status is None:
            continue
        if LADDER_RANK.get(current_status, 0) < LADDER_RANK.get(previous_status, 0):
            return True
    return False


def _seconds_to_next_scheduled_compass(now: datetime) -> float:
    cph = ZoneInfo("Europe/Copenhagen")
    local = now.astimezone(cph)
    candidates = [
        local.replace(hour=8, minute=17, second=0, microsecond=0),
        local.replace(hour=20, minute=17, second=0, microsecond=0),
    ]
    for candidate in candidates:
        if candidate >= local:
            return (candidate - local).total_seconds()
    tomorrow = (local + timedelta(days=1)).replace(hour=8, minute=17, second=0, microsecond=0)
    return (tomorrow - local).total_seconds()


def _protective_transition(
    *, latest_compass: Mapping[str, Any], current_data_status: str,
    current_action: str, current_market: Mapping[str, Any], current_ladder: Any,
    heat: str,
) -> bool:
    previous_status = str(latest_compass.get("data_status") or "")
    if previous_status != current_data_status:
        return True
    previous_action = str(latest_compass.get("action_now") or "")
    if ACTION_RANK.get(current_action, 0) < ACTION_RANK.get(previous_action, 0):
        return True
    previous_market = latest_compass.get("market_now") if isinstance(latest_compass.get("market_now"), Mapping) else {}
    if str(current_market.get("directional_state") or "") == "BEARISH" and str(previous_market.get("directional_state") or "") != "BEARISH":
        return True
    if _ladder_more_defensive(latest_compass.get("capitalization_ladder"), current_ladder):
        return True
    if heat == "HOT_DOWNSIDE_REASSESSMENT":
        return True
    return False


def evaluate(
    *,
    auto_state: Mapping[str, Any],
    auto_pointer: Mapping[str, Any],
    latest_compass: Mapping[str, Any],
    entry_latest: Mapping[str, Any],
    prior_state: Mapping[str, Any] | None,
    cn_package: Mapping[str, Any] | None,
    cn_binding: Mapping[str, Any] | None,
    now: datetime,
) -> dict[str, Any]:
    prior_state = prior_state or {}
    source_sha = str(auto_pointer.get("packet_sha256") or auto_state.get("packet_sha256") or "")
    compass_source_sha = str(
        nh.nested(latest_compass, "source_bindings", "auto_market_state", "packet_sha256") or ""
    )
    heat, heat_detail = heat_state(entry_latest)

    if not source_sha:
        return {
            "contract": CONTRACT,
            "evaluated_at_utc": nh.iso(now) if hasattr(nh, "iso") else now.isoformat().replace("+00:00", "Z"),
            "dispatch": False,
            "upstream_refresh_required": False,
            "reason": "AUTO_STATE_SOURCE_SHA_MISSING",
            "heat_state": heat,
            "heat_detail": heat_detail,
        }

    owner_freshness = nh.owner_freshness(auto_state, now)
    if str(owner_freshness.get("status") or "") != "PASS":
        return {
            "contract": CONTRACT,
            "evaluated_at_utc": now.isoformat().replace("+00:00", "Z"),
            "dispatch": False,
            "upstream_refresh_required": True,
            "reason": "UPSTREAM_OWNER_FRESHNESS_STALE",
            "source_packet_sha256": source_sha,
            "latest_compass_source_packet_sha256": compass_source_sha or None,
            "owner_freshness_status": owner_freshness.get("status"),
            "owner_freshness_reasons": list(owner_freshness.get("reasons") or []),
            "heat_state": heat,
            "heat_detail": heat_detail,
            "authority": {
                "portfolio_execution": False,
                "forecast_change": False,
                "market_threshold_change": False,
                "purpose": "REQUEST_FRESH_OWNER_EVIDENCE_BEFORE_COMPASS_REASSESSMENT",
            },
        }

    if source_sha == compass_source_sha:
        return {
            "contract": CONTRACT,
            "evaluated_at_utc": now.isoformat().replace("+00:00", "Z"),
            "dispatch": False,
            "upstream_refresh_required": False,
            "reason": "LATEST_COMPASS_ALREADY_BINDS_CURRENT_OWNER_PACKET",
            "source_packet_sha256": source_sha,
            "heat_state": heat,
            "heat_detail": heat_detail,
        }

    last_request_at = prior_state.get("last_request_at_utc") or prior_state.get("last_dispatch_at_utc")
    last_request_age = _age_seconds(now, last_request_at)
    last_requested_source = str(
        prior_state.get("last_requested_source_sha")
        or prior_state.get("last_dispatched_source_sha")
        or ""
    )
    latest_issued = parse_utc(latest_compass.get("issued_at_utc"))
    request_unbound = bool(
        last_request_age is not None
        and (latest_issued is None or latest_issued < parse_utc(last_request_at))
        and source_sha != compass_source_sha
    )
    request_in_flight = bool(request_unbound and last_request_age < REQUEST_RETRY_SECONDS)
    request_retry_due = bool(request_unbound and last_request_age >= REQUEST_RETRY_SECONDS)

    cn_ok = isinstance(cn_package, Mapping) and str((cn_binding or {}).get("status") or "") == "PASS"
    owner_ok = nh._health_ok(auto_state, now)
    current_data_status = "OK" if owner_ok and cn_ok else "DEGRADED"
    action = nh.action_context(auto_state, as_of=now)
    market = nh.derive_market_now(auto_state, action, as_of=now)
    ladder = nh.capitalization_ladder(auto_state, action, market, as_of=now)
    protection = nh.protection_tracker(
        auto_state, action, market, cn_package, as_of=now, prior_compass=latest_compass
    )

    causes: list[str] = []
    if str(latest_compass.get("data_status") or "") != current_data_status:
        causes.append("DATA_HEALTH_CHANGED")
    if str(latest_compass.get("action_now") or "") != str(action.get("NOW") or ""):
        causes.append("ACTION_STATE_CHANGED")

    prior_market = latest_compass.get("market_now") if isinstance(latest_compass.get("market_now"), Mapping) else {}
    if (
        str(prior_market.get("directional_state") or "") != str(market.get("directional_state") or "")
        or str(prior_market.get("regime") or "") != str(market.get("regime") or "")
    ):
        causes.append("MARKET_STATE_CHANGED")

    if _ladder_status(latest_compass.get("capitalization_ladder")) != _ladder_status(ladder):
        causes.append("CAPITALIZATION_LADDER_CHANGED")

    previous_protection = latest_compass.get("protection_tracker")
    if isinstance(previous_protection, Mapping):
        protection_keys = (
            "pullback_risk_state", "pullback_class", "distribution_risk",
            "eta_window", "confidence_quality", "reentry_state",
        )
        if tuple(previous_protection.get(k) for k in protection_keys) != tuple(protection.get(k) for k in protection_keys):
            causes.append("PROTECTION_STATE_CHANGED")
        if (
            str(protection.get("reentry_state") or "") == "REVIEW"
            and str(previous_protection.get("reentry_state") or "") != "REVIEW"
        ):
            causes.append("REENTRY_REVIEW_OPENED")

    last_heat = str(prior_state.get("last_heat_state") or "NORMAL")
    # Heat is a refresh accelerator only when the current owner evidence is
    # decision-eligible. Stale/degraded evidence must never manufacture a
    # "market move" event; health transitions are handled separately above.
    if current_data_status == "OK" and heat != "NORMAL" and heat != last_heat:
        causes.append("MARKET_HEAT_ENTERED")

    if request_retry_due and causes:
        causes.insert(0, "PRIOR_REQUEST_NOT_BOUND_RETRY")

    current_action = str(action.get("NOW") or "")
    protective = _protective_transition(
        latest_compass=latest_compass,
        current_data_status=current_data_status,
        current_action=current_action,
        current_market=market,
        current_ladder=ladder,
        heat=heat,
    )
    if isinstance(previous_protection, Mapping):
        old_risk = str(previous_protection.get("pullback_risk_state") or "NORMAL")
        new_risk = str(protection.get("pullback_risk_state") or "NORMAL")
        if nh.PROTECTION_RANK.get(new_risk, -1) > nh.PROTECTION_RANK.get(old_risk, -1):
            protective = True
        old_dist = str(previous_protection.get("distribution_risk") or "NONE")
        new_dist = str(protection.get("distribution_risk") or "NONE")
        dist_rank = {"NONE": 0, "WARNING": 1, "CONFIRMED": 2, "UNKNOWN": -1}
        if dist_rank.get(new_dist, -1) > dist_rank.get(old_dist, -1):
            protective = True
    cooldown_age = last_request_age
    suppressed: list[str] = []
    reason = "NO_MATERIAL_CHANGE"
    dispatch = bool(causes)
    seconds_to_scheduled = _seconds_to_next_scheduled_compass(now)
    if dispatch and request_in_flight and not protective:
        suppressed = list(causes)
        dispatch = False
        reason = "REQUEST_IN_FLIGHT"
    elif (
        dispatch
        and not protective
        and not request_retry_due
        and 0 <= seconds_to_scheduled <= SCHEDULE_PROXIMITY_SECONDS
    ):
        suppressed = list(causes)
        dispatch = False
        reason = "SCHEDULED_SLOT_IMMINENT"
    elif (
        dispatch
        and not protective
        and not request_retry_due
        and cooldown_age is not None
        and cooldown_age < NON_PROTECTIVE_COOLDOWN_SECONDS
    ):
        suppressed = list(causes)
        dispatch = False
        reason = "COOLDOWN_ACTIVE"
    elif dispatch:
        reason = "MATERIAL_REASSESSMENT_REQUIRED"

    return {
        "contract": CONTRACT,
        "evaluated_at_utc": now.isoformat().replace("+00:00", "Z"),
        "dispatch": dispatch,
        "upstream_refresh_required": False,
        "reason": reason,
        "cause_codes": causes if dispatch else [],
        "suppressed_cause_codes": suppressed,
        "protective_bypass": protective,
        "cooldown_seconds": NON_PROTECTIVE_COOLDOWN_SECONDS,
        "request_retry_seconds": REQUEST_RETRY_SECONDS,
        "scheduled_slot_proximity_seconds": SCHEDULE_PROXIMITY_SECONDS,
        "seconds_to_next_scheduled_compass": seconds_to_scheduled,
        "last_request_age_seconds": cooldown_age,
        "last_requested_source_sha": last_requested_source or None,
        "source_packet_sha256": source_sha,
        "latest_compass_source_packet_sha256": compass_source_sha or None,
        "current_data_status": current_data_status,
        "current_action": current_action,
        "current_market_state": market,
        "current_ladder": _ladder_status(ladder),
        "current_protection_tracker": protection,
        "heat_state": heat,
        "heat_detail": heat_detail,
        "authority": {
            "portfolio_execution": False,
            "forecast_change": False,
            "market_threshold_change": False,
            "purpose": "EVENT_DRIVEN_REASSESSMENT_ADMISSION_ONLY",
        },
    }


def run(repo_root: Path, output_root: Path, now: datetime | None = None) -> dict[str, Any]:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(microsecond=0)
    auto_pointer = read_json(repo_root / AUTO_POINTER)
    auto_state = read_json(repo_root / Path(str(auto_pointer["packet_path"])))
    compass_pointer = read_json(repo_root / COMPASS_POINTER)
    latest_compass = read_json(repo_root / Path(str(compass_pointer["compass_path"])))
    entry_latest = read_json(repo_root / ENTRY_LATEST)
    state_path = repo_root / output_root / "STATE.json"
    prior_state = read_json(state_path) if state_path.exists() else None
    cn_package, cn_binding = nh.load_cn_context(repo_root)

    decision = evaluate(
        auto_state=auto_state,
        auto_pointer=auto_pointer,
        latest_compass=latest_compass,
        entry_latest=entry_latest,
        prior_state=prior_state,
        cn_package=cn_package,
        cn_binding=cn_binding,
        now=now,
    )

    heat = str(decision.get("heat_state") or "NORMAL")
    requested_sha = (
        decision.get("source_packet_sha256")
        if decision.get("dispatch")
        else (prior_state or {}).get("last_requested_source_sha")
        or (prior_state or {}).get("last_dispatched_source_sha")
    )
    requested_at = (
        decision.get("evaluated_at_utc")
        if decision.get("dispatch")
        else (prior_state or {}).get("last_request_at_utc")
        or (prior_state or {}).get("last_dispatch_at_utc")
    )
    new_state = {
        "contract": STATE_CONTRACT,
        "last_heat_state": heat,
        "last_requested_source_sha": requested_sha,
        "last_request_at_utc": requested_at,
        # Legacy aliases retained for old readers. They mean workflow dispatch
        # accepted, not that a new Compass necessarily finished binding yet.
        "last_dispatched_source_sha": requested_sha,
        "last_dispatch_at_utc": requested_at,
    }

    root = repo_root / output_root
    root.mkdir(parents=True, exist_ok=True)
    if decision.get("dispatch") or prior_state is None or heat != str((prior_state or {}).get("last_heat_state") or "NORMAL"):
        state_path.write_text(json.dumps(new_state, sort_keys=True, indent=2) + "\n")

    if decision.get("dispatch"):
        dt = now.strftime("%Y/%m/%d")
        run_dir = root / "runs" / dt
        run_dir.mkdir(parents=True, exist_ok=True)
        run_path = run_dir / f"{now:%H%M%S}_{str(decision['source_packet_sha256'])[:12]}.json"
        run_path.write_text(json.dumps(decision, sort_keys=True, indent=2) + "\n")
        (root / "LATEST.json").write_text(json.dumps(decision, sort_keys=True, indent=2) + "\n")
        protection_event = any(
            code in {"PROTECTION_STATE_CHANGED", "REENTRY_REVIEW_OPENED"}
            for code in decision.get("cause_codes", [])
        )
        public = {
            "contract": PUBLIC_CONTRACT,
            "status": "REASSESSMENT_REQUESTED",
            "detected_at_utc": decision["evaluated_at_utc"],
            "cause_codes": decision.get("cause_codes", []),
            "message": (
                "Protection or re-entry state changed. Compass reassessment is in progress."
                if protection_event
                else "Material market move or decision-state change detected. Compass reassessment is in progress."
            ),
            "authority": {
                "official_compass_change": False,
                "portfolio_execution": False,
            },
        }
        (root / "PUBLIC_STATUS.json").write_text(json.dumps(public, sort_keys=True, indent=2) + "\n")

    return decision


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    decision = run(args.repo_root, args.output_root)
    print(json.dumps(decision, sort_keys=True))


if __name__ == "__main__":
    main()
