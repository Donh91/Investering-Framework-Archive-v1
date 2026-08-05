from __future__ import annotations

import argparse,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from typing import Any,Iterable
UTC=timezone.utc
SEVERITY={'GREEN':0,'AMBER':1,'UNKNOWN':1,'RED':2}

def parse_time(value:Any):
    if isinstance(value,(int,float)):return datetime.fromtimestamp(value,UTC)
    if not isinstance(value,str) or not value:return None
    try:return datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(UTC)
    except ValueError:return None
def read_json(path:Path):
    if not path.exists():return None,'MISSING'
    try:value=json.loads(path.read_text(encoding='utf-8'))
    except (OSError,json.JSONDecodeError):return None,'INVALID_JSON'
    return (value,None) if isinstance(value,dict) else (None,'INVALID_SHAPE')
def sha256_path(path):return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() and path.is_file() else None
def first_time(obj,keys:Iterable[str]):
    if not obj:return None
    for key in keys:
        stamp=parse_time(obj.get(key))
        if stamp:return stamp
    return None
def normalized_status(value):
    x=str(value or 'UNKNOWN').upper()
    if x in {'GREEN','AMBER','RED'}:return x
    if x in {'PASS','READY','COMPLETE','DURABLE_PASS','SUCCESS','SKIPPED_NO_DELTA','SKIPPED_NO_ELIGIBLE_INPUT'}:return 'GREEN'
    if x in {'PARTIAL','DEGRADED','PENDING','UNKNOWN','RECOVERING','UNAVAILABLE'}:return 'AMBER'
    if x in {'FAIL','FAILED','BLOCKED','SOURCE_UNAVAILABLE'}:return 'RED'
    return 'UNKNOWN'
def combine_status(*values):return max(values,key=lambda v:SEVERITY.get(v,1))
def freshness(timestamp,reference,green_hours,red_hours):
    if timestamp is None:return 'UNKNOWN','TIMESTAMP_UNAVAILABLE',None
    age=round(max(0.0,(reference-timestamp).total_seconds()/3600.0),3)
    if age<=green_hours:return 'GREEN','FRESH',age
    if age<=red_hours:return 'AMBER','DELAYED',age
    return 'RED','STALE',age
def pointer_entry(root,pointer):
    if not isinstance(pointer,dict):return {'path':None,'declared_sha256':None,'actual_sha256':None,'hash_status':'UNKNOWN'}
    rel=pointer.get('path') if isinstance(pointer.get('path'),str) else None;actual=sha256_path(root/rel) if rel else None;declared=pointer.get('sha256') if isinstance(pointer.get('sha256'),str) else None
    state='MISSING' if actual is None else 'UNDECLARED' if declared is None else 'MATCH' if actual==declared else 'MISMATCH'
    return {'path':rel,'declared_sha256':declared,'actual_sha256':actual,'hash_status':state}
def pointer_object(root,pointer):
    if not pointer.get('path'):return None
    return read_json(root/pointer['path'])[0]
def hash_status(pointer):return 'GREEN' if pointer['hash_status']=='MATCH' else 'RED' if pointer['hash_status']=='MISMATCH' else 'AMBER'
def paired_director_receipt(root,pointer):
    rel=pointer.get('path')
    if not isinstance(rel,str):return None,None
    output=root/rel
    for path in (output.with_name('DAILY_DIRECTOR_RECEIPT.json'),output.with_name('receipt.json')):
        value,error=read_json(path)
        if value is not None:return value,str(path.relative_to(root))
        if error not in {None,'MISSING'}:return None,str(path.relative_to(root))
    return None,None
