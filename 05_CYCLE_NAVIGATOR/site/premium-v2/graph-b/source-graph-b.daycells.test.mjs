/** Source Graph B regression: isolated native renderer, no network or published prices. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const HOUR=3600000,DAY=24*HOUR,START=Date.parse('2026-11-09T00:00:00Z');
const iso=ms=>new Date(ms).toISOString().replace('.000Z','Z');

class Element {
 constructor(tag='div'){this.tag=tag;this.attrs={};this.children=[];this.dataset={};this.style={};this.textContent='';this.hidden=false;}
 setAttribute(k,v){this.attrs[k]=String(v);}
 getAttribute(k){return this.attrs[k]??null;}
 append(...children){this.children.push(...children);}
 replaceChildren(...children){this.children=[...children];}
 querySelector(sel){return sel==='[data-actual-daily-ranges]'?
  this.children.find(c=>Object.hasOwn(c.attrs,'data-actual-daily-ranges'))??null:null;}
 addEventListener(){}
}

function harness(){
 const elements=new Map();
 const doc={
  body:{classList:{contains:()=>false}},documentElement:{},
  getElementById(id){if(!elements.has(id))elements.set(id,new Element());return elements.get(id);},
  querySelector(){return null;},querySelectorAll(){return [];},
  createElement:tag=>new Element(tag),createElementNS:(_ns,tag)=>new Element(tag),
  createTextNode:text=>Object.assign(new Element('text'),{textContent:text})
 };
 let script=fs.readFileSync(new URL('./source-graph-b.mjs',import.meta.url),'utf8');
 const importLine="import {readOfficialGraphB,replayObservedUntil} from './official-source-adapter.mjs';";
 assert.ok(script.includes(importLine),'renderer import contract changed; update harness');
 script=script.replace(importLine,'');
 script=script.replaceAll('import.meta.url',JSON.stringify('https://example.invalid/graph-b/source-graph-b.mjs'));
 const boundary="document.querySelectorAll('[data-asset]').forEach(b=>b.addEventListener";
 assert.ok(script.includes(boundary),'renderer entry boundary changed; update harness');
 script=script.slice(0,script.indexOf(boundary));
 const replayObservedUntil=(model,at)=>{
  const closed=Date.parse(at);
  const visible=(model.hourly_observations||[]).filter(p=>p.time*1000<=closed);
  return visible.length?[visible]:[];
 };
 const ctx=vm.createContext({
  document:doc,URL,Intl,Date,console,
  replayObservedUntil,
  readOfficialGraphB(){throw Error('NO_REAL_SOURCE_OR_NETWORK_IN_TEST');}
 });
 vm.runInContext(script+";globalThis.__render=(source,hour,selected='BTC')=>{model=source;asset=selected;language='en';sliderHour=hour;plot();}",ctx);
 return {render:ctx.__render,get:id=>doc.getElementById(id)};
}

function source(hours=6,asset='BTC'){
 const base=asset==='BTC'?100:200;
 const boundaries=[[0,2],[2,4],[4,7]].map(([a,b])=>({
  window_start_utc:iso(START+a*DAY),window_end_utc:iso(START+b*DAY),
  forecast_low:base-12,forecast_high:base+20
 }));
 return {
  asset,source_status:'SOURCE_BOUNDED',forecast_status:'SOURCE_ISSUED',
  forecast_comparison_quote_status:'SAME_DECLARED_UNIT',
  daily_range_status:'UNAVAILABLE',daily_ranges:[],actual_daily_ranges:[],
  live_freshness:'FRESH',actual_quote_unit:'USDT',forecast_declared_quote_unit:'USDT',
  forecast_week:'2026-W46',public_issue_number:34,bands:boundaries,
  forecast:Array.from({length:7},(_,i)=>({
   day:i+1,time:(START+(i+1)*DAY)/1000,
   expected_close:base+i,low:base-10+i,high:base+12+i
  })),
  hourly_observations:Array.from({length:hours},(_,i)=>({
   time:(START+(i+1)*HOUR)/1000,value:base+Math.floor(i/24)
  })),
  last_observed_at_utc:iso(START+hours*HOUR)
 };
}
const points=d=>[...d.matchAll(/[ML](-?[0-9.]+),(-?[0-9.]+)/g)]
 .map(m=>[Number(m[1]),Number(m[2])]);
// v2.4G2b (owner-approval pending): the forecast may be a monotone cubic through the SAME knots.
// Knots = the M point plus the end point of every C segment (or every L point for a polyline).
const knots=d=>{const out=[];for(const m of d.matchAll(/([MLC])([^MLCZ]*)/g)){const n=m[2].trim().split(/[ ,]+/).map(Number);if(n.length>=2)out.push([n[n.length-2],n[n.length-1]])}return out};
const cubics=d=>{const k=[...d.matchAll(/C([^MLCZ]*)/g)].map(m=>m[1].trim().split(/[ ,]+/).map(Number));return k};
for(const asset of ['BTC','ETH']){
 test(asset+' day cell begins Monday 00Z, spans seven cells and retains close knots',()=>{
  const x=harness(),m=source(6,asset);x.render(m,6,asset);
  const band=x.get('range-band').getAttribute('d');
  assert.equal(Math.min(...points(band).map(p=>p[0])),14);
  assert.equal((band.match(/Z/g)||[]).length,7);
  assert.equal(knots(x.get('forecast').getAttribute('d')).length,7);
  assert.equal(points(x.get('range-upper').getAttribute('d')).length,14);
  assert.equal(points(x.get('range-lower').getAttribute('d')).length,14);
 });
 test(asset+' hidden future observation cannot rescale earlier replay',()=>{
  const original=source(168,asset),future=source(168,asset);
  future.hourly_observations[100].value=999999;
  const left=harness(),right=harness();
  left.render(original,24,asset);right.render(future,24,asset);
  assert.equal(left.get('forecast').getAttribute('d'),right.get('forecast').getAttribute('d'));
  assert.equal(left.get('actual').getAttribute('d'),right.get('actual').getAttribute('d'));
 });
 test(asset+' does not draw issued forecast when source unavailable',()=>{
  const m=source(6,asset);m.source_status='UNAVAILABLE';
  const x=harness();x.render(m,6,asset);
  assert.equal(x.get('range-band').getAttribute('d'),'');
  assert.equal(x.get('forecast').getAttribute('d'),'');
 });
 test(asset+' incompatible quote draws no forecast band or knots',()=>{
  const m=source(6,asset);m.forecast_status='SOURCE_ISSUED_QUOTE_INCOMPARABLE';
  m.forecast_comparison_quote_status='UNVERIFIED_OR_DIFFERENT_UNIT';
  const x=harness();x.render(m,6,asset);
  assert.equal(x.get('range-band').getAttribute('d'),'');
  assert.equal(x.get('forecast').getAttribute('d'),'');
 });
}


// SITE owner's 9 Nov W46 GENERAL REHEARSAL. All prices are intentionally
// FICTIONAL and exist ONLY in this Node test, never in public data or Pages.
// This calls the ACTUAL source-graph-b.mjs plot() from harness(), not a
// recreated chart, new forecast generator or retrospectively scored signal.
test('W46 7 distinct frozen closes produce a non-flat BLUE weekly Graph B path; green follows chosen hour',()=>{
 const m=source(108,'BTC');
 const expected=[77150,78900,78020,80840,79280,82300,80760];
 const lows=[75650,77050,76700,79100,77800,80500,79400];
 const highs=[78350,80120,79200,82100,80550,83600,82400];
 m.bands=m.bands.map(b=>({...b,forecast_low:75000,forecast_high:84000}));
 m.forecast=m.forecast.map((p,i)=>({...p,expected_close:expected[i],low:lows[i],high:highs[i]}));
 m.hourly_observations=m.hourly_observations.map((p,i)=>({
  ...p,value:76000+Math.floor(i/24)*370+(i%24)*16
 }));
 const early=harness(),late=harness();
 early.render(m,30,'BTC');late.render(m,80,'BTC');
 const blue=late.get('forecast').getAttribute('d'), knotsBlue=knots(blue);
 assert.equal(knotsBlue.length,7,'NO_SEVEN_ORIGINAL_FROZEN_DAY_POINTS');
 assert.equal(new Set(knotsBlue.map(p=>p[1])).size,7,
  'BLUE_EXPECTED_CLOSE_PATH_IS_WRONGLY_STRAIGHT');
 assert.ok(Math.max(...knotsBlue.map(p=>p[1]))-Math.min(...knotsBlue.map(p=>p[1]))>100,
  'BLUE_UNDERREPRESENTS_SOURCE_MOVEMENT');
 assert.equal(early.get('forecast').getAttribute('d'),blue,
  'FROZEN_FORECAST_CHANGED_DURING_WEEK_REPLAY');
 assert.notEqual(early.get('actual').getAttribute('d'),late.get('actual').getAttribute('d'),
  'GREEN_OBSERVED_SERIES_DID_NOT_REVEAL_HOURLY_PROGRESS');
 assert.equal((late.get('range-band').getAttribute('d').match(/Z/g)||[]).length,7,
  'HIGH_LOW_DAILY_CELLS_NOT_RENDERED');
 assert.ok(late.get('actual').getAttribute('d').startsWith('M'));
 // Removing source issuance immediately removes blue, without touching green.
 const unavailable={...m,forecast_status:'UNAVAILABLE',forecast:[]};
 const gate=harness();gate.render(unavailable,80,'BTC');
 assert.equal(gate.get('forecast').getAttribute('d'),'',
  'PUBLISHED_FAKE_BLUE_PERSISTED_WITHOUT_SEVEN_DAY_SOURCE');
 assert.ok(gate.get('actual').getAttribute('d').length>0,
  'SOURCE_REFUSAL_ERASED_INDEPENDENT_VERIFIED_GREEN_OBSERVATIONS');
});

// v2.4G2: the forecast dots are exactly the 7 source-issued expected closes; nothing is added,
// interpolated or shown when the forecast is not issued or the quote is not comparable.
for(const asset of ['BTC','ETH']){
 test(asset+' forecast dots coincide with the 7 forecast knots and vanish without issuance',()=>{
  const x=harness(),m=source(80,asset);x.render(m,80,asset);
  const knotList=knots(x.get('forecast').getAttribute('d'));
  const dots=[...x.get('forecast-points').getAttribute('d').matchAll(/M(-?[0-9.]+),(-?[0-9.]+) l0,0/g)]
   .map(v=>[Number(v[1]),Number(v[2])]);
  assert.equal(dots.length,7,'FORECAST_DOTS_NOT_SEVEN');
  assert.deepEqual(dots,knotList,'FORECAST_DOTS_NOT_ON_SOURCE_KNOTS');
  const off=source(6,asset);off.forecast_status='SOURCE_ISSUED_QUOTE_INCOMPARABLE';
  off.forecast_comparison_quote_status='UNVERIFIED_OR_DIFFERENT_UNIT';
  const y=harness();y.render(off,6,asset);
  assert.equal(y.get('forecast-points').getAttribute('d')??'','','FORECAST_DOTS_WITHOUT_COMPARABLE_ISSUANCE');
 });
}

// v2.4G2b: the curve passes through all 7 source points (±0.5 px) and never overshoots the
// y-range of each neighbouring pair (no implied highs or lows). Fictional test prices only.
test('monotone forecast passes through the 7 points and never overshoots a neighbouring pair',()=>{
 const m=source(80,'BTC');
 const expected=[77150,78900,78020,80840,79280,82300,80760];
 m.forecast=m.forecast.map((p,i)=>({...p,expected_close:expected[i],low:expected[i]-1500,high:expected[i]+1500}));
 const x=harness();x.render(m,80,'BTC');
 const d=x.get('forecast').getAttribute('d'),k=knots(d),dots=[...x.get('forecast-points').getAttribute('d').matchAll(/M(-?[0-9.]+),(-?[0-9.]+) l0,0/g)].map(v=>[+v[1],+v[2]]);
 assert.equal(k.length,7);
 k.forEach((p,i)=>{assert.ok(Math.abs(p[0]-dots[i][0])<=0.5&&Math.abs(p[1]-dots[i][1])<=0.5,'CURVE_MISSES_SOURCE_POINT_'+i)});
 const segs=cubics(d);
 segs.forEach((c,i)=>{const p0=k[i],[x1,y1,x2,y2,x3,y3]=c;const lo=Math.min(p0[1],y3)-0.5,hi=Math.max(p0[1],y3)+0.5;
  for(let j=0;j<=50;j++){const t=j/50,u=1-t;const yy=u*u*u*p0[1]+3*u*u*t*y1+3*u*t*t*y2+t*t*t*y3;
   assert.ok(yy>=lo&&yy<=hi,'CURVE_OVERSHOOT_SEGMENT_'+i+'_t'+t)}});
});
