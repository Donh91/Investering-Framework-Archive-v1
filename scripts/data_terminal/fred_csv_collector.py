#!/usr/bin/env python3
"""Shadow-only, dependency-free FRED CSV collector for Data Terminal Phase 1."""
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
from typing import Any

AUTHORITY = {
    "binding": False,
    "canonical_acceptance": False,
    "state_change": False,
    "portfolio_action": False,
}
DEFAULT_SERIES = "DGS10"
DEFAULT_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
DEFAULT_STALE_AFTER_SECONDS = 7 * 24 * 60 * 60
USER_AGENT = "Investering-Data-Terminal-Shadow/0.1 (+https://github.com/Donh91/Investering-Framework-Archive-v1)"


class CollectorError(RuntimeError):
    """Expected collector failure with an explicit machine status."""

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
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise CollectorError("MALFORMED_TIMESTAMP", f"Invalid ISO-8601 timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise CollectorError("MALFORMED_TIMESTAMP", "Timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def utc_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


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


def parse_fred_csv(payload: bytes, series: str) -> tuple[list[Observation], list[dict[str, str]]]:
    try:
        text = payload.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise CollectorError("SCHEMA_DRIFT", "Payload is not valid UTF-8 CSV") from exc
    reader = csv.DictReader(text.splitlines())
    if reader.fieldnames is None:
        raise CollectorError("EMPTY_RESPONSE", "CSV has no header")
    date_column = "DATE" if "DATE" in reader.fieldnames else "observation_date" if "observation_date" in reader.fieldnames else None
    if date_column is None or series not in reader.fieldnames:
        raise CollectorError("SCHEMA_DRIFT", f"Expected date column and series column {series}; got {reader.fieldnames}")
    observations: list[Observation] = []
    missing: list[dict[str, str]] = []
    for row_number, row in enumerate(reader, start=2):
        date_value = (row.get(date_column) or "").strip()
        raw_value = (row.get(series) or "").strip()
        try:
            source_date = datetime.strptime(date_value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError as exc:
            raise CollectorError("MALFORMED_TIMESTAMP", f"Invalid source date at CSV row {row_number}: {date_value}") from exc
        if raw_value in {"", ".", "NA", "N/A", "null"}:
            missing.append({"field": series, "source_date": date_value, "status": "UNKNOWN"})
            continue
        try:
            numeric_value = float(raw_value)
        except ValueError as exc:
            raise CollectorError("SCHEMA_DRIFT", f"Non-numeric {series} value at CSV row {row_number}: {raw_value}") from exc
        observations.append(Observation(date=utc_iso(source_date), value=numeric_value))
    if not observations:
        raise CollectorError("EMPTY_RESPONSE", "CSV contained no usable observations")
    observations.sort(key=lambda item: item.date)
    return observations, missing


def build_artifacts(
    *,
    payload: bytes,
    retrieval_timestamp: datetime,
    series: str,
    source_url: str,
    acquisition_mode: str,
    stale_after_seconds: int,
) -> dict[str, dict[str, Any]]:
    observations, missing = parse_fred_csv(payload, series)
    latest = observations[-1]
    source_timestamp = parse_timestamp(latest.date)
    freshness_seconds = max(0, int((retrieval_timestamp - source_timestamp).total_seconds()))
    status = "PASS" if freshness_seconds <= stale_after_seconds else "STALE"
    payload_hash = sha256_bytes(payload)
    run_id = f"DT_FRED_{retrieval_timestamp.strftime('%Y%m%dT%H%M%SZ')}_{payload_hash[:12]}"
    source_health = {
        "source_id": "FRED_CSV_MACRO_CORE",
        "series": series,
        "status": status,
        "source_timestamp": utc_iso(source_timestamp),
        "retrieval_timestamp": utc_iso(retrieval_timestamp),
        "freshness_seconds": freshness_seconds,
        "stale_after_seconds": stale_after_seconds,
        "payload_sha256": payload_hash,
        "acquisition_mode": acquisition_mode,
        "source_substitution": {"used": False, "substitute_source_id": None, "reason": None},
        "authority": AUTHORITY,
    }
    observation = {
        "observation_id": f"FRED:{series}:{source_timestamp.date().isoformat()}",
        "source_id": "FRED_CSV_MACRO_CORE",
        "field": series,
        "value": latest.value,
        "unit": "PERCENT",
        "direct_or_derived": "DIRECT",
        "source_convention": "FRED_REPORTED_DAILY_OBSERVATION",
        "venue_specific": False,
        "source_timestamp": utc_iso(source_timestamp),
        "retrieval_timestamp": utc_iso(retrieval_timestamp),
        "payload_sha256": payload_hash,
        "revision_policy": "APPEND_ONLY_DO_NOT_OVERWRITE_PRIOR_RECEIPTS",
        "authority": AUTHORITY,
    }
    receipt_material = {
        "run_id": run_id,
        "source_id": "FRED_CSV_MACRO_CORE",
        "source_url": source_url,
        "retrieval_timestamp": utc_iso(retrieval_timestamp),
        "payload_sha256": payload_hash,
        "source_timestamp": utc_iso(source_timestamp),
        "status": status,
        "observation_ids": [observation["observation_id"]],
        "missing": missing,
        "conflicts": [],
        "source_substitution": source_health["source_substitution"],
        "authority": AUTHORITY,
    }
    receipt = dict(receipt_material)
    receipt["receipt_sha256"] = sha256_bytes(canonical_json_bytes(receipt_material))
    snapshot = {
        "snapshot_id": f"{run_id}_SNAPSHOT",
        "run_id": run_id,
        "status": status,
        "source_lineage": {"source_health": source_health, "receipt_sha256": receipt["receipt_sha256"]},
        "observations": {series: observation},
        "missing": missing,
        "conflicts": [],
        "authority": AUTHORITY,
    }
    handoff = {
        "handoff_id": f"{run_id}_DATA_PING_CANDIDATE",
        "parent_terminal_run_id": run_id,
        "quality": {"status": status, "freshness_seconds": freshness_seconds, "source_count": 1},
        "source_lineage": {"source_id": "FRED_CSV_MACRO_CORE", "payload_sha256": payload_hash, "receipt_sha256": receipt["receipt_sha256"]},
        "observations": {"macro_core": {series: observation}},
        "missing": missing,
        "conflicts": [],
        "artifacts": {
            "source_health": "source_health.json",
            "receipt": f"receipts/{run_id}__receipt.json",
            "snapshot": f"snapshots/{run_id}__snapshot.json",
        },
        "authority": AUTHORITY,
    }
    terminal_state = {
        "pointer_version": "0.1",
        "status": "SHADOW_CANDIDATE_ONLY",
        "run_id": run_id,
        "target_path": f"snapshots/{run_id}__snapshot.json",
        "target_sha256": sha256_bytes(canonical_json_bytes(snapshot)),
        "updated_at": utc_iso(retrieval_timestamp),
        "source_health": [source_health],
        "missing": [item["field"] for item in missing],
        "conflicts": [],
        "authority": AUTHORITY,
    }
    return {
        "source_health": source_health,
        "receipt": receipt,
        "snapshot": snapshot,
        "handoff": handoff,
        "terminal_state": terminal_state,
    }


def write_artifacts(output_dir: Path, artifacts: dict[str, dict[str, Any]]) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "receipts").mkdir(exist_ok=True)
    (output_dir / "snapshots").mkdir(exist_ok=True)
    run_id = str(artifacts["receipt"]["run_id"])
    paths = {
        output_dir / "source_health.json": artifacts["source_health"],
        output_dir / "receipts" / f"{run_id}__receipt.json": artifacts["receipt"],
        output_dir / "snapshots" / f"{run_id}__snapshot.json": artifacts["snapshot"],
        output_dir / "latest_terminal_state.json": artifacts["terminal_state"],
        output_dir / "latest_data_ping_handoff.json": artifacts["handoff"],
    }
    for path, value in paths.items():
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return sorted(paths)


def error_payload(status: str, message: str, retrieval_timestamp: datetime) -> dict[str, Any]:
    return {
        "status": status,
        "error": message,
        "retrieval_timestamp": utc_iso(retrieval_timestamp),
        "missing": ["SOURCE_OBSERVATION"],
        "conflicts": [],
        "authority": AUTHORITY,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--series", default=DEFAULT_SERIES)
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
    source_url = args.url.format(series=args.series)
    try:
        payload, acquisition_mode = load_payload(args.fixture, source_url, args.timeout, args.retries, args.backoff)
        artifacts = build_artifacts(
            payload=payload,
            retrieval_timestamp=retrieval,
            series=args.series,
            source_url=source_url,
            acquisition_mode=acquisition_mode,
            stale_after_seconds=args.stale_after_seconds,
        )
        paths = write_artifacts(args.output_dir, artifacts)
        print(json.dumps({"status": artifacts["source_health"]["status"], "paths": [str(path) for path in paths]}, sort_keys=True))
        return 0 if artifacts["source_health"]["status"] == "PASS" else 3
    except CollectorError as exc:
        print(json.dumps(error_payload(exc.status, str(exc), retrieval), sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
