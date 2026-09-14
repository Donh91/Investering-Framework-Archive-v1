#!/usr/bin/env python3
import argparse, hashlib, json, re
from collections import Counter
from pathlib import Path


def load(p):
    return json.loads(p.read_text())


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def latest_weekly(root):
    files=list(root.glob('research/api_agent/outputs/weekly/*/W*/MASTER_MONDAY_MACHINE_PACKAGE.json'))
    if not files: raise SystemExit('no weekly machine package')
    def key(p):
        m=re.search(r'/([0-9]{4})/W([0-9]{2})/',p.as_posix()); return (int(m.group(1)),int(m.group(2)))
    return max(files,key=key)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); ap.add_argument('--output-root',default='research/framework_intelligence/phase1'); a=ap.parse_args()
    root=Path(a.repo_root); weekly_path=latest_weekly(root); weekly=load(weekly_path)
    year=int(weekly['iso_year']); week=int(weekly['iso_week'])
    adj_rel=Path(f'research/experiment_lifecycle/weekly_adjudication/{year}/W{week:02d}.json'); adj_path=root/adj_rel
    adj=load(adj_path) if adj_path.exists() else None
    actions=(adj or {}).get('candidate_actions',[])
    admission=Counter(x.get('scientific_admission_status','UNKNOWN') for x in actions)
    lifecycle=Counter(x.get('lifecycle_state','UNKNOWN') for x in actions)
    selected=Counter(x.get('selected_action','UNKNOWN') for x in actions)
    duplicates=sum(1 for x in actions if x.get('scientific_admission_status')=='SEMANTIC_DUPLICATE_KEEP_SHADOW')
    qualified=[x for x in actions if x.get('scientific_admission_status')=='QUALIFIED_FOR_FORWARD_TEST']
    ranges=[x for x in qualified if ' RANGE' in x.get('title','').upper()]
    supported_ranges=[x for x in ranges if x.get('lifecycle_state')=='MATURED_SUPPORTED']
    pkg_reg=((weekly.get('scorecard') or {}).get('experiment_registry_status'))
    pkg_status=((weekly.get('scorecard') or {}).get('status'))
    contradictions=[]
    if adj and pkg_status=='UNAVAILABLE_EXPERIMENT_REGISTRY':
        contradictions.append('WEEKLY_PACKAGE_REGISTRY_UNAVAILABLE_BUT_MATCHING_ADJUDICATION_EXISTS')
    if pkg_reg=='AVAILABLE' and pkg_status=='UNAVAILABLE_EXPERIMENT_REGISTRY':
        contradictions.append('WEEKLY_PACKAGE_SCORECARD_INTERNAL_REGISTRY_STATUS_CONTRADICTION')
    consultation=[]
    if supported_ranges:
        consultation.append({'type':'RANGE_CONTEXT','note':f'{len(supported_ranges)} qualified RANGE candidate(s) are MATURED_SUPPORTED; remain shadow-only and replication/adversarial gates still apply.'})
    if duplicates:
        consultation.append({'type':'WEEKLY_ANALYSIS_CONTEXT','note':f'{duplicates} semantic duplicates excluded from independent-support interpretation.'})
    if contradictions:
        consultation.append({'type':'CONTRADICTION_CONTEXT','note':'Matching shadow evidence exposes an information-utilization inconsistency in the weekly package.'})
    if not consultation:
        consultation=[{'type':'NO_MATERIAL_LEARNING','note':'No bounded consultation context materially changes interpretation.'}]
    out={
      'contract':'FRAMEWORK_INTELLIGENCE_PHASE1_LIVE_SHADOW_v1','authority':'RESEARCH_ONLY_SHADOW','iso_year':year,'iso_week':week,
      'live_master_monday_influence':False,'cycle_navigator_influence':False,'canonical_promotion':False,'portfolio_authority':False,
      'sources':{
        'weekly_machine_package':{'path':weekly_path.relative_to(root).as_posix(),'sha256':sha256(weekly_path),'created_at_utc':weekly.get('created_at_utc'),'package_sha256':weekly.get('package_sha256'),'freeze_sha256':weekly.get('freeze_sha256')},
        'matching_weekly_adjudication':{'path':adj_rel.as_posix(),'available':bool(adj),'sha256':sha256(adj_path) if adj else None,'generated_at_utc':(adj or {}).get('generated_at_utc')}
      },
      'experiment_memory':{
        'raw_candidate_count':len(actions),'semantic_duplicate_count':duplicates,'duplicate_adjusted_qualified_count':len(qualified),
        'scientific_admission_counts':dict(sorted(admission.items())),'lifecycle_counts':dict(sorted(lifecycle.items())),'selected_action_counts':dict(sorted(selected.items()))
      },
      'range_lab':{
        'qualified_range_family_count':len(ranges),'matured_supported_range_count':len(supported_ranges),
        'supported_range_candidates':[{'candidate_id':x.get('candidate_id'),'title':x.get('title'),'matured_outcome_count':x.get('matured_outcome_count'),'replication_receipts':x.get('replication_receipts',[])} for x in supported_ranges],
        'forecast_skill_claim':'UNPROVEN','canonical_effect':False
      },
      'weekly_package_registry_report':{'experiment_registry_status':pkg_reg,'scorecard_status':pkg_status},
      'contradictions':contradictions,'consultation':consultation,'would_offer_to_master_monday':True,'live_consumed':False,
      'scientific_firewall':{'status':'PASS','forecast_skill':'UNPROVEN','confirmatory_promotion':False},
      'phase1_observation_state':'OBSERVED'
    }
    out_root=root/a.output_root/str(year)/f'W{week:02d}'; out_root.mkdir(parents=True,exist_ok=True)
    dest=out_root/'LIVE_PARALLEL_SHADOW.json'; dest.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    latest=root/a.output_root/'LATEST.json'; latest.parent.mkdir(parents=True,exist_ok=True); latest.write_bytes(dest.read_bytes())
    print(dest)

if __name__=='__main__': main()
