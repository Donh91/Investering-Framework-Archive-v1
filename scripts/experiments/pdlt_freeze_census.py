from __future__ import annotations

import argparse
import hashlib
import json
from datetime import timedelta
from pathlib import Path
from typing import Any


def canon(v: Any) -> bytes:
    return (json.dumps(v, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(v: Any) -> str:
    return hashlib.sha256(canon(v)).hexdigest()


def read(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    return json.loads(path.read_text())


def parse_dt(value: str):
    from datetime import datetime, timezone
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--census", type=Path, required=True)
    ap.add_argument("--model", type=Path, required=True)
    ap.add_argument("--ab", type=Path)
    ap.add_argument("--arm-c", type=Path)
    ap.add_argument("--arm-d", type=Path)
    ap.add_argument("--receipt-c", type=Path)
    ap.add_argument("--receipt-d", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    census = read(args.census)
    model = read(args.model)
    if census is None or model is None:
        raise SystemExit("census_or_model_missing")
    if census.get("model_ready") is not True or census.get("core_available") is not True:
        raise SystemExit("census_not_forecast_ready")
    cutoff = parse_dt(census["cutoff_utc"])
    ab = read(args.ab)
    c = read(args.arm_c)
    d = read(args.arm_d)
    rc = read(args.receipt_c)
    rd = read(args.receipt_d)
    arms: dict[str, Any] = {}
    if ab:
        arms["A"] = {"prediction": ab.get("arm_a"), "source_sha256": sha(ab)}
        if census.get("cfgi_available"):
            arms["B"] = {"prediction": ab.get("arm_b"), "source_sha256": sha(ab), "fired_candidates": ab.get("fired_candidates", [])}
    if c:
        arms["C"] = {"prediction": c, "source_sha256": sha(c), "receipt_sha256": sha(rc) if rc else None}
    if d and census.get("cfgi_available"):
        arms["D"] = {"prediction": d, "source_sha256": sha(d), "receipt_sha256": sha(rd) if rd else None}
    if "A" not in arms or "C" not in arms:
        raise SystemExit("minimum_arms_A_C_required")
    census_id = "PDLT-CENSUS-" + hashlib.sha256(canon({"cutoff":census["cutoff_utc"],"c":census["context_c_sha256"],"d":census.get("context_d_sha256")})).hexdigest()[:20]
    value = {
        "contract": "PDLT_FROZEN_CENSUS_v1",
        "forecast_id": census_id,
        "experiment_id": "PDLT-v1.1-RUN",
        "frozen_at_utc": census["cutoff_utc"],
        "cutoff_utc": census["cutoff_utc"],
        "outcome_due_utc": {
            "PULLBACK_72H": (cutoff + timedelta(hours=72)).isoformat().replace("+00:00", "Z"),
            "HEAVY_PULLBACK_7D": (cutoff + timedelta(days=7)).isoformat().replace("+00:00", "Z"),
            "PERSISTENT_DISTRIBUTION_14D": (cutoff + timedelta(days=14)).isoformat().replace("+00:00", "Z"),
        },
        "start_btc": census["context_c"]["latest"]["market_metrics"]["spot"]["BTCUSDT"]["close"],
        "model_sha256": sha(model),
        "outcome_thresholds": model.get("outcome_thresholds"),
        "context_c_sha256": census["context_c_sha256"],
        "context_d_sha256": census.get("context_d_sha256"),
        "arms": arms,
        "available_contrasts": [x for x, ok in {
            "B-A": "B" in arms,
            "D-C": "D" in arms,
            "C-A": "C" in arms,
            "D-B": "D" in arms and "B" in arms,
            "D-A": "D" in arms,
        }.items() if ok],
        "authority": {"canonical_promotion":False,"framework_state_change":False,"model_weight_change":False,"portfolio_action":False},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canon(value))
    print(json.dumps({"status":"PASS","forecast_id":census_id,"arms":sorted(arms),"contrasts":value["available_contrasts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
