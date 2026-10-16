import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { inspectOfficialPublicFeeds } from './official-feed-parity.mjs';

// Synthetic shapes only, not simulated market predictions or public observations.
// Reproduce the current official public site/build-public.mjs output contracts
// including the W42 public issue #29 (machine issue 30) and W41 completed CN28.
const NOW = '2026-10-12T12:00:00Z';
const baseRows = ['day_1_2', 'day_3_4', 'day_5_7'].flatMap((window, ix) => [
  { asset: 'BTC', window, forecast_low: 80000 - ix * 1000, forecast_high: 87000,
    actual_low: 81000 - ix * 1000, actual_high: 86000, score: 60 - ix },
  { asset: 'ETH', window, forecast_low: 2300, forecast_high: 2700,
    actual_low: 2360 - ix * 10, actual_high: 2670, score: 40 - ix }
]);
const latest = {
  schema: 'CN_PUBLIC_SNAPSHOT_V2',
  generated_at: '2026-10-12T11:40:00Z',
  pointer: { iso_year: 2026, iso_week: 42, issue_number: 30, status: 'DEGRADED' },
  package: {
    issue_number: 30, status: 'DEGRADED',
    forecast_freeze: {
      btc_range_low: 78000, btc_range_high: 88000,
      eth_range_low: 2260, eth_range_high: 2720
    }
  },
  public_series: {
    contract: 'CN_PUBLIC_SERIES_INDEX_v1',
    current_public_projection: { public_issue_number: 29, forecast_week: '2026-W42' },
    latest_completed_score: {
      public_issue_number: 28, forecast_week: '2026-W41', price_range_score: 49.56, status: 'FINAL_DUAL_TRACK'
    }
  },
  public_scorecard: {
    contract: 'CN_PUBLIC_WEEKLY_SCORECARD_v1', status: 'FINAL_DUAL_TRACK', public_issue_number: 28,
    forecast_week: '2026-W41', market_structure_precision: null, combined_score: null,
    price_range_precision: {
      formula: '70pct_containment_plus_30pct_jaccard',
      score: 49.56, btc_score: 62.94, eth_score: 36.17,
      actuals_hourly_coverage: 168, rows: baseRows,
      intraday_window_scores: {day_1_2: 79.59, day_3_4: 36.25, day_5_7: 32.83}
    }
  }
};
const compass = {
  contract: 'PUBLIC_COMPASS_PROJECTION_v1',
  compass_id: 'CMP-TEST-20261012', issued_at_utc: '2026-10-12T09:35:11Z', data_status: 'OK',
  weekly_context: {status: 'ALIGNED', forecast_week: '2026-W42', public_issue_number: 29},
  action_now: 'HOLD_WAIT',
  protection_tracker: {
    pullback_risk_state: 'BUILDING', distribution_risk: 'UNKNOWN', reentry_state: 'INACTIVE'
  },
  sell_assessment: {state:'UNAVAILABLE'}
};
const read = (l=latest,c=compass,opts={})=>inspectOfficialPublicFeeds(l,c,{nowUtc:NOW,...opts});
const mutate = (fun)=>{
  const l=structuredClone(latest),c=structuredClone(compass);
  fun(l,c);
  return read(l,c);
};
const it=(desc,callback)=>{try{callback();console.log('PASS',desc)}catch(err){console.error('FAIL',desc);throw err}};

