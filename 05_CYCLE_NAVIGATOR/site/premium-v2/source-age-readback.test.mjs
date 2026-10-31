import test from 'node:test';
import assert from 'node:assert/strict';
import {originalSourceAgeAtIssue,originalSourceAgeLabel} from '../source-age-readback.mjs';

const issue='2026-10-13T14:14:43Z';
const compass='CMP-EXACT-ORIGINAL';
const projection={contract:'PUBLIC_COMPASS_PROJECTION_v1',compass_id:compass,issued_at_utc:issue};
const originalTimestamp=age=>Number.isSafeInteger(age)&&age>=0?
  new Date(Date.parse(issue)-age*1000).toISOString().replace('.000Z','Z'):issue;
const internal=(age=8083,packetAge=6945)=>({
 contract:'OFFICIAL_DAILY_COMPASS_v1',compass_id:compass,issued_at_utc:issue,
 source_bindings:{auto_market_state:{freshness:{evaluated_at_utc:issue,checks:[
  {lane:'source_observation_freshness',age_seconds:age,status:'PASS',timestamp:originalTimestamp(age)},
  {lane:'auto_market_state_packet',age_seconds:packetAge,status:'PASS',timestamp:originalTimestamp(packetAge)}
 ]}}}
});

test('original independent observation/packet ages retained without deriving status or direction',()=>{
 const m=originalSourceAgeAtIssue(internal(),projection);
 assert.equal(m.status,'ORIGINAL_ISSUANCE_CLOCKS_ONLY');
 assert.equal(m.compass_id,compass);
 assert.equal(m.observation_age_seconds_at_issue,8083);
 assert.equal(m.packet_age_seconds_at_issue,6945);
 assert.equal(m.provider_first_published_at_utc,null);
 assert.equal(m.first_investor_delivery_at_utc,null);
 assert.equal(m.authority,'PRESENTATION_ONLY_NO_GATE_OR_SIGNAL');
 const publicComp={...projection,original_source_age_at_issue:m};
 assert.match(originalSourceAgeLabel(publicComp,{lang:'da',valid:true}),/markedsdata 135 min, kildepakke 116 min/);
 assert.match(originalSourceAgeLabel(publicComp,{lang:'en',valid:true}),/market data 135 min, source packet 116 min/);
});

test('missing original receipt never manufactures zero-age current freshness',()=>{
 const unknown=originalSourceAgeAtIssue({ ...internal(),source_bindings:{}},projection);
 assert.equal(unknown.status,'UNKNOWN');
 const pub={...projection,original_source_age_at_issue:unknown};
 assert.match(originalSourceAgeLabel(pub,{valid:true}),/ukendt/);
 assert.equal(originalSourceAgeLabel(pub,{valid:false}),'');
});

test('independent internal/public forecast id or issued clock mismatch fails closed',()=>{
 assert.equal(originalSourceAgeAtIssue({...internal(),compass_id:'WRONG'},projection).status,'UNKNOWN');
 assert.equal(originalSourceAgeAtIssue({...internal(),issued_at_utc:'2026-10-13T14:14:44Z'},projection).status,'UNKNOWN');
 assert.equal(originalSourceAgeAtIssue({...internal(),issued_at_utc:'not-a-time'},projection).status,'UNKNOWN');
 assert.equal(originalSourceAgeAtIssue({...internal(),contract:'INTERNAL_V2_UNKNOWN'},projection).status,'UNKNOWN');
 for(const future of ['OFFICIAL_DAILY_COMPASS_v2','OFFICIAL_DAILY_COMPASS_v3','OFFICIAL_DAILY_COMPASS_v99']){
  assert.equal(originalSourceAgeAtIssue({...internal(),contract:future},projection).status,'UNKNOWN');
 }
});

