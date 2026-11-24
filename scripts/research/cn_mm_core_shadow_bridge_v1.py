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
        replay = owner.PinnedSourceReplay(ROOT, head)
        if replay.ledger_raw != ledger_raw:
            raise ValueError("SHADOW_PINNED_LEDGER_MISMATCH")
        floor = replay.floor
        start, end, frozen = map(clock, (freeze["window_start_utc"], freeze["window_end_utc"],
                                        freeze["created_at_utc"]))
        if not start < end <= frozen:
            raise ValueError("INVALID_FREEZE_WINDOW")

        packet["core"] = evaluate_rows(read_rows(ledger_raw), iso(start), iso(end), iso(floor),
                                       replay.verify, owner.PROVENANCE_MUTABLE_FIELDS)
    except (ValueError, TypeError, KeyError, AttributeError, RuntimeError, OSError, OverflowError, csv.Error, ImportError, subprocess.SubprocessError):
        packet["core"] = unknown("FROZEN_SOURCE_OR_OWNER_UNAVAILABLE")
    packet["packet_sha256"] = sha(canon(packet))
    return packet


def verify_packet_projection(packet, freeze, ledger_raw, registry_raw, *, repo):
    """Recompute from original source bytes, not merely the self-hashed ledger.

    Keep the v1 packet shape unchanged; persistence is a versioned readback
    diagnostic, not an independent PIT claim.
    """
    owner = load_owner()
    replay = owner.PinnedSourceReplay(repo, packet["checkout_sha"])
    if (sha(ledger_raw) != packet.get("ledger_sha256") or
            replay.ledger_raw != ledger_raw or replay.registry_raw != registry_raw):
        raise ValueError("SHADOW_LEDGER_BINDING_MISMATCH")
    start, end, frozen = map(clock, (freeze["window_start_utc"], freeze["window_end_utc"], freeze["created_at_utc"]))
    if not start < end <= frozen:
        raise ValueError("SHADOW_FREEZE_WINDOW_INVALID")
    diagnostics = {}
    sequence_inputs = []
    verified_rows = {}

    def verify(row, at, decisions):
        persistence = replay.verify(row, at, decisions)
        diagnostics[row["event_id"]] = persistence
        verified_rows[row["event_id"]] = row
        sequence_inputs.append(owner.sequence_observation(row, at, persistence))

    expected = evaluate_rows(read_rows(ledger_raw), iso(start), iso(end), iso(replay.floor),
                             verify, owner.PROVENANCE_MUTABLE_FIELDS)
    if expected["status"] != "CORE_REPLAY_AT_OBSERVATION_ONLY" or packet["core"] != expected:
        raise ValueError("SHADOW_PROJECTION_MISMATCH")
    try:
        sequence = owner.sequence_census(sequence_inputs, history_truncated=expected["history_truncated"])
    except ValueError as exc:
        sequence = {"status": "BLOCKED_SOURCE_SEQUENCE_CONFLICT", "reason": str(exc),
                    "forecast_authority": False}
    from scripts.experiments.etf_absorption_transmission_v1 import pinned_settled_context
    latest = expected["latest_observation"]
    etf = pinned_settled_context(repo, latest["source_commit"], packet["checkout_sha"],
                                 clock(latest["observation_utc"]))
    from scripts.research.cn_mm_optional_source_context_v1 import forensics_context, leverage_context
    forensics = forensics_context(replay, latest["source_commit"], clock(latest["observation_utc"]))
    leverage = leverage_context(replay,verified_rows[latest["event_id"]],clock(latest["observation_utc"]))
    return {"persistence": diagnostics[latest["event_id"]],
            "sequence": sequence, "etf_context": etf, "forensics_context": forensics,
            "leverage_context": leverage}


