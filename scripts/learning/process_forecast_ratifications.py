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

from forecast_ratification_contract import (  # noqa: E402
    CUTOVER_COMMIT_SHA,
    DECISION_SLA_MINUTES,
    PACKET_RECORDING_TOLERANCE_MINUTES,
    RATIFICATION_PACKET_V2,
    RATIFICATION_TERMINAL_V1,
    decision_deadline,
    is_post_cutover_candidate,
    iso,
    parse_dt,
    validate_packet_shape,
)
import ratify_forecast_candidate as ratifier  # noqa: E402

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


def index_candidates(root: Path) -> dict[str, tuple[dict[str, Any], list[Path]]]:
    found: dict[str, tuple[dict[str, Any], list[Path]]] = {}
    for path in sorted(root.rglob("*.json")) if root.exists() else []:
        value = read(path)
        if value.get("contract") != "FORECAST_CANDIDATE_v1":
            continue
        cid = str(value.get("candidate_id") or "")
        if not cid:
            raise ValueError(f"CANDIDATE_ID_MISSING:{path}")
        if cid not in found:
            found[cid] = (value, [path])
            continue
        existing, paths = found[cid]
        if canon(existing) != canon(value):
            raise ValueError(f"DIVERGENT_DUPLICATE_CANDIDATE:{cid}")
        paths.append(path)
    return found


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


def packet_git_recorded_at(repo_root: Path, packet_path: Path) -> datetime:
    repo_root = repo_root.resolve()
    try:
        rel = packet_path.resolve().relative_to(repo_root).as_posix()
    except ValueError as exc:
        raise ValueError("RATIFICATION_PACKET_OUTSIDE_REPOSITORY") from exc
    proc = subprocess.run(
        ["git", "log", "--diff-filter=A", "--follow", "--reverse", "--format=%cI", "--", rel],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    rows = [row.strip() for row in proc.stdout.splitlines() if row.strip()]
    if not rows:
        raise ValueError(f"RATIFICATION_PACKET_NOT_GIT_RECORDED:{rel}")
    return parse_dt(rows[0])


def validate_packet_timing(candidate: dict[str, Any], packet: dict[str, Any], git_recorded_at: datetime, now: datetime) -> datetime:
    if packet.get("candidate_id") != candidate.get("candidate_id"):
        raise ValueError("CANDIDATE_ID_MISMATCH")
    if packet.get("candidate_sha256") != digest(candidate):
        raise ValueError("CANDIDATE_HASH_MISMATCH")
    created = parse_dt(str(candidate["created_at_utc"]))
    decision_at = parse_dt(str(packet["decision_at_utc"]))
    deadline = decision_deadline(str(candidate["created_at_utc"]))
    if decision_at < created:
        raise ValueError("RATIFICATION_PRECEDES_CANDIDATE")
    if decision_at > deadline:
        raise ValueError("RATIFICATION_DECISION_SLA_EXCEEDED")
    if decision_at > now:
        raise ValueError("RATIFICATION_DECISION_IN_FUTURE")
    delta = (git_recorded_at - decision_at).total_seconds()
    if delta < 0:
        raise ValueError("RATIFICATION_GIT_RECORD_PRECEDES_DECISION")
    if delta > PACKET_RECORDING_TOLERANCE_MINUTES * 60:
        raise ValueError("RATIFICATION_PACKET_BACKDATED_OR_LATE_RECORDED")
    return decision_at


def candidate_metric_value(evidence: dict[str, Any], metric: str) -> Any:
    return ratifier.metric_value(evidence, metric)


def select_baseline(capture_root: Path, metric: str, decision_at: datetime) -> tuple[Path, dict[str, Any], datetime]:
    eligible: list[tuple[datetime, Path, dict[str, Any]]] = []
    for path in sorted(capture_root.rglob("*.json")) if capture_root.exists() else []:
        try:
            value = read(path)
            observed = ratifier.evidence_timestamp(value)
        except Exception:
            continue
        if observed > decision_at:
            continue
        start = candidate_metric_value(value, metric)
        if not isinstance(start, (int, float)):
            continue
        eligible.append((observed, path, value))
    if not eligible:
        raise ValueError("NO_BASELINE_EVIDENCE_AT_OR_BEFORE_RATIFICATION_DECISION")
    eligible.sort(key=lambda row: (row[0], row[1].as_posix()))
    observed, path, value = eligible[-1]
    return path, value, observed


def terminal_record(
    candidate: dict[str, Any],
    candidate_paths: list[Path],
    disposition: str,
    now: datetime,
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
        "terminal_at_utc": iso(now),
        "disposition": disposition,
        "prospective_cutover_commit_sha": CUTOVER_COMMIT_SHA,
        "decision_sla_minutes": DECISION_SLA_MINUTES,
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
            "outcome_blind": packet.get("outcome_blind"),
        }
    if baseline is not None and baseline_path is not None:
        value["baseline"] = {
            "path": baseline_path.as_posix(),
            "sha256": digest(baseline),
            "observed_at_utc": iso(ratifier.evidence_timestamp(baseline)),
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


def write_terminal(path: Path, value: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = read(path)
        if canon(existing) != canon(value):
            # terminal_at_utc is allowed to differ only for a duplicate recomputation;
            # bind comparison to all immutable semantic fields by retaining existing.
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
    candidates = index_candidates(pending_root)
    packets = index_packets(packet_root)
    counts: dict[str, int] = {}
    errors: list[dict[str, str]] = []

    for cid, (candidate, candidate_paths) in sorted(candidates.items()):
        terminal_path = terminal_root / f"{cid}.json"
        if terminal_path.exists():
            counts["ALREADY_TERMINAL"] = counts.get("ALREADY_TERMINAL", 0) + 1
            continue
        try:
            if not is_post_cutover_candidate(candidate):
                terminal = terminal_record(candidate, candidate_paths, "LEGACY_PRE_CUTOVER_HINDSIGHT_INELIGIBLE", now)
                write_terminal(terminal_path, terminal)
                counts["LEGACY_PRE_CUTOVER_HINDSIGHT_INELIGIBLE"] = counts.get("LEGACY_PRE_CUTOVER_HINDSIGHT_INELIGIBLE", 0) + 1
                continue

            packet_row = packets.get(cid)
            deadline = decision_deadline(str(candidate["created_at_utc"]))
            if packet_row is None:
                if now <= deadline:
                    counts["AWAITING_OWNER_DECISION"] = counts.get("AWAITING_OWNER_DECISION", 0) + 1
                    continue
                terminal = terminal_record(candidate, candidate_paths, "EXPIRED_NO_OWNER_DECISION", now)
                write_terminal(terminal_path, terminal)
                counts["EXPIRED_NO_OWNER_DECISION"] = counts.get("EXPIRED_NO_OWNER_DECISION", 0) + 1
                continue

            packet, packet_path = packet_row
            git_recorded_at = packet_git_recorded_at(repo_root, packet_path)
            decision_at = validate_packet_timing(candidate, packet, git_recorded_at, now)
            if packet["decision"] == "REJECT":
                terminal = terminal_record(
                    candidate,
                    candidate_paths,
                    "REJECTED_BY_OWNER",
                    now,
                    packet,
                    packet_path,
                    git_recorded_at,
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
                packet,
                packet_path,
                git_recorded_at,
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

    orphan_packets = sorted(set(packets) - set(candidates))
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
