#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from datetime import datetime,timezone
from pathlib import Path
from shared_row_tournament_weekly import filter_consumer_rows
ROOT=Path('06_RESEARCH_LAB/shared_row_model_tournament_v1')
def rows(p):
    with p.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def main():
    m=json.loads((ROOT/'OWNER_BINDING_MATRIX.json').read_text()); runtime=json.loads((ROOT/'RUNTIME_STATUS.json').read_text()); raw_rows=rows(ROOT/'data/PROSPECTIVE_SHARED_ROW_LEDGER.csv'); raw_div=rows(ROOT/'14_DIVERGENCE_FNP_LEDGER.csv'); valid_rows,valid_div,excluded=filter_consumer_rows(raw_rows,raw_div,runtime); rn=len(valid_rows); dn=len(valid_div); states={}
    for f in m['families']:
        if f['status']=='BLOCKED': state='UNTESTABLE'
        elif f['status'] in {'PARTIAL','READY'} and rn==0: state='COLLECTING'
        elif rn>0: state='EVALUABLE'
        else: state='INSUFFICIENT_EVIDENCE'
        states[f['family_id']]=state
    out={'contract':'SHARED_ROW_RELEVANCE_LIFECYCLE_v1','authority':'RESEARCH_ONLY_NON_CANONICAL','generated_at_utc':datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z'),'overall_state':'COLLECTING' if rn==0 else 'EVALUABLE','states':states,'eligible_row_n':rn,'divergence_n':dn,'consumer_integrity_filter':{'raw_rows':len(raw_rows),'raw_divergences':len(raw_div),'excluded':excluded},'terminal_verdict':'INSUFFICIENT_EVIDENCE','automatic_research_metadata_only':True,'canonical_effect':False}
    (ROOT/'RELEVANCE_STATE.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps({'status':'PASS','eligible_rows':rn,'divergences':dn,'overall_state':out['overall_state']},sort_keys=True))
if __name__=='__main__':main()
