#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONTRACT = "SEGMENT_RETURN_RESEARCH_FOUNDATION_v1"
SOURCE_CONTRACT = "C5E_TOP100_BREADTH_OWNER_v1_2"
REQUIRED_DEL_OWNER_CONTRACT = "GOVERNED_SEGMENT_RETURN_SERIES_v1"

RANK_BUCKETS = {
    "RANK_3_25": (3, 25),
    "RANK_26_50": (26, 50),
    "RANK_51_100": (51, 100),
}

# Mirror the repository's existing 4h settled-interval convention (3.5-4.5h)
# proportionally for a 24h research interval: 24h +/- 12.5% = 21-27h.
DAILY_INTERVAL_TARGET_HOURS = 24.0
DAILY_INTERVAL_TOLERANCE_HOURS = 3.0
DAILY_INTERVAL_MIN_HOURS = DAILY_INTERVAL_TARGET_HOURS - DAILY_INTERVAL_TOLERANCE_HOURS
DAILY_INTERVAL_MAX_HOURS = DAILY_INTERVAL_TARGET_HOURS + DAILY_INTERVAL_TOLERANCE_HOURS


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object_required:{path}")
    return value


def parse_utc(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def finite_positive(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        return None
    return number


def snapshot_time(value: dict[str, Any]) -> datetime | None:
    return (
        parse_utc(value.get("retrieval_timestamp"))
        or parse_utc(value.get("freeze_timestamp"))
        or parse_utc(value.get("observation"))
    )


def valid_snapshot(value: dict[str, Any]) -> bool:
    return (
        value.get("contract") == SOURCE_CONTRACT
        and isinstance(value.get("constituents"), list)
        and snapshot_time(value) is not None
    )


def canonical_daily_snapshots(snapshot_root: Path) -> list[tuple[datetime, Path, dict[str, Any]]]:
    by_day: dict[str, tuple[datetime, Path, dict[str, Any]]] = {}
    if not snapshot_root.exists():
        return []
    for path in sorted(snapshot_root.rglob("owner_snapshot.json")):
        try:
            value = load_json(path)
        except Exception:
            continue
        if not valid_snapshot(value):
            continue
        ts = snapshot_time(value)
        assert ts is not None
        day = ts.date().isoformat()
        prior = by_day.get(day)
        if prior is None or ts > prior[0]:
            by_day[day] = (ts, path, value)
    return [by_day[day] for day in sorted(by_day)]


def constituent_map(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for row in snapshot.get("constituents") or []:
        if not isinstance(row, dict):
            continue
        asset_id = str(row.get("asset_id") or "").strip()
        price = finite_positive(row.get("price_usd"))
        rank = row.get("filtered_rank")
        market_cap = finite_positive(row.get("market_cap_usd"))
        if not asset_id or isinstance(rank, bool) or not isinstance(rank, int):
            continue
        rows[asset_id] = {
            "asset_id": asset_id,
            "price_usd": price,
            "filtered_rank": rank,
            "market_cap_usd": market_cap,
        }
    return rows


def raw_price_map(owner_snapshot_path: Path, snapshot: dict[str, Any]) -> tuple[dict[str, float], bool]:
    """Use raw Top150 only when it is hash- and run-bound to this owner snapshot."""
    raw_path = owner_snapshot_path.with_name("raw_source_payload.json")
    receipt_path = owner_snapshot_path.with_name("receipt.json")
    manifest_path = owner_snapshot_path.with_name("artifact_manifest.json")
    if not raw_path.exists() or not receipt_path.exists() or not manifest_path.exists():
        return {}, False
    try:
        raw_bytes = raw_path.read_bytes()
        value = json.loads(raw_bytes)
        receipt = load_json(receipt_path)
        manifest = load_json(manifest_path)
    except Exception:
        return {}, False
    run_id = snapshot.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        return {}, False
    raw_sha = hashlib.sha256(raw_bytes).hexdigest()
    if receipt.get("run_id") != run_id or receipt.get("raw_sha256") != raw_sha:
        return {}, False
    if manifest.get("contract") != "C5E_ARTIFACT_MANIFEST_v1" or manifest.get("run_id") != run_id:
        return {}, False
    members = manifest.get("members")
    if not isinstance(members, list):
        return {}, False
    member = next((x for x in members if isinstance(x, dict) and x.get("path") == "raw_source_payload.json"), None)
    if not isinstance(member, dict) or member.get("sha256") != raw_sha or member.get("bytes") != len(raw_bytes):
        return {}, False
    if not isinstance(value, list):
        return {}, False
    prices: dict[str, float] = {}
    for row in value:
        if not isinstance(row, dict):
            continue
        asset_id = str(row.get("id") or "").strip()
        price = finite_positive(row.get("current_price"))
        if asset_id and price is not None:
            prices[asset_id] = price
    return prices, True

def current_price_map(owner_snapshot_path: Path, snapshot: dict[str, Any]) -> tuple[dict[str, float], set[str], bool]:
    """Prefer normalized owner prices and use only hash-bound raw Top150 dropout prices."""
    normalized = constituent_map(snapshot)
    prices = {
        asset_id: float(row["price_usd"])
        for asset_id, row in normalized.items()
        if finite_positive(row.get("price_usd")) is not None
    }
    normalized_ids = set(prices)
    raw_prices, raw_binding_valid = raw_price_map(owner_snapshot_path, snapshot)
    for asset_id, price in raw_prices.items():
        prices.setdefault(asset_id, price)
    return prices, normalized_ids, raw_binding_valid


def simple_return(previous_price: float | None, current_price: float | None) -> float | None:
    if previous_price is None or current_price is None or previous_price <= 0:
        return None
    return current_price / previous_price - 1.0


def cohort_return(
    prior_rows: dict[str, dict[str, Any]],
    current_prices: dict[str, float],
    current_normalized_ids: set[str],
    low: int,
    high: int,
) -> dict[str, Any]:
    cohort = [
        row for row in prior_rows.values()
        if low <= int(row["filtered_rank"]) <= high
    ]
    returns: list[float] = []
    market_caps: list[float] = []
    matched_assets: list[str] = []
    missing_assets: list[str] = []
    missing_prior_price_assets: list[str] = []
    missing_current_price_assets: list[str] = []
    raw_fallback_assets: list[str] = []

    for row in cohort:
        asset_id = row["asset_id"]
        prior_price = finite_positive(row.get("price_usd"))
        current_price = finite_positive(current_prices.get(asset_id))
        value = simple_return(prior_price, current_price)
        if value is None:
            missing_assets.append(asset_id)
            if prior_price is None:
                missing_prior_price_assets.append(asset_id)
            if current_price is None:
                missing_current_price_assets.append(asset_id)
        else:
            returns.append(value)
            matched_assets.append(asset_id)
            if asset_id not in current_normalized_ids:
                raw_fallback_assets.append(asset_id)
        cap = finite_positive(row.get("market_cap_usd"))
        if cap is not None:
            market_caps.append(cap)

    complete = bool(cohort) and len(returns) == len(cohort)
    return {
        # Never publish a survivor-only cohort average. Full frozen membership coverage is required.
        "return": (sum(returns) / len(returns)) if complete else None,
        "cohort_count": len(cohort),
        "matched_count": len(returns),
        "matched_fraction": (len(returns) / len(cohort)) if cohort else None,
        "complete_price_coverage": complete,
        "missing_asset_ids": missing_assets,
        "missing_prior_price_asset_ids": missing_prior_price_assets,
        "missing_current_price_asset_ids": missing_current_price_assets,
        "raw_top150_fallback_asset_ids": raw_fallback_assets,
        "prior_market_cap_min_usd": min(market_caps) if market_caps else None,
        "prior_market_cap_median_usd": statistics.median(market_caps) if market_caps else None,
        "prior_market_cap_max_usd": max(market_caps) if market_caps else None,
        "matched_asset_ids": matched_assets,
    }


def eligible_daily_interval(interval_hours: float) -> bool:
    return DAILY_INTERVAL_MIN_HOURS <= interval_hours <= DAILY_INTERVAL_MAX_HOURS


def build_rows(snapshot_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    snapshots = canonical_daily_snapshots(snapshot_root)
    output_rows: list[dict[str, Any]] = []
    lineage: list[dict[str, Any]] = []

    for index in range(1, len(snapshots)):
        prior_ts, prior_path, prior = snapshots[index - 1]
        current_ts, current_path, current = snapshots[index]
        prior_rows = constituent_map(prior)
        current_prices, current_normalized_ids, raw_binding_valid = current_price_map(current_path, current)
        interval_hours = (current_ts - prior_ts).total_seconds() / 3600.0
        interval_ok = eligible_daily_interval(interval_hours)

        btc_raw = simple_return(
            finite_positive((prior_rows.get("bitcoin") or {}).get("price_usd")),
            finite_positive(current_prices.get("bitcoin")),
        )
        eth_raw = simple_return(
            finite_positive((prior_rows.get("ethereum") or {}).get("price_usd")),
            finite_positive(current_prices.get("ethereum")),
        )
        buckets = {
            name: cohort_return(prior_rows, current_prices, current_normalized_ids, low, high)
            for name, (low, high) in RANK_BUCKETS.items()
        }
        raw_returns = {
            "BTC": btc_raw,
            "ETH": eth_raw,
            "RANK_3_25": buckets["RANK_3_25"]["return"],
            "RANK_26_50": buckets["RANK_26_50"]["return"],
            "RANK_51_100": buckets["RANK_51_100"]["return"],
            "MICROCAPS": None,
        }

        row = {
            "date": current_ts.date().isoformat(),
            "prior_date": prior_ts.date().isoformat(),
            "interval_hours": round(interval_hours, 6),
            "daily_interval_eligible": interval_ok,
            "interval_status": "ELIGIBLE_24H_RESEARCH_WINDOW" if interval_ok else "IRREGULAR_INTERVAL_EXCLUDED_FROM_DAILY_SERIES",
            "BTC": btc_raw if interval_ok else None,
            "ETH": eth_raw if interval_ok else None,
            "RANK_3_25": raw_returns["RANK_3_25"] if interval_ok else None,
            "RANK_26_50": raw_returns["RANK_26_50"] if interval_ok else None,
            "RANK_51_100": raw_returns["RANK_51_100"] if interval_ok else None,
            "MICROCAPS": None,
            "raw_point_to_point_returns": raw_returns,
            "bucket_diagnostics": buckets,
            "current_raw_top150_binding_valid": raw_binding_valid,
        }
        output_rows.append(row)
        lineage.append({
            "date": row["date"],
            "prior_snapshot": prior_path.as_posix(),
            "current_snapshot": current_path.as_posix(),
            "current_raw_price_fallback_path": current_path.with_name("raw_source_payload.json").as_posix(),
            "current_raw_top150_binding_valid": raw_binding_valid,
            "prior_retrieval_timestamp": prior_ts.isoformat().replace("+00:00", "Z"),
            "current_retrieval_timestamp": current_ts.isoformat().replace("+00:00", "Z"),
            "interval_hours": row["interval_hours"],
            "daily_interval_eligible": interval_ok,
            "prior_membership_hash": ((prior.get("universe") or {}).get("membership_hash")),
            "current_membership_hash": ((current.get("universe") or {}).get("membership_hash")),
        })
    return output_rows, lineage


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "date", "prior_date", "interval_hours", "daily_interval_eligible",
        "BTC", "ETH", "RANK_3_25", "RANK_26_50", "RANK_51_100", "MICROCAPS",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: "" if row.get(field) is None else row.get(field) for field in fields})


def build_report(snapshot_root: Path, csv_path: Path, generated_at_utc: str | None = None) -> dict[str, Any]:
    rows, lineage = build_rows(snapshot_root)
    generated = (
        parse_utc(generated_at_utc).isoformat().replace("+00:00", "Z")
        if generated_at_utc and parse_utc(generated_at_utc)
        else datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )
    write_csv(csv_path, rows)
    eligible_rows = sum(1 for row in rows if row["daily_interval_eligible"])
    complete_bucket_rows = sum(
        1
        for row in rows
        if row["daily_interval_eligible"]
        and all(
            row["bucket_diagnostics"][bucket]["complete_price_coverage"]
            for bucket in RANK_BUCKETS
        )
    )
    return {
        "contract": CONTRACT,
        "status": "RESEARCH_ONLY_NOT_DEL_OWNER",
        "generated_at_utc": generated,
        "source_contract": SOURCE_CONTRACT,
        "return_method": "PRIOR_SNAPSHOT_FROZEN_RANK_COHORT_EQUAL_WEIGHT_PRICE_RETURN_WITH_FULL_MEMBERSHIP_PRICE_COVERAGE",
        "point_in_time": True,
        "lookahead_membership": False,
        "survivor_only_bucket_average_allowed": False,
        "raw_top150_dropout_price_fallback": True,
        "forward_fill": False,
        "interpolation": False,
        "row_count": len(rows),
        "eligible_daily_interval_row_count": eligible_rows,
        "complete_bucket_daily_row_count": complete_bucket_rows,
        "daily_interval_policy": {
            "target_hours": DAILY_INTERVAL_TARGET_HOURS,
            "minimum_hours": DAILY_INTERVAL_MIN_HOURS,
            "maximum_hours": DAILY_INTERVAL_MAX_HOURS,
            "basis": "SCALED_FROM_EXISTING_4H_3_5_TO_4_5_HOUR_SETTLED_INTERVAL_CONVENTION",
            "irregular_rows_retained_for_LINEAGE_but_returns_excluded_from_daily_series": True,
        },
        "csv_path": csv_path.as_posix(),
        "rows": rows,
        "lineage": lineage,
        "rank_proxy_semantics": {
            "RANK_3_25": "Prior snapshot filtered CoinGecko market-cap ranks 3-25, research proxy only.",
            "RANK_26_50": "Prior snapshot filtered CoinGecko market-cap ranks 26-50, research proxy only.",
            "RANK_51_100": "Prior snapshot filtered CoinGecko market-cap ranks 51-100, research proxy only.",
            "MICROCAPS": "DATA_UNAVAILABLE_CURRENT_OWNER_STOPS_AT_TOP100",
            "canonical_market_cap_band_mapping": False,
        },
        "del_activation": {
            "satisfies_required_owner_contract": False,
            "required_contract": REQUIRED_DEL_OWNER_CONTRACT,
            "required_status": "GOVERNED",
            "blockers": [
                "CANONICAL_MARKET_CAP_BUCKET_TAXONOMY_MISSING",
                "MICROCAP_RETURN_OWNER_MISSING",
                "RANK_PROXIES_MUST_NOT_BE_RELABELED_AS_CAP_BUCKETS",
            ],
        },
        "authority": {
            "research_only": True,
            "portfolio_execution": False,
            "canonical_market_state": False,
            "market_threshold_change": False,
            "model_weight_change": False,
            "del_activation": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--generated-at-utc")
    args = parser.parse_args()
    report = build_report(args.snapshot_root, args.output_csv, args.generated_at_utc)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "row_count": report["row_count"],
        "eligible_daily_interval_row_count": report["eligible_daily_interval_row_count"],
        "complete_bucket_daily_row_count": report["complete_bucket_daily_row_count"],
        "satisfies_del": report["del_activation"]["satisfies_required_owner_contract"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
