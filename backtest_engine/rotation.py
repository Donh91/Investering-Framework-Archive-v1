from __future__ import annotations

from dataclasses import dataclass


AUTHORITY_STATUSES = {
    "DIRECT_OWNER",
    "DIRECT_CHALLENGER_APPROVED",
    "DIRECT_CANDIDATE_UNVALIDATED",
    "DERIVED_DIAGNOSTIC",
    "UNAVAILABLE",
}


@dataclass(frozen=True)
class RotationEvidence:
    direct_ethbtc_available: bool
    ethbtc_authority_status: str
    ethbtc_settled_close: float | None
    ethbtc_positive_settled_run: int
    eth_leads_btc_sessions: int
    large_cap_breadth: float | None
    broad_alt_breadth: float | None
    beta_neutral_alt_return_20d: float | None
    btc_dominance_change_5d: float | None
    flow_confirmation: bool | None
    source_qa_pass: bool

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.ethbtc_authority_status not in AUTHORITY_STATUSES:
            errors.append("unsupported ETH/BTC authority status")
        if self.direct_ethbtc_available and self.ethbtc_settled_close is None:
            errors.append("direct availability requires a settled close")
        if self.ethbtc_positive_settled_run < 0 or self.eth_leads_btc_sessions < 0:
            errors.append("run counts cannot be negative")
        for name, value in {
            "large_cap_breadth": self.large_cap_breadth,
            "broad_alt_breadth": self.broad_alt_breadth,
        }.items():
            if value is not None and not 0.0 <= value <= 1.0:
                errors.append(f"{name} must be between 0 and 1")
        return errors


def classify_rotation(evidence: RotationEvidence) -> dict[str, object]:
    errors = evidence.validate()
    if errors:
        return {"status": "INVALID_EVIDENCE", "errors": errors}

    direct_authority = evidence.ethbtc_authority_status in {
        "DIRECT_OWNER", "DIRECT_CHALLENGER_APPROVED"
    }
    can_score_direct_gate = (
        evidence.source_qa_pass
        and evidence.direct_ethbtc_available
        and direct_authority
        and evidence.ethbtc_settled_close is not None
    )
    eth_candidate = (
        can_score_direct_gate
        and evidence.ethbtc_positive_settled_run >= 3
        and evidence.eth_leads_btc_sessions >= 2
        and evidence.ethbtc_settled_close >= 0.0275
    )
    eth_confirmed = (
        eth_candidate
        and evidence.ethbtc_settled_close > 0.03
        and evidence.ethbtc_positive_settled_run >= 4
    )
    large_candidate = (
        eth_confirmed
        and evidence.large_cap_breadth is not None
        and evidence.large_cap_breadth >= 0.50
    )
    large_confirmed = (
        large_candidate
        and evidence.btc_dominance_change_5d is not None
        and evidence.btc_dominance_change_5d <= 0.0
        and evidence.flow_confirmation is True
    )
    broad_candidate = (
        large_confirmed
        and evidence.broad_alt_breadth is not None
        and evidence.broad_alt_breadth >= 0.55
    )
    broad_confirmed = (
        broad_candidate
        and evidence.beta_neutral_alt_return_20d is not None
        and evidence.beta_neutral_alt_return_20d > 0.0
    )

    if broad_confirmed:
        label = "BROAD_ALT_ROTATION_CONFIRMED"
    elif broad_candidate:
        label = "BROAD_ALT_ROTATION_CANDIDATE"
    elif large_confirmed:
        label = "SELECTIVE_LARGE_CAP_ROTATION_CONFIRMED"
    elif large_candidate:
        label = "SELECTIVE_LARGE_CAP_ROTATION_CANDIDATE"
    elif eth_confirmed:
        label = "ETH_RELATIVE_STRENGTH_CONFIRMED"
    elif eth_candidate:
        label = "ETH_RELATIVE_STRENGTH_CANDIDATE"
    else:
        label = "NO_SIGNAL"

    return {
        "status": "PASS",
        "label": label,
        "can_score_direct_gate": can_score_direct_gate,
        "eth_relative_strength_candidate": eth_candidate,
        "eth_relative_strength_confirmed": eth_confirmed,
        "selective_large_cap_candidate": large_candidate,
        "selective_large_cap_confirmed": large_confirmed,
        "broad_alt_candidate": broad_candidate,
        "broad_alt_confirmed": broad_confirmed,
        "canonical_rotation_permission": broad_confirmed,
    }
