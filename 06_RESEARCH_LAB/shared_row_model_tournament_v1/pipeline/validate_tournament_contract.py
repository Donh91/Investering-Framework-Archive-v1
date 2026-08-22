#!/usr/bin/env python3
import csv,json,pathlib
R=pathlib.Path(__file__).resolve().parents[1]
A={'SPARSE_STACK_SUPPORTED','FULL_STACK_INCREMENTAL_EDGE_SUPPORTED','TASK_DEPENDENT_PARETO_FRONT','INSUFFICIENT_EVIDENCE'}
reg=json.loads((R/'03_CANDIDATE_REGISTRY.json').read_text());assert reg['authority']=='RESEARCH_ONLY_NON_CANONICAL';assert reg['promotion_allowed'] is False
ids=[c['id'] for c in reg['candidates']];assert len(ids)==len(set(ids));assert 'C07_SIMPLE_3' in ids and 'C12_FULL_STACK' in ids;assert next(c for c in reg['candidates'] if c['id']=='C07_SIMPLE_3')['favored'] is False
v=json.loads((R/'25_FINAL_MACHINE_READABLE_VERDICT.json').read_text());assert v['terminal_verdict'] in A;assert v['canonical_change'] is False;assert v['portfolio_change'] is False
h=next(csv.reader(open(R/'data/PROSPECTIVE_SHARED_ROW_LEDGER.csv',encoding='utf-8')));assert {'event_id','observation_timestamp_utc','information_cutoff_utc','candidate_decisions','outcome_24h','outcome_72h','outcome_7d','provenance_hash'}.issubset(set(h))
f=next(csv.reader(open(R/'14_DIVERGENCE_FNP_LEDGER.csv',encoding='utf-8')));assert {'outcome_24h','outcome_72h','outcome_7d'}.issubset(set(f));print('SHARED_ROW_TOURNAMENT_CONTRACT_PASS')
