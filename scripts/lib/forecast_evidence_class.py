from __future__ import annotations

from typing import Any, Iterable

OWNER_RATIFIED = "API_AGENT_OWNER_RATIFIED_PROSPECTIVE_v1"
AUTOMATED_EXPERIMENT = "AUTOMATED_SCIENTIFIC_EXPERIMENT_SHADOW_v1"
LEGACY_UNCLASSIFIED = "LEGACY_OR_UNCLASSIFIED_FORECAST"

OWNER_RATIFICATION_CONTRACT = "FORECAST_RATIFICATION_PACKET_v2"
EXPERIMENT_ADMISSION_CONTRACT = "EXPERIMENT_SCIENTIFIC_ADMISSION_v1"
EXPERIMENT_ADMISSION_STATUS = "QUALIFIED_FOR_FORWARD_TEST"


class EvidenceClassError(ValueError):
    pass


def _owner_signal(record: dict[str, Any]) -> bool:
    return (
        record.get("contract") == "FROZEN_FORECAST_v1"
        and record.get("ratification_contract") == OWNER_RATIFICATION_CONTRACT
        and record.get("ratification_outcome_blind") is True
        and bool(record.get("candidate_id"))
    )


def _experiment_signal(record: dict[str, Any]) -> bool:
    admission = record.get("scientific_admission")
    return (
        record.get("contract") == "FROZEN_FORECAST_v1"
        and record.get("experimental_only") is True
        and bool(record.get("source_candidate_id"))
        and isinstance(admission, dict)
        and admission.get("contract") == EXPERIMENT_ADMISSION_CONTRACT
        and admission.get("status") == EXPERIMENT_ADMISSION_STATUS
    )


def classify_forecast_evidence(record: dict[str, Any]) -> str:
    """Classify a frozen forecast without granting scientific skill authority.

    The two prospective evidence classes are deliberately mutually exclusive:
    API-agent forecasts are owner-ratified and outcome-blind, while automated
    experiment forecasts are scientifically admitted but remain shadow-only.
    Historical/legacy records without either complete provenance pattern stay
    explicitly unclassified and are not eligible for cross-record pooling by
    this contract.
    """
    if record.get("contract") != "FROZEN_FORECAST_v1":
        raise EvidenceClassError("NOT_FROZEN_FORECAST_V1")
    owner = _owner_signal(record)
    experiment = _experiment_signal(record)
    if owner and experiment:
        raise EvidenceClassError("FORECAST_EVIDENCE_CLASS_CONFLICT_OWNER_AND_EXPERIMENT")
    if owner:
        return OWNER_RATIFIED
    if experiment:
        return AUTOMATED_EXPERIMENT
    return LEGACY_UNCLASSIFIED


def scientific_pool_compatibility_key(record: dict[str, Any]) -> str | None:
    """Return a class key only for explicit prospective evidence classes.

    A non-null key means only that records share an evidence-governance class.
    It does not establish settlement eligibility, independence, calibration,
    effective N, or forecasting skill.
    """
    evidence_class = classify_forecast_evidence(record)
    if evidence_class in {OWNER_RATIFIED, AUTOMATED_EXPERIMENT}:
        return evidence_class
    return None


def assert_same_evidence_class(records: Iterable[dict[str, Any]]) -> str:
    keys = [scientific_pool_compatibility_key(record) for record in records]
    if not keys:
        raise EvidenceClassError("NO_FORECASTS_TO_CLASSIFY")
    if any(key is None for key in keys):
        raise EvidenceClassError("LEGACY_OR_UNCLASSIFIED_FORECAST_CANNOT_BE_POOLED")
    unique = set(keys)
    if len(unique) != 1:
        raise EvidenceClassError("CROSS_EVIDENCE_CLASS_POOLING_FORBIDDEN")
    return next(iter(unique))


def evidence_class_authority(evidence_class: str) -> dict[str, Any]:
    if evidence_class == OWNER_RATIFIED:
        return {
            "owner_ratification_required": True,
            "automated_scientific_admission": False,
            "shadow_or_research_only": True,
            "cross_evidence_class_pooling": False,
            "forecast_skill_authority": False,
            "portfolio_action": False,
        }
    if evidence_class == AUTOMATED_EXPERIMENT:
        return {
            "owner_ratification_required": False,
            "automated_scientific_admission": True,
            "shadow_or_research_only": True,
            "cross_evidence_class_pooling": False,
            "forecast_skill_authority": False,
            "portfolio_action": False,
        }
    return {
        "owner_ratification_required": None,
        "automated_scientific_admission": None,
        "shadow_or_research_only": True,
        "cross_evidence_class_pooling": False,
        "forecast_skill_authority": False,
        "portfolio_action": False,
    }
