#!/usr/bin/env python3
"""Research-only evaluator. No market transforms or thresholds live here."""
import csv,json

def parse_bool(v):
    if v is None:return None
    s=str(v).strip().lower()
    if s in {'1','true','yes','positive','signal'}:return 1
    if s in {'0','false','no','negative','no_signal'}:return 0
    return None

def ratio(a,b): return None if b==0 else a/b

def confusion(ds,ys):
    tp=fp=tn=fn=0
    for d,y in zip(ds,ys):
        if d is None or y is None:continue
        if d==1 and y==1:tp+=1
        elif d==1:fp+=1
        elif y==0:tn+=1
        else:fn+=1
    return {'n':tp+fp+tn+fn,'tp':tp,'fp':fp,'tn':tn,'fn':fn}

def metrics(c):
    return {**c,'precision':ratio(c['tp'],c['tp']+c['fp']),'recall':ratio(c['tp'],c['tp']+c['fn']),'false_positive_rate':ratio(c['fp'],c['fp']+c['tn']),'false_negative_rate':ratio(c['fn'],c['fn']+c['tp'])}

def validate_row(r):
    if r.get('information_cutoff_utc') and r.get('observation_timestamp_utc') and r['information_cutoff_utc']>r['observation_timestamp_utc']:
        raise ValueError('lookahead cutoff')

def evaluate(rows,candidates,outcome='outcome_24h'):
    for r in rows:validate_row(r)
    ys=[parse_bool(r.get(outcome)) for r in rows]
    decisions={}
    out={}
    for cid in candidates:
        ds=[parse_bool(json.loads(r.get('candidate_decisions') or '{}').get(cid)) for r in rows]
        decisions[cid]=ds;out[cid]=metrics(confusion(ds,ys))
    disagreements={}
    for i,a in enumerate(candidates):
        for b in candidates[i+1:]:
            pairs=[(x,y) for x,y in zip(decisions[a],decisions[b]) if x is not None and y is not None]
            disagreements[a+'__vs__'+b]={'n':len(pairs),'rate':None if not pairs else sum(x!=y for x,y in pairs)/len(pairs)}
    return {'metrics':out,'disagreements':disagreements}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('ledger');p.add_argument('registry');p.add_argument('--outcome-field',default='outcome_24h');a=p.parse_args()
    rows=list(csv.DictReader(open(a.ledger,encoding='utf-8')));reg=json.load(open(a.registry,encoding='utf-8'))
    print(json.dumps(evaluate(rows,[c['id'] for c in reg['candidates']],a.outcome_field),indent=2,sort_keys=True))
