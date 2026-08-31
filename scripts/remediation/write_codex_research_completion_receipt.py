#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc
TELEMETRY_CONTRACT = "CODEX_EXECUTION_TELEMETRY_v1"
QUALITY_CONTRACT = "CODEX_EXECUTION_QUALITY_v1"
TELEMETRY_STATUSES = {"CAPTURED", "PARTIAL", "UNAVAILABLE"}
FIRST_TEST_OUTCOMES = {"PASS", "FAIL", "NOT_RUN"}
FAILURE_DIMENSIONS = {
    "TEST_FAILURE",
    "TOOL_FAILURE",
    "ENVIRONMENT_FAILURE",
    "CONTRACT_FAILURE",
    "SCOPE_FAILURE",
    "OTHER",
}
INTEGER_METRICS = {
    "tool_calls_before_first_edit",
    "read_search_calls_before_first_edit",
    "unique_files_read_before_first_edit",
    "edits_after_first_test",
    "total_edits",
    "files_changed",
    "test_cycles",
    "rework_cycles",
    "input_tokens",
    "output_tokens",
}
NUMBER_METRICS = {"elapsed_seconds_to_first_edit", "total_latency_seconds"}
BOOLEAN_METRICS = {"final_test_success"}
ENUM_METRICS = {"first_model_triggered_test_outcome"}
ALLOWED_METRICS = INTEGER_METRICS | NUMBER_METRICS | BOOLEAN_METRICS | ENUM_METRICS
ALLOWED_TELEMETRY_KEYS = {"contract", "telemetry_status", "evidence", "metrics", "failure_attribution"}


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def unavailable_execution_quality(*, legacy: bool = False) -> dict[str, Any]:
    block: dict[str, Any] = {
        "contract": QUALITY_CONTRACT,
        "telemetry_status": "UNAVAILABLE",
        "evidence": [],
        "metrics": {},
        "failure_attribution": [],
    }
    if legacy:
        block["legacy_receipt_without_telemetry"] = True
    return block


def _validate_nonnegative_int(name: str, value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"EXECUTION_TELEMETRY_INVALID_INTEGER:{name}")
    return value


def _validate_nonnegative_number(name: str, value: Any) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"EXECUTION_TELEMETRY_INVALID_NUMBER:{name}")
    return value


def normalize_execution_quality(data: dict[str, Any]) -> dict[str, Any]:
    if set(data) - ALLOWED_TELEMETRY_KEYS:
        raise ValueError("EXECUTION_TELEMETRY_UNKNOWN_TOP_LEVEL_FIELD")
    if data.get("contract") != TELEMETRY_CONTRACT:
        raise ValueError("EXECUTION_TELEMETRY_CONTRACT_INVALID")
    status = str(data.get("telemetry_status") or "")
    if status not in TELEMETRY_STATUSES:
        raise ValueError("EXECUTION_TELEMETRY_STATUS_INVALID")

    evidence = data.get("evidence", [])
    if not isinstance(evidence, list) or any(not isinstance(x, str) or not x.strip() for x in evidence):
        raise ValueError("EXECUTION_TELEMETRY_EVIDENCE_INVALID")

    metrics = data.get("metrics", {})
    if not isinstance(metrics, dict):
        raise ValueError("EXECUTION_TELEMETRY_METRICS_INVALID")
    unknown_metrics = set(metrics) - ALLOWED_METRICS
    if unknown_metrics:
        raise ValueError("EXECUTION_TELEMETRY_UNKNOWN_METRIC")

    normalized_metrics: dict[str, Any] = {}
    for name, value in metrics.items():
        if name in INTEGER_METRICS:
            normalized_metrics[name] = _validate_nonnegative_int(name, value)
        elif name in NUMBER_METRICS:
            normalized_metrics[name] = _validate_nonnegative_number(name, value)
        elif name in BOOLEAN_METRICS:
            if not isinstance(value, bool):
                raise ValueError(f"EXECUTION_TELEMETRY_INVALID_BOOLEAN:{name}")
            normalized_metrics[name] = value
        elif name == "first_model_triggered_test_outcome":
            if value not in FIRST_TEST_OUTCOMES:
                raise ValueError("EXECUTION_TELEMETRY_FIRST_TEST_OUTCOME_INVALID")
            normalized_metrics[name] = value

    attribution = data.get("failure_attribution", [])
    if not isinstance(attribution, list):
        raise ValueError("EXECUTION_TELEMETRY_FAILURE_ATTRIBUTION_INVALID")
    normalized_attribution: list[dict[str, str]] = []
    for item in attribution:
        if not isinstance(item, dict) or set(item) != {"dimension", "evidence_ref"}:
            raise ValueError("EXECUTION_TELEMETRY_FAILURE_ATTRIBUTION_INVALID")
        dimension = str(item.get("dimension") or "")
        evidence_ref = str(item.get("evidence_ref") or "")
        if dimension not in FAILURE_DIMENSIONS or not evidence_ref.strip():
            raise ValueError("EXECUTION_TELEMETRY_FAILURE_ATTRIBUTION_INVALID")
        normalized_attribution.append({"dimension": dimension, "evidence_ref": evidence_ref})

    if status in {"CAPTURED", "PARTIAL"} and not evidence:
        raise ValueError("EXECUTION_TELEMETRY_EVIDENCE_REQUIRED")
    if status in {"CAPTURED", "PARTIAL"} and not normalized_metrics and not normalized_attribution:
        raise ValueError("EXECUTION_TELEMETRY_OBSERVATION_REQUIRED")
    if status == "UNAVAILABLE" and (normalized_metrics or normalized_attribution):
        raise ValueError("EXECUTION_TELEMETRY_UNAVAILABLE_WITH_OBSERVATIONS")

    return {
        "contract": QUALITY_CONTRACT,
        "telemetry_status": status,
        "evidence": evidence,
        "metrics": normalized_metrics,
        "failure_attribution": normalized_attribution,
    }


