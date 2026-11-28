import assert from 'node:assert/strict';
import {forwardOutlook} from './forward-outlook.mjs';
import {sourceTrace} from './source-trace.mjs';
const latest={schema:'CN_PUBLIC_SNAPSHOT_V2',
 public_series:{current_public_projection:{forecast_week:'2026-W43',public_issue_number:30}}};
const compass={contract:'PUBLIC_COMPASS_PROJECTION_v1',
 weekly_context:{forecast_week:'2026-W43',public_issue_number:30},
 full_stack:{contract:'PUBLIC_COMPASS_FULL_STACK_READBACK_v1',
 source_status:{cycle_navigator:'WEEKLY_POINTER_ALIGNED',strategic:'BOUND_WEEKLY_ANCHOR'},
 weekly:{summary_2_3w:'A retest or recovery remains unresolved.'},
 strategic:{status:'BOUND_WEEKLY_ANCHOR',authority:'CYCLE_NAVIGATOR_OWNED_NOT_NEW_SITE_FORECAST',
 issued_at_utc:'2026-10-19T05:19:14Z',horizon_21_30d:{
  summary:'Mixed market outlook.',expected_path:'First assess BTC retest, then ETH relative leadership.',
  btc_direction:'MIXED',eth_direction:'MIXED',confidence:'LOW',
  scenarios:[{label:'BASE',thesis:'Recovery attempts and retests continue.'},{label:'BEAR',thesis:'The recovery fails.'}],
  falsifiers:['Strong ETH relative leadership would challenge the base case.']}}}};
const trace={contract:'CN_PREMIUM_SOURCE_TRACE_v1',status:'PARTIAL_OR_DEGRADED',
 long_horizons:[{id:'2_3w',direction:'MIXED',owner:'CYCLE_NAVIGATOR_WEEKLY'},
 {id:'21_30d',direction:'MIXED',owner:'CYCLE_NAVIGATOR_STRATEGIC_CONTEXT'}]};
const model=forwardOutlook(latest,compass,trace);
assert.equal(model.status,'FROZEN_CONTEXT_ONLY');
assert.equal(model.weekly.direction,'MIXED');
assert.equal(model.weekly.summary,'A retest or recovery remains unresolved.');
assert.equal(model.strategic.expected_path,'First assess BTC retest, then ETH relative leadership.');
assert.equal(model.strategic.scenarios.length,2);
assert.equal(model.strategic.falsifiers.length,1);
assert.equal(model.strategic.btc_direction,'MIXED');
assert.equal(model.price_path_status,'NOT_ISSUED');
assert.equal(forwardOutlook(latest,compass,{...trace,status:'UNVERIFIED'}).status,'UNAVAILABLE');
assert.equal(forwardOutlook(latest,{...compass,weekly_context:{forecast_week:'2026-W42',public_issue_number:29}},trace).status,'UNAVAILABLE');
assert.equal(forwardOutlook(latest,{...compass,full_stack:{...compass.full_stack,source_status:{cycle_navigator:'UNVERIFIED',strategic:'UNVERIFIED'}}},trace).strategic.available,false);
const future=structuredClone(compass);future.full_stack.strategic.issued_at_utc='2999-01-01T00:00:00Z';
assert.equal(forwardOutlook(latest,future,trace).strategic.available,false);
const privateLeak=structuredClone(compass);
privateLeak.full_stack.strategic.horizon_21_30d.expected_path='Target BTC $100,000 from secret provider';
privateLeak.full_stack.strategic.horizon_21_30d.scenarios.push({label:'BULL',thesis:'Target $180000'});
privateLeak.full_stack.strategic.horizon_21_30d.falsifiers.push('10% event');
const filtered=forwardOutlook(latest,privateLeak,trace);
assert.equal(filtered.strategic.expected_path,null);
assert.equal(filtered.strategic.scenarios.length,2);
assert.equal(filtered.strategic.falsifiers.length,1);
const forged=structuredClone(compass);forged.full_stack.strategic.authority='NEW_SITE_FORECAST_ENGINE';
assert.equal(forwardOutlook(latest,forged,trace).strategic.available,false);
console.log('PASS 13 forward outlook positive / negative source, no-price, no-private, false-provenance checks');

/* Exercise the real sourceTrace -> forwardOutlook join, not a hand-written
 * trace that already assumes the desired owner. Synthetic public fixtures. */
const joinedLatest={...latest,pointer:{iso_year:2026,iso_week:43}};
const joinedCompass=structuredClone(compass);
joinedCompass.full_stack.status='PARTIAL_OR_DEGRADED';
joinedCompass.full_stack.source_status.official='VERIFIED';
Object.assign(joinedCompass.full_stack.weekly,{iso_year:2026,iso_week:43,direction_2_3w:'MIXED'});
joinedCompass.full_stack.strategic.horizon_21_30d.direction='MIXED';
const parsed={delivery_health:'FRESH',weekly:{state:'OK',forecast_week:'2026-W43',public_issue_number:30},
 compass:{state:'FRESH',permit_path_live_gates:true}};
const evaluation=Date.parse('2026-10-19T09:00:00Z');
const joined=(c=joinedCompass,l=joinedLatest,p=parsed)=>{
 const t=sourceTrace(l,c,p);
 return {trace:t,model:forwardOutlook(l,c,t,{nowMs:evaluation})};
};
const positive=joined();
assert.equal(positive.trace.long_horizons[1].owner,'CYCLE_NAVIGATOR_STRATEGIC_CONTEXT');
assert.equal(positive.model.strategic.available,true);
assert.equal(positive.model.strategic.btc_direction,'MIXED');
assert.equal(positive.model.price_path_status,'NOT_ISSUED');
assert.equal(positive.trace.decision_authority,'OFFICIAL_COMPASS_ONLY');
const expiredDaily=joined(joinedCompass,joinedLatest,{...parsed,compass:{state:'EXPIRED',permit_path_live_gates:false}});
assert.equal(expiredDaily.trace.official_current,false);
assert.equal(expiredDaily.model.strategic.available,true);
for(const mutate of [
 c=>{c.full_stack.source_status.strategic='UNVERIFIED'},
 c=>{c.full_stack.source_status.cycle_navigator='UNVERIFIED'},
 c=>{c.full_stack.strategic.authority='OFFICIAL_ACTION'},
 c=>{c.full_stack.strategic.status='UNVERIFIED'},
 c=>{c.full_stack.weekly.iso_week=42},
 c=>{c.weekly_context.public_issue_number=29},
 c=>{c.full_stack.strategic.horizon_21_30d.direction='BUY'},
 c=>{c.full_stack.strategic.horizon_21_30d.direction='UNAVAILABLE'},
 c=>{c.full_stack.strategic.issued_at_utc='2026-10-20T09:00:00Z'}
]){
 const c=structuredClone(joinedCompass);mutate(c);
 assert.equal(joined(c).model.strategic.available,false);
}
assert.equal(joined(joinedCompass,joinedLatest,{...parsed,delivery_health:'STALE'}).model.strategic.available,false);
assert.equal(joined(joinedCompass,{...joinedLatest,pointer:{iso_year:2026,iso_week:42}}).model.strategic.available,false);
for(const d of ['UP','DOWN','SIDEWAYS','MIXED','NO_EDGE']){
 const c=structuredClone(joinedCompass);c.full_stack.strategic.horizon_21_30d.direction=d;
 assert.equal(joined(c).model.strategic.direction,d);
}
console.log('PASS 21 joined strategic source controls (synthetic, no forecast authority)');
