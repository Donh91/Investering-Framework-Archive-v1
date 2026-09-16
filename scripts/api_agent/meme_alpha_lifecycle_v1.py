from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, Set

DEFAULT_PHOENIX_CONFIG: Dict[str, float] = {
    "minimum_age_hours": 24.0,
    "minimum_drawdown_pct": 65.0,
    "minimum_liquidity_usd": 10_000.0,
    "minimum_liquidity_survival_ratio": 0.35,
    "minimum_buyer_velocity_acceleration": 1.50,
    "maximum_seller_velocity_ratio_for_recovery": 0.90,
    "minimum_volume_reacceleration": 1.50,
    "maximum_social_saturation": 0.65,
    "minimum_onchain_social_lead_minutes": 30.0,
    "minimum_holder_breadth_delta_pct": 5.0,
    "maximum_top10_concentration_delta_pct": -2.0,
    "maximum_retest_liquidity_deterioration_pct": 25.0,
}

PHOENIX_STATES = {
    "INELIGIBLE",
    "CRASHED_SURVIVOR",
    "DORMANT",
    "PHOENIX_WAKEUP",
    "PHOENIX_PRE_RECLAIM_CONVERGENCE",
    "PHOENIX_RECLAIM",
    "PHOENIX_RETEST_PENDING",
    "PHOENIX_RETEST_PASSED",
    "PHOENIX_GAMBLE_CANDIDATE",
    "FAILED_RECLAIM",
    "INVALIDATED",
}


