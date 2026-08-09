from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


HORIZONS = (4, 12, 24, 48, 72)
ENRICHED_BASE_FIELDS = [
    "timestamp_utc", "timestamp_copenhagen", "source_window_end_utc",
    "btc_open", "btc_high", "btc_low", "btc_close", "btc_volume", "btc_quote_volume", "btc_trade_count",
    "btc_taker_buy_base_volume", "btc_taker_buy_quote_volume", "btc_taker_sell_quote_volume", "btc_taker_buy_quote_share",
    "btc_return_1h_pct", "btc_range_1h_pct",
    "eth_open", "eth_high", "eth_low", "eth_close", "eth_volume", "eth_quote_volume", "eth_trade_count",
    "eth_taker_buy_base_volume", "eth_taker_buy_quote_volume", "eth_taker_sell_quote_volume", "eth_taker_buy_quote_share",
    "eth_return_1h_pct", "eth_range_1h_pct",
    "ethbtc_open", "ethbtc_high", "ethbtc_low", "ethbtc_close", "ethbtc_return_1h_pct", "ethbtc_range_1h_pct",
    "derived_ethbtc_close", "ethbtc_direct_minus_derived_bps",
    "btc_open_interest", "btc_open_interest_value", "btc_oi_change_1h_pct", "btc_open_interest_source",
    "eth_open_interest", "eth_open_interest_value", "eth_oi_change_1h_pct", "eth_open_interest_source",
    "btc_long_short_ratio", "btc_long_account", "btc_short_account", "btc_long_short_source",
    "eth_long_short_ratio", "eth_long_account", "eth_short_account", "eth_long_short_source",
    "btc_funding_event_rate", "btc_funding_source", "eth_funding_event_rate", "eth_funding_source",
    "btc_price_oi_state", "eth_price_oi_state", "spot_status", "derivatives_status",
]
ENRICHED_DERIVED_FIELDS = [
    field
    for horizon in HORIZONS
    for field in (
        f"btc_return_{horizon}h_pct",
        f"eth_return_{horizon}h_pct",
        f"ethbtc_return_{horizon}h_pct",
        f"eth_minus_btc_return_{horizon}h_pct",
        f"btc_oi_change_{horizon}h_pct",
        f"eth_oi_change_{horizon}h_pct",
    )
]
ENRICHED_FIELDS = ENRICHED_BASE_FIELDS + ENRICHED_DERIVED_FIELDS


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def load_packets(root: Path, iso_year: int, iso_week: int) -> list[tuple[Path, dict[str, Any]]]:
    packets: list[tuple[Path, dict[str, Any]]] = []
    if not root.exists():
        return packets
    for path in sorted(root.rglob("*.json")):
        if path.name == "LATEST.json" or "weekly" in path.parts:
            continue
        try:
            data = json.loads(path.read_text())
            stamp = parse_utc(data["captured_at_utc"])
        except Exception:
            continue
        y, w, _ = stamp.isocalendar()
        if y == iso_year and w == iso_week:
            packets.append((path, data))
    return packets


