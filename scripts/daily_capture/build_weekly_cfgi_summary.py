from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def cfgi_from_capture(packet: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return CFGI rows from a daily capture without adding source calls.

    Prefer the legacy owner-file summary when it is present so historical
    captures retain their original billing/component semantics. Current
    DAILY_LIVE_ANCHOR_INDEX_v3 captures expose the accepted point-in-time
    CFGI observations under market_metrics.sentiment.cfgi.symbols; use that
    representation only when legacy rows are absent.
    """
    owner = next((x for x in packet.get("owners", []) if x.get("owner_id") == "cfgi_sentiment"), {})
    rows: list[dict[str, Any]] = []
    billing: dict[str, Any] = {}
    fields: list[str] = []
    for file in owner.get("files", []):
        summary = file.get("summary", {})
        if not isinstance(summary, dict):
            continue
        if isinstance(summary.get("rows"), list):
            rows = summary["rows"]
        if isinstance(summary.get("fields"), list):
            fields = summary["fields"]
        if isinstance(summary.get("billing"), dict):
            billing = summary["billing"]
    if rows:
        if fields and not isinstance(billing.get("credits_used"), int):
            billing["credits_used"] = len(rows) * len(fields)
            billing["usage_source"] = "DERIVED_FROM_FIELDS_X_ROWS"
        return rows, billing

    sentiment = packet.get("market_metrics", {}).get("sentiment", {})
    cfgi = sentiment.get("cfgi", {}) if isinstance(sentiment, dict) else {}
    symbols = cfgi.get("symbols", {}) if isinstance(cfgi, dict) else {}
    if not isinstance(symbols, dict):
        return [], billing

    current_rows: list[dict[str, Any]] = []
    for symbol, observation in symbols.items():
        if not isinstance(observation, dict):
            continue
        score = observation.get("score")
        if not isinstance(score, (int, float)):
            continue
        row: dict[str, Any] = {
            "symbol": str(symbol),
            "score": score,
        }
        for key in ("classification", "price", "timestamp", "owner_status", "stale"):
            if key in observation:
                row[key] = observation[key]
        components = observation.get("components")
        if isinstance(components, dict) and components:
            row["components"] = components
        current_rows.append(row)

    return current_rows, billing


def target_week_window(now: datetime, mode: str) -> tuple[datetime, datetime]:
    """Return a strictly bounded UTC ISO week for preclose or prior-week final.

    On Monday the FINAL market-close job settles the *previous* completed week;
    computing the ISO week from the execution clock silently points at the new
    (often empty) week. Keep the collector/observation timestamp unchanged.
    """
    if mode not in {"preclose", "final"}:
        raise ValueError("Unsupported weekly close mode")
    utc_now = now.astimezone(timezone.utc)
    monday = (utc_now - timedelta(days=utc_now.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    if mode == "final":
        monday -= timedelta(days=7)
    return monday, monday + timedelta(days=7)


def resolve_close_mode(mode: str, *, event_name: str, event_path: str, run_attempt: str = "") -> str:
    """Resolve trigger mode; reject reruns without immutable original-week anchor.

    A GitHub rerun retains the original event payload and RUN_ID, but its
    datetime.now() is a new clock. Without the original ISO-week anchor a
    rerun after rollover could corrupt another weekly summary. Refuse every
    Actions retry until the independent original-run clock is available.
    """
    if run_attempt and run_attempt != "1":
        raise ValueError("RERUN_ORIGINAL_WEEK_UNBOUND_FAIL_CLOSED")
    if event_name == "workflow_dispatch":
        # The existing workflow_dispatch payload specifies a mode, but it
        # does not bind the original ISO week. A queued first attempt may
        # execute across Monday UTC rollover; do not write a different week.
        raise ValueError("DISPATCH_ORIGINAL_WEEK_UNBOUND_FAIL_CLOSED")
    if mode in ("preclose", "final"):
        return mode
    if mode != "auto" or event_name not in ("schedule", "workflow_dispatch") or not event_path:
        raise ValueError("WEEKLY_MODE_UNAVAILABLE")
    payload = json.loads(Path(event_path).read_text())
    if not isinstance(payload, dict):
        raise ValueError("INVALID_GITHUB_EVENT")
    if event_name == "schedule":
        schedules = {"35 23 * * 0": "preclose", "5 2 * * 1": "final"}
        if payload.get("schedule") not in schedules:
            raise ValueError("UNKNOWN_SCHEDULE")
        return schedules[payload["schedule"]]
    raise ValueError("WEEKLY_MODE_UNAVAILABLE")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--mode", choices=("auto", "preclose", "final"), default="auto")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    mode = resolve_close_mode(args.mode, event_name=os.getenv('GITHUB_EVENT_NAME', ''), event_path=os.getenv('GITHUB_EVENT_PATH', ''), run_attempt=os.getenv('GITHUB_RUN_ATTEMPT', ''))
    if os.getenv('GITHUB_EVENT_NAME') == 'schedule':
        # A delayed first attempt after UTC week rollover cannot safely
        # reconstruct the event's original ISO week from wall clock alone.
        expected_utc_weekday = 6 if mode == "preclose" else 0
        if now.weekday() != expected_utc_weekday:
            raise ValueError("SCHEDULED_WEEK_ROLLOVER_UNBOUND_FAIL_CLOSED")
    monday, week_end = target_week_window(now, mode)
    observations: list[dict[str, Any]] = []
    credits_used = 0
    latest_remaining: int | None = None

    for path in sorted(args.capture_root.rglob("*.json")):
        if path.name == "LATEST.json":
            continue
        try:
            packet = json.loads(path.read_text())
            captured = datetime.fromisoformat(str(packet["captured_at_utc"]).replace("Z", "+00:00"))
        except Exception:
            continue
        if not monday <= captured < week_end:
            continue
        rows, billing = cfgi_from_capture(packet)
        if not rows:
            continue
        used = billing.get("credits_used")
        remaining = billing.get("credits_remaining")
        if isinstance(used, int):
            credits_used += used
        if isinstance(remaining, int):
            latest_remaining = remaining
        observations.append({
            "captured_at_utc": packet.get("captured_at_utc"),
            "rows": rows,
            "billing": billing,
            "source_path": str(path),
        })

    by_symbol: dict[str, dict[str, Any]] = {}
    for observation in observations:
        for row in observation["rows"]:
            if not isinstance(row, dict) or not isinstance(row.get("score"), (int, float)):
                continue
            symbol = str(row.get("symbol", "UNKNOWN"))
            item = by_symbol.setdefault(symbol, {"scores": [], "component_snapshots": 0, "latest_components": {}})
            item["scores"].append({"timestamp": observation["captured_at_utc"], "score": row["score"]})
            components = row.get("components")
            if isinstance(components, dict) and components:
                item["component_snapshots"] += 1
                item["latest_components"] = components

    summary: dict[str, Any] = {}
    for symbol, item in by_symbol.items():
        scores = item["scores"]
        vals = [x["score"] for x in scores]
        summary[symbol] = {
            "open": vals[0], "high": max(vals), "low": min(vals), "close": vals[-1],
            "observations": len(vals), "component_snapshots": item["component_snapshots"],
            "latest_components": item["latest_components"],
            "first_timestamp": scores[0]["timestamp"], "last_timestamp": scores[-1]["timestamp"],
        }

    package = {
        "contract": "WEEKLY_CFGI_DERIVED_SUMMARY_v1",
        "iso_year": monday.isocalendar().year,
        "iso_week": monday.isocalendar().week,
        "source": "DAILY_RAW_CAPTURE_INDEX_v2_OWNER_SUMMARIES",
        "api_calls_added": 0,
        "credits_used_by_source_captures": credits_used,
        "latest_credits_remaining": latest_remaining,
        "capture_count": len(observations),
        "symbols": summary,
        "status": "PASS" if summary else "SOURCE_UNAVAILABLE",
        "authority": "SHADOW_CALIBRATION_INPUT",
        "canonical_data_ping": False,
        "framework_state_change": False,
        "portfolio_action": False,
    }
    body = canonical(package)
    out = args.output_root / str(monday.isocalendar().year) / f"W{monday.isocalendar().week:02d}"
    out.mkdir(parents=True, exist_ok=True)
    target = out / "WEEKLY_CFGI_DERIVED_SUMMARY.json"
    target.write_bytes(body)
    receipt = {
        "contract": "WEEKLY_CFGI_DERIVED_RECEIPT_v1",
        "sha256": hashlib.sha256(body).hexdigest(),
        "status": package["status"],
        "capture_count": len(observations),
        "api_calls_added": 0,
    }
    (out / "WEEKLY_CFGI_DERIVED_RECEIPT.json").write_bytes(canonical(receipt))
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
