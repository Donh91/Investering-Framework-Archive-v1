#!/usr/bin/env python3
"""Decide whether the next live-anchor run should refresh slow macro context.

This is a capture-scheduling helper only. It does not classify the market,
change thresholds, forward-fill macro data, or grant portfolio authority.

The normal daily FRED slot remains authoritative for cadence. This helper adds
bounded recovery: if the most recent live-anchor capture containing non-empty
macro evidence is too old, the next successful tactical anchor run may refresh
the same FRED owner.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

CONTRACT = "SLOW_MACRO_RECOVERY_DECISION_v1"
DEFAULT_THRESHOLD_HOURS = 24.0


def parse_utc(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        out = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if out.utcoffset() is None:
        return None
    return out.astimezone(timezone.utc)


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def has_macro(packet: Mapping[str, Any]) -> bool:
    metrics = packet.get("market_metrics")
    macro = metrics.get("macro") if isinstance(metrics, Mapping) else None
    return isinstance(macro, Mapping) and bool(macro)


def latest_valid_macro_capture(capture_root: Path) -> tuple[datetime | None, str | None]:
    if not capture_root.exists():
        return None, None
    latest: tuple[datetime, str] | None = None
    for path in capture_root.rglob("*.json"):
        if path.name == "LATEST.json":
            continue
        packet = read_json(path)
        if not isinstance(packet, Mapping):
            continue
        if packet.get("contract") != "DAILY_LIVE_ANCHOR_INDEX_v3":
            continue
        if not has_macro(packet):
            continue
        stamp = parse_utc(packet.get("captured_at_utc"))
        if stamp is None:
            continue
        rel = path.as_posix()
        if latest is None or stamp > latest[0]:
            latest = (stamp, rel)
    return latest if latest is not None else (None, None)


def decide(capture_root: Path, now: datetime, threshold_hours: float = DEFAULT_THRESHOLD_HOURS) -> dict[str, Any]:
    now = now.astimezone(timezone.utc)
    latest, path = latest_valid_macro_capture(capture_root)
    threshold_seconds = max(0.0, float(threshold_hours)) * 3600.0

    if latest is None:
        due = True
        reason = "NO_VALID_MACRO_CAPTURE"
        age_seconds = None
    else:
        age_seconds = (now - latest).total_seconds()
        if age_seconds < 0:
            due = True
            reason = "LATEST_MACRO_CAPTURE_FROM_FUTURE"
        elif age_seconds >= threshold_seconds:
            due = True
            reason = "MACRO_RECOVERY_DUE"
        else:
            due = False
            reason = "MACRO_CAPTURE_FRESH_ENOUGH"

    return {
        "contract": CONTRACT,
        "evaluated_at_utc": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "run_slow_lane": due,
        "reason": reason,
        "latest_valid_macro_capture_utc": latest.isoformat().replace("+00:00", "Z") if latest else None,
        "latest_valid_macro_capture_path": path,
        "age_seconds": age_seconds,
        "recovery_threshold_hours": float(threshold_hours),
        "authority": {
            "market_state_change": False,
            "portfolio_action": False,
            "source_substitution": False,
            "forward_fill": False,
            "purpose": "CAPTURE_RECOVERY_SCHEDULING_ONLY",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture-root", type=Path, default=Path("03_DAILY_CAPTURE_LOGS/captures"))
    parser.add_argument("--now-utc")
    parser.add_argument("--threshold-hours", type=float, default=DEFAULT_THRESHOLD_HOURS)
    args = parser.parse_args()
    now = parse_utc(args.now_utc) if args.now_utc else datetime.now(timezone.utc)
    if now is None:
        raise SystemExit("INVALID_NOW_UTC")
    print(json.dumps(decide(args.capture_root, now, args.threshold_hours), sort_keys=True))


if __name__ == "__main__":
    main()
