"""Offline falsifier for vault equity curves polluted by depositor flows.

Research-only. No provider access, strategy evaluation, score, order or wallet.
The model deliberately supports only a witnessed before/after external-flow
boundary at each checkpoint. It is NOT a generic reconstruction of Hypercore
share supply, fees, or actual executable investor returns.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

CONTRACT = "RESEARCH_VAULT_FLOW_INTEGRITY_V1"
ALLOWED_EVIDENCE = {"SYNTHETIC_FIXTURE", "UNATTESTED_RESEARCH"}
EPSILON = Decimal("0.000001")


class EvidenceRefused(ValueError):
    """Cannot infer a flow-neutral return from incomplete or future evidence."""


def _utc(value: object, field: str) -> datetime:
    if not isinstance(value, str):
        raise EvidenceRefused(f"{field}:MISSING_UTC")
    try:
        date = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise EvidenceRefused(f"{field}:BAD_UTC") from exc
    if date.tzinfo is None or date.utcoffset() != timedelta(0):
        raise EvidenceRefused(f"{field}:EXPLICIT_UTC_REQUIRED")
    return date


def _amount(value: object, field: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise EvidenceRefused(f"{field}:DECIMAL_STRING_REQUIRED")
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise EvidenceRefused(f"{field}:INVALID_AMOUNT") from exc
    if not number.is_finite():
        raise EvidenceRefused(f"{field}:NONFINITE_AMOUNT")
    return number


def _point(record: dict, *, after: datetime, as_of: datetime, idx: int) -> tuple:
    prefix = f"points[{idx}]"
    if not isinstance(record, dict):
        raise EvidenceRefused(f"{prefix}:NOT_OBJECT")
    event = _utc(record.get("event_at_utc"), prefix + ".event_at_utc")
    known = _utc(record.get("first_known_at_utc"), prefix + ".first_known_at_utc")
    if not after < event <= known <= as_of:
        raise EvidenceRefused(f"{prefix}:CLOCK_LEAK_OR_REORDER")
    for flag in ("flow_boundary_complete", "valuation_evidence_complete"):
        if record.get(flag) is not True:
            raise EvidenceRefused(f"{prefix}:{flag}:UNPROVEN")
    before_flow = _amount(record.get("equity_before_flow_usd"), prefix + ".equity_before_flow_usd")
    flow = _amount(record.get("external_net_flow_usd"), prefix + ".external_net_flow_usd")
    after_flow = _amount(record.get("equity_after_flow_usd"), prefix + ".equity_after_flow_usd")
    if before_flow < 0 or after_flow < 0:
        raise EvidenceRefused(f"{prefix}:NEGATIVE_EQUITY")
    if abs(before_flow + flow - after_flow) > EPSILON:
        raise EvidenceRefused(f"{prefix}:FLOW_RECONCILIATION_FAILED")
    return event, before_flow, flow, after_flow


def evaluate(payload: dict) -> dict:
    """Compare naive account-value moves with witnessed flow-neutral subperiod returns.

    Inputs must be explicitly frozen synthetic fixtures or unadmitted research.
    Unknown fee treatment, deposits between valuation boundaries, or unavailable
    source clocks are grounds to ABSTAIN by raising EvidenceRefused.
    """
    if not isinstance(payload, dict) or payload.get("contract") != CONTRACT:
        raise EvidenceRefused("WRONG_CONTRACT")
    evidence = payload.get("evidence_class")
    if evidence not in ALLOWED_EVIDENCE:
        raise EvidenceRefused("EVIDENCE_CLASS_NOT_ADMITTED")
    if payload.get("fee_treatment") != "NET_INTERNALISED":
        raise EvidenceRefused("FEE_TREATMENT_UNVERIFIED")
    as_of = _utc(payload.get("as_of_utc"), "as_of_utc")
    start = _utc(payload.get("start_at_utc"), "start_at_utc")
    first_known = _utc(payload.get("start_first_known_at_utc"), "start_first_known_at_utc")
    if not start <= first_known <= as_of:
        raise EvidenceRefused("START_NOT_FIRST_KNOWN_AT_DECISION")
    initial = _amount(payload.get("start_equity_after_flow_usd"), "start_equity_after_flow_usd")
    if initial <= 0:
        raise EvidenceRefused("START_NONPOSITIVE_EQUITY")
    points = payload.get("points")
    if not isinstance(points, list) or not points:
        raise EvidenceRefused("NO_ORIGINAL_CHECKPOINTS")
    if len(points) > 5000:
        raise EvidenceRefused("UNBOUNDED_CHECKPOINTS")

    if first_known > _utc(points[0].get("event_at_utc") if isinstance(points[0], dict) else None, "points[0].event_at_utc"):
        raise EvidenceRefused("START_BASELINE_NOT_KNOWN_BEFORE_FIRST_EVENT")

    previous_equity = initial
    previous_event = start
    naive_peak = initial
    max_naive_dd = Decimal(0)
    index = Decimal(1)
    index_peak = Decimal(1)
    max_twr_dd = Decimal(0)
    flow_total = Decimal(0)
    for i, record in enumerate(points):
        event, pre, flow, post = _point(record, after=previous_event, as_of=as_of, idx=i)
        if previous_equity <= 0:
            raise EvidenceRefused(f"points[{i}]:ZERO_EQUITY_EPOCH_UNRESOLVED")
        index *= pre / previous_equity
        if index == 0 and i < len(points) - 1:
            raise EvidenceRefused(f"points[{i}]:BANKRUPTCY_EPOCH_REQUIRES_NEW_LEDGER")
        index_peak = max(index_peak, index)
        max_twr_dd = max(max_twr_dd, Decimal(1) - index / index_peak)
        naive_peak = max(naive_peak, post)
        max_naive_dd = max(max_naive_dd, Decimal(1) - post / naive_peak)
        flow_total += flow
        previous_equity = post
        previous_event = event
    return {
        "contract": "RESEARCH_VAULT_FLOW_INTEGRITY_RESULT_V1",
        "authority": "RESEARCH_ONLY",
        "evidence_class": evidence,
        "observations": len(points),
        "as_of_utc": payload["as_of_utc"],
        "naive_equity_return_pct": str((previous_equity / initial - 1) * 100),
        "flow_neutral_twr_pct": str((index - 1) * 100),
        "naive_account_drawdown_pct": str(max_naive_dd * 100),
        "flow_neutral_drawdown_pct": str(max_twr_dd * 100),
        "net_external_flow_usd": str(flow_total),
        "eligible_to_rank_vaults": False,
        "prospective_skill_supported": False,
        "tradable_alpha_supported": False,
        "method_limit": "Witnessed boundary flows only; no share ledger, investor fee, fill or source custody proof",
    }
