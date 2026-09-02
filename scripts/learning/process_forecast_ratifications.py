#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
sys.path.insert(0, str(ROOT / "scripts" / "learning"))

from forecast_candidate_grouping import classified_candidate_groups  # noqa: E402
from forecast_ratification_baseline import select_archived_baseline  # noqa: E402
from forecast_ratification_contract import (  # noqa: E402
    CANDIDATE_RECORDING_TOLERANCE_MINUTES,
    CUTOVER_COMMIT_SHA,
    DECISION_SLA_MINUTES,
    PACKET_RECORDING_TOLERANCE_MINUTES,
    RATIFICATION_PACKET_V2,
    RATIFICATION_TERMINAL_V1,
    decision_deadline,
    iso,
    parse_dt,
    validate_packet_shape,
)
import forecast_ratification_freezer as ratifier  # noqa: E402

UTC = timezone.utc

AUTHORITY = {
    "portfolio_action": False,
    "framework_state_change": False,
    "model_weight_change": False,
    "canonical_promotion": False,
    "self_promotion": False,
}


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def index_packets(root: Path) -> dict[str, tuple[dict[str, Any], Path]]:
    found: dict[str, tuple[dict[str, Any], Path]] = {}
    for path in sorted(root.rglob("*.json")) if root.exists() else []:
        value = read(path)
        validate_packet_shape(value)
        cid = str(value["candidate_id"])
        if path.stem != cid:
            raise ValueError(f"RATIFICATION_PACKET_FILENAME_MISMATCH:{path}")
        if cid in found:
            raise ValueError(f"MULTIPLE_RATIFICATION_PACKETS:{cid}")
        found[cid] = (value, path)
    return found