def receipt_time(data):return first_time(data,('completed_at_utc','created_at_utc','generated_at_utc','timestamp_utc','created_unix'))
def is_api_receipt(path,data):return 'API_AGENT_RECEIPT' in str(data.get('contract') or '') or path.name.endswith('RECEIPT.json') or path.name=='receipt.json'
def collect_api_usage(root,reference):
    month=reference.strftime('%Y-%m');count=input_tokens=output_tokens=0;cost=0.0;latest=None;seen=set()
    for base in (root/'research/api_agent/outputs',root/'research/api_agent/receipts'):
        for path in base.rglob('*.json') if base.exists() else []:
            data,error=read_json(path)
            if error or data is None or not is_api_receipt(path,data):continue
            identity=str(data.get('response_id') or data.get('request_hash') or data.get('output_hash') or path)
            if identity in seen:continue
            seen.add(identity);stamp=receipt_time(data)
            if stamp and (latest is None or stamp>latest[0]):latest=(stamp,path,data)
            if not stamp or stamp.strftime('%Y-%m')!=month:continue
            count+=1
            try:cost+=float(data.get('cost_usd',data.get('estimated_cost_usd',0)) or 0)
            except (TypeError,ValueError):pass
            usage=data.get('usage') if isinstance(data.get('usage'),dict) else {}
            try:input_tokens+=int(usage.get('input_tokens',data.get('input_tokens',0)) or 0);output_tokens+=int(usage.get('output_tokens',data.get('output_tokens',0)) or 0)
            except (TypeError,ValueError):pass
    row=None
    if latest:row={'path':str(latest[1].relative_to(root)),'completed_at_utc':latest[0].isoformat().replace('+00:00','Z'),'status':latest[2].get('status'),'model':latest[2].get('model'),'task':latest[2].get('task',latest[2].get('task_id')),'cost_usd':latest[2].get('cost_usd',latest[2].get('estimated_cost_usd'))}
    return {'month':month,'receipt_count':count,'cost_usd':round(cost,6),'input_tokens':input_tokens,'output_tokens':output_tokens,'latest':row}
def direct_system(root,path,contract,green_hours,red_hours,reference,missing_reason):
    value,error=read_json(root/path)
    if error:return {'status':'AMBER' if error=='MISSING' else 'RED','reason':missing_reason if error=='MISSING' else error,'path':str(path),'timestamp_utc':None,'age_hours':None},value
    stamp=first_time(value,('generated_at_utc','created_at_utc','completed_at_utc'));fresh,reason,age=freshness(stamp,reference,green_hours,red_hours)
    semantic='GREEN' if value.get('contract')==contract else 'RED'
    return {'status':combine_status(fresh,semantic),'reason':reason if semantic=='GREEN' else 'INVALID_CONTRACT','path':str(path),'timestamp_utc':stamp.isoformat().replace('+00:00','Z') if stamp else None,'age_hours':age},value
