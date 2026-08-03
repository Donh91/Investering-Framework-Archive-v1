from __future__ import annotations

import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def canonical(value:Any)->bytes:return (json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()
def load_json(path:Path)->Any:return json.loads(path.read_text())
def ts(raw:Any):return datetime.fromisoformat(str(raw).replace('Z','+00:00')).astimezone(timezone.utc)
def find_time(output:dict[str,Any],receipt:dict[str,Any]|None):
    for source in (receipt or {},output):
        for key in ('captured_at_utc','created_at_utc','generated_at_utc','freeze_utc','response_created_at_utc'):
            if source.get(key):
                try:return ts(source[key])
                except Exception:pass
    return None

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--weekly-pointer',type=Path,required=True);ap.add_argument('--daily-output-root',type=Path,required=True);ap.add_argument('--freeze-file',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    weekly=load_json(a.weekly_pointer);freeze=load_json(a.freeze_file);start=ts(freeze['window_start_utc']);end=ts(freeze['window_end_utc'])
    candidates=[];seen=set()
    for path in a.daily_output_root.rglob('DAILY_DIRECTOR_OUTPUT.json'):
        try:out=load_json(path)
        except Exception:continue
        rp=path.with_name('DAILY_DIRECTOR_RECEIPT.json');receipt=load_json(rp) if rp.exists() else None;when=find_time(out,receipt)
        if not when or not(start<=when<end):continue
        key=(when.isoformat(),out.get('output_hash') or hashlib.sha256(canonical(out)).hexdigest())
        if key in seen:continue
        seen.add(key);candidates.append((when,path,out,receipt,key[1]))
    candidates.sort(key=lambda x:x[0])
    by_day={}
    for row in candidates:by_day[row[0].date().isoformat()]=row
    outputs=[]
    for day,row in sorted(by_day.items()):
        when,path,out,receipt,oh=row
        outputs.append({'local_day_key':day,'captured_at_utc':when.isoformat().replace('+00:00','Z'),'path':str(path),'output_sha256':hashlib.sha256(canonical(out)).hexdigest(),'receipt_sha256':hashlib.sha256(canonical(receipt)).hexdigest() if receipt else None,'output':out,'receipt':receipt})
    context={'contract':'WEEKLY_API_CALIBRATION_CONTEXT_v2','authority':'SHADOW_ONLY','iso_year':freeze['iso_year'],'iso_week':freeze['iso_week'],'window_start_utc':freeze['window_start_utc'],'window_end_utc':freeze['window_end_utc'],'freeze_sha256':freeze['freeze_sha256'],'weekly_capture_pack':weekly,'daily_director_rows':outputs,'daily_director_count':len(outputs),'selection_rule':'latest eligible row per UTC date within frozen week, deduplicated by timestamp and output hash','handoff_targets':['RAW_WEEKLY_CALIBRATION','FORECAST_LEDGER','MASTER_MONDAY_PREP','SPECIALIST_REVIEW'],'rules':['Do not rewrite frozen forecasts.','Separate data quality from market evidence.','Preserve disagreement, missingness and censored outcomes.','Evaluate analysis and operational translation separately.','No framework-state, model-weight or portfolio authority.']}
    context['context_hash']=hashlib.sha256(canonical(context)).hexdigest();a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(canonical(context));print(json.dumps({'status':'PASS','daily_rows':len(outputs),'context_hash':context['context_hash']},sort_keys=True))
if __name__=='__main__':main()
