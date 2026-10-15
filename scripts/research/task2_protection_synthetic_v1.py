#!/usr/bin/env python3
"""TASK2/EDGE-001 research-only, SYNTHETIC single-warning economic falsifier.

No historical dataset, source admission, portfolio advice, SELL rule, model call,
API access, parameter tuning, or Round3 outcome join. Existing #1530/#1553 own
later promotion. Evaluates only predeclared one-warning policies on synthetic paths.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from math import isfinite

UTC = timezone.utc
STATES = {"ELEVATED", "HIGH", "CONFIRMED"}


@dataclass(frozen=True)
class Quote:
    at: datetime
    known_at: datetime
    bid: float
    ask: float
    capacity_usd: float


@dataclass(frozen=True)
class Warning:
    source_known_at: datetime
    issued_at: datetime
    delivered_at: datetime
    state: str
    original_proof: str = "SYNTHETIC_FIXTURE_ONLY"


@dataclass(frozen=True)
class Policy:
    trim_fraction: float
    execution_delay_h: float
    fixed_reentry_h: float
    fee_fraction: float
    slippage_fraction: float
    gas_usd_per_fill: float = 0.0


def _utc(value: datetime) -> bool:
    return (isinstance(value, datetime) and value.tzinfo is not None and
            value.utcoffset() == timedelta(0))


def _clean_nonnegative(value: float) -> bool:
    return isinstance(value, (int, float)) and isfinite(value) and value >= 0


def validate(quotes: list[Quote], warning: Warning, policy: Policy, initial_usd: float) -> None:
    if len(quotes) < 2 or not _clean_nonnegative(initial_usd) or initial_usd <= 0:
        raise ValueError("SYNTHETIC_TAPE_OR_CAPITAL_INVALID")
    if warning.original_proof != "SYNTHETIC_FIXTURE_ONLY" or warning.state not in STATES:
        raise ValueError("HISTORICAL_OR_UNAUTHORIZED_WARNING_BLOCKED")
    if not all(_utc(t) for t in (warning.source_known_at, warning.issued_at, warning.delivered_at)):
        raise ValueError("CLOCK_NOT_UTC")
    if not warning.source_known_at <= warning.issued_at <= warning.delivered_at:
        raise ValueError("LOOKAHEAD_OR_DELIVERY_CLOCK_INVERSION")
    for field in (policy.trim_fraction, policy.execution_delay_h, policy.fixed_reentry_h,
                  policy.fee_fraction, policy.slippage_fraction, policy.gas_usd_per_fill):
        if not _clean_nonnegative(field):
            raise ValueError("POLICY_COST_OR_DELAY_INVALID")
    if not 0 < policy.trim_fraction <= 1 or policy.fee_fraction >= 1 or policy.slippage_fraction >= 1:
        raise ValueError("POLICY_RANGE_INVALID")
    previous = None
    for quote in quotes:
        if not _utc(quote.at) or not _utc(quote.known_at):
            raise ValueError("CLOCK_NOT_UTC")
        if previous and quote.at <= previous:
            raise ValueError("OUT_OF_ORDER_OR_DUPLICATE_QUOTE")
        # This fixture uses simultaneous quote publication, not hindsight OHLC fills.
        if quote.known_at != quote.at:
            raise ValueError("QUOTE_CAPTURE_NOT_SYNTHETIC_EXECUTION_CLOCK")
        if not all(_clean_nonnegative(v) for v in (quote.bid, quote.ask, quote.capacity_usd)):
            raise ValueError("NONFINITE_OR_NEGATIVE_QUOTE")
        if not 0 < quote.bid <= quote.ask or quote.capacity_usd <= 0:
            raise ValueError("BID_ASK_OR_LIQUIDITY_INVALID")
        previous = quote.at


def simulate_synthetic(quotes: list[Quote], warning: Warning, policy: Policy,
                       initial_usd: float = 10_000.0) -> dict:
    """Single fixed warning, next executable quote, fixed-clock reentry; NO hindsight.

    Outright refusal of historical source requests is intentional: an independent
    PIT/outcome gate must be implemented by an approved owner, not caller flags.
    """
    validate(quotes, warning, policy, initial_usd)
    start_mid = (quotes[0].bid + quotes[0].ask) / 2
    units_initial = initial_usd / start_mid  # incumbent holder; not a new entry
    hold_equity = []
    sim_equity = []
    units, cash = units_initial, 0.0
    trading_fees, slippage_paid, gas_paid, turnover = 0.0, 0.0, 0.0, 0.0
    sale_at = buy_at = None
    sale_status = "NO_ELIGIBLE_EXECUTION_QUOTE"
    reentry_status = "NOT_APPLICABLE"
    first_sell_clock = warning.delivered_at + timedelta(hours=policy.execution_delay_h)
    intended_buy_clock = None
    for quote in quotes:
        if sale_at is None and quote.at > quotes[0].at and quote.at > first_sell_clock:
            desired_units = units_initial * policy.trim_fraction
            notional = desired_units * quote.bid
            if notional <= quote.capacity_usd:
                proceeds = notional * (1 - policy.slippage_fraction) * (1 - policy.fee_fraction) - policy.gas_usd_per_fill
                if proceeds > 0:
                    trading_fees += notional * (1 - policy.slippage_fraction) * policy.fee_fraction
                    slippage_paid += notional * policy.slippage_fraction
                    gas_paid += policy.gas_usd_per_fill
                    turnover += notional
                    units -= desired_units
                    cash += proceeds
                    sale_at = quote.at
                    intended_buy_clock = sale_at + timedelta(hours=policy.fixed_reentry_h)
                    sale_status = "FILLED_SYNTHETIC"
                else:
                    sale_status = "BLOCKED_BY_COSTS"
            else:
                sale_status = "BLOCKED_BY_LIQUIDITY"
            # One attempt, no cherry-picked fill time or retry after a worse quote.
            first_sell_clock = datetime.max.replace(tzinfo=UTC)
        if sale_at is not None and buy_at is None and quote.at > sale_at and quote.at >= intended_buy_clock:
            desired_notional = cash
            if desired_notional <= quote.capacity_usd:
                investable = cash * (1 - policy.fee_fraction) - policy.gas_usd_per_fill
                if investable > 0:
                    trading_fees += cash * policy.fee_fraction
                    slippage_paid += investable * policy.slippage_fraction / (1 + policy.slippage_fraction)
                    gas_paid += policy.gas_usd_per_fill
                    turnover += cash
                    units += investable / (quote.ask * (1 + policy.slippage_fraction))
                    cash = 0.0
                    buy_at = quote.at
                    reentry_status = "FILLED_SYNTHETIC"
                else:
                    reentry_status = "BLOCKED_BY_COSTS"
            else:
                reentry_status = "BLOCKED_BY_LIQUIDITY"
            # One planned buy attempt, no after-the-fact optimization.
            intended_buy_clock = datetime.max.replace(tzinfo=UTC)
        # Like-for-like terminal liquidation quote and fee; cash carries no risk-free interest.
        hold_equity.append(units_initial * quote.bid * (1 - policy.fee_fraction))
        sim_equity.append(units * quote.bid * (1 - policy.fee_fraction) + cash)
    if sale_at is not None and buy_at is None and reentry_status == "NOT_APPLICABLE":
        reentry_status = "HORIZON_ENDED_BEFORE_REENTRY"

    def drawdown(equity: list[float]) -> float:
        peak = initial_usd
        worst = 0.0
        for wealth in equity:
            peak = max(peak, wealth)
            worst = max(worst, 1 - wealth / peak)
        return worst

    hold_final, policy_final = hold_equity[-1], sim_equity[-1]
    return {
        "contract": "TASK2_EDGE001_SYNTHETIC_COUNTERFACTUAL_v1",
        "evidence_class": "SYNTHETIC_ONLY_NOT_HISTORICAL_EDGE",
        "live_sell_rule": "NONE",
        "capital_role": "EXISTING_HOLDER_ONLY",
        "input_quotes": len(quotes),
        "sale_status": sale_status,
        "reentry_status": reentry_status,
        "sale_at": sale_at.isoformat() if sale_at else None,
        "reentry_at": buy_at.isoformat() if buy_at else None,
        "terminal_hold_usd": round(hold_final, 6),
        "terminal_policy_usd": round(policy_final, 6),
        "net_delta_vs_hold_usd": round(policy_final - hold_final, 6),
        "time_partially_out_of_market_hours": round((buy_at or quotes[-1].at).timestamp()/3600 - sale_at.timestamp()/3600, 6) if sale_at else 0.0,
        "trade_notional_turnover_usd": round(turnover, 6),
        "intermediate_trading_fees_usd": round(trading_fees, 6),
        "intermediate_slippage_usd": round(slippage_paid, 6),
        "gas_cost_usd": round(gas_paid, 6),
        "spread_included_in_bid_ask": True,
        "terminal_fee_applied_symmetrically_to_held_units": True,
        "max_drawdown_hold_fraction": round(drawdown(hold_equity), 8),
        "max_drawdown_policy_fraction": round(drawdown(sim_equity), 8),
        "historical_result_admissible": False,
        "statistical_significance_admissible": False,
        "portfolio_action_authorized": False,
    }


def price_only_lead_synthetic(quotes: list[Quote], warning: Warning) -> dict:
    """Frozen P1/P2-like synthetic price references, outcome-free warning-clock comparison.

    The first running-peak crossing is computed online on this fictional quote tape;
    no later global peak/trough is used. NOT an admitted historic lead statistic.
    """
    validate(quotes, warning, Policy(.5, 0, 1, 0, 0), 10_000.0)
    if not quotes[0].at <= warning.delivered_at <= quotes[-1].at:
        raise ValueError("WARNING_DELIVERY_OUTSIDE_SYNTHETIC_TAPE")
    peaks = 0.0
    first = {"P1_PRICE_ONLY_5PCT": None, "P2_PRICE_ONLY_3PCT": None}
    for quote in quotes:
        spot = (quote.bid + quote.ask) / 2
        peaks = max(peaks, spot)
        drawdown = 1 - spot / peaks
        if drawdown >= .05 - 1e-12 and first["P1_PRICE_ONLY_5PCT"] is None:
            first["P1_PRICE_ONLY_5PCT"] = quote.at
        if drawdown >= .03 - 1e-12 and first["P2_PRICE_ONLY_3PCT"] is None:
            first["P2_PRICE_ONLY_3PCT"] = quote.at
    return {
        "evidence_class": "SYNTHETIC_ONLY_NOT_HISTORICAL_EDGE",
        "lead_vs_p1_hours": (first["P1_PRICE_ONLY_5PCT"] - warning.delivered_at).total_seconds()/3600
                              if first["P1_PRICE_ONLY_5PCT"] else None,
        "lead_vs_p2_hours": (first["P2_PRICE_ONLY_3PCT"] - warning.delivered_at).total_seconds()/3600
                              if first["P2_PRICE_ONLY_3PCT"] else None,
        "p1_crossing_utc": first["P1_PRICE_ONLY_5PCT"].isoformat() if first["P1_PRICE_ONLY_5PCT"] else None,
        "p2_crossing_utc": first["P2_PRICE_ONLY_3PCT"].isoformat() if first["P2_PRICE_ONLY_3PCT"] else None,
        "no_price_trigger_in_window": all(t is None for t in first.values()),
        "independent_event_families_verified": False,
        "historical_lead_certified": False,
    }

