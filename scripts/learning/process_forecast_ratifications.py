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

from forecast_candidate_grouping import classified_candidate_groups_with_quarantine  # noqa: E402
from forecast_ratification_baseline import MAX_BASELINE_AGE_MINUTES, select_archived_baseline  # noqa: E402
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


def _repo_relative(repo_root: Path, path: Path, label: str) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"{label}_OUTSIDE_REPOSITORY") from exc


def _git(repo_root: Path, args: list[str], *, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root.resolve(),
        capture_output=True,
        text=text,
        check=True,
    )


def git_path_has_history(repo_root: Path, path: Path) -> bool:
    rel = _repo_relative(repo_root, path, "GIT_PATH")
    proc = _git(repo_root, ["log", "-1", "--format=%H", "--", rel])
    return bool(str(proc.stdout).strip())


def git_first_add_record(repo_root: Path, path: Path, label: str) -> tuple[datetime, str, str, bytes]:
    """Return first-add time/commit/historical path/content for an immutable record.

    `--follow` preserves rename ancestry. The first-add commit may contain the
    file under an earlier directory, so resolve the added path from that commit
    rather than assuming the current path existed there.
    """
    rel = _repo_relative(repo_root, path, label)
    proc = _git(
        repo_root,
        ["log", "--diff-filter=A", "--follow", "--reverse", "--format=%H%x09%cI", "--", rel],
    )
    rows = [row.strip() for row in str(proc.stdout).splitlines() if row.strip()]
    if not rows:
        raise ValueError(f"{label}_NOT_GIT_RECORDED:{rel}")
    first = rows[0].split("\t", 1)
    if len(first) != 2:
        raise ValueError(f"{label}_GIT_FIRST_ADD_FORMAT_INVALID")
    commit_sha, recorded_raw = first
    recorded_at = parse_dt(recorded_raw)

    diff = _git(repo_root, ["diff-tree", "--root", "--no-commit-id", "--name-status", "-r", commit_sha])
    added_paths: list[str] = []
    for line in str(diff.stdout).splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0] == "A":
            added_paths.append(parts[-1])
    if rel in added_paths:
        historical_rel = rel
    else:
        same_name = [candidate for candidate in added_paths if Path(candidate).name == path.name]
        if len(same_name) != 1:
            raise ValueError(f"{label}_FIRST_ADD_PATH_AMBIGUOUS")
        historical_rel = same_name[0]

    blob = _git(repo_root, ["show", f"{commit_sha}:{historical_rel}"], text=False).stdout
    if not isinstance(blob, (bytes, bytearray)):
        raise ValueError(f"{label}_FIRST_ADD_CONTENT_UNAVAILABLE")
    return recorded_at, commit_sha, historical_rel, bytes(blob)


def validate_first_add_json_binding(repo_root: Path, path: Path, label: str, current: dict[str, Any]) -> tuple[datetime, str]:
    recorded_at, commit_sha, _, first_blob = git_first_add_record(repo_root, path, label)
    try:
        first_value = json.loads(first_blob.decode("utf-8"))
    except Exception as exc:
        raise ValueError(f"{label}_FIRST_ADD_JSON_INVALID") from exc
    if canon(first_value) != canon(current):
        raise ValueError(f"{label}_CONTENT_CHANGED_AFTER_FIRST_ADD")
    return recorded_at, commit_sha


def index_packets_with_quarantine(root: Path) -> tuple[dict[str, tuple[dict[str, Any], Path]], set[str], list[dict[str, str]]]:
    found: dict[str, tuple[dict[str, Any], Path]] = {}
    blocked: set[str] = set()
    quarantines: list[dict[str, str]] = []
    for path in sorted(root.rglob("*.json")) if root.exists() else []:
        inferred = path.stem
        try:
            value = read(path)
        except Exception as exc:
            blocked.add(inferred)
            quarantines.append({"candidate_id": inferred, "path": path.as_posix(), "error": f"RATIFICATION_PACKET_JSON_INVALID:{exc}"})
            continue
        cid = str(value.get("candidate_id") or inferred)
        try:
            validate_packet_shape(value)
            if path.stem != cid:
                raise ValueError("RATIFICATION_PACKET_FILENAME_MISMATCH")
        except Exception as exc:
            blocked.add(cid)
            quarantines.append({"candidate_id": cid, "path": path.as_posix(), "error": str(exc)})
            continue
        if cid in found:
            blocked.add(cid)
            previous = found.pop(cid)
            quarantines.append({"candidate_id": cid, "path": previous[1].as_posix(), "error": "MULTIPLE_RATIFICATION_PACKETS"})
            quarantines.append({"candidate_id": cid, "path": path.as_posix(), "error": "MULTIPLE_RATIFICATION_PACKETS"})
            continue
        if cid in blocked:
            quarantines.append({"candidate_id": cid, "path": path.as_posix(), "error": "RATIFICATION_PACKET_ID_ALREADY_QUARANTINED"})
            continue
        found[cid] = (value, path)
    return found, blocked, quarantines


