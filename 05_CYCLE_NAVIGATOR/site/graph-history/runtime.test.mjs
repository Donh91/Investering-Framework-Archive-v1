// Exercises the ACTUAL Graph History inline browser module with a fake DOM.
// All fabricated W46 data is TEST-ONLY and NEVER reaches Pages/public sources.
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {resolve} from 'node:path';

const root=fileURLToPath(new URL('../../../',import.meta.url));
const page=readFileSync(resolve(root,'05_CYCLE_NAVIGATOR/site/graph-history/index.html'),'utf8');
const match=page.match(/<script type="module">([\s\S]*?)<\/script>/);
assert.ok(match,'GRAPH_HISTORY_MODULE_MISSING');
const javascript=match[1];

function week45(){
 return {week:'2026-W45',forecast_status:'UNAVAILABLE',forecast:[],
  forecast_model_declared_quote:'UNAVAILABLE',source_sha256:'b'.repeat(64),
  issued_at_utc:'2026-11-02T08:19:08Z',first_eligible_utc:'2026-11-02T09:00:00Z',
  actual_status:'LIVE',observed_hours:3};
}
function syntheticWeek46(){
 return {week:'2026-W46',forecast_status:'PUBLISHED',
  forecast_model_declared_quote:'USDT',source_sha256:'a'.repeat(64),
  issued_at_utc:'2026-11-09T07:20:00Z',first_eligible_utc:'2026-11-09T08:00:00Z',
  actual_status:'PENDING',observed_hours:0,
  forecast:Array.from({length:7},(_,i)=>({day:i+1,low:77000,expected_close:78000+i*250,high:83000}))};
}
function fixture(){
 return {contract:'CN_GRAPH_HISTORY_TIMELINE_v1',actual_unit:'USDT',
  comparison_precision_eligible:false,weeks:[week45(),syntheticWeek46()],actual:[
   {time:'2026-11-02T01:00:00Z',close:80200},
   {time:'2026-11-02T02:00:00Z',close:80150},
   // one missing 03:00 UTC source bar must visibly split observed segments
   {time:'2026-11-02T04:00:00Z',close:80300}
  ]};
}
const clone=x=>structuredClone(x);

class Element{
 constructor(tag){this.tag=tag;this.children=[];this.attrs={};this.textContent='';this.value='';this.parent=null;this.listeners={};}
 setAttribute(k,v){this.attrs[k]=String(v)}
 append(...items){for(const item of items){item.parent=this;this.children.push(item)}}
 replaceChildren(...items){this.children=[];this.append(...items)}
 get firstChild(){return this.children[0]||null}
 remove(){if(!this.parent)return;this.parent.children=this.parent.children.filter(x=>x!==this);this.parent=null}
 addEventListener(k,fn){this.listeners[k]=fn}
}
async function run(value,{clientWidth=390,fetchError=false}={}){
 const elements=new Map();
 const ids=['plot','scroll','period','last-close','last-time','notice','weeks','forecasts','hours','archive'];
 for(const id of ids)elements.set(id,new Element(id));
 elements.get('period').value='10';
 elements.get('scroll').scrollWidth=880;
 elements.get('scroll').clientWidth=clientWidth;
 elements.get('scroll').scrollLeft=0;
 const document={getElementById:id=>{
  assert.ok(elements.has(id),'UNEXPECTED_ELEMENT_'+id);return elements.get(id);
 },createElement:tag=>new Element(tag),createElementNS:(ns,tag)=>{
  assert.equal(ns,'http://www.w3.org/2000/svg');return new Element(tag);
 }};
 const fetched=[];
 const fetch=async (url)=>{fetched.push(url);if(fetchError)throw Error('OFFLINE');
  assert.equal(url,'../data/graph-history/timeline.json');
  return {ok:true,json:async()=>clone(value)};
 };
 await vm.runInNewContext('(async()=>{'+javascript+'\n})()',{document,fetch,Date,Intl,console},{timeout:3500});
 const paths=elements.get('plot').children.filter(x=>x.tag==='path');
 return {elements,fetched,paths,
  blue:paths.filter(x=>x.attrs.stroke==='#79aaff'),
  green:paths.filter(x=>x.attrs.stroke==='#31d0a0')};
}
test('W45 0/7 + synthetic W46 7/7 is shown with USDT original blue only, green has hourly gap',async()=>{
 const r=await run(fixture());
 assert.equal(r.elements.get('weeks').textContent,2);
 assert.equal(r.elements.get('forecasts').textContent,1);
 assert.equal(r.elements.get('hours').textContent,'3');
 assert.equal(r.fetched.length,1);
 assert.equal(r.blue.length,1);
 assert.equal(r.green.length,1);
 assert.ok((r.green[0].attrs.d.match(/M/g)||[]).length>=2,'MISSING_SOURCE_HOUR_INTERPOLATED');
 assert.match(r.elements.get('notice').textContent,/1 uge\(r\)/);
 assert.match(r.elements.get('last-close').textContent,/USDT/);
 assert.equal(r.elements.get('scroll').scrollLeft,490);
 assert.equal(r.elements.get('archive').children.length,2);
});
test('official seven closes in USD are archived as real, but never drawn against USDT',async()=>{
 const d=fixture();d.weeks[1].forecast_model_declared_quote='USD';
 const r=await run(d);
 assert.equal(r.blue.length,0);
 assert.equal(r.green.length,1);
 assert.equal(r.elements.get('forecasts').textContent,0);
 assert.match(r.elements.get('notice').textContent,/2 uge\(r\)/);
 assert.match(r.elements.get('archive').children[0].children[1].textContent,/Original udstedt · ikke sammenlignelig med USDT/);
 assert.match(r.elements.get('archive').children[0].children[1].textContent,/prognosevaluta USD/);
});
test('original quote missing or fake proof, late issue, premature day 1 and wrong window never draw blue',async()=>{
 for(const change of [
  d=>{d.weeks[1].forecast_model_declared_quote='UNAVAILABLE'},
  d=>{d.weeks[1].source_sha256='invalid'},
  d=>{d.weeks[1].issued_at_utc='2026-11-10T07:00:00Z'},
  d=>{d.weeks[1].issued_at_utc='2026-11-09T08:00:01Z'},
  d=>{d.weeks[1].forecast[2].day=7},
  d=>{d.weeks[1].forecast[2].expected_close=99999},
  d=>{d.actual_unit='USD'},
 ]){
  const d=fixture();change(d);
  const r=await run(d);
  assert.equal(r.blue.length,0);
  assert.equal(r.elements.get('forecasts').textContent,0);
  assert.equal(r.green.length,1);
 }
});
test('real W45 history with no original seven-day blue remains readable and currency-safe',async()=>{
 const d=fixture();d.weeks=[week45()];
 const r=await run(d,{clientWidth:430});
 assert.equal(r.blue.length,0);
 assert.equal(r.green.length,1);
 assert.equal(r.elements.get('forecasts').textContent,0);
 assert.match(r.elements.get('notice').textContent,/Ingen opdigtet blå kurve/);
});
test('offline Graph History fails closed without fabricated observations or a source-issued blue curve',async()=>{
 const r=await run(fixture(),{fetchError:true});
 assert.equal(r.blue.length,0);
 assert.equal(r.green.length,0);
 assert.match(r.elements.get('notice').textContent,/utilgængelig/);
});
