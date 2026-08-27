#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json,re,urllib.request,zipfile
from datetime import datetime,timezone
from pathlib import Path
from xml.etree import ElementTree as ET
URL='https://thedocs.worldbank.org/en/doc/5d903e848db1d1b83e0ec8f744e55570-0350012021/related/CMO-Historical-Data-Monthly.xlsx'
AUTH={'binding':False,'canonical_acceptance':False,'state_change':False,'portfolio_action':False}
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def sha(b): return hashlib.sha256(b).hexdigest()
def utc(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def col(ref):
 s=re.match(r'([A-Z]+)',ref).group(1); n=0
 for c in s:n=n*26+ord(c)-64
 return n-1
def parse_xlsx(payload:bytes):
 z=zipfile.ZipFile(__import__('io').BytesIO(payload)); shared=[]
 if 'xl/sharedStrings.xml' in z.namelist():
  root=ET.fromstring(z.read('xl/sharedStrings.xml'))
  for si in root.findall('m:si',NS): shared.append(''.join(t.text or '' for t in si.iter('{%s}t'%NS['m'])))
 candidates=[]
 for name in z.namelist():
  if not name.startswith('xl/worksheets/sheet') or not name.endswith('.xml'): continue
  root=ET.fromstring(z.read(name)); rows=[]
  for r in root.findall('.//m:row',NS):
   vals={}
   for c in r.findall('m:c',NS):
    v=c.find('m:v',NS); val='' if v is None else (v.text or '')
    if c.attrib.get('t')=='s' and val!='': val=shared[int(val)]
    vals[col(c.attrib['r'])]=val
   if vals: rows.append(vals)
  flat=' '.join(str(v) for rr in rows[:15] for v in rr.values())
  if 'Copper' in flat and 'Gold' in flat: candidates=rows; break
 if not candidates: raise ValueError('Copper/Gold worksheet not found')
 header=None
 for rr in candidates:
  inv={str(v).strip():k for k,v in rr.items()}
  if 'Copper' in inv and 'Gold' in inv: header=(inv['Copper'],inv['Gold']); continue
  if header:
   d=str(rr.get(0,'')).strip(); cv=rr.get(header[0]); gv=rr.get(header[1])
   if not d or cv in (None,'') or gv in (None,''): continue
   try: c=float(cv); g=float(gv)
   except: continue
   if re.match(r'^\d{4}M\d{2}$',d): period=d[:4]+'-'+d[-2:]
   elif re.match(r'^\d{4}-\d{2}',d): period=d[:7]
   else: continue
   yield period,c,g
def ema(vals,n):
 a=2/(n+1); out=[]; e=None
 for v in vals: e=v if e is None else a*v+(1-a)*e; out.append(e)
 return out
def rsi(vals,n=14):
 out=[None]*len(vals); gains=[]; losses=[]
 for i in range(1,len(vals)):
  d=vals[i]-vals[i-1]; gains.append(max(d,0)); losses.append(max(-d,0))
  if i<n: continue
  if i==n: ag=sum(gains[-n:])/n; al=sum(losses[-n:])/n
  else: ag=(ag*(n-1)+gains[-1])/n; al=(al*(n-1)+losses[-1])/n
  out[i]=100 if al==0 else 100-100/(1+ag/al)
 return out
def features(monthly,offset):
 bars=[]
 for i in range(offset+1,len(monthly),2):
  a,b=monthly[i-1],monthly[i]; bars.append({'bar_end_period':b['period'],'ratio':(a['ratio']+b['ratio'])/2})
 vals=[x['ratio'] for x in bars]; e12,e26=ema(vals,12),ema(vals,26); mac=[a-b for a,b in zip(e12,e26)]; sig=ema(mac,9); rs=rsi(vals)
 for i,x in enumerate(bars):
  x.update(macd=mac[i],macd_signal=sig[i],macd_hist=mac[i]-sig[i],rsi14=rs[i])
  if i==0:x['regime_state']='UNCLEAR'
  else:
   h=x['macd_hist']; ph=bars[i-1]['macd_hist']; x['regime_state']='TURNING_POSITIVE' if h>0>=ph else 'TURNING_NEGATIVE' if h<0<=ph else 'EXPANSION' if h>0 else 'CONTRACTION'
 return bars
def build(payload,retrieved):
 rows=list(parse_xlsx(payload)); monthly=[]
 for p,c,g in rows:
  ckg=c/1000.0; gkg=g/0.0311034768; monthly.append({'period':p,'copper_source':c,'gold_source':g,'copper_usd_per_kg':ckg,'gold_usd_per_kg':gkg,'ratio':ckg/gkg})
 if len(monthly)<100: raise ValueError('insufficient monthly history')
 h=sha(payload); return {'contract':'WORLD_BANK_COPPER_GOLD_SHADOW_v1','status':'PASS','retrieved_at_utc':retrieved,'source':{'provider':'World Bank','product':'Commodity Markets Pink Sheet, Monthly Prices','url':URL,'payload_sha256':h,'source_convention':'PERIOD_AVERAGE_MACRO_PROXY_NOT_FUTURES_CONTINUOUS_CONTRACT_CLOSE'},'coverage':{'first_period':monthly[0]['period'],'last_period':monthly[-1]['period'],'observations':len(monthly)},'monthly':monthly,'settled_2m':{'JAN_FEB':features(monthly,0),'FEB_MAR':features(monthly,1)},'authority':AUTH}
def fetch(timeout):
 req=urllib.request.Request(URL,headers={'User-Agent':'Investering-Framework-Shadow/1.0'}); return urllib.request.urlopen(req,timeout=timeout).read()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--fixture',type=Path); ap.add_argument('--output-root',type=Path,required=True); ap.add_argument('--timeout',type=float,default=20); a=ap.parse_args(); payload=a.fixture.read_bytes() if a.fixture else fetch(a.timeout); now=utc(); d=build(payload,now); root=a.output_root; root.mkdir(parents=True,exist_ok=True); h=d['source']['payload_sha256']; rev=root/'revisions'/f'{h}.json'; rev.parent.mkdir(exist_ok=True)
 if not rev.exists(): rev.write_text(json.dumps(d,sort_keys=True,separators=(',',':'))+'\n')
 latest={'contract':'WORLD_BANK_COPPER_GOLD_LATEST_v1','revision_path':str(rev.relative_to(root)),'payload_sha256':h,'retrieved_at_utc':now,'last_period':d['coverage']['last_period'],'authority':AUTH}; (root/'LATEST.json').write_text(json.dumps(latest,indent=2,sort_keys=True)+'\n'); print(json.dumps({'status':'PASS','revision':str(rev),'coverage':d['coverage']})); return 0
if __name__=='__main__': raise SystemExit(main())
