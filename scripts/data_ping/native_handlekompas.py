#!/usr/bin/env python3
"""Native Handlekompas and official daily Compass owner.

The hourly Native Handlekompas remains a source-call-free readback of the pinned
Auto Market State. The official daily Compass is a frozen, auditable navigation
artifact derived from the same owner plus current Cycle Navigator context.
Neither surface has portfolio-execution or source-override authority.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.cycle_navigator.daily_price_journey import validated_public_copy
from scripts.data_ping.cycle_participation_readback import cycle_participation_readback

CONTRACT = "NATIVE_HANDLEKOMPAS_v1"
POINTER = "NATIVE_HANDLEKOMPAS_LATEST_POINTER_v1"
OFFICIAL_COMPASS_CONTRACT = "OFFICIAL_DAILY_COMPASS_v1"
# Schema 5 (AUDIT-04b, 2026-11-24): adds the descriptive blocks source_freshness, cn_band_status and
# risk_freshness. The version feeds compass_id, so every post-upgrade compass gets a new immutable slot and a
# pre-upgrade slot is never rewritten with different bytes.
OFFICIAL_COMPASS_SCHEMA_VERSION = 6  # independent descriptive participation; legacy projections unchanged
# V3_2 adds the explicit Main-Framework permission ceiling for proactive long-cycle actions.
OFFICIAL_COMPASS_DECISION_POLICY_VERSION = "2026-10-31_OBSERVED_MOMENTUM_SOURCE_SEPARATION_V4_1"
OFFICIAL_COMPASS_POINTER = "OFFICIAL_DAILY_COMPASS_LATEST_POINTER_v1"
PUBLIC_COMPASS_CONTRACT = "PUBLIC_COMPASS_PROJECTION_v1"
PUBLIC_COMPASS_POINTER = "PUBLIC_COMPASS_LATEST_POINTER_v1"
NEXT_12H_NOWCAST_SEMANTICS = "OBSERVED_MOMENTUM_NOT_FORECAST"
LEGACY_12H_SEMANTICS = "LEGACY_UNVERIFIED_NOT_FORWARD"
DEFAULT_AUTO_STATE_POINTER = Path("04_MARKET_LEARNING/entry_signals/auto_market_state/LATEST.json")
DEFAULT_CN_POINTER = Path("05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json")
CN_DECISION_PROJECTION_ADDENDUM = "DECISION_PROJECTION_ADDENDUM_v1.json"
DEFAULT_ROOT = Path("04_MARKET_LEARNING/handlekompas")
DEFAULT_OFFICIAL_ROOT = DEFAULT_ROOT / "official"

AUTHORITY = {
    "binding": False,
    "portfolio_execution": False,
    "canonical_state_change": False,
    "market_threshold_change": False,
    "model_weight_change": False,
    "owner_switch": False,
    "purpose": "CONCISE_NATIVE_MARKET_STATE_READBACK",
}

OFFICIAL_AUTHORITY = {
    "classification": "OFFICIAL_NAVIGATION_OUTPUT",
    "portfolio_execution": False,
    "source_override": False,
    "post_hoc_rewrite": False,
    "canonical_market_state_change": False,
    "market_threshold_change": False,
    "model_weight_change": False,
}

CAPITALIZATION_ORDER = ("BTC", "ETH", "LARGE_CAPS", "MID_CAPS", "SMALL_CAPS", "MICROCAPS", "MEMES")
HORIZON_ORDER = ("NEXT_12H", "NEXT_1_3D", "NEXT_5_7D", "NEXT_2_3W", "CYCLE_ALTCOINS_3_8W")
SCORED_HORIZON_ORDER = ("NEXT_12H", "NEXT_1_3D", "NEXT_5_7D")
ALTCOIN_STATES = {
    "DEFENSIVE", "CONSOLIDATION", "PRE_ROTATION", "ROTATION", "BROAD_ALTSEASON",
    "PARABOLIC_ALTSEASON", "DISTRIBUTION", "EXIT_RISK", "UNCLEAR",
}
ALTCOIN_WARNINGS = {
    "NONE", "PARABOLIC_ALTSEASON_WARNING", "DISTRIBUTION_WARNING",
    "EXIT_WARNING", "STRUCTURAL_BREAKDOWN_WARNING",
}
PROTECTION_RISK_STATES = {"NORMAL", "BUILDING", "ELEVATED", "HIGH", "CONFIRMED", "UNAVAILABLE"}
DISTRIBUTION_RISK_STATES = {"NONE", "WARNING", "CONFIRMED", "UNKNOWN"}
REENTRY_STATES = {"INACTIVE", "WAIT_FOR_FLUSH", "WAIT_FOR_RECLAIM", "REVIEW", "UNAVAILABLE"}
PROTECTION_RANK = {"UNAVAILABLE": -1, "NORMAL": 0, "BUILDING": 1, "ELEVATED": 2, "HIGH": 3, "CONFIRMED": 4}
LIMIT_TOKENS = ("QUOTA", "RATE_LIMIT", "USAGE_LIMIT", "429")
BUDGET_TOKENS = ("TOKEN", "CREDIT", "BUDGET", "INSUFFICIENT_FUNDS")
AUTH_TOKENS = ("AUTH", "UNAUTHORIZED", "FORBIDDEN", "401", "403", "API_KEY")


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def nested(value: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, Mapping):
            return None
        value = value.get(key)
    return value


def finite(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    out = float(value)
    return out if math.isfinite(out) else None


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def file_binding(repo_root: Path, rel_path: Path, *, raw: bytes | None = None) -> dict[str, Any]:
    path = repo_root / rel_path
    raw = path.read_bytes() if raw is None else raw
    blob = None
    try:
        blob = subprocess.check_output(
            ["git", "rev-parse", "--verify", f"HEAD:{rel_path.as_posix()}"],
            cwd=repo_root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        blob = None
    return {
        "path": rel_path.as_posix(),
        "content_sha256": digest(raw),
        "git_blob_sha": blob,
    }


def head_sha(repo_root: Path) -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True).strip()
    except Exception:
        return None


def load_auto_state(repo_root: Path, pointer_path: Path) -> Mapping[str, Any]:
    pointer = read_json(repo_root / pointer_path)
    packet_path = pointer.get("packet_path")
    if not isinstance(packet_path, str) or not packet_path:
        raise ValueError("AUTO_MARKET_STATE_POINTER_MISSING_PACKET_PATH")
    packet = read_json(repo_root / packet_path)
    if pointer.get("packet_sha256") != packet.get("packet_sha256"):
        raise ValueError("AUTO_MARKET_STATE_POINTER_HASH_MISMATCH")
    return packet


def load_auto_state_bundle(repo_root: Path, pointer_path: Path) -> tuple[Mapping[str, Any], Mapping[str, Any], Path]:
    pointer = read_json(repo_root / pointer_path)
    packet_path_raw = pointer.get("packet_path")
    if not isinstance(packet_path_raw, str) or not packet_path_raw:
        raise ValueError("AUTO_MARKET_STATE_POINTER_MISSING_PACKET_PATH")
    packet_path = Path(packet_path_raw)
    packet = read_json(repo_root / packet_path)
    if pointer.get("packet_sha256") != packet.get("packet_sha256"):
        raise ValueError("AUTO_MARKET_STATE_POINTER_HASH_MISMATCH")
    return pointer, packet, packet_path


def load_prior_compass(repo_root: Path, pointer_path: Path) -> Mapping[str, Any]:
    """Read prior protection/re-entry context only through its exact binding.

    An absent pointer may be handled by a first-issuance caller. A present but
    corrupt pointer must never be treated as an empty or trustworthy prior.
    """
    pointer = read_json(repo_root / pointer_path)
    if not isinstance(pointer, Mapping) or pointer.get("contract") != OFFICIAL_COMPASS_POINTER:
        raise ValueError("PRIOR_COMPASS_POINTER_INVALID")
    path_raw = pointer.get("compass_path")
    if not isinstance(path_raw, str) or not path_raw:
        raise ValueError("PRIOR_COMPASS_PATH_MISSING")
    path = (repo_root / path_raw).resolve()
    if not path.is_relative_to(repo_root.resolve()):
        raise ValueError("PRIOR_COMPASS_PATH_OUTSIDE_REPOSITORY")
    raw = path.read_bytes()
    if pointer.get("compass_content_sha256") != digest(raw):
        raise ValueError("PRIOR_COMPASS_CONTENT_HASH_MISMATCH")
    compass = json.loads(raw)
    if not isinstance(compass, Mapping) or compass.get("contract") != OFFICIAL_COMPASS_CONTRACT:
        raise ValueError("PRIOR_COMPASS_CONTRACT_INVALID")
    self_digest = digest(canon({key: value for key, value in compass.items() if key != "compass_sha256"}))
    if compass.get("compass_sha256") != self_digest or pointer.get("compass_sha256") != self_digest:
        raise ValueError("PRIOR_COMPASS_SELF_HASH_MISMATCH")
    compass_id = compass.get("compass_id")
    issued = compass.get("issued_at_utc")
    if (not isinstance(compass_id, str) or not compass_id
            or pointer.get("compass_id") != compass_id or path.stem != compass_id
            or _parse_utc(issued) is None or pointer.get("issued_at_utc") != issued):
        raise ValueError("PRIOR_COMPASS_IDENTITY_MISMATCH")
    return compass


CN_OFFLINE_ISSUER_METHOD = "CN_OWNER_AUTHORIZED_API_FREE_SEVEN_DAY_v1"


def cn_issuer_method(cn_package: Mapping[str, Any] | None) -> str:
    """K10 (2026-11-19): which issuer produced the weekly CN. W46/W47 predate the explicit field and state the
    method only in their readable text; those immutable packages are classified from that text, never rewritten."""
    if not isinstance(cn_package, Mapping):
        return "UNAVAILABLE"
    explicit = cn_package.get("issuer_method")
    if isinstance(explicit, str) and explicit:
        return explicit
    text = cn_package.get("readable_markdown")
    if isinstance(text, str) and ("Method: " + CN_OFFLINE_ISSUER_METHOD) in text:
        return CN_OFFLINE_ISSUER_METHOD
    return "UNSTATED"


def cn_protection_state_basis(cn_package: Mapping[str, Any] | None) -> str:
    """K11: an offline-issued protection state is carried forward, not re-evaluated."""
    if not isinstance(cn_package, Mapping):
        return "UNAVAILABLE"
    protection = _cn_decision_projection(cn_package).get("protection") if isinstance(_cn_decision_projection(cn_package), Mapping) else None
    basis = protection.get("state_basis") if isinstance(protection, Mapping) else None
    if isinstance(basis, str) and basis:
        return basis
    return "INHERITED_FROM_PRIOR_ISSUE" if cn_issuer_method(cn_package) == CN_OFFLINE_ISSUER_METHOD else "UNSTATED"


def load_cn_context(repo_root: Path, pointer_path: Path = DEFAULT_CN_POINTER) -> tuple[Mapping[str, Any] | None, dict[str, Any]]:
    path = repo_root / pointer_path
    if not path.exists():
        return None, {"status": "UNAVAILABLE", "reason": "CN_POINTER_MISSING"}
    pointer = read_json(path)
    week_dir = pointer.get("week_dir")
    if not isinstance(week_dir, str) or not week_dir:
        return None, {"status": "UNAVAILABLE", "reason": "CN_WEEK_DIR_MISSING"}
    package_path = Path(week_dir) / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json"
    abs_package = repo_root / package_path
    if not abs_package.exists():
        return None, {"status": "UNAVAILABLE", "reason": "CN_MACHINE_PACKAGE_MISSING"}
    # Bind the exact bytes we parse, before consuming any protection or
    # forecast projection. Matching the issue number alone is not custody.
    package_raw = abs_package.read_bytes()
    package_sha = digest(package_raw)
    declared_sha = pointer.get("machine_package_sha256")
    if not isinstance(declared_sha, str) or not declared_sha:
        return None, {"status": "DEGRADED", "reason": "CN_POINTER_PACKAGE_HASH_MISSING"}
    if declared_sha != package_sha:
        return None, {"status": "DEGRADED", "reason": "CN_POINTER_PACKAGE_HASH_MISMATCH"}
    package = json.loads(package_raw)
    if pointer.get("issue_number") != package.get("issue_number"):
        return None, {"status": "DEGRADED", "reason": "CN_POINTER_PACKAGE_ISSUE_MISMATCH"}

    binding: dict[str, Any] = {
        "status": "PASS",
        "pointer": file_binding(repo_root, pointer_path),
        "machine_package": file_binding(repo_root, package_path, raw=package_raw),
        "issue_number": package.get("issue_number"),
        "iso_week": pointer.get("iso_week"),
        "iso_year": pointer.get("iso_year"),
        "decision_projection_source": "MACHINE_PACKAGE",
    }

    # Transitional compatibility is append-only. A legacy weekly freeze is
    # never rewritten. A sidecar may only supply the typed projection when it
    # is hash-bound to the exact frozen machine package and explicitly declares
    # zero forecast-rewrite authority.
    if not _cn_decision_projection(package):
        addendum_path = Path(week_dir) / CN_DECISION_PROJECTION_ADDENDUM
        abs_addendum = repo_root / addendum_path
        if abs_addendum.exists():
            addendum = read_json(abs_addendum)
            valid = (
                isinstance(addendum, Mapping)
                and addendum.get("contract") == "CYCLE_NAVIGATOR_DECISION_PROJECTION_ADDENDUM_v1"
                and addendum.get("base_machine_package_sha256") == package_sha
                and addendum.get("forecast_rewrite") is False
                and addendum.get("portfolio_execution") is False
                and isinstance(addendum.get("decision_projection"), Mapping)
                and str(nested(addendum, "decision_projection", "contract") or "")
                == "CYCLE_NAVIGATOR_DECISION_PROJECTION_v1"
            )
            binding["decision_projection_addendum"] = file_binding(repo_root, addendum_path)
            if valid:
                package = dict(package)
                package["decision_projection"] = addendum["decision_projection"]
                binding["decision_projection_source"] = "HASH_BOUND_COMPATIBILITY_ADDENDUM"
            else:
                binding["decision_projection_source"] = "INVALID_COMPATIBILITY_ADDENDUM_IGNORED"
    return package, binding


def classify_provider_health(auto_state: Mapping[str, Any]) -> dict[str, Any]:
    health = auto_state.get("source_health") or {}
    issues: list[dict[str, Any]] = []
    for lane, row in sorted(health.items() if isinstance(health, Mapping) else []):
        if not isinstance(row, Mapping):
            continue
        status = str(row.get("status") or "UNKNOWN")
        if status == "PASS":
            continue
        classification = str(row.get("classification") or "UNKNOWN")
        text = f"{classification} {row.get('detail','')}".upper()
        if any(token in text for token in LIMIT_TOKENS):
            issue_class = "QUOTA_OR_RATE_LIMIT"
        elif any(token in text for token in BUDGET_TOKENS):
            issue_class = "TOKEN_OR_BUDGET_EXHAUSTION"
        elif any(token in text for token in AUTH_TOKENS):
            issue_class = "AUTHENTICATION_OR_PERMISSION"
        else:
            issue_class = "SOURCE_OR_RUNTIME_DEGRADATION"
        issues.append({"lane": lane, "status": status, "classification": classification, "issue_class": issue_class})
    cfgi = next((row for row in issues if row["lane"] == "sentiment"), None)
    return {
        "status": "DEGRADED" if issues else "PASS",
        "cfgi": cfgi or {"status": "PASS_OR_NOT_EXPLICITLY_DEGRADED", "issue_class": None},
        "issues": issues,
    }


def budget_health(auto_state: Mapping[str, Any], external_budget: Mapping[str, Any] | None = None) -> dict[str, Any]:
    provider = classify_provider_health(auto_state)
    exhaustion = [row for row in provider["issues"] if row["issue_class"] in {"QUOTA_OR_RATE_LIMIT", "TOKEN_OR_BUDGET_EXHAUSTION"}]
    if isinstance(external_budget, Mapping):
        status = external_budget.get("status") or external_budget.get("budget_status")
        remaining = external_budget.get("remaining_monthly_budget")
        spent = external_budget.get("month_to_date_spend")
        providers = external_budget.get("providers") if isinstance(external_budget.get("providers"), Mapping) else {}
        external_signals: list[dict[str, Any]] = []
        for name, row in sorted(providers.items()):
            if not isinstance(row, Mapping):
                continue
            provider_status = str(row.get("status") or "UNKNOWN")
            if provider_status in {"EXHAUSTED", "LOW_INSUFFICIENT_FOR_NEXT_STANDARD_CALL"}:
                external_signals.append({
                    "provider": str(name),
                    "status": provider_status,
                    "reason": row.get("reason"),
                    "credits_remaining": row.get("credits_remaining"),
                    "current_standard_call_expected_credits": row.get("current_standard_call_expected_credits"),
                })
        if status or remaining is not None or spent is not None or providers:
            effective = str(status or "AVAILABLE")
            if external_signals:
                effective = "DEGRADED"
            return {
                "status": effective,
                "scope": external_budget.get("scope"),
                "exact_monthly_spend_available": spent is not None,
                "exact_remaining_budget_available": remaining is not None,
                "month_to_date_spend": spent,
                "remaining_monthly_budget": remaining,
                "source": "BOUND_EXTERNAL_BUDGET_STATUS",
                "providers": providers,
                "provider_signals": exhaustion + external_signals,
            }
    if exhaustion:
        return {
            "status": "DEGRADED",
            "exact_monthly_spend_available": False,
            "exact_remaining_budget_available": False,
            "reason": "OBSERVED_PROVIDER_QUOTA_TOKEN_OR_BUDGET_SIGNAL",
            "provider_signals": exhaustion,
        }
    return {
        "status": "UNKNOWN_EXACT_SPEND_NO_EXHAUSTION_SIGNAL",
        "exact_monthly_spend_available": False,
        "exact_remaining_budget_available": False,
        "reason": "NO_ACCOUNT_LEVEL_COST_LEDGER_BOUND_TO_THIS_PACKET",
        "provider_signals": [],
    }


def action_context(auto_state: Mapping[str, Any], *, as_of: datetime | None = None) -> dict[str, Any]:
    """Translate current canonical owner state without reviving retired proxy gates.

    The 12 July governance retirement gives Top-100 breadth and ETHBTC > 0.03
    zero action weight. They remain visible as descriptive context only.
    """
    ns = auto_state.get("normalized_state") or {}
    live = ns.get("live_market") or {}
    breadth = nested(ns, "breadth", "aggregate") or {}
    entry = ns.get("entry_signal_reference") or {}
    ratio = finite(live.get("ethbtc"))
    advance = finite(breadth.get("advance_ratio"))
    blockers = _core_blockers(auto_state)
    alt_blockers = [lane for lane in list(auto_state.get("blockers") or []) if lane in ALT_SCOPED_LANES]
    validation = str(auto_state.get("validation_status") or "UNKNOWN")
    entry_state = entry.get("state") if isinstance(entry, Mapping) else None

    healthy = (
        validation != "FAIL"
        and _core_decision_ready(auto_state)
        and _health_ok(auto_state, as_of)
    )

    # IMPORTANT: legacy GRADUATED_ALTCOIN_TOPUP_ACTIVE observations are
    # FORWARD_ONLY_NOT_PROMOTION_READY. A later canonical promotion must
    # deliberately update this implementation; an observer label cannot grant
    # action authority by itself.
    now = "HOLD_WAIT" if healthy else "HOLD_WAIT_DATA_DEGRADED"

    why: list[str] = []
    if ratio is not None:
        why.append(f"DESCRIPTIVE_ETHBTC={ratio:.6f}")
    if advance is not None:
        why.append(f"DESCRIPTIVE_TOP100_BREADTH={advance:.2f}")
    if entry_state:
        why.append(f"ENTRY_SIGNAL_OBSERVER={entry_state}")
    why.append("BREADTH_ACTION_AUTHORITY=RETIRED_ZERO_WEIGHT")
    if blockers:
        why.append("BLOCKERS=" + ",".join(blockers))
    if alt_blockers:
        why.append("ALT_CONTEXT_DEGRADED=" + ",".join(alt_blockers))

    return {
        "NOW": now,
        "PREPARE": "ONLY_EXPLICIT_CANONICAL_PROMOTION_OR_REGISTERED_DECISION_OWNER_CAN_SET_PREPARE",
        "TOPUP_GATE": "RETIRED_BREADTH_ETHBTC_PROXY_HAS_ZERO_ACTION_WEIGHT; FUTURE_PROMOTION_REQUIRES_DELIBERATE_CANONICAL_IMPLEMENTATION_CHANGE",
        "RISK_DOWN": "ONLY_CANONICAL_PROTECTION_OR_DECISION_OWNER_CAN_ESCALATE_RISK; RETIRED_BREADTH_ETHBTC_PROXIES_ARE_DESCRIPTIVE_ONLY",
        "WHY": why,
        "proxy_authority": {
            "top100_breadth_action_weight": 0,
            "ethbtc_0_03_gate_action_weight": 0,
            "legacy_entry_observer_action_authority": False,
        },
    }


def build(auto_state: Mapping[str, Any], *, external_budget: Mapping[str, Any] | None = None, now: datetime | None = None) -> dict[str, Any]:
    generated = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(microsecond=0)
    provider = classify_provider_health(auto_state)
    freshness = owner_freshness(auto_state, generated)
    source_validation = str(auto_state.get("validation_status") or "UNKNOWN")
    decision_context_status = str(auto_state.get("decision_context_status") or "UNKNOWN")
    decision_ready = (
        source_validation != "FAIL"
        and _core_decision_ready(auto_state)
    )
    # Optional/non-decision lanes remain visible in provider/source health, but
    # must not alone suppress a healthy governed Compass decision context.
    effective_data_status = "PASS" if decision_ready and freshness.get("status") == "PASS" else "DEGRADED"
    native_action = action_context(auto_state, as_of=generated)
    market_direction = derive_market_now(auto_state, native_action, as_of=generated)
    packet = {
        "contract": CONTRACT,
        "generated_at_utc": generated.isoformat().replace("+00:00", "Z"),
        "source": {
            "contract": auto_state.get("contract"),
            "packet_generated_at_utc": auto_state.get("packet_generated_at_utc"),
            "packet_sha256": auto_state.get("packet_sha256"),
            "source_snapshot_commit_sha": nested(auto_state, "source_snapshot", "exact_commit_sha"),
            "validation_status": auto_state.get("validation_status"),
            "decision_context_status": auto_state.get("decision_context_status"),
        },
        "action": native_action,
        "market_direction": market_direction,
        "DATA_HEALTH": {
            "status": effective_data_status,
            "source_validation_status": auto_state.get("validation_status"),
            "decision_context_status": auto_state.get("decision_context_status"),
            "blockers": list(auto_state.get("blockers") or []),
            "optional_degraded_lanes": list(auto_state.get("optional_degraded_lanes") or []),
            "alt_context_status": "USABLE" if _alt_context_usable(auto_state) else "DEGRADED_ALT_OUTPUTS_UNAVAILABLE",
            "owner_freshness": freshness,
            "provider_health": provider,
        },
        "BUDGET_HEALTH": budget_health(auto_state, external_budget),
        "manual_market_data_required": False,
        "authority": AUTHORITY,
    }
    packet["handlekompas_sha256"] = digest(canon({k: v for k, v in packet.items() if k != "handlekompas_sha256"}))
    return packet


def write(packet: Mapping[str, Any], output_root: Path) -> dict[str, Any]:
    dt = datetime.fromisoformat(str(packet["generated_at_utc"]).replace("Z", "+00:00"))
    path = output_root / "runs" / dt.strftime("%Y/%m/%d") / f"{dt:%H%M%S}_{packet['handlekompas_sha256'][:12]}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canon(packet))
    output_root.mkdir(parents=True, exist_ok=True)
    pointer = {
        "contract": POINTER,
        "handlekompas_path": path.as_posix(),
        "handlekompas_sha256": packet["handlekompas_sha256"],
        "generated_at_utc": packet["generated_at_utc"],
        "source_packet_sha256": nested(packet, "source", "packet_sha256"),
        "NOW": nested(packet, "action", "NOW"),
        "data_health": nested(packet, "DATA_HEALTH", "status"),
        "budget_health": nested(packet, "BUDGET_HEALTH", "status"),
        "manual_market_data_required": False,
        "authority": AUTHORITY,
    }
    (output_root / "LATEST.json").write_bytes(canon(pointer))
    return {"path": path.as_posix(), "pointer": (output_root / "LATEST.json").as_posix(), "sha256": packet["handlekompas_sha256"]}


def _feature(
    feature_id: str,
    value: Any,
    unit: str | None,
    source: str,
    observed_at: Any,
    health: Any,
    *,
    source_owner: str | None = None,
    retrieved_at: Any = None,
) -> dict[str, Any]:
    normalized = value if value is None or isinstance(value, (str, int, float, bool)) else None
    if normalized is None:
        eligibility = "MISSING"
    elif health == "PASS":
        eligibility = "ELIGIBLE_PRESENT"
    else:
        eligibility = "CONTEXT_ONLY_OR_DEGRADED"
    return {
        "feature_id": feature_id,
        "value": normalized,
        "unit": unit,
        "source_path": source,
        "source_owner": source_owner,
        "observed_at": observed_at,
        "retrieved_at": retrieved_at,
        "freshness_state": health or "UNKNOWN",
        "eligibility": eligibility,
    }


def _funding_clock_metadata(auto_state: Mapping[str, Any], funding: Any) -> dict[str, Any]:
    """Keep settlement separate from the bound capture clock, which is not vendor first-known."""
    settlement = None
    raw = funding.get("funding_time") if isinstance(funding, Mapping) else None
    if isinstance(raw, int) and not isinstance(raw, bool) and 10**12 <= raw < 10**13:
        try:
            settlement = datetime.fromtimestamp(raw / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z")
        except (OverflowError, OSError, ValueError):
            pass

    health = nested(auto_state, "source_health", "live_anchor")
    health = health if isinstance(health, Mapping) else {}
    target = nested(health, "provenance", "target")
    target = target if isinstance(target, Mapping) else {}
    snapshot_sha = nested(auto_state, "source_snapshot", "exact_commit_sha")
    stamp = nested(health, "freshness", "retrieval_freshness", "timestamp")
    capture = _parse_utc(stamp) if isinstance(stamp, str) and stamp.endswith("Z") else None
    packet = _parse_utc(auto_state.get("packet_generated_at_utc"))
    bound = (
        health.get("status") == "PASS"
        and nested(health, "freshness", "retrieval_freshness", "status") == "PASS"
        and isinstance(snapshot_sha, str) and len(snapshot_sha) == 40
        and target.get("exact_commit_sha") == snapshot_sha
        and target.get("exact_path") == health.get("target_path")
        and isinstance(health.get("target_path"), str) and bool(health["target_path"])
        and isinstance(target.get("git_blob_sha"), str) and len(target["git_blob_sha"]) == 40
        and capture is not None and packet is not None and capture <= packet
    )
    return {
        "settlement_at_utc": settlement,
        "observed_at": None,
        "retrieved_at": None,
        "source_batch_captured_at_utc": stamp if bound else None,
        "quote_clock_status": "CAPTURE_ONLY_PROVIDER_FIRST_KNOWN_UNKNOWN" if bound else "UNKNOWN_NOT_PIT_ADMITTED",
    }


def evidence_snapshot(auto_state: Mapping[str, Any], packet_path: Path) -> dict[str, Any]:
    ns = auto_state.get("normalized_state") or {}
    live = ns.get("live_market") or {}
    rich_breadth = ns.get("breadth") or {}
    current_breadth = ns.get("current_breadth") or {}
    breadth_aggregate = rich_breadth.get("aggregate") or {}
    derivatives = ns.get("derivatives") or {}
    derivative_hourly = derivatives.get("hourly") or {}
    derivative_live = derivatives.get("live_anchor") or {}
    dominance = ns.get("btc_dominance") or {}
    etf = ns.get("settled_etf") or {}
    stable = ns.get("stablecoin_liquidity") or {}
    sentiment = ns.get("sentiment") or {}
    cfgi = nested(sentiment, "cfgi") or {}
    cfgi_symbols = cfgi.get("symbols") if isinstance(cfgi, Mapping) else {}
    cfgi_symbols = cfgi_symbols if isinstance(cfgi_symbols, Mapping) else {}
    btc_sentiment = cfgi_symbols.get("BTC") if isinstance(cfgi_symbols.get("BTC"), Mapping) else {}
    eth_sentiment = cfgi_symbols.get("ETH") if isinstance(cfgi_symbols.get("ETH"), Mapping) else {}
    market_sentiment = cfgi_symbols.get("MARKET") if isinstance(cfgi_symbols.get("MARKET"), Mapping) else {}
    altseason = ns.get("altseason_context") or {}
    source_health = auto_state.get("source_health") or {}
    altseason_bc = nested(altseason, "blockchaincenter_altcoin_season")
    altseason_value = finite(nested(altseason_bc, "horizons", "90", "published_score"))
    altseason_observed = nested(altseason_bc, "observation_date_utc")
    altseason_retrieved = nested(altseason_bc, "retrieved_at_utc")
    altseason_health = nested(source_health, "altseason_context", "status")
    # Explicit opt-in: only when the upstream owner itself marked the lane
    # DEGRADED_CARRY (<= 72h) and the current value is missing, show the last
    # valid BC 90d value as degraded context with its age. Never PASS.
    altseason_carry = ns.get("altseason_carry") if altseason_health == "DEGRADED_CARRY" else None
    altseason_carry_used = (
        altseason_value is None and isinstance(altseason_carry, Mapping)
        and finite(altseason_carry.get("value")) is not None
    )
    if altseason_carry_used:
        altseason_value = finite(altseason_carry.get("value"))
        altseason_observed = altseason_carry.get("source_observation_date_utc")
        altseason_retrieved = altseason_carry.get("source_retrieved_at_utc")
    packet_observed = auto_state.get("packet_generated_at_utc")
    packet_source = packet_path.as_posix()

    hourly_health = nested(source_health, "hourly_market", "status")
    breadth_health = nested(source_health, "breadth", "status")
    derivatives_health = nested(source_health, "derivatives", "status")
    sentiment_health = nested(source_health, "sentiment", "status")

    breadth_ratio = finite(current_breadth.get("advance_ratio"))
    if breadth_ratio is None:
        breadth_ratio = finite(breadth_aggregate.get("advance_ratio"))
    breadth_advancers = finite(current_breadth.get("advancers"))
    if breadth_advancers is None:
        breadth_advancers = finite(breadth_aggregate.get("advancers"))
    breadth_decliners = finite(current_breadth.get("decliners"))
    if breadth_decliners is None:
        breadth_decliners = finite(breadth_aggregate.get("decliners"))
    breadth_observed = current_breadth.get("observed_at_utc") or rich_breadth.get("retrieved_at_utc")

    btc_oi = finite(derivative_hourly.get("btc_open_interest"))
    eth_oi = finite(derivative_hourly.get("eth_open_interest"))
    btc_funding = finite(nested(derivative_live, "BTC-USDT-SWAP", "funding", "funding_rate"))
    eth_funding = finite(nested(derivative_live, "ETH-USDT-SWAP", "funding", "funding_rate"))
    derivative_hourly_observed = derivative_hourly.get("observation_open_utc") or live.get("observation_open_utc")

    rows = [
        _feature("btc_usdt", finite(live.get("btc_usdt")), "USDT", packet_source, live.get("observation_open_utc"), hourly_health, source_owner="HOURLY_SEQUENCE"),
        _feature("eth_usdt", finite(live.get("eth_usdt")), "USDT", packet_source, live.get("observation_open_utc"), hourly_health, source_owner="HOURLY_SEQUENCE"),
        _feature("ethbtc", finite(live.get("ethbtc")), "ratio", packet_source, live.get("observation_open_utc"), hourly_health, source_owner="HOURLY_SEQUENCE"),
        _feature("breadth_advance_ratio", breadth_ratio, "ratio", packet_source, breadth_observed, breadth_health, source_owner=str(current_breadth.get("source") or "RICH_BREADTH_OWNER")),
        _feature("breadth_advancers", breadth_advancers, "count", packet_source, breadth_observed, breadth_health, source_owner=str(current_breadth.get("source") or "RICH_BREADTH_OWNER")),
        _feature("breadth_decliners", breadth_decliners, "count", packet_source, breadth_observed, breadth_health, source_owner=str(current_breadth.get("source") or "RICH_BREADTH_OWNER")),
        _feature("breadth_equal_weight_24h", finite(breadth_aggregate.get("equal_weight_mean_return_24h_pct")), "pct", packet_source, rich_breadth.get("retrieved_at_utc"), breadth_health, source_owner="RICH_BREADTH_OWNER"),
        _feature("btc_dominance_pct", finite(dominance.get("value_pct")), "pct", packet_source, dominance.get("source_timestamp"), nested(source_health, "btc_dominance", "status"), source_owner="COINMARKETCAP_BTC_D", retrieved_at=dominance.get("source_verified_timestamp")),
        _feature("btc_etf_musd", finite(etf.get("btc_reported_total_musd")), "MUSD", packet_source, etf.get("session_date"), nested(source_health, "settled_etf", "status"), source_owner="FARSIDE_SETTLED_ETF", retrieved_at=etf.get("retrieved_at_utc")),
        _feature("eth_etf_musd", finite(etf.get("eth_reported_total_musd")), "MUSD", packet_source, etf.get("session_date"), nested(source_health, "settled_etf", "status"), source_owner="FARSIDE_SETTLED_ETF", retrieved_at=etf.get("retrieved_at_utc")),
        _feature("stablecoin_total_usd", finite(stable.get("total_usd")), "USD", packet_source, stable.get("source_timestamp"), nested(source_health, "stablecoin_liquidity", "status"), source_owner="DEFILLAMA_STABLECOINS", retrieved_at=stable.get("retrieved_at_utc")),
        _feature("btc_open_interest", btc_oi, "contracts", packet_source, derivative_hourly_observed, derivatives_health, source_owner="OKX_HOURLY_DERIVATIVES"),
        _feature("eth_open_interest", eth_oi, "contracts", packet_source, derivative_hourly_observed, derivatives_health, source_owner="OKX_HOURLY_DERIVATIVES"),
        _feature("btc_funding", btc_funding, "rate", packet_source, None, derivatives_health, source_owner="OKX_LIVE_SWAP"),
        _feature("eth_funding", eth_funding, "rate", packet_source, None, derivatives_health, source_owner="OKX_LIVE_SWAP"),
        _feature("sentiment_state", market_sentiment.get("classification"), None, packet_source, market_sentiment.get("timestamp"), sentiment_health, source_owner="CFGI", retrieved_at=cfgi.get("retrieved_at_utc")),
        _feature("sentiment_market_score", finite(market_sentiment.get("score")), "index", packet_source, market_sentiment.get("timestamp"), sentiment_health, source_owner="CFGI", retrieved_at=cfgi.get("retrieved_at_utc")),
        _feature("sentiment_btc_score", finite(btc_sentiment.get("score")), "index", packet_source, btc_sentiment.get("timestamp"), sentiment_health, source_owner="CFGI", retrieved_at=cfgi.get("retrieved_at_utc")),
        _feature("sentiment_eth_score", finite(eth_sentiment.get("score")), "index", packet_source, eth_sentiment.get("timestamp"), sentiment_health, source_owner="CFGI", retrieved_at=cfgi.get("retrieved_at_utc")),
        _feature("altseason_score_90d", altseason_value, "index", packet_source, altseason_observed, altseason_health, source_owner="BLOCKCHAINCENTER", retrieved_at=altseason_retrieved),
        _feature("entry_signal_state", nested(ns, "entry_signal_reference", "state"), None, packet_source, nested(ns, "entry_signal_reference", "generated_at_utc"), nested(source_health, "entry_signal_reference", "status"), source_owner="ENTRY_SIGNAL_LEDGER"),
        _feature("btc_delta_since_prior_packet_pct", _delta_pct(auto_state, "btc_usdt"), "pct", packet_source, live.get("observation_open_utc"), hourly_health, source_owner="AUTO_MARKET_STATE_DELTA"),
        _feature("eth_delta_since_prior_packet_pct", _delta_pct(auto_state, "eth_usdt"), "pct", packet_source, live.get("observation_open_utc"), hourly_health, source_owner="AUTO_MARKET_STATE_DELTA"),
        _feature("ethbtc_delta_since_prior_packet_pct", _delta_pct(auto_state, "ethbtc"), "pct", packet_source, live.get("observation_open_utc"), hourly_health, source_owner="AUTO_MARKET_STATE_DELTA"),
    ]
    for row in rows:
        if row["feature_id"] in ("btc_funding", "eth_funding"):
            symbol = "BTC-USDT-SWAP" if row["feature_id"] == "btc_funding" else "ETH-USDT-SWAP"
            row.update(_funding_clock_metadata(auto_state, nested(derivative_live, symbol, "funding")))
        if row["feature_id"] == "altseason_score_90d" and altseason_carry_used:
            row.update({
                "value_semantics": "DEGRADED_CARRY_LAST_VALID_BC_90D_NOT_FRESH",
                "carry_age_hours": altseason_carry.get("age_hours"),
                "carry_max_age_hours": altseason_carry.get("max_age_hours"),
                "carry_source_packet_generated_at_utc": altseason_carry.get("source_packet_generated_at_utc"),
            })
    available = sum(row["value"] is not None for row in rows)
    missing = [row["feature_id"] for row in rows if row["value"] is None]
    pass_lane_missing = [
        row["feature_id"] for row in rows
        if row["value"] is None and row["freshness_state"] == "PASS"
    ]
    return {
        "selected_features": rows,
        "available_features": available,
        "expected_selected_features": len(rows),
        "missing_feature_ids": missing,
        "pass_lane_missing_feature_ids": pass_lane_missing,
        "mapping_integrity_status": "PASS" if not pass_lane_missing else "FAIL_PASS_LANE_MISSING_VALUE",
        "breadth_temporal_selection": current_breadth or None,
        "full_feature_universe_reference": {
            "contract": auto_state.get("contract"),
            "packet_path": packet_source,
            "packet_sha256": auto_state.get("packet_sha256"),
            "note": "Full immutable upstream packet is the backtest feature universe; selected_features is a compact index, not a forced 100-field schema.",
        },
    }

def _delta_pct(auto_state: Mapping[str, Any], key: str) -> float | None:
    return finite(nested(auto_state, "deltas_since_prior_auto_packet", key, "pct"))


def _parse_utc(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def owner_freshness(auto_state: Mapping[str, Any], as_of: datetime) -> dict[str, Any]:
    """Re-evaluate the upstream owner's own freshness contract at issuance time."""
    as_of = as_of.astimezone(timezone.utc)
    packet_time = _parse_utc(auto_state.get("packet_generated_at_utc"))
    freshness = nested(auto_state, "source_health", "hourly_market", "freshness")
    reasons: list[str] = []
    checks: list[dict[str, Any]] = []
    owner_max_ages: list[float] = []
    if packet_time is None:
        reasons.append("PACKET_TIMESTAMP_MISSING")
    if not isinstance(freshness, Mapping):
        reasons.append("OWNER_FRESHNESS_POLICY_MISSING")
    else:
        if str(freshness.get("status") or "UNKNOWN") != "PASS":
            reasons.append("OWNER_FRESHNESS_STATUS_NOT_PASS")
        for lane in (
            "pointer_freshness", "retrieval_freshness", "session_coverage_freshness",
            "source_observation_freshness",
        ):
            row = freshness.get(lane)
            if not isinstance(row, Mapping):
                continue
            # The upstream vector permits explicitly unavailable optional
            # dimensions. A present observation, however, cannot borrow a
            # different dimension's TTL or disappear from issuance checks.
            if (row.get("status") == "UNAVAILABLE" and row.get("timestamp") is None
                    and row.get("max_age_seconds") is None):
                continue
            maximum = finite(row.get("max_age_seconds"))
            stamp = _parse_utc(row.get("timestamp"))
            if maximum is None or maximum < 0:
                reasons.append(f"{lane.upper()}_MAX_AGE_UNAVAILABLE")
                continue
            owner_max_ages.append(maximum)
            if stamp is None:
                reasons.append(f"{lane.upper()}_TIMESTAMP_MISSING")
                checks.append({"lane": lane, "status": "UNAVAILABLE", "age_seconds": None, "max_age_seconds": maximum})
                continue
            age = (as_of - stamp).total_seconds()
            status = "PASS" if 0 <= age <= maximum and str(row.get("status") or "UNKNOWN") == "PASS" else "STALE"
            if status != "PASS":
                reasons.append(f"{lane.upper()}_STALE")
            checks.append({"lane": lane, "status": status, "age_seconds": age, "max_age_seconds": maximum, "timestamp": row.get("timestamp")})
    if not owner_max_ages:
        reasons.append("OWNER_FRESHNESS_MAX_AGE_UNAVAILABLE")
    if packet_time is not None and owner_max_ages:
        maximum = min(owner_max_ages)
        age = (as_of - packet_time).total_seconds()
        status = "PASS" if 0 <= age <= maximum else "STALE"
        if status != "PASS":
            reasons.append("PACKET_TIMESTAMP_STALE")
        checks.append({
            "lane": "auto_market_state_packet", "status": status, "age_seconds": age,
            "max_age_seconds": maximum, "timestamp": auto_state.get("packet_generated_at_utc"),
        })
    return {
        "status": "PASS" if not reasons else "STALE_OR_UNAVAILABLE",
        "evaluated_at_utc": as_of.isoformat().replace("+00:00", "Z"),
        "packet_generated_at_utc": auto_state.get("packet_generated_at_utc"),
        "reasons": reasons,
        "checks": checks,
    }


