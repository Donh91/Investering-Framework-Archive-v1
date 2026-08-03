from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path


def canon(v):return (json.dumps(v,sort_keys=True,separators=(',',':'))+'\n').encode()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--receipt',type=Path,required=True);ap.add_argument('--pending-root',type=Path,required=True);a=ap.parse_args()
    out=json.loads(a.output.read_text());receipt=json.loads(a.receipt.read_text());now=datetime.now(timezone.utc);created=[]
    for i,c in enumerate(out.get('forecast_candidates',[]),1):
        material={'contract':'FORECAST_CANDIDATE_v1','authority':'UNRATIFIED_RESEARCH_ONLY','candidate_id':hashlib.sha256(canon({'receipt':receipt.get('output_hash'),'index':i,'candidate':c})).hexdigest()[:24],'created_at_utc':now.isoformat().replace('+00:00','Z'),'model':receipt.get('model'),'task':receipt.get('task'),'prompt_sha256':receipt.get('prompt_hash'),'context_sha256':receipt.get('context_hash'),'source_output_sha256':receipt.get('output_hash'),'candidate':c,'ratification_status':'PENDING','self_promotion_allowed':False}
        p=a.pending_root/f'{now:%Y/%m/%d}'/f"{material['candidate_id']}.json";p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(canon(material));created.append(str(p))
    print(json.dumps({'status':'PASS','candidate_count':len(created),'paths':created},sort_keys=True))
if __name__=='__main__':main()
