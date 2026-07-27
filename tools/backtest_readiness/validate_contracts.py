#!/usr/bin/env python3
"""Validate frozen BACKTEST BUILD architecture contracts.

This tool performs engineering validation only. It does not load market data,
run economic tests, or produce framework/portfolio decisions.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
ARCH = ROOT / "04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/architecture"

OWNER_PATH = ARCH / "OWNER_DATASET_REGISTRY_v1.json"
GATE_PATH = ARCH / "READINESS_GATE_v2.json"
MATRIX_PATH = ARCH / "TEST_MATRIX_v1.json"
FIXTURE_PATH = ROOT / "tests/backtest_readiness/fixtures/temporal_contract_cases.json"

ALLOWED_ROLES = {
    "OWNER_SELECTED",
    "OWNER_CANDIDATE",
    "OWNER_CANDIDATE_BINANCE_SPECIFIC",
    "OWNER_PENDING_BYTE_AUDIT",
    "OWNER_BLOCKED_INCOMPLETE",
    "CHALLENGER_SELECTED",
    "CHALLENGER_ONLY",
    "CHALLENGER_OKX_SPECIFIC",
    "CHALLENGER",
    "CANDIDATE",
    "FIXTURE_SELECTED",
}

ECONOMIC_PREFIXES = ("BT",)


@dataclass(frozen=True)
class ValidationResult:
    errors: list[str]
    warnings: list[str]
    checks: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def ensure_unique(values: Iterable[str], label: str, errors: list[str]) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    if duplicates:
        errors.append(f"{label} contains duplicates: {sorted(duplicates)}")


def parse_utc(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError(f"timestamp is not timezone-aware: {value}")
    return parsed


def validate_owner_registry(registry: dict[str, Any]) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[str] = []

    if registry.get("registry_id") != "BACKTEST_OWNER_DATASET_REGISTRY_v1":
        errors.append("unexpected registry_id")
    checks.append("registry_id")

    packages = registry.get("package_roots")
    datasets = registry.get("datasets")
    if not isinstance(packages, list) or not packages:
        errors.append("package_roots must be a non-empty list")
        packages = []
    if not isinstance(datasets, list) or not datasets:
        errors.append("datasets must be a non-empty list")
        datasets = []

    ensure_unique((str(item.get("package_id")) for item in packages), "package_ids", errors)
    ensure_unique((str(item.get("dataset_id")) for item in datasets), "dataset_ids", errors)
    checks.extend(["package_id_uniqueness", "dataset_id_uniqueness"])

    package_ids = {item.get("package_id") for item in packages}
    for dataset in datasets:
        dataset_id = str(dataset.get("dataset_id"))
        role = dataset.get("role")
        if role not in ALLOWED_ROLES:
            errors.append(f"{dataset_id}: unsupported role {role!r}")

        source_package = dataset.get("source_package")
        if source_package and source_package not in package_ids:
            errors.append(f"{dataset_id}: unknown source_package {source_package}")

        allowed = dataset.get("allowed_tests", [])
        forbidden = set(dataset.get("forbidden_tests", []))
        overlap = forbidden.intersection(allowed)
        if overlap:
            errors.append(f"{dataset_id}: tests both allowed and forbidden: {sorted(overlap)}")

        authority = str(dataset.get("authority", ""))
        if "DERIVED" in authority:
            for test in allowed:
                if "BT04" in test or "H7" in test or "DIRECT_GATE" in test:
                    errors.append(f"{dataset_id}: derived dataset allowed in direct gate test {test}")

        if role == "OWNER_BLOCKED_INCOMPLETE" and not dataset.get("blocking_conditions"):
            errors.append(f"{dataset_id}: blocked owner lacks blocking_conditions")

    selected_by_test: dict[str, list[str]] = {}
    for dataset in datasets:
        role = str(dataset.get("role", ""))
        if role not in {"OWNER_SELECTED"}:
            continue
        for test_id in dataset.get("allowed_tests", []):
            selected_by_test.setdefault(test_id, []).append(str(dataset.get("dataset_id")))

    for test_id, owners in selected_by_test.items():
        # Multiple owners are permitted only when they represent explicitly different
        # assets required by the same test, not duplicate owners for one metric.
        if len(owners) != len(set(owners)):
            errors.append(f"{test_id}: duplicate selected owner IDs")

    checks.extend([
        "roles",
        "package_references",
        "direct_derived_authority",
        "allowed_forbidden_disjoint",
    ])
    return ValidationResult(errors, warnings, checks)


def validate_gate(gate: dict[str, Any]) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[str] = []

    if gate.get("gate_id") != "BACKTEST_READINESS_GATE_v2":
        errors.append("unexpected gate_id")

    policy = gate.get("execution_policy", {})
    if policy.get("economic_backtest_allowed") is not False:
        errors.append("economic_backtest_allowed must remain false")
    if policy.get("parameter_search_allowed") is not False:
        errors.append("parameter_search_allowed must remain false")

    rows = gate.get("mandatory_gates", [])
    ensure_unique((str(row.get("gate")) for row in rows), "mandatory_gates", errors)
    by_id = {row.get("gate"): row for row in rows}

    expected = {f"G{i:02d}" for i in range(1, 21)}
    actual_prefixes = {str(key).split("_")[0] for key in by_id}
    missing = expected - actual_prefixes
    if missing:
        errors.append(f"missing mandatory gate prefixes: {sorted(missing)}")

    g20 = next((row for row in rows if str(row.get("gate", "")).startswith("G20_")), None)
    if not g20 or g20.get("status") != "NO":
        errors.append("G20 must remain NO until artifact-backed approval")

    g02 = next((row for row in rows if str(row.get("gate", "")).startswith("G02_")), None)
    if g02 and g02.get("status") == "PASS":
        warnings.append("G02 is PASS; confirm final master byte audit receipt exists")

    checks.extend(["execution_lock", "gate_uniqueness", "gate_coverage", "G20_lock"])
    return ValidationResult(errors, warnings, checks)


def iter_tests(matrix: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any]]]:
    for family, rows in matrix.get("families", {}).items():
        for row in rows:
            yield family, row


def validate_matrix(matrix: dict[str, Any]) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[str] = []

    rows = list(iter_tests(matrix))
    ensure_unique((str(row.get("test_id")) for _, row in rows), "test_ids", errors)

    for family, row in rows:
        test_id = str(row.get("test_id", ""))
        if not test_id:
            errors.append(f"{family}: test missing test_id")
        if not row.get("primary_endpoint"):
            errors.append(f"{test_id}: missing primary_endpoint")
        if not row.get("status"):
            errors.append(f"{test_id}: missing status")
        if family == "CANONICAL_HYPOTHESES":
            if not row.get("owner_data"):
                errors.append(f"{test_id}: canonical hypothesis missing owner_data")
            if not row.get("split"):
                errors.append(f"{test_id}: canonical hypothesis missing split rule")

    global_rules = matrix.get("global_rules", {})
    if global_rules.get("economic_execution_authorized") is not False:
        errors.append("economic_execution_authorized must remain false")
    if global_rules.get("primary_endpoint_can_change_after_execution") is not False:
        errors.append("primary endpoint mutation must remain forbidden")
    if global_rules.get("holdout_can_be_rerun_after_failure") is not False:
        errors.append("holdout rerun after failure must remain forbidden")

    checks.extend(["test_id_uniqueness", "primary_endpoints", "canonical_contracts", "global_locks"])
    return ValidationResult(errors, warnings, checks)


def validate_temporal_fixtures(fixtures: dict[str, Any]) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[str] = []

    cases = fixtures.get("cases", [])
    ensure_unique((str(case.get("case_id")) for case in cases), "temporal_case_ids", errors)

    for case in cases:
        case_id = str(case.get("case_id"))
        try:
            knowledge = parse_utc(case["knowledge_at_utc"])
            decision = parse_utc(case["decision_at_utc"])
            execution = parse_utc(case["execution_at_utc"])
            label_end = parse_utc(case["label_end_utc"])
            valid = knowledge <= decision <= execution < label_end
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"{case_id}: malformed temporal fixture: {exc}")
            continue

        expected_valid = bool(case.get("expected_valid"))
        if valid != expected_valid:
            errors.append(f"{case_id}: expected_valid={expected_valid}, computed={valid}")

    checks.append("temporal_fixture_expectations")
    return ValidationResult(errors, warnings, checks)


def merge_results(results: Iterable[ValidationResult]) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[str] = []
    for result in results:
        errors.extend(result.errors)
        warnings.extend(result.warnings)
        checks.extend(result.checks)
    return ValidationResult(errors, warnings, checks)


def run_validation() -> ValidationResult:
    registry = load_json(OWNER_PATH)
    gate = load_json(GATE_PATH)
    matrix = load_json(MATRIX_PATH)
    fixtures = load_json(FIXTURE_PATH)
    return merge_results([
        validate_owner_registry(registry),
        validate_gate(gate),
        validate_matrix(matrix),
        validate_temporal_fixtures(fixtures),
    ])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, help="Optional JSON result path")
    args = parser.parse_args()

    try:
        result = run_validation()
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        payload = {"status": "FAIL", "errors": [str(exc)], "warnings": [], "checks": []}
        print(json.dumps(payload, indent=2))
        return 1

    payload = {
        "status": "PASS" if result.ok else "FAIL",
        "errors": result.errors,
        "warnings": result.warnings,
        "checks": sorted(set(result.checks)),
        "economic_backtest_executed": False,
        "readiness_gate_G20": "NO",
    }

    rendered = json.dumps(payload, indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
