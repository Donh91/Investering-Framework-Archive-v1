from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Direct script execution sets sys.path[0] to scripts/daily_capture, not repository root.
# Bootstrap only the local repo import path; this performs no network/data access.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backtest_engine.blind_dual_run import collect_from_latest_capture


B2_EXPERIMENT_ID = "G0-B2-AMENDED-FULL-REDUCED-v1"
B2_EXPERIMENT_STATUS = "CLOSED_NON_TESTABLE_PROVENANCE_UNRECOVERABLE"
R2_TERMINAL_VERDICT = "ROTATION_PROVENANCE_UNRECOVERABLE_CLOSE_B2"


def apply_r2_closed_identity_overlay(coverage_path: Path) -> dict[str, Any]:
    """Close the current B2 identity without altering market or policy semantics.

    The underlying pair/identifying counters remain visible for engineering health and
    provenance continuity. The current frozen experiment identity is no longer eligible
    to become B2-ready, even if generic identifying-coverage arithmetic would otherwise
    cross its historical thresholds.
    """
    coverage = json.loads(coverage_path.read_text())
    for lane in coverage.get("per_lane", {}).values():
        lane["identifying_coverage_threshold_met"] = bool(lane.get("b2_coverage_ready"))
        lane["b2_coverage_ready"] = False
        lane["coverage_band"] = "B2_CLOSED_NON_TESTABLE"
        lane["closure_reason"] = "FINAL_BOUNDED_ROTATION_PROVENANCE_UNRECOVERABLE"
    coverage.update(
        {
            "experiment_identity": B2_EXPERIMENT_ID,
            "experiment_status": B2_EXPERIMENT_STATUS,
            "terminal_research_verdict": R2_TERMINAL_VERDICT,
            "evidence_class": "NON_B2_EVIDENCE",
            "evidence_purpose": "HEALTH_ONLY",
            "b2_analysis_authorized": False,
            "readiness_basis": "B2_IDENTITY_CLOSED_PROVENANCE_UNRECOVERABLE",
            "r3_authorized": False,
        }
    )
    coverage_path.write_text(json.dumps(coverage, sort_keys=True, separators=(",", ":")) + "\n")
    return coverage


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture-root", type=Path, required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    ap.add_argument("--sensor-registry", type=Path, required=True)
    ap.add_argument("--policy-registry", type=Path, required=True)
    ap.add_argument("--rotation-evaluator", type=Path, required=True)
    ap.add_argument("--crosswalk-contract", type=Path, required=True)
    args = ap.parse_args()
    result = collect_from_latest_capture(
        capture_root=args.capture_root,
        output_root=args.output_root,
        sensor_registry_path=args.sensor_registry,
        policy_registry_path=args.policy_registry,
        rotation_evaluator_path=args.rotation_evaluator,
        crosswalk_contract_path=args.crosswalk_contract,
    )
    closed = apply_r2_closed_identity_overlay(Path(result["coverage"]))
    result["experiment_identity"] = closed["experiment_identity"]
    result["experiment_status"] = closed["experiment_status"]
    result["evidence_class"] = closed["evidence_class"]
    result["evidence_purpose"] = closed["evidence_purpose"]
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