def intelligence_projection(packet, diagnostics=None):
    """One shared feature-side vocabulary for MM and CN; no outcome fields.

    Only call with diagnostics returned by original-owner replay. Observation
    permission is not a forecast and is never a C2 activation credential.
    Preserve existing v1 immutable packet bytes and consumer compatibility.
    """
    base = {"contract": "CN_MM_SHARED_INTELLIGENCE_FEATURE_v1",
            "authority": "RESEARCH_ONLY_NON_CANONICAL",
            "status": "UNKNOWN", "packet_sha256": packet.get("packet_sha256"),
            "checkout_sha": packet.get("checkout_sha"), "freeze_sha256": packet.get("freeze_sha256"),
            "scientific_pit_eligible": False, "forecast_authority": False,
            "canonical_effect": False, "portfolio_execution": False,
            "independent_first_known_utc": None, "observation": None,
            "models": {"C0": "EXISTING_CN_UNCHANGED", "C1": "ORIGINAL_TASK2_A_OWNER",
                       "C2": {"status": "BLOCKED_PENDING_REVIEWED_ACTIVATION_AND_KNOWN_BY",
                              "observed_c06_permission": None, "issued": False}},
            "families": {}, "sequence": None}
    core = packet.get("core", {})
    if core.get("status") == "CORE_REPLAY_AT_OBSERVATION_ONLY" and diagnostics is not None:
        latest = core["latest_observation"]
        decisions = latest["decisions"]
        p, s = diagnostics["persistence"], diagnostics["sequence"]
        etf, liq = diagnostics["etf_context"], diagnostics["forensics_context"]
        leverage = diagnostics["leverage_context"]
        base.update(status="SOURCE_REPLAYED_OBSERVATION_ONLY",
                    observation={k: latest[k] for k in ("event_id","observation_utc","source_commit","provenance_sha256")})
        base["models"]["C2"]["observed_c06_permission"] = decisions["C06_BREADTH_BTCD"]
        base["families"] = {
            "ETHBTC_PERSISTENCE": {"status":"SOURCE_REPLAYED","permission":decisions["C01_ETHBTC"],
                "side":p["side"],"consecutive_hours":p["consecutive_same_side"],
                "left_censored":p["left_censored"],"stable_confirmation_utc":None},
            "BREADTH_SURVIVAL": {"status":"SOURCE_REPLAYED","permission":decisions["C02_BREADTH"]},
            "BTCD_PATH_RECLAIM": {"status":"SOURCE_REPLAYED","permission":decisions["C03_BTCD"]},
            "ETF_FLOW_QUALITY": {"status":etf["status"],"source_sha256":etf.get("source_sha256"),
                "session_date":etf.get("session_date"),"absorption_state":None},
            "LEVERAGE_CONTEXT": {"status":leverage["status"],"source_sha256":leverage.get("source_sha256"),
                "reset_state":None,"reclaim_state":None,"assets":leverage["assets"]},
            "LIQUIDATION_CLEARANCE": {"status":liq["status"],"source_sha256":liq.get("source_sha256"),
                "source_completeness_verified":False,"clearance_state":None},
        }
        base["sequence"] = {"status":s["status"],"observed_episode_n":s.get("observed_episode_n"),
                            "active_ordered_proxy_episode_n":s.get("active_ordered_proxy_episode_n"),
                            "original_sequence_equivalence":False}
        base["frozen_candidates"] = dict(decisions)
    base["feature_sha256"] = sha(canon(base))
    return base


def learning_checkout_at_cutoff(repo, head, cutoff):
    """Select the original first-parent repository snapshot, not today's data.

    Committer clocks are history proxies only. No independent source known-by
    or HTTP delivery is inferred. Do not select by author date or read files
    from the working tree. Reject clock inversion across the selected boundary.
    """
    if not re.fullmatch("[0-9a-f]{40}",head) or cutoff.utcoffset()!=timedelta(0):
        raise ValueError("LEARNING_CHECKOUT_OR_CUTOFF_INVALID")
    def run(*args):
        return subprocess.check_output(["git","-C",str(repo),*args],
                                       stderr=subprocess.DEVNULL,timeout=30).decode().strip()
    if run("rev-parse","--is-shallow-repository")!="false":
        raise ValueError("LEARNING_FULL_HISTORY_REQUIRED")
    run("merge-base","--is-ancestor",head,"HEAD")
    # --before alone can stop traversal at an out-of-order commit. Inspect the
    # actual contiguous first-parent chain, and reject a local clock inversion.
    lines=run("log","--first-parent","--format=%H%x09%cI",head).splitlines()
    selected=None
    for line in lines:
        commit,stamp=line.split("\t")
        at=datetime.fromisoformat(stamp).astimezone(timezone.utc)
        if selected is not None and at>cutoff:
            # An older parent stamped after the cutoff contaminates the
            # selected tree even if its child has an earlier clock.
            raise ValueError("LEARNING_FIRST_PARENT_CLOCK_INVERSION")
        if selected is None and at<=cutoff:
            selected={"checkout_sha":commit,"checkout_committer_utc":iso(at),
                      "source_cutoff_utc":iso(cutoff),
                      "clock_class":"FIRST_PARENT_COMMITTER_CLOCK_NOT_INDEPENDENT_KNOWN_BY"}
    if selected is None:
        raise ValueError("LEARNING_NO_CHECKOUT_BEFORE_CUTOFF")
    return selected


