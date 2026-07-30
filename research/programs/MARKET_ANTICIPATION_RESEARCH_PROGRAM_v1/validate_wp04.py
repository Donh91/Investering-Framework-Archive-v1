import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTRACT = json.loads((ROOT / 'WP04_LIQUIDITY_STRESS_PROPAGATION_CONTRACT_v1.json').read_text())
SCHEMA = json.loads((ROOT / 'WP04_EVENT_SCHEMA_v1.json').read_text())
STATE = json.loads((ROOT / 'WP04_EXECUTION_STATE_v1.json').read_text())

assert CONTRACT['scope'] == 'PREREGISTRATION_ONLY'
assert CONTRACT['development_window_only'] is True
assert CONTRACT['final_holdout_accessed'] is False
assert len(CONTRACT['stress_chains']) == 3
assert len(CONTRACT['frozen_windows']) == 8
assert CONTRACT['event_deduplication'] == 'ONE_INDEPENDENT_EVENT_PER_ACTIVE_OVERLAP_CLUSTER'
assert SCHEMA['interpolation_allowed'] is False
assert SCHEMA['outcome_status_allowed'] == ['NOT_CALCULATED']
assert STATE['historical_events_enumerated'] == 0
assert STATE['forward_returns_calculated'] is False
assert STATE['economic_tests_run'] == 0
assert STATE['parameter_search_run'] is False
assert STATE['final_holdout'] == 'SEALED'
assert STATE['framework_promotion'] == 'NONE'
assert STATE['portfolio_effect'] == 'NONE'
print('WP04_PREREGISTRATION_STRUCTURAL_VALIDATION_PASS')
