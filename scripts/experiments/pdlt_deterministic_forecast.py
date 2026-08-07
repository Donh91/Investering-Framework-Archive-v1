from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

PROB_KEYS = ["p_pullback_72h","p_heavy_pullback_7d","p_persistent_distribution_14d"]


def canon(v: Any) -> bytes:
    return (json.dumps(v, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(v: Any) -> str:
    return hashlib.sha256(canon(v)).hexdigest()


def read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def prediction(probabilities: dict[str, float], evidence: list[str], valid: bool = True, abstain: str | None = None) -> dict[str, Any]:
    risk = max(float(probabilities.get(k, 0.0)) for k in PROB_KEYS) * 100.0
    return {
        "prediction_valid": valid,
        **{k: round(float(probabilities.get(k, 0.0)), 8) for k in PROB_KEYS},
        "expected_lead_time_hours": 0.0,
        "exit_risk_0_100": round(risk, 4),
        "top_3_evidence_fields": evidence[:3],
        "falsifier": "OUTCOME_MATURATION",
        "abstain_reason": abstain,
    }


def condition_matches(condition: dict[str, Any], deltas: dict[str, Any]) -> bool:
    symbol = condition["symbol"]
    field = condition["field"]
    value = deltas.get(symbol, {}).get(field)
    if not isinstance(value, (int, float)):
        return False
    threshold = float(condition["threshold"])
    op = condition.get("operator", "<=")
    if op == "<=":
        return float(value) <= threshold
    if op == ">=":
        return float(value) >= threshold
    raise ValueError(f"unsupported_operator:{op}")


def run(model: dict[str, Any], context_d: dict[str, Any]) -> dict[str, Any]:
    if model.get("contract") != "PDLT_FROZEN_MODEL_v1":
        raise ValueError("invalid_frozen_model")
    cfgi = context_d.get("cfgi")
    if not isinstance(cfgi, dict):
        raise ValueError("cfgi_missing_for_arm_b")
    deltas = cfgi.get("latest_deltas", {})
    baseline = model.get("baseline_probabilities", {})
    arm_a = prediction(baseline, ["UNCONDITIONAL_DISCOVERY_BASE_RATE"])
    b_probs = {k: float(baseline.get(k, 0.0)) for k in PROB_KEYS}
    fired: list[str] = []
    for candidate in model.get("candidates", []):
        if candidate.get("forward_eligible") is not True:
            continue
        conditions = candidate.get("conditions", [])
        if conditions and all(condition_matches(c, deltas) for c in conditions):
            fired.append(str(candidate.get("candidate_id")))
            probs = candidate.get("probabilities", {})
            for key in PROB_KEYS:
                if isinstance(probs.get(key), (int, float)):
                    b_probs[key] = max(b_probs[key], float(probs[key]))
    arm_b = prediction(b_probs, fired if fired else ["NO_CFGI_CANDIDATE_FIRED"])
    return {
        "contract": "PDLT_DETERMINISTIC_AB_v1",
        "experiment_id": "PDLT-v1.1-RUN",
        "cutoff_utc": context_d.get("cutoff_utc"),
        "model_sha256": sha(model),
        "context_sha256": sha(context_d),
        "fired_candidates": fired,
        "arm_a": arm_a,
        "arm_b": arm_b,
        "authority": "SHADOW_ONLY_NO_PORTFOLIO_AUTHORITY",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", type=Path, required=True)
    ap.add_argument("--context-d", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    value = run(read(args.model), read(args.context_d))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canon(value))
    print(json.dumps({"status":"PASS","fired_candidates":value["fired_candidates"],"model_sha256":value["model_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
