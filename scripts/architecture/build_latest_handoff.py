from __future__ import annotations
import argparse,csv,hashlib,json
from datetime import datetime,timezone
from pathlib import Path


def load(p):
    try:return json.loads(p.read_text())
    except Exception:return None
def canon(v):return (json.dumps(v,sort_keys=True,separators=(',',':'))+'\n').encode()
def latest(root,name='*.json'):
    rows=[]
    if root.exists():
        for p in root.rglob(name):
            v=load(p)
            if not v:continue
            raw=next((v.get(k) for k in ('captured_at_utc','created_at_utc','generated_at_utc','freeze_utc','retrieved_at_utc') if v.get(k)),None)
            rows.append((str(raw or ''),p,v))
    return sorted(rows,key=lambda x:x[0])[-1] if rows else (None,None,None)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path('.'));a=ap.parse_args();r=a.repo_root;now=datetime.now(timezone.utc)
    cap=latest(r/'03_DAILY_CAPTURE_LOGS/captures');director=latest(r/'research/api_agent/outputs/daily','DAILY_DIRECTOR_OUTPUT.json');weekly=latest(r/'research/api_agent/outputs/weekly','MASTER_MONDAY_DELIVERY_POINTER.json');health=latest(r/'research/architecture_health')
    accepted=latest(r/'research/data_ping_bridge/accepted');incidents=[str(p) for p in sorted((r/'09_SOURCE_QA/incidents').glob('*.md'))[-20:]] if (r/'09_SOURCE_QA/incidents').exists() else []
    pending=[str(p) for p in sorted((r/'research/api_agent/forecast_candidates/PENDING').rglob('*.json'))] if (r/'research/api_agent/forecast_candidates/PENDING').exists() else []
    def ptr(row):
        _,p,v=row
        return None if p is None else {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    handoff={'contract':'LATEST_HANDOFF_v1','generated_at_utc':now.isoformat().replace('+00:00','Z'),'pointers':{'latest_capture':ptr(cap),'latest_director_output':ptr(director),'latest_weekly_output':ptr(weekly),'health':ptr(health),'latest_accepted_data_ping':ptr(accepted)},'open_incidents':incidents,'pending_forecast_candidates':pending,'authority':'READ_ONLY_ROUTING_SURFACE'}
    handoff['handoff_sha256']=hashlib.sha256(canon(handoff)).hexdigest();(r/'LATEST_HANDOFF.json').write_bytes(canon(handoff))
    lines=['# LATEST HANDOFF','',f"Generated: {handoff['generated_at_utc']}",f"Hash: `{handoff['handoff_sha256']}`",'']+[f"- **{k}**: `{(v or {}).get('path','UNAVAILABLE')}`" for k,v in handoff['pointers'].items()]+['',f"Open incidents: {len(incidents)}",f"Pending forecast candidates: {len(pending)}"]
    (r/'LATEST_HANDOFF.md').write_text('\n'.join(lines)+'\n')
    captures=[]
    for p in (r/'03_DAILY_CAPTURE_LOGS/captures').rglob('*.json') if (r/'03_DAILY_CAPTURE_LOGS/captures').exists() else []:
        v=load(p)
        if v:captures.append(v)
    owners={}
    for c in captures:
        for o in c.get('owners',[]):
            key=o.get('owner_id');owners.setdefault(key,[0,0]);owners[key][1]+=1;owners[key][0]+=int(o.get('status')=='PASS')
    out=r/'03_DAILY_CAPTURE_LOGS/weekly/RELIABILITY_LEDGER.csv';out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['generated_at_utc','owner_id','pass_count','observation_count','pass_rate']);
        for k,(p,n) in sorted(owners.items()):w.writerow([handoff['generated_at_utc'],k,p,n,round(p/n,6) if n else 0])
    print(json.dumps({'status':'PASS','handoff_sha256':handoff['handoff_sha256'],'owners':len(owners)},sort_keys=True))
if __name__=='__main__':main()
