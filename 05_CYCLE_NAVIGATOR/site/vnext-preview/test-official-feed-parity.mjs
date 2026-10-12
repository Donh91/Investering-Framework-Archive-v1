import assert from 'node:assert/strict';
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
    current_public_projection: { public_issue_number: 29, forecast_week: '2026-W42' },
    latest_completed_score: {
      public_issue_number: 28, forecast_week: '2026-W41', price_range_score: 49.56
    }
  },
  public_scorecard: {
    contract: 'CN_PUBLIC_WEEKLY_SCORECARD_v1', public_issue_number: 28,
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
 assert.equal(o.weekly.state,'MISMATCH');
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
console.log('SUCCESS: 39 public-feed source parity/lineage/freshness/score/stages proof tests — NO SITE SIGNAL AUTHORITY.');

