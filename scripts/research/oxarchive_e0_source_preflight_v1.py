#!/usr/bin/env python3
"""0xArchive E0 metadata/PIT preflight, never a data or trading attestation.

Pure stdlib. No HTTP, API credentials, vendor code, market values or writes.
The input contains only source receipt metadata; raw/provider rows belong in
the separately authorized restricted data plane. A PASS means that declared
metadata is internally consistent, NOT that any declared fact is true.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import stat
from pathlib import Path
from typing import Any

CONTRACT = "OXARCHIVE_E0_SOURCE_RECEIPT_V1"
REPORT_CONTRACT = "OXARCHIVE_E0_METADATA_PREFLIGHT_V1"
ALLOWED_FAMILIES = {
    "hyperliquid_core", "hyperliquid_spot", "hyperliquid_hip3",
    "hyperliquid_hip4", "lighter_mainnet", "lighter_robinhood_chain",
}
ALLOWED_TYPES = {
    "trades", "candles", "funding", "open_interest", "liquidations",
    "l2_orderbook", "l3_orderbook", "l4_orderbook", "orders",
}
ROOT_KEYS = {
    "contract", "study_id", "purpose", "data_placement",
    "rights_state", "decision_cutoff_utc", "receipts",
}
RECEIPT_KEYS = {
    "receipt_id", "provider", "family", "market_id", "datatype",
    "source_id", "api_version", "provider_request_id", "schema_sha256",
    "window_start_utc", "window_end_utc", "event_max_utc",
    "source_first_known_utc", "availability_evidence",
    "provider_available_at_utc", "retrieved_at_utc", "quality_state",
    "gap_count", "row_count", "finality", "binding",
}
BINDING_KEYS = {
    "repository", "private_commit_sha", "path", "sha256", "bytes",
}
SHA256 = re.compile(r"[a-f0-9]{64}\Z")
SHA40 = re.compile(r"[a-f0-9]{40}\Z")
UTC = dt.timezone.utc


def _stamp(value: Any) -> dt.datetime:
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", value
    ):
        raise ValueError("timestamp_must_be_full_utc_Z")
    result = dt.datetime.fromisoformat(value[:-1] + "+00:00")
    if result.utcoffset() != dt.timedelta(0):
        raise ValueError("timestamp_not_utc")
    return result


def _is_hash(value: Any, pattern: re.Pattern[str]) -> bool:
    return isinstance(value, str) and pattern.fullmatch(value) is not None


def _positive_int(value: Any) -> bool:
    return type(value) is int and value > 0


def _nonnegative_int(value: Any) -> bool:
    return type(value) is int and value >= 0


def _text(value: Any) -> bool:
    return isinstance(value, str) and 0 < len(value) <= 160 and value.strip() == value


def inspect(document: Any) -> dict[str, Any]:
    """Return only non-sensitive error codes; never echo input contents."""
    errors: set[str] = set()
    count = 0
    if not isinstance(document, dict):
        errors.add("ROOT_NOT_OBJECT")
        document = {}
    if set(document) - ROOT_KEYS:
        errors.add("UNKNOWN_ROOT_FIELDS")
    if document.get("contract") != CONTRACT:
        errors.add("CONTRACT_INVALID")
    if not _text(document.get("study_id")):
        errors.add("STUDY_ID_INVALID")
    if document.get("purpose") != "SHADOW_SOURCE_FEASIBILITY":
        errors.add("PURPOSE_UNAUTHORIZED")
    if document.get("data_placement") != "PRIVATE_REFERENCED_ONLY":
        errors.add("PRIVATE_DATA_BOUNDARY_INVALID")
    if document.get("rights_state") != "INTERNAL_RESEARCH_RIGHTS_REVIEWED":
        errors.add("DATA_RIGHTS_UNRESOLVED")
    try:
        cutoff = _stamp(document.get("decision_cutoff_utc"))
    except (ValueError, OverflowError):
        errors.add("DECISION_CUTOFF_INVALID")
        cutoff = None
    receipts = document.get("receipts")
    if not isinstance(receipts, list) or not receipts or len(receipts) > 25:
        errors.add("RECEIPTS_COUNT_INVALID")
        receipts = []
    seen: set[str] = set()
    for receipt in receipts:
        count += 1
        if not isinstance(receipt, dict):
            errors.add("RECEIPT_NOT_OBJECT")
            continue
        if set(receipt) - RECEIPT_KEYS:
            errors.add("UNKNOWN_RECEIPT_FIELDS")
        rid = receipt.get("receipt_id")
        if not _text(rid):
            errors.add("RECEIPT_ID_INVALID")
        elif rid in seen:
            errors.add("DUPLICATE_RECEIPT_ID")
        else:
            seen.add(rid)
        if receipt.get("provider") != "0xarchive":
            errors.add("PROVIDER_INVALID")
        family = receipt.get("family")
        datatype = receipt.get("datatype")
        if not isinstance(family, str) or family not in ALLOWED_FAMILIES:
            errors.add("FAMILY_INVALID")
        if not isinstance(datatype, str) or datatype not in ALLOWED_TYPES:
            errors.add("DATATYPE_INVALID")
        if family in {"hyperliquid_spot", "hyperliquid_hip4"} and datatype == "funding":
            errors.add("FAMILY_DATATYPE_INCOMPATIBLE")
        if datatype == "l3_orderbook" and family != "lighter_mainnet":
            errors.add("FAMILY_DATATYPE_INCOMPATIBLE")
        if datatype == "l4_orderbook" and not (
            isinstance(family, str) and family.startswith("hyperliquid_")
        ):
            errors.add("FAMILY_DATATYPE_INCOMPATIBLE")
        for field in ("market_id", "source_id", "provider_request_id"):
            if not _text(receipt.get(field)):
                errors.add("SOURCE_IDENTITY_INCOMPLETE")
        if receipt.get("api_version") != "2026-10-01":
            errors.add("API_VERSION_UNPINNED")
        if not _is_hash(receipt.get("schema_sha256"), SHA256):
            errors.add("SCHEMA_HASH_INVALID")
        times: dict[str, dt.datetime] = {}
        for field in (
            "window_start_utc", "window_end_utc", "event_max_utc",
            "source_first_known_utc", "provider_available_at_utc",
            "retrieved_at_utc",
        ):
            try:
                times[field] = _stamp(receipt.get(field))
            except (ValueError, OverflowError):
                errors.add("SOURCE_CLOCK_INVALID")
        if len(times) == 6 and cutoff is not None:
            start = times["window_start_utc"]
            end = times["window_end_utc"]
            event = times["event_max_utc"]
            known = times["source_first_known_utc"]
            available = times["provider_available_at_utc"]
            retrieved = times["retrieved_at_utc"]
            if not start <= event < end <= cutoff:
                errors.add("FUTURE_OR_EMPTY_EVENT_WINDOW")
            if not event <= known <= cutoff:
                errors.add("SOURCE_FIRST_KNOWN_AFTER_CUTOFF")
            if not event <= available <= cutoff:
                errors.add("SOURCE_AVAILABLE_AFTER_CUTOFF")
            if retrieved < event:
                errors.add("RETRIEVED_BEFORE_EVENT")
            # A late retrieval can be legitimate, never treat it as PIT proof.
        if receipt.get("availability_evidence") != "IMMUTABLE_PRIOR_PUBLICATION_RECEIPT":
            errors.add("FIRST_KNOWN_PROVENANCE_UNVERIFIED")
        if receipt.get("quality_state") != "COMPLETE_WINDOW":
            errors.add("COVERAGE_NOT_COMPLETE")
        if not _nonnegative_int(receipt.get("gap_count")) or receipt.get("gap_count") != 0:
            errors.add("GAPS_OR_INVALID_GAP_COUNT")
        if not _positive_int(receipt.get("row_count")):
            errors.add("ROW_COUNT_INVALID")
        if receipt.get("finality") != "FINALIZED":
            errors.add("FINALITY_UNRESOLVED")
        binding = receipt.get("binding")
        if not isinstance(binding, dict):
            errors.add("PRIVATE_BINDING_MISSING")
            continue
        if set(binding) - BINDING_KEYS:
            errors.add("UNKNOWN_BINDING_FIELDS")
        if binding.get("repository") != "Donh91/secrets":
            errors.add("RESTRICTED_REPOSITORY_REQUIRED")
        if not _is_hash(binding.get("private_commit_sha"), SHA40):
            errors.add("PRIVATE_COMMIT_INVALID")
        path = binding.get("path")
        if not _text(path) or path.startswith("/") or ".." in Path(path).parts or "\\" in path:
            errors.add("PRIVATE_PATH_INVALID")
        if not _is_hash(binding.get("sha256"), SHA256):
            errors.add("DATA_DIGEST_INVALID")
        if not _positive_int(binding.get("bytes")):
            errors.add("DATA_LENGTH_INVALID")
    return {
        "contract": REPORT_CONTRACT,
        "status": "SCHEMA_ONLY_PASS" if not errors else "HOLD",
        "errors": sorted(errors),
        "receipt_count": count,
        "external_source_authenticated": False,
        "raw_dataset_bytes_verified": False,
        "first_known_proof_independently_verified": False,
        "trading_edge_proven": False,
        "production_admitted": False,
        "publication_authorized": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline, metadata-only source preflight")
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args(argv)
    try:
        path = args.manifest
        # Refuse links, directories, pipes and oversized inputs.
        mode = path.lstat().st_mode
        if not stat.S_ISREG(mode) or path.stat().st_size > 262144:
            raise ValueError("UNSAFE_MANIFEST_FILE")
        obj = json.loads(path.read_text(encoding="utf-8"))
        report = inspect(obj)
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError):
        report = inspect({})
        report["errors"] = sorted(set(report["errors"]) | {"MANIFEST_UNREADABLE_OR_UNSAFE"})
        report["status"] = "HOLD"
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0 if report["status"] == "SCHEMA_ONLY_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
