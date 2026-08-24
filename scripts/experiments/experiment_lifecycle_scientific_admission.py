#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import experiment_lifecycle as base

UTC = timezone.utc
ADMISSION_CONTRACT = "EXPERIMENT_SCIENTIFIC_ADMISSION_v1"
ADMISSION_REGISTRY_CONTRACT = "EXPERIMENT_SCIENTIFIC_ADMISSION_REGISTRY_v1"
QUALIFIED = "QUALIFIED_FOR_FORWARD_TEST"


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def canonical_metric(path: str | None) -> str | None:
    if not path:
        return None
    raw = str(path).strip()
    for prefix in (
        "latest_capture.market_metrics.",
        "latest_capture.",
        "market_metrics.",
        "market.",
    ):
        if raw.startswith(prefix):
            raw = raw[len(prefix):]
            break
    try:
        return base.canonical_path(raw)
    except Exception:
        return raw


def semantic_spec(spec: dict[str, Any]) -> dict[str, Any]:
    components = []
    for item in spec.get("components", []):
        components.append({"metric_path": canonical_metric(item.get("metric_path")), "operator": item.get("operator"), "threshold": item.get("threshold")})
    components.sort(key=lambda row: (str(row["metric_path"]), str(row["operator"]), str(row["threshold"])))
    return {
        "kind": spec.get("kind"),
        "components": components,
        "target_metric_path": canonical_metric(spec.get("target_metric_path")),
        "target_direction": spec.get("target_direction"),
        "target_threshold_pct": spec.get("target_threshold_pct"),
        "target_range_lower_pct": spec.get("target_range_lower_pct"),
        "target_range_upper_pct": spec.get("target_range_upper_pct"),
        "horizon_days": spec.get("horizon_days"),
        "regime_dependency": spec.get("regime_dependency"),
    }


def default_plan(spec: dict[str, Any]) -> dict[str, Any]:
    kind = str(spec.get("kind") or "")
    components = spec.get("components") or []
    component_paths = [canonical_metric(row.get("metric_path")) for row in components]
    if kind == "SENSOR_COMBINATION":
        problem = "Determine whether this sensor conjunction explains a measurable information gap or forecast error that the existing stack does not already explain."
        baseline = ["CURRENT_FRAMEWORK_WITHOUT_CANDIDATE", "BEST_SINGLE_COMPONENT_CONTROL", "DETERMINISTIC_PLACEBO"]
        claim = "The conjunction adds prospective information beyond the strongest component and current framework baseline."
    elif kind == "FORECAST_TEST":
        problem = "Determine whether this frozen forecast claim adds prospective decision information beyond the existing Director baseline and no-action control."
        baseline = ["CURRENT_FRAMEWORK_WITHOUT_CANDIDATE", "ALWAYS_WAIT", "DETERMINISTIC_PLACEBO"]
        claim = "The forecast improves prospective directional, range or timing evidence after false-positive and false-negative cost."
    elif kind == "SEQUENCE_TEST":
        problem = "Determine whether the proposed ordering or lead-lag sequence adds timely information beyond current sequence logic."
        baseline = ["CURRENT_SEQUENCE_BASELINE", "LAGGED_CONTROL", "DETERMINISTIC_PLACEBO"]
        claim = "The sequence adds actionable lead time or discrimination beyond current sequence evidence."
    else:
        problem = "Determine whether the proposed data-quality hypothesis detects a failure class not already covered by current validation."
        baseline = ["CURRENT_DATA_QUALITY_BASELINE", "NULL_CONTROL"]
        claim = "The test improves detection or resilience without unacceptable complexity or false alarms."
    return {
        "problem_to_solve": problem,
        "existing_capability_overlap": component_paths,
        "baseline": baseline,
        "incremental_value_claim": claim,
        "expected_lead_lag": "FIXED_HORIZON_AS_SPECIFIED",
        "regime_dependency": spec.get("regime_dependency"),
        "success_criteria": [
            "candidate beats the relevant baseline on prospective independent windows",
            "candidate beats the strongest single-component control when a multi-sensor claim is made",
            "negative or placebo controls do not reproduce the claimed edge",
            "point-in-time and temporal-leakage checks remain clean",
            "observed value remains worthwhile after complexity tax",
        ],
        "failure_criteria": [
            "no incremental value versus baseline",
            "placebo or negative control performs similarly",
            "material temporal leakage or hindsight dependence",
            "semantic redundancy with an already registered candidate",
            "unstable or unexplained regime dependence",
            "false-positive or false-negative cost outweighs benefit",
        ],
        "kill_criteria": [
            "semantic duplicate without distinct information claim",
            "non-falsifiable or unmappable specification",
            "persistent redundancy after prospective comparison",
            "leakage, hindsight fit or unsupported point-in-time lineage",
            "complexity, fragility or maintenance cost exceeds measured incremental value",
        ],
        "negative_controls": ["DETERMINISTIC_PLACEBO", "LAGGED_OR_TIME_SHIFTED_CONTROL", "BEST_SINGLE_COMPONENT_CONTROL"],
        "adversarial_checks": ["POINT_IN_TIME_AVAILABILITY", "TEMPORAL_LEAKAGE", "REDUNDANCY_COLLINEARITY", "REGIME_STRATIFICATION", "LEAD_LAG_TIMELINESS", "FALSE_POSITIVE_FALSE_NEGATIVE_COST"],
        "complexity_tax": {
            "maintenance": "MEASURE",
            "dependencies": "CURRENT_STACK_ONLY_UNLESS_SEPARATELY_APPROVED",
            "api_or_token_cost": "MEASURE",
            "latency": "MEASURE",
            "source_fragility": "MEASURE",
            "security_privacy": "NO_NEW_AUTHORITY",
            "governance_burden": "MEASURE",
            "correlated_failure_risk": "MEASURE",
        },
        "authority_ceiling": "RESEARCH_ONLY_NON_CANONICAL",
        "prospective_evidence_required": kind != "DATA_QUALITY_TEST",
    }


