# Research-only synthetic probe
Executed twice in this conversation using a JavaScript isolate. 22/22 expected invariants matched both times. No market data, network requests, real positions or order authority. All values are fictional unit-test examples, including risk parameters and bar windows; they are not selected trading thresholds. Reproduce offline by wrapping the following exact body in a function and printing its return value (or use the fenced code as new Function body in plain Node.js; no dependency). Results recorded separately in SYNTHETIC_RECEIPT.json.

Known unresolved issues: this toy is not hardened input validation, strict availability-schema/source completeness, quote custody, duplicate/pooled-token handling beyond tested cases, whole book risk, cashflow timing, fees/mark accounting, fill simulation or statistical proof. The 22 checks do not certify these absent functions. In particular compression needs typed validated time/identity/volume/clocks; AVWAP needs complete source intervals and unit/venue contracts; risk needs a validated portfolio-wide cap/atomic reservations, strict typed booleans, bounded risk budget, jump/tail and total-loss stress; netEquity is absolute PnL not TWR; opportunity adjudication needs finite/cost-positive fields and no-fill/no-exit separate states. Claude review should require those before implementation. No code copied from Carver or others.

```javascript
function compression(bars, t, cfg={impulse:0.15, contraction:0.6, maxAge:1}){
 const eligible=bars.filter(b=>b.end<=t&&b.available<=t);
 if(eligible.length!==bars.filter(b=>b.end<=t).length) return {state:"UNKNOWN"};
 if(eligible.length<7||eligible.some((b,i)=>!Number.isFinite(b.c)||!Number.isFinite(b.h)||!Number.isFinite(b.l)||b.l<=0||b.h<b.c||b.c<b.l||(i&&b.end!==eligible[i-1].end+1))||t-eligible.at(-1).end>cfg.maxAge)return {state:"UNKNOWN"};
 const w=eligible.slice(-7), [a,b,c,d,e,f,g]=w;
 const impulsive=c.c/a.c-1>=cfg.impulse;
 const r1=(d.h-d.l)/d.c,r2=(e.h-e.l)/e.c,r3=(f.h-f.l)/f.c;
 const tight=r1>0&&r2<=r1&&r3<=r2&&r3/r1<=cfg.contraction&&d.l<e.l&&e.l<f.l;
 const level=Math.max(d.h,e.h,f.h);
 return {state:impulsive&&tight&&g.c>level?"CANDIDATE":"NO_SETUP",level};
}
function avwap(trades,anchor,t){
 if(anchor.known>t||anchor.event>anchor.known)return {state:"UNKNOWN"};
 const w=trades.filter(x=>x.event>=anchor.event&&x.event<=t);
 if(!w.length||w.some(x=>x.available>t||x.q<=0||!Number.isFinite(x.p)||!Number.isFinite(x.q)||x.p<=0)||new Set(w.map(x=>x.id)).size!==w.length)return {state:"UNKNOWN"};
 return {state:"OK",value:w.reduce((s,x)=>s+x.p*x.q,0)/w.reduce((s,x)=>s+x.q,0)};
}
function paperNotional(x){
 if(!x.complete||!x.exitQualified||!x.fresh||![x.capital,x.vol,x.stop,x.risk,x.capacity,x.capRemaining,x.signal].every(Number.isFinite)||x.capital<=0||x.vol<=0||x.stop<=0||x.risk<0||x.capacity<0||x.capRemaining<0)return {state:"ABSTAIN",notional:0};
 const budget=x.capital*x.risk;
 return {state:"OK",notional:Math.max(0,Math.min(Math.abs(Math.max(-1,Math.min(1,x.signal)))*budget/Math.max(x.vol,x.stop),x.capacity,x.capRemaining))};
}
function netEquity(start,end,netExternal,complete){
 if(!complete||![start,end,netExternal].every(Number.isFinite))return null;
 return end-start-netExternal;
}
function adjudicateOpportunity(x){
 if(!x.entered)return x.eligible&&x.decisionKnown?{state:"ABSTAIN",net:0}:{state:"UNKNOWN",net:null};
 if(!x.exitKnown)return {state:"UNKNOWN",net:null};
 return {state:"CLOSED",net:x.exit-x.entry-x.fees};
}
const b=[{c:100,h:102,l:98},{c:110,h:112,l:105},{c:125,h:128,l:119},{c:121,h:128,l:115},{c:123,h:127,l:119},{c:124,h:126,l:122},{c:130,h:132,l:124}].map((x,i)=>({...x,end:i+1,available:i+1}));
const t=[{id:1,event:1,available:1,p:100,q:1},{id:2,event:2,available:2,p:110,q:3}];
const risk={complete:true,exitQualified:true,fresh:true,capital:10000,vol:.04,stop:.05,risk:.01,capacity:900,capRemaining:700,signal:1};
const tests=[
 ["compression_positive",compression(b,7).state,"CANDIDATE"],
 ["compression_early",compression(b,6).state,"UNKNOWN"],
 ["compression_future_invariance",compression([...b,{c:1,h:2,l:1,end:8,available:8}],7).state,"CANDIDATE"],
 ["compression_available_late",compression(b.map((x,i)=>i===6?{...x,available:8}:x),7).state,"UNKNOWN"],
 ["compression_breakout_missing",compression(b.map((x,i)=>i===6?{...x,c:125}:x),7).state,"NO_SETUP"],
 ["compression_gap",compression(b.filter((x,i)=>i!==4),7).state,"UNKNOWN"],
 ["compression_stale",compression(b,9).state,"UNKNOWN"],
 ["avwap_weighted",avwap(t,{event:1,known:1},2).value,107.5],
 ["avwap_anchor_hindsight",avwap(t,{event:1,known:3},2).state,"UNKNOWN"],
 ["avwap_late_trade",avwap(t.map((x,i)=>i?{...x,available:3}:x),{event:1,known:1},2).state,"UNKNOWN"],
 ["avwap_duplicate",avwap([...t,t[1]],{event:1,known:1},2).state,"UNKNOWN"],
 ["risk_cluster_cap",paperNotional(risk).notional,700],
 ["risk_exit_unavailable",paperNotional({...risk,exitQualified:false}).state,"ABSTAIN"],
 ["risk_stale",paperNotional({...risk,fresh:false}).state,"ABSTAIN"],
 ["risk_zero_vol",paperNotional({...risk,vol:0}).state,"ABSTAIN"],
 ["risk_signal_capped",paperNotional({...risk,signal:5,capacity:5000,capRemaining:5000}).notional,2000],
 ["risk_vol_double",paperNotional({...risk,vol:.10,capacity:5000,capRemaining:5000}).notional,1000],
 ["deposit_not_profit",netEquity(1000,1500,500,true),0],
 ["incomplete_equity",netEquity(1000,1500,500,false),null],
 ["unobserved_exit_not_zero",adjudicateOpportunity({entered:true,exitKnown:false}).net,null],
 ["known_no_trade_kept",adjudicateOpportunity({entered:false,eligible:true,decisionKnown:true}).net,0],
 ["costs_can_flip_win",adjudicateOpportunity({entered:true,exitKnown:true,entry:100,exit:101,fees:2}).net,-1]
 ];
return tests.map(([name,actual,expected])=>({name,actual,expected,pass:Object.is(actual,expected)}));
```
