#!/usr/bin/env python3
"""Prospective, non-binding T8 Multi-Ping Aggregation instrumentation.

Rows are created only from already-accepted DATA PING packets that explicitly
contain a MULTI_PING_AGGREGATION feature block. Missing fields remain UNKNOWN.
Outcomes are attached append-only from a later source-bound framework state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SOURCE_CONTRACT = "T8_MULTI_PING_SOURCE_ROW_v1"
OUTCOME_CONTRACT = "T8_MULTI_PING_OUTCOME_v1"
LATEST_CONTRACT = "T8_MULTI_PING_LATEST_v1"
AUTHORITY = {
    "research_only": True,
    "binding": False,
    "independent_authority": False,
    "canonical_acceptance": False,
    "portfolio_action": False,
    "market_gate_change": False,
    "model_weight_change": False,
    "automatic_signal_promotion": False,
}


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha(value: Any) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def parse_time(value: str) -> datetime:
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.utcoffset() is None:
        raise ValueError("timezone_required")
    return dt.astimezone(timezone.utc)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"object_required:{path}")
    return value


def write_immutable(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = canon(value)
    if path.exists():
        if path.read_bytes() != raw:
            raise ValueError(f"immutable_conflict:{path}")
        return
    path.write_bytes(raw)


def _multi_ping_block(packet: dict[str, Any]) -> dict[str, Any] | None:
    for key in ("MULTI_PING_AGGREGATION", "multi_ping_aggregation"):
        value = packet.get(key)
        if isinstance(value, dict):
            return value
    framework = packet.get("framework_interpretation")
    if isinstance(framework, dict):
        for key in ("MULTI_PING_AGGREGATION", "multi_ping_aggregation"):
            value = framework.get(key)
            if isinstance(value, dict):
                return value
    return None


def _window_count(value: Any) -> int:
    if isinstance(value, bool):
        raise ValueError("window_runs_invalid")
    if isinstance(value, int):
        count = value
    elif isinstance(value, list):
        count = len(value)
    else:
        raise ValueError("window_runs_required")
    if count not in {3, 4}:
        raise ValueError("window_runs_must_be_3_or_4")
    return count


def _state(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field}_required")
    return value.strip()


def _optional_enum(value: Any, allowed: set[str], default: str = "UNKNOWN") -> str:
    if value is None:
        return default
    text = str(value).strip().upper()
    if text not in allowed:
        raise ValueError("invalid_optional_enum:" + text)
    return text


def _number_or_none(value: Any, field: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field}_must_be_number_or_null")
    return float(value)


def source_row(packet: dict[str, Any], source_path: str) -> dict[str, Any] | None:
    if packet.get("contract") != "ACCEPTED_DATA_PING_PACKET_v1":
        raise ValueError("accepted_data_ping_contract_required")
    if packet.get("acceptance_status") != "ACCEPTED":
        raise ValueError("accepted_status_required")
    freeze_utc = str(packet.get("freeze_utc") or "")
    parse_time(freeze_utc)
    snapshot_id = _state(packet.get("snapshot_id"), "snapshot_id")
    block = _multi_ping_block(packet)
    if block is None:
        return None
    if block.get("authority") != "FORWARD_TEST_ONLY":
        raise ValueError("multi_ping_authority_must_be_FORWARD_TEST_ONLY")

    latest = _state(block.get("latest_ping_state"), "latest_ping_state")
    aggregated = _state(block.get("aggregated_state"), "aggregated_state")
    delay = _number_or_none(block.get("delay_minutes"), "delay_minutes")
    if delay is None or delay < 0:
        raise ValueError("nonnegative_delay_minutes_required")

    dependency = _optional_enum(
        block.get("dependency_to_latest_ping"),
        {"UNKNOWN", "DEPENDENT", "PARTIALLY_DEPENDENT", "INDEPENDENTLY_SUPPORTED"},
    )
    redundancy = _optional_enum(
        block.get("redundancy_class"),
        {"UNKNOWN", "REDUNDANT", "PARTIALLY_REDUNDANT", "NON_REDUNDANT"},
    )
    unique_information_gain = _number_or_none(block.get("unique_information_gain"), "unique_information_gain")
    if unique_information_gain is not None and not -1.0 <= unique_information_gain <= 1.0:
        raise ValueError("unique_information_gain_out_of_bounds")

    packet_hash = sha(packet)
    row_id = "T8-" + hashlib.sha256(f"{snapshot_id}|{freeze_utc}|{packet_hash}".encode()).hexdigest()[:20]
    return {
        "contract": SOURCE_CONTRACT,
        "test_id": "MULTI_PING_AGGREGATION_VALUE",
        "row_id": row_id,
        "authority": AUTHORITY,
        "source_packet": {
            "snapshot_id": snapshot_id,
            "freeze_utc": freeze_utc,
            "source_path": source_path,
            "sha256": packet_hash,
        },
        "benchmark": "LATEST_PING_ONLY",
        "window_run_count": _window_count(block.get("window_runs")),
        "latest_ping_state": latest,
        "aggregation_state": aggregated,
        "state_flip_reduced_at_freeze": block.get("state_flip_reduced"),
        "delay_minutes": delay,
        "data_quality": block.get("data_quality", "UNKNOWN"),
        "dependency_to_latest_ping": dependency,
        "redundancy_class": redundancy,
        "unique_information_gain": unique_information_gain,
        "eventual_framework_state": None,
        "false_flip_count": None,
        "false_flip_reduction": None,
        "delay_cost": None,
        "delay_cost_status": "UNRESOLVED_NO_REGISTERED_COST_FUNCTION",
        "right_censored": True,
        "retrospective_creation": False,
        "historical_chat_reconstruction": False,
    }


def materialize_packet(packet_path: Path, output_root: Path, repo_root: Path) -> dict[str, Any]:
    packet = read_json(packet_path)
    try:
        source_ref = packet_path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        source_ref = packet_path.as_posix()
    row = source_row(packet, source_ref)
    if row is None:
        return {"status": "NOOP_NO_MULTI_PING_BLOCK", "packet": source_ref, "authority": AUTHORITY}

    path = output_root / "source_rows" / f"{row['row_id']}.json"
    write_immutable(path, row)
    latest = {
        "contract": LATEST_CONTRACT,
        "status": "SOURCE_ROW_FROZEN",
        "row_id": row["row_id"],
        "source_row_path": path.as_posix(),
        "source_row_sha256": sha(row),
        "authority": AUTHORITY,
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "LATEST.json").write_bytes(canon(latest))
    return latest


def scan(accepted_root: Path, output_root: Path, repo_root: Path) -> dict[str, Any]:
    accepted_root.mkdir(parents=True, exist_ok=True)
    considered = 0
    frozen = 0
    noop = 0
    errors: list[dict[str, str]] = []
    for path in sorted(accepted_root.rglob("*.json")):
        considered += 1
        try:
            result = materialize_packet(path, output_root, repo_root)
            if result["status"] == "SOURCE_ROW_FROZEN":
                frozen += 1
            else:
                noop += 1
        except ValueError as exc:
            errors.append({"path": path.as_posix(), "error": str(exc)})
    summary = {
        "contract": "T8_MULTI_PING_SCAN_v1",
        "status": "PASS" if not errors else "DEGRADED",
        "considered_packets": considered,
        "source_rows_frozen_or_verified": frozen,
        "no_multi_ping_block": noop,
        "errors": errors,
        "authority": AUTHORITY,
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "LATEST_SCAN.json").write_bytes(canon(summary))
    return summary


def attach_outcome(
    source_path: Path,
    framework_state: str,
    observed_at_utc: str,
    evidence_ref: str,
    evidence_sha256: str,
    output_root: Path,
) -> dict[str, Any]:
    source = read_json(source_path)
    if source.get("contract") != SOURCE_CONTRACT:
        raise ValueError("source_row_contract_required")
    parse_time(observed_at_utc)
    source_time = parse_time(source["source_packet"]["freeze_utc"])
    outcome_time = parse_time(observed_at_utc)
    if outcome_time <= source_time:
        raise ValueError("outcome_must_be_after_source_freeze")
    if not isinstance(evidence_ref, str) or not evidence_ref.strip():
        raise ValueError("evidence_ref_required")
    if not isinstance(evidence_sha256, str) or len(evidence_sha256) != 64:
        raise ValueError("evidence_sha256_required")
    framework_state = _state(framework_state, "eventual_framework_state")

    latest_error = int(source["latest_ping_state"] != framework_state)
    aggregation_error = int(source["aggregation_state"] != framework_state)
    outcome = {
        "contract": OUTCOME_CONTRACT,
        "test_id": "MULTI_PING_AGGREGATION_VALUE",
        "row_id": source["row_id"],
        "authority": AUTHORITY,
        "source_row_sha256": sha(source),
        "source_freeze_utc": source["source_packet"]["freeze_utc"],
        "outcome_observed_at_utc": observed_at_utc,
        "outcome_evidence_ref": evidence_ref,
        "outcome_evidence_sha256": evidence_sha256,
        "eventual_framework_state": framework_state,
        "latest_ping_error_indicator": latest_error,
        "aggregation_error_indicator": aggregation_error,
        "false_flip_count": {
            "latest_ping_only": latest_error,
            "multi_ping_aggregation": aggregation_error,
        },
        "false_flip_reduction": latest_error - aggregation_error,
        "delay_minutes": source["delay_minutes"],
        "delay_cost": None,
        "delay_cost_status": "UNRESOLVED_NO_REGISTERED_COST_FUNCTION",
        "dependency_to_latest_ping": source["dependency_to_latest_ping"],
        "redundancy_class": source["redundancy_class"],
        "unique_information_gain": source["unique_information_gain"],
        "right_censored": False,
        "source_row_rewritten": False,
    }
    path = output_root / "outcomes" / source["row_id"] / f"{evidence_sha256}.json"
    write_immutable(path, outcome)
    return {"status": "OUTCOME_ATTACHED", "path": path.as_posix(), "outcome_sha256": sha(outcome), "authority": AUTHORITY}


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p_packet = sub.add_parser("packet")
    p_packet.add_argument("--packet", type=Path, required=True)
    p_packet.add_argument("--output-root", type=Path, required=True)
    p_packet.add_argument("--repo-root", type=Path, default=Path("."))

    p_scan = sub.add_parser("scan")
    p_scan.add_argument("--accepted-root", type=Path, required=True)
    p_scan.add_argument("--output-root", type=Path, required=True)
    p_scan.add_argument("--repo-root", type=Path, default=Path("."))

    p_out = sub.add_parser("outcome")
    p_out.add_argument("--source-row", type=Path, required=True)
    p_out.add_argument("--framework-state", required=True)
    p_out.add_argument("--observed-at-utc", required=True)
    p_out.add_argument("--evidence-ref", required=True)
    p_out.add_argument("--evidence-sha256", required=True)
    p_out.add_argument("--output-root", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "packet":
        result = materialize_packet(args.packet, args.output_root, args.repo_root)
    elif args.command == "scan":
        result = scan(args.accepted_root, args.output_root, args.repo_root)
    else:
        result = attach_outcome(
            args.source_row,
            args.framework_state,
            args.observed_at_utc,
            args.evidence_ref,
            args.evidence_sha256,
            args.output_root,
        )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
