#!/usr/bin/env python3
"""Mature outcomes from immutable hourly source commits.

The row-time baseline is reconstructed from its frozen source commit and reconciled
against the later append-only hourly tree. A mismatch, gap, duplicate, mutable source
or incomplete horizon remains unavailable and is never scored.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import core_shared_row_materializer as core
import prospective_evidence_controller as evidence

REPO_ROOT = Path(".")
ROOT = Path("06_RESEARCH_LAB/shared_row_model_tournament_v1")
ROWS = ROOT / "data/PROSPECTIVE_SHARED_ROW_LEDGER.csv"
DETAIL = ROOT / "data/OUTCOME_DETAIL_LEDGER.csv"
HOURLY = Path("03_DAILY_CAPTURE_LOGS/hourly")
CONTRACT = ROOT / "CORE_FAMILY_PROSPECTIVE_CONTRACT_v1.json"
HORIZONS = {"24h": 24, "72h": 72, "7d": 168}


def parse(value: str) -> datetime:
    return core.parse_ts(value)


def iso(value: datetime) -> str:
    return core.iso(value)


def canon(value: Any) -> str:
    return core.canon(value)


def pct(value: float, baseline: float) -> float:
    return (value / baseline - 1.0) * 100.0


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def detail_keys() -> set[tuple[str, str]]:
    return {(row["event_id"], row["horizon"]) for row in read_csv(DETAIL)}


def append_detail(row: dict[str, Any]) -> None:
    with DETAIL.open(newline="", encoding="utf-8-sig") as handle:
        fields = next(csv.reader(handle))
    with DETAIL.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writerow({key: row.get(key, "") for key in fields})


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception as exc:
        raise RuntimeError("OUTCOME_SOURCE_COMMIT_UNAVAILABLE") from exc


def _hourly_prefix() -> str:
    try:
        return HOURLY.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError as exc:
        raise RuntimeError("OUTCOME_HOURLY_PATH_OUTSIDE_REPOSITORY") from exc


def hourly_payloads(commit: str) -> list[tuple[str, bytes]]:
    prefix = _hourly_prefix()
    try:
        output = subprocess.check_output(
            ["git", "-C", str(REPO_ROOT), "ls-tree", "-r", "--name-only", commit, "--", prefix],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception as exc:
        raise RuntimeError("OUTCOME_SOURCE_TREE_UNREACHABLE") from exc
    paths = sorted(path for path in output.splitlines() if path.endswith(".csv"))
    if not paths:
        raise RuntimeError("OUTCOME_HOURLY_SOURCE_PATHS_MISSING")
    return [(path, core.git_blob(commit, path)) for path in paths]


def source_bindings(commit: str, payloads: list[tuple[str, bytes]]) -> list[dict[str, Any]]:
    return [
        {
            "path": path,
            "sha256": core.sha_bytes(payload),
            "bytes": len(payload),
            "source_commit": commit,
            "owner_contract": "HOURLY_SEQUENCE_CAPTURE_v2_2_DIRECT_BINANCE_SPOT",
            "provider": "Binance spot",
        }
        for path, payload in payloads
    ]


def _unique_records(records: list[dict[str, Any]]) -> dict[datetime, dict[str, Any]]:
    counts = Counter(row["ts"] for row in records)
    duplicates = sorted(timestamp for timestamp, count in counts.items() if count != 1)
    if duplicates:
        raise RuntimeError(f"OUTCOME_SOURCE_DUPLICATE_TIMESTAMP:{iso(duplicates[-1])}")
    return {row["ts"]: row for row in records}


def select_end(records: dict[datetime, dict[str, Any]], target: datetime, wall: datetime) -> dict[str, Any] | None:
    candidates = [
        row
        for timestamp, row in records.items()
        if target <= timestamp <= target + timedelta(hours=1) and row["available"] <= wall
    ]
    return min(candidates, key=lambda row: row["ts"]) if candidates else None


def continuous_path(
    records: dict[datetime, dict[str, Any]], start: datetime, end: datetime, wall: datetime
) -> list[dict[str, Any]] | None:
    output = []
    cursor = start
    while cursor <= end:
        row = records.get(cursor)
        if row is None or row["available"] > wall:
            return None
        output.append(row)
        cursor += timedelta(hours=1)
    return output


def calc(asset: str, baseline: dict[str, Any], end: dict[str, Any], path_rows: list[dict[str, Any]]) -> dict[str, float]:
    base_value = float(baseline[asset])
    end_value = float(end[asset])
    returns = [pct(float(row[asset]), base_value) for row in path_rows]
    return {
        "baseline": base_value,
        "end": end_value,
        "forward": pct(end_value, base_value),
        "mae": min(returns),
        "mfe": max(returns),
    }


def _baseline_matches(current: dict[str, Any], frozen: dict[str, Any]) -> bool:
    return bool(
        iso(current["ts"]) == frozen.get("timestamp_utc")
        and iso(current["available"]) == frozen.get("source_window_end_utc")
        and float(current["ethbtc"]) == float(frozen.get("ethbtc_close"))
        and float(current["btc"]) == float(frozen.get("btc_close"))
        and float(current["eth"]) == float(frozen.get("eth_close"))
    )


def run(now_override: str | None = None) -> dict[str, Any]:
    shared_rows = read_csv(ROWS)
    fields = list(shared_rows[0].keys()) if shared_rows else []
    if not shared_rows:
        return {
            "status": "PASS",
            "rows": 0,
            "horizons_written": 0,
            "unavailable_horizons": 0,
            "outcome_contract": "ETHBTC_FORWARD_RELATIVE_RETURN_OUTCOME_v1",
        }
    wall = parse(now_override) if now_override else datetime.now(timezone.utc)
    wall = wall.replace(microsecond=0)
    outcome_commit = git_head()
    core.REPO_ROOT = REPO_ROOT
    evidence.REPO_ROOT = REPO_ROOT
    evidence.CONTRACT = CONTRACT
    payloads = hourly_payloads(outcome_commit)
    all_records = core.parse_hourly_payloads(payloads)
    records = _unique_records(all_records)
    bindings_by_path = {item["path"]: item for item in source_bindings(outcome_commit, payloads)}
    existing = detail_keys()
    changed = 0
    unavailable: Counter[str] = Counter()
    frozen_decisions = {row["event_id"]: row.get("candidate_decisions", "") for row in shared_rows}
    frozen_identity = {
        row["event_id"]: (
            row.get("observation_timestamp_utc", ""),
            row.get("information_cutoff_utc", ""),
            row.get("source_version_commit", ""),
            row.get("source_binding_manifest_sha256", ""),
            row.get("provenance_hash", ""),
        )
        for row in shared_rows
    }
    for row in shared_rows:
        if row.get("row_integrity_contract") != core.ROW_INTEGRITY_CONTRACT:
            unavailable["PRE_REPAIR_OR_UNBOUND_ROW"] += len(HORIZONS)
            continue
        try:
            evidence.verify_frozen_provenance(row)
        except Exception:
            unavailable["ROW_FROZEN_PROVENANCE_MISMATCH"] += len(HORIZONS)
            continue
        try:
            verified = evidence.verify_source_bindings(row, parse(row["information_cutoff_utc"]))
        except Exception:
            unavailable["ROW_SOURCE_BINDING_RECONSTRUCTION_FAILED"] += len(HORIZONS)
            continue
        frozen_baseline = verified["baseline"]
        baseline_ts = parse(frozen_baseline["timestamp_utc"])
        current_baseline = records.get(baseline_ts)
        if current_baseline is None or not _baseline_matches(current_baseline, frozen_baseline):
            unavailable["ROW_TIME_BASELINE_MISMATCH"] += len(HORIZONS)
            continue
        for horizon, hours in HORIZONS.items():
            outcome_field = f"outcome_{horizon}"
            mae_field = f"mae_{horizon}"
            mfe_field = f"mfe_{horizon}"
            key = (row["event_id"], horizon)
            if str(row.get(outcome_field, "")).strip():
                if key not in existing:
                    raise RuntimeError("matured outcome field lacks append-only detail binding")
                continue
            target = parse(row["information_cutoff_utc"]) + timedelta(hours=hours)
            if wall < target:
                continue
            end = select_end(records, target, wall)
            if end is None:
                unavailable["HORIZON_END_UNAVAILABLE"] += 1
                continue
            path_rows = continuous_path(records, baseline_ts, end["ts"], wall)
            if path_rows is None:
                unavailable["HORIZON_PATH_NOT_HOURLY_CONTINUOUS"] += 1
                continue
            ethbtc = calc("ethbtc", current_baseline, end, path_rows)
            btc = calc("btc", current_baseline, end, path_rows)
            eth = calc("eth", current_baseline, end, path_rows)
            row[outcome_field] = "1" if ethbtc["forward"] > 0 else "0"
            row[mae_field] = f"{ethbtc['mae']:.8f}"
            row[mfe_field] = f"{ethbtc['mfe']:.8f}"
            if key not in existing:
                used_bindings = [bindings_by_path[path] for path in sorted({item["path"] for item in path_rows})]
                detail = {
                    "event_id": row["event_id"],
                    "horizon": horizon,
                    "observation_timestamp_utc": row["observation_timestamp_utc"],
                    "information_cutoff_utc": row["information_cutoff_utc"],
                    "target_timestamp_utc": iso(target),
                    "selected_end_timestamp_utc": iso(end["ts"]),
                    "baseline_timestamp_utc": iso(current_baseline["ts"]),
                    "ethbtc_baseline": ethbtc["baseline"],
                    "ethbtc_end": ethbtc["end"],
                    "ethbtc_forward_return_pct": ethbtc["forward"],
                    "ethbtc_mae_pct": ethbtc["mae"],
                    "ethbtc_mfe_pct": ethbtc["mfe"],
                    "btc_baseline": btc["baseline"],
                    "btc_end": btc["end"],
                    "btc_forward_return_pct": btc["forward"],
                    "btc_mae_pct": btc["mae"],
                    "btc_mfe_pct": btc["mfe"],
                    "eth_baseline": eth["baseline"],
                    "eth_end": eth["end"],
                    "eth_forward_return_pct": eth["forward"],
                    "eth_mae_pct": eth["mae"],
                    "eth_mfe_pct": eth["mfe"],
                    "sample_count": len(path_rows),
                    "source_contract": "HOURLY_SEQUENCE_CAPTURE_v2_2_DIRECT_BINANCE_SPOT",
                    "row_source_commit": row["source_version_commit"],
                    "row_source_binding_sha256": row["source_binding_manifest_sha256"],
                    "outcome_source_commit": outcome_commit,
                    "outcome_source_bindings": canon(used_bindings),
                    "baseline_reconciled": True,
                    "matured_at_utc": iso(wall),
                }
                detail["provenance_hash"] = hashlib.sha256(canon(detail).encode("utf-8")).hexdigest()
                append_detail(detail)
                existing.add(key)
            changed += 1
    for row in shared_rows:
        event_id = row["event_id"]
        if row.get("candidate_decisions", "") != frozen_decisions[event_id]:
            raise RuntimeError("candidate decisions changed during outcome maturation")
        identity = (
            row.get("observation_timestamp_utc", ""),
            row.get("information_cutoff_utc", ""),
            row.get("source_version_commit", ""),
            row.get("source_binding_manifest_sha256", ""),
            row.get("provenance_hash", ""),
        )
        if identity != frozen_identity[event_id]:
            raise RuntimeError("frozen row identity changed during outcome maturation")
    if changed:
        write_csv(ROWS, shared_rows, fields)
    return {
        "status": "PASS",
        "rows": len(shared_rows),
        "horizons_written": changed,
        "unavailable_horizons": sum(unavailable.values()),
        "unavailable_reasons": dict(sorted(unavailable.items())),
        "outcome_source_commit": outcome_commit,
        "outcome_contract": "ETHBTC_FORWARD_RELATIVE_RETURN_OUTCOME_v1",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--now-utc")
    args = parser.parse_args()
    print(json.dumps(run(args.now_utc), sort_keys=True))


if __name__ == "__main__":
    main()
