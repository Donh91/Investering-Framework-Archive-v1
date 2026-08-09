from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from .rotation import RotationEvidence, classify_rotation

CONTRACT = "SHADOW_SIMPLIFICATION_DUAL_RUN_v2"
MODE = "BLINDED_PAIRED_EVIDENCE_COLLECTION"
COVERAGE_CONTRACT = "PROSPECTIVE_B2_COVERAGE_VALIDITY_v2"
VALIDITY_CONTRACT = "PROSPECTIVE_B2_COUNTERFACTUAL_IDENTIFIABILITY_v1"
WINDOW_SECONDS = 259200
FULL_PROFILE = "FULL_STACK"
REDUCED_PROFILE = "REDUCED_EXECUTION_STACK"
PRIMARY_LANES = ("ROTATION_PERMISSION", "REBUY_STATE", "TRIM_EXIT_STATE")

REDUCED_SENSOR_IDS = (
    "BREADTH_ADVANCE_RATIO","BREADTH_OUTPERFORM_BTC","BTC_DOMINANCE","BTC_ETF_FLOW",
    "BTC_FUNDING","BTC_OPEN_INTEREST","BTC_SPOT_STRUCTURE","BTC_VOLATILITY_DRAWDOWN",
    "DIRECT_DERIVED_PARITY","ETF_SESSION_COMPLETENESS","ETHBTC_DIRECT","ETH_ETF_FLOW",
    "ETH_FUNDING","ETH_OPEN_INTEREST","ETH_SPOT_STRUCTURE","ETH_VOLATILITY_DRAWDOWN",
    "SOURCE_FRESHNESS","VENUE_PARITY",
)
FORBIDDEN = {
    "state_agreement_rate","agreement_rate","disagreement_rate","divergence_rate",
    "false_transition_count","false_transition_comparison","missed_warning_count",
    "missed_warning_comparison","forecast_score","forecast_score_comparison",
    "stack_rank","stack_ranking","winner",
}
ROTATION_MAP = {
    "NO_SIGNAL":"NO_ROTATION",
    "ETH_RELATIVE_STRENGTH_CANDIDATE":"NO_ROTATION",
    "ETH_RELATIVE_STRENGTH_CONFIRMED":"ETH_RELATIVE_STRENGTH",
    "SELECTIVE_LARGE_CAP_ROTATION_CANDIDATE":"ETH_RELATIVE_STRENGTH",
    "SELECTIVE_LARGE_CAP_ROTATION_CONFIRMED":"SELECTIVE_LARGE_CAP",
    "BROAD_ALT_ROTATION_CANDIDATE":"SELECTIVE_LARGE_CAP",
    "BROAD_ALT_ROTATION_CONFIRMED":"BROAD_ALT",
}