def validate_candidate_git_timing(candidate: dict[str, Any], candidate_paths: list[Path], repo_root: Path, now: datetime) -> datetime:
    if len(candidate_paths) != 1:
        raise ValueError("POST_CUTOVER_DUPLICATE_CANDIDATE_PATHS")
    git_recorded_at, _ = validate_first_add_json_binding(repo_root, candidate_paths[0], "CANDIDATE", candidate)
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
        "baseline_max_age_minutes": MAX_BASELINE_AGE_MINUTES,
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
            "selection_semantics": "FRESHEST_IMMUTABLE_ARCHIVED_CAPTURE_AT_OR_BEFORE_OWNER_DECISION_NO_METRIC_HISTORY_FALLBACK",
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
        {"path": row["path"].as_posix(), "sha256": row["sha256"], "created_at_utc": row.get("created_at_utc")}
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


def post_cutover_quarantine_terminal_record(quarantine: dict[str, Any], now: datetime) -> dict[str, Any]:
    value: dict[str, Any] = {
        "contract": RATIFICATION_TERMINAL_V1,
        "candidate_id": quarantine["candidate_id"],
        "candidate_sha256": None,
        "candidate_paths": quarantine.get("paths", []),
        "candidate_variants": quarantine.get("variants", []),
        "terminal_at_utc": iso(now),
        "disposition": "POST_CUTOVER_CANDIDATE_STRUCTURE_QUARANTINED",
        "quarantine_reason": quarantine.get("error"),
        "prospective_cutover_commit_sha": CUTOVER_COMMIT_SHA,
        "historical_candidate_rewritten": False,
        "outcome_data_read": False,
        "ratification_allowed": False,
        "authority": AUTHORITY,
    }
    value["terminal_sha256"] = digest(value)
    return value


def verify_terminal_self_hash(value: dict[str, Any]) -> None:
    expected = value.get("terminal_sha256")
    material = dict(value)
    material.pop("terminal_sha256", None)
    if expected != digest(material):
        raise ValueError("RATIFICATION_TERMINAL_SELF_HASH_MISMATCH")


