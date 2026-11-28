import test from 'node:test';
import assert from 'node:assert/strict';
import {bindNativeParticipation,readCycleParticipation,renderCycleParticipation,bindNativeAltseason,readAltseason,altseasonDisplay,t6ObservationPath,bindT6Observation,t6ResearchDisplay} from '../cycle-participation.mjs';
const observed='2026-11-25T10:00:00Z',issued='2026-11-25T10:15:00Z',nowUtc='2026-11-25T11:00:00Z';
function fixture(){
 const row={state:'OBSERVED_PROXY',coverage:'TOP100_FULL_RANK_WINDOW',advancing:'MAJORITY',outperforming_btc:'MAJORITY',outperforming_eth:'HALF'};
 const cycle_participation={contract:'CN_CYCLE_PARTICIPATION_READBACK_v1',semantics:'OBSERVED_24H_RELATIVE_PERFORMANCE_NOT_CAPITAL_FLOW',
 authority:'DESCRIPTIVE_ONLY_NO_ACTION_OR_FORECAST',status:'OBSERVED_PARTICIPATION',observed_at_utc:observed,valid_until_utc:'2026-11-25T18:00:00Z',
 relative_leader:'ETH',phase:'UNAVAILABLE',rotation_confirmed:false,buckets:{LARGE_ALT_PROXY:{...row},MID_ALT_PROXY:{...row},SMALL_ALT_PROXY:{...row,coverage:'TOP100_TAIL_ONLY_NOT_FULL_SMALL_CAP_UNIVERSE'},MICROCAP_PROXY:{state:'UNAVAILABLE'},MEMES:{state:'UNAVAILABLE'}}};
 const c={contract:'PUBLIC_COMPASS_PROJECTION_v1',data_status:'DEGRADED',weekly_context:{status:'MISMATCH'},compass_id:'CMP-TEST',issued_at_utc:issued,cycle_participation};
 const l={schema:'CN_PUBLIC_SNAPSHOT_V2',generated_at:'2026-11-25T10:30:00Z',package:{status:'DEGRADED'}};
 const n={contract:'NATIVE_HANDLEKOMPAS_v1',generated_at_utc:issued,source:{packet_sha256:'a'.repeat(64)},cycle_participation};
 const a={contract:'AUTO_MARKET_STATE_PACKET_v1',packet_sha256:'a'.repeat(64),packet_generated_at_utc:'2026-11-25T10:10:00Z'};
 function bind(){c.full_stack={source_status:{native:'VERIFIED_NEWER_OR_DIFFERENT_SOURCE'},native:{checked_at_utc:issued},native_cycle_participation_binding:bindNativeParticipation(n,a,{verified:true})};}
 bind();return {c,l,n,a,bind};
}
test('actual cycle renderer independent of weekly and action health; mutation changes output',()=>{
 const x=fixture(),elements=Object.fromEntries(['cn-map-participation','cn-map-participation-details'].map(k=>[k,{hidden:true,textContent:''}]));
 const doc={getElementById:k=>elements[k]};
 renderCycleParticipation(doc,x.l,x.c,{nowUtc,lang:'en'});
 assert.equal(elements['cn-map-participation'].hidden,false);
 assert.match(elements['cn-map-participation'].textContent,/ETH/);
 assert.match(elements['cn-map-participation-details'].textContent,/not capital flow or cycle phase/);
 x.n.cycle_participation.relative_leader='BTC';
 for(const k of ['LARGE_ALT_PROXY','MID_ALT_PROXY','SMALL_ALT_PROXY']){
  x.n.cycle_participation.buckets[k].outperforming_btc='HALF';
  x.n.cycle_participation.buckets[k].outperforming_eth='MAJORITY';
 }
 x.n.cycle_participation.buckets.LARGE_ALT_PROXY.outperforming_btc='MAJORITY';x.bind();
 renderCycleParticipation(doc,x.l,x.c,{nowUtc,lang:'en'});
 assert.match(elements['cn-map-participation'].textContent,/BTC/);
 assert.match(elements['cn-map-participation-details'].textContent,/Large: majority/);
 renderCycleParticipation(doc,x.l,x.c,{nowUtc:'2026-11-25T18:00:00Z'});
 assert.equal(elements['cn-map-participation'].hidden,true);
 assert.equal(elements['cn-map-participation'].textContent,'');
});
test('unverified digest gate and mismatched Auto packet cannot supply proof',()=>{
 const x=fixture();assert.equal(bindNativeParticipation(x.n,x.a),null);
 x.n.source.packet_sha256='b'.repeat(64);x.bind();
 assert.equal(readCycleParticipation(x.l,x.c,{nowUtc}),null);
});
test('malformed clocks, unbound source, fabricated micro and false phase fail closed',()=>{
 for(const edit of [
 x=>x.c.full_stack.native_cycle_participation_binding.issued_at_utc='2026-11-25T10:16:00Z',
 x=>x.l.generated_at='2026-11-25T09:00:00Z',
 x=>x.l.generated_at='2026-11-25T12:00:00Z',
 x=>x.c.full_stack.native_cycle_participation_binding.readback.phase='ROTATION',
 x=>x.c.full_stack.native_cycle_participation_binding.readback.buckets.MICROCAP_PROXY.state='OBSERVED_PROXY',
 x=>x.c.full_stack.native_cycle_participation_binding.readback.valid_until_utc='2026-11-26T18:00:00Z'
 ]){const x=fixture();edit(x);assert.equal(readCycleParticipation(x.l,x.c,{nowUtc}),null);}
});

