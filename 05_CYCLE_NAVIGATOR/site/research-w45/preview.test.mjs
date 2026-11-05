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
const baseOutcomes={
 contract:'RESEARCH_W45_PROSPECTIVE_OUTCOMES_v1',forecast_week:'2026-W45',
 created_at_utc:'2026-11-05T04:00:00Z',
 original_research_issued_at_utc:study.generated_at_utc,
 original_research_source_sha256:'a'.repeat(64),
 original_monday_daily_forecast_issued_counts:{BTC:0,ETH:0},
 source_mode:'PUBLIC_LIVE_W45',source_state:'UNAVAILABLE_FAIL_CLOSED',
 source_failure:'PUBLIC_LIVE_SOURCE_IDENTITY_UNVERIFIED',
 source_issue_number:null,observed_through_utc:null,observed_hours:0,
 matured_observations:0,total_forecast_observations:8,
 assets:{BTC:{matured_days:0,claim_of_edge:false},ETH:{matured_days:0,claim_of_edge:false}},
 rows:['BTC','ETH'].flatMap(asset=>study.forecast.assets[asset].forecast.map(p=>({
  asset,utc_date:p.utc_date,day:p.day,target_close_at_utc:p.target_close_at_utc,
  B0_original_expected_close_USDT:p.B0_persistence_expected_close,
  B1_original_expected_close_USDT:p.B1_decay_momentum_expected_close,
  observed_close_USDT:null,B0_absolute_percentage_error:null,
  B1_absolute_percentage_error:null,outcome_state:'PENDING_UTC_TARGET'
 }))),
 research_only:true,provider_first_known_verified:false,
 independent_scientific_edge_proven:false,official_scoring_eligible:false,
 portfolio_action_authority:false
};
function matureFirstOutcome(fixture,btcValue=79990.5,ethValue=2422){
 fixture.created_at_utc='2026-11-06T01:00:00Z';
 fixture.source_mode='PUBLIC_LIVE_W45';
 fixture.source_state='VERIFIED_PUBLIC_CAPTURE_NOT_INDEPENDENT_FIRST_KNOWN';
 fixture.observed_through_utc='2026-11-06T00:00:00Z';fixture.observed_hours=96;
 fixture.matured_observations=2;
 for(const i of [0,4]){
  const row=fixture.rows[i],v=i===0?btcValue:ethValue;
  row.outcome_state='MATURED_PUBLIC_CAPTURE';row.observed_close_USDT=v;
  row.B0_absolute_percentage_error=Number((Math.abs(row.B0_original_expected_close_USDT/v-1)*100).toFixed(5));
  row.B1_absolute_percentage_error=Number((Math.abs(row.B1_original_expected_close_USDT/v-1)*100).toFixed(5));
 }
 return fixture;
}

async function execute({history=clone(baseHistory),research=clone(study),
 outcomes=clone(baseOutcomes),now='2026-11-05T04:00:00Z',width=390,failFetch=false}={}){
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
  'matured-count','rehearsal-source','rehearsal-note','results','plot','hover','chart-note'];
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
  assert.ok(['../data/graph-history/timeline.json','../data/research-w45-shadow.json',
   '../data/research-w45-outcomes.json'].includes(url));
  return{ok:true,json:async()=>clone(url.includes('graph-history')?history:
    url.includes('outcomes')?outcomes:research)}
 };
 await vm.runInNewContext('(async()=>{'+source+'\n})()',{
   fetch,document,window,Date:FakeDate,console
 },{timeout:3500});
 return{elements,calls,requested,canvas,history,research,outcomes};
}

