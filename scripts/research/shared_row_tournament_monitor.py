#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path('06_RESEARCH_LAB/shared_row_model_tournament_v1'); REGISTRY=Path('04_MARKET_LEARNING/shadow_registry/REGISTRY.json')
def read_csv(p):
    with p.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def main():
    required=[ROOT/'OWNER_BINDING_MATRIX.json',ROOT/'TRANSFORM_FREEZE_REGISTRY.json',ROOT/'03_CANDIDATE_REGISTRY.json',ROOT/'04_SHARED_ROW_SCHEMA.json',ROOT/'data/PROSPECTIVE_SHARED_ROW_LEDGER.csv',ROOT/'14_DIVERGENCE_FNP_LEDGER.csv',ROOT/'RELEVANCE_STATE.json',REGISTRY]
    issues=[f'MISSING:{p}' for p in required if not p.exists()]
    matrix=json.loads((ROOT/'OWNER_BINDING_MATRIX.json').read_text()); reg=json.loads(REGISTRY.read_text())
    if 'SHARED_ROW_MODEL_TOURNAMENT_V1' not in {x['sensor_id'] for x in reg['sensors']}: issues.append('SHADOW_REGISTRY_NOT_REGISTERED')
    rr=read_csv(ROOT/'data/PROSPECTIVE_SHARED_ROW_LEDGER.csv'); dd=read_csv(ROOT/'14_DIVERGENCE_FNP_LEDGER.csv')
    unresolved=[f['family_id'] for f in matrix['families'] if f['status']!='READY' or f['candidate_decision_contract_status']!='READY']
    mats={h:sum(bool(x.get(f'matured_{h}_utc')) for x in dd) for h in ['24h','72h','7d']}; next_event='FIRST_ELIGIBLE_SHARED_ROW' if not unresolved else 'FREEZE:'+','.join(unresolved[:3])
    out={'contract':'SHARED_ROW_TOURNAMENT_MONITOR_v1','authority':'RESEARCH_ONLY_NON_CANONICAL','generated_at_utc':datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z'),'status':'PASS' if not issues else 'FAIL','scoring_readiness':'NOT_READY_NO_SHARED_ROWS' if not rr else 'READY_FOR_AVAILABLE_MATURED_OUTCOMES','eligible_row_n':len(rr),'divergence_n':len(dd),'matured':mats,'unresolved_family_bindings':unresolved,'issues':issues,'exact_next_evidence_event':next_event,'canonical_effect':False}
    d=ROOT/'monitor'; d.mkdir(parents=True,exist_ok=True); (d/'LATEST.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,sort_keys=True)); raise SystemExit(0 if not issues else 2)
if __name__=='__main__':main()
