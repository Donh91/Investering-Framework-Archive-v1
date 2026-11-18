import test from 'node:test';
import assert from 'node:assert/strict';
import {cycleMapModel,cycleMapMarkup} from './cycle-map.mjs';
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