def calibration_intelligence(repo, freeze_file, freeze):
    """Existing MM calibration consumer, strictly separated feature/learning lanes.

    No API call, new writer, model promotion or change in calibration eligibility.
    Bound workload until a reviewed incremental owner exists. Late data block
    this optional learning lane rather than entering an earlier frozen context.
    """
    result = {"contract":"CN_MM_SHARED_INTELLIGENCE_CALIBRATION_v1",
              "authority":"RESEARCH_ONLY_NON_CANONICAL","status":"UNAVAILABLE",
              "forecast_authority":False,"canonical_effect":False,"automatic_weight_updates":False,
              "feature":None,"learning":{"status":"UNAVAILABLE"},"task2":{"status":"UNAVAILABLE"},
              "feature_uses_outcomes":False,"independent_first_known_utc":None}
    try:
        if repo.resolve()!=ROOT or Path.cwd().resolve()!=ROOT:
            raise ValueError("INTELLIGENCE_PINNED_REPO_REQUIRED")
        head = git("rev-parse","HEAD").decode().strip()
        _, raw, actual = freeze_identity(freeze_file, head, compare_worktree=True)
        if actual != freeze:
            raise ValueError("INTELLIGENCE_FREEZE_MISMATCH")
        packet = build_checkout(freeze_file, head)
        result["checkout_sha"] = head
        result["freeze_sha256"] = freeze["freeze_sha256"]
        result["freeze_file_sha256"] = sha(raw)
        if packet["core"]["status"] == "CORE_REPLAY_AT_OBSERVATION_ONLY":
            diagnostics = verify_packet_projection(packet, freeze, committed(LEDGER,head),
                         committed(BASE/"TRANSFORM_FREEZE_REGISTRY.json",head),repo=repo)
            result["feature"] = intelligence_projection(packet,diagnostics)
        else:
            result["feature"] = intelligence_projection(packet)
        result["status"] = "SHADOW_CONTEXT_ONLY"
    except (ValueError, TypeError, KeyError, AttributeError, RuntimeError, OSError, OverflowError,
            csv.Error, ImportError, subprocess.SubprocessError):
        result["reason"]="PINNED_FEATURE_CONTEXT_UNAVAILABLE"
        return result
    result.update(calibration_learning_at_cutoff(repo,head,freeze))
    # Keep full delta inventory in the deterministic audit, but do not send an
    # ever-growing list of event identifiers through the existing paid lane.
    inventory=result.get("incremental_inventory")
    if isinstance(inventory,dict) and "inventory_sha256" in inventory:
        result["incremental_inventory"] = {
            **{k:v for k,v in inventory.items() if not isinstance(v,list)},
            "identity_counts":{k:len(v) for k,v in inventory.items() if isinstance(v,list)},
            "identity_lists_omitted_from_calibration_context":True}
    result["context_sha256"] = sha(canon(result))
    return result