def f(value: str | float | int | None) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fmt(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return format(value, ".12g")
    return str(value)


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
                    stamp = parse_utc(stamp_raw)
                    y, w, _ = stamp.isocalendar()
                    if y == iso_year and w == iso_week:
                        rows[stamp_raw] = row
        except Exception:
            continue
    return [rows[key] for key in sorted(rows)]


def pct_change(current: float | None, previous: float | None) -> float | None:
    return None if current is None or previous in (None, 0) else (current / previous - 1.0) * 100.0


def enrich_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    by_stamp = {parse_utc(row["timestamp_utc"]): row for row in rows if row.get("timestamp_utc")}
    enriched: list[dict[str, str]] = []
    for source in rows:
        stamp = parse_utc(source["timestamp_utc"])
        out: dict[str, str] = {
            field: source.get(field, "")
            for field in ENRICHED_BASE_FIELDS
            if field not in ("derived_ethbtc_close", "ethbtc_direct_minus_derived_bps")
        }
        btc = f(source.get("btc_close"))
        eth = f(source.get("eth_close"))
        direct = f(source.get("ethbtc_close"))
        derived = None if btc in (None, 0) or eth is None else eth / btc
        out["derived_ethbtc_close"] = fmt(derived)
        out["ethbtc_direct_minus_derived_bps"] = fmt(
            None if direct is None or derived in (None, 0) else (direct / derived - 1.0) * 10_000.0
        )
        for horizon in HORIZONS:
            previous = by_stamp.get(stamp - timedelta(hours=horizon))
            prev_btc = f(previous.get("btc_close")) if previous else None
            prev_eth = f(previous.get("eth_close")) if previous else None
            prev_ethbtc = f(previous.get("ethbtc_close")) if previous else None
            btc_return = pct_change(btc, prev_btc)
            eth_return = pct_change(eth, prev_eth)
            ethbtc_return = pct_change(direct, prev_ethbtc)
            out[f"btc_return_{horizon}h_pct"] = fmt(btc_return)
            out[f"eth_return_{horizon}h_pct"] = fmt(eth_return)
            out[f"ethbtc_return_{horizon}h_pct"] = fmt(ethbtc_return)
            out[f"eth_minus_btc_return_{horizon}h_pct"] = fmt(
                None if btc_return is None or eth_return is None else eth_return - btc_return
            )
            out[f"btc_oi_change_{horizon}h_pct"] = fmt(
                pct_change(f(source.get("btc_open_interest")), f(previous.get("btc_open_interest")) if previous else None)
            )
            out[f"eth_oi_change_{horizon}h_pct"] = fmt(
                pct_change(f(source.get("eth_open_interest")), f(previous.get("eth_open_interest")) if previous else None)
            )
        enriched.append({field: out.get(field, "") for field in ENRICHED_FIELDS})
    return enriched


def max_contiguous_gap(missing: list[datetime]) -> int:
    if not missing:
        return 0
    best = current = 1
    for previous, current_stamp in zip(missing, missing[1:]):
        if current_stamp - previous == timedelta(hours=1):
            current += 1
        else:
            current = 1
        best = max(best, current)
    return best


def hourly_gap_diagnostics(rows: list[dict[str, str]], iso_year: int, iso_week: int) -> dict[str, Any]:
    start = datetime.combine(date.fromisocalendar(iso_year, iso_week, 1), datetime.min.time(), tzinfo=timezone.utc)
    expected = [start + timedelta(hours=i) for i in range(168)]
    observed = {parse_utc(row["timestamp_utc"]) for row in rows if row.get("timestamp_utc")}
    missing = [stamp for stamp in expected if stamp not in observed]
    tracked_fields = [
        "btc_close", "eth_close", "ethbtc_close",
        "btc_quote_volume", "eth_quote_volume",
        "btc_trade_count", "eth_trade_count",
        "btc_taker_buy_quote_share", "eth_taker_buy_quote_share",
        "btc_open_interest", "eth_open_interest",
        "btc_long_short_ratio", "eth_long_short_ratio",
    ]
    per_field = {}
    for field in tracked_fields:
        complete = sum(row.get(field) not in (None, "") for row in rows)
        per_field[field] = {
            "complete_hours": complete,
            "coverage_pct": round((complete / 168.0) * 100.0, 3),
        }
    return {
        "expected_hours": 168,
        "observed_hours": len(observed),
        "missing_hour_count": len(missing),
        "missing_hours_utc": [stamp.isoformat().replace("+00:00", "Z") for stamp in missing],
        "max_contiguous_gap_hours": max_contiguous_gap(missing),
        "per_field_completeness": per_field,
    }


def range_summary(rows: list[dict[str, str]], prefix: str) -> dict[str, float | None]:
    if not rows:
        return {"open": None, "high": None, "low": None, "close": None}
    opens = [f(row.get(f"{prefix}_open")) for row in rows]
    highs = [f(row.get(f"{prefix}_high")) for row in rows]
    lows = [f(row.get(f"{prefix}_low")) for row in rows]
    closes = [f(row.get(f"{prefix}_close")) for row in rows]
    opens = [x for x in opens if x is not None]
    highs = [x for x in highs if x is not None]
    lows = [x for x in lows if x is not None]
    closes = [x for x in closes if x is not None]
    return {
        "open": opens[0] if opens else None,
        "high": max(highs) if highs else None,
        "low": min(lows) if lows else None,
        "close": closes[-1] if closes else None,
    }


def day_window_actuals(rows: list[dict[str, str]], iso_year: int, iso_week: int) -> dict[str, Any]:
    start = datetime.combine(date.fromisocalendar(iso_year, iso_week, 1), datetime.min.time(), tzinfo=timezone.utc)
    windows = {
        "DAY1_2": (start, start + timedelta(days=2)),
        "DAY3_4": (start + timedelta(days=2), start + timedelta(days=4)),
        "DAY5_7": (start + timedelta(days=4), start + timedelta(days=7)),
    }
    result: dict[str, Any] = {"basis": "UTC_ISO_WEEK", "windows": {}}
    for label, (window_start, window_end) in windows.items():
        subset = [
            row for row in rows
            if row.get("timestamp_utc") and window_start <= parse_utc(row["timestamp_utc"]) < window_end
        ]
        result["windows"][label] = {
            "window_start_utc": window_start.isoformat().replace("+00:00", "Z"),
            "window_end_utc": window_end.isoformat().replace("+00:00", "Z"),
            "observed_hours": len(subset),
            "btc": range_summary(subset, "btc"),
            "eth": range_summary(subset, "eth"),
            "ethbtc": range_summary(subset, "ethbtc"),
        }
    return result


def hourly_sequence_summary(rows: list[dict[str, str]]) -> dict[str, Any]:
    expected = 168
    timestamps = [row.get("timestamp_utc") for row in rows if row.get("timestamp_utc")]
    spot_complete = [row for row in rows if all(row.get(k) not in (None, "") for k in ("btc_close", "eth_close", "ethbtc_close"))]
    flow_complete = [row for row in rows if all(row.get(k) not in (None, "") for k in ("btc_taker_buy_quote_share", "eth_taker_buy_quote_share"))]
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
        "contract": "WEEKLY_HOURLY_SEQUENCE_EVIDENCE_v2",
        "expected_hourly_rows": expected,
        "observed_hourly_rows": len(rows),
        "hourly_coverage_pct": round((len(rows) / expected) * 100.0, 3) if expected else 0.0,
        "spot_complete_hours": len(spot_complete),
        "spot_flow_complete_hours": len(flow_complete),
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
            "week_range": range_summary(rows, "btc"),
        },
        "eth": {
            "down_hours": sum(x < 0 for x in eth_returns),
            "up_hours": sum(x > 0 for x in eth_returns),
            "max_abs_return_1h_pct": max((abs(x) for x in eth_returns), default=None),
            "max_range_1h_pct": max(eth_ranges, default=None),
            "price_oi_state_counts": dict(sorted(eth_price_oi.items())),
            "week_range": range_summary(rows, "eth"),
        },
        "ethbtc": {
            "down_hours": sum(x < 0 for x in ethbtc_returns),
            "up_hours": sum(x > 0 for x in ethbtc_returns),
            "week_range": range_summary(rows, "ethbtc"),
        },
        "sequence_evidence_only": True,
        "market_interpretation": False,
    }