def build_dashboard(repo_root,reference=None):
    reference=reference or datetime.now(UTC);handoff,handoff_error=read_json(repo_root/'LATEST_HANDOFF.json');automation,automation_error=read_json(repo_root/'research/architecture_health/LATEST_AUTOMATION_HEALTH.json');architecture,architecture_error=read_json(repo_root/'research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json');pointers=handoff.get('pointers',{}) if handoff else {}
    capture_pointer=pointer_entry(repo_root,pointers.get('latest_capture'));director_pointer=pointer_entry(repo_root,pointers.get('latest_director_output'));weekly_pointer=pointer_entry(repo_root,pointers.get('latest_weekly_output'));capture=pointer_object(repo_root,capture_pointer);director=pointer_object(repo_root,director_pointer);weekly=pointer_object(repo_root,weekly_pointer);director_receipt,director_receipt_path=paired_director_receipt(repo_root,director_pointer)
    capture_time=first_time(capture,('captured_at_utc','snapshot_utc','generated_at_utc','created_at_utc'));director_time=first_time(director,('completed_at_utc','generated_at_utc','created_at_utc','captured_at_utc')) or receipt_time(director_receipt);weekly_time=first_time(weekly,('completed_at_utc','generated_at_utc','created_at_utc','freeze_recorded_at_utc','published_at_utc'))
    capture_fresh,capture_reason,capture_age=freshness(capture_time,reference,8,16);director_fresh,director_reason,director_age=freshness(director_time,reference,12,30);weekly_fresh,weekly_reason,weekly_age=freshness(weekly_time,reference,24*8,24*15)
    semantic_source=(director_receipt or {}).get('status') or (director or {}).get('status');director_semantic=normalized_status(semantic_source)
    if str(semantic_source or '').upper()=='SKIPPED_NO_DELTA':director_semantic='GREEN';director_reason='EXPECTED_SKIP_NO_COMPARABLE_DELTA'
    elif str(semantic_source or '').upper()=='SKIPPED_NO_ELIGIBLE_INPUT':director_semantic='GREEN';director_reason='EXPECTED_SKIP_NO_ELIGIBLE_INPUT'
    experiment_system,experiment=direct_system(repo_root,Path('research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json'),'EXPERIMENT_LIFECYCLE_REGISTRY_v1',36,72,reference,'NO_EXPERIMENT_REGISTRY_YET')
    sync_system,sync=direct_system(repo_root,Path('research/experiment_lifecycle/LATEST_EXPERIMENT_RECEIPT_SYNC.json'),'EXPERIMENT_RECEIPT_SYNC_v1',48,96,reference,'NO_EXPERIMENT_RECEIPT_SYNC_YET')
    if sync and sync.get('status')=='UNAVAILABLE':sync_system['status']='AMBER';sync_system['reason']='EXECUTION_PLANE_UNAVAILABLE'
    if sync and sync.get('status')=='FAIL':sync_system['status']='RED';sync_system['reason']='RECEIPT_SYNC_FAILED'
    remediation_system,remediation=direct_system(repo_root,Path('research/remediation/LATEST_REMEDIATION_QUEUE.json'),'REMEDIATION_MATURATION_ENGINE_v1',18,36,reference,'NO_REMEDIATION_QUEUE_YET')
    systems={'daily_capture':{'status':combine_status(capture_fresh,hash_status(capture_pointer)),'reason':capture_reason,'age_hours':capture_age,'timestamp_utc':capture_time.isoformat().replace('+00:00','Z') if capture_time else None,'pointer':capture_pointer},'openai_daily_director':{'status':combine_status(director_fresh,hash_status(director_pointer),director_semantic),'reason':director_reason,'age_hours':director_age,'timestamp_utc':director_time.isoformat().replace('+00:00','Z') if director_time else None,'semantic_status':semantic_source,'pointer':director_pointer,'receipt_path':director_receipt_path},'weekly_output':{'status':combine_status(weekly_fresh,hash_status(weekly_pointer)),'reason':weekly_reason,'age_hours':weekly_age,'timestamp_utc':weekly_time.isoformat().replace('+00:00','Z') if weekly_time else None,'pointer':weekly_pointer},'automation_health':{'status':normalized_status(automation.get('status') if automation else None),'generated_at_utc':automation.get('generated_at_utc') if automation else None,'red_count':automation.get('red_count') if automation else None,'amber_count':automation.get('amber_count') if automation else None,'blockers':automation.get('blockers',[]) if automation else [],'input_error':automation_error},'architecture_health':{'status':normalized_status(architecture.get('status') if architecture else None),'generated_at_utc':architecture.get('generated_at_utc') if architecture else None,'blockers':architecture.get('blockers',[]) if architecture else [],'input_error':architecture_error},'experiment_lifecycle':experiment_system,'experiment_receipt_sync':sync_system,'remediation_maturation':remediation_system}
    actions=[]
    for name,system in systems.items():
        reason=system.get('reason') or system.get('input_error') or system.get('blockers') or 'REQUIRED_INPUT_UNAVAILABLE'
        if system['status']=='RED':actions.append({'priority':'P0','system':name,'reason':reason})
        elif system['status'] in {'AMBER','UNKNOWN'}:actions.append({'priority':'P1','system':name,'reason':reason})
    actions.sort(key=lambda row:(row['priority'],row['system']));overall='GREEN'
    for system in systems.values():overall=combine_status(overall,system['status'])
    dispatch=read_json(repo_root/'research/experiment_lifecycle/LATEST_EXPERIMENT_DISPATCH_MANIFEST.json')[0] or {}
    dashboard={'contract':'OPERATIONS_DASHBOARD_v1_2','authority':'OPERATIONAL_OBSERVABILITY_ONLY','generated_at_utc':reference.isoformat().replace('+00:00','Z'),'overall_status':overall,'source_status':{'latest_handoff':handoff_error or 'PASS','automation_health':automation_error or 'PASS','architecture_health':architecture_error or 'PASS'},'systems':systems,'agent_activity':{'openai_api':collect_api_usage(repo_root,reference),'pending_forecast_candidates':len(handoff.get('pending_forecast_candidates',[])) if handoff else 0,'experiments':{'candidate_count':(experiment or {}).get('candidate_count',0),'state_counts':(experiment or {}).get('state_counts',{}),'dispatch_request_count':dispatch.get('request_count',0)},'remediation':{'codex_ready':((remediation or {}).get('summary') or {}).get('codex_ready',0),'needs_more_evidence':((remediation or {}).get('summary') or {}).get('needs_more_evidence',0),'automatic_code_write':(remediation or {}).get('automatic_code_write',False),'automatic_merge':(remediation or {}).get('automatic_merge',False)}},'incidents':{'open_count':len(handoff.get('open_incidents',[])) if handoff else 0,'paths':handoff.get('open_incidents',[]) if handoff else []},'required_actions':actions}
    canonical=json.dumps(dashboard,sort_keys=True,separators=(',',':')).encode();dashboard['dashboard_sha256']=hashlib.sha256(canonical).hexdigest();return dashboard
