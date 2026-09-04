#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from compounding_learning_engine import build_state
from compounding_learning_utils import enrich_registry_with_candidate_specs, parse_utc, read_json, write_json
from experiment_lifecycle import canon, registry

ROOT = Path(__file__).resolve().parents[2]
COMPOUNDING_ROOT = ROOT / "research/experiment_lifecycle/compounding_learning"
COMPOUNDING_POLICY = COMPOUNDING_ROOT / "POLICY.json"
COMPOUNDING_STATE = COMPOUNDING_ROOT / "LATEST.json"
COMPOUNDING_NEXT = COMPOUNDING_ROOT / "NEXT_BEST_EXPERIMENT.json"
ADMISSION = ROOT / "research/experiment_lifecycle/LATEST_SCIENTIFIC_ADMISSION_REGISTRY.json"
ADJUDICATION = ROOT / "research/experiment_lifecycle/weekly_adjudication/LATEST.json"
MONTHLY = ROOT / "research/monthly_learning_council/STATE.json"


def materialize_compounding_learning(value: dict, candidate_root: Path, now: str) -> dict:
    if not COMPOUNDING_POLICY.exists():
        return {"status": "NOT_CONFIGURED"}
    enriched = enrich_registry_with_candidate_specs(value, candidate_root)
    state, nxt, changed = build_state(
        enriched,
        read_json(ADMISSION, {}),
        read_json(ADJUDICATION, {}),
        read_json(MONTHLY, {}),
        read_json(COMPOUNDING_POLICY, {}),
        read_json(COMPOUNDING_STATE, {}),
        parse_utc(now),
    )
    if changed or not COMPOUNDING_STATE.exists():
        write_json(COMPOUNDING_STATE, state)
        write_json(COMPOUNDING_NEXT, nxt)
    return {
        "status": state.get("status"),
        "changed": changed,
        "new_checkpoint_candidate_count": state.get("new_checkpoint_candidate_count", 0),
        "primary_action": state.get("primary_action"),
        "target": state.get("target"),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate-root", type=Path, required=True)
    ap.add_argument("--observation-root", type=Path, required=True)
    ap.add_argument("--forecast-root", type=Path, required=True)
    ap.add_argument("--outcome-root", type=Path, required=True)
    ap.add_argument("--receipt-root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    value = registry(
        args.candidate_root,
        args.observation_root,
        args.forecast_root,
        args.outcome_root,
        args.receipt_root,
        now,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canon(value))
    compounding = materialize_compounding_learning(value, args.candidate_root, now)
    print(canon({
        "status": "PASS",
        "candidate_count": value["candidate_count"],
        "state_counts": value["state_counts"],
        "compounding_learning": compounding,
    }).decode().strip())


if __name__ == "__main__":
    main()
