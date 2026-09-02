#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any


UTC = timezone.utc
PROVENANCE_CONTRACT = "RICH_BREADTH_SAMPLING_PROVENANCE_v1"
ORDINARY_CHECKPOINT = "ORDINARY_CHECKPOINT"
ADAPTIVE_BOOST = "ADAPTIVE_BOOST"
ROLLING_24H = "SOURCE_REPORTED_ROLLING_24H_AT_RETRIEVAL"
INDEPENDENCE_POLICY = "DOWNSTREAM_EXPLICIT_ORIGIN_AND_NON_OVERLAPPING_WINDOW_VALIDATION_REQUIRED"
AUTHORITY_FALSE_FIELDS = (
    "can_create_market_evidence",
    "can_create_rotation_vote",
    "can_create_portfolio_permission",
    "can_change_canonical_state",
)


def parse_utc(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.utcoffset() is None:
        return None
    return parsed.astimezone(UTC)


def iso(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def valid_provenance(value: Any) -> bool:
    if not isinstance(value, dict) or value.get("contract") != PROVENANCE_CONTRACT:
        return False
    mode = value.get("sampling_mode")
    if mode not in {ORDINARY_CHECKPOINT, ADAPTIVE_BOOST}:
        return False
    capture_run_id = value.get("capture_run_id")
    if not isinstance(capture_run_id, str) or re.fullmatch(r"gh-[0-9]+-[0-9]+", capture_run_id) is None:
        return False
    if value.get("independence_policy") != INDEPENDENCE_POLICY:
        return False
    if any(value.get(field) is not False for field in AUTHORITY_FALSE_FIELDS):
        return False
    if mode == ORDINARY_CHECKPOINT:
        return (
            value.get("capture_origin") == "RICH_BREADTH_CHECKPOINT"
            and value.get("adaptive_selection") is False
            and value.get("parent_cadence_run_id") is None
            and value.get("parent_cadence_observation_path") is None
            and value.get("parent_cadence_observation_sha256") is None
        )
    parent_sha = value.get("parent_cadence_observation_sha256")
    parent_run_id = value.get("parent_cadence_run_id")
    parent_path = value.get("parent_cadence_observation_path")
    path = PurePosixPath(parent_path) if isinstance(parent_path, str) else None
    return (
        value.get("capture_origin") == "ADAPTIVE_ROTATION_CADENCE"
        and value.get("adaptive_selection") is True
        and parent_run_id == capture_run_id
        and path is not None
        and not path.is_absolute()
        and ".." not in path.parts
        and bool(parent_path.strip())
        and isinstance(parent_sha, str)
        and len(parent_sha) == 64
        and all(ch in "0123456789abcdef" for ch in parent_sha)
    )


def sampling_context(payload: Any, source_path: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        payload = {}
    observation = payload.get("observation") if isinstance(payload.get("observation"), dict) else {}
    provenance = payload.get("sampling_provenance")
    retrieval_text = observation.get("retrieval_timestamp_utc") or payload.get("retrieved_at_utc")
    retrieved = parse_utc(retrieval_text)
    window_semantics = observation.get("window_semantics")
    window_start = retrieved - timedelta(hours=24) if retrieved and window_semantics == ROLLING_24H else None
    window_end = retrieved if window_start else None

    authority = payload.get("authority")
    checkpoint_valid = payload.get("contract") == "RICH_BREADTH_CHECKPOINT_v1" and isinstance(authority, dict) and all(
        authority.get(field) is False
        for field in ("binding", "canonical_acceptance", "state_change", "portfolio_action")
    )

    if not checkpoint_valid:
        mode = "UNKNOWN"
        origin = "UNKNOWN"
        reason = "CHECKPOINT_CONTRACT_OR_AUTHORITY_INVALID"
        parent_run_id = None
    elif provenance is None:
        mode = "UNKNOWN"
        origin = "UNKNOWN"
        reason = "LEGACY_ORIGIN_UNKNOWN_NOT_INFERRED"
        parent_run_id = None
    elif not valid_provenance(provenance):
        mode = "UNKNOWN"
        origin = "UNKNOWN"
        reason = "INVALID_PROVENANCE_FAIL_CLOSED"
        parent_run_id = None
    else:
        mode = provenance["sampling_mode"]
        origin = provenance["capture_origin"]
        parent_run_id = provenance.get("parent_cadence_run_id")
        if mode == ADAPTIVE_BOOST:
            reason = "ADAPTIVE_BOOST_ENDOGENOUS_NOT_ADDITIONAL_CONFIRMATION"
        elif window_start is None:
            reason = "WINDOW_SEMANTICS_OR_TIMESTAMP_UNAVAILABLE"
        else:
            reason = "PENDING_NON_OVERLAP_SELECTION"

    eligible = mode == ORDINARY_CHECKPOINT and window_start is not None
    return {
        "source_path": source_path,
        "retrieved_at_utc": iso(retrieved) if retrieved else None,
        "sampling_mode": mode,
        "capture_origin": origin,
        "parent_cadence_run_id": parent_run_id,
        "source_window_semantics": window_semantics if isinstance(window_semantics, str) else "UNKNOWN",
        "source_window_start_utc": iso(window_start) if window_start else None,
        "source_window_end_utc": iso(window_end) if window_end else None,
        "independent_confirmation_eligible": eligible,
        "independent_observation": False,
        "independence_group_id": None,
        "independence_reason": reason,
    }


def _window(row: dict[str, Any]) -> tuple[datetime, datetime] | None:
    start = parse_utc(row.get("source_window_start_utc"))
    end = parse_utc(row.get("source_window_end_utc"))
    if start is None or end is None or start >= end:
        return None
    return start, end


def _group_id(start: datetime, end: datetime) -> str:
    raw = f"{iso(start)}|{iso(end)}".encode("utf-8")
    return "BREADTH-WINDOW-" + hashlib.sha256(raw).hexdigest()[:20]


def _overlap(left: tuple[datetime, datetime], right: tuple[datetime, datetime]) -> bool:
    return left[0] < right[1] and right[0] < left[1]


def summarize(checkpoints: list[tuple[str, Any]]) -> dict[str, Any]:
    rows = [sampling_context(payload, path) for path, payload in checkpoints]
    eligible = sorted(
        (row for row in rows if row["independent_confirmation_eligible"]),
        key=lambda row: (row["source_window_end_utc"], row["source_path"]),
    )
    anchors: list[tuple[tuple[datetime, datetime], str]] = []
    last_selected_end: datetime | None = None
    for row in eligible:
        window = _window(row)
        if window is None:
            continue
        if last_selected_end is None or window[0] >= last_selected_end:
            group_id = _group_id(*window)
            row["independent_observation"] = True
            row["independence_group_id"] = group_id
            row["independence_reason"] = "SELECTED_NON_OVERLAPPING_ORDINARY_WINDOW"
            anchors.append((window, group_id))
            last_selected_end = window[1]

    for row in rows:
        if row["independent_observation"]:
            continue
        window = _window(row)
        if window is not None:
            for anchor_window, group_id in anchors:
                if _overlap(window, anchor_window):
                    row["independence_group_id"] = group_id
                    break
        if row["independence_reason"] == "PENDING_NON_OVERLAP_SELECTION":
            row["independence_reason"] = "OVERLAPPING_ROLLING_WINDOW_NOT_ADDITIONAL_CONFIRMATION"

    independent_count = sum(row["independent_observation"] for row in rows)
    modes = {
        mode: sum(row["sampling_mode"] == mode for row in rows)
        for mode in (ORDINARY_CHECKPOINT, ADAPTIVE_BOOST, "UNKNOWN")
    }
    return {
        "contract": "ROTATION_SURVIVAL_SAMPLING_INDEPENDENCE_v1",
        "authority": {
            "canonical_state": False,
            "market_evidence": False,
            "rotation_vote": False,
            "portfolio_permission": False,
            "automatic_phase_promotion": False,
        },
        "window_rule": "EXPLICIT_ORDINARY_ORIGIN_PLUS_NON_OVERLAPPING_SOURCE_REPORTED_ROLLING_24H_WINDOWS",
        "raw_capture_count": len(rows),
        "ordinary_capture_count": modes[ORDINARY_CHECKPOINT],
        "adaptive_boost_capture_count": modes[ADAPTIVE_BOOST],
        "unknown_origin_capture_count": modes["UNKNOWN"],
        "independent_observation_count": independent_count,
        "survival_confirmation_count": independent_count,
        "non_independent_capture_count": len(rows) - independent_count,
        "sampling_context": rows,
    }


def read_json(path: Path) -> Any:
    def reject_nonfinite(value: str) -> None:
        raise ValueError(f"non-finite JSON value: {value}")

    return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_nonfinite)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", action="append", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = summarize([(path.as_posix(), read_json(path)) for path in args.checkpoint])
    body = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(body, encoding="utf-8")
    else:
        print(body, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