def qualification_status(spec: dict[str, Any], duplicate_of: str | None) -> tuple[str, list[str]]:
    if duplicate_of:
        return "SEMANTIC_DUPLICATE_KEEP_SHADOW", [f"semantic_duplicate_of={duplicate_of}"]
    kind = spec.get("kind")
    components = spec.get("components") or []
    if kind == "FORECAST_TEST" and spec.get("target_unit_contract_version") != base.UNIT_CONTRACT_VERSION:
        return "TARGET_UNIT_QUARANTINED", ["forecast_target_unit_contract_not_v2"]
    if kind != "FORECAST_TEST" and not components:
        return "WAITING_FOR_MAPPING", ["no_machine_mappable_components"]
    if kind == "SENSOR_COMBINATION" and len(components) < 2:
        return "KEEP_SHADOW_INSUFFICIENT_COMBINATION", ["sensor_combination_requires_two_or_more_components"]
    if spec.get("target_direction") != "NONE" and not spec.get("target_metric_path"):
        return "BLOCKED_INVALID_TARGET", ["target_metric_path_missing"]
    return QUALIFIED, []


def admission_record(candidate: dict[str, Any], duplicate_of: str | None, now: str, historical: bool) -> dict[str, Any]:
    spec = candidate["spec"]
    semantic = semantic_spec(spec)
    status, reasons = qualification_status(spec, duplicate_of)
    return {
        "contract": ADMISSION_CONTRACT,
        "candidate_id": candidate["candidate_id"],
        "candidate_created_at_utc": candidate.get("created_at_utc"),
        "admission_frozen_at_utc": now,
        "historical_candidate_requalification": historical,
        "no_retroactive_rescore": True,
        "semantic_fingerprint": digest(semantic),
        "semantic_spec": semantic,
        "status": status,
        "status_reasons": reasons,
        "plan": default_plan(spec),
        "method_reference": "06_RESEARCH_LAB/protocols/README.md",
        "admission_rule_reference": "06_RESEARCH_LAB/protocols/SHADOW_IDEA_ADMISSION_RULE_v1.md",
        "authority": {"canonical_effect": False, "portfolio_execution": False, "framework_state_change": False, "threshold_change": False, "weight_change": False, "automatic_promotion": False},
    }


