from __future__ import annotations

import argparse
from datetime import datetime, timezone
from typing import Any

from research_governance_common import ROOT, GOV, digest, load_json, persist_json

BASE = GOV / "compounding_learning_v1"
POLICY, STATE = BASE / "POLICY.json", BASE / "STATE.json"
NEXT, BACKLOG, EVENTS = BASE / "NEXT_BEST_EXPERIMENT.json", BASE / "LEARNING_BACKLOG.json", BASE / "events"
EVENT_ROOT = EVENTS
EXP = ROOT / "research/experiment_lifecycle"
REGISTRY = EXP / "LATEST_EXPERIMENT_REGISTRY.json"
ADMISSION = EXP / "LATEST_SCIENTIFIC_ADMISSION_REGISTRY.json"
ADJUDICATION = EXP / "weekly_adjudication/LATEST.json"
T13_ACTIVATION = ROOT / "research/api_agent/forecast_skill/COHORT_ACTIVATION_v1.json"
T13_STATUS = ROOT / "research/api_agent/forecast_skill/LATEST_STUDY_STATUS.json"

DESCRIPTIVE_CHECKPOINT_DAYS = [7, 14, 30, 60, 90, 120, 180, 240]
PROFILE_DEFAULTS = {
    "FAST": {"day_checkpoints": DESCRIPTIVE_CHECKPOINT_DAYS, "matured_checkpoints": [5, 10, 20]},
    "STANDARD": {"day_checkpoints": DESCRIPTIVE_CHECKPOINT_DAYS, "matured_checkpoints": [5, 10, 20, 40]},
    "LONG": {"day_checkpoints": DESCRIPTIVE_CHECKPOINT_DAYS, "matured_checkpoints": [10, 25, 50, 100]},
    "CONFIRMATORY": {"day_checkpoints": DESCRIPTIVE_CHECKPOINT_DAYS, "matured_checkpoints": []},
}
ESCALATIONS = {"RUN_INCREMENTAL_VALUE_AND_ADVERSARIAL_REVIEW", "RUN_FAILURE_AND_RETIREMENT_REVIEW"}
PRIORITY = {
    "CONTESTED": 0, "SUPPORTED_NEEDS_INCREMENTAL_VALUE": 1,
    "NEGATIVE_EVIDENCE_NEEDS_FAILURE_REVIEW": 2, "INCONCLUSIVE_KEEP_FROZEN": 3,
    "WAIT_FOR_MORE_PROSPECTIVE_EVIDENCE": 4, "ARCHIVE_DUPLICATE": 5,
    "WAIT_FOR_MAPPING": 6, "KEEP_QUARANTINED": 7,
    "WAIT_FOR_REFRESHED_UNIFIED_ADJUDICATION": 8,
}


def _dt(value: Any):
    if not value:
        return None
    try:
        text = str(value).replace("Z", "+00:00")
        out = datetime.fromisoformat(text)
        return out.astimezone(timezone.utc) if out.tzinfo else None
    except ValueError:
        return None


def _now(value=None):
    if value:
        out = _dt(value)
        if not out:
            raise ValueError("invalid --as-of-utc timestamp")
        return out
    return datetime.now(timezone.utc)


def _maps(admission, adjudication):
    amap = {str(r.get("candidate_id")): r for r in admission.get("candidates", []) if isinstance(r, dict) and r.get("candidate_id")}
    jmap = {str(r.get("candidate_id")): r for r in adjudication.get("candidate_actions", []) if isinstance(r, dict) and r.get("candidate_id")}
    return amap, jmap


def _profile(candidate, policy):
    profiles = policy.get("profiles") or PROFILE_DEFAULTS
    explicit = str(candidate.get("learning_profile") or "").upper()
    if explicit in profiles:
        return explicit
    title, kind, test_id = (str(candidate.get(k) or "").upper() for k in ("title", "kind", "test_id"))
    if "CONFIRMATORY" in title or test_id.startswith("FORECAST_SKILL_CONFIRMATORY"):
        return "CONFIRMATORY"
    if "INTRADAY" in title or "INTRADAY" in kind:
        return "FAST"
    if kind in {"FORECAST_TEST", "SENSOR_COMBINATION", "SEQUENCE_TEST"}:
        return "STANDARD"
    return str(policy.get("default_profile") or "STANDARD").upper()


