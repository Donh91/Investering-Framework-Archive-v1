from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

SOURCE_CONTRACT = "DAILY_SETTLED_ETF_CALIBRATION_v1"
ADAPTER_CONTRACT = "ETF_OWNER_INPUT_ADAPTER_v1"
JOIN_CONTRACT = "ETF_OWNER_ASOF_JOIN_v1"


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


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


def validate_owner_record(path: Path) -> OwnerRecord:
    try:
        record = json.loads(path.read_text())
    except Exception as exc:
        raise ValueError(f"INVALID_JSON:{path}") from exc

    if record.get("contract") != SOURCE_CONTRACT:
        raise ValueError(f"CONTRACT_MISMATCH:{path}")
    if record.get("authority") != "SHADOW_CALIBRATION_INPUT_ONLY":
        raise ValueError(f"AUTHORITY_MISMATCH:{path}")
    if record.get("canonical_data_ping") is not False:
        raise ValueError(f"CANONICAL_AUTHORITY_VIOLATION:{path}")
    if record.get("framework_state_change") is not False or record.get("portfolio_action") is not False:
        raise ValueError(f"STATE_AUTHORITY_VIOLATION:{path}")

    verification = record.get("verification") or {}
    required = {
        "retrieval_count": 2,
        "rows_identical_across_retrievals": True,
        "all_fund_cells_known": True,
        "total_parity_required": True,
        "source": "FARSIDE_CANONICAL_TABLES",
    }
    for key, expected in required.items():
        if verification.get(key) != expected:
            raise ValueError(f"VERIFICATION_FAILURE:{key}:{path}")
    if float(verification.get("minimum_separation_seconds", 0)) < 60:
        raise ValueError(f"VERIFICATION_FAILURE:minimum_separation_seconds:{path}")

    session = str(record.get("session_date") or "")
    try:
        date.fromisoformat(session)
    except Exception as exc:
        raise ValueError(f"INVALID_SESSION_DATE:{path}") from exc

    known_at_raw = record.get("retrieved_at_utc")
    if not known_at_raw:
        raise ValueError(f"MISSING_KNOWN_AT:{path}")
    known_at = parse_utc(str(known_at_raw))

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
        if asset not in {"BTC", "ETH"} or asset in by_asset:
            raise ValueError(f"ASSET_SET_INVALID:{path}")
        if row.get("date") != session:
            raise ValueError(f"SESSION_ROW_MISMATCH:{path}")
        if row.get("session_final") is not True or row.get("total_parity") is not True:
            raise ValueError(f"ROW_NOT_SETTLED:{path}")
        values = row.get("fund_values")
        if not isinstance(values, list) or not values or any(value is None for value in values):
            raise ValueError(f"UNKNOWN_FUND_CELL:{path}")
        try:
            float(row["reported_total"])
            float(row["calculated_total"])
        except Exception as exc:
            raise ValueError(f"TOTAL_INVALID:{path}") from exc
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
    )


def load_owner_records(root: Path) -> list[OwnerRecord]:
    records: list[OwnerRecord] = []
    if not root.exists():
        return records
    for path in sorted(root.rglob("*.json")):
        if path.name == "LATEST.json":
            continue
        records.append(validate_owner_record(path))
    return sorted(records, key=lambda row: (row.known_at_utc, row.session_date, row.path))


def asof_join(records: list[OwnerRecord], cutoff_utc: datetime) -> dict[str, Any]:
    cutoff = cutoff_utc.astimezone(timezone.utc)
    eligible = [row for row in records if row.known_at_utc <= cutoff]
    base: dict[str, Any] = {
        "contract": JOIN_CONTRACT,
        "adapter_contract": ADAPTER_CONTRACT,
        "authority": "SHADOW_RESEARCH_INPUT_ONLY",
        "cutoff_utc": iso_utc(cutoff),
        "selection_rule": "MAX(retrieved_at_utc) WHERE retrieved_at_utc <= cutoff_utc",
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

    selected = max(eligible, key=lambda row: (row.known_at_utc, row.session_date, row.path))
    base.update({
        "status": "AVAILABLE",
        "source_path": selected.path,
        "session_date": selected.session_date,
        "known_at_utc": iso_utc(selected.known_at_utc),
        "row_signature_sha256": selected.row_signature_sha256,
        "session_age_calendar_days_at_cutoff": (cutoff.date() - date.fromisoformat(selected.session_date)).days,
        "raw_reported_totals": {"BTC": selected.btc_reported_total, "ETH": selected.eth_reported_total},
    })
    return base


def readiness(root: Path) -> dict[str, Any]:
    records = load_owner_records(root)
    return {
        "contract": "ETF_OWNER_ADAPTER_PREFLIGHT_v1",
        "adapter_contract": ADAPTER_CONTRACT,
        "source_contract": SOURCE_CONTRACT,
        "status": "VERIFIED_ADAPTER_WITH_OWNER_ROWS" if records else "VERIFIED_ADAPTER_PENDING_FIRST_OWNER_ROW",
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
        result = asof_join(load_owner_records(args.etf_root), parse_utc(args.cutoff_utc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
