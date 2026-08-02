from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    monday = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    rows: list[dict[str, Any]] = []
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
        if captured < monday:
            continue
        cfgi = packet.get("market_metrics", {}).get("sentiment", {}).get("cfgi", {})
        symbols = cfgi.get("symbols", {}) if isinstance(cfgi, dict) else {}
        if not symbols:
            continue
        owner = next((x for x in packet.get("owners", []) if x.get("owner_id") == "cfgi_sentiment"), {})
        billing: dict[str, Any] = {}
        for file in owner.get("files", []):
            summary = file.get("summary", {})
            if isinstance(summary, dict) and isinstance(summary.get("billing"), dict):
                billing = summary["billing"]
        used = billing.get("credits_used")
        remaining = billing.get("credits_remaining")
        if isinstance(used, int):
            credits_used += used
        if isinstance(remaining, int):
            latest_remaining = remaining
        rows.append({
            "captured_at_utc": packet.get("captured_at_utc"),
            "timeframe": cfgi.get("timeframe"),
            "symbols": symbols,
            "billing": billing,
            "source_path": str(path),
        })

    by_symbol: dict[str, dict[str, Any]] = {}
    for row in rows:
        for symbol, values in row["symbols"].items():
            if not isinstance(values, dict) or not isinstance(values.get("score"), (int, float)):
                continue
            item = by_symbol.setdefault(symbol, {"scores": [], "component_snapshots": 0})
            item["scores"].append({"timestamp": row["captured_at_utc"], "score": values["score"]})
            if any(k in values for k in ("whales", "orders", "technical", "volatility")):
                item["component_snapshots"] += 1

    summary: dict[str, Any] = {}
    for symbol, item in by_symbol.items():
        scores = item.pop("scores")
        vals = [x["score"] for x in scores]
        summary[symbol] = {
            "open": vals[0], "high": max(vals), "low": min(vals), "close": vals[-1],
            "observations": len(vals), "component_snapshots": item["component_snapshots"],
            "first_timestamp": scores[0]["timestamp"], "last_timestamp": scores[-1]["timestamp"],
        }

    package = {
        "contract": "WEEKLY_CFGI_DERIVED_SUMMARY_v1",
        "iso_year": monday.isocalendar().year,
        "iso_week": monday.isocalendar().week,
        "source": "DAILY_RAW_CAPTURE_INDEX_v2",
        "api_calls_added": 0,
        "credits_used_by_source_captures": credits_used,
        "latest_credits_remaining": latest_remaining,
        "capture_count": len(rows),
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
        "capture_count": len(rows),
        "api_calls_added": 0,
    }
    (out / "WEEKLY_CFGI_DERIVED_RECEIPT.json").write_bytes(canonical(receipt))
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
