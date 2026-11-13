import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {validateChallengerPublic,CHALLENGER_A_PUBLIC_CONTRACT} from './challenger-a-panel.mjs';
const iso='2026-11-16T10:35:00Z';
const day=k=>({day:k,scored_from_utc:'2026-11-'+String(15+k).padStart(2,'0')+'T11:00:00Z',
 end_utc:'2026-11-'+String(16+k).padStart(2,'0')+'T00:00:00Z',
 band:{range:{'0.8':[65000,80000]},close:{'0.8':[68000,78000]}}});
const mk=()=>({
 contract:CHALLENGER_A_PUBLIC_CONTRACT,publication_status:'ISSUED_FROZEN',visibility:'SHADOW_ONLY',
 source:{blob_sha:'a'.repeat(40),first_in_main_commit:'b'.repeat(40),
  first_in_main_utc:'2026-11-16T10:40:00Z',sha256:'c'.repeat(64)},
 issuance:{contract:'TASK2_CHALLENGER_A_SQRT_T_VOL_BAND_v1',formula_version:'A1',
  issuance_sha256:'d'.repeat(64),week:'2026-W47',issue_clock_utc:iso,
  authority:{research_only:true,official_forecast:false,trading:false,promotion:false},
  assets:{BTC:{P0:70000,days:Array.from({length:7},(_,i)=>day(i+1))},
   ETH:{P0:2000,days:Array.from({length:7},(_,i)=>day(i+1))}}}
});
const now=Date.parse('2026-11-20T12:00:00Z');
test('complete source-pinned W47 shadow issuance renders as eligible',()=>{
 const v=validateChallengerPublic(mk(),now);
 assert.equal(v.ok,true);assert.equal(v.days.BTC.length,7);
 assert.equal(v.week,'2026-W47');assert.equal(v.source_commit,'b'.repeat(40));
});
test('reject missing issuer, missing source, future clocks and retroactive publication',()=>{
 for(const mutate of [
  p=>{p.contract='CN_OFFICIAL_FORECAST'},
  p=>{p.issuance.authority.official_forecast=true},
  p=>{p.issuance.week='2026-W46'},
  p=>{delete p.source.first_in_main_commit},
  p=>{p.source.first_in_main_utc='2026-11-21T10:40:00Z'},
  p=>{p.source.first_in_main_utc='2026-11-16T12:00:00Z'},
  p=>{p.issuance.issue_clock_utc='2026-11-21T12:00:00Z'},
  p=>{p.issuance.assets.ETH.days.pop()},
  p=>{p.issuance.assets.BTC.days[0].band.range['0.8']=[82000,67000]}
 ]){const p=mk();mutate(p);assert.equal(validateChallengerPublic(p,now).ok,false)}
 assert.equal(validateChallengerPublic(null,now).ok,false);
});
test('source-only integration into Prognose tab and no official graph mutation',async()=>{
 const tabs=await readFile(new URL('./premium-tabs.mjs',import.meta.url),'utf8');
 const css=await readFile(new URL('./premium-tabs.css',import.meta.url),'utf8');
 assert.match(tabs,/mountChallengerA\(graphPanel/);
 assert.match(tabs,/selected\.key === 'graph'.*challengerPanel\.refresh\(\)/);
 assert.match(css,/\.cn-challenger-a/);
 assert.doesNotMatch(tabs,/Math\.sin|forecast_low|forecast_high/);
});