def git_first_add_at(repo_root: Path, path: Path, label: str) -> datetime:
    repo_root = repo_root.resolve()
    try:
        rel = path.resolve().relative_to(repo_root).as_posix()
    except ValueError as exc:
        raise ValueError(f"{label}_OUTSIDE_REPOSITORY") from exc
    proc = subprocess.run(
        ["git", "log", "--diff-filter=A", "--follow", "--reverse", "--format=%cI", "--", rel],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    rows = [row.strip() for row in proc.stdout.splitlines() if row.strip()]
    if not rows:
        raise ValueError(f"{label}_NOT_GIT_RECORDED:{rel}")
    return parse_dt(rows[0])


def validate_candidate_git_timing(candidate: dict[str, Any], candidate_paths: list[Path], repo_root: Path, now: datetime) -> datetime:
    if len(candidate_paths) != 1:
        raise ValueError("POST_CUTOVER_DUPLICATE_CANDIDATE_PATHS")
    git_recorded_at = git_first_add_at(repo_root, candidate_paths[0], "CANDIDATE")
    created = parse_dt(str(candidate["created_at_utc"]))
    delta = (git_recorded_at - created).total_seconds()
    if delta < 0:
        raise ValueError("CANDIDATE_GIT_RECORD_PRECEDES_CREATED_AT")
    if delta > CANDIDATE_RECORDING_TOLERANCE_MINUTES * 60:
        raise ValueError("CANDIDATE_CREATED_AT_BACKDATED_OR_LATE_RECORDED")
    if git_recorded_at > now:
        raise ValueError("CANDIDATE_GIT_RECORD_IN_FUTURE")
    return git_recorded_at


def validate_packet_timing(
    candidate: dict[str, Any],
    packet: dict[str, Any],
    packet_git_recorded_at: datetime,
    candidate_git_recorded_at: datetime,
    now: datetime,
) -> datetime:
    if packet.get("candidate_id") != candidate.get("candidate_id"):
        raise ValueError("CANDIDATE_ID_MISMATCH")
    if packet.get("candidate_sha256") != digest(candidate):
        raise ValueError("CANDIDATE_HASH_MISMATCH")
    created = parse_dt(str(candidate["created_at_utc"]))
    decision_at = parse_dt(str(packet["decision_at_utc"]))
    deadline = decision_deadline(str(candidate["created_at_utc"]))
    if decision_at < created:
        raise ValueError("RATIFICATION_PRECEDES_CANDIDATE")
    if decision_at < candidate_git_recorded_at:
        raise ValueError("RATIFICATION_PRECEDES_CANDIDATE_GIT_RECORD")
    if decision_at > deadline:
        raise ValueError("RATIFICATION_DECISION_SLA_EXCEEDED")
    if decision_at > now:
        raise ValueError("RATIFICATION_DECISION_IN_FUTURE")
    delta = (packet_git_recorded_at - decision_at).total_seconds()
    if delta < 0:
        raise ValueError("RATIFICATION_GIT_RECORD_PRECEDES_DECISION")
    if delta > PACKET_RECORDING_TOLERANCE_MINUTES * 60:
        raise ValueError("RATIFICATION_PACKET_BACKDATED_OR_LATE_RECORDED")
    return decision_at


def select_baseline(capture_root: Path, metric: str, decision_at: datetime) -> tuple[Path, dict[str, Any], datetime]:
    return select_archived_baseline(
        capture_root,
        metric,
        decision_at,
        metric_value=ratifier.metric_value,
        evidence_timestamp=ratifier.evidence_timestamp,
    )


def terminal_record(
    candidate: dict[str, Any],
    candidate_paths: list[Path],
    disposition: str,
    now: datetime,
    candidate_git_recorded: datetime | None = None,
    packet: dict[str, Any] | None = None,
    packet_path: Path | None = None,
    packet_git_recorded: datetime | None = None,
    baseline_path: Path | None = None,
    baseline: dict[str, Any] | None = None,
    frozen: dict[str, Any] | None = None,
    frozen_path: Path | None = None,
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "contract": RATIFICATION_TERMINAL_V1,
        "candidate_id": candidate["candidate_id"],
        "candidate_sha256": digest(candidate),
        "candidate_paths": [path.as_posix() for path in candidate_paths],
        "candidate_created_at_utc": candidate.get("created_at_utc"),
        "candidate_git_recorded_at_utc": iso(candidate_git_recorded) if candidate_git_recorded else None,
        "terminal_at_utc": iso(now),
        "disposition": disposition,
        "prospective_cutover_commit_sha": CUTOVER_COMMIT_SHA,
        "decision_sla_minutes": DECISION_SLA_MINUTES,
        "candidate_recording_tolerance_minutes": CANDIDATE_RECORDING_TOLERANCE_MINUTES,
        "packet_recording_tolerance_minutes": PACKET_RECORDING_TOLERANCE_MINUTES,
        "historical_candidate_rewritten": False,
        "outcome_data_read": False,
        "authority": AUTHORITY,
    }
    if packet is not None and packet_path is not None and packet_git_recorded is not None:
        value["ratification"] = {
            "contract": RATIFICATION_PACKET_V2,
            "packet_path": packet_path.as_posix(),
            "packet_sha256": digest(packet),
            "decision": packet.get("decision"),
            "decision_at_utc": packet.get("decision_at_utc"),
            "git_recorded_at_utc": iso(packet_git_recorded),
            "authority": packet.get("authority"),
            "owner_actor": packet.get("owner_actor"),
            "outcome_blind": packet.get("outcome_blind"),
            "decision_basis_scope": packet.get("decision_basis_scope"),
            "outcome_paths_read": packet.get("outcome_paths_read"),
        }
    if baseline is not None and baseline_path is not None:
        value["baseline"] = {
            "path": baseline_path.as_posix(),
            "sha256": digest(baseline),
            "observed_at_utc": iso(ratifier.evidence_timestamp(baseline)),
            "selection_semantics": "LATEST_IMMUTABLE_ARCHIVED_CAPTURE_AT_OR_BEFORE_OWNER_DECISION",
        }
    if frozen is not None and frozen_path is not None:
        value["frozen_forecast"] = {
            "forecast_id": frozen.get("forecast_id"),
            "path": frozen_path.as_posix(),
            "sha256": digest(frozen),
            "frozen_at_utc": frozen.get("frozen_at_utc"),
            "outcome_due_utc": frozen.get("outcome_due_utc"),
            "settlement_contract_version": frozen.get("settlement_contract_version"),
        }
    value["terminal_sha256"] = digest(value)
    return value


def legacy_divergent_terminal_record(group: dict[str, Any], now: datetime) -> dict[str, Any]:
    variants = [
        {
            "path": row["path"].as_posix(),
            "sha256": row["sha256"],
            "created_at_utc": row.get("created_at_utc"),
        }
        for row in group["variants"]
    ]
    value: dict[str, Any] = {
        "contract": RATIFICATION_TERMINAL_V1,
        "candidate_id": group["candidate_id"],
        "candidate_sha256": None,
        "candidate_paths": [path.as_posix() for path in group["paths"]],
        "candidate_variants": variants,
        "candidate_variant_count": len(variants),
        "candidate_group_classification": group["classification"],
        "terminal_at_utc": iso(now),
        "disposition": "LEGACY_PRE_CUTOVER_DIVERGENT_DUPLICATE_HINDSIGHT_INELIGIBLE",
        "prospective_cutover_commit_sha": CUTOVER_COMMIT_SHA,
        "historical_candidate_rewritten": False,
        "outcome_data_read": False,
        "ratification_allowed": False,
        "authority": AUTHORITY,
    }
    value["terminal_sha256"] = digest(value)
    return value


def write_terminal(path: Path, value: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = read(path)
        if canon(existing) != canon(value):
            existing_copy = dict(existing)
            value_copy = dict(value)
            existing_copy.pop("terminal_at_utc", None)
            value_copy.pop("terminal_at_utc", None)
            existing_copy.pop("terminal_sha256", None)
            value_copy.pop("terminal_sha256", None)
            if canon(existing_copy) != canon(value_copy):
                raise ValueError(f"RATIFICATION_TERMINAL_COLLISION:{path.stem}")
        return "DUPLICATE_NOOP"
    path.write_bytes(canon(value))
    return "CREATED"


def process(
    pending_root: Path,
    packet_root: Path,
    terminal_root: Path,
    frozen_root: Path,
    capture_root: Path,
    repo_root: Path,
    now: datetime,
) -> dict[str, Any]:
    groups = classified_candidate_groups(pending_root)
    packets = index_packets(packet_root)
    counts: dict[str, int] = {}
    errors: list[dict[str, str]] = []

    for cid, group in sorted(groups.items()):
        terminal_path = terminal_root / f"{cid}.json"
        if terminal_path.exists():
            counts["ALREADY_TERMINAL"] = counts.get("ALREADY_TERMINAL", 0) + 1
            continue
        try:
            classification = group["classification"]
            if classification == "LEGACY_PRE_CUTOVER_DIVERGENT_DUPLICATE":
                terminal = legacy_divergent_terminal_record(group, now)
                write_terminal(terminal_path, terminal)
                counts[terminal["disposition"]] = counts.get(terminal["disposition"], 0) + 1
                continue

            candidate = group["candidate"]
            candidate_paths = group["paths"]
            if classification.startswith("LEGACY_PRE_CUTOVER"):
                terminal = terminal_record(candidate, candidate_paths, "LEGACY_PRE_CUTOVER_HINDSIGHT_INELIGIBLE", now)
                write_terminal(terminal_path, terminal)
                counts["LEGACY_PRE_CUTOVER_HINDSIGHT_INELIGIBLE"] = counts.get("LEGACY_PRE_CUTOVER_HINDSIGHT_INELIGIBLE", 0) + 1
                continue

            packet_row = packets.get(cid)
            deadline = decision_deadline(str(candidate["created_at_utc"]))
            if packet_row is None and now <= deadline:
                counts["AWAITING_OWNER_DECISION"] = counts.get("AWAITING_OWNER_DECISION", 0) + 1
                continue

            candidate_git_recorded = validate_candidate_git_timing(candidate, candidate_paths, repo_root, now)

            if packet_row is None:
                terminal = terminal_record(
                    candidate,
                    candidate_paths,
                    "EXPIRED_NO_OWNER_DECISION",
                    now,
                    candidate_git_recorded,
                )
                write_terminal(terminal_path, terminal)
                counts["EXPIRED_NO_OWNER_DECISION"] = counts.get("EXPIRED_NO_OWNER_DECISION", 0) + 1
                continue

            packet, packet_path = packet_row
            packet_git_recorded = git_first_add_at(repo_root, packet_path, "RATIFICATION_PACKET")
            decision_at = validate_packet_timing(candidate, packet, packet_git_recorded, candidate_git_recorded, now)
            if packet["decision"] == "REJECT":
                terminal = terminal_record(
                    candidate,
                    candidate_paths,
                    "REJECTED_BY_OWNER",
                    now,
                    candidate_git_recorded,
                    packet,
                    packet_path,
                    packet_git_recorded,
                )
                write_terminal(terminal_path, terminal)
                counts["REJECTED_BY_OWNER"] = counts.get("REJECTED_BY_OWNER", 0) + 1
                continue

            metric = str((candidate.get("candidate") or {}).get("metric_path") or "")
            baseline_path, baseline, _ = select_baseline(capture_root, metric, decision_at)
            status, frozen, frozen_path = ratifier.freeze_candidate(
                candidate,
                packet,
                baseline,
                baseline_path,
                frozen_root,
                None,
            )
            terminal = terminal_record(
                candidate,
                candidate_paths,
                "RATIFIED_AND_FROZEN",
                now,
                candidate_git_recorded,
                packet,
                packet_path,
                packet_git_recorded,
                baseline_path,
                baseline,
                frozen,
                frozen_path,
            )
            write_terminal(terminal_path, terminal)
            counts["RATIFIED_AND_FROZEN"] = counts.get("RATIFIED_AND_FROZEN", 0) + 1
            counts[f"FREEZE_{status}"] = counts.get(f"FREEZE_{status}", 0) + 1
        except Exception as exc:
            errors.append({"candidate_id": cid, "error": str(exc)})

    orphan_packets = sorted(set(packets) - set(groups))
    if orphan_packets:
        errors.append({"candidate_id": "MULTIPLE", "error": "ORPHAN_RATIFICATION_PACKETS:" + ",".join(orphan_packets)})

    return {
        "contract": "FORECAST_RATIFICATION_PROCESS_RUN_v1",
        "status": "FAIL" if errors else "PASS",
        "prospective_cutover_commit_sha": CUTOVER_COMMIT_SHA,
        "outcome_data_read": False,
        "counts": counts,
        "errors": errors,
        "authority": AUTHORITY,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pending-root", type=Path, required=True)
    ap.add_argument("--packet-root", type=Path, required=True)
    ap.add_argument("--terminal-root", type=Path, required=True)
    ap.add_argument("--frozen-root", type=Path, required=True)
    ap.add_argument("--capture-root", type=Path, required=True)
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--now-utc")
    args = ap.parse_args()
    now = parse_dt(args.now_utc) if args.now_utc else datetime.now(UTC)
    result = process(
        args.pending_root,
        args.packet_root,
        args.terminal_root,
        args.frozen_root,
        args.capture_root,
        args.repo_root.resolve(),
        now,
    )
    print(json.dumps(result, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