# Lane-scoped degradation (2026-11-19, Research Closure RC09/K06). altseason_context is CONTEXT_ONLY for the
# BTC/ETH core: one failed BlockchainCenter scrape blanked direction, every horizon, the ladder and protection
# (7 episodes since 2026-09-26, about 46 h). It still blocks every altcoin output (the 3-8w altcoin cycle lane
# and every alt ladder rung) unless its health is PASS or the <=72 h DEGRADED_CARRY of #2244. The upstream
# registry, blockers list and native recovery stay unchanged: this only stops a context lane from failing the core.
ALT_SCOPED_LANES = frozenset({"altseason_context"})
ALT_CONTEXT_USABLE = frozenset({"PASS", "DEGRADED_CARRY"})
ALT_LADDER_SEGMENTS = frozenset({"LARGE_CAPS", "MID_CAPS", "SMALL_CAPS", "MICROCAPS"})


def _core_blockers(auto_state: Mapping[str, Any]) -> list[str]:
    return [lane for lane in list(auto_state.get("blockers") or []) if lane not in ALT_SCOPED_LANES]


def _alt_context_usable(auto_state: Mapping[str, Any]) -> bool:
    """Alt outputs fail closed only when the producer listed altseason_context as a blocker and its health is
    neither PASS nor the bounded DEGRADED_CARRY (the producer lists any non-PASS required lane as a blocker)."""
    if "altseason_context" not in list(auto_state.get("blockers") or []):
        return True
    status = nested(auto_state, "source_health", "altseason_context", "status")
    return str(status or "") in ALT_CONTEXT_USABLE


