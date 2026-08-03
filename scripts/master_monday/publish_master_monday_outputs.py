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
    translation=api.get('operational_translation') or {'status':'UNAVAILABLE_NOT_PRODUCED','reason':'Separate operational translation was not present in validated API output.'}
    scorecard=api.get('scorecard') or {'status':'PENDING_MATURED_OUTCOMES','analysis_layer':{},'operational_translation_layer':{}}
    machine={'contract':'MASTER_MONDAY_MACHINE_PACKAGE_v1','created_at_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'iso_year':freeze['iso_year'],'iso_week':freeze['iso_week'],'freeze_sha256':freeze['freeze_sha256'],'preflight_sha256':preflight['package_sha256'],'context_hash':context['context_hash'],'api_status':a.api_status,'api_receipt':receipt,'analysis':analysis,'operational_translation':translation,'scorecard':scorecard,'authority':{'portfolio_action':False,'canonical_promotion':False,'model_weight_change':False}}
    machine['package_sha256']=sha(machine);a.output_dir.mkdir(parents=True,exist_ok=True)
    files={'MASTER_MONDAY_MACHINE_PACKAGE.json':machine,'MASTER_MONDAY_CALIBRATION_SCORECARD.json':scorecard,'MASTER_MONDAY_OPERATIONAL_TRANSLATION.json':translation}
    for name,obj in files.items():(a.output_dir/name).write_bytes(canon(obj))
    report=f"# MASTER MONDAY — {freeze['iso_year']}-W{int(freeze['iso_week']):02d}\n\nPreflight: **{preflight['packet']['status']}**\n\nAPI calibration: **{a.api_status.upper()}**\n\n## Analysis layer\n\n```json\n{json.dumps(analysis,ensure_ascii=False,indent=2)}\n```\n\n## Operational translation\n\n```json\n{json.dumps(translation,ensure_ascii=False,indent=2)}\n```\n"
    (a.output_dir/'MASTER_MONDAY_REPORT.md').write_text(report)
    pointer={'contract':'MASTER_MONDAY_DELIVERY_POINTER_v1','iso_year':freeze['iso_year'],'iso_week':freeze['iso_week'],'status':'READY' if a.api_status=='success' else 'READY_WITH_API_FAILURE','machine_package_path':str(a.output_dir/'MASTER_MONDAY_MACHINE_PACKAGE.json'),'machine_package_sha256':machine['package_sha256'],'report_path':str(a.output_dir/'MASTER_MONDAY_REPORT.md'),'preflight_status':preflight['packet']['status'],'freeze_sha256':freeze['freeze_sha256']}
    (a.output_dir/'MASTER_MONDAY_DELIVERY_POINTER.json').write_bytes(canon(pointer))
if __name__=='__main__':main()
