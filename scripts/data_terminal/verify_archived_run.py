#!/usr/bin/env python3
"""Deterministically replay and verify an archived Data Terminal shadow run."""
from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path
from typing import Any, Iterable

AUTHORITY_KEYS = ("binding", "canonical_acceptance", "state_change", "portfolio_action")
EXPECTED_ARCHIVE_FILES = {
    "latest_data_ping_handoff.json",
    "latest_terminal_state.json",
    "source_health.json",
}


class ReplayVerificationError(RuntimeError):
    """Raised when an archived replay gate fails."""


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def load_json_bytes(payload: bytes, name: str) -> Any:
    try:
        return json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReplayVerificationError(f"JSON_PARSE_FAIL:{name}:{exc}") from exc


def iter_dicts(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_dicts(child)


def verify_false_authority_blocks(documents: dict[str, Any]) -> int:
    count = 0
    for document in documents.values():
        for candidate in iter_dicts(document):
            if all(key in candidate for key in AUTHORITY_KEYS):
                count += 1
                if any(candidate[key] is not False for key in AUTHORITY_KEYS):
                    raise ReplayVerificationError("AUTHORITY_FLAG_NOT_FALSE")
    if count == 0:
        raise ReplayVerificationError("AUTHORITY_BLOCKS_NOT_FOUND")
    return count


def verify_missing_unknown(documents: dict[str, Any]) -> tuple[int, int]:
    reference_count = 0
    unique_rows: set[tuple[str, str, str]] = set()
    for name in ("receipt", "snapshot", "handoff"):
        for row in documents[name].get("missing", []):
            reference_count += 1
            if not isinstance(row, dict) or row.get("status") != "UNKNOWN":
                raise ReplayVerificationError(f"MISSING_NOT_UNKNOWN:{name}")
            if row.get("value") == 0:
                raise ReplayVerificationError(f"MISSING_COERCED_TO_ZERO:{name}")
            unique_rows.add((str(row.get("field")), str(row.get("source_date")), str(row.get("status"))))
    return reference_count, len(unique_rows)


def verify_receipt_hash(receipt: dict[str, Any]) -> None:
    expected = receipt.get("receipt_sha256")
    if not isinstance(expected, str):
        raise ReplayVerificationError("RECEIPT_HASH_MISSING")
    material = dict(receipt)
    material.pop("receipt_sha256", None)
    actual = sha256_bytes(canonical_json_bytes(material))
    if actual != expected:
        raise ReplayVerificationError("RECEIPT_HASH_MISMATCH")


def verify_snapshot_pointer(terminal: dict[str, Any], snapshot: dict[str, Any], snapshot_name: str) -> None:
    if terminal.get("target_path") != snapshot_name:
        raise ReplayVerificationError("SNAPSHOT_POINTER_PATH_MISMATCH")
    expected = terminal.get("target_sha256")
    actual = sha256_bytes(canonical_json_bytes(snapshot))
    if expected != actual:
        raise ReplayVerificationError("SNAPSHOT_POINTER_HASH_MISMATCH")


def verify_handoff_references(handoff: dict[str, Any], archive_names: set[str]) -> None:
    artifacts = handoff.get("artifacts")
    if not isinstance(artifacts, dict) or not artifacts:
        raise ReplayVerificationError("HANDOFF_ARTIFACTS_MISSING")
    for label, relative_path in artifacts.items():
        if relative_path not in archive_names:
            raise ReplayVerificationError(f"HANDOFF_REFERENCE_MISSING:{label}:{relative_path}")


def verify_source_semantics(documents: dict[str, Any]) -> None:
    health = documents["source_health"]
    receipt = documents["receipt"]
    snapshot = documents["snapshot"]
    handoff = documents["handoff"]
    terminal = documents["terminal"]

    if health.get("acquisition_mode") != "NETWORK":
        raise ReplayVerificationError("NOT_NETWORK_ACQUISITION")
    if health.get("source_substitution", {}).get("used") is not False:
        raise ReplayVerificationError("SOURCE_SUBSTITUTION_USED")
    if receipt.get("source_substitution", {}).get("used") is not False:
        raise ReplayVerificationError("RECEIPT_SOURCE_SUBSTITUTION_USED")
    if terminal.get("status") != "SHADOW_CANDIDATE_ONLY":
        raise ReplayVerificationError("TERMINAL_NOT_SHADOW_ONLY")

    observations = []
    observations.extend(snapshot.get("observations", {}).values())
    observations.extend(handoff.get("observations", {}).get("macro_core", {}).values())
    if not observations:
        raise ReplayVerificationError("OBSERVATION_MISSING")
    for observation in observations:
        if observation.get("direct_or_derived") != "DIRECT":
            raise ReplayVerificationError("OBSERVATION_NOT_DIRECT")
        if observation.get("revision_policy") != "APPEND_ONLY_DO_NOT_OVERWRITE_PRIOR_RECEIPTS":
            raise ReplayVerificationError("REVISION_POLICY_NOT_APPEND_ONLY")


def reconstruct_archive(archive_dir: Path, manifest: dict[str, Any]) -> tuple[bytes, list[dict[str, Any]]]:
    archive = manifest.get("archive", {})
    parts = archive.get("parts")
    if not isinstance(parts, list) or len(parts) != archive.get("part_count"):
        raise ReplayVerificationError("PART_COUNT_MISMATCH")

    ordered = sorted(parts, key=lambda item: item.get("order", 0))
    chunks: list[bytes] = []
    part_results: list[dict[str, Any]] = []
    for expected_order, part in enumerate(ordered, start=1):
        if part.get("order") != expected_order:
            raise ReplayVerificationError("PART_ORDER_MISMATCH")
        path = archive_dir / str(part.get("path"))
        if not path.is_file():
            raise ReplayVerificationError(f"PART_MISSING:{path.name}")
        payload = path.read_bytes()
        checks = {
            "path": path.name,
            "order": expected_order,
            "character_count": len(payload),
            "sha256": sha256_bytes(payload),
            "git_blob_sha1": git_blob_sha1(payload),
        }
        if checks["character_count"] != part.get("character_count"):
            raise ReplayVerificationError(f"PART_CHARACTER_COUNT_MISMATCH:{path.name}")
        if checks["sha256"] != part.get("sha256"):
            raise ReplayVerificationError(f"PART_SHA256_MISMATCH:{path.name}")
        if checks["git_blob_sha1"] != part.get("git_blob_sha1"):
            raise ReplayVerificationError(f"PART_GIT_BLOB_MISMATCH:{path.name}")
        chunks.append(payload)
        part_results.append(checks)

    encoded = b"".join(chunks)
    if len(encoded) != archive.get("base64_character_count"):
        raise ReplayVerificationError("BASE64_CHARACTER_COUNT_MISMATCH")
    if sha256_bytes(encoded) != archive.get("base64_sha256"):
        raise ReplayVerificationError("BASE64_SHA256_MISMATCH")
    try:
        decoded = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ReplayVerificationError(f"BASE64_DECODE_FAIL:{exc}") from exc
    return decoded, part_results


def verify_zip(decoded: bytes, manifest: dict[str, Any]) -> tuple[dict[str, bytes], list[dict[str, Any]]]:
    workflow = manifest.get("github_workflow", {})
    if len(decoded) != workflow.get("artifact_size_bytes"):
        raise ReplayVerificationError("ARTIFACT_SIZE_MISMATCH")
    if sha256_bytes(decoded) != workflow.get("artifact_sha256"):
        raise ReplayVerificationError("ARTIFACT_SHA256_MISMATCH")

    try:
        with zipfile.ZipFile(io.BytesIO(decoded)) as archive:
            if archive.testzip() is not None:
                raise ReplayVerificationError("ZIP_CRC_FAIL")
            names = set(archive.namelist())
            payloads = {name: archive.read(name) for name in names}
    except zipfile.BadZipFile as exc:
        raise ReplayVerificationError(f"ZIP_PARSE_FAIL:{exc}") from exc

    expected_rows = manifest.get("files")
    if not isinstance(expected_rows, list):
        raise ReplayVerificationError("MANIFEST_FILE_ROWS_MISSING")
    expected_names = {str(row.get("path")) for row in expected_rows}
    if names != expected_names:
        raise ReplayVerificationError("ARCHIVE_FILE_SET_MISMATCH")
    if len(names) != manifest.get("verification", {}).get("expected_file_count"):
        raise ReplayVerificationError("ARCHIVE_FILE_COUNT_MISMATCH")
    if not EXPECTED_ARCHIVE_FILES.issubset(names):
        raise ReplayVerificationError("REQUIRED_TOP_LEVEL_FILES_MISSING")
    if len([name for name in names if name.startswith("receipts/")]) != 1:
        raise ReplayVerificationError("RECEIPT_FILE_COUNT_MISMATCH")
    if len([name for name in names if name.startswith("snapshots/")]) != 1:
        raise ReplayVerificationError("SNAPSHOT_FILE_COUNT_MISMATCH")

    file_results: list[dict[str, Any]] = []
    rows_by_path = {str(row.get("path")): row for row in expected_rows}
    for name in sorted(names):
        payload = payloads[name]
        row = rows_by_path[name]
        actual = {"path": name, "size_bytes": len(payload), "sha256": sha256_bytes(payload)}
        if actual["size_bytes"] != row.get("size_bytes"):
            raise ReplayVerificationError(f"FILE_SIZE_MISMATCH:{name}")
        if actual["sha256"] != row.get("sha256"):
            raise ReplayVerificationError(f"FILE_SHA256_MISMATCH:{name}")
        file_results.append(actual)
    return payloads, file_results


def verify_archive(archive_dir: Path) -> dict[str, Any]:
    manifest_paths = sorted(archive_dir.glob("*.manifest.json"))
    if len(manifest_paths) != 1:
        raise ReplayVerificationError("MANIFEST_COUNT_MISMATCH")
    manifest = json.loads(manifest_paths[0].read_text(encoding="utf-8"))
    if manifest.get("schema") != "DATA_TERMINAL_LIVE_ARTIFACT_ARCHIVE_MANIFEST":
        raise ReplayVerificationError("MANIFEST_SCHEMA_MISMATCH")
    if manifest.get("status") != "VERIFIED_SHADOW_LIVE_PILOT_ARCHIVE":
        raise ReplayVerificationError("MANIFEST_STATUS_MISMATCH")

    decoded, part_results = reconstruct_archive(archive_dir, manifest)
    payloads, file_results = verify_zip(decoded, manifest)
    names = set(payloads)
    receipt_name = next(name for name in names if name.startswith("receipts/"))
    snapshot_name = next(name for name in names if name.startswith("snapshots/"))
    documents = {
        "source_health": load_json_bytes(payloads["source_health.json"], "source_health.json"),
        "terminal": load_json_bytes(payloads["latest_terminal_state.json"], "latest_terminal_state.json"),
        "handoff": load_json_bytes(payloads["latest_data_ping_handoff.json"], "latest_data_ping_handoff.json"),
        "receipt": load_json_bytes(payloads[receipt_name], receipt_name),
        "snapshot": load_json_bytes(payloads[snapshot_name], snapshot_name),
    }

    verify_receipt_hash(documents["receipt"])
    verify_snapshot_pointer(documents["terminal"], documents["snapshot"], snapshot_name)
    verify_handoff_references(documents["handoff"], names)
    missing_reference_count, unique_missing_count = verify_missing_unknown(documents)
    authority_count = verify_false_authority_blocks(documents)
    verify_source_semantics(documents)

    expected_authority_count = manifest.get("verification", {}).get("authority_block_count")
    if expected_authority_count is not None and authority_count != expected_authority_count:
        raise ReplayVerificationError("AUTHORITY_BLOCK_COUNT_MISMATCH")

    run_id = documents["receipt"].get("run_id")
    if run_id != manifest.get("terminal_run", {}).get("run_id"):
        raise ReplayVerificationError("RUN_ID_MISMATCH")

    if manifest.get("archive", {}).get("active_data_ping_pointer_changed") is not False:
        raise ReplayVerificationError("ACTIVE_DATA_PING_POINTER_CHANGED")
    if manifest.get("archive", {}).get("latest_data_terminal_pointer_changed") is not False:
        raise ReplayVerificationError("LATEST_DATA_TERMINAL_POINTER_CHANGED")

    gates = {
        "archive_parts": "PASS",
        "base64_reconstruction": "PASS",
        "artifact_digest": "PASS",
        "zip_integrity": "PASS",
        "file_manifest": "PASS",
        "json_parse": "PASS",
        "receipt_hash": "PASS",
        "snapshot_pointer_hash": "PASS",
        "handoff_references": "PASS",
        "missing_unknown_not_zero": "PASS",
        "authority_flags_all_false": "PASS",
        "source_substitution_false": "PASS",
        "direct_observation_label": "PASS",
        "append_only_revision_policy": "PASS",
        "shadow_only_authority": "PASS",
        "active_pointer_immutability": "PASS",
    }
    return {
        "schema": "DATA_TERMINAL_PHASE1_REPLAY_VERIFICATION",
        "schema_version": "0.1",
        "report_id": "DATA_TERMINAL_PHASE1_REPLAY_GATE_20260721_01",
        "overall_status": "PASS",
        "run_id": run_id,
        "github_workflow_run_id": manifest.get("github_workflow", {}).get("run_id"),
        "artifact_sha256": manifest.get("github_workflow", {}).get("artifact_sha256"),
        "archive_part_count": len(part_results),
        "archive_file_count": len(file_results),
        "authority_block_count": authority_count,
        "missing_reference_count": missing_reference_count,
        "unique_missing_row_count": unique_missing_count,
        "row_validity": "PASS",
        "coverage_readiness": "READY_FOR_PHASE1_CLOSEOUT_REVIEW",
        "edge_or_promotion_status": "NOT_APPLICABLE",
        "phase1_completion": "NOT_YET_DECLARED_SECOND_LIVE_REPEAT_REQUIRED",
        "gates": gates,
        "authority": {
            "binding": False,
            "canonical_acceptance": False,
            "framework_state_change": False,
            "portfolio_action": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive_dir", type=Path)
    parser.add_argument("--report-output", type=Path)
    args = parser.parse_args()
    try:
        report = verify_archive(args.archive_dir)
    except (OSError, json.JSONDecodeError, ReplayVerificationError) as exc:
        report = {
            "schema": "DATA_TERMINAL_PHASE1_REPLAY_VERIFICATION",
            "schema_version": "0.1",
            "overall_status": "FAIL",
            "error": str(exc),
            "authority": {
                "binding": False,
                "canonical_acceptance": False,
                "framework_state_change": False,
                "portfolio_action": False,
            },
        }
        if args.report_output:
            args.report_output.parent.mkdir(parents=True, exist_ok=True)
            args.report_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(report, sort_keys=True))
        return 1

    if args.report_output:
        args.report_output.parent.mkdir(parents=True, exist_ok=True)
        args.report_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