def load_etf_records(root: Path | None, iso_year: int, iso_week: int) -> list[dict[str, Any]]:
    if root is None or not root.exists():
        return []
    latest_by_session: dict[str, dict[str, Any]] = {}
    for path in sorted(root.rglob("*.json")):
        if path.name == "LATEST.json":
            continue
        try:
            record = json.loads(path.read_text())
            session = record["session_date"]
            session_date = date.fromisoformat(session)
            y, w, _ = session_date.isocalendar()
            if (y, w) != (iso_year, iso_week):
                continue
        except Exception:
            continue
        previous = latest_by_session.get(session)
        if previous is None or str(record.get("retrieved_at_utc", "")) >= str(previous.get("retrieved_at_utc", "")):
            latest_by_session[session] = record
    return [latest_by_session[key] for key in sorted(latest_by_session)]


def etf_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    daily = []
    totals = {"BTC": 0.0, "ETH": 0.0}
    counts = {"BTC": 0, "ETH": 0}
    for record in records:
        item = {"session_date": record.get("session_date"), "BTC": None, "ETH": None}
        for row in record.get("rows", []):
            asset = row.get("asset")
            total = f(row.get("reported_total"))
            if asset in totals and total is not None:
                item[asset] = total
                totals[asset] += total
                counts[asset] += 1
        daily.append(item)
    return {
        "contract": "WEEKLY_SETTLED_ETF_CALIBRATION_v1",
        "records": daily,
        "week_total_reported_units": {
            asset: totals[asset] if counts[asset] else None for asset in totals
        },
        "session_counts": counts,
        "authority": "SHADOW_CALIBRATION_INPUT_ONLY",
    }


