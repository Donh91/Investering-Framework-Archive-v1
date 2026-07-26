import pandas as pd, numpy as np, json
exec(open('engine.py').read().split('rows=[]; Q=')[0])
D='../data/'; R='../results/'
g=pd.read_csv(R+'grid_all.csv',parse_dates=['s13','r15','s17','r19','s21','r22','s25','r26'])
ok=g[g.miss==0].sort_values('score').reset_index(drop=True)

print("=== FULL-GRID robusthed (alle 3240 konfig. med 7/7 signaler) ===")
print(ok.stage_now.value_counts().to_string())
print(f"RE_FIRED-andel: {(ok.stage_now=='RE_FIRED').mean():.1%} | median osc_now {ok.osc_now.median():.1f}")

print("\n=== FAMILIE-BIDRAG: bedste resemblance-score pr. familie ===")
for col in ['cur','wf','h','L','rrp']:
    print(g.groupby(col)['score'].min().round(0).to_string(),"\n")

def buildS(cols,cur='B_usd',rrp='avg',h=13,L=52,wf='EQ',Es=26):
    rser={'wed':rrp_wed,'avg':rrp_avg,'last':rrp_last}[rrp]
    X=pd.DataFrame(dict(fed=base.fed,tga=base.tga,rrp=rser,
        ecb=(base.ecb_n if cur=='A_native' else base.ecb_u),
        boj=(base.boj_n if cur=='A_native' else base.boj_u)))[list(cols)]
    dd=X.diff(h); z=(dd-dd.rolling(L,min_periods=26).mean())/dd.rolling(L,min_periods=26).std()
    C=sum(SIGN[c]*z[c] for c in cols)
    return C.ewm(span=Es,adjust=False).mean()

S=buildS(['fed','ecb','boj','tga','rrp'])
Sp=S[S>0].dropna(); hi=np.quantile(Sp,0.55)
print("=== ARCTAN-KOSMETIK (numerisk) ===")
lam=np.tan(0.86*np.pi/2)/hi
osc=100*(2/np.pi)*np.arctan(lam*S)
def crossdates(x,th):
    v=x.values; t=x.index
    return [t[i] for i in range(1,len(v)) if not np.isnan(v[i-1]) and v[i-1]>=th>v[i]]
a=crossdates(S,hi); b_=crossdates(osc,86.0)
print(f"  downcross-datoer S vs osc(86): identiske = {a==b_} (n={len(a)})  -> arctan ændrer INTET signal")

print("\n=== HALVING-MASKENS ARBEJDE (TOP-1 S) ===")
lo=-RATIO*hi
raw=len(crossdates(S,hi))+len(crossdates(-S,-lo))
res=machine(S,hi); masked=sum(1 for r in res for k in ['sell','re'] if r[k] is not None)
print(f"  rå tærskelkryds i serien: {raw} | efter halving-maske: {masked}  -> masken sletter {raw-masked} ({1-masked/raw:.0%})")

print("\n=== KOMPONENT-ABLATION (TOP-1 params, q re-scannet, resemblance-score) ===")
sets={'FED_ONLY':['fed'],'US_NET (fed-tga-rrp)':['fed','tga','rrp'],
      'CB3 (fed+ecb+boj)':['fed','ecb','boj'],'ALL5 (base)':['fed','ecb','boj','tga','rrp'],
      'NO_BOJ (fed+ecb-tga-rrp)':['fed','ecb','tga','rrp']}
for name,cols in sets.items():
    S2=buildS(cols); Sp2=S2[S2>0].dropna(); best=None
    for q in [.55,.65,.75,.82,.90]:
        h2=np.quantile(Sp2,q); sat=np.nanmean(np.abs(S2.values)>RATIO*h2)
        if sat<0.45: continue
        r2=machine(S2,h2); sc,miss=score(r2)
        if best is None or (miss,sc)<(best[0],best[1]): best=(miss,sc,q,r2[3]['stage'],r2)
    if best:
        miss,sc,q,st,r2=best; s25=r2[3]['sell']
        print(f"  {name:26s} miss={miss} score={sc:6.1f} (q={q}) 2025-sell={str(s25.date()) if s25 else '—'} stage_nu={st}")
    else: print(f"  {name:26s} shape-gate FAIL")

print("\n=== SHARPE-FORDELING over ALLE 3240 maskerede konfigurationer (ingen selektion) ===")
k=json.load(open(D+'kraken_btc_w.json')); kk=[x for x in k['result'] if x!='last'][0]
bb=pd.DataFrame(k['result'][kk],columns=['t','o','h','l','c','v','vw','n'])
bb['close_dt']=pd.to_datetime(bb.t.astype(int),unit='s')+pd.Timedelta(days=7)
cl=bb.c.astype(float).values[:-1]; ct=bb.close_dt.values[:-1]
r1=np.diff(np.log(cl))
def idx(d): return int(np.searchsorted(ct,np.datetime64(pd.Timestamp(d))))
sh=[]
for _,row in ok.iterrows():
    inm=np.zeros(len(cl),bool); prev=0
    for s,r in [(row.s13,row.r15),(row.s17,row.r19),(row.s21,row.r22),(row.s25,row.r26 if pd.notna(row.r26) else None)]:
        i_s=idx(s); inm[prev:i_s]=True; prev=idx(r) if (r is not None and pd.notna(r)) else len(cl)-1
    st=r1*inm[:-1]
    if st.std()>0: sh.append(st.mean()*52/(st.std()*np.sqrt(52)))
sh=np.array(sh)
print(f"  n={len(sh)}  median Sharpe {np.median(sh):.2f}  p10 {np.percentile(sh,10):.2f}  p90 {np.percentile(sh,90):.2f}")
print(f"  andel > hold(0.66): {(sh>0.66).mean():.0%}   andel > 40W-MA(0.87): {(sh>0.87).mean():.0%}")
json.dump(dict(sharpe_median=float(np.median(sh)),beat_hold=float((sh>0.66).mean()),beat_ma=float((sh>0.87).mean())),open(R+'sharpe_dist.json','w'))
