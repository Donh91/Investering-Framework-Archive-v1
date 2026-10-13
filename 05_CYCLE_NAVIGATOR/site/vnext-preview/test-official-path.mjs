import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { officialPathView, PATH_CONTRACT } from './official-path.mjs';

const folder=dirname(fileURLToPath(import.meta.url));
const raw=JSON.parse(readFileSync(resolve(folder,'seed.json'),'utf8'));
const check=(modify,opt={})=>{
 const original=structuredClone(raw);
 if(modify)modify(original);
 return officialPathView(original,opt);
};
let tests=0;
const test=(name,fn)=>{fn();console.log('PASS',++tests,name)};
const base=check();

test('Exact W41 archive source reads as archive, not live',()=>{
 assert.equal(base.contract,PATH_CONTRACT);
 assert.equal(base.status,'SOURCE_BOUND');
 assert.equal(base.is_live,false);
 assert.equal(base.verified_current,false);
 assert.match(base.source_label,/Arkiv · ikke live · CN #28 · 2026-W41/);
 assert.equal(base.source_health,'DEGRADED');
 assert.equal(base.source_issue,28);
 assert.equal(base.source_week,'2026-W41');
});
test('Only BTC historically documented, no live confirmed ETH stage',()=>{
 assert.equal(base.current_checkpoint.key,'BTC');
 assert.equal(base.current_checkpoint.status,'FROZEN_WEEK_REFERENCE');
 assert.equal(base.next_checkpoint.key,'ETH');
 assert.equal(base.next_checkpoint.status,'UNCONFIRMED');
 assert.match(base.next_gate,/ETH\/BTC/);
 assert.equal(base.full_phases[1].status,'UNCONFIRMED');
});
test('Full canonical phase route, compact five-stop path, no synthetic phase jumps',()=>{
 assert.deepEqual(base.full_phases.map(x=>x.key),[
  'BTC','ETH','LARGE_MID','ALT_IGNITION','MICRO','BROAD',
  'MANIA','DISTRIBUTION','PROTECTION','REENTRY'
 ]);
 assert.deepEqual(base.concise_phases.map(x=>x.key),
  ['BTC','ETH','LARGE_MID','ALT_IGNITION','PROTECTION']);
 assert.equal(base.full_phases.filter(x=>x.is_reference).length,1);
 assert.ok(!base.full_phases.some(x=>x.status==='ACTIVE'||x.status==='CONFIRMED_CYCLE'));
});
test('No stopwatch or invented DSB temporal spacing from conditional W41 source prose',()=>{
 assert.equal(base.phase_eta,'Ingen verificeret ETA');
 assert.match(base.source_window,/W41/);
 assert.equal(base.altseason.eta,'Ingen verificeret ETA');
 assert.equal(base.altseason.status,'WATCH_ONLY');
 assert.notEqual(base.altseason.status,'CONFIRMED');
});
test('Exact current source seven tier actions never convert HOLD to leadership or micro to memes',()=>{
 assert.equal(base.rotation.length,7);
 assert.deepEqual(base.rotation.map(x=>x.key),[
  'BTC','ETH','LARGE_CAPS','MID_CAPS','SMALL_CAPS','MICROCAPS','MEMES'
 ]);
 assert.deepEqual(base.rotation.map(x=>x.action),[
  'HOLD','HOLD','WAIT','WAIT','WAIT','HARD_WAIT','UNAVAILABLE'
 ]);
 assert.equal(base.rotation.find(x=>x.key==='MEMES').eta,null);
 assert.equal(base.full_phases[1].status,'UNCONFIRMED');
});
test('Long cycle 4–8w stays unavailable, no invented strategic ETA',()=>{
 assert.match(base.structural_long.weeks_4_8,/UNAVAILABLE/i);
 assert.match(base.structural_long.weeks_2_3,/Selective/);
});
test('Separate protection and sell cannot become automatic completed cycle phases',()=>{
 assert.equal(base.protection,'BUILDING');
 assert.equal(base.sell,'UNAVAILABLE');
 assert.equal(base.reentry,'INACTIVE');
 for(const phase of base.full_phases.slice(7)){
  assert.notEqual(phase.status,'CONFIRMED_CYCLE');
  assert.equal(phase.is_reference,false);
 }
});
test('DO NOT set observed BTC current reference without two independent weekly text hooks',()=>{
 for(const mutate of [
   d=>{d.weekly.market_state='Unknown cycle, no verified leadership';},
   d=>{d.weekly.rotation_ladder[0].status='BTC recently moved in USD';}
 ]){
  const p=check(mutate);
  assert.equal(p.status,'SOURCE_BOUND');
  assert.equal(p.current_checkpoint,null);
  assert.equal(p.next_checkpoint,null);
  assert.equal(p.full_phases[0].status,'UNCONFIRMED');
 }
});
test('ETH HOLD and false positive 30d altseason label cannot confirm broad altseason',()=>{
 const p=check(d=>{
   d.compass.capitalization_ladder.find(x=>x.segment==='ETH').status='HOLD';
   d.weekly.altseason_countdown[0].phase='30d alt participation: ALTCOIN_SEASON at 99';
 });
 assert.equal(p.next_checkpoint.status,'UNCONFIRMED');
 assert.equal(p.altseason.status,'WATCH_ONLY');
 assert.equal(p.altseason.eta,'Ingen verificeret ETA');
});
test('All risk/SELL states only contextual, never phase promotions',()=>{
 const p=check(d=>{
  d.compass.protection_tracker.distribution_risk='CONFIRMED';
  d.compass.sell_assessment.state='SELL';
  d.compass.protection_tracker.reentry_state='REVIEW';
 });
 assert.equal(p.full_phases[7].status,'SOURCE_RISK_CONDITION_NOT_CYCLE_CONFIRMATION');
 assert.equal(p.full_phases[8].status,'SOURCE_SELL_CONTEXT_NOT_CYCLE_CONFIRMATION');
 assert.equal(p.full_phases[7].is_reference,false);
 assert.equal(p.current_checkpoint.key,'BTC');
});
test('Fail closed on wrong preview identity, week, missing price/frozen owner, stale sources',()=>{
 for(const mutate of [
  d=>{d.weekly.public_issue_number=30;},
  d=>{d.weekly.forecast_week='2026-W42';},
  d=>{d.compass.compass_id='WRONG';},
  d=>{d.compass.data_status='DEGRADED';},
  d=>{d.weekly.status='UNKNOWN';},
  d=>{d.weekly.rotation_ladder=null;},
  d=>{d.compass.capitalization_ladder=null;},
  d=>{d.weekly.altseason_countdown=null;},
  d=>{d.source_status='UNKNOWN';}
 ]){
  const p=check(mutate);
  assert.equal(p.status,'UNAVAILABLE');
  assert.equal(p.current_checkpoint,null);
  assert.equal(p.rotation.length,0);
 }
});
test('Cannot claim archived preview as real-time source through caller flag',()=>{
 const p=check(null,{mode:'live',verifiedAlignment:true});
 assert.equal(p.status,'UNAVAILABLE');
 assert.equal(p.is_live,false);
});
test('Live verification requires all source identities and cannot be toggled by one flag',()=>{
 const p=check(d=>{
   d.source_status='LIVE';
   d.weekly.public_issue_number=29;
   d.weekly.forecast_week='2026-W42';
   d.compass.weekly_context={public_issue_number:29,forecast_week:'2026-W42',status:'MISMATCH'};
 },{mode:'live',verifiedAlignment:true});
 assert.equal(p.status,'UNAVAILABLE');
 assert.equal(p.verified_current,false);
});
test('Danish/English changes presentation, not phase/source/actions',()=>{
 const english=check(null,{lang:'en'});
 assert.equal(english.status,base.status);
 assert.equal(english.current_checkpoint.key,base.current_checkpoint.key);
 assert.equal(english.next_checkpoint.key,base.next_checkpoint.key);
 assert.deepEqual(english.rotation.map(x=>x.action),base.rotation.map(x=>x.action));
 assert.deepEqual(english.full_phases.map(x=>x.key),base.full_phases.map(x=>x.key));
 assert.equal(english.phase_eta,'No verified ETA');
 assert.match(english.source_label,/Archived · not live/);
});
test('No private wallet/positions leak to site view',()=>{
 const p=check(d=>{
  d.private_wallet_address='0xprivate';
  d.compass.holdings=[{name:'NOT_ALLOWED'}];
 });
 assert.equal(JSON.stringify(p).includes('0xprivate'),false);
 assert.equal(JSON.stringify(p).includes('NOT_ALLOWED'),false);
});
test('Frozen evidence is never mutated',()=>{
 const before=JSON.stringify(raw);
 officialPathView(raw);
 officialPathView(raw,{lang:'en'});
 assert.equal(JSON.stringify(raw),before);
});
console.log('SUCCESS: '+tests+' source-bounded PATH contract tests, no active phase/ETA/BUY/SELL fabricated.');
