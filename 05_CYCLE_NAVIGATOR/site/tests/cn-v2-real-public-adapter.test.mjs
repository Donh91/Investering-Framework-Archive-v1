/**
 * CN SITE v2 pre-design contract. Runs on the EXACT generated public bundle,
 * not a synthetic screenshot fixture. Does NOT authorize redesign release.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
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
