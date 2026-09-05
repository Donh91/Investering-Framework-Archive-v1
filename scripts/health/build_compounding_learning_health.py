from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXPECTED_DAYS = [7, 14, 30, 60, 90, 120, 180, 240]


def load(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text())
        return value if isinstance(value, dict) else None
    except Exception:
        return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.repo_root
    base = root / "00_ARCHIVE_CONTROL/research_governance_v1/compounding_learning_v1"
    paths = {
        "adjudication": root / "research/experiment_lifecycle/weekly_adjudication/LATEST.json",
        "state": base / "STATE.json",
        "proposal": base / "NEXT_BEST_EXPERIMENT.json",
        "backlog": base / "LEARNING_BACKLOG.json",
    }
    data = {key: load(path) for key, path in paths.items()}
    blockers: list[str] = []

    def fail(code: str) -> None:
        if code not in blockers:
            blockers.append(code)

    adjudication, state, proposal, backlog = (data[key] for key in ("adjudication", "state", "proposal", "backlog"))
    if not adjudication or adjudication.get("contract") != "UNIFIED_EXPERIMENTAL_LIFECYCLE_ADJUDICATION_v1":
        fail("UNIFIED_ADJUDICATION_UNAVAILABLE_OR_INVALID")
    if not state or state.get("contract") != "COMPOUNDING_LEARNING_CONTROLLER_STATE_v1":
        fail("COMPOUNDING_LEARNING_STATE_UNAVAILABLE_OR_INVALID")
    if not proposal or proposal.get("contract") != "NEXT_BEST_EXPERIMENT_PROPOSAL_v1":
        fail("NEXT_BEST_TEST_PROPOSAL_UNAVAILABLE_OR_INVALID")
    if not backlog or backlog.get("contract") != "LEARNING_BACKLOG_v1":
        fail("LEARNING_BACKLOG_UNAVAILABLE_OR_INVALID")

    if state:
        if (
            state.get("authority") != "RESEARCH_ONLY_NON_CANONICAL"
            or state.get("scientific_interpretation_owner") != "UNIFIED_EXPERIMENTAL_LIFECYCLE_ADJUDICATION_v1"
            or state.get("controller_role") != "NEXT_LEARNING_STRATEGY_ONLY"
        ):
            fail("COMPOUNDING_LEARNING_OWNERSHIP_BREACH")
        for key in (
            "canonical_effect", "portfolio_execution", "automatic_promotion", "automatic_canonical_write",
            "automatic_threshold_change", "automatic_weight_change", "automatic_market_rule_change",
            "model_weight_change", "retrospective_rescore_allowed", "frozen_parent_rewrite_allowed",
        ):
            if state.get(key) is not False:
                fail("COMPOUNDING_LEARNING_AUTHORITY_BREACH")
        if state.get("descriptive_checkpoint_days") != EXPECTED_DAYS:
            fail("COMPOUNDING_LEARNING_CHECKPOINT_SCHEDULE_INVALID")
        if adjudication and state.get("adjudication_generated_at_utc") != adjudication.get("generated_at_utc"):
            fail("COMPOUNDING_LEARNING_ADJUDICATION_DRIFT")
        expected_events = set(state.get("learning_event_ids") or [])
        event_dir = base / "events"
        actual_events = {path.stem for path in event_dir.glob("LE-*.json")} if event_dir.exists() else set()
        if not expected_events.issubset(actual_events):
            fail("COMPOUNDING_LEARNING_EVENT_HISTORY_INCOMPLETE")

    if proposal:
        for key in ("canonical_effect", "portfolio_execution", "model_weight_change", "automatic_promotion"):
            if proposal.get(key) is not False:
                fail("NEXT_BEST_TEST_AUTHORITY_BREACH")
        if proposal.get("proposal_status") != "NO_NEW_SCIENTIFICALLY_ELIGIBLE_CHILD_TEST":
            for key in ("problem_uncertainty", "hypothesis", "explicit_falsifier", "what_would_change_our_view", "expected_information_gain"):
                if not proposal.get(key):
                    fail("NEXT_BEST_TEST_CONTRACT_INCOMPLETE")
            if proposal.get("requires_scientific_admission") is not True or proposal.get("automatic_execution") is not False:
                fail("NEXT_BEST_TEST_SCIENTIFIC_ADMISSION_BYPASS")

    status = "PASS" if not blockers else "FAIL"
    output = {
        "contract": "COMPOUNDING_LEARNING_HEALTH_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": status,
        "blockers": blockers,
        "paths": {key: str(path.relative_to(root)) for key, path in paths.items()},
        "summary": {
            "run_disposition": state.get("run_disposition") if state else None,
            "hypothesis_family_count": len(state.get("hypothesis_families") or []) if state else None,
            "learning_event_count": len(state.get("learning_event_ids") or []) if state else None,
            "backlog_entry_count": backlog.get("entry_count") if backlog else None,
            "proposal_status": proposal.get("proposal_status") if proposal else None,
        },
        "authority": {"canonical_effect": False, "portfolio_execution": False},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "blockers": blockers}, sort_keys=True))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
