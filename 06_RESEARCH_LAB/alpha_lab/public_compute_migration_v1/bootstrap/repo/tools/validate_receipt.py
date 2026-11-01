"""Fail-closed W1 synthetic-only schema and chronology validation.

A schema PASS is not original source attestation. This code is deliberately
incapable of admitting market data, writing to GitHub, or calling private repos.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from tools.produce_synthetic import REPO, TEST_DATA


class RejectedReceipt(ValueError):
    pass


def validate_document(doc: dict[str, Any], schema_path: Path) -> None:
    schema_bytes = schema_path.read_bytes()
    schema = json.loads(schema_bytes)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(doc), key=lambda e: list(map(str, e.path)))
    if errors:
        raise RejectedReceipt("SCHEMA_REJECT: " + "; ".join(e.message for e in errors[:5]))
    # W1 is synthetic-only. Future real-source work must have a separate,
    # independently reviewed validator and admission identity; never silently
    # enable PUBLIC_CHAIN_RPC by widening this one.
    required = {
        "deployment_stage": "SYNTHETIC_TEST",
        "source_class": "SYNTHETIC_FIXTURE",
        "mode": "SYNTHETIC_TEST",
        "status": "SYNTHETIC_COMPLETE",
        "source_id": "SYNTHETIC_FIXTURE_V1",
        "event_count": 0,
        "chain_id": 4663,
    }
    if any(doc.get(key) != value for key, value in required.items()):
        raise RejectedReceipt("NON_SYNTHETIC_W1_FORBIDDEN")
    if doc["collector"]["public_repo"] != REPO:
        raise RejectedReceipt("PUBLIC_REPO_ID_MISMATCH")
    if doc["collector"]["schema_sha256"] != hashlib.sha256(schema_bytes).hexdigest():
        raise RejectedReceipt("SCHEMA_DIGEST_MISMATCH")
    if doc["source_data_sha256"] != hashlib.sha256(TEST_DATA).hexdigest():
        raise RejectedReceipt("SYNTHETIC_DATA_DIGEST_MISMATCH")
    if doc["collector"]["code_commit_sha40"] != doc["github"]["head_sha40"]:
        raise RejectedReceipt("GIT_HEAD_INCONSISTENT")
    if doc["github"]["run_id"] <= 0 or doc["github"]["run_attempt"] <= 0:
        raise RejectedReceipt("RUN_ID_INVALID")
    if doc["github"]["event"] != "workflow_dispatch":
        raise RejectedReceipt("W1_ONLY_MANUAL_DISPATCH")
    cover = doc["coverage"]
    if cover["end_block"] < cover["start_block"] or cover["safe_head_block"] < cover["end_block"]:
        raise RejectedReceipt("CHAIN_ORDER_INVALID")
    if cover["blocks_requested"] != cover["end_block"] - cover["start_block"] + 1:
        raise RejectedReceipt("RANGE_LENGTH_INVALID")
    if cover["blocks_completed"] != cover["blocks_requested"]:
        raise RejectedReceipt("INCOMPLETE_SYNTHETIC_RANGE")
    if cover["missing_ranges_count"] != 0 or not cover["contiguous"] or cover["reorg_suspected"] or not cover["has_all_original_ranges"]:
        raise RejectedReceipt("SYNTHETIC_COVERAGE_NOT_COMPLETE")
    clocks = [
        doc["github"]["job_started_at_utc"],
        doc["clock"]["source_observation_started_at_utc"],
        doc["clock"]["first_observed_at_utc"],
        doc["clock"]["source_observation_completed_at_utc"],
        doc["github"]["job_completed_at_utc"],
        doc["clock"]["receipt_available_at_utc"],
    ]
    try:
        instants = [datetime.fromisoformat(s.replace("Z", "+00:00")) for s in clocks]
    except (ValueError, TypeError) as exc:
        raise RejectedReceipt("TIMESTAMP_INVALID") from exc
    if instants != sorted(instants):
        raise RejectedReceipt("CLOCK_ORDER_INVALID")
    if any(doc["provenance_claims"].values() if isinstance(doc["provenance_claims"], dict) else []):
        # public_source_only is the single expected true claim
        if {k: v for k, v in doc["provenance_claims"].items() if k != "public_source_only"} != {
            "original_machine_first_known_certified": False,
            "canonical_alpha_census_recovered": False,
            "private_signal_or_trade_permission": False,
            "safe_for_private_import": False,
        }:
            raise RejectedReceipt("PROVENANCE_ESCALATION")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt")
    parser.add_argument("--schema", required=True)
    args = parser.parse_args()
    doc = json.loads(Path(args.receipt).read_text())
    validate_document(doc, Path(args.schema))
    print("W1_SYNTHETIC_SCHEMA_AND_SEMANTICS_PASS_NOT_REAL_SOURCE")


if __name__ == "__main__":
    main()
