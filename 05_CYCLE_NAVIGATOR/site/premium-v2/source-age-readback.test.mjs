import test from 'node:test';
import assert from 'node:assert/strict';
import {originalSourceAgeAtIssue,originalSourceAgeLabel} from '../source-age-readback.mjs';
import {inheritedProtectionOrigin,kompasTruthBanner,kompasTruthReadback} from '../kompas-truth-banner.mjs';

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

test('issuer clock statuses must both be PASS before presenting numeric source ages',()=>{
 for(const laneIndex of [0,1]){
  for(const bad of ['WARN','FAIL','UNKNOWN','',null,undefined]){
   const d=internal();
   const lane=d.source_bindings.auto_market_state.freshness.checks[laneIndex];
   if(bad===undefined)delete lane.status; else lane.status=bad;
   const readback=originalSourceAgeAtIssue(d,projection);
   assert.equal(readback.status,'UNKNOWN','non-PASS clock cannot be a numeric age');
   const shown=originalSourceAgeLabel({...projection,original_source_age_at_issue:readback},
     {lang:'en',valid:true});
   assert.match(shown,/unknown/);
   assert.doesNotMatch(shown,/market data [0-9]/);
  }
 }
 assert.equal(originalSourceAgeAtIssue(internal(),projection).status,
   'ORIGINAL_ISSUANCE_CLOCKS_ONLY');
});

test('copied public metadata cannot hide a non-PASS clock under valid source flag',()=>{
 const valid=originalSourceAgeAtIssue(internal(),projection);
 for(const lane of ['observation_clock_status','packet_clock_status']){
  for(const bad of ['FAIL','WARN',null,undefined]){
   const forged={...valid,[lane]:bad};
   const pub={...projection,original_source_age_at_issue:forged};
   assert.match(originalSourceAgeLabel(pub,{valid:true,lang:'da'}),/ukendt/);
   assert.match(originalSourceAgeLabel(pub,{valid:true,lang:'en'}),/unknown/);
  }
 }
 assert.match(originalSourceAgeLabel(
   {...projection,original_source_age_at_issue:valid},{valid:true}),/markedsdata 135 min/);
});

test('truth banner binds source age to the original issue and ages after expiry',()=>{
 const official={...internal(),data_status:"OK"};
 const source=originalSourceAgeAtIssue(official,projection);
 const issued=Date.parse(official.issued_at_utc);
 const expiry=issued+45*60000;
 const origin={public_issue_number:32,issued_date_utc:'2026-11-02'};
 const freshness={contract:'OFFICIAL_COMPASS_SOURCE_FRESHNESS_READBACK_v1',
   status:'VERIFIED_OWNER_POLICY',valid_until_utc:new Date(expiry).toISOString()};
 const compass={...projection,original_source_age_at_issue:source};
 const read=(input=official,feed=compass)=>({...feed,full_stack:{truth_banner:
   kompasTruthReadback(input,feed,{origin,officialFreshness:freshness})}});
 assert.equal(kompasTruthBanner(read(),{nowMs:issued}).state,'FRESH');
 const inherited={...official,cn_protection_state_basis:'INHERITED_FROM_PRIOR_ISSUE'};
 const cases={nowMs:issued+60*60000,weeklyAligned:true};
 const stale=kompasTruthBanner(read(inherited),cases);
 assert.equal(stale.state,'STALE');
 assert.match(stale.text,/udgave #32 \(2026-11-02 UTC\).*Dataalder/);
 assert.match(kompasTruthBanner(read(inherited),{...cases,weeklyAligned:false}).text,/ophav ukendt/);
 assert.equal(kompasTruthBanner({...read(),compass_id:'MISMATCH'},cases).state,'MISSING');
 assert.equal(kompasTruthBanner({...compass,full_stack:{}},cases).state,'MISSING');
 assert.equal(kompasTruthBanner(read({...official,data_status:'DEGRADED'}),cases).state,'DEGRADED');
 const drifted=originalSourceAgeAtIssue({...official,issued_at_utc:'2026-10-01T00:00:00Z'},projection);
 assert.equal(kompasTruthBanner(read(official,{...compass,original_source_age_at_issue:drifted}),cases).state,'MISSING');
});

test('legacy carry reaches original public issue and fails closed on missing or mismatched chain links',async()=>{
 const p={pullback_risk_state:'ELEVATED',pullback_class:'Retest',distribution_risk:'UNKNOWN'};
 const machine=(n,protection=p)=>({issue_number:n,previous_issue_number:n-1,
   generated_unix:1793607548+(n-33)*604800,decision_projection:{protection}});
 const carry=n=>({...machine(n),readable_markdown:'Week\nMethod: CN_OWNER_AUTHORIZED_API_FREE_SEVEN_DAY_v1\n'});
 const start=carry(35),prior=carry(34),original=machine(33);
 const chain=new Map([[34,{pkg:prior,publicIssue:33}],[33,{pkg:original,publicIssue:32}]]);
 const read=n=>chain.get(n);
 assert.deepEqual(await inheritedProtectionOrigin(start,read),
   {public_issue_number:32,issued_date_utc:'2026-11-02'});
 assert.equal(await inheritedProtectionOrigin(start,n=>n===34?read(n):null),null);
 assert.equal(await inheritedProtectionOrigin(start,n=>({...read(n),pkg:machine(n,{...p,pullback_risk_state:'HIGH'})})),null);
 const explicit=machine(36,{...p,state_basis:'INHERITED_FROM_PRIOR_ISSUE',inherited_from_issue_number:33});
 assert.deepEqual(await inheritedProtectionOrigin(explicit,read),
   {public_issue_number:32,issued_date_utc:'2026-11-02'});
});
