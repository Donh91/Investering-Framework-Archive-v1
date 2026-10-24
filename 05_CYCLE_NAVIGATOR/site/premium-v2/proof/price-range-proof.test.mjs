import test from 'node:test';
import assert from 'node:assert/strict';
import {sourceOnlyPriceRangeProof} from './price-range-proof.mjs';
function make(){
 const windows={};const rows=[];
 for(const [id,s,e,h,phase,score] of [
 ['day_1_2','2026-10-19T00:00:00Z','2026-10-21T00:00:00Z',42,'COMPLETE',83.90],
 ['day_3_4','2026-10-21T00:00:00Z','2026-10-23T00:00:00Z',48,'COMPLETE',85.25],
 ['day_5_7','2026-10-23T00:00:00Z','2026-10-26T00:00:00Z',15,'LIVE',72.83]
 ]){
  windows[id]={phase,score_to_date:score,rows_scored:2,rows_total:2,
    observed_hours:h,expected_hours_final:id==='day_5_7'?72:h,
    coverage_complete_to_date:true,window_start_utc:s,window_end_utc:e,
    scoring_start_utc:id==='day_1_2'?'2026-10-19T06:00:00Z':s,
    frozen_sequence_text:'Original range evidence only'};
  rows.push({asset:'BTC',window:id,forecast_low:80000,forecast_high:85000});
  rows.push({asset:'ETH',window:id,forecast_low:2300,forecast_high:2520});
 }
 return {schema:'CN_PUBLIC_SNAPSHOT_V2',
  public_series:{current_public_projection:{public_issue_number:30,forecast_week:'2026-W43'}},
  public_live_precision:{contract:'CN_PUBLIC_LIVE_PRICE_PRECISION_v1',
   public_issue_number:30,forecast_week:'2026-W43',
   score_family:'PRICE_RANGE_PRECISION',formula:'70pct_containment_plus_30pct_jaccard',
   frozen_at_utc:'2026-10-19T05:19:14Z',scoring_valid_from_utc:'2026-10-19T06:00:00Z',
   live_as_of_utc:'2026-10-23T15:00:00Z',freshness_sla_minutes:90,
   window_scores:windows,rows}};
}
test('canonical W43 70/30 source produces two complete windows and one provisional LIVE',()=>{
 const v=sourceOnlyPriceRangeProof(make(),{now_utc:'2026-10-23T17:30:00Z'});
 assert.equal(v.status,'PROVISIONAL_SOURCE_READBACK');
 assert.deepEqual(v.window_items.map(i=>i.state),[
  'WINDOW_OBSERVED_COMPLETE','WINDOW_OBSERVED_COMPLETE','WINDOW_IN_PROGRESS']);
 assert.deepEqual(v.window_items.map(i=>i.source_reported_score_to_date),[83.9,85.25,72.83]);
 assert.equal(v.window_items[2].coverage_ratio,15/72);
 assert.equal(v.edge_score,null);assert.equal(v.proof_sealed,false);
 assert.equal(v.source_stale,true);
});
test('wrong issue or substituted score family rejected before display',()=>{
 const a=make();a.public_series.current_public_projection.public_issue_number=31;
 assert.equal(sourceOnlyPriceRangeProof(a,{now_utc:'2026-10-23T17:30:00Z'}).window_items.length,0);
 const b=make();b.public_live_precision.score_family='EDGE_BINARY';
 assert.equal(sourceOnlyPriceRangeProof(b,{now_utc:'2026-10-23T17:30:00Z'}).status,'UNAVAILABLE');
});
test('post-outcome issue timing cannot become retrospectively approved Proof',()=>{
 const a=make();a.public_live_precision.frozen_at_utc='2026-10-19T12:00:00Z';
 assert.equal(sourceOnlyPriceRangeProof(a,{now_utc:'2026-10-23T17:30:00Z'}).reason,
   'ISSUANCE_OR_OBSERVATION_CLOCK_UNVERIFIED');
});
test('incorrectly labeled complete or future observation is rejected',()=>{
 const a=make();a.public_live_precision.window_scores.day_1_2.observed_hours=41;
 assert.equal(sourceOnlyPriceRangeProof(a,{now_utc:'2026-10-23T17:30:00Z'}).reason,'MISLABELED_COMPLETE_WINDOW');
 const b=make();b.public_live_precision.live_as_of_utc='2026-10-24T00:00:00Z';
 assert.equal(sourceOnlyPriceRangeProof(b,{now_utc:'2026-10-23T17:30:00Z'}).reason,'ISSUANCE_OR_OBSERVATION_CLOCK_UNVERIFIED');
});
test('window scores not independently sealed and missing scored rows cannot be fabricated',()=>{
 const a=make();a.public_live_precision.window_scores.day_1_2.score_to_date=null;
 assert.equal(sourceOnlyPriceRangeProof(a,{now_utc:'2026-10-23T17:30:00Z'}).reason,'COMPLETE_SCORE_MISSING');
});

test('canonical NOT_STARTED third window retains valid earlier score and frozen ranges',()=>{
 const a=make(),w=a.public_live_precision.window_scores;
 a.public_live_precision.live_as_of_utc='2026-10-22T12:00:00Z';
 w.day_3_4.phase='LIVE';w.day_3_4.observed_hours=36;
 w.day_5_7.phase='NOT_STARTED';w.day_5_7.observed_hours=0;
 w.day_5_7.rows_scored=0;w.day_5_7.score_to_date=null;
 const v=sourceOnlyPriceRangeProof(a,{now_utc:'2026-10-22T12:30:00Z'});
 assert.equal(v.status,'PROVISIONAL_SOURCE_READBACK');
 assert.deepEqual(v.window_items.map(x=>x.state),[
  'WINDOW_OBSERVED_COMPLETE','WINDOW_IN_PROGRESS','PENDING']);
 assert.equal(v.window_items[0].source_reported_score_to_date,83.9);
 assert.equal(v.window_items[2].source_reported_score_to_date,null);
 assert.equal(v.window_items[2].original_ranges.length,2);
 assert.equal(v.proof_sealed,false);
});
test('NOT_STARTED cannot conceal any score, actual observation, or spoofed phase',()=>{
 const a=make(),w=a.public_live_precision.window_scores.day_5_7;
 w.phase='NOT_STARTED';w.observed_hours=0;w.rows_scored=0;
 a.public_live_precision.live_as_of_utc='2026-10-22T12:00:00Z';
 let v=sourceOnlyPriceRangeProof(a,{now_utc:'2026-10-22T12:30:00Z'});
 assert.equal(v.reason,'PENDING_HAS_OBSERVATIONS');
 w.score_to_date=null;w.observed_hours=1;
 v=sourceOnlyPriceRangeProof(a,{now_utc:'2026-10-22T12:30:00Z'});
 assert.equal(v.reason,'PENDING_HAS_OBSERVATIONS');
 w.observed_hours=0;w.phase='UNKNOWN_STARTED';
 v=sourceOnlyPriceRangeProof(a,{now_utc:'2026-10-22T12:30:00Z'});
 assert.equal(v.reason,'WINDOW_PHASE_INVALID');
});
