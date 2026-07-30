import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def load(name):
    return json.loads((ROOT / name).read_text())

ledger = load('WP04C_ENUMERATION_LEDGER_v1.json')
audit = load('WP04C_DATASET_REPLAY_AUDIT_v1.json')
state = load('WP04C_EXECUTION_STATE_v1.json')

assert audit['result'] == 'NOT_ENUMERABLE_FROM_REPOSITORY_STATE'
assert state['trigger_contract_modified'] is False
assert state['historical_counts_exposed'] is False
assert state['outcomes_inspected'] is False
assert state['final_holdout_accessed'] is False

chains = {x['chain_id']: x for x in ledger['chains']}
assert chains['LSP_MACRO_TO_CRYPTO']['candidate_count'] is None
assert chains['LSP_LEVERAGE_TO_SPOT']['candidate_count'] is None
assert chains['LSP_ROTATION_FAILURE']['candidate_count'] == 1
assert chains['LSP_ROTATION_FAILURE']['eligible_for_outcome_testing'] is False
assert ledger['parameter_changes_after_count_visibility'] is False
assert ledger['outcomes_inspected'] is False
assert ledger['final_holdout_accessed'] is False
print('WP04C_VALIDATION_PASS')
