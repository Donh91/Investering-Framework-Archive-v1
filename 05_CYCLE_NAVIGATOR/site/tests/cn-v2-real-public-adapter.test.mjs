/**
 * CN SITE v2 pre-design contract. Runs on the EXACT generated public bundle,
 * not a synthetic screenshot fixture. Does NOT authorize redesign release.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {runInNewContext} from 'node:vm';
import {resolve,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {readOfficialGraphB,replayObservedUntil} from '../premium-v2/graph-b/official-source-adapter.mjs';

const site=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const repo=resolve(site,'../..');
const json=p=>JSON.parse(readFileSync(p,'utf8'));
const latestPath=resolve(site,'dist/data/latest.json');
const lineagePath=resolve(site,'dist/data/publication-lineage.json');
assert.ok(existsSync(latestPath),'BUILD_REAL_PUBLIC_LATEST_FIRST');
assert.ok(existsSync(lineagePath),'BUILD_AND_CHECK_REAL_PUBLIC_LINEAGE_FIRST');
const latest=json(latestPath),lineage=json(lineagePath);
const live=latest.public_live_precision;
const now=new Date(Math.max(Date.now(),Date.parse(latest.generated_at)||0)).toISOString();
const untrustedCopy=()=>structuredClone(latest);

test('v2 DEPLOYED MODULE: redesigned site can import the very same validated source logic',async()=>{
 const publicEntry=resolve(site,'dist/cn-site-v2-source.mjs');
 const implementation=resolve(site,'dist/source-adapter/official-source-adapter.mjs');
 assert.ok(existsSync(publicEntry),'PUBLIC_ADAPTER_ENTRYPOINT_NOT_PACKAGED');
 assert.ok(existsSync(implementation),'PUBLIC_ADAPTER_IMPLEMENTATION_NOT_PACKAGED');
 const shipped=await import(pathToFileURL(publicEntry).href);
 assert.equal(typeof shipped.readOfficialGraphB,'function');
 assert.equal(typeof shipped.replayObservedUntil,'function');
 for(const asset of ['BTC','ETH']){
  const args={now_utc:now,publication_lineage:lineage};
  const shippedResult=shipped.readOfficialGraphB(latest,asset,args);
  const canonicalResult=readOfficialGraphB(latest,asset,args);
  assert.deepEqual(shippedResult,canonicalResult,'SOURCE_ADAPTER_CHANGED_WHEN_SHIPPED');
  assert.equal(shippedResult.source_status,'SOURCE_BOUNDED');
 }
});

test('v2 REAL SITE: original publication proof and source ownership, no second writer',()=>{
 assert.equal(latest.schema,'CN_PUBLIC_SNAPSHOT_V2');
 assert.equal(live.contract,'CN_PUBLIC_LIVE_PRICE_PRECISION_v1');
 assert.equal(live.forecast_week,latest.public_series.current_public_projection.forecast_week);
 assert.equal(live.public_issue_number,latest.public_series.current_public_projection.public_issue_number);
 assert.equal(lineage.contract,'CN_PUBLICATION_LINEAGE_RELEASE_RECEIPT_v1');
 assert.equal(lineage.forecast_week,live.forecast_week);
 assert.equal(lineage.public_issue_number,live.public_issue_number);
 assert.equal(lineage.source_to_public_equality,'PASS');
 assert.equal(lineage.prospective_forecast_points_created,0);
 assert.equal(lineage.last_observed_close_utc,live.hourly_price_path?.observed_through_utc);
});

for(const asset of ['BTC','ETH']){
 test('v2 REAL SITE '+asset+': one source-issued forecast and exact observed hours',()=>{
  const out=readOfficialGraphB(latest,asset,{now_utc:now,publication_lineage:lineage});
  assert.equal(out.source_status,'SOURCE_BOUNDED',JSON.stringify(out));
  assert.equal(out.asset,asset);
  assert.equal(out.score_authority,false);
  assert.equal(out.proof_authority,false);
  assert.equal(out.forecast_week,live.forecast_week);
  assert.equal(out.public_issue_number,live.public_issue_number);
  const expected=live.daily_price_path?.[asset];
  const compared=out.forecast_comparison_quote_status==='SAME_DECLARED_UNIT';
  if(expected?.status==='PUBLISHED'&&compared){
   assert.equal(out.forecast_status,'SOURCE_ISSUED');
   assert.equal(out.forecast.length,7);
   assert.deepEqual(out.forecast.map(x=>({
     day:x.day,expected_close:x.expected_close,low:x.low,high:x.high
   })),expected.points.map(x=>({
     day:x.day,expected_close:x.expected_close,low:x.low,high:x.high
   })));
  }else{
   assert.equal(out.forecast.length,0,'NO_SOURCE_ISSUED_SEVEN_DAY_PATH_ALLOWED');
  }
  const originals=live.hourly_price_path?.[asset]||[];
  assert.equal(out.hourly_observations.length,originals.length);
  assert.deepEqual(out.hourly_observations.map(x=>({
   time:new Date(x.time*1000).toISOString(),close:x.value
  })),originals.map(x=>({time:x.observed_at_utc.replace('.000Z','Z').replace('Z','.000Z'),close:x.close})));
  assert.deepEqual(out.actual_segments.flat().map(x=>x.value),originals.map(x=>x.close));
  for(const segment of out.actual_segments)
    for(let i=1;i<segment.length;i++)assert.equal(segment[i].time-segment[i-1].time,3600,'NO_HOURLY_GAP_BRIDGING');
  if(originals.length){
   assert.equal(out.last_observed_at_utc,originals.at(-1).observed_at_utc);
   const earlier=originals[0].observed_at_utc;
   const replay=replayObservedUntil(out,earlier).flat();
   assert.equal(replay.length,1,'NO_FUTURE_OBSERVATION_IN_REPLAY');
   assert.equal(replay[0].value,originals[0].close);
  }
 });
}

test('v2 REAL SITE: original corrected W46 matches its archived raw source, if active',()=>{
 if(live.forecast_week!=='2026-W46')return;
 const archive=json(resolve(repo,'05_CYCLE_NAVIGATOR/weekly/2026/W46/CYCLE_NAVIGATOR_FORECAST_FREEZE.json'));
 assert.equal(archive.daily_price_path.forecast_week,'2026-W46');
 for(const asset of ['BTC','ETH']){
  assert.deepEqual(live.daily_price_path[asset].points,archive.daily_price_path[asset].points);
  const out=readOfficialGraphB(latest,asset,{now_utc:now,publication_lineage:lineage});
  assert.deepEqual(out.forecast.map(x=>x.expected_close),
    archive.daily_price_path[asset].points.map(x=>x.expected_close));
 }
});

test('v2 REAL SITE: adversarial issue mismatch, source mismatch, quote mismatch all fail closed',()=>{
 const mismatch=untrustedCopy();
 mismatch.public_live_precision.public_issue_number+=1;
 for(const asset of ['BTC','ETH']){
  const out=readOfficialGraphB(mismatch,asset,{now_utc:now,publication_lineage:lineage});
  assert.equal(out.source_status,'UNAVAILABLE');
  assert.equal(out.forecast.length,0);
 }
 const invalidLineage={...lineage,source_to_public_equality:'FAIL'};
 assert.equal(readOfficialGraphB(latest,'BTC',{now_utc:now,publication_lineage:invalidLineage}).source_status,'UNAVAILABLE');
 const quote=untrustedCopy();
 quote.public_live_precision.price_quote_labels.forecast_model_declared.BTC='USD';
 const out=readOfficialGraphB(quote,'BTC',{now_utc:now});
 assert.equal(out.forecast_comparison_quote_status,'UNVERIFIED_OR_DIFFERENT_UNIT');
 assert.equal(out.forecast.length,0);
 const future=untrustedCopy(),row=future.public_live_precision.hourly_price_path.BTC;
 if(row.length){row[0].observed_at_utc='2099-01-01T01:00:00Z';
  assert.equal(readOfficialGraphB(future,'BTC',{now_utc:now}).source_status,'UNAVAILABLE');}
});

test('v2 REAL SITE: legacy live Graph B and canonical source adapter plot identical real BTC/ETH series',()=>{
 // This is a non-rendering parity canary, NOT a redesign. The existing chart
 // remains the sole production renderer until a separately accepted cutover.
 const sandbox={window:{CNI18n:{language:'da'}},document:{addEventListener(){}}};
 runInNewContext(readFileSync(resolve(site,'frozen-week-chart.js'),'utf8'),sandbox,
  {filename:'frozen-week-chart.js'});
 const legacy=sandbox.window.CNWeekChart;
 assert.equal(typeof legacy.model,'function');
 assert.equal(typeof legacy.linePlan,'function');
 for(const asset of ['BTC','ETH']){
  const old=legacy.model(latest,asset,Date.parse(now));
  assert.ok(old,'LEGACY_W46_OR_CURRENT_CANNOT_READ_VERIFIED_SNAPSHOT:'+asset);
  const oldPlan=legacy.linePlan(old);
  const modern=readOfficialGraphB(latest,asset,{now_utc:now,publication_lineage:lineage});
  assert.equal(modern.source_status,'SOURCE_BOUNDED');
  if(live.daily_price_path?.[asset]?.status==='PUBLISHED'&&
     modern.forecast_comparison_quote_status==='SAME_DECLARED_UNIT'){
   assert.equal(modern.forecast_status,'SOURCE_ISSUED',
    'REAL_SOURCE_ISSUED_DAILY_POINTS_MUST_SURVIVE:'+asset);
  }else assert.equal(modern.forecast.length,0,'NO_UNISSUED_FORECAST_POINTS:'+asset);
  assert.deepEqual(Array.from(oldPlan.forecast,p=>({time:p.time,value:p.value})),
   modern.forecast.map(p=>({time:p.time,value:p.expected_close})),
   'LEGACY_AND_DESIGN_FREE_BLUE_FORECAST_DIFFER:'+asset);
  assert.deepEqual(Array.from(oldPlan.actualRuns,run=>Array.from(run,p=>({
    time:p.time,value:p.value
  }))),modern.actual_segments.map(run=>run.map(p=>({
   time:p.time,value:p.value
  }))), 'LEGACY_AND_DESIGN_FREE_GREEN_ACTUALS_DIFFER:'+asset);
  assert.equal(old.stale,modern.live_freshness==='STALE',
   'LEGACY_AND_DESIGN_FREE_ACTUAL_FRESHNESS_DIFFER:'+asset);
 }
});

test('v2 prospective W47 rollover: no silent reuse of the original W46 forecast or actuals',()=>{
 if(live.forecast_week!=='2026-W46')return; // next real week has its own owner source
 const bad=untrustedCopy(),bm=bad.public_live_precision;
 bad.public_series.current_public_projection.forecast_week='2026-W47';
 bm.forecast_week='2026-W47';
 bm.daily_price_path.forecast_week='2026-W47';
 bm.hourly_price_path.forecast_week='2026-W47';
 for(const asset of ['BTC','ETH'])
  assert.equal(readOfficialGraphB(bad,asset,{now_utc:'2026-11-16T11:30:00Z'}).source_reason,
   'FROZEN_WEEK_BOUNDS_INVALID','W46_UTC_BOUNDS_NOT_A_W47_FORECAST:'+asset);

 // A hypothetical W47 UNISSUED state is a test fixture, NOT a published
 // historical forecast. Explicitly no carry-forward blue/green price series.
 const state=untrustedCopy(),m=state.public_live_precision;
 state.public_series.current_public_projection.forecast_week='2026-W47';
 state.public_series.current_public_projection.public_issue_number+=1;
 m.forecast_week='2026-W47';m.public_issue_number+=1;
 m.window_scores.day_1_2.window_start_utc='2026-11-16T00:00:00Z';
 m.window_scores.day_1_2.scoring_start_utc='2026-11-16T11:00:00Z';
 m.window_scores.day_5_7.window_end_utc='2026-11-23T00:00:00Z';
 m.frozen_at_utc='2026-11-16T10:52:34Z';
 m.scoring_valid_from_utc='2026-11-16T11:00:00Z';
 m.live_as_of_utc='2026-11-16T00:00:00Z';
 m.hourly_price_path.forecast_week='2026-W47';
 m.hourly_price_path.public_issue_number=m.public_issue_number;
 m.hourly_price_path.observed_through_utc='2026-11-16T00:00:00Z';
 m.daily_observations.observed_through_utc='2026-11-16T00:00:00Z';
 m.daily_price_path.forecast_week='2026-W47';
 if(m.daily_range_plan)m.daily_range_plan.forecast_week='2026-W47';
 for(const asset of ['BTC','ETH']){
  m.hourly_price_path[asset]=[];
  m.daily_observations[asset]=[];
  m.daily_price_path[asset]={status:'UNAVAILABLE',points:[]};
  if(m.daily_range_plan)m.daily_range_plan[asset]={status:'UNAVAILABLE',points:[]};
  const out=readOfficialGraphB(state,asset,{now_utc:'2026-11-16T11:30:00Z'});
  assert.equal(out.source_status,'SOURCE_BOUNDED');
  assert.equal(out.forecast_status,'UNAVAILABLE');
  assert.equal(out.forecast.length,0);
  assert.deepEqual(out.actual_segments,[]);
  assert.equal(out.is_current_quote,false);
 }
});
