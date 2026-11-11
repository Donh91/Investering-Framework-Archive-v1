#!/usr/bin/env python3
"""Research Lab evidence-conversion PRE-FLIGHT, read-only, non-adjudicating.

No Git/network/API calls, no writes, no outcome promotion, no new owner.
Consumes only existing public machine summaries. Usage:
  python -m scripts.research.research_lab_evidence_conversion_preflight_v1 --repo-root .
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import stat
from collections import Counter
from pathlib import Path

REGISTRY = "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json"
ADMISSION = "research/experiment_lifecycle/LATEST_SCIENTIFIC_ADMISSION_REGISTRY.json"
SHARED_NEXT = "06_RESEARCH_LAB/shared_row_model_tournament_v1/NEXT_ACTION_STATE.json"
SHARED_RUNTIME = "06_RESEARCH_LAB/shared_row_model_tournament_v1/RUNTIME_STATUS.json"
FNP = "research/framework_memory/fnp_forward_rows/LATEST.json"
CN_STATE = "05_CYCLE_NAVIGATOR/autonomous_calibration_v1/STATE.json"
CN_LEDGER = "05_CYCLE_NAVIGATOR/forward_range_ledger/FORWARD_RANGE_LEDGER_v0_1.csv"
SOURCE_GATE = "scripts/experiments/source_git_anchor.py"
# Native Git blob of the observed exact main source gate. Deliberately pinned:
# ANY implementation change must be re-reviewed before the diagnostic may
# positively attest its temporal behavior. This is not an admission grant.
PINNED_SOURCE_GATE_GIT_BLOB_SHA1 = "247913a2cd8bfdd5e3e8154dc372876077992192"


def checked_path(root: Path, relative: str) -> Path:
    """Refuse symlinked ancestors/leaves, special files and out-of-root paths."""
    base = root.resolve(strict=True)
    rel = Path(relative)
    if rel.is_absolute() or not rel.parts or ".." in rel.parts:
        raise ValueError("SOURCE_MISSING_OR_UNTRUSTED:" + relative)
    target = base
    for part in rel.parts:
        target = target / part
        if target.is_symlink():
            raise ValueError("SOURCE_MISSING_OR_UNTRUSTED:" + relative)
    try:
        if (not target.resolve(strict=True).is_relative_to(base)
                or not stat.S_ISREG(target.stat(follow_symlinks=False).st_mode)):
            raise ValueError("SOURCE_MISSING_OR_UNTRUSTED:" + relative)
    except (OSError, RuntimeError) as exc:
        raise ValueError("SOURCE_MISSING_OR_UNTRUSTED:" + relative) from exc
    return target


def load(root: Path, relative: str) -> dict:
    target = checked_path(root, relative)
    value = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("INVALID_JSON_OBJECT:" + relative)
    return value


def audit(root: Path) -> dict:
    """Only descriptive, fail-closed preflight. Counts are not independent trials."""
    registry, admission = load(root, REGISTRY), load(root, ADMISSION)
    nxt, run = load(root, SHARED_NEXT), load(root, SHARED_RUNTIME)
    fnp, cn = load(root, FNP), load(root, CN_STATE)
    # Pin the *actual bytes*, not just comments and an if-condition that could
    # have its body changed to `return True`. Any new gate code => NOT_ATTESTED.
    try:
        source_code = checked_path(root, SOURCE_GATE).read_bytes()
    except ValueError as exc:
        raise ValueError("SOURCE_GATE_UNAVAILABLE") from exc
    git_blob = b"blob " + str(len(source_code)).encode("ascii") + b"\0" + source_code
    actual_git_blob_sha1 = hashlib.sha1(git_blob).hexdigest()
    deliberate_gate = actual_git_blob_sha1 == PINNED_SOURCE_GATE_GIT_BLOB_SHA1
    candidates = registry.get("candidates")
    rows = admission.get("candidates")
    if not isinstance(candidates, list) or not isinstance(rows, list):
        raise ValueError("REGISTRY_CANDIDATES_UNAVAILABLE")
    if not all(isinstance(x, dict) for x in candidates + rows):
        raise ValueError("REGISTRY_CANDIDATES_MALFORMED")
    declared = registry.get("candidate_count")
    scientific_declared = admission.get("candidate_count")
    if declared != len(candidates) or scientific_declared != len(rows):
        raise ValueError("REGISTRY_COUNT_DRIFT")
    ids = [x.get("candidate_id") for x in candidates]
    if any(not isinstance(x, str) or not x for x in ids) or len(ids) != len(set(ids)):
        raise ValueError("CANDIDATE_ID_DRIFT")
    admission_ids = [x.get("candidate_id") for x in rows]
    if (any(not isinstance(x, str) or not x for x in admission_ids)
            or len(admission_ids) != len(set(admission_ids))
            or set(admission_ids) != set(ids)):
        raise ValueError("ADMISSION_CANDIDATE_ID_DRIFT")
    status_counts = dict(Counter(x.get("status", "UNKNOWN") for x in rows))
    if status_counts != admission.get("status_counts"):
        raise ValueError("ADMISSION_STATUS_COUNT_DRIFT")

    matured = sum(int(x.get("matured_outcome_count", 0)) for x in candidates)
    eligible = sum(int(x.get("scientific_score_eligible_outcome_count", 0)) for x in candidates)
    reasons = Counter()
    for candidate in candidates:
        for reason, count in (candidate.get("scientific_score_nonadmission_counts_v1") or {}).items():
            reasons[str(reason)] += int(count)
    if matured < eligible or any(count < 0 for count in reasons.values()):
        raise ValueError("OUTCOME_COUNT_INVARIANT_BROKEN")
    raw_rows = nxt.get("evidence_summary", {}).get("eligible_rows_total")
    runtime_rows = run.get("eligible_prospective_rows")
    with checked_path(root, CN_LEDGER).open(newline="", encoding="utf-8") as f:
        ledger_rows = list(csv.DictReader(f))
    if not isinstance(raw_rows, int) or not isinstance(runtime_rows, int):
        raise ValueError("SHARED_ROW_COUNTER_UNAVAILABLE")
    if any(not isinstance(x, dict) for x in ledger_rows):
        raise ValueError("CN_LEDGER_MALFORMED")
    example_rows = sum("EXAMPLE_ONLY" in " ".join(str(y) for y in row.values()) for row in ledger_rows)
    real_ledger_rows = len(ledger_rows) - example_rows
    if real_ledger_rows < 0:
        raise ValueError("CN_LEDGER_COUNT_INVALID")
    return {
        "contract": "RESEARCH_LAB_EVIDENCE_CONVERSION_PREFLIGHT_v1",
        "status": "DIAGNOSTIC_ONLY_NOT_SCIENTIFIC_ADMISSION",
        "authority": {
            "read_only": True, "scientific_promotion": False,
            "live_forecast": False, "model_weights": False, "portfolio": False,
            "scheduler": False, "provider_calls": False
        },
        "experiment": {
            "candidate_count": len(candidates),
            "matured_outcome_count_candidate_summed_nonindependent": matured,
            "scientific_score_eligible_candidate_summed_nonindependent": eligible,
            "scientific_admission_status_counts": status_counts,
            "nonadmission_reason_counts": dict(sorted(reasons.items())),
            "timed_git_anchor_policy": (
                "EXPLICIT_FAIL_CLOSED_WITHOUT_TRUSTED_SERVER_ACCEPTANCE_CLOCK"
                if deliberate_gate else "NOT_ATTESTED_SOURCE_CHANGED"
            ),
            "source_gate_actual_git_blob_sha1": actual_git_blob_sha1,
            "source_gate_expected_git_blob_sha1": PINNED_SOURCE_GATE_GIT_BLOB_SHA1,
            "timed_anchor_correction_authorized": False,
            "next": "PROVE_TRUSTED_PROSPECTIVE_SERVER_ACCEPTANCE_CLOCK_OR_RETAIN_ZERO"
        },
        "shared_row": {
            "runtime_eligible_rows": runtime_rows,
            "next_action_reported_eligible_rows": raw_rows,
            "semantics": (
                "RECONCILE_ROW_GRAIN_AND_SOURCE_FIRST; DO_NOT_ASSUME_STALE_WRITER"
                if runtime_rows != raw_rows else "COUNTERS_EQUAL_UNVERIFIED_SEMANTICS"
            ),
            "reported_next_action": nxt.get("primary_action"),
            "terminal_verdict": nxt.get("terminal_verdict"),
            "matured_7d_rows_reported": nxt.get("evidence_summary", {}).get("matured_rows", {}).get("7d"),
        },
        "fnp": {
            "source_rows": fnp.get("current_source_row_count"),
            "ignored_source_receipts": fnp.get("source_receipts_ignored_nondivergence_or_other_contract"),
            "status": fnp.get("status"),
            "evaluator_available": fnp.get("authoritative_fnp_evaluator_available"),
            "next": "TRACE_EXISTING_OBSERVER_PRODUCER_AND_PERSISTENCE_WITH_NATIVE_RUN"
        },
        "cycle_navigator": {
            "calibration_reported_verified_rows": cn.get("eligible_verified_row_n"),
            "legacy_baseline_ledger_real_rows": real_ledger_rows,
            "legacy_baseline_ledger_example_rows": example_rows,
            "next": "BUILD_PROSPECTIVE_W47_PLUS_PAIRED_BASELINE_WITH_ORIGINAL_ISSUE_CLOCK"
        },
        "hard_limits": [
            "NO_AUTOMATIC_ANCHOR_RELAXATION",
            "NO_RETROACTIVE_SCIENTIFIC_ADMISSION",
            "NO_PROMOTION_FROM_COUNTS_OR_GREEN_CI",
            "NO_UNVERIFIED_SHARED_ROW_GRAIN_EQUALITY",
            "NO_PRIVATE_DATA_IN_PUBLIC_ARCHIVE",
            "NO_LIVE_TRADING_OR_FORECAST_CHANGE"
        ]
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()
    try:
        result = audit(args.repo_root.resolve())
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
        result = {
            "contract": "RESEARCH_LAB_EVIDENCE_CONVERSION_PREFLIGHT_v1",
            "status": "FAIL_CLOSED",
            "error": str(error),
            "scientific_promotion": False
        }
        print(json.dumps(result, sort_keys=True))
        raise SystemExit(2) from error
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
