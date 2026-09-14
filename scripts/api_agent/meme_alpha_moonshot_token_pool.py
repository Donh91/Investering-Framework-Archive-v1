from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def number(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def integer(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def parse_time(value: Any) -> int:
    if not isinstance(value, str) or not value:
        return 0
    try:
        return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())
    except ValueError:
        return 0


def pool_quality_key(event: dict[str, Any], config: dict[str, Any]) -> tuple[Any, ...]:
    scanner = config.get("scanner") if isinstance(config.get("scanner"), dict) else {}
    micro = config.get("microstructure") if isinstance(config.get("microstructure"), dict) else {}
    minimum_liquidity = number(scanner.get("absolute_minimum_liquidity_usd"), 5000.0)
    minimum_sells = integer(micro.get("minimum_successful_sells"), 3)
    liquidity = number(event.get("liquidity_usd"))
    sells = integer(event.get("sells_h1"))
    transactions = integer(event.get("buys_h1")) + sells
    executable = int(liquidity >= minimum_liquidity and sells >= minimum_sells)
    return (
        executable,
        int(sells >= minimum_sells),
        liquidity,
        number(event.get("volume_h1_usd")),
        transactions,
        -number(event.get("age_minutes"), 10**9),
        str(event.get("pool_address") or ""),
    )


def pool_summary(event: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "pool_address", "pool_id", "dex_id", "pool_created_at", "age_minutes",
        "token_role", "token_price_usd", "liquidity_usd", "market_cap_usd",
        "volume_h1_usd", "buys_h1", "sells_h1", "price_change_h1_pct",
        "price_change_h6_pct", "raw_sha256",
    )
    return {key: event.get(key) for key in keys if key in event}


def collapse_token_pools(events: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        if not isinstance(event, dict):
            continue
        network = str(event.get("network") or "eth")
        token = str(event.get("token_ca") or "").lower()
        if not token:
            continue
        groups.setdefault(f"{network}:{token}", []).append(event)

    output: list[dict[str, Any]] = []
    for token_key in sorted(groups):
        rows = groups[token_key]
        canonical = max(rows, key=lambda row: pool_quality_key(row, config))
        row = dict(canonical)
        created_rows = [(parse_time(item.get("pool_created_at")), item) for item in rows]
        created_rows = [item for item in created_rows if item[0] > 0]
        earliest = min(created_rows, key=lambda item: item[0])[1] if created_rows else canonical
        ages = [number(item.get("age_minutes"), 0.0) for item in rows]
        token_age = max(ages) if ages else number(canonical.get("age_minutes"), 999999.0)

        aggregate_buys_h1 = sum(integer(item.get("buys_h1")) for item in rows)
        aggregate_sells_h1 = sum(integer(item.get("sells_h1")) for item in rows)
        aggregate_volume_h1 = sum(number(item.get("volume_h1_usd")) for item in rows)
        aggregate_liquidity = sum(max(0.0, number(item.get("liquidity_usd"))) for item in rows)
        denom_age = max(1.0, min(token_age, 60.0))

        # Discovery age belongs to the token, not whichever secondary pool currently has the best execution.
        row["age_minutes"] = token_age
        row["buyer_velocity_per_minute"] = aggregate_buys_h1 / denom_age
        row["transaction_velocity_per_minute"] = (aggregate_buys_h1 + aggregate_sells_h1) / denom_age
        row["volume_to_liquidity_h1"] = aggregate_volume_h1 / aggregate_liquidity if aggregate_liquidity > 0 else 0.0
        row["token_aggregate_buys_h1"] = aggregate_buys_h1
        row["token_aggregate_sells_h1"] = aggregate_sells_h1
        row["token_aggregate_volume_h1_usd"] = aggregate_volume_h1
        row["token_aggregate_liquidity_usd"] = aggregate_liquidity
        # Canonical-pool buys/sells/liquidity remain untouched for the execution gate.
        row["token_observed_earliest_pool_created_at"] = earliest.get("pool_created_at")
        row["observed_pool_count"] = len(rows)
        row["observed_pool_set"] = [pool_summary(item) for item in sorted(rows, key=lambda x: str(x.get("pool_address") or ""))]
        row["canonical_pool_basis"] = "IN_BATCH_EXECUTION_QUALITY"
        row["token_identity"] = token_key
        row["microstructure_basis"] = "TOKEN_AGE_WITH_MULTI_POOL_AGGREGATION"
        output.append(row)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Collapse a new-pools feed to one deterministic token-level observation per exact CA.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text())
    config = json.loads(args.config.read_text())
    if not isinstance(payload, dict) or not isinstance(payload.get("events"), list):
        raise SystemExit("MOONSHOT_SCAN_BATCH_events_required")
    result = dict(payload)
    result["raw_pool_event_count"] = len(payload["events"])
    result["events"] = collapse_token_pools(payload["events"], config)
    result["token_event_count"] = len(result["events"])
    result["pool_identity_contract"] = "MOONSHOT_TOKEN_POOL_IDENTITY_v2"
    result["microstructure_contract"] = "MOONSHOT_TOKEN_MICROSTRUCTURE_AGGREGATION_v2"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_bytes(result))
    print(json.dumps({"raw_pool_events": result["raw_pool_event_count"], "token_events": result["token_event_count"], "contract": result["pool_identity_contract"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
