from __future__ import annotations

import statistics
from typing import Iterable, Mapping


def gate_state(price: float, threshold: float) -> bool:
    if price <= 0:
        raise ValueError("price must be positive")
    return price > threshold


def make_dual_source_row(
    *,
    session_date: str,
    owner_close: float | None,
    challenger_close: float | None,
    owner_settled: bool,
    challenger_settled: bool,
    thresholds: Iterable[float] = (0.0275, 0.03),
) -> dict:
    row = {
        "session_date": session_date,
        "owner_close": owner_close,
        "challenger_close": challenger_close,
        "owner_settled": owner_settled,
        "challenger_settled": challenger_settled,
        "owner_available": owner_close is not None,
        "challenger_available": challenger_close is not None,
        "close_deviation_bps": None,
        "gate_agreement": {},
    }
    if owner_close is not None and challenger_close is not None and owner_settled and challenger_settled:
        row["close_deviation_bps"] = abs(challenger_close / owner_close - 1.0) * 10_000.0
        row["gate_agreement"] = {
            str(level): gate_state(owner_close, level) == gate_state(challenger_close, level)
            for level in thresholds
        }
    return row


def summarize_live_dual_source(rows: Iterable[Mapping], contract: Mapping) -> dict:
    material = list(rows)
    overlap = [
        row for row in material
        if row.get("owner_available")
        and row.get("challenger_available")
        and row.get("owner_settled")
        and row.get("challenger_settled")
        and row.get("close_deviation_bps") is not None
    ]
    deviations = [float(row["close_deviation_bps"]) for row in overlap]
    thresholds = [str(value) for value in contract["thresholds"]]
    agreement = {
        level: (sum(bool(row["gate_agreement"].get(level)) for row in overlap) / len(overlap) if overlap else None)
        for level in thresholds
    }
    sorted_dev = sorted(deviations)
    p95 = sorted_dev[min(len(sorted_dev) - 1, int(round(0.95 * (len(sorted_dev) - 1))))] if sorted_dev else None
    metrics = {
        "live_overlap_sessions": len(overlap),
        "median_abs_close_dev_bps": statistics.median(deviations) if deviations else None,
        "p95_abs_close_dev_bps": p95,
        "max_abs_close_dev_bps": max(deviations) if deviations else None,
        "gate_agreement": agreement,
        "owner_outage_sessions": sum(not row.get("owner_available", False) for row in material),
        "challenger_only_confirmations": sum(
            not row.get("owner_available", False)
            and row.get("challenger_available", False)
            and row.get("challenger_settled", False)
            for row in material
        ),
    }
    enough = len(overlap) >= int(contract["minimum_live_overlap_sessions"])
    dev_pass = bool(deviations) and (
        metrics["median_abs_close_dev_bps"] <= contract["median_abs_close_dev_bps_max"]
        and metrics["p95_abs_close_dev_bps"] <= contract["p95_abs_close_dev_bps_max"]
        and metrics["max_abs_close_dev_bps"] <= contract["max_abs_close_dev_bps_max"]
    )
    gate_pass = bool(overlap) and all(
        value is not None and value >= contract["gate_agreement_rate_min"]
        for value in agreement.values()
    )
    metrics["owner_substitution_eligible"] = enough and dev_pass and gate_pass
    metrics["authority"] = "DUAL_SOURCE_OWNER_SUBSTITUTION_ELIGIBLE" if metrics["owner_substitution_eligible"] else "CHALLENGER_CONFIRMATION_ONLY"
    return metrics
