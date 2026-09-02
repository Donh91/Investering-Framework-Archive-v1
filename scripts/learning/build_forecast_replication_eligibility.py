#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

CONTRACT = "FORECAST_REPLICATION_ELIGIBILITY_v1"
SETTLEMENT_CONTRACT = "MODEL_CALIBRATION_SETTLEMENT_ELIGIBILITY_v1"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"


def receipts(root: Path):
    if not root.exists():
        return
    for path in sorted(root.rglob("*.json")):
        try:
            value = load(path)
        except Exception:
            continue
        if value.get("contract") == "EXPERIMENT_EXECUTION_RECEIPT_v1":
            yield path, value


def build(settlement: dict[str, Any], receipt_root: Path, min_independent_forecasts: int, max_disagreement_rate: float) -> dict[str, Any]:
    if settlement.get("contract") != SETTLEMENT_CONTRACT:
        raise ValueError("SETTLEMENT_ELIGIBILITY_CONTRACT_MISMATCH")
    if settlement.get("eligibility_scope") != "SETTLEMENT_TIMING_ONLY":
        raise ValueError("SETTLEMENT_ELIGIBILITY_SCOPE_NOT_EXPLICIT")
    eligible_ids = {
        str(row.get("forecast_id"))
        for row in settlement.get("rows", [])
        if row.get("settlement_score_eligible") is True or row.get("scientific_score_eligible") is True
    }
    by_forecast: dict[str, list[dict[str, Any]]] = {fid: [] for fid in eligible_ids}
    for path, receipt in receipts(receipt_root) or []:
        fid = receipt.get("local_frozen_forecast_id")
        if fid in by_forecast:
            by_forecast[str(fid)].append({**receipt, "_path": path.as_posix()})

    rows = []
    agreements = 0
    disagreements = 0
    independently_assessed = 0
    for fid in sorted(eligible_ids):
        matches = by_forecast.get(fid, [])
        verified = [r for r in matches if r.get("component_recompute_performed") is True and r.get("independent_data_verification_performed") is True]
        mismatch = any(r.get("replication_status") == "REPLICATION_MISMATCH" for r in verified)
        agree = any(r.get("replication_status") in {"REPLICATED_FIRED", "REPLICATED_NOT_FIRED"} for r in verified) and not mismatch
        if verified:
            independently_assessed += 1
        if mismatch:
            disagreements += 1
        elif agree:
            agreements += 1
        rows.append({
            "forecast_id": fid,
            "receipt_count": len(matches),
            "independent_verified_receipt_count": len(verified),
            "independent_replication_assessed": bool(verified),
            "replication_agreement": True if agree else (False if mismatch else None),
            "replication_statuses": sorted({str(r.get("replication_status")) for r in matches if r.get("replication_status")}),
        })

    denominator = agreements + disagreements
    disagreement_rate = (disagreements / denominator) if denominator else None
    if independently_assessed < min_independent_forecasts:
        status = "BLOCKED_INSUFFICIENT_INDEPENDENT_REPLICATION"
    elif disagreement_rate is None:
        status = "BLOCKED_NO_INDEPENDENT_REPLICATION_OUTCOMES"
    elif disagreement_rate > max_disagreement_rate:
        status = "FAIL_DISAGREEMENT_RATE"
    else:
        status = "PASS"
    return {
        "contract": CONTRACT,
        "status": status,
        "settlement_eligible_forecast_count": len(eligible_ids),
        "independently_assessed_forecast_count": independently_assessed,
        "agreement_forecast_count": agreements,
        "disagreement_forecast_count": disagreements,
        "disagreement_rate": disagreement_rate,
        "max_disagreement_rate": max_disagreement_rate,
        "minimum_independent_forecasts": min_independent_forecasts,
        "rows": rows,
        "scientific_skill_authority": False,
        "authority": {"portfolio_action": False, "model_weight_change": False, "automatic_promotion": False, "forecast_skill_claim": False},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--settlement-eligibility", type=Path, required=True)
    ap.add_argument("--receipt-root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--min-independent-forecasts", type=int, default=20)
    ap.add_argument("--max-disagreement-rate", type=float, default=0.05)
    args = ap.parse_args()
    result = build(load(args.settlement_eligibility), args.receipt_root, args.min_independent_forecasts, args.max_disagreement_rate)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(canon(result))
    print(json.dumps({k: result[k] for k in ("status", "settlement_eligible_forecast_count", "independently_assessed_forecast_count", "agreement_forecast_count", "disagreement_forecast_count", "disagreement_rate")}, sort_keys=True))


if __name__ == "__main__":
    main()
