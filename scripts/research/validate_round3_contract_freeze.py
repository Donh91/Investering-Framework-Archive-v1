#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path('06_RESEARCH_LAB/round3_new_information_v1')
LEGACY = Path('06_RESEARCH_LAB/historical_altseason_pullback_v1/config.json')


def load(name: str):
    return json.loads((ROOT / name).read_text())


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def validate_materialized_v2(status: dict):
    mat = ROOT / 'materialized_v2'
    receipt_path = mat / 'V2_MATERIALIZATION_RECEIPT.json'
    pair_path = mat / 'V2_EVENT_CONTROL_PAIRS.csv'
    commitment_path = mat / 'V2_CATALOG_COMMITMENT.json'
    present = [p.exists() for p in (receipt_path, pair_path, commitment_path)]
    if not any(present):
        assert status.get('v2_materialized') is not True
        return
    assert all(present), 'partial V2 materialization commitment is forbidden'

    receipt = json.loads(receipt_path.read_text())
    commitment = json.loads(commitment_path.read_text())
    pair_git_lf_sha = sha256_file(pair_path)

    assert receipt['contract'] == 'V2_EPISODE_CATALOG_MATERIALIZATION_RECEIPT_v1'
    assert commitment['contract'] == 'ROUND3_V2_CATALOG_COMMITMENT_v1'
    assert receipt['source_values_loaded'] is False
    assert receipt['round1_round2_relabelled'] is False
    assert receipt['round3_source_files_read'] == []
    assert commitment['source_values_loaded_at_freeze'] is False
    assert commitment['round3_source_files_read_at_freeze'] == []
    assert commitment['round1_round2_relabelled'] is False

    assert receipt['episode_count_by_era'] == {
        'ALTSEASON_2020_2021': 81,
        'MODERN_ANALOGUE_2025_2026': 54,
    }
    assert receipt['control_count_by_era'] == {
        'ALTSEASON_2020_2021': 79,
        'MODERN_ANALOGUE_2025_2026': 50,
    }
    assert receipt['failed_match_reasons'] == {
        'ANCHOR_MATCH_FEATURES_MISSING': 1,
        'NO_ELIGIBLE_CONTROL_IN_CALIPER': 5,
    }
    assert commitment['episode_count_total'] == 135
    assert commitment['matched_control_count_total'] == 129
    assert commitment['unmatched_episode_count'] == 6

    assert receipt['pair_set_line_ending_equivalence'] == 'SAME_135_CSV_RECORDS_CRLF_ARTIFACT_VS_LF_GIT_CONTENT'
    assert receipt['pair_set_sha256'] == receipt['pair_set_artifact_crlf_sha256']
    assert pair_git_lf_sha == receipt['pair_set_git_lf_sha256']
    assert receipt['pair_set_sha256'] == commitment['pair_set_sha256'] == status['v2_pair_set_sha256']
    assert receipt['catalog_sha256'] == commitment['catalog_sha256'] == status['v2_catalog_sha256']
    assert receipt['input_panel_sha256'] == commitment['input_panel_sha256']

    with pair_path.open(newline='') as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 135
    assert sum(r['control_status'] == 'OK' for r in rows) == 129
    assert sum(r['control_status'] != 'OK' for r in rows) == 6
    assert sum(r['era'] == 'ALTSEASON_2020_2021' for r in rows) == 81
    assert sum(r['era'] == 'MODERN_ANALOGUE_2025_2026' for r in rows) == 54

    assert status['v2_materialized'] is True
    assert status['v2_episode_count'] == 135
    assert status['v2_matched_control_count'] == 129
    print('ROUND3_V2_COMMITMENT_PASS', receipt['catalog_sha256'], receipt['pair_set_sha256'], pair_git_lf_sha)


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
    binding = load('PRIVATE_DATA_PLANE_BINDING_RECEIPT.json')
    terms = load('PROVIDER_TERMS_AND_RETENTION_BOUNDARY_RECEIPT.json')
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

    assert zone['status'] == 'PRIVATE_DATA_PLANE_BOUND_COLLECTION_ONLY'
    assert zone['canonical_framework_repo']['visibility_at_binding'] == 'PUBLIC'
    assert zone['canonical_framework_repo']['raw_provider_payloads_allowed'] is False
    assert zone['canonical_framework_repo']['normalized_provider_market_values_allowed'] is False
    assert zone['restricted_data_plane']['repository'] == 'Donh91/secrets'
    assert zone['restricted_data_plane']['visibility_verified'] == 'PRIVATE'
    assert zone['restricted_data_plane']['raw_provider_payloads_allowed'] is True
    assert zone['restricted_data_plane']['credentials_in_git_forbidden'] is True
    assert zone['github_storage_audit']['suitable_private_repository_found'] is True
    assert zone['activation_gate']['collection_workflow_may_be_scheduled_after_pass'] is True
    assert zone['activation_gate']['hypothesis_testing_after_pass'] is False
    assert zone['activation_gate']['outcome_scoring_after_pass'] is False

    assert binding['restricted_repo'] == 'Donh91/secrets'
    assert binding['restricted_repo_visibility'] == 'PRIVATE'
    assert binding['destination_access_verified'] is True
    assert binding['public_raw_provider_values_allowed'] is False
    assert binding['private_raw_provider_values_allowed'] is True
    assert binding['hypothesis_testing_active'] is False
    assert binding['outcome_scoring_active'] is False

    assert terms['scope'] == 'PROSPECTIVE_PRIVATE_INTERNAL_RESEARCH_COLLECTION_ONLY'
    assert terms['formal_legal_opinion_asserted'] is False
    assert terms['public_raw_provider_payload_storage'] is False
    assert len(terms['sources']) == 4
    assert all(s['public_redistribution'] is False for s in terms['sources'])
    assert terms['hypothesis_testing_authorized'] is False
    assert terms['outcome_scoring_authorized'] is False

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
    assert status['restricted_data_plane'] == 'Donh91/secrets'
    assert 'PRIVATE_STORAGE_REQUIRED' not in status['blockers']
    assert status['source_states']['SC01_OKX_ETH_OI_HOURLY_V1'] == 'FROZEN_PRIVATE_CANARY_READY'
    assert status['source_states']['SC03_OKX_ETH_REALIZED_FUNDING_V1'] == 'FROZEN_PRIVATE_CANARY_READY'
    assert status['source_states']['SC14_DERIBIT_ETH_TRUE_25D_SKEW_V1'] == 'FROZEN_PRIVATE_CANARY_READY'
    assert status['source_states']['SC06_BINANCE_ETH_BOOK_DEPTH_V1'] == 'FROZEN_CANARY_ONLY_PERSISTENT_RUNTIME_REQUIRED'

    validate_materialized_v2(status)

    print('ROUND3_CONTRACT_FREEZE_PASS')
    print('PRIMARY_COUNT', hyps['primary_count'])
    print('GLOBAL_FWER_ALPHA', hyps['global_family']['familywise_alpha'])
    print('V2_CAP_HOURS', v2['v2_episode_rule']['closure_cap_hours_after_trigger'])
    print('COLLECTION_ACTIVE', status['collection_active'])
    print('RESTRICTED_DATA_PLANE', zone['restricted_data_plane']['repository'])
    print('RAW_PUBLIC_STORAGE', zone['canonical_framework_repo']['raw_provider_payloads_allowed'])


if __name__ == '__main__':
    main()
