from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def load(p:Path):return json.loads(p.read_text())
def canon(v:Any)->bytes:return (json.dumps(v,sort_keys=True,separators=(',',':'))+'\n').encode()
def sha(v:Any)->str:return hashlib.sha256(canon(v)).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',type=Path,required=True);ap.add_argument('--preflight',type=Path,required=True);ap.add_argument('--context',type=Path,required=True);ap.add_argument('--api-output',type=Path);ap.add_argument('--api-receipt',type=Path);ap.add_argument('--api-status',required=True);ap.add_argument('--output-dir',type=Path,required=True);a=ap.parse_args()
    freeze=load(a.freeze);preflight=load(a.preflight);context=load(a.context);api=load(a.api_output) if a.api_output and a.api_output.exists() else {};receipt=load(a.api_receipt) if a.api_receipt and a.api_receipt.exists() else {}
    analysis=api.get('analysis') or api.get('calibration') or api.get('summary') or {'status':'UNAVAILABLE_API_FAILURE' if a.api_status!='success' else 'UNAVAILABLE_NOT_PRODUCED'}
    translation=api.get('operational_translation') or {'status':'UNAVAILABLE_API_CONTRACT','reason':'WEEKLY_CALIBRATION_SHADOW validated output contract does not currently include an operational_translation field.'}
    if api.get('scorecard'):
        scorecard=api['scorecard']
    else:
        learning=context.get('experiment_learning') if isinstance(context.get('experiment_learning'),dict) else {}
        matured=learning.get('new_matured_outcomes') if isinstance(learning.get('new_matured_outcomes'),list) else []
        scorecard={
            'status':'UNAVAILABLE_API_CONTRACT' if matured else 'PENDING_MATURED_OUTCOMES',
            'analysis_layer':{},
            'operational_translation_layer':{},
            'matured_outcome_count':len(matured),
            'reason':'WEEKLY_CALIBRATION_SHADOW validated output contract does not currently include a scorecard field.' if matured else 'No newly matured experiment outcomes were supplied to this weekly context; formal outcome scoring remains pending.'
        }
    shadow_path=Path('research/api_agent/outputs/shadow_admission/LATEST_SHADOW_ADMISSION_DECISION.json')
    shadow=load(shadow_path) if shadow_path.exists() else {'contract':'SHADOW_ADMISSION_AI_DECISION_v1','overall_status':'NOT_YET_AVAILABLE','candidate_decisions':[],'master_monday_summary':'No autonomous shadow-admission decision has been published yet.'}
    shadow_reporting={'mode':'REPORT_AFTER_DECISION_NO_APPROVAL_PROMPT','human_confirmation_required':False,'decision':shadow}
    machine={'contract':'MASTER_MONDAY_MACHINE_PACKAGE_v1','created_at_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'iso_year':freeze['iso_year'],'iso_week':freeze['iso_week'],'freeze_sha256':freeze['freeze_sha256'],'preflight_sha256':preflight['package_sha256'],'context_hash':context['context_hash'],'api_status':a.api_status,'api_receipt':receipt,'analysis':analysis,'operational_translation':translation,'scorecard':scorecard,'shadow_admission':shadow_reporting,'authority':{'portfolio_action':False,'canonical_promotion':False,'model_weight_change':False}}
    machine['package_sha256']=sha(machine);a.output_dir.mkdir(parents=True,exist_ok=True)
    files={'MASTER_MONDAY_MACHINE_PACKAGE.json':machine,'MASTER_MONDAY_CALIBRATION_SCORECARD.json':scorecard,'MASTER_MONDAY_OPERATIONAL_TRANSLATION.json':translation,'MASTER_MONDAY_SHADOW_ADMISSION.json':shadow_reporting}
    for name,obj in files.items():(a.output_dir/name).write_bytes(canon(obj))
    report=f"# MASTER MONDAY — {freeze['iso_year']}-W{int(freeze['iso_week']):02d}\n\nPreflight: **{preflight['packet']['status']}**\n\nAPI calibration: **{a.api_status.upper()}**\n\n## Analysis layer\n\n```json\n{json.dumps(analysis,ensure_ascii=False,indent=2)}\n```\n\n## Operational translation\n\n```json\n{json.dumps(translation,ensure_ascii=False,indent=2)}\n```\n\n## Calibration scorecard\n\n```json\n{json.dumps(scorecard,ensure_ascii=False,indent=2)}\n```\n\n## Autonomous shadow admission\n\nThis section is reporting-only. The OpenAI API lifecycle decision does not require owner confirmation.\n\n```json\n{json.dumps(shadow,ensure_ascii=False,indent=2)}\n```\n"
    (a.output_dir/'MASTER_MONDAY_REPORT.md').write_text(report)
    pointer={'contract':'MASTER_MONDAY_DELIVERY_POINTER_v1','iso_year':freeze['iso_year'],'iso_week':freeze['iso_week'],'status':'READY' if a.api_status=='success' else 'READY_WITH_API_FAILURE','machine_package_path':str(a.output_dir/'MASTER_MONDAY_MACHINE_PACKAGE.json'),'machine_package_sha256':machine['package_sha256'],'report_path':str(a.output_dir/'MASTER_MONDAY_REPORT.md'),'preflight_status':preflight['packet']['status'],'freeze_sha256':freeze['freeze_sha256'],'scorecard_status':scorecard.get('status','UNKNOWN'),'operational_translation_status':translation.get('status','UNKNOWN'),'shadow_admission_status':shadow.get('overall_status','UNKNOWN'),'shadow_admission_human_confirmation_required':False}
    (a.output_dir/'MASTER_MONDAY_DELIVERY_POINTER.json').write_bytes(canon(pointer))
if __name__=='__main__':main()
