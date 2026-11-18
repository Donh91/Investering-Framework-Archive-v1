"""Offline historical research replay. No network or production authority."""
import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

HOUR = 3600000
DAY = 24 * HOUR
HORIZONS = ((12, .015), (24, .025), (72, .04))
A_METHODS = ('static_rate', 'expanding_rate', 'rolling7', 'rolling30', 'rolling90', 'ewma7', 'ewma30', 'mix', 'fixed_price', 'fixed_flow', 'rebase_price', 'rebase_flow', 'recal_price', 'recal_flow')
B_METHODS = ('fixed', 'rolling30_full', 'rolling30_nonoverlap', 'ewma7_nonoverlap', 'ewma30_nonoverlap', 'mix_nonoverlap', 'conditional_vol', 'shock_blend', 'online_experts')


def utc(year, month=1, day=1):
    return int(datetime(year, month, day, tzinfo=timezone.utc).timestamp() * 1000)


def spec(year):
    if year not in (2024, 2025, 2026):
        raise ValueError('UNSUPPORTED_YEAR')
    return dict(year=year, start=utc(year), end=utc(2026, 11, 17) if year == 2026 else utc(year + 1))


def mean(xs):
    return sum(xs) / len(xs)


def rms(xs):
    return math.sqrt(mean([x*x for x in xs]))


def clip(p):
    return max(.005, min(.995, p))


def sig(x):
    return 1 / (1 + math.exp(-max(-35, min(35, x))))


def logit(p):
    p = clip(p)
    return math.log(p / (1-p))


def quant(xs, p):
    if not xs:
        raise ValueError('NO_QUANTILE_SAMPLE')
    return sorted(xs)[max(0, min(len(xs)-1, math.ceil(p*len(xs))-1))]


def validate_bars(raw, s):
    n = len(raw)
    expected = (s['end']-s['start']) // HOUR
    if any(not isinstance(r, list) or len(r) != 12 for r in raw):
        raise ValueError('SOURCE_SHAPE')
    if any(type(r[0]) is not int or type(r[6]) is not int for r in raw):
        raise ValueError('SOURCE_CLOCK_TYPE')
    dup = n-len({r[0] for r in raw})
    grid = sum(r[0] != s['start']+i*HOUR or r[6] != r[0]+HOUR-1 for i,r in enumerate(raw))
    bad = 0
    for r in raw:
        try:
            if any(isinstance(r[k], bool) for k in (4,7,10)):
                raise ValueError('BOOLEAN_VALUE')
            c,v,u = map(float,(r[4],r[7],r[10]))
            bad += not (all(map(math.isfinite,(c,v,u))) and c>0 and v>0 and 0<=u<=v)
        except (ValueError,TypeError,OverflowError):
            bad += 1
    q = dict(n=n, expected=expected, duplicates=dup, grid=grid, bad=bad)
    if n!=expected or dup or grid or bad:
        raise ValueError('SOURCE_INVALID '+json.dumps(q))
    return q


def create_rows(raw,s,h,bar):
    c,v,u = ([float(r[k]) for r in raw] for k in (4,7,10))
    ret = [0.] + [math.log(c[i]/c[i-1]) for i in range(1,len(c))]
    out=[]
    for i in range(len(c)-h):
        t=s['start']+(i+1)*HOUR
        j=i-4
        if j<240 or t%(6*HOUR):
            continue
        vol=max(1e-8,rms(ret[j-47:j+1])); short=rms(ret[j-5:j+1]); q=sum(v[j-5:j+1])
        y=int(any(c[k]<=c[i+1]*(1-bar) for k in range(i+2,i+h+1)))
        neg6=-math.log(c[j]/c[j-6])
        out.append(dict(i=i,t=t,known=t+(h+4)*HOUR,y=y,vol=vol,ratio=short/vol,neg6=neg6,phase=(t-s['start'])%(h*HOUR)==0,f=[neg6,-math.log(c[j]/c[j-24]),vol,short/vol,1-2*sum(u[j-5:j+1])/q,math.log(q/(sum(v[j-47:j+1])/8))]))
    return out


def fit(rows,k):
    means=[mean([r['f'][j] for r in rows]) for j in range(k)]
    sd=[max(1e-10,math.sqrt(mean([(r['f'][j]-m)**2 for r in rows]))) for j,m in enumerate(means)]
    def x(f):
        return [1]+[max(-6,min(6,(f[j]-m)/sd[j])) for j,m in enumerate(means)]
    X=[x(r['f']) for r in rows]; w=[logit(mean([r['y'] for r in rows]))]+[0.]*k
    for _ in range(600):
        g=[0.]*(k+1)
        for row,r in zip(X,rows):
            e=sig(sum(z*b for z,b in zip(row,w)))-r['y']
            for j in range(k+1):
                g[j]+=e*row[j]
        for j in range(k+1):
            w[j]-=.05*(g[j]/len(rows)+(.05*w[j] if j else 0))
    return lambda f:clip(sig(sum(z*b for z,b in zip(x(f),w))))


