#!/usr/bin/env python3
"""Reproduce an exposed original-cohort B2 diagnostic, never an R2 release.

Inputs stay local. Output contains original object identities, clocks, counts and
equality flags only. No raw prices, provider values, returns or new predictions.
The cohort, comparator and outcomes were already exposed in October14/16 files.
"""
import argparse
import hashlib
import json
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path

PIN='098c50d36b222c4c8ffa179a5879d36a74194bc4'
SOURCE_RESULT_SHA='d39a2e71a66138c9cfadaf84348db3f2fb66d82280175a2544c8826ccd9fa939'
EXPLORATORY='04_MARKET_LEARNING/handlekompas/research/2026-10-14__TASK2_R1_EXPLORATORY_BASELINE_AND_SIMULATION_RELEASE_v1.json'
EXPLORATORY_BLOB='656c2c9db472ba7f42a548bb932e244d93ca5890'

def need(ok, message):
    if not ok: raise ValueError(message)

def blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()

def canonical_hash(d, field):
    payload=(json.dumps({k:v for k,v in d.items() if k!=field},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)+'\n').encode()
    return hashlib.sha256(payload).hexdigest()

def utc(t): return datetime.fromisoformat(t.replace('Z','+00:00'))
def sign(x): return 'UP' if x>0 else 'DOWN' if x<0 else 'ABSTAIN'

