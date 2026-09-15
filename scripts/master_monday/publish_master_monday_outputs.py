from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def load(p:Path):return json.loads(p.read_text())
def canon(v:Any)->bytes:return (json.dumps(v,sort_keys=True,separators=(',',':'))+'\n').encode()
def sha(v:Any)->str:return hashlib.sha256(canon(v)).hexdigest()
def parse_time(value:Any):
    if isinstance(value,(int,float)):
        try:return datetime.fromtimestamp(value,timezone.utc)
        except Exception:return None
    if isinstance(value,str):
        try:
            dt=datetime.fromisoformat(value.replace('Z','+00:00'))
            return (dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)
        except Exception:return None
    return None
def semantic_identities(value:Any)->set[str]:
    result:set[str]=set()
    if isinstance(value,dict):
        for key,item in value.items():
            if key=='semantic_identity' and isinstance(item,str) and item:result.add(item)
            else:result.update(semantic_identities(item))
    elif isinstance(value,list):
        for item in value:result.update(semantic_identities(item))
    return result
def build_learning_decision_impact(context:dict[str,Any],learning:dict[str,Any]|None,receipt:dict[str,Any],iso_year:int,iso_week:int)->dict[str,Any]:
    base={
        'contract':'LEARNING_DECISION_IMPACT_v1',
        'authority':'SHADOW_MEASUREMENT_ONLY',
        'iso_year':iso_year,
        'iso_week':iso_week,
        'evaluation_horizon_weeks':8,
        'learning_input_present':False,
        'changed_calibration_decision':None,
        'exact_input_responsible':[],
        'potential_incremental_inputs':[],
        'automatic_deletion':False,
        'retirement_review_rule':'After 8 evaluable weekly observations, eight FALSE decisions with zero novel unconsumed inputs triggers retirement/merge review; missing consumption or NOT_EVALUABLE never counts as proof of zero value.',
    }
    if not isinstance(learning,dict) or learning.get('contract')!='MASTER_MONDAY_LEARNING_PACKET_v1':
        return {**base,'assessment_status':'NO_VALID_LEARNING_INPUT','reason':'No valid MASTER_MONDAY_LEARNING_PACKET_v1 was available.'}
    base['learning_input_present']=True
    base['learning_packet_generated_at_utc']=learning.get('generated_at_utc')
    base['learning_packet_sha256']=sha(learning)
    decision_time=parse_time(receipt.get('created_unix'))
    learning_time=parse_time(learning.get('generated_at_utc'))
    if decision_time is not None and learning_time is not None and learning_time>decision_time:
        return {**base,'assessment_status':'NOT_EVALUABLE_LATE_PACKET','reason':'Learning packet was generated after the frozen calibration API decision and is excluded prospectively.'}
    baseline_ids=semantic_identities(context)
    learning_ids=semantic_identities(learning)
    novel=sorted(learning_ids-baseline_ids)
    structured=[]
    for key in ('contradictions','method_improvement_candidates','strengthened','weakened'):
        rows=learning.get(key)
        if isinstance(rows,list) and rows:structured.append(key)
    potential=novel+[f'NONEMPTY:{key}' for key in structured]
    base['baseline_semantic_identity_count']=len(baseline_ids)
    base['learning_semantic_identity_count']=len(learning_ids)
    base['potential_incremental_inputs']=potential
    base['learning_live_consumption_allowed']=learning.get('live_consumption_allowed') is True
    if not potential:
        return {**base,'assessment_status':'EVALUABLE_NO_INCREMENTAL_INPUT','changed_calibration_decision':False,'reason':'The advisory packet added no novel semantic identities or decision-relevant structured deltas beyond the frozen baseline context.'}
    return {**base,'assessment_status':'NOT_EVALUABLE_NOVEL_INPUT_NOT_CONSUMED','reason':'Novel advisory input existed, but the packet is advisory-only and was not allowed to alter the frozen baseline calibration. Fix/authorize the consumer edge before attributing decision impact.'}
