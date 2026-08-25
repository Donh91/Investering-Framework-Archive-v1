#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
import prospective_evidence_controller as evidence
ROOT=Path('06_RESEARCH_LAB/shared_row_model_tournament_v1'); LED=ROOT/'data/PROSPECTIVE_SHARED_ROW_LEDGER.csv'; FNP=ROOT/'14_DIVERGENCE_FNP_LEDGER.csv'; REG=ROOT/'03_CANDIDATE_REGISTRY.json'; OUT=ROOT/'weekly'
ACTIVE_COLLECTION_STATE='ACTIVE_POST_REPAIR_PROSPECTIVE_COLLECTION'
ACTIVE_FLOOR_STATUS='ACTIVE_POST_REPAIR_FLOOR'
ROW_INTEGRITY_CONTRACT='SHARED_ROW_P0_BINDING_v1'
SHA256_RE=re.compile(r'^[0-9a-f]{64}$')
def read(p):
    with p.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def ts(v):
    try:
        d=datetime.fromisoformat(str(v or '').replace('Z','+00:00'))
        return d.astimezone(timezone.utc) if d.tzinfo else None
    except Exception:return None
def filter_consumer_rows(rows,divs,runtime,verify_source_bindings=None):
    """Return only active-floor rows with reconstructable immutable provenance."""
    excluded={'runtime_inactive':0,'duplicate_event_id':0,'integrity_contract':0,'pre_floor_or_timestamp':0,'source_binding':0,'immutable_provenance':0,'divergence_parent':0,'divergence_provenance':0}
    floor=ts(runtime.get('core_prospective_eligibility_start'))
    active=(runtime.get('collection_state')==ACTIVE_COLLECTION_STATE and runtime.get('core_prospective_eligibility_status')==ACTIVE_FLOOR_STATUS and floor is not None)
    if not active:
        excluded['runtime_inactive']=len(rows); excluded['divergence_parent']=len(divs)
        return [],[],excluded
    counts={}
    for row in rows:
        event_id=str(row.get('event_id') or ''); counts[event_id]=counts.get(event_id,0)+1
    verify=verify_source_bindings or evidence.verify_source_bindings
    valid={}
    for row in rows:
        event_id=str(row.get('event_id') or '')
        if not event_id or counts[event_id]!=1:
            excluded['duplicate_event_id']+=1; continue
        if row.get('row_integrity_contract')!=ROW_INTEGRITY_CONTRACT:
            excluded['integrity_contract']+=1; continue
        observation=ts(row.get('observation_timestamp_utc')); cutoff=ts(row.get('information_cutoff_utc'))
        if observation is None or cutoff is None or observation!=cutoff or observation<floor:
            excluded['pre_floor_or_timestamp']+=1; continue
        provenance=str(row.get('provenance_hash') or '')
        if not SHA256_RE.fullmatch(provenance):
            excluded['immutable_provenance']+=1; continue
        try:
            decisions=json.loads(row.get('candidate_decisions') or '{}')
            if not isinstance(decisions,dict) or not decisions or not all(isinstance(value,bool) for value in decisions.values()): raise ValueError('candidate decisions')
            verify(row,cutoff)
        except Exception:
            excluded['source_binding']+=1; continue
        valid[event_id]=row
    valid_divs=[]
    for div in divs:
        parent=valid.get(str(div.get('event_id') or ''))
        if parent is None:
            excluded['divergence_parent']+=1; continue
        divergence_id=str(div.get('divergence_id') or '')
        expected=hashlib.sha256((parent['provenance_hash']+divergence_id).encode('utf-8')).hexdigest()
        if (not divergence_id or div.get('provenance_hash')!=expected or div.get('observation_timestamp_utc')!=parent.get('observation_timestamp_utc') or div.get('information_cutoff_utc')!=parent.get('information_cutoff_utc')):
            excluded['divergence_provenance']+=1; continue
        valid_divs.append(div)
    return list(valid.values()),valid_divs,excluded
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
    raw_rows=read(LED); raw_div=read(FNP); runtime=json.loads((ROOT/'RUNTIME_STATUS.json').read_text()); rows,div,excluded=filter_consumer_rows(raw_rows,raw_div,runtime); now=datetime.now(timezone.utc); y,w,_=now.isocalendar(); ids=[c['id'] for c in json.loads(REG.read_text())['candidates']]
    perf={cid:{h:metrics(rows,cid,h) for h in ['24h','72h','7d']} for cid in ids}; mats={h:sum(bool(d.get(f'matured_{h}_utc')) for d in div) for h in ['24h','72h','7d']}
    challengers=['C08_SIMPLE_3_ETF','C09_SIMPLE_3_ETF_LEVERAGE','C10_STABLECOIN_CHALLENGER','C11_CFGI_CHALLENGER','C12_FULL_STACK']
    report={'contract':'SHARED_ROW_TOURNAMENT_WEEKLY_v1','authority':'RESEARCH_ONLY_NON_CANONICAL','generated_at_utc':now.replace(microsecond=0).isoformat().replace('+00:00','Z'),'iso_year':y,'iso_week':w,'status':'COLLECTING' if not rows else 'EVALUATING','eligible_rows_total':len(rows),'consensus_rows':sum(1 for r in rows if len(set(json.loads(r.get('candidate_decisions') or '{}').values()))<=1),'divergences_total':len(div),'matured':mats,'candidate_performance':perf,'incremental_value_matrix':[incr(rows,'C07_SIMPLE_3',x) for x in challengers],'tail_error_prevention':{'status':'UNAVAILABLE' if not div else 'EVALUATE_FROM_MATURED_DIVERGENCES','n':len(div)},'consumer_integrity_filter':{'raw_rows':len(raw_rows),'raw_divergences':len(raw_div),'excluded':excluded},'architecture_gate':'INSUFFICIENT_EVIDENCE','canonical_effect':False}
    OUT.mkdir(parents=True,exist_ok=True); name=f'SHARED_ROW_TOURNAMENT_WEEKLY_{y}-W{w:02d}.json'; (OUT/name).write_text(json.dumps(report,indent=2,sort_keys=True)+'\n'); (OUT/'LATEST.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    (OUT/'LATEST.md').write_text(f'# Shared Row Tournament Weekly\n\n- Week: `{y}-W{w:02d}`\n- Eligible rows: **{len(rows)}**\n- Divergences: **{len(div)}**\n- Matured 24h / 72h / 7d: **{mats["24h"]} / {mats["72h"]} / {mats["7d"]}**\n- Architecture gate: `INSUFFICIENT_EVIDENCE`\n\nNo narrative winner is permitted before prospective evidence can support it.\n')
    print(json.dumps({'status':'PASS','report':str(OUT/name),'eligible_rows':len(rows),'divergences':len(div)},sort_keys=True))
if __name__=='__main__':main()
