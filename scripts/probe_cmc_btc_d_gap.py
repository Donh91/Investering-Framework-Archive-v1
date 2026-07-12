#!/usr/bin/env python3
from __future__ import annotations
import json, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = 'https://api.coinmarketcap.com/data-api/v3/global-metrics/quotes/historical'
UA = 'Mozilla/5.0 (compatible; Investering-Truth-Layer-Recovery/1.0; +https://github.com/)'
OUT = Path('btc_d_gap_probe')
OUT.mkdir(exist_ok=True)

def ep(s):
    return int(datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp())

def fetch(name, start, end, interval):
    params={'convertId':'2781','timeStart':str(ep(start)),'timeEnd':str(ep(end)),'interval':interval}
    url=BASE+'?'+urllib.parse.urlencode(params)
    req=urllib.request.Request(url, headers={'User-Agent':UA,'Accept':'application/json,text/plain,*/*','Referer':'https://coinmarketcap.com/charts/bitcoin-dominance/'})
    try:
        with urllib.request.urlopen(req,timeout=120) as r:
            raw=r.read()
        (OUT/f'{name}.json').write_bytes(raw)
        payload=json.loads(raw)
        quotes=payload.get('data',{}).get('quotes',[])
        summary={'name':name,'url':url,'status':'OK','count':len(quotes),'quotes':[{'timestamp':q.get('timestamp'),'btcDominance':q.get('btcDominance'),'btc_dominance':q.get('btc_dominance')} for q in quotes]}
    except Exception as e:
        summary={'name':name,'url':url,'status':'ERROR','error':repr(e)}
    (OUT/f'{name}_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))

fetch('daily_2023_01_04_to_07','2023-01-04','2023-01-07','1d')
fetch('hourly_2023_01_05','2023-01-05','2023-01-06','1h')
fetch('hourly_named_2023_01_05','2023-01-05','2023-01-06','hourly')
