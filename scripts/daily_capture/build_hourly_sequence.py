from __future__ import annotations
import argparse,csv,hashlib,json,math,urllib.error,urllib.parse,urllib.request
from datetime import datetime,timedelta,timezone
from pathlib import Path
from zoneinfo import ZoneInfo
A={"binding":False,"canonical_acceptance":False,"state_change":False,"portfolio_action":False}
SPOT="https://data-api.binance.vision/api/v3/klines"; FUT="https://fapi.binance.com"; TZ=ZoneInfo("Europe/Copenhagen")
SS=("BTCUSDT","ETHUSDT","ETHBTC"); FS=("BTCUSDT","ETHUSDT")
F=["timestamp_utc","timestamp_copenhagen","source_window_end_utc","btc_open","btc_high","btc_low","btc_close","btc_volume","btc_return_1h_pct","btc_range_1h_pct","eth_open","eth_high","eth_low","eth_close","eth_volume","eth_return_1h_pct","eth_range_1h_pct","ethbtc_open","ethbtc_high","ethbtc_low","ethbtc_close","ethbtc_return_1h_pct","ethbtc_range_1h_pct","btc_open_interest","btc_open_interest_value","btc_oi_change_1h_pct","eth_open_interest","eth_open_interest_value","eth_oi_change_1h_pct","btc_long_short_ratio","btc_long_account","btc_short_account","eth_long_short_ratio","eth_long_account","eth_short_account","btc_funding_event_rate","eth_funding_event_rate","btc_price_oi_state","eth_price_oi_state","spot_status","derivatives_status"]
class E(RuntimeError):
 def __init__(s,status,msg):super().__init__(msg);s.status=status
def h(b):return hashlib.sha256(b).hexdigest()
def iso(d):return d.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def ms(d):return int(d.timestamp()*1000)
def hr(x):return x-x%3600000
def url(base,p):return base+"?"+urllib.parse.urlencode(p)
def get(u):
 r=urllib.request.Request(u,headers={"User-Agent":"Investering-Hourly-Sequence/2.0","Accept":"application/json"})
 try:
  with urllib.request.urlopen(r,timeout=15) as q:b=q.read()
 except urllib.error.HTTPError as x:
  body=x.read().decode("utf-8","replace");raise E("GEO_RESTRICTED" if x.code in(403,451) or "restricted location" in body.lower() else "HTTP_ERROR",f"HTTP {x.code}: {body[:200]}") from x
 except Exception as x:raise E("NETWORK_ERROR",str(x)) from x
 if not b:raise E("EMPTY_RESPONSE","empty response")
 return b
def doc(b):
 try:v=json.loads(b)
 except Exception as x:raise E("SCHEMA_DRIFT","invalid JSON") from x
 if isinstance(v,dict) and("code" in v or "msg" in v):raise E("SOURCE_ERROR",str(v.get("msg",v)))
 return v
def spot(b,s):
 v=doc(b);o={}
 if not isinstance(v,list):raise E("SCHEMA_DRIFT",s)
 for i,r in enumerate(v):
  if not isinstance(r,list) or len(r)<12:raise E("SCHEMA_DRIFT",f"{s}:{i}")
  try:t=hr(int(r[0]));op,hi,lo,cl,vol=map(float,r[1:6])
  except Exception as x:raise E("SCHEMA_DRIFT",f"{s}:{i}:numeric") from x
  if hi<max(op,cl) or lo>min(op,cl):raise E("INVALID_OHLC",f"{s}:{i}")
  o[t]={"open":op,"high":hi,"low":lo,"close":cl,"volume":vol}
 return o
def oi(b,s):
 o={}
 for i,r in enumerate(doc(b)):
  try:o[hr(int(r["timestamp"]))]={"oi":float(r["sumOpenInterest"]),"value":float(r.get("sumOpenInterestValue") or 0)}
  except Exception as x:raise E("SCHEMA_DRIFT",f"{s}:oi:{i}") from x
 return o
def ls(b,s):
 o={}
 for i,r in enumerate(doc(b)):
  try:o[hr(int(r["timestamp"]))]={"ratio":float(r["longShortRatio"]),"long":float(r["longAccount"]),"short":float(r["shortAccount"])}
  except Exception as x:raise E("SCHEMA_DRIFT",f"{s}:ls:{i}") from x
 return o