test('newer hourly native readback is independent of the official slot and weekly freeze',()=>{
 const x=fixture(),n={contract:'NATIVE_HANDLEKOMPAS_v1',generated_at_utc:'2026-11-25T10:25:00Z',source:{packet_sha256:'a'.repeat(64)},cycle_participation:structuredClone(x.c.cycle_participation)};
 const a={contract:'AUTO_MARKET_STATE_PACKET_v1',packet_sha256:'a'.repeat(64),packet_generated_at_utc:'2026-11-25T10:20:00Z'};
 n.cycle_participation.relative_leader='BTC';
 for(const k of ['LARGE_ALT_PROXY','MID_ALT_PROXY','SMALL_ALT_PROXY'])n.cycle_participation.buckets[k].outperforming_btc='MINORITY';
 const b=bindNativeParticipation(n,a,{verified:true});
 assert.ok(b);
 x.c.full_stack.native_cycle_participation_binding=b;
 x.c.full_stack.source_status={native:'VERIFIED_NEWER_OR_DIFFERENT_SOURCE'};
 x.c.full_stack.native={checked_at_utc:n.generated_at_utc};
 assert.equal(readCycleParticipation(x.l,x.c,{nowUtc}).relative_leader,'BTC');
 assert.equal(bindNativeParticipation(n,a),null);
 assert.equal(bindNativeParticipation(n,{...a,packet_sha256:'b'.repeat(64)},{verified:true}),null);
 x.c.full_stack.native.checked_at_utc='2026-11-25T10:26:00Z';
 assert.equal(readCycleParticipation(x.l,x.c,{nowUtc}),null);
});

test('new native missing evidence cannot silently borrow the older official observation',()=>{
 const x=fixture();x.c.full_stack.native_cycle_participation_binding=null;
 assert.equal(readCycleParticipation(x.l,x.c,{nowUtc}),null);
});

test('live altseason source category survives weekly mismatch; stale, carry and future never become ETA',()=>{
 const x=fixture(),n={contract:'NATIVE_HANDLEKOMPAS_v1',generated_at_utc:issued,source:{packet_sha256:'a'.repeat(64)},
 altseason_readback:{contract:'CN_ALTSEASON_OBSERVATION_v1',source:'BLOCKCHAINCENTER_90D',authority:'CONTEXT_ONLY_NO_TRANSITION_OR_ETA',
 status:'OBSERVED',state:'ALTCOIN_SEASON',observed_at_utc:observed,valid_until_utc:'2026-11-26T10:00:00Z'}};
 const a={contract:'AUTO_MARKET_STATE_PACKET_v1',packet_sha256:'a'.repeat(64),packet_generated_at_utc:'2026-11-25T10:10:00Z'};
 x.c.full_stack.source_status={native:'VERIFIED_NEWER_OR_DIFFERENT_SOURCE'};
 x.c.full_stack.native={checked_at_utc:issued};
 function bind(){x.c.full_stack.native_altseason_binding=bindNativeAltseason(n,a,{verified:true});}
 bind();assert.match(altseasonDisplay(x.l,x.c,{nowUtc,lang:'en'}).state,/Altcoin season/);
 n.altseason_readback.state='BITCOIN_SEASON';bind();
 assert.match(altseasonDisplay(x.l,x.c,{nowUtc,lang:'en'}).state,/Bitcoin season/);
 assert.equal(altseasonDisplay(x.l,x.c,{nowUtc,lang:'en'}).eta,'No verified ETA');
 assert.equal(readAltseason(x.l,x.c,{nowUtc:'2026-11-26T10:00:00Z'}),null);
 n.altseason_readback.status='CARRIED_NOT_FRESH';n.altseason_readback.valid_until_utc='2026-11-28T10:00:00Z';bind();
 assert.match(altseasonDisplay(x.l,x.c,{nowUtc,lang:'en'}).state,/carried, not fresh/);
 assert.equal(bindNativeAltseason(n,{...a,packet_sha256:'b'.repeat(64)},{verified:true}),null);
 assert.equal(readAltseason(x.l,x.c,{nowUtc:'2026-11-25T09:00:00Z'}),null);
});

