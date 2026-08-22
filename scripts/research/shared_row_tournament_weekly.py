#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path('06_RESEARCH_LAB/shared_row_model_tournament_v1'); LED=ROOT/'data/PROSPECTIVE_SHARED_ROW_LEDGER.csv'; FNP=ROOT/'14_DIVERGENCE_FNP_LEDGER.csv'; REG=ROOT/'03_CANDIDATE_REGISTRY.json'; OUT=ROOT/'weekly'
def read(p):
    with p.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def b(v):
    s=str(v).strip().lower(); return 1 if s in {'1','true','yes','positive','signal','permission'} else 0 if s in {'0','false','no','negative','no_signal','wait','block'} else None
def ratio(a,z):return None if z==0 else a/z
def metrics(rows,cid,h):
    tp=fp=tn=fn=0; mae=[]; mfe=[]
    for r in rows:
        try:d=b(json.loads(r.get('candidate_decisions') or '{}').get(cid))
        except Exception:d=None
        y=b(r.get(f'outcome_{h}'))
        if d is None or y is None: continue
        if d==1 and y==1:tp+=1
        elif d==1:fp+=1
        elif y==0:tn+=1
        else:fn+=1
        for name,arr in [(f'mae_{h}',mae),(f'mfe_{h}',mfe)]:
            try:
                if str(r.get(name,'')).strip(): arr.append(float(r[name]))
            except Exception: pass
    n=tp+fp+tn+fn
    return {'n':n,'tp':tp,'fp':fp,'tn':tn,'fn':fn,'precision':ratio(tp,tp+fp),'recall':ratio(tp,tp+fn),'false_positive_rate':ratio(fp,fp+tn),'false_negative_rate':ratio(fn,fn+tp),'mae_mean':sum(mae)/len(mae) if mae else None,'mfe_mean':sum(mfe)/len(mfe) if mfe else None}
def incr(rows,base,other,h='24h'):
    changed=wins=fails=0
    for r in rows:
        try:d=json.loads(r.get('candidate_decisions') or '{}')
        except Exception:continue
        a,bv=b(d.get(base)),b(d.get(other)); y=b(r.get(f'outcome_{h}'))
        if a is None or bv is None or a==bv:continue
        changed+=1
        if y is not None:
            wins+=int(bv==y and a!=y); fails+=int(bv!=y and a==y)
    return {'addition':other,'vs':base,'horizon':h,'decisions_changed_n':changed,'unique_wins_n':wins,'unique_failures_n':fails,'delay_cost':'UNAVAILABLE_UNTIL_CONFIRMATION_TIMESTAMPS','tail_errors_avoided':'UNAVAILABLE_UNTIL_NUMERIC_TAIL_OUTCOMES'}
def main():
    rows=read(LED); div=read(FNP); now=datetime.now(timezone.utc); y,w,_=now.isocalendar(); ids=[c['id'] for c in json.loads(REG.read_text())['candidates']]
    perf={cid:{h:metrics(rows,cid,h) for h in ['24h','72h','7d']} for cid in ids}; mats={h:sum(bool(d.get(f'matured_{h}_utc')) for d in div) for h in ['24h','72h','7d']}
    report={'contract':'SHARED_ROW_TOURNAMENT_WEEKLY_v1','authority':'RESEARCH_ONLY_NON_CANONICAL','generated_at_utc':now.replace(microsecond=0).isoformat().replace('+00:00','Z'),'iso_year':y,'iso_week':w,'status':'COLLECTING' if not rows else 'EVALUATING','eligible_rows_total':len(rows),'consensus_rows':sum(1 for r in rows if len(set(json.loads(r.get('candidate_decisions') or '{}').values()))<=1),'divergences_total':len(div),'matured':mats,'candidate_performance':perf,'incremental_value_matrix':[incr(rows,'C07_SIMPLE_3',x) for x in ['C08_SIMPLE_3_ETF','C09_SIMPLE_3_ETF_LEV','C10_BEST_SPARSE_STABLECOIN','C11_BEST_SPARSE_CFGI','C12_FULL_STACK']],'tail_error_prevention':{'status':'UNAVAILABLE' if not div else 'EVALUATE_FROM_MATURED_DIVERGENCES','n':len(div)},'architecture_gate':'INSUFFICIENT_EVIDENCE','canonical_effect':False}
    OUT.mkdir(parents=True,exist_ok=True); name=f'SHARED_ROW_TOURNAMENT_WEEKLY_{y}-W{w:02d}.json'; (OUT/name).write_text(json.dumps(report,indent=2,sort_keys=True)+'\n'); (OUT/'LATEST.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    (OUT/'LATEST.md').write_text(f'# Shared Row Tournament Weekly\n\n- Week: `{y}-W{w:02d}`\n- Eligible rows: **{len(rows)}**\n- Divergences: **{len(div)}**\n- Matured 24h / 72h / 7d: **{mats["24h"]} / {mats["72h"]} / {mats["7d"]}**\n- Architecture gate: `INSUFFICIENT_EVIDENCE`\n\nNo narrative winner is permitted before prospective evidence can support it.\n')
    print(json.dumps({'status':'PASS','report':str(OUT/name),'eligible_rows':len(rows),'divergences':len(div)},sort_keys=True))
if __name__=='__main__':main()
