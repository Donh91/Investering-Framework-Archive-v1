#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
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
        if not asset_id or price is None or isinstance(rank, bool) or not isinstance(rank, int):
            continue
        rows[asset_id] = {
            "asset_id": asset_id,
            "price_usd": price,
            "filtered_rank": rank,
            "market_cap_usd": market_cap,
        }
    return rows


def simple_return(previous_price: float | None, current_price: float | None) -> float | None:
    if previous_price is None or current_price is None or previous_price <= 0:
        return None
    return current_price / previous_price - 1.0


def cohort_return(
    prior_rows: dict[str, dict[str, Any]],
    current_rows: dict[str, dict[str, Any]],
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
    for row in cohort:
        current = current_rows.get(row["asset_id"])
        value = simple_return(
            finite_positive(row.get("price_usd")),
            finite_positive(current.get("price_usd")) if current else None,
        )
        if value is not None:
            returns.append(value)
            matched_assets.append(row["asset_id"])
        cap = finite_positive(row.get("market_cap_usd"))
        if cap is not None:
            market_caps.append(cap)
    return {
        "return": (sum(returns) / len(returns)) if returns else None,
        "cohort_count": len(cohort),
        "matched_count": len(returns),
        "matched_fraction": (len(returns) / len(cohort)) if cohort else None,
        "prior_market_cap_min_usd": min(market_caps) if market_caps else None,
        "prior_market_cap_median_usd": statistics.median(market_caps) if market_caps else None,
        "prior_market_cap_max_usd": max(market_caps) if market_caps else None,
        "matched_asset_ids": matched_assets,
    }


def build_rows(snapshot_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    snapshots = canonical_daily_snapshots(snapshot_root)
    output_rows: list[dict[str, Any]] = []
    lineage: list[dict[str, Any]] = []

    for index in range(1, len(snapshots)):
        prior_ts, prior_path, prior = snapshots[index - 1]
        current_ts, current_path, current = snapshots[index]
        prior_rows = constituent_map(prior)
        current_rows = constituent_map(current)
        gap_days = (current_ts.date() - prior_ts.date()).days

        btc = simple_return(
            finite_positive((prior_rows.get("bitcoin") or {}).get("price_usd")),
            finite_positive((current_rows.get("bitcoin") or {}).get("price_usd")),
        )
        eth = simple_return(
            finite_positive((prior_rows.get("ethereum") or {}).get("price_usd")),
            finite_positive((current_rows.get("ethereum") or {}).get("price_usd")),
        )
        buckets = {
            name: cohort_return(prior_rows, current_rows, low, high)
            for name, (low, high) in RANK_BUCKETS.items()
        }

        row = {
            "date": current_ts.date().isoformat(),
            "prior_date": prior_ts.date().isoformat(),
            "gap_days": gap_days,
            "consecutive_calendar_day": gap_days == 1,
            "BTC": btc,
            "ETH": eth,
            "RANK_3_25": buckets["RANK_3_25"]["return"],
            "RANK_26_50": buckets["RANK_26_50"]["return"],
            "RANK_51_100": buckets["RANK_51_100"]["return"],
            "MICROCAPS": None,
            "bucket_diagnostics": buckets,
        }
        output_rows.append(row)
        lineage.append({
            "date": row["date"],
            "prior_snapshot": prior_path.as_posix(),
            "current_snapshot": current_path.as_posix(),
            "prior_retrieval_timestamp": prior_ts.isoformat().replace("+00:00", "Z"),
            "current_retrieval_timestamp": current_ts.isoformat().replace("+00:00", "Z"),
            "prior_membership_hash": ((prior.get("universe") or {}).get("membership_hash")),
            "current_membership_hash": ((current.get("universe") or {}).get("membership_hash")),
        })
    return output_rows, lineage


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["date", "BTC", "ETH", "RANK_3_25", "RANK_26_50", "RANK_51_100", "MICROCAPS"]
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
    return {
        "contract": CONTRACT,
        "status": "RESEARCH_ONLY_NOT_DEL_OWNER",
        "generated_at_utc": generated,
        "source_contract": SOURCE_CONTRACT,
        "return_method": "PRIOR_SNAPSHOT_FROZEN_RANK_COHORT_EQUAL_WEIGHT_PRICE_RETURN",
        "point_in_time": True,
        "lookahead_membership": False,
        "forward_fill": False,
        "interpolation": False,
        "row_count": len(rows),
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
        "satisfies_del": report["del_activation"]["satisfies_required_owner_contract"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
