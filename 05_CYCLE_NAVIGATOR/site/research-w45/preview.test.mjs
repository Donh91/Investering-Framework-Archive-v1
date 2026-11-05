// Source-bound optional W45 research page execution regression, no network,
// no Chrome dependency, no producer write, no synthetic official forecasts.
// Evaluates the page's *actual* inline module JS with a DOM and Canvas spy.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {resolve} from 'node:path';
import vm from 'node:vm';
import test from 'node:test';

const root=fileURLToPath(new URL('../../../',import.meta.url));
const page=readFileSync(resolve(root,'05_CYCLE_NAVIGATOR/site/research-w45/index.html'),'utf8');
const match=page.match(/<script type="module">([\s\S]*?)<\/script>/);
assert.ok(match,'W45_PAGE_INLINE_MODULE_MISSING');
const source=match[1];
const study=JSON.parse(readFileSync(resolve(root,
 '06_RESEARCH_LAB/mission_packets/2026-11-05__W45_MIDWEEK_PROSPECTIVE_BENCHMARK_v1.json'),'utf8'));
assert.equal(study.contract,'RESEARCH_W45_MIDWEEK_FORWARD_BENCHMARK_v1');
const baseHistory={
 contract:'CN_GRAPH_HISTORY_TIMELINE_v1',
 actual_unit:'USDT',
 forecast_unit:'PER_WEEK_DECLARED_OR_UNAVAILABLE',
 comparison_precision_eligible:false,
 weeks:[{week:'2026-W45',forecast_status:'UNAVAILABLE',forecast:[]}],
 actual:study.observations.slice(-70).map(row=>({time:row.candle_close_at_utc,close:row.BTC_USDT}))
};
const clone=x=>JSON.parse(JSON.stringify(x));

async function execute({history=clone(baseHistory),research=clone(study),now='2026-11-05T04:00:00Z',width=390,failFetch=false}={}){
 const elements=new Map(),calls=[];
 class FakeElement{
  constructor(tag='div'){this.tag=tag;this.textContent='';this.className='';this.children=[];this.style={};}
  replaceChildren(){this.children=[]}
  append(...xs){this.children.push(...xs)}
  getBoundingClientRect(){return {width,height:360}}
 }
 const ctx={
  setTransform(){},clearRect(){},fillRect(){},beginPath(){this.moves=0},
  moveTo(){this.moves=(this.moves||0)+1},lineTo(){},arc(){},fill(){},
  stroke(){calls.push({kind:'stroke',color:this.strokeStyle,moves:this.moves,dash:[...(this.dash||[])]})},
  setLineDash(p){this.dash=p},
  fillText(){},
  font:'',fillStyle:'',lineWidth:0,strokeStyle:'',textAlign:''
 };
 const ids=['last-value','last-time','actual-count','source-status','freshness',
  'results','plot','hover','chart-note'];
 for(const id of ids)elements.set(id,new FakeElement(id));
 const canvas=elements.get('plot');canvas.getContext=kind=>kind==='2d'?ctx:null;canvas.width=0;canvas.height=0;
 class FakeDate extends Date{static now(){return Date.parse(now)}}
 const document={
  getElementById:id=>{assert.ok(elements.has(id),'UNEXPECTED_PAGE_ELEMENT_'+id);return elements.get(id)},
  createElement:tag=>new FakeElement(tag)
 };
 const window={devicePixelRatio:2,addEventListener:(ev,fn)=>{assert.equal(ev,'resize');assert.equal(typeof fn,'function')}};
 const requested=[];
 const fetch=async url=>{
  requested.push(url);
  if(failFetch)throw Error('NETWORK_UNAVAILABLE');
  assert.ok(['../data/graph-history/timeline.json','../data/research-w45-shadow.json'].includes(url));
  return{ok:true,json:async()=>clone(url.includes('graph-history')?history:research)}
 };
 await vm.runInNewContext('(async()=>{'+source+'\n})()',{
   fetch,document,window,Date:FakeDate,console
 },{timeout:3500});
 return{elements,calls,requested,canvas,history,research};
}