def metrics(rows,m):
    if not rows:
        return None
    y=[r['y'] for r in rows]; p=[r['p'][m] for r in rows]; pos=sum(y); n=len(y)
    positive=[a for a,b in zip(p,y) if b]; negative=[a for a,b in zip(p,y) if not b]
    auc=sum(1 if a>b else .5 if a==b else 0 for a in positive for b in negative)
    return dict(n=n,pos=pos,brier=round(mean([(a-b)**2 for a,b in zip(p,y)]),5),ll=round(-mean([b*math.log(a)+(1-b)*math.log(1-a) for a,b in zip(p,y)]),5),mean=round(mean(p),4),auc=round(auc/(pos*(n-pos)),4) if 0<pos<n else None)


def matured(rows,t):
    return [r for r in rows if r['known']<t]


def rate(rows,p,w=4):
    return clip((sum(r['y'] for r in rows)+w*p)/(len(rows)+w))


def memory(hist,t,p,d):
    return rate(hist if d is None else [r for r in hist if r['t']>=t-d*DAY],p,8)


def ew(hist,t,p,d,w=8):
    a=[.5**((t-r['t'])/(d*DAY)) for r in hist]
    return clip((sum(r['y']*v for r,v in zip(hist,a))+w*p)/(sum(a)+w))


def delta(hist,key,target):
    lo,hi=-10.,10.
    for _ in range(45):
        mid=(lo+hi)/2
        if mean([sig(logit(r[key])+mid) for r in hist])<target:
            lo=mid
        else:
            hi=mid
    return (lo+hi)/2


def periods(s):
    y=s['year']
    return [('Mar-Jun',utc(y,3),utc(y,7)),('Jul-Oct',utc(y,7),utc(y,11)),('Nov-Dec',utc(y,11),s['end'])]


