import json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

def test_validation_policy_is_shadow_only():
    p=json.loads((ROOT/'research/evidence_gap/ADAPTIVE_EVIDENCE_GAP_VALIDATION_POLICY_v1_1.json').read_text())
    a=p['authority']
    assert a['can_change_market_rules'] is False
    assert a['can_change_thresholds'] is False
    assert a['can_change_weights'] is False
    assert a['can_change_canonical_state'] is False
    assert a['can_create_portfolio_action'] is False
    assert a['can_self_promote_sensor'] is False
    assert p['anti_hindsight']['discovery_episode_counts_as_validation'] is False
    assert p['promotion_review_minimums']['automatic_promotion'] is False


def test_promotion_review_requires_time_episodes_and_supported_value(tmp_path):
    registry=tmp_path/'registry.json'; audit=tmp_path/'audit.json'
    registry.write_text(json.dumps({'items':{'EG-X':{'gap_id':'EG-X','first_seen_utc':'2026-01-01T00:00:00Z','closure_state':'PROSPECTIVE_CAPTURE_ACTIVE'}}}))
    audit.write_text(json.dumps({'results':[{'gap_id':'EG-X','validation_state':'USEFUL_RESEARCH_EVIDENCE','non_discovery_episode_count':3,'incremental_value':'SUPPORTED','source_reliability':'PASS','decision_timing_value':'IMPROVED','false_signal_value':'NO_CHANGE','evidence_references':['later-episode-a'],'counterevidence_references':[],'rationale':'repeatable'}]}))
    subprocess.run([sys.executable,str(ROOT/'scripts/api_agent/apply_evidence_gap_validation.py'),'--registry',str(registry),'--audit',str(audit),'--min-episodes','3','--min-days','14'],check=True)
    out=json.loads(registry.read_text())['items']['EG-X']['validation']
    assert out['promotion_review_eligible'] is True
    assert out['automatic_promotion'] is False
    assert out['discovery_episode_counts_as_validation'] is False


def test_rejection_closes_gap_without_market_authority(tmp_path):
    registry=tmp_path/'registry.json'; audit=tmp_path/'audit.json'
    registry.write_text(json.dumps({'items':{'EG-Y':{'gap_id':'EG-Y','first_seen_utc':'2026-01-01T00:00:00Z','closure_state':'PROSPECTIVE_CAPTURE_ACTIVE'}}}))
    audit.write_text(json.dumps({'results':[{'gap_id':'EG-Y','validation_state':'REJECTED_NO_INCREMENTAL_VALUE','non_discovery_episode_count':4,'incremental_value':'NOT_SUPPORTED','source_reliability':'PASS','decision_timing_value':'NO_CHANGE','false_signal_value':'NO_CHANGE','evidence_references':[],'counterevidence_references':['later-b','later-c'],'rationale':'no incremental value'}]}))
    subprocess.run([sys.executable,str(ROOT/'scripts/api_agent/apply_evidence_gap_validation.py'),'--registry',str(registry),'--audit',str(audit)],check=True)
    item=json.loads(registry.read_text())['items']['EG-Y']
    assert item['closure_state']=='CLOSED'
    assert item['validation']['promotion_review_eligible'] is False


def test_decision_miss_registry_marks_discovery_only(tmp_path):
    audit=tmp_path/'miss.json'; reg=tmp_path/'miss-reg.json'
    audit.write_text(json.dumps({'misses':[{'phase':'PULLBACK_REENTRY','miss_type':'MISSED_PULLBACK_REENTRY','decision_reference':'before','outcome_reference':'after','miss_description':'missed rebound','proposed_metric_name':'x','counterfactual_theory':'might help','confidence':'MODERATE'}]}))
    subprocess.run([sys.executable,str(ROOT/'scripts/api_agent/decision_miss_registry.py'),'--audit',str(audit),'--registry',str(reg)],check=True)
    item=next(iter(json.loads(reg.read_text())['items'].values()))
    assert item['validation_semantics']=='DISCOVERY_ONLY_DOES_NOT_VALIDATE_PROPOSED_METRIC'
    assert item['authority']['portfolio_action'] is False
