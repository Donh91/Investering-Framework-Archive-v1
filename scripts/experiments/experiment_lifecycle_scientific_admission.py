#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

import experiment_lifecycle as base

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from forecast_settlement_contract import (  # noqa: E402
    SETTLEMENT_EXACT_TARGET_TIME_V1,
    supports_exact_price_settlement,
)

UTC = timezone.utc
ADMISSION_CONTRACT = "EXPERIMENT_SCIENTIFIC_ADMISSION_v1"
ADMISSION_REGISTRY_CONTRACT = "EXPERIMENT_SCIENTIFIC_ADMISSION_REGISTRY_v1"
QUALIFIED = "QUALIFIED_FOR_FORWARD_TEST"
# A persistent sensor condition is ONE fire episode. Replicating every observation of the same
# episode created ~4 identical requests per candidate per day (63,219 requests for 319 candidates
# by 2026-11-14) and broke the storage-health gate. Only an episode START is dispatched.
FIRED_STATES = {"FIRED", "FIRED_NO_TARGET"}
# Missing/unknown observations are not observed evidence that a fire episode has ended.
# Only an observed false condition can re-arm a previously firing candidate.
DEFINITIVE_EPISODE_STATES = FIRED_STATES | {"OBSERVED_NOT_FIRED"}
DISPATCH_LISTING_RULE = "PENDING_UNRECEIPTED_QUALIFIED_ONLY"


def prior_observation_status(observation_root: Path, candidate_id: str, before_utc: str) -> str | None:
    """Last DEFINITIVE earlier episode state; unknown/missing observations do not re-arm."""
    best: tuple[str, str] | None = None
    folder = observation_root / candidate_id
    for path in folder.glob("*.json") if folder.is_dir() else []:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(value, dict) or value.get("contract") != "EXPERIMENT_OBSERVATION_v1":
            continue
        # A no-dispatch HOLD observation must not consume the paid-path episode start.
        if isinstance(value.get("source"), dict) and value["source"].get("mode") == EXISTING_ONLY_MODE:
            continue
        observed = str(value.get("observed_at_utc") or "")
        status = str(value.get("evaluation_status") or "")
        if status not in DEFINITIVE_EPISODE_STATES:
            continue  # WAITING_FOR_DATA, mapping gaps and invalid/unknown states are not a false signal
        if observed and observed < before_utc and (best is None or observed > best[0]):
            best = (observed, status)
    return best[1] if best else None


ALLOCATION_POLICY_VERSION = "FORECAST_SLOT_ALLOCATION_v2_LEAST_SERVED_30D_LRS_ID_WINDOW_CAP"
ALLOCATION_LOOKBACK_DAYS = 30


class AllocationIntegrityError(ValueError):
    """Frozen-forecast history cannot be trusted for allocation; issue no new forecasts this run."""


def _utc_key(value: Any) -> str:
    """Normalised UTC sort key. Naive or unparseable times are rejected, never read as host-local time."""
    if not isinstance(value, str) or not value:
        raise AllocationIntegrityError("allocation_time_missing")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise AllocationIntegrityError("allocation_time_unparseable") from None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise AllocationIntegrityError("allocation_time_timezone_naive")
    try:
        return parsed.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    except (OverflowError, ValueError):
        raise AllocationIntegrityError("allocation_time_unrepresentable") from None


CANONICAL_CAPTURE_CLOCK = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
SUPPORTED_CAPTURE_YEARS = range(2000, 9000)  # keeps lookback/horizon arithmetic representable
FORECAST_IDENTITY_KEYS = ("forecast_id", "source_candidate_id", "causal_event_window_id", "frozen_at_utc")


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise AllocationIntegrityError("forecast_file_duplicate_key")
        value[key] = item
    return value


def _reject_constant(_: str) -> Any:
    raise AllocationIntegrityError("forecast_file_non_finite_number")


def _finite_float(text: str) -> float:
    number = float(text)
    if not math.isfinite(number):  # e.g. 1e999 overflows to infinity
        raise AllocationIntegrityError("forecast_file_non_finite_number")
    return number


def strict_json_loads(text: str) -> Any:
    """json.loads that rejects duplicate keys at any depth and NaN/Infinity/overflowing numbers."""
    return json.loads(text, object_pairs_hook=_reject_duplicate_keys, parse_constant=_reject_constant, parse_float=_finite_float)


def canonical_capture_clock(value: Any) -> bool:
    """True only for the exact capture spelling every historical window was hashed from
    (``YYYY-MM-DDTHH:MM:SSZ``). Other spellings of the same instant would hash to a different window."""
    if not isinstance(value, str) or not CANONICAL_CAPTURE_CLOCK.fullmatch(value):
        return False
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return False
    return parsed.year in SUPPORTED_CAPTURE_YEARS


def capture_clock_parseable(value: Any) -> bool:
    """Exception-safe check that ``base.dt`` can turn the capture into a UTC instant."""
    try:
        base.dt(value)
    except (ValueError, OverflowError, TypeError):
        return False
    return True


def causal_event_window(run_id: str, captured: str) -> str:
    """Unchanged historical derivation; callers must pass a canonical capture clock and a run id."""
    return base.sha({"run": run_id, "captured": captured})[:20]


def canonical_forecast_id(candidate_id: str, window_id: str) -> str:
    return "EXP-FC-" + base.sha({"candidate_id": candidate_id, "window": window_id})[:20]


def unique_frozen_forecasts(forecast_root: Path) -> dict[str, dict[str, Any]]:
    """Strict read of the frozen-forecast store, keyed by immutable forecast_id.

    Stricter than ``base.registry``: files are parsed with duplicate-key and non-finite-number
    rejection; duplicate paths for one forecast_id must be byte-identical (counted once), anything else
    is a conflict. Also: every ``*.json`` file must parse to an object
    with a string ``contract`` (files with another contract and no forecast identity keys are known
    non-forecast files and are ignored; forecast-shaped files with another contract are unclassifiable;
    non-JSON files are ignored); every FROZEN_FORECAST_v1 row must carry source_candidate_id,
    forecast_id, causal_event_window_id and a timezone-aware frozen_at_utc; its forecast_id must be
    the canonical ID for (candidate, window); and one (candidate, window) may hold only one forecast_id.
    Any violation raises AllocationIntegrityError. Skipping such a row instead would make its candidate
    look under-served and could undercount a window's occupied slots.
    """
    rows: dict[str, dict[str, Any]] = {}
    raw_bytes: dict[str, bytes] = {}
    pair_owner: dict[tuple[str, str], str] = {}
    paths = sorted(p for p in forecast_root.rglob("*.json") if p.is_file()) if forecast_root.exists() else []
    for path in paths:
        try:
            data = path.read_bytes()
            value = strict_json_loads(data.decode("utf-8"))
        except AllocationIntegrityError:
            raise
        except (OSError, UnicodeDecodeError, ValueError, RecursionError):
            raise AllocationIntegrityError("forecast_file_unreadable") from None
        if not isinstance(value, dict) or not isinstance(value.get("contract"), str):
            raise AllocationIntegrityError("forecast_file_unclassifiable")
        if value["contract"] != "FROZEN_FORECAST_v1":
            if any(key in value for key in FORECAST_IDENTITY_KEYS):  # forecast-shaped but not a supported forecast contract
                raise AllocationIntegrityError("forecast_file_unclassifiable")
            continue
        cid, fid, window = (value.get(k) for k in ("source_candidate_id", "forecast_id", "causal_event_window_id"))
        if not all(isinstance(item, str) and item for item in (cid, fid, window)):
            raise AllocationIntegrityError("forecast_identity_missing")
        if fid in rows:
            # exact bytes, not parsed-dict equality (which would equate 1, 1.0 and true or key reorders)
            if raw_bytes[fid] != data:
                raise AllocationIntegrityError("forecast_id_ownership_or_content_conflict")
            continue
        _utc_key(value.get("frozen_at_utc"))
        if fid != canonical_forecast_id(cid, window):
            if pair_owner.get((cid, window)) not in (None, fid):
                raise AllocationIntegrityError("forecast_candidate_window_conflict")
            raise AllocationIntegrityError("forecast_id_not_canonical_for_candidate_window")
        if pair_owner.setdefault((cid, window), fid) != fid:
            raise AllocationIntegrityError("forecast_candidate_window_conflict")
        rows[fid] = value
        raw_bytes[fid] = data
    return rows