it('real public CN #29 and machine #30 stay distinct; W42 ranges source-bound',()=>{
 const o=read();
 assert.equal(o.weekly.public_issue_number,29);
 assert.equal(o.weekly.machine_issue_number,30);
 assert.equal(o.weekly.forecast_week,'2026-W42');
 assert.equal(o.weekly.state,'DEGRADED');
 assert.deepEqual(o.weekly.btc_range,{low:78000,high:88000});
 assert.deepEqual(o.weekly.eth_range,{low:2260,high:2720});
 assert.equal(o.delivery_health,'FRESH');
});
it('last scored CN28 W41 is separate from W42; never legacy cross-era blend',()=>{
 const o=read();
 assert.equal(o.completed_score.state,'FINAL_PUBLIC_SCORECARD');
 assert.equal(o.completed_score.public_issue_number,28);
 assert.equal(o.completed_score.price_range_precision,49.56);
 assert.equal(o.completed_score.rows.length,6);
 assert.equal(o.completed_score.market_structure_precision,null);
 assert.equal(o.completed_score.combined_score,null);
 assert.match(o.completed_score.proof_state,/NOT_INDEPENDENTLY_SEALED/);
});
it('fresh official HOLD_WAIT survives without SELL from pullback watch',()=>{
 const o=read();
 assert.equal(o.compass.state,'FRESH');
 assert.equal(o.compass.action_now,'HOLD_WAIT');
 assert.equal(o.compass.pullback_risk_state,'BUILDING');
 assert.equal(o.compass.sell_assessment_state,'UNAVAILABLE');
 assert.equal(o.compass.distribution_risk,'UNKNOWN');
 assert.equal(o.compass.reentry_state,'INACTIVE');
 assert.equal(o.compass.permit_path_live_gates,true);
});
it('future W42 binary Edge cannot be scored from current site feeds',()=>{
 const o=read();
 assert.equal(o.edge_claims.status,'NO_AUTHENTICATED_FEED');
 assert.equal(o.edge_claims.score,null);
});
it('missing/mismatched root contract fails closed',()=>{
 assert.equal(read({schema:'OTHER'},compass).weekly.state,'UNAVAILABLE');
 assert.equal(read(latest,{contract:'OTHER'}).compass.action_now,'UNAVAILABLE');
});
it('untrusted public series identity fails closed before consuming CN, Compass or scores',()=>{
 for(const contract of [undefined, null, 'CN_PUBLIC_SERIES_INDEX_v0', 'CN_PUBLIC_SERIES_INDEX_v2']){
   const o=mutate(l=>{l.public_series.contract=contract});
   assert.equal(o.weekly.state,'UNAVAILABLE');
   assert.equal(o.compass.action_now,'UNAVAILABLE');
   assert.equal(o.completed_score.price_range_precision,null);
   assert.equal(o.compass.permit_path_live_gates,false);
   assert.equal(o.delivery_health,'UNAVAILABLE');
 }
});
it('missing weekly public issue cannot default to machine identity',()=>{
 const o=mutate(l=>{delete l.public_series.current_public_projection.public_issue_number});
 assert.equal(o.weekly.state,'MISMATCH');
 assert.equal(o.weekly.public_issue_number,null);
});
it('different public week than weekly pointer fails closed',()=>{
 const o=mutate(l=>{l.public_series.current_public_projection.forecast_week='2026-W41'});
 assert.equal(o.weekly.state,'MISMATCH');
 assert.equal(o.compass.permit_path_live_gates,false);
});
it('weekly machine number mismatch does not reclassify public identity',()=>{
 const o=mutate(l=>{l.pointer.issue_number=29});
 assert.equal(o.weekly.state,'MISMATCH');
});
it('a degraded weekly forecast is never reported as healthy',()=>{
 assert.equal(read().weekly.state,'DEGRADED');
});
it('explicit missing numeric weekly range stays null',()=>{
 const o=mutate(l=>{l.package.forecast_freeze.eth_range_high=null});
 assert.equal(o.weekly.eth_range,null);
 assert.deepEqual(o.weekly.btc_range,{low:78000,high:88000});
});
it('weekly/Compass ID mismatch blocks PATH without overwriting independently valid NOW',()=>{
 const o=mutate((l,c)=>{c.weekly_context.public_issue_number=28});
 assert.equal(o.compass.action_now,'HOLD_WAIT');
 assert.equal(o.compass.permit_path_live_gates,false);
 assert.notEqual(o.compass.weekly_alignment,'ALIGNED');
});
it('explicit MISMATCH in Compass source blocks PATH',()=>{
 const o=mutate((l,c)=>{c.weekly_context.status='MISMATCH'});
 assert.equal(o.compass.weekly_alignment,'MISMATCH');
 assert.equal(o.compass.permit_path_live_gates,false);
});
it('missing alignment never gets guessed from equal issue IDs',()=>{
 const o=mutate((l,c)=>{c.weekly_context.status='UNVERIFIED'});
 assert.equal(o.compass.permit_path_live_gates,false);
});
it('stale Compass action, protection, SELL and reentry all fail closed',()=>{
 const o=mutate((l,c)=>{c.issued_at_utc='2026-10-10T00:00:00Z';c.action_now='BUY';c.sell_assessment.state='SELL'});
 assert.equal(o.compass.state,'STALE');
 assert.equal(o.compass.action_now,'UNAVAILABLE');
 assert.equal(o.compass.sell_assessment_state,'UNAVAILABLE');
 assert.equal(o.compass.pullback_risk_state,'UNAVAILABLE');
 assert.equal(o.compass.permit_path_live_gates,false);
});
it('future Compass timestamp cannot be treated as fresh',()=>{
 const o=mutate((l,c)=>{c.issued_at_utc='2026-10-13T00:00:00Z'});
 assert.equal(o.compass.state,'UNAVAILABLE');
 assert.equal(o.compass.action_now,'UNAVAILABLE');
});
it('stale site delivery reports STALE independently of weekly freeze validity',()=>{
 const o=mutate(l=>{l.generated_at='2026-10-09T00:00:00Z'});
 assert.equal(o.delivery_health,'STALE');
 assert.equal(o.weekly.state,'DEGRADED');
});
it('stale delivery cannot preserve an apparently fresh NOW action',()=>{
 const o=mutate(l=>{l.generated_at='2026-10-09T00:00:00Z'});
 assert.equal(o.delivery_health,'STALE');
 assert.equal(o.compass.action_now,'UNAVAILABLE');
 assert.equal(o.compass.pullback_risk_state,'UNAVAILABLE');
 assert.equal(o.compass.permit_path_live_gates,false);
});
it('public Compass time after its builder snapshot cannot be presented as live',()=>{
 const o=mutate((l,c)=>{
   l.generated_at='2026-10-12T09:05:00Z';
   c.issued_at_utc='2026-10-12T09:35:11Z';
 });
 assert.equal(o.compass.action_now,'UNAVAILABLE');
 assert.equal(o.compass.permit_path_live_gates,false);
});
it('timestamps without explicit timezone cannot bypass UTC comparison',()=>{
 const o=mutate((l,c)=>{c.issued_at_utc='2026-10-12T09:35:11'});
 assert.equal(o.compass.action_now,'UNAVAILABLE');
 assert.equal(o.compass.state,'UNAVAILABLE');
});
it('scorecard different public number cannot be credited',()=>{
 const o=mutate(l=>{l.public_scorecard.public_issue_number=27});
 assert.equal(o.completed_score.state,'MISMATCH_OR_INCOMPLETE');
 assert.equal(o.completed_score.price_range_precision,null);
});
it('scorecard different forecast week cannot be credited',()=>{
 const o=mutate(l=>{l.public_scorecard.forecast_week='2026-W40'});
 assert.equal(o.completed_score.state,'MISMATCH_OR_INCOMPLETE');
});
it('public index and scorecard mismatched numeric values fail',()=>{
 const o=mutate(l=>{l.public_series.latest_completed_score.price_range_score=100});
 assert.equal(o.completed_score.state,'MISMATCH_OR_INCOMPLETE');
});
it('incomplete 167-hour observation never inherits final score',()=>{
 const o=mutate(l=>{l.public_scorecard.price_range_precision.actuals_hourly_coverage=167});
 assert.equal(o.completed_score.state,'MISMATCH_OR_INCOMPLETE');
});
it('missing BTC/ETH price window invalidates complete chart instead of manufacturing a bar',()=>{
 const o=mutate(l=>{l.public_scorecard.price_range_precision.rows.pop()});
 assert.equal(o.completed_score.state,'MISMATCH_OR_INCOMPLETE');
});
it('duplicate interval cannot count twice',()=>{
 const o=mutate(l=>{l.public_scorecard.price_range_precision.rows[5]=structuredClone(l.public_scorecard.price_range_precision.rows[4])});
 assert.equal(o.completed_score.state,'MISMATCH_OR_INCOMPLETE');
});
it('CN27+ structure or blended score may not reappear numerically',()=>{
 const o=mutate(l=>{l.public_scorecard.market_structure_precision=92});
 assert.equal(o.completed_score.state,'MISMATCH_OR_INCOMPLETE');
});
it('wrong price scoring formula cannot claim continuity',()=>{
 const o=mutate(l=>{l.public_scorecard.price_range_precision.formula='100pct_containment'});
 assert.equal(o.completed_score.state,'MISMATCH_OR_INCOMPLETE');
});
it('a scored current W42 week is not eligible as completed forecast',()=>{
 const o=mutate(l=>{l.public_scorecard.public_issue_number=29;l.public_series.latest_completed_score.public_issue_number=29});
 assert.equal(o.completed_score.state,'MISMATCH_OR_INCOMPLETE');
});
it('missing source does not fabricate permission or score',()=>{
 const o=read({schema:'CN_PUBLIC_SNAPSHOT_V2'},compass);
 assert.equal(o.weekly.state,'UNAVAILABLE');
 assert.equal(o.completed_score.state,'UNAVAILABLE');
 assert.equal(o.compass.permit_path_live_gates,false);
});
it('invalid time policy rejects unsafe freshness inputs',()=>{
 assert.throws(()=>read(latest,compass,{nowUtc:'yesterday'}),/INVALID_READBACK_CLOCK_POLICY/);
 assert.throws(()=>read(latest,compass,{compassMaxAgeHours:-1}),/INVALID_READBACK_CLOCK_POLICY/);
});
const validW42 = (l,c) => {
 c.protection_tracker.contract='COMPASS_PROTECTION_TRACKER_v1';
 c.protection_tracker.authority={new_market_classifier:false,portfolio_execution:false};
 c.protection_tracker.pullback_risk_state='ELEVATED';
 c.protection_tracker.public_explanation={
   contract:'CN_PUBLIC_PROTECTION_COPY_v1',forecast_week:'2026-W42',
   risk_state:'ELEVATED',onset_start_utc:null,onset_end_utc:null
 };
 c.bull_bear_scale={
   contract:'OFFICIAL_COMPASS_BULL_BEAR_DISPLAY_v1',
   semantics:'EVIDENCE_BALANCE_NOT_PROBABILITY',
   resolution:'COARSE_CATEGORICAL_DIRECTION',
   mapping_version:'DIRECTION_ONLY_COARSE_v1',
   owner:'OFFICIAL_COMPASS',
   source_of_truth_contract:'MARKET_WEATHER_SOURCE_OF_TRUTH_v1',
   authority:{site_synthesis_allowed:false,new_market_classifier:false,probability_model:false,portfolio_execution:false},
   horizons:{'1_3d':{status:'OK',bull:5,bear:5,bias:'NEUTRAL'}}
 };
};
it('live public feed transfers W42 official possible WEEK with no precise onset/SELL',()=>{
 const o=mutate(validW42);
 assert.equal(o.compass.state,'FRESH');
 assert.equal(o.compass.action_now,'HOLD_WAIT');
 assert.equal(o.compass.pullback_window.window_kind,'WEEK_ONLY');
 assert.equal(o.compass.pullback_window.window_start_utc,null);
 assert.equal(o.compass.pullback_window.window_end_utc,null);
 assert.match(o.compass.pullback_window.headline,/uge 42.*ingen præcis ETA/);
 assert.equal(o.compass.bull_bear_1_3d.bull,5);
 assert.equal(o.compass.bull_bear_1_3d.bear,5);
 assert.equal(o.compass.sell_assessment_state,'UNAVAILABLE');
});
it('stale weekly delivery blocks risk ETA and Bull/Bear even when Compass object looks fresh',()=>{
 const o=mutate((l,c)=>{validW42(l,c);l.generated_at='2026-10-09T00:00:00Z'});
 assert.equal(o.compass.pullback_window,null);
 assert.equal(o.compass.bull_bear_1_3d,null);
 assert.equal(o.compass.action_now,'UNAVAILABLE');
});
it('misaligned public CN week blocks risk ETA but does not rewrite Compass action',()=>{
 const o=mutate((l,c)=>{validW42(l,c);c.weekly_context.public_issue_number=28});
 assert.equal(o.compass.pullback_window,null);
 assert.equal(o.compass.permit_path_live_gates,false);
 assert.equal(o.compass.action_now,'HOLD_WAIT');
});
it('malformed governed W42 window does not create dates',()=>{
 const o=mutate((l,c)=>{validW42(l,c);c.protection_tracker.public_explanation.onset_start_utc='2026-10-14T02:00:00Z'});
 assert.equal(o.compass.pullback_window.window_kind,'INVALID_DATE_PAIR');
 assert.equal(o.compass.pullback_window.window_start_utc,null);
});
it('legacy or incomplete protection contract yields unavailable ETA but no fabricated action',()=>{
 const o=mutate((l,c)=>{validW42(l,c);c.protection_tracker.contract='SOME_UNKNOWN_OWNER'});
 assert.equal(o.compass.pullback_window,null);
 assert.equal(o.compass.action_now,'HOLD_WAIT');
});
it('W42 official NORMAL must remain no active warning, not a timed pullback alarm',()=>{
 const o=mutate((l,c)=>{
   validW42(l,c);
   c.protection_tracker.pullback_risk_state='NORMAL';
   c.protection_tracker.public_explanation.risk_state='NORMAL';
 });
 assert.equal(o.compass.pullback_risk_state,'NORMAL');
 assert.equal(o.compass.pullback_window.window_kind,'NO_ACTIVE_WATCH');
 assert.match(o.compass.pullback_window.headline,/Ingen aktiv pullback-watch/);
 assert.equal(o.compass.pullback_window.window_start_utc,null);
 assert.equal(o.compass.sell_assessment_state,'UNAVAILABLE');
});
it('fresh aligned Official Compass supplies descriptive staged risk without implicit imminence',()=>{
 const o=mutate(validW42);
 assert.equal(o.compass.pullback_stage.source_risk_state,'ELEVATED');
 assert.equal(o.compass.pullback_stage.ordinal_risk_class,2);
 assert.match(o.compass.pullback_stage.stage_label,/Forhøjet/);
 assert.match(o.compass.pullback_stage.proximity_label,/ikke dokumenteret/);
 assert.equal(o.compass.pullback_stage.evidence_quality,'Evidenskvalitet ukendt');
 assert.equal(o.compass.pullback_stage.quality_semantics,'EVIDENCE_QUALITY_NOT_PROBABILITY');
 assert.equal(o.compass.pullback_stage.sell_permission,false);
 assert.equal(o.compass.pullback_stage.confirmed_market_decline,false);
});
it('stale/misaligned official weekly context cannot expose Pullback stage',()=>{
 for (const alter of [
  (l,c)=>{validW42(l,c);l.generated_at='2026-10-10T00:00:00Z'},
  (l,c)=>{validW42(l,c);c.weekly_context.status='MISMATCH'},
  (l,c)=>{validW42(l,c);c.data_status='DEGRADED'}
 ]) {
  const o=mutate(alter);
  assert.equal(o.compass.pullback_stage,null);
 }
});
it('valid Normal source is quiet and cannot be converted into automatic crash alert',()=>{
 const o=mutate((l,c)=>{validW42(l,c);c.protection_tracker.pullback_risk_state='NORMAL';c.protection_tracker.public_explanation.risk_state='NORMAL'});
 assert.equal(o.compass.pullback_stage.source_risk_state,'NORMAL');
 assert.equal(o.compass.pullback_stage.ordinal_risk_class,0);
 assert.equal(o.compass.pullback_window.window_kind,'NO_ACTIVE_WATCH');
 assert.equal(o.compass.pullback_stage.sell_permission,false);
});
it('fresh official Pullback investor view rejects fake 1–10 odds and alt damage while preserving 2–3w',()=>{
 const o=mutate(validW42);
 const p=o.compass.pullback_investor_facts;
 assert.equal(p.authority,'SOURCE_ONLY_UI');
 assert.equal(p.risk_state,'ELEVATED');
 assert.equal(p.items.length,10);
 assert.equal(p.items.find(x=>x.id==='likelihood').source,'NOT_CALIBRATED');
 assert.equal(p.items.find(x=>x.id==='alt_impact').source,'UNQUANTIFIED');
 assert.equal(p.items.find(x=>x.id==='duration').source,'UNASSESSED');
 assert.match(p.items.find(x=>x.id==='eta').value,/uge 42.*ingen præcis ETA/);
 assert.equal(o.compass.sell_assessment_state,'UNAVAILABLE');
});
it('stale, misaligned or invalid typed window never promotes investor drilldown',()=>{
 for(const alter of [
  (l,c)=>{validW42(l,c);l.generated_at='2026-10-09T00:00:00Z';},
  (l,c)=>{validW42(l,c);c.weekly_context.public_issue_number=28;},
  (l,c)=>{validW42(l,c);c.protection_tracker.public_explanation.onset_start_utc='2026-10-14T03:00:00Z';}
 ]) {
  const o=mutate(alter);
  assert.equal(o.compass.pullback_investor_facts,null);
 }
});
const pathOwnerFixture=(l,c)=>{
 l.package.market_state='Completed W41 was a BTC-led advance in USD, relative rotation not confirmed.';
 l.package.rotation_ladder=[
  {segment:'BTC',status:'Led the W41 USD advance'},
  {segment:'ETH',status:'ETH/BTC relative stabilization not confirmed'},
  {segment:'Large caps',status:'Unconfirmed'},
  {segment:'Midcaps',status:'Unconfirmed'},
  {segment:'Small caps',status:'Unconfirmed'},
  {segment:'Microcaps',status:'Unconfirmed'}
 ];
 l.package.altseason_countdown=[
  {phase:'30d alt participation: active watch, broad not confirmed',window:'Now / W42'},
  {phase:'ETH-relative stabilization: not confirmed',window:'W42-next 3 weeks, conditional'},
  {phase:'Large-cap to midcap transmission: not confirmed',window:'Next 2-3 weeks, conditional'},
  {phase:'Small- and microcap transmission: not confirmed',window:'No supported ETA'},
  {phase:'Broad, multi-horizon altseason: paused',window:'No supported ETA'}
 ];
 l.package.decision_projection={
  next_2_3w:{direction:'MIXED',summary:'Selective rotation, evidence still mixed.'},
  weeks_4_8:{direction:'UNAVAILABLE',summary:'No supported 4-8w call.'}
 };
 c.capitalization_ladder=[
  {segment:'BTC',action:'HOLD',status:'HOLD',eta:'now'},
  {segment:'ETH',action:'HOLD',status:'HOLD',eta:'now'},
  {segment:'LARGE_CAPS',action:'WAIT',status:'WAIT',eta:'conditional'},
  {segment:'MID_CAPS',action:'WAIT',status:'WAIT',eta:'conditional'},
  {segment:'SMALL_CAPS',action:'WAIT',status:'WAIT',eta:'no fixed ETA'},
  {segment:'MICROCAPS',action:'HARD_WAIT',status:'HARD_WAIT',eta:'no fixed ETA'},
  {segment:'MEMES',action:'UNAVAILABLE',status:'UNAVAILABLE',eta:null}
 ];
};
it('existing public feeds provide real source-joined PATH, not forecast a phased hop',()=>{
 const o=mutate(pathOwnerFixture);
 assert.equal(o.path.state,'SOURCE_BOUND');
 assert.equal(o.path.source_issue,29);
 assert.equal(o.path.source_week,'2026-W42');
 assert.equal(o.path.current_checkpoint.key,'BTC');
 assert.equal(o.path.current_checkpoint.status,'FROZEN_WEEK_REFERENCE');
 assert.equal(o.path.next_checkpoint.key,'ETH');
 assert.equal(o.path.next_checkpoint.status,'UNCONFIRMED');
 assert.equal(o.path.phase_eta,'Ingen verificeret ETA');
 assert.equal(o.path.full_phases.length,10);
 assert.equal(o.path.rotation.length,7);
 assert.equal(o.path.rotation[6].action,'UNAVAILABLE');
 assert.equal(o.path.altseason.status,'WATCH_ONLY');
});
it('missing tier source means PATH unavailable, NOT a fabricated live phase',()=>{
 const o=mutate((l,c)=>{pathOwnerFixture(l,c);delete c.capitalization_ladder;});
 assert.equal(o.path.state,'UNAVAILABLE');
 assert.equal(o.compass.action_now,'HOLD_WAIT');
});
it('misaligned or stale public Compass blocks PATH completely',()=>{
 for(const alter of [
  (l,c)=>{pathOwnerFixture(l,c);c.weekly_context.status='MISMATCH';},
  (l,c)=>{pathOwnerFixture(l,c);c.weekly_context.public_issue_number=28;},
  (l,c)=>{pathOwnerFixture(l,c);l.generated_at='2026-10-09T00:00:00Z';}
 ]){
  const o=mutate(alter);
  assert.equal(o.path.state,'UNAVAILABLE');
  assert.equal(o.path.current_checkpoint,null);
  assert.equal(o.path.full_phases.length,0);
 }
});
it('PHASE user-visible NEXT gate does not claim altseason or ETA from 30d shadow',()=>{
 const o=mutate((l,c)=>{pathOwnerFixture(l,c);l.package.altseason_countdown[0].phase='30d alt participation: ALTCOIN_SEASON 95';});
 assert.equal(o.path.state,'SOURCE_BOUND');
 assert.equal(o.path.altseason.status,'WATCH_ONLY');
 assert.equal(o.path.phase_eta,'Ingen verificeret ETA');
 assert.equal(o.path.full_phases[5].status,'UNCONFIRMED');
});

