import pandas as pd, numpy as np, json
D='../data/'; R='../results/'
g=pd.read_csv(R+'grid_all.csv',parse_dates=['s13','r15','s17','r19','s21','r22','s25','r26'])
ok=g[g.miss==0].sort_values('score').reset_index(drop=True)
top50=ok.head(50)
print("=== ANCHOR-DECOMPOSED ERROR (median |weeks| over best-50) ===")
A=dict(s13='2013-12-23',r15='2015-01-05',s17='2017-11-27',r19='2019-01-14',
       s21='2021-03-15',r22='2022-06-27',s25='2025-09-15')
for c,a in A.items():
    e=(top50[c]-pd.Timestamp(a)).dt.days.abs()/7
    print(f"  {c}: median {e.median():5.1f}w  p25-p75 {e.quantile(.25):.0f}-{e.quantile(.75):.0f}w")
k=json.load(open(D+'kraken_btc_w.json'))
kk=[x for x in k['result'] if x!='last'][0]
b=pd.DataFrame(k['result'][kk],columns=['t','o','h','l','c','v','vw','n']).astype({'t':int})
b['open_dt']=pd.to_datetime(b.t,unit='s'); b['close_dt']=b.open_dt+pd.Timedelta(days=7)
b[['o','h','l','c']]=b[['o','h','l','c']].astype(float)
b=b.iloc[:-1]
print(f"\nBTC settled weekly: {b.open_dt.iloc[0].date()} .. close {b.close_dt.iloc[-1].date()}  last_close={b.c.iloc[-1]:,.1f} [UTC-basis, cross-check ikke ledger]")
ct=b.close_dt.values; cl=b.c.values; hi=b.h.values; lo=b.l.values
def px(d):
    i=np.searchsorted(ct,np.datetime64(pd.Timestamp(d)))
    return (None if i>=len(cl) else float(cl[i]), i)
def fwd(i,wk):
    j=i+wk; return None if j>=len(cl) else float(cl[j]/cl[i]-1)
def mfe_mae(i,wk):
    j=min(len(cl)-1,i+wk)
    return float(hi[i+1:j+1].max()/cl[i]-1) if j>i else None, float(lo[i+1:j+1].min()/cl[i]-1) if j>i else None
CH_S=[('2013-12-23','2015-01-05'),('2017-11-27','2019-01-14'),('2021-03-15','2022-06-27'),('2025-09-15',None)]
print("\n=== STEELMAN: outcomes of HIS chart-anchor dates (as if original signals) ===")
print("SELL events:")
for s,r in CH_S:
    ps,i=px(s)
    seg_end = px(r)[1] if r else len(cl)-1
    fmax=float(hi[i+1:seg_end+1].max()) if seg_end>i else ps
    fmin=float(lo[i+1:seg_end+1].min()) if seg_end>i else ps
    line=f"  SELL {s}: px≈{ps:>9,.0f} | later-high-before-RE {fmax/ps-1:+7.1%} | avoided-low {fmin/ps-1:+7.1%}"
    if r:
        pr,j=px(r); line+=f" | RE {r} px≈{pr:>8,.0f} | roundtrip exit->re {ps/pr-1:+.1%} bedre end hold | uger ude {(j-i)}"
    print(line)
print("RE events (entry quality):")
for _,r in CH_S:
    if not r: continue
    pr,j=px(r)
    f4,f12,f26,f52=fwd(j,4),fwd(j,12),fwd(j,26),fwd(j,52)
    fe,ma=mfe_mae(j,26)
    print(f"  RE {r}: px≈{pr:>8,.0f} fwd4 {f4:+.1%} fwd12 {f12:+.1%} fwd26 {f26:+.1%} fwd52 {f52:+.1%} | MFE26 {fe:+.1%} MAE26 {ma:+.1%}")
print("\n=== TOP-1 reconstruction dates vs chart anchors (label: RECONSTRUCTED, NOT ORIGINAL) ===")
t1=ok.iloc[0]
print(t1[['cur','rrp','h','L','wf','E','q','sat','score','s13','r15','s17','r19','s21','r22','s25','stage_now','osc_now']].to_string())
print("\n=== STRATEGY BATTERY (settled weekly, 2013-10 .. 2026-07) ===")
r1=np.diff(np.log(cl))
def strat(pairs,name):
    inmkt=np.zeros(len(cl),bool); segs=[]; prev_re=0
    for s,r in pairs:
        i_s=px(s)[1]; segs.append((prev_re,i_s)); prev_re=px(r)[1] if r else len(cl)-1
    for a,bnd in segs: inmkt[a:bnd]=True
    st=r1*inmkt[:-1]
    mu,sd=st.mean()*52,st.std()*np.sqrt(52)
    eq=st.cumsum(); dd=(eq-np.maximum.accumulate(eq)).min()
    print(f"  {name:32s} tid-i-mkt {inmkt.mean():4.0%}  CAGR~{np.exp(mu)-1:+7.1%}  Sharpe {mu/sd:5.2f}  maxDD(log) {dd:6.2f}")
