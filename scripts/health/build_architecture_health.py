from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

TIMESTAMP_KEYS = ("captured_at_utc", "retrieved_at_utc", "created_at_utc", "generated_at_utc", "freeze_utc", "snapshot_utc")


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text())
        return value if isinstance(value, dict) else None
    except Exception:
        return None


def parse_dt(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def row_timestamp(value: dict[str, Any]) -> datetime | None:
    for key in TIMESTAMP_KEYS:
        dt = parse_dt(value.get(key))
        if dt:
            return dt
    for nested_key in ("packet", "meta", "receipt"):
        nested = value.get(nested_key)
        if isinstance(nested, dict):
            for key in TIMESTAMP_KEYS:
                dt = parse_dt(nested.get(key))
                if dt:
                    return dt
    return None


def latest_json(root: Path) -> tuple[Path | None, dict[str, Any] | None, datetime | None]:
    candidates: list[tuple[datetime, str, Path, dict[str, Any]]] = []
    if root.exists():
        for path in root.rglob("*.json"):
            value = read_json(path)
            if value is None:
                continue
            ts = row_timestamp(value)
            if ts is not None:
                candidates.append((ts, str(path), path, value))
    if not candidates:
        return None, None, None
    ts, _, path, value = max(candidates, key=lambda row: (row[0], row[1]))
    return path, value, ts


def age_hours(now: datetime, ts: datetime | None) -> float | None:
    return None if ts is None else max(0.0, (now - ts).total_seconds() / 3600.0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--json-output", type=Path, required=True)
    ap.add_argument("--md-output", type=Path, required=True)
    ap.add_argument("--now-utc")
    args = ap.parse_args()
    root = args.repo_root
    now = parse_dt(args.now_utc) if args.now_utc else datetime.now(timezone.utc)
    assert now is not None

    cap_path, cap, cap_ts = latest_json(root / "03_DAILY_CAPTURE_LOGS/captures")
    daily_path, daily, daily_ts = latest_json(root / "research/api_agent/outputs/daily")
    weekly_path, weekly, weekly_ts = latest_json(root / "research/api_agent/outputs/weekly")
    etf_path, etf, etf_ts = latest_json(root / "research/etf_owner")
    ping_files = list((root / "research/data_ping_bridge/accepted").rglob("*.json")) if (root / "research/data_ping_bridge/accepted").exists() else []

    owners: list[dict[str, Any]] = []
    cfgi_remaining = None
    if cap:
        for owner in cap.get("owners", []):
            if not isinstance(owner, dict):
                continue
            owners.append({"owner_id": owner.get("owner_id"), "status": owner.get("status", "UNKNOWN")})
            if owner.get("owner_id") == "cfgi_sentiment":
                for file_row in owner.get("files", []):
                    summary = file_row.get("summary") if isinstance(file_row, dict) else None
                    if isinstance(summary, dict) and summary.get("credits_remaining") is not None:
                        cfgi_remaining = summary["credits_remaining"]

    pass_count = sum(row["status"] == "PASS" for row in owners)
    blockers: list[str] = []
    severity = 0

    def add(code: str, level: int) -> None:
        nonlocal severity
        if code not in blockers:
            blockers.append(code)
        severity = max(severity, level)

    cap_age = age_hours(now, cap_ts)
    daily_age = age_hours(now, daily_ts)
    weekly_age = age_hours(now, weekly_ts)
    etf_age = age_hours(now, etf_ts)

    if cap is None:
        add("NO_DAILY_CAPTURE", 2)
    elif cap_age is None or cap_age > 8:
        add("DAILY_CAPTURE_STALE", 2)
    if owners and pass_count < max(1, len(owners) - 1):
        add("OWNER_COVERAGE_DEGRADED", 1)
    if daily is None:
        add("NO_DAILY_DIRECTOR_OUTPUT", 1)
    elif daily_age is None or daily_age > 36:
        add("DAILY_DIRECTOR_STALE", 1)

    monday_or_later = now.weekday() == 0 and now.hour >= 4 or now.weekday() > 0
    if weekly is None:
        add("NO_WEEKLY_API_OUTPUT_YET", 2 if monday_or_later else 1)
    elif weekly_age is None or weekly_age > 9 * 24:
        add("WEEKLY_API_OUTPUT_STALE", 2)

    if etf is None:
        add("NO_ETF_OWNER_OUTPUT", 1)
    else:
        rows = etf.get("rows", []) if isinstance(etf, dict) else []
        if any(isinstance(row, dict) and row.get("total_parity") is False for row in rows):
            add("ETF_TOTAL_PARITY_FAILED", 2)
        if etf.get("status") not in {"PASS", "COMPLETE"}:
            add("ETF_OWNER_DEGRADED", 1)
        if etf_age is None or etf_age > 96:
            add("ETF_OWNER_STALE", 1)

    status = "RED" if severity >= 2 else ("AMBER" if severity == 1 else "GREEN")
    health = {
        "contract": "ARCHITECTURE_HEALTH_DASHBOARD_v2",
        "generated_at_utc": now.isoformat().replace("+00:00", "Z"),
        "status": status,
        "freshness_hours": {"capture": cap_age, "daily_director": daily_age, "weekly_calibration": weekly_age, "etf_owner": etf_age},
        "owners": {"count": len(owners), "pass_count": pass_count, "rows": owners},
        "latest_capture_path": str(cap_path) if cap_path else None,
        "latest_daily_director_path": str(daily_path) if daily_path else None,
        "latest_weekly_calibration_path": str(weekly_path) if weekly_path else None,
        "latest_etf_owner_path": str(etf_path) if etf_path else None,
        "accepted_data_ping_count": len(ping_files),
        "cfgi_credits_remaining": cfgi_remaining,
        "blockers": blockers,
        "authority": {"framework_state_change": False, "portfolio_action": False},
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(health, sort_keys=True, separators=(",", ":")) + "\n")
    lines = ["# Architecture Health", f"Status: **{status}**", f"Generated: {health['generated_at_utc']}", "", f"Owners: {pass_count}/{len(owners)} PASS", f"Accepted DATA PINGs: {len(ping_files)}", f"CFGI credits remaining: {cfgi_remaining if cfgi_remaining is not None else 'UNKNOWN'}", "", "## Freshness hours"]
    lines += [f"- {key}: {value if value is not None else 'UNKNOWN'}" for key, value in health["freshness_hours"].items()]
    lines += ["", "## Blockers"] + ([f"- {code}" for code in blockers] or ["- None"])
    args.md_output.write_text("\n".join(lines) + "\n")
    print(json.dumps({"status": status, "blockers": blockers}, sort_keys=True))


if __name__ == "__main__":
    main()
