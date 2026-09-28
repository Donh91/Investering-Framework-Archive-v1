#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

AUTHORITY = "RESEARCH_ONLY_NON_CANONICAL"
ALLOWED_ACTIONS = {"WAIT_FOR_MORE_EVIDENCE", "RESEARCH_NEW_HYPOTHESIS"}


def read_json(path: Path):
    return json.loads(path.read_text())


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    args = ap.parse_args()
    repo = args.repo_root.resolve()
    base = repo / "05_CYCLE_NAVIGATOR/internal_learning"
    state = read_json(base / "STATE.json")
    policy = read_json(base / "POLICY.json")
    ledger = read_jsonl(repo / "05_CYCLE_NAVIGATOR/track_record/CN_INTERNAL_PRECISION_LEDGER.jsonl")

    if state.get("contract") != "CN_PRECISION_LEARNING_STATE_v1":
        raise SystemExit("CN_PRECISION_LEARNING_BAD_STATE_CONTRACT")
    if state.get("authority") != AUTHORITY:
        raise SystemExit("CN_PRECISION_LEARNING_BAD_AUTHORITY")

    for key in (
        "canonical_effect",
        "portfolio_execution",
        "paid_data_authorized",
        "deep_research_authorized",
        "external_provider_calls_authorized",
        "automatic_promotion",
        "automatic_threshold_change",
        "automatic_weight_change",
        "public_surface_effect",
    ):
        if state.get(key) is not False:
            raise SystemExit(f"CN_PRECISION_LEARNING_FIREWALL:{key}")

    if state.get("primary_action") not in ALLOWED_ACTIONS:
        raise SystemExit("CN_PRECISION_LEARNING_BAD_ACTION")

    if policy.get("public_surface_locked") is not True or policy.get("internal_additive_only") is not True:
        raise SystemExit("CN_PRECISION_LEARNING_POLICY_FIREWALL_MISSING")

    historical_families = sorted({k for row in ledger for k in (row.get("family_scores") or {})})
    current_families = sorted((state.get("family_states") or {}).keys())
    if historical_families != current_families:
        raise SystemExit(
            f"CN_PRECISION_LEARNING_FAMILY_HISTORY_LOSS:{historical_families}!={current_families}"
        )

    if ledger:
        latest = sorted(
            ledger,
            key=lambda r: (
                int(r["completed_iso_year"]),
                int(r["completed_iso_week"]),
                int(r.get("issue_scored", 0)),
            ),
        )[-1]
        if state.get("last_settled_score_key") != latest.get("score_key"):
            raise SystemExit("CN_PRECISION_LEARNING_LATEST_SCORE_KEY_MISMATCH")

        snapshot = repo / state["latest_weekly_snapshot"]
        if not snapshot.exists():
            raise SystemExit("CN_PRECISION_LEARNING_WEEKLY_SNAPSHOT_MISSING")
        snap = read_json(snapshot)
        if snap.get("score_key") != latest.get("score_key"):
            raise SystemExit("CN_PRECISION_LEARNING_WEEKLY_SCORE_KEY_MISMATCH")
        if snap.get("public_surface_effect") is not False:
            raise SystemExit("CN_PRECISION_LEARNING_WEEKLY_PUBLIC_FIREWALL")

    checkpoint_path = state.get("latest_checkpoint")
    if checkpoint_path:
        cp = repo / checkpoint_path
        if not cp.exists():
            raise SystemExit("CN_PRECISION_LEARNING_CHECKPOINT_MISSING")
        value = read_json(cp)
        for key in ("canonical_effect", "portfolio_execution", "public_surface_effect"):
            if value.get(key) is not False:
                raise SystemExit(f"CN_PRECISION_LEARNING_CHECKPOINT_FIREWALL:{key}")
        review = value.get("api_review")
        if isinstance(review, dict) and review.get("forecast_candidates") not in (None, []):
            raise SystemExit("CN_PRECISION_LEARNING_API_FORECAST_CANDIDATE_LEAK")

    print(
        json.dumps(
            {
                "status": "PASS",
                "latest_score_key": state.get("last_settled_score_key"),
                "settled_week_count": state.get("settled_week_count"),
                "checkpoint_sequence": state.get("checkpoint_sequence"),
                "family_count": len(current_families),
                "primary_action": state.get("primary_action"),
                "public_surface_effect": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