def fallback_scorecard(context:dict[str,Any])->dict[str,Any]:
    learning=context.get('experiment_learning') if isinstance(context.get('experiment_learning'),dict) else {}
    registry_status=str(learning.get('status') or 'UNAVAILABLE_CONTEXT')
    matured=learning.get('new_matured_outcomes')
    registry_available=(registry_status=='AVAILABLE')
    evidence_available=(registry_available and learning.get('matured_outcome_evidence_available') is True and isinstance(matured,list))
    if not registry_available:
        return {
            'status':'UNAVAILABLE_EXPERIMENT_REGISTRY',
            'experiment_registry_status':registry_status,
            'outcome_ingestion_status':learning.get('outcome_ingestion_status','UNAVAILABLE'),
            'analysis_layer':{},
            'operational_translation_layer':{},
            'matured_outcome_count':None,
            'reason':'Experiment registry evidence is unavailable; an unavailable registry cannot be represented as a valid empty matured-outcome set.',
        }
    if not evidence_available:
        return {
            'status':'INCOMPLETE_EXPERIMENT_OUTCOME_INGESTION',
            'experiment_registry_status':registry_status,
            'outcome_ingestion_status':learning.get('outcome_ingestion_status','INCOMPLETE'),
            'analysis_layer':{},
            'operational_translation_layer':{},
            'matured_outcome_count':None,
            'reason':'Experiment registry is available, but matured-outcome evidence ingestion is incomplete. This lane is degraded without misreporting the registry itself as unavailable.',
        }
    return {
        'status':'UNAVAILABLE_API_CONTRACT' if matured else 'PENDING_MATURED_OUTCOMES',
        'experiment_registry_status':registry_status,
        'analysis_layer':{},
        'operational_translation_layer':{},
        'matured_outcome_count':len(matured),
        'reason':'WEEKLY_CALIBRATION_SHADOW validated output contract does not currently include a scorecard field.' if matured else 'A valid experiment registry supplied zero newly matured outcomes; formal outcome scoring remains pending.',
    }
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',type=Path,required=True);ap.add_argument('--preflight',type=Path,required=True);ap.add_argument('--context',type=Path,required=True);ap.add_argument('--api-output',type=Path);ap.add_argument('--api-receipt',type=Path);ap.add_argument('--api-status',required=True);ap.add_argument('--output-dir',type=Path,required=True);ap.add_argument('--learning-packet',type=Path,default=Path('research/framework_learning/LATEST_MASTER_MONDAY_LEARNING_PACKET.json'));a=ap.parse_args()
    freeze=load(a.freeze);preflight=load(a.preflight);context=load(a.context);api=load(a.api_output) if a.api_output and a.api_output.exists() else {};receipt=load(a.api_receipt) if a.api_receipt and a.api_receipt.exists() else {}
    learning=load(a.learning_packet) if a.learning_packet.exists() else None
    learning_impact=build_learning_decision_impact(context,learning,receipt,int(freeze['iso_year']),int(freeze['iso_week']))
    analysis=api.get('analysis') or api.get('calibration') or api.get('summary') or {'status':'UNAVAILABLE_API_FAILURE' if a.api_status!='success' else 'UNAVAILABLE_NOT_PRODUCED'}
    translation=api.get('operational_translation') or {'status':'UNAVAILABLE_API_CONTRACT','reason':'WEEKLY_CALIBRATION_SHADOW validated output contract does not currently include an operational_translation field.'}
    registry_fallback=fallback_scorecard(context)
    if registry_fallback['status']=='UNAVAILABLE_EXPERIMENT_REGISTRY':
        scorecard=registry_fallback
    elif api.get('scorecard'):
        scorecard=api['scorecard']
    else:
        scorecard=registry_fallback
    shadow_path=Path('research/api_agent/outputs/shadow_admission/LATEST_SHADOW_ADMISSION_DECISION.json')
    shadow=load(shadow_path) if shadow_path.exists() else {'contract':'SHADOW_ADMISSION_AI_DECISION_v1','overall_status':'NOT_YET_AVAILABLE','candidate_decisions':[],'master_monday_summary':'No autonomous shadow-admission decision has been published yet.'}
    shadow_reporting={'mode':'REPORT_AFTER_DECISION_NO_APPROVAL_PROMPT','human_confirmation_required':False,'decision':shadow}
    machine={'contract':'MASTER_MONDAY_MACHINE_PACKAGE_v1','created_at_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'iso_year':freeze['iso_year'],'iso_week':freeze['iso_week'],'freeze_sha256':freeze['freeze_sha256'],'preflight_sha256':preflight['package_sha256'],'context_hash':context['context_hash'],'api_status':a.api_status,'api_receipt':receipt,'analysis':analysis,'operational_translation':translation,'scorecard':scorecard,'shadow_admission':shadow_reporting,'learning_decision_impact':learning_impact,'authority':{'portfolio_action':False,'canonical_promotion':False,'model_weight_change':False}}
    machine['package_sha256']=sha(machine);a.output_dir.mkdir(parents=True,exist_ok=True)
    files={'MASTER_MONDAY_MACHINE_PACKAGE.json':machine,'MASTER_MONDAY_CALIBRATION_SCORECARD.json':scorecard,'MASTER_MONDAY_OPERATIONAL_TRANSLATION.json':translation,'MASTER_MONDAY_SHADOW_ADMISSION.json':shadow_reporting,'MASTER_MONDAY_LEARNING_DECISION_IMPACT.json':learning_impact}
    for name,obj in files.items():(a.output_dir/name).write_bytes(canon(obj))
    machine_path=a.output_dir/'MASTER_MONDAY_MACHINE_PACKAGE.json'
    subprocess.run([
        sys.executable,'scripts/orchestration/consumer_receipt.py',
        '--repo-root','.',
        '--manifest','research/framework_handoffs/LATEST_FRAMEWORK_HANDOFF_MANIFEST.json',
        '--consumer','MASTER_MONDAY',
        '--target',str(machine_path),
        '--self-hash-field','package_sha256',
        '--declared','WEEKLY_CLOSE',
        '--declared','EXPERIMENT_REGISTRY',
    ],check=True)
    machine=load(machine_path)
    experiment_status=(context.get('experiment_learning') or {}).get('status','UNAVAILABLE_CONTEXT') if isinstance(context.get('experiment_learning'),dict) else 'UNAVAILABLE_CONTEXT'
    report=f"# MASTER MONDAY — {freeze['iso_year']}-W{int(freeze['iso_week']):02d}\n\nPreflight: **{preflight['packet']['status']}**\n\nAPI calibration: **{a.api_status.upper()}**\n\nExperiment registry evidence: **{experiment_status}**\n\nConsumer receipt: **{(machine.get('consumer_receipt') or {}).get('status','UNAVAILABLE')}**\n\nLearning decision impact: **{learning_impact.get('assessment_status','UNKNOWN')}**\n\n## Analysis layer\n\n```json\n{json.dumps(analysis,ensure_ascii=False,indent=2)}\n```\n\n## Operational translation\n\n```json\n{json.dumps(translation,ensure_ascii=False,indent=2)}\n```\n\n## Calibration scorecard\n\n```json\n{json.dumps(scorecard,ensure_ascii=False,indent=2)}\n```\n\n## Learning decision impact — 8 week shadow measurement\n\n```json\n{json.dumps(learning_impact,ensure_ascii=False,indent=2)}\n```\n\n## Autonomous shadow admission\n\nThis section is reporting-only. The OpenAI API lifecycle decision does not require owner confirmation.\n\n```json\n{json.dumps(shadow,ensure_ascii=False,indent=2)}\n```\n"
    (a.output_dir/'MASTER_MONDAY_REPORT.md').write_text(report)
    pointer={'contract':'MASTER_MONDAY_DELIVERY_POINTER_v1','iso_year':freeze['iso_year'],'iso_week':freeze['iso_week'],'status':'READY' if a.api_status=='success' else 'READY_WITH_API_FAILURE','machine_package_path':str(machine_path),'machine_package_sha256':machine['package_sha256'],'report_path':str(a.output_dir/'MASTER_MONDAY_REPORT.md'),'preflight_status':preflight['packet']['status'],'freeze_sha256':freeze['freeze_sha256'],'experiment_learning_status':experiment_status,'scorecard_status':scorecard.get('status','UNKNOWN'),'operational_translation_status':translation.get('status','UNKNOWN'),'shadow_admission_status':shadow.get('overall_status','UNKNOWN'),'shadow_admission_human_confirmation_required':False,'consumer_receipt_status':(machine.get('consumer_receipt') or {}).get('status','UNAVAILABLE'),'learning_decision_impact_status':learning_impact.get('assessment_status'),'learning_changed_calibration_decision':learning_impact.get('changed_calibration_decision')}
    (a.output_dir/'MASTER_MONDAY_DELIVERY_POINTER.json').write_bytes(canon(pointer))
if __name__=='__main__':main()
