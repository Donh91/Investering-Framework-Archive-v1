// Research-only offline replay. No network, secrets, schedulers or production authority.
// Input: a JSON array of Binance BTCUSDT hourly spot klines, in UTC order.
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
const HOUR=3600000;
const A={"lag":4,"step":6,"priorPseudo":8,"horizons":[[12,0.015],[24,0.025],[72,0.04]],"methods":["static_rate","expanding_rate","rolling7","rolling30","rolling90","ewma7","ewma30","mix","fixed_price","fixed_flow","rebase_price","rebase_flow","recal_price","recal_flow"]};
const B={"lag":4,"step":6,"priorWeight":4,"horizons":[[12,0.015],[24,0.025],[72,0.04]],"models":["fixed","rolling30_full","rolling30_nonoverlap","ewma7_nonoverlap","ewma30_nonoverlap","mix_nonoverlap","conditional_vol","shock_blend","online_experts"],"volShockRatio":1.5,"negative6Threshold":0.01,"shockFloorWeight":0.5,"expertEta":2};
function spec(year){if(![2024,2025,2026].includes(year))throw Error("UNSUPPORTED_YEAR");return {year,start:Date.UTC(year,0,1),end:year===2026?Date.UTC(2026,10,17):Date.UTC(year+1,0,1)}}

function sum(a){return a.reduce((s,x)=>s+x,0)}

function rms(a){return Math.sqrt(sum(a.map(x=>x*x))/a.length)}

function clip(p){return Math.max(.005,Math.min(.995,p))}

function sig(x){return 1/(1+Math.exp(-Math.max(-35,Math.min(35,x))))}

function logit(p){return Math.log(clip(p)/(1-clip(p)))}

function quant(a,p){if(!a.length)throw Error("NO_QUANTILE_SAMPLE");let x=a.slice().sort((a,b)=>a-b);return x[Math.max(0,Math.min(x.length-1,Math.ceil(p*x.length)-1))]}

function validateBars(a,s){const q={n:a.length,expected:(s.end-s.start)/HOUR,duplicates:a.length-new Set(a.map(r=>r[0])).size,grid:a.filter((r,i)=>r[0]!==s.start+i*HOUR||r[6]!==r[0]+HOUR-1).length,bad:a.filter(r=>!(Number.isFinite(+r[4])&&+r[4]>0&&Number.isFinite(+r[7])&&+r[7]>0&&Number.isFinite(+r[10])&&+r[10]>=0&&+r[10]<=+r[7])).length};if(q.n!==q.expected||q.duplicates||q.grid||q.bad)throw Error("SOURCE_INVALID "+JSON.stringify(q));return q}

function createRows(a,s,h,bar){const c=a.map(r=>+r[4]),v=a.map(r=>+r[7]),u=a.map(r=>+r[10]),r=c.map((x,i)=>i?Math.log(x/c[i-1]):0),out=[];for(let i=0;i+h<a.length;i++){let t=s.start+(i+1)*HOUR,j=i-A.lag;if(j<240||t%(A.step*HOUR))continue;let vol=Math.max(1e-8,rms(r.slice(j-47,j+1))),short=rms(r.slice(j-5,j+1)),q=sum(v.slice(j-5,j+1)),y=0;for(let k=i+2;k<=i+h;k++)if(c[k]<=c[i+1]*(1-bar)){y=1;break}let neg6=-Math.log(c[j]/c[j-6]);out.push({i,t,known:t+(h+A.lag)*HOUR,y,vol,ratio:short/vol,neg6,phase:(t-s.start)%(h*HOUR)===0,f:[neg6,-Math.log(c[j]/c[j-24]),vol,short/vol,1-2*sum(u.slice(j-5,j+1))/q,Math.log(q/(sum(v.slice(j-47,j+1))/8))]})}return out}

function fit(rows,k){let means=Array.from({length:k},(_,j)=>sum(rows.map(x=>x.f[j]))/rows.length),sd=means.map((m,j)=>Math.max(1e-10,Math.sqrt(sum(rows.map(x=>(x.f[j]-m)**2))/rows.length))),x=f=>[1,...means.map((m,j)=>Math.max(-6,Math.min(6,(f[j]-m)/sd[j])))],X=rows.map(r=>x(r.f)),w=Array(k+1).fill(0);w[0]=logit(sum(rows.map(r=>r.y))/rows.length);for(let t=0;t<600;t++){let g=w.map(()=>0);for(let i=0;i<rows.length;i++){let e=sig(sum(X[i].map((z,j)=>z*w[j])))-rows[i].y;for(let j=0;j<w.length;j++)g[j]+=e*X[i][j]}for(let j=0;j<w.length;j++)w[j]-=.05*(g[j]/rows.length+(j?.05*w[j]:0))}return f=>clip(sig(sum(x(f).map((z,j)=>z*w[j]))))}

