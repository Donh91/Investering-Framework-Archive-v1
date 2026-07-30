import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HISTORY = json.loads((ROOT / 'WP03B_OWNER_HISTORY_COMPLETION_v1.json').read_text())
EVENT = json.loads((ROOT / 'WP03B_EVENT_MATERIALIZATION_STATE_v1.json').read_text())
STATE = json.loads((ROOT / 'WP03B_EXECUTION_STATE_v1.json').read_text())

assert HISTORY['development_window_only'] is True
assert HISTORY['final_holdout_accessed'] is False
assert HISTORY['forward_returns_calculated'] is False
assert EVENT['upgrade_to_fully_replayable'] is False
assert EVENT['current_lineage_class'] == 'OWNER_PARTIAL'
assert EVENT['daily_context']['usage'] == 'CONTEXT_ONLY_NOT_CHECKPOINT_SUBSTITUTION'
assert EVENT['outcomes'] == 'NOT_CALCULATED'
assert STATE['economic_tests_run'] == 0
assert STATE['final_holdout'] == 'SEALED'
assert STATE['framework_promotion'] == 'NONE'
assert STATE['portfolio_effect'] == 'NONE'
print('WP03B_STRUCTURAL_VALIDATION_PASS')