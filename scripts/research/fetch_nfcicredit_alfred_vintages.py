#!/usr/bin/env python3
"""Fetch the three preregistered NFCICREDIT T-90 vintages from FRED/ALFRED API.

Requires FRED_API_KEY. Writes deterministic CSV plus provenance JSON. Missing
values remain missing. No summarisation layer is used.
"""
import argparse,csv,hashlib,json,os,urllib.parse,urllib.request
from datetime import date,timedelta,datetime,timezone
from pathlib import Path

TOPS=(date(2013,11,30),date(2017,12,17),date(2021,11,10))
SERIES='NFCICREDIT'
BASE='https://api.stlouisfed.org/fred/series/observations'


def fetch(api_key,asof):
    start=asof-timedelta(days=365*3+35)
    q=urllib.parse.urlencode({'series_id':SERIES,'api_key':api_key,'file_type':'json','observation_start':start.isoformat(),'observation_end':asof.isoformat(),'realtime_start':'1776-07-04','realtime_end':asof.isoformat(),'output_type':1})
    raw=urllib.request.urlopen(BASE+'?'+q,timeout=30).read()
    payload=json.loads(raw)
    rows=[]
    for r in payload.get('observations',[]):
        if r.get('value') in (None,'','.'): continue
        rows.append({'observation_date':r['date'],'vintage_asof':asof.isoformat(),'value':r['value']})
    return raw,rows


def main():
    p=argparse.ArgumentParser();p.add_argument('--output-csv',type=Path,required=True);p.add_argument('--provenance',type=Path,required=True);a=p.parse_args()
    key=os.environ.get('FRED_API_KEY','').strip()
    if not key: raise SystemExit('FRED_API_KEY is required; fail closed')
    all_rows=[]; receipts=[]
    for top in TOPS:
        asof=top-timedelta(days=90); raw,rows=fetch(key,asof); all_rows.extend(rows)
        receipts.append({'top':top.isoformat(),'vintage_asof':asof.isoformat(),'rows':len(rows),'payload_sha256':hashlib.sha256(raw).hexdigest()})
    a.output_csv.parent.mkdir(parents=True,exist_ok=True)
    with a.output_csv.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['observation_date','vintage_asof','value']);w.writeheader();w.writerows(all_rows)
    prov={'contract':'NFCICREDIT_ALFRED_VINTAGES_v1','series':SERIES,'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'endpoint':BASE,'requests':receipts,'k17':'DETERMINISTIC_PARSE_NO_LLM','authority':'RESEARCH_ONLY_NO_EXECUTION'}
    a.provenance.write_text(json.dumps(prov,indent=2,sort_keys=True)+'\n')
    return 0

if __name__=='__main__': raise SystemExit(main())