def run_a(raw,s):
    validate_bars(raw,s); cutoff=utc(s['year'],3); results=[]
    for h,bar in HORIZONS:
        rows=create_rows(raw,s,h,bar); train=matured(rows,cutoff)
        if len(train)<50:
            raise ValueError('TRAINING_INSUFFICIENT')
        prior=clip(mean([r['y'] for r in train])); F,G=fit(train,4),fit(train,6)
        ff=[dict(r,price=F(r['f']),flow=G(r['f'])) for r in rows]; test=[]
        for x in ff:
            t=x['t']
            if t<cutoff:
                continue
            hist=matured(ff,t); recent=[z for z in hist if z['t']>=t-30*DAY]
            p=dict(static_rate=prior,expanding_rate=memory(hist,t,prior,None),rolling7=memory(hist,t,prior,7),rolling30=memory(hist,t,prior,30),rolling90=memory(hist,t,prior,90),ewma7=ew(hist,t,prior,7),ewma30=ew(hist,t,prior,30),fixed_price=x['price'],fixed_flow=x['flow'])
            p['mix']=clip((p['ewma7']+p['ewma30'])/2)
            for m in ('price','flow'):
                p['rebase_'+m]=clip(sig(logit(x[m])+logit(p['rolling30'])-logit(prior)))
                p['recal_'+m]=clip(sig(logit(x[m])+delta(recent,m,p['rolling30']))) if len(recent)>=30 else p['rebase_'+m]
            test.append(dict(x,p=p))
        result=dict(h=h,train=[len(train),sum(r['y'] for r in train),prior],periods={},nonoverlap={})
        for name,lo,hi in periods(s):
            a=[x for x in test if lo<=x['t'] and x['t']+72*HOUR<=hi]
            if not a:
                continue
            result['periods'][name]={m:metrics(a,m) for m in A_METHODS}
            d=[x for x in a if ((x['t']-lo)//HOUR)%h==0]
            result['nonoverlap'][name]={m:metrics(d,m) for m in ('static_rate','rolling30','mix','fixed_flow','recal_flow')}
        results.append(result)
    return results


def run_b(raw,s):
    validate_bars(raw,s); cutoff=utc(s['year'],3); results=[]
    for h,bar in HORIZONS:
        rows=create_rows(raw,s,h,bar); train=matured(rows,cutoff); ind=[x for x in train if x['phase']]
        if not ind:
            raise ValueError('TRAINING_INSUFFICIENT')
        prior=rate(ind,.5,.5); q1,q2=[quant([x['vol'] for x in train],p) for p in (1/3,2/3)]
        def bucket(x):
            return 0 if x['vol']<=q1 else 1 if x['vol']<=q2 else 2
        cp=[rate([x for x in ind if bucket(x)==k],prior,4) for k in range(3)]
        preds=[]; experts=('fixed','rolling30_nonoverlap','ewma7_nonoverlap','ewma30_nonoverlap','conditional_vol','shock_blend')
        for x in rows:
            t=x['t']
            if t<cutoff:
                continue
            hist=matured(rows,t); nh=[z for z in hist if z['phase']]
            recent=[z for z in nh if z['t']>=t-30*DAY]; allrecent=[z for z in hist if z['t']>=t-30*DAY]; local=[z for z in nh if z['t']>=t-90*DAY and bucket(z)==bucket(x)]
            p=dict(fixed=prior,rolling30_full=rate(allrecent,prior,4*h/6),rolling30_nonoverlap=rate(recent,prior),ewma7_nonoverlap=ew(nh,t,prior,7,4),ewma30_nonoverlap=ew(nh,t,prior,30,4))
            p['mix_nonoverlap']=(p['ewma7_nonoverlap']+p['ewma30_nonoverlap'])/2
            p['conditional_vol']=rate(local,p['mix_nonoverlap'],4)
            shock=x['ratio']>=1.5 and x['neg6']>=.01
            p['shock_blend']=max(p['mix_nonoverlap'],.5*p['mix_nonoverlap']+.5*cp[2]) if shock else p['mix_nonoverlap']
            past=[z for z in matured(preds,t) if z['phase'] and z['t']>=t-90*DAY]
            weights=[math.exp(-2*(mean([(z['p'][m]-z['y'])**2 for z in past]) if past else 0)) for m in experts]
            p['online_experts']=sum(w*p[m] for m,w in zip(experts,weights))/sum(weights)
            preds.append(dict(x,p=p,shock=shock))
        def ms(a):
            return dict(n=len(a),pos=sum(x['y'] for x in a),m={m:[round(mean([(x['p'][m]-x['y'])**2 for x in a]),5),round(mean([x['p'][m] for x in a]),5)] if a else None for m in B_METHODS})
        result=dict(h=h,train=[len(train),len(ind),prior],cut=[q1,q2],conditionalPriors=cp,periods=[])
        for name,lo,hi in periods(s):
            t=[x for x in preds if lo<=x['t'] and x['t']+72*HOUR<=hi]
            result['periods'].append(dict(name=name,all=ms(t),nonoverlap=ms([x for x in t if x['phase']]),shock=ms([x for x in t if x['shock']])))
        results.append(result)
    return results


def selftest():
    t=utc(2026); s=dict(year=2026,start=t,end=t+400*HOUR)
    raw=[[t+i*HOUR,'100','101','99',str(100+i/100),'1',t+(i+1)*HOUR-1,'100','1','.6','60','0'] for i in range(400)]
    def rejects(a):
        try:
            validate_bars(a,s)
        except ValueError:
            return True
        return False
    good=validate_bars(raw,s); rows=create_rows(raw,s,12,.015); i=rows[0]['i']
    mut=[r[:4]+['1']+r[5:] if k>i-4 else r for k,r in enumerate(raw)]
    q=raw.copy(); q[10]=q[9]
    bad=[r[:10]+['101']+r[11:] if k==100 else r for k,r in enumerate(raw)]
    phases=[r for r in rows if r['phase']]
    return dict(complete=good['n']==400,duplicate_reject=rejects(q),missing_reject=rejects(raw[1:]),invalid_taker_reject=rejects(bad),future_features_invariant=rows[0]['f']==create_rows(mut,s,12,.015)[0]['f'],maturity_boundary=len(matured([{'known':k} for k in (99,100,101)],100))==1,exact_horizon_delay=all(r['known']-r['t']==16*HOUR for r in rows),phase_nonoverlap=all(b['t']-a['t']==12*HOUR for a,b in zip(phases,phases[1:])),empty_prior=rate([],.2)==.2,brier_fixture=metrics([dict(y=0,p={'x':.5}),dict(y=1,p={'x':.5})],'x')['brier']==.25,empty_metrics=metrics([],'x') is None,clip_bounds=clip(0)==.005 and clip(1)==.995,invalid_shape_reject=rejects(raw[:10]+[[]]+raw[11:]),invalid_clock_type_reject=rejects([[str(raw[0][0])]+raw[0][1:]]+raw[1:]),nonfinite_reject=rejects([raw[0][:4]+['NaN']+raw[0][5:]]+raw[1:]))


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('input',nargs='?'); p.add_argument('year',nargs='?',type=int); p.add_argument('--self-test',action='store_true'); args=p.parse_args()
    if args.self_test:
        tests=selftest(); print(json.dumps(tests,indent=2)); return int(not all(tests.values()))
    if args.input is None or args.year is None:
        p.error('INPUT YEAR or --self-test required')
    data=Path(args.input).read_bytes(); raw=json.loads(data); s=spec(args.year)
    print(json.dumps(dict(authority='EXPOST_DEVELOPMENT_ONLY',sha256=hashlib.sha256(data).hexdigest(),quality=validate_bars(raw,s),A=run_a(raw,s),B=run_b(raw,s)),indent=2,allow_nan=False))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
