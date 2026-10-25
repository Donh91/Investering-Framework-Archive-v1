#!/usr/bin/env python3
"""Value-free overlap census of the ten hash-pinned original hourly artifacts.

Run locally with the authorized private rescue bundle. Never commit the bundle.
Counts describe source exposures, not independent events or forecast outcomes.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import io
import json
from pathlib import Path
import zipfile

PACKAGE_SHA256 = "843e86017bfab58529fb9467797413252506c9d8de11920a3e4f3eea1608f490"
PACKAGE_BYTES = 114019
ENDPOINTS = frozenset(
    [f"{asset}_spot.json" for asset in ("BTCUSDT", "ETHUSDT", "ETHBTC")]
    + [f"{asset}_{kind}_okx.json" for asset in ("BTCUSDT", "ETHUSDT")
       for kind in ("funding", "oi", "long_short")]
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def original_responses(data: bytes) -> list[tuple[str, str, bytes]]:
    if len(data) != PACKAGE_BYTES or sha(data) != PACKAGE_SHA256:
        raise ValueError("ORIGINAL_PACKAGE_IDENTITY_MISMATCH")
    result = []
    total = 0
    with zipfile.ZipFile(io.BytesIO(data)) as outer:
        if outer.testzip() is not None:
            raise ValueError("OUTER_CRC_FAILURE")
        manifest = json.loads(outer.read("MANIFEST.json"))
        members = manifest["files"]
        paths = [item["path"] for item in members]
        if len(paths) != 10 or len(set(paths)) != 10:
            raise ValueError("CAPTURE_SET_INVALID")
        if sorted(outer.namelist()) != sorted(paths + ["MANIFEST.json", "PRIVATE_HANDOFF_README.txt"]):
            raise ValueError("OUTER_MEMBER_SET_INVALID")
        for item in members:
            raw = outer.read(item["path"])
            if len(raw) != item["bytes"] or sha(raw) != item["sha256"]:
                raise ValueError("ORIGINAL_ZIP_IDENTITY_MISMATCH")
            total += len(raw)
            with zipfile.ZipFile(io.BytesIO(raw)) as inner:
                names = inner.namelist()
                if len(names) != 9 or set(names) != ENDPOINTS or inner.testzip() is not None:
                    raise ValueError("RESPONSE_MEMBER_SET_OR_CRC_INVALID")
                result.extend((str(item["artifact_id"]), name, inner.read(name)) for name in sorted(names))
    if total != 107644 or len(result) != 90:
        raise ValueError("ORIGINAL_TOTALS_INVALID")
    return result


def summarize(responses: list[tuple[str, str, bytes]]) -> dict:
    """Pure census used by real input and synthetic negative controls.

    Row digests are transient only and are never returned. Unknown/error/empty
    responses fail closed rather than silently contributing zero observations.
    """
    groups = defaultdict(lambda: defaultdict(list))
    captures = defaultdict(set)
    seen = set()
    for capture, endpoint, payload in responses:
        if endpoint not in ENDPOINTS or (capture, endpoint) in seen:
            raise ValueError("UNKNOWN_OR_DUPLICATE_RESPONSE")
        seen.add((capture, endpoint))
        captures[capture].add(endpoint)
        body = json.loads(payload)
        if endpoint.endswith("_okx.json"):
            if not isinstance(body, dict) or body.get("code") != "0":
                raise ValueError("PROVIDER_RESPONSE_NOT_SUCCESS")
            rows = body.get("data")
        else:
            rows = body
        if not isinstance(rows, list) or not rows:
            raise ValueError("EMPTY_OR_INVALID_RESPONSE")
        for row in rows:
            if "funding" in endpoint:
                timestamp = row.get("fundingTime") if isinstance(row, dict) else None
            else:
                timestamp = row[0] if isinstance(row, list) and row else None
            if isinstance(timestamp, bool) or not isinstance(timestamp, (str, int)) or not str(timestamp).isdigit():
                raise ValueError("SOURCE_TIMESTAMP_INVALID")
            digest = sha(json.dumps(row, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":"), allow_nan=False).encode())
            groups[endpoint][str(timestamp)].append((capture, digest))
    if not captures or any(names != ENDPOINTS for names in captures.values()):
        raise ValueError("INCOMPLETE_CAPTURE_ENDPOINT_SET")
    by_source = []
    for endpoint, timestamps in sorted(groups.items()):
        total = sum(map(len, timestamps.values()))
        by_source.append({
            "source_filename": endpoint,
            "raw_row_instances": total,
            "unique_source_timestamps": len(timestamps),
            "repeated_timestamp_instances": total - len(timestamps),
            "timestamps_with_changed_payload": sum(len({digest for _, digest in rows}) > 1 for rows in timestamps.values()),
            "max_exposures_one_timestamp": max(map(len, timestamps.values())),
        })
    total = sum(row["raw_row_instances"] for row in by_source)
    unique = sum(row["unique_source_timestamps"] for row in by_source)
    return {
        "contract": "TASK2_ORIGINAL_CAPTURE_OVERLAP_REPRODUCTION_v1",
        "authority": "RESEARCH_ONLY_SOURCE_QUALITY_NOT_PIT_ADMISSION",
        "captured_artifact_count": len(captures),
        "endpoint_response_count": len(seen),
        "raw_row_instances_total": total,
        "unique_endpoint_timestamp_pairs": unique,
        "repeated_endpoint_timestamp_exposures": total - unique,
        "repeated_exposure_fraction": (total - unique) / total,
        "source_payload_change_timestamp_pairs": sum(row["timestamps_with_changed_payload"] for row in by_source),
        "by_source": by_source,
        "independent_event_count": None,
        "pit_admitted": False,
        "forecast_skill_tested": False,
        "raw_values_or_row_hashes_disclosed": False,
        "interpretation": "Repeated source exposures are not independent samples. No observed payload changes does not prove vendor revision immunity. Endpoint-timestamp pairs are not independent market events or outcome trials.",
    }


def audit(data: bytes) -> dict:
    result = summarize(original_responses(data))
    result["original_package_sha256"] = PACKAGE_SHA256
    result["original_package_bytes"] = len(data)
    result["original_zip_bytes"] = 107644
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = audit(args.bundle.read_bytes())
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile):
        parser.exit(2, "SOURCE_INTEGRITY_FAIL: no census emitted\n")
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