def _f(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _ratio(current: Any, baseline: Any) -> float:
    b = _f(baseline)
    if b <= 0:
        return 0.0
    return _f(current) / b


def _drawdown_pct(peak: Any, current: Any) -> float:
    p = _f(peak)
    c = _f(current)
    if p <= 0 or c < 0:
        return 0.0
    return max(0.0, min(100.0, (1.0 - c / p) * 100.0))


def phoenix_eligibility(snapshot: Dict[str, Any], config: Dict[str, float] | None = None) -> Dict[str, Any]:
    cfg = {**DEFAULT_PHOENIX_CONFIG, **(config or {})}
    drawdown = _drawdown_pct(snapshot.get("prior_peak_market_cap_usd"), snapshot.get("current_market_cap_usd"))
    liquidity_survival = _ratio(snapshot.get("current_liquidity_usd"), snapshot.get("prior_peak_liquidity_usd"))

    reasons = []
    if not bool(snapshot.get("identity_ok", False)):
        reasons.append("IDENTITY_UNRESOLVED")
    if _f(snapshot.get("age_hours")) < cfg["minimum_age_hours"]:
        reasons.append("TOO_YOUNG")
    if snapshot.get("prior_demand_state") != "REAL_PRIOR_DEMAND":
        reasons.append("PRIOR_DEMAND_UNPROVEN")
    if drawdown < cfg["minimum_drawdown_pct"]:
        reasons.append("DRAWDOWN_TOO_SHALLOW")
    if _f(snapshot.get("current_liquidity_usd")) < cfg["minimum_liquidity_usd"]:
        reasons.append("LIQUIDITY_TOO_LOW")
    if not bool(snapshot.get("sellability_pass", False)):
        reasons.append("SELLABILITY_UNRESOLVED_OR_FAILED")

    return {
        "eligible": not reasons,
        "reasons": reasons,
        "drawdown_from_verified_peak_pct": round(drawdown, 6),
        "liquidity_survival_ratio": round(liquidity_survival, 6),
    }


def hard_fail_reasons(snapshot: Dict[str, Any]) -> list[str]:
    checks = {
        "IDENTITY_CONFLICT": bool(snapshot.get("identity_conflict", False)),
        "HONEYPOT_OR_FAILED_SELL": bool(snapshot.get("honeypot_or_failed_sell", False)),
        "NO_EXECUTABLE_LIQUIDITY": bool(snapshot.get("no_executable_liquidity", False)),
        "CRITICAL_LIQUIDITY_WITHDRAWAL": bool(snapshot.get("critical_liquidity_withdrawal", False)),
        "CONTROL_ENTITY_DUMP": bool(snapshot.get("deployer_or_control_entity_dump", False)),
        "PRIOR_PEAK_ARTIFACT": bool(snapshot.get("prior_peak_artifact", False)),
    }
    return [name for name, fired in checks.items() if fired]


def derive_phoenix_signal_families(snapshot: Dict[str, Any], config: Dict[str, float] | None = None) -> Set[str]:
    cfg = {**DEFAULT_PHOENIX_CONFIG, **(config or {})}
    families: Set[str] = set()

    buyer_accel = _ratio(snapshot.get("buyer_velocity"), snapshot.get("dormant_buyer_velocity"))
    seller_ratio = _ratio(snapshot.get("seller_velocity"), snapshot.get("dormant_seller_velocity"))
    volume_accel = _ratio(snapshot.get("volume_velocity"), snapshot.get("dormant_volume_velocity"))
    microstructure = (
        buyer_accel >= cfg["minimum_buyer_velocity_acceleration"]
        and (
            (seller_ratio > 0 and seller_ratio <= cfg["maximum_seller_velocity_ratio_for_recovery"])
            or volume_accel >= cfg["minimum_volume_reacceleration"]
        )
    )
    if microstructure:
        families.add("M")

    liquidity_survival = _ratio(snapshot.get("current_liquidity_usd"), snapshot.get("prior_peak_liquidity_usd"))
    if (
        _f(snapshot.get("current_liquidity_usd")) >= cfg["minimum_liquidity_usd"]
        and liquidity_survival >= cfg["minimum_liquidity_survival_ratio"]
    ):
        families.add("L")

    if int(snapshot.get("independent_quality_wallet_reentries") or 0) >= 1:
        families.add("W")

    social_saturation = _f(snapshot.get("social_saturation"), 1.0)
    onchain_lead = _f(snapshot.get("onchain_wakeup_lead_minutes_vs_social"), -1.0)
    if social_saturation <= cfg["maximum_social_saturation"] and onchain_lead >= cfg["minimum_onchain_social_lead_minutes"]:
        families.add("S")

    holder_breadth_delta = _f(snapshot.get("holder_breadth_delta_pct"))
    top10_delta = _f(snapshot.get("top10_concentration_delta_pct"))
    if holder_breadth_delta >= cfg["minimum_holder_breadth_delta_pct"] or top10_delta <= cfg["maximum_top10_concentration_delta_pct"]:
        families.add("H")

    if bool(snapshot.get("reclaim_confirmed", False)):
        families.add("P")

    return families


def phoenix_retest_passes(snapshot: Dict[str, Any], config: Dict[str, float] | None = None) -> bool:
    cfg = {**DEFAULT_PHOENIX_CONFIG, **(config or {})}
    if not bool(snapshot.get("retest_completed", False)):
        return False
    if not bool(snapshot.get("sellability_pass", False)):
        return False
    if bool(snapshot.get("quality_wallet_distribution", False)):
        return False
    if bool(snapshot.get("price_structure_invalidated", False)):
        return False
    if bool(snapshot.get("sell_pressure_reaccelerated", False)):
        return False
    if _f(snapshot.get("retest_liquidity_deterioration_pct")) > cfg["maximum_retest_liquidity_deterioration_pct"]:
        return False
    if not bool(snapshot.get("buyer_breadth_above_dormant_baseline", False)):
        return False
    return True


def classify_phoenix_state(
    snapshot: Dict[str, Any],
    previous_state: str | None = None,
    config: Dict[str, float] | None = None,
) -> Dict[str, Any]:
    cfg = {**DEFAULT_PHOENIX_CONFIG, **(config or {})}
    previous = previous_state or "INELIGIBLE"
    if previous not in PHOENIX_STATES:
        raise ValueError(f"unknown previous_state: {previous}")

    hard_fails = hard_fail_reasons(snapshot)
    eligibility = phoenix_eligibility(snapshot, cfg)
    families = derive_phoenix_signal_families(snapshot, cfg)

    result: Dict[str, Any] = {
        "previous_state": previous,
        "signal_families": sorted(families),
        "hard_fail_reasons": hard_fails,
        **eligibility,
    }

    if hard_fails:
        result["state"] = "INVALIDATED"
        return result
    if not eligibility["eligible"]:
        result["state"] = "INELIGIBLE"
        return result

    if previous == "PHOENIX_RETEST_PENDING":
        if not bool(snapshot.get("retest_completed", False)):
            result["state"] = "PHOENIX_RETEST_PENDING"
            return result
        if phoenix_retest_passes(snapshot, cfg):
            result["state"] = "PHOENIX_RETEST_PASSED"
        else:
            result["state"] = "FAILED_RECLAIM"
        return result

    if previous == "PHOENIX_RETEST_PASSED":
        if bool(snapshot.get("deep_research_pass", False)) and "M" in families and ("W" in families or "L" in families) and len(families) >= 3:
            result["state"] = "PHOENIX_GAMBLE_CANDIDATE"
        else:
            result["state"] = "PHOENIX_RETEST_PASSED"
        return result

    if previous == "PHOENIX_RECLAIM" and bool(snapshot.get("pullback_active", False)):
        result["state"] = "PHOENIX_RETEST_PENDING"
        return result

    social_ok = _f(snapshot.get("social_saturation"), 1.0) <= cfg["maximum_social_saturation"]
    pre_reclaim = "M" in families and ("L" in families or "W" in families) and len(families) >= 3 and social_ok

    if pre_reclaim and bool(snapshot.get("reclaim_confirmed", False)):
        result["state"] = "PHOENIX_RECLAIM"
        return result
    if pre_reclaim:
        result["state"] = "PHOENIX_PRE_RECLAIM_CONVERGENCE"
        return result

    wakeup = len(families - {"P"}) >= 2 and ("M" in families or "L" in families)
    if wakeup:
        result["state"] = "PHOENIX_WAKEUP"
        return result

    any_recovery = bool(families - {"P"})
    result["state"] = "CRASHED_SURVIVOR" if any_recovery else "DORMANT"
    return result


def attach_lifecycle_observation(
    token_state: Dict[str, Any],
    snapshot: Dict[str, Any],
    observed_at_utc: str,
    config: Dict[str, float] | None = None,
) -> Dict[str, Any]:
    """Return a copy with an append-only Phoenix observation.

    This helper deliberately does not execute trades, size positions, mutate Moonshot
    champion rules, or infer historical values that are absent from the snapshot.
    """
    state = deepcopy(token_state)
    previous = state.get("phoenix_state")
    classified = classify_phoenix_state(snapshot, previous_state=previous, config=config)
    state["phoenix_state"] = classified["state"]
    state.setdefault("phoenix_history", []).append(
        {
            "observed_at_utc": observed_at_utc,
            "state": classified["state"],
            "signal_families": classified["signal_families"],
            "drawdown_from_verified_peak_pct": classified["drawdown_from_verified_peak_pct"],
            "liquidity_survival_ratio": classified["liquidity_survival_ratio"],
            "hard_fail_reasons": classified["hard_fail_reasons"],
        }
    )
    return state