it('pending public scorecard cannot be promoted to FINAL by complete-looking numeric rows',()=>{
 const o=mutate(l=>{l.public_scorecard.status='PENDING';l.public_series.latest_completed_score.status='PENDING';});
 assert.equal(o.completed_score.state,'MISMATCH_OR_INCOMPLETE');
 assert.equal(o.completed_score.price_range_precision,null);
});
it('final scorecard with nonfinal public index cannot be presented as matured',()=>{
 const o=mutate(l=>{l.public_series.latest_completed_score.status='PENDING';});
 assert.equal(o.completed_score.state,'MISMATCH_OR_INCOMPLETE');
});
it('mismatched scorecard and public index maturity attestations fail closed',()=>{
 const o=mutate(l=>{l.public_scorecard.status='FINAL_UNVERIFIED';});
 assert.equal(o.completed_score.state,'MISMATCH_OR_INCOMPLETE');
});

// Real canonical SOURCE CONSUMER proof, not a frozen W42 synthetic test.
// Builds ONLY local ephemeral site/dist, never deploys or writes a producer.
// CI checks the PR merge checkout against the actual public owner files at
// test time, including later W43+ source rotations without hard-coded prices.
it('actual public build readback agrees with canonical weekly, Compass and matured score owners',()=>{
 const root=resolve(dirname(fileURLToPath(import.meta.url)),'../../..');
 const site=resolve(root,'05_CYCLE_NAVIGATOR/site');
 const json=(path)=>JSON.parse(readFileSync(resolve(root,path),'utf8'));
 const pointer=json('05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json');
 const index=json('05_CYCLE_NAVIGATOR/public_series/CN_PUBLIC_SERIES_INDEX.json');
 const publicCompass=json('04_MARKET_LEARNING/handlekompas/official/PUBLIC_LATEST_COMPASS.json');
 assert.equal(pointer.contract,'CYCLE_NAVIGATOR_DELIVERY_POINTER_v1');
 assert.equal(index.contract,'CN_PUBLIC_SERIES_INDEX_v1');
 assert.equal(publicCompass.contract,'PUBLIC_COMPASS_LATEST_POINTER_v1');
 assert.ok(publicCompass.public_projection_path.startsWith('04_MARKET_LEARNING/handlekompas/official/public/'));
 assert.ok(!publicCompass.public_projection_path.includes('..'));
 const projectionBytes=readFileSync(resolve(root,publicCompass.public_projection_path));
 assert.equal(createHash('sha256').update(projectionBytes).digest('hex'),publicCompass.public_projection_content_sha256);
 execFileSync(process.execPath,[resolve(site,'build-public.mjs')],{
   cwd:root,encoding:'utf8',timeout:60000,maxBuffer:1024*1024
 });
 const liveLatest=json('05_CYCLE_NAVIGATOR/site/dist/data/latest.json');
 const liveCompass=json('05_CYCLE_NAVIGATOR/site/dist/data/compass.json');
 assert.equal(liveLatest.schema,'CN_PUBLIC_SNAPSHOT_V2');
 assert.equal(liveLatest.public_series?.contract,index.contract);
 assert.equal(liveCompass.contract,'PUBLIC_COMPASS_PROJECTION_v1');
 assert.equal(liveLatest.pointer.iso_week,pointer.iso_week);
 assert.equal(liveLatest.pointer.iso_year,pointer.iso_year);
 assert.equal(liveLatest.pointer.issue_number,pointer.issue_number);
 assert.equal(liveLatest.package.issue_number,pointer.issue_number);
 assert.equal(liveLatest.package.status,pointer.status);
 assert.equal(liveLatest.public_series.current_public_projection.public_issue_number,
   index.current_public_projection.public_issue_number);
 assert.equal(liveLatest.public_series.current_public_projection.forecast_week,
   index.current_public_projection.forecast_week);
 assert.equal(liveCompass.compass_id,publicCompass.compass_id);
 assert.equal(liveCompass.issued_at_utc,publicCompass.issued_at_utc);
 assert.equal(liveLatest.public_scorecard.public_issue_number,index.latest_completed_score.public_issue_number);
 assert.equal(liveLatest.public_scorecard.forecast_week,index.latest_completed_score.forecast_week);
 assert.equal(liveLatest.public_scorecard.status,index.latest_completed_score.status);
 const now=new Date().toISOString();
 const actual=inspectOfficialPublicFeeds(liveLatest,liveCompass,{nowUtc:now});
 assert.equal(actual.delivery_health,'FRESH');
 assert.equal(actual.weekly.public_issue_number,index.current_public_projection.public_issue_number);
 assert.equal(actual.weekly.machine_issue_number,pointer.issue_number);
 assert.equal(actual.weekly.forecast_week,index.current_public_projection.forecast_week);
 assert.equal(actual.weekly.state,pointer.status==='DEGRADED'?'DEGRADED':'OK');
 assert.equal(actual.completed_score.state,'FINAL_PUBLIC_SCORECARD');
 assert.equal(actual.completed_score.forecast_week,index.latest_completed_score.forecast_week);
 assert.equal(actual.completed_score.price_range_precision,index.latest_completed_score.price_range_score);
 assert.equal(actual.completed_score.market_structure_precision,null);
 assert.equal(actual.completed_score.combined_score,null);
 assert.match(actual.completed_score.proof_state,/NOT_INDEPENDENTLY_SEALED/);
 assert.equal(actual.edge_claims.score,null);
 assert.equal(actual.edge_claims.status,'NO_AUTHENTICATED_FEED');
 if(actual.compass.state==='FRESH'){
   assert.equal(actual.compass.action_now,liveCompass.action_now);
   assert.equal(actual.compass.weekly_alignment,'ALIGNED');
   assert.equal(actual.compass.permit_path_live_gates,true);
 }else{
   assert.equal(actual.compass.action_now,'UNAVAILABLE');
   assert.equal(actual.compass.permit_path_live_gates,false);
 }
 // Adversarial mutations to the *real built* readback, not fabricated prices.
 const wrongContract=structuredClone(liveLatest);
 wrongContract.public_series.contract='CN_PUBLIC_SERIES_INDEX_v0';
 const wrongContractResult=inspectOfficialPublicFeeds(wrongContract,liveCompass,{nowUtc:now});
 assert.equal(wrongContractResult.weekly.state,'UNAVAILABLE');
 assert.equal(wrongContractResult.compass.action_now,'UNAVAILABLE');
 assert.equal(wrongContractResult.completed_score.price_range_precision,null);
 const wrongWeek=structuredClone(liveLatest);
 wrongWeek.public_series.current_public_projection.forecast_week='1900-W01';
 const mismatched=inspectOfficialPublicFeeds(wrongWeek,liveCompass,{nowUtc:now});
 assert.equal(mismatched.weekly.state,'MISMATCH');
 assert.equal(mismatched.compass.permit_path_live_gates,false);
 const pending=structuredClone(liveLatest);
 pending.public_series.latest_completed_score.status='PENDING';
 assert.equal(inspectOfficialPublicFeeds(pending,liveCompass,{nowUtc:now}).completed_score.state,'MISMATCH_OR_INCOMPLETE');
 const partial=structuredClone(liveLatest);
 partial.public_scorecard.price_range_precision.actuals_hourly_coverage=167;
 assert.equal(inspectOfficialPublicFeeds(partial,liveCompass,{nowUtc:now}).completed_score.state,'MISMATCH_OR_INCOMPLETE');
 const stale=structuredClone(liveLatest);
 stale.generated_at='2026-01-01T00:00:00Z';
 const staleResult=inspectOfficialPublicFeeds(stale,liveCompass,{nowUtc:now});
 assert.equal(staleResult.delivery_health,'STALE');
 assert.equal(staleResult.compass.action_now,'UNAVAILABLE');
 assert.equal(staleResult.compass.permit_path_live_gates,false);
 for(const obj of [liveLatest,liveCompass]){
   const forbidden=/^(?:api_?key|private_?key|access_?token|refresh_?token|raw_?payload|restricted_?provider_?values)$/i;
   const scan=(node)=>{if(!node||typeof node!=='object')return;
     for(const [key,value] of Object.entries(node)){
       assert.ok(!forbidden.test(key),'Restricted public output key: '+key);
       scan(value);
     }
   };
   scan(obj);
 }
 console.log('REAL_SOURCE_BUILD_PARITY_VERIFIED: '+actual.weekly.forecast_week+
   ' public #'+actual.weekly.public_issue_number+' machine #'+actual.weekly.machine_issue_number+
   ' Compass '+actual.compass.state+' score '+actual.completed_score.forecast_week+
   '; local build only, not Pages or native Safari.');
});

console.log('SUCCESS: synthetic + actual canonical public-build source parity, maturity, freshness, risk and PATH gates — NO SITE SIGNAL AUTHORITY.');

