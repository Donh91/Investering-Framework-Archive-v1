import test from 'node:test';
import assert from 'node:assert/strict';
import {cycleSourceReadback} from './cycle-source-readback.mjs';
const keys=['BTC','ETH','LARGE_CAPS','MID_CAPS','SMALL_CAPS','MICROCAPS','MEMES'];
const p={state:'SOURCE_BOUND',source_issue:32,source_week:'2026-W45',
 source_identity:'CMP-SOURCE-32',source_health:'DEGRADED',
 full_phases:['BTC','ETH','LARGE_MID','ALT_IGNITION','MICRO','BROAD',
  'MANIA','DISTRIBUTION','PROTECTION','REENTRY'].map(key=>({key})),
 current_checkpoint:null,next_checkpoint:null,
 rotation:keys.map((key,i)=>({key,action:i<2?'HOLD':i<5?'WAIT':i===5?'HARD_WAIT':'UNAVAILABLE'}))};
const view={weekly:{public_issue_number:32,forecast_week:'2026-W45'},
 compass:{state:'FRESH',permit_path_live_gates:true,compass_id:'CMP-SOURCE-32'},
 path:p};
const read=(v=view,lang='da')=>cycleSourceReadback({view:v,lang});
test('W45 degraded + no verifiable phase never promotes a current stage',()=>{
 const x=read();
 assert.equal(x.state,'PARTIAL_WEEKLY');
 assert.equal(x.referenceKind,'NO_VERIFIED_PHASE');
 assert.match(x.meaning,/Ingen aktiv markedsfase/);
 assert.match(x.reason,/delvis/);
 assert.match(x.weekLabel,/CN #32 · 2026-W45/);
 assert.match(x.nextMeaning,/ikke dokumenteret/);
 assert.deepEqual(x.rotation.map(z=>z.state),['hold','hold','wait','wait','wait','caution','missing']);
 assert.equal(x.rotation[6].sourceAction,'UNAVAILABLE');
});
test('HOLD is existing position only, not confirmed ETH phase',()=>{
 const x=read();
 assert.equal(x.rotation[1].action,'Behold eksisterende');
 assert.equal(x.referenceKind,'NO_VERIFIED_PHASE');
 assert.ok(!x.meaning.includes('ETH-lederskab bekræftet'));
});
test('a verified frozen weekly checkpoint is labeled only as reference',()=>{
 const v=structuredClone(view);v.path.source_health='OK';
 v.path.current_checkpoint={key:'BTC',status:'FROZEN_WEEK_REFERENCE'};
 v.path.next_checkpoint={key:'ETH',status:'UNCONFIRMED'};
 const x=read(v,'en');
 assert.equal(x.state,'SOURCE_ALIGNED');
 assert.equal(x.referenceKind,'FROZEN_WEEK_REFERENCE');
 assert.match(x.meaning,/not a confirmed current market phase/);
 assert.match(x.nextMeaning,/unconfirmed/);
});
test('wrong original issue/clock, incomplete phase or missing tier fail closed',()=>{
 for(const changed of [
  {path:{...p,source_issue:33}},
  {path:{...p,source_identity:'FAKE'}},
  {path:{...p,full_phases:p.full_phases.slice(0,4)}},
  {compass:{...view.compass,state:'EXPIRED'}}
 ]){
  const x=read({...view,...changed});
  assert.equal(x.state,'UNAVAILABLE');
  assert.deepEqual(x.rotation,[]);
 }
 const v={...view,path:{...p,rotation:p.rotation.slice(0,6)}};
 assert.deepEqual(read(v).rotation,[]);
});
test('unknown action cannot become a buy, phase or meme proxy',()=>{
 const v=structuredClone(view);
 v.path.rotation[6].action='BUY';
 const x=read(v);
 assert.equal(x.rotation[6].state,'missing');
 assert.equal(x.rotation[6].sourceAction,'BUY');
 assert.equal(x.referenceKind,'NO_VERIFIED_PHASE');
});

const independentlyObserved=()=>({delivery_health:'FRESH',
 compass:{compass_id:'CMP-LIVE',state:'UNAVAILABLE',permit_path_live_gates:false},
 live_observation:{compass_id:'CMP-LIVE',semantics:'OBSERVED_MOMENTUM_NOT_CYCLE_OR_FORECAST',
  authority:'PRESENTATION_ONLY',direction:'BEARISH',observation_open_utc:'2026-11-25T10:00:00Z'}});
test('actual orientation model remains live with unavailable weekly data, never promotes phase or flow',()=>{
 const v=independentlyObserved(),m=read(v);
 assert.equal(m.state,'LIVE_OBSERVATION_ONLY');
 assert.equal(m.referenceKind,'NONE');
 assert.deepEqual(m.rotation,[]);
 assert.match(m.weekLabel,/faldende/);
 assert.match(m.meaning,/ikke en bekræftet cyklusfase/);
 v.live_observation.direction='BULLISH';
 assert.match(read(v,'en').weekLabel,/rising/);
});
test('orientation model rejects stale, mismatched, malformed or action-bearing observations',()=>{
 for(const mutate of [v=>v.delivery_health='STALE',v=>v.live_observation.compass_id='other',
  v=>v.live_observation.authority='TRADE',v=>v.live_observation.direction='ROTATION',
  v=>v.live_observation.observation_open_utc='bad']){
  const v=independentlyObserved();mutate(v);assert.equal(read(v).state,'UNAVAILABLE');
 }
});
test('verified weekly reference and independent current observation remain distinct',()=>{
 const v=structuredClone(view);v.delivery_health='FRESH';
 v.live_observation={...independentlyObserved().live_observation,compass_id:v.compass.compass_id};
 const m=read(v);
 assert.equal(m.state,'PARTIAL_WEEKLY');
 assert.equal(m.referenceKind,'NO_VERIFIED_PHASE');
 assert.match(m.weekLabel,/faldende.*CN #32/);
 assert.match(m.meaning,/ikke en bekræftet cyklusfase/);
 assert.equal(m.rotation.length,7);
});
