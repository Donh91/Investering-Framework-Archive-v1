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
for(const asset of ['BTC','ETH']){
 test(asset+' day cell begins Monday 00Z, spans seven cells and retains close knots',()=>{
  const x=harness(),m=source(6,asset);x.render(m,6,asset);
  const band=x.get('range-band').getAttribute('d');
  assert.equal(Math.min(...points(band).map(p=>p[0])),14);
  assert.equal((band.match(/Z/g)||[]).length,7);
  assert.equal(points(x.get('forecast').getAttribute('d')).length,7);
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
