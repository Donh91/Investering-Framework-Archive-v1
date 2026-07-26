"""GCBLO reconstruction engine — FROZEN PROTOCOL per ChatGPT governance spec.
Label: RECONSTRUCTED_CHALLENGER_NOT_ORIGINAL_GCBLO
Freeze (declared BEFORE any BTC-outcome evaluation):
  grid: h in {1,4,13,26,52}w; zwin L in {26,52,104,156}w rolling; EMA E in {4,8,13,26,52}w;
        weights in {EQ,GDP,USDSHARE,INVVOL}; currency in {A_native,B_usd}; RRP in {wed,avg,last};
        TGA: wed only (WDTGAL BLOCKED_EGRESS); thresholds via q in {.55,.65,.75,.82,.90} on S+.
  S_hi = quantile(S>0,q); S_lo = -0.6908*S_hi   [ratio fixed by tan(0.8*pi/2)/tan(0.86*pi/2)]
  shape gate: frac(|S|>0.6908*S_hi) >= 0.45
  state machine (his Steps 1-4, halving-masked): arm S>hi -> SELL first downcross hi ->
        must reach S<lo -> RE first upcross lo. One sell+re max per halving cycle.
  anchors (from his July-2026 weekly chart): SELL 2013-12-23, 2017-11-27, 2021-03-15, 2025-09-15;
        RE 2015-01-05, 2019-01-14, 2022-06-27.  2026 RE candidate NOT scored (that is the claim under test).
  score = sum |weeks diff| over 7 anchors, +52 per missing. PASS bar: score<=45 & no missing.
Selection criterion = resemblance to displayed oscillator ONLY. No BTC data enters this file."""
import pandas as pd, numpy as np, json, itertools, sys
D='../data/'
def fred(s):
    d=pd.read_csv(D+s+'.csv'); d.columns=['dt','v']; d['dt']=pd.to_datetime(d['dt'])
    d['v']=pd.to_numeric(d['v'],errors='coerce'); return d.set_index('dt')['v'].dropna()
W=fred('WALCL'); T=fred('WTREGEN'); Rd=fred('RRPONTSYD')
E_=fred('ECBASSETSW'); J=fred('JPNASSETS'); eur=fred('DEXUSEU'); jpy=fred('DEXJPUS')
idx=pd.date_range('2005-01-05','2026-07-22',freq='W-WED')
ffill=lambda s: s.reindex(s.index.union(idx)).ffill().reindex(idx)
rrp_wed=ffill(Rd)*1000
rrp_avg=(Rd.resample('W-WED').mean()*1000).reindex(idx).ffill()
rrp_last=(Rd.resample('W-WED').last()*1000).reindex(idx).ffill()
base=pd.DataFrame(dict(fed=ffill(W),tga=ffill(T),ecb_n=ffill(E_),boj_n=ffill(J),
                       eur=ffill(eur),jpy=ffill(jpy)))
base['ecb_u']=base.ecb_n*base.eur; base['boj_u']=base.boj_n*100/base.jpy
SIGN=dict(fed=1,ecb=1,boj=1,tga=-1,rrp=-1)
GDPW=dict(fed=.55,ecb=.33,boj=.12,tga=.55,rrp=.55)
def weights(fam,dfU):
    if fam=='EQ': return {c:1. for c in SIGN}
    if fam=='GDP': return dict(GDPW)
    m={c:np.nanmean(np.abs(dfU[c])) for c in SIGN}
    if fam=='USDSHARE':
        s=sum(m.values()); return {c:5*m[c]/s for c in SIGN}
    if fam=='INVVOL':
        v={c:np.nanstd(np.diff(dfU[c].dropna())) for c in SIGN}
        iv={c:1/v[c] for c in SIGN}; s=sum(iv.values()); return {c:5*iv[c]/s for c in SIGN}
HALV=[pd.Timestamp(x) for x in ['2012-11-28','2016-07-09','2020-05-11','2024-04-20']]
SELL_A=[pd.Timestamp(x) for x in ['2013-12-23','2017-11-27','2021-03-15','2025-09-15']]
RE_A=[pd.Timestamp(x) for x in ['2015-01-05','2019-01-14','2022-06-27']]
RATIO=np.tan(0.8*np.pi/2)/np.tan(0.86*np.pi/2)
def machine(S,hi):
    lo=-RATIO*hi; t=S.index; v=S.values; out=[]
    ends=HALV[1:]+[t[-1]+pd.Timedelta(weeks=1)]
    for ci,(H,Hn) in enumerate(zip(HALV,ends)):
        m=(t>=H)&(t<Hn); vv=v[m]; tt=t[m]
        armed=sold=below=False; sd=rd=None; stage='NOT_ARMED'
        for i in range(1,len(vv)):
            if np.isnan(vv[i]) or np.isnan(vv[i-1]): continue
            if not armed and vv[i]>hi: armed=True; stage='ARMED_ABOVE'
            if armed and not sold and vv[i-1]>=hi>vv[i]: sold=True; sd=tt[i]; stage='SOLD_ABOVE_LO'
            if sold and not below and vv[i]<lo: below=True; stage='IN_STAYOUT'
            if below and rd is None and vv[i-1]<=lo<vv[i]: rd=tt[i]; stage='RE_FIRED'
        out.append(dict(cycle=ci,sell=sd,re=rd,stage=stage))
    return out