def _forecast_rows(source: Path | dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return source if isinstance(source, dict) else unique_frozen_forecasts(source)


def forecast_service_history(source: Path | dict[str, dict[str, Any]], before_utc: str, lookback_days: int = ALLOCATION_LOOKBACK_DAYS) -> dict[str, tuple[int, str]]:
    """(unique forecast count, latest freeze time) per candidate over forecasts frozen in
    ``[before_utc - lookback_days, before_utc)``.

    Outcome-blind by construction: only identity and freeze-time fields of frozen forecasts are read,
    never outcome, hit/miss or score records. Excluding the current and later windows keeps a replay
    of the same capture identical to the original allocation. The bounded lookback stops a candidate
    with a long service history from being locked out forever by newer, never-served candidates.
    """
    cutoff = _utc_key(before_utc)
    floor = _utc_key((datetime.fromisoformat(cutoff.replace("Z", "+00:00")) - timedelta(days=lookback_days)).isoformat())
    history: dict[str, tuple[int, str]] = {}
    for value in _forecast_rows(source).values():
        cid, frozen = str(value["source_candidate_id"]), _utc_key(value.get("frozen_at_utc"))
        if floor <= frozen < cutoff:
            count, last = history.get(cid, (0, ""))
            history[cid] = (count + 1, max(last, frozen))
    return history


def window_occupancy(source: Path | dict[str, dict[str, Any]], window_id: str) -> tuple[set[str], dict[str, str]]:
    """(unique forecast_ids frozen in this causal event window, candidate_id -> forecast_id membership).

    The cap is charged against the unique-ID set; membership only decides which candidates already
    hold a row. A (candidate, window) with two IDs never gets this far: the strict store read rejects it.
    """
    ids: set[str] = set()
    members: dict[str, str] = {}
    for fid, value in sorted(_forecast_rows(source).items()):
        if value.get("causal_event_window_id") != window_id:
            continue
        ids.add(fid)
        cid = str(value["source_candidate_id"])
        if members.setdefault(cid, fid) != fid:
            raise AllocationIntegrityError("forecast_candidate_window_conflict")
    return ids, members


def forecast_allocation_key(candidate: dict[str, Any], history: dict[str, tuple[int, str]]) -> tuple[int, int, str, str]:
    """Deterministic least-served order: kind priority, fewest recent slots, least recently served, then ID."""
    cid = str(candidate.get("candidate_id") or "")
    count, last = history.get(cid, (0, ""))
    return (0 if candidate.get("spec", {}).get("kind") == "FORECAST_TEST" else 1, count, last, cid)


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def apply_exact_settlement_contract(frozen: dict[str, Any]) -> dict[str, Any]:
    """Freeze exact settlement only for newly created supported price forecasts."""
    metric_path = str(frozen.get("metric_path") or "")
    if not supports_exact_price_settlement(metric_path):
        return frozen
    existing = frozen.get("settlement_contract_version")
    if existing not in (None, SETTLEMENT_EXACT_TARGET_TIME_V1):
        raise ValueError(f"SETTLEMENT_CONTRACT_CONFLICT:{existing}")
    frozen["settlement_contract_version"] = SETTLEMENT_EXACT_TARGET_TIME_V1
    frozen["settlement_activation_semantics"] = "FROZEN_AT_CREATION_PROSPECTIVE_ONLY"
    return frozen


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


# --- #1557 value-free proposal slot census -------------------------------------------------
# One immutable, derived census per authenticated Daily Director source batch. It enumerates every
# raw proposal slot BEFORE the producer filters, maps or deduplicates, and keeps only metadata
# (array/index, slot hash, origin family, outcome, candidate id). It is engineering observability:
# coverage is PARTIAL, independent N and the global denominator stay null, nothing is promoted and
# the existing candidate/admission/forecast/dispatch writes are unchanged.
PROPOSAL_SLOT_CENSUS_CONTRACT = "EXPERIMENT_PROPOSAL_SLOT_CENSUS_v1"
SLOT_ORIGIN_FAMILIES = ("model_experiment", "legacy_sensor", "emergent_pair", "model_forecast")
SLOT_OUTCOMES = ("malformed", "mapping_rejected", "normalized_new", "normalized_existing_duplicate", "error")
# Receipt status -> attempts whose output survived into DAILY_DIRECTOR_OUTPUT.json.
SURVIVING_OUTPUT_BY_STATUS = {"PASS": 1, "API_OUTPUT_INVALID": 0, "COST_EXCEEDED": 0, "SKIPPED_OWNER_RUN_ALREADY_ANALYZED": 0, "SKIPPED_NO_DELTA": 0}
# daily-director-shadow.yml "Write zero-cost skipped output": no model call, response_id null and no
# declared forecast count. Such a batch is SKIPPED: neither INVALID nor complete.
WORKFLOW_SKIP_STATUSES = frozenset({"SKIPPED_NO_DELTA", "SKIPPED_OWNER_RUN_ALREADY_ANALYZED"})
UNKNOWN = "UNKNOWN"
SHA256_HEX = re.compile(r"[0-9a-f]{64}")
# The fixed ValueError codes raised by base.component/base.normalize. Anything else is stored as the
# exception type name only: exception text may echo proposal values.
SLOT_ERROR_CODES = frozenset({"invalid_component", "threshold_required", "invalid_kind_or_direction", "invalid_identity_or_horizon", "invalid_directional_target", "invalid_range_target"})
CENSUS_INTERNAL_ERROR = "CENSUS_INTERNAL_ERROR"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _error_code(exc: Exception) -> str:
    """Allowlisted fixed codes only; never exception text."""
    text = str(exc)
    return text if text in SLOT_ERROR_CODES else type(exc).__name__


def _census_id(hashes: dict[str, str | None]) -> str:
    return "PSC-" + _sha256_bytes(":".join(str(hashes[k]) for k in ("output_sha256", "context_sha256", "receipt_sha256")).encode())[:20]


def _parse(data: bytes | None, name: str, reasons: list[str]) -> Any:
    if data is None:
        reasons.append(f"{name}_file_missing")
        return None
    try:
        return json.loads(data)
    except ValueError:
        reasons.append(f"{name}_not_json")
        return None


def _container(output: Any, name: str) -> tuple[str, list[tuple[int | None, Any]]]:
    if not isinstance(output, dict) or name not in output:
        return "ABSENT", []
    value = output[name]
    if isinstance(value, list):
        return "LIST", list(enumerate(value))
    return "NOT_A_LIST", [(None, value)]


def _classify_slot(item: Any, family: str, latest: dict[str, Any], existing: dict[str, dict[str, Any]], source: dict[str, Any], seen: set[str]) -> dict[str, Any]:
    if not isinstance(item, dict):
        return {"outcome": "malformed"}
    try:
        if family == "model_forecast":
            mapped = base.from_forecast(item, latest)
            if not mapped:
                return {"outcome": "mapping_rejected", "reason": "explicit_target_unit_contract_required"}
            item = mapped
        candidate_id = "EC-" + base.sha(base.identity_spec(base.normalize(item)))[:20]
    except Exception as exc:  # the producer records these slots as rejected
        return {"outcome": "error", "reason": _error_code(exc)}
    prior = existing.get(candidate_id)
    if candidate_id in seen:
        registration = "REPEAT_WITHIN_BATCH"
    elif prior is None or all((prior.get("source") or {}).get(key) == source[key] for key in ("daily_output_sha256", "daily_context_sha256", "daily_receipt_sha256")):
        registration = "FIRST_SEEN_IN_THIS_BATCH"  # unregistered, or registered by this same batch: replay-invariant
    else:
        registration = "REGISTERED_BY_OTHER_SOURCE"
    seen.add(candidate_id)
    new = registration == "FIRST_SEEN_IN_THIS_BATCH"
    return {"outcome": "normalized_new" if new else "normalized_existing_duplicate", "candidate_id": candidate_id, "registration": registration}


def proposal_slot_census(
    output_bytes: bytes | None,
    context_bytes: bytes | None,
    receipt_bytes: bytes | None,
    *,
    legacy_items: list[dict[str, Any]],
    legacy_catalog_sha256: str | None,
    existing_candidates: dict[str, dict[str, Any]],
    known_response_identities: dict[str, str] | None = None,
    source_batch_path: str | None = None,
    mode: str = "PROSPECTIVE_PRODUCER_CAPTURE",
) -> dict[str, Any]:
    """Pure, deterministic per-batch census. Missing evidence is INVALID or UNKNOWN, never zero."""
    reasons: list[str] = []
    output = _parse(output_bytes, "output", reasons)
    context = _parse(context_bytes, "context", reasons)
    receipt = _parse(receipt_bytes, "receipt", reasons)
    if output is not None and not isinstance(output, dict):
        reasons.append("output_not_object")
    if context is not None and not isinstance(context, dict):
        reasons.append("context_not_object")
    if not isinstance(receipt, dict):
        if receipt is not None:
            reasons.append("receipt_not_object")
        receipt = {}
    output_d = output if isinstance(output, dict) else {}
    context_d = context if isinstance(context, dict) else {}
    hashes = {
        "output_sha256": _sha256_bytes(output_bytes) if output_bytes is not None else None,
        "context_sha256": _sha256_bytes(context_bytes) if context_bytes is not None else None,
        "context_canonical_sha256": _sha256_bytes(canonical(context)) if context is not None else None,
        "receipt_sha256": _sha256_bytes(receipt_bytes) if receipt_bytes is not None else None,
    }
    # api_gateway.py hashes the exact output bytes and the canonical context bytes.
    for name, observed, field in (("output", hashes["output_sha256"], "output_hash"), ("context", hashes["context_canonical_sha256"], "context_hash")):
        declared = receipt.get(field)
        if not isinstance(declared, str) or not SHA256_HEX.fullmatch(declared):
            reasons.append(f"{name}_hash_missing")
        elif observed != declared:
            reasons.append(f"{name}_hash_mismatch")
    if receipt.get("task") != "DAILY_DIRECTOR_SHADOW":
        reasons.append("receipt_task_not_daily_director")
    status = receipt.get("status")
    if status not in SURVIVING_OUTPUT_BY_STATUS:
        reasons.append("receipt_status_unknown")
    skipped = status in WORKFLOW_SKIP_STATUSES

    response_id = receipt.get("response_id")
    if skipped:
        if response_id is not None:
            reasons.append("skip_receipt_has_response_identity")
        response_id = None
    elif not isinstance(response_id, str) or not response_id.strip():
        reasons.append("response_identity_missing")
        response_id = None
    response_ids = receipt.get("response_ids")
    if "response_ids" not in receipt:
        response_ids = None
    elif not isinstance(response_ids, list) or not response_ids or not all(isinstance(r, str) and r.strip() for r in response_ids):
        reasons.append("response_ids_malformed")
        response_ids = None
    else:
        if skipped:
            reasons.append("skip_receipt_has_response_identity")
        if len(set(response_ids)) != len(response_ids):
            reasons.append("response_identity_duplicated_within_batch")
        if response_id is not None and response_ids[-1] != response_id:
            reasons.append("response_identity_contradiction")
    identities = sorted({_sha256_bytes(r.encode()) for r in (response_ids or []) + ([response_id] if response_id else [])})

    attempt_count = receipt.get("attempt_count")
    if "attempt_count" not in receipt:
        attempt_count = None
    elif type(attempt_count) is not int or attempt_count < 0:
        reasons.append("attempt_count_malformed")
        attempt_count = None
    if attempt_count is not None and response_ids is not None and attempt_count != len(response_ids):
        reasons.append("attempt_count_response_ids_mismatch")
    attempts = attempt_count if attempt_count is not None else len(response_ids) if response_ids is not None else None
    surviving = SURVIVING_OUTPUT_BY_STATUS.get(status) if isinstance(status, str) else None
    if attempts is not None and surviving is not None and attempts < surviving:
        reasons.append("attempt_count_inconsistent_with_status")
    abandoned: int | str = attempts - surviving if attempts is not None and surviving is not None and attempts >= surviving else UNKNOWN
    parse_errors = receipt.get("parse_errors")

    latest = ((context_d.get("latest_capture") or {}).get("market_metrics") or {}) if isinstance(context_d.get("latest_capture"), dict) else {}
    captured = (context_d.get("latest_capture") or {}).get("captured_at_utc") if isinstance(context_d.get("latest_capture"), dict) else None
    try:
        base.dt(captured)
    except (TypeError, ValueError):
        reasons.append("capture_clock_malformed")
        captured = None
    source = {"daily_output_sha256": base.sha(output), "daily_context_sha256": base.sha(context), "daily_receipt_sha256": base.sha(receipt)}

    experiment_state, experiment_slots = _container(output_d, "experiment_candidates")
    forecast_state, forecast_slots = _container(output_d, "forecast_candidates")
    if forecast_state == "ABSENT":
        reasons.append("forecast_candidates_absent")  # required gateway field
    declared = receipt.get("forecast_candidate_count")
    observed_forecast_count = len(forecast_slots) if forecast_state == "LIST" else None
    if "forecast_candidate_count" not in receipt:
        if not skipped:  # the workflow skip branch declares no count; the observed count stays authoritative
            reasons.append("declared_forecast_count_missing")
    elif type(declared) is not int:
        reasons.append("declared_forecast_count_malformed")
    elif declared != observed_forecast_count:
        reasons.append("declared_forecast_count_mismatch")
    try:
        emergent = base.emergent_pairs(context_d, latest)
    except Exception as exc:
        reasons.append("emergent_pair_derivation_error:" + _error_code(exc))
        emergent = []
    # Same order as the producer's raw list, so the first slot of a candidate id is the creator.
    families = (
        ("model_experiment", "output.experiment_candidates", experiment_slots),
        ("legacy_sensor", "legacy_sensor_catalog.pairs", list(enumerate(legacy_items))),
        ("emergent_pair", "context.metric_deltas.emergent_pairs", list(enumerate(emergent))),
        ("model_forecast", "output.forecast_candidates", forecast_slots),
    )
    seen: set[str] = set()
    slots = []
    for family, array, items in families:
        for index, item in items:
            row = {"origin_family": family, "array": array, "index": index, "slot_sha256": _sha256_bytes(canonical(item))}
            row.update({"outcome": "malformed", "reason": "container_not_a_list"} if index is None else _classify_slot(item, family, latest, existing_candidates, source, seen))
            slots.append(row)

    census_id = _census_id(hashes)
    for identity in identities:
        owner = (known_response_identities or {}).get(identity)
        if owner is not None and owner != census_id:
            reasons.append("response_identity_reused_by_other_batch")
            break
    by_family = {family: {outcome: 0 for outcome in SLOT_OUTCOMES} for family in SLOT_ORIGIN_FAMILIES}
    for row in slots:
        by_family[row["origin_family"]][row["outcome"]] += 1
    model = [row for row in slots if row["origin_family"] in {"model_forecast", "model_experiment"}]
    if skipped and model:
        reasons.append("skip_receipt_with_model_slots")
    reasons = sorted(set(reasons))
    batch_status = "INVALID" if reasons else "SKIPPED" if skipped else "VALID_OBSERVED_BATCH"
    return {
        "contract": PROPOSAL_SLOT_CENSUS_CONTRACT,
        "census_id": census_id,
        "classification": mode,
        "source_family": "DAILY_DIRECTOR_SHADOW",
        "source_batch_path": source_batch_path,
        "batch_status": batch_status,
        "complete_for_observed_batch": batch_status == "VALID_OBSERVED_BATCH",
        "invalid_reasons": reasons,
        "binding": {**hashes, "receipt_output_hash": receipt.get("output_hash"), "receipt_context_hash": receipt.get("context_hash"), "receipt_contract": receipt.get("contract"), "receipt_status": status, "legacy_sensor_catalog_sha256": legacy_catalog_sha256, "producer_source": source},
        "response_identity_sha256": identities,
        "attempts": {
            "attempt_count": attempts if attempts is not None else UNKNOWN,
            "surviving_output_attempts": surviving if surviving is not None else UNKNOWN,
            "abandoned_attempts_without_surviving_output": abandoned,
            "parse_error_count": len(parse_errors) if isinstance(parse_errors, list) else UNKNOWN,
            "pre_receipt_attempts": UNKNOWN,
        },
        "declared_forecast_candidate_count": declared if type(declared) is int else UNKNOWN,
        "containers": {"output.experiment_candidates": experiment_state, "output.forecast_candidates": forecast_state},
        "slots": slots,
        "counts": {
            "observed_raw_slot_count": len(slots),
            "model_emission_slot_count": len(model),
            "distinct_normalized_hypothesis_count": len({row["candidate_id"] for row in slots if "candidate_id" in row}),
            "distinct_model_normalized_hypothesis_count": len({row["candidate_id"] for row in model if "candidate_id" in row}),
            "independent_effective_n": None,
            "independent_effective_n_status": UNKNOWN,
            "by_family_outcome": by_family,
        },
        "clock": {"source_capture_clock_utc": captured, "semantics": "CAPTURE_CLOCK_NOT_PROPOSAL_GENERATION_OR_FIRST_PUBLICATION", "receipt_created_unix": receipt.get("created_unix")},
        "coverage": {"label": "PARTIAL", "scope": "SINGLE_SOURCE_FAMILY_OBSERVED_BATCH_ONLY", "global_proposal_time_trial_denominator": None, "broad_search": "BROAD_SEARCH_BLOCKED"},
        "authority": {"canonical_effect": False, "admission_effect": False, "automatic_promotion": False, "portfolio_execution": False, "framework_state_change": False},
    }


def census_internal_error(output_bytes: bytes | None, context_bytes: bytes | None, receipt_bytes: bytes | None, *, source_batch_path: str | None, mode: str) -> dict[str, Any]:
    """Fixed-code INVALID census when the census itself failed: raw-byte hashes only, no parsed value, no exception text."""
    hashes = {
        "output_sha256": _sha256_bytes(output_bytes) if output_bytes is not None else None,
        "context_sha256": _sha256_bytes(context_bytes) if context_bytes is not None else None,
        "receipt_sha256": _sha256_bytes(receipt_bytes) if receipt_bytes is not None else None,
    }
    return {
        "contract": PROPOSAL_SLOT_CENSUS_CONTRACT,
        "census_id": _census_id(hashes),
        "classification": mode,
        "source_family": "DAILY_DIRECTOR_SHADOW",
        "source_batch_path": source_batch_path,
        "batch_status": "INVALID",
        "complete_for_observed_batch": False,
        "invalid_reasons": [CENSUS_INTERNAL_ERROR],
        "binding": {**hashes, "context_canonical_sha256": None, "receipt_output_hash": None, "receipt_context_hash": None, "receipt_contract": None, "receipt_status": None, "legacy_sensor_catalog_sha256": None, "producer_source": None},
        "response_identity_sha256": [],
        "attempts": {key: UNKNOWN for key in ("attempt_count", "surviving_output_attempts", "abandoned_attempts_without_surviving_output", "parse_error_count", "pre_receipt_attempts")},
        "declared_forecast_candidate_count": UNKNOWN,
        "containers": {"output.experiment_candidates": UNKNOWN, "output.forecast_candidates": UNKNOWN},
        "slots": [],
        "counts": {
            "observed_raw_slot_count": UNKNOWN,
            "model_emission_slot_count": UNKNOWN,
            "distinct_normalized_hypothesis_count": UNKNOWN,
            "distinct_model_normalized_hypothesis_count": UNKNOWN,
            "independent_effective_n": None,
            "independent_effective_n_status": UNKNOWN,
            "by_family_outcome": UNKNOWN,
        },
        "clock": {"source_capture_clock_utc": None, "semantics": "CAPTURE_CLOCK_NOT_PROPOSAL_GENERATION_OR_FIRST_PUBLICATION", "receipt_created_unix": None},
        "coverage": {"label": "PARTIAL", "scope": "SINGLE_SOURCE_FAMILY_OBSERVED_BATCH_ONLY", "global_proposal_time_trial_denominator": None, "broad_search": "BROAD_SEARCH_BLOCKED"},
        "authority": {"canonical_effect": False, "admission_effect": False, "automatic_promotion": False, "portfolio_execution": False, "framework_state_change": False},
    }


def isolated_census(inputs: tuple[bytes | None, bytes | None, bytes | None], build: Callable[[], dict[str, Any]], *, source_batch_path: str | None, mode: str) -> dict[str, Any]:
    """The census is observability: no failure while building or serialising it may stop or change the producer."""
    try:
        census = build()
        canonical(census)  # the same serialisation base.write_new uses
        return census
    except Exception:  # noqa: BLE001 - deliberately broad; only the fixed code is kept, never exception text
        return census_internal_error(*inputs, source_batch_path=source_batch_path, mode=mode)


def load_census_identities(census_root: Path) -> dict[str, str]:
    known: dict[str, str] = {}
    for _, value in sorted(base.jsons(census_root, PROPOSAL_SLOT_CENSUS_CONTRACT), key=lambda item: item[0].as_posix()):
        for identity in value.get("response_identity_sha256") or []:
            known.setdefault(str(identity), str(value.get("census_id")))
    return known


def _read_optional(path: Path) -> bytes | None:
    return path.read_bytes() if path.is_file() else None


def retrospective_census(repo_root: Path, daily_root: Path, candidate_root: Path, legacy_catalog: Path | None) -> list[dict[str, Any]]:
    """Derived read-only view over archived daily batches, in path (chronological) order."""
    existing = {value["candidate_id"]: value for _, value in base.unique_candidate_rows(candidate_root)[0]}
    legacy_items = base.legacy(legacy_catalog)
    legacy_sha = _read_optional(legacy_catalog) if legacy_catalog else None
    known: dict[str, str] = {}
    rows = []
    for receipt_path in sorted(daily_root.rglob("DAILY_DIRECTOR_RECEIPT.json"), key=lambda p: p.as_posix()):
        folder = receipt_path.parent
        inputs = (_read_optional(folder / "DAILY_DIRECTOR_OUTPUT.json"), _read_optional(folder / "context.json"), receipt_path.read_bytes())
        batch_path = base.rel(repo_root, folder)
        census = isolated_census(inputs, lambda: proposal_slot_census(
            *inputs, legacy_items=legacy_items, legacy_catalog_sha256=_sha256_bytes(legacy_sha) if legacy_sha is not None else None,
            existing_candidates=existing, known_response_identities=known, source_batch_path=batch_path, mode="RETROSPECTIVE_DERIVED_VIEW"),
            source_batch_path=batch_path, mode="RETROSPECTIVE_DERIVED_VIEW")
        for identity in census["response_identity_sha256"]:
            known.setdefault(identity, census["census_id"])
        for slot in census["slots"]:
            if "candidate_id" in slot:  # derived-view only: was the slot's hypothesis ever registered?
                slot["in_candidate_store"] = slot["candidate_id"] in existing
        rows.append(census)
    return rows


def aggregate_census(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_family = {family: {outcome: 0 for outcome in SLOT_OUTCOMES} for family in SLOT_ORIGIN_FAMILIES}
    reasons: dict[str, int] = {}
    hypotheses: set[str] = set()
    model_hypotheses: set[str] = set()
    abandoned = unknown_attempts = with_abandoned = not_in_store = unknown_slot_counts = 0
    for row in rows:
        for reason in row["invalid_reasons"]:
            reasons[reason] = reasons.get(reason, 0) + 1
        if not isinstance(row["counts"]["by_family_outcome"], dict):
            unknown_slot_counts += 1  # CENSUS_INTERNAL_ERROR: slots were not enumerated, so they are not zero
        else:
            for family, outcomes in row["counts"]["by_family_outcome"].items():
                for outcome, count in outcomes.items():
                    by_family[family][outcome] += count
        for slot in row["slots"]:
            if "candidate_id" in slot:
                hypotheses.add(slot["candidate_id"])
                not_in_store += int(slot.get("in_candidate_store") is False)
                if slot["origin_family"] in {"model_forecast", "model_experiment"}:
                    model_hypotheses.add(slot["candidate_id"])
        value = row["attempts"]["abandoned_attempts_without_surviving_output"]
        if value == UNKNOWN:
            unknown_attempts += 1
        else:
            abandoned += value
            with_abandoned += int(value > 0)
    valid = sum(1 for row in rows if row["batch_status"] == "VALID_OBSERVED_BATCH")
    skipped = sum(1 for row in rows if row["batch_status"] == "SKIPPED")
    return {
        "contract": "EXPERIMENT_PROPOSAL_SLOT_CENSUS_AGGREGATE_v1",
        "batch_count": len(rows),
        "valid_batch_count": valid,
        "skipped_batch_count": skipped,
        "invalid_batch_count": len(rows) - valid - skipped,
        "invalid_reason_counts": dict(sorted(reasons.items())),
        "slot_counts_unknown_batch_count": unknown_slot_counts,
        "slots_by_family_outcome": by_family,
        "observed_raw_slot_count": sum(row["counts"]["observed_raw_slot_count"] for row in rows if type(row["counts"]["observed_raw_slot_count"]) is int),
        "model_emission_slot_count": sum(row["counts"]["model_emission_slot_count"] for row in rows if type(row["counts"]["model_emission_slot_count"]) is int),
        "distinct_normalized_hypothesis_count": len(hypotheses),
        "distinct_model_normalized_hypothesis_count": len(model_hypotheses),
        "independent_effective_n": None,
        "normalized_slots_not_in_candidate_store": not_in_store,
        "attempts_unknown_batch_count": unknown_attempts,
        "known_abandoned_attempts_without_surviving_output": abandoned,
        "batches_with_known_abandoned_attempts": with_abandoned,
        "coverage": {"label": "PARTIAL", "global_proposal_time_trial_denominator": None, "broad_search": "BROAD_SEARCH_BLOCKED"},
    }


def retrospective_main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(prog="experiment_lifecycle_scientific_admission.py retrospective-census")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--daily-root", type=Path, default=Path("research/api_agent/outputs/daily"))
    parser.add_argument("--candidate-root", type=Path, default=Path("research/experiment_lifecycle/candidates"))
    parser.add_argument("--legacy-sensor-catalog", type=Path)
    parser.add_argument("--rows-output", type=Path, help="optional JSONL of per-batch census rows (derived, not committed)")
    args = parser.parse_args(argv)
    rows = retrospective_census(args.repo_root, args.daily_root, args.candidate_root, args.legacy_sensor_catalog)
    if args.rows_output:
        args.rows_output.parent.mkdir(parents=True, exist_ok=True)
        args.rows_output.write_bytes(b"".join(canonical(row) for row in rows))
    print(json.dumps(aggregate_census(rows), sort_keys=True))



EXISTING_ONLY_MODE = "BUDGET_HOLD_EXISTING_ADMITTED_ONLY_v1"


def existing_only_source(root: Path, context_path: Path, hold_path: Path, now: datetime) -> tuple[dict, dict]:
    """Bind the original writer's current context and explicit clean HOLD; no model receipt."""
    evidence_root = root / "research/experiment_lifecycle/budget_hold_inputs"
    run = os.environ.get("GITHUB_RUN_ID", "")
    attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "")
    head = os.environ.get("GITHUB_SHA", "")
    if not (re.fullmatch(r"[1-9][0-9]*", run) and re.fullmatch(r"[1-9][0-9]*", attempt)
            and re.fullmatch(r"[0-9a-f]{40}", head)):
        raise ValueError("hold_native_identity_missing")
    folder = evidence_root / f"{run}-{attempt}"
    if (context_path.absolute() != folder / "context.json"
            or hold_path.absolute() != folder / "budget_disposition.json"
            or context_path.resolve() != context_path.absolute()
            or hold_path.resolve() != hold_path.absolute()):
        raise ValueError("hold_evidence_path_invalid")
    context_bytes, hold_bytes = context_path.read_bytes(), hold_path.read_bytes()
    context = strict_json_loads(context_bytes.decode("utf-8"))
    receipt = strict_json_loads(hold_bytes.decode("utf-8"))
    if (not isinstance(context, dict) or not isinstance(receipt, dict)
            or receipt.get("contract") != "ROUTINE_API_BUDGET_DISPOSITION_v1"
            or receipt.get("lane") != "director" or receipt.get("disposition") != "HOLD"
            or receipt.get("reason") != "API_RESERVE_GUARD_BLOCKED"
            or (receipt.get("run_id"), receipt.get("run_attempt"), receipt.get("head_sha")) != (run, attempt, head)
            or any(receipt.get(k) is not False for k in ("paid_call_executed_here", "analysis_completed_here", "paid_authority"))):
        raise ValueError("hold_receipt_unverified")
    guards = receipt.get("guard_observations")
    if not isinstance(guards, list) or not all(isinstance(g, dict) for g in guards):
        raise ValueError("hold_guard_sequence_invalid")
    sequence = [(g.get("guard"), g.get("disposition"), g.get("returncode")) for g in guards]
    if sequence not in [[("lane", "HOLD", 1)], [("lane", "PASS", 0), ("monthly", "HOLD", 1)]]:
        raise ValueError("hold_guard_sequence_invalid")
    if any(type(g.get("returncode")) is not int or not isinstance(g.get("stdout_sha256"), str)
           or not SHA256_HEX.fullmatch(g["stdout_sha256"]) for g in guards):
        raise ValueError("hold_guard_binding_invalid")
    for guard in guards:
        budget = guard.get("budget")
        if not isinstance(budget, dict):
            raise ValueError("hold_guard_budget_missing")
        remaining, reserve = budget.get("remaining_usd"), budget.get("reserve_usd")
        def finite_number(value):
            return type(value) in (int, float) and math.isfinite(value)
        expected_reserve = 0.05 if guard["guard"] == "lane" else 4.0
        if not finite_number(remaining) or not finite_number(reserve) or reserve != expected_reserve:
            raise ValueError("hold_guard_budget_invalid")
        exhausted = remaining <= reserve
        if guard["guard"] == "monthly":
            owner_remaining, owner_reserve = budget.get("owner_global_remaining_usd_after_risk"), budget.get("owner_global_reserve_usd")
            if not finite_number(owner_remaining) or not finite_number(owner_reserve) or owner_reserve != 4.0:
                raise ValueError("hold_guard_owner_budget_invalid")
            exhausted = exhausted or owner_remaining < owner_reserve
        expected_disposition = "HOLD" if exhausted else "PASS"
        expected_status = "BLOCKED" if exhausted else "PASS"
        expected_reason = "API_RESERVE_GUARD_BLOCKED" if exhausted else "GUARD_PASS"
        if (guard["disposition"] != expected_disposition or budget.get("status") != expected_status
                or guard.get("reason") != expected_reason):
            raise ValueError("hold_guard_budget_contradiction")
    latest = context.get("latest_capture")
    coverage = context.get("coverage")
    if not isinstance(latest, dict) or not isinstance(coverage, dict):
        raise ValueError("hold_capture_invalid")
    captured, rid = latest.get("captured_at_utc"), latest.get("run_id")
    if (not canonical_capture_clock(captured) or not isinstance(rid, str) or not rid.strip()
            or not isinstance(latest.get("market_metrics"), dict)):
        raise ValueError("hold_capture_invalid")
    age = now - base.dt(captured)
    if not timedelta(0) <= age <= timedelta(hours=4):
        raise ValueError("hold_capture_stale_or_future")
    comparable = coverage.get("comparable_numeric_metrics")
    if (type(comparable) is not int or comparable <= 0
            or context.get("delta_status") not in {"DELTA_READY", "DELTA_DEGRADED_STALE_PREDECESSOR"}):
        raise ValueError("hold_market_delta_unavailable")
    return context, {
        "mode": EXISTING_ONLY_MODE, "source_run_id": rid,
        "daily_output_sha256": None, "daily_receipt_sha256": None,
        "daily_context_sha256": base.sha(context),
        "daily_context_path": base.rel(root, context_path),
        "context_bytes_sha256": hashlib.sha256(context_bytes).hexdigest(),
        "budget_hold_receipt_path": base.rel(root, hold_path),
        "budget_hold_receipt_sha256": hashlib.sha256(hold_bytes).hexdigest(),
    }


def strict_hold_candidate_rows(root: Path) -> tuple[list[tuple[Path, dict]], set[str]]:
    """Read the complete candidate census before HOLD writes.

    Historical duplicate IDs with identical specs but different records are
    not independently qualified. Keep the existing canonical representative
    for registry compatibility, but quarantine the entire ambiguous ID from
    HOLD selection. Do not rewrite or delete historical rows.
    """
    rows: dict[str, tuple[Path, dict, bytes]] = {}
    ambiguous: set[str] = set()
    if not root.is_dir() or root.resolve() != root.absolute():
        raise ValueError("hold_candidate_root_invalid")
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("hold_candidate_symlink")
        if path.suffix != ".json":
            continue
        data = path.read_bytes()
        value = strict_json_loads(data.decode("utf-8"))
        if not isinstance(value, dict) or value.get("contract") != "EXPERIMENT_CANDIDATE_v1":
            raise ValueError("hold_candidate_invalid")
        cid = value.get("candidate_id")
        if not isinstance(cid, str) or not re.fullmatch(r"EC-[0-9a-f]{20}", cid) or path.stem != cid:
            raise ValueError("hold_candidate_identity_invalid")
        if not isinstance(value.get("spec"), dict):
            raise ValueError("hold_candidate_spec_invalid")
        old = rows.get(cid)
        if old is not None:
            if old[1]["spec"] != value["spec"]:
                raise ValueError("hold_candidate_spec_conflict")
            if old[2] != data:
                ambiguous.add(cid)
            # Match the legacy representative only for descriptive compatibility.
            key = lambda item: (str(item[1].get("created_at_utc") or ""),
                                str(item[1].get("registered_at_utc") or ""), item[0].as_posix())
            if key((path, value)) >= key(old):
                continue
        rows[cid] = (path, value, data)
    return [(p, v) for p, v, _ in rows.values()], ambiguous


def existing_only_admissions(root: Path) -> dict[str, dict]:
    """Do not silently accept conflicting admission records or malformed authority."""
    rows: dict[str, dict] = {}
    raw: dict[str, bytes] = {}
    if not root.is_dir() or root.resolve() != root.absolute():
        raise ValueError("hold_admission_root_invalid")
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("hold_admission_symlink")
        if path.suffix != ".json":
            continue
        data = path.read_bytes()
        value = strict_json_loads(data.decode("utf-8"))
        if not isinstance(value, dict) or value.get("contract") != ADMISSION_CONTRACT:
            raise ValueError("hold_admission_invalid")
        cid = value.get("candidate_id")
        if not isinstance(cid, str) or not re.fullmatch(r"EC-[0-9a-f]{20}", cid) or path.stem != cid:
            raise ValueError("hold_admission_identity_invalid")
        if cid in raw and raw[cid] != data:
            raise ValueError("hold_admission_conflict")
        rows[cid], raw[cid] = value, data
    return rows


def hold_candidate_eligible(candidate: dict, admission: dict | None, captured: str) -> bool:
    if not admission or admission.get("status") != QUALIFIED:
        return False
    spec = candidate["spec"]
    candidate_authority = candidate.get("authority")
    if (not isinstance(candidate_authority, dict)
            or set(candidate_authority) != {"canonical_promotion", "framework_state_change", "model_weight_change", "portfolio_action"}
            or any(v is not False for v in candidate_authority.values())):
        return False
    authority = admission.get("authority")
    if (not isinstance(authority, dict)
            or set(authority) != {"canonical_effect", "portfolio_execution", "framework_state_change",
                                  "threshold_change", "weight_change", "automatic_promotion"}
            or any(v is not False for v in authority.values())
            or admission.get("no_retroactive_rescore") is not True
            or admission.get("candidate_id") != candidate.get("candidate_id")
            or admission.get("candidate_created_at_utc") != candidate.get("created_at_utc")
            or admission.get("semantic_spec") != semantic_spec(spec)
            or admission.get("semantic_fingerprint") != digest(semantic_spec(spec))
            or qualification_status(spec, None)[0] != QUALIFIED):
        return False
    try:
        created, registered, frozen, capture = (_utc_key(t) for t in
            (candidate.get("created_at_utc"), candidate.get("registered_at_utc"),
             admission.get("admission_frozen_at_utc"), captured))
        return created <= registered <= frozen < capture
    except AllocationIntegrityError:
        return False


def capture_already_observed(root: Path, cid: str, captured: str, run_id: str, *, hold_only: bool = False) -> bool:
    for _, row in base.jsons(root / cid, "EXPERIMENT_OBSERVATION_v1"):
        source = row.get("source")
        if (row.get("candidate_id") == cid and row.get("observed_at_utc") == captured
                and isinstance(source, dict) and source.get("source_run_id") == run_id
                and (not hold_only or source.get("mode") == EXISTING_ONLY_MODE)):
            return True
    return False


HOLD_PUBLICATION_START = "EXPERIMENT_HOLD_PUBLICATION_START_v1"
HOLD_PUBLICATION_COMPLETE = "EXPERIMENT_HOLD_PUBLICATION_COMPLETE_v1"
HOLD_PUBLICATION_ARTIFACT = re.compile(
    r"(?:research/experiment_lifecycle/observations/EC-[0-9a-f]{20}/EO-[0-9a-f]{20}"
    r"|research/framework_memory/forecast_memory/[0-9]{4}/[0-9]{2}/EXP-FC-[0-9a-f]{20})\.json"
)


def hold_publication_root(root: Path) -> Path:
    return root / "research/experiment_lifecycle/budget_hold_inputs/publication"


def hold_publication_artifact(root: Path, path: Path) -> tuple[str, str]:
    key = path.absolute().relative_to(root).as_posix()
    if (not HOLD_PUBLICATION_ARTIFACT.fullmatch(key) or path.resolve() != path.absolute()
            or not path.is_file()):
        raise ValueError("hold_publication_artifact_invalid")
    return key, hashlib.sha256(path.read_bytes()).hexdigest()


def hold_publication_preflight(root: Path, window: str | None) -> dict | None:
    """Refuse an interrupted HOLD publication before either writer can write.

    Only process-level restart detection, not automatic repair or a trusted
    source clock. Completed manifests bind the immutable newly written bytes.
    """
    folder = hold_publication_root(root)
    if folder.resolve() != folder.absolute():
        raise ValueError("hold_publication_path_invalid")
    if not folder.exists():
        return None
    if not folder.is_dir():
        raise ValueError("hold_publication_path_invalid")
    found = None
    for entry in sorted(folder.iterdir()):
        if (not re.fullmatch(r"[0-9a-f]{20}", entry.name) or entry.is_symlink()
                or not entry.is_dir()):
            raise ValueError("hold_publication_path_invalid")
        start_path, done_path = entry / "started.json", entry / "completed.json"
        if (set(x.name for x in entry.iterdir()) != {"started.json", "completed.json"}
                or any(x.is_symlink() or not x.is_file() for x in (start_path, done_path))):
            raise ValueError("hold_publication_incomplete")
        start_bytes = start_path.read_bytes()
        start = strict_json_loads(start_bytes.decode("utf-8"))
        done = strict_json_loads(done_path.read_text(encoding="utf-8"))
        if (not isinstance(start, dict) or not isinstance(done, dict)
                or set(start) != {"contract", "window", "source_run_id", "captured_at_utc",
                                  "context_sha256", "hold_receipt_sha256"}
                or set(done) != {"contract", "window", "started_sha256", "artifacts"}
                or start["contract"] != HOLD_PUBLICATION_START
                or done["contract"] != HOLD_PUBLICATION_COMPLETE
                or start["window"] != entry.name or done["window"] != entry.name
                or not canonical_capture_clock(start["captured_at_utc"])
                or not isinstance(start["source_run_id"], str) or not start["source_run_id"].strip()
                or causal_event_window(start["source_run_id"], start["captured_at_utc"]) != entry.name
                or not all(isinstance(start[k], str) and SHA256_HEX.fullmatch(start[k])
                           for k in ("context_sha256", "hold_receipt_sha256"))
                or done["started_sha256"] != hashlib.sha256(start_bytes).hexdigest()
                or not isinstance(done["artifacts"], dict)):
            raise ValueError("hold_publication_receipt_invalid")
        for key, expected in done["artifacts"].items():
            if (not isinstance(key, str) or not HOLD_PUBLICATION_ARTIFACT.fullmatch(key)
                    or not isinstance(expected, str) or not SHA256_HEX.fullmatch(expected)
                    or hold_publication_artifact(root, root / key) != (key, expected)):
                raise ValueError("hold_publication_artifact_changed")
        if entry.name == window:
            found = start
    return found


def hold_publication_write(path: Path, value: dict) -> str:
    # Exclusive creation: an interrupted marker is deliberately not replaced.
    data = canonical(value)
    with path.open("xb") as out:
        out.write(data)
        out.flush()
        os.fsync(out.fileno())
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    for name in (
        "repo-root", "daily-context", "candidate-root", "observation-root", "dispatch-root", "forecast-root", "outcome-root", "receipt-root", "registry-output", "manifest-output", "admission-root", "admission-registry-output",
    ):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--daily-output", type=Path)
    parser.add_argument("--daily-receipt", type=Path)
    parser.add_argument("--existing-admitted-only", action="store_true")
    parser.add_argument("--budget-hold-receipt", type=Path)
    parser.add_argument("--legacy-sensor-catalog", type=Path)
    parser.add_argument("--repository", default="Donh91/Investering-Framework-Archive-v1")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--max-new-forecasts", type=int, default=5)
    parser.add_argument("--proposal-census-root", type=Path, help="default: <admission-root>/../proposal_slot_census")
    args = parser.parse_args()
    hold = args.existing_admitted_only
    if hold:
        if args.daily_output or args.daily_receipt or args.legacy_sensor_catalog or not args.budget_hold_receipt or not 0 <= args.max_new_forecasts <= 5:
            parser.error("existing-only requires HOLD receipt, no proposal inputs, and cap at most 5")
    elif not args.daily_output or not args.daily_receipt or args.budget_hold_receipt:
        parser.error("normal mode requires daily output and receipt, no HOLD receipt")

    # Forecast-store integrity is checked before any write. base.registry would raise on an identity
    # conflict later anyway (after observations/dispatch were written), so a corrupt store is a
    # truthful whole-run failure with a fixed diagnostic code, never a partial run or false summary.
    try:
        frozen_rows = unique_frozen_forecasts(args.forecast_root)
    except AllocationIntegrityError as exc:
        print(json.dumps({"status": "FORECAST_STORE_INTEGRITY_FAILURE", "code": str(exc), "writes_performed": False}, sort_keys=True), file=sys.stderr)
        raise SystemExit(3) from None

    root = args.repo_root.resolve()
    if hold:
        try:
            context, hold_source = existing_only_source(root, args.daily_context, args.budget_hold_receipt, datetime.now(UTC))
            admissions = existing_only_admissions(args.admission_root)
            hold_rows, ambiguous_ids = strict_hold_candidate_rows(args.candidate_root)
            if set(admissions) - {row["candidate_id"] for _, row in hold_rows}:
                raise ValueError("hold_orphan_admission")
        except (OSError, ValueError, TypeError, RecursionError):
            raise SystemExit("existing_only_evidence_unverified") from None
        output, receipt = {}, {}
    else:
        output = base.read(args.daily_output)
        context = base.read(args.daily_context)
        receipt = base.read(args.daily_receipt)
    # Preserve the legacy missing/null/empty-string clock fallback (forecast allocation still holds).
    # A present wrong JSON type is not missing, even when falsey. Reject it before any producer write.
    # A malformed latest_capture container must not be silently treated as an absent clock either.
    latest_capture = context.get("latest_capture")
    raw_capture_early = latest_capture.get("captured_at_utc") if isinstance(latest_capture, dict) else None
    clock_missing = raw_capture_early is None or (isinstance(raw_capture_early, str) and raw_capture_early == "")
    if ((latest_capture is not None and not isinstance(latest_capture, dict))
            or (not clock_missing and (not isinstance(raw_capture_early, str) or not capture_clock_parseable(raw_capture_early)))):
        print(json.dumps({"status": "CAPTURE_CLOCK_INVALID", "writes_performed": False}, sort_keys=True), file=sys.stderr)
        raise SystemExit(4)
    latest = ((latest_capture or {}).get("market_metrics") or {})
    previous = ((context.get("previous_capture") or {}).get("market_metrics") or {})
    captured = base.iso(datetime.now(UTC)) if clock_missing else raw_capture_early
    when = base.dt(captured)
    now = base.iso(datetime.now(UTC))
    source = hold_source if hold else {"daily_output_sha256": base.sha(output), "daily_context_sha256": base.sha(context), "daily_receipt_sha256": base.sha(receipt), "source_run_id": (context.get("latest_capture") or {}).get("run_id")}

    # Check pending HOLD publication before the paid path can create a proposal census.
    early_run = source["source_run_id"]
    early_window = (causal_event_window(early_run, captured)
                    if canonical_capture_clock(raw_capture_early) and isinstance(early_run, str)
                    and early_run.strip() else None)
    try:
        previous_publication = hold_publication_preflight(root, early_window)
        if hold and previous_publication is not None:
            if previous_publication["context_sha256"] != source["daily_context_sha256"]:
                raise ValueError("hold_publication_context_changed")
    except (OSError, ValueError, TypeError, RecursionError):
        raise SystemExit("hold_publication_recovery_required") from None

    raw = [] if hold else [item for item in output.get("experiment_candidates", []) if isinstance(item, dict)] + base.legacy(args.legacy_sensor_catalog) + base.emergent_pairs(context, latest)
    rejected = []
    for item in output.get("forecast_candidates", []):
        if not isinstance(item, dict):
            continue
        mapped = base.from_forecast(item, latest)
        if mapped:
            raw.append(mapped)
        else:
            rejected.append({"title": f"Prospective {item.get('metric_path')}", "error": "explicit_target_unit_contract_required"})

    if hold:
        existing_candidate_rows = hold_rows
    else:
        existing_candidate_rows, _ = base.unique_candidate_rows(args.candidate_root)
    existing_candidates = {value["candidate_id"]: value for _, value in existing_candidate_rows}
    if not hold:
        # #1557: account for every raw slot before the filtering/mapping/dedup below (metadata only).
        census_root = args.proposal_census_root or args.admission_root.parent / "proposal_slot_census"
        try:
            batch_path = base.rel(root, args.daily_output.parent)
        except ValueError:  # batch outside the repo root: keep the census, omit the path
            batch_path = None
        census_inputs = (args.daily_output.read_bytes(), args.daily_context.read_bytes(), args.daily_receipt.read_bytes())

        def build_census() -> dict[str, Any]:
            legacy_bytes = _read_optional(args.legacy_sensor_catalog) if args.legacy_sensor_catalog else None
            return proposal_slot_census(
                *census_inputs,
                legacy_items=base.legacy(args.legacy_sensor_catalog), legacy_catalog_sha256=_sha256_bytes(legacy_bytes) if legacy_bytes is not None else None,
                existing_candidates=existing_candidates, known_response_identities=load_census_identities(census_root), source_batch_path=batch_path)

        census = isolated_census(census_inputs, build_census, source_batch_path=batch_path, mode="PROSPECTIVE_PRODUCER_CAPTURE")
        base.write_new(census_root / when.strftime("%Y/%m") / f"{census['census_id']}.json", census)
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
            if candidate_id in existing_candidates:
                continue
            path = args.candidate_root / when.strftime("%Y/%m") / f"{candidate_id}.json"
            if base.write_new(path, value):
                new_ids.add(candidate_id)
                existing_candidates[candidate_id] = value
        except Exception as exc:
            rejected.append({"title": str(item.get("title") or "UNKNOWN"), "error": str(exc)})

    if not hold:
        admissions = load_admissions(args.admission_root)
    semantic_owner: dict[str, str] = {}
    all_candidates = sorted(existing_candidates.values(), key=lambda row: (str(row.get("created_at_utc") or ""), str(row.get("candidate_id") or "")))
    for candidate in all_candidates:
        cid = candidate["candidate_id"]
        existing = admissions.get(cid)
        semantic_id = digest(semantic_spec(candidate["spec"]))
        owner = semantic_owner.get(semantic_id)
        if existing is None and hold:
            continue
        if existing is None:
            record = admission_record(candidate, owner, now, historical=cid not in new_ids)
            path = args.admission_root / str(candidate.get("created_at_utc") or now)[:7].replace("-", "/") / f"{cid}.json"
            base.write_new(path, record)
            admissions[cid] = record
        if owner is None and admissions[cid].get("status") != "SEMANTIC_DUPLICATE_KEEP_SHADOW":
            semantic_owner[semantic_id] = cid

    admission_registry = build_admission_registry(admissions, now)
    if not hold:
        args.admission_registry_output.parent.mkdir(parents=True, exist_ok=True)
        args.admission_registry_output.write_bytes(canonical(admission_registry))

    new_forecasts = 0
    dispatch = 0
    episode_continuations = 0
    if hold:
        candidate_rows = list(hold_rows)
    else:
        candidate_rows, _ = base.unique_candidate_rows(args.candidate_root)
    # The cap is per causal event window: rows already frozen in this window (by any earlier run or
    # policy) occupy slots and are never rewritten; only the remainder may be issued.
    # A window is only derived from a canonical capture clock and a real run id (the historical
    # derivation is unchanged); anything else holds allocation for this run (0 new forecasts).
    raw_capture = (context.get("latest_capture") or {}).get("captured_at_utc")
    run_id = source["source_run_id"]
    # A whitespace-only source ID is missing, not a causal identity. Never trim a valid ID: historical hashes stay unchanged.
    event_window = causal_event_window(run_id, captured) if canonical_capture_clock(raw_capture) and isinstance(run_id, str) and run_id.strip() else None
    allocation = {"policy_version": ALLOCATION_POLICY_VERSION, "lookback_days": ALLOCATION_LOOKBACK_DAYS, "cap": args.max_new_forecasts,
                  "causal_event_window_id": event_window, "status": "OK", "by_kind": {}}
    service_history: dict[str, tuple[int, str]] = {}
    occupied_ids: set[str] = set()
    occupied: dict[str, str] = {}
    available_slots = 0
    if not canonical_capture_clock(raw_capture):
        allocation["status"] = "FAIL_CLOSED:capture_clock_noncanonical"
    elif event_window is None:
        allocation["status"] = "FAIL_CLOSED:capture_run_id_missing"
    else:
        service_history = forecast_service_history(frozen_rows, captured)
        occupied_ids, occupied = window_occupancy(frozen_rows, event_window)
        available_slots = max(0, args.max_new_forecasts - len(occupied_ids))
    allocation.update({"occupied_slots_before": len(occupied_ids), "available_slots": available_slots})
    issued_slots = 0
    candidate_rows.sort(key=lambda item: forecast_allocation_key(item[1], service_history))
    hold_observed = 0
    publication_start_sha = None
    publication_folder = None
    publication_artifacts: dict[str, str] = {}
    if hold:
        if previous_publication is not None:
            candidate_rows = []  # completed capture is immutable across attempts
        else:
            if early_window is None or early_window != event_window:
                raise SystemExit("hold_publication_window_invalid")
            publication_folder = hold_publication_root(root) / early_window
            # The directory itself is a durable pending indicator if marker writing fails.
            publication_folder.mkdir(parents=True, exist_ok=False)
            publication_start_sha = hold_publication_write(publication_folder / "started.json", {
                "contract": HOLD_PUBLICATION_START, "window": early_window,
                "source_run_id": early_run, "captured_at_utc": captured,
                "context_sha256": source["daily_context_sha256"],
                "hold_receipt_sha256": source["budget_hold_receipt_sha256"],
            })
    for spec_path, candidate in candidate_rows:
        spec = candidate["spec"]
        cid = candidate["candidate_id"]
        if hold and (cid in ambiguous_ids or not hold_candidate_eligible(candidate, admissions.get(cid), captured)
                     or capture_already_observed(args.observation_root, cid, captured, run_id)):
            continue
        # A subsequent paid analysis of the same source may register genuinely new proposals,
        # but must not observe/freeze the already observed existing candidate again.
        if not hold and cid not in new_ids and event_window is not None and capture_already_observed(
                args.observation_root, cid, captured, run_id, hold_only=True):
            continue
        admission = admissions[cid]
        admitted = admission.get("status") == QUALIFIED
        legacy_forecast_unit_ambiguous = spec.get("kind") == "FORECAST_TEST" and spec.get("target_unit_contract_version") != base.UNIT_CONTRACT_VERSION
        results = [base.evaluate(item, latest, previous) for item in spec["components"]]
        mapping = not spec["components"] and spec["kind"] != "FORECAST_TEST"
        missing = any(item["matched"] is None for item in results)
        fired = admitted and not legacy_forecast_unit_ambiguous and not mapping and ((not spec["components"] and spec["kind"] == "FORECAST_TEST") or (results and not missing and all(item["matched"] for item in results)))
        status = "TARGET_UNIT_QUARANTINED" if legacy_forecast_unit_ambiguous else "SCIENTIFIC_ADMISSION_BLOCKED" if not admitted and not mapping else "WAITING_FOR_MAPPING" if mapping else "WAITING_FOR_DATA" if missing else "FIRED_NO_TARGET" if fired and spec["target_direction"] == "NONE" else "FIRED" if fired else "OBSERVED_NOT_FIRED"
        observation_id = "EO-" + base.sha({"candidate_id": candidate["candidate_id"], "captured": captured, "source": source} if not hold else {"candidate_id": cid, "window": event_window, "mode": EXISTING_ONLY_MODE})[:20]
        observation = {"contract": "EXPERIMENT_OBSERVATION_v1", "observation_id": observation_id, "candidate_id": candidate["candidate_id"], "observed_at_utc": captured, "evaluation_status": status, "component_results": results, "scientific_admission_status": admission.get("status"), "scientific_admission_sha256": digest(admission), "source": source, "authority": "SHADOW_ONLY"}
        observation_path = args.observation_root / candidate["candidate_id"] / f"{observation_id}.json"
        is_new = False if mapping and candidate["candidate_id"] not in new_ids else base.write_new(observation_path, observation)
        if hold:
            if not is_new:
                raise SystemExit("hold_publication_recovery_required")
            key, sha = hold_publication_artifact(root, observation_path)
            publication_artifacts[key] = sha
            hold_observed += 1

        forecast_id = None
        start = base.at(latest, spec.get("target_metric_path") or "") if spec.get("target_metric_path") else None
        eligible = admitted and fired and spec["target_direction"] != "NONE" and isinstance(start, (int, float))
        if hold:
            eligible = eligible and is_new and type(start) in (int, float) and math.isfinite(start)
        kind_stats = allocation["by_kind"].setdefault(str(spec.get("kind")), {"eligible": 0, "issued_new": 0, "held_in_window": 0})
        kind_stats["eligible"] += int(eligible)
        if candidate["candidate_id"] in occupied:
            kind_stats["held_in_window"] += 1
            forecast_id = occupied[candidate["candidate_id"]] if eligible else None
        elif eligible and issued_slots < available_slots:
            issued_slots += 1
            window = event_window
            forecast_id = canonical_forecast_id(candidate["candidate_id"], window)
            frozen = {
                "contract": "FROZEN_FORECAST_v1", "unit_contract_version": base.UNIT_CONTRACT_VERSION, "forecast_id": forecast_id, "source_candidate_id": candidate["candidate_id"], "source_observation_id": observation_id,
                "frozen_at_utc": captured, "outcome_due_utc": base.iso(when + timedelta(days=spec["horizon_days"])), "metric_path": base.canonical_path(spec["target_metric_path"]), "metric_path_root": base.CAPTURE_DOCUMENT_ROOT,
                "direction": spec["target_direction"], "start_value": float(start), "target_mode": "PCT_MOVE" if spec["target_direction"] in {"UP", "DOWN"} else "PCT_RANGE", "threshold_pct": spec["target_threshold_pct"], "range_lower_pct": spec["target_range_lower_pct"], "range_upper_pct": spec["target_range_upper_pct"],
                "causal_event_window_id": window, "experimental_only": True,
                "scientific_admission": {"contract": ADMISSION_CONTRACT, "status": admission.get("status"), "record_sha256": digest(admission), "semantic_fingerprint": admission.get("semantic_fingerprint"), "method_reference": admission.get("method_reference")},
                "controls": {"always_wait": "ALWAYS_WAIT", "single_component_specs": spec["components"], "deterministic_placebo_direction": base.placebo(window), "control_freeze_time_utc": captured, "required_future_reviews": ["REDUNDANCY_COLLINEARITY", "NEGATIVE_CONTROL", "REGIME_STRATIFICATION", "LEAD_LAG_TIMELINESS", "FALSE_POSITIVE_FALSE_NEGATIVE_COST"]},
                "authority": {"portfolio_action": False, "framework_state_change": False, "model_weight_change": False, "canonical_promotion": False},
            }
            apply_exact_settlement_contract(frozen)
            forecast_path = args.forecast_root / when.strftime("%Y/%m") / f"{forecast_id}.json"
            if base.write_new(forecast_path, frozen):
                if hold:
                    key, sha = hold_publication_artifact(root, forecast_path)
                    publication_artifacts[key] = sha
                new_forecasts += 1
                kind_stats["issued_new"] += 1
            elif hold:
                raise SystemExit("hold_publication_recovery_required")

        if hold:
            continue  # Never create replication/registration requests on budget HOLD.
        episode_start = candidate["candidate_id"] in new_ids or (
            fired and prior_observation_status(args.observation_root, candidate["candidate_id"], captured) not in FIRED_STATES)
        if admitted and is_new and fired and not episode_start:
            episode_continuations += 1  # same fire episode: the observation is kept, no new request
        if admitted and is_new and episode_start:
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

    # LATEST lists only qualified requests that have no execution receipt yet. Every request and
    # receipt file stays immutable on disk; the consumer builds its receipt manifest from its own
    # receipt files, so receipted requests never need to be listed again.
    receipted = {str(value.get("request_id")) for _, value in base.jsons(args.receipt_root, "EXPERIMENT_EXECUTION_RECEIPT_v1")
                 if value.get("request_id")}
    requests = []
    total_qualified = 0
    for path, value in base.jsons(args.dispatch_root, "EXPERIMENT_REQUEST_v1"):
        if value.get("scientific_admission_status") != QUALIFIED:
            continue
        total_qualified += 1
        if value.get("request_id") in receipted:
            continue
        relative_path = base.rel(root, path)
        requests.append({"request_id": value["request_id"], "candidate_id": value["candidate_id"], "path": relative_path, "sha256": base.sha(value), "raw_url": f"https://raw.githubusercontent.com/{args.repository}/{args.branch}/{relative_path}"})
    manifest = {"contract": "EXPERIMENT_DISPATCH_MANIFEST_v2_SCIENTIFIC_ADMISSION", "generated_at_utc": now, "source_repository": args.repository, "source_branch": args.branch, "request_count": len(requests), "requests": sorted(requests, key=lambda item: item["request_id"]), "admission_required": QUALIFIED, "authority": "SHADOW_ONLY_CROSS_REPO_DISPATCH",
                "listing_rule": DISPATCH_LISTING_RULE, "total_qualified_request_count": total_qualified,
                "receipted_request_count": total_qualified - len(requests), "history_root": base.rel(root, args.dispatch_root)}
    if not hold:
        args.manifest_output.parent.mkdir(parents=True, exist_ok=True)
        args.manifest_output.write_bytes(base.canon(manifest))
    summary = {"candidate_count": reg["candidate_count"], "new_candidate_count": len(new_ids), "new_forecasts": new_forecasts, "forecast_allocation": allocation, "dispatch_created": dispatch, "episode_continuations_not_dispatched": episode_continuations, "admission_status_counts": admission_registry["status_counts"], "rejected": rejected}
    if hold:
        if publication_folder is not None:
            hold_publication_write(publication_folder / "completed.json", {
                "contract": HOLD_PUBLICATION_COMPLETE, "window": early_window,
                "started_sha256": publication_start_sha, "artifacts": publication_artifacts,
            })
        summary.update({"mode": EXISTING_ONLY_MODE, "observations_created": hold_observed, "ambiguous_candidate_count": len(ambiguous_ids), "paid_call_executed_here": False, "analysis_completed_here": False})
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    if sys.argv[1:2] == ["retrospective-census"]:
        retrospective_main(sys.argv[2:])
    else:
        main()
