// Premium vNext candidate production-source contract tests.
// Runs in current SITE gate; synthetic source fixtures NEVER reach public dist.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {inspectOfficialPublicFeeds} from './official-feed-parity.mjs';
const dir=dirname(fileURLToPath(import.meta.url));
const read=name=>readFileSync(resolve(dir,name),'utf8');
const site=readFileSync(resolve(dir,'../build-public.mjs'),'utf8');
const html=read('index.html'),client=read('app.mjs'),css=read('premium.css');
const now='2026-10-19T09:00:00Z';
const windows=['day_1_2','day_3_4','day_5_7'];
const rows=windows.flatMap((window,i)=>['BTC','ETH'].map((asset)=>({
  window,asset,forecast_low:asset==='BTC'?77000:2150,
  forecast_high:asset==='BTC'?86500:2600,
  actual_low:asset==='BTC'?79500:2260,
  actual_high:asset==='BTC'?84300:2480,
  score:asset==='BTC'?86-i:84-i
})));
const latest={
 schema:'CN_PUBLIC_SNAPSHOT_V2',generated_at:'2026-10-19T08:55:00Z',
 pointer:{iso_year:2026,iso_week:43,issue_number:31,status:'DEGRADED'},
 package:{issue_number:31,status:'DEGRADED',forecast_freeze:{
  btc_range_low:77000,btc_range_high:86500,eth_range_low:2150,eth_range_high:2600}},
 public_series:{contract:'CN_PUBLIC_SERIES_INDEX_v1',
  current_public_projection:{public_issue_number:30,forecast_week:'2026-W43'},
  latest_completed_score:{public_issue_number:29,forecast_week:'2026-W42',status:'FINAL_DUAL_TRACK',price_range_score:85.25}},
 public_scorecard:{contract:'CN_PUBLIC_WEEKLY_SCORECARD_v1',status:'FINAL_DUAL_TRACK',
  public_issue_number:29,forecast_week:'2026-W42',
  combined_score:null,market_structure_precision:null,
  price_range_precision:{formula:'70pct_containment_plus_30pct_jaccard',
    score:85.25,btc_score:86,eth_score:84,actuals_hourly_coverage:168,rows,
    intraday_window_scores:{day_1_2:84,day_3_4:85,day_5_7:86}}}
};
const compass={
 contract:'PUBLIC_COMPASS_PROJECTION_v1',data_status:'OK',
 compass_id:'CMP-SYNTHETIC-W43',issued_at_utc:'2026-10-19T08:50:00Z',
 weekly_context:{status:'ALIGNED',forecast_week:'2026-W43',public_issue_number:30},
 full_stack:{official_freshness:{
  contract:'OFFICIAL_COMPASS_SOURCE_FRESHNESS_READBACK_v1',
  status:'VERIFIED_OWNER_POLICY',semantics:'SOURCE_FRESHNESS_EXPIRY_NOT_FORECAST_ETA',
  source_asof_utc:'2026-10-19T08:45:00Z',valid_until_utc:'2026-10-19T10:00:00Z'
 }},
 action_now:'HOLD_WAIT',horizons:{NEXT_12H:{expected_direction:'UP'}},
 protection_tracker:{pullback_risk_state:'ELEVATED',
  distribution_risk:'UNKNOWN',reentry_state:'INACTIVE'},
 sell_assessment:{state:'UNAVAILABLE'}
};
const run=(l=latest,c=compass,clock=now)=>inspectOfficialPublicFeeds(l,c,{nowUtc:clock});
const good=run();
assert.equal(good.weekly.forecast_week,'2026-W43');
assert.equal(good.weekly.state,'DEGRADED');
assert.deepEqual(good.weekly.btc_range,{low:77000,high:86500});
assert.equal(good.compass.state,'FRESH');
assert.equal(good.compass.action_now,'HOLD_WAIT');
assert.equal(good.compass.permit_path_live_gates,true);
assert.equal(good.completed_score.state,'FINAL_PUBLIC_SCORECARD');
assert.equal(good.completed_score.forecast_week,'2026-W42');
assert.equal(good.completed_score.price_range_precision,85.25);
assert.equal(good.completed_score.rows.length,6);
assert.equal(good.completed_score.market_structure_precision,null);
assert.match(good.completed_score.proof_state,/NOT_INDEPENDENTLY_SEALED/);
const stale=structuredClone(latest);stale.generated_at='2026-10-18T06:00:00Z';
assert.equal(run(stale).compass.action_now,'UNAVAILABLE');
const misjoined=structuredClone(latest);misjoined.public_series.current_public_projection.forecast_week='2026-W42';
assert.equal(run(misjoined).compass.permit_path_live_gates,false);
assert.equal(run(misjoined).completed_score.state,'FINAL_PUBLIC_SCORECARD'); // Past completed result has its own exact source identity; never promoted into live action.
const expired=structuredClone(compass);expired.full_stack.official_freshness.valid_until_utc='2026-10-19T08:59:00Z';
assert.equal(run(latest,expired).compass.action_now,'UNAVAILABLE');
const wrongWeek=structuredClone(compass);wrongWeek.weekly_context.public_issue_number=29;
assert.equal(run(latest,wrongWeek).compass.permit_path_live_gates,false);
const partial=structuredClone(latest);partial.public_scorecard.price_range_precision.actuals_hourly_coverage=167;
assert.equal(run(partial).completed_score.state,'MISMATCH_OR_INCOMPLETE');
const retro=structuredClone(latest);retro.public_scorecard.market_structure_precision=60;
assert.equal(run(retro).completed_score.state,'MISMATCH_OR_INCOMPLETE');
const resultWithoutSource=run(null,null);
assert.equal(resultWithoutSource.compass.action_now,'UNAVAILABLE');
assert.equal(resultWithoutSource.completed_score.price_range_precision,null);
assert.match(html,/<section id="view-overview"/);
assert.match(html,/<section id="view-compass"/);
assert.match(html,/<section id="view-results"/);
assert.match(html,/aria-label="Vælg sprog"/);
assert.match(html,/href="\.\.\/frozen-week-chart.css"/);
assert.match(client,/\.\.\/data\/latest.json/);
assert.match(client,/\.\.\/data\/compass.json/);
assert.match(client,/CNWeekChart\.mount\(host,feeds.latest\)/);
assert.match(client,/inspectOfficialPublicFeeds\(feeds.latest,feeds.compass\)/);
assert.match(client,/setInterval\(refresh,60000\)/);
assert.doesNotMatch(client,/seed\.json|localhost|private\/|secrets\/|api\.coingecko|wallet/i);
assert.match(css,/@media\(max-width:520px\)/);
assert.match(css, /prefers-reduced-motion/);
assert.match(site,/resolve\(outputDir,"vnext"\)/);
assert.match(site,/await copyFile\(resolve\(siteDir,"vnext-live",file\),resolve\(vnextDir,file\)\)/);
execFileSync(process.execPath,['--check',resolve(dir,'app.mjs')],{stdio:'pipe'});
console.log('PASS vNext: W43 source truth, official freshness, score isolation, negative gates, three-view shell, i18n and syntax');
