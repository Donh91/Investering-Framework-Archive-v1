#!/usr/bin/env python3
"""Native Handlekompas and official daily Compass owner.

The hourly Native Handlekompas remains a source-call-free readback of the pinned
Auto Market State. The official daily Compass is a frozen, auditable navigation
artifact derived from the same owner plus current Cycle Navigator context.
Neither surface has portfolio-execution or source-override authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

CONTRACT = "NATIVE_HANDLEKOMPAS_v1"
POINTER = "NATIVE_HANDLEKOMPAS_LATEST_POINTER_v1"
OFFICIAL_COMPASS_CONTRACT = "OFFICIAL_DAILY_COMPASS_v1"
OFFICIAL_COMPASS_POINTER = "OFFICIAL_DAILY_COMPASS_LATEST_POINTER_v1"
PUBLIC_COMPASS_CONTRACT = "PUBLIC_COMPASS_PROJECTION_v1"
PUBLIC_COMPASS_POINTER = "PUBLIC_COMPASS_LATEST_POINTER_v1"
DEFAULT_AUTO_STATE_POINTER = Path("04_MARKET_LEARNING/entry_signals/auto_market_state/LATEST.json")
DEFAULT_CN_POINTER = Path("05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json")
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

CAPITALIZATION_ORDER = ("BTC", "ETH", "LARGE_CAPS", "MID_CAPS", "SMALL_CAPS", "MICROCAPS")
HORIZON_ORDER = ("NEXT_12H", "NEXT_1_3D", "NEXT_5_7D", "CYCLE_ALTCOINS_3_8W")
SCORED_HORIZON_ORDER = ("NEXT_12H", "NEXT_1_3D", "NEXT_5_7D")
ALTCOIN_STATES = {
    "DEFENSIVE", "CONSOLIDATION", "PRE_ROTATION", "ROTATION", "BROAD_ALTSEASON",
    "PARABOLIC_ALTSEASON", "DISTRIBUTION", "EXIT_RISK", "UNCLEAR",
}
ALTCOIN_WARNINGS = {
    "NONE", "PARABOLIC_ALTSEASON_WARNING", "DISTRIBUTION_WARNING",
    "EXIT_WARNING", "STRUCTURAL_BREAKDOWN_WARNING",
}
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


def file_binding(repo_root: Path, rel_path: Path) -> dict[str, Any]:
    path = repo_root / rel_path
    raw = path.read_bytes()
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
    package = read_json(abs_package)
    if pointer.get("issue_number") != package.get("issue_number"):
        return None, {"status": "DEGRADED", "reason": "CN_POINTER_PACKAGE_ISSUE_MISMATCH"}
    return package, {
        "status": "PASS",
        "pointer": file_binding(repo_root, pointer_path),
        "machine_package": file_binding(repo_root, package_path),
        "issue_number": package.get("issue_number"),
        "iso_week": pointer.get("iso_week"),
        "iso_year": pointer.get("iso_year"),
    }


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
    ns = auto_state.get("normalized_state") or {}
    live = ns.get("live_market") or {}
    breadth = nested(ns, "breadth", "aggregate") or {}
    entry = ns.get("entry_signal_reference") or {}
    ratio = finite(live.get("ethbtc"))
    advance = finite(breadth.get("advance_ratio"))
    blockers = list(auto_state.get("blockers") or [])
    validation = str(auto_state.get("validation_status") or "UNKNOWN")
    decision_health = str(auto_state.get("decision_context_status") or "UNKNOWN")
    entry_state = entry.get("state") if isinstance(entry, Mapping) else None

    healthy = validation != "FAIL" and decision_health == "PASS" and not blockers and _health_ok(auto_state, as_of)
    if healthy and entry_state == "GRADUATED_ALTCOIN_TOPUP_ACTIVE":
        now = "GRADUATED_TOPUP_ACTIVE"
    elif advance is not None and advance < 0.40:
        now = "HOLD_DEFENSIVE_WAIT"
    elif not healthy:
        now = "HOLD_WAIT_DATA_DEGRADED"
    elif ratio is not None and ratio > 0.03 and advance is not None and advance >= 0.50:
        now = "PREPARE"
    else:
        now = "HOLD_WAIT"

    why: list[str] = []
    if ratio is not None:
        why.append(f"ETHBTC={ratio:.6f}")
    if advance is not None:
        why.append(f"TOP100_BREADTH={advance:.2f}")
    if entry_state:
        why.append(f"ENTRY_SIGNAL={entry_state}")
    if blockers:
        why.append("BLOCKERS=" + ",".join(blockers))

    return {
        "NOW": now,
        "PREPARE": "ETHBTC_STRENGTH_PLUS_BREADTH_GTE_0_50_PLUS_HEALTHY_NATIVE_STATE",
        "TOPUP_GATE": "ONLY_EXISTING_ENTRY_SIGNAL_OR_REGISTERED_CANONICAL_CONFIRMATION_CAN_ACTIVATE_TOPUP; PROXY_BREADTH_NEVER_SELF_PROMOTES",
        "RISK_DOWN": "BREADTH_LT_0_40_OR_ETHBTC_WEAKENS_OR_NATIVE_HEALTH_DEGRADES_MATERIALLY",
        "WHY": why,
    }


def build(auto_state: Mapping[str, Any], *, external_budget: Mapping[str, Any] | None = None, now: datetime | None = None) -> dict[str, Any]:
    generated = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(microsecond=0)
    provider = classify_provider_health(auto_state)
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
        "action": action_context(auto_state),
        "DATA_HEALTH": {
            "status": auto_state.get("validation_status"),
            "decision_context_status": auto_state.get("decision_context_status"),
            "blockers": list(auto_state.get("blockers") or []),
            "optional_degraded_lanes": list(auto_state.get("optional_degraded_lanes") or []),
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


def _feature(feature_id: str, value: Any, unit: str | None, source: str, observed_at: Any, health: Any) -> dict[str, Any]:
    return {
        "feature_id": feature_id,
        "value": value if value is None or isinstance(value, (str, int, float, bool)) else None,
        "unit": unit,
        "source_path": source,
        "observed_at": observed_at,
        "freshness_state": health or "UNKNOWN",
        "eligibility": "ELIGIBLE" if health == "PASS" else "CONTEXT_ONLY_OR_DEGRADED",
    }


def evidence_snapshot(auto_state: Mapping[str, Any], packet_path: Path) -> dict[str, Any]:
    ns = auto_state.get("normalized_state") or {}
    live = ns.get("live_market") or {}
    breadth = nested(ns, "breadth", "aggregate") or {}
    derivatives = ns.get("derivatives") or {}
    dominance = ns.get("btc_dominance") or {}
    etf = ns.get("settled_etf") or {}
    stable = ns.get("stablecoin_liquidity") or {}
    sentiment = ns.get("sentiment") or {}
    altseason = ns.get("altseason_context") or {}
    source_health = auto_state.get("source_health") or {}
    observed = auto_state.get("packet_generated_at_utc")

    rows = [
        _feature("btc_usdt", finite(live.get("btc_usdt")), "USD", packet_path.as_posix(), observed, nested(source_health, "hourly_market", "status")),
        _feature("eth_usdt", finite(live.get("eth_usdt")), "USD", packet_path.as_posix(), observed, nested(source_health, "hourly_market", "status")),
        _feature("ethbtc", finite(live.get("ethbtc")), "ratio", packet_path.as_posix(), observed, nested(source_health, "hourly_market", "status")),
        _feature("breadth_advance_ratio", finite(breadth.get("advance_ratio")), "ratio", packet_path.as_posix(), observed, nested(source_health, "breadth", "status")),
        _feature("breadth_advancers", finite(breadth.get("advancers")), "count", packet_path.as_posix(), observed, nested(source_health, "breadth", "status")),
        _feature("breadth_decliners", finite(breadth.get("decliners")), "count", packet_path.as_posix(), observed, nested(source_health, "breadth", "status")),
        _feature("breadth_equal_weight_24h", finite(breadth.get("equal_weight_mean_return_24h_pct")), "pct", packet_path.as_posix(), observed, nested(source_health, "breadth", "status")),
        _feature("btc_dominance_pct", finite(dominance.get("value_pct")), "pct", packet_path.as_posix(), observed, nested(source_health, "btc_dominance", "status")),
        _feature("btc_etf_musd", finite(etf.get("btc_reported_total_musd")), "MUSD", packet_path.as_posix(), observed, nested(source_health, "settled_etf", "status")),
        _feature("eth_etf_musd", finite(etf.get("eth_reported_total_musd")), "MUSD", packet_path.as_posix(), observed, nested(source_health, "settled_etf", "status")),
        _feature("stablecoin_total_usd", finite(stable.get("total_usd")), "USD", packet_path.as_posix(), observed, nested(source_health, "stablecoin_liquidity", "status")),
        _feature("btc_open_interest", finite(nested(derivatives, "BTC-USDT-SWAP", "open_interest", "open_interest")), "contracts", packet_path.as_posix(), observed, nested(source_health, "derivatives", "status")),
        _feature("eth_open_interest", finite(nested(derivatives, "ETH-USDT-SWAP", "open_interest", "open_interest")), "contracts", packet_path.as_posix(), observed, nested(source_health, "derivatives", "status")),
        _feature("btc_funding", finite(nested(derivatives, "BTC-USDT-SWAP", "funding", "funding_rate")), "rate", packet_path.as_posix(), observed, nested(source_health, "derivatives", "status")),
        _feature("eth_funding", finite(nested(derivatives, "ETH-USDT-SWAP", "funding", "funding_rate")), "rate", packet_path.as_posix(), observed, nested(source_health, "derivatives", "status")),
        _feature("sentiment_state", sentiment.get("classification") if isinstance(sentiment, Mapping) else None, None, packet_path.as_posix(), observed, nested(source_health, "sentiment", "status")),
        _feature("altseason_score_90d", finite(nested(altseason, "blockchaincenter_altcoin_season", "horizons", "90", "published_score")), "index", packet_path.as_posix(), observed, nested(source_health, "altseason_context", "status")),
        _feature("entry_signal_state", nested(ns, "entry_signal_reference", "state"), None, packet_path.as_posix(), observed, nested(source_health, "entry_signal_reference", "status")),
    ]
    available = sum(row["value"] is not None for row in rows)
    return {
        "selected_features": rows,
        "available_features": available,
        "expected_selected_features": len(rows),
        "full_feature_universe_reference": {
            "contract": auto_state.get("contract"),
            "packet_path": packet_path.as_posix(),
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
            maximum = finite(row.get("max_age_seconds"))
            stamp = _parse_utc(row.get("timestamp"))
            if maximum is None:
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


def _health_ok(auto_state: Mapping[str, Any], as_of: datetime | None = None) -> bool:
    structural = (
        str(auto_state.get("validation_status") or "UNKNOWN") == "PASS"
        and str(auto_state.get("decision_context_status") or "UNKNOWN") == "PASS"
        and not list(auto_state.get("blockers") or [])
    )
    if not structural:
        return False
    return as_of is None or owner_freshness(auto_state, as_of)["status"] == "PASS"


def derive_market_now(auto_state: Mapping[str, Any], action: Mapping[str, Any], *, as_of: datetime | None = None) -> dict[str, Any]:
    if not _health_ok(auto_state, as_of):
        return {"directional_state": "UNAVAILABLE", "regime": "DATA_DEGRADED", "summary": "Current market direction is unavailable because required state is degraded."}
    posture = str(action.get("NOW") or "HOLD_WAIT")
    btc = _delta_pct(auto_state, "btc_usdt")
    eth = _delta_pct(auto_state, "eth_usdt")
    ethbtc = _delta_pct(auto_state, "ethbtc")
    if posture == "GRADUATED_TOPUP_ACTIVE":
        direction = "BULLISH"
    elif posture == "PREPARE":
        direction = "BULLISH" if btc is not None and ethbtc is not None and btc >= 0 and ethbtc >= 0 else "MIXED"
    elif posture == "HOLD_DEFENSIVE_WAIT":
        direction = "BEARISH" if btc is not None and eth is not None and btc < 0 and eth < 0 else "MIXED"
    else:
        direction = "NEUTRAL" if btc is not None and eth is not None and btc * eth >= 0 else "MIXED"
    summary_map = {
        "BULLISH": "Market state is constructive, but deployment still depends on the existing confirmation gate.",
        "BEARISH": "Market pressure is negative and breadth/relative-strength conditions favor capital protection.",
        "NEUTRAL": "Market is balanced enough that waiting for confirmation has more edge than forcing direction.",
        "MIXED": "Market signals conflict; near-term navigation stays selective and confirmation-driven.",
    }
    return {"directional_state": direction, "regime": posture, "summary": summary_map[direction]}


def _weekly_direction(cn_package: Mapping[str, Any] | None) -> str:
    if not isinstance(cn_package, Mapping):
        return "NO_EDGE"
    text = " ".join(str(cn_package.get(k) or "") for k in ("market_state", "base_case_this_week")).lower()
    if "consolidation" in text or "unresolved" in text:
        return "SIDEWAYS"
    if "confirmed breakdown" in text and "no confirmed breakdown" not in text and "rather than a confirmed breakdown" not in text:
        return "DOWN"
    if "broad expansion" in text and "not" not in text:
        return "UP"
    return "NO_EDGE"


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


def _altcoin_cycle_lane(cn_package: Mapping[str, Any] | None, posture: str, issued: datetime) -> dict[str, Any]:
    if not isinstance(cn_package, Mapping):
        return {
            **_unavailable_horizon("Current Cycle Navigator context is unavailable; the long-cycle lane fails closed."),
            "state": "UNCLEAR", "warning": "NONE", "through_date": None, "horizon_days": None,
        }
    structured = cn_package.get("compass_4_8_weeks")
    if not isinstance(structured, Mapping):
        structured = {}
    text = " ".join(str(cn_package.get(key) or "") for key in (
        "market_state", "base_case_this_week", "base_case_2_3_weeks", "base_case_4_8_weeks",
    )).lower()
    countdown = cn_package.get("altseason_countdown")
    countdown_text = " ".join(
        f"{row.get('phase', '')} {row.get('window', '')}"
        for row in countdown if isinstance(row, Mapping)
    ).lower() if isinstance(countdown, list) else ""
    explicit_state = str(structured.get("state") or "").upper()
    if explicit_state in ALTCOIN_STATES:
        state = explicit_state
    elif "exit risk" in text:
        state = "EXIT_RISK"
    elif "distribution" in text:
        state = "DISTRIBUTION"
    elif "parabolic altseason" in text:
        state = "PARABOLIC_ALTSEASON"
    elif "broad altseason" in countdown_text and "paused" not in countdown_text and "inactive" not in countdown_text:
        state = "BROAD_ALTSEASON"
    elif "volatile consolidation" in text or "consolidation persists" in text:
        state = "CONSOLIDATION"
    elif "pre_rotation" in text or "pre-rotation" in text or "selective eth" in text:
        state = "PRE_ROTATION"
    elif "rotation" in text:
        state = "ROTATION"
    else:
        state = "UNCLEAR"
    warning = str(structured.get("warning") or "NONE").upper()
    if warning not in ALTCOIN_WARNINGS:
        warning = "NONE"
    direction = {
        "PRE_ROTATION": "UP", "ROTATION": "UP", "BROAD_ALTSEASON": "UP", "PARABOLIC_ALTSEASON": "UP",
        "CONSOLIDATION": "SIDEWAYS", "DEFENSIVE": "DOWN", "DISTRIBUTION": "DOWN", "EXIT_RISK": "DOWN",
    }.get(state, "NO_EDGE")
    action_posture = "BUY" if posture == "GRADUATED_TOPUP_ACTIVE" else "PREPARE_BUY" if posture == "PREPARE" else "HOLD"
    through = issued.date() + timedelta(days=28)
    summary = str(
        structured.get("summary") or cn_package.get("base_case_4_8_weeks")
        or cn_package.get("base_case_2_3_weeks") or cn_package.get("base_case_this_week")
        or "No eligible long-cycle summary is published."
    )
    return {
        "expected_direction": direction,
        "label": state,
        "state": state,
        "expected_path": summary,
        "action_posture": action_posture,
        "warning": warning,
        "through_date": through.isoformat(),
        "horizon_days": 28,
        "confirmation_trigger": {"type": "CURRENT_CN_STATE", "states": ["ROTATION", "BROAD_ALTSEASON"]},
        "invalidation_trigger": {"type": "CURRENT_CN_STATE", "states": ["DEFENSIVE", "DISTRIBUTION", "EXIT_RISK"]},
        "eta": f"through {through.isoformat()}",
        "confidence": None,
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
        return {key: dict(unavailable) for key in HORIZON_ORDER}

    posture = str(action.get("NOW") or "HOLD_WAIT")
    current = derive_market_now(auto_state, action, as_of=as_of)["directional_state"]
    weekly = _weekly_direction(cn_package)

    if posture == "GRADUATED_TOPUP_ACTIVE":
        d12, a12 = "UP", "DEPLOY"
    elif posture == "PREPARE":
        d12, a12 = ("UP" if current == "BULLISH" else "MIXED"), "PREPARE"
    elif posture == "HOLD_DEFENSIVE_WAIT":
        d12, a12 = ("DOWN" if current == "BEARISH" else "MIXED"), "HOLD"
    else:
        d12, a12 = "SIDEWAYS", "HOLD"

    if not isinstance(cn_package, Mapping):
        forward_unavailable = _unavailable_horizon("Current Cycle Navigator context is unavailable; this forward lane fails closed.")
        return {
            "NEXT_12H": {
                "expected_direction": d12, "label": "BULLISH" if d12 == "UP" else "BEARISH" if d12 == "DOWN" else "NEUTRAL" if d12 == "SIDEWAYS" else "MIXED",
                "expected_path": "Current-state continuation unless the native confirmation or deterioration gate changes state.",
                "action_posture": a12,
                "confirmation_trigger": {"type": "ACTION_STATE", "states": ["PREPARE", "GRADUATED_TOPUP_ACTIVE"]},
                "invalidation_trigger": {"type": "ACTION_STATE", "states": ["HOLD_DEFENSIVE_WAIT", "HOLD_WAIT_DATA_DEGRADED"]},
                "eta": "0-12h", "confidence": None,
            },
            "NEXT_1_3D": dict(forward_unavailable),
            "NEXT_5_7D": dict(forward_unavailable),
            "CYCLE_ALTCOINS_3_8W": _altcoin_cycle_lane(None, posture, as_of or datetime.now(timezone.utc)),
        }

    if posture in {"GRADUATED_TOPUP_ACTIVE", "PREPARE"} and weekly in {"UP", "SIDEWAYS"}:
        d13, a13 = "UP", "PREPARE"
    elif posture == "HOLD_DEFENSIVE_WAIT":
        d13, a13 = ("DOWN" if weekly == "DOWN" else "MIXED"), "WAIT"
    else:
        d13, a13 = weekly if weekly != "NO_EDGE" else "SIDEWAYS", "WAIT"

    d57 = weekly
    if d57 == "NO_EDGE":
        d57 = "SIDEWAYS" if posture in {"HOLD_WAIT", "HOLD_DEFENSIVE_WAIT"} else "MIXED"
    a57 = "PREPARE" if posture in {"PREPARE", "GRADUATED_TOPUP_ACTIVE"} and d57 != "DOWN" else "WAIT"

    label = lambda d: "BULLISH" if d == "UP" else "BEARISH" if d == "DOWN" else "NEUTRAL" if d == "SIDEWAYS" else "MIXED"
    confirm = {"type": "ACTION_STATE", "states": ["PREPARE", "GRADUATED_TOPUP_ACTIVE"]}
    invalidate = {"type": "ACTION_STATE", "states": ["HOLD_DEFENSIVE_WAIT", "HOLD_WAIT_DATA_DEGRADED"]}
    return {
        "NEXT_12H": {
            "expected_direction": d12, "label": label(d12),
            "expected_path": "Current-state continuation unless the native confirmation or deterioration gate changes state.",
            "action_posture": a12, "confirmation_trigger": confirm, "invalidation_trigger": invalidate,
            "eta": "0-12h", "confidence": None,
        },
        "NEXT_1_3D": {
            "expected_direction": d13, "label": label(d13),
            "expected_path": "Short-horizon state is cross-checked against the current weekly regime; transmission must improve before risk moves down-cap.",
            "action_posture": a13, "confirmation_trigger": confirm, "invalidation_trigger": invalidate,
            "eta": "24-72h", "confidence": None,
        },
        "NEXT_5_7D": {
            "expected_direction": d57, "label": label(d57),
            "expected_path": str((cn_package or {}).get("base_case_this_week") or "No stronger weekly path is eligible; remain fail-closed."),
            "action_posture": a57, "confirmation_trigger": confirm, "invalidation_trigger": invalidate,
            "eta": "120-168h", "confidence": None,
        },
        "CYCLE_ALTCOINS_3_8W": _altcoin_cycle_lane(cn_package, posture, as_of or datetime.now(timezone.utc)),
    }


def capitalization_ladder(
    auto_state: Mapping[str, Any], action: Mapping[str, Any], market_now: Mapping[str, Any],
    *, as_of: datetime | None = None,
) -> list[dict[str, Any]]:
    if not _health_ok(auto_state, as_of):
        return [
            {"segment": seg, "status": "UNAVAILABLE", "direction": "UNAVAILABLE", "eta": None,
             "reason": "Required current-state evidence is degraded.",
             "upgrade_trigger": {"type": "ACTION_STATE", "states": ["PREPARE", "GRADUATED_TOPUP_ACTIVE"]},
             "deterioration_trigger": {"type": "ACTION_STATE", "states": ["HOLD_WAIT_DATA_DEGRADED"]}}
            for seg in CAPITALIZATION_ORDER
        ]
    posture = str(action.get("NOW") or "HOLD_WAIT")
    direction = str(market_now.get("directional_state") or "MIXED")
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
        "LARGE_CAPS": "First alt-risk tier eligible after ETH/breadth confirmation.",
        "MID_CAPS": "Requires durable large-cap transmission and stronger breadth.",
        "SMALL_CAPS": "Requires confirmed mid-cap participation before deployment.",
        "MICROCAPS": "Highest-beta tier remains last in the rotation sequence.",
    }
    confirm = {"type": "ACTION_STATE", "states": ["PREPARE", "GRADUATED_TOPUP_ACTIVE"]}
    deteriorate = {"type": "ACTION_STATE", "states": ["HOLD_DEFENSIVE_WAIT", "HOLD_WAIT_DATA_DEGRADED"]}
    eta_by_state = {"HOLD": "now", "DEPLOY": "now", "PREPARE": "0-3d", "WAIT": "1-7d conditional", "HARD_WAIT": "no fixed ETA"}
    rows = []
    for seg, state in zip(CAPITALIZATION_ORDER, states):
        rows.append({
            "segment": seg,
            "status": state,
            "direction": direction if seg in {"BTC", "ETH"} else ("MIXED" if state in {"WAIT", "HARD_WAIT"} else direction),
            "eta": eta_by_state[state],
            "reason": reasons[seg],
            "upgrade_trigger": confirm,
            "deterioration_trigger": deteriorate,
        })
    return rows


def build_public_projection(compass: Mapping[str, Any]) -> dict[str, Any]:
    public_ladder = []
    for row in compass.get("capitalization_ladder", []):
        public_ladder.append({
            "segment": row.get("segment"),
            "status": row.get("status"),
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
    return {
        "contract": PUBLIC_COMPASS_CONTRACT,
        "compass_id": compass.get("compass_id"),
        "issued_at_utc": compass.get("issued_at_utc"),
        "data_status": compass.get("data_status"),
        "market_now": compass.get("market_now"),
        "horizons": public_horizons,
        "capitalization_ladder": public_ladder,
        "action_now": compass.get("action_now"),
        "next_meaningful_change_eta": compass.get("next_meaningful_change_eta"),
        "conclusion": compass.get("conclusion"),
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
    evidence = evidence_snapshot(auto_state, packet_path)
    data_status = "OK" if _health_ok(auto_state, issued) and cn_eligible else "DEGRADED"
    source_identity = f"{auto_state.get('packet_sha256')}|{issued.date().isoformat()}|{run_reason}"
    compass_id = f"CMP-{issued:%Y%m%d}-{digest(source_identity.encode())[:12]}"
    next_eta = horizons["NEXT_12H"].get("eta") if data_status == "OK" else None
    conclusion = (
        f"{horizons['NEXT_12H']['label']} next 12h; {horizons['NEXT_1_3D']['label']} over 1-3d; "
        f"{horizons['NEXT_5_7D']['label']} over 5-7d; "
        f"{horizons['CYCLE_ALTCOINS_3_8W']['label']} for the long-cycle altcoin lane. Current action: {action.get('NOW')}."
    )
    packet = {
        "contract": OFFICIAL_COMPASS_CONTRACT,
        "schema_version": 1,
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
        "market_reference": {
            "btc_usdt": finite(nested(auto_state, "normalized_state", "live_market", "btc_usdt")),
            "eth_usdt": finite(nested(auto_state, "normalized_state", "live_market", "eth_usdt")),
            "ethbtc": finite(nested(auto_state, "normalized_state", "live_market", "ethbtc")),
            "observation_open_utc": nested(auto_state, "normalized_state", "live_market", "observation_open_utc"),
        },
        "market_now": market_now,
        "horizons": horizons,
        "capitalization_ladder": ladder,
        "action_now": action.get("NOW"),
        "native_action_contract": action,
        "next_meaningful_change_eta": next_eta,
        "conclusion": conclusion,
        "outcome_maturity": {"12h": "PENDING_MATURITY", "72h": "PENDING_MATURITY", "168h": "PENDING_MATURITY"},
        "scoring_contract": "OFFICIAL_DAILY_COMPASS_SCORING_v1",
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
            if latest_pointer.get("source_packet_sha256") == current_source_sha:
                latest_path_raw = latest_pointer.get("compass_path")
                if isinstance(latest_path_raw, str) and latest_path_raw:
                    latest_path = Path(latest_path_raw)
                    if latest_path.exists():
                        path = latest_path
    scheduled_slot_reasons = {"SCHEDULED_MORNING", "SCHEDULED_EVENING"}
    if reason in scheduled_slot_reasons and day_dir.exists():
        # Each scheduled slot owns one immutable freeze per day. A retry of the
        # same slot reuses that slot only; morning must never suppress evening.
        for candidate in sorted(day_dir.glob("CMP-*.json")):
            prior_candidate = read_json(candidate)
            if str(prior_candidate.get("run_reason") or "") == reason:
                path = candidate
                break
    elif reason == "SCHEDULED_DAILY" and day_dir.exists():
        # Legacy compatibility for historical single-daily freezes.
        existing = sorted(day_dir.glob("CMP-*.json"))
        if existing:
            path = existing[0]
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
        compass = build_official_compass(
            auto_state,
            packet_path=packet_path,
            cn_package=cn_package,
            cn_binding=cn_binding,
            repo_root=args.repo_root,
            issued_at=issued,
            run_reason=args.run_reason,
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
