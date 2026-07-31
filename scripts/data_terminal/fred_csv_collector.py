#!/usr/bin/env python3
"""Shadow-only, dependency-free FRED CSV owner collector."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

AUTHORITY = {"binding": False, "canonical_acceptance": False, "state_change": False, "portfolio_action": False}
DEFAULT_SERIES = ("DGS2", "DGS10", "DTWEXBGS", "VIXCLS")
DEFAULT_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
DEFAULT_STALE_AFTER_SECONDS = 7 * 24 * 60 * 60
USER_AGENT = "Investering-Data-Terminal-Shadow/0.2 (+https://github.com/Donh91/Investering-Framework-Archive-v1)"
UNITS = {"DGS2": "PERCENT", "DGS10": "PERCENT", "DTWEXBGS": "INDEX", "VIXCLS": "INDEX"}


class CollectorError(RuntimeError):
    def __init__(self, status: str, message: str):
        super().__init__(message)
        self.status = status


@dataclass(frozen=True)
class Observation:
    date: str
    value: float


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def parse_timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CollectorError("MALFORMED_TIMESTAMP", f"Invalid ISO-8601 timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise CollectorError("MALFORMED_TIMESTAMP", "Timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def utc_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_series(series: str | Iterable[str]) -> tuple[str, ...]:
    values = tuple(item.strip().upper() for item in ([series] if isinstance(series, str) else series) if item.strip())
    if not values or len(values) != len(set(values)):
        raise CollectorError("INVALID_SERIES_SET", "Series set must be non-empty and unique")
    return values


def fetch_payload(url: str, timeout: float, retries: int, backoff: float) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/csv"})
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = response.read()
                if not payload:
                    raise CollectorError("EMPTY_RESPONSE", "FRED returned an empty payload")
                return payload
        except CollectorError:
            raise
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(backoff * (2**attempt))
    raise CollectorError("NETWORK_ERROR", f"FRED retrieval failed after {retries + 1} attempts: {last_error}")


def load_payload(fixture: Path | None, url: str, timeout: float, retries: int, backoff: float) -> tuple[bytes, str]:
    if fixture is not None:
        try:
            payload = fixture.read_bytes()
        except OSError as exc:
            raise CollectorError("FIXTURE_READ_ERROR", str(exc)) from exc
        if not payload:
            raise CollectorError("EMPTY_RESPONSE", "Fixture payload is empty")
        return payload, "FIXTURE"
    return fetch_payload(url, timeout, retries, backoff), "NETWORK"


def parse_fred_csv(payload: bytes, series: str | Iterable[str]) -> tuple[dict[str, list[Observation]], list[dict[str, str]]]:
    series_set = normalize_series(series)
    try:
        text = payload.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise CollectorError("SCHEMA_DRIFT", "Payload is not valid UTF-8 CSV") from exc
    reader = csv.DictReader(text.splitlines())
    if reader.fieldnames is None:
        raise CollectorError("EMPTY_RESPONSE", "CSV has no header")
    date_column = "DATE" if "DATE" in reader.fieldnames else "observation_date" if "observation_date" in reader.fieldnames else None
    missing_columns = [item for item in series_set if item not in reader.fieldnames]
    if date_column is None or missing_columns:
        raise CollectorError("SCHEMA_DRIFT", f"Expected date column and series {series_set}; got {reader.fieldnames}")
    observations = {item: [] for item in series_set}
    missing: list[dict[str, str]] = []
    seen_dates: set[str] = set()
    for row_number, row in enumerate(reader, start=2):
        date_value = (row.get(date_column) or "").strip()
        try:
            source_date = datetime.strptime(date_value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError as exc:
            raise CollectorError("MALFORMED_TIMESTAMP", f"Invalid source date at CSV row {row_number}: {date_value}") from exc
        if date_value in seen_dates:
            raise CollectorError("DUPLICATE_TIMESTAMP", f"Duplicate source date: {date_value}")
        seen_dates.add(date_value)
        for item in series_set:
            raw_value = (row.get(item) or "").strip()
            if raw_value in {"", ".", "NA", "N/A", "null"}:
                missing.append({"field": item, "source_date": date_value, "status": "UNKNOWN"})
                continue
            try:
                numeric_value = float(raw_value)
            except ValueError as exc:
                raise CollectorError("SCHEMA_DRIFT", f"Non-numeric {item} value at CSV row {row_number}: {raw_value}") from exc
            observations[item].append(Observation(date=utc_iso(source_date), value=numeric_value))
    empty = [item for item, rows in observations.items() if not rows]
    if empty:
        raise CollectorError("EMPTY_RESPONSE", f"No usable observations for: {empty}")
    for rows in observations.values():
        rows.sort(key=lambda item: item.date)
    return observations, missing


def build_artifacts(*, payload: bytes, retrieval_timestamp: datetime, series: str | Iterable[str], source_url: str, acquisition_mode: str, stale_after_seconds: int) -> dict[str, dict[str, Any]]:
    series_set = normalize_series(series)
    rows_by_series, missing = parse_fred_csv(payload, series_set)
    payload_hash = sha256_bytes(payload)
    run_id = f"DT_FRED_MULTI_{retrieval_timestamp.strftime('%Y%m%dT%H%M%SZ')}_{payload_hash[:12]}"
    health_rows: list[dict[str, Any]] = []
    observations: dict[str, dict[str, Any]] = {}
    for item in series_set:
        latest = rows_by_series[item][-1]
        source_timestamp = parse_timestamp(latest.date)
        freshness = max(0, int((retrieval_timestamp - source_timestamp).total_seconds()))
        status = "PASS" if freshness <= stale_after_seconds else "STALE"
        health_rows.append({"source_id": "FRED_CSV_MACRO_CORE", "series": item, "status": status, "source_timestamp": utc_iso(source_timestamp), "retrieval_timestamp": utc_iso(retrieval_timestamp), "freshness_seconds": freshness, "stale_after_seconds": stale_after_seconds, "payload_sha256": payload_hash, "acquisition_mode": acquisition_mode, "source_substitution": {"used": False, "substitute_source_id": None, "reason": None}, "authority": AUTHORITY})
        observations[item] = {"observation_id": f"FRED:{item}:{source_timestamp.date().isoformat()}", "source_id": "FRED_CSV_MACRO_CORE", "field": item, "value": latest.value, "unit": UNITS.get(item, "SOURCE_REPORTED"), "direct_or_derived": "DIRECT", "source_convention": "FRED_REPORTED_DAILY_OBSERVATION", "venue_specific": False, "source_timestamp": utc_iso(source_timestamp), "retrieval_timestamp": utc_iso(retrieval_timestamp), "payload_sha256": payload_hash, "revision_policy": "APPEND_ONLY_DO_NOT_OVERWRITE_PRIOR_RECEIPTS", "authority": AUTHORITY}
    aggregate_status = "PASS" if all(row["status"] == "PASS" for row in health_rows) else "STALE"
    receipt_material = {"run_id": run_id, "source_id": "FRED_CSV_MACRO_CORE", "series": list(series_set), "source_url": source_url, "retrieval_timestamp": utc_iso(retrieval_timestamp), "payload_sha256": payload_hash, "source_timestamps": {item: observations[item]["source_timestamp"] for item in series_set}, "status": aggregate_status, "observation_ids": [observations[item]["observation_id"] for item in series_set], "missing": missing, "conflicts": [], "source_substitution": {"used": False, "substitute_source_id": None, "reason": None}, "authority": AUTHORITY}
    receipt = dict(receipt_material)
    receipt["receipt_sha256"] = sha256_bytes(canonical_json_bytes(receipt_material))
    snapshot = {"snapshot_id": f"{run_id}_SNAPSHOT", "run_id": run_id, "status": aggregate_status, "source_lineage": {"source_health": health_rows, "receipt_sha256": receipt["receipt_sha256"]}, "observations": observations, "missing": missing, "conflicts": [], "authority": AUTHORITY}
    handoff = {"handoff_id": f"{run_id}_DATA_PING_CANDIDATE", "parent_terminal_run_id": run_id, "quality": {"status": aggregate_status, "source_count": 1, "series_count": len(series_set)}, "source_lineage": {"source_id": "FRED_CSV_MACRO_CORE", "payload_sha256": payload_hash, "receipt_sha256": receipt["receipt_sha256"]}, "observations": {"macro_core": observations}, "missing": missing, "conflicts": [], "artifacts": {"source_health": "source_health.json", "receipt": f"receipts/{run_id}__receipt.json", "snapshot": f"snapshots/{run_id}__snapshot.json", "manifest": "artifact_manifest.json"}, "authority": AUTHORITY}
    terminal_state = {"pointer_version": "0.2", "status": "SHADOW_CANDIDATE_ONLY", "run_id": run_id, "target_path": f"snapshots/{run_id}__snapshot.json", "target_sha256": sha256_bytes(canonical_json_bytes(snapshot)), "updated_at": utc_iso(retrieval_timestamp), "source_health": health_rows, "missing": sorted({item["field"] for item in missing}), "conflicts": [], "authority": AUTHORITY}
    return {"source_health": {"run_id": run_id, "status": aggregate_status, "series": health_rows, "authority": AUTHORITY}, "receipt": receipt, "snapshot": snapshot, "handoff": handoff, "terminal_state": terminal_state}


def write_artifacts(output_dir: Path, artifacts: dict[str, dict[str, Any]], raw_payload: bytes | None = None) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "receipts").mkdir(exist_ok=True)
    (output_dir / "snapshots").mkdir(exist_ok=True)
    (output_dir / "raw").mkdir(exist_ok=True)
    run_id = str(artifacts["receipt"]["run_id"])
    paths: dict[Path, Any] = {output_dir / "source_health.json": artifacts["source_health"], output_dir / "receipts" / f"{run_id}__receipt.json": artifacts["receipt"], output_dir / "snapshots" / f"{run_id}__snapshot.json": artifacts["snapshot"], output_dir / "latest_terminal_state.json": artifacts["terminal_state"], output_dir / "latest_data_ping_handoff.json": artifacts["handoff"]}
    for path, value in paths.items():
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    written = list(paths)
    if raw_payload is not None:
        raw_path = output_dir / "raw" / f"{run_id}__fred.csv"
        raw_path.write_bytes(raw_payload)
        written.append(raw_path)
    manifest_members = []
    for path in sorted(written):
        payload = path.read_bytes()
        manifest_members.append({"path": path.relative_to(output_dir).as_posix(), "bytes": len(payload), "sha256": sha256_bytes(payload)})
    manifest = {"contract": "WP04C5B_ARTIFACT_MANIFEST_v1", "run_id": run_id, "member_count": len(manifest_members), "members": manifest_members, "authority": AUTHORITY}
    manifest_path = output_dir / "artifact_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    written.append(manifest_path)
    return sorted(written)


def verify_artifact_readback(output_dir: Path) -> dict[str, Any]:
    manifest = json.loads((output_dir / "artifact_manifest.json").read_text(encoding="utf-8"))
    failures = []
    for member in manifest["members"]:
        path = output_dir / member["path"]
        if not path.is_file():
            failures.append({"path": member["path"], "reason": "MISSING"})
            continue
        payload = path.read_bytes()
        if len(payload) != member["bytes"] or sha256_bytes(payload) != member["sha256"]:
            failures.append({"path": member["path"], "reason": "HASH_OR_SIZE_MISMATCH"})
    return {"status": "PASS" if not failures else "FAIL", "member_count": manifest["member_count"], "failures": failures, "authority": AUTHORITY}


def error_payload(status: str, message: str, retrieval_timestamp: datetime) -> dict[str, Any]:
    return {"status": status, "error": message, "retrieval_timestamp": utc_iso(retrieval_timestamp), "missing": ["SOURCE_OBSERVATION"], "conflicts": [], "authority": AUTHORITY}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--series", default=",".join(DEFAULT_SERIES))
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--fixture", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path(".data-terminal-output"))
    parser.add_argument("--retrieval-timestamp")
    parser.add_argument("--stale-after-seconds", type=int, default=DEFAULT_STALE_AFTER_SECONDS)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--backoff", type=float, default=0.25)
    args = parser.parse_args()
    retrieval = parse_timestamp(args.retrieval_timestamp) if args.retrieval_timestamp else datetime.now(timezone.utc)
    series_set = normalize_series(args.series.split(","))
    source_url = args.url.format(series=",".join(series_set))
    try:
        payload, acquisition_mode = load_payload(args.fixture, source_url, args.timeout, args.retries, args.backoff)
        artifacts = build_artifacts(payload=payload, retrieval_timestamp=retrieval, series=series_set, source_url=source_url, acquisition_mode=acquisition_mode, stale_after_seconds=args.stale_after_seconds)
        paths = write_artifacts(args.output_dir, artifacts, raw_payload=payload)
        readback = verify_artifact_readback(args.output_dir)
        print(json.dumps({"status": artifacts["receipt"]["status"], "readback": readback, "paths": [str(path) for path in paths]}, sort_keys=True))
        return 0 if artifacts["receipt"]["status"] == "PASS" and readback["status"] == "PASS" else 3
    except CollectorError as exc:
        print(json.dumps(error_payload(exc.status, str(exc), retrieval), sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