def load_execution_quality(path: Path | None) -> dict[str, Any]:
    if path is None:
        return unavailable_execution_quality()
    data = read_json(path)
    if not isinstance(data, dict):
        raise ValueError("EXECUTION_TELEMETRY_DOCUMENT_INVALID")
    return normalize_execution_quality(data)


def build_completion_receipt(
    repo_root: Path,
    candidate_id: str,
    merge_commit_sha: str,
    pr_number: int,
    evidence: list[str],
    *,
    telemetry_path: Path | None = None,
    verified_at_utc: str | None = None,
) -> dict[str, Any]:
    state = read_json(repo_root / "LATEST_CODEX_EXECUTION_STATE.json")
    matches = [
        t for t in state.get("tasks", [])
        if isinstance(t, dict) and t.get("candidate_id") == candidate_id and t.get("source_type") == "RESEARCH_INTAKE"
    ]
    if len(matches) != 1:
        raise ValueError("RESEARCH_TASK_NOT_UNIQUE_OR_MISSING")
    task = matches[0]
    if task.get("state") not in {"IN_REMEDIATION", "POST_FIX_OBSERVATION"}:
        raise ValueError("TASK_NOT_IN_VERIFIABLE_REMEDIATION_STATE")
    if not evidence or any(not isinstance(x, str) or not x.strip() for x in evidence):
        raise ValueError("VERIFICATION_EVIDENCE_INVALID")

    receipt = {
        "contract": "CODEX_RESEARCH_COMPLETION_RECEIPT_v1",
        "status": "VERIFIED",
        "candidate_id": candidate_id,
        "signature": task.get("signature"),
        "candidate_sha256": task.get("candidate_sha256"),
        "task_contract_sha256": task.get("task_contract_sha256"),
        "pr_number": pr_number,
        "merge_commit_sha": merge_commit_sha,
        "verified_at_utc": verified_at_utc or now_iso(),
        "verification_evidence": evidence,
        "post_fix_gate": task.get("post_fix_gate"),
        "execution_quality": load_execution_quality(telemetry_path),
    }
    receipt["receipt_sha256"] = canonical_hash({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    return receipt


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, default=Path("."))
    p.add_argument("--candidate-id", required=True)
    p.add_argument("--merge-commit-sha", required=True)
    p.add_argument("--pr-number", type=int, required=True)
    p.add_argument("--evidence", action="append", required=True)
    p.add_argument(
        "--execution-telemetry-json",
        type=Path,
        help="Optional CODEX_EXECUTION_TELEMETRY_v1 document. Omit when deterministic process telemetry was not captured.",
    )
    args = p.parse_args()

    telemetry_path = args.execution_telemetry_json
    if telemetry_path is not None and not telemetry_path.is_absolute():
        telemetry_path = args.repo_root / telemetry_path
    receipt = build_completion_receipt(
        args.repo_root,
        args.candidate_id,
        args.merge_commit_sha,
        args.pr_number,
        args.evidence,
        telemetry_path=telemetry_path,
    )
    out = args.repo_root / "research/codex/completions" / f"{args.candidate_id}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "VERIFIED", "path": str(out), "receipt_sha256": receipt["receipt_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