def _core_decision_ready(auto_state: Mapping[str, Any]) -> bool:
    """decision_context PASS, or DEGRADED only because of alt-scoped context lanes."""
    blockers = list(auto_state.get("blockers") or [])
    status = str(auto_state.get("decision_context_status") or "UNKNOWN")
    if _core_blockers(auto_state):
        return False
    return status == "PASS" or (status == "DEGRADED" and bool(blockers))


def _health_ok(auto_state: Mapping[str, Any], as_of: datetime | None = None) -> bool:
    validation = str(auto_state.get("validation_status") or "UNKNOWN")
    structural = (
        validation != "FAIL"
        and _core_decision_ready(auto_state)
    )
    if not structural:
        return False
    return as_of is None or owner_freshness(auto_state, as_of)["status"] == "PASS"


def derive_market_now(auto_state: Mapping[str, Any], action: Mapping[str, Any], *, as_of: datetime | None = None) -> dict[str, Any]:
    """Describe current market direction independently from action permission.

    Direction answers what the observed market is doing. Action permission answers
    what the governed portfolio layer is allowed to do. A bearish market may still
    map to HOLD; a bullish market may still map to WAIT/HOLD.
    """
    posture = str(action.get("NOW") or "HOLD_WAIT")
    if not _health_ok(auto_state, as_of):
        return {
            "directional_state": "UNAVAILABLE",
            "regime": "DATA_DEGRADED",
            "action_permission": posture,
            "btc_delta_pct": _delta_pct(auto_state, "btc_usdt"),
            "eth_delta_pct": _delta_pct(auto_state, "eth_usdt"),
            "ethbtc_delta_pct": _delta_pct(auto_state, "ethbtc"),
            "eth_relative_state": "UNAVAILABLE",
            "summary": "Current market direction is unavailable because required state is degraded.",
        }

    btc = _delta_pct(auto_state, "btc_usdt")
    eth = _delta_pct(auto_state, "eth_usdt")
    ethbtc = _delta_pct(auto_state, "ethbtc")
    current_observation = nested(auto_state, "normalized_state", "live_market", "observation_open_utc")
    prior_observation = nested(auto_state, "predecessor", "market_observation_open_utc")
    same_price_observation = bool(
        isinstance(current_observation, str)
        and current_observation
        and isinstance(prior_observation, str)
        and current_observation == prior_observation
    )
    no_new_price_observation = bool(
        same_price_observation
        and btc == 0
        and eth == 0
        and (ethbtc == 0 or ethbtc is None)
    )

    if no_new_price_observation:
        direction = "UNCHANGED_NO_NEW_OBSERVATION"
    elif btc is None or eth is None:
        direction = "MIXED"
    elif btc > 0 and eth > 0:
        direction = "BULLISH"
    elif btc < 0 and eth < 0:
        direction = "BEARISH"
    elif btc == 0 and eth == 0:
        direction = "NEUTRAL"
    else:
        direction = "MIXED"

    if no_new_price_observation:
        relative = "NO_NEW_OBSERVATION"
    elif ethbtc is None:
        relative = "UNAVAILABLE"
    elif ethbtc > 0:
        relative = "STRENGTHENING"
    elif ethbtc < 0:
        relative = "WEAKENING"
    else:
        relative = "FLAT"

    summary_map = {
        "BULLISH": "BTC and ETH are both advancing over the latest governed comparison interval; action authority remains separate.",
        "BEARISH": "BTC and ETH are both declining over the latest governed comparison interval; this does not create sell authority.",
        "NEUTRAL": "BTC and ETH are unchanged across two distinct governed market observations.",
        "MIXED": "BTC/ETH direction is conflicting or incomplete; action authority remains separate.",
        "UNCHANGED_NO_NEW_OBSERVATION": "The price owner repeated the same completed hourly observation; no fresh directional market claim is made.",
    }
    regime_map = {
        "BULLISH": "BULLISH",
        "BEARISH": "BEARISH",
        "NEUTRAL": "NEUTRAL",
        "MIXED": "MIXED",
        "UNCHANGED_NO_NEW_OBSERVATION": "NO_NEW_OBSERVATION",
    }
    return {
        "directional_state": direction,
        "regime": regime_map[direction],
        "action_permission": posture,
        "btc_delta_pct": btc,
        "eth_delta_pct": eth,
        "ethbtc_delta_pct": ethbtc,
        "eth_relative_state": relative,
        "market_observation_open_utc": current_observation,
        "predecessor_market_observation_open_utc": prior_observation,
        "new_price_observation": not no_new_price_observation,
        "summary": summary_map[direction],
    }


