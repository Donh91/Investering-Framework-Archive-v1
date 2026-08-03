from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path

def run(*args:str)->bytes:
    return subprocess.run(list(args),capture_output=True,check=True).stdout

def local_sha256(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def remote_bytes(path:str,ref:str)->bytes:
    return run('git','show',f'{ref}:{path}')

def blob(path:str,ref:str)->str:
    return run('git','rev-parse',f'{ref}:{path}').decode().strip()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--manifest',type=Path,required=True);ap.add_argument('--ref',default='origin/main');ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    m=json.loads(a.manifest.read_text());rows=[]
    for item in m['artifacts']:
        path=item['path'];p=Path(path);expected_sha=item.get('sha256');expected_blob=item.get('blob_sha')
        local_sha=local_sha256(p) if p.exists() else None
        try:
            rb=remote_bytes(path,a.ref);remote_sha=hashlib.sha256(rb).hexdigest();remote_blob=blob(path,a.ref)
        except Exception:
            remote_sha=None;remote_blob=None
        status='PASS' if expected_sha and expected_blob and local_sha==expected_sha and remote_sha==expected_sha and remote_blob==expected_blob else 'FAIL'
        rows.append({'path':path,'expected_sha256':expected_sha,'local_sha256':local_sha,'readback_sha256':remote_sha,'expected_blob_sha':expected_blob,'readback_blob_sha':remote_blob,'status':status})
    out={'contract':'DURABLE_READBACK_RECEIPT_v2','ref':a.ref,'status':'DURABLE_PASS' if rows and all(r['status']=='PASS' for r in rows) else 'FAIL','artifacts':rows}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,sort_keys=True,separators=(',',':'))+'\n')
    if out['status']!='DURABLE_PASS':raise SystemExit('READBACK_FAILED')
if __name__=='__main__':main()
