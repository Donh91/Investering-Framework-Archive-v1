#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path('06_RESEARCH_LAB/round3_new_information_v1')
LEGACY = Path('06_RESEARCH_LAB/historical_altseason_pullback_v1/config.json')


def load(name: str):
    return json.loads((ROOT / name).read_text())


def main():
    acceptance = load('BLUEPRINT_ACCEPTANCE_RECEIPT.json')
    v2 = load('V2_EPISODE_AND_CONTROL_CONTRACT_v1.json')
    hyps = load('PRIMARY_HYPOTHESIS_REGISTRY_v1.json')
    src = load('SOURCE_CONTRACT_REGISTRY_v1.json')
    inf = load('MULTIPLICITY_POWER_HOLD_CONTRACT_v1.json')
    zone = load('COLLECTION_ZONE_CONTRACT_v1.json')
    schema = load('NORMALIZED_ROW_SCHEMA_v1.json')
    change = load('CHANGE_CONTROL_v1.json')
    status = load('COLLECTION_STATUS.json')
    legacy = json.loads(LEGACY.read_text())

    assert acceptance['decision'] == 'CONDITIONAL_ACCEPT_FOR_CONTRACT_FREEZE_AND_PROSPECTIVE_COLLECTION_ONLY'
    assert acceptance['blueprint_package']['sha256'] == '340b9dea7a322626727a3059f47899ad2acfafaa7137fb19fd9b64f3163874ea'
    assert acceptance['acceptance']['round1_round2_closed_evidence'] is True
    assert acceptance['freeze_base']['round3_source_values_inspected_for_acceptance'] is False
    assert acceptance['freeze_base']['round3_outcome_scoring_performed'] is False

    assert legacy['contract'] == v2['legacy_binding']['config_contract']
    assert legacy['episode_drawdown_trigger_pct'] == v2['legacy_binding']['episode_drawdown_trigger_pct'] == 5.0
    assert legacy['episode_recovery_fraction'] == v2['legacy_binding']['episode_recovery_fraction'] == 0.75
    assert legacy['episode_min_separation_hours'] == v2['legacy_binding']['episode_min_separation_hours'] == 24
    assert v2['v2_episode_rule']['closure_cap_hours_after_trigger'] == 336
    assert v2['v2_episode_rule']['round1_round2_relabelled'] is False
    assert v2['control_design']['time_caliper_days_absolute'] == 30
    assert v2['control_design']['same_era_required'] is True
    assert v2['control_design']['round3_source_values_allowed_in_control_selection'] is False
    assert v2['control_design']['round3_source_missingness_allowed_in_control_selection'] is False
    assert len(v2['control_design']['matching_features']) == 5

    assert hyps['primary_count'] == 4
    assert hyps['global_family']['familywise_alpha'] == 0.05
    assert hyps['common_contract']['actionable_window'] == 'T-24H_THROUGH_T-1H'
    assert hyps['common_contract']['policy_threshold_is_not_a_stage1_rejection_gate'] is True
    ids = [h['hypothesis_id'] for h in hyps['hypotheses']]
    assert ids == [
        'R3-H01-ETH-OI-EXPANSION',
        'R3-H02-ETH-FUNDING-BURDEN',
        'R3-H03-ETH-BID-DEPTH-WITHDRAWAL',
        'R3-H04-ETH-25D-PUT-SKEW',
    ]
    assert all(h['threshold_status'] == 'FROZEN_STAGE2_ONLY' for h in hyps['hypotheses'])

    assert len(src['sources']) == 4
    assert src['raw_provider_values_public_repo_allowed'] is False
    assert all(s['activation_requirement'] == 'PRIVATE_STORAGE_AND_TERMS_BOUNDARY_PASS' for s in src['sources'])
    assert all(s['no_fill'] is True and s['no_venue_substitution'] is True for s in src['sources'])

    assert inf['inference']['familywise_alpha'] == 0.05
    assert inf['prospective_blocks']['minimum_complete_pairs_each'] == 30
    assert inf['prospective_blocks']['minimum_complete_pair_coverage'] == 0.80
    assert inf['power_gate']['minimum_familywise_power_at_0_67'] == 0.80
    assert inf['stage2_hold']['benchmark'] == 'HOLD'
    assert inf['stage2_hold']['allowed_only_after_stage1_global_success'] is True
    assert inf['stage2_hold']['threshold_retuning'] is False

    assert zone['status'] == 'BLOCKED_PRIVATE_STORAGE_REQUIRED'
    assert zone['canonical_framework_repo']['visibility_at_freeze'] == 'PUBLIC'
    assert zone['canonical_framework_repo']['raw_provider_payloads_allowed'] is False
    assert zone['canonical_framework_repo']['normalized_provider_market_values_allowed'] is False
    assert zone['private_zone_requirements']['provider_terms_review_required_before_activation'] is True
    assert zone['activation_gate']['collection_workflow_may_be_scheduled_before_pass'] is False
    assert zone['activation_gate']['provider_calls_from_round3_collection_before_pass'] is False

    assert schema['public_repo_rows_forbidden'] is True
    assert schema['missingness']['missing_is_zero'] is False
    assert schema['missingness']['forward_fill_forbidden'] is True
    assert schema['missingness']['interpolation_forbidden'] is True
    assert change['closed_evidence_firewall']['round1_reopened'] is False
    assert change['closed_evidence_firewall']['round2_reopened'] is False

    assert status['collection_active'] is False
    assert status['hypothesis_testing_active'] is False
    assert status['outcome_scoring_active'] is False
    assert status['paid_historical_api_calls_authorized'] is False
    assert 'PRIVATE_STORAGE_REQUIRED' in status['blockers']

    print('ROUND3_CONTRACT_FREEZE_PASS')
    print('PRIMARY_COUNT', hyps['primary_count'])
    print('GLOBAL_FWER_ALPHA', hyps['global_family']['familywise_alpha'])
    print('V2_CAP_HOURS', v2['v2_episode_rule']['closure_cap_hours_after_trigger'])
    print('COLLECTION_ACTIVE', status['collection_active'])
    print('RAW_PUBLIC_STORAGE', zone['canonical_framework_repo']['raw_provider_payloads_allowed'])


if __name__ == '__main__':
    main()
