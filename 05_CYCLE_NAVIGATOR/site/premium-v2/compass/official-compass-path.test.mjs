import test from 'node:test';
import assert from 'node:assert/strict';
import {readOfficialCompassPath} from './official-compass-path.mjs';
const latest=()=>({schema:'CN_PUBLIC_SNAPSHOT_V2',
 public_series:{current_public_projection:{forecast_week:'2026-W43',public_issue_number:30}},
 package:{market_cycle_context:{
 current_phase:'UNAVAILABLE',next_gate:'Need durable ETH leadership'}}});
function official(){
 const directions={NEXT_12H:'UP',NEXT_1_3D:'MIXED',NEXT_5_7D:'MIXED',
 NEXT_2_3W:'MIXED',CYCLE_ALTCOINS_3_8W:'UNAVAILABLE'};
 const tiers=['BTC','ETH','LARGE_CAPS','MID_CAPS','SMALL_CAPS','MICROCAPS','MEMES'];
 return {contract:'PUBLIC_COMPASS_PROJECTION_v1',data_status:'OK',
  issued_at_utc:'2026-10-23T17:05:30Z',action_now:'HOLD_WAIT',compass_id:'CMP-TEST-READONLY',
  weekly_context:{contract:'CN_COMPASS_WEEKLY_ALIGNMENT_v1',status:'ALIGNED',
   forecast_week:'2026-W43',public_issue_number:30},
  full_stack:{official_freshness:{contract:'OFFICIAL_COMPASS_SOURCE_FRESHNESS_READBACK_v1',
   status:'VERIFIED_OWNER_POLICY',source_asof_utc:'2026-10-23T15:00:00Z',
   valid_until_utc:'2026-10-23T18:00:00Z'}},
  horizons:Object.fromEntries(Object.entries(directions).map(([k,expected_direction])=>[k,
   {expected_direction,action_posture:'WAIT',expected_path:'source-copy only'}])),
  capitalization_ladder:tiers.map(segment=>({segment,status:'WAIT',action:'WAIT',direction:'MIXED',
    reason:'source reason only'})),
  bull_bear_scale:{contract:'OFFICIAL_COMPASS_BULL_BEAR_DISPLAY_v1',
   semantics:'EVIDENCE_BALANCE_NOT_PROBABILITY',authority:{probability_model:false},
   horizons:{'1_3d':{bull:5,bear:5},'5_7d':{bull:5,bear:5},'2_3w':{bull:5,bear:5}}}
 };
}
test('official HOLD_WAIT remains display-only and never becomes BUY or probability',()=>{
 const v=readOfficialCompassPath(official(),latest(),{now_utc:'2026-10-23T17:30:00Z'});
 assert.equal(v.status,'SOURCE_CURRENT');assert.equal(v.official_action,'HOLD_WAIT');
 assert.equal(v.official_action_current,true);assert.equal(v.bull_bear_semantics,'EVIDENCE_BALANCE_NOT_PROBABILITY');
 assert.equal(v.horizons.length,5);assert.equal(v.capitalization_ladder.length,7);
 assert.equal(v.path_phases.length,10);assert.equal(v.path_current_phase,'UNAVAILABLE');
 assert.equal(v.path_weekly_alignment,'ALIGNED');
 assert.equal(v.rotation_confirmed,false);assert.equal(v.probability_model,false);
});
test('after official expiry, historical action cannot be current',()=>{
 const l=latest();l.package.market_cycle_context.current_phase='ROTATION';
 const v=readOfficialCompassPath(official(),l,{now_utc:'2026-10-23T18:01:00Z'});
 assert.equal(v.status,'SOURCE_EXPIRED');assert.equal(v.official_action,'HOLD_WAIT');
 assert.equal(v.official_action_current,false);
 assert.equal(v.action_allowed_to_display_as_current,false);
 assert.equal(v.path_current_phase,'UNAVAILABLE');
 assert.equal(v.rotation_confirmed,false);
 assert.equal(v.path_next_gate,null);
});
test('an unmatched weekly issue cannot borrow the current Official action for PATH',()=>{
 const l=latest();l.package.market_cycle_context.current_phase='ROTATION';
 const c=official();c.weekly_context.public_issue_number=29;
 const v=readOfficialCompassPath(c,l,{now_utc:'2026-10-23T17:30:00Z'});
 assert.equal(v.official_action_current,true);
 assert.equal(v.path_weekly_alignment,'UNVERIFIED');
 assert.equal(v.path_current_phase,'UNAVAILABLE');
 assert.equal(v.rotation_confirmed,false);
 assert.equal(v.path_next_gate,null);
});
test('spoofed freshness, missing segment or unofficial action fail closed',()=>{
 const v=official();v.full_stack.official_freshness.status='SELF_DECLARED';
 assert.equal(readOfficialCompassPath(v,latest(),{now_utc:'2026-10-23T17:30:00Z'}).status,'UNAVAILABLE');
 const n=official();n.capitalization_ladder.pop();
 assert.equal(readOfficialCompassPath(n,latest(),{now_utc:'2026-10-23T17:30:00Z'}).reason,'FIVE_HORIZON_SEVEN_TIER_CONTRACT_MISMATCH');
 const b=official();b.action_now='SUGGESTED_BUY';
 assert.equal(readOfficialCompassPath(b,latest(),{now_utc:'2026-10-23T17:30:00Z'}).reason,'UNRECOGNIZED_OFFICIAL_ACTION');
});
test('path checkpoint never invented when original market cycle phase absent',()=>{
 const l=latest();l.package.market_cycle_context.current_phase='We are now in microcap mania!!!';
 const v=readOfficialCompassPath(official(),l,{now_utc:'2026-10-23T17:30:00Z'});
 assert.equal(v.path_current_phase,'UNAVAILABLE');assert.equal(v.rotation_confirmed,false);
});

test('canonical phase machine codes map to the actual 10-stage PATH without ETA',()=>{
 const cases=[
  ['PRE_ROTATION','BTC leadership'],
  ['ROTATION','Large + Mid rotation'],
  ['BROAD_ALTSEASON','Broad altseason'],
  ['PARABOLIC_ALTSEASON','Mania / euphoria'],
  ['DISTRIBUTION','Distribution'],
  ['EXIT_RISK','Exit / protection']
 ];
 for(const [code,expected] of cases){
  const l=latest();l.package.market_cycle_context.current_phase=code;
  const m=readOfficialCompassPath(official(),l,{now_utc:'2026-10-23T17:30:00Z'});
  assert.equal(m.path_current_phase,expected,code);
  assert.equal(m.rotation_confirmed,true,code);
  assert.equal(m.path_phases.filter(p=>p===expected).length,1);
  assert.equal(m.decision_authority,false);
 }
});
test('defensive, unsupported and missing producer phase cannot invent reentry or current step',()=>{
 for(const code of ['DEFENSIVE','CONSOLIDATION','UNCLEAR','UNAVAILABLE',null]){
  const l=latest();l.package.market_cycle_context.current_phase=code;
  const m=readOfficialCompassPath(official(),l,{now_utc:'2026-10-23T17:30:00Z'});
  assert.equal(m.path_current_phase,'UNAVAILABLE',String(code));
  assert.equal(m.rotation_confirmed,false,String(code));
 }
});
