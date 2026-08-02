from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any

URLS={'BTC':'https://farside.co.uk/btc/','ETH':'https://farside.co.uk/eth/'}


def clean(s: str) -> str:
    s=re.sub(r'<[^>]+>',' ',s)
    return re.sub(r'\s+',' ',unescape(s)).strip()


def parse_number(s: str) -> float | None:
    s=s.strip().replace(',','').replace('$','').replace('(','-').replace(')','')
    if s in {'','-','–','—','N/A'}: return None
    m=re.fullmatch(r'(-?\d+(?:\.\d+)?)\s*([KMB]?)',s,re.I)
    if not m: return None
    v=float(m.group(1)); scale={'':1,'K':1e3,'M':1e6,'B':1e9}[m.group(2).upper()]
    return v*scale


def parse_tables(html: str, asset: str) -> list[dict[str, Any]]:
    rows=[]
    for tr in re.findall(r'<tr\b[^>]*>(.*?)</tr>',html,re.I|re.S):
        cells=[clean(x) for x in re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>',tr,re.I|re.S)]
        if len(cells)<2: continue
        date=cells[0]
        if not re.search(r'\d',date): continue
        values=[parse_number(c) for c in cells[1:]]
        if not any(v is not None for v in values): continue
        rows.append({'asset':asset,'date_label':date,'fund_values':values[:-1],'reported_total':values[-1],'raw_cells':cells})
    return rows


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument('--output-dir',type=Path,required=True); ap.add_argument('--fixture-dir',type=Path)
    args=ap.parse_args(); args.output_dir.mkdir(parents=True,exist_ok=True)
    out=[]; source_hashes={}; errors=[]
    for asset,url in URLS.items():
        try:
            if args.fixture_dir:
                raw=(args.fixture_dir/f'{asset.lower()}.html').read_bytes()
            else:
                req=urllib.request.Request(url,headers={'User-Agent':'InvesteringFramework/1.0 (+audit owner capture)'})
                with urllib.request.urlopen(req,timeout=30) as r: raw=r.read()
            source_hashes[asset]=hashlib.sha256(raw).hexdigest()
            rows=parse_tables(raw.decode('utf-8','replace'),asset)
            if not rows: raise ValueError('NO_PARSEABLE_ROWS')
            latest=rows[-1]
            calc=sum(v for v in latest['fund_values'] if v is not None)
            parity=None if latest['reported_total'] is None else abs(calc-latest['reported_total']) <= max(0.2,abs(latest['reported_total'])*0.01)
            latest['calculated_total']=calc; latest['total_parity']=parity
            out.append(latest)
        except Exception as e:
            errors.append({'asset':asset,'error':str(e)})
    status='PASS' if len(out)==2 and not errors else ('PARTIAL' if out else 'SOURCE_UNAVAILABLE')
    snap={'contract':'FARSIDE_ETF_OWNER_SNAPSHOT_v1','retrieved_at_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'status':status,'rows':out,'errors':errors,'source_hashes':source_hashes,'authority':'SHADOW_ONLY'}
    raw=(json.dumps(snap,sort_keys=True,separators=(',',':'))+'\n').encode(); sha=hashlib.sha256(raw).hexdigest()
    (args.output_dir/'owner_snapshot.json').write_bytes(raw)
    receipt={'contract':'FARSIDE_ETF_OWNER_RECEIPT_v1','status':status,'snapshot_sha256':sha,'row_count':len(out),'source_type':'WEB_TABLE','portfolio_action':False}
    (args.output_dir/'receipt.json').write_text(json.dumps(receipt,sort_keys=True)+'\n')
    print(json.dumps(receipt,sort_keys=True))
    if status=='SOURCE_UNAVAILABLE': raise SystemExit(2)

if __name__=='__main__': main()
