"""Task 2 frozen R1 pairwise falsification, public metadata only.

RESEARCH DEVELOPMENT ONLY. No original first-known, no prospective sample,
no source reconstruction from revised values, no trading rule or model tuning.
Inputs are the two pinned October 2026 public original research receipts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPLORATORY = ROOT / "04_MARKET_LEARNING/handlekompas/research/2026-10-14__TASK2_R1_EXPLORATORY_BASELINE_AND_SIMULATION_RELEASE_v1.json"
ADMISSION = ROOT / "04_MARKET_LEARNING/handlekompas/research/2026-10-15__TASK2_R1_NATIVE_V3_ORIGINAL_ADMISSION_v2.json"
EXPLORATORY_BLOB = "656c2c9db472ba7f42a548bb932e244d93ca5890"
ADMISSION_BLOB = "9e728b835de294e5777222c171a89874a69dae95"
DIRECTIONS = {"UP", "DOWN"}
ASSETS = ("BTC", "ETH")


def git_blob(payload: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\\x00" + payload).hexdigest()


def frozen_read(path: Path, expected_blob: str) -> dict:
    raw = path.read_bytes()
    if git_blob(raw) != expected_blob:
        raise ValueError("PINNED_PUBLIC_RESEARCH_BLOB_CHANGED")
    return json.loads(raw)


def analyze(source: dict, admission: dict) -> dict:
    """Matched published sign-only controls, never scientific-edge admission."""
    population = source.get("measured_exploratory_population") or {}
    cohort = admission.get("cohort") or {}
    attempts = admission.get("rows") or []
    cases = population.get("source_rows") or []
    if (source.get("contract") != "TASK2_R1_EXPLORATORY_BASELINE_AND_R2_R7_RELEASE_SPEC_v1"
            or admission.get("contract") != "TASK2_R1_NATIVE_V3_ORIGINAL_ADMISSION_v2"
            or admission.get("status") != "RESEARCH_ONLY_NOT_ADMITTED"
            or cohort.get("original_attempts") != 11
            or cohort.get("original_outcomes_present") != 9
            or cohort.get("original_outcomes_absent") != 2
            or cohort.get("admitted") != 0
            or cohort.get("independent_market_event_families_certified") != 0
            or len(attempts) != 11 or len(cases) != 9):
        raise ValueError("ORIGINAL_R1_FROZEN_ROSTER_OR_SCIENTIFIC_GATE_CHANGED")
    index = {r["forecast_id"]: r for r in attempts}
    if len(index) != 11 or len({r["id"] for r in cases}) != 9:
        raise ValueError("DUPLICATE_ORIGINAL_ATTEMPT")
    included = {r["id"] for r in cases}
    if included != {r["forecast_id"] for r in attempts if r["original_outcome_status"] == "PRESENT"}:
        raise ValueError("SELECTED_OUTCOMES_NOT_ORIGINAL_PRESENT_CENSUS")
    for r in cases:
        prior = index[r["id"]]
        if (prior["admissibility"] != "NOT_ADMITTED"
                or prior["independent_market_event_family"] is not None
                or prior["first_user_delivery_at_utc"] is not None
                or prior["original_forecast_path"] != r["original_forecast_path"]
                or prior["original_forecast_git_blob_sha"] != r["original_forecast_git_blob"]
                or prior["original_outcome_git_blob_sha"] != r["original_outcome_git_blob"]):
            raise ValueError("UNBOUND_OR_PRETENDED_PIT_ORIGINAL")
    output = {}
    for asset in ASSETS:
        paired = []
        abstain = 0
        all_outcomes = Counter()
        per_day = {}
        for r in cases:
            actual = r.get(f"recorded_12h_{asset}_realized_sign")
            model = r.get("original_next_12h_direction")
            baseline = r.get(f"prior_packet_{asset}_delta_sign")
            if actual not in DIRECTIONS or baseline not in DIRECTIONS:
                raise ValueError("OUTCOME_OR_ORIGINAL_BASELINE_NOT_DIRECTIONAL")
            all_outcomes[actual] += 1
            if model not in DIRECTIONS:
                if model not in {"MIXED", "SIDEWAYS", "UNAVAILABLE", "NO_EDGE"}:
                    raise ValueError("UNREGISTERED_FORECAST_ABSTENTION")
                abstain += 1
                continue
            paired.append((r, model, baseline, actual))
            per_day.setdefault(r["id"][4:12], []).append((model == actual, baseline == actual))
        n = len(paired)
        if n + abstain != 9:
            raise ValueError("NONRECONCILING_PAIRED_DENOMINATOR")
        f = sum(model == actual for _, model, _, actual in paired)
        b = sum(base == actual for _, _, base, actual in paired)
        only_f = sum(model == actual and base != actual for _, model, base, actual in paired)
        only_b = sum(model != actual and base == actual for _, model, base, actual in paired)
        if f - b != only_f - only_b:
            raise ValueError("PAIRED_DISCORDANCE_ARITHMETIC_BROKEN")
        output[asset] = {
            "original_outcomes": len(cases),
            "matched_directional_pairs": n,
            "excluded_original_abstention": abstain,
            "forecast_correct": f,
            "previous_packet_momentum_correct": b,
            "forecast_only_correct": only_f,
            "baseline_only_correct": only_b,
            "forecast_identical_to_momentum": sum(m == base for _, m, base, _ in paired),
            "always_up_correct_on_same_pairs": sum(actual == "UP" for _, _, _, actual in paired),
            "always_down_correct_on_same_pairs": sum(actual == "DOWN" for _, _, _, actual in paired),
            "inverse_direction_correct_on_same_pairs": n - f,
            "per_issue_day": {
                day: {"paired": len(vals), "forecast_correct": sum(x for x, _ in vals),
                      "momentum_correct": sum(y for _, y in vals)}
                for day, vals in sorted(per_day.items())
            },
            "not_independent_trials": True,
        }
    targets = Counter(r["target_at_utc"] for r in cases)
    return {
        "contract": "TASK2_R1_PAIRED_FALSIFICATION_DEVELOPMENT_v1",
        "classification": "EXPOST_ALREADY_INSPECTED_NOT_PIT_NOT_HOLDOUT",
        "source_public_git_blobs": {"exploratory": EXPLORATORY_BLOB, "admission": ADMISSION_BLOB},
        "attempts": 11, "original_matured_outcomes": 9, "missing_original_outcomes": 2,
        "original_first_known_admitted": 0,
        "independent_market_families_certified": 0,
        "unique_target_utc_clocks": len(targets),
        "target_clock_repeat_groups": sum(count > 1 for count in targets.values()),
        "by_asset": output,
        "scientific_information_edge_admitted": False,
        "investor_action_edge_admitted": False,
        "after_cost_execution_tested": False,
        "selected_challenger_for_production": None,
        "notes": [
            "All public outcome signs in this cohort were already inspected before analysis.",
            "Both assets and multiple issues share outcomes and shock families; n=8 per asset is descriptive, not eight independent events.",
            "The baseline is originally recorded previous-packet delta sign, not a synthetic one-hour return.",
            "Always-direction and inverted controls are retrospective diagnostics, never competing promoted models.",
            "No first-delivery, provider first-known or independent event-family certification exists.",
        ],
    }


def execute() -> dict:
    return analyze(frozen_read(EXPLORATORY, EXPLORATORY_BLOB),
                   frozen_read(ADMISSION, ADMISSION_BLOB))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = execute()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\\n"
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload, encoding="utf-8")
    print(payload)
