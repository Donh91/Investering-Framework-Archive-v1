import test from 'node:test';
import assert from 'node:assert/strict';
import {KOMPAS_HORIZONS,kompasHorizonStatusRows} from './kompas-horizon-status.mjs';

const compass={
  contract:'PUBLIC_COMPASS_PROJECTION_v1',data_status:'OK',compass_id:'CMP-TEST-1',
  market_now:{directional_state:'BULLISH'},
  horizons:{
    NEXT_1_3D:{expected_direction:'UP'},
    NEXT_5_7D:{expected_direction:'MIXED'},
    NEXT_2_3W:{expected_direction:'DOWN'}
  }
};
const view={compass:{state:'FRESH',permit_path_live_gates:true,compass_id:'CMP-TEST-1'}};
const by=(rows,id)=>rows.find(row=>row.id===id);
const strategicTrace={
 contract:'CN_PREMIUM_SOURCE_TRACE_v1',status:'PARTIAL_OR_DEGRADED',
 sources:[{id:'official',status:'UNAVAILABLE'},{id:'strategic',status:'BOUND_WEEKLY_ANCHOR'}],
 long_horizons:[{id:'21_30d',owner:'CYCLE_NAVIGATOR_STRATEGIC_CONTEXT',direction:'DOWN'}]
};
const sourceBoundStrategy={contract:'CN_PUBLIC_FORWARD_OUTLOOK_v1',
 status:'FROZEN_CONTEXT_ONLY',strategic:{available:true,btc_direction:'DOWN'}};

test('all 14 exact source-contract horizons are represented once, in canonical order',()=>{
  const ids=KOMPAS_HORIZONS.map(x=>x[0]);
  assert.equal(ids.length,14);
  assert.equal(new Set(ids).size,14);
  assert.deepEqual(ids,['NOW','H0_12H','H24H','H1_3D','H5_7D','H8_14D','H15_21D','H2_3W','H21_30D','H4_8W','H1_3M','H3_6M','H6_9M','H9_12M']);
  const actual=kompasHorizonStatusRows({compass,view,observationCurrent:true});
  assert.deepEqual(actual.rows.map(r=>r.id),ids);
  assert.equal(actual.contract,'CN_KOMPAS_PRO_14_HORIZON_PRESENTATION_v1');
});

test('official verified horizons show source directions, not numeric price targets',()=>{
  const {rows,officialSourceCurrent}=kompasHorizonStatusRows({compass,view,observationCurrent:true});
  assert.equal(officialSourceCurrent,true);
  assert.deepEqual(['H1_3D','H5_7D','H2_3W'].map(k=>by(rows,k).tone),['up','mixed','down']);
  for(const id of ['H1_3D','H5_7D','H2_3W']){
    assert.equal(by(rows,id).status,'OFFICIAL_DIRECTION_ONLY');
    assert.match(by(rows,id).priceLabel,/ikke kursmål/);
  }
  assert.equal(by(rows,'H24H').status,'PENDING');
  assert.equal(by(rows,'H21_30D').status,'NONBINDING_CONTEXT');
  for(const x of rows)assert.equal(x.sourceStatus==='OFFICIAL_SOURCE_DIRECTION_ONLY'||x.sourceStatus==='NOT_ISSUED_IN_THIS_VIEW',true);
});

test('now and 0-12h remain observed momentum and never a future forecast',()=>{
  const fresh=kompasHorizonStatusRows({compass,view,observationCurrent:true}).rows;
  assert.equal(by(fresh,'NOW').status,'CURRENT_OBSERVATION');
  assert.equal(by(fresh,'H0_12H').status,'CURRENT_OBSERVATION');
  assert.match(by(fresh,'H0_12H').sourceLabel,/ikke prognose/);
  const stale=kompasHorizonStatusRows({compass,view,observationCurrent:false}).rows;
  assert.equal(by(stale,'NOW').status,'OBSERVATION_UNAVAILABLE');
  assert.equal(by(stale,'H0_12H').tone,'missing');
});

test('expired, wrong ID, fake contract and invalid official direction all fail closed',()=>{
  for(const v of [
    {...view,compass:{...view.compass,state:'EXPIRED'}},
    {...view,compass:{...view.compass,compass_id:'CMP-SPOOF'}},
    {...view,compass:{...view.compass,permit_path_live_gates:false}}
  ]){
    const x=kompasHorizonStatusRows({compass,view:v});
    assert.equal(x.officialSourceCurrent,false);
    for(const id of ['NOW','H0_12H','H1_3D','H5_7D','H2_3W','H21_30D']){
      assert.equal(by(x.rows,id).status,'SOURCE_UNAVAILABLE');
      assert.equal(by(x.rows,id).tone,'missing');
    }
    // Nonissued research type is a timeless truth, not stale market data.
    assert.equal(by(x.rows,'H24H').status,'PENDING');
    assert.equal(by(x.rows,'H8_14D').status,'RESEARCH_ONLY');
    assert.equal(by(x.rows,'H9_12M').status,'SCENARIO_ONLY');
  }
  const fake=kompasHorizonStatusRows({compass:{...compass,contract:'FAKE'},view});
  assert.equal(fake.officialSourceCurrent,false);
  const corrupt={...compass,horizons:{...compass.horizons,NEXT_5_7D:{expected_direction:'BUY'}}};
  assert.equal(by(kompasHorizonStatusRows({compass:corrupt,view}).rows,'H5_7D').status,'SOURCE_UNAVAILABLE');
});