def fund(b,s):
 o={}
 for i,r in enumerate(doc(b)):
  try:o[hr(int(r["fundingTime"]))]=float(r["fundingRate"])
  except Exception as x:raise E("SCHEMA_DRIFT",f"{s}:fund:{i}") from x
 return o
def pc(a,b):return None if a is None or b in(None,0) else(a/b-1)*100
def rg(a,b):return None if a is None or b in(None,0) else(a/b-1)*100
def fmt(v):return "" if v is None or(isinstance(v,float) and(math.isnan(v) or math.isinf(v))) else format(v,".12g") if isinstance(v,float) else str(v)
def st(p,o):
 if p is None or o is None:return "UNAVAILABLE"
 if p<0<o:return "PRICE_DOWN_OI_UP"
 if p>0>o:return "PRICE_UP_OI_DOWN"
 if p>0 and o>0:return "PRICE_UP_OI_UP"
 if p<0 and o<0:return "PRICE_DOWN_OI_DOWN"
 return "MIXED_FLAT"
def grab(fix,name,u):
 try:
  b=(fix/name).read_bytes() if fix else get(u);return "PASS",b,None
 except E as x:return x.status,None,str(x)
 except OSError as x:return "MISSING_FIXTURE",None,str(x)
def merge(root,rows):
 touched=[];g={}
 for r in rows:g.setdefault(r["timestamp_utc"][:10],[]).append(r)
 for day,inc in g.items():
  p=root/day[:4]/day[5:7]/f"{day}.csv";p.parent.mkdir(parents=True,exist_ok=True);old={}
  if p.exists():
   with p.open(newline="",encoding="utf-8") as q:
    for r in csv.DictReader(q):
     if r.get("timestamp_utc"):old[r["timestamp_utc"]]=r
  for n in inc:
   k=n["timestamp_utc"];q=old.get(k,{});z={}
   for x in F:
    nv=fmt(n.get(x));z[x]=nv if nv!="" else q.get(x,"")
   old[k]=z
  with p.open("w",newline="",encoding="utf-8") as q:
   w=csv.DictWriter(q,fieldnames=F);w.writeheader();w.writerows(old[k] for k in sorted(old))
  touched.append(p.as_posix())
 return touched