test('page runs source-bound actual hourly curve and exactly two separate shadow paths at mobile 390 and 430',async()=>{
 for(const width of [390,430]){
  const r=await execute({width});
  const text=id=>r.elements.get(id).textContent;
  assert.equal(text('actual-count'),'70 / 168');
  assert.match(text('hover'),/USDT/);
  assert.match(text('chart-note'),/Original blå mandagsprognose: 0\/7/);
  assert.equal(r.canvas.width,width*2);
  assert.equal(r.elements.get('results').children.length,8);
  assert.equal(r.elements.get('matured-count').textContent,'0 / 8');
  assert.equal(r.requested.length,3);
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

test('BTC and ETH first daily results require source receipt AFTER UTC close, later days pending',async()=>{
 const history=clone(baseHistory);
 history.actual.push({time:'2026-11-06T00:00:00Z',close:79990.5});
 const outcomes=matureFirstOutcome(clone(baseOutcomes));
 const r=await execute({history,outcomes,now:'2026-11-06T01:00:00Z'});
 const rows=r.elements.get('results').children;
 assert.equal(r.elements.get('matured-count').textContent,'2 / 8');
 assert.equal(rows[0].children[3].textContent,'79.990,50');
 assert.match(rows[0].children[4].textContent,/ %$/);
 assert.match(rows[0].children[5].textContent,/ %$/);
 assert.equal(rows[4].children[3].textContent,'2.422,00');
 assert.equal(rows[1].children[3].textContent,'Afventer UTC-luk');
 assert.equal(rows[5].children[3].textContent,'Afventer UTC-luk');
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


test('outcome claim cannot promote research to original Monday issuance, even with plausible prices',async()=>{
 const changes=[
  x=>{x.official_scoring_eligible=true},
  x=>{x.portfolio_action_authority=true},
  x=>{x.original_monday_daily_forecast_issued_counts.BTC=7},
  x=>{x.original_research_issued_at_utc='2026-11-02T08:19:08Z'},
  x=>{x.rows[4].B1_original_expected_close_USDT+=1},
  x=>{x.original_research_source_sha256='invalid'}
 ];
 for(const change of changes){const outcomes=clone(baseOutcomes);change(outcomes);
  const r=await execute({outcomes});
  assert.match(r.elements.get('hover').textContent,/Kilden kan ikke valideres/);
  assert.equal(r.calls.length,0);
 }
});

test('reported mature results before UTC target, after future capture, or math tampering are rejected',async()=>{
 for(const action of [
  x=>{x.rows[0].B1_absolute_percentage_error+=2},
  x=>{x.created_at_utc='2026-11-05T09:00:00Z'},
  x=>{x.observed_through_utc='2026-11-05T08:00:00Z'},
  x=>{x.matured_observations=8},
  x=>{x.rows[4].observed_close_USDT=9999},
 ]){
  const history=clone(baseHistory);history.actual.push({time:'2026-11-06T00:00:00Z',close:79990.5});
  const outcomes=matureFirstOutcome(clone(baseOutcomes));action(outcomes);
  const r=await execute({history,outcomes,now:'2026-11-06T01:00:00Z'});
  assert.match(r.elements.get('hover').textContent,/Kilden kan ikke valideres/);
  assert.equal(r.calls.length,0);
 }
});

test('claimed BTC outcome must agree exactly with independently displayed Graph History close',async()=>{
 const history=clone(baseHistory);history.actual.push({time:'2026-11-06T00:00:00Z',close:79990.51});
 const outcomes=matureFirstOutcome(clone(baseOutcomes));
 const r=await execute({history,outcomes,now:'2026-11-06T01:00:00Z'});
 assert.match(r.elements.get('hover').textContent,/Kilden kan ikke valideres/);
 assert.equal(r.calls.length,0);
});

test('source unavailable after UTC target means awaiting source, not an invented outcome',async()=>{
 const outcomes=clone(baseOutcomes);
 outcomes.created_at_utc='2026-11-06T01:00:00Z';
 outcomes.rows[0].outcome_state='AWAITING_VERIFIED_SOURCE';
 outcomes.rows[4].outcome_state='AWAITING_VERIFIED_SOURCE';
 const r=await execute({outcomes,now:'2026-11-06T01:00:00Z'});
 assert.equal(r.elements.get('matured-count').textContent,'0 / 8');
 assert.equal(r.elements.get('results').children[0].children[3].textContent,'Kilde afventes');
 assert.equal(r.elements.get('results').children[4].children[3].textContent,'Kilde afventes');
});
