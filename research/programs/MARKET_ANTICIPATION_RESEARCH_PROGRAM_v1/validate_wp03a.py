import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENUM = json.loads((ROOT / 'WP03A_OWNER_EVENT_ENUMERATION_v1.json').read_text())
AUDIT = json.loads((ROOT / 'WP03A_LINEAGE_AUDIT_v1.json').read_text())

assert ENUM['development_window_only'] is True
assert ENUM['final_holdout_accessed'] is False
assert ENUM['forward_returns_calculated'] is False
assert ENUM['economic_ranking_calculated'] is False
assert ENUM['independent_event_count'] == len(ENUM['events'])
assert ENUM['follow_up_row_count'] == len(ENUM['same_cluster_follow_ups'])
assert len({e['event_id'] for e in ENUM['events']}) == len(ENUM['events'])
assert all(e['outcome_status'] == 'NOT_CALCULATED' for e in ENUM['events'])
assert all(e['lineage_class'] in {'FULLY_REPLAYABLE','OWNER_PARTIAL','SHADOW_ONLY','BLOCKED','RIGHT_CENSORED'} for e in ENUM['events'])
assert all(r['classification'] == 'SAME_CLUSTER_FOLLOW_UP' for r in ENUM['same_cluster_follow_ups'])
assert AUDIT['classification_counts']['OWNER_PARTIAL'] == 1
assert AUDIT['classification_counts']['SAME_CLUSTER_FOLLOW_UP'] == 8
assert AUDIT['classification_counts']['BLOCKED'] == 3
print('WP03A_STRUCTURAL_VALIDATION_PASS')
