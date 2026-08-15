from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

KEYS = (
    "btc_return_pct", "eth_return_pct", "ethbtc_return_pct",
    "btc_oi_change_pct", "eth_oi_change_pct",
    "btc_long_short_change_pct", "eth_long_short_change_pct",
)


def sign(value: Any) -> int:
    if not isinstance(value, (int, float)) or value == 0:
        return 0
    return 1 if value > 0 else -1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", type=Path, required=True)
    parser.add_argument("--director-output", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    context = json.loads(args.context.read_text())
    director = json.loads(args.director_output.read_text())
    intel = context.get("api_intelligence_v2") if isinstance(context.get("api_intelligence_v2"), dict) else {}
    horizons = intel.get("horizons") if isinstance(intel.get("horizons"), dict) else {}
    findings: list[dict[str, Any]] = []
    for horizon, row in horizons.items():
        if not isinstance(row, dict) or row.get("status") != "READY":
            continue
        signed = {key: sign(row.get(key)) for key in KEYS if sign(row.get(key)) != 0}
        positives = sorted(key for key, value in signed.items() if value > 0)
        negatives = sorted(key for key, value in signed.items() if value < 0)
        if positives and negatives:
            findings.append({"horizon_hours": horizon, "positive_metrics": positives, "negative_metrics": negatives})

    breadth = intel.get("breadth_delta") if isinstance(intel.get("breadth_delta"), dict) else {}
    breadth_sign = sign(breadth.get("advance_ratio_delta_pp"))
    director_two_sided = bool(director.get("evidence_for")) and bool(director.get("evidence_against"))
    multi_horizon_conflict = len(findings) >= 2
    breadth_cross_conflict = False
    if breadth_sign and findings:
        return_signs = []
        for finding in findings:
            if "btc_return_pct" in finding["positive_metrics"] or "eth_return_pct" in finding["positive_metrics"]:
                return_signs.append(1)
            if "btc_return_pct" in finding["negative_metrics"] or "eth_return_pct" in finding["negative_metrics"]:
                return_signs.append(-1)
        breadth_cross_conflict = any(value == -breadth_sign for value in return_signs)

    trigger = director.get("status") in {"READY", "DEGRADED"} and director_two_sided and (multi_horizon_conflict or breadth_cross_conflict)
    result = {
        "contract": "API_CONFLICT_ROUTER_v1",
        "conflict_review": trigger,
        "operational_only": True,
        "canonical_market_state": False,
        "multi_horizon_conflict": multi_horizon_conflict,
        "breadth_cross_conflict": breadth_cross_conflict,
        "findings": findings,
        "reason": "SIGNAL_FAMILY_DISAGREEMENT" if trigger else "NO_BOUNDED_CONFLICT_TRIGGER",
        "authority": {"framework_state_change": False, "portfolio_action": False, "market_rule_change": False},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    print(f"conflict_review={'true' if trigger else 'false'}")
    print(f"conflict_reason={result['reason']}")


if __name__ == "__main__":
    main()