test('segment detail reflects advancing and ETH-relative observations, not a rotation sequence',()=>{
 const x=fixture(),elements=Object.fromEntries(['cn-map-participation','cn-map-participation-details'].map(k=>[k,{hidden:true,textContent:''}]));
 const doc={getElementById:k=>elements[k]},details=elements['cn-map-participation-details'];
 renderCycleParticipation(doc,x.l,x.c,{nowUtc,lang:'en'});
 assert.match(details.textContent,/Large: majority outperform BTC, half outperform ETH, majority advancing/);
 assert.match(details.textContent,/not the full small-cap universe/);
 assert.match(details.textContent,/Rotation sequence unverified/);
 x.n.cycle_participation.buckets.LARGE_ALT_PROXY.advancing='MINORITY';
 x.n.cycle_participation.buckets.LARGE_ALT_PROXY.outperforming_eth='MAJORITY';x.bind();
 renderCycleParticipation(doc,x.l,x.c,{nowUtc,lang:'da'});
 assert.match(details.textContent,/Store: flertal slår BTC, flertal slår ETH, mindretal stiger/);
 assert.match(details.textContent,/Rotationssekvens ikke verificeret/);
 x.n.cycle_participation.buckets.MID_ALT_PROXY={state:'UNAVAILABLE'};
 x.n.cycle_participation.status='PARTIAL_OBSERVATION';x.bind();
 renderCycleParticipation(doc,x.l,x.c,{nowUtc,lang:'en'});
 assert.match(details.textContent,/Mid: unavailable/);
});
test('impossible UTC calendar dates and 24:00 do not normalize into valid source observations',()=>{
 for(const [bad,exp,packet,issued] of [
  ['2026-02-30T10:00:00Z','2026-03-02T18:00:00Z','2026-03-02T10:10:00Z','2026-03-02T10:15:00Z'],
  ['2026-11-24T24:00:00Z','2026-11-25T08:00:00Z','2026-11-25T00:10:00Z','2026-11-25T00:15:00Z']
 ]){
  const x=fixture();
  Object.assign(x.n.cycle_participation,{observed_at_utc:bad,valid_until_utc:exp});
  x.n.generated_at_utc=issued;x.a.packet_generated_at_utc=packet;
  assert.equal(bindNativeParticipation(x.n,x.a,{verified:true}),null);
 }
});

test('relative benchmark order is enforced for every segment, on binding and readback',()=>{
 const states=['MINORITY','HALF','MAJORITY'];
 for(const leader of ['BTC','ETH','TIED'])for(const [bi,btc] of states.entries())for(const [ei,eth] of states.entries()){
  const expected=leader==='BTC'?ei>=bi:leader==='ETH'?bi>=ei:bi===ei;
  for(const key of ['LARGE_ALT_PROXY','MID_ALT_PROXY','SMALL_ALT_PROXY']){
   const x=fixture();x.n.cycle_participation.relative_leader=leader;
   for(const k of ['LARGE_ALT_PROXY','MID_ALT_PROXY','SMALL_ALT_PROXY'])Object.assign(x.n.cycle_participation.buckets[k],{outperforming_btc:'HALF',outperforming_eth:'HALF'});
   x.bind();assert.ok(x.c.full_stack.native_cycle_participation_binding);
   Object.assign(x.c.full_stack.native_cycle_participation_binding.readback.buckets[key],{outperforming_btc:btc,outperforming_eth:eth});
   assert.equal(Boolean(readCycleParticipation(x.l,x.c,{nowUtc})),expected);
   Object.assign(x.n.cycle_participation.buckets[key],{outperforming_btc:btc,outperforming_eth:eth});
   assert.equal(Boolean(bindNativeParticipation(x.n,x.a,{verified:true})),expected);
  }
 }
});

