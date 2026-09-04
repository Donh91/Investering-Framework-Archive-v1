#!/usr/bin/env python3
"""Deterministic GitHub-native replacement for recurring Claude OTA readbacks.

This program reads existing framework-owned artifacts only. It performs no market
source calls and has no canonical, threshold, promotion, or portfolio authority.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

UTC = timezone.utc
CONTRACT = "NATIVE_OTA_READBACK_v1"
REGISTERED_ETHBTC_LEVEL = 0.03
AUTHORITY = {
    "canonical_state_change": False,
    "market_rule_change": False,
    "threshold_change": False,
    "portfolio_execution": False,
    "experiment_promotion": False,
    "source_owner_creation": False,
}


def utcnow() -> datetime:
    return datetime.now(UTC)


def iso_z(value: datetime) -> str:
    return value.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_dt(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None


def safe_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text())
        return payload if isinstance(payload, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def safe_float(value: Any) -> float | None:
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def sha256_json(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class Hour:
    ts: datetime
    btc_open: float
    btc_high: float
    btc_low: float
    btc_close: float
    eth_open: float
    eth_high: float
    eth_low: float
    eth_close: float
    ethbtc_open: float
    ethbtc_high: float
    ethbtc_low: float
    ethbtc_close: float


HOURLY_FIELDS = (
    "btc_open", "btc_high", "btc_low", "btc_close",
    "eth_open", "eth_high", "eth_low", "eth_close",
    "ethbtc_open", "ethbtc_high", "ethbtc_low", "ethbtc_close",
)


def load_hourly_rows(repo_root: Path, lookback_days: int = 45) -> list[Hour]:
    """Load and de-duplicate archived hourly rows by their source timestamp."""
    base = repo_root / "03_DAILY_CAPTURE_LOGS/hourly"
    cutoff = utcnow().date() - timedelta(days=lookback_days)
    rows: dict[datetime, Hour] = {}
    for path in sorted(base.glob("*/*/*.csv")):
        try:
            if date.fromisoformat(path.stem) < cutoff:
                continue
        except ValueError:
            pass
        try:
            with path.open(newline="") as handle:
                for raw in csv.DictReader(handle):
                    ts = parse_dt(raw.get("timestamp_utc"))
                    if ts is None:
                        continue
                    values = [safe_float(raw.get(field)) for field in HOURLY_FIELDS]
                    if any(value is None for value in values):
                        continue
                    rows[ts] = Hour(ts, *[float(value) for value in values])
        except (OSError, csv.Error):
            continue
    return [rows[key] for key in sorted(rows)]


def _session_payload(day: date, rows: list[Hour], status: str) -> dict[str, Any]:
    first, last = rows[0], rows[-1]
    btc_return = ((last.btc_close / first.btc_open) - 1.0) * 100.0 if first.btc_open else None
    eth_return = ((last.eth_close / first.eth_open) - 1.0) * 100.0 if first.eth_open else None
    return {
        "date_utc": day.isoformat(),
        "session_status": status,
        "hour_count": len(rows),
        "btc": {
            "open": first.btc_open,
            "high": max(row.btc_high for row in rows),
            "low": min(row.btc_low for row in rows),
            "close": last.btc_close,
            "return_pct": btc_return,
        },
        "eth": {
            "open": first.eth_open,
            "high": max(row.eth_high for row in rows),
            "low": min(row.eth_low for row in rows),
            "close": last.eth_close,
            "return_pct": eth_return,
        },
        "ethbtc": {
            "open": first.ethbtc_open,
            "high": max(row.ethbtc_high for row in rows),
            "low": min(row.ethbtc_low for row in rows),
            "close": last.ethbtc_close,
            "return_pct": ((last.ethbtc_close / first.ethbtc_open) - 1.0) * 100.0 if first.ethbtc_open else None,
        },
        "eth_minus_btc_return_pp": None if btc_return is None or eth_return is None else eth_return - btc_return,
        "last_hour_open_utc": iso_z(last.ts),
    }


def build_daily(rows: Iterable[Hour]) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    """Separate exact 24-hour UTC sessions from the newest incomplete session."""
    by_day: dict[date, dict[int, Hour]] = {}
    for row in rows:
        by_day.setdefault(row.ts.date(), {})[row.ts.hour] = row

    settled: list[dict[str, Any]] = []
    incomplete: dict[str, Any] | None = None
    for day in sorted(by_day):
        hour_map = by_day[day]
        day_rows = [hour_map[hour] for hour in sorted(hour_map)]
        complete = len(day_rows) == 24 and set(hour_map) == set(range(24))
        payload = _session_payload(day, day_rows, "SETTLED_COMPLETE_24H" if complete else "IN_PROGRESS_INCOMPLETE")
        if complete:
            settled.append(payload)
        elif incomplete is None or payload["date_utc"] > incomplete["date_utc"]:
            incomplete = payload
    return settled, incomplete


def consecutive_tail(values: list[bool]) -> int:
    count = 0
    for value in reversed(values):
        if not value:
            break
        count += 1
    return count


def linear_slope(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    x_mean = (len(values) - 1) / 2.0
    y_mean = sum(values) / len(values)
    denominator = sum((index - x_mean) ** 2 for index in range(len(values)))
    if denominator == 0:
        return None
    return sum((index - x_mean) * (value - y_mean) for index, value in enumerate(values)) / denominator


def monotonic_nonincreasing(values: list[float]) -> bool | None:
    if len(values) < 2:
        return None
    return all(current <= previous for previous, current in zip(values, values[1:]))


def threshold_analysis(settled: list[dict[str, Any]], incomplete: dict[str, Any] | None) -> dict[str, Any]:
    level = REGISTERED_ETHBTC_LEVEL
    if not settled:
        return {
            "registered_level_read_only": level,
            "threshold_authority": "READ_ONLY_EXISTING_REGISTERED_LEVEL",
            "status": "UNAVAILABLE_NO_SETTLED_SESSIONS",
        }

    latest = settled[-1]
    previous = settled[-2] if len(settled) >= 2 else None
    closes = [float(session["ethbtc"]["close"]) for session in settled]
    last7 = settled[-7:]
    close_margins = [((float(session["ethbtc"]["close"]) / level) - 1.0) * 100.0 for session in last7]
    low_margins = [((float(session["ethbtc"]["low"]) / level) - 1.0) * 100.0 for session in last7]

    crossed_below = bool(
        previous
        and float(previous["ethbtc"]["close"]) >= level
        and float(latest["ethbtc"]["close"]) < level
    )
    reclaimed = bool(
        previous
        and float(previous["ethbtc"]["close"]) < level
        and float(latest["ethbtc"]["close"]) >= level
    )

    result: dict[str, Any] = {
        "registered_level_read_only": level,
        "threshold_authority": "READ_ONLY_EXISTING_REGISTERED_LEVEL",
        "latest_settled_date_utc": latest["date_utc"],
        "latest_settled_close": latest["ethbtc"]["close"],
        "latest_settled_low": latest["ethbtc"]["low"],
        "latest_settled_close_margin_pct": ((float(latest["ethbtc"]["close"]) / level) - 1.0) * 100.0,
        "latest_settled_low_margin_pct": ((float(latest["ethbtc"]["low"]) / level) - 1.0) * 100.0,
        "consecutive_settled_closes_at_or_above": consecutive_tail([close >= level for close in closes]),
        "settled_close_crossed_below_on_latest": crossed_below,
        "settled_close_reclaimed_on_latest": reclaimed,
        "last7_settled_close_margin_pct": close_margins,
        "last7_settled_low_margin_pct": low_margins,
        "last7_close_margin_slope_pp_per_session": linear_slope(close_margins),
        "last7_low_margin_slope_pp_per_session": linear_slope(low_margins),
        "last7_close_margin_monotonic_compression": monotonic_nonincreasing(close_margins),
        "last7_low_margin_monotonic_compression": monotonic_nonincreasing(low_margins),
    }
    if incomplete:
        result["in_progress"] = {
            "date_utc": incomplete["date_utc"],
            "hour_count": incomplete["hour_count"],
            "low": incomplete["ethbtc"]["low"],
            "latest_close": incomplete["ethbtc"]["close"],
            "low_margin_pct": ((float(incomplete["ethbtc"]["low"]) / level) - 1.0) * 100.0,
            "close_margin_pct": ((float(incomplete["ethbtc"]["close"]) / level) - 1.0) * 100.0,
            "semantics": "IN_PROGRESS_NEVER_SETTLED_EVIDENCE",
        }
    return result


def leadership_analysis(settled: list[dict[str, Any]], incomplete: dict[str, Any] | None) -> dict[str, Any]:
    def eth_led(session: dict[str, Any]) -> bool:
        spread = session.get("eth_minus_btc_return_pp")
        return spread is not None and float(spread) > 0.0

    last4 = settled[-4:]
    last6 = settled[-6:]
    result: dict[str, Any] = {
        "settled_eth_led_last_4": sum(eth_led(session) for session in last4),
        "settled_sessions_last_4": len(last4),
        "settled_eth_led_last_6": sum(eth_led(session) for session in last6),
        "settled_sessions_last_6": len(last6),
        "consecutive_btc_led_settled": consecutive_tail([not eth_led(session) for session in settled]),
        "latest_settled_relative_pp": settled[-1]["eth_minus_btc_return_pp"] if settled else None,
        "classification": "DESCRIPTIVE_RELATIVE_LEADERSHIP_ONLY",
    }
    if incomplete:
        spread = incomplete.get("eth_minus_btc_return_pp")
        result["in_progress_relative_pp"] = spread
        result["in_progress_leader"] = "UNKNOWN" if spread is None else ("ETH" if spread > 0 else "BTC")
        result["in_progress_semantics"] = "IN_PROGRESS_CONTEXT_ONLY"
    return result


def latest_etf(repo_root: Path) -> dict[str, Any]:
    path = repo_root / "research/etf_owner/LATEST_FARSIDE_ETF_OWNER.json"
    payload = safe_json(path)
    if not payload:
        return {"status": "FRAMEWORK_DATA_GAP", "path": str(path.relative_to(repo_root))}
    history = payload.get("history_rows") or {}
    latest: dict[str, Any] = {}
    for asset in ("BTC", "ETH"):
        asset_rows = history.get(asset) if isinstance(history, dict) else None
        finals = [row for row in (asset_rows or []) if isinstance(row, dict) and row.get("session_final") is True]
        finals.sort(key=lambda row: str(row.get("date") or ""))
        if finals:
            row = finals[-1]
            latest[asset] = {
                "date": row.get("date"),
                "reported_total": row.get("reported_total"),
                "session_final": True,
                "total_parity": row.get("total_parity"),
            }
    return {
        "status": "PASS" if latest else "SOURCE_DATA_LIMITATION",
        "contract": payload.get("contract"),
        "authority": payload.get("authority"),
        "latest_final": latest,
        "path": str(path.relative_to(repo_root)),
    }


def pullback_status(repo_root: Path) -> dict[str, Any]:
    path = repo_root / "03_DAILY_CAPTURE_LOGS/pullback_forensics/LATEST.json"
    payload = safe_json(path)
    if not payload:
        return {"status": "FRAMEWORK_DATA_GAP", "path": str(path.relative_to(repo_root))}
    lane1 = payload.get("lane1_liquidations") or {}
    lane2b = payload.get("lane2b_moneyness_skew") or {}
    return {
        "status": "PASS",
        "contract": payload.get("contract"),
        "authority": payload.get("authority"),
        "lane1_executed_liquidations": {
            "status_by_asset": {asset: (value or {}).get("status") for asset, value in lane1.items()} if isinstance(lane1, dict) else {},
            "semantics": "LOWER_BOUND_WHERE_PAGE_COMPLETENESS_UNVERIFIED",
        },
        "lane2a_dvol": payload.get("lane2a_dvol"),
        "lane2b_moneyness_skew": {
            "status_by_asset": {asset: (value or {}).get("status") for asset, value in lane2b.items()} if isinstance(lane2b, dict) else {},
            "semantics": "MONEYNESS_BUCKET_SKEW_NOT_25_DELTA",
        },
        "lane3_orderbook": {
            "status": "DEFERRED_BY_RATIFIED_PILOT",
            "reason": "MULTI_HOUR_CADENCE_CANNOT_EVIDENTIALLY_MEASURE_MINUTE_SCALE_REFILL_OR_EVAPORATION",
        },
        "path": str(path.relative_to(repo_root)),
    }


def situation_room_status(repo_root: Path) -> dict[str, Any]:
    latest_path = repo_root / "03_DAILY_CAPTURE_LOGS/catalyst_overlay/situation_room/LATEST.json"
    latest = safe_json(latest_path)
    if not latest:
        return {"status": "FRAMEWORK_DATA_GAP", "path": str(latest_path.relative_to(repo_root))}
    relative_daily = latest.get("path")
    daily = safe_json(repo_root / str(relative_daily)) if relative_daily else None
    return {
        "status": "PASS" if daily else "SOURCE_DATA_LIMITATION",
        "owner_contract": latest.get("contract"),
        "authority": latest.get("authority"),
        "observation_date_utc": latest.get("observation_date_utc"),
        "run_status": latest.get("run_status"),
        "daily_result": latest.get("daily_result"),
        "verified_event_count": len((daily or {}).get("events") or []),
        "unverified_discovery_count": len((daily or {}).get("unverified_discoveries") or []),
        "l4_bridge_status": "PARTIAL_NATIVE_DISCOVERY_CONTEXT_NOT_FULL_L4_ATTRIBUTION_OWNER",
        "l4_evidence_rule": "NO_L4_EVIDENCE_ROW_FROM_UNVERIFIED_DISCOVERY_OR_RETROSPECTIVE_TAGGING",
        "path": str(latest_path.relative_to(repo_root)),
    }


def breadth_status(repo_root: Path) -> dict[str, Any]:
    path = repo_root / "03_DAILY_CAPTURE_LOGS/breadth_rich/LATEST.json"
    payload = safe_json(path)
    if not payload:
        return {"status": "FRAMEWORK_DATA_GAP", "path": str(path.relative_to(repo_root))}
    aggregate = payload.get("aggregate") or {}
    return {
        "status": "PASS",
        "evidence_role": "PROXY_ONLY_DESCRIPTIVE_ZERO_EXECUTION_WEIGHT",
        "advance_ratio": aggregate.get("advance_ratio"),
        "advancers": aggregate.get("advancers"),
        "decliners": aggregate.get("decliners"),
        "flat": aggregate.get("flat"),
        "outperforming_btc_count": aggregate.get("outperforming_btc_count"),
        "outperforming_eth_count": aggregate.get("outperforming_eth_count"),
        "membership_hash": aggregate.get("membership_hash"),
        "path": str(path.relative_to(repo_root)),
    }


def cadence_status(repo_root: Path) -> dict[str, Any]:
    path = repo_root / "03_DAILY_CAPTURE_LOGS/cadence/LATEST.json"
    payload = safe_json(path)
    if not payload:
        return {"status": "FRAMEWORK_DATA_GAP", "path": str(path.relative_to(repo_root))}
    return {
        "status": "PASS",
        "authority": payload.get("authority"),
        "generated_at_utc": payload.get("generated_at_utc"),
        "boost_active": payload.get("boost_active"),
        "boost_reasons": payload.get("boost_reasons"),
        "registered_ethbtc_level_read_only": payload.get("registered_ethbtc_level_read_only"),
        "ethbtc_live": payload.get("ethbtc_live"),
        "latest_top100_proxy_advance_ratio": payload.get("latest_top100_proxy_advance_ratio"),
        "path": str(path.relative_to(repo_root)),
    }


def legacy_ota_status(repo_root: Path) -> dict[str, Any]:
    path = repo_root / "04_MARKET_LEARNING/claude_ota/LATEST_CLAUDE_OTA_STATUS_v1.json"
    payload = safe_json(path)
    if not payload:
        return {"status": "ABSENT", "operational_role": "NONE"}
    return {
        "status": "LEGACY_CONTEXT_ONLY",
        "latest_source_run_timestamp_utc": payload.get("latest_source_run_timestamp_utc"),
        "operational_role": "NONE_AFTER_NATIVE_PRODUCTION_PROOF",
        "may_override_native_owners": False,
        "path": str(path.relative_to(repo_root)),
    }


def previous_native(repo_root: Path) -> dict[str, Any] | None:
    return safe_json(repo_root / "04_MARKET_LEARNING/ota_native/LATEST.json")


def material_deltas(current: dict[str, Any], previous: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not previous:
        return [{"id": "BOOTSTRAP", "classification": "CONTEXT_ONLY", "claim": "First native OTA readback; no prior native report exists."}]

    deltas: list[dict[str, Any]] = []
    current_settled = current.get("settled_session") or {}
    previous_settled = previous.get("settled_session") or {}
    if current_settled.get("date_utc") != previous_settled.get("date_utc"):
        deltas.append({
            "id": "D-SETTLE",
            "classification": "NEW_INFORMATION",
            "claim": f"New settled session {current_settled.get('date_utc')}",
        })

    gate = current.get("ethbtc_gate") or {}
    prior_gate = previous.get("ethbtc_gate") or {}
    if gate.get("latest_settled_close") != prior_gate.get("latest_settled_close"):
        deltas.append({"id": "D-ETHBTC", "classification": "EVIDENTIAL", "claim": "ETHBTC settled evidence advanced."})
    if gate.get("settled_close_crossed_below_on_latest"):
        deltas.append({
            "id": "D-GATE-BREAK",
            "classification": "EVIDENTIAL",
            "claim": "ETHBTC settled close crossed below the existing registered 0.0300 reference.",
        })
    if gate.get("settled_close_reclaimed_on_latest"):
        deltas.append({
            "id": "D-GATE-RECLAIM",
            "classification": "EVIDENTIAL",
            "claim": "ETHBTC settled close reclaimed the existing registered 0.0300 reference.",
        })

    leadership = current.get("eth_leadership") or {}
    prior_leadership = previous.get("eth_leadership") or {}
    if leadership.get("consecutive_btc_led_settled") != prior_leadership.get("consecutive_btc_led_settled"):
        deltas.append({
            "id": "D-LEADERSHIP",
            "classification": "CONTEXT_ONLY",
            "claim": "Settled BTC/ETH relative-leadership sequence changed.",
        })

    return deltas or [{"id": "NO_MATERIAL_DELTA", "classification": "CONTEXT_ONLY", "claim": "No new settled or threshold-transition evidence since prior native report."}]


def build_report(repo_root: Path, trigger: str, trigger_only: bool) -> tuple[dict[str, Any], bool]:
    hourly_rows = load_hourly_rows(repo_root)
    settled, incomplete = build_daily(hourly_rows)
    gate = threshold_analysis(settled, incomplete)

    report: dict[str, Any] = {
        "contract": CONTRACT,
        "schema_version": 1,
        "generated_at_utc": iso_z(utcnow()),
        "trigger": trigger,
        "mode": "TRIGGER_ONLY" if trigger_only else "FULL_FIXED_OR_MANUAL",
        "authority": AUTHORITY,
        "source_policy": "READ_EXISTING_GITHUB_OWNERS_ONLY_NO_NEW_MARKET_SOURCE_CALLS",
        "settled_session": settled[-1] if settled else None,
        "in_progress_session": incomplete,
        "ethbtc_gate": gate,
        "eth_leadership": leadership_analysis(settled, incomplete),
        "owner_readback": {
            "etf": latest_etf(repo_root),
            "pullback_forensics": pullback_status(repo_root),
            "situation_room": situation_room_status(repo_root),
            "breadth": breadth_status(repo_root),
            "adaptive_cadence": cadence_status(repo_root),
        },
        "legacy_claude_ota": legacy_ota_status(repo_root),
        "governance": {
            "framework_interpretation": "DEFERRED_TO_CURRENT_CANONICAL_OWNERS",
            "portfolio_action": "NONE_FROM_NATIVE_OTA",
            "new_threshold": False,
            "canonical_state_change": False,
            "experiment_promotion": False,
            "do_not_force_finding": True,
        },
        "qa": {
            "settled_definition": "EXACTLY_24_UNIQUE_UTC_HOURLY_ROWS_00_THROUGH_23",
            "in_progress_high_may_be_called_cycle_high": False,
            "in_progress_data_may_be_called_settled": False,
            "framework_gap_vs_context_gap_separated": True,
            "orderbook_delta_over_60m_allowed": False,
            "data_missing_semantics": "UNKNOWN_NOT_ZERO",
        },
    }

    report["classified_deltas"] = material_deltas(report, previous_native(repo_root))
    counts = {"NEW_INFORMATION": 0, "EVIDENTIAL": 0, "CONTEXT_ONLY": 0}
    for item in report["classified_deltas"]:
        classification = item.get("classification")
        if classification in counts:
            counts[classification] += 1
    report["classification_counts"] = counts

    early = bool(gate.get("settled_close_crossed_below_on_latest") or gate.get("settled_close_reclaimed_on_latest"))
    report["early_trigger"] = {
        "triggered": early,
        "reasons": [
            label for label, active in (
                ("ETHBTC_SETTLED_CROSS_BELOW_REGISTERED_0_0300", gate.get("settled_close_crossed_below_on_latest")),
                ("ETHBTC_SETTLED_RECLAIM_REGISTERED_0_0300", gate.get("settled_close_reclaimed_on_latest")),
            ) if active
        ],
        "adaptive_rotation_attention": report["owner_readback"]["adaptive_cadence"].get("boost_active"),
        "note": "Adaptive cadence is attention-only and does not create a rule or force a native OTA report.",
    }

    framework_gaps = [
        name for name, owner in report["owner_readback"].items()
        if isinstance(owner, dict) and owner.get("status") == "FRAMEWORK_DATA_GAP"
    ]
    report["gap_accounting"] = {
        "framework_data_gaps": framework_gaps,
        "ota_context_gaps": [],
        "rule": "If a native owner artifact exists, absence from an external/legacy OTA context is OTA_CONTEXT_GAP, not FRAMEWORK_DATA_GAP.",
    }

    report["report_hash_sha256"] = ""
    report["report_hash_sha256"] = sha256_json(report)
    return report, early


def write_report(repo_root: Path, report: dict[str, Any]) -> Path:
    generated = parse_dt(report["generated_at_utc"]) or utcnow()
    root = repo_root / "04_MARKET_LEARNING/ota_native"
    run_dir = root / generated.strftime("%Y/%m/%d")
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / (generated.strftime("%H%M%S") + "_NATIVE_OTA_READBACK.json")
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    path.write_text(text)
    (root / "LATEST.json").write_text(text)
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--trigger", default="MANUAL")
    parser.add_argument("--trigger-only", action="store_true")
    parser.add_argument("--output-status")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    report, early = build_report(repo_root, args.trigger, args.trigger_only)
    emitted = (not args.trigger_only) or early
    output_path: Path | None = None
    if emitted:
        output_path = write_report(repo_root, report)

    status = {
        "contract": "NATIVE_OTA_EXECUTION_STATUS_v1",
        "generated_at_utc": report["generated_at_utc"],
        "trigger_only": args.trigger_only,
        "early_triggered": early,
        "emitted": emitted,
        "output_path": None if output_path is None else str(output_path.relative_to(repo_root)),
        "report_hash_sha256": report["report_hash_sha256"],
    }
    if args.output_status:
        status_path = repo_root / args.output_status
        status_path.parent.mkdir(parents=True, exist_ok=True)
        status_path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")
    print(json.dumps(status, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
