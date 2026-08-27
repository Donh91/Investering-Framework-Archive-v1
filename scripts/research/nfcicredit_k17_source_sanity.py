#!/usr/bin/env python3
import argparse,csv,json
from datetime import date
from pathlib import Path


def run(path):
    rows=[]
    with path.open(newline='') as f:
        for r in csv.DictReader(f):
            ds=r.get('DATE') or r.get('observation_date'); raw=r.get('NFCICREDIT')
            if ds and raw not in (None,'','.'):
                rows.append((date.fromisoformat(ds),float(raw)))
    if not rows: return {'status':'FAIL_CLOSED_EMPTY','authority':'RESEARCH_ONLY_NO_EXECUTION'}
    rows.sort(); first,last=rows[0][0],rows[-1][0]
    crisis=[v for d,v in rows if date(2008,9,1) <= d <= date(2009,3,31)]
    anchor=max(crisis) if crisis else None
    coverage_ok=first <= date(1972,1,1) and last >= date(2026,1,1)
    anchor_ok=anchor is not None and anchor > 0.0
    status='PASS' if coverage_ok and anchor_ok else 'FAIL_CLOSED_SOURCE_SANITY'
    return {'status':status,'first_observation':first.isoformat(),'last_observation':last.isoformat(),'observation_count':len(rows),'sanity_anchor':'2008-09-01..2009-03-31 max must be positive','sanity_anchor_value':anchor,'coverage_ok':coverage_ok,'anchor_ok':anchor_ok,'note':'sanity anchor detects source/parser failure; it does not establish provenance','authority':'RESEARCH_ONLY_NO_EXECUTION'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--csv',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args(); out=run(a.csv);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,sort_keys=True));return 0 if out['status']=='PASS' else 2
if __name__=='__main__': raise SystemExit(main())
