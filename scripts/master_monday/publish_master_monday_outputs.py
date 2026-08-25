from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def load(p:Path):return json.loads(p.read_text())
def canon(v:Any)->bytes:return (json.dumps(v,sort_keys=True,separators=(',',':'))+'\n').encode()
def sha(v:Any)->str:return hashlib.sha256(canon(v)).hexdigest()
def fallback_scorecard(context:dict[str,Any])->dict[str,Any]:
    learning=context.get('experiment_learning') if isinstance(context.get('experiment_learning'),dict) else {}
    registry_status=str(learning.get('status') or 'UNAVAILABLE_CONTEXT')
    matured=learning.get('new_matured_outcomes')
    evidence_available=(registry_status=='AVAILABLE' and learning.get('matured_outcome_evidence_available') is True and isinstance(matured,list))
    if not evidence_available:
        return {
            'status':'UNAVAILABLE_EXPERIMENT_REGISTRY',
            'experiment_registry_status':registry_status,
            'analysis_layer':{},
            'operational_translation_layer':{},
            'matured_outcome_count':None,
            'reason':'Experiment registry evidence is unavailable; an unavailable registry cannot be represented as a valid empty matured-outcome set.',
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
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',type=Path,required=True);ap.add_argument('--preflight',type=Path,required=True);ap.add_argument('--context',type=Path,required=True);ap.add_argument('--api-output',type=Path);ap.add_argument('--api-receipt',type=Path);ap.add_argument('--api-status',required=True);ap.add_argument('--output-dir',type=Path,required=True);a=ap.parse_args()
    freeze=load(a.freeze);preflight=load(a.preflight);context=load(a.context);api=load(a.api_output) if a.api_output and a.api_output.exists() else {};receipt=load(a.api_receipt) if a.api_receipt and a.api_receipt.exists() else {}
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
    machine={'contract':'MASTER_MONDAY_MACHINE_PACKAGE_v1','created_at_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'iso_year':freeze['iso_year'],'iso_week':freeze['iso_week'],'freeze_sha256':freeze['freeze_sha256'],'preflight_sha256':preflight['package_sha256'],'context_hash':context['context_hash'],'api_status':a.api_status,'api_receipt':receipt,'analysis':analysis,'operational_translation':translation,'scorecard':scorecard,'shadow_admission':shadow_reporting,'authority':{'portfolio_action':False,'canonical_promotion':False,'model_weight_change':False}}
    machine['package_sha256']=sha(machine);a.output_dir.mkdir(parents=True,exist_ok=True)
    files={'MASTER_MONDAY_MACHINE_PACKAGE.json':machine,'MASTER_MONDAY_CALIBRATION_SCORECARD.json':scorecard,'MASTER_MONDAY_OPERATIONAL_TRANSLATION.json':translation,'MASTER_MONDAY_SHADOW_ADMISSION.json':shadow_reporting}
    for name,obj in files.items():(a.output_dir/name).write_bytes(canon(obj))
    experiment_status=(context.get('experiment_learning') or {}).get('status','UNAVAILABLE_CONTEXT') if isinstance(context.get('experiment_learning'),dict) else 'UNAVAILABLE_CONTEXT'
    report=f"# MASTER MONDAY — {freeze['iso_year']}-W{int(freeze['iso_week']):02d}\n\nPreflight: **{preflight['packet']['status']}**\n\nAPI calibration: **{a.api_status.upper()}**\n\nExperiment registry evidence: **{experiment_status}**\n\n## Analysis layer\n\n```json\n{json.dumps(analysis,ensure_ascii=False,indent=2)}\n```\n\n## Operational translation\n\n```json\n{json.dumps(translation,ensure_ascii=False,indent=2)}\n```\n\n## Calibration scorecard\n\n```json\n{json.dumps(scorecard,ensure_ascii=False,indent=2)}\n```\n\n## Autonomous shadow admission\n\nThis section is reporting-only. The OpenAI API lifecycle decision does not require owner confirmation.\n\n```json\n{json.dumps(shadow,ensure_ascii=False,indent=2)}\n```\n"
    (a.output_dir/'MASTER_MONDAY_REPORT.md').write_text(report)
    pointer={'contract':'MASTER_MONDAY_DELIVERY_POINTER_v1','iso_year':freeze['iso_year'],'iso_week':freeze['iso_week'],'status':'READY' if a.api_status=='success' else 'READY_WITH_API_FAILURE','machine_package_path':str(a.output_dir/'MASTER_MONDAY_MACHINE_PACKAGE.json'),'machine_package_sha256':machine['package_sha256'],'report_path':str(a.output_dir/'MASTER_MONDAY_REPORT.md'),'preflight_status':preflight['packet']['status'],'freeze_sha256':freeze['freeze_sha256'],'experiment_learning_status':experiment_status,'scorecard_status':scorecard.get('status','UNKNOWN'),'operational_translation_status':translation.get('status','UNKNOWN'),'shadow_admission_status':shadow.get('overall_status','UNKNOWN'),'shadow_admission_human_confirmation_required':False}
    (a.output_dir/'MASTER_MONDAY_DELIVERY_POINTER.json').write_bytes(canon(pointer))
if __name__=='__main__':main()