def rows(start,end,S,O,L,U,ss,ds):
 out=[];prev={s:None for s in SS};po={s:None for s in FS};d=start
 while d<=end:
  t=ms(d);r={"timestamp_utc":iso(d),"timestamp_copenhagen":d.astimezone(TZ).replace(microsecond=0).isoformat(),"source_window_end_utc":iso(end+timedelta(hours=1)),"spot_status":ss,"derivatives_status":ds}
  for s,p in(("BTCUSDT","btc"),("ETHUSDT","eth"),("ETHBTC","ethbtc")):
   c=S.get(s,{}).get(t)
   if c:
    for k in("open","high","low","close"):r[f"{p}_{k}"]=c[k]
    if p!="ethbtc":r[f"{p}_volume"]=c["volume"]
    r[f"{p}_return_1h_pct"]=pc(c["close"],prev[s] or c["open"]);r[f"{p}_range_1h_pct"]=rg(c["high"],c["low"]);prev[s]=c["close"]
  for s,p in(("BTCUSDT","btc"),("ETHUSDT","eth")):
   x=O.get(s,{}).get(t)
   if x:r[f"{p}_open_interest"]=x["oi"];r[f"{p}_open_interest_value"]=x["value"];r[f"{p}_oi_change_1h_pct"]=pc(x["oi"],po[s]);po[s]=x["oi"]
   x=L.get(s,{}).get(t)
   if x:r[f"{p}_long_short_ratio"]=x["ratio"];r[f"{p}_long_account"]=x["long"];r[f"{p}_short_account"]=x["short"]
   if t in U.get(s,{}):r[f"{p}_funding_event_rate"]=U[s][t]
   r[f"{p}_price_oi_state"]=st(r.get(f"{p}_return_1h_pct"),r.get(f"{p}_oi_change_1h_pct"))
  out.append(r);d+=timedelta(hours=1)
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--output-root",type=Path,required=True);ap.add_argument("--raw-output",type=Path,required=True);ap.add_argument("--lookback-hours",type=int,default=14);ap.add_argument("--retrieval-timestamp");ap.add_argument("--fixture-dir",type=Path);a=ap.parse_args()
 now=datetime.fromisoformat(a.retrieval_timestamp.replace("Z","+00:00")) if a.retrieval_timestamp else datetime.now(timezone.utc);now=now.astimezone(timezone.utc);end=now.replace(minute=0,second=0,microsecond=0)-timedelta(hours=1);start=end-timedelta(hours=max(1,a.lookback_hours)-1);sm,em=ms(start),ms(end+timedelta(hours=1))-1;a.raw_output.mkdir(parents=True,exist_ok=True)
 S={};O={};L={};U={};rec=[];sf=df=0
 for s in SS:
  u=url(SPOT,{"symbol":s,"interval":"1h","startTime":sm,"endTime":em,"limit":1000});q,b,e=grab(a.fixture_dir,f"{s}_spot.json",u);x={"name":f"{s}_spot","status":q,"url":u,"error":e}
  if b:
   p=a.raw_output/f"{s}_spot.json";p.write_bytes(b);x.update(bytes=len(b),sha256=h(b))
   try:S[s]=spot(b,s);x["row_count"]=len(S[s])
   except E as z:x.update(status=z.status,error=str(z));sf+=1
  else:sf+=1
  rec.append(x)
 for s in FS:
  qs={"oi":("/futures/data/openInterestHist",{"symbol":s,"period":"1h","startTime":sm,"endTime":em,"limit":500}),"long_short":("/futures/data/globalLongShortAccountRatio",{"symbol":s,"period":"1h","startTime":sm,"endTime":em,"limit":500}),"funding":("/fapi/v1/fundingRate",{"symbol":s,"startTime":sm,"endTime":em,"limit":1000})}
  for k,(path,pms) in qs.items():
   u=url(FUT+path,pms);q,b,e=grab(a.fixture_dir,f"{s}_{k}.json",u);x={"name":f"{s}_{k}","status":q,"url":u,"error":e}
   if b:
    (a.raw_output/f"{s}_{k}.json").write_bytes(b);x.update(bytes=len(b),sha256=h(b))
    try:
     v=oi(b,s) if k=="oi" else ls(b,s) if k=="long_short" else fund(b,s);({"oi":O,"long_short":L,"funding":U}[k])[s]=v;x["row_count"]=len(v)
    except E as z:x.update(status=z.status,error=str(z));df+=1
   else:df+=1
   rec.append(x)
 ss="PASS" if sf==0 else "PARTIAL" if S else "FAIL";groups=sum(bool(O.get(s)) for s in FS)+sum(bool(L.get(s)) for s in FS);ds="PASS" if df==0 else "PARTIAL" if groups else "UNAVAILABLE";R=rows(start,end,S,O,L,U,ss,ds);paths=merge(a.output_root,R);n=len(R);sc=sum(r.get("btc_close") is not None and r.get("eth_close") is not None and r.get("ethbtc_close") is not None for r in R);dc=sum(r.get("btc_open_interest") is not None and r.get("eth_open_interest") is not None for r in R);status="COMPLETE" if sc==n and ds=="PASS" else "PARTIAL" if sc else "FAILED";rid="HOURLY_SEQUENCE_"+now.strftime("%Y%m%dT%H%M%SZ")+"_"+h(json.dumps(rec,sort_keys=True).encode())[:12]
 m={"contract":"HOURLY_SEQUENCE_CAPTURE_v2","run_id":rid,"retrieved_at_utc":iso(now),"window_start_utc":iso(start),"window_end_utc":iso(end+timedelta(hours=1)),"requested_hours":n,"spot_complete_hours":sc,"derivatives_oi_complete_hours":dc,"status":status,"spot_status":ss,"derivatives_status":ds,"interpolation":False,"forward_fill":False,"permanent_outputs":paths,"source_records":rec,"authority":A};rd=a.output_root/"runs"/now.strftime("%Y/%m/%d");rd.mkdir(parents=True,exist_ok=True);rp=rd/f"{now:%H%M%S}_{rid}.json";rp.write_text(json.dumps(m,indent=2,sort_keys=True)+"\n");(a.output_root/"LATEST.json").write_text(json.dumps({"contract":"HOURLY_SEQUENCE_LATEST_POINTER_v1","run_id":rid,"run_path":rp.as_posix(),"retrieved_at_utc":m["retrieved_at_utc"],"window_start_utc":m["window_start_utc"],"window_end_utc":m["window_end_utc"],"status":status,"spot_complete_hours":sc,"requested_hours":n},indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"run_id":rid,"hours":n,"spot_complete_hours":sc,"derivatives_oi_complete_hours":dc},sort_keys=True));raise SystemExit(2 if sc==0 else 0)
if __name__=="__main__":main()
