// Public ETHBTC development-only replay; no source admission, trade, or runtime authority.
// Usage: import {replay,selfTest} from this module; replay(array_of_completed_Binance_UTC_daily_klines).
// Caller must establish source/rights/as-of/cutoff and complete last candle before calling. No network in module.
function replay(rows) {
  if (!Array.isArray(rows) || rows.length < 231) throw Error("INSUFFICIENT_SPOT_DAILY_ROWS");
  for(let i=0;i<rows.length;i++){let r=rows[i];if(!Array.isArray(r)||!Number.isSafeInteger(r[0])||r[0]%86400000!==0||!(Number(r[1])>0)||!(Number(r[4])>0)||!Number.isFinite(Number(r[1]))||!Number.isFinite(Number(r[4]))||!Number.isSafeInteger(r[6])||r[6]<r[0]||r[6]>r[0]+86399999||(i&&r[0]-rows[i-1][0]!==86400000))throw Error("INVALID_OR_NONCONTIGUOUS_UTC_DAILY_ROW:"+i)}
  const C=rows.map(r=>Number(r[4])),O=rows.map(r=>Number(r[1])),D=rows.map(r=>new Date(r[0]).toISOString().slice(0,10)),good=rows.map(r=>r[6]===r[0]+86399999);
  const avg=z=>z.length?z.reduce((s,v)=>s+v,0)/z.length:null;
  const med=z=>{if(!z.length)return null;let x=[...z].sort((a,b)=>a-b);return (x[Math.floor((x.length-1)/2)]+x[Math.ceil((x.length-1)/2)])/2};
  const models=[];
  for(const w of [20,50,100]){
    const above=C.map((v,i)=>i>=w&&good.slice(i-w,i+1).every(Boolean)?v>avg(C.slice(i-w,i)):null);
    const events=[];let last=-100,censored=0;
    for(let i=200;i<rows.length-30;i++){
      if(above[i]!==true||above[i-1]!==false||i-last<30)continue;last=i;
      // Qualification outcome is never used to choose the next issue date.
      if(!good.slice(i+1,i+31).every(Boolean)||above[i+1]===null||above[i+2]===null){censored++;continue;}
      const hold=above[i+1]&&above[i+2], e={date:D[i],confirmed:hold};
      for(const h of [7,30]) {e["first"+h]=C[i+h]/O[i+1]-1;e["wait"+h]=hold?C[i+h]/O[i+3]-1:0;}
      events.push(e);
    }
    const groups=[["all",events],["2018-23",events.filter(x=>x.date<"2024-01-01")],["2024+",events.filter(x=>x.date>="2024-01-01")]];
    models.push({window_days:w,censored,events,groups:groups.map(([era,e])=>({era,n:e.length,confirmed:e.filter(x=>x.confirmed).length,metrics:[7,30].map(h=>({h,firstMean:avg(e.map(x=>x["first"+h])),waitMean:avg(e.map(x=>x["wait"+h])),firstMedian:med(e.map(x=>x["first"+h])),waitMedian:med(e.map(x=>x["wait"+h])),firstPositive:e.filter(x=>x["first"+h]>0).length,waitPositive:e.filter(x=>x["wait"+h]>0).length,avoidedLoss:e.filter(x=>!x.confirmed&&x["first"+h]<0).length,missedGain:e.filter(x=>!x.confirmed&&x["first"+h]>0).length}))}))});
  }
  return {n:rows.length,first:D[0],last:D.at(-1),short_days:D.filter((_,i)=>!good[i]),models};
}
function selfTest(){
 const origin=Date.parse("2020-01-01"), rows=Array.from({length:250},(_,i)=>{let p=i<200?1:i===200?1.1:i===201?1.2:i===202?1.3:1.4;return [origin+i*86400000,p,p,p,p,0,origin+(i+1)*86400000-1]});
 const assert=(v,m)=>{if(!v)throw Error(m)};
 const x=replay(rows);assert(x.models.every(m=>m.events.length===1&&m.events[0].confirmed),"cross and hold");
 assert(x.models.every(m=>Math.abs(m.events[0].wait7)<1e-12),"delayed fill same terminal");
 const changed=rows.map(r=>[...r]);changed[201][4]=0.9;
 assert(replay(changed).models.every(m=>m.events[0].confirmed===false&&m.events[0].wait30===0),"abstention kept");
 const later=rows.map(r=>[...r]);later[210][4]=2;
 assert(replay(later).models.every((m,i)=>m.events[0].date===x.models[i].events[0].date&&m.events[0].confirmed===x.models[i].events[0].confirmed),"later outcome mutation cannot change earlier decision");
 const bad=rows.filter((_,i)=>i!==100);let rejected=false;try{replay(bad)}catch(e){rejected=true}assert(rejected,"missing day rejected");
 const invalid=rows.map(r=>[...r]);invalid[10][1]="Infinity";rejected=false;try{replay(invalid)}catch(e){rejected=true}assert(rejected,"invalid price rejected");
 const short=rows.map(r=>[...r]);short[210][6]-=1000;
 assert(replay(short).models.every(m=>m.censored===1&&m.events.length===0),"partial outcome censored");
 const shortInput=rows.map(r=>[...r]);shortInput[199][6]-=1000;
 assert(replay(shortInput).models.every(m=>m.events.length===0),"partial lookback excluded");
 return {passed:8};
}
export {replay,selfTest};