def git_member(repo, path):
    p=subprocess.run(['git','--no-replace-objects','-C',str(repo),'ls-tree','-r','--format=%(objectname)',PIN,'--',path],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
    need(p.returncode==0,'FROZEN_GIT_TREE_UNAVAILABLE')
    found=p.stdout.decode().splitlines()
    need(len(found)<=1,'AMBIGUOUS_FROZEN_GIT_MEMBERSHIP')
    return found[0] if found else None

def run(root, repo, source):
    raw=source.read_bytes()
    need(hashlib.sha256(raw).hexdigest()==SOURCE_RESULT_SHA,'SOURCE_AUDIT_RESULT_CHANGED')
    audit=json.loads(raw);need(audit['summary']['original_forecasts']==11,'WRONG_ATTEMPT_COHORT')
    r=(repo/EXPLORATORY).read_bytes();need(blob(r)==EXPLORATORY_BLOB,'EXPOSED_COHORT_DEFINITION_CHANGED')
    originals=json.loads(r)['measured_exploratory_population']['source_rows']
    need(len(originals)==9,'ORIGINAL_OUTCOME_DENOMINATOR_CHANGED')
    indexed={x['id']:x for x in originals}
    rows=[];totals=Counter();intervals=[]
    for audited in audit['rows']:
        fid=audited['forecast_id'];fraw=(root/(fid+'.json')).read_bytes();f=json.loads(fraw)
        need(f['compass_id']==fid and canonical_hash(f,'compass_sha256')==f['compass_sha256'],'FORECAST_IDENTITY_FAILURE')
        date_path=f['issued_at_utc'][:10].replace('-','/')
        forecast_path='04_MARKET_LEARNING/handlekompas/official/daily/'+date_path+'/'+fid+'.json'
        outcome_path='04_MARKET_LEARNING/handlekompas/official/outcomes/'+date_path+'/'+fid+'_12h.json'
        need(git_member(repo,forecast_path)==blob(fraw),'FROZEN_FORECAST_GIT_MEMBERSHIP_MISMATCH')
        eligible=audited['scope_specific_source_chain_complete']
        row={'forecast_id':fid,'scoped_source_chain_complete':eligible,'full_R1_admitted':False,'forecast_git_blob':blob(fraw),'issued_at_utc':f['issued_at_utc']}
        if fid not in indexed:
            need(git_member(repo,outcome_path) is None,'ORIGINAL_ABSENCE_NOT_CONFIRMED')
            row['original_outcome_status']='ABSENT_AT_FROZEN_SNAPSHOT'
            totals['original_outcomes_absent']+=1
            rows.append(row);continue
        original=indexed[fid];need(blob(fraw)==original['original_forecast_git_blob'],'FROZEN_FORECAST_BLOB_MISMATCH')
        oraw=(root/(fid+'_12h.json')).read_bytes();o=json.loads(oraw)
        need(blob(oraw)==original['original_outcome_git_blob'],'FROZEN_OUTCOME_BLOB_MISMATCH')
        need(git_member(repo,original['original_outcome_path'])==blob(oraw),'FROZEN_OUTCOME_GIT_MEMBERSHIP_MISMATCH')
        need(canonical_hash(o,'outcome_sha256')==o['outcome_sha256'],'OUTCOME_CONTENT_DIGEST_MISMATCH')
        need(o['compass_id']==fid and o['compass_sha256']==f['compass_sha256'],'OUTCOME_FORECAST_IDENTITY_MISMATCH')
        need(o['forecast_path']==original['original_forecast_path'],'OUTCOME_FORECAST_PATH_MISMATCH')
        need(o['scoring_contract']==f['scoring_contract']=='OFFICIAL_DAILY_COMPASS_SCORING_v3','SCORING_VERSION_MISMATCH')
        need(o['horizon']=='12h' and o['issued_at_utc']==f['issued_at_utc'],'ISSUE_HORIZON_MISMATCH')
        need(o['target_at_utc']==o['target_observation_at_utc']==original['target_at_utc'],'TARGET_CLOCK_MISMATCH')
        need(utc(o['matured_at_utc'])>=utc(o['target_at_utc']),'PREMATURE_OUTCOME')
        need(o['time_basis']['nominal_horizon_hours']==12 and o['time_basis']['effective_window_hours']==12,'WINDOW_MISMATCH')
        intervals.append((utc(f['issued_at_utc']),utc(o['target_at_utc'])))
        row.update(original_outcome_status='FROZEN_ORIGINAL_HASH_AND_TARGET_MATCHED',outcome_git_blob=blob(oraw),target_at_utc=o['target_at_utc'])
        totals['original_outcomes_present']+=1
        features={x['feature_id']:x['value'] for x in f['evidence_snapshot']['selected_features']}
        label=f['horizons']['NEXT_12H']['expected_direction']
        count=Counter()
        for asset in ('btc','eth'):
            d=o['direction_accuracy'][asset]
            need(d['predicted']==label,'RECORDED_ORIGINAL_PREDICTION_MISMATCH')
            b2=sign(features[asset+'_delta_since_prior_packet_pct'])
            realized=d['realized_pct'];need(isinstance(realized,(int,float)),'ORIGINAL_REALIZED_OUTCOME_ABSENT')
            if label not in ('UP','DOWN'):
                need(d['result']=='ABSTAINED','ORIGINAL_ABSTENTION_MISMATCH')
                count['original_abstained_slots']+=1
            else:
                model_correct=(realized>0 if label=='UP' else realized<0)
                need(d['result']==('CORRECT' if model_correct else 'INCORRECT') and d['correct']==model_correct,'ORIGINAL_RECORDED_SCORE_MISMATCH')
                count['all_original_nonabstained_slots']+=1
                if eligible and b2!='ABSTAIN':
                    count['matched_slots']+=1
                    count['direction_equal_slots']+=int(label==b2)
                    count['model_correct_slots']+=int(model_correct)
                    count['B2_correct_slots']+=int(realized>0 if b2=='UP' else realized<0)
        row['counts']=dict(count)
        totals.update(count)
        rows.append(row)
    need(len(rows)==11 and totals['original_outcomes_present']==9 and totals['original_outcomes_absent']==2,'ATTEMPT_RECONCILIATION_FAILED')
    merged=[]
    for start,end in sorted(intervals):
        if merged and start<=merged[-1][1]:merged[-1]=(merged[-1][0],max(end,merged[-1][1]))
        else:merged.append((start,end))
    return {'contract':'TASK2_SCOPED_ORIGINAL_12H_B2_DEVELOPMENT_REPRODUCTION_v1','classification':'EXPOSED_DEVELOPMENT_ONLY_NOT_CERTIFIED_R2_OR_HOLDOUT',
        'frozen_original_snapshot':PIN,'source_audit_result_sha256':SOURCE_RESULT_SHA,'exposed_cohort_definition_git_blob':EXPLORATORY_BLOB,
        'baseline':'B2_SIGN_OF_ORIGINAL_PRIOR_PACKET_DELTA_ZERO_ABSTAINS','matching':'SAME_ASSET_ISSUANCE_ORIGINAL_12H_TARGET_OBSERVATION',
        'original_attempts':11,'scope_specific_source_complete_attempts':sum(x['scoped_source_chain_complete'] for x in rows),
        'counts':dict(totals),'paired_correctness_count_lift':totals['model_correct_slots']-totals['B2_correct_slots'],
        'connected_overlap_blocks_in_nine_target_bound_rows':len(merged),'certified_independent_market_event_families':None,
        'confidence_interval':'NOT_ESTIMABLE_FROM_ONE_EXPOSED_DEPENDENT_BLOCK','untouched_holdout':False,
        'new_preregistration_before_outcome_exposure':False,'generalizable_information_edge_established':False,
        'R2_release_or_original_R1_ledger_change':False,'investor_delivery_fills_costs_or_economics_verified':False,'rows':rows}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--evidence-root',type=Path,required=True);p.add_argument('--repo-root',type=Path,required=True)
    p.add_argument('--source-result',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    try:d=run(a.evidence_root,a.repo_root,a.source_result)
    except Exception as e:
        print(json.dumps({'status':'FAIL','check':str(e) if isinstance(e,ValueError) else type(e).__name__}));raise SystemExit(1)
    a.out.write_text(json.dumps(d,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':'PASS_EXPOSED_DEVELOPMENT_REPRODUCTION','counts':d['counts'],'paired_lift':d['paired_correctness_count_lift'],'overlap_blocks':d['connected_overlap_blocks_in_nine_target_bound_rows']}))

if __name__=='__main__': main()
