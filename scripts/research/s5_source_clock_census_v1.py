#!/usr/bin/env python3
"""Read-only, value-free S5 source/clock census. Does NOT certify PIT.

Intended to prevent treating a successful archived fixture replay as
source-timestamp-verified prospective evidence. No prediction/outcome join.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

HOUR_MS = 3_600_000
CONTRACT = "S5_SOURCE_CLOCK_CENSUS_V1"
SOURCE_CONTRACT = "DERIVATIVES_HOURLY_SOURCE_CAPTURE_V1"
SERIES = ("spot_hourly", "oi_hourly", "futures_taker_hourly", "basis_hourly")


def ms_utc(value: Any) -> int:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("decision_cutoff_must_be_explicit_utc_Z")
    try:
        moment = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError("decision_cutoff_invalid") from exc
    if moment.utcoffset() is None or moment.minute or moment.second or moment.microsecond:
        raise ValueError("decision_cutoff_not_hour_aligned")
    return int(moment.timestamp() * 1000)


def row_ms(row: Any) -> int:
    if not isinstance(row, dict):
        raise ValueError("row_not_an_object")
    ts = row.get("timestamp_ms")
    if not isinstance(ts, int) or isinstance(ts, bool) or ts % HOUR_MS:
        raise ValueError("timestamp_ms_not_hour_aligned_int")
    return ts


def census_capture(capture: dict[str, Any], *, source_blob_sha: str | None = None) -> dict[str, Any]:
    if not isinstance(capture, dict) or capture.get("contract") != SOURCE_CONTRACT:
        raise ValueError("source_contract_invalid")
    cutoff = ms_utc(capture.get("decision_cutoff_utc"))
    result: dict[str, Any] = {}
    all_windows_present = True
    # 24h features require a completed -25h price/OI baseline and -24..-1h flows.
    baseline_hours = [cutoff - (25 - index) * HOUR_MS for index in range(25)]
    flow_hours = baseline_hours[1:]
    source_published = 0
    source_retrieved = 0
    for field in SERIES:
        rows = capture.get(field)
        if not isinstance(rows, list):
            raise ValueError(f"{field}_missing_or_not_list")
        ts = [row_ms(row) for row in rows]
        if len(ts) != len(set(ts)):
            raise ValueError(f"{field}_duplicate_hourly_clock")
        needed = baseline_hours if field in ("spot_hourly", "oi_hourly") else flow_hours
        existing = set(ts)
        absent = sum(x not in existing for x in needed)
        if absent:
            all_windows_present = False
        pub = sum("source_first_known_utc" in row or "source_published_at_utc" in row for row in rows)
        ret = sum("retrieved_at_utc" in row for row in rows)
        source_published += pub
        source_retrieved += ret
        result[field] = {
            "rows_total": len(rows),
            "rows_before_cutoff": sum(x < cutoff for x in ts),
            "rows_at_or_after_cutoff": sum(x >= cutoff for x in ts),
            "required_24h_timestamps": len(needed),
            "required_24h_timestamps_missing": absent,
            "row_retrieval_clocks_declared": ret,
            "row_publication_clocks_declared": pub,
        }

    funds = capture.get("funding_events")
    if not isinstance(funds, list):
        raise ValueError("funding_events_missing_or_not_list")
    funding_ts = []
    for row in funds:
        if not isinstance(row, dict):
            raise ValueError("funding_row_not_object")
        ts = row.get("timestamp_ms")
        if not isinstance(ts, int) or isinstance(ts, bool):
            raise ValueError("funding_timestamp_not_int")
        funding_ts.append(ts)
    if len(funding_ts) != len(set(funding_ts)):
        raise ValueError("duplicate_funding_timestamp")
    pub_f = sum("source_first_known_utc" in r or "source_published_at_utc" in r for r in funds)
    ret_f = sum("retrieved_at_utc" in r for r in funds)
    source_published += pub_f
    source_retrieved += ret_f
    result["funding_events"] = {
        "rows_total": len(funds),
        "rows_before_cutoff": sum(t < cutoff for t in funding_ts),
        "rows_at_or_after_cutoff": sum(t >= cutoff for t in funding_ts),
        "row_retrieval_clocks_declared": ret_f,
        "row_publication_clocks_declared": pub_f,
    }
    provenance = capture.get("provenance") if isinstance(capture.get("provenance"), dict) else {}
    explicit_capture_clock = provenance.get("captured_at_utc") or provenance.get("retrieved_at_utc")
    # Even declared capture/publish timestamps cannot themselves prove independent first-known.
    return {
        "contract": CONTRACT,
        "authority": "RESEARCH_ONLY",
        "source_contract": SOURCE_CONTRACT,
        "symbol": capture.get("symbol"),
        "source_id": capture.get("source_id"),
        "venue": capture.get("venue"),
        "source_git_blob_sha": source_blob_sha,
        "decision_cutoff_utc": capture.get("decision_cutoff_utc"),
        "capability_24h_window_state": "COMPLETE" if all_windows_present else "MISSING_INPUT_WINDOW",
        "source_clock_state": "UNVERIFIED_FIRST_KNOWN",
        "source_clock_reason": "ARCHIVED_CAPTURE_NOT_AN_INDEPENDENT_PROVIDER_RELEASE_OR_AS_OF_AVAILABILITY_PROOF",
        "source_capture_clock_declared": explicit_capture_clock,
        "source_publication_clocks_declared": source_published,
        "source_retrieval_clocks_declared": source_retrieved,
        "funding_settlement_is_not_publication_proof": True,
        "independent_provider_first_known_verified": False,
        "prospective_pit_admitted": False,
        "realized_outcome_join_performed": False,
        "economic_edge_claim": "NOT_ESTIMABLE",
        "series": result,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--git-blob-sha", type=str)
    args = parser.parse_args()
    raw = args.input.read_bytes()
    census = census_capture(json.loads(raw), source_blob_sha=args.git_blob_sha)
    census["source_file_sha256"] = hashlib.sha256(raw).hexdigest()
    text = json.dumps(census, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
