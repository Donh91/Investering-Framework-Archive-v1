#!/usr/bin/env python3
"""Explicit live transport adapter for synchronized FRED owner capture.

Each official series is fetched independently, preserved byte-for-byte, then
combined deterministically into the existing Data Terminal collector format.
No source substitution or silent fallback is permitted.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
COLLECTOR_PATH = HERE / "fred_csv_collector.py"
SPEC = importlib.util.spec_from_file_location("fred_csv_collector", COLLECTOR_PATH)
collector = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = collector
assert SPEC.loader is not None
SPEC.loader.exec_module(collector)

SERIES_STALE_AFTER_SECONDS = {
    "DGS2": 7 * 24 * 60 * 60,
    "DGS10": 7 * 24 * 60 * 60,
    "VIXCLS": 7 * 24 * 60 * 60,
    "DTWEXBGS": 10 * 24 * 60 * 60,
}


def deterministic_composite(payloads: dict[str, bytes], series_set: tuple[str, ...]) -> bytes:
    values: dict[str, dict[str, str]] = {}
    all_dates: set[str] = set()
    for series in series_set:
        observations, missing = collector.parse_fred_csv(payloads[series], (series,))
        series_values = {item.date[:10]: format(item.value, ".15g") for item in observations[series]}
        for item in missing:
            series_values[item["source_date"]] = "."
        values[series] = series_values
        all_dates.update(series_values)
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(["DATE", *series_set])
    for source_date in sorted(all_dates):
        writer.writerow([source_date, *(values[series].get(source_date, ".") for series in series_set)])
    return stream.getvalue().encode("utf-8")


def apply_series_freshness_policy(artifacts: dict[str, dict]) -> None:
    health_rows = artifacts["source_health"]["series"]
    for row in health_rows:
        threshold = SERIES_STALE_AFTER_SECONDS[row["series"]]
        row["stale_after_seconds"] = threshold
        row["status"] = "PASS" if row["freshness_seconds"] <= threshold else "STALE"
    aggregate = "PASS" if all(row["status"] == "PASS" for row in health_rows) else "STALE"
    artifacts["source_health"]["status"] = aggregate
    receipt = artifacts["receipt"]
    receipt["status"] = aggregate
    receipt_material = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    receipt["receipt_sha256"] = collector.sha256_bytes(collector.canonical_json_bytes(receipt_material))
    snapshot = artifacts["snapshot"]
    snapshot["status"] = aggregate
    snapshot["source_lineage"]["receipt_sha256"] = receipt["receipt_sha256"]
    handoff = artifacts["handoff"]
    handoff["quality"]["status"] = aggregate
    handoff["source_lineage"]["receipt_sha256"] = receipt["receipt_sha256"]
    terminal = artifacts["terminal_state"]
    terminal["source_health"] = health_rows
    terminal["target_sha256"] = collector.sha256_bytes(collector.canonical_json_bytes(snapshot))


def extend_manifest(output_dir: Path, run_id: str, source_payloads: dict[str, bytes], composite: bytes) -> None:
    source_dir = output_dir / "raw" / "source_payloads"
    source_dir.mkdir(parents=True, exist_ok=True)
    source_rows = []
    for series, payload in sorted(source_payloads.items()):
        path = source_dir / f"{run_id}__{series}.csv"
        path.write_bytes(payload)
        source_rows.append({"series": series, "path": path.relative_to(output_dir).as_posix(), "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()})
    lineage = {
        "contract": "WP04C5B_FRED_SOURCE_PAYLOAD_LINEAGE_v1",
        "run_id": run_id,
        "source_payloads": source_rows,
        "composite": {"bytes": len(composite), "sha256": hashlib.sha256(composite).hexdigest()},
        "source_substitution": False,
        "authority": collector.AUTHORITY,
    }
    lineage_path = output_dir / "source_payload_lineage.json"
    lineage_path.write_text(json.dumps(lineage, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest_path = output_dir / "artifact_manifest.json"
    members = []
    for path in sorted(p for p in output_dir.rglob("*") if p.is_file() and p != manifest_path):
        payload = path.read_bytes()
        members.append({"path": path.relative_to(output_dir).as_posix(), "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()})
    manifest = {"contract": "WP04C5B_ARTIFACT_MANIFEST_v1", "run_id": run_id, "member_count": len(members), "members": members, "authority": collector.AUTHORITY}
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--series", default=",".join(collector.DEFAULT_SERIES))
    parser.add_argument("--output-dir", type=Path, default=Path("data-terminal-output"))
    parser.add_argument("--retrieval-timestamp")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--backoff", type=float, default=0.25)
    args = parser.parse_args()
    retrieval = collector.parse_timestamp(args.retrieval_timestamp) if args.retrieval_timestamp else datetime.now(timezone.utc)
    series_set = collector.normalize_series(args.series.split(","))
    try:
        payloads = {}
        for series in series_set:
            url = collector.DEFAULT_URL.format(series=series)
            payloads[series] = collector.fetch_payload(url, args.timeout, args.retries, args.backoff)
        composite = deterministic_composite(payloads, series_set)
        source_url = "MULTI_SOURCE:" + ",".join(collector.DEFAULT_URL.format(series=item) for item in series_set)
        artifacts = collector.build_artifacts(payload=composite, retrieval_timestamp=retrieval, series=series_set, source_url=source_url, acquisition_mode="NETWORK_MULTI_SOURCE", stale_after_seconds=max(SERIES_STALE_AFTER_SECONDS.values()))
        apply_series_freshness_policy(artifacts)
        collector.write_artifacts(args.output_dir, artifacts, raw_payload=composite)
        run_id = artifacts["receipt"]["run_id"]
        extend_manifest(args.output_dir, run_id, payloads, composite)
        readback = collector.verify_artifact_readback(args.output_dir)
        source_health = {row["series"]: {"status": row["status"], "source_timestamp": row["source_timestamp"], "freshness_seconds": row["freshness_seconds"], "stale_after_seconds": row["stale_after_seconds"]} for row in artifacts["source_health"]["series"]}
        capture_integrity = "PASS" if readback["status"] == "PASS" and len(payloads) == len(series_set) else "FAIL"
        print(json.dumps({"capture_integrity": capture_integrity, "source_freshness": artifacts["receipt"]["status"], "source_health": source_health, "readback": readback, "run_id": run_id, "source_count": len(payloads)}, sort_keys=True))
        return 0 if capture_integrity == "PASS" else 3
    except collector.CollectorError as exc:
        print(json.dumps(collector.error_payload(exc.status, str(exc), retrieval), sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
