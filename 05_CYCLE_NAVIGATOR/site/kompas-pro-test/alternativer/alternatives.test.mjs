import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {runInNewContext} from "node:vm";
import {buildWeek,expectedDaily,forecastFingerprint,ASSETS,WEEK} from "./full-week-fixture.mjs";

const sourcePath=new URL("../../frozen-week-chart.js",import.meta.url);
const source=readFileSync(fileURLToPath(sourcePath),"utf8");
const ctx={window:{CNI18n:{language:"da"}},document:{addEventListener(){}},Date,console};
runInNewContext(source,ctx,{filename:"frozen-week-chart.js"});
const native=ctx.window.CNWeekChart;
const dataAt=h=>buildWeek({hours:h});
const model=(d,asset)=>native.model(d.data,asset,Date.parse(d.nowUtc));
const nativeLine=(d,asset)=>native.linePlan(model(d,asset));
const stable=forecastFingerprint();

test("full week fixture has seven source-issued forecast points and 168 hourly observations",()=>{
 const day7=dataAt(168);
 assert.equal(day7.week,WEEK);
 assert.equal(day7.data.public_live_precision.daily_range_plan.BTC.points.length,7);
 assert.equal(day7.data.public_live_precision.daily_range_plan.ETH.points.length,7);
 for(const asset of ["BTC","ETH"]){
   const m=model(day7,asset);
   assert.ok(m,asset+" original model must accept synthetic source-shaped data");
   assert.equal(m.daily.length,7);
   assert.equal(m.hourly.length,168);
   assert.equal(m.days.filter(d=>d.actual).length,7);
   assert.equal(nativeLine(day7,asset).forecast.length,7);
   assert.equal(nativeLine(day7,asset).actualRuns.flat().length,168);
   m.daily.forEach((p,i)=>{
     assert.equal(p.day,i+1);
     assert.equal(p.expected_close,ASSETS[asset].close[i]);
     assert.equal(p.low,ASSETS[asset].low[i]);
     assert.equal(p.high,ASSETS[asset].high[i]);
   });
 }
});
test("Monday, Wednesday, Sunday: frozen blue forecast never changes, only green advances",()=>{
 const cases=[[16,16,0],[64,64,2],[168,168,7]];
 for(const asset of ["BTC","ETH"]){
   const frozen=JSON.stringify(expectedDaily(asset));
   for(const [hours,expectedObserved,expectedCompleted] of cases){
     const data=dataAt(hours),m=model(data,asset),plan=nativeLine(data,asset);
     assert.ok(m,asset+" native chart accepts "+hours);
     assert.equal(m.hourly.length,expectedObserved);
     assert.equal(plan.actualRuns.flat().length,expectedObserved);
     assert.equal(m.days.filter(d=>d.actual).length,expectedCompleted);
     assert.equal(plan.forecast.length,7);
     assert.equal(JSON.stringify(expectedDaily(asset)),frozen);
     assert.equal(forecastFingerprint(),stable);
     assert.ok(m.hourly.every(p=>p.time<=Date.parse(data.nowUtc)/1000));
   }
 }
});
test("a 7 day full-week fixture has 7 distinct real day timestamps and no invented eighth day",()=>{
 const data=dataAt(168);
 for(const a of ["BTC","ETH"]){
   const m=model(data,a),f=native.linePlan(m).forecast;
   assert.equal(new Set(f.map(p=>p.time)).size,7);
   assert.equal(f[6].time-f[0].time,6*86400);
   assert.equal(data.data.public_live_precision.daily_observations[a].length,7);
   for(let i=0;i<7;i++)assert.equal(f[i].value,ASSETS[a].close[i]);
 }
});
test("fail-closed original source renderer: when 7/7 missing it does not fabricate blue path",()=>{
 const bad=buildWeek({hours:168,missing:true});
 const m=model(bad,"BTC");
 assert.ok(m);
 assert.equal(m.daily.length,0);
 assert.equal(native.linePlan(m).forecast.length,0);
});
test("design is isolated to separate QA directory, original Github renderer is the only drawing engine",()=>{
 const dir=new URL(".",import.meta.url);
 const html=readFileSync(fileURLToPath(new URL("index.html",dir)),"utf8");
 const app=readFileSync(fileURLToPath(new URL("app.mjs",dir)),"utf8");
 assert.match(html,/data-kompas-alternative/);
 assert.match(html,/frozen-week-chart\.js/);
 assert.match(html,/lightweight-charts-5\.2\.0\.js/);
 assert.match(html,/data-stage="168"/);
 assert.match(html,/data-concept-choice="nordic"/);
 assert.match(html,/data-concept-choice="atelier"/);
 assert.match(html,/data-concept-choice="signal"/);
 assert.match(html,/full-week-fixture/);
 assert.match(app,/CNWeekChart\.mount/);
 assert.doesNotMatch(app,/createChart\(/);
 assert.doesNotMatch(html,/appdeploy/);
});
