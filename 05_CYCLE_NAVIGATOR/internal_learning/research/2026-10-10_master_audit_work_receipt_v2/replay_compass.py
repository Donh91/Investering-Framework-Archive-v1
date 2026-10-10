#!/usr/bin/env python3
"""One-shot read-only audit. No runtime imports, writes only to explicit output dir."""
import argparse, csv, hashlib, json, subprocess
from pathlib import Path
from collections import Counter
from datetime import datetime, timedelta

def stamp(s):
    return datetime.fromisoformat(s.replace('Z','+00:00')) if s else None

def digest(d,key):
    b=(json.dumps({k:v for k,v in d.items() if k!=key},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)+'\n').encode()
    return hashlib.sha256(b).hexdigest()

def run(root,out):
    base=root/'04_MARKET_LEARNING/handlekompas/official'
    freezes={}
    for p in sorted((base/'daily').rglob('*.json')):
        d=json.loads(p.read_text()); freezes[d['compass_id']]=(p,d)
    outcomes={}
    for p in sorted((base/'outcomes').rglob('*.json')):
        d=json.loads(p.read_text()); outcomes[d['compass_id'],d['horizon']]=(p,d)
    hourly={}
    for p in sorted((root/'03_DAILY_CAPTURE_LOGS/hourly/2026').rglob('*.csv')):
        if '2026-09-' not in p.name and '2026-10-' not in p.name: continue
        for d in csv.DictReader(p.open(encoding='utf-8-sig')):
            opened=stamp(d.get('timestamp_utc'))
            if opened: hourly.setdefault(opened,[]).append((stamp(d.get('source_window_end_utc')) or opened+timedelta(hours=1),d,str(p.relative_to(root))))
    rows=[]; counts=Counter(); by_score=Counter(); mismatch=[]; persistence_pairs=[]
    for cid,(fp,f) in freezes.items():
        hash_ok=digest(f,'compass_sha256')==f.get('compass_sha256')
        counts['freeze_hash_pass' if hash_ok else 'freeze_hash_fail']+=1
        for h,k in [('12h','NEXT_12H'),('72h','NEXT_1_3D'),('168h','NEXT_5_7D')]:
            op,o=outcomes.get((cid,h),(None,{})); call=f.get('horizons',{}).get(k,{})
            tb=o.get('time_basis',{}); a=o.get('action_utility',{}); ref=f.get('market_reference',{})
            row=dict(compass_id=cid,horizon=h,source_path=str(fp.relative_to(root)),source_file_sha256=hashlib.sha256(fp.read_bytes()).hexdigest(),payload_hash_pass=hash_ok,issued_at_utc=f.get('issued_at_utc'),bound_main_sha=f.get('bound_main_sha'),method_version=f.get('decision_policy_version'),source_class='UNTESTABLE',source_form='FROZEN_OFFICIAL_ARTIFACT',temporal_admission='PENDING_KNOWLEDGE_TIME',original_publication_time='UNKNOWN',eligible_knowledge_time='UNKNOWN',predicted=call.get('expected_direction'),action=call.get('action_posture'),outcome_path=str(op.relative_to(root)) if op else '',outcome_status='MATURED_ARTIFACT' if o else 'NO_OUTCOME_AT_SNAPSHOT',scoring_contract=o.get('scoring_contract'),start_reference_at_utc=tb.get('start_reference_at_utc'),target_at_utc=o.get('target_at_utc'),target_observation_at_utc=o.get('target_observation_at_utc'),matured_at_utc=o.get('matured_at_utc'),btc_result=o.get('direction_accuracy',{}).get('btc',{}).get('result'),eth_result=o.get('direction_accuracy',{}).get('eth',{}).get('result'),btc_return_pct=o.get('realized',{}).get('btc_return_pct'),eth_return_pct=o.get('realized',{}).get('eth_return_pct'),action_proxy=a.get('result'),hold_protective_mislabel=a.get('action')=='HOLD' and a.get('result')=='PROTECTIVE',effective_window_hours=tb.get('effective_window_hours'),independent_event_family='NOT_ASSIGNED',economic_edge_status='NOT_ESTABLISHED')
            if not o:
                start=stamp(ref.get('source_window_end_utc'))
                if start is None and ref.get('observation_open_utc'): start=stamp(ref['observation_open_utc'])+timedelta(hours=1)
                due=start+timedelta(hours=int(h[:-1])) if start else None
                row['reference_due_at_utc']=due.isoformat() if due else ''
                row['missing_outcome_class']='PAST_REFERENCE_HORIZON_NOT_CAUSALLY_DIAGNOSED' if due and due<=stamp('2026-10-10T17:20:34Z') else 'NOT_DUE_OR_UNKNOWN'
                counts['missing_'+row['missing_outcome_class']]+=1
            if o:
                counts['outcome_hash_pass' if digest(o,'outcome_sha256')==o.get('outcome_sha256') else 'outcome_hash_fail']+=1
                counts['freeze_binding_pass' if o.get('compass_sha256')==f.get('compass_sha256') else 'freeze_binding_fail']+=1
                legacy=o.get('scoring_contract')=='OFFICIAL_DAILY_COMPASS_SCORING_v1'
                candidates=hourly.get(stamp(o.get('target_observation_at_utc') if legacy else o.get('target_observation_open_at_utc')),[])
                if not legacy: candidates=[x for x in candidates if x[0]==stamp(o.get('target_observation_at_utc'))]
                row['endpoint_time_semantics']='LEGACY_OPEN_TIMESTAMP_NOT_CLOSE' if legacy else 'V2_EXPLICIT_CLOSE'
                ok=[]
                for close,t,path in candidates:
                    check=True
                    for asset in ['btc','eth']:
                        start=ref.get(asset+'_usdt'); end=t.get(asset+'_close'); expected=o.get('realized',{}).get(asset+'_return_pct')
                        actual=(float(end)/start-1)*100 if start and end else None
                        check=check and actual is not None and expected is not None and abs(actual-expected)<1e-8
                    ok.append(check)
                row['endpoint_return_replay']='PASS' if any(ok) else 'FAIL_OR_SOURCE_UNAVAILABLE'
                counts['endpoint_return_'+row['endpoint_return_replay']]+=1
                if not any(ok): mismatch.append(dict(compass_id=cid,horizon=h,candidate_rows=len(candidates)))
                for asset in ['btc','eth']:
                    result=o.get('direction_accuracy',{}).get(asset,{}).get('result')
                    pred=call.get('expected_direction'); realized=o.get('realized',{}).get(asset+'_return_pct')
                    expected='ABSTAINED' if pred in [None,'MIXED','NO_EDGE','UNAVAILABLE'] else ('UNAVAILABLE' if realized is None else ('CORRECT' if (realized>0 if pred=='UP' else realized<0 if pred=='DOWN' else abs(realized)<={'12h':1.5,'72h':3,'168h':5}[h]) else 'INCORRECT'))
                    counts['direction_replay_pass' if result==expected else 'direction_replay_fail']+=1
                    by_score[(o.get('scoring_contract','LEGACY_UNVERSIONED'),h,asset,call.get('expected_direction'),result)]+=1
                pred=call.get('expected_direction'); actual=o.get('realized',{}).get('btc_return_pct')
                prior=next((x.get('value') for x in f.get('evidence_snapshot',{}).get('selected_features',[]) if x.get('feature_id')=='btc_delta_since_prior_packet_pct'),None)
                if pred in ['UP','DOWN'] and isinstance(prior,(int,float)) and prior!=0 and actual is not None:
                    naive='UP' if prior>0 else 'DOWN'
                    persistence_pairs.append(dict(compass_id=cid,horizon=h,scoring_contract=o.get('scoring_contract'),method_version=f.get('decision_policy_version'),forecast_prediction=pred,baseline_prediction=naive,framework_correct=(actual>0 if pred=='UP' else actual<0),baseline_correct=(actual>0 if naive=='UP' else actual<0)))
            rows.append(row)
    out.mkdir(parents=True,exist_ok=True)
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with (out/'modern_forecast_population.csv').open('w',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=fields);w.writeheader();w.writerows(rows)
    summary=dict(source_commit=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),freezes=len(freezes),forecast_horizon_rows=len(rows),matured_outcomes=len(outcomes),missing_outcome_rows=len(rows)-len(outcomes),hold_protective_mislabels=sum(r['hold_protective_mislabel'] for r in rows),counts=dict(counts),score_strata=[dict(scoring_contract=k[0],horizon=k[1],asset=k[2],prediction=k[3],result=k[4],rows=v) for k,v in sorted(by_score.items(),key=lambda kv:str(kv[0]))],endpoint_mismatches=mismatch,limitations=['No publication or first-commit knowledge-time admission; self-hash is integrity not temporal proof','Rows overlap and BTC/ETH are correlated; no independent N or statistical edge claimed','Endpoint prices replayed from current pinned hourly files, not original source vintages','No position execution, fees, sellability, re-entry or economic comparator replay','Legacy forecasts and 24h/48h/2-3w/4-8w not covered'])
    summary['direction_persistence_pairs']=persistence_pairs
    summary['limitations'].append('Paired persistence comparison conditional on UP/DOWN and available nonzero frozen prior delta; descriptive only, not matched AI ablation or statistical edge')
    (out/'modern_population_receipt.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ['score_strata','endpoint_mismatches','limitations','direction_persistence_pairs']}));print('endpoint_mismatches',len(mismatch))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('repo',type=Path);p.add_argument('out',type=Path);a=p.parse_args();run(a.repo,a.out)
