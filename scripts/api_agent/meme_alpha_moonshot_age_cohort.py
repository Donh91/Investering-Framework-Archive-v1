from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

AGE_BUCKETS: list[tuple[int, int | None]] = [
    (0, 15),
    (15, 30),
    (30, 60),
    (60, 120),
    (120, 240),
    (240, 480),
    (480, 960),
    (960, 1440),
    (1440, None),
]
FIELDS = {
    "buyer_velocity": "buyer_velocity_per_minute",
    "transaction_velocity": "transaction_velocity_per_minute",
    "volume_to_liquidity": "volume_to_liquidity_h1",
    "liquidity_resilience": "liquidity_usd",
}
MIN_PEERS = 5
PRE_ORIGIN_CONTRACT = "MOONSHOT_PRE_ORIGIN_EVENT_COHORT_v2"


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def number(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def age_bucket_index(age_minutes: float) -> int:
    age = max(0.0, age_minutes)
    for idx, (lo, hi) in enumerate(AGE_BUCKETS):
        if age >= lo and (hi is None or age < hi):
            return idx
    return len(AGE_BUCKETS) - 1


def bucket_label(index: int) -> str:
    lo, hi = AGE_BUCKETS[index]
    return f"{lo}-{hi if hi is not None else 'inf'}m"


def percentile_rank(values: list[float], value: float) -> float:
    finite = [x for x in values if math.isfinite(x)]
    if not finite:
        return 0.0
    less = sum(1 for x in finite if x < value)
    equal = sum(1 for x in finite if x == value)
    return 100.0 * (less + 0.5 * equal) / len(finite)


def peer_indices(events: list[dict[str, Any]], target_index: int) -> tuple[list[int], str]:
    bucket_members: dict[int, list[int]] = {idx: [] for idx in range(len(AGE_BUCKETS))}
    for idx, event in enumerate(events):
        bucket_members[age_bucket_index(number(event.get("age_minutes"), 999999.0))].append(idx)
    selected = list(bucket_members[target_index])
    if len(selected) >= MIN_PEERS:
        return selected, "EXACT_AGE_BUCKET"
    for radius in range(1, len(AGE_BUCKETS)):
        for neighbor in (target_index - radius, target_index + radius):
            if 0 <= neighbor < len(AGE_BUCKETS):
                selected.extend(bucket_members[neighbor])
        selected = sorted(set(selected))
        if len(selected) >= MIN_PEERS:
            return selected, "ADJACENT_AGE_BUCKET_EXPANSION"
    return list(range(len(events))), "GLOBAL_FALLBACK_LOW_N"


def normalize_age_cohorts(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rank exact-CA-collapsed new-pool events by age.

    These percentiles are intentionally *pre-origin*.  A new-pool feed can contain
    an old token receiving a new pool, so this ranking is a discovery prefilter,
    never final token-birth truth and never sufficient for adaptive training.
    """
    output: list[dict[str, Any]] = []
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            continue
        target_bucket = age_bucket_index(number(event.get("age_minutes"), 999999.0))
        peers, scope = peer_indices(events, target_bucket)
        peer_events = [events[i] for i in peers if isinstance(events[i], dict)]
        row = dict(event)
        row["birth_cohort_percentiles"] = {
            name: round(percentile_rank([number(peer.get(source)) for peer in peer_events], number(event.get(source))), 3)
            for name, source in FIELDS.items()
        }
        row["birth_cohort"] = {
            "contract": PRE_ORIGIN_CONTRACT,
            "role": "DISCOVERY_PREFILTER_ONLY",
            "population": "EXACT_CA_COLLAPSED_NEW_POOL_EVENTS_PRE_ORIGIN",
            "age_bucket": bucket_label(target_bucket),
            "peer_count": len(peer_events),
            "scope": scope,
            "age_comparable": scope != "GLOBAL_FALLBACK_LOW_N",
            "may_train_adaptive_rules": False,
            "may_directly_create_user_alert": False,
        }
        output.append(row)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Age-normalize pre-origin Moonshot discovery events.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text())
    if not isinstance(payload, dict) or not isinstance(payload.get("events"), list):
        raise SystemExit("MOONSHOT_SCAN_BATCH_events_required")
    result = dict(payload)
    result["events"] = normalize_age_cohorts(payload["events"])
    result["cohort_contract"] = PRE_ORIGIN_CONTRACT
    result["cohort_role"] = "DISCOVERY_PREFILTER_ONLY"
    result["pre_origin_population_warning"] = "New-pool events can include existing tokens. Origin adjudication is required before learning or alert admission."
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_bytes(result))
    print(json.dumps({"events": len(result["events"]), "cohort_contract": result["cohort_contract"], "cohort_role": result["cohort_role"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