def render_markdown(data):
    lines=['# Operations Dashboard','',f"Overall: **{data['overall_status']}**",f"Generated: `{data['generated_at_utc']}`",'','## Systems','','| System | Status | Detail | Age hours |','|---|---:|---|---:|']
    for name,system in data['systems'].items():lines.append(f"| `{name}` | **{system['status']}** | {system.get('reason') or system.get('semantic_status') or '-'} | {system.get('age_hours') if system.get('age_hours') is not None else '-'} |")
    usage=data['agent_activity']['openai_api'];exp=data['agent_activity']['experiments'];rem=data['agent_activity']['remediation'];lines+=['','## AI and learning activity','',f"- OpenAI receipts this month: **{usage['receipt_count']}**",f"- OpenAI cost this month: **${usage['cost_usd']:.6f}**",f"- Pending forecast candidates: **{data['agent_activity']['pending_forecast_candidates']}**",f"- Experiment candidates: **{exp['candidate_count']}**",f"- Experiment dispatch requests: **{exp['dispatch_request_count']}**",f"- Codex-ready remediation tasks: **{rem['codex_ready']}**",f"- Needs-more-evidence items: **{rem['needs_more_evidence']}**",'','## Incidents','',f"Open incident references: **{data['incidents']['open_count']}**",'','## Required actions','']
    lines.extend(f"- **{row['priority']}** `{row['system']}` - {row['reason']}" for row in data['required_actions']) if data['required_actions'] else lines.append('- None')
    lines+=['',f"Dashboard SHA-256: `{data['dashboard_sha256']}`",''];return '\n'.join(lines)
def main():
    p=argparse.ArgumentParser();p.add_argument('--repo-root',type=Path,required=True);p.add_argument('--json-output',type=Path,required=True);p.add_argument('--md-output',type=Path,required=True);p.add_argument('--reference-time');a=p.parse_args();result=build_dashboard(a.repo_root,parse_time(a.reference_time) if a.reference_time else None);a.json_output.parent.mkdir(parents=True,exist_ok=True);a.md_output.parent.mkdir(parents=True,exist_ok=True);a.json_output.write_text(json.dumps(result,sort_keys=True,separators=(',',':'))+'\n');a.md_output.write_text(render_markdown(result));print(json.dumps({'status':result['overall_status'],'dashboard_sha256':result['dashboard_sha256']},sort_keys=True))
if __name__=='__main__':main()