def verify_existing_terminal(repo_root: Path, path: Path) -> str:
    current = read(path)
    verify_terminal_self_hash(current)
    try:
        _, _, _, first_blob = git_first_add_record(repo_root, path, "RATIFICATION_TERMINAL")
    except ValueError as exc:
        if "NOT_GIT_RECORDED" in str(exc):
            return "LOCAL_PENDING_COMMIT"
        raise
    try:
        first_value = json.loads(first_blob.decode("utf-8"))
    except Exception as exc:
        raise ValueError("RATIFICATION_TERMINAL_FIRST_ADD_JSON_INVALID") from exc
    if canon(first_value) != canon(current):
        raise ValueError("RATIFICATION_TERMINAL_CONTENT_CHANGED_AFTER_FIRST_ADD")
    return "GIT_BOUND"


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
    groups, group_quarantines = classified_candidate_groups_with_quarantine(pending_root)
    packets, blocked_packet_ids, packet_quarantines = index_packets_with_quarantine(packet_root)
    counts: dict[str, int] = {}
    errors: list[dict[str, str]] = [
        {"candidate_id": str(row.get("candidate_id") or "UNKNOWN"), "error": str(row.get("error") or "STRUCTURE_QUARANTINED")}
        for row in [*group_quarantines, *packet_quarantines]
    ]

    # Persist an append-only fail-closed terminal for identifiable prospective
    # duplicate groups. Malformed single files remain quarantined by path only.
    for quarantine in group_quarantines:
        cid = str(quarantine.get("candidate_id") or "")
        if not cid or not str(quarantine.get("error") or "").startswith("POST_CUTOVER_DUPLICATE_CANDIDATE_ID"):
            continue
        terminal_path = terminal_root / f"{cid}.json"
        if not terminal_path.exists() and not git_path_has_history(repo_root, terminal_path):
            write_terminal(terminal_path, post_cutover_quarantine_terminal_record(quarantine, now))
            counts["POST_CUTOVER_CANDIDATE_STRUCTURE_QUARANTINED"] = counts.get("POST_CUTOVER_CANDIDATE_STRUCTURE_QUARANTINED", 0) + 1

    for cid, group in sorted(groups.items()):
        terminal_path = terminal_root / f"{cid}.json"
        if terminal_path.exists():
            try:
                verify_existing_terminal(repo_root, terminal_path)
                counts["ALREADY_TERMINAL"] = counts.get("ALREADY_TERMINAL", 0) + 1
            except Exception as exc:
                errors.append({"candidate_id": cid, "error": str(exc)})
            continue
        if git_path_has_history(repo_root, terminal_path):
            errors.append({"candidate_id": cid, "error": "RATIFICATION_TERMINAL_MISSING_BUT_GIT_RECORDED"})
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

            if cid in blocked_packet_ids:
                errors.append({"candidate_id": cid, "error": "RATIFICATION_PACKET_STRUCTURE_QUARANTINED"})
                continue

            packet_row = packets.get(cid)
            deadline = decision_deadline(str(candidate["created_at_utc"]))
            if packet_row is None and now <= deadline:
                counts["AWAITING_OWNER_DECISION"] = counts.get("AWAITING_OWNER_DECISION", 0) + 1
                continue

            candidate_git_recorded = validate_candidate_git_timing(candidate, candidate_paths, repo_root, now)

            if packet_row is None:
                terminal = terminal_record(candidate, candidate_paths, "EXPIRED_NO_OWNER_DECISION", now, candidate_git_recorded)
                write_terminal(terminal_path, terminal)
                counts["EXPIRED_NO_OWNER_DECISION"] = counts.get("EXPIRED_NO_OWNER_DECISION", 0) + 1
                continue

            packet, packet_path = packet_row
            packet_git_recorded, _ = validate_first_add_json_binding(repo_root, packet_path, "RATIFICATION_PACKET", packet)
            decision_at = validate_packet_timing(candidate, packet, packet_git_recorded, candidate_git_recorded, now)
            if packet["decision"] == "REJECT":
                terminal = terminal_record(
                    candidate, candidate_paths, "REJECTED_BY_OWNER", now, candidate_git_recorded,
                    packet, packet_path, packet_git_recorded,
                )
                write_terminal(terminal_path, terminal)
                counts["REJECTED_BY_OWNER"] = counts.get("REJECTED_BY_OWNER", 0) + 1
                continue

            metric = str((candidate.get("candidate") or {}).get("metric_path") or "")
            baseline_path, baseline, _ = select_baseline(capture_root, metric, decision_at)
            status, frozen, frozen_path = ratifier.freeze_candidate(candidate, packet, baseline, baseline_path, frozen_root, None)
            terminal = terminal_record(
                candidate, candidate_paths, "RATIFIED_AND_FROZEN", now, candidate_git_recorded,
                packet, packet_path, packet_git_recorded, baseline_path, baseline, frozen, frozen_path,
            )
            write_terminal(terminal_path, terminal)
            counts["RATIFIED_AND_FROZEN"] = counts.get("RATIFIED_AND_FROZEN", 0) + 1
            counts[f"FREEZE_{status}"] = counts.get(f"FREEZE_{status}", 0) + 1
        except Exception as exc:
            errors.append({"candidate_id": cid, "error": str(exc)})

    orphan_packets = sorted(set(packets) - set(groups))
    for cid in orphan_packets:
        errors.append({"candidate_id": cid, "error": "ORPHAN_RATIFICATION_PACKET"})

    return {
        "contract": "FORECAST_RATIFICATION_PROCESS_RUN_v1",
        "status": "FAIL" if errors else "PASS",
        "pipeline_blocking": False,
        "execution_disposition": "CONTINUE_WITH_QUARANTINE" if errors else "CONTINUE",
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
    if result.get("pipeline_blocking"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
