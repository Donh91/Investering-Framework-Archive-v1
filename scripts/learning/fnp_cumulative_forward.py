#!/usr/bin/env python3
"""Prospective T5 FNP instrumentation over the existing T2 divergence owner.

This module creates no market semantics. It only converts an already-authoritative
T2 WAIT-vs-BTC_PARTIAL divergence receipt into one immutable T5 source row and can
later bind the matching T2 maturity receipt as an immutable evidence attachment.

The FNP damage-avoided / missed-upside evaluator remains explicitly blocked by the
current PDLT methods hardening. Consequently no derived FNP metric or final
classification is emitted here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.api_agent.forward_evidence_observer import canonical_hash as t2_hash  # noqa: E402

SOURCE_CONTRACT = "FNP_CUMULATIVE_SOURCE_v1"
ATTACHMENT_CONTRACT = "FNP_CUMULATIVE_OUTCOME_ATTACHMENT_v1"
RUN_CONTRACT = "FNP_CUMULATIVE_RUN_RECEIPT_v1"
T2_RECEIPT_CONTRACT = "BTC_PARTIAL_WAIT_COVERAGE_RECEIPT_v1"
T2_MATURITY_CONTRACT = "BTC_PARTIAL_WAIT_MATURITY_RECEIPT_v1"
TEST_ID = "FNP_CUMULATIVE"
SOURCE_TEST_ID = "GATE_BTC_PARTIAL_FT_1"
ACTIVATION_UTC = "2026-09-23T23:52:00Z"
HORIZON_FIELDS = {
    "24H": "frozen_horizon_24h",
    "72H": "frozen_horizon_72h",
    "7D": "frozen_horizon_7d",
}
FROZEN_HASH_FIELDS = [
    "row_id", "timestamp_utc", "source_run_id", "framework_state", "asset_tier",
    "benchmark_action_WAIT", "experimental_action_BTC_PARTIAL", "decision_divergence",
    "entry_reference_price", "position_fraction_assumed", "frozen_horizon_24h",
    "frozen_horizon_72h", "frozen_horizon_7d", "source_lineage",
]
AUTHORITY = {
    "research_only": True,
    "binding": False,
    "framework_state_change": False,
    "market_rule_change": False,
    "market_threshold_change": False,
    "model_weight_change": False,
    "portfolio_action": False,
    "automatic_execution": False,
    "automatic_promotion": False,
    "classification_authority": False,
}


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object_required:{path}")
    return value


def parse_utc(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"{field}_explicit_utc_required")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(f"{field}_invalid") from exc
    return parsed.astimezone(timezone.utc)


def iso_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_immutable(path: Path, value: dict[str, Any]) -> str:
    raw = canonical_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != raw:
            raise ValueError(f"immutable_conflict:{path}")
        return "DUPLICATE_NOOP"
    path.write_bytes(raw)
    return "CREATED"


def validate_zero_authority(value: Any) -> None:
    if not isinstance(value, dict):
        raise ValueError("source_authority_required")
    for key in ("framework_state_change", "portfolio_action", "market_rule_change", "threshold_change", "weight_change", "canonical_promotion"):
        if value.get(key) is not False:
            raise ValueError(f"source_authority_not_zero:{key}")


def validate_t2_divergence(receipt: dict[str, Any]) -> dict[str, Any]:
    if receipt.get("contract") != T2_RECEIPT_CONTRACT or receipt.get("test_id") != SOURCE_TEST_ID:
        raise ValueError("t2_divergence_receipt_contract_required")
    if receipt.get("status") != "DIVERGENCE_CAPTURED":
        raise ValueError("t2_divergence_captured_required")
    if receipt.get("counts_as_outcome_row") is not False:
        raise ValueError("source_receipt_must_not_be_outcome")
    validate_zero_authority(receipt.get("authority"))

    row = receipt.get("divergence_source_row")
    if not isinstance(row, dict):
        raise ValueError("divergence_source_row_required")
    if row.get("decision_divergence") is not True:
        raise ValueError("explicit_decision_divergence_required")
    if row.get("benchmark_action_WAIT") != "WAIT":
        raise ValueError("wait_benchmark_required")
    if row.get("experimental_action_BTC_PARTIAL") != "BTC_PARTIAL":
        raise ValueError("btc_partial_blocked_action_required")

    observed = parse_utc(row.get("timestamp_utc"), "timestamp_utc")
    if observed < parse_utc(ACTIVATION_UTC, "activation_utc"):
        raise ValueError("retrospective_row_backfill_forbidden")
    asset = row.get("asset_tier")
    if not isinstance(asset, str) or not asset.strip():
        raise ValueError("asset_tier_required")
    entry = row.get("entry_reference_price")
    if isinstance(entry, bool) or not isinstance(entry, (int, float)) or float(entry) <= 0:
        raise ValueError("entry_reference_price_required")

    lineage = row.get("source_lineage")
    if not isinstance(lineage, dict) or not lineage.get("source_hash") or not lineage.get("source_run_id"):
        raise ValueError("source_lineage_required")
    if lineage.get("source_hash") != receipt.get("source_hash") or lineage.get("source_run_id") != receipt.get("source_run_id"):
        raise ValueError("source_lineage_mismatch")

    horizons: dict[str, str] = {}
    previous = observed
    for horizon, field in HORIZON_FIELDS.items():
        due = parse_utc(row.get(field), field)
        if due <= previous:
            raise ValueError("frozen_horizon_order_invalid")
        horizons[horizon] = iso_z(due)
        previous = due

    frozen_subset = {key: row.get(key) for key in FROZEN_HASH_FIELDS}
    expected = row.get("frozen_input_sha256")
    if not isinstance(expected, str) or expected != t2_hash(frozen_subset):
        raise ValueError("t2_frozen_input_hash_invalid")
    return row


def source_row_from_t2(receipt: dict[str, Any]) -> dict[str, Any]:
    row = validate_t2_divergence(receipt)
    source_receipt_sha = digest(receipt)
    source_frozen_sha = str(row["frozen_input_sha256"])
    row_id = "T5-" + hashlib.sha256(f"{source_frozen_sha}|{TEST_ID}".encode()).hexdigest()[:20]
    horizons = {name: row[field] for name, field in HORIZON_FIELDS.items()}
    return {
        "contract": SOURCE_CONTRACT,
        "test_id": TEST_ID,
        "row_id": row_id,
        "observed_at_utc": row["timestamp_utc"],
        "source_test_id": SOURCE_TEST_ID,
        "source_check_id": receipt.get("check_id"),
        "source_receipt_sha256": source_receipt_sha,
        "source_divergence_row_id": row.get("row_id"),
        "source_frozen_input_sha256": source_frozen_sha,
        "asset_tier": row["asset_tier"],
        "blocked_action": row["experimental_action_BTC_PARTIAL"],
        "benchmark_action": row["benchmark_action_WAIT"],
        "decision_divergence": True,
        "entry_reference_price": float(row["entry_reference_price"]),
        "position_fraction_assumed": row.get("position_fraction_assumed"),
        "frozen_horizons": horizons,
        "outcome_fields": {
            "actual_cost_pct": None,
            "drawdown_avoided_pct": None,
            "missed_upside_pct": None,
            "final_classification": None,
        },
        "outcome_evaluator_status": "BLOCKED_AUTHORITATIVE_FNP_EVALUATOR_MISSING",
        "framework_acceptance": "PENDING_OUTCOME_MATURITY_AND_EVALUATOR",
        "source_lineage": {
            "source_hash": row["source_lineage"]["source_hash"],
            "source_run_id": row["source_lineage"]["source_run_id"],
            "t2_receipt_sha256": source_receipt_sha,
        },
        "retrospective_creation": False,
        "authority": AUTHORITY,
    }


def freeze_receipt(receipt: dict[str, Any], output_root: Path) -> dict[str, Any]:
    row = source_row_from_t2(receipt)
    day = row["observed_at_utc"][:10]
    path = output_root / "source_rows" / day / f"{row['row_id']}.json"
    status = write_immutable(path, row)
    return {"status": status, "row_id": row["row_id"], "path": path.as_posix(), "row_sha256": digest(row)}


def validate_source_row(row: dict[str, Any]) -> None:
    if row.get("contract") != SOURCE_CONTRACT or row.get("test_id") != TEST_ID:
        raise ValueError("t5_source_contract_invalid")
    if row.get("decision_divergence") is not True:
        raise ValueError("t5_source_divergence_required")
    if row.get("blocked_action") != "BTC_PARTIAL" or row.get("benchmark_action") != "WAIT":
        raise ValueError("t5_source_action_binding_invalid")
    if not isinstance(row.get("asset_tier"), str) or not row["asset_tier"]:
        raise ValueError("t5_source_asset_tier_required")
    if row.get("retrospective_creation") is not False:
        raise ValueError("t5_retrospective_creation_forbidden")
    if row.get("outcome_evaluator_status") != "BLOCKED_AUTHORITATIVE_FNP_EVALUATOR_MISSING":
        raise ValueError("t5_evaluator_boundary_invalid")
    fields = row.get("outcome_fields")
    if not isinstance(fields, dict) or any(value is not None for value in fields.values()):
        raise ValueError("premature_t5_outcome_forbidden")
    if row.get("authority") != AUTHORITY:
        raise ValueError("t5_authority_invalid")
    observed = parse_utc(row.get("observed_at_utc"), "observed_at_utc")
    previous = observed
    horizons = row.get("frozen_horizons")
    if not isinstance(horizons, dict) or set(horizons) != set(HORIZON_FIELDS):
        raise ValueError("t5_frozen_horizons_invalid")
    for name in ("24H", "72H", "7D"):
        due = parse_utc(horizons[name], f"horizon_{name}")
        if due <= previous:
            raise ValueError("t5_frozen_horizon_order_invalid")
        previous = due


def attach_maturity(source_row: dict[str, Any], maturity: dict[str, Any], output_root: Path) -> dict[str, Any]:
    validate_source_row(source_row)
    if maturity.get("contract") != T2_MATURITY_CONTRACT or maturity.get("test_id") != SOURCE_TEST_ID:
        raise ValueError("t2_maturity_contract_required")
    if maturity.get("row_id") != source_row.get("source_divergence_row_id"):
        raise ValueError("maturity_row_id_mismatch")
    if maturity.get("frozen_input_sha256") != source_row.get("source_frozen_input_sha256"):
        raise ValueError("maturity_frozen_input_mismatch")
    if maturity.get("counts_as_outcome_row") is not False or maturity.get("owner_attach_required_before_outcome_row_count") is not True:
        raise ValueError("t2_maturity_owner_boundary_invalid")
    validate_zero_authority(maturity.get("authority"))

    matured = maturity.get("matured_horizons")
    if not isinstance(matured, dict):
        raise ValueError("matured_horizons_required")
    frozen = source_row["frozen_horizons"]
    raw_inputs: dict[str, Any] = {}
    for horizon, value in sorted(matured.items()):
        if horizon not in frozen or not isinstance(value, dict):
            raise ValueError("unexpected_maturity_horizon")
        due = parse_utc(value.get("due_utc"), "maturity_due_utc")
        if iso_z(due) != frozen[horizon]:
            raise ValueError("maturity_due_does_not_match_frozen_horizon")
        observed = parse_utc(value.get("observed_at_utc"), "maturity_observed_at_utc")
        if observed < due:
            raise ValueError("partial_maturity_window_forbidden")
        if not value.get("source_hash"):
            raise ValueError("maturity_source_hash_required")
        raw_inputs[horizon] = {
            "due_utc": frozen[horizon],
            "observed_at_utc": iso_z(observed),
            "return_pct": value.get("return_pct"),
            "max_favorable_excursion_pct": value.get("max_favorable_excursion_pct"),
            "max_adverse_excursion_pct": value.get("max_adverse_excursion_pct"),
            "benchmark_return_pct": value.get("benchmark_return_pct"),
            "source_hash": value.get("source_hash"),
            "source_provider": value.get("source_provider"),
            "data_quality": value.get("data_quality"),
        }

    attachment = {
        "contract": ATTACHMENT_CONTRACT,
        "test_id": TEST_ID,
        "row_id": source_row["row_id"],
        "source_row_sha256": digest(source_row),
        "source_t2_maturity_sha256": digest(maturity),
        "as_of_utc": maturity.get("as_of_utc"),
        "maturity_complete": maturity.get("maturity_complete") is True,
        "raw_evaluator_inputs_by_frozen_horizon": raw_inputs,
        "derived_fnp_metrics": {
            "actual_cost_pct": None,
            "drawdown_avoided_pct": None,
            "missed_upside_pct": None,
            "final_classification": None,
        },
        "evaluation_status": "BLOCKED_AUTHORITATIVE_FNP_EVALUATOR_MISSING",
        "evaluation_reason": "PDLT_METHODS_HARDENING_FORBIDS_FNP_DAMAGE_AVOIDED_MISSED_UPSIDE_INFERENCE_UNTIL_AUTHORITATIVE_EVALUATOR_EXISTS",
        "counts_as_valid_outcome_row": False,
        "retrospective_horizon_selection": False,
        "authority": AUTHORITY,
    }
    path = output_root / "outcome_attachments" / f"{source_row['row_id']}.json"
    status = write_immutable(path, attachment)
    return {"status": status, "row_id": source_row["row_id"], "path": path.as_posix(), "attachment_sha256": digest(attachment)}


def json_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*.json") if path.name != "LATEST.json")


def source_rows_by_divergence_id(output_root: Path) -> dict[str, tuple[Path, dict[str, Any]]]:
    rows: dict[str, tuple[Path, dict[str, Any]]] = {}
    for path in json_files(output_root / "source_rows"):
        row = read_json(path)
        validate_source_row(row)
        key = str(row.get("source_divergence_row_id") or "")
        if not key:
            raise ValueError("source_divergence_row_id_required")
        if key in rows:
            raise ValueError(f"duplicate_t5_source_divergence_id:{key}")
        rows[key] = (path, row)
    return rows


def scan(receipt_root: Path, maturity_root: Path, output_root: Path, run_id: str, as_of_utc: str | None) -> dict[str, Any]:
    created = duplicate = ignored = invalid = 0
    errors: list[str] = []

    for path in json_files(receipt_root):
        try:
            receipt = read_json(path)
            if receipt.get("contract") != T2_RECEIPT_CONTRACT:
                ignored += 1
                continue
            if receipt.get("status") != "DIVERGENCE_CAPTURED":
                ignored += 1
                continue
            result = freeze_receipt(receipt, output_root)
            if result["status"] == "CREATED":
                created += 1
            else:
                duplicate += 1
        except Exception as exc:
            invalid += 1
            errors.append(f"{path.as_posix()}:{exc}")

    attachments_created = attachments_duplicate = 0
    rows = source_rows_by_divergence_id(output_root)
    for path in json_files(maturity_root):
        try:
            maturity = read_json(path)
            if maturity.get("contract") != T2_MATURITY_CONTRACT:
                continue
            row_id = str(maturity.get("row_id") or "")
            pair = rows.get(row_id)
            if pair is None:
                continue
            result = attach_maturity(pair[1], maturity, output_root)
            if result["status"] == "CREATED":
                attachments_created += 1
            else:
                attachments_duplicate += 1
        except Exception as exc:
            invalid += 1
            errors.append(f"{path.as_posix()}:{exc}")

    if as_of_utc:
        generated = iso_z(parse_utc(as_of_utc, "as_of_utc"))
    else:
        generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    run = {
        "contract": RUN_CONTRACT,
        "run_id": run_id,
        "generated_at_utc": generated,
        "source_receipt_root": receipt_root.as_posix(),
        "maturity_receipt_root": maturity_root.as_posix(),
        "source_rows_created": created,
        "source_rows_duplicate_noop": duplicate,
        "source_receipts_ignored_nondivergence_or_other_contract": ignored,
        "outcome_attachments_created": attachments_created,
        "outcome_attachments_duplicate_noop": attachments_duplicate,
        "invalid_input_count": invalid,
        "errors": errors,
        "current_source_row_count": len(source_rows_by_divergence_id(output_root)),
        "authoritative_fnp_evaluator_available": False,
        "derived_fnp_metrics_emitted": False,
        "retrospective_backfill_performed": False,
        "status": "PASS_NO_ELIGIBLE_INPUT" if created == 0 and duplicate == 0 and invalid == 0 else ("PASS" if invalid == 0 else "FAIL_CLOSED"),
        "authority": AUTHORITY,
    }
    if invalid:
        raise ValueError("invalid_t5_inputs:" + "|".join(errors[:5]))
    run_path = output_root / "runs" / f"{run_id}.json"
    write_immutable(run_path, run)
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "LATEST.json").write_bytes(canonical_bytes(run))
    return run


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    scan_parser = sub.add_parser("scan")
    scan_parser.add_argument("--t2-receipt-root", type=Path, required=True)
    scan_parser.add_argument("--t2-maturity-root", type=Path, required=True)
    scan_parser.add_argument("--output-root", type=Path, required=True)
    scan_parser.add_argument("--run-id", required=True)
    scan_parser.add_argument("--as-of-utc")

    freeze_parser = sub.add_parser("freeze")
    freeze_parser.add_argument("--receipt", type=Path, required=True)
    freeze_parser.add_argument("--output-root", type=Path, required=True)

    attach_parser = sub.add_parser("attach")
    attach_parser.add_argument("--source-row", type=Path, required=True)
    attach_parser.add_argument("--maturity", type=Path, required=True)
    attach_parser.add_argument("--output-root", type=Path, required=True)

    validate_parser = sub.add_parser("validate-root")
    validate_parser.add_argument("--output-root", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "scan":
        result = scan(args.t2_receipt_root, args.t2_maturity_root, args.output_root, args.run_id, args.as_of_utc)
    elif args.command == "freeze":
        result = freeze_receipt(read_json(args.receipt), args.output_root)
    elif args.command == "attach":
        result = attach_maturity(read_json(args.source_row), read_json(args.maturity), args.output_root)
    else:
        rows = source_rows_by_divergence_id(args.output_root)
        result = {
            "status": "PASS",
            "source_row_count": len(rows),
            "duplicate_source_divergence_ids": 0,
            "authority": AUTHORITY,
        }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