function metrics(rows,m){let n=rows.length;if(!n)return null;let y=rows.map(x=>x.y),p=rows.map(x=>x.p[m]),pos=sum(y),auc=0;for(let i=0;i<n;i++)if(y[i])for(let j=0;j<n;j++)if(!y[j])auc+=p[i]>p[j]?1:p[i]===p[j]?.5:0;return {n,pos,brier:+(sum(p.map((x,i)=>(x-y[i])**2))/n).toFixed(5),ll:+(-sum(p.map((x,i)=>y[i]*Math.log(x)+(1-y[i])*Math.log(1-x)))/n).toFixed(5),mean:+(sum(p)/n).toFixed(4),auc:pos&&pos<n?+(auc/(pos*(n-pos))).toFixed(4):null}}

function matured(rows,t){return rows.filter(z=>z.known<t)}

function memory(hist,t,prior,d){let h=d===Infinity?hist:hist.filter(x=>x.t>=t-d*24*HOUR);return clip((sum(h.map(x=>x.y))+A.priorPseudo*prior)/(h.length+A.priorPseudo))}

function ew(hist,t,p,d,w=8){let a=hist.map(x=>Math.pow(.5,(t-x.t)/(d*24*HOUR)));return clip((sum(hist.map((x,i)=>x.y*a[i]))+w*p)/(sum(a)+w))}

function rate(h,p,w=4){return clip((sum(h.map(x=>x.y))+w*p)/(h.length+w))}

function delta(hist,key,target){let l=-10,u=10;for(let j=0;j<45;j++){let mid=(l+u)/2,mean=sum(hist.map(x=>sig(logit(x[key])+mid)))/hist.length;if(mean<target)l=mid;else u=mid}return(l+u)/2}

function periods(s){return [["Mar-Jun",Date.UTC(s.year,2,1),Date.UTC(s.year,6,1)],["Jul-Oct",Date.UTC(s.year,6,1),Date.UTC(s.year,10,1)],["Nov-Dec",Date.UTC(s.year,10,1),s.end]].filter(x=>x[2]>x[1])}

function runA(raw,s){validateBars(raw,s);let trainEnd=Date.UTC(s.year,2,1);return A.horizons.map(([h,bar])=>{let rows=createRows(raw,s,h,bar),train=matured(rows,trainEnd);if(train.length<50)throw Error("TRAINING_INSUFFICIENT");let prior=clip(sum(train.map(x=>x.y))/train.length),F=fit(train,4),G=fit(train,6),ff=rows.map(x=>({...x,price:F(x.f),flow:G(x.f)})),test=[];for(let x of ff){if(x.t<trainEnd)continue;let hist=matured(ff,x.t),recent=hist.filter(z=>z.t>=x.t-30*24*HOUR),p={static_rate:prior,expanding_rate:memory(hist,x.t,prior,Infinity),rolling7:memory(hist,x.t,prior,7),rolling30:memory(hist,x.t,prior,30),rolling90:memory(hist,x.t,prior,90),ewma7:ew(hist,x.t,prior,7),ewma30:ew(hist,x.t,prior,30),fixed_price:x.price,fixed_flow:x.flow};p.mix=clip((p.ewma7+p.ewma30)/2);for(let m of ["price","flow"]){p["rebase_"+m]=clip(sig(logit(x[m])+logit(p.rolling30)-logit(prior)));p["recal_"+m]=recent.length>=30?clip(sig(logit(x[m])+delta(recent,m,p.rolling30))):p["rebase_"+m]};test.push({...x,p})}let res={h,train:[train.length,sum(train.map(x=>x.y)),prior],periods:{},nonoverlap:{}};for(let [name,lo,hi] of periods(s)){let a=test.filter(x=>x.t>=lo&&x.t+72*HOUR<=hi);if(!a.length)continue;res.periods[name]=Object.fromEntries(A.methods.map(m=>[m,metrics(a,m)]));let d=a.filter(x=>Math.floor((x.t-lo)/HOUR)%h===0);res.nonoverlap[name]=Object.fromEntries(["static_rate","rolling30","mix","fixed_flow","recal_flow"].map(m=>[m,metrics(d,m)]))}return res})}

