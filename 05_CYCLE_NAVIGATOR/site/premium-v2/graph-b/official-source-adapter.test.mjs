import test from 'node:test';
import assert from 'node:assert/strict';
import {readOfficialGraphB,replayObservedUntil} from './official-source-adapter.mjs';

const start='2026-10-19T00:00:00Z',end='2026-10-26T00:00:00Z';
function fixture(){
 const hourly=['2026-10-19T01:00:00Z','2026-10-19T02:00:00Z','2026-10-19T04:00:00Z'];
 const score={day_1_2:{window_start_utc:start},day_3_4:{},day_5_7:{window_end_utc:end}};
 const rows=['day_1_2','day_3_4','day_5_7'].flatMap(w=>['BTC','ETH'].map(asset=>({
  asset,window:w,forecast_low:asset==='BTC'?78000:1900,forecast_high:asset==='BTC'?86000:2600
 })));
 return {
  schema:'CN_PUBLIC_SNAPSHOT_V2',public_series:{current_public_projection:{public_issue_number:30,forecast_week:'2026-W43'}},
  public_live_precision:{
   contract:'CN_PUBLIC_LIVE_PRICE_PRECISION_v1',public_issue_number:30,forecast_week:'2026-W43',
   freshness_sla_minutes:90,frozen_at_utc:'2026-10-19T05:19:14Z',window_scores:score,rows,
   daily_observations:{contract:'CN_PUBLIC_DAILY_OBSERVATIONS_v1',observed_through_utc:hourly[2]},
   hourly_price_path:{contract:'CN_PUBLIC_HOURLY_PRICE_PATH_v1',source:'HOURLY_SPOT_PASS_ONLY',
    semantics:'OBSERVED_HOURLY_CLOSE_NOT_A_PROSPECTIVE_FORECAST',public_issue_number:30,
    forecast_week:'2026-W43',observed_through_utc:hourly[2],
    BTC:hourly.map((t,i)=>({observed_at_utc:t,close:82000+i*100})),
    ETH:hourly.map((t,i)=>({observed_at_utc:t,close:2400+i*5}))},
   daily_price_path:{contract:'CN_FROZEN_DAILY_PRICE_PATH_v1',forecast_week:'2026-W43',
    BTC:{status:'UNAVAILABLE',points:[]},ETH:{status:'UNAVAILABLE',points:[]}}
  }
 };
}
const now='2026-10-19T04:20:00Z';
test('W43 genuine ranges+actual does NOT become an invented blue forecast',()=>{
 const m=readOfficialGraphB(fixture(),'BTC',{now_utc:now});
 assert.equal(m.source_status,'SOURCE_BOUNDED');
 assert.equal(m.forecast_status,'UNAVAILABLE');assert.deepEqual(m.forecast,[]);
 assert.equal(m.bands.length,3);assert.equal(m.hourly_observations.length,3);
 assert.equal(m.actual_segments.length,2); // exact 03:00 UTC missing gap
 assert.equal(m.live_freshness,'FRESH');
});
test('wrong issue/asset/clock/source provenance FAIL CLOSED',()=>{
 const v=fixture();v.public_live_precision.public_issue_number=31;
 assert.equal(readOfficialGraphB(v,'BTC',{now_utc:now}).source_reason,'PUBLIC_WEEK_OR_ISSUE_MISMATCH');
 assert.equal(readOfficialGraphB(fixture(),'SOL',{now_utc:now}).source_reason,'UNSUPPORTED_ASSET');
 assert.equal(readOfficialGraphB(fixture(),'ETH',{now_utc:'invalid'}).source_reason,'NOW_CLOCK_UNVERIFIED');
 const x=fixture();x.public_live_precision.hourly_price_path.source='MODEL_OUTPUT';
 assert.equal(readOfficialGraphB(x,'BTC',{now_utc:now}).source_reason,'HOURLY_SOURCE_PROVENANCE_INVALID');
});
test('duplicates, future points and non-hourly observations are rejected',()=>{
 const v=fixture();v.public_live_precision.hourly_price_path.BTC[1].observed_at_utc=
    v.public_live_precision.hourly_price_path.BTC[0].observed_at_utc;
 assert.equal(readOfficialGraphB(v,'BTC',{now_utc:now}).source_reason,'HOURLY_SAMPLES_UNVERIFIED');
 const n=fixture();n.public_live_precision.hourly_price_path.BTC[2].observed_at_utc='2026-10-19T04:30:00Z';
 assert.equal(readOfficialGraphB(n,'BTC',{now_utc:now}).source_reason,'HOURLY_SAMPLES_UNVERIFIED');
});
test('prospective PUBLISHED is only a structurally valid 7-day source path, never a generated line',()=>{
 const v=fixture();
 v.public_live_precision.daily_price_path.BTC={status:'PUBLISHED',points:Array.from({length:7},(_,i)=>({
  day:i+1,low:81000,high:84000,expected_close:82000+i*100
 }))};
 const m=readOfficialGraphB(v,'BTC',{now_utc:'2026-10-19T06:00:00Z'});
 assert.equal(m.forecast_status,'SOURCE_ISSUED');assert.equal(m.forecast.length,7);
 const bad=fixture();bad.public_live_precision.daily_price_path.BTC={status:'PUBLISHED',points:[{day:1,expected_close:82000}]};
 assert.equal(readOfficialGraphB(bad,'BTC',{now_utc:now}).forecast_status,'PUBLISHED_INVALID_FAIL_CLOSED');
 assert.equal(readOfficialGraphB(bad,'BTC',{now_utc:now}).forecast.length,0);
});
test('stale quotes NEVER claim current market price; replay never anticipates outcome',()=>{
 const m=readOfficialGraphB(fixture(),'BTC',{now_utc:'2026-10-19T08:00:00Z'});
 assert.equal(m.live_freshness,'STALE');assert.equal(m.is_current_quote,false);
 const r=replayObservedUntil(m,'2026-10-19T02:00:00Z');
 assert.equal(r.flat().length,2);assert.equal(m.hourly_observations.length,3);
});
test('mismatched release lineage fails closed',()=>{
 const m=readOfficialGraphB(fixture(),'ETH',{now_utc:now,publication_lineage:{
  contract:'CN_PUBLICATION_LINEAGE_RELEASE_RECEIPT_v1',
  forecast_week:'2026-W42',public_issue_number:30,source_to_public_equality:'PASS',last_observed_close_utc:'2026-10-19T04:00:00Z'
 }});
 assert.equal(m.source_reason,'PUBLIC_RELEASE_LINEAGE_MISMATCH');
});

test('post-cutoff or future-issued published daily path is rejected',()=>{
 const v=fixture();v.public_live_precision.daily_price_path.BTC={
   status:'PUBLISHED',points:Array.from({length:7},(_,i)=>({
    day:i+1,low:81000,high:84000,expected_close:82000+i*100
   }))
 };
 assert.equal(readOfficialGraphB(v,'BTC',{now_utc:'2026-10-19T04:20:00Z'}).forecast.length,0);
 v.public_live_precision.frozen_at_utc='2026-10-21T06:00:00Z';
 assert.equal(readOfficialGraphB(v,'BTC',{now_utc:'2026-10-21T07:00:00Z'}).forecast.length,0);
});
