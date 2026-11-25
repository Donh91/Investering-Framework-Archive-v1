import test from 'node:test';
import assert from 'node:assert/strict';
import {bindNativeParticipation,readCycleParticipation,renderCycleParticipation,bindNativeAltseason,readAltseason,altseasonDisplay} from '../cycle-participation.mjs';
const observed='2026-11-25T10:00:00Z',issued='2026-11-25T10:15:00Z',nowUtc='2026-11-25T11:00:00Z';
function fixture(){
 const row={state:'OBSERVED_PROXY',coverage:'TOP100_FULL_RANK_WINDOW',advancing:'MAJORITY',outperforming_btc:'MINORITY',outperforming_eth:'HALF'};
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
 assert.match(details.textContent,/Large: minority outperform BTC, half outperform ETH, majority advancing/);
 assert.match(details.textContent,/not the full small-cap universe/);
 assert.match(details.textContent,/Rotation sequence unverified/);
 x.n.cycle_participation.buckets.LARGE_ALT_PROXY.advancing='MINORITY';
 x.n.cycle_participation.buckets.LARGE_ALT_PROXY.outperforming_eth='MAJORITY';x.bind();
 renderCycleParticipation(doc,x.l,x.c,{nowUtc,lang:'da'});
 assert.match(details.textContent,/Store: mindretal slår BTC, flertal slår ETH, mindretal stiger/);
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
