import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';

// Design-neutral, source-owned baseline. A designer may replace every chart
// component, but must not replace the original W46 issuer with demo data.
const repo=resolve(dirname(fileURLToPath(import.meta.url)),'../../..');
const weekly=resolve(repo,'05_CYCLE_NAVIGATOR/weekly/2026/W46');
const read=p=>JSON.parse(readFileSync(p,'utf8'));
const freezeBytes=readFileSync(resolve(weekly,'CYCLE_NAVIGATOR_FORECAST_FREEZE.json'));
const freeze=JSON.parse(freezeBytes);
const receipt=read(resolve(weekly,'CYCLE_NAVIGATOR_SITE_PUBLIC_FREEZE_RECEIPT.json'));
const manifest=read(resolve(weekly,'CYCLE_NAVIGATOR_SOURCE_MANIFEST.json'));

test('CN v2 design baseline: original same-Monday amended W46 is hash-bound and never a synthetic mock',()=>{
 const sha=createHash('sha256').update(freezeBytes).digest('hex');
 assert.equal(receipt.source_forecast_freeze_sha256,sha);
 assert.equal(manifest.owner_approved_same_day_revision?.after_forecast_sha256,sha);
 assert.equal(freeze.daily_price_path?.contract,'CN_FROZEN_DAILY_PRICE_PATH_v1');
 assert.equal(freeze.daily_price_path.forecast_week,'2026-W46');
 assert.equal(receipt.daily_product_acceptance?.status,'COMPLETE');
 assert.equal(receipt.daily_product_acceptance?.no_backward_reconstruction,true);
 assert.ok(Date.parse(receipt.scoring_valid_from_utc)>Date.parse(receipt.daily_product_acceptance.issued_at_utc));
 for(const asset of ['BTC','ETH']){
  assert.equal(freeze.price_quote?.[asset],'USDT');
  const row=freeze.daily_price_path[asset];
  assert.equal(row.status,'PUBLISHED');
  assert.equal(row.points.length,7);
  for(let i=0;i<7;i++){
   const p=row.points[i];
   assert.equal(p.day,i+1);
   assert.ok([p.low,p.expected_close,p.high].every(x=>typeof x==='number'&&Number.isFinite(x)&&x>0));
   assert.ok(p.low<=p.expected_close&&p.expected_close<=p.high);
  }
 }
});

test('CN v2 design boundary: renderer stays downstream of original source and actuals',()=>{
 const code=readFileSync(resolve(repo,'05_CYCLE_NAVIGATOR/site/frozen-week-chart.js'),'utf8');
 assert.match(code,/function model\(data,key,now=Date\.now\(\)\)/);
 assert.match(code,/CN_FROZEN_DAILY_PRICE_PATH_v1/);
 assert.match(code,/CN_PUBLIC_HOURLY_PRICE_PATH_v1/);
 assert.match(code,/function linePlan\(m\)/);
 assert.match(code,/function mount\(host,data\)/);
 assert.match(code,/baseline\.setData\(plan\.forecast\)/);
 assert.match(code,/plan\.actualRuns/);
});
