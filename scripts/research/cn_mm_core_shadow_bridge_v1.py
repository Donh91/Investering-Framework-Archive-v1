"""Reuse the existing C01-C07 owner in the frozen weekly shadow lane.

No official forecast, model weighting, portfolio action, or scientific edge claim.
Source replay at a pinned checkout is not independent first-publication proof.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.master_monday.strict_json_v1 import load_evidence_object
from scripts.master_monday.weekly_source_binding_v1 import verify_sidecar

BASE = Path("06_RESEARCH_LAB/shared_row_model_tournament_v1")
LEDGER = BASE / "data/PROSPECTIVE_SHARED_ROW_LEDGER.csv"
POINTER = Path("03_DAILY_CAPTURE_LOGS/weekly/LATEST_WEEKLY_CALIBRATION.json")
CORE = ("C01_ETHBTC", "C02_BREADTH", "C03_BTCD", "C04_ETHBTC_BREADTH",
        "C05_ETHBTC_BTCD", "C06_BREADTH_BTCD", "C07_SIMPLE_3")
SINGLES = {"ETHBTC_PERSISTENCE": CORE[0], "BTCD_PATH_RECLAIM": CORE[2],
           "BREADTH_SURVIVAL": CORE[1]}
WITHOUT = {"ETHBTC_PERSISTENCE": CORE[5], "BTCD_PATH_RECLAIM": CORE[3],
           "BREADTH_SURVIVAL": CORE[4]}
MAX_ROWS = 12


def canon(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def clock(value):
    if not isinstance(value, str):
        raise ValueError("CLOCK_MISSING")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.utcoffset() != timedelta(0):
        raise ValueError("CLOCK_NOT_UTC")
    return result


def iso(value):
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def read_rows(raw):
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""), strict=True)
    if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
        raise ValueError("LEDGER_HEADER_INVALID")
    rows = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError("LEDGER_ROW_SHAPE_INVALID")
    return rows


def unknown(reason, **extra):
    return {"status": "UNKNOWN", "reason": reason, "latest_observation": None,
            "attribution": None, "transition_diagnostic": None, **extra}


def evaluate_rows(rows, start, end, floor, verify, mutable_fields):
    """Forecast-side projection only. A rejected recent row never falls back silently."""
    try:
        start, end, floor = map(clock, (start, end, floor))
        if start >= end:
            raise ValueError("WINDOW_INVALID")
        selected = []
        for row in rows:
            at = clock(row.get("observation_timestamp_utc"))
            if max(start, floor) <= at < end:
                selected.append((at, row))
        if not selected:
            return unknown("NO_ELIGIBLE_OBSERVATIONS", selected_row_n=0)
        ids = Counter(row.get("event_id") for _, row in selected)
        clocks = Counter(at for at, _ in selected)
        if any(n != 1 for n in ids.values()) or any(n != 1 for n in clocks.values()):
            return unknown("DUPLICATE_OBSERVATION")
        selected.sort(key=lambda item: item[0])
        history = []
        for at, row in selected[-MAX_ROWS:]:
            if (row.get("event_id") != "PSR_" + at.strftime("%Y%m%dT%H%M%SZ") or
                    clock(row.get("information_cutoff_utc")) != at or
                    row.get("row_integrity_contract") != "SHARED_ROW_P0_BINDING_v1"):
                return unknown("OBSERVATION_IDENTITY_INVALID")
            # Never pass mature outcomes, adverse/favorable excursions, or future
            # outcome-owner receipts into the feature-side owner replay.
            projection = {k: v for k, v in row.items() if k not in mutable_fields}
            decisions = load_evidence_object(projection["candidate_decisions"].encode())
            load_evidence_object(projection["source_binding_manifest"].encode())
            if not set(CORE).issubset(decisions) or any(type(decisions[k]) is not bool for k in CORE):
                return unknown("CORE_DECISIONS_INCOMPLETE")
            verify(projection, at, decisions)
            history.append({"event_id": row["event_id"], "observation_utc": iso(at),
                            "source_commit": row["source_version_commit"],
                            "provenance_sha256": row["provenance_hash"],
                            "decisions": {k: decisions[k] for k in CORE}})
        latest = history[-1]
        d = latest["decisions"]
        attribution = {family: {"single_candidate": candidate, "observed_permission": d[candidate],
                               "without_family_candidate": WITHOUT[family],
                               "without_family_permission": d[WITHOUT[family]],
                               "pivotal_in_frozen_and_rule": d[WITHOUT[family]] != d[CORE[-1]]}
                       for family, candidate in SINGLES.items()}
        transitions = {}
        for family, candidate in SINGLES.items():
            rising = [(a["observation_utc"], b["observation_utc"])
                      for a, b in zip(history, history[1:])
                      if not a["decisions"][candidate] and b["decisions"][candidate]]
            if d[candidate] and rising:
                transitions[family] = list(rising[-1])
        # Only ordered observation intervals, never exact market event times.
        # The frozen core is not the original persistence/rollover sequence.
        ordered = len(transitions) == len(SINGLES) and all(
            clock(transitions[a][1]) <= clock(transitions[b][0])
            for a, b in zip(SINGLES, list(SINGLES)[1:]))
        diagnostic = {"status": "ORDERED_OBSERVATION_INTERVALS" if ordered else "ORDER_NOT_ESTABLISHED",
                      "intervals": transitions, "original_sequence_equivalence": False,
                      "event_time_certified": False}
        return {"status": "CORE_REPLAY_AT_OBSERVATION_ONLY", "reason": None,
                "selected_row_n": len(selected), "replayed_row_n": len(history),
                "history_truncated": len(selected) > MAX_ROWS, "history": history,
                "latest_observation": latest, "attribution": attribution,
                "transition_diagnostic": diagnostic}
    except (ValueError, TypeError, KeyError, AttributeError, RuntimeError, OSError, OverflowError, csv.Error, ImportError, subprocess.SubprocessError):
        return unknown("OWNER_REPLAY_OR_LEDGER_VALIDATION_FAILED")


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, timeout=30).stdout


def committed(path, head, *, compare_worktree=False):
    raw = git("show", f"{head}:{path.as_posix()}")
    if compare_worktree and (ROOT / path).read_bytes() != raw:
        raise ValueError("DIRTY_SOURCE_BYTES")
    return raw


def freeze_identity(path, head, *, compare_worktree):
    if not re.fullmatch("[0-9a-f]{40}", head):
        raise ValueError("INVALID_CHECKOUT_SHA")
    relative = path.resolve().relative_to(ROOT)
    raw = committed(relative, head, compare_worktree=compare_worktree)
    value = load_evidence_object(raw)
    year, week = value["iso_year"], value["iso_week"]
    if type(year) is not int or type(week) is not int:
        raise ValueError("INVALID_WEEK")
    datetime.fromisocalendar(year, week, 1)
    expected = Path(f"research/master_monday_preflight/frozen/{year}/W{week:02d}/WEEKLY_EVIDENCE_FREEZE.json")
    if relative != expected or not re.fullmatch("[0-9a-f]{64}", value["freeze_sha256"]):
        raise ValueError("FREEZE_IDENTITY_MISMATCH")
    return relative, raw, value


def load_owner():
    directory = str(Path(__file__).resolve().parent)
    if directory not in sys.path:
        sys.path.insert(0, directory)
    import prospective_evidence_controller as owner
    return owner


def build_checkout(freeze_file, head):
    if git("rev-parse", "HEAD").decode().strip() != head or Path.cwd().resolve() != ROOT:
        raise ValueError("PINNED_CHECKOUT_REQUIRED")
    path, frozen_bytes, freeze = freeze_identity(freeze_file, head, compare_worktree=True)
    packet = {"contract": "CN_MM_CORE_SHADOW_BRIDGE_v1", "authority": "RESEARCH_ONLY_NON_CANONICAL",
              "checkout_sha": head, "freeze_sha256": freeze["freeze_sha256"],
              "freeze_file_sha256": sha(frozen_bytes), "completed_week": f"{freeze['iso_year']}-W{freeze['iso_week']:02d}",
              "first_known_status": "UNKNOWN", "scientific_pit_eligible": False,
              "forecast_authority": False, "portfolio_execution": False, "canonical_effect": False,
              "target_semantics": "ETHBTC_FORWARD_RELATIVE_RETURN_GT_ZERO_NOT_ALTSEASON_LIFECYCLE",
              "ledger_sha256": None, "source_presence": "PINNED_CHECKOUT_NOT_FIRST_KNOWN_PROOF"}
    try:
        ledger_raw = committed(LEDGER, head, compare_worktree=True)
        packet["ledger_sha256"] = sha(ledger_raw)
        pointer = load_evidence_object(committed(POINTER, head, compare_worktree=True))
        binding = verify_sidecar(ROOT / path.parent, pointer=pointer, freeze=freeze,
                                 capture_root=Path("03_DAILY_CAPTURE_LOGS"),
                                 expected_freeze_sha256=freeze["freeze_sha256"])
        if binding["status"] != "BYTE_BINDING_AND_RECEIPT_VERIFIED":
            raise ValueError("MM_SOURCE_BINDING_UNVERIFIED")
        committed(Path(binding["source_path"]), head, compare_worktree=True)
        committed(path.parent / "SOURCE_BINDINGS" / (freeze["freeze_sha256"] + ".json"),
                  head, compare_worktree=True)
        for name in ("TRANSFORM_FREEZE_REGISTRY.json", "CORE_FAMILY_PROSPECTIVE_CONTRACT_v1.json",
                     "03_CANDIDATE_REGISTRY.json", "RUNTIME_STATUS.json"):
            committed(BASE / name, head, compare_worktree=True)
        owner = load_owner()
        eligible = set(owner.eligible_candidates())
        if not set(CORE).issubset(eligible):
            raise ValueError("FROZEN_CORE_INACTIVE")
        floor = max(owner.eligibility_floor_for_candidate(k) for k in CORE)
        start, end, frozen = map(clock, (freeze["window_start_utc"], freeze["window_end_utc"],
                                        freeze["created_at_utc"]))
        if not start < end <= frozen:
            raise ValueError("INVALID_FREEZE_WINDOW")

        def verify(row, at, decisions):
            owner.verify_frozen_provenance(row)
            owner.validate_core_decision_contract(row, decisions, eligible)
            owner.verify_source_bindings(row, at)

        packet["core"] = evaluate_rows(read_rows(ledger_raw), iso(start), iso(end), iso(floor),
                                       verify, owner.PROVENANCE_MUTABLE_FIELDS)
    except (ValueError, TypeError, KeyError, AttributeError, RuntimeError, OSError, OverflowError, csv.Error, ImportError, subprocess.SubprocessError):
        packet["core"] = unknown("FROZEN_SOURCE_OR_OWNER_UNAVAILABLE")
    packet["packet_sha256"] = sha(canon(packet))
    return packet


def verify_packet_projection(packet, freeze, ledger_raw, registry_raw):
    """Recompute the observation projection; source replay remains the owner's job.

    This prevents a self-rehashed packet from inventing a different candidate
    decision or interval ordering at publication or CN consumption.
    """
    if sha(ledger_raw) != packet.get("ledger_sha256"):
        raise ValueError("SHADOW_LEDGER_BINDING_MISMATCH")
    registry = load_evidence_object(registry_raw)
    rule = registry["core_activation_rule"]
    families = {r["family_id"]: r for r in registry["families"]}
    if set(rule["start_only_when"]) != set(SINGLES) or set(rule["candidates"]) != set(CORE):
        raise ValueError("SHADOW_FROZEN_CORE_MISMATCH")
    floor = max(clock(families[k]["prospective_eligibility_start"]) for k in SINGLES)
    start, end, frozen = map(clock, (freeze["window_start_utc"], freeze["window_end_utc"], freeze["created_at_utc"]))
    if not start < end <= frozen:
        raise ValueError("SHADOW_FREEZE_WINDOW_INVALID")
    mutable = {f"{k}_{h}" for h in ("24h", "72h", "7d") for k in ("outcome", "mae", "mfe")}
    expected = evaluate_rows(read_rows(ledger_raw), iso(start), iso(end), iso(floor),
                             lambda *_: None, mutable)
    if expected["status"] != "CORE_REPLAY_AT_OBSERVATION_ONLY" or packet["core"] != expected:
        raise ValueError("SHADOW_PROJECTION_MISMATCH")


def publish_packet(packet_path, freeze_file, head, output_dir):
    _, frozen_bytes, freeze = freeze_identity(freeze_file, head, compare_worktree=True)
    raw = packet_path.read_bytes()
    packet = load_evidence_object(raw)
    body = dict(packet)
    claimed = body.pop("packet_sha256", None)
    if (raw != canon(packet) or claimed != sha(canon(body)) or
            packet.get("contract") != "CN_MM_CORE_SHADOW_BRIDGE_v1" or
            packet.get("authority") != "RESEARCH_ONLY_NON_CANONICAL" or
            packet.get("checkout_sha") != head or packet.get("freeze_sha256") != freeze["freeze_sha256"] or
            packet.get("freeze_file_sha256") != sha(frozen_bytes) or
            packet.get("first_known_status") != "UNKNOWN" or
            any(packet.get(k) is not False for k in ("scientific_pit_eligible", "forecast_authority",
                                                      "portfolio_execution", "canonical_effect"))):
        raise ValueError("SHADOW_PACKET_BINDING_OR_AUTHORITY_MISMATCH")
    if packet.get("ledger_sha256") is not None and packet["ledger_sha256"] != sha(committed(LEDGER, head)):
        raise ValueError("SHADOW_LEDGER_BINDING_MISMATCH")
    if packet["core"]["status"] == "CORE_REPLAY_AT_OBSERVATION_ONLY":
        verify_packet_projection(packet, freeze, committed(LEDGER, head),
                                 committed(BASE / "TRANSFORM_FREEZE_REGISTRY.json", head))
    elif packet["core"]["status"] != "UNKNOWN" or packet["core"].get("latest_observation") is not None:
        raise ValueError("SHADOW_UNKNOWN_STATUS_INVALID")
    expected_output_dir = ROOT / "research/api_agent/outputs/weekly" / str(freeze["iso_year"]) / f"W{freeze['iso_week']:02d}"
    if output_dir.resolve() != expected_output_dir.resolve():
        raise ValueError("SHADOW_PUBLICATION_ROUTE_MISMATCH")
    target = output_dir / ("CN_MM_CORE_SHADOW_" + freeze["freeze_sha256"] + ".json")
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with target.open("xb") as handle:
            handle.write(raw)
    except FileExistsError:
        if target.read_bytes() != raw:
            raise ValueError("SHADOW_PACKET_WRITE_ONCE_CONFLICT")
    return target


def consume_cn_shadow(repo, mm_pointer):
    """Read only an exact committed MM packet. No mutation of official CN value."""
    result = {"contract": "CN_MM_CORE_SHADOW_CONSUMPTION_v1", "authority": "RESEARCH_ONLY_NON_CANONICAL",
              "status": "UNKNOWN", "reason": "MM_SHADOW_RECEIPT_UNAVAILABLE",
              "official_forecast_effect": False, "scientific_pit_eligible": False,
              "packet_sha256": None, "shadow_candidate_decision": None}
    try:
        year, week = mm_pointer["iso_year"], mm_pointer["iso_week"]
        freeze_sha = mm_pointer["freeze_sha256"]
        if type(year) is not int or type(week) is not int or not re.fullmatch("[0-9a-f]{64}", freeze_sha):
            raise ValueError("MM_IDENTITY_INVALID")
        datetime.fromisocalendar(year, week, 1)
        relative = Path(f"research/api_agent/outputs/weekly/{year}/W{week:02d}/CN_MM_CORE_SHADOW_{freeze_sha}.json")
        path = repo / relative
        if not path.exists():
            return result
        if not path.resolve().is_relative_to(repo.resolve()):
            raise ValueError("SHADOW_PATH_ESCAPE")

        def run(*args):
            return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, timeout=30).stdout

        raw = path.read_bytes()
        if raw != run("show", f"HEAD:{relative.as_posix()}"):
            raise ValueError("SHADOW_RECEIPT_NOT_COMMITTED")
        packet = load_evidence_object(raw)
        body = dict(packet)
        digest = body.pop("packet_sha256", None)
        if (raw != canon(packet) or digest != sha(canon(body)) or
                packet.get("contract") != "CN_MM_CORE_SHADOW_BRIDGE_v1" or
                packet.get("authority") != "RESEARCH_ONLY_NON_CANONICAL" or
                packet.get("freeze_sha256") != freeze_sha or
                packet.get("completed_week") != f"{year}-W{week:02d}" or
                packet.get("first_known_status") != "UNKNOWN" or
                any(packet.get(k) is not False for k in ("scientific_pit_eligible", "forecast_authority",
                                                          "portfolio_execution", "canonical_effect"))):
            raise ValueError("SHADOW_RECEIPT_BINDING_OR_AUTHORITY_INVALID")
        head = packet["checkout_sha"]
        if not re.fullmatch("[0-9a-f]{40}", head):
            raise ValueError("SHADOW_SOURCE_COMMIT_INVALID")
        run("merge-base", "--is-ancestor", head, "HEAD")
        freeze_path = f"research/master_monday_preflight/frozen/{year}/W{week:02d}/WEEKLY_EVIDENCE_FREEZE.json"
        frozen = run("show", f"{head}:{freeze_path}")
        if (sha(frozen) != packet["freeze_file_sha256"] or
                load_evidence_object(frozen)["freeze_sha256"] != freeze_sha):
            raise ValueError("SHADOW_FREEZE_BYTES_INVALID")
        core = packet["core"]
        if core["status"] != "CORE_REPLAY_AT_OBSERVATION_ONLY":
            return {**result, "packet_sha256": digest, "reason": "MM_CORE_REPLAY_UNAVAILABLE"}
        verify_packet_projection(packet, load_evidence_object(frozen),
                                 run("show", f"{head}:{LEDGER.as_posix()}"),
                                 run("show", f"{head}:{(BASE / 'TRANSFORM_FREEZE_REGISTRY.json').as_posix()}"))
        latest = core["latest_observation"]
        decisions = latest["decisions"]
        if set(decisions) != set(CORE) or any(type(v) is not bool for v in decisions.values()):
            raise ValueError("SHADOW_DECISIONS_INVALID")
        return {**result, "status": "CONSUMED_SHADOW_ONLY", "reason": None,
                "packet_sha256": digest, "packet_file_sha256": sha(raw), "checkout_sha": head,
                "observation_utc": latest["observation_utc"],
                "shadow_candidate_decision": decisions[CORE[-1]],
                "candidate_id": CORE[-1], "target_semantics": packet["target_semantics"],
                "observation_only": True, "edge_established": False}
    except (ValueError, TypeError, KeyError, AttributeError, RuntimeError, OSError, subprocess.SubprocessError):
        return {**result, "reason": "MM_SHADOW_RECEIPT_INVALID"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze-file", type=Path, required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--publish-from", type=Path)
    args = parser.parse_args()
    if args.publish_from is not None:
        print(publish_packet(args.publish_from, args.freeze_file, args.expected_head, args.output))
        return
    packet = build_checkout(args.freeze_file, args.expected_head)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canon(packet))
    print(json.dumps({"status": packet["core"]["status"], "packet_sha256": packet["packet_sha256"]}))


if __name__ == "__main__":
    main()
