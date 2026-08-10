from __future__ import annotations

import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path


def load(path: Path): return json.loads(path.read_text())

def normalize_row(row):
    asset=row.get('asset'); assert asset in {'BTC','ETH'}, row
    assert row.get('session_final') is True and row.get('total_parity') is True, row
    assert row.get('reported_total') is not None, row
    assert row.get('unknown_cells_fully_accounted_by_reported_total') is True, row
    return {
        'asset':asset,'date':row.get('date'),'fund_headers':row.get('fund_headers'),'fund_values':row.get('fund_values'),
        'unknown_fund_cells':row.get('unknown_fund_cells',[]),'unknown_fund_cell_count':int(row.get('unknown_fund_cell_count',0)),
        'reported_total':row.get('reported_total'),'calculated_total':row.get('calculated_total'),'total_parity':True,'session_final':True,
        'unknown_cells_fully_accounted_by_reported_total':True,
    }

def history(snapshot):
    out={}
    for asset,rows in (snapshot.get('history_rows') or {}).items():
        for raw in rows:
            row=normalize_row(raw); assert row['asset']==asset,row; out[(asset,row['date'])]=row
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--first',type=Path,required=True); ap.add_argument('--second',type=Path,required=True); ap.add_argument('--output-root',type=Path,required=True); ap.add_argument('--now-utc'); a=ap.parse_args()
    first,second=load(a.first),load(a.second)
    assert first.get('status')=='PASS' and second.get('status')=='PASS',(first,second)
    assert first.get('unknown_cells_are_not_imputed') is True and second.get('unknown_cells_are_not_imputed') is True
    h1,h2=history(first),history(second); common=sorted(set(h1)&set(h2)); assert common
    for key in common: assert h1[key]==h2[key],{'key':key,'first':h1[key],'second':h2[key]}
    sessions=sorted({d for asset,d in common if ('BTC',d) in h2 and ('ETH',d) in h2}); assert sessions
    now=datetime.fromisoformat(a.now_utc.replace('Z','+00:00')) if a.now_utc else datetime.now(timezone.utc); now=now.astimezone(timezone.utc)
    root=a.output_root; day=root/now.strftime('%Y/%m/%d'); day.mkdir(parents=True,exist_ok=True); materialized=[]
    for session_date in sessions:
        rows=[h2[('BTC',session_date)],h2[('ETH',session_date)]]
        body={'contract':'DAILY_SETTLED_ETF_CALIBRATION_v2','authority':'SHADOW_CALIBRATION_INPUT_ONLY','session_date':session_date,'retrieved_at_utc':second.get('retrieved_at_utc'),'verification':{'retrieval_count':2,'minimum_separation_seconds':60,'rows_identical_across_retrievals':True,'all_fund_cells_known':all(r['unknown_fund_cell_count']==0 for r in rows),'unknown_cells_imputed':False,'unknown_cells_fully_accounted_by_reported_total':True,'total_parity_required':True,'source':'FARSIDE_CANONICAL_ALL_DATA_TABLES'},'rows':rows,'source_hashes_first':first.get('source_hashes',{}),'source_hashes_second':second.get('source_hashes',{}),'canonical_data_ping':False,'framework_state_change':False,'portfolio_action':False}
        sig=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest(); body['row_signature_sha256']=sig
        existing=None
        for p in root.rglob('*.json'):
            if p.name=='LATEST.json': continue
            try: old=load(p)
            except Exception: continue
            if old.get('session_date')==session_date and old.get('row_signature_sha256')==sig: existing=p; break
        if existing is None:
            existing=day/f"{now.strftime('%H%M%S')}_{session_date}.json"; existing.write_text(json.dumps(body,indent=2,sort_keys=True)+'\n')
        materialized.append((session_date,existing,sig,body))
    session_date,path,sig,body=materialized[-1]
    pointer={'contract':'DAILY_SETTLED_ETF_LATEST_POINTER_v2','path':str(path),'session_date':session_date,'retrieved_at_utc':body['retrieved_at_utc'],'row_signature_sha256':sig,'status':'PASS','history_sessions_materialized':len(materialized)}
    (root/'LATEST.json').write_text(json.dumps(pointer,indent=2,sort_keys=True)+'\n'); print(json.dumps(pointer,sort_keys=True))
if __name__=='__main__': main()