def _age(candidate, admission_row, as_of):
    if admission_row.get("historical_candidate_requalification"):
        start = _dt(candidate.get("forward_test_started_at_utc"))
        if not start:
            return None, "DISABLED_HISTORICAL_REQUALIFICATION_WITHOUT_FORWARD_START"
        basis = "FORWARD_TEST_STARTED_AT_UTC"
    else:
        raw = candidate.get("forward_test_started_at_utc") or candidate.get("created_at_utc")
        start = _dt(raw)
        basis = "FORWARD_TEST_STARTED_AT_UTC" if candidate.get("forward_test_started_at_utc") else "CANDIDATE_CREATED_AT_UTC_OPERATIONAL_ONLY"
    if not start or start > as_of:
        return None, "UNAVAILABLE"
    return int((as_of - start).total_seconds() // 86400), basis


def _current(candidate, admission_row, row):
    if not row:
        return False, "MISSING_CANDIDATE_ADJUDICATION"
    if str(row.get("lifecycle_state") or "") != str(candidate.get("state") or ""):
        return False, "LIFECYCLE_STATE_DRIFT"
    if int(row.get("matured_outcome_count") or 0) != int(candidate.get("matured_outcome_count") or 0):
        return False, "MATURED_COUNT_DRIFT"
    current_admission = str(admission_row.get("status") or candidate.get("scientific_admission_status") or "")
    row_admission = str(row.get("scientific_admission_status") or "")
    if current_admission and row_admission and current_admission != row_admission:
        return False, "SCIENTIFIC_ADMISSION_DRIFT"
    if row.get("canonical_effect") is not False or row.get("portfolio_execution") is not False:
        return False, "ADJUDICATION_AUTHORITY_BREACH"
    return True, "CURRENT"


def _learning(row, current):
    if not current or not row:
        return (
            "WAIT_FOR_REFRESHED_UNIFIED_ADJUDICATION", "CONTINUE_OBSERVING",
            "Unified Adjudication must refresh before evidence can be interpreted", False, "NONE",
        )
    action, reason = str(row.get("selected_action") or ""), str(row.get("reason") or "")
    if action == "RUN_INCREMENTAL_VALUE_AND_ADVERSARIAL_REVIEW":
        return (
            "SUPPORTED_NEEDS_INCREMENTAL_VALUE", "RUN_INCREMENTAL_VALUE_TEST",
            "supportive evidence requires independent incremental-value and adversarial review", True,
            "DOES_THE_FAMILY_ADD_INCREMENTAL_PROSPECTIVE_VALUE_BEYOND_FROZEN_BASELINE_AND_CONTROLS",
        )
    if action == "RUN_FAILURE_AND_RETIREMENT_REVIEW":
        return (
            "NEGATIVE_EVIDENCE_NEEDS_FAILURE_REVIEW", "STRESS_TEST_REGIME_SPECIFICITY",
            "negative evidence requires bounded failure review without rewriting the parent", True,
            "IS_FAILURE_GENERAL_OR_REGIME_SPECIFIC_UNDER_A_NEW_PREREGISTERED_CHILD",
        )
    mapped = {
        "KEEP_SHADOW_INCONCLUSIVE": ("INCONCLUSIVE_KEEP_FROZEN", reason or "mature evidence remains inconclusive"),
        "ARCHIVE_ONLY_DUPLICATE": ("ARCHIVE_DUPLICATE", reason or "semantic duplicate"),
        "WAIT_FOR_MAPPING": ("WAIT_FOR_MAPPING", reason or "machine mapping missing"),
        "KEEP_QUARANTINED": ("KEEP_QUARANTINED", reason or "scientific admission blocked forward execution"),
    }
    state, why = mapped.get(action, ("WAIT_FOR_MORE_PROSPECTIVE_EVIDENCE", reason or "insufficient mature evidence"))
    return state, "CONTINUE_OBSERVING", why, False, "NONE"


def evaluate_candidates(registry, admission, adjudication, policy, previous_state, as_of):
    amap, jmap = _maps(admission, adjudication)
    prior = set(previous_state.get("emitted_event_keys") or [])
    packets = []
    for candidate in registry.get("candidates", []):
        if not isinstance(candidate, dict) or not candidate.get("candidate_id"):
            continue
        cid = str(candidate["candidate_id"])
        admission_row = amap.get(cid, {})
        profile = _profile(candidate, policy)
        cfg = (policy.get("profiles") or PROFILE_DEFAULTS).get(profile, PROFILE_DEFAULTS["STANDARD"])
        age, basis = _age(candidate, admission_row, as_of)
        matured = int(candidate.get("matured_outcome_count") or 0)
        keys = []
        for day in cfg.get("day_checkpoints", []):
            key = f"{cid}:CHECKPOINT:DAY:{int(day)}"
            if age is not None and age >= int(day) and key not in prior:
                keys.append(key)
        for count in cfg.get("matured_checkpoints", []):
            key = f"{cid}:CHECKPOINT:MATURED:{int(count)}"
            if matured >= int(count) and key not in prior:
                keys.append(key)
        row = jmap.get(cid)
        current, freshness = _current(candidate, admission_row, row)
        if current and str(row.get("selected_action") or "") in ESCALATIONS:
            key = f"{cid}:ADJUDICATION:{row['selected_action']}:{matured}"
            if key not in prior:
                keys.append(key)
        if not keys:
            continue
        state, action, why, eligible, question = _learning(row, current)
        packets.append({
            "contract": "COMPOUNDING_LEARNING_CHECKPOINT_PACKET_v1",
            "candidate_id": cid,
            "parent_candidate_id": cid,
            "title": str(candidate.get("title") or ""),
            "kind": str(candidate.get("kind") or ""),
            "learning_profile": profile,
            "candidate_state": str(candidate.get("state") or ""),
            "scientific_admission_status": str(admission_row.get("status") or candidate.get("scientific_admission_status") or ""),
            "historical_candidate_requalification": bool(admission_row.get("historical_candidate_requalification")),
            "age_days": age,
            "age_basis": basis,
            "observation_count": int(candidate.get("observation_count") or 0),
            "matured_outcome_count": matured,
            "semantic_fingerprint": str(admission_row.get("semantic_fingerprint") or candidate.get("semantic_fingerprint") or ""),
            "trigger_event_keys": sorted(keys),
            "descriptive_checkpoint_days_reached_this_run": sorted(int(k.rsplit(":", 1)[-1]) for k in keys if ":CHECKPOINT:DAY:" in k),
            "checkpoint_semantics": "DESCRIPTIVE_OPERATIONAL_LEARNING_ONLY_NO_CONFIRMATORY_PEEKING",
            "unified_adjudication_action": row.get("selected_action") if current and row else None,
            "unified_adjudication_reason": row.get("reason") if current and row else None,
            "adjudication_freshness": freshness,
            "learning_state": state,
            "recommended_action": action,
            "reason": why,
            "proposal_eligible": eligible,
            "next_falsifiable_question": question,
            "scientific_interpretation_owner": "UNIFIED_EXPERIMENTAL_LIFECYCLE_ADJUDICATION_v1",
            "controller_role": "NEXT_LEARNING_STRATEGY_ONLY",
            "frozen_parent_preserved": True,
            "retrospective_rescore_allowed": False,
            "canonical_effect": False,
            "portfolio_execution": False,
            "automatic_promotion": False,
            "automatic_threshold_change": False,
            "automatic_weight_change": False,
        })
    packets.sort(key=lambda x: (
        0 if x["proposal_eligible"] else 1,
        PRIORITY.get(x["learning_state"], 99),
        -x["matured_outcome_count"], -x["observation_count"], x["candidate_id"],
    ))
    selected = packets[: int(policy.get("max_checkpoint_candidates_per_run", 25))]
    return selected, sorted({key for packet in selected for key in packet["trigger_event_keys"]})


def build_hypothesis_families(registry, admission, adjudication):
    amap, jmap = _maps(admission, adjudication)
    groups = {}
    for candidate in registry.get("candidates", []):
        if not isinstance(candidate, dict) or not candidate.get("candidate_id"):
            continue
        admission_row = amap.get(str(candidate["candidate_id"]), {})
        family_key = str(admission_row.get("semantic_fingerprint") or candidate.get("semantic_fingerprint") or candidate["candidate_id"])
        groups.setdefault(family_key, []).append((candidate, admission_row, jmap.get(str(candidate["candidate_id"]))))

    families = []
    for family_key, members in groups.items():
        support, negative, inconclusive, duplicate = [], [], [], []
        stale, quarantine, mapping, signatures = [], [], [], []
        titles, kinds, profiles, regimes = set(), set(), set(), set()
        matured_total = observation_total = 0
        max_observations = 0
        for candidate, admission_row, row in members:
            cid = str(candidate["candidate_id"])
            titles.add(str(candidate.get("title") or ""))
            kinds.add(str(candidate.get("kind") or ""))
            profiles.add(_profile(candidate, {"profiles": PROFILE_DEFAULTS, "default_profile": "STANDARD"}))
            if candidate.get("regime_dependency"):
                regimes.add(str(candidate["regime_dependency"]))
            matured = int(candidate.get("matured_outcome_count") or 0)
            observations = int(candidate.get("observation_count") or 0)
            matured_total += matured
            observation_total += observations
            max_observations = max(max_observations, observations)
            current, _ = _current(candidate, admission_row, row)
            if not current or not row:
                stale.append(cid)
                continue
            action = str(row.get("selected_action") or "")
            if action == "RUN_INCREMENTAL_VALUE_AND_ADVERSARIAL_REVIEW":
                support.append(cid)
            elif action == "RUN_FAILURE_AND_RETIREMENT_REVIEW":
                negative.append(cid)
            elif action == "KEEP_SHADOW_INCONCLUSIVE":
                inconclusive.append(cid)
            elif action == "ARCHIVE_ONLY_DUPLICATE":
                duplicate.append(cid)
            elif action == "KEEP_QUARANTINED":
                quarantine.append(cid)
            elif action == "WAIT_FOR_MAPPING":
                mapping.append(cid)
            if action in ESCALATIONS or action == "KEEP_SHADOW_INCONCLUSIVE":
                signatures.append({
                    "candidate_id": cid,
                    "selected_action": action,
                    "lifecycle_state": candidate.get("state"),
                    "matured_outcome_count": matured,
                })

        if support and negative:
            status = "CONTESTED"
        elif support:
            status = "SUPPORTED_NEEDS_INCREMENTAL_VALUE"
        elif negative:
            status = "NEGATIVE_EVIDENCE_NEEDS_FAILURE_REVIEW"
        elif inconclusive:
            status = "INCONCLUSIVE_KEEP_FROZEN"
        elif stale:
            status = "WAIT_FOR_REFRESHED_UNIFIED_ADJUDICATION"
        elif quarantine:
            status = "KEEP_QUARANTINED"
        elif mapping:
            status = "WAIT_FOR_MAPPING"
        elif duplicate and len(duplicate) == len(members):
            status = "ARCHIVE_DUPLICATE"
        else:
            status = "WAIT_FOR_MORE_PROSPECTIVE_EVIDENCE"

        uncertainty = {
            "CONTESTED": "COMPETING_PROSPECTIVE_EXPLANATIONS_REMAIN_UNRESOLVED",
            "SUPPORTED_NEEDS_INCREMENTAL_VALUE": "INCREMENTAL_VALUE_INDEPENDENCE_AND_REPLICATION_REMAIN_UNRESOLVED",
            "NEGATIVE_EVIDENCE_NEEDS_FAILURE_REVIEW": "GENERAL_FAILURE_VERSUS_REGIME_SPECIFICITY_REMAINS_UNRESOLVED",
            "INCONCLUSIVE_KEEP_FROZEN": "MORE_MATURE_PROSPECTIVE_EVIDENCE_REQUIRED_UNDER_FROZEN_METHOD",
        }.get(status, "MATURE_PROSPECTIVE_EVIDENCE_NOT_YET_SUFFICIENT")
        material = bool(signatures)
        redundant = bool(duplicate or len(members) > 1)
        complexity = "MODERATE" if "SENSOR_COMBINATION" in kinds or len(kinds) > 1 else "LOW"
        family = {
            "contract": "LEARNING_STATE_FAMILY_v1",
            "semantic_identity": family_key,
            "candidate_ids": sorted(str(member[0]["candidate_id"]) for member in members),
            "titles": sorted(x for x in titles if x),
            "kinds": sorted(x for x in kinds if x),
            "learning_profiles": sorted(profiles),
            "current_evidence_status": status,
            "supporting_evidence_refs": sorted(support),
            "contradicting_evidence_refs": sorted(negative),
            "inconclusive_evidence_refs": sorted(inconclusive),
            "stale_adjudication_refs": sorted(stale),
            "unresolved_uncertainty": uncertainty,
            "known_regime_dependence": sorted(regimes) or ["UNSPECIFIED"],
            "redundancy_collinearity_warning": redundant,
            "complexity_burden": complexity,
            "confidence_class": "LOW" if status in {"CONTESTED", "INCONCLUSIVE_KEEP_FROZEN", "WAIT_FOR_REFRESHED_UNIFIED_ADJUDICATION"} else "LOW_TO_MODERATE" if material else "LOW",
            "matured_outcome_count_total": matured_total,
            "observation_count_total": observation_total,
            "max_candidate_observation_count": max_observations,
            "material_evidence": material,
            "material_evidence_signature": sorted(signatures, key=lambda row: (row["candidate_id"], row["selected_action"])),
            "canonical_effect": False,
        }
        family["material_evidence_fingerprint"] = digest({
            "semantic_identity": family_key,
            "status": status,
            "signature": family["material_evidence_signature"],
        }) if material else None
        family["evidence_fingerprint"] = digest({key: value for key, value in family.items() if key != "evidence_fingerprint"})
        families.append(family)
    return sorted(families, key=lambda x: (PRIORITY.get(x["current_evidence_status"], 99), x["semantic_identity"]))


def derive_learning_delta(previous_state, families):
    prior = {str(row.get("semantic_identity")): row for row in previous_state.get("hypothesis_families", []) if isinstance(row, dict) and row.get("semantic_identity")}
    changed = []
    for family in families:
        if not family["material_evidence"]:
            continue
        old = prior.get(family["semantic_identity"])
        if not old or old.get("material_evidence_fingerprint") != family.get("material_evidence_fingerprint"):
            changed.append({
                "semantic_identity": family["semantic_identity"],
                "previous_status": old.get("current_evidence_status") if old else None,
                "new_status": family["current_evidence_status"],
                "previous_evidence_fingerprint": old.get("material_evidence_fingerprint") if old else None,
                "new_evidence_fingerprint": family["material_evidence_fingerprint"],
            })
    return {"contract": "LEARNING_DELTA_v1", "material_change": bool(changed), "changed_family_count": len(changed), "changed_families": changed}


def _score(family):
    status = family["current_evidence_status"]
    uncertainty = {"CONTESTED": 1.0, "NEGATIVE_EVIDENCE_NEEDS_FAILURE_REVIEW": 0.95, "SUPPORTED_NEEDS_INCREMENTAL_VALUE": 0.9}.get(status, 0.5)
    decision = 1.0 if set(family.get("kinds") or []) & {"FORECAST_TEST", "SEQUENCE_TEST", "SENSOR_COMBINATION"} else 0.6
    observability = min(1.0, max(0.25, float(family.get("max_candidate_observation_count") or 0) / 20.0))
    independence = 0.45 if family.get("redundancy_collinearity_warning") else 1.0
    regime = 0.65 if family.get("known_regime_dependence") == ["UNSPECIFIED"] else 1.0
    profiles = set(family.get("learning_profiles") or [])
    time_to_learning = 1.0 if "FAST" in profiles else 0.8 if "STANDARD" in profiles else 0.55 if "LONG" in profiles else 0.45
    adversarial = 1.0 if status in {"CONTESTED", "SUPPORTED_NEEDS_INCREMENTAL_VALUE"} else 0.85
    complexity = 0.25 if family.get("complexity_burden") == "MODERATE" else 0.10
    value = round(max(0, min(100,
        25 * uncertainty + 15 * decision + 15 + 10 * observability + 10 * independence +
        10 * regime + 10 * time_to_learning + 5 * adversarial - 10 * complexity
    )), 2)
    return {
        "score": value,
        "score_interpretation": "TRANSPARENT_HEURISTIC_FOR_RANKING_NOT_AN_EMPIRICAL_PROBABILITY",
        "components": {
            "uncertainty_reduction": uncertainty,
            "decision_relevance": decision,
            "falsifiability_strength": 1.0,
            "observability_feasibility": round(observability, 4),
            "independence_from_tested_information": independence,
            "regime_coverage": regime,
            "time_to_learning": time_to_learning,
            "adversarial_disconfirmation_value": adversarial,
            "complexity_penalty": complexity,
        },
    }


def generate_candidate_tests(families):
    tests = []
    for family in families:
        status = family["current_evidence_status"]
        test_type = {
            "CONTESTED": "CONTRADICTION_DISCRIMINATION_TEST",
            "SUPPORTED_NEEDS_INCREMENTAL_VALUE": "INCREMENTAL_VALUE_AND_ADVERSARIAL_REPLICATION_TEST",
            "NEGATIVE_EVIDENCE_NEEDS_FAILURE_REVIEW": "REGIME_SPECIFICITY_FAILURE_STRESS_TEST",
        }.get(status)
        if not test_type:
            continue
        if test_type.startswith("INCREMENTAL"):
            hypothesis = "Supported family adds incremental prospective value beyond frozen baseline and controls in an independent forward sample."
            falsifier = "Child fails to add incremental value or reveals leakage, redundancy, or non-independent information."
            change_view = "Independent incremental value strengthens the family; failure or redundancy weakens it without rewriting the parent."
        elif test_type.startswith("REGIME"):
            hypothesis = "Negative parent result is regime-specific rather than a general absence of prospective value."
            falsifier = "Preregistered regime-conditioned child also fails, or regime split cannot be defined point-in-time without leakage."
            change_view = "Successful prospective regime discrimination narrows the failure domain; repeated failure supports broader retirement review."
        else:
            hypothesis = "Competing prospective evidence can be discriminated by one preregistered child test."
            falsifier = "Child remains inconclusive, cannot distinguish explanations, or needs post-outcome target/horizon/regime changes."
            change_view = "Discriminating prospective evidence resolves the contested state; another mixed result preserves uncertainty."
        parent = (family.get("supporting_evidence_refs") or family.get("contradicting_evidence_refs") or family.get("candidate_ids") or [None])[0]
        row = {
            "contract": "NEXT_BEST_TEST_CANDIDATE_v1",
            "test_type": test_type,
            "semantic_identity": family["semantic_identity"],
            "parent_candidate_id": parent,
            "problem_uncertainty": family["unresolved_uncertainty"],
            "hypothesis": hypothesis,
            "explicit_baseline": "FROZEN_PARENT_BASELINE_AND_CONTROLS",
            "explicit_falsifier": falsifier,
            "what_would_change_our_view": change_view,
            "expected_information_gain": _score(family),
            "expected_incremental_value": "UNPROVEN_TO_BE_MEASURED_PROSPECTIVELY",
            "required_data_lineage": [
                "EXPERIMENT_LIFECYCLE_REGISTRY_v1",
                "EXPERIMENT_SCIENTIFIC_ADMISSION_REGISTRY_v1",
                "UNIFIED_EXPERIMENTAL_LIFECYCLE_ADJUDICATION_v1",
                "NEW_CHILD_PROSPECTIVE_EVIDENCE_ONLY",
            ],
            "target_horizon_regime": {
                "target": parent,
                "horizon": "MUST_BE_FIXED_BY_NEW_SCIENTIFIC_ADMISSION",
                "regime": family["known_regime_dependence"],
            },
            "negative_controls": ["ALWAYS_WAIT_CONTROL", "STRONGEST_OR_SINGLE_COMPONENT_CONTROL", "DETERMINISTIC_PLACEBO_DIRECTION"],
            "redundancy_risk": "ELEVATED" if family["redundancy_collinearity_warning"] else "NORMAL",
            "complexity_tax": family["complexity_burden"],
            "false_positive_cost": "MUST_BE_FROZEN_BY_SCIENTIFIC_ADMISSION",
            "false_negative_cost": "MUST_BE_FROZEN_BY_SCIENTIFIC_ADMISSION",
            "revisit_condition": "AFTER_NEW_CHILD_HAS_MATURE_PROSPECTIVE_EVIDENCE_AND_UNIFIED_ADJUDICATION",
            "requires_scientific_admission": True,
            "automatic_execution": False,
            "canonical_effect": False,
            "portfolio_execution": False,
        }
        row["candidate_test_id"] = "NBT-" + digest({"semantic_identity": row["semantic_identity"], "test_type": test_type})[:20]
        tests.append(row)
    return sorted(tests, key=lambda x: (-float(x["expected_information_gain"]["score"]), x["candidate_test_id"]))


def select_bounded_next_best_test(tests, max_count=1):
    if not tests:
        return {
            "contract": "NEXT_BEST_EXPERIMENT_PROPOSAL_v1",
            "schema": "NEXT_BEST_TEST_PROPOSAL_v1",
            "authority": "RESEARCH_ONLY_NON_CANONICAL",
            "proposal_status": "NO_NEW_SCIENTIFICALLY_ELIGIBLE_CHILD_TEST",
            "source": "COMPOUNDING_LEARNING",
            "requires_scientific_admission": True,
            "automatic_execution": False,
            "canonical_effect": False,
            "portfolio_execution": False,
            "model_weight_change": False,
            "automatic_promotion": False,
        }, tests
    proposal = dict(tests[0])
    proposal.update({
        "contract": "NEXT_BEST_EXPERIMENT_PROPOSAL_v1",
        "schema": "NEXT_BEST_TEST_PROPOSAL_v1",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "proposal_status": "PROPOSAL_ONLY_ROUTE_THROUGH_EXISTING_RESEARCH_GOVERNANCE_AND_SCIENTIFIC_ADMISSION",
        "source": "COMPOUNDING_LEARNING",
        "proposed_priority": 1,
        "competing_tests_ranked_lower": [
            {"rank": index + 2, "candidate_test_id": row["candidate_test_id"], "score": row["expected_information_gain"]["score"], "reason_ranked_lower": "LOWER_TRANSPARENT_INFORMATION_VALUE_SCORE"}
            for index, row in enumerate(tests[1:6])
        ],
        "frozen_parent_preserved": True,
        "child_may_mutate_parent": False,
        "new_test_automatically_admitted": False,
        "retrospective_rescore_allowed": False,
        "automatic_parameter_search": False,
        "requires_scientific_admission": True,
        "automatic_execution": False,
        "canonical_effect": False,
        "portfolio_execution": False,
        "model_weight_change": False,
        "automatic_threshold_change": False,
        "automatic_market_rule_change": False,
        "automatic_promotion": False,
        "next_route": [
            "RESEARCH_MEMORY_NOVELTY", "DECISION_IMPACT_VOI", "INDEPENDENT_ADVERSARIAL_SENTINEL",
            "META_ORCHESTRATOR", "SCIENTIFIC_ADMISSION_OR_EXISTING_OWNER",
            "PROSPECTIVE_FREEZE_IF_AUTHORIZED", "EXPERIMENT_EXECUTION_PLANE",
        ],
    })
    return proposal, tests


def build_learning_backlog(previous, tests, proposal, as_of):
    entries = {str(row.get("backlog_id")): dict(row) for row in previous.get("entries", []) if isinstance(row, dict) and row.get("backlog_id")}
    current, selected = set(), str(proposal.get("candidate_test_id") or "")
    now = as_of.isoformat().replace("+00:00", "Z")
    for rank, test in enumerate(tests, 1):
        backlog_id = "LB-" + digest({"candidate_test_id": test["candidate_test_id"]})[:20]
        current.add(backlog_id)
        old = entries.get(backlog_id, {})
        status = "SELECTED_NEXT_BEST_TEST" if test["candidate_test_id"] == selected else "RANKED_NOT_SELECTED"
        history = list(old.get("history") or [])
        if old.get("status") and old.get("status") != status:
            history.append({"changed_at_utc": now, "from": old["status"], "to": status})
        entries[backlog_id] = {
            "backlog_id": backlog_id,
            "candidate_test_id": test["candidate_test_id"],
            "semantic_identity": test["semantic_identity"],
            "test_type": test["test_type"],
            "problem_uncertainty": test["problem_uncertainty"],
            "score": test["expected_information_gain"]["score"],
            "status": status,
            "rank": rank,
            "first_seen_at_utc": old.get("first_seen_at_utc") or now,
            "last_seen_at_utc": now,
            "deprioritized_reason": None if status == "SELECTED_NEXT_BEST_TEST" else "LOWER_INFORMATION_VALUE_THAN_SELECTED_TEST",
            "requires_scientific_admission": True,
            "automatic_execution": False,
            "canonical_effect": False,
            "portfolio_execution": False,
            "history": history[-20:],
        }
    for backlog_id, entry in entries.items():
        if backlog_id not in current and entry.get("status") != "HISTORICAL_RETAINED":
            history = list(entry.get("history") or [])
            history.append({"changed_at_utc": now, "from": entry.get("status"), "to": "HISTORICAL_RETAINED"})
            entry["status"] = "HISTORICAL_RETAINED"
            entry["history"] = history[-20:]
    rows = sorted(entries.values(), key=lambda x: (0 if x.get("status") == "SELECTED_NEXT_BEST_TEST" else 1, int(x.get("rank") or 999999), x.get("backlog_id")))
    return {
        "contract": "LEARNING_BACKLOG_v1",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "generated_at_utc": now,
        "entry_count": len(rows),
        "entries": rows,
        "preserve_rejected_and_deprioritized": True,
        "canonical_effect": False,
        "portfolio_execution": False,
    }


def _t13_status(as_of):
    activation, status = load_json(T13_ACTIVATION, {}), load_json(T13_STATUS, {})
    if not isinstance(activation, dict) or not activation:
        return {
            "contract": "COMPOUNDING_LEARNING_T13_FIREWALL_v1",
            "phase": "ACTIVATION_NOT_AVAILABLE",
            "operational_checkpoint_days_reached": [],
            "interim_performance_inference_allowed": False,
            "scientific_method_change_allowed": False,
            "automatic_child_experiment_allowed": False,
        }
    start, end = _dt(activation.get("cohort_start_utc")), _dt(activation.get("cohort_end_utc_exclusive"))
    if start and as_of < start:
        phase, day = "PRE_START", 0
    elif start and end and start <= as_of < end:
        phase, day = "ACCRUING", int((as_of - start).total_seconds() // 86400) + 1
    elif end and as_of >= end:
        phase, day = "ACCRUAL_CLOSED", int(activation.get("freeze_accrual_window_days") or 240)
    else:
        phase, day = "UNKNOWN", None
    return {
        "contract": "COMPOUNDING_LEARNING_T13_FIREWALL_v1",
        "study_id": activation.get("study_id"),
        "phase": phase,
        "cohort_start_utc": activation.get("cohort_start_utc"),
        "cohort_end_utc_exclusive": activation.get("cohort_end_utc_exclusive"),
        "accrual_day": day,
        "operational_checkpoint_days_reached": [d for d in DESCRIPTIVE_CHECKPOINT_DAYS if day is not None and day >= d],
        "forecast_skill_status": activation.get("forecast_skill_status") or (status.get("forecast_skill_status") if isinstance(status, dict) else None) or "UNPROVEN",
        "study_status": status.get("status") if isinstance(status, dict) else None,
        "outcome_data_read_flag": bool(activation.get("outcome_data_read", status.get("outcome_data_read", False) if isinstance(status, dict) else False)),
        "interim_performance_inference_allowed": False,
        "scientific_method_change_allowed": False,
        "automatic_child_experiment_allowed": False,
        "checkpoint_scope": "ACCRUAL_HEALTH_DATA_QUALITY_CONCENTRATION_AND_MATURITY_READINESS_ONLY",
        "checkpoint_may_not_emit_skill_verdict": True,
        "final_confirmatory_test_owner": "FORECAST_SKILL_CONFIRMATORY_V1_3_1_PLUS_BINDING_V1_3_2_ERRATUM",
    }


def _event(previous, families, delta, adjudication, as_of):
    if not delta["material_change"]:
        return None
    graph = digest([
        {"semantic_identity": family["semantic_identity"], "status": family["current_evidence_status"], "fp": family["material_evidence_fingerprint"]}
        for family in families if family["material_evidence"]
    ])
    seed = {"previous": previous.get("evidence_fingerprint"), "graph": graph, "adjudication": adjudication.get("generated_at_utc"), "delta": delta["changed_families"]}
    event_id = "LE-" + digest(seed)[:24]
    return {
        "contract": "LEARNING_EVENT_v1",
        "event_id": event_id,
        "generated_at_utc": as_of.isoformat().replace("+00:00", "Z"),
        "previous_state_reference": previous.get("evidence_fingerprint"),
        "new_learning_graph_reference": graph,
        "adjudication_generated_at_utc": adjudication.get("generated_at_utc"),
        "evidence_delta": delta,
        "why_change_is_justified": "Unified Experimental Adjudication produced materially different mature evidence in at least one semantic family.",
        "what_did_not_change": [
            "FROZEN_PARENT_EVIDENCE", "SCIENTIFIC_ADMISSION_CONTRACT", "CANONICAL_FRAMEWORK_AUTHORITY",
            "MARKET_THRESHOLDS_AND_MODEL_WEIGHTS", "PORTFOLIO_ACTION",
        ],
        "retroactive_mutation": False,
        "canonical_effect": False,
        "portfolio_execution": False,
    }


def _build_products(registry, admission, adjudication, policy, previous, previous_backlog, as_of):
    packets, new_keys = evaluate_candidates(registry, admission, adjudication, policy, previous, as_of)
    event_keys = sorted(set(previous.get("emitted_event_keys") or []) | set(new_keys))
    families = build_hypothesis_families(registry, admission, adjudication)
    delta = derive_learning_delta(previous, families)
    tests = generate_candidate_tests(families)
    proposal, ranked = select_bounded_next_best_test(tests, int(policy.get("max_next_best_tests_per_run", 1)))
    backlog = build_learning_backlog(previous_backlog, ranked, proposal, as_of)
    event = _event(previous, families, delta, adjudication, as_of)
    t13 = _t13_status(as_of)
    action = "PROPOSE_NEXT_BEST_TEST" if proposal.get("candidate_test_id") else "CONTINUE_OBSERVING"
    target = str(proposal.get("parent_candidate_id") or "EXPERIMENT_LIFECYCLE")
    disposition = "MATERIAL_LEARNING_DELTA" if event else "DESCRIPTIVE_CHECKPOINT_ONLY" if packets else "NO_MATERIAL_LEARNING_DELTA"
    state = {
        "contract": "COMPOUNDING_LEARNING_CONTROLLER_STATE_v1",
        "schema": "LEARNING_STATE_v1",
        "status": "ACTIVE",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "generated_at_utc": as_of.isoformat().replace("+00:00", "Z"),
        "primary_action": action,
        "target": target,
        "reason": str(proposal.get("problem_uncertainty") or "no fresh adjudicated uncertainty justifies a new child-test proposal"),
        "run_disposition": disposition,
        "family": "EXPERIMENT_LEARNING_AND_CALIBRATION",
        "learning_loop": "OBSERVE_FREEZE_TEST_MATURE_ADJUDICATE_LEARN_CHALLENGE_RETEST_IMPROVE",
        "scientific_interpretation_owner": "UNIFIED_EXPERIMENTAL_LIFECYCLE_ADJUDICATION_v1",
        "controller_role": "NEXT_LEARNING_STRATEGY_ONLY",
        "registry_candidate_count": int(registry.get("candidate_count") or len(registry.get("candidates", []))),
        "scientific_admission_candidate_count": int(admission.get("candidate_count") or len(admission.get("candidates", []))),
        "adjudication_generated_at_utc": adjudication.get("generated_at_utc"),
        "checkpoint_packet_count": len(packets),
        "new_learning_event_count": delta["changed_family_count"],
        "learning_packets": packets,
        "hypothesis_families": families,
        "learning_delta": delta,
        "emitted_event_keys": event_keys,
        "learning_event_ids": sorted(set(previous.get("learning_event_ids") or []) | ({event["event_id"]} if event else set())),
        "next_best_experiment": proposal,
        "learning_backlog_reference": "00_ARCHIVE_CONTROL/research_governance_v1/compounding_learning_v1/LEARNING_BACKLOG.json",
        "t13_confirmatory_firewall": t13,
        "descriptive_checkpoint_days": DESCRIPTIVE_CHECKPOINT_DAYS,
        "frozen_parent_rewrite_allowed": False,
        "retrospective_rescore_allowed": False,
        "canonical_effect": False,
        "portfolio_execution": False,
        "paid_data_authorized": False,
        "deep_research_authorized": False,
        "external_provider_calls_authorized": False,
        "automatic_promotion": False,
        "automatic_canonical_write": False,
        "automatic_threshold_change": False,
        "automatic_weight_change": False,
        "automatic_market_rule_change": False,
        "model_weight_change": False,
    }
    state["evidence_fingerprint"] = digest({
        "material": [(f["semantic_identity"], f["current_evidence_status"], f["material_evidence_fingerprint"]) for f in families],
        "packets": packets,
        "proposal": proposal,
        "backlog": [(r["backlog_id"], r["status"], r["score"]) for r in backlog["entries"] if r["status"] != "HISTORICAL_RETAINED"],
        "t13": t13.get("operational_checkpoint_days_reached"),
        "event_keys": event_keys,
    })
    proposal = dict(proposal)
    proposal["evidence_fingerprint"] = state["evidence_fingerprint"]
    state["next_best_experiment"] = proposal
    return state, proposal, backlog, event


def build_state(registry, admission, adjudication, policy, previous_state, as_of):
    state, proposal, _, _ = _build_products(registry, admission, adjudication, policy, previous_state, {}, as_of)
    return state, proposal


def _validate_policy(policy):
    if policy.get("contract") != "COMPOUNDING_LEARNING_CONTROLLER_POLICY_v1" or policy.get("authority") != "RESEARCH_ONLY_NON_CANONICAL":
        raise RuntimeError("compounding learning policy contract/authority invalid")
    forbidden = (
        "canonical_effect", "automatic_promotion", "automatic_canonical_write", "portfolio_execution",
        "model_weight_change", "automatic_threshold_change", "automatic_weight_change",
        "automatic_market_rule_change", "retrospective_rescore_allowed", "frozen_parent_rewrite_allowed",
    )
    if any(policy.get(key) is not False for key in forbidden):
        raise RuntimeError("compounding learning policy firewall invalid")
    profiles = policy.get("profiles") or {}
    for name in ("FAST", "STANDARD", "LONG", "CONFIRMATORY"):
        if sorted(set(int(v) for v in profiles.get(name, {}).get("day_checkpoints", []))) != DESCRIPTIVE_CHECKPOINT_DAYS:
            raise RuntimeError(f"{name} profile must implement 7/14/30/60/90/120/180/240 descriptive checkpoints")


def _validate_inputs(registry, admission, adjudication):
    if registry.get("contract") != "EXPERIMENT_LIFECYCLE_REGISTRY_v1":
        raise RuntimeError("invalid experiment registry")
    if admission.get("contract") != "EXPERIMENT_SCIENTIFIC_ADMISSION_REGISTRY_v1":
        raise RuntimeError("invalid scientific admission registry")
    if adjudication.get("contract") != "UNIFIED_EXPERIMENTAL_LIFECYCLE_ADJUDICATION_v1" or adjudication.get("authority") != "RESEARCH_ONLY_NON_CANONICAL":
        raise RuntimeError("invalid unified adjudication")
    for key in ("canonical_effect", "portfolio_execution", "automatic_threshold_change", "automatic_weight_change", "automatic_market_rule_change"):
        if adjudication.get(key) is not False:
            raise RuntimeError(f"unified adjudication firewall invalid: {key}")


def _persist_event_append_only(event):
    path = EVENT_ROOT / f"{event['event_id']}.json"
    if path.exists():
        old = load_json(path, {})
        left, right = dict(old), dict(event)
        left.pop("generated_at_utc", None)
        right.pop("generated_at_utc", None)
        if not isinstance(old, dict) or old.get("event_id") != event.get("event_id") or digest(left) != digest(right):
            raise RuntimeError("append-only learning event mutation attempted")
        return False
    persist_json(path, event)
    return True


def run_controller(*, dry_run=False, as_of_utc=None):
    policy = load_json(POLICY, {})
    _validate_policy(policy)
    registry, admission, adjudication = load_json(REGISTRY, {}), load_json(ADMISSION, {}), load_json(ADJUDICATION, {})
    if not all(isinstance(value, dict) for value in (registry, admission, adjudication)):
        raise RuntimeError("required experiment inputs unavailable")
    _validate_inputs(registry, admission, adjudication)
    previous = load_json(STATE, {}) or {}
    previous_backlog = load_json(BACKLOG, {}) or {}
    state, proposal, backlog, event = _build_products(registry, admission, adjudication, policy, previous, previous_backlog, _now(as_of_utc))
    should_persist = previous.get("evidence_fingerprint") != state["evidence_fingerprint"] or previous_backlog.get("contract") != "LEARNING_BACKLOG_v1"
    if not dry_run:
        if event:
            _persist_event_append_only(event)
        if should_persist:
            persist_json(STATE, state)
            persist_json(NEXT, proposal)
            persist_json(BACKLOG, backlog)
    return state


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--as-of-utc")
    args = parser.parse_args()
    state = run_controller(dry_run=args.dry_run, as_of_utc=args.as_of_utc)
    print({key: state[key] for key in ("contract", "run_disposition", "checkpoint_packet_count", "new_learning_event_count", "primary_action", "target")})