def score(res):
    s=0; miss=0
    for ci,sa in enumerate(SELL_A):
        sd=res[ci]['sell']
        if sd is None: s+=52; miss+=1
        else: s+=abs((sd-sa).days)/7
    for ci,ra in enumerate(RE_A):
        rd=res[ci]['re']
        if rd is None: s+=52; miss+=1
        else: s+=abs((rd-ra).days)/7
    return s,miss
rows=[]; Q=[.55,.65,.75,.82,.90]
for cur in ['A_native','B_usd']:
    dfU=pd.DataFrame(dict(fed=base.fed,ecb=base.ecb_u,boj=base.boj_u,tga=base.tga,rrp=rrp_wed))
    for rv,rser in [('wed',rrp_wed),('avg',rrp_avg),('last',rrp_last)]:
        X=pd.DataFrame(dict(fed=base.fed,tga=base.tga,rrp=rser,
             ecb=(base.ecb_n if cur=='A_native' else base.ecb_u),
             boj=(base.boj_n if cur=='A_native' else base.boj_u)))
        for h in [1,4,13,26,52]:
            dd=X.diff(h)
            for L in [26,52,104,156]:
                mu=dd.rolling(L,min_periods=max(26,L//2)).mean()
                sg=dd.rolling(L,min_periods=max(26,L//2)).std()
                z=(dd-mu)/sg
                for wf in ['EQ','GDP','USDSHARE','INVVOL']:
                    wts=weights(wf,dfU)
                    C=sum(SIGN[c]*wts[c]*z[c] for c in SIGN)
                    for Es in [4,8,13,26,52]:
                        S=C.ewm(span=Es,adjust=False).mean()
                        Sp=S[S>0].dropna()
                        if len(Sp)<50: continue
                        for q in Q:
                            hi=np.quantile(Sp,q)
                            sat=np.nanmean(np.abs(S.values)>RATIO*hi)
                            if sat<0.45: continue
                            res=machine(S,hi)
                            sc,miss=score(res)
                            cur_stage=res[3]['stage']; margin=(S.iloc[-1]-(-RATIO*hi))/(RATIO*hi)
                            lam=np.tan(0.86*np.pi/2)/hi
                            osc_now=100*(2/np.pi)*np.arctan(lam*S.iloc[-1])
                            rows.append(dict(cur=cur,rrp=rv,h=h,L=L,wf=wf,E=Es,q=q,sat=round(sat,3),
                                score=round(sc,1),miss=miss,
                                s13=res[0]['sell'],r15=res[0]['re'],s17=res[1]['sell'],r19=res[1]['re'],
                                s21=res[2]['sell'],r22=res[2]['re'],s25=res[3]['sell'],r26=res[3]['re'],
                                stage_now=cur_stage,S_now=round(float(S.iloc[-1]),3),
                                margin_vs_lo=round(float(margin),3),osc_now=round(float(osc_now),1)))
df=pd.DataFrame(rows)
df.to_csv('../results/grid_all.csv',index=False)
print("configs evaluated (post shape-gate):",len(df))
ok=df[df.miss==0].sort_values('score')
print("configs with all 7 anchors matched:",len(ok))
PASS=ok[ok.score<=45]
print("RESEMBLANCE_PASS (score<=45, no miss):",len(PASS))
print("\nTOP 12 by resemblance:")
cols=['cur','rrp','h','L','wf','E','q','sat','score','s13','r15','s17','r19','s21','r22','s25','stage_now','osc_now']
print(ok.head(12)[cols].to_string(index=False))
print("\n=== KEY STAT: current cycle-4 state among RESEMBLANCE_PASS ===")
if len(PASS):
    print(PASS.stage_now.value_counts().to_string())
    print("RE_FIRED share:",f"{(PASS.stage_now=='RE_FIRED').mean():.1%}")
    print("osc_now: median",PASS.osc_now.median()," p10..p90:",PASS.osc_now.quantile(.1),"..",PASS.osc_now.quantile(.9))
    print("2025 SELL date distribution (PASS):")
    print(PASS.s25.dt.date.value_counts().head(8).to_string())
PASS.to_csv('../results/grid_pass.csv',index=False)
print("\nwidest bar: top-50 by score regardless of PASS:")
print(ok.head(50).stage_now.value_counts().to_string())