function runB(raw,s){validateBars(raw,s);let trainEnd=Date.UTC(s.year,2,1);return B.horizons.map(([h,bar])=>{let rows=createRows(raw,s,h,bar),train=matured(rows,trainEnd),ind=train.filter(x=>x.phase);if(!ind.length)throw Error("TRAINING_INSUFFICIENT");let prior=rate(ind,.5,.5),q1=quant(train.map(x=>x.vol),1/3),q2=quant(train.map(x=>x.vol),2/3),bucket=x=>x.vol<=q1?0:x.vol<=q2?1:2,cp=[0,1,2].map(k=>rate(ind.filter(x=>bucket(x)===k),prior,4)),preds=[],experts=["fixed","rolling30_nonoverlap","ewma7_nonoverlap","ewma30_nonoverlap","conditional_vol","shock_blend"];for(let x of rows){if(x.t<trainEnd)continue;let hist=matured(rows,x.t),nh=hist.filter(z=>z.phase),recent=nh.filter(z=>z.t>=x.t-30*24*HOUR),allrecent=hist.filter(z=>z.t>=x.t-30*24*HOUR),local=nh.filter(z=>z.t>=x.t-90*24*HOUR&&bucket(z)===bucket(x)),p={fixed:prior,rolling30_full:rate(allrecent,prior,4*h/6),rolling30_nonoverlap:rate(recent,prior),ewma7_nonoverlap:ew(nh,x.t,prior,7,4),ewma30_nonoverlap:ew(nh,x.t,prior,30,4)};p.mix_nonoverlap=(p.ewma7_nonoverlap+p.ewma30_nonoverlap)/2;p.conditional_vol=rate(local,p.mix_nonoverlap,4);let shock=x.ratio>=B.volShockRatio&&x.neg6>=B.negative6Threshold;p.shock_blend=shock?Math.max(p.mix_nonoverlap,(1-B.shockFloorWeight)*p.mix_nonoverlap+B.shockFloorWeight*cp[2]):p.mix_nonoverlap;let past=matured(preds,x.t).filter(z=>z.phase&&z.t>=x.t-90*24*HOUR),weights=experts.map(m=>Math.exp(-B.expertEta*(past.length?sum(past.map(z=>(z.p[m]-z.y)**2))/past.length:0)));p.online_experts=sum(experts.map((m,k)=>weights[k]*p[m]))/sum(weights);preds.push({...x,p,shock,localN:local.length,feedbackN:past.length})}return {h,train:[train.length,ind.length,prior],cut:[q1,q2],conditionalPriors:cp,periods:periods(s).map(([name,lo,hi])=>{let t=preds.filter(x=>x.t>=lo&&x.t+72*HOUR<=hi),ms=a=>({n:a.length,pos:sum(a.map(x=>x.y)),m:Object.fromEntries(B.models.map(m=>[m,a.length?[sum(a.map(x=>(x.p[m]-x.y)**2))/a.length,sum(a.map(x=>x.p[m]))/a.length].map(z=>+z.toFixed(5)):null]))});return {name,all:ms(t),nonoverlap:ms(t.filter(x=>x.phase)),shock:ms(t.filter(x=>x.shock))}})}})}

function selftest(){let t=Date.UTC(2026,0,1),s={year:2026,start:t,end:t+400*HOUR},raw=Array.from({length:400},(_,i)=>[t+i*HOUR,"100","101","99",String(100+i/100),"1",t+(i+1)*HOUR-1,"100","1",".6","60","0"]);function rejects(f){try{f();return false}catch{return true}}let good=validateBars(raw,s),rows=createRows(raw,s,12,.015),i=rows[0].i,mutated=raw.map((r,k)=>k>i-A.lag?r.map((x,j)=>j===4?"1":x):r),r2=createRows(mutated,s,12,.015)[0];let q=raw.slice();q[10]=q[9];let bad=raw.map((r,i)=>i===100?r.map((x,j)=>j===10?"101":x):r);return {complete:good.n===400,duplicate_reject:rejects(()=>validateBars(q,s)),missing_reject:rejects(()=>validateBars(raw.slice(1),s)),invalid_taker_reject:rejects(()=>validateBars(bad,s)),future_features_invariant:JSON.stringify(rows[0].f)===JSON.stringify(r2.f),maturity_boundary:matured([{known:99},{known:100},{known:101}],100).length===1,exact_horizon_delay:rows.every(r=>r.known-r.t===16*HOUR),phase_nonoverlap:rows.filter(r=>r.phase).every((r,i,a)=>i===0||r.t-a[i-1].t===12*HOUR),empty_prior:rate([],.2)===.2,brier_fixture:metrics([{y:0,p:{x:.5}},{y:1,p:{x:.5}}],"x").brier===.25,empty_metrics:metrics([],"x")===null,clip_bounds:clip(0)===.005&&clip(1)===.995}}

const args=process.argv.slice(2);
if(args[0]==="--self-test"){const tests=selftest();console.log(JSON.stringify(tests,null,2));if(Object.values(tests).some(x=>!x))process.exitCode=1;}
else {if(args.length!==2)throw Error("Usage: node replay.mjs INPUT.json YEAR or --self-test");const bytes=readFileSync(args[0]);const raw=JSON.parse(bytes.toString("utf8"));const s=spec(Number(args[1]));console.log(JSON.stringify({authority:"EXPOST_DEVELOPMENT_ONLY",sha256:createHash("sha256").update(bytes).digest("hex"),quality:validateBars(raw,s),A:runA(raw,s),B:runB(raw,s)},null,2));}
