from __future__ import annotations

import copy
import math
from typing import Any

from scripts.api_agent.meme_alpha_prospective import stable_hash, validate_shadow_feature

REPLAY_CONTRACT = "JEV_ALPHA_LAB_BLIND_REPLAY_V1"
OBSERVATION_CONTRACT = "MEME_ALPHA_G2_G3_SHADOW_OBSERVATION_v1"
FORBIDDEN_OUTCOME_KEYS = {
    "outcome","outcome_class","outcome_matured","mfe_after_discovery","mae_after_discovery",
    "realizable_return_after_slippage","exit_feasibility","falsifier_result","missed_winner_audit",
    "future_price","future_market_cap","ath",
}
ALLOWED_COUNTERFACTUAL_ACTIONS = {"RETAIN", "DEEP_DIVE", "FRONTIER_REVIEW"}

def _contains_forbidden_key(value: Any) -> bool:
    if isinstance(value, dict):
        return any(str(k).lower() in FORBIDDEN_OUTCOME_KEYS or _contains_forbidden_key(v) for k,v in value.items())
    if isinstance(value, list):
        return any(_contains_forbidden_key(v) for v in value)
    return False

def _verified_unsigned_observation(observation: dict[str, Any]) -> dict[str, Any]:
    if observation.get("contract") != OBSERVATION_CONTRACT:
        raise ValueError("UNSUPPORTED_OBSERVATION_CONTRACT")
    if not observation.get("observation_sha256"):
        raise ValueError("OBSERVATION_SHA256_REQUIRED")
    unsigned = copy.deepcopy(observation)
    supplied = str(unsigned.pop("observation_sha256"))
    if stable_hash(unsigned) != supplied:
        raise ValueError("OBSERVATION_SHA256_MISMATCH")
    return unsigned

def build_blind_state(observation: dict[str, Any]) -> dict[str, Any]:
    """Verify frozen input, then reject outcome leakage before constructing research-only state."""
    if _contains_forbidden_key(observation):
        raise ValueError("OUTCOME_LEAKAGE_DETECTED")
    unsigned = _verified_unsigned_observation(observation)
    cutoff = str(observation.get("cutoff_utc", ""))
    if not cutoff:
        raise ValueError("CUTOFF_REQUIRED")
    features = copy.deepcopy(list(observation.get("features", [])))
    for feature in features:
        errors = validate_shadow_feature(feature, cutoff)
        if errors:
            raise ValueError("INVALID_POINT_IN_TIME_FEATURE:" + ",".join(sorted(errors)))
    state = {
        "replay_contract": REPLAY_CONTRACT,
        "source_observation_sha256": str(observation["observation_sha256"]),
        "identity": copy.deepcopy(observation.get("identity", {})),
        "cutoff_minutes": observation.get("cutoff_minutes"),
        "cutoff_utc": cutoff,
        "collector_status": observation.get("collector_status"),
        "data_state": observation.get("data_state"),
        "features": features,
        "wallet_roles": copy.deepcopy(observation.get("wallet_roles", [])),
    }
    state["blind_state_sha256"] = stable_hash(state)
    return state

def freeze_challenger_prediction(*, blind_state: dict[str, Any], challenger: str,
    question_contract_version: str, predictions: dict[str, Any], model_version: str | None = None) -> dict[str, Any]:
    if _contains_forbidden_key(predictions):
        raise ValueError("PREDICTION_CONTAINS_OUTCOME_FIELD")
    if not blind_state.get("blind_state_sha256"):
        raise ValueError("BLIND_STATE_SHA256_REQUIRED")
    if not challenger:
        raise ValueError("CHALLENGER_REQUIRED")
    if not question_contract_version:
        raise ValueError("QUESTION_CONTRACT_VERSION_REQUIRED")
    if "route" in predictions:
        validate_counterfactual_route(str(predictions["route"]))
    record = {
        "contract":"JEV_ALPHA_LAB_CHALLENGER_PREDICTION_V1","replay_contract":REPLAY_CONTRACT,
        "blind_state_sha256":str(blind_state["blind_state_sha256"]),
        "source_observation_sha256":str(blind_state["source_observation_sha256"]),
        "challenger":str(challenger),"question_contract_version":str(question_contract_version),
        "model_version":model_version,"predictions":copy.deepcopy(predictions),
        "authority":{"production_routing":False,"portfolio_action":False,"automatic_trading":False,"canonical_promotion":False},
    }
    record["prediction_sha256"] = stable_hash(record)
    return record

def counterfactual_route(judgments: dict[str, Any]) -> str:
    """Shadow-only preregistered composition. Noul values are probabilities, not confidence."""
    names=("evidence_conflict","deep_dive_value","frontier_review_need","material_evidence","preserve_verbatim")
    values={}
    for name in names:
        value=float(judgments.get(name,0.5))
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError("INVALID_JUDGMENT_PROBABILITY:"+name)
        values[name]=value
    if values["frontier_review_need"] >= .80 or values["evidence_conflict"] >= .80:
        return "FRONTIER_REVIEW"
    if values["deep_dive_value"] >= .70 or values["material_evidence"] >= .70:
        return "DEEP_DIVE"
    return "RETAIN"

def validate_counterfactual_route(route: str) -> None:
    if route not in ALLOWED_COUNTERFACTUAL_ACTIONS:
        raise ValueError("FORBIDDEN_REPLAY_ROUTE")