# R1 scientific-validity freeze. This is provenance metadata only. It does not
# grant, remove, or modify any market/policy authority.
CURRENT_DEPENDENCY_MAP: dict[str, dict[str, Any]] = {
    "ROTATION_PERMISSION": {
        "structural_identifiability": "DEPENDENCY_MAP_UNPROVEN",
        "dependency_provenance_status": "UNPROVEN",
        "candidate_full_only_dependencies": ["BREADTH_ABOVE_MA50"],
        "proven_consumed_full_only_dependencies": [],
        "reason": "DEPENDENCY_MAP_UNPROVEN",
        "note": (
            "BREADTH_ABOVE_MA50 is Full-only with VETO_ONLY authority, but current repository provenance "
            "does not prove a deterministic mapping from that sensor into any consumed RotationEvidence field."
        ),
    },
    "REBUY_STATE": {
        "structural_identifiability": "NATIVE_OUTPUT_UNAVAILABLE_FOR_PROSPECTIVE_COUNTERFACTUAL",
        "dependency_provenance_status": "NATIVE_OUTPUT_UNAVAILABLE",
        "candidate_full_only_dependencies": [],
        "proven_consumed_full_only_dependencies": [],
        "reason": "NATIVE_OUTPUT_UNAVAILABLE_FOR_PROSPECTIVE_COUNTERFACTUAL",
        "note": "No current deterministic prospective REBUY_LOCK output producer is proven by the audited runtime.",
    },
    "TRIM_EXIT_STATE": {
        "structural_identifiability": "NATIVE_OUTPUT_UNAVAILABLE_FOR_PROSPECTIVE_COUNTERFACTUAL",
        "dependency_provenance_status": "NATIVE_OUTPUT_UNAVAILABLE",
        "candidate_full_only_dependencies": [],
        "proven_consumed_full_only_dependencies": [],
        "reason": "NATIVE_OUTPUT_UNAVAILABLE_FOR_PROSPECTIVE_COUNTERFACTUAL",
        "note": "No current deterministic prospective TRIM_NO_TRIM output producer is proven by the audited runtime.",
    },
}


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def obj_sha(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


DEPENDENCY_MAP_HASH = obj_sha(CURRENT_DEPENDENCY_MAP)


def utc(value: str) -> datetime:
    out = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if out.tzinfo is None:
        raise ValueError("timezone-aware UTC required")
    return out.astimezone(timezone.utc)


def fixed_window_id(value: str) -> int:
    return int(utc(value).timestamp()) // WINDOW_SECONDS


def _no_comparison(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if str(key) in FORBIDDEN:
                raise ValueError(f"comparison key forbidden: {key}")
            _no_comparison(nested)
    elif isinstance(value, list):
        for nested in value:
            _no_comparison(nested)


def load_profiles(registry: Mapping[str, Any]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    full = tuple(str(row[0]) for row in registry.get("rows", []))
    reduced = tuple(registry.get("stack_profiles", {}).get(REDUCED_PROFILE, ()))
    if len(full) != 32 or len(set(full)) != 32:
        raise ValueError("FULL_STACK identity drift")
    if len(reduced) != 18 or tuple(sorted(reduced)) != tuple(sorted(REDUCED_SENSOR_IDS)):
        raise ValueError("REDUCED_EXECUTION_STACK identity drift")
    return full, reduced


def _qa(capture: Mapping[str, Any]) -> bool:
    return (
        capture.get("status") == "COMPLETE"
        and capture.get("anchor_core_passed") == capture.get("anchor_core_planned")
        and int(capture.get("anchor_core_planned", 0)) > 0
    )


def rotation_output(capture: Mapping[str, Any], profile_id: str) -> tuple[str | None, dict[str, Any]]:
    by_profile = capture.get("profile_native_rotation_evidence")
    explicit = by_profile.get(profile_id) if isinstance(by_profile, Mapping) else None
    if isinstance(explicit, Mapping):
        try:
            evidence = RotationEvidence(
                bool(explicit["direct_ethbtc_available"]), str(explicit["ethbtc_authority_status"]),
                explicit.get("ethbtc_settled_close"), int(explicit["ethbtc_positive_settled_run"]),
                int(explicit["eth_leads_btc_sessions"]), explicit.get("large_cap_breadth"),
                explicit.get("broad_alt_breadth"), explicit.get("beta_neutral_alt_return_20d"),
                explicit.get("btc_dominance_change_5d"), explicit.get("flow_confirmation"),
                bool(explicit["source_qa_pass"]),
            )
        except (KeyError, TypeError, ValueError):
            return None, {"adapter_mode":"EXPLICIT_PROFILE_NATIVE_EVIDENCE_INVALID","imputation":False}
        meta = {"adapter_mode":"EXPLICIT_PROFILE_NATIVE_EVIDENCE","imputation":False}
    else:
        # Gate 0-F admitted the current native fail-closed path. The two zeros below
        # are evaluator-control sentinels, not sensor observations. Missingness remains explicit.
        evidence = RotationEvidence(False, "UNAVAILABLE", None, 0, 0, None, None, None, None, None, _qa(capture))
        meta = {
            "adapter_mode":"NATIVE_FAIL_CLOSED","imputation":False,
            "evaluator_control_sentinels":{"ethbtc_positive_settled_run":0,"eth_leads_btc_sessions":0},
            "missing_inputs":[
                "ETHBTC_DIRECT_SETTLED_CLOSE","ETHBTC_POSITIVE_SETTLED_RUN","ETH_LEADS_BTC_SESSIONS",
                "LARGE_CAP_BREADTH","BROAD_ALT_BREADTH","BETA_NEUTRAL_ALT_RETURN_20D",
                "BTC_DOMINANCE_CHANGE_5D","FLOW_CONFIRMATION",
            ],
        }
    result = classify_rotation(evidence)
    if result.get("status") != "PASS":
        return None, {**meta, "native_evaluator_status":result.get("status")}
    output = ROTATION_MAP.get(str(result["label"]))
    return output, {
        **meta, "native_evaluator_status":"PASS", "native_evaluator_label":result["label"],
        "evaluator":"backtest_engine/rotation.py::classify_rotation",
    }


def explicit_policy(capture: Mapping[str, Any], profile_id: str, family: str, allowed: Iterable[str]) -> tuple[str | None, str]:
    rows = capture.get("profile_native_policy_outputs")
    profile = rows.get(profile_id) if isinstance(rows, Mapping) else None
    if not isinstance(profile, Mapping) or family not in profile:
        return None, "POLICY_OUTPUT_UNAVAILABLE"
    value = str(profile[family])
    if value not in set(allowed):
        return None, "NATIVE_POLICY_VALUE_INVALID"
    return value, "EXPLICIT_PROFILE_NATIVE_OUTPUT"


def missingness(capture: Mapping[str, Any], sensors: Iterable[str]) -> dict[str, str]:
    available: set[str] = set()
    if _qa(capture):
        available.add("SOURCE_FRESHNESS")
    breadth = capture.get("market_metrics", {}).get("breadth", {})
    if isinstance(breadth, Mapping) and breadth.get("constituent_count"):
        available.add("BREADTH_ADVANCE_RATIO")
    explicit = capture.get("sensor_values")
    if isinstance(explicit, Mapping):
        for sensor, row in explicit.items():
            if isinstance(row, Mapping) and row.get("mapping_class") in {"EXACT","MECHANICALLY_EQUIVALENT"} and row.get("value") is not None:
                available.add(str(sensor))
    return {str(s):("AVAILABLE" if str(s) in available else "UNAVAILABLE") for s in sensors}


def make_child(
    capture: Mapping[str, Any], capture_path: Path, capture_hash: str, run_id: str,
    profile_id: str, sensors: tuple[str, ...], sensor_hash: str, policy_registry: Mapping[str, Any],
    policy_hash: str, rotation_hash: str, crosswalk_hash: str,
) -> dict[str, Any]:
    rotation, rmeta = rotation_output(capture, profile_id)
    families = policy_registry["families"]
    rebuy, rsource = explicit_policy(capture, profile_id, "REBUY_LOCK", families["REBUY_LOCK"]["decision_values"])
    trim, tsource = explicit_policy(capture, profile_id, "TRIM_NO_TRIM", families["TRIM_NO_TRIM"]["decision_values"])
    lanes = {
        "ROTATION_PERMISSION":{"output":rotation,"eligibility":rotation is not None,"exclusion_reason":None if rotation is not None else "POLICY_OUTPUT_UNAVAILABLE","native_family":"ROTATION_PERMISSION","native_source":rmeta},
        "REBUY_STATE":{"output":rebuy,"eligibility":rebuy is not None,"exclusion_reason":None if rebuy is not None else "POLICY_OUTPUT_UNAVAILABLE","native_family":"REBUY_LOCK","native_source":rsource,"crosswalk_identity":"GATE0E_REBUY_STATE_TO_REBUY_LOCK_v1"},
        "TRIM_EXIT_STATE":{"output":trim,"eligibility":trim is not None,"exclusion_reason":None if trim is not None else "POLICY_OUTPUT_UNAVAILABLE","native_family":"TRIM_NO_TRIM","native_source":tsource,"crosswalk_identity":"GATE0E_TRIM_EXIT_STATE_TO_TRIM_NO_TRIM_v1"},
    }
    child = {
        "schema_version":"BLINDED_DUAL_RUN_PROFILE_CHILD_v2","contract":CONTRACT,"mode":MODE,
        "authority":{"shadow_only":True,"portfolio_action":False,"canonical_state_change":False,"automatic_promotion":False},
        "run_id":run_id,"snapshot_utc":capture["captured_at_utc"],"capture_path":str(capture_path),"capture_hash":capture_hash,
        "profile_id":profile_id,"profile_sensor_count":len(sensors),"profile_hash":obj_sha(list(sensors)),
        "sensor_registry_hash":sensor_hash,"policy_registry_hash":policy_hash,
        "evaluator_hashes":{"rotation":rotation_hash,"gate0e_crosswalk":crosswalk_hash},
        "missingness_by_sensor":missingness(capture, sensors),
        "source_failures":[o.get("owner_id") for o in capture.get("owners",[]) if isinstance(o,Mapping) and o.get("status") not in {"PASS","DISABLED"}],
        "policy_lanes":lanes,
    }
    _no_comparison(child)
    return child


def _lane_validity(children: Mapping[str, Mapping[str, Any]], lane: str) -> dict[str, Any]:
    full = children[FULL_PROFILE]["policy_lanes"][lane]
    reduced = children[REDUCED_PROFILE]["policy_lanes"][lane]
    pair_valid = bool(full["eligibility"] and reduced["eligibility"])
    frozen = CURRENT_DEPENDENCY_MAP[lane]

    reason = frozen["reason"]
    if not pair_valid:
        reason = (
            "NATIVE_OUTPUT_UNAVAILABLE_FOR_PROSPECTIVE_COUNTERFACTUAL"
            if lane in {"REBUY_STATE", "TRIM_EXIT_STATE"}
            else "PAIR_EXECUTION_INVALID"
        )
    elif lane == "ROTATION_PERMISSION":
        modes = {
            full.get("native_source", {}).get("adapter_mode"),
            reduced.get("native_source", {}).get("adapter_mode"),
        }
        if "NATIVE_FAIL_CLOSED" in modes:
            reason = "NO_PROFILE_SPECIFIC_COUNTERFACTUAL_EVIDENCE"

    return {
        "pair_execution_valid": pair_valid,
        "identifying_opportunity": False,
        "identifying_exclusion_reason": reason,
        "structural_identifiability": frozen["structural_identifiability"],
        "dependency_provenance_status": frozen["dependency_provenance_status"],
        "dependency_map_hash": DEPENDENCY_MAP_HASH,
        "validity_contract": VALIDITY_CONTRACT,
    }


def make_receipt(capture: Mapping[str, Any], capture_path: Path, capture_hash: str, run_id: str, children: Mapping[str, Mapping[str, Any]], child_paths: Mapping[str, str]) -> dict[str, Any]:
    full, reduced = children[FULL_PROFILE], children[REDUCED_PROFILE]
    if full["snapshot_utc"] != reduced["snapshot_utc"] or full["capture_hash"] != reduced["capture_hash"]:
        raise ValueError("asymmetric pair")
    eligibility = {}
    validity = {}
    for lane in PRIMARY_LANES:
        f, r = full["policy_lanes"][lane], reduced["policy_lanes"][lane]
        eligibility[lane] = {
            "eligible_for_both":bool(f["eligibility"] and r["eligibility"]),
            "full_eligible":bool(f["eligibility"]),"reduced_eligible":bool(r["eligibility"]),
            "full_exclusion_reason":f["exclusion_reason"],"reduced_exclusion_reason":r["exclusion_reason"],
        }
        validity[lane] = _lane_validity(children, lane)
    receipt = {
        "schema_version":"BLINDED_PAIRED_EVIDENCE_RECEIPT_v3","contract":CONTRACT,"mode":MODE,
        "coverage_validity_contract":COVERAGE_CONTRACT,
        "authority":{"passive_collection_only":True,"b2_analysis_authorized":False,"portfolio_action":False,"automatic_promotion":False},
        "run_id":run_id,"snapshot_utc":capture["captured_at_utc"],"capture_path":str(capture_path),"capture_hash":capture_hash,
        "profiles":{
            FULL_PROFILE:{"path":child_paths[FULL_PROFILE],"artifact_hash":obj_sha(full),"profile_hash":full["profile_hash"]},
            REDUCED_PROFILE:{"path":child_paths[REDUCED_PROFILE],"artifact_hash":obj_sha(reduced),"profile_hash":reduced["profile_hash"]},
        },
        "excluded_profiles":{"LEGACY_MINIMAL":"EXCLUDED_UNRECOVERABLE"},
        "lane_eligibility":eligibility,
        "lane_validity":validity,
        "fixed_72h_window_id":fixed_window_id(capture["captured_at_utc"]),
        "missingness_by_profile":{FULL_PROFILE:full["missingness_by_sensor"],REDUCED_PROFILE:reduced["missingness_by_sensor"]},
        "source_failure_counts":{FULL_PROFILE:len(full["source_failures"]),REDUCED_PROFILE:len(reduced["source_failures"])},
    }
    _no_comparison(receipt)
    return receipt


def load_pair_receipts(root: Path) -> list[dict[str, Any]]:
    if not root.exists():
        return []
    rows = []
    for path in sorted(root.rglob("PAIR_RECEIPT.json")):
        row = json.loads(path.read_text())
        if row.get("schema_version") in {"BLINDED_PAIRED_EVIDENCE_RECEIPT_v2", "BLINDED_PAIRED_EVIDENCE_RECEIPT_v3"}:
            rows.append(row)
    return rows


def _receipt_validity(row: Mapping[str, Any], lane: str) -> dict[str, Any]:
    current = row.get("lane_validity", {}).get(lane)
    if isinstance(current, Mapping):
        return dict(current)
    legacy_pair = row.get("lane_eligibility", {}).get(lane, {}).get("eligible_for_both") is True
    return {
        "pair_execution_valid": legacy_pair,
        "identifying_opportunity": False,
        "identifying_exclusion_reason": "PRE_R1_B2_VALIDITY_UNPROVEN",
        "structural_identifiability": "PRE_R1_B2_VALIDITY_UNPROVEN",
        "dependency_provenance_status": "PRE_R1_B2_VALIDITY_UNPROVEN",
        "validity_contract": "PRE_R1_NONE",
    }


def _span_weeks(ts: list[str]) -> float:
    return (utc(ts[-1])-utc(ts[0])).total_seconds()/(7*86400) if ts else 0.0


def _window_partial(windows: list[int], now: datetime) -> bool:
    return now.timestamp() < (windows[-1]+1)*WINDOW_SECONDS if windows else False


def coverage_progress(receipts: Iterable[Mapping[str, Any]], *, now_utc: str | None = None) -> dict[str, Any]:
    rows = list(receipts)
    per_lane = {}
    now = utc(now_utc) if now_utc else datetime.now(timezone.utc)
    for lane in PRIMARY_LANES:
        pair_rows = [r for r in rows if _receipt_validity(r, lane).get("pair_execution_valid") is True]
        identifying_rows = [r for r in rows if _receipt_validity(r, lane).get("identifying_opportunity") is True]
        pair_ts = sorted(str(r["snapshot_utc"]) for r in pair_rows)
        identifying_ts = sorted(str(r["snapshot_utc"]) for r in identifying_rows)
        pair_windows = sorted({fixed_window_id(t) for t in pair_ts})
        identifying_windows = sorted({fixed_window_id(t) for t in identifying_ts})
        pair_weeks = _span_weeks(pair_ts)
        identifying_weeks = _span_weeks(identifying_ts)
        identifying_count = len(identifying_windows)
        band = (
            "COVERAGE_READY" if identifying_count >= 30 and identifying_weeks >= 12
            else "WINDOW_COUNT_MET_TIME_NOT_MET" if identifying_count >= 30
            else "MATURING_NOT_READY" if identifying_count >= 10
            else "EARLY_ACCUMULATION"
        )
        current_meta = CURRENT_DEPENDENCY_MAP[lane]
        observed_meta = [_receipt_validity(r, lane) for r in rows if isinstance(r.get("lane_validity"), Mapping)]
        structural = observed_meta[-1].get("structural_identifiability") if observed_meta else current_meta["structural_identifiability"]
        provenance = observed_meta[-1].get("dependency_provenance_status") if observed_meta else current_meta["dependency_provenance_status"]
        per_lane[lane] = {
            # Legacy technical aliases retained for compatibility. They are NOT B2-readiness evidence.
            "eligible_row_count":len(pair_rows),
            "occupied_fixed_72h_windows":len(pair_windows),
            "occupied_window_ids":pair_windows,
            "elapsed_prospective_weeks":pair_weeks,
            "pair_execution_valid_rows":len(pair_rows),
            "identifying_opportunity_rows":len(identifying_rows),
            "occupied_pair_execution_windows":len(pair_windows),
            "occupied_pair_execution_window_ids":pair_windows,
            "occupied_identifying_windows":identifying_count,
            "occupied_identifying_window_ids":identifying_windows,
            "elapsed_pair_execution_weeks":pair_weeks,
            "elapsed_identifying_weeks":identifying_weeks,
            "structural_identifiability":structural,
            "dependency_provenance_status":provenance,
            "coverage_band":band,
            "b2_coverage_ready":identifying_count >= 30 and identifying_weeks >= 12,
            "right_edge_partial_window":_window_partial(identifying_windows, now),
            "pair_execution_right_edge_partial_window":_window_partial(pair_windows, now),
        }
    out = {
        "schema_version":"PROSPECTIVE_B2_COVERAGE_MONITOR_v2","coverage_contract":COVERAGE_CONTRACT,
        "validity_contract":VALIDITY_CONTRACT,"dependency_map_hash":DEPENDENCY_MAP_HASH,
        "window_seconds":WINDOW_SECONDS,"window_formula":"floor(unix_timestamp_seconds / 259200)",
        "paired_receipt_count":len(rows),"per_lane":per_lane,"b2_analysis_authorized":False,
        "readiness_basis":"IDENTIFYING_OPPORTUNITY_ONLY",
        "legacy_pre_r1_rows":"PRE_R1_B2_VALIDITY_UNPROVEN_UNLESS_SEPARATELY_VALIDATED",
    }
    _no_comparison(out)
    return out


def collect_from_latest_capture(
    *, capture_root: Path, output_root: Path, sensor_registry_path: Path, policy_registry_path: Path,
    rotation_evaluator_path: Path, crosswalk_contract_path: Path,
) -> dict[str, Any]:
    pointer = json.loads((capture_root/"LATEST.json").read_text())
    rel = Path(str(pointer["path"]))
    capture_path = capture_root/(rel.relative_to("captures") if rel.parts and rel.parts[0] == "captures" else rel)
    capture = json.loads(capture_path.read_text())
    if capture.get("contract") != "DAILY_LIVE_ANCHOR_INDEX_v3" or capture.get("authority") != "SHADOW_OBSERVATION_ONLY":
        raise ValueError("current-owner capture contract/authority drift")
    if capture.get("framework_state_change") is not False or capture.get("portfolio_action") is not False:
        raise ValueError("forbidden capture authority")
    capture_hash = file_sha(capture_path)
    sensors, policy = json.loads(sensor_registry_path.read_text()), json.loads(policy_registry_path.read_text())
    full_sensors, reduced_sensors = load_profiles(sensors)
    sensor_hash, policy_hash = file_sha(sensor_registry_path), file_sha(policy_registry_path)
    rotation_hash, crosswalk_hash = file_sha(rotation_evaluator_path), file_sha(crosswalk_contract_path)
    run_id = "B2P-"+hashlib.sha256((capture_hash+sensor_hash+policy_hash+rotation_hash+crosswalk_hash+VALIDITY_CONTRACT+DEPENDENCY_MAP_HASH).encode()).hexdigest()[:20]
    stamp = utc(capture["captured_at_utc"])
    run_dir = output_root/"runs"/f"{stamp:%Y}"/f"{stamp:%m}"/f"{stamp:%d}"/run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    paths = {FULL_PROFILE:str(run_dir/"FULL_STACK.json"),REDUCED_PROFILE:str(run_dir/"REDUCED_EXECUTION_STACK.json")}
    children = {
        FULL_PROFILE:make_child(capture,capture_path,capture_hash,run_id,FULL_PROFILE,full_sensors,sensor_hash,policy,policy_hash,rotation_hash,crosswalk_hash),
        REDUCED_PROFILE:make_child(capture,capture_path,capture_hash,run_id,REDUCED_PROFILE,reduced_sensors,sensor_hash,policy,policy_hash,rotation_hash,crosswalk_hash),
    }
    for profile, child in children.items():
        Path(paths[profile]).write_text(canonical(child)+"\n")
    receipt = make_receipt(capture,capture_path,capture_hash,run_id,children,paths)
    receipt_path = run_dir/"PAIR_RECEIPT.json"
    receipt_path.write_text(canonical(receipt)+"\n")
    coverage = coverage_progress(load_pair_receipts(output_root/"runs"), now_utc=capture["captured_at_utc"])
    coverage_path = output_root/"COVERAGE_LATEST.json"
    coverage_path.write_text(canonical(coverage)+"\n")
    return {"run_id":run_id,"pair_receipt":str(receipt_path),"coverage":str(coverage_path)}