test('English labels remain explicit about research/price/authority boundaries',()=>{
  const rows=kompasHorizonStatusRows({compass,view,lang:'en',observationCurrent:true}).rows;
  assert.equal(by(rows,'H1_3D').value,'Rising');
  assert.equal(by(rows,'H8_14D').value,'Research, not issued');
  assert.equal(by(rows,'H21_30D').value,'Strategic context pending');
  assert.equal(by(rows,'H9_12M').value,'Scenario not issued');
  assert.equal(by(rows,'H24H').value,'Not issued');
  assert.ok(rows.every(r=>!('low' in r)&&!('high' in r)&&!('expected_close' in r)));
});

test('verified 21-30d BTC strategic direction is nonbinding and not a price target',()=>{
 const {rows}=kompasHorizonStatusRows({compass,view,
  strategic:sourceBoundStrategy,trace:strategicTrace});
 const r=by(rows,'H21_30D');
 assert.equal(r.status,'VERIFIED_STRATEGIC_CONTEXT_ONLY');
 assert.equal(r.sourceStatus,'STRATEGIC_SOURCE_NONBINDING');
 assert.equal(r.tone,'down');
 assert.equal(r.value,'Faldende');
 assert.match(r.sourceLabel,/ikke-bindende/);
 assert.match(r.priceLabel,/ikke kursmål/);
 assert.equal(by(rows,'H1_3M').status,'SCENARIO_ONLY');
});

test('unverified strategic evidence is never treated as an issued official forecast',()=>{
 for(const strategic of [
  {contract:'FAKE',status:'FROZEN_CONTEXT_ONLY',strategic:{available:true,btc_direction:'UP'}},
  {contract:'CN_PUBLIC_FORWARD_OUTLOOK_v1',status:'UNAVAILABLE',strategic:{available:true,btc_direction:'UP'}},
  {contract:'CN_PUBLIC_FORWARD_OUTLOOK_v1',status:'FROZEN_CONTEXT_ONLY',strategic:{available:true,btc_direction:'BUY'}},
  {contract:'CN_PUBLIC_FORWARD_OUTLOOK_v1',status:'FROZEN_CONTEXT_ONLY',strategic:{available:false,btc_direction:'UP'}}
 ]){
  const {rows}=kompasHorizonStatusRows({compass,view,strategic});
  assert.equal(by(rows,'H21_30D').status,'NONBINDING_CONTEXT');
 }
 const strategic={contract:'CN_PUBLIC_FORWARD_OUTLOOK_v1',status:'FROZEN_CONTEXT_ONLY',
  strategic:{available:true,btc_direction:'DOWN'}};
 const expired={...view,compass:{...view.compass,state:'EXPIRED'}};
 assert.equal(by(kompasHorizonStatusRows({compass,view:expired,strategic}).rows,'H21_30D').status,'SOURCE_UNAVAILABLE');
});


test('frozen verified strategic context survives official expiry without upgrading daily forecast',()=>{
 const expired={...view,compass:{...view.compass,state:'EXPIRED'}};
 const result=kompasHorizonStatusRows({compass,view:expired,strategic:sourceBoundStrategy,
  trace:strategicTrace,lang:'da'});
 assert.equal(result.officialSourceCurrent,false);
 assert.equal(by(result.rows,'H1_3D').status,'SOURCE_UNAVAILABLE');
 assert.equal(by(result.rows,'NOW').status,'SOURCE_UNAVAILABLE');
 const long=by(result.rows,'H21_30D');
 assert.equal(long.status,'VERIFIED_STRATEGIC_CONTEXT_ONLY');
 assert.equal(long.sourceStatus,'STRATEGIC_SOURCE_NONBINDING');
 assert.equal(long.value,'Faldende');
 assert.match(long.sourceLabel,/Tidligere udstedt.*ikke-bindende/);
 assert.match(long.priceLabel,/ikke kursmål/);
 assert.equal(by(result.rows,'H8_14D').value,'Research, ikke udstedt');
 assert.equal(by(result.rows,'H1_3M').value,'Scenarie ikke udstedt');
});

test('spoofed/stale/missing trace cannot resurrect strategic context after official expiry',()=>{
 const expired={...view,compass:{...view.compass,state:'EXPIRED'}};
 const falsifiers=[
  null,
  {...strategicTrace,contract:'UNTRUSTED'},
  {...strategicTrace,status:'UNVERIFIED'},
  {...strategicTrace,sources:[{id:'strategic',status:'UNAVAILABLE'}]},
  {...strategicTrace,long_horizons:[{id:'21_30d',owner:'UNTRUSTED',direction:'DOWN'}]},
  {...strategicTrace,long_horizons:[{id:'21_30d',owner:'CYCLE_NAVIGATOR_STRATEGIC_CONTEXT',direction:'UNAVAILABLE'}]}
 ];
 for(const trace of falsifiers){
  const x=kompasHorizonStatusRows({compass,view:expired,strategic:sourceBoundStrategy,trace});
  assert.equal(by(x.rows,'H21_30D').status,'SOURCE_UNAVAILABLE');
  assert.equal(by(x.rows,'H1_3D').status,'SOURCE_UNAVAILABLE');
  assert.equal(by(x.rows,'H9_12M').status,'SCENARIO_ONLY');
 }
 const fake={...sourceBoundStrategy,contract:'UNTRUSTED'};
 assert.equal(by(kompasHorizonStatusRows({compass,view:expired,strategic:fake,
  trace:strategicTrace}).rows,'H21_30D').status,'SOURCE_UNAVAILABLE');
});
