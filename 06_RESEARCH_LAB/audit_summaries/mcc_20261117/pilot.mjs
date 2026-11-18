// MCC-20261117 exploratory public price-only pilot. No live use.
// node pilot.mjs input.json > rerun.json ; node pilot.mjs --self-test
import fs from "node:fs";
import { createHash } from "node:crypto";
function normalize(raw, cutoff) {
  if (!Array.isArray(raw)) throw Error("invalid payload");
  const d=raw.filter(x=>Number(x[6])<cutoff).map(x=>[Number(x[0]),String(x[1]),String(x[2]),String(x[3]),String(x[4]),String(x[5]),Number(x[6])]);
  if(d.length<201) throw Error("insufficient warmup");
  for(let i=0;i<d.length;i++){let [t,o,h,l,c,v,e]=d[i]; [o,h,l,c,v]=[o,h,l,c,v].map(Number);if(!Number.isFinite(t)||e!==t+604800000-1||![o,h,l,c,v].every(Number.isFinite)||l<=0||h<Math.max(o,c)||l>Math.min(o,c)||v<0||(i&&t-d[i-1][0]!==604800000))throw Error("source quality failure at "+i)}
  return d;
}
function pilot(d) {
  const avg=a=>a.reduce((s,x)=>s+x,0)/a.length, rd=x=>Math.round(x*1e6)/1e6;
  const date=t=>new Date(t).toISOString().slice(0,10);
  const prices=d.map(x=>({t:x[0],o:+x[1],h:+x[2],l:+x[3],c:+x[4],end:x[6]}));
  for(let i=199;i<prices.length;i++) prices[i].ma=avg(prices.slice(i-199,i+1).map(x=>x.c));
  const rules={
    BUY_HOLD:(p,k)=>k===0?1:null,
    STATIC_50:(p,k)=>.5,
    SMA_TREND:(p,k)=>p.c>=p.ma?1:0,
    SMA_DEFENSIVE_50:(p,k)=>p.c>=p.ma?1:.5,
    SMA_ACCUMULATION_50:(p,k)=>p.c<p.ma?1:.5,
    DCA_26:(p,k)=>null
  };
  function run(start,end,rule,fee){
    let cash=1,qty=0,peak=1,maxdd=0,fees=0,turnover=0,tradeCount=0,exposure=0;
    const equityPath=[];
    for(let i=start;i<=end;i++){
      // Signals only from already closed candle, trade next open.
      let p=prices[i],prior=prices[i-1],k=i-start,w=rules[rule](prior,k),asset=qty*p.o,eq=cash+asset,delta=0;
      if(rule==="DCA_26"&&k<26)delta=Math.min(cash/(1+fee),1/26);
      else if(w!==null){const target=w*eq;delta=(target-asset)/(1+(target>=asset?w:-w)*fee);}
      if(Math.abs(delta)>1e-12){
        const cost=Math.abs(delta)*fee;cash-=delta+cost;qty+=delta/p.o;fees+=cost;turnover+=Math.abs(delta);tradeCount++;
      }
      if(cash<-1e-8||qty<-1e-8)throw Error("long-only invariant");
      const nav=cash+qty*p.c;peak=Math.max(peak,nav);maxdd=Math.min(maxdd,nav/peak-1);
      exposure+=qty*p.c/nav;equityPath.push(nav);
    }
    let nav=equityPath.at(-1);
    return {return_pct:rd((nav-1)*100),weekly_close_max_drawdown_pct:rd(maxdd*100),fee_pct_of_initial:rd(fees*100),turnover_initial_units:rd(turnover),trades:tradeCount,mean_weekly_equity_exposure_pct:rd(exposure/equityPath.length*100),terminal_nav:rd(nav)};
  }
  const start=200,end=prices.length-1,split=prices.findIndex(p=>p.t>=Date.parse("2024-01-01T00:00:00Z"));
  const ranges=[["ALL",start,end],["PRE_2024",start,split-1],["FROM_2024",split,end]].filter(x=>x[1]>=start&&x[2]>=x[1]);
  const outcomes=[];
  for(const [period,a,b] of ranges)for(const fee of [.001,.003])for(const rule of Object.keys(rules)) outcomes.push({period,first_open:date(prices[a].t),last_close:date(prices[b].end),weeks:b-a+1,fee_bps:fee*10000,rule,...run(a,b,rule,fee)});
  const events=[];
  for(let i=200;i<prices.length;i++){const p=prices[i],q=prices[i-1];if((p.c<p.ma)===(q.c<q.ma))continue;for(const h of [4,13,26]){const mature=i+h<prices.length;events.push({signal_date:date(p.end),type:p.c<p.ma?"DOWNCROSS":"RECLAIM",horizon_weeks:h,outcome_status:mature?"MATURED_RETROSPECTIVE":"PENDING",return_pct:mature?rd((prices[i+h].c/p.c-1)*100):null,mae_pct:mature?rd((Math.min(p.c,...prices.slice(i+1,i+h+1).map(x=>x.l))/p.c-1)*100):null})}}
  return {source_rows:prices.length,eligible_simulation_weeks:prices.length-start,first_open:date(prices[0].t),last_close:date(prices.at(-1).end),events,outcomes};
}
function selfTest(){
  const a=Date.parse("2020-01-06T00:00:00Z"),week=604800000;
  const raw=Array.from({length:230},(_,i)=>[a+i*week,"100","100","100","100","1",a+(i+1)*week-1]);
  const c=a+230*week, rows=normalize(raw,c);
  function check(ok,msg){if(!ok)throw Error(msg)}
  const p=pilot(rows);
  const bh=p.outcomes.find(x=>x.period==="ALL"&&x.fee_bps===10&&x.rule==="BUY_HOLD");
  check(Math.abs(bh.terminal_nav-1/1.001)<.000001,"fee / next open");
  check(bh.trades===1,"buy hold trades");
  check(p.events.length===0,"flat no crossings");
  check(p.outcomes.every(x=>x.terminal_nav<=1.000001),"flat wealth no creation");
  const g=raw.slice();g.splice(100,1);let fail=false;try{normalize(g,c)}catch(e){fail=true}check(fail,"reject gap");
  const bad=raw.map(x=>x.slice());bad[25][3]="101";fail=false;try{normalize(bad,c)}catch(e){fail=true}check(fail,"reject invalid low");
  const amended=raw.map(x=>x.slice());amended[amended.length-1][4]="99";amended[amended.length-1][3]="99";
  const z=pilot(normalize(amended,c));check(z.events.filter(x=>x.signal_date!==z.last_close).length===0,"no retrospective signal mutation");
  check(normalize(raw,c-week).length===229,"exclude incomplete");
  return {tests:8,status:"PASS"};
}
const cutoff=Date.parse("2026-11-16T00:00:00Z");
if(process.argv[2]==="--self-test"){console.log(JSON.stringify(selfTest(),null,2));}else{const raw=JSON.parse(fs.readFileSync(process.argv[2],"utf8"));const rows=normalize(raw,cutoff);console.log(JSON.stringify({normalized_sha256:createHash("sha256").update(JSON.stringify(rows)).digest("hex"),tests:selfTest(),...pilot(rows)},null,2));}