mu,sd=r1.mean()*52,r1.std()*np.sqrt(52)
eq=r1.cumsum(); print(f"  {'BUY&HOLD':32s} tid-i-mkt 100%  CAGR~{np.exp(mu)-1:+7.1%}  Sharpe {mu/sd:5.2f}  maxDD(log) {(eq-np.maximum.accumulate(eq)).min():6.2f}")
strat(CH_S,'GCBLO chart-anker (steelman)')
strat([(t1.s13,t1.r15),(t1.s17,t1.r19),(t1.s21,t1.r22),(t1.s25,None)],'TOP-1 rekonstruktion')
ma40=pd.Series(cl).rolling(40).mean().values
sig=(cl>ma40); st=r1*sig[:-1]
mu,sd=st.mean()*52,st.std()*np.sqrt(52); eq=st.cumsum()
print(f"  {'40W-MA trendregel (ingen makro)':32s} tid-i-mkt {sig.mean():4.0%}  CAGR~{np.exp(mu)-1:+7.1%}  Sharpe {mu/sd:5.2f}  maxDD(log) {(eq-np.maximum.accumulate(eq)).min():6.2f}")
print("\n=== TRANSMISSION 3-LAG (L2=DXY-ben; kreditben BLOCKED) ===")
dx=pd.read_csv(D+'DTWEXBGS.csv'); dx.columns=['dt','v']; dx['dt']=pd.to_datetime(dx.dt)
dx['v']=pd.to_numeric(dx.v,errors='coerce'); dxw=dx.set_index('dt').v.dropna().resample('W-WED').last().ffill()
dch=dxw.diff(13)
for _,r in CH_S:
    if not r: continue
    rT=pd.Timestamp(r); pr,j=px(r)
    l2=dch[(dch.index>=rT)&(dch<0)].index.min()
    okma=(cl>ma40); l3=None
    for i2 in range(j,len(cl)-1):
        if okma[i2] and okma[i2+1]: l3=b.close_dt.iloc[i2+1]; break
    j3=px(l3)[1] if l3 is not None else None
    f26_re=fwd(j,26); _,mae_re=mfe_mae(j,26)
    if j3:
        f26_l3=fwd(j3,26); _,mae_l3=mfe_mae(j3,26)
        print(f"  RE {r}: L2(DXY) {str(l2.date())} (+{int((l2-rT).days/7)}w)  L3(pris) {str(l3.date())} (+{int((pd.Timestamp(l3)-rT).days/7)}w) | fwd26 RE {f26_re:+.1%} vs L3 {f26_l3:+.1%} | MAE26 RE {mae_re:+.1%} vs L3 {mae_l3:+.1%}")
print(f"  NU: DXY Δ13w = {dch.iloc[-1]:+.2f} ({'L2 PASS' if dch.iloc[-1]<0 else 'L2 FAIL'}) | BTC {cl[-1]:,.0f} vs 40W-MA {ma40[-1]:,.0f} -> L3 {'PASS' if cl[-1]>ma40[-1] else 'FAIL'}")
print("\n=== LOCO (leave-one-cycle-out på resemblance-ranking) ===")
def sc_wo(row,drop):
    s=0
    pairs={1:('s13','2013-12-23','r15','2015-01-05'),2:('s17','2017-11-27','r19','2019-01-14'),3:('s21','2021-03-15','r22','2022-06-27')}
    for c,(sc_,sa,rc,ra) in pairs.items():
        if c==drop: continue
        s+=abs((row[sc_]-pd.Timestamp(sa)).days)/7+abs((row[rc]-pd.Timestamp(ra)).days)/7
    s+=abs((row['s25']-pd.Timestamp('2025-09-15')).days)/7
    return s
for drop in [1,2,3]:
    ok2=ok.copy(); ok2['sc2']=ok2.apply(lambda r: sc_wo(r,drop),axis=1)
    b1=ok2.sort_values('sc2').iloc[0]
    pairs={1:('s13','2013-12-23','r15','2015-01-05'),2:('s17','2017-11-27','r19','2019-01-14'),3:('s21','2021-03-15','r22','2022-06-27')}
    sc_,sa,rc,ra=pairs[drop]
    es=abs((b1[sc_]-pd.Timestamp(sa)).days)/7; er=abs((b1[rc]-pd.Timestamp(ra)).days)/7
    print(f"  drop cyklus {drop}: ny top-1 held-out fejl SELL {es:.0f}w, RE {er:.0f}w  (cfg {b1.cur}/{b1.rrp}/h{b1.h}/L{b1.L}/{b1.wf}/E{b1.E}/q{b1.q})")