def calibration_learning_at_cutoff(repo,head,freeze):
    """Read both learning owners from one historical tree, independent of features."""
    result={"learning":{"status":"UNAVAILABLE"},"task2":{"status":"UNAVAILABLE"}}
    cutoff = clock(freeze["created_at_utc"])
    learning_pin = None
    try:
        learning_pin = learning_checkout_at_cutoff(repo,head,cutoff)
        result["learning_source_snapshot"] = learning_pin
        owner = load_owner()
        replay = owner.PinnedSourceReplay(repo,learning_pin["checkout_sha"])
        rows = read_rows(replay.ledger_raw)
        detail = read_rows(replay.read_blob(replay.checkout,replay.BASE+"/data/OUTCOME_DETAIL_LEDGER.csv"))
        if len(rows)>512:
            raise ValueError("LEARNING_REPLAY_BUDGET_EXCEEDED_INCREMENTAL_OWNER_REQUIRED")
        if any(clock(r["observation_timestamp_utc"])>cutoff for r in rows) or any(
                clock(d["matured_at_utc"])>cutoff for d in detail):
            raise ValueError("LEARNING_LATER_THAN_FROZEN_CALIBRATION_CUTOFF")
        from scripts.research.cn_mm_outcome_source_audit_v1 import audit_outcome_cohort
        audit = audit_outcome_cohort(replay,evaluate=True)
        research = audit["matched_research"]
        learning = {"status":research["status"],"verified_n":audit["verified_n"],
                    "rejected_n":audit["rejected_n"],"unavailable_n":audit["unmatured_or_unavailable_n"],
                    "verified_horizon_counts":audit["verified_horizon_counts"],
                    "source_cutoff_utc":iso(cutoff),"source_checkout_sha":replay.checkout,
                    "scientific_pit_eligible":False,
                    "forecast_authority":False,"automatic_weight_updates":False}
        if audit["status"]=="REPLAY_COMPLETE":
            learning["horizons"] = research["core_ablation"]["horizons"]
            learning["meta_learning"] = research["core_ablation"]["meta_learning"]
            learning["dependence"] = research["dependence"]
            learning["veto_magnitude"] = research["veto_magnitude"]
            learning["episode_opportunity"] = research["episode_opportunity"]
        result["learning"] = learning
    except (ValueError, TypeError, KeyError, AttributeError, RuntimeError, OSError, OverflowError,
            csv.Error, ImportError, subprocess.SubprocessError) as exc:
        result["learning"] = {"status":"UNAVAILABLE","reason":str(exc).split(":")[0][:120],
                              "forecast_authority":False}
    try:
        from scripts.research.cn_mm_task2_comparator_readback_v1 import audit_week
        if learning_pin is None:
            raise ValueError("TASK2_NO_CUTOFF_CHECKOUT")
        comparison = audit_week(load_owner().PinnedSourceReplay(repo,learning_pin["checkout_sha"]),
                                freeze["iso_year"],freeze["iso_week"])
        if clock(comparison["original_score"]["clock"])>cutoff:
            raise ValueError("TASK2_SCORE_AFTER_FROZEN_CUTOFF")
        result["task2"] = {k:comparison[k] for k in ("status","week","paired_n","interval_metrics",
                            "original_score","original_issue","original_cn_freeze","hourly_pin",
                            "scientific_pit_eligible","forecast_authority","c2_status")}
        result["task2"]["point_comparison"] = {k:v for k,v in comparison["point_comparison"].items() if k!="rows"}
    except (ValueError, TypeError, KeyError, AttributeError, RuntimeError, OSError, OverflowError,
            csv.Error, ImportError, subprocess.SubprocessError):
        result["task2"] = {"status":"UNAVAILABLE","reason":"ORIGINAL_SCORE_MISSING_LATE_OR_UNVERIFIED",
                           "forecast_authority":False}
    # Compare original previous-week tree to current cutoff tree, not mutable
    # LATEST or a self-asserted cached verdict. This is an actionable delta
    # inventory, not authorization to skip any full verification.
    try:
        if learning_pin is None: raise ValueError("DELTA_CURRENT_PIN_MISSING")
        previous=datetime.fromisocalendar(freeze["iso_year"],freeze["iso_week"],1)-timedelta(days=7)
        year,week,_=previous.isocalendar()
        path=Path(f"research/master_monday_preflight/frozen/{year}/W{week:02d}/WEEKLY_EVIDENCE_FREEZE.json")
        old=load_evidence_object(committed(path,learning_pin["checkout_sha"]))
        if (old["iso_year"],old["iso_week"])!=(year,week) or clock(old["created_at_utc"])>=cutoff:
            raise ValueError("DELTA_PREVIOUS_FREEZE_INVALID")
        before_pin=learning_checkout_at_cutoff(repo,learning_pin["checkout_sha"],clock(old["created_at_utc"]))
        owner=load_owner()
        before=owner.PinnedSourceReplay(repo,before_pin["checkout_sha"])
        after=owner.PinnedSourceReplay(repo,learning_pin["checkout_sha"])
        if before.floor!=after.floor or before.registry_raw!=after.registry_raw:
            raise ValueError("DELTA_OWNER_POLICY_CHANGED")
        detail_path=before.BASE+"/data/OUTCOME_DETAIL_LEDGER.csv"
        from scripts.research.cn_mm_outcome_source_audit_v1 import immutable_delta_inventory
        result["incremental_inventory"]=immutable_delta_inventory(read_rows(before.ledger_raw),
            read_rows(before.read_blob(before.checkout,detail_path)),read_rows(after.ledger_raw),
            read_rows(after.read_blob(after.checkout,detail_path)),owner.PROVENANCE_MUTABLE_FIELDS)
        result["incremental_source_snapshots"]={"previous":before_pin,"current":learning_pin}
    except (ValueError, TypeError, KeyError, AttributeError, RuntimeError, OSError, OverflowError,
            csv.Error, ImportError, subprocess.SubprocessError) as exc:
        result["incremental_inventory"]={"status":"UNAVAILABLE","reason":str(exc).split(":")[0][:120],
                                         "prior_verdict_reuse_authorized":False}
    return result