const t6Auth={binding:false,market_interpretation:'NONE',canonical_acceptance:false,state_change:false,portfolio_action:false,market_threshold_change:false,model_weight_change:false,research_only:true};
function t6Fixture(event='NO_ELIGIBLE_FIRST_CROSS'){
 const seq='T6-'+'a'.repeat(16),at='2026-11-25T10:00:00Z',digest='b'.repeat(64);
 const p={contract:'ROTATION_SURVIVAL_LATEST_v1',authority:{...t6Auth},event,observed_at_utc:at,
  observation_path:'research/framework_memory/rotation_survival_forward_rows/observations/2026-11-25_'+'c'.repeat(20)+'.json',
  observation_sha256:digest,active_sequence_id:null};
 const o={contract:'ROTATION_SURVIVAL_OBSERVATION_v1',authority:{...t6Auth},event,observed_at_utc:at,source_packet_sha256:'d'.repeat(64),
  retrospective_creation:false,active_sequence_id_before:null,first_cross_detected:false,axes:{private:'DO_NOT_PUBLISH'},right_censored:true};
 if(event==='FIRST_CROSS_FROZEN'){p.active_sequence_id=seq;o.first_cross_detected=true;delete o.right_censored;}
 if(event==='ACTIVE_SEQUENCE_OBSERVATION'||event==='ETHBTC_REVERSAL_OBSERVED'){
  const active=event==='ACTIVE_SEQUENCE_OBSERVATION';p.active_sequence_id=active?seq:null;
  Object.assign(o,{sequence_id:seq,active_sequence_id_before:seq,time_in_state_days:2,right_censored:active});
 }
 return {p,o,digest};
}
test('T6 only projects dated research events and never leaks source values or grants authority',()=>{
 const latest={schema:'CN_PUBLIC_SNAPSHOT_V2',generated_at:'2026-11-25T10:30:00Z'};
 const compass={contract:'PUBLIC_COMPASS_PROJECTION_v1',weekly_context:{status:'MISMATCH'},full_stack:{}};
 const row={hidden:true,textContent:''},doc={getElementById:id=>id==='cn-map-t6-research'?row:null};
 for(const event of ['NO_ELIGIBLE_FIRST_CROSS','FIRST_CROSS_FROZEN','ACTIVE_SEQUENCE_OBSERVATION','ETHBTC_REVERSAL_OBSERVED']){
  const {p,o,digest}=t6Fixture(event);
  const b=bindT6Observation(p,o,digest,{nowUtc});
  assert.ok(b);assert.equal(b.event,event);assert.equal(Object.keys(b).length,4);
  assert.equal(JSON.stringify(b).includes('DO_NOT_PUBLISH'),false);
  compass.full_stack.t6_research_observation=b;
  renderCycleParticipation(doc,latest,compass,{nowUtc,lang:'en'});
  assert.equal(row.hidden,false);assert.match(row.textContent,/Last recorded T6 research observation/);
  assert.match(row.textContent,/not current rotation confirmation or forecast/);
 }
 compass.full_stack.t6_research_observation=null;
 renderCycleParticipation(doc,latest,compass,{nowUtc});assert.equal(row.hidden,true);assert.equal(row.textContent,'');
});
test('T6 tampered pointer, authority, event, sequence, chronology and malformed path fail closed',()=>{
 const attacks=[
  x=>x.p.observation_path=x.p.observation_path.replace('/observations/','/observations/../'),
  x=>x.p.observation_path=x.p.observation_path.replace('2026-11-25_','2026-11-24_'),
  x=>x.p.observation_sha256='f'.repeat(64),
  x=>x.o.authority.portfolio_action=true,
  x=>x.p.authority.market_interpretation='LIVE',
  x=>x.o.retrospective_creation=true,
  x=>x.o.event='FIRST_CROSS_FROZEN',
  x=>x.p.active_sequence_id='T6-'+'a'.repeat(16),
  x=>x.o.first_cross_detected=true,
  x=>x.o.right_censored=false,
  x=>x.o.sequence_id='T6-'+'a'.repeat(16),
  x=>x.o.observed_at_utc='2026-11-25T09:59:00Z',
  x=>{x.p.observed_at_utc=x.o.observed_at_utc='2026-11-25T12:00:00Z';},
  x=>{x.p.observed_at_utc=x.o.observed_at_utc='2026-11-25T24:00:00Z';},
 ];
 for(const mutate of attacks){const x=t6Fixture();mutate(x);assert.equal(bindT6Observation(x.p,x.o,x.digest,{nowUtc}),null);}
 for(const event of ['ACTIVE_SEQUENCE_OBSERVATION','ETHBTC_REVERSAL_OBSERVED']){
  const x=t6Fixture(event);x.o.time_in_state_days=-1;assert.equal(bindT6Observation(x.p,x.o,x.digest,{nowUtc}),null);
 }
 const {p,o,digest}=t6Fixture(),b=bindT6Observation(p,o,digest,{nowUtc});
 const c={contract:'PUBLIC_COMPASS_PROJECTION_v1',full_stack:{t6_research_observation:b}};
 const latest={schema:'CN_PUBLIC_SNAPSHOT_V2',generated_at:'2026-11-25T09:59:00Z'};
 assert.equal(t6ResearchDisplay(latest,c,{nowUtc}),'');
 latest.generated_at='2026-11-25T12:00:00Z';assert.equal(t6ResearchDisplay(latest,c,{nowUtc}),'');
 latest.generated_at='2026-11-25T10:30:00Z';b.authority='TRADE';assert.equal(t6ResearchDisplay(latest,c,{nowUtc}),'');
});