def load_admissions(root: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for _, value in base.jsons(root, ADMISSION_CONTRACT):
        cid = value.get("candidate_id")
        if cid:
            rows[str(cid)] = value
    return rows


def build_admission_registry(admissions: dict[str, dict[str, Any]], now: str) -> dict[str, Any]:
    counts: dict[str, int] = {}
    rows = []
    for cid, value in sorted(admissions.items()):
        status = str(value.get("status") or "UNKNOWN")
        counts[status] = counts.get(status, 0) + 1
        rows.append({
            "candidate_id": cid,
            "status": status,
            "semantic_fingerprint": value.get("semantic_fingerprint"),
            "historical_candidate_requalification": bool(value.get("historical_candidate_requalification")),
            "duplicate_of": next((r.split("=", 1)[1] for r in value.get("status_reasons", []) if str(r).startswith("semantic_duplicate_of=")), None),
        })
    return {
        "contract": ADMISSION_REGISTRY_CONTRACT,
        "generated_at_utc": now,
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "candidate_count": len(rows),
        "status_counts": counts,
        "candidates": rows,
        "rules": {"new_forward_execution_requires": QUALIFIED, "historical_hypotheses_are_not_rewritten": True, "no_retroactive_rescore": True, "semantic_deduplication": True, "method_reference": "06_RESEARCH_LAB/protocols/README.md"},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    for name in (
        "repo-root", "daily-output", "daily-context", "daily-receipt", "candidate-root", "observation-root", "dispatch-root", "forecast-root", "outcome-root", "receipt-root", "registry-output", "manifest-output", "admission-root", "admission-registry-output",
    ):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--legacy-sensor-catalog", type=Path)
    parser.add_argument("--repository", default="Donh91/Investering-Framework-Archive-v1")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--max-new-forecasts", type=int, default=5)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    output = base.read(args.daily_output)
    context = base.read(args.daily_context)
    receipt = base.read(args.daily_receipt)
    latest = ((context.get("latest_capture") or {}).get("market_metrics") or {})
    previous = ((context.get("previous_capture") or {}).get("market_metrics") or {})
    captured = (context.get("latest_capture") or {}).get("captured_at_utc") or base.iso(datetime.now(UTC))
    when = base.dt(captured)
    now = base.iso(datetime.now(UTC))
    source = {"daily_output_sha256": base.sha(output), "daily_context_sha256": base.sha(context), "daily_receipt_sha256": base.sha(receipt), "source_run_id": (context.get("latest_capture") or {}).get("run_id")}

    raw = [item for item in output.get("experiment_candidates", []) if isinstance(item, dict)] + base.legacy(args.legacy_sensor_catalog) + base.emergent_pairs(context, latest)
    rejected = []
    for item in output.get("forecast_candidates", []):
        if not isinstance(item, dict):
            continue
        mapped = base.from_forecast(item, latest)
        if mapped:
            raw.append(mapped)
        else:
            rejected.append({"title": f"Prospective {item.get('metric_path')}", "error": "explicit_target_unit_contract_required"})

    existing_candidates = {value["candidate_id"]: value for _, value in base.jsons(args.candidate_root, "EXPERIMENT_CANDIDATE_v1")}
    new_ids: set[str] = set()
    for item in raw:
        try:
            spec = base.normalize(item)
            candidate_id = "EC-" + base.sha(base.identity_spec(spec))[:20]
            value = {
                "contract": "EXPERIMENT_CANDIDATE_v1",
                "candidate_id": candidate_id,
                "created_at_utc": captured,
                "registered_at_utc": now,
                "target_unit_contract_version": spec.get("target_unit_contract_version"),
                "spec": spec,
                "source": {**source, "daily_output_path": base.rel(root, args.daily_output), "daily_context_path": base.rel(root, args.daily_context), "daily_receipt_path": base.rel(root, args.daily_receipt)},
                "dormancy_policy": {"automatic_age_expiry": False, "retain_until": "FALSIFIED_OR_GOVERNANCE_CLOSED"},
                "authority": {"canonical_promotion": False, "framework_state_change": False, "model_weight_change": False, "portfolio_action": False},
            }
            path = args.candidate_root / when.strftime("%Y/%m") / f"{candidate_id}.json"
            if base.write_new(path, value):
                new_ids.add(candidate_id)
                existing_candidates[candidate_id] = value
        except Exception as exc:
            rejected.append({"title": str(item.get("title") or "UNKNOWN"), "error": str(exc)})

    admissions = load_admissions(args.admission_root)
    semantic_owner: dict[str, str] = {}
    all_candidates = sorted(existing_candidates.values(), key=lambda row: (str(row.get("created_at_utc") or ""), str(row.get("candidate_id") or "")))
    for candidate in all_candidates:
        cid = candidate["candidate_id"]
        existing = admissions.get(cid)
        semantic_id = digest(semantic_spec(candidate["spec"]))
        owner = semantic_owner.get(semantic_id)
        if existing is None:
            record = admission_record(candidate, owner, now, historical=cid not in new_ids)
            path = args.admission_root / str(candidate.get("created_at_utc") or now)[:7].replace("-", "/") / f"{cid}.json"
            base.write_new(path, record)
            admissions[cid] = record
        if owner is None and admissions[cid].get("status") != "SEMANTIC_DUPLICATE_KEEP_SHADOW":
            semantic_owner[semantic_id] = cid

    admission_registry = build_admission_registry(admissions, now)
    args.admission_registry_output.parent.mkdir(parents=True, exist_ok=True)
    args.admission_registry_output.write_bytes(canonical(admission_registry))

    new_forecasts = 0
    dispatch = 0
    candidate_rows = base.jsons(args.candidate_root, "EXPERIMENT_CANDIDATE_v1")
    candidate_rows.sort(key=lambda item: (0 if item[1].get("spec", {}).get("kind") == "FORECAST_TEST" else 1, str(item[1].get("candidate_id") or "")))
    for spec_path, candidate in candidate_rows:
        spec = candidate["spec"]
        admission = admissions[candidate["candidate_id"]]
        admitted = admission.get("status") == QUALIFIED
        legacy_forecast_unit_ambiguous = spec.get("kind") == "FORECAST_TEST" and spec.get("target_unit_contract_version") != base.UNIT_CONTRACT_VERSION
        results = [base.evaluate(item, latest, previous) for item in spec["components"]]
        mapping = not spec["components"] and spec["kind"] != "FORECAST_TEST"
        missing = any(item["matched"] is None for item in results)
        fired = admitted and not legacy_forecast_unit_ambiguous and not mapping and ((not spec["components"] and spec["kind"] == "FORECAST_TEST") or (results and not missing and all(item["matched"] for item in results)))
        status = "TARGET_UNIT_QUARANTINED" if legacy_forecast_unit_ambiguous else "SCIENTIFIC_ADMISSION_BLOCKED" if not admitted and not mapping else "WAITING_FOR_MAPPING" if mapping else "WAITING_FOR_DATA" if missing else "FIRED_NO_TARGET" if fired and spec["target_direction"] == "NONE" else "FIRED" if fired else "OBSERVED_NOT_FIRED"
        observation_id = "EO-" + base.sha({"candidate_id": candidate["candidate_id"], "captured": captured, "source": source})[:20]
        observation = {"contract": "EXPERIMENT_OBSERVATION_v1", "observation_id": observation_id, "candidate_id": candidate["candidate_id"], "observed_at_utc": captured, "evaluation_status": status, "component_results": results, "scientific_admission_status": admission.get("status"), "scientific_admission_sha256": digest(admission), "source": source, "authority": "SHADOW_ONLY"}
        observation_path = args.observation_root / candidate["candidate_id"] / f"{observation_id}.json"
        is_new = False if mapping and candidate["candidate_id"] not in new_ids else base.write_new(observation_path, observation)

        forecast_id = None
        start = base.at(latest, spec.get("target_metric_path") or "") if spec.get("target_metric_path") else None
        if admitted and fired and spec["target_direction"] != "NONE" and isinstance(start, (int, float)) and new_forecasts < args.max_new_forecasts:
            window = base.sha({"run": source["source_run_id"], "captured": captured})[:20]
            forecast_id = "EXP-FC-" + base.sha({"candidate_id": candidate["candidate_id"], "window": window})[:20]
            frozen = {
                "contract": "FROZEN_FORECAST_v1", "unit_contract_version": base.UNIT_CONTRACT_VERSION, "forecast_id": forecast_id, "source_candidate_id": candidate["candidate_id"], "source_observation_id": observation_id,
                "frozen_at_utc": captured, "outcome_due_utc": base.iso(when + timedelta(days=spec["horizon_days"])), "metric_path": base.canonical_path(spec["target_metric_path"]), "metric_path_root": base.CAPTURE_DOCUMENT_ROOT,
                "direction": spec["target_direction"], "start_value": float(start), "target_mode": "PCT_MOVE" if spec["target_direction"] in {"UP", "DOWN"} else "PCT_RANGE", "threshold_pct": spec["target_threshold_pct"], "range_lower_pct": spec["target_range_lower_pct"], "range_upper_pct": spec["target_range_upper_pct"],
                "causal_event_window_id": window, "experimental_only": True,
                "scientific_admission": {"contract": ADMISSION_CONTRACT, "status": admission.get("status"), "record_sha256": digest(admission), "semantic_fingerprint": admission.get("semantic_fingerprint"), "method_reference": admission.get("method_reference")},
                "controls": {"always_wait": "ALWAYS_WAIT", "single_component_specs": spec["components"], "deterministic_placebo_direction": base.placebo(window), "control_freeze_time_utc": captured, "required_future_reviews": ["REDUNDANCY_COLLINEARITY", "NEGATIVE_CONTROL", "REGIME_STRATIFICATION", "LEAD_LAG_TIMELINESS", "FALSE_POSITIVE_FALSE_NEGATIVE_COST"]},
                "authority": {"portfolio_action": False, "framework_state_change": False, "model_weight_change": False, "canonical_promotion": False},
            }
            if base.write_new(args.forecast_root / when.strftime("%Y/%m") / f"{forecast_id}.json", frozen):
                new_forecasts += 1

        if admitted and is_new and (candidate["candidate_id"] in new_ids or fired):
            request_id = "ER-" + base.sha({"candidate_id": candidate["candidate_id"], "observation_id": observation_id})[:20]
            request = {"contract": "EXPERIMENT_REQUEST_v1", "request_id": request_id, "candidate_id": candidate["candidate_id"], "created_at_utc": now, "request_type": "SENSOR_FIRE_REPLICATION" if fired else "SPEC_REGISTRATION", "spec": spec, "embedded_observation": observation, "local_frozen_forecast_id": forecast_id, "scientific_admission_status": admission.get("status"), "scientific_admission_sha256": digest(admission), "source_spec_path": base.rel(root, spec_path), "source_spec_sha256": base.sha(candidate), "authority": {"automatic_trade": False, "canonical_promotion": False, "portfolio_action": False}}
            dispatch += int(base.write_new(args.dispatch_root / when.strftime("%Y/%m/%d") / f"{request_id}.json", request))

    reg = base.registry(args.candidate_root, args.observation_root, args.forecast_root, args.outcome_root, args.receipt_root, now)
    admission_by_id = {row["candidate_id"]: row for row in admission_registry["candidates"]}
    for row in reg.get("candidates", []):
        adm = admission_by_id.get(row["candidate_id"])
        row["scientific_admission_status"] = adm.get("status") if adm else "UNAVAILABLE"
        row["semantic_fingerprint"] = adm.get("semantic_fingerprint") if adm else None
    reg.setdefault("rules", {})["new_forward_execution_requires"] = QUALIFIED
    reg["scientific_admission_registry_path"] = base.rel(root, args.admission_registry_output)
    args.registry_output.parent.mkdir(parents=True, exist_ok=True)
    args.registry_output.write_bytes(base.canon(reg))

    requests = []
    for path, value in base.jsons(args.dispatch_root, "EXPERIMENT_REQUEST_v1"):
        if value.get("scientific_admission_status") != QUALIFIED:
            continue
        relative_path = base.rel(root, path)
        requests.append({"request_id": value["request_id"], "candidate_id": value["candidate_id"], "path": relative_path, "sha256": base.sha(value), "raw_url": f"https://raw.githubusercontent.com/{args.repository}/{args.branch}/{relative_path}"})
    manifest = {"contract": "EXPERIMENT_DISPATCH_MANIFEST_v2_SCIENTIFIC_ADMISSION", "generated_at_utc": now, "source_repository": args.repository, "source_branch": args.branch, "request_count": len(requests), "requests": sorted(requests, key=lambda item: item["request_id"]), "admission_required": QUALIFIED, "authority": "SHADOW_ONLY_CROSS_REPO_DISPATCH"}
    args.manifest_output.parent.mkdir(parents=True, exist_ok=True)
    args.manifest_output.write_bytes(base.canon(manifest))
    print(json.dumps({"candidate_count": reg["candidate_count"], "new_candidate_count": len(new_ids), "new_forecasts": new_forecasts, "dispatch_created": dispatch, "admission_status_counts": admission_registry["status_counts"], "rejected": rejected}, sort_keys=True))


if __name__ == "__main__":
    main()