def calibration_feature_binding(context, freeze):
    """Small durable reference for existing MM machine package, no new writer."""
    missing = {"contract":"CN_MM_CALIBRATION_FEATURE_BINDING_v1","status":"UNAVAILABLE",
               "forecast_authority":False}
    try:
        intelligence = context["cn_mm_shared_intelligence"]
        feature = intelligence["feature"]
        if intelligence["status"]!="SHADOW_CONTEXT_ONLY" or not isinstance(feature,dict):
            return missing
        if (sha(canon({k:v for k,v in context.items() if k!="context_hash"}))!=context["context_hash"] or
                sha(canon({k:v for k,v in intelligence.items() if k!="context_sha256"}))!=intelligence["context_sha256"] or
                sha(canon({k:v for k,v in feature.items() if k!="feature_sha256"}))!=feature["feature_sha256"] or
                intelligence["freeze_sha256"]!=freeze["freeze_sha256"] or
                feature["freeze_sha256"]!=freeze["freeze_sha256"] or
                feature["checkout_sha"]!=intelligence["checkout_sha"] or
                intelligence["feature_uses_outcomes"] is not False or
                feature["forecast_authority"] is not False or
                feature["models"]["C2"]["issued"] is not False or
                feature["canonical_effect"] is not False):
            return {**missing,"reason":"CONTEXT_OR_FEATURE_BINDING_INVALID"}
        return {"contract":missing["contract"],"status":"BOUND_CALIBRATION_FEATURE",
                "forecast_authority":False,"freeze_sha256":freeze["freeze_sha256"],
                "checkout_sha":feature["checkout_sha"],"packet_sha256":feature["packet_sha256"],
                "feature_sha256":feature["feature_sha256"],"context_sha256":context["context_hash"],
                "intelligence_context_sha256":intelligence["context_sha256"]}
    except (ValueError,TypeError,KeyError,AttributeError,OverflowError):
        return missing