def write_enriched_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ENRICHED_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--hourly-root", type=Path)
    parser.add_argument("--etf-root", type=Path)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--iso-year", type=int)
    parser.add_argument("--iso-week", type=int)
    parser.add_argument("--previous-week", action="store_true")
    parser.add_argument("--now-utc", help="Test-only ISO timestamp")
    args = parser.parse_args()

    now = parse_utc(args.now_utc) if args.now_utc else datetime.now(timezone.utc)
    if args.iso_year or args.iso_week:
        if not (args.iso_year and args.iso_week):
            raise SystemExit("ISO_YEAR_AND_WEEK_MUST_BE_PAIRED")
        iso_year, iso_week = args.iso_year, args.iso_week
    elif args.previous_week:
        previous = now - timedelta(days=7)
        iso_year, iso_week, _ = previous.isocalendar()
    else:
        iso_year, iso_week, _ = now.isocalendar()

    packets = load_packets(args.input_root, iso_year, iso_week)
    hourly_rows = load_hourly_rows(args.hourly_root, iso_year, iso_week) if args.hourly_root else []
    enriched = enrich_rows(hourly_rows)
    etf_records = load_etf_records(args.etf_root, iso_year, iso_week)

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
    gaps = hourly_gap_diagnostics(hourly_rows, iso_year, iso_week)
    windows = day_window_actuals(hourly_rows, iso_year, iso_week)
    etf = etf_summary(etf_records)

    anchor_ready = eligible >= 15
    hourly_ready = hourly["spot_complete_hours"] >= 150 and gaps["max_contiguous_gap_hours"] <= 6
    readiness = "READY" if anchor_ready and hourly_ready else "DEGRADED" if eligible or hourly_rows else "BLOCKED"

    artifact_dir = args.output_root / str(iso_year) / f"W{iso_week:02d}"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    enriched_path = artifact_dir / "WEEKLY_HOURLY_ENRICHED.csv"
    facts_path = artifact_dir / "WEEKLY_SEQUENCE_FACTS.json"
    write_enriched_csv(enriched_path, enriched)

    latest = enriched[-1] if enriched else {}
    facts = {
        "contract": "WEEKLY_SEQUENCE_FACTS_v1",
        "authority": "SHADOW_CALIBRATION_INPUT_ONLY",
        "iso_year": iso_year,
        "iso_week": iso_week,
        "generated_at_utc": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "gap_diagnostics": gaps,
        "day_window_actuals": windows,
        "settled_etf": etf,
        "latest_rolling_features": {
            key: latest.get(key, "")
            for key in ENRICHED_DERIVED_FIELDS
        },
        "market_interpretation": False,
        "forecast_evaluation_performed": False,
        "interpolation": False,
        "forward_fill": False,
    }
    facts_path.write_text(json.dumps(facts, indent=2, sort_keys=True) + "\n")

    pack = {
        "contract": "WEEKLY_RAW_CALIBRATION_PACK_v3",
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
        "hourly_gap_diagnostics": gaps,
        "day_window_actuals": windows,
        "settled_etf": etf,
        "enriched_hourly_path": str(enriched_path.relative_to(args.output_root.parent)),
        "sequence_facts_path": str(facts_path.relative_to(args.output_root.parent)),
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

    year_dir = args.output_root / str(iso_year)
    year_dir.mkdir(parents=True, exist_ok=True)
    output = year_dir / f"W{iso_week:02d}.json"
    output.write_text(json.dumps(pack, indent=2, sort_keys=True) + "\n")
    pointer = args.output_root / "LATEST_WEEKLY_CALIBRATION.json"
    pointer.write_text(json.dumps({
        "contract": "LATEST_WEEKLY_CALIBRATION_POINTER_v3",
        "path": str(output.relative_to(args.output_root.parent)),
        "iso_year": iso_year,
        "iso_week": iso_week,
        "readiness": pack["readiness"],
        "capture_count": len(packets),
        "hourly_rows": len(hourly_rows),
        "enriched_hourly_path": pack["enriched_hourly_path"],
        "sequence_facts_path": pack["sequence_facts_path"],
        "missing_hour_count": gaps["missing_hour_count"],
        "max_contiguous_gap_hours": gaps["max_contiguous_gap_hours"],
    }, indent=2, sort_keys=True) + "\n")
    print(output)


if __name__ == "__main__":
    main()
