#!/usr/bin/env python3
"""Prospective shared-row ingestion + divergence freeze.

This script never defines market semantics. It only accepts a row whose family transforms
and candidate decisions were already produced under merged READY contracts. Missing is
never zero. Rows and divergences are append-only by identity/provenance.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path("06_RESEARCH_LAB/shared_row_model_tournament_v1")
LEDGER=ROOT/"data/PROSPECTIVE_SHARED_ROW_LEDGER.csv"
FNP=ROOT/"14_DIVERGENCE_FNP_LEDGER.csv"
FREEZE=ROOT/"TRANSFORM_FREEZE_REGISTRY.json"
REG=ROOT/"03_CANDIDATE_REGISTRY.json"

def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def load_json(p): return json.loads(p.read_text(encoding='utf-8'))
def rows(p):
    if not p.exists(): return []
    with p.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def append(p,row):
    with p.open(newline='',encoding='utf-8-sig') as f: fields=next(csv.reader(f))
    with p.open('a',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); w.writerow({k:row.get(k,'') for k in fields})
def ready(fr,family_id):
    x=fr.get(family_id,{})
    return x.get('status')=='READY' and x.get('candidate_decision_contract_status')=='READY'
def eligible_candidates():
    freeze=load_json(FREEZE); fr={x['family_id']:x for x in freeze['families']}; out=[]
    registry=load_json(REG)['candidates']
    core_rule=freeze.get('core_activation_rule',{})
    core_ids=set(core_rule.get('candidates',[]))
    core_families=core_rule.get('start_only_when',[])
    core_ready=bool(core_families) and all(ready(fr,x) for x in core_families)
    for c in registry:
        cid=c['id']
        if cid in core_ids:
            if core_ready: out.append(cid)
            continue
        fam=c.get('families')
        # Dynamic challengers and Full Stack require a separately frozen dynamic/base decision contract.
        if fam is None or isinstance(fam,str):
            continue
        if all(ready(fr,x) for x in fam): out.append(cid)
    return out

def validate_payload(r):
    required=['event_id','observation_timestamp_utc','information_cutoff_utc','source_version_commit','regime_tag','catalyst_tag','catalyst_evidence_id','candidate_decisions']
    missing=[k for k in required if not str(r.get(k,'')).strip()]
    if missing: raise ValueError('missing required fields: '+','.join(missing))
    if r['information_cutoff_utc']>r['observation_timestamp_utc']: raise ValueError('information cutoff after observation')
    decisions=r['candidate_decisions'] if isinstance(r['candidate_decisions'],dict) else json.loads(r['candidate_decisions'])
    eligible=set(eligible_candidates())
    illegal=sorted(set(decisions)-eligible)
    if illegal: raise ValueError('decision supplied for non-eligible candidate: '+','.join(illegal))
    if not decisions: raise ValueError('no eligible candidate decisions supplied')
    r=dict(r); r['candidate_decisions']=canon(decisions)
    for k,v in r.items():
        if k.endswith('_missing') and str(v).lower() in {'true','1','yes'}:
            prefix=k[:-8]
            for rk,rv in r.items():
                if rk.startswith(prefix) and rk!=k and str(rv).strip()=='0': raise ValueError(f'missing family {prefix} encoded as zero')
    r['provenance_hash']=hashlib.sha256(canon({k:v for k,v in r.items() if k!='provenance_hash'}).encode()).hexdigest()
    return r,decisions

def ingest(path):
    r,decisions=validate_payload(load_json(path))
    if any(x['event_id']==r['event_id'] for x in rows(LEDGER)): raise ValueError('event_id already frozen')
    append(LEDGER,r)
    ids=sorted(decisions); existing={x['divergence_id'] for x in rows(FNP)}; n=0
    for i,a in enumerate(ids):
        for b in ids[i+1:]:
            if str(decisions[a])==str(decisions[b]): continue
            did=f"{r['event_id']}__{a}__vs__{b}"
            if did in existing: continue
            d={'divergence_id':did,'event_id':r['event_id'],'observation_timestamp_utc':r['observation_timestamp_utc'],'information_cutoff_utc':r['information_cutoff_utc'],'candidate_a':a,'candidate_b':b,'decision_a':decisions[a],'decision_b':decisions[b],'divergence_frozen_utc':now(),'catalyst_tag':r['catalyst_tag'],'regime_tag':r['regime_tag'],'provenance_hash':hashlib.sha256((r['provenance_hash']+did).encode()).hexdigest()}
            append(FNP,d); n+=1
    return {'status':'PASS','event_id':r['event_id'],'eligible_candidates':ids,'divergences_frozen':n,'provenance_hash':r['provenance_hash']}
def status():
    ec=eligible_candidates(); rr=rows(LEDGER); dd=rows(FNP)
    return {'status':'PASS','eligible_candidates':ec,'eligible_row_n':len(rr),'divergence_n':len(dd),'ingestion_ready':bool(ec),'note':'No market semantics are implemented here.'}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--ingest-row',type=Path); ap.add_argument('--status-only',action='store_true'); a=ap.parse_args()
    print(json.dumps(ingest(a.ingest_row) if a.ingest_row else status(),indent=2,sort_keys=True))
if __name__=='__main__': main()