def calibration_learning_binding(context,freeze,api_receipt,api_status):
    """Durable linkage to actual supplied calibration inputs, not model use.

    The gateway receipt hashes the ENTIRE context (including context_hash).
    The context's own self-digest excludes context_hash. Do not compare the
    two different digests or infer that the model used a particular feature.
    """
    result={"contract":"CN_MM_CALIBRATION_LEARNING_BINDING_v1","status":"UNAVAILABLE",
            "api_input_status":"UNATTESTED","model_utilization_verified":False,
            "scientific_pit_eligible":False,"forecast_authority":False,
            "automatic_weight_updates":False}
    feature=calibration_feature_binding(context,freeze)
    if feature["status"]!="BOUND_CALIBRATION_FEATURE":
        return result
    try:
        intelligence=context["cn_mm_shared_intelligence"]
        learning=intelligence["learning"]
        task2=intelligence["task2"]
        inventory=intelligence.get("incremental_inventory",{})
        whole_hash=sha(canon(context))
        api_input_status="UNATTESTED"
        if isinstance(api_receipt,dict) and api_receipt:
            if (api_receipt.get("contract")!="API_AGENT_RECEIPT_v3" or
                api_receipt.get("task")!="WEEKLY_CALIBRATION_SHADOW" or
                api_receipt.get("context_hash")!=whole_hash):
                api_input_status="RECEIPT_CONTEXT_MISMATCH"
            elif (api_status=="success" and api_receipt.get("status")=="PASS" and
                  isinstance(api_receipt.get("response_id"),str) and api_receipt["response_id"] and
                  api_receipt.get("untrusted_input_envelope") is True):
                api_input_status="MATCHED_GATEWAY_INPUT_RECEIPT"
            else:
                api_input_status="MATCHED_CONTEXT_NO_SUCCESSFUL_API_DELIVERY"
        result.update(status="BOUND_RESEARCH_CONTEXT",
            api_input_status=api_input_status,context_sha256=context["context_hash"],
            gateway_context_sha256=whole_hash,
            intelligence_context_sha256=intelligence["context_sha256"],
            feature_sha256=feature["feature_sha256"],freeze_sha256=feature["freeze_sha256"],
            learning_sha256=sha(canon(learning)),task2_sha256=sha(canon(task2)),
            incremental_inventory_sha256=inventory.get("inventory_sha256"),
            learning_status=learning["status"],task2_status=task2["status"],
            verified_outcome_n=learning.get("verified_n"),task2_paired_n=task2.get("paired_n"),
            source_checkout_sha=learning.get("source_checkout_sha"),
            source_cutoff_utc=learning.get("source_cutoff_utc"))
        result["binding_sha256"]=sha(canon(result))
        return result
    except (ValueError,TypeError,KeyError,AttributeError,OverflowError):
        return {"contract":result["contract"],"status":"UNAVAILABLE",
                "api_input_status":"UNATTESTED","model_utilization_verified":False,
                "scientific_pit_eligible":False,"forecast_authority":False,
                "automatic_weight_updates":False}


def compare_calibration_feature(machine, pointer, feature):
    """A new binding must match independently replayed CN feature bytes.

    Older MM packages remain explicit UNATTESTED, not falsely paired.
    The machine and pointer use the existing package self-hash convention.
    """
    binding = machine.get("cn_mm_calibration_feature_binding")
    if not isinstance(binding,dict) or binding.get("status")=="UNAVAILABLE":
        return "UNATTESTED_MM_CALIBRATION_BINDING"
    try:
        if (machine["package_sha256"]!=pointer["machine_package_sha256"] or
                sha(canon({k:v for k,v in machine.items() if k!="package_sha256"}))!=machine["package_sha256"] or
                machine["freeze_sha256"]!=pointer["freeze_sha256"] or
                binding["contract"]!="CN_MM_CALIBRATION_FEATURE_BINDING_v1" or
                binding["status"]!="BOUND_CALIBRATION_FEATURE" or
                binding["forecast_authority"] is not False or
                binding["context_sha256"]!=machine["context_hash"] or
                any(binding[k]!=feature[k] for k in ("freeze_sha256","checkout_sha","packet_sha256","feature_sha256"))):
            return "MM_CALIBRATION_FEATURE_MISMATCH"
        return "MATCHED_MM_CALIBRATION_FEATURE"
    except (ValueError,TypeError,KeyError,AttributeError,OverflowError):
        return "MM_CALIBRATION_FEATURE_MISMATCH"


