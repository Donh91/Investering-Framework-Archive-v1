from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_packets(root: Path, iso_year: int, iso_week: int) -> list[tuple[Path, dict[str, Any]]]:
    packets: list[tuple[Path, dict[str, Any]]] = []
    if not root.exists():
        return packets
    for path in sorted(root.rglob("*.json")):
        if path.name == "LATEST.json" or "weekly" in path.parts:
            continue
        try:
            data = json.loads(path.read_text())
            stamp = datetime.fromisoformat(data["captured_at_utc"].replace("Z", "+00:00"))
        except Exception:
            continue
        y, w, _ = stamp.isocalendar()
        if y == iso_year and w == iso_week:
            packets.append((path, data))
    return packets


def f(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def load_hourly_rows(root: Path, iso_year: int, iso_week: int) -> list[dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    if not root.exists():
        return []
    for path in sorted(root.rglob("*.csv")):
        try:
            with path.open(newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    stamp_raw = row.get("timestamp_utc")
                    if not stamp_raw:
                        continue
                    stamp = datetime.fromisoformat(stamp_raw.replace("Z", "+00:00"))
                    y, w, _ = stamp.isocalendar()
                    if y == iso_year and w == iso_week:
                        rows[stamp_raw] = row
        except Exception:
            continue
    return [rows[key] for key in sorted(rows)]


def hourly_sequence_summary(rows: list[dict[str, str]]) -> dict[str, Any]:
    expected = 168
    timestamps = [row.get("timestamp_utc") for row in rows if row.get("timestamp_utc")]
    spot_complete = [row for row in rows if all(row.get(k) not in (None, "") for k in ("btc_close", "eth_close", "ethbtc_close"))]
    oi_complete = [row for row in rows if all(row.get(k) not in (None, "") for k in ("btc_open_interest", "eth_open_interest"))]
    ls_complete = [row for row in rows if all(row.get(k) not in (None, "") for k in ("btc_long_short_ratio", "eth_long_short_ratio"))]

    btc_returns = [f(row.get("btc_return_1h_pct")) for row in rows]
    btc_returns = [x for x in btc_returns if x is not None]
    eth_returns = [f(row.get("eth_return_1h_pct")) for row in rows]
    eth_returns = [x for x in eth_returns if x is not None]
    ethbtc_returns = [f(row.get("ethbtc_return_1h_pct")) for row in rows]
    ethbtc_returns = [x for x in ethbtc_returns if x is not None]
    btc_ranges = [f(row.get("btc_range_1h_pct")) for row in rows]
    btc_ranges = [x for x in btc_ranges if x is not None]
    eth_ranges = [f(row.get("eth_range_1h_pct")) for row in rows]
    eth_ranges = [x for x in eth_ranges if x is not None]

    price_oi = Counter(row.get("btc_price_oi_state") for row in rows if row.get("btc_price_oi_state"))
    eth_price_oi = Counter(row.get("eth_price_oi_state") for row in rows if row.get("eth_price_oi_state"))

    return {
        "contract": "WEEKLY_HOURLY_SEQUENCE_EVIDENCE_v1",
        "expected_hourly_rows": expected,
        "observed_hourly_rows": len(rows),
        "hourly_coverage_pct": round((len(rows) / expected) * 100.0, 3) if expected else 0.0,
        "spot_complete_hours": len(spot_complete),
        "derivatives_oi_complete_hours": len(oi_complete),
        "long_short_complete_hours": len(ls_complete),
        "first_hour_utc": timestamps[0] if timestamps else None,
        "last_hour_utc": timestamps[-1] if timestamps else None,
        "btc": {
            "down_hours": sum(x < 0 for x in btc_returns),
            "up_hours": sum(x > 0 for x in btc_returns),
            "max_abs_return_1h_pct": max((abs(x) for x in btc_returns), default=None),
            "max_range_1h_pct": max(btc_ranges, default=None),
            "price_oi_state_counts": dict(sorted(price_oi.items())),
        },
        "eth": {
            "down_hours": sum(x < 0 for x in eth_returns),
            "up_hours": sum(x > 0 for x in eth_returns),
            "max_abs_return_1h_pct": max((abs(x) for x in eth_returns), default=None),
            "max_range_1h_pct": max(eth_ranges, default=None),
            "price_oi_state_counts": dict(sorted(eth_price_oi.items())),
        },
        "ethbtc": {
            "down_hours": sum(x < 0 for x in ethbtc_returns),
            "up_hours": sum(x > 0 for x in ethbtc_returns),
        },
        "sequence_evidence_only": True,
        "market_interpretation": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--hourly-root", type=Path)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--iso-year", type=int)
    parser.add_argument("--iso-week", type=int)
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    current_year, current_week, _ = now.isocalendar()
    iso_year = args.iso_year or current_year
    iso_week = args.iso_week or current_week
    packets = load_packets(args.input_root, iso_year, iso_week)
    hourly_rows = load_hourly_rows(args.hourly_root, iso_year, iso_week) if args.hourly_root else []

    status_counts = Counter(packet.get("status", "UNKNOWN") for _, packet in packets)
    owner_status: dict[str, Counter[str]] = {}
    eligible = 0
    source_paths: list[str] = []
    for path, packet in packets:
        source_paths.append(str(path))
        eligible += int(bool(packet.get("weekly_calibration_eligible")))
        for owner in packet.get("owners", []):
            owner_status.setdefault(owner["owner_id"], Counter())[owner.get("status", "UNKNOWN")] += 1

    hourly = hourly_sequence_summary(hourly_rows)
    anchor_ready = eligible >= 15
    hourly_ready = hourly["spot_complete_hours"] >= 150
    readiness = "READY" if anchor_ready and hourly_ready else "DEGRADED" if eligible or hourly_rows else "BLOCKED"

    pack = {
        "contract": "WEEKLY_RAW_CALIBRATION_PACK_v2",
        "authority": "SHADOW_CALIBRATION_INPUT_ONLY",
        "iso_year": iso_year,
        "iso_week": iso_week,
        "generated_at_utc": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "capture_count": len(packets),
        "eligible_capture_count": eligible,
        "capture_status_counts": dict(sorted(status_counts.items())),
        "owner_health": {key: dict(sorted(value.items())) for key, value in sorted(owner_status.items())},
        "source_capture_paths": source_paths,
        "hourly_sequence": hourly,
        "sequence_evidence_built": bool(hourly_rows),
        "raw_outcome_analysis": False,
        "forecast_evaluation_performed": False,
        "framework_state_change": False,
        "portfolio_action": False,
        "handoff_targets": [
            "RAW_WEEKLY_CALIBRATION",
            "FORECAST_LEDGER_EVALUATION",
            "MASTER_MONDAY_PREP",
            "SPECIALIST_WEEKLY_REVIEW",
            "PULLBACK_SEQUENCE_REPLAY",
        ],
        "readiness": readiness,
        "readiness_components": {
            "anchor_lane": "READY" if anchor_ready else "DEGRADED" if eligible else "BLOCKED",
            "hourly_sequence_lane": "READY" if hourly_ready else "DEGRADED" if hourly_rows else "BLOCKED",
        },
    }

    week_dir = args.output_root / str(iso_year)
    week_dir.mkdir(parents=True, exist_ok=True)
    output = week_dir / f"W{iso_week:02d}.json"
    output.write_text(json.dumps(pack, indent=2, sort_keys=True) + "\n")
    pointer = args.output_root / "LATEST_WEEKLY_CALIBRATION.json"
    pointer.write_text(json.dumps({
        "contract": "LATEST_WEEKLY_CALIBRATION_POINTER_v2",
        "path": str(output.relative_to(args.output_root.parent)),
        "iso_year": iso_year,
        "iso_week": iso_week,
        "readiness": pack["readiness"],
        "capture_count": len(packets),
        "hourly_rows": len(hourly_rows),
    }, indent=2, sort_keys=True) + "\n")
    print(output)


if __name__ == "__main__":
    main()
