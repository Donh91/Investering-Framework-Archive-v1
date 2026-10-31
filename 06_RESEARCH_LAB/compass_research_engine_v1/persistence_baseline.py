"""Pure, deterministic paired-direction baseline, without source access.

An input row represents one prospective pre-outcome issuance and a matched
realized endpoint. This code does NOT adjudicate PIT eligibility, maturity,
independent clusters or edge. Caller must prove those separately.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping

UP, DOWN, SIDEWAYS = "UP", "DOWN", "SIDEWAYS"
DIRECTIONS = {UP, DOWN, SIDEWAYS}


def sign(value: float) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("NUMERIC_DELTA_REQUIRED")
    import math
    if not math.isfinite(value):
        raise ValueError("FINITE_DELTA_REQUIRED")
    return UP if value > 0 else DOWN if value < 0 else SIDEWAYS


def compare_pairs(rows: Iterable[Mapping[str, object]]) -> dict[str, object]:
    """Counts matched 12h observations. Does not claim statistical edge."""
    outcomes = []
    seen = set()
    excluded = {"unverified": 0, "unmatured": 0, "abstained": 0}
    total = 0
    for row in rows:
        total += 1
        cluster = row.get("cluster_id")
        if not isinstance(cluster, str) or not cluster or cluster in seen:
            raise ValueError("UNIQUE_CLUSTER_REQUIRED")
        seen.add(cluster)
        if row.get("pit_verified") is not True:
            excluded["unverified"] += 1
            continue
        if row.get("matured") is not True:
            excluded["unmatured"] += 1
            continue
        forecast = row.get("forecast_direction")
        actual = row.get("actual_direction")
        if forecast not in (UP, DOWN) or actual not in (UP, DOWN):
            excluded["abstained"] += 1
            continue
        baseline = sign(row.get("known_momentum_pct"))
        if baseline not in (UP, DOWN):
            excluded["abstained"] += 1
            continue
        outcomes.append((forecast == actual, baseline == actual))
    n = len(outcomes)
    return {
        "contract": "CRE_PAIRED_DIRECTION_DESCRIPTIVE_V1",
        "n_independent_clusters": n,
        "input_cluster_count": total,
        "excluded_unverified": excluded["unverified"],
        "excluded_unmatured": excluded["unmatured"],
        "excluded_abstained": excluded["abstained"],
        "forecast_correct": sum(f for f, _ in outcomes),
        "baseline_correct": sum(b for _, b in outcomes),
        "forecast_only_correct": sum(f and not b for f, b in outcomes),
        "baseline_only_correct": sum(b and not f for f, b in outcomes),
        "incremental_edge_certified": None,
        "authority": "RESEARCH_ONLY_NO_AUTOMATIC_CALIBRATION",
    }