def read_calibration_feature_binding(repo, pointer, feature, read_committed, *, include_learning=False):
    def result(status, learning=None):
        return (status,learning) if include_learning else status
    if not pointer.get("machine_package_path"):
        return result("UNATTESTED_MM_CALIBRATION_BINDING")
    try:
        expected = Path(f"research/api_agent/outputs/weekly/{pointer['iso_year']}/W{pointer['iso_week']:02d}/MASTER_MONDAY_MACHINE_PACKAGE.json")
        if Path(pointer["machine_package_path"])!=expected:
            return result("MM_CALIBRATION_FEATURE_MISMATCH")
        raw=(repo/expected).read_bytes()
        if raw!=read_committed("show",f"HEAD:{expected.as_posix()}"):
            return result("MM_CALIBRATION_FEATURE_MISMATCH")
        machine=load_evidence_object(raw)
        status=compare_calibration_feature(machine,pointer,feature)
        learning=None
        if status=="MATCHED_MM_CALIBRATION_FEATURE" and include_learning:
            binding=machine.get("cn_mm_calibration_learning_binding")
            if isinstance(binding,dict) and binding.get("status")=="BOUND_RESEARCH_CONTEXT":
                if (sha(canon({k:v for k,v in binding.items() if k!="binding_sha256"}))==binding.get("binding_sha256") and
                    binding.get("contract")=="CN_MM_CALIBRATION_LEARNING_BINDING_v1" and
                    binding.get("context_sha256")==machine["context_hash"] and
                    binding.get("intelligence_context_sha256")==machine["cn_mm_calibration_feature_binding"]["intelligence_context_sha256"] and
                    binding.get("freeze_sha256")==feature["freeze_sha256"] and
                    binding.get("feature_sha256")==feature["feature_sha256"] and
                    all(binding.get(k) is False for k in ("model_utilization_verified","scientific_pit_eligible","forecast_authority","automatic_weight_updates"))):
                    # No outcome values in CN feature or forecast. Only the
                    # delivery metadata from the separately bound MM lane.
                    learning={k:binding.get(k) for k in ("status","binding_sha256","api_input_status",
                                "learning_status","task2_status","verified_outcome_n","task2_paired_n",
                                "model_utilization_verified","scientific_pit_eligible","forecast_authority")}
        return result(status,learning)
    except (ValueError,TypeError,KeyError,AttributeError,OSError,subprocess.SubprocessError):
        return result("MM_CALIBRATION_FEATURE_MISMATCH")


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
                                 committed(BASE / "TRANSFORM_FREEZE_REGISTRY.json", head), repo=ROOT)
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
        diagnostics = verify_packet_projection(packet, load_evidence_object(frozen),
                                 run("show", f"{head}:{LEDGER.as_posix()}"),
                                 run("show", f"{head}:{(BASE / 'TRANSFORM_FREEZE_REGISTRY.json').as_posix()}"), repo=repo)
        latest = core["latest_observation"]
        decisions = latest["decisions"]
        if set(decisions) != set(CORE) or any(type(v) is not bool for v in decisions.values()):
            raise ValueError("SHADOW_DECISIONS_INVALID")
        shared = intelligence_projection(packet,diagnostics)
        binding_status,learning_delivery = read_calibration_feature_binding(repo,mm_pointer,shared,run,include_learning=True)
        return {**result, "status": "CONSUMED_SHADOW_ONLY", "reason": None,
                "packet_sha256": digest, "packet_file_sha256": sha(raw), "checkout_sha": head,
                "observation_utc": latest["observation_utc"],
                "shadow_candidate_decision": decisions[CORE[-1]],
                "candidate_id": CORE[-1], "target_semantics": packet["target_semantics"],
                "observation_only": True, "edge_established": False,
                "persistence_diagnostic": diagnostics["persistence"],
                "sequence_diagnostic": diagnostics["sequence"],
                "etf_context": diagnostics["etf_context"],
                "forensics_context": diagnostics["forensics_context"],
                "leverage_context": diagnostics["leverage_context"],
                "shared_intelligence_feature": shared if binding_status!="MM_CALIBRATION_FEATURE_MISMATCH" else None,
                "shared_feature_binding_status": binding_status,
                "mm_learning_delivery":learning_delivery}
    except (ValueError, TypeError, KeyError, AttributeError, RuntimeError, OSError, OverflowError,
            csv.Error, ImportError, subprocess.SubprocessError):
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