def _cn_decision_projection(cn_package: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if not isinstance(cn_package, Mapping):
        return {}
    projection = cn_package.get("decision_projection")
    if not isinstance(projection, Mapping):
        return {}
    if str(projection.get("contract") or "") != "CYCLE_NAVIGATOR_DECISION_PROJECTION_v1":
        return {}
    return projection


def _cn_direction(cn_package: Mapping[str, Any] | None, lane: str) -> str:
    """Preserve the distinction between absent CN evidence and genuine NO_EDGE.

    A missing/invalid structured lane is UNKNOWN, not a measured negative
    hypothesis. Only an explicit and eligible typed NO_EDGE may be reported.
    """
    projection = _cn_decision_projection(cn_package)
    row = projection.get(lane)
    if not isinstance(row, Mapping):
        return "UNAVAILABLE"
    raw = row.get("direction")
    direction = raw.strip().upper() if isinstance(raw, str) else ""
    return direction if direction in {"UP", "DOWN", "SIDEWAYS", "MIXED", "NO_EDGE", "UNAVAILABLE"} else "UNAVAILABLE"


def _cn_projection_summary(cn_package: Mapping[str, Any] | None, lane: str) -> str | None:
    projection = _cn_decision_projection(cn_package)
    row = projection.get(lane)
    if not isinstance(row, Mapping):
        return None
    summary = row.get("summary")
    return str(summary).strip() if isinstance(summary, str) and summary.strip() else None


def _weekly_direction(cn_package: Mapping[str, Any] | None) -> str:
    """Backward-compatible helper, now structured-only.

    Free-form Cycle Navigator prose is context, never a machine decision field.
    """
    return _cn_direction(cn_package, "next_5_7d")


def _unavailable_horizon(reason: str) -> dict[str, Any]:
    return {
        "expected_direction": "UNAVAILABLE",
        "label": "UNAVAILABLE",
        "expected_path": reason,
        "action_posture": "NO_EDGE",
        "confirmation_trigger": {"type": "ACTION_STATE", "states": ["PREPARE", "GRADUATED_TOPUP_ACTIVE"]},
        "invalidation_trigger": {"type": "ACTION_STATE", "states": ["HOLD_DEFENSIVE_WAIT", "HOLD_WAIT_DATA_DEGRADED"]},
        "eta": None,
        "confidence": None,
    }


ALT_CONTEXT_DEGRADED_REASON = (
    "Altseason context is degraded (not PASS and no <=72 h carry); the altcoin lanes fail closed while the BTC/ETH lanes stay live."
)


def _scoped_altcoin_cycle_lane(
    auto_state: Mapping[str, Any], cn_package: Mapping[str, Any] | None, posture: str, issued: datetime,
) -> dict[str, Any]:
    if not _alt_context_usable(auto_state):
        return {
            **_unavailable_horizon(ALT_CONTEXT_DEGRADED_REASON),
            "state": "UNCLEAR",
            "warning": "NONE",
            "through_date": None,
            "horizon_days": None,
        }
    return _altcoin_cycle_lane(cn_package, posture, issued)


def _altcoin_cycle_lane(cn_package: Mapping[str, Any] | None, posture: str, issued: datetime) -> dict[str, Any]:
    projection = _cn_decision_projection(cn_package)
    structured = projection.get("weeks_4_8") if isinstance(projection, Mapping) else None
    if not isinstance(structured, Mapping):
        return {
            **_unavailable_horizon(
                "Structured Cycle Navigator 4-8 week decision projection is unavailable; free-form prose is context only."
            ),
            "state": "UNCLEAR",
            "warning": "NONE",
            "through_date": None,
            "horizon_days": None,
        }

    state = str(structured.get("state") or "UNCLEAR").upper()
    if state not in ALTCOIN_STATES:
        state = "UNCLEAR"
    warning = str(structured.get("warning") or "NONE").upper()
    if warning not in ALTCOIN_WARNINGS:
        warning = "NONE"
    direction = str(structured.get("direction") or "NO_EDGE").upper()
    if direction not in {"UP", "DOWN", "SIDEWAYS", "MIXED", "NO_EDGE", "UNAVAILABLE"}:
        direction = "NO_EDGE"
    summary = str(
        structured.get("summary")
        or (cn_package or {}).get("base_case_4_8_weeks")
        or "No eligible structured long-cycle summary is published."
    )
    through_raw = structured.get("through_date")
    through = str(through_raw) if isinstance(through_raw, str) and through_raw else None
    horizon_days = structured.get("horizon_days")
    if isinstance(horizon_days, bool) or not isinstance(horizon_days, int) or horizon_days <= 0:
        horizon_days = None
    proposed_action_posture = str(structured.get("action_posture") or "HOLD").upper()
    if proposed_action_posture not in {"BUY", "PREPARE_BUY", "HOLD", "WAIT", "NO_EDGE", "UNAVAILABLE"}:
        proposed_action_posture = "NO_EDGE"

    # Cycle Navigator is navigation-only and has no independent action permission.
    # Proactive long-cycle actions must stay at or below the current Main-Framework
    # permission carried by the native action posture.
    if proposed_action_posture == "BUY":
        if posture == "GRADUATED_TOPUP_ACTIVE":
            action_posture = "BUY"
            action_permission = "MAIN_FRAMEWORK_DEPLOY_PERMISSION"
        elif posture == "PREPARE":
            action_posture = "PREPARE_BUY"
            action_permission = "MAIN_FRAMEWORK_PREPARE_PERMISSION"
        else:
            action_posture = "WAIT"
            action_permission = "WITHHELD_PENDING_MAIN_FRAMEWORK_PERMISSION"
    elif proposed_action_posture == "PREPARE_BUY":
        if posture in {"PREPARE", "GRADUATED_TOPUP_ACTIVE"}:
            action_posture = "PREPARE_BUY"
            action_permission = "MAIN_FRAMEWORK_PREPARE_PERMISSION"
        else:
            action_posture = "WAIT"
            action_permission = "WITHHELD_PENDING_MAIN_FRAMEWORK_PERMISSION"
    else:
        action_posture = proposed_action_posture
        action_permission = "NON_PROACTIVE_NAVIGATION"

    return {
        "expected_direction": direction,
        "label": state,
        "state": state,
        "expected_path": summary,
        "action_posture": action_posture,
        "warning": warning,
        "through_date": through,
        "horizon_days": horizon_days,
        "confirmation_trigger": {"type": "STRUCTURED_CN_STATE", "states": ["ROTATION", "BROAD_ALTSEASON"]},
        "invalidation_trigger": {"type": "STRUCTURED_CN_STATE", "states": ["DEFENSIVE", "DISTRIBUTION", "EXIT_RISK"]},
        "eta": str(structured.get("eta") or "UNKNOWN"),
        "confidence": structured.get("confidence"),
    }


def protection_tracker(
    auto_state: Mapping[str, Any],
    action: Mapping[str, Any],
    market_now: Mapping[str, Any],
    cn_package: Mapping[str, Any] | None,
    *,
    as_of: datetime | None = None,
    prior_compass: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Project protection and re-entry from structured canonical decision fields only.

    Cycle Navigator prose remains explanatory context. It must never be parsed
    into an alert, distribution state, re-entry gate, or event-driven refresh.
    """
    issued = (as_of or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(microsecond=0)
    issued_text = issued.isoformat().replace("+00:00", "Z")
    prior_tracker = (prior_compass or {}).get("protection_tracker") if isinstance(prior_compass, Mapping) else None
    prior_tracker = prior_tracker if isinstance(prior_tracker, Mapping) else {}
    prior_risk = str(prior_tracker.get("pullback_risk_state") or "NORMAL")
    prior_reentry = str(prior_tracker.get("reentry_state") or "INACTIVE")
    # Preserve only an outstanding protective obligation, never stale REVIEW
    # permission, while evidence is unavailable. Legacy missing memory is not
    # reconstructed by guessing from prices, prose, or a corrupt carry value.
    gap_pending = None
    if prior_risk in {"HIGH", "CONFIRMED"}:
        gap_pending = "WAIT_FOR_FLUSH"
    elif prior_risk in {"NORMAL", "BUILDING", "ELEVATED"} and prior_reentry in {"WAIT_FOR_RECLAIM", "REVIEW"}:
        gap_pending = "WAIT_FOR_RECLAIM"
    elif prior_risk == "UNAVAILABLE" and prior_reentry == "UNAVAILABLE":
        carried = prior_tracker.get("reentry_pending_before_gap")
        if isinstance(carried, str) and carried in {"WAIT_FOR_FLUSH", "WAIT_FOR_RECLAIM"}:
            gap_pending = carried

    if not _health_ok(auto_state, issued) or not isinstance(cn_package, Mapping):
        return {
            "contract": "COMPASS_PROTECTION_TRACKER_v1",
            "pullback_risk_state": "UNAVAILABLE",
            "pullback_class": "UNKNOWN",
            "distribution_risk": "UNKNOWN",
            "eta_window": "UNKNOWN",
            "confidence_quality": "LOW",
            "decisive_public_drivers": [],
            "invalidation": "Fresh canonical market and Cycle Navigator evidence is required.",
            "last_material_change_at": issued_text,
            "data_quality": "DEGRADED",
            "reentry_state": "UNAVAILABLE",
            "reentry_pending_before_gap": gap_pending,
            "reentry_message": "Re-entry review is unavailable until canonical evidence is healthy.",
            "authority": {"portfolio_execution": False, "wallet_specific": False, "new_market_classifier": False},
        }

    projection = _cn_decision_projection(cn_package)
    structured = projection.get("protection") if isinstance(projection, Mapping) else None
    if not isinstance(structured, Mapping):
        return {
            "contract": "COMPASS_PROTECTION_TRACKER_v1",
            "pullback_risk_state": "UNAVAILABLE",
            "pullback_class": "UNKNOWN",
            "distribution_risk": "UNKNOWN",
            "eta_window": "UNKNOWN",
            "confidence_quality": "LOW",
            "decisive_public_drivers": [],
            "invalidation": "A structured Cycle Navigator protection projection is required; prose is not machine authority.",
            "last_material_change_at": issued_text,
            "data_quality": "STRUCTURED_PROTECTION_PROJECTION_UNAVAILABLE",
            "reentry_state": "UNAVAILABLE",
            "reentry_pending_before_gap": gap_pending,
            "reentry_message": "Re-entry review is unavailable until structured canonical protection evidence exists.",
            "authority": {"portfolio_execution": False, "wallet_specific": False, "new_market_classifier": False},
        }

    risk = str(structured.get("pullback_risk_state") or "UNAVAILABLE").upper()
    if risk not in PROTECTION_RISK_STATES:
        risk = "UNAVAILABLE"
    risk_class = str(structured.get("pullback_class") or "UNKNOWN").upper()
    distribution = str(structured.get("distribution_risk") or "UNKNOWN").upper()
    if distribution not in DISTRIBUTION_RISK_STATES:
        distribution = "UNKNOWN"
    quality = str(structured.get("confidence_quality") or "LOW").upper()
    if quality not in {"LOW", "MEDIUM", "HIGH"}:
        quality = "LOW"
    eta_raw = structured.get("eta_window")
    eta_window = str(eta_raw) if isinstance(eta_raw, str) and eta_raw.strip() else "UNKNOWN"
    drivers_raw = structured.get("drivers")
    drivers = [str(x) for x in drivers_raw[:4]] if isinstance(drivers_raw, list) else []

    posture = str(action.get("NOW") or "HOLD_WAIT")
    direction = str(market_now.get("directional_state") or "MIXED")
    if direction == "UNCHANGED_NO_NEW_OBSERVATION":
        direction = "UNAVAILABLE"

    if risk in {"HIGH", "CONFIRMED"}:
        reentry = "WAIT_FOR_FLUSH"
        reentry_message = "Protection phase. Do not treat stabilization alone as a re-entry signal."
    elif prior_risk == "UNAVAILABLE" and gap_pending is not None and risk != "UNAVAILABLE":
        reentry = "WAIT_FOR_RECLAIM"
        reentry_message = "Evidence is restored; re-entry remains blocked pending a new governed constructive confirmation."
    elif prior_risk in {"HIGH", "CONFIRMED"} and risk not in {"UNAVAILABLE"}:
        reentry = "WAIT_FOR_RECLAIM"
        reentry_message = "Risk has eased, but re-entry stays blocked until a governed constructive confirmation is restored."
    elif prior_reentry in {"WAIT_FOR_RECLAIM", "REVIEW"} and risk in {"NORMAL", "BUILDING", "ELEVATED"}:
        # The outstanding reclaim requirement survives repeated ELEVATED
        # observations. REVIEW is conditional, not a latched permission.
        constructive = (
            risk in {"NORMAL", "BUILDING"}
            and posture in {"PREPARE", "GRADUATED_TOPUP_ACTIVE"}
            and direction == "BULLISH"
        )
        if constructive:
            reentry = "REVIEW"
            if prior_reentry == "REVIEW":
                reentry_message = "Re-entry review remains open while governed constructive confirmation persists."
            else:
                reentry_message = "Re-entry review is open; this is a review state, not an automatic buy instruction."
        else:
            reentry = "WAIT_FOR_RECLAIM"
            reentry_message = "Risk has eased, but re-entry watch remains active until governed constructive confirmation arrives."
    else:
        reentry = "INACTIVE" if risk != "UNAVAILABLE" else "UNAVAILABLE"
        reentry_message = "No re-entry review is active." if reentry == "INACTIVE" else "Re-entry review is unavailable."

    material = (risk, risk_class, distribution, eta_window, quality, reentry)
    prior_material = (
        str(prior_tracker.get("pullback_risk_state") or ""),
        str(prior_tracker.get("pullback_class") or ""),
        str(prior_tracker.get("distribution_risk") or ""),
        str(prior_tracker.get("eta_window") or ""),
        str(prior_tracker.get("confidence_quality") or ""),
        str(prior_tracker.get("reentry_state") or ""),
    )
    last_change = str(prior_tracker.get("last_material_change_at") or "") if material == prior_material else issued_text
    if not last_change:
        last_change = issued_text

    invalidation = str(structured.get("invalidation") or "")
    if not invalidation:
        invalidation = "Later structured canonical protection evidence must explicitly downgrade or clear this state."

    public_explanation = None
    forecast_week = str(((cn_package.get("forecast_freeze") or {}).get("bull_bear_scale") or {}).get("forecast_week") or "")
    try:
        year_text, week_text = forecast_week.split("-W")
        public_explanation = validated_public_copy(structured, int(year_text), int(week_text))
    except (ValueError, TypeError):
        pass

    return {
        "contract": "COMPASS_PROTECTION_TRACKER_v1",
        "pullback_risk_state": risk,
        "pullback_class": risk_class,
        "distribution_risk": distribution,
        "eta_window": eta_window,
        "confidence_quality": quality,
        "decisive_public_drivers": drivers,
        "invalidation": invalidation,
        "public_explanation": public_explanation,
        "last_material_change_at": last_change,
        "data_quality": "OK" if risk != "UNAVAILABLE" else "DEGRADED",
        "reentry_state": reentry,
        **({"reentry_pending_before_gap": gap_pending} if risk == "UNAVAILABLE" else {}),
        "reentry_message": reentry_message,
        "authority": {"portfolio_execution": False, "wallet_specific": False, "new_market_classifier": False},
    }


def _bull_bear_bias(bull: int, bear: int) -> str:
    delta = bull - bear
    if delta >= 4:
        return "BULLISH"
    if delta >= 2:
        return "LEAN_BULLISH"
    if delta <= -4:
        return "BEARISH"
    if delta <= -2:
        return "LEAN_BEARISH"
    return "NEUTRAL"


def _bull_bear_row(direction: str, summary: str, *, bear_overlay: int = 0) -> dict[str, Any]:
    direction = str(direction or "UNAVAILABLE").upper()
    if direction in {"NO_EDGE", "UNAVAILABLE"}:
        return {
            "status": "UNAVAILABLE",
            "bull": None,
            "bear": None,
            "bias": "UNAVAILABLE",
            "summary": summary,
        }
    if direction == "UP":
        bull, bear = 7, 3
    elif direction == "DOWN":
        bull, bear = 3, 7
    else:
        bull, bear = 5, 5

    if bear_overlay:
        shift = max(0, min(int(bear_overlay), bull))
        bull -= shift
        bear += shift

    return {
        "status": "OK",
        "bull": bull,
        "bear": bear,
        "bias": _bull_bear_bias(bull, bear),
        "summary": summary,
    }


def bull_bear_scale(horizons: Mapping[str, Any]) -> dict[str, Any]:
    """Display-only evidence balance derived from Official Compass directions.

    This is not a new market classifier and not a probability model. It is a
    deliberately coarse visual encoding of already-governed Compass direction.
    Protection / re-entry remains a separate governed lane and is never
    double-counted into Market Weather.
    """
    h13 = horizons.get("NEXT_1_3D") if isinstance(horizons, Mapping) else None
    h57 = horizons.get("NEXT_5_7D") if isinstance(horizons, Mapping) else None
    h23 = horizons.get("NEXT_2_3W") if isinstance(horizons, Mapping) else None
    h13 = h13 if isinstance(h13, Mapping) else {}
    h57 = h57 if isinstance(h57, Mapping) else {}
    h23 = h23 if isinstance(h23, Mapping) else {}

    return {
        "contract": "OFFICIAL_COMPASS_BULL_BEAR_DISPLAY_v1",
        "semantics": "EVIDENCE_BALANCE_NOT_PROBABILITY",
        "owner": "OFFICIAL_COMPASS",
        "source_of_truth_contract": "MARKET_WEATHER_SOURCE_OF_TRUTH_v1",
        "mapping_version": "DIRECTION_ONLY_COARSE_v1",
        "resolution": "COARSE_CATEGORICAL_DIRECTION",
        "horizons": {
            "1_3d": _bull_bear_row(
                str(h13.get("expected_direction") or "UNAVAILABLE"),
                str(h13.get("expected_path") or "No governed 1-3d Compass path is available."),
            ),
            "5_7d": _bull_bear_row(
                str(h57.get("expected_direction") or "UNAVAILABLE"),
                str(h57.get("expected_path") or "No governed 5-7d Compass path is available."),
            ),
            "2_3w": _bull_bear_row(
                str(h23.get("expected_direction") or "UNAVAILABLE"),
                str(h23.get("expected_path") or "Awaiting a governed 2-3 week Compass horizon."),
            ),
        },
        "authority": {
            "new_market_classifier": False,
            "probability_model": False,
            "portfolio_execution": False,
            "site_synthesis_allowed": False,
        },
    }


def horizon_map(
    auto_state: Mapping[str, Any], action: Mapping[str, Any], cn_package: Mapping[str, Any] | None,
    *, as_of: datetime | None = None,
) -> dict[str, Any]:
    if not _health_ok(auto_state, as_of):
        unavailable = {
            "expected_direction": "UNAVAILABLE",
            "label": "UNAVAILABLE",
            "expected_path": "Required current-state evidence is degraded.",
            "action_posture": "NO_EDGE",
            "confirmation_trigger": {"type": "ACTION_STATE", "states": ["PREPARE", "GRADUATED_TOPUP_ACTIVE"]},
            "invalidation_trigger": {"type": "ACTION_STATE", "states": ["HOLD_DEFENSIVE_WAIT", "HOLD_WAIT_DATA_DEGRADED"]},
            "eta": None,
            "confidence": None,
        }
        rows = {key: dict(unavailable) for key in HORIZON_ORDER}
        rows["NEXT_12H"].update({
            "semantics": NEXT_12H_NOWCAST_SEMANTICS,
            "predictive_edge_status": "NOT_PROVEN",
            "eta_kind": "NONE",
            "reassessment_window": None,
        })
        return rows

    posture = str(action.get("NOW") or "HOLD_WAIT")
    current = derive_market_now(auto_state, action, as_of=as_of)["directional_state"]
    d13_source = _cn_direction(cn_package, "next_1_3d")
    d57_source = _cn_direction(cn_package, "next_5_7d")
    d23_source = _cn_direction(cn_package, "next_2_3w")
    s13_source = _cn_projection_summary(cn_package, "next_1_3d")
    s23_source = _cn_projection_summary(cn_package, "next_2_3w")

    direction_map = {
        "BULLISH": "UP",
        "BEARISH": "DOWN",
        "NEUTRAL": "SIDEWAYS",
        "MIXED": "MIXED",
        "UNAVAILABLE": "UNAVAILABLE",
        "UNCHANGED_NO_NEW_OBSERVATION": "UNAVAILABLE",
    }
    d12 = direction_map.get(current, "MIXED")
    if posture == "GRADUATED_TOPUP_ACTIVE":
        a12 = "DEPLOY"
    elif posture == "PREPARE":
        a12 = "PREPARE"
    else:
        a12 = "HOLD"

    if not isinstance(cn_package, Mapping):
        forward_unavailable = _unavailable_horizon("Current Cycle Navigator context is unavailable; this forward lane fails closed.")
        return {
            "NEXT_12H": {
                "expected_direction": d12, "label": "BULLISH" if d12 == "UP" else "BEARISH" if d12 == "DOWN" else "NEUTRAL" if d12 == "SIDEWAYS" else "MIXED",
                "expected_path": "Current directional state is descriptive and independent of action permission; continuation is reassessed when governed market evidence changes.",
                "action_posture": a12,
                "confirmation_trigger": {"type": "ACTION_STATE", "states": ["PREPARE", "GRADUATED_TOPUP_ACTIVE"]},
                "invalidation_trigger": {"type": "ACTION_STATE", "states": ["HOLD_DEFENSIVE_WAIT", "HOLD_WAIT_DATA_DEGRADED"]},
                "eta": None, "confidence": None,
                "semantics": NEXT_12H_NOWCAST_SEMANTICS,
                "predictive_edge_status": "NOT_PROVEN",
                "eta_kind": "REASSESSMENT_WINDOW_ONLY",
                "reassessment_window": "0-12h",
            },
            "NEXT_1_3D": dict(forward_unavailable),
            "NEXT_5_7D": dict(forward_unavailable),
            "NEXT_2_3W": dict(forward_unavailable),
            "CYCLE_ALTCOINS_3_8W": _scoped_altcoin_cycle_lane(auto_state, None, posture, as_of or datetime.now(timezone.utc)),
        }

    if d13_source == "UNAVAILABLE":
        d13, a13 = "UNAVAILABLE", "WAIT"
    elif posture in {"GRADUATED_TOPUP_ACTIVE", "PREPARE"} and d13_source in {"UP", "SIDEWAYS"}:
        d13, a13 = "UP", "PREPARE"
    elif posture == "HOLD_DEFENSIVE_WAIT" and d13_source != "NO_EDGE":
        d13, a13 = ("DOWN" if d13_source == "DOWN" else "MIXED"), "WAIT"
    else:
        d13, a13 = d13_source, "WAIT"

    d57 = d57_source
    a57 = "PREPARE" if posture in {"PREPARE", "GRADUATED_TOPUP_ACTIVE"} and d57 not in {"DOWN", "NO_EDGE", "UNAVAILABLE"} else "WAIT"

    label = lambda d: (
        "BULLISH" if d == "UP" else
        "BEARISH" if d == "DOWN" else
        "NEUTRAL" if d == "SIDEWAYS" else
        "NO_EDGE" if d == "NO_EDGE" else
        "UNAVAILABLE" if d == "UNAVAILABLE" else
        "MIXED"
    )
    confirm = {"type": "ACTION_STATE", "states": ["PREPARE", "GRADUATED_TOPUP_ACTIVE"]}
    invalidate = {"type": "ACTION_STATE", "states": ["HOLD_DEFENSIVE_WAIT", "HOLD_WAIT_DATA_DEGRADED"]}
    return {
        "NEXT_12H": {
            "expected_direction": d12, "label": label(d12),
            "expected_path": "Current-state continuation unless the native confirmation or deterioration gate changes state.",
            "action_posture": a12, "confirmation_trigger": confirm, "invalidation_trigger": invalidate,
            "eta": None, "confidence": None,
            "semantics": NEXT_12H_NOWCAST_SEMANTICS,
            "predictive_edge_status": "NOT_PROVEN",
            "eta_kind": "REASSESSMENT_WINDOW_ONLY",
            "reassessment_window": "0-12h",
        },
        "NEXT_1_3D": (
            _unavailable_horizon("Structured Cycle Navigator 1-3 day decision projection is unavailable.")
            if d13 == "UNAVAILABLE" else {
                "expected_direction": d13, "label": label(d13),
                "expected_path": (
                    s13_source if s13_source and d13 == d13_source
                    else "Action posture differs from the source Cycle Navigator direction; no independent 1-3 day forecast upgrade is implied."
                    if d13 != d13_source
                    else "No eligible typed Cycle Navigator 1-3 day path is published."
                ),
                "action_posture": a13, "confirmation_trigger": confirm, "invalidation_trigger": invalidate,
                "eta": "24-72h", "confidence": None,
            }
        ),
        "NEXT_5_7D": (
            _unavailable_horizon("Structured Cycle Navigator 5-7 day decision projection is unavailable.")
            if d57 == "UNAVAILABLE" else {
                "expected_direction": d57, "label": label(d57),
                "expected_path": str((cn_package or {}).get("base_case_this_week") or "No stronger weekly path is eligible; remain fail-closed."),
                "action_posture": a57, "confirmation_trigger": confirm, "invalidation_trigger": invalidate,
                "eta": "120-168h", "confidence": None,
            }
        ),
        "NEXT_2_3W": (
            {
                "expected_direction": d23_source,
                "label": label(d23_source),
                "expected_path": s23_source or "No eligible structured 2-3 week path is published.",
                "action_posture": "PREPARE" if posture in {"PREPARE", "GRADUATED_TOPUP_ACTIVE"} and d23_source == "UP" else "WAIT",
                "confirmation_trigger": confirm,
                "invalidation_trigger": invalidate,
                "eta": "14-21d",
                "confidence": None,
            }
            if d23_source not in {"NO_EDGE", "UNAVAILABLE"}
            else ({
                "expected_direction": "NO_EDGE",
                "label": "NO_EDGE",
                "expected_path": "Ingen klar fordel. " + (s23_source or "Ingen dokumenteret 2-3-ugers retningsmæssig fordel."),
                "action_posture": "WAIT",
                "confirmation_trigger": confirm,
                "invalidation_trigger": invalidate,
                "eta": None,
                "confidence": None,
            } if d23_source == "NO_EDGE"
            else _unavailable_horizon("Structured Cycle Navigator 2-3 week decision projection is unavailable."))
        ),
        "CYCLE_ALTCOINS_3_8W": _scoped_altcoin_cycle_lane(auto_state, cn_package, posture, as_of or datetime.now(timezone.utc)),
    }


def capitalization_ladder(
    auto_state: Mapping[str, Any], action: Mapping[str, Any], market_now: Mapping[str, Any],
    *, as_of: datetime | None = None,
) -> list[dict[str, Any]]:
    if not _health_ok(auto_state, as_of):
        rows = [
            {"segment": seg, "status": "UNAVAILABLE", "action": "UNAVAILABLE", "direction": "UNAVAILABLE", "eta": None,
             "reason": "Required current-state evidence is degraded.",
             "upgrade_trigger": {"type": "ACTION_STATE", "states": ["PREPARE", "GRADUATED_TOPUP_ACTIVE"]},
             "deterioration_trigger": {"type": "ACTION_STATE", "states": ["HOLD_WAIT_DATA_DEGRADED"]}}
            for seg in CAPITALIZATION_ORDER[:-1]
        ]
        rows.append({
            "segment": "MEMES",
            "status": "UNAVAILABLE",
            "action": "UNAVAILABLE",
            "direction": "UNAVAILABLE",
            "eta": None,
            "reason": "Required current-state evidence is degraded, and meme risk still requires a governed meme-specific decision owner.",
            "upgrade_trigger": {"type": "GOVERNED_MEME_DECISION_OWNER", "states": ["ELIGIBLE"]},
            "deterioration_trigger": {"type": "GOVERNED_MEME_DECISION_OWNER", "states": ["UNAVAILABLE", "INELIGIBLE"]},
        })
        return rows
    posture = str(action.get("NOW") or "HOLD_WAIT")
    direction = str(market_now.get("directional_state") or "MIXED")
    if direction == "UNCHANGED_NO_NEW_OBSERVATION":
        direction = "UNAVAILABLE"
    if posture == "GRADUATED_TOPUP_ACTIVE":
        states = ("HOLD", "DEPLOY", "PREPARE", "WAIT", "HARD_WAIT", "HARD_WAIT")
    elif posture == "PREPARE":
        states = ("HOLD", "PREPARE", "PREPARE", "WAIT", "HARD_WAIT", "HARD_WAIT")
    elif posture == "HOLD_DEFENSIVE_WAIT":
        states = ("HOLD", "HOLD", "WAIT", "WAIT", "HARD_WAIT", "HARD_WAIT")
    else:
        states = ("HOLD", "HOLD", "WAIT", "WAIT", "WAIT", "HARD_WAIT")
    reasons = {
        "BTC": "Liquidity anchor; preserve core while the short-horizon gate resolves.",
        "ETH": "Relative-strength leadership must hold before broader rotation is trusted.",
        "LARGE_CAPS": "First alt-risk tier eligible only after a registered canonical confirmation.",
        "MID_CAPS": "Requires durable large-cap transmission under a registered canonical confirmation.",
        "SMALL_CAPS": "Requires confirmed mid-cap participation before deployment.",
        "MICROCAPS": "Highest-beta non-meme tier remains late in the rotation sequence.",
        "MEMES": "Meme risk is a separate rung and requires a governed meme-specific decision owner.",
    }
    confirm = {"type": "ACTION_STATE", "states": ["PREPARE", "GRADUATED_TOPUP_ACTIVE"]}
    deteriorate = {"type": "ACTION_STATE", "states": ["HOLD_DEFENSIVE_WAIT", "HOLD_WAIT_DATA_DEGRADED"]}
    eta_by_state = {"HOLD": "now", "DEPLOY": "now", "PREPARE": "0-3d", "WAIT": "1-7d conditional", "HARD_WAIT": "no fixed ETA"}
    rows = []
    alt_usable = _alt_context_usable(auto_state)
    for seg, state in zip(CAPITALIZATION_ORDER[:-1], states):
        if seg in ALT_LADDER_SEGMENTS and not alt_usable:
            rows.append({
                "segment": seg, "status": "UNAVAILABLE", "action": "UNAVAILABLE", "direction": "UNAVAILABLE", "eta": None,
                "reason": ALT_CONTEXT_DEGRADED_REASON,
                "upgrade_trigger": {"type": "SOURCE_HEALTH", "lane": "altseason_context", "states": sorted(ALT_CONTEXT_USABLE)},
                "deterioration_trigger": deteriorate,
            })
            continue
        rows.append({
            "segment": seg,
            "status": state,
            "action": state,
            "direction": direction if seg in {"BTC", "ETH"} else ("MIXED" if state in {"WAIT", "HARD_WAIT"} else direction),
            "eta": eta_by_state[state],
            "reason": reasons[seg],
            "upgrade_trigger": confirm,
            "deterioration_trigger": deteriorate,
        })
    rows.append({
        "segment": "MEMES",
        "status": "UNAVAILABLE",
        "action": "UNAVAILABLE",
        "direction": "UNAVAILABLE",
        "eta": None,
        "reason": reasons["MEMES"] + " No such owner is currently bound, so MICROCAPS cannot be used as a proxy.",
        "upgrade_trigger": {"type": "GOVERNED_MEME_DECISION_OWNER", "states": ["ELIGIBLE"]},
        "deterioration_trigger": {"type": "GOVERNED_MEME_DECISION_OWNER", "states": ["UNAVAILABLE", "INELIGIBLE"]},
    })
    return rows


def sell_assessment(
    auto_state: Mapping[str, Any],
    protection: Mapping[str, Any],
    *,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    """Expose SELL as a separate fail-closed decision surface.

    Existing exit-calibration owners are descriptive/accountability-only and
    cannot be promoted into a live sell rule. Protection or distribution risk
    is context, never sell authority by itself.
    """
    healthy = _health_ok(auto_state, as_of)
    reason = (
        "Required current-state evidence is degraded."
        if not healthy
        else "No governed sell/trim decision owner is bound. Protection and distribution risk are not sell instructions."
    )
    return {
        "contract": "COMPASS_SELL_ASSESSMENT_v1",
        "state": "UNAVAILABLE",
        "horizon": "UNKNOWN",
        "eta": "UNKNOWN",
        "reason": reason,
        "protection_context": {
            "pullback_risk_state": protection.get("pullback_risk_state"),
            "distribution_risk": protection.get("distribution_risk"),
        },
        "authority": {
            "portfolio_execution": False,
            "new_sell_rule": False,
            "automatic_action": False,
            "protection_is_sell_authority": False,
        },
    }


# ---------------------------------------------------------------------------------------------------------
# AUDIT-04b (2026-11-24). Three separately inspectable DESCRIPTIVE facts. None of them changes action,
# protection, score, horizon or sell state; escalating an action on any of them is a separate owner decision.
#   source_freshness   FRESH | STALE | UNKNOWN          is the daily owner evidence inside its own SLA?
#   cn_band_status     NOT_BREACHED | BREACHED | UNTESTABLE   did a COMPLETED UTC daily close break the frozen floor?
#   risk_freshness     FRESH | INHERITED | STALE | DEGRADED   where does the displayed risk state come from?
# A fourth fact, consumer delivery, is a release receipt and is never produced here.
# ---------------------------------------------------------------------------------------------------------
SOURCE_FRESHNESS_CONTRACT = "COMPASS_SOURCE_FRESHNESS_v1"
CN_BAND_STATUS_CONTRACT = "CN_BAND_STATUS_v2"
RISK_FRESHNESS_CONTRACT = "COMPASS_RISK_FRESHNESS_v1"
DESCRIPTIVE_AUTHORITY = "DESCRIPTIVE_ONLY_NO_SCORE_RISK_OR_ACTION"
DESCRIPTIVE_RELEASE_STAGE = "SHADOW"
HOURLY_DAILY_CSV_ROOT = "03_DAILY_CAPTURE_LOGS/hourly"
COMPLETED_CANDLE_SEMANTICS = "COMPLETED_1H_CANDLE_CLOSE_VALUE_ON_CANDLE_OPEN_LABEL"
# The Sunday 23:00-24:00 UTC candle completes the forecast week; it can only be observed in the next ISO week.
# The frozen week stays comparable for this bounded window after the week ends, never longer.
SUNDAY_CLOSE_WINDOW = timedelta(hours=24)
INHERITANCE_WALK_MAX_WEEKS = 12
INHERITED_BASIS = "INHERITED_FROM_PRIOR_ISSUE"
FLOOR_ASSETS = ("BTC", "ETH")


def _stamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _is_commit_sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 40 and all(c in "0123456789abcdef" for c in value)


def _git_bound_bytes(repo_root: Path, commit: str, rel_path: str) -> tuple[bytes, str] | None:
    """Bytes and Git blob of one path at one exact commit. The blob is recomputed from the bytes that were read."""
    try:
        raw = subprocess.check_output(["git", "show", f"{commit}:{rel_path}"], cwd=repo_root, stderr=subprocess.DEVNULL)
        blob = subprocess.check_output(
            ["git", "rev-parse", "--verify", f"{commit}:{rel_path}"], cwd=repo_root, text=True, stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None
    if hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest() != blob:
        return None
    return raw, blob


def source_freshness(auto_state: Mapping[str, Any], as_of: datetime, *, packet_path: Path | None = None) -> dict[str, Any]:
    """Fact 1. The owner's own freshness contract, re-evaluated at issuance, as a three-valued status.

    STALE needs a clock that is provably older than its own limit. A missing policy, a missing timestamp or a
    timestamp in the future is UNKNOWN: it is not evidence of freshness and not evidence of age.
    """
    as_of = as_of.astimezone(timezone.utc)
    owner = owner_freshness(auto_state, as_of)
    checks = [row for row in owner.get("checks") or [] if isinstance(row, Mapping)]
    stale_lanes = sorted(
        str(row.get("lane")) for row in checks
        if finite(row.get("age_seconds")) is not None and finite(row.get("max_age_seconds")) is not None
        and float(row["age_seconds"]) > float(row["max_age_seconds"])
    )
    if not owner["reasons"]:
        status = "FRESH"
    elif stale_lanes:
        status = "STALE"
    else:
        status = "UNKNOWN"
    aged = [row for row in checks if finite(row.get("age_seconds")) is not None]
    oldest = max(aged, key=lambda row: float(row["age_seconds"])) if aged else None
    return {
        "contract": SOURCE_FRESHNESS_CONTRACT,
        "status": status,
        "reasons": list(owner["reasons"]),
        "stale_lanes": stale_lanes,
        "clock": {
            "evaluated_at_utc": owner["evaluated_at_utc"],
            "packet_generated_at_utc": auto_state.get("packet_generated_at_utc"),
            "observation_open_utc": nested(auto_state, "normalized_state", "live_market", "observation_open_utc"),
            "oldest_lane": oldest.get("lane") if oldest else None,
            "oldest_age_seconds": oldest.get("age_seconds") if oldest else None,
            "oldest_max_age_seconds": oldest.get("max_age_seconds") if oldest else None,
        },
        "binding": {
            "auto_market_state_packet_path": packet_path.as_posix() if packet_path is not None else None,
            "auto_market_state_packet_sha256": auto_state.get("packet_sha256"),
            "source_snapshot_commit_sha": nested(auto_state, "source_snapshot", "exact_commit_sha"),
        },
        "authority": DESCRIPTIVE_AUTHORITY,
        "release_stage": DESCRIPTIVE_RELEASE_STAGE,
    }


def _iso_week_start(iso_year: int, iso_week: int) -> datetime | None:
    try:
        monday = datetime.fromisocalendar(iso_year, iso_week, 1)
    except (ValueError, TypeError):
        return None
    return monday.replace(tzinfo=timezone.utc)


def _cn_issue_time(cn_package: Mapping[str, Any]) -> datetime | None:
    generated = finite(cn_package.get("generated_unix"))
    if generated is None or generated <= 0:
        return None
    try:
        return datetime.fromtimestamp(generated, timezone.utc)
    except (OverflowError, ValueError, OSError):
        return None


def cn_band_status(
    auto_state: Mapping[str, Any],
    cn_package: Mapping[str, Any] | None,
    cn_binding: Mapping[str, Any] | None,
    repo_root: Path,
    as_of: datetime,
    *,
    source_status: str = "UNKNOWN",
) -> dict[str, Any]:
    """Fact 2. Completed UTC daily closes of the frozen forecast week against the frozen floors.

    The daily close is the close of the 23:00-24:00 UTC hourly candle, read from the daily hourly CSV as Git
    holds it at the snapshot commit the owner packet is bound to. It is not the eight-row capture window, so the
    status is valid all day. Factual comparison only: it never alters protection, forecast, score or action.

    forecast_floor_status compares against the frozen WEEKLY floor (the forecast's own invalidation envelope);
    daily_floor_status compares each day against that day's own frozen low.
      BREACHED      at least one eligible completed close is strictly below the floor (a fact that stays true);
      NOT_BREACHED  every eligible completed close the bound source can know is readable and none is below,
                    and the daily source is FRESH;
      UNTESTABLE    anything else. Missing evidence is never reported as "no breach".
    """
    as_of = as_of.astimezone(timezone.utc)

    def untestable(reason: str) -> dict[str, Any]:
        return {
            "contract": CN_BAND_STATUS_CONTRACT,
            "forecast_floor_status": "UNTESTABLE",
            "daily_floor_status": "UNTESTABLE",
            "reason": reason,
            "authority": DESCRIPTIVE_AUTHORITY,
            "release_stage": DESCRIPTIVE_RELEASE_STAGE,
        }

    if not isinstance(cn_package, Mapping) or not isinstance(cn_binding, Mapping) or cn_binding.get("status") != "PASS":
        return untestable("CN_BINDING_UNAVAILABLE")
    freeze = cn_package.get("forecast_freeze")
    if not isinstance(freeze, Mapping) or cn_package.get("issue_number") != cn_binding.get("issue_number"):
        return untestable("CN_BINDING_UNAVAILABLE")
    iso_year, iso_week = cn_binding.get("iso_year"), cn_binding.get("iso_week")
    if type(iso_year) is not int or type(iso_week) is not int:
        return untestable("CN_WEEK_UNAVAILABLE")
    week_start = _iso_week_start(iso_year, iso_week)
    if week_start is None:
        return untestable("CN_WEEK_UNAVAILABLE")
    week_end = week_start + timedelta(days=7)
    week = f"{iso_year:04d}-W{iso_week:02d}"
    if any(nested(freeze, "price_quote", asset) != "USDT" for asset in FLOOR_ASSETS):
        return untestable("QUOTE_MISMATCH_OR_UNSTATED")
    path = freeze.get("daily_price_path")
    if not isinstance(path, Mapping) or path.get("contract") != "CN_FROZEN_DAILY_PRICE_PATH_v1" or path.get("forecast_week") != week:
        return untestable("CN_DAILY_PATH_UNAVAILABLE")
    weekly_floor: dict[str, float] = {}
    daily_floor: dict[str, dict[int, float]] = {}
    for asset in FLOOR_ASSETS:
        floor = finite(freeze.get(f"{asset.lower()}_range_low"))
        points = nested(path, asset, "points")
        if floor is None or floor <= 0 or not isinstance(points, list) or len(points) != 7:
            return untestable("CN_FLOOR_UNAVAILABLE")
        per_day: dict[int, float] = {}
        for point in points:
            if not isinstance(point, Mapping):
                return untestable("CN_FLOOR_UNAVAILABLE")
            day, low = point.get("day"), finite(point.get("low"))
            if type(day) is not int or day not in range(1, 8) or day in per_day or low is None or low <= 0:
                return untestable("CN_FLOOR_UNAVAILABLE")
            per_day[day] = low
        weekly_floor[asset], daily_floor[asset] = floor, per_day
    issue = _cn_issue_time(cn_package)
    if issue is None:
        return untestable("CN_ISSUE_CLOCK_UNAVAILABLE")
    if as_of < issue:
        return untestable("AS_OF_BEFORE_FORECAST_ISSUE")
    if as_of >= week_end + SUNDAY_CLOSE_WINDOW:
        return untestable("FORECAST_WEEK_EXPIRED_BEYOND_SUNDAY_CLOSE_WINDOW")

    live = nested(auto_state, "normalized_state", "live_market")
    lane = nested(auto_state, "source_health", "hourly_market")
    snapshot = nested(auto_state, "source_snapshot", "exact_commit_sha")
    if not isinstance(live, Mapping) or not isinstance(lane, Mapping):
        return untestable("HOURLY_OWNER_UNAVAILABLE")
    if not _is_commit_sha(snapshot):
        return untestable("SNAPSHOT_COMMIT_UNBOUND")
    bar = _parse_utc(live.get("observation_open_utc"))
    available = _parse_utc(auto_state.get("packet_generated_at_utc"))
    if (bar is None or available is None or bar.minute or bar.second or bar.microsecond
            or live.get("observation_semantics") != COMPLETED_CANDLE_SEMANTICS
            or bar + timedelta(hours=1) > available or available > as_of):
        return untestable("BAR_FUTURE_INCOMPLETE_OR_CLOCK_UNAVAILABLE")
    row_health = lane.get("row")
    bar_csv = f"{HOURLY_DAILY_CSV_ROOT}/{bar:%Y/%m/%Y-%m-%d}.csv"
    if (lane.get("status") != "PASS" or not isinstance(row_health, Mapping)
            or row_health.get("status") != "PASS" or row_health.get("classification") != "HOURLY_EXACT_ROW_BOUND"
            or _parse_utc(row_health.get("timestamp_utc")) != bar
            or nested(row_health, "provenance", "exact_commit_sha") != snapshot
            or nested(row_health, "provenance", "exact_path") != bar_csv):
        return untestable("HOURLY_ROW_BINDING_UNAVAILABLE")
    bound_blob = nested(row_health, "provenance", "git_blob_sha")

    cache: dict[str, tuple[list[dict[str, str]], str] | None] = {}

    def day_rows(rel: str) -> tuple[list[dict[str, str]], str] | None:
        if rel not in cache:
            got = _git_bound_bytes(repo_root, snapshot, rel)
            if got is None:
                cache[rel] = None
            else:
                try:
                    cache[rel] = (list(csv.DictReader(io.StringIO(got[0].decode("utf-8-sig")))), got[1])
                except (UnicodeDecodeError, csv.Error):
                    cache[rel] = None
        return cache[rel]

    def exact_row(rel: str, candle_open: datetime) -> tuple[dict[str, float] | None, str | None, str | None]:
        loaded = day_rows(rel)
        if loaded is None:
            return None, None, "ROW_SOURCE_UNREADABLE_AT_SNAPSHOT"
        rows, blob = loaded
        label = _stamp(candle_open)
        matches = [row for row in rows if row.get("timestamp_utc") == label]
        if len(matches) != 1:
            return None, blob, "ROW_MISSING" if not matches else "ROW_DUPLICATE"
        row = matches[0]
        # source_window_end_utc is the end of the capture window that wrote the row. A backfilled row carries a later
        # window; a window that ends before the candle closes cannot hold a completed candle, and a window that
        # ends after the owner packet was generated cannot have been known to it.
        window_end = _parse_utc(row.get("source_window_end_utc"))
        if row.get("spot_status") != "PASS" or window_end is None or window_end < candle_open + timedelta(hours=1):
            return None, blob, "ROW_NOT_A_COMPLETED_PASS_CANDLE"
        if window_end > available:
            return None, blob, "ROW_CAPTURED_AFTER_OWNER_PACKET"
        closes: dict[str, float] = {}
        for asset in FLOOR_ASSETS:
            try:
                value = float(row.get(f"{asset.lower()}_close"))
            except (TypeError, ValueError, OverflowError):
                return None, blob, "ROW_PRICE_INVALID"
            if not math.isfinite(value) or value <= 0:
                return None, blob, "ROW_PRICE_INVALID"
            closes[asset] = value
        return closes, blob, None

    # The owner's bound row must be byte-identical in Git and carry the owner's own closes (same quote and asset).
    owner_closes, owner_blob, owner_error = exact_row(bar_csv, bar)
    if owner_error is not None or owner_closes is None:
        return untestable("HOURLY_ROW_BINDING_UNAVAILABLE:" + str(owner_error))
    if owner_blob != bound_blob:
        return untestable("HOURLY_ROW_BLOB_MISMATCH")
    if any(finite(live.get(f"{asset.lower()}_usdt")) != owner_closes[asset] for asset in FLOOR_ASSETS):
        return untestable("OWNER_CLOSE_MISMATCH")

    days: list[dict[str, Any]] = []
    first_weekly: dict[str, dict[str, Any]] = {}
    first_daily: dict[str, dict[str, Any]] = {}
    observed = untested = 0
    evaluated_through = None
    pending: list[str] = []
    for index in range(7):
        day_start = week_start + timedelta(days=index)
        candle_open = day_start + timedelta(hours=23)
        candle_close = candle_open + timedelta(hours=1)
        entry: dict[str, Any] = {
            "day_utc": day_start.date().isoformat(),
            "iso_day": index + 1,
            "candle_open_utc": _stamp(candle_open),
            "candle_close_utc": _stamp(candle_close),
        }
        if candle_open < issue:
            # The forecast must be frozen before the candle opens; an earlier close is not a forecast outcome.
            entry["state"] = "PRE_ISSUE"
        elif candle_open > bar:
            entry["state"] = "PENDING"
            pending.append(entry["day_utc"])
        else:
            rel = f"{HOURLY_DAILY_CSV_ROOT}/{day_start:%Y/%m/%Y-%m-%d}.csv"
            closes, blob, error = exact_row(rel, candle_open)
            entry["source"] = {"path": rel, "git_blob_sha": blob}
            if error is not None or closes is None:
                entry["state"], entry["reason"] = "UNTESTABLE", error
                untested += 1
            else:
                entry["state"] = "OBSERVED"
                observed += 1
                evaluated_through = entry["day_utc"]
                entry["assets"] = {}
                for asset in FLOOR_ASSETS:
                    close = closes[asset]
                    day_low = daily_floor[asset][index + 1]
                    below_week = close < weekly_floor[asset]
                    below_day = close < day_low
                    entry["assets"][asset] = {
                        "symbol": asset + "USDT",
                        "close": close,
                        "weekly_floor": weekly_floor[asset],
                        "daily_floor": day_low,
                        "close_below_weekly_floor": below_week,
                        "close_below_daily_floor": below_day,
                    }
                    # Every breach is stamped with the candle's CLOSE time: that is when the close became a fact.
                    mark = {"day_utc": entry["day_utc"], "breach_at_utc": _stamp(candle_close), "close": close}
                    if below_week and asset not in first_weekly:
                        first_weekly[asset] = {**mark, "floor": weekly_floor[asset]}
                    if below_day and asset not in first_daily:
                        first_daily[asset] = {**mark, "floor": day_low}
        days.append(entry)

    def verdict(breached: bool) -> tuple[str, str | None]:
        if breached:
            return "BREACHED", None
        if untested:
            return "UNTESTABLE", "COMPLETED_DAY_ROW_UNTESTABLE"
        if not observed:
            return "UNTESTABLE", "NO_ELIGIBLE_COMPLETED_CLOSE"
        if source_status != "FRESH":
            return "UNTESTABLE", "DAILY_SOURCE_NOT_FRESH"
        return "NOT_BREACHED", None

    weekly_status, weekly_reason = verdict(bool(first_weekly))
    daily_status, daily_reason = verdict(bool(first_daily))
    return {
        "contract": CN_BAND_STATUS_CONTRACT,
        "forecast_floor_status": weekly_status,
        "daily_floor_status": daily_status,
        "reason": weekly_reason,
        "daily_reason": daily_reason,
        "forecast_week": week,
        "quote": "USDT",
        "semantics": "COMPLETED_UTC_DAILY_CLOSE_ONLY_NOT_INTRADAY_OR_RISK_CLASSIFICATION",
        "daily_close_definition": "CLOSE_OF_23_00_UTC_HOURLY_CANDLE_FROM_GIT_BOUND_DAILY_CSV_AT_SNAPSHOT",
        "comparison": "STRICTLY_BELOW_FLOOR; EQUAL_IS_NOT_A_BREACH",
        "original_freeze": {
            "issue_number": cn_package.get("issue_number"),
            "public_issue_number": cn_package.get("public_issue_number"),
            "issued_at_utc": _stamp(issue),
            "machine_package_sha256": nested(cn_binding, "machine_package", "content_sha256"),
            "weekly_floor": dict(weekly_floor),
        },
        "source": {
            "snapshot_commit_sha": snapshot,
            "bound_bar_open_utc": _stamp(bar),
            "bound_bar_csv": {"path": bar_csv, "git_blob_sha": owner_blob},
            "quote_binding": "CSV_CLOSE_EQUALS_OWNER_LIVE_MARKET_USDT_AT_THE_BOUND_BAR",
        },
        "evaluated_through_day_utc": evaluated_through,
        "pending_days_utc": pending,
        "observed_days": observed,
        "first_weekly_floor_breach": first_weekly,
        "first_daily_floor_breach": first_daily,
        "days": days,
        "authority": DESCRIPTIVE_AUTHORITY,
        "release_stage": DESCRIPTIVE_RELEASE_STAGE,
    }


def _cn_protection_inherited(cn_package: Mapping[str, Any]) -> bool:
    return cn_protection_state_basis(cn_package) == INHERITED_BASIS


def _same_protection_state(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    a = nested(left, "decision_projection", "protection")
    b = nested(right, "decision_projection", "protection")
    return bool(isinstance(a, Mapping) and isinstance(b, Mapping) and all(
        isinstance(a.get(key), str) and a.get(key) == b.get(key)
        for key in ("pullback_risk_state", "pullback_class", "distribution_risk")
    ))


def _read_bound_weekly_issue(repo_root: Path, week_start: datetime) -> tuple[Mapping[str, Any], str, str] | None:
    """One weekly machine package, accepted only through its own hash-binding delivery pointer."""
    iso = week_start.isocalendar()
    week_dir = Path(f"05_CYCLE_NAVIGATOR/weekly/{iso[0]:04d}/W{iso[1]:02d}")
    try:
        pointer = read_json(repo_root / week_dir / "CYCLE_NAVIGATOR_DELIVERY_POINTER.json")
        raw = (repo_root / week_dir / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json").read_bytes()
        package = json.loads(raw)
    except (OSError, ValueError):
        return None
    sha = digest(raw)
    if (not isinstance(pointer, Mapping) or not isinstance(package, Mapping)
            or pointer.get("contract") != "CYCLE_NAVIGATOR_DELIVERY_POINTER_v1"
            or pointer.get("week_dir") != week_dir.as_posix()
            or pointer.get("machine_package_sha256") != sha
            or pointer.get("issue_number") != package.get("issue_number")):
        return None
    return package, sha, f"{iso[0]:04d}-W{iso[1]:02d}"


def cn_protection_origin(
    cn_package: Mapping[str, Any] | None,
    cn_binding: Mapping[str, Any] | None,
    repo_root: Path,
) -> dict[str, Any]:
    """The last weekly issue that EVALUATED the protection state the bound issue carries.

    The offline issuer copies the state forward. Immutable packages from before its explicit state_basis field
    truncate the declared chain (W48 declares issue 35 although 35 and 34 were carried too), so the chain is
    walked issue by issue through hash-bound packages until one that was not carried. An unresolved chain is
    reported as UNRESOLVED; it is never guessed.
    """
    def unresolved(reason: str, chain: list[int]) -> dict[str, Any]:
        return {"status": "UNRESOLVED", "reason": reason, "chain_issue_numbers": chain}

    if not isinstance(cn_package, Mapping) or not isinstance(cn_binding, Mapping):
        return unresolved("CN_UNAVAILABLE", [])
    iso_year, iso_week = cn_binding.get("iso_year"), cn_binding.get("iso_week")
    cursor = _iso_week_start(iso_year, iso_week) if type(iso_year) is int and type(iso_week) is int else None
    issue_number = cn_package.get("issue_number")
    if cursor is None or type(issue_number) is not int or issue_number <= 0:
        return unresolved("CN_WEEK_OR_ISSUE_UNAVAILABLE", [])
    package: Mapping[str, Any] = cn_package
    sha = nested(cn_binding, "machine_package", "content_sha256")
    week = f"{iso_year:04d}-W{iso_week:02d}"
    chain = [issue_number]
    weeks_left = INHERITANCE_WALK_MAX_WEEKS
    while _cn_protection_inherited(package):
        declared = nested(package, "decision_projection", "protection", "inherited_from_issue_number")
        prior = declared if declared is not None else package.get("previous_issue_number")
        current = package.get("issue_number")
        if type(prior) is not int or type(current) is not int or not 0 < prior < current:
            return unresolved("PRIOR_ISSUE_NUMBER_INVALID", chain)
        found = None
        while weeks_left > 0 and found is None:
            weeks_left -= 1
            cursor = cursor - timedelta(days=7)
            candidate = _read_bound_weekly_issue(repo_root, cursor)
            if candidate is not None and candidate[0].get("issue_number") == prior:
                found = candidate
        if found is None:
            return unresolved("PRIOR_ISSUE_NOT_FOUND_HASH_BOUND", chain)
        earlier = _cn_issue_time(found[0])
        later = _cn_issue_time(package)
        if earlier is None or later is None or earlier >= later or not _same_protection_state(package, found[0]):
            return unresolved("PRIOR_ISSUE_STATE_OR_CLOCK_MISMATCH", chain)
        package, sha, week = found
        chain.append(prior)
    issued = _cn_issue_time(package)
    if issued is None:
        return unresolved("ORIGIN_ISSUE_CLOCK_UNAVAILABLE", chain)
    return {
        "status": "RESOLVED",
        "issue_number": package.get("issue_number"),
        "public_issue_number": package.get("public_issue_number"),
        "forecast_week": week,
        "evaluated_at_utc": _stamp(issued),
        "machine_package_sha256": sha,
        "issuer_method": cn_issuer_method(package),
        "chain_issue_numbers": chain,
        "issues_carried": len(chain) - 1,
    }


def risk_freshness(
    auto_state: Mapping[str, Any],
    protection: Mapping[str, Any],
    *,
    data_status: str,
    mapping_integrity_status: Any,
    source: Mapping[str, Any],
    band: Mapping[str, Any],
    cn_package: Mapping[str, Any] | None,
    cn_binding: Mapping[str, Any] | None,
    repo_root: Path,
    as_of: datetime,
) -> dict[str, Any]:
    """Fact 3. Provenance of the displayed risk state. Descriptive only.

      STALE      the daily source is provably past its SLA, or the bound weekly forecast week has expired;
      DEGRADED   the state is unavailable or the packet is not OK for any other reason;
      INHERITED  healthy evidence, but the weekly issuer carried the state forward instead of evaluating it;
      FRESH      healthy evidence and a state evaluated in the bound weekly issue.
    A completed-close floor breach never changes this status. It is named in basis, and cn_band_status stays the
    one place that states it. Neither field produces a risk severity, an action or a SELL.
    """
    as_of = as_of.astimezone(timezone.utc)
    cn_eligible = isinstance(cn_package, Mapping) and isinstance(cn_binding, Mapping) and cn_binding.get("status") == "PASS"
    basis: list[str] = []
    degraded: list[str] = []
    stale: list[str] = []

    source_status = str(source.get("status") or "UNKNOWN")
    if source_status == "STALE":
        stale.append("DAILY_SOURCE_STALE:" + ",".join(source.get("stale_lanes") or []))
    elif source_status != "FRESH":
        degraded.append("DAILY_SOURCE_FRESHNESS_UNKNOWN")
    if str(auto_state.get("validation_status") or "UNKNOWN") == "FAIL":
        degraded.append("OWNER_VALIDATION_FAIL")
    blockers = _core_blockers(auto_state)
    if blockers:
        degraded.append("CORE_BLOCKERS=" + ",".join(sorted(str(x) for x in blockers)))
    elif not _core_decision_ready(auto_state):
        degraded.append("DECISION_CONTEXT_" + str(auto_state.get("decision_context_status") or "UNKNOWN"))
    if not cn_eligible:
        binding_status = str((cn_binding or {}).get("status") or "UNAVAILABLE") if isinstance(cn_binding, Mapping) else "UNAVAILABLE"
        degraded.append("CN_BINDING_" + binding_status)
    if str(mapping_integrity_status) != "PASS":
        degraded.append("MAPPING_INTEGRITY_" + str(mapping_integrity_status or "UNKNOWN"))
    risk_state = str(protection.get("pullback_risk_state") or "UNAVAILABLE")
    if risk_state == "UNAVAILABLE" and cn_eligible and not degraded and not stale:
        degraded.append("PROTECTION_" + str(protection.get("data_quality") or "UNAVAILABLE"))
    if data_status != "OK" and not degraded and not stale:
        degraded.append("PACKET_DATA_STATUS_" + str(data_status))

    week_expired = False
    if cn_eligible:
        iso_year, iso_week = cn_binding.get("iso_year"), cn_binding.get("iso_week")
        week_start = _iso_week_start(iso_year, iso_week) if type(iso_year) is int and type(iso_week) is int else None
        if week_start is None:
            degraded.append("CN_WEEK_UNAVAILABLE")
        elif as_of >= week_start + timedelta(days=7) + SUNDAY_CLOSE_WINDOW:
            week_expired = True

    origin = cn_protection_origin(cn_package, cn_binding, repo_root) if cn_eligible else {"status": "UNRESOLVED", "reason": "CN_UNAVAILABLE", "chain_issue_numbers": []}
    inherited = bool(cn_eligible and _cn_protection_inherited(cn_package))
    state_basis = cn_protection_state_basis(cn_package if cn_eligible else None)

    if stale:
        status = "STALE"
        basis += stale + degraded
    elif degraded:
        status = "DEGRADED"
        basis += degraded
    elif week_expired:
        status = "STALE"
        basis.append("CN_FORECAST_WEEK_EXPIRED")
    elif inherited:
        status = "INHERITED"
    else:
        status = "FRESH"
        basis.append("EVALUATED_IN_BOUND_WEEKLY_ISSUE")
    if stale and week_expired:
        basis.append("CN_FORECAST_WEEK_EXPIRED")
    if inherited:
        basis.append(INHERITED_BASIS)
        if origin.get("status") != "RESOLVED":
            basis.append("INHERITANCE_ORIGIN_UNRESOLVED:" + str(origin.get("reason")))
    for label, key in (("FORECAST_WEEKLY_FLOOR_BREACHED", "first_weekly_floor_breach"),
                       ("FORECAST_DAILY_FLOOR_BREACHED", "first_daily_floor_breach")):
        marks = band.get(key)
        if isinstance(marks, Mapping):
            for asset in FLOOR_ASSETS:
                mark = marks.get(asset)
                if isinstance(mark, Mapping):
                    basis.append(f"{label}:{asset}@{mark.get('breach_at_utc')}")
    if risk_state != "UNAVAILABLE" and status in {"STALE", "DEGRADED"}:
        # G1: a packet that is not OK must not show a live state without saying so.
        basis.append("LIVE_RISK_STATE_DISPLAYED_ON_NON_OK_EVIDENCE")

    since = None
    if origin.get("status") == "RESOLVED":
        since = {
            "kind": "RISK_STATE_LAST_EVALUATED_BY_WEEKLY_ISSUER",
            "at_utc": origin["evaluated_at_utc"],
            "issue_number": origin["issue_number"],
            "public_issue_number": origin["public_issue_number"],
            "forecast_week": origin["forecast_week"],
        }
    return {
        "contract": RISK_FRESHNESS_CONTRACT,
        "status": status,
        "since": since,
        "basis": basis,
        "displayed_pullback_risk_state": risk_state,
        "inheritance": {
            "state_basis": state_basis,
            "issuer_method": cn_issuer_method(cn_package if cn_eligible else None),
            "declared_inherited_from_issue_number": nested(cn_package, "decision_projection", "protection", "inherited_from_issue_number") if cn_eligible else None,
            "origin": origin,
        },
        "source_freshness_status": source_status,
        "forecast_floor_status": band.get("forecast_floor_status"),
        "authority": DESCRIPTIVE_AUTHORITY,
        "release_stage": DESCRIPTIVE_RELEASE_STAGE,
    }


# Public projection: descriptive statuses only, never internal paths, commits or packet bindings.
_PUBLIC_DESCRIPTIVE_DROP = {
    "source_freshness": ("binding",),
    "cn_band_status": ("source",),
    "risk_freshness": (),
    "cycle_participation": (),
}


def _public_descriptive(compass: Mapping[str, Any]) -> dict[str, Any]:
    """Emit a block only when the frozen compass carries it, so a pre-upgrade slot re-projects byte-identically."""
    out: dict[str, Any] = {}
    for key, drop in _PUBLIC_DESCRIPTIVE_DROP.items():
        block = compass.get(key)
        if not isinstance(block, Mapping):
            continue
        view = {k: v for k, v in block.items() if k not in drop}
        if key == "cn_band_status" and isinstance(view.get("days"), list):
            view["days"] = [{k: v for k, v in day.items() if k != "source"} if isinstance(day, Mapping) else day for day in view["days"]]
        out[key] = view
    return out


def build_public_projection(compass: Mapping[str, Any]) -> dict[str, Any]:
    public_ladder = []
    for row in compass.get("capitalization_ladder", []):
        public_ladder.append({
            "segment": row.get("segment"),
            "status": row.get("status"),
            "action": row.get("action"),
            "direction": row.get("direction"),
            "eta": row.get("eta"),
            "reason": row.get("reason"),
        })
    public_horizons = {
        key: {
            "expected_direction": value.get("expected_direction"),
            "label": value.get("label"),
            "expected_path": value.get("expected_path"),
            "action_posture": value.get("action_posture"),
            "eta": value.get("eta"),
            **({"state": value.get("state"), "warning": value.get("warning"), "through_date": value.get("through_date"), "horizon_days": value.get("horizon_days")} if key == "CYCLE_ALTCOINS_3_8W" else {}),
        }
        for key, value in (compass.get("horizons") or {}).items()
        if key in HORIZON_ORDER and isinstance(value, Mapping)
    }
    # A legacy 12h direction may be scored only as its ORIGINAL historical issue.
    # Public projection must never silently promote a missing/forged marker to
    # a prospective prediction, nor inherit a 12h price-event ETA.
    twelve = public_horizons.get("NEXT_12H")
    original_twelve = (compass.get("horizons") or {}).get("NEXT_12H")
    eligible_nowcast = (
        compass.get("decision_policy_version") == OFFICIAL_COMPASS_DECISION_POLICY_VERSION
        and isinstance(twelve, dict) and isinstance(original_twelve, Mapping)
        and original_twelve.get("semantics") == NEXT_12H_NOWCAST_SEMANTICS
        and original_twelve.get("predictive_edge_status") == "NOT_PROVEN"
    )
    if isinstance(twelve, dict):
        twelve.update({
            "semantics": NEXT_12H_NOWCAST_SEMANTICS if eligible_nowcast else LEGACY_12H_SEMANTICS,
            "predictive_edge_status": "NOT_PROVEN",
            "eta_kind": "REASSESSMENT_WINDOW_ONLY" if eligible_nowcast else "NONE",
            "reassessment_window": original_twelve.get("reassessment_window") if eligible_nowcast else None,
            "eta": None,
        })
        if not eligible_nowcast:
            twelve.update({
                "expected_direction": "UNAVAILABLE",
                "label": "UNAVAILABLE",
                "expected_path": "Legacy or unverified 12h semantics, not a forward forecast.",
            })
    return {
        "contract": PUBLIC_COMPASS_CONTRACT,
        "compass_id": compass.get("compass_id"),
        "source_compass_sha256": compass.get("compass_sha256"),
        "issued_at_utc": compass.get("issued_at_utc"),
        "data_status": compass.get("data_status"),
        "market_now": compass.get("market_now"),
        "horizons": public_horizons,
        "bull_bear_scale": compass.get("bull_bear_scale"),
        "capitalization_ladder": public_ladder,
        "protection_tracker": compass.get("protection_tracker"),
        **_public_descriptive(compass),
        "sell_assessment": compass.get("sell_assessment"),
        "action_now": compass.get("action_now"),
        "next_meaningful_change_eta": None,
        "conclusion": (
            compass.get("conclusion")
            if eligible_nowcast and "next 12h" not in str(compass.get("conclusion") or "").lower()
            else "Observed market momentum only; no verified 12h forward forecast."
        ),
        "authority": {"official_navigation_output": True, "portfolio_execution": False, "source_override": False},
    }


def build_official_compass(
    auto_state: Mapping[str, Any],
    *,
    packet_path: Path,
    cn_package: Mapping[str, Any] | None,
    cn_binding: Mapping[str, Any] | None,
    repo_root: Path,
    issued_at: datetime | None = None,
    run_reason: str = "ON_DEMAND",
    prior_compass: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    issued = (issued_at or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(microsecond=0)
    issued_text = issued.isoformat().replace("+00:00", "Z")
    freshness = owner_freshness(auto_state, issued)
    cn_eligible = isinstance(cn_package, Mapping) and str((cn_binding or {}).get("status") or "UNAVAILABLE") == "PASS"
    eligible_cn = cn_package if cn_eligible else None
    action = action_context(auto_state, as_of=issued)
    market_now = derive_market_now(auto_state, action, as_of=issued)
    horizons = horizon_map(auto_state, action, eligible_cn, as_of=issued)
    ladder = capitalization_ladder(auto_state, action, market_now, as_of=issued)
    protection = protection_tracker(
        auto_state, action, market_now, eligible_cn, as_of=issued, prior_compass=prior_compass
    )
    bull_bear = bull_bear_scale(horizons)
    sell = sell_assessment(auto_state, protection, as_of=issued)
    evidence = evidence_snapshot(auto_state, packet_path)
    data_status = "OK" if _health_ok(auto_state, issued) and cn_eligible and evidence.get("mapping_integrity_status") == "PASS" else "DEGRADED"
    source = source_freshness(auto_state, issued, packet_path=packet_path)
    band = cn_band_status(auto_state, eligible_cn, cn_binding, repo_root, issued, source_status=source["status"])
    risk_provenance = risk_freshness(
        auto_state, protection, data_status=data_status,
        mapping_integrity_status=evidence.get("mapping_integrity_status"),
        source=source, band=band, cn_package=eligible_cn, cn_binding=cn_binding, repo_root=repo_root, as_of=issued,
    )
    decision_context = {
        "auto_market_state_packet_sha256": auto_state.get("packet_sha256"),
        "cycle_navigator_machine_sha256": nested(cn_binding, "machine_package", "content_sha256"),
        "cycle_navigator_projection_addendum_sha256": nested(cn_binding, "decision_projection_addendum", "content_sha256"),
        "cycle_navigator_projection_source": nested(cn_binding, "decision_projection_source"),
        "cycle_navigator_issue_number": nested(cn_binding, "issue_number"),
    }
    decision_context_fingerprint = digest(canon(decision_context))
    source_identity = (
        f"{decision_context_fingerprint}|{issued.date().isoformat()}|{run_reason}|"
        f"schema={OFFICIAL_COMPASS_SCHEMA_VERSION}|policy={OFFICIAL_COMPASS_DECISION_POLICY_VERSION}"
    )
    compass_id = f"CMP-{issued:%Y%m%d}-{digest(source_identity.encode())[:12]}"
    next_eta = None  # Observed momentum cannot supply a future price-event ETA.
    conclusion = (
        f"Observed momentum {horizons['NEXT_12H']['label']} (not a 12h forecast); {horizons['NEXT_1_3D']['label']} over 1-3d; "
        f"{horizons['NEXT_5_7D']['label']} over 5-7d; "
        f"{horizons['CYCLE_ALTCOINS_3_8W']['label']} for the long-cycle altcoin lane. Current action: {action.get('NOW')}."
    )
    packet = {
        "contract": OFFICIAL_COMPASS_CONTRACT,
        "schema_version": OFFICIAL_COMPASS_SCHEMA_VERSION,
        "decision_policy_version": OFFICIAL_COMPASS_DECISION_POLICY_VERSION,
        "decision_context_fingerprint": decision_context_fingerprint,
        "compass_id": compass_id,
        "issued_at_utc": issued_text,
        "run_reason": run_reason,
        "bound_main_sha": head_sha(repo_root),
        "data_status": data_status,
        "source_bindings": {
            "auto_market_state": {
                "packet_path": packet_path.as_posix(),
                "packet_sha256": auto_state.get("packet_sha256"),
                "packet_generated_at_utc": auto_state.get("packet_generated_at_utc"),
                "source_snapshot_commit_sha": nested(auto_state, "source_snapshot", "exact_commit_sha"),
                "freshness": freshness,
            },
            "cycle_navigator": cn_binding or {"status": "UNAVAILABLE"},
        },
        "evidence_snapshot": evidence,
        "cycle_participation": cycle_participation_readback(auto_state, as_of=issued),
        "market_reference": {
            "btc_usdt": finite(nested(auto_state, "normalized_state", "live_market", "btc_usdt")),
            "eth_usdt": finite(nested(auto_state, "normalized_state", "live_market", "eth_usdt")),
            "ethbtc": finite(nested(auto_state, "normalized_state", "live_market", "ethbtc")),
            "observation_open_utc": nested(auto_state, "normalized_state", "live_market", "observation_open_utc"),
        },
        "market_now": market_now,
        "cn_issuer_method": cn_issuer_method(eligible_cn),
        "cn_protection_state_basis": cn_protection_state_basis(eligible_cn),
        "source_freshness": source,
        "cn_band_status": band,
        "risk_freshness": risk_provenance,
        "horizons": horizons,
        "bull_bear_scale": bull_bear,
        "capitalization_ladder": ladder,
        "protection_tracker": protection,
        "sell_assessment": sell,
        "action_now": action.get("NOW"),
        "native_action_contract": action,
        "next_meaningful_change_eta": next_eta,
        "conclusion": conclusion,
        "outcome_maturity": {"12h": "PENDING_MATURITY", "72h": "PENDING_MATURITY", "168h": "PENDING_MATURITY"},
        "scoring_contract": "OFFICIAL_DAILY_COMPASS_SCORING_v3",
        "authority": OFFICIAL_AUTHORITY,
    }
    packet["compass_sha256"] = digest(canon({k: v for k, v in packet.items() if k != "compass_sha256"}))
    return packet


def _immutable_write(path: Path, value: Mapping[str, Any]) -> None:
    payload = canon(value)
    if path.exists():
        if path.read_bytes() != payload:
            raise ValueError(f"IMMUTABLE_COMPASS_REWRITE_BLOCKED:{path.as_posix()}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def write_official_compass(compass: Mapping[str, Any], output_root: Path) -> dict[str, Any]:
    dt = datetime.fromisoformat(str(compass["issued_at_utc"]).replace("Z", "+00:00"))
    day_dir = output_root / "daily" / dt.strftime("%Y/%m/%d")
    reason = str(compass.get("run_reason") or "ON_DEMAND")
    path = day_dir / f"{compass['compass_id']}.json"
    selected: Mapping[str, Any] = compass
    existing_freeze = False
    if reason == "ON_DEMAND":
        # A render request is allowed to materialize a fresh Compass only when
        # the canonical owner packet changed. Reusing the same owner evidence
        # must not manufacture another prospective observation.
        latest_pointer_path = output_root / "LATEST_COMPASS.json"
        if latest_pointer_path.exists():
            latest_pointer = read_json(latest_pointer_path)
            current_source_sha = nested(compass, "source_bindings", "auto_market_state", "packet_sha256")
            current_context_fingerprint = compass.get("decision_context_fingerprint")
            if latest_pointer.get("source_packet_sha256") == current_source_sha:
                latest_path_raw = latest_pointer.get("compass_path")
                if isinstance(latest_path_raw, str) and latest_path_raw:
                    latest_path = Path(latest_path_raw)
                    if latest_path.exists():
                        latest_compass = read_json(latest_path)
                        if (
                            int(latest_compass.get("schema_version") or 0) == int(compass.get("schema_version") or 0)
                            and latest_compass.get("decision_policy_version") == compass.get("decision_policy_version")
                            and latest_compass.get("decision_context_fingerprint") == current_context_fingerprint
                            and latest_compass.get("protection_tracker") is not None
                            and latest_compass.get("sell_assessment") is not None
                        ):
                            path = latest_path
    scheduled_slot_reasons = {"SCHEDULED_MORNING", "SCHEDULED_EVENING"}
    if reason in scheduled_slot_reasons and day_dir.exists():
        # Each scheduled slot owns one immutable freeze per day. A retry of the
        # same slot reuses that slot only; morning must never suppress evening.
        for candidate in sorted(day_dir.glob("CMP-*.json")):
            prior_candidate = read_json(candidate)
            if (
                str(prior_candidate.get("run_reason") or "") == reason
                and int(prior_candidate.get("schema_version") or 0) == int(compass.get("schema_version") or 0)
                and prior_candidate.get("decision_policy_version") == compass.get("decision_policy_version")
            ):
                path = candidate
                break
    elif reason == "SCHEDULED_DAILY" and day_dir.exists():
        # Legacy compatibility for historical single-daily freezes. Policy
        # migrations must still create a new immutable artifact rather than
        # reusing bytes produced under different decision semantics.
        for candidate in sorted(day_dir.glob("CMP-*.json")):
            prior_candidate = read_json(candidate)
            if (
                str(prior_candidate.get("run_reason") or "") == reason
                and int(prior_candidate.get("schema_version") or 0) == int(compass.get("schema_version") or 0)
                and prior_candidate.get("decision_policy_version") == compass.get("decision_policy_version")
            ):
                path = candidate
                break
    if path.exists():
        prior = read_json(path)
        expected_id = path.stem
        expected_sha = digest(canon({k: v for k, v in prior.items() if k != "compass_sha256"}))
        if prior.get("compass_id") != expected_id or prior.get("compass_sha256") != expected_sha:
            raise ValueError(f"IMMUTABLE_COMPASS_INTEGRITY_FAILED:{path.as_posix()}")
        selected = prior
        existing_freeze = True
        dt = datetime.fromisoformat(str(selected["issued_at_utc"]).replace("Z", "+00:00"))
    _immutable_write(path, selected)
    compass_content_sha256 = digest(path.read_bytes())
    public = build_public_projection(selected)
    public["projection_sha256"] = digest(canon({k: v for k, v in public.items() if k != "projection_sha256"}))
    public_path = output_root / "public" / dt.strftime("%Y/%m/%d") / f"{selected['compass_id']}.json"
    _immutable_write(public_path, public)
    public_content_sha256 = digest(public_path.read_bytes())

    pointer = {
        "contract": OFFICIAL_COMPASS_POINTER,
        "compass_id": selected.get("compass_id"),
        "issued_at_utc": selected.get("issued_at_utc"),
        "data_status": selected.get("data_status"),
        "compass_path": path.as_posix(),
        "compass_sha256": selected.get("compass_sha256"),
        "compass_content_sha256": compass_content_sha256,
        "public_projection_path": public_path.as_posix(),
        "public_projection_sha256": public.get("projection_sha256"),
        "public_projection_content_sha256": public_content_sha256,
        "source_packet_sha256": nested(selected, "source_bindings", "auto_market_state", "packet_sha256"),
        "decision_policy_version": selected.get("decision_policy_version"),
        "decision_context_fingerprint": selected.get("decision_context_fingerprint"),
        "authority": OFFICIAL_AUTHORITY,
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "LATEST_COMPASS.json").write_bytes(canon(pointer))
    public_pointer = {
        "contract": PUBLIC_COMPASS_POINTER,
        "compass_id": selected.get("compass_id"),
        "issued_at_utc": selected.get("issued_at_utc"),
        "data_status": selected.get("data_status"),
        "public_projection_path": public_path.as_posix(),
        "public_projection_sha256": public.get("projection_sha256"),
        "public_projection_content_sha256": public_content_sha256,
    }
    (output_root / "PUBLIC_LATEST_COMPASS.json").write_bytes(canon(public_pointer))
    return {
        "status": "EXISTING_DAILY_FREEZE" if existing_freeze else "WRITTEN",
        "path": path.as_posix(),
        "public_path": public_path.as_posix(),
        "pointer": (output_root / "LATEST_COMPASS.json").as_posix(),
        "compass_id": selected.get("compass_id"),
        "sha256": selected.get("compass_sha256"),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--auto-state-pointer", type=Path, default=DEFAULT_AUTO_STATE_POINTER)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--budget-status", type=Path)
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--official-daily-compass", action="store_true")
    parser.add_argument("--run-reason", default="ON_DEMAND")
    parser.add_argument("--issued-at-utc")
    args = parser.parse_args()

    pointer, auto_state, packet_path = load_auto_state_bundle(args.repo_root, args.auto_state_pointer)
    if args.official_daily_compass:
        issued = None
        if args.issued_at_utc:
            issued = datetime.fromisoformat(args.issued_at_utc.replace("Z", "+00:00"))
        cn_package, cn_binding = load_cn_context(args.repo_root)
        prior_compass = None
        prior_pointer_path = args.repo_root / args.output_root / "LATEST_COMPASS.json"
        if prior_pointer_path.exists():
            prior_compass = load_prior_compass(args.repo_root, args.output_root / "LATEST_COMPASS.json")
        compass = build_official_compass(
            auto_state,
            packet_path=packet_path,
            cn_package=cn_package,
            cn_binding=cn_binding,
            repo_root=args.repo_root,
            issued_at=issued,
            run_reason=args.run_reason,
            prior_compass=prior_compass,
        )
        result = compass if args.no_write else write_official_compass(compass, args.output_root)
        print(json.dumps(result, sort_keys=True))
        return

    external_budget = None
    if args.budget_status:
        p = args.repo_root / args.budget_status
        if p.exists():
            external_budget = read_json(p)
    packet = build(auto_state, external_budget=external_budget)
    result = packet if args.no_write else {**write(packet, args.output_root), "NOW": packet["action"]["NOW"], "DATA_HEALTH": packet["DATA_HEALTH"]["status"], "BUDGET_HEALTH": packet["BUDGET_HEALTH"]["status"]}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
