#!/usr/bin/env python3
"""EDGE-001/T5 two-sleeve research ROW CONTRACT, not a portfolio simulator.

Validates structural/causal preconditions of candidate shadow rows. It does
NOT verify provider provenance, run historical scoring, admit a row to PIT,
calculate edge, persist values, or authorize BUY/SELL. Private numeric inputs
must never be serialized into the public Archive or PR/CI logs.

Owner: existing EDGE-001 #1530, source/PIT #1596, Strategist #1157.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timedelta
from math import isfinite
from re import fullmatch

CONTRACT = "EDGE001_TWO_SLEEVE_SHADOW_ROW_v1"
ROLES = frozenset({"PRE_IGNITION_MICRO", "LATE_LIQUID_LARGE", "CASH"})
STATES = frozenset({"NOT_ADMITTED", "SOURCE_REVIEW_PENDING", "SHADOW_ACCOUNTING_CANDIDATE"})
REQUIRED_FIELDS = frozenset({
    "record_id", "source_commit", "source_receipt_id", "source_contract_id",
    "first_known_at", "asof_at", "issued_at", "delivered_at",
    "sleeve_role", "original_consensus_or_abstention", "market_regime_frozen",
    "asset_universe_vintage", "event_family_id", "currency", "initial_capital",
    "notional", "execution_at", "quote_at", "quote_first_known_at",
    "capacity_at_execution", "bid_ask", "fees_slippage_gas",
    "filled_fraction", "missed_fill", "opportunity_cost", "drawdown",
    "terminal_net_liquidatable_wealth", "hold_baseline_wealth",
    "tax_assumption_or_unknown", "status",
})


def _fail(reason: str) -> None:
    # Constant error codes only. Never echo an untrusted private record/value.
    raise ValueError(reason)


def _utc(raw: object, field: str, *, nullable: bool = False) -> datetime | None:
    if raw is None and nullable:
        return None
    if not isinstance(raw, str) or not raw.endswith("Z"):
        _fail("TWO_SLEEVE_CLOCK_INVALID_" + field.upper())
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        _fail("TWO_SLEEVE_CLOCK_INVALID_" + field.upper())
    if dt.utcoffset() != timedelta(0):
        _fail("TWO_SLEEVE_CLOCK_NOT_UTC_" + field.upper())
    return dt


def _money(raw: object, field: str, *, nullable: bool = False,
           positive: bool = False) -> float | None:
    if raw is None and nullable:
        return None
    if type(raw) not in (int, float) or not isfinite(raw):
        _fail("TWO_SLEEVE_FINITE_REQUIRED_" + field.upper())
    if raw < 0 or (positive and raw == 0):
        _fail("TWO_SLEEVE_NONNEGATIVE_REQUIRED_" + field.upper())
    return float(raw)


def validate_two_sleeve_shadow_row(record: Mapping) -> dict:
    """Fail closed on broken structural inputs, NEVER certify economic evidence.

    This function deliberately returns a value-free metadata verdict. Even a
    syntactically valid SHA/receipt is NOT proof of provider-first-known or fill.
    """
    if not isinstance(record, Mapping) or set(record) != REQUIRED_FIELDS:
        _fail("TWO_SLEEVE_FIELDS_EXACT_SET_REQUIRED")
    for key in ("record_id", "source_receipt_id", "source_contract_id",
                "original_consensus_or_abstention", "market_regime_frozen",
                "asset_universe_vintage", "event_family_id"):
        if not isinstance(record[key], str) or not record[key].strip():
            _fail("TWO_SLEEVE_REQUIRED_ID_INVALID")
    if not isinstance(record["source_commit"], str) or not fullmatch(
        r"[0-9a-fA-F]{40}", record["source_commit"]
    ):
        _fail("TWO_SLEEVE_SHA40_REQUIRED")
    if record["sleeve_role"] not in ROLES or record["status"] not in STATES:
        _fail("TWO_SLEEVE_RESEARCH_ONLY_ENUM_REQUIRED")
    if record["currency"] != "USD":
        _fail("TWO_SLEEVE_CURRENCY_USD_REQUIRED")
    if record["tax_assumption_or_unknown"] != "UNKNOWN":
        _fail("TWO_SLEEVE_TAX_UNVERIFIED_MUST_BE_UNKNOWN")
    first = _utc(record["first_known_at"], "first_known_at")
    asof = _utc(record["asof_at"], "asof_at")
    issued = _utc(record["issued_at"], "issued_at")
    delivered = _utc(record["delivered_at"], "delivered_at")
    if not first <= asof <= issued <= delivered:
        _fail("TWO_SLEEVE_CAUSAL_SOURCE_CLOCK_INVALID")

    initial = _money(record["initial_capital"], "initial_capital", positive=True)
    notional = _money(record["notional"], "notional")
    if notional > initial:
        _fail("TWO_SLEEVE_UNMODELED_LEVERAGE_BLOCKED")
    fraction = _money(record["filled_fraction"], "filled_fraction")
    if fraction > 1:
        _fail("TWO_SLEEVE_FILL_FRACTION_INVALID")
    if type(record["missed_fill"]) is not bool:
        _fail("TWO_SLEEVE_MISSED_FILL_BOOL_REQUIRED")
    if record["missed_fill"] and fraction > 0:
        _fail("TWO_SLEEVE_MISSED_FILL_CANNOT_BE_FILLED")
    cap = _money(record["capacity_at_execution"], "capacity_at_execution",
                 nullable=True)
    _money(record["opportunity_cost"], "opportunity_cost", nullable=True)
    dd = _money(record["drawdown"], "drawdown", nullable=True)
    if dd is not None and dd > 1:
        _fail("TWO_SLEEVE_DRAWDOWN_FRACTION_INVALID")
    terminal = _money(record["terminal_net_liquidatable_wealth"],
                      "terminal_net_liquidatable_wealth", nullable=True)
    _money(record["hold_baseline_wealth"], "hold_baseline_wealth",
           nullable=True)

    quote_at = _utc(record["quote_at"], "quote_at", nullable=True)
    quote_known = _utc(record["quote_first_known_at"], "quote_first_known_at",
                       nullable=True)
    execution = _utc(record["execution_at"], "execution_at", nullable=True)
    quote = record["bid_ask"]
    if quote is not None:
        if not isinstance(quote, Mapping) or set(quote) != {"bid", "ask"}:
            _fail("TWO_SLEEVE_BID_ASK_PAIR_REQUIRED")
        bid = _money(quote["bid"], "bid", positive=True)
        ask = _money(quote["ask"], "ask", positive=True)
        if ask < bid:
            _fail("TWO_SLEEVE_NEGATIVE_SPREAD_BLOCKED")
    costs = record["fees_slippage_gas"]
    if not isinstance(costs, Mapping) or set(costs) != {"fees", "slippage", "gas"}:
        _fail("TWO_SLEEVE_COST_COMPONENTS_REQUIRED")
    for key in ("fees", "slippage", "gas"):
        _money(costs[key], key, nullable=not bool(fraction))

    if record["sleeve_role"] == "CASH":
        if notional != 0 or fraction != 0 or record["missed_fill"]:
            _fail("TWO_SLEEVE_CASH_NO_TRADE_REQUIRED")
        if any(v is not None for v in (quote, cap, quote_at, quote_known, execution)):
            _fail("TWO_SLEEVE_CASH_NO_EXECUTION_QUOTE")
    elif fraction > 0:
        if notional <= 0 or cap is None or notional * fraction > cap:
            _fail("TWO_SLEEVE_FILL_EXCEEDS_CAPACITY")
        if any(v is None for v in (quote, quote_at, quote_known, execution)):
            _fail("TWO_SLEEVE_EXECUTION_PROOF_FIELDS_REQUIRED")
        if not delivered < quote_at <= quote_known <= execution:
            _fail("TWO_SLEEVE_QUOTE_AFTER_DELIVERY_REQUIRED")
    elif terminal is not None:
        # No credit for an unsellable/failed microcap exit.
        _fail("TWO_SLEEVE_UNFILLED_TERMINAL_WEALTH_BLOCKED")

    return {
        "contract": CONTRACT,
        "structural_status": "STRUCTURAL_ONLY_UNVERIFIED_PROVENANCE",
        "provider_first_known_verified": False,
        "actual_fill_verified": False,
        "historical_pit_admitted": False,
        "portfolio_economic_edge_admitted": False,
        "statistical_significance_admitted": False,
        "live_portfolio_action_authorized": False,
        "private_values_echoed": False,
    }


def audit_two_sleeve_shadow_batch(records: Sequence[Mapping]) -> dict:
    """Compare eligibility of one three-role cohort, NOT investment returns.

    Same initial capital and issue clock are necessary but insufficient for
    matched historical controls. No numeric or private data is emitted.
    """
    if not isinstance(records, (list, tuple)) or not records:
        _fail("TWO_SLEEVE_NONEMPTY_BATCH_REQUIRED")
    for row in records:
        validate_two_sleeve_shadow_row(row)
    if len({row["record_id"] for row in records}) != len(records):
        _fail("TWO_SLEEVE_DUPLICATE_RECORD")
    roles = [row["sleeve_role"] for row in records]
    if len(set(roles)) != len(roles):
        _fail("TWO_SLEEVE_DUPLICATE_ROLE")
    if len({row["initial_capital"] for row in records}) != 1:
        _fail("TWO_SLEEVE_UNMATCHED_STARTING_WEALTH")
    if len({row["asof_at"] for row in records}) != 1:
        _fail("TWO_SLEEVE_UNMATCHED_DECISION_CLOCK")
    if len({row["event_family_id"] for row in records}) != 1:
        _fail("TWO_SLEEVE_UNMATCHED_EVENT_FAMILY")
    return {
        "contract": CONTRACT,
        "roles_present": sorted(roles),
        "complete_three_role_cohort": set(roles) == ROLES,
        "matched_start_and_clock": True,
        "valid_for_historical_scoring": False,
        "economic_edge_claim_allowed": False,
        "independent_event_family_n": None,
        "evidence_status": "RESEARCH_SCHEMA_ONLY_NOT_ADMITTED",
    }
