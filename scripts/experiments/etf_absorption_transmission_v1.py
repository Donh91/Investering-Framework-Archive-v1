from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

SOURCE_CONTRACT = "DAILY_SETTLED_ETF_CALIBRATION_v2"
SOURCE_IDENTITIES = {
    "DAILY_SETTLED_ETF_CALIBRATION_v1": "FARSIDE_CANONICAL_TABLES",
    SOURCE_CONTRACT: "FARSIDE_CANONICAL_ALL_DATA_TABLES",
}
ADAPTER_CONTRACT = "ETF_OWNER_INPUT_ADAPTER_v1"
JOIN_CONTRACT = "ETF_OWNER_ASOF_JOIN_v1"


def parse_utc(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("INVALID_KNOWN_AT")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.utcoffset() is None:
        raise ValueError("TIMEZONE_REQUIRED")
    return parsed.astimezone(timezone.utc)


def finite_number(value: Any) -> bool:
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def strict_json(path: Path):
    def constant(raw):
        raise ValueError('NON_FINITE_JSON')
    def number(raw):
        value = float(raw)
        if not math.isfinite(value):
            raise ValueError('NON_FINITE_JSON')
        return value
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('DUPLICATE_JSON_KEY')
            result[key] = value
        return result
    return json.loads(path.read_text(), parse_float=number, parse_constant=constant, object_pairs_hook=pairs)


def iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rows_signature(rows: list[dict[str, Any]]) -> str:
    return hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class OwnerRecord:
    path: str
    session_date: str
    known_at_utc: datetime
    row_signature_sha256: str
    btc_reported_total: float
    eth_reported_total: float
    source_contract: str = SOURCE_CONTRACT


def validate_owner_record(path: Path) -> OwnerRecord:
    try:
        record = strict_json(path)
    except Exception as exc:
        raise ValueError(f"INVALID_JSON:{path}") from exc

    if not isinstance(record, dict):
        raise ValueError(f"RECORD_OBJECT_REQUIRED:{path}")
    contract = record.get("contract")
    if not isinstance(contract, str) or contract not in SOURCE_IDENTITIES:
        raise ValueError(f"CONTRACT_MISMATCH:{path}")
    if record.get("authority") != "SHADOW_CALIBRATION_INPUT_ONLY":
        raise ValueError(f"AUTHORITY_MISMATCH:{path}")
    if record.get("canonical_data_ping") is not False:
        raise ValueError(f"CANONICAL_AUTHORITY_VIOLATION:{path}")
    if record.get("framework_state_change") is not False or record.get("portfolio_action") is not False:
        raise ValueError(f"STATE_AUTHORITY_VIOLATION:{path}")

    verification = record.get("verification") or {}
    if not isinstance(verification, dict):
        raise ValueError(f"VERIFICATION_INVALID:{path}")
    required = {
        "retrieval_count": 2,
        "rows_identical_across_retrievals": True,
        "all_fund_cells_known": True,
        "total_parity_required": True,
        "source": SOURCE_IDENTITIES[contract],
    }
    for key, expected in required.items():
        if type(verification.get(key)) is not type(expected) or verification.get(key) != expected:
            raise ValueError(f"VERIFICATION_FAILURE:{key}:{path}")
    separation = verification.get("minimum_separation_seconds")
    if not finite_number(separation) or separation < 60:
        raise ValueError(f"VERIFICATION_FAILURE:minimum_separation_seconds:{path}")
    if contract == SOURCE_CONTRACT:
        if verification.get('unknown_cells_imputed') is not False or verification.get('unknown_cells_fully_accounted_by_reported_total') is not True:
            raise ValueError(f"VERIFICATION_FAILURE:unknown_cells:{path}")

    session = str(record.get("session_date") or "")
    try:
        date.fromisoformat(session)
    except Exception as exc:
        raise ValueError(f"INVALID_SESSION_DATE:{path}") from exc

    known_at_raw = record.get("retrieved_at_utc")
    if not known_at_raw:
        raise ValueError(f"MISSING_KNOWN_AT:{path}")
    known_at = parse_utc(str(known_at_raw))
    if date.fromisoformat(session) > known_at.date():
        raise ValueError(f"SESSION_AFTER_KNOWLEDGE_TIME:{path}")

    rows = record.get("rows")
    if not isinstance(rows, list) or len(rows) != 2:
        raise ValueError(f"ROW_SET_INVALID:{path}")
    expected_signature = rows_signature(rows)
    if record.get("row_signature_sha256") != expected_signature:
        raise ValueError(f"ROW_SIGNATURE_MISMATCH:{path}")

    by_asset: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError(f"ROW_INVALID:{path}")
        asset = row.get("asset")
        if asset not in ("BTC", "ETH") or asset in by_asset:
            raise ValueError(f"ASSET_SET_INVALID:{path}")
        if row.get("date") != session:
            raise ValueError(f"SESSION_ROW_MISMATCH:{path}")
        if row.get("session_final") is not True or row.get("total_parity") is not True:
            raise ValueError(f"ROW_NOT_SETTLED:{path}")
        values = row.get("fund_values")
        if not isinstance(values, list) or not values or any(value is None for value in values):
            raise ValueError(f"UNKNOWN_FUND_CELL:{path}")
        headers = row.get('fund_headers')
        if (not isinstance(headers, list) or len(headers) != len(values)
                or any(not isinstance(h, str) or not h for h in headers) or len(set(headers)) != len(headers)):
            raise ValueError(f"FUND_HEADER_MISMATCH:{path}")
        reported, calculated = row.get('reported_total'), row.get('calculated_total')
        if not all(finite_number(x) for x in [reported, calculated, *values]):
            raise ValueError(f"TOTAL_INVALID:{path}")
        # Preserve the existing source owner's max(0.2, 1% of reported total)
        # parity tolerance; do not introduce a new market/source rule.
        summed = sum(values)
        if not finite_number(summed) or calculated != summed or abs(summed - reported) > max(0.2, abs(reported) * 0.01):
            raise ValueError(f"TOTAL_PARITY_MISMATCH:{path}")
        if contract == SOURCE_CONTRACT and (type(row.get('unknown_fund_cell_count')) is not int
                or row['unknown_fund_cell_count'] != 0 or row.get('unknown_fund_cells') != []
                or row.get('unknown_cells_fully_accounted_by_reported_total') is not True):
            raise ValueError(f"UNKNOWN_FUND_CELL_METADATA:{path}")
        by_asset[asset] = row

    if set(by_asset) != {"BTC", "ETH"}:
        raise ValueError(f"ASSET_SET_INVALID:{path}")

    return OwnerRecord(
        path=str(path),
        session_date=session,
        known_at_utc=known_at,
        row_signature_sha256=expected_signature,
        btc_reported_total=float(by_asset["BTC"]["reported_total"]),
        eth_reported_total=float(by_asset["ETH"]["reported_total"]),
        source_contract=contract,
    )


def load_owner_records(root: Path, *, diagnostics: list[dict] | None = None) -> list[OwnerRecord]:
    records: list[OwnerRecord] = []
    issues = diagnostics if diagnostics is not None else []
    if not root.is_dir():
        issues.append({'path': str(root), 'reason': 'OWNER_ROOT_UNAVAILABLE'})
        return records
    paths = []
    def scan_error(exc):
        issues.append({'path': str(exc.filename or root), 'reason': 'OWNER_DIRECTORY_UNREADABLE'})
    for directory, _, filenames in os.walk(root, onerror=scan_error):
        paths.extend(Path(directory) / name for name in filenames if name.endswith('.json'))
    for path in sorted(paths):
        if path.name == "LATEST.json":
            continue
        try:
            records.append(validate_owner_record(path))
        except (ValueError, TypeError, OverflowError) as exc:
            issues.append({'path': str(path), 'reason': str(exc).split(':', 1)[0]})
    return sorted(records, key=lambda row: (row.known_at_utc, row.session_date, row.path))


def asof_join(records: list[OwnerRecord], cutoff_utc: datetime) -> dict[str, Any]:
    if cutoff_utc.utcoffset() is None:
        raise ValueError('CUTOFF_TIMEZONE_REQUIRED')
    cutoff = cutoff_utc.astimezone(timezone.utc)
    eligible = [row for row in records if row.known_at_utc <= cutoff]
    base: dict[str, Any] = {
        "contract": JOIN_CONTRACT,
        "adapter_contract": ADAPTER_CONTRACT,
        "authority": "SHADOW_RESEARCH_INPUT_ONLY",
        "cutoff_utc": iso_utc(cutoff),
        "selection_rule": "MAX(session_date), THEN MAX(retrieved_at_utc), WHERE retrieved_at_utc <= cutoff_utc",
        "session_date_is_availability_time": False,
        "asof_last_settled_session": True,
        "synthetic_weekend_rows": False,
        "interpolation": False,
        "forward_fill": False,
        "flow_state_derived": False,
        "event_definition_applied": False,
        "market_interpretation": False,
    }
    if not eligible:
        base.update({"status": "UNAVAILABLE", "reason": "NO_VERIFIED_OWNER_RECORD_KNOWN_BY_CUTOFF"})
        return base

    selected = max(eligible, key=lambda row: (row.session_date, row.known_at_utc, row.path))
    competing = [r for r in eligible if (r.session_date, r.known_at_utc) == (selected.session_date, selected.known_at_utc)]
    if len({r.row_signature_sha256 for r in competing}) != 1:
        base.update(status='UNAVAILABLE', reason='CONFLICTING_OWNER_REVISIONS_AT_SAME_KNOWLEDGE_TIME')
        return base
    base.update({
        "status": "AVAILABLE",
        "source_path": selected.path,
        "source_contract": selected.source_contract,
        "session_date": selected.session_date,
        "known_at_utc": iso_utc(selected.known_at_utc),
        "row_signature_sha256": selected.row_signature_sha256,
        "session_age_calendar_days_at_cutoff": (cutoff.date() - date.fromisoformat(selected.session_date)).days,
        "raw_reported_totals": {"BTC": selected.btc_reported_total, "ETH": selected.eth_reported_total},
    })
    return base


def readiness(root: Path) -> dict[str, Any]:
    diagnostics = []
    records = load_owner_records(root, diagnostics=diagnostics)
    return {
        "contract": "ETF_OWNER_ADAPTER_PREFLIGHT_v1",
        "adapter_contract": ADAPTER_CONTRACT,
        "source_contract": SOURCE_CONTRACT,
        "status": "VERIFIED_ADAPTER_WITH_OWNER_ROWS" if records else ("UNAVAILABLE_OWNER_EVIDENCE" if diagnostics else "VERIFIED_ADAPTER_PENDING_FIRST_OWNER_ROW"),
        "supported_source_contracts": list(SOURCE_IDENTITIES),
        "owner_ingestion_diagnostics": diagnostics,
        "valid_owner_record_count": len(records),
        "external_calls_performed": 0,
        "flow_state_derived": False,
        "event_definition_applied": False,
        "experiment_executed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--etf-root", type=Path, required=True)
    parser.add_argument("--cutoff-utc")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=["preflight", "asof"], required=True)
    args = parser.parse_args()
    if args.mode == "preflight":
        result = readiness(args.etf_root)
    else:
        if not args.cutoff_utc:
            raise SystemExit("cutoff_utc_required")
        diagnostics = []
        result = asof_join(load_owner_records(args.etf_root, diagnostics=diagnostics), parse_utc(args.cutoff_utc))
        result['owner_ingestion_diagnostics'] = diagnostics
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps(result, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