test('page runs source-bound actual hourly curve and exactly two separate shadow paths at mobile 390 and 430',async()=>{
 for(const width of [390,430]){
  const r=await execute({width});
  const text=id=>r.elements.get(id).textContent;
  assert.equal(text('actual-count'),'70 / 168');
  assert.match(text('hover'),/USDT/);
  assert.match(text('chart-note'),/Original blå mandagsprognose: 0\/7/);
  assert.equal(r.canvas.width,width*2);
  assert.equal(r.elements.get('results').children.length,4);
  assert.equal(r.requested.length,2);
  assert.ok(r.calls.some(x=>x.color==='#38d2a8'),'REAL_GREEN_MISSING');
  assert.ok(r.calls.some(x=>x.color==='#efb864'&&x.dash.length),'SHADOW_B1_MISSING');
  assert.ok(r.calls.some(x=>x.color==='#9cabc2'&&x.dash.length),'SHADOW_B0_MISSING');
  assert.ok(!r.calls.some(x=>x.color==='#79aaff'||x.color==='#5f96ff'),'FAKE_ORIGINAL_BLUE_RENDERED');
  assert.match(r.elements.get('results').children[0].children.at(-1).textContent,/—/);
 }
});

test('genuine hourly source gaps break the observed stroke, do not bridge missing hours',async()=>{
 const history=clone(baseHistory);
 history.actual.splice(20,1);
 const r=await execute({history,width:390});
 const green=r.calls.find(x=>x.color==='#38d2a8');
 assert.ok(green&&green.moves>=2,'MISSING_CANDLE_INTERPOLATED_INSTEAD_OF_BREAK');
 assert.equal(r.elements.get('actual-count').textContent,'69 / 168');
});

test('prospective daily research scoring remains empty until the actual UTC close',async()=>{
 const history=clone(baseHistory);
 history.actual.push({time:'2026-11-06T00:00:00Z',close:79990.5});
 let r=await execute({history,now:'2026-11-06T01:00:00Z'});
 let first=r.elements.get('results').children[0].children;
 assert.equal(first[3].textContent,'79.990,50');
 assert.match(first[4].textContent,/ %$/);
 assert.equal(r.elements.get('results').children[1].children[3].textContent,'Afventer');
});

test('missing or retroactively changed Monday CN original is quarantined, never fabricated',async()=>{
 for(const mutation of [
  h=>{h.weeks[0].forecast_status='PUBLISHED'},
  h=>{h.weeks[0].forecast=[{day:1,expected_close:85000}]},
  h=>{h.actual_unit='USD'}
 ]){
  const history=clone(baseHistory);mutation(history);
  const r=await execute({history});
  assert.match(r.elements.get('hover').textContent,/Kilden kan ikke valideres/);
  assert.ok(!r.calls.some(x=>x.color==='#efb864'));
 }
});

test('shadow source authority tamper and future-known values fail closed',async()=>{
 for(const change of [
  d=>{d.forecast.site_blue_original_forecast_eligible=true},
  d=>{d.forecast.official_scoring_eligible=true},
  d=>{d.forecast.portfolio_action_authority=true},
  d=>{d.original_W45_daily_price_path_status.BTC='PUBLISHED'},
  d=>{d.forecast.assets.BTC.forecast[0].target_close_at_utc='2026-11-05T00:00:00Z'}
 ]){
  const research=clone(study);change(research);
  const r=await execute({research});
  assert.match(r.elements.get('hover').textContent,/Kilden kan ikke valideres/);
 }
 const history=clone(baseHistory);
 history.actual.push({time:'2026-11-06T00:00:00Z',close:91000});
 const r=await execute({history,now:'2026-11-05T04:00:00Z'});
 assert.match(r.elements.get('hover').textContent,/Kilden kan ikke valideres/);
});

test('missing research fetch does not show a misleading modeled chart or fallback blue curve',async()=>{
 const r=await execute({failFetch:true});
 assert.equal(r.calls.length,0);
 assert.match(r.elements.get('hover').textContent,/Kilden kan ikke valideres/);
 assert.match(r.elements.get('chart-note').textContent,/KILDE_HENTNING_FEJLET|NETWORK_UNAVAILABLE/);
});
