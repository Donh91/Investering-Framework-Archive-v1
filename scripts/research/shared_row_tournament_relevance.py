#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path('06_RESEARCH_LAB/shared_row_model_tournament_v1')
def nrows(p):
    with p.open(newline='',encoding='utf-8-sig') as f:return sum(1 for _ in csv.DictReader(f))
def main():
    m=json.loads((ROOT/'OWNER_BINDING_MATRIX.json').read_text()); rn=nrows(ROOT/'data/PROSPECTIVE_SHARED_ROW_LEDGER.csv'); dn=nrows(ROOT/'14_DIVERGENCE_FNP_LEDGER.csv'); states={}
    for f in m['families']:
        if f['status']=='BLOCKED': state='UNTESTABLE'
        elif f['status'] in {'PARTIAL','READY'} and rn==0: state='COLLECTING'
        elif rn>0: state='EVALUABLE'
        else: state='INSUFFICIENT_EVIDENCE'
        states[f['family_id']]=state
    out={'contract':'SHARED_ROW_RELEVANCE_LIFECYCLE_v1','authority':'RESEARCH_ONLY_NON_CANONICAL','generated_at_utc':datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z'),'overall_state':'COLLECTING' if rn==0 else 'EVALUABLE','states':states,'eligible_row_n':rn,'divergence_n':dn,'terminal_verdict':'INSUFFICIENT_EVIDENCE','automatic_research_metadata_only':True,'canonical_effect':False}
    (ROOT/'RELEVANCE_STATE.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps({'status':'PASS','eligible_rows':rn,'divergences':dn,'overall_state':out['overall_state']},sort_keys=True))
if __name__=='__main__':main()