test('duplicated, missing, null, negative and non-integer source clocks rejected',()=>{
 for(const invalid of [null,-1,1.5,'1800',NaN]) {
  assert.equal(originalSourceAgeAtIssue(internal(invalid),projection).status,'UNKNOWN');
 }
 const d=internal();
 d.source_bindings.auto_market_state.freshness.checks.push({
  lane:'auto_market_state_packet',age_seconds:90,status:'PASS'
 });
 assert.equal(originalSourceAgeAtIssue(d,projection).status,'UNKNOWN');
 const d2=internal();
 d2.source_bindings.auto_market_state.freshness.checks.splice(0,1);
 assert.equal(originalSourceAgeAtIssue(d2,projection).status,'UNKNOWN');
 assert.equal(originalSourceAgeAtIssue(internal(30,90),projection).status,'UNKNOWN');
 for(const malformedChecks of [{},'not-array',null,17]){
  const bad=internal();
  bad.source_bindings.auto_market_state.freshness.checks=malformedChecks;
  assert.equal(originalSourceAgeAtIssue(bad,projection).status,'UNKNOWN');
 }
 assert.equal(originalSourceAgeAtIssue({...internal(),compass_id:null},projection).status,'UNKNOWN');
 assert.equal(originalSourceAgeAtIssue({...internal(),compass_id:''},projection).status,'UNKNOWN');
});

test('a forged copied age object cannot be shown for another official issue',()=>{
 const m=originalSourceAgeAtIssue(internal(),projection);
 const p={...projection,issued_at_utc:'2026-10-14T14:14:43Z',original_source_age_at_issue:m};
 assert.match(originalSourceAgeLabel(p,{valid:true}),/ukendt/);
 const sameClockDifferentId={...projection,compass_id:'CMP-CORRECTED-SAME-SECOND',original_source_age_at_issue:m};
 assert.match(originalSourceAgeLabel(sameClockDifferentId,{valid:true}),/ukendt/);
 assert.match(originalSourceAgeLabel(sameClockDifferentId,{lang:'en',valid:true}),/unknown/);
 const forgedContradictory={...projection,original_source_age_at_issue:{...m,observation_age_seconds_at_issue:1,packet_age_seconds_at_issue:100}};
 assert.match(originalSourceAgeLabel(forgedContradictory,{valid:true}),/ukendt/);
});

test('the presentation only code never implies market action or recalibrates source policy',()=>{
 const m=originalSourceAgeAtIssue(internal(1801,1),projection);
 const txt=originalSourceAgeLabel({...projection,original_source_age_at_issue:m},{valid:true});
 assert.match(txt,/31 min/);
 assert.doesNotMatch(txt,/SELL|BUY|P=|4\/5/);
});

test('adversarial contradictory timestamp/age or evaluation clock fails closed',()=>{
 assert.equal(originalSourceAgeAtIssue(internal(),projection).status,'ORIGINAL_ISSUANCE_CLOCKS_ONLY');
 const badObservation=internal();
 badObservation.source_bindings.auto_market_state.freshness.checks[0].timestamp=issue;
 assert.equal(originalSourceAgeAtIssue(badObservation,projection).status,'UNKNOWN');
 const badPacket=internal();
 badPacket.source_bindings.auto_market_state.freshness.checks[1].timestamp=issue;
 assert.equal(originalSourceAgeAtIssue(badPacket,projection).status,'UNKNOWN');
 const wrongEvaluation=internal();
 wrongEvaluation.source_bindings.auto_market_state.freshness.evaluated_at_utc='2026-10-13T14:14:42Z';
 assert.equal(originalSourceAgeAtIssue(wrongEvaluation,projection).status,'UNKNOWN');
 const noEvaluation=internal();
 delete noEvaluation.source_bindings.auto_market_state.freshness.evaluated_at_utc;
 assert.equal(originalSourceAgeAtIssue(noEvaluation,projection).status,'UNKNOWN');
 const missingObservationTimestamp=internal();
 delete missingObservationTimestamp.source_bindings.auto_market_state.freshness.checks[0].timestamp;
 assert.equal(originalSourceAgeAtIssue(missingObservationTimestamp,projection).status,'UNKNOWN');
 const futurePacket=internal();
 futurePacket.source_bindings.auto_market_state.freshness.checks[1].timestamp='2026-10-13T14:15:43Z';
 assert.equal(originalSourceAgeAtIssue(futurePacket,projection).status,'UNKNOWN');
});
