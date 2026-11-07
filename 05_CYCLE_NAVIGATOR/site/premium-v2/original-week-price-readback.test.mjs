import test from 'node:test';
import assert from 'node:assert/strict';
import {buildWeek} from '../kompas-pro-test/alternativer/full-week-fixture.mjs';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {verifiedOriginalWeekPrices,originalWeekPriceLabel} from './original-week-price-readback.mjs';
import {KOMPAS_HORIZONS,kompasHorizonStatusRows} from './kompas-horizon-status.mjs';

function fixture(){
 const f=buildWeek({hours:168});
 const snapshot={...structuredClone(f.data),schema:'CN_PUBLIC_SNAPSHOT_V2'};
 const lineage={
  contract:'CN_PUBLICATION_LINEAGE_RELEASE_RECEIPT_v1',
  forecast_week:'2026-W46',public_issue_number:46,
  source_to_public_equality:'PASS',
  last_observed_close_utc:f.observedThroughUtc
 };
 return {f,snapshot,lineage};
}
const prove=(snapshot,lineage,nowUtc='2026-11-16T01:00:00Z')=>
 verifiedOriginalWeekPrices({latest:snapshot,publicationLineage:lineage,nowUtc});

test('both ORIGINAL source-issued BTC/ETH forecasts and price boundaries are summarized without a model',()=>{
 const {snapshot,lineage}=fixture();
 const status=prove(snapshot,lineage);
 assert.equal(status.contract,'CN_KOMPAS_PRO_ORIGINAL_WEEK_PRICE_READBACK_v1');
 assert.equal(status.status,'SOURCE_ISSUED_BOTH');
 assert.equal(status.forecast_week,'2026-W46');
 assert.equal(status.public_issue_number,46);
 assert.equal(status.quote,'USDT');
 assert.equal(status.official_action_authority,false);
 assert.equal(status.forecast_issued_by_this_consumer,false);
 for(const asset of ['BTC','ETH']){
  assert.equal(status[asset].original_expected_closes,7);
  assert.equal(status[asset].original_low_high_days,7);
  assert.ok(status[asset].week_daily_low_min<=status[asset].expected_last_daily_close);
  assert.ok(status[asset].week_daily_high_max>=status[asset].expected_last_daily_close);
 }
 assert.equal(status.BTC.expected_last_daily_close,
   snapshot.public_live_precision.daily_price_path.BTC.points[6].expected_close);
 assert.match(originalWeekPriceLabel(status,{lang:'da'}),/Oprindeligt frosset 2026-W46/);
 assert.match(originalWeekPriceLabel(status,{lang:'en'}),/Original/);
 assert.match(originalWeekPriceLabel(status,{lang:'da'}),/ETH søndagsluk/);
});

test('official expiry and stale green actual do not invalidate a frozen original week',()=>{
 const {snapshot,lineage}=fixture();
 const valid=prove(snapshot,lineage,'2026-11-21T00:00:00Z');
 assert.equal(valid.status,'SOURCE_ISSUED_BOTH');
 assert.equal(valid.BTC.actual_price_freshness,'STALE');
 const expired={compass:{state:'EXPIRED',permit_path_live_gates:false,compass_id:'EXPIRED'}};
 const m=kompasHorizonStatusRows({compass:null,view:expired,originalWeekPrice:valid});
 assert.equal(m.officialSourceCurrent,false);
 assert.equal(m.rows.length,14);
 const weekly=m.rows.find(x=>x.id==='H5_7D');
 assert.equal(weekly.status,'SOURCE_ISSUED_WEEK_PRICE_ONLY');
 assert.equal(weekly.sourceStatus,'ORIGINAL_WEEK_PRICE_NOT_DAILY_ACTION');
 assert.match(weekly.priceLabel,/BTC søndagsluk/);
 assert.equal(m.rows.find(x=>x.id==='H1_3D').status,'SOURCE_UNAVAILABLE');
 assert.equal(m.rows.find(x=>x.id==='H24H').status,'PENDING');
});

