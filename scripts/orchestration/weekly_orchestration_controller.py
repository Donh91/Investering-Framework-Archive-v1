from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def digest(value: Any) -> str:
    raw = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    return hashlib.sha256(raw).hexdigest()


def expected_completed_week(now: datetime) -> tuple[int, int, str]:
    monday = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    start = monday - timedelta(days=7)
    iso = start.isocalendar()
    return iso.year, iso.week, monday.isoformat().replace("+00:00", "Z")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture-root", type=Path, required=True)
    ap.add_argument("--accepted-data-ping-root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--now-utc", help="Test-only ISO timestamp")
    args = ap.parse_args()

    now = datetime.fromisoformat(args.now_utc.replace("Z", "+00:00")) if args.now_utc else datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    now = now.astimezone(timezone.utc)

    close_pointer = args.capture_root / "weekly_close" / "LATEST_WEEKLY_MARKET_CLOSE.json"
    weekly_pointer = args.capture_root / "weekly" / "LATEST_WEEKLY_CALIBRATION.json"
    if not close_pointer.exists():
        raise SystemExit("FINAL_WEEK_CLOSE_MISSING")
    if not weekly_pointer.exists():
        raise SystemExit("WEEKLY_CAPTURE_BRIDGE_MISSING")

    pointer = load(close_pointer)
    if pointer.get("contract") != "WEEKLY_MARKET_CLOSE_POINTER_v2":
        raise SystemExit("WEEK_CLOSE_POINTER_CONTRACT_INVALID")
    if pointer.get("final") is not True or pointer.get("close_mode") != "FINAL_COMPLETED_ISO_WEEK" or pointer.get("completeness") != "COMPLETE":
        raise SystemExit("WEEK_CLOSE_NOT_FINAL")

    package_path = args.capture_root / str(pointer.get("path", ""))
    if not package_path.exists():
        raise SystemExit("WEEK_CLOSE_PACKAGE_MISSING")
    package = load(package_path)
    package_hash = digest(package)
    if package_hash != pointer.get("sha256"):
        raise SystemExit("WEEK_CLOSE_HASH_MISMATCH")
    if package.get("final") is not True or package.get("close_mode") != "FINAL_COMPLETED_ISO_WEEK" or package.get("completeness") != "COMPLETE":
        raise SystemExit("WEEK_CLOSE_PACKAGE_NOT_FINAL")

    expected_year, expected_week, expected_end = expected_completed_week(now)
    for source in (pointer, package):
        if int(source.get("iso_year", -1)) != expected_year or int(source.get("iso_week", -1)) != expected_week:
            raise SystemExit("WEEK_CLOSE_WRONG_ISO_WEEK")
        if source.get("window_end_utc") != expected_end:
            raise SystemExit("WEEK_CLOSE_WRONG_WINDOW_END")

    weekly = load(weekly_pointer)
    weekly_year = weekly.get("iso_year")
    weekly_week = weekly.get("iso_week")
    if weekly_year is not None and int(weekly_year) != expected_year:
        raise SystemExit("WEEKLY_BRIDGE_WRONG_ISO_YEAR")
    if weekly_week is not None and int(weekly_week) != expected_week:
        raise SystemExit("WEEKLY_BRIDGE_WRONG_ISO_WEEK")

    accepted = []
    parse_errors = []
    if args.accepted_data_ping_root.exists():
        for p in sorted(args.accepted_data_ping_root.rglob("*.json")):
            try:
                row = load(p)
            except Exception as exc:
                parse_errors.append({"path": str(p), "error": type(exc).__name__})
                continue
            if row.get("contract") == "ACCEPTED_DATA_PING_PACKET_v1" and row.get("acceptance_status") == "ACCEPTED":
                accepted.append({"path": str(p), "snapshot_id": row.get("snapshot_id"), "freeze_utc": row.get("freeze_utc"), "sha256": digest(row)})

    freeze = {
        "contract": "WEEKLY_ORCHESTRATION_FREEZE_v2",
        "created_at_utc": now.isoformat().replace("+00:00", "Z"),
        "status": "READY",
        "iso_year": expected_year,
        "iso_week": expected_week,
        "window_end_utc": expected_end,
        "final_week_close": {
            "pointer_path": str(close_pointer),
            "pointer_sha256": digest(pointer),
            "package_path": str(package_path),
            "package_sha256": package_hash,
        },
        "weekly_capture_bridge": {"path": str(weekly_pointer), "sha256": digest(weekly)},
        "accepted_data_pings": accepted,
        "accepted_data_ping_parse_errors": parse_errors,
        "handoff_targets": ["RAW_WEEKLY_CALIBRATION", "CYCLE_NAVIGATOR", "MASTER_MONDAY_PREP", "FORECAST_LEDGER"],
        "authority": {"canonical_promotion": False, "model_weight_change": False, "portfolio_action": False},
    }
    freeze["freeze_sha256"] = digest(freeze)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(freeze, sort_keys=True, separators=(",", ":")) + "\n")
    print(json.dumps({"status": "READY", "iso_year": expected_year, "iso_week": expected_week, "accepted_data_pings": len(accepted), "freeze_sha256": freeze["freeze_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
