import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,readFile,mkdir,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,resolve,dirname} from 'node:path';
import {projectPullbackReport,buildPublicPullback,CONTRACT} from '../build-pullback-research.mjs';

const NOW=new Date('2026-10-31T12:00:00Z'),DAY='2026-10-31';
function original(){
 const n=2;
 return {contract:'KOMPAS_ROLLING_14D_HISTORICAL_ACCOUNTABILITY_v1',
  scope:'rolling14',research_only:true,automatic_model_reweighting:false,
  trade_permission:'NONE',first_known_publication_verified:false,
  frozen_forecasts_unchanged:true,generated_at_utc:'2026-10-31T11:26:30Z',
  copenhagen_date:DAY,all_issuances:{forecasts:149,
   all_issuance_rows:[{private_provider_key:'FORBIDDEN_RAW_VALUE'}]},
  pullback_warning_timebox_shadow:{
   contract:'PULLBACK_RADAR_TIMEBOX_SHADOW_v1',
   first_known_publication_verified:false,prospective_holdout_completed:false,
   automatic_model_reweighting:false,trade_permission:'NONE',
   repeated_elevated_count_is_not_warning_success:true,
   expired_alert_cannot_be_credited_from_later_drop:true,
   false_negative_recall_unknown_without_matched_no_alert_grid:true,
   economically_executable_edge:null,calibrated_probability:null,
   new_warning_or_escalation_events:n,
   warning_state_counts:{NO_WARNING:7,REPEAT_STATE_NOT_NEW_WARNING:137,
    LEFT_CENSORED_NO_TRANSITION_PROOF:2,NEW_WARNING:1,ESCALATION:1,
    SOURCE_UNAVAILABLE_OR_UNQUALIFIED:1},
   horizons:Object.fromEntries(['12h','24h','72h'].map(h=>[h,{
    new_warning_or_escalation_n:n,matured_n:2,hit_n:0,false_alarm_n:2,
    pending_n:0,unknown_n:0,warning_skill_or_edge:null,
    hit_rate_descriptive:0}]))
  }};
}
const bytes=object=>Buffer.from(JSON.stringify(object));
const go=r=>projectPullbackReport(bytes(r),{now:NOW,expectedDay:DAY});
test('only a bounded public receipt is exported, no original rows, no fake probabilities',()=>{
 const v=go(original());
 assert.equal(v.contract,CONTRACT);assert.equal(v.status,'RESEARCH_ONLY');
 assert.equal(v.all_issuances,149);
 assert.equal(v.source_state_counts.repeated,137);
 assert.equal(v.new_warning_events,2);
 assert.equal(v.horizons['72h'].false_alarms,2);
 assert.equal(v.horizons['72h'].hits,0);
 assert.equal(v.horizons['72h'].hit_rate_descriptive,null);
 assert.equal(v.authority.live_warning,false);
 assert.equal(v.scientific_edge_status,'NOT_PROVEN');
 assert.match(v.source_sha256,/^[0-9a-f]{64}$/);
 assert.doesNotMatch(JSON.stringify(v),/FORBIDDEN_RAW_VALUE|private_provider_key/);
});
test('zero fresh alerts is NOT zero risk and has no hit-rate denominator',()=>{
 const r=original();const x=r.pullback_warning_timebox_shadow;
 x.new_warning_or_escalation_events=0;
 x.warning_state_counts.NO_WARNING+=2;
 delete x.warning_state_counts.NEW_WARNING;
 delete x.warning_state_counts.ESCALATION;
 for(const v of Object.values(x.horizons)){v.new_warning_or_escalation_n=0;v.matured_n=0;v.hit_n=0;v.false_alarm_n=0;}
 const a=go(r);
 assert.equal(a.status,'RESEARCH_ONLY');
 assert.equal(a.new_warning_events,0);
 assert.equal(a.horizons['12h'].hit_rate_descriptive,null);
 assert.equal(a.risk_state_is_not_new_warning,true);
});
test('missing new radar field on immutable historical report fails closed',()=>{
 const r=original();delete r.pullback_warning_timebox_shadow;
 const a=go(r);assert.equal(a.status,'UNAVAILABLE');assert.equal(a.new_warning_events,null);
});
test('bad original custody/authority or fake promotion is rejected',()=>{
 for(const change of [
  r=>r.trade_permission='BUY',
  r=>r.automatic_model_reweighting=true,
  r=>r.first_known_publication_verified=true,
  r=>r.pullback_warning_timebox_shadow.trade_permission='SELL',
  r=>r.pullback_warning_timebox_shadow.economically_executable_edge=1,
  r=>r.pullback_warning_timebox_shadow.repeated_elevated_count_is_not_warning_success=false,
 ]){
  const r=original();change(r);
  assert.equal(go(r).status,'UNAVAILABLE');
 }
});
test('invalid horizon denominators and contradictory sample size rejected',()=>{
 for(const change of [
  r=>r.pullback_warning_timebox_shadow.horizons['72h'].matured_n=3,
  r=>r.pullback_warning_timebox_shadow.horizons['12h'].hit_n=3,
  r=>r.pullback_warning_timebox_shadow.horizons['24h'].pending_n=1,
  r=>r.pullback_warning_timebox_shadow.warning_state_counts.NEW_WARNING=12,
  r=>r.pullback_warning_timebox_shadow.warning_state_counts.PRIVATE_STATUS=1,
  r=>r.pullback_warning_timebox_shadow.new_warning_or_escalation_events=150
 ]){
  const r=original();change(r);assert.equal(go(r).status,'UNAVAILABLE');
 }
});
test('source date, Copenhagen clock and retention enforce no stale research as live',()=>{
 for(const [now,day] of [
  [new Date('2026-11-02T23:00:00Z'),DAY],
  [NOW,'2026-10-30'],
  [new Date('2026-10-31T08:00:00Z'),DAY]
 ]){
  const v=projectPullbackReport(bytes(original()),{now,expectedDay:day});
  assert.equal(v.status,'UNAVAILABLE');
 }
});
test('missing, old, and bad JSON fail closed with no fabricated numbers',()=>{
 for(const b of [Buffer.from(''),Buffer.from('{bad'),Buffer.alloc(8_000_001)]){
  const x=projectPullbackReport(b,{now:NOW,expectedDay:DAY});
  assert.equal(x.status,'UNAVAILABLE');assert.equal(x.horizons,null);
 }
});
test('site file builder on no source publishes unavailable, never crashes canonical site',async()=>{
 const tmp=await mkdtemp(join(tmpdir(),'pullback-site-'));
 try{
  const output=join(tmp,'dist','data','pullback-research.json');
  const r=await buildPublicPullback({repoRoot:tmp,output,now:NOW});
  assert.equal(r.status,'UNAVAILABLE');assert.equal(r.reason,'AWAITING_FIRST_QUALIFIED_RESEARCH_REPORT');
  assert.deepEqual(JSON.parse(await readFile(output,'utf8')),r);
 }finally{await rm(tmp,{recursive:true,force:true});}
});
test('site reads newest signed daily file once, no arbitrary path or older hidden signal',async()=>{
 const tmp=await mkdtemp(join(tmpdir(),'pullback-site-'));
 try{
  const p=resolve(tmp,'04_MARKET_LEARNING/handlekompas/research/rolling_14d/daily/2026/10/31/2026-10-31_ROLLING14.json');
  await mkdir(dirname(p),{recursive:true});await writeFile(p,bytes(original()));
  const output=join(tmp,'dist','data','pullback-research.json');
  const result=await buildPublicPullback({repoRoot:tmp,output,now:NOW});
  assert.equal(result.status,'RESEARCH_ONLY');
  assert.equal(result.new_warning_events,2);
  assert.equal(JSON.parse(await readFile(output,'utf8')).source_sha256,result.source_sha256);
 }finally{await rm(tmp,{recursive:true,force:true});}
});
