from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path

def sha256(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def blob(path:str,ref:str)->str:
    p=subprocess.run(['git','rev-parse',f'{ref}:{path}'],capture_output=True,text=True,check=True)
    return p.stdout.strip()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--manifest',type=Path,required=True);ap.add_argument('--ref',default='origin/main');ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    m=json.loads(a.manifest.read_text());rows=[]
    for item in m['artifacts']:
        p=Path(item['path']); expected=item['sha256']; actual=sha256(p) if p.exists() else None
        try:b=blob(item['path'],a.ref)
        except Exception:b=None
        status='PASS' if actual==expected and b else 'FAIL'
        rows.append({'path':item['path'],'expected_sha256':expected,'readback_sha256':actual,'expected_blob_sha':item.get('blob_sha'),'readback_blob_sha':b,'status':status})
    out={'contract':'DURABLE_READBACK_RECEIPT_v1','ref':a.ref,'status':'DURABLE_PASS' if all(r['status']=='PASS' for r in rows) else 'FAIL','artifacts':rows}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,sort_keys=True,separators=(',',':'))+'\n')
    if out['status']!='DURABLE_PASS':raise SystemExit('READBACK_FAILED')
if __name__=='__main__':main()
