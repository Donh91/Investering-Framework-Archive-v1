/** Test-only DOM/clock/fetch harness. Exercises actual UI modules and real adapters. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';
import {readOfficialCompassPath} from './compass/official-compass-path.mjs';
import {readOfficialGraphB,replayObservedUntil} from './graph-b/official-source-adapter.mjs';
import {sourceOnlyPriceRangeProof} from './proof/price-range-proof.mjs';

function snapshot({last=168}={}){
 const start=Date.parse('2026-10-19T00:00:00Z'),hour=3600000;
 const iso=n=>new Date(start+n*hour).toISOString().replace('.000Z','Z');
 const windows={},rows=[];
 for(const [id,a,b] of [['day_1_2',0,48],['day_3_4',48,96],['day_5_7',96,168]]){
  const observed=Math.max(0,Math.min(last,b)-a);
  windows[id]={window_start_utc:iso(a),window_end_utc:iso(b),scoring_start_utc:iso(a),
   phase:last>=b?'COMPLETE':last<=a?'NOT_STARTED':'LIVE',observed_hours:observed,
   expected_hours_final:b-a,rows_total:2,rows_scored:observed?2:0,
   coverage_complete_to_date:true,score_to_date:observed?75:null};
  for(const asset of ['BTC','ETH'])rows.push({asset,window:id,
   forecast_low:asset==='BTC'?80000:2000,forecast_high:asset==='BTC'?90000:3000});
 }
 const hourly={contract:'CN_PUBLIC_HOURLY_PRICE_PATH_v1',source:'HOURLY_SPOT_PASS_ONLY',
  semantics:'OBSERVED_HOURLY_CLOSE_NOT_A_PROSPECTIVE_FORECAST',forecast_week:'2026-W43',
  public_issue_number:30,observed_through_utc:iso(last)};
 for(const asset of ['BTC','ETH'])hourly[asset]=[167,168].filter(n=>n<=last).map(n=>({
  observed_at_utc:iso(n),close:(asset==='BTC'?80000:2000)+n}));
 return {schema:'CN_PUBLIC_SNAPSHOT_V2',package:{market_cycle_context:{current_phase:'BROAD_ALTSEASON'}},
  public_series:{current_public_projection:{public_issue_number:30,forecast_week:'2026-W43'}},
  public_live_precision:{contract:'CN_PUBLIC_LIVE_PRICE_PRECISION_v1',public_issue_number:30,
   forecast_week:'2026-W43',score_family:'PRICE_RANGE_PRECISION',formula:'70pct_containment_plus_30pct_jaccard',
   frozen_at_utc:'2026-10-18T23:00:00Z',scoring_valid_from_utc:iso(0),
   live_as_of_utc:iso(last),freshness_sla_minutes:90,window_scores:windows,rows,
   daily_observations:{contract:'CN_PUBLIC_DAILY_OBSERVATIONS_v1',observed_through_utc:iso(last)},
   hourly_price_path:hourly,daily_price_path:{contract:'CN_FROZEN_DAILY_PRICE_PATH_v1',
    forecast_week:'2026-W43',BTC:{status:'UNAVAILABLE',points:[]},ETH:{status:'UNAVAILABLE',points:[]}}}};
}
function compass(){
 return {contract:'PUBLIC_COMPASS_PROJECTION_v1',data_status:'OK',action_now:'HOLD',
  issued_at_utc:'2026-10-26T00:00:00Z',full_stack:{official_freshness:{
   contract:'OFFICIAL_COMPASS_SOURCE_FRESHNESS_READBACK_v1',status:'VERIFIED_OWNER_POLICY',
   source_asof_utc:'2026-10-26T00:00:00Z',valid_until_utc:'2026-10-26T02:00:00Z'}},
  weekly_context:{contract:'CN_COMPASS_WEEKLY_ALIGNMENT_v1',status:'ALIGNED',
   forecast_week:'2026-W43',public_issue_number:30},
  horizons:Object.fromEntries(['NEXT_12H','NEXT_1_3D','NEXT_5_7D','NEXT_2_3W','CYCLE_ALTCOINS_3_8W'].map(k=>[k,{expected_direction:'UP',action_posture:'WAIT',expected_path:'Source-issued scenario only'}])),
  capitalization_ladder:['BTC','ETH','LARGE_CAPS','MID_CAPS','SMALL_CAPS','MICROCAPS','MEMES'].map(segment=>({segment,status:'SOURCE'})),
  bull_bear_scale:{contract:'OFFICIAL_COMPASS_BULL_BEAR_DISPLAY_v1',semantics:'EVIDENCE_BALANCE_NOT_PROBABILITY',
   authority:{probability_model:false},horizons:Object.fromEntries(['1_3d','5_7d','2_3w'].map(k=>[k,{bull:8,bear:2}]))}};
}
class Element{
 constructor(tag=''){this.tagName=tag.toUpperCase();this.textContent='';this.dataset={};this.style={};this.children=[];this.attrs={};this.listeners={};this.open=false;this.didFocus=false;}
 get firstElementChild(){return this.children[0]||null}
 focus(){this.didFocus=true}
 append(...nodes){this.children.push(...nodes)}
 replaceChildren(...nodes){this.children=nodes;this.textContent=''}
 setAttribute(k,v){this.attrs[k]=String(v)}
 getAttribute(k){return this.attrs[k]}
 querySelector(){return null}
 addEventListener(k,fn){this.listeners[k]=fn}
 click(){return this.listeners.click?.({currentTarget:this})}
}
async function harness(path,{latest=snapshot(),fetcher=null,sourceTransform=null}={}){
 let now=Date.parse('2026-10-26T00:30:00Z'),serial=0;
 const timers=new Map(),elements=new Map(),events={};
 const get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id)};
 const buttons={};
 for(const [key,values] of Object.entries({asset:['BTC','ETH'],lang:['da','en'],proofStep:['freeze','observed','assess']})){
  buttons[key]=values.map(value=>{const e=new Element();e.dataset[key]=value;return e});
 }
 const doc={documentElement:{lang:'da'},hidden:false,getElementById:get,
  createElement:tag=>new Element(tag),createElementNS:(namespace,tag)=>new Element(tag),createTextNode:text=>({textContent:text}),
  querySelector:()=>null,querySelectorAll:q=>q==='[data-asset]'?buttons.asset:q==='[data-lang]'?buttons.lang:q==='[data-proof-step]'?buttons.proofStep:[],
  addEventListener:(k,fn)=>(events[k]??=[]).push(fn),dispatchEvent:e=>(events[e.type]||[]).forEach(fn=>fn(e))};
 const timer=(fn,ms)=>{const id=++serial;timers.set(id,{fn,at:now+ms});return id};
 let fetchImpl=fetcher||((url)=>Promise.resolve({ok:true,json:async()=>String(url).endsWith('compass.json')?compass():String(url).endsWith('publication-lineage.json')?null:latest}));
 class Clock extends Date {constructor(...args){super(...(args.length?args:[now]))} static now(){return now}}
 const context={document:doc,window:{addEventListener(){},matchMedia:()=>({matches:false})},
  fetch:(...args)=>fetchImpl(...args),URL,Date:Clock,Intl,AbortSignal,CustomEvent:class{constructor(type){this.type=type}},
  setTimeout:timer,clearTimeout:id=>timers.delete(id),setInterval:timer,clearInterval:id=>timers.delete(id),
  readOfficialCompassPath,readOfficialGraphB,replayObservedUntil,sourceOnlyPriceRangeProof,
  sourceReadbackProofRows:()=>[],console,navigator:{}};
 let source=(await readFile(new URL(path,import.meta.url),'utf8'))
  .replace(/^import .*;\n/gm,'').replaceAll('import.meta.url',JSON.stringify('https://test.invalid/next/assets/app.js'));
 if(sourceTransform)source=sourceTransform(source);
 vm.runInNewContext(source,context,{filename:path});
 const settle=async()=>{for(let i=0;i<6;i++)await new Promise(resolve=>setImmediate(resolve))};
 await settle();
 return {get,doc,buttons,settle,timers,setFetch:fn=>{fetchImpl=fn},
  async advance(iso){now=Date.parse(iso);for(const [id,t] of [...timers])if(t.at<=now){timers.delete(id);t.fn()}await settle()},
  language(value){doc.documentElement.lang=value;doc.dispatchEvent({type:'cn:languagechange'})}};
}
test('P2-A loaded Bull/Bear clears on offline refresh and stays unavailable across DA/EN',async()=>{
 const h=await harness('./compass/compass-path-ui.mjs');
 assert.equal(h.get('official-pilot-bias').textContent,'8 / 2');
 assert.match(h.get('official-pilot-bias-note').textContent,/2026.*UTC/);
 h.setFetch(async()=>{throw Error('TEST_OFFLINE')});
 h.doc.dispatchEvent({type:'visibilitychange'});await h.settle();
 for(const language of ['en','da','en']){
  h.language(language);
  assert.equal(h.get('official-pilot-bias').textContent,'—');
  assert.equal(h.get('official-pilot-action').textContent,'—');
  assert.doesNotMatch(h.get('official-pilot-bias-note').textContent,/8 \/ 2|2026/);
 }
 await h.advance('2026-10-26T03:00:00Z');h.language('en');
 assert.equal(h.get('official-pilot-status').textContent,'SOURCE UNAVAILABLE');
});
test('P2-A open-tab expiry clears numerical Bull/Bear and its current validity',async()=>{
 const h=await harness('./compass/compass-path-ui.mjs');
 await h.advance('2026-10-26T02:00:01Z');
 assert.equal(h.get('official-pilot-bias').textContent,'—');
 h.language('en');assert.equal(h.get('official-pilot-bias').textContent,'—');
 assert.match(h.get('official-pilot-status').textContent,/EXPIRED/);
});
test('P2-B weekly replay includes 168, scrubs 167 exactly, missing last close caps at 167',async()=>{
 for(const last of [168,167]){
  const h=await harness('./graph-b/source-graph-b.mjs',{latest:snapshot({last})});
  assert.equal(h.get('hour-slider').max,String(last));
  assert.match(h.get('observed-value').textContent,new RegExp('80[.,]'+last));
  const slider=h.get('hour-slider');slider.value='167';slider.listeners.input({currentTarget:slider});
  assert.match(h.get('observed-value').textContent,/80[.,]167/);
  slider.value='168';slider.listeners.input({currentTarget:slider});
  assert.equal(slider.value,String(last));
  assert.match(h.get('observed-value').textContent,new RegExp('80[.,]'+last));
 }
});
test('P2-D unresolved and out-of-order asset fetches cannot borrow BTC under ETH label',async()=>{
 const h=await harness('./graph-b/source-graph-b.mjs');
 const pending=[];
 h.setFetch(url=>new Promise(resolve=>pending.push({url,resolve})));
 h.buttons.asset[1].click(); // ETH loading
 h.buttons.lang[1].click();
 assert.equal(h.get('pair').textContent,'ETH / USD');
 assert.equal(h.get('observed-value').textContent,'—');
 h.get('hour-slider').listeners.input({currentTarget:{value:'168'}});
 assert.equal(h.get('observed-value').textContent,'—');
 h.buttons.asset[0].click(); // BTC wins the race
 for(const p of pending.slice(2))p.resolve({ok:true,json:async()=>String(p.url).endsWith('latest.json')?snapshot():null});
 await h.settle();assert.match(h.get('observed-value').textContent,/80,168/);
 for(const p of pending.slice(0,2))p.resolve({ok:true,json:async()=>String(p.url).endsWith('latest.json')?snapshot():null});
 await h.settle();assert.equal(h.get('pair').textContent,'BTC / USD');
 assert.match(h.get('observed-value').textContent,/80,168/);
});
test('P2-C Proof renders timestamp and SLA separately from provisional score; open tab expires',async()=>{
 const h=await harness('./proof/proof-explorer.mjs');
 assert.match(h.get('proof-freshness').textContent,/CURRENT.*2026-10-26T00:00:00Z.*90 min/);
 assert.match(h.get('proof-status').textContent,/FORELØBIG/);
 assert.ok([...h.timers.values()].some(t=>t.at===Date.parse('2026-10-26T01:30:00.001Z')));
 await h.advance('2026-10-26T01:30:00.001Z');
 assert.equal(h.get('proof-freshness').dataset.freshness,'stale');
 assert.match(h.get('proof-freshness').textContent,/^STALE/);
 h.language('en');assert.match(h.get('proof-status').textContent,/PROVISIONAL/);
 assert.match(h.get('proof-freshness').textContent,/STALE.*Freshness limit/);
 h.buttons.proofStep[2].click();assert.match(h.get('proof-focus').textContent,/75/);
 assert.equal(h.get('proof-freshness').dataset.freshness,'stale');
});
test('P2-C failed Proof source exposes unavailable freshness, no leftover score',async()=>{
 const h=await harness('./proof/proof-explorer.mjs',{fetcher:async()=>{throw Error('TEST_OFFLINE')}});
 h.language('en');assert.equal(h.get('proof-freshness').dataset.freshness,'unavailable');
 assert.equal(h.get('proof-status').textContent,'SOURCE MISSING');
 assert.equal(h.get('proof-windows').children.length,0);
});
test('Graph missing selected prices shows no borrowed quote and disables replay',async()=>{
 const latest=snapshot();latest.public_live_precision.hourly_price_path.BTC=[];
 const h=await harness('./graph-b/source-graph-b.mjs',{latest});
 assert.equal(h.get('observed-value').textContent,'—');
 assert.equal(h.get('hour-slider').disabled,true);
 assert.equal(h.get('actual').attrs.d,'');
});
test('Graph freshness expires in an already-open tab without another fetch',async()=>{
 const h=await harness('./graph-b/source-graph-b.mjs');
 assert.doesNotMatch(h.get('feed-status').textContent,/FORÆLDEDE/);
 assert.equal(h.get('variant-panel').dataset.freshness,'fresh');
 await h.advance('2026-10-26T01:30:01Z');
 assert.match(h.get('feed-status').textContent,/FORÆLDEDE/);
 assert.equal(h.get('variant-panel').dataset.freshness,'stale');
 h.buttons.lang[1].click();assert.match(h.get('feed-status').textContent,/STALE OBSERVATIONS/);
});
test('Proof expiry is armed even when optional external source links never respond',async()=>{
 const latest=snapshot();
 const h=await harness('./proof/proof-explorer.mjs',{fetcher:url=>
  String(url).endsWith('latest.json')?Promise.resolve({ok:true,json:async()=>latest}):new Promise(()=>{})});
 assert.equal(h.get('proof-freshness').dataset.freshness,'current');
 await h.advance('2026-10-26T01:30:00.001Z');
 assert.equal(h.get('proof-freshness').dataset.freshness,'stale');
});
test('Open tab rechecks all three public feeds and clears evidence on source failure',async()=>{
 for(const [path,assertCleared] of [
  ['./graph-b/source-graph-b.mjs',h=>{
   assert.equal(h.get('observed-value').textContent,'—');
   assert.equal(h.get('forecast').attrs.d,'');
  }],
  ['./compass/compass-path-ui.mjs',h=>{
   assert.equal(h.get('official-pilot-action').textContent,'—');
   assert.equal(h.get('official-pilot-bias').textContent,'—');
  }],
  ['./proof/proof-explorer.mjs',h=>{
   assert.equal(h.get('proof-status').textContent,'KILDE MANGLER');
   assert.equal(h.get('proof-windows').children.length,0);
  }]
 ]){
  const h=await harness(path);
  h.setFetch(async()=>{throw Error('SOURCE_OUTAGE')});
  await h.advance('2026-10-26T00:35:01Z');
  assertCleared(h);
 }
});
test('Open Graph B follows a newly published close while a manual replay stays put',async()=>{
 const initial=snapshot({last:167}),updated=snapshot({last:168});
 const h=await harness('./graph-b/source-graph-b.mjs',{latest:initial});
 h.setFetch(url=>Promise.resolve({ok:true,json:async()=>
  String(url).endsWith('latest.json')?updated:null}));
 await h.advance('2026-10-26T00:35:01Z');
 assert.equal(h.get('hour-slider').max,'168');
 assert.match(h.get('observed-value').textContent,/80[.,]168/);
 const replay=await harness('./graph-b/source-graph-b.mjs',{latest:updated});
 const slider=replay.get('hour-slider');slider.value='167';slider.listeners.input({currentTarget:slider});
 await replay.advance('2026-10-26T00:35:01Z');
 assert.equal(slider.value,'167');
 assert.match(replay.get('observed-value').textContent,/80[.,]167/);
});

test('Compass five horizons expose only source-issued direction, posture and native disclosures',async()=>{
 const h=await harness('./compass/compass-path-ui.mjs');
 const rows=h.get('official-pilot-horizons').children;
 assert.equal(rows.length,5);
 assert.equal(h.get('official-product-pilot').dataset.sourceState,'current');
 assert.equal(rows[1].children[0].textContent,'1–3D');
 assert.equal(rows[1].children[1].textContent,'OP');
 assert.equal(rows[1].children[2].textContent,'AFVENT');
 assert.equal(rows[1].children[3].children[0].textContent,'Læs kildegrundlag');
 assert.equal(rows[1].children[3].children[1].textContent,'Source-issued scenario only');
 h.language('en');
 const english=h.get('official-pilot-horizons').children;
 assert.equal(english[1].children[1].textContent,'UP');
 assert.equal(english[1].children[2].textContent,'WAIT');
 assert.equal(english[1].children[3].children[0].textContent,'Source detail');
});
test('Expired Compass removes current horizon and rotation postures without backfilling',async()=>{
 const h=await harness('./compass/compass-path-ui.mjs');
 // Let the 5-min refresh start, but NEVER resolve it. Only the original
 // deadline timer can expire the source-issued numbers and disclosures.
 h.setFetch(()=>new Promise(()=>{}));
 await h.advance('2026-10-26T02:00:01Z');
 assert.equal(h.get('official-product-pilot').dataset.sourceState,'expired');
 const first=h.get('official-pilot-horizons').children[0];
 assert.equal(first.children[1].textContent,'—');
 assert.equal(first.children[2].textContent,'UDLØBET');
 assert.equal(first.children.length,3);
 assert.equal(h.get('official-pilot-rotation').children[0].children[1].textContent,'—');
 h.language('en');
 assert.equal(h.get('official-pilot-horizons').children[0].children[2].textContent,'EXPIRED');
});

test('An unchanged background source refresh preserves an expanded official scenario and summary focus',async()=>{
 const h=await harness('./compass/compass-path-ui.mjs');
 const cards=h.get('official-pilot-horizons').children;
 const old=cards[1].children[3],summary=old.children[0];
 old.open=true;h.doc.activeElement=summary;
 await h.advance('2026-10-26T00:35:01Z'); // 5-min source refresh; same issued source
 const next=h.get('official-pilot-horizons').children[1].children[3];
 assert.notEqual(next,old);
 assert.equal(next.open,true);
 assert.equal(next.children[0].didFocus,true);
 h.doc.activeElement=next.children[0];
 h.language('en');
 const en=h.get('official-pilot-horizons').children[1].children[3];
 assert.equal(en.open,true);
 assert.equal(en.children[0].didFocus,true);
 assert.equal(en.children[0].textContent,'Source detail');
});
test('A live original deadline masks horizons despite an unresolved periodic refresh and catches a removed timer guard',async()=>{
 const source='./compass/compass-path-ui.mjs';
 const run=async sourceTransform=>{
  const h=await harness(source,{sourceTransform});
  h.setFetch(()=>new Promise(()=>{}));
  await h.advance('2026-10-26T02:00:01Z');
  return h;
 };
 const live=await run(null);
 assert.equal(live.get('official-pilot-action').textContent,'—');
 assert.equal(live.get('official-pilot-horizons').children[0].children[2].textContent,'UDLØBET');
 assert.equal(live.get('official-pilot-horizons').children[0].children.length,3);
 const mutated=await run(code=>{
  const sentinel='if(ms>0&&ms<2147483000)expiryTimer=setTimeout';
  assert.ok(code.includes(sentinel),'timer guard must be present for negative control');
  return code.replace(sentinel,'if(false)expiryTimer=setTimeout');
 });
 assert.notEqual(mutated.get('official-pilot-action').textContent,'—',
  'negative control must expose previously retained current action');
 assert.equal(mutated.get('official-pilot-horizons').children[0].children[3].tagName,'DETAILS',
  'negative control must retain stale source disclosure');
});
