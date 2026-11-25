import test from 'node:test';
import assert from 'node:assert/strict';
import {cycleMapModel,cycleMapMarkup,renderCycleMap} from './cycle-map.mjs';
import {inspectOfficialPublicFeeds} from '../vnext-live/official-feed-parity.mjs';
function fixture(phase='PRE_ROTATION'){
 const latest={generated_at:'2026-11-17T13:45:00Z',package:{issue_number:35,status:'OK',generated_unix:1794818153,market_cycle_context:{current_phase:phase,next_gate:'Source gate'},decision_projection:{weeks_4_8:{state:'BROAD_ALTSEASON'}}},public_series:{current_public_projection:{public_issue_number:34,forecast_week:'2026-W47'}}};
 const view={delivery_health:'FRESH',weekly:{state:'OK',public_issue_number:34,machine_issue_number:35,forecast_week:'2026-W47'},compass:{state:'FRESH',permit_path_live_gates:true,compass_id:'c'},path:{state:'SOURCE_BOUND',source_identity:'c',source_issue:34,source_week:'2026-W47',current_checkpoint:{key:'BTC',status:'FROZEN_WEEK_REFERENCE'}}};
 return {latest,view};
}
test('map only exact published enum; never borrows confidence or forward state',()=>{
 for(const p of ['PRE_ROTATION','ROTATION','BROAD_ALTSEASON','PARABOLIC_ALTSEASON','DISTRIBUTION']){const m=cycleMapModel(fixture(p));assert.equal(m.phase.code,p);assert.equal(m.confidence,'UNQUANTIFIED');assert.equal(m.evidence,'HYPOTHESIS');}
 for(const p of ['DEFENSIVE','EXIT_RISK','UNAVAILABLE','CONTRACTION','ACCUMULATION','__proto__'])assert.equal(cycleMapModel(fixture(p)).phase,null);
});
test('degraded package has gate only; no dot or false confidence',()=>{const x=fixture();x.latest.package.status=x.view.weekly.state='DEGRADED';const m=cycleMapModel(x);assert.equal(m.phase,null);assert.equal(m.rotation,null);assert.equal(m.gate,'Source gate');});
test('stale/mismatched/different week clears marker and source gate',()=>{for(const change of [x=>x.view.delivery_health='STALE',x=>x.view.weekly.forecast_week='2026-W46',x=>x.latest.package.generated_unix=9999999999]){const x=fixture();change(x);const m=cycleMapModel(x);assert.equal(m.phase,null);assert.equal(m.rotation,null);assert.equal(m.gate,null);}});
test('rotation marker needs explicit frozen BTC reference and fresh exact join; no HOLD or live inference',()=>{let x=fixture('UNAVAILABLE');assert.equal(cycleMapModel(x).rotation.kind,'FROZEN_WEEK_REFERENCE');for(const change of [x=>x.view.path.current_checkpoint={key:'ETH',status:'HOLD'},x=>x.view.compass.state='STALE',x=>x.view.path.source_identity='different',x=>x.view.path.current_checkpoint=null]){x=fixture();change(x);assert.equal(cycleMapModel(x).rotation,null);}});
test('initial markup contains no active dot, no trading wording and no external dependency',()=>{assert.match(cycleMapMarkup,/cn-map-phase-dot[^>]+hidden/);assert.match(cycleMapMarkup,/cn-map-rotation-dot[^>]+hidden/);assert.doesNotMatch(cycleMapMarkup,/https?:|buy now|sell now/i);});

function liveFixture(){
 const latest={schema:'CN_PUBLIC_SNAPSHOT_V2',generated_at:'2026-11-25T10:30:00Z',public_series:{contract:'CN_PUBLIC_SERIES_INDEX_v1'},package:{status:'DEGRADED'}};
 const compass={contract:'PUBLIC_COMPASS_PROJECTION_v1',data_status:'OK',compass_id:'CMP-LIVE',issued_at_utc:'2026-11-25T10:25:00Z',weekly_context:{status:'MISMATCH'},market_now:{directional_state:'BEARISH',eth_relative_state:'STRENGTHENING',market_observation_open_utc:'2026-11-25T09:00:00Z'},full_stack:{official_freshness:{contract:'OFFICIAL_COMPASS_SOURCE_FRESHNESS_READBACK_v1',status:'VERIFIED_OWNER_POLICY',semantics:'SOURCE_FRESHNESS_EXPIRY_NOT_FORECAST_ETA',source_asof_utc:'2026-11-25T09:00:00Z',valid_until_utc:'2026-11-25T12:00:00Z'}}};
 return {latest,compass};
}
const inspect=x=>inspectOfficialPublicFeeds(x.latest,x.compass,{nowUtc:'2026-11-25T11:00:00Z'});
test('native observed momentum reaches actual cycle map independently of weekly mismatch and changes on source mutation',()=>{
 const x=liveFixture(),v=inspect(x);assert.equal(v.weekly.state,'MISMATCH');assert.equal(v.compass.permit_path_live_gates,false);assert.equal(v.compass.action_now,'UNAVAILABLE');
 const model=cycleMapModel({view:v,latest:x.latest});assert.equal(model.observation.direction,'BEARISH');assert.equal(model.phase,null);assert.equal(model.rotation,null);
 const e={textContent:'',hidden:true};const doc={getElementById:id=>id==='cn-cycle-map'?{dataset:{}}:id==='cn-map-live-observation'?e:null};
 renderCycleMap(doc,{view:v,latest:x.latest,lang:'en'});assert.equal(e.hidden,false);assert.match(e.textContent,/Observed momentum: falling/);assert.match(e.textContent,/Not a cycle phase or forecast/);
 x.compass.market_now.directional_state='BULLISH';x.compass.market_now.eth_relative_state='WEAKENING';const changed=inspect(x);
 renderCycleMap(doc,{view:changed,latest:x.latest,lang:'en'});assert.match(e.textContent,/Observed momentum: rising/);assert.match(e.textContent,/ETH\/BTC weakening/);assert.equal(changed.compass.action_now,'UNAVAILABLE');
});
test('independent observation rejects expired owner, stale delivery, future observation, malformed enum and unauthenticated source',()=>{
 for(const mutate of [x=>x.compass.full_stack.official_freshness.valid_until_utc='2026-11-25T11:00:00Z',x=>x.latest.generated_at='2026-11-23T10:30:00Z',x=>x.compass.market_now.market_observation_open_utc='2026-11-25T10:26:00Z',x=>x.compass.market_now.directional_state='ROTATION',x=>x.compass.full_stack.official_freshness.status='UNVERIFIED',x=>x.compass.market_now.market_observation_open_utc='2026-11-23T09:00:00Z']){
  const x=liveFixture();mutate(x);const v=inspect(x);assert.equal(v.live_observation,null);assert.equal(cycleMapModel({view:v,latest:x.latest}).observation,null);
 }
});
