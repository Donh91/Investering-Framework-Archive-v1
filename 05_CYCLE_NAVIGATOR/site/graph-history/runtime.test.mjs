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
  blue:paths.filter(x=>x.attrs.stroke==='#2563eb'),
  green:paths.filter(x=>x.attrs.stroke==='#099866'),
  amber:paths.filter(x=>x.attrs.stroke==='#e9ae65'),
  dividers:elements.get('plot').children.filter(x=>x.tag==='line'&&x.attrs.stroke==='#9aa8bb')};
}
test('PUBLIC W46-only start removes W45 actual-only weeks without erasing source archive',async()=>{
 const d=fixture();d.start_week='2026-W46';
 d.actual.push({time:'2026-11-09T01:00:00Z',close:74600});
 d.actual.push({time:'2026-11-09T02:00:00Z',close:74500});
 const r=await run(d);
 assert.equal(r.elements.get('weeks').textContent,1);
 assert.equal(r.elements.get('forecasts').textContent,1);
 assert.equal(r.elements.get('hours').textContent,'2');
 assert.equal(r.elements.get('archive').children.length,1);
 assert.equal(r.elements.get('archive').children[0].children[0].textContent,'2026-W46');
 assert.equal(r.dividers.length,1);
 assert.equal(r.blue.length,1);
 assert.equal(r.green.length,1);
 assert.match(r.elements.get('last-close').textContent,/USDT/);
 const unavailable=fixture();unavailable.start_week='2026-W46';
 unavailable.weeks[1].forecast_status='UNAVAILABLE';
 const absent=await run(unavailable);
 assert.equal(absent.elements.get('weeks').textContent,0);
 assert.equal(absent.elements.get('forecasts').textContent,0);
 assert.equal(absent.elements.get('hours').textContent,'0');
 assert.equal(absent.blue.length,0);
 assert.equal(absent.green.length,0);
 assert.equal(absent.elements.get('archive').children.length,1);
 assert.match(absent.elements.get('notice').textContent,/Ingen prognosehistorik før mandag 9. november/);
});

test('W45 0/7 + synthetic W46 7/7 is shown with USDT original blue only, green has hourly gap',async()=>{
 const r=await run(fixture());
 assert.equal(r.elements.get('weeks').textContent,2);
 assert.equal(r.elements.get('forecasts').textContent,1);
 assert.equal(r.elements.get('hours').textContent,'3');
 assert.equal(r.fetched.length,1);
 assert.equal(r.blue.length,1);
 assert.equal(r.green.length,1);
 assert.equal(r.dividers.length,2,'WEEK_SEPARATORS_MISSING');
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

function honestThursday(){
 const row=(asset)=>{
  const values=asset==='BTC'?[75573.64,74670.48,74133.78,73813.61]:[2244.16,2210.28,2190.20,2178.24];
  const ranges=asset==='BTC'?[[74143.64,77417.33],[71871.41,78516.89],[71354.82,77578.57],[71046.66,77020.96]]:
    [[2186.31,2315.09],[2097.79,2364.50],[2078.73,2328.80],[2067.38,2307.65]];
  return values.map((v,i)=>({day:i+4,target_at_utc:new Date(Date.UTC(2026,10,6+i)).toISOString().replace('.000Z','Z'),
   expected_close:v,low:ranges[i][0],high:ranges[i][1]}));
 };
 return {contract:'CN_GRAPH_HISTORY_FIRST_HONEST_MIDWEEK_RESEARCH_v1',
  forecast_week:'2026-W45',original_source:'OWNER_ISSUED_2026_11_05_COMMENT_6668153478',
  frozen_packet_sha256:'c'.repeat(64),
  issued_at_utc:'2026-11-05T20:11:38Z',input_cutoff_utc:'2026-11-05T18:00:00Z',
  price_quote:'USDT',provider_first_known_verified:false,research_only:true,
  original_monday_issuance:false,official_scoring_eligible:false,portfolio_action_authority:false,
  BTC:row('BTC'),ETH:row('ETH')};
}

test('later Thursday W45 research is never plotted as a competing third forecast series',async()=>{
 const d=fixture();d.first_honest_midweek_research=honestThursday();
 const r=await run(d);
 assert.equal(r.amber.length,0,'RESEARCH_SNEAKED_INTO_APPROVED_TWO_LINE_HISTORY');
 assert.equal(r.blue.length,1);
 assert.equal(r.green.length,1);
 assert.equal(r.elements.get('forecasts').textContent,1,'RESEARCH_MUST_NOT_COUNT_AS_ORIGINAL');
 assert.doesNotMatch(r.elements.get('notice').textContent,/Gul stiplet/);
 assert.equal(d.first_honest_midweek_research.BTC[0].target_at_utc,'2026-11-06T00:00:00Z');
});

test('malformed or promoted W45 research never changes original green and blue history',async()=>{
 const mutations=[
  d=>{d.first_honest_midweek_research.issued_at_utc='2026-11-05T18:00:00Z'},
  d=>{d.first_honest_midweek_research.input_cutoff_utc='2026-11-05T21:00:00Z'},
  d=>{d.first_honest_midweek_research.price_quote='USD'},
  d=>{d.first_honest_midweek_research.official_scoring_eligible=true},
  d=>{d.first_honest_midweek_research.original_monday_issuance=true},
  d=>{d.first_honest_midweek_research.provider_first_known_verified=true},
  d=>{d.first_honest_midweek_research.portfolio_action_authority=true},
  d=>{d.first_honest_midweek_research.frozen_packet_sha256='invalid'},
  d=>{d.first_honest_midweek_research.BTC[0].target_at_utc='2026-11-05T00:00:00Z'},
  d=>{d.first_honest_midweek_research.BTC[0].expected_close=1e9},
  d=>{d.first_honest_midweek_research.ETH[0].low=99999},
  d=>{d.weeks[0].forecast_status='PUBLISHED'},
  d=>{d.actual_unit='USD'}
 ];
 for(const mutate of mutations){
  const d=fixture();d.first_honest_midweek_research=honestThursday();mutate(d);
  const r=await run(d);
  assert.equal(r.amber.length,0,'UNTRUSTED_MIDWEEK_OVERLAY_RENDERED');
  assert.equal(r.green.length,1);
  assert.equal(r.elements.get('forecasts').textContent,r.blue.length,'RESEARCH_COUNTED_AS_OFFICIAL');
 }
});

test('offline Graph History fails closed without fabricated observations or a source-issued blue curve',async()=>{
 const r=await run(fixture(),{fetchError:true});
 assert.equal(r.blue.length,0);
 assert.equal(r.green.length,0);
 assert.match(r.elements.get('notice').textContent,/utilgængelig/);
});

test('original approved light History styling and compact route use one verified renderer',async()=>{
 const html=page;
 assert.match(html,/background:#f6f8fc/);
 assert.match(html,/\.cn-embedded-history #plot\{/);
 assert.match(html,/URLSearchParams\(location\.search\)/);
 assert.match(html,/Ugegrænser/);
 assert.doesNotMatch(html,/radial-gradient\(/);
 assert.doesNotMatch(html,/class="midweek"/);
 const d=fixture();d.weeks=[week45()];
 const r=await run(d,{clientWidth:430});
 assert.equal(r.elements.get('plot').attrs.width,'430','SINGLE_WEEK_MUST_NOT_FORCE_WIDE_SCROLL');
 assert.equal(r.dividers.length,1,'VISIBLE_WEEK_BOUNDARY_REQUIRED');
 assert.equal(r.blue.length,0,'W45_MISSING_FORECAST_MUST_REMAIN_UNPLOTTED');
});
