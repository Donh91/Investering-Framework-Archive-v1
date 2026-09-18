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
deduplicated.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
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
            "reason": "AUTO_STATE_SOURCE_SHA_MISSING",
            "heat_state": heat,
            "heat_detail": heat_detail,
        }

    if source_sha == compass_source_sha:
        return {
            "contract": CONTRACT,
            "evaluated_at_utc": now.isoformat().replace("+00:00", "Z"),
            "dispatch": False,
            "reason": "LATEST_COMPASS_ALREADY_BINDS_CURRENT_OWNER_PACKET",
            "source_packet_sha256": source_sha,
            "heat_state": heat,
            "heat_detail": heat_detail,
        }

    if source_sha == str(prior_state.get("last_dispatched_source_sha") or ""):
        return {
            "contract": CONTRACT,
            "evaluated_at_utc": now.isoformat().replace("+00:00", "Z"),
            "dispatch": False,
            "reason": "SOURCE_ALREADY_DISPATCHED",
            "source_packet_sha256": source_sha,
            "heat_state": heat,
            "heat_detail": heat_detail,
        }

    cn_ok = isinstance(cn_package, Mapping) and str((cn_binding or {}).get("status") or "") == "PASS"
    owner_ok = nh._health_ok(auto_state, now)
    current_data_status = "OK" if owner_ok and cn_ok else "DEGRADED"
    action = nh.action_context(auto_state, as_of=now)
    market = nh.derive_market_now(auto_state, action, as_of=now)
    ladder = nh.capitalization_ladder(auto_state, action, market, as_of=now)

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

    last_heat = str(prior_state.get("last_heat_state") or "NORMAL")
    # Heat is a refresh accelerator only when the current owner evidence is
    # decision-eligible. Stale/degraded evidence must never manufacture a
    # "market move" event; health transitions are handled separately above.
    if current_data_status == "OK" and heat != "NORMAL" and heat != last_heat:
        causes.append("MARKET_HEAT_ENTERED")

    dispatch = bool(causes)
    return {
        "contract": CONTRACT,
        "evaluated_at_utc": now.isoformat().replace("+00:00", "Z"),
        "dispatch": dispatch,
        "reason": "MATERIAL_REASSESSMENT_REQUIRED" if dispatch else "NO_MATERIAL_CHANGE",
        "cause_codes": causes,
        "source_packet_sha256": source_sha,
        "latest_compass_source_packet_sha256": compass_source_sha or None,
        "current_data_status": current_data_status,
        "current_action": action.get("NOW"),
        "current_market_state": market,
        "current_ladder": _ladder_status(ladder),
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
    new_state = {
        "contract": STATE_CONTRACT,
        "last_heat_state": heat,
        "last_dispatched_source_sha": (
            decision.get("source_packet_sha256")
            if decision.get("dispatch")
            else (prior_state or {}).get("last_dispatched_source_sha")
        ),
        "last_dispatch_at_utc": (
            decision.get("evaluated_at_utc")
            if decision.get("dispatch")
            else (prior_state or {}).get("last_dispatch_at_utc")
        ),
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
        public = {
            "contract": PUBLIC_CONTRACT,
            "status": "REASSESSMENT_REQUESTED",
            "detected_at_utc": decision["evaluated_at_utc"],
            "cause_codes": decision.get("cause_codes", []),
            "message": "Material market move or decision-state change detected. Compass reassessment is in progress.",
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