test('independent original week prices enrich Official direction without changing action or other horizons',()=>{
 const {snapshot,lineage}=fixture();
 const originalWeekPrice=prove(snapshot,lineage);
 const compass={
  contract:'PUBLIC_COMPASS_PROJECTION_v1',data_status:'OK',compass_id:'SOURCE_ID_1',
  horizons:{NEXT_1_3D:{expected_direction:'MIXED'},NEXT_5_7D:{expected_direction:'MIXED'},
    NEXT_2_3W:{expected_direction:'UP'}}
 };
 const view={compass:{state:'FRESH',permit_path_live_gates:true,compass_id:'SOURCE_ID_1'}};
 const m=kompasHorizonStatusRows({compass,view,originalWeekPrice});
 assert.deepEqual(m.rows.map(x=>x.id),KOMPAS_HORIZONS.map(x=>x[0]));
 assert.equal(m.rows.find(x=>x.id==='H5_7D').status,'OFFICIAL_DIRECTION_ONLY');
 assert.match(m.rows.find(x=>x.id==='H5_7D').priceLabel,/dags-low\/high samlet/);
 assert.equal(m.rows.find(x=>x.id==='H1_3D').status,'OFFICIAL_DIRECTION_ONLY');
 assert.match(m.rows.find(x=>x.id==='H1_3D').priceLabel,/ikke kursmål/);
 assert.equal(m.rows.find(x=>x.id==='H8_14D').status,'RESEARCH_ONLY');
 assert.equal(m.rows.find(x=>x.id==='H9_12M').status,'SCENARIO_ONLY');
});

test('fail-closed for missing or wrong publication lineage, quote mismatch and one-asset absence',()=>{
 const {snapshot,lineage}=fixture();
 const copies=[
  [snapshot,null],
  [snapshot,{...lineage,source_to_public_equality:'FAIL'}],
  [snapshot,{...lineage,forecast_week:'2026-W45'}],
  [snapshot,{...lineage,public_issue_number:45}],
  [snapshot,{...lineage,last_observed_close_utc:'2026-11-16T01:00:00Z'}],
  [{...snapshot,public_live_precision:{...snapshot.public_live_precision,
    price_quote_labels:{...snapshot.public_live_precision.price_quote_labels,
     forecast_model_declared:{BTC:'USD',ETH:'USDT'}}}},lineage],
  [{...snapshot,public_live_precision:{...snapshot.public_live_precision,
    daily_price_path:{...snapshot.public_live_precision.daily_price_path,
      ETH:{status:'UNAVAILABLE',points:[]}}}},lineage],
  [{...snapshot,public_live_precision:{...snapshot.public_live_precision,
    daily_range_plan:{...snapshot.public_live_precision.daily_range_plan,
      BTC:{...snapshot.public_live_precision.daily_range_plan.BTC,
       points:snapshot.public_live_precision.daily_range_plan.BTC.points.map(
        (p,i)=>i===0?{...p,low:p.low+1}:p)}}}},lineage]
 ];
 for(const [s,l] of copies){
  const val=prove(s,l);
  assert.equal(val.status,'UNAVAILABLE',JSON.stringify({reason:val.source_reason,quote:s.public_live_precision.price_quote_labels?.forecast_model_declared}));
  assert.equal(originalWeekPriceLabel(val),null);
  const m=kompasHorizonStatusRows({compass:null,view:null,originalWeekPrice:val});
  assert.equal(m.rows.find(x=>x.id==='H5_7D').status,'SOURCE_UNAVAILABLE');
 }
});

test('future observed data, spoofed snapshot, incomplete week and invalid clock cannot issue price',()=>{
 const {snapshot,lineage}=fixture();
 assert.equal(prove(snapshot,lineage,'2026-11-15T12:00:00Z').status,'UNAVAILABLE');
 assert.equal(verifiedOriginalWeekPrices({latest:snapshot,publicationLineage:lineage,nowUtc:'NOT-A-DATE'}).status,'UNAVAILABLE');
 assert.equal(prove({...snapshot,schema:'FAKE'},lineage).status,'UNAVAILABLE');
 const s=structuredClone(snapshot);
 s.public_live_precision.daily_price_path.BTC.points.pop();
 assert.equal(prove(s,lineage).status,'UNAVAILABLE');
});

test('private source or fake daily research scenarios are never inferred from original readback',()=>{
 const {snapshot,lineage}=fixture();
 const val=prove(snapshot,lineage);
 assert.ok(!('numeric_scenario_probability' in val));
 assert.ok(!('official_action' in val));
 assert.ok(!('forecast' in val));
 assert.ok(!('issued_prediction' in val));
});


test('eight-lane Research Parallel Lanes manifest passes original deterministic schema guard, no agent dispatch',()=>{
 const validator=fileURLToPath(new URL('../../../scripts/research/validate_parallel_research_manifest_v1.py',import.meta.url));
 const manifest=fileURLToPath(new URL('../../../04_MARKET_LEARNING/handlekompas/research/kompas_pro_elite_20261107/RESEARCH_PARALLEL_LANES_V1_MISSION.json',import.meta.url));
 const output=JSON.parse(execFileSync('python3',[validator,manifest],{encoding:'utf8'}));
 assert.equal(output.status,'PASS_SCHEMA_ONLY');
 assert.equal(output.lanes,8);
 assert.equal(output.does_not_dispatch_agents_or_jobs,true);
});
