#!/usr/bin/env python3
"""
Reproduce the FRED Macro Core recent backfill archive.

Requires:
    FRED_API_KEY=<32-character key>

No API key is stored in this script or archive.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

BASE_URL = "https://api.stlouisfed.org/fred"
BACKFILL_START = "2026-06-25"
BACKFILL_END = "2026-07-16"

REQUIRED = [
    "DGS3MO","DGS2","DGS10","DFII10","T10Y2Y","T10Y3M","T10YIE","DFF","SOFR",
    "DTWEXBGS","BAA10Y","NFCI","WALCL","RRPONTSYD","WTREGEN","WRESBAL","M2SL",
    "CPIAUCSL","CPILFESL","PCEPILFE","UNRATE","PAYEMS","ICSA","INDPRO","RSAFS",
    "CFNAI","GDPC1",
]
OPTIONAL = ["BAMLH0A0HYM2"]
REVISION_SENSITIVE = [
    "CPIAUCSL","CPILFESL","PCEPILFE","UNRATE","PAYEMS",
    "INDPRO","RSAFS","M2SL","CFNAI","GDPC1",
]
RESTRICTED_REDISTRIBUTION = {"BAA10Y", "BAMLH0A0HYM2"}
MONTHLY = {"M2SL","CPIAUCSL","CPILFESL","PCEPILFE","UNRATE","PAYEMS","INDPRO","RSAFS","CFNAI"}
QUARTERLY = {"GDPC1"}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def request_json(path: str, params: dict[str, Any], retries: int = 3) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    key = os.environ.get("FRED_API_KEY")
    if not key:
        raise RuntimeError("FRED_API_KEY environment variable is required.")
    if len(key) != 32 or not key.isalnum() or key.lower() != key:
        raise RuntimeError("FRED_API_KEY must be a 32-character lowercase alphanumeric string.")
    clean = {k: v for k, v in params.items() if v is not None}
    clean["api_key"] = key
    clean["file_type"] = "json"
    url = f"{BASE_URL}/{path}?{urllib.parse.urlencode(clean)}"
    ledger = []
    for attempt in range(1, retries + 1):
        started = utc_now()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Cycle-Navigator-FRED-Archive/1.0"})
            with urllib.request.urlopen(req, timeout=60) as response:
                payload = json.loads(response.read().decode("utf-8"))
            completed = utc_now()
            ledger.append({"attempt_number": attempt, "started_utc": started, "completed_utc": completed, "status": "PASS", "response_count": payload.get("count", len(payload.get("seriess", []))), "error_text": ""})
            return payload, ledger
        except Exception as exc:
            completed = utc_now()
            ledger.append({"attempt_number": attempt, "started_utc": started, "completed_utc": completed, "status": "FAIL", "response_count": 0, "error_text": str(exc)})
            if attempt < retries:
                time.sleep(2 ** (attempt - 1))
    raise RuntimeError(json.dumps(ledger, ensure_ascii=False))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def normalize_observations(series_id: str, metadata: dict[str, Any], payload: dict[str, Any], retrieved: str) -> list[dict[str, Any]]:
    out = []
    for item in payload.get("observations", []):
        raw = item.get("value")
        value = None if raw in {None, "."} else float(raw)
        out.append({
            "series_id": series_id,
            "observation_date": item.get("date"),
            "value": value,
            "value_status": "MISSING_SOURCE_MARKER" if raw == "." else "OK",
            "raw_value": raw,
            "realtime_start": item.get("realtime_start"),
            "realtime_end": item.get("realtime_end"),
            "retrieved_utc": retrieved,
            "frequency": metadata.get("frequency"),
            "units": metadata.get("units"),
            "seasonal_adjustment": metadata.get("seasonal_adjustment"),
            "source_title": metadata.get("title"),
            "release_title": "NOT_COLLECTED_RECENT_BACKFILL_SCOPE",
        })
    return out


def observation_start(series_id: str) -> str:
    if series_id in QUARTERLY:
        return "2025-01-01"
    if series_id in MONTHLY:
        return "2026-01-01"
    return BACKFILL_START


def checksum_tree(root: Path) -> None:
    lines = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name != "checksums.sha256":
            lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(root)}")
    (root / "checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


def zip_tree(root: Path) -> Path:
    destination = root.with_suffix(".zip")
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(root.rglob("*")):
            if path.is_file():
                archive.write(path, arcname=f"{root.name}/{path.relative_to(root)}")
    with zipfile.ZipFile(destination) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f"ZIP CRC failure: {bad}")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    root = Path(args.out)
    retrieved = utc_now()
    ledger_lines = []

    for sid in REQUIRED + OPTIONAL:
        payload, attempts = request_json("series", {"series_id": sid})
        write_json(root / "raw_action_extracts" / "metadata" / f"{sid}.json", payload)
        metadata = payload["seriess"][0]
        for attempt in attempts:
            ledger_lines.append({"request_id": f"{sid}_metadata_{attempt['attempt_number']}", "series_id": sid, "request_type": "metadata", "endpoint_or_action_name": "fred/series", "parameters": {"series_id": sid}, **attempt, "raw_output_path": f"raw_action_extracts/metadata/{sid}.json"})
        if sid in RESTRICTED_REDISTRIBUTION:
            write_json(root / "raw_action_extracts" / "observations_latest" / f"{sid}.json", {"series_id": sid, "status": "METADATA_ONLY_REDISSEMINATION_RESTRICTION", "numeric_observations_included": False})
            continue
        params = {"series_id": sid, "observation_start": observation_start(sid), "observation_end": BACKFILL_END, "units": "lin", "output_type": 1, "sort_order": "asc", "limit": 100000, "offset": 0}
        payload, attempts = request_json("series/observations", params)
        write_json(root / "raw_action_extracts" / "observations_latest" / f"{sid}.json", payload)
        rows = normalize_observations(sid, metadata, payload, retrieved)
        fields = list(rows[0].keys()) if rows else ["series_id","observation_date","value","value_status","raw_value","realtime_start","realtime_end","retrieved_utc","frequency","units","seasonal_adjustment","source_title","release_title"]
        write_csv(root / "normalized" / "native" / f"{sid}.csv", rows, fields)
        for attempt in attempts:
            ledger_lines.append({"request_id": f"{sid}_latest_{attempt['attempt_number']}", "series_id": sid, "request_type": "observations_latest", "endpoint_or_action_name": "fred/series/observations", "parameters": params, **attempt, "raw_output_path": f"raw_action_extracts/observations_latest/{sid}.json"})

    for sid in REVISION_SENSITIVE:
        for request_type, output_type in [("initial_release", 4), ("revisions", 3)]:
            params = {"series_id": sid, "realtime_start": "2025-01-01" if output_type == 4 else BACKFILL_START, "realtime_end": BACKFILL_END, "observation_start": "2025-01-01", "observation_end": BACKFILL_END, "units": "lin", "output_type": output_type, "sort_order": "asc", "limit": 100000, "offset": 0}
            try:
                payload, _ = request_json("series/observations", params)
            except Exception as exc:
                payload = {"series_id": sid, "request_type": request_type, "request_parameters": params, "retrieved_utc": retrieved, "status": "FAIL", "raw_error_text": str(exc)}
            write_json(root / "raw_action_extracts" / request_type / f"{sid}.json", payload)
        params = {"series_id": sid, "realtime_start": BACKFILL_START, "realtime_end": BACKFILL_END, "sort_order": "asc", "limit": 10000, "offset": 0}
        try:
            payload, _ = request_json("series/vintagedates", params)
        except Exception as exc:
            payload = {"series_id": sid, "request_type": "vintage_dates", "request_parameters": params, "retrieved_utc": retrieved, "status": "FAIL", "raw_error_text": str(exc)}
        write_json(root / "raw_action_extracts" / "vintage_dates" / f"{sid}.json", payload)

    with (root / "request_ledger.jsonl").open("w", encoding="utf-8") as handle:
        for line in ledger_lines:
            handle.write(json.dumps(line, ensure_ascii=False) + "\n")
    write_json(root / "manifest_reproduction.json", {"created_utc": retrieved, "required_series": REQUIRED, "optional_series": OPTIONAL, "interpolation_used": False, "fabrication_used": False})
    checksum_tree(root)
    destination = zip_tree(root)
    print(json.dumps({"zip": str(destination), "zip_sha256": hashlib.sha256(destination.read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
