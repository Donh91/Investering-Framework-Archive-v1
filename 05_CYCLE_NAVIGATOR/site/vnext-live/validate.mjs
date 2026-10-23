// Premium vNext candidate production-source contract tests.
// Runs in current SITE gate; synthetic source fixtures NEVER reach public dist.
import assert from 'node:assert/strict';
import './test-premium-experience.mjs';
import {readFileSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {inspectOfficialPublicFeeds} from './official-feed-parity.mjs';
import {mondayContext,mondayLabels} from './monday-public-bridge.mjs';
import {sourceTrace} from './source-trace.mjs';
import './test-forward-outlook.mjs';
import {chartSourceFingerprint} from './chart-source-key.mjs';
import {verifiedBtcFrozenReference} from './official-path.mjs';
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

// An explicit denial must NEVER become a blue CURRENT/LEADERSHIP badge.
assert.equal(verifiedBtcFrozenReference(
 'BTC-led rotation was not confirmed','BTC leadership is unconfirmed'),false);
assert.equal(verifiedBtcFrozenReference(
 'BTC led on the completed week','BTC leadership was not confirmed'),false);
assert.equal(verifiedBtcFrozenReference(
 'BTC did not lead during the completed week','BTC was the leader'),false);
assert.equal(verifiedBtcFrozenReference(
 'The market has no confirmed leader','BTC lead remains unknown'),false);
assert.equal(verifiedBtcFrozenReference(
 'BTC led the completed week','BTC leadership was confirmed'),true);
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
// Master Monday is verified WEEKLY context, never an alternative live action.
// These are actual executable parity tests, not just checks for function names.
const mondayLatest=structuredClone(latest);
mondayLatest.pointer.completed_source_week=42;
mondayLatest.pointer.completed_source_year=2026;
const mondayCompass=structuredClone(compass);
mondayCompass.full_stack.contract='PUBLIC_COMPASS_FULL_STACK_READBACK_v1';
mondayCompass.full_stack.source_status={master_monday:'SOURCE_ALIGNED',master_monday_analysis:'COMPLETE'};
mondayCompass.full_stack.master_monday={
 contract:'PUBLIC_MASTER_MONDAY_WEEKLY_CONTEXT_READBACK_v1',
 completed_week:'2026-W42',status:'SOURCE_ALIGNED',analytics_status:'COMPLETE',
 scorecard_status:'COMPLETE',operational_translation_status:'COMPLETE',
 api_analysis_status:'AVAILABLE_SHADOW_ONLY',authority:'WEEKLY_CONTEXT_ONLY_NO_CURRENT_ACTION',
 internal_secret:'PRIVATE_DO_NOT_SHOW'
};
const mondayRead=(l=mondayLatest,c=mondayCompass,t=now)=>mondayContext(l,c,run(l,c,t));
const mondayGood=mondayRead();
assert.equal(mondayGood.source_state,'SOURCE_ALIGNED');
assert.equal(mondayGood.completed_week,'2026-W42');
assert.equal(mondayGood.analytics_status,'COMPLETE');
assert.equal(mondayGood.current_action_authority,false);
assert.equal(mondayGood.api_analysis_status,'AVAILABLE_SHADOW_ONLY');
assert.equal(JSON.stringify(mondayGood).includes('PRIVATE_DO_NOT_SHOW'),false);
assert.match(mondayLabels(mondayGood,'da').title,/komplet/);
assert.match(mondayLabels(mondayGood,'en').title,/complete/);
const monPartial=structuredClone(mondayCompass);
monPartial.full_stack.master_monday.analytics_status='PARTIAL_ANALYTICS';
monPartial.full_stack.source_status.master_monday_analysis='PARTIAL_ANALYTICS';
assert.equal(mondayRead(mondayLatest,monPartial).analytics_status,'PARTIAL_ANALYTICS');
assert.match(mondayLabels(mondayRead(mondayLatest,monPartial),'da').title,/delvist/);
const monConflict=structuredClone(mondayCompass);
monConflict.full_stack.master_monday.analytics_status='CONFLICTING_ANALYTICS';
monConflict.full_stack.source_status.master_monday_analysis='CONFLICTING_ANALYTICS';
assert.equal(mondayRead(mondayLatest,monConflict).analytics_status,'CONFLICTING_ANALYTICS');
assert.match(mondayLabels(mondayRead(mondayLatest,monConflict),'en').title,/Conflicting/);
const mismatchAnalytics=structuredClone(monPartial);
mismatchAnalytics.full_stack.source_status.master_monday_analysis='COMPLETE';
assert.equal(mondayRead(mondayLatest,mismatchAnalytics).source_state,'UNVERIFIED');
const missingMachine=structuredClone(mondayCompass);
delete missingMachine.full_stack.master_monday;
assert.equal(mondayRead(mondayLatest,missingMachine).analytics_status,'UNVERIFIED');
const wrongSourceStatus=structuredClone(mondayCompass);
wrongSourceStatus.full_stack.source_status.master_monday='UNVERIFIED';
assert.equal(mondayRead(mondayLatest,wrongSourceStatus).source_state,'UNVERIFIED');
const wrongCompletedWeek=structuredClone(mondayCompass);
wrongCompletedWeek.full_stack.master_monday.completed_week='2026-W43';
assert.equal(mondayRead(mondayLatest,wrongCompletedWeek).source_state,'UNVERIFIED');
const yearOldMonday=structuredClone(mondayCompass);
yearOldMonday.full_stack.master_monday.completed_week='2025-W42';
assert.equal(mondayRead(mondayLatest,yearOldMonday).source_state,'UNVERIFIED',
  'Year-old completed W42 must not masquerade as current W42');
const wrongSourceYear=structuredClone(mondayLatest);
wrongSourceYear.pointer.completed_source_year=2025;
assert.equal(mondayRead(wrongSourceYear).source_state,'UNVERIFIED',
  'Publicly declared source year must match its immutable completed week');
const missingSourceYear=structuredClone(mondayLatest);
delete missingSourceYear.pointer.completed_source_year;
assert.equal(mondayRead(missingSourceYear).source_state,'UNVERIFIED',
  'Absent explicit completed source-year is not permission to infer one');
const inconsistentSourceWeek=structuredClone(mondayLatest);
inconsistentSourceWeek.pointer.completed_source_week=40;
assert.equal(mondayRead(inconsistentSourceWeek).source_state,'UNVERIFIED',
  'An old week cannot be presented as current weekly baseline');
const wrongPointerWeek=structuredClone(mondayLatest);
wrongPointerWeek.pointer.completed_source_week=41;
assert.equal(mondayRead(wrongPointerWeek).source_state,'UNVERIFIED');
const deniedAuthority=structuredClone(mondayCompass);
deniedAuthority.full_stack.master_monday.authority='CURRENT_ACTION';
assert.equal(mondayRead(mondayLatest,deniedAuthority).source_state,'UNVERIFIED');
const staleDelivery=structuredClone(mondayLatest);
staleDelivery.generated_at='2026-10-17T08:00:00Z';
assert.equal(mondayRead(staleDelivery).source_state,'UNVERIFIED');
const noCompass=structuredClone(mondayCompass);
noCompass.full_stack.contract='INVALID';
assert.equal(mondayRead(mondayLatest,noCompass).source_state,'UNVERIFIED');
// Executed full-stack evidence tests. This never makes research tradeable.
const traceCompass=structuredClone(mondayCompass);
traceCompass.full_stack.status='PARTIAL_OR_DEGRADED';
traceCompass.full_stack.source_status={
 official:'VERIFIED',auto_market_state:'HASH_VERIFIED',
 native:'SOURCE_ALIGNED',shadow:'STALE_RESEARCH',
 strategic:'BOUND_WEEKLY_ANCHOR',master_monday:'SOURCE_ALIGNED',
 cycle_navigator:'WEEKLY_POINTER_ALIGNED'
};
traceCompass.full_stack.weekly={iso_week:43,iso_year:2026,direction_2_3w:'MIXED'};
traceCompass.full_stack.strategic={
 status:'BOUND_WEEKLY_ANCHOR',authority:'CYCLE_NAVIGATOR_OWNED_NOT_NEW_SITE_FORECAST',
 horizon_21_30d:{direction:'UP'},horizon_4_8w:{direction:'UNCLEAR'}
};
const trace=(l=mondayLatest,c=traceCompass,t=now)=>sourceTrace(l,c,run(l,c,t));
const sourceGood=trace();
assert.equal(sourceGood.status,'PARTIAL_OR_DEGRADED');
assert.equal(sourceGood.decision_authority,'OFFICIAL_COMPASS_ONLY');
assert.deepEqual(sourceGood.long_horizons.map(x=>x.direction),['MIXED','UP','UNCLEAR']);
assert.equal(sourceGood.official_current,true);
assert.equal(sourceGood.long_horizons[2].owner,'CYCLE_NAVIGATOR_STRATEGIC_CONTEXT',
  'The 4–8w owner is CN, even when an authorized strategic overlay supplies context');
assert.equal(sourceGood.sources.length,7);
assert.equal(sourceGood.sources.find(x=>x.id==='shadow').status,'STALE_RESEARCH');
assert.notEqual(sourceGood.status,'COMPLETE','Stale research is not a complete source inventory');
const traceComplete=structuredClone(traceCompass);
traceComplete.full_stack.status='COMPLETE';
traceComplete.full_stack.source_status.shadow='ALIGNED_RESEARCH';
traceComplete.full_stack.source_status.master_monday_analysis='COMPLETE';
assert.equal(trace(mondayLatest,traceComplete).status,'COMPLETE');
const forgedComplete=structuredClone(traceCompass);
forgedComplete.full_stack.status='COMPLETE';
assert.equal(trace(mondayLatest,forgedComplete).status,'UNVERIFIED',
  'A claimed COMPLETE with stale Shadow is a contradiction, not a green badge');
const invalidStatus=structuredClone(traceCompass);
invalidStatus.full_stack.source_status.shadow='BUY';
assert.equal(trace(mondayLatest,invalidStatus).sources.find(x=>x.id==='shadow').status,'UNAVAILABLE',
  'Unrecognized public source enums must never render as action signals');
const badWeek=structuredClone(mondayLatest);
badWeek.public_series.current_public_projection.forecast_week='2026-W42';
assert.deepEqual(trace(badWeek).long_horizons.map(x=>x.direction),['UNAVAILABLE','UNAVAILABLE','UNAVAILABLE']);
const wrongIssue=structuredClone(traceCompass);
wrongIssue.weekly_context.public_issue_number=29;
assert.equal(trace(mondayLatest,wrongIssue).status,'UNVERIFIED');
const expiredTrace=structuredClone(traceCompass);
expiredTrace.full_stack.official_freshness.valid_until_utc='2026-10-19T08:59:00Z';
const expiredContext=trace(mondayLatest,expiredTrace);
assert.equal(expiredContext.status,'PARTIAL_OR_DEGRADED');
assert.equal(expiredContext.official_current,false);
assert.equal(expiredContext.reason,'OFFICIAL_NOT_CURRENT_CONTEXT_ONLY');
assert.equal(expiredContext.sources.find(x=>x.id==='official').status,'UNAVAILABLE');
assert.deepEqual(expiredContext.long_horizons.map(x=>x.direction),['MIXED','UP','UNCLEAR'],
  'Official expiry must not erase independently eligible CN / strategic source evidence');
const staleOfficial=structuredClone(traceCompass);
staleOfficial.data_status='DEGRADED';
const staleOfficialContext=trace(mondayLatest,staleOfficial);
assert.equal(staleOfficialContext.official_current,false);
assert.equal(staleOfficialContext.sources.find(x=>x.id==='official').status,'UNAVAILABLE');
assert.equal(staleOfficialContext.long_horizons[0].direction,'MIXED');
const missingStack=structuredClone(traceCompass);
delete missingStack.full_stack;
assert.equal(trace(mondayLatest,missingStack).status,'UNVERIFIED');
const contradictoryResearch=structuredClone(traceCompass);
contradictoryResearch.full_stack.source_status.strategic='UNVERIFIED';
assert.deepEqual(trace(mondayLatest,contradictoryResearch).long_horizons.map(x=>x.direction),
 ['MIXED','UNAVAILABLE','UNAVAILABLE']);
const mutatedResearchAuthority=structuredClone(traceCompass);
mutatedResearchAuthority.full_stack.strategic.authority='OFFICIAL_ACTION';
assert.deepEqual(trace(mondayLatest,mutatedResearchAuthority).long_horizons.map(x=>x.direction),
 ['MIXED','UNAVAILABLE','UNAVAILABLE']);
const noCNProvenance=structuredClone(traceCompass);
noCNProvenance.full_stack.source_status.cycle_navigator='UNVERIFIED';
assert.deepEqual(trace(mondayLatest,noCNProvenance).long_horizons.map(x=>x.direction),
 ['UNAVAILABLE','UNAVAILABLE','UNAVAILABLE'],
 'Neither the 4–8w CN outlook nor strategic overlays can outlive invalid weekly provenance');
const wrongWeeklySource=structuredClone(traceCompass);
wrongWeeklySource.full_stack.weekly.iso_week=42;
assert.equal(trace(mondayLatest,wrongWeeklySource).long_horizons[0].direction,'UNAVAILABLE');
const unsafeDirection=structuredClone(traceCompass);
unsafeDirection.full_stack.strategic.horizon_21_30d.direction='BUY NOW 99%';
assert.equal(trace(mondayLatest,unsafeDirection).long_horizons[1].direction,'UNAVAILABLE');
const stalePublic=structuredClone(mondayLatest);
stalePublic.generated_at='2026-10-18T06:00:00Z';
assert.equal(trace(stalePublic).status,'UNVERIFIED');
assert.equal(sourceTrace(null,null,null).sources.every(x=>x.status==='UNAVAILABLE'),true);
assert.equal(JSON.stringify(sourceGood).includes('PRIVATE_DO_NOT_SHOW'),false);
assert.match(html,/data-contract="CN_PREMIUM_SOURCE_TRACE_v1"/);
assert.match(css,/\.source-trace-details summary\{min-height:44px/);
assert.match(html,/id="long-horizon-body"/);
assert.match(html,/id="source-trace-body"/);
assert.match(client,/sourceTrace\(feeds\?\.latest,feeds\?\.compass,view\)/);
assert.match(client,/drawSourceTrace\(\)/);
assert.match(client,/OFFICIAL_NOT_CURRENT_CONTEXT_ONLY/);
assert.match(client,/CYCLE_NAVIGATOR_STRATEGIC_CONTEXT/);
assert.match(site,/"monday-public-bridge.mjs","source-trace.mjs"/);
assert.doesNotMatch(read('source-trace.mjs'),/fetch\(|\bwallet\b|\bOPENAI_API_KEY\b|eval\(/i);
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
assert.match(html,/data-contract="PUBLIC_MASTER_MONDAY_WEEKLY_CONTEXT_READBACK_v1"/);
assert.match(html,/id="monday-reading"/);
assert.match(html,/id="monday-week"/);
assert.match(html,/id="monday-api"/);
assert.match(client,/mondayContext\(feeds\?\.latest,feeds\?\.compass,view\)/);
assert.match(client,/forwardOutlook\(feeds\?\.latest,feeds\?\.compass,trace\)/);
assert.match(html,/class="cn-forward"/);
assert.match(site,/summary_2_3w:weeklyAligned\?publicNarrative/);
assert.match(site,/expected_path:publicNarrative\(anchor\?\.strategic_21_30d\?\.expected_path\)/);
assert.match(client,/function drawMonday\(\)/);
assert.match(client,/function drawCompass\(\)\{\s*drawMonday\(\);/);
assert.match(site,/"chart-source-key.mjs","forward-outlook.mjs","monday-public-bridge.mjs"/);
assert.match(site,/"iso_year","iso_week","completed_source_year","completed_source_week"/);
assert.doesNotMatch(read('monday-public-bridge.mjs'),/fetch\(|\bwallet\b|\bsecret\b|\bOPENAI_API_KEY\b/i);

assert.match(html,/aria-label="Vælg sprog"/);
assert.match(html,/href="\.\.\/frozen-week-chart.css"/);
assert.match(client,/\.\.\/data\/latest.json/);
assert.match(client,/\.\.\/data\/compass.json/);
assert.match(client,/CNWeekChart\.mount\(host,chartData\)/);
assert.match(client,/inspectOfficialPublicFeeds\(feeds.latest,feeds.compass,\{lang\}\)/);
assert.match(client,/setInterval\(refresh,60000\)/);
assert.doesNotMatch(client,/seed\.json|localhost|private\/|secrets\/|api\.coingecko|wallet/i);
assert.match(css,/@media\(max-width:520px\)/);
assert.match(css, /prefers-reduced-motion/);
assert.match(html, /role="tablist"/);
assert.equal((html.match(/role="tabpanel"/g)||[]).length,4);
assert.equal((html.match(/role="tab"/g)||[]).length,4);
assert.match(html,/id="view-path"/);
assert.match(html,/id="premium-risk-steps"/);
assert.match(html,/id="premium-balance-bars"/);
assert.match(html,/id="premium-proof-copy"/);
assert.match(html,/id="premium-proof-price-status"/);
assert.match(html,/id="premium-proof-direction-status"/);
assert.match(html,/id="premium-proof-pullback-status"/);
assert.equal((html.match(/class="product-more"/g)||[]).length,2);
assert.match(client,/renderProductExperience\(view,feeds,lang\)/);
const experience=read('premium-experience.mjs'),experienceCss=read('premium-experience.css');
assert.match(experience,/officialBullBear\(current,'1_3d'\)/);
assert.match(experience,/officialPullbackStage/);
assert.match(experience,/officialPathView\(null,\{lang\}\)/);
assert.match(experience,/riskStageLabel\(s,lang\)/);
assert.match(client,/const target=a\.dataset\.navTo/);
assert.match(client,/document\.querySelector\('\[data-tab="'\+target\+'"\]'\)\?\.focus\(\)/);
assert.match(experience,/permit_path_live_gates===true/);
assert.match(experience,/publicAuditPrompt/);
assert.doesNotMatch(experience,/fetch\(|OPENAI_API_KEY|seed\.json/);
assert.match(experienceCss,/min-height:44px/);
// Chart redraw must track semantic source changes (not just fetch object identity),
 // otherwise a refresh can destroy zoom, selected UTC day and the chosen asset.
assert.match(client, /lastChartFingerprint!==fingerprint\|\|lastChartLang!==lang/);
assert.match(client, /chartSourceFingerprint\(chartData\)/);
// Behavioral counterexample (Codex P2): a frozen source keeps its live
// observation bytes while the weekly public projection is temporarily
// misjoined, then repaired. Both transitions MUST invalidate the view.
const liveChartFixture=structuredClone(latest);
liveChartFixture.public_live_precision={
  public_issue_number:30,forecast_week:'2026-W43',live_as_of_utc:now,
  window_scores:{day_1_2:{window_start_utc:'2026-10-19T00:00:00Z'}},
  rows:[{asset:'BTC',window:'day_1_2',forecast_low:77000,forecast_high:86500}],
  daily_price_path:{BTC:{status:'UNAVAILABLE'}},
  daily_observations:{BTC:[]}
};
const validKey=chartSourceFingerprint(liveChartFixture,Date.parse(now));
const reloaded=structuredClone(liveChartFixture);
reloaded.generated_at='2026-10-19T09:01:00Z';
assert.equal(chartSourceFingerprint(reloaded,Date.parse(now)),validKey,
  'Fresh fetch of unchanged chart must preserve zoom and asset selection');
const wronglyJoined=structuredClone(liveChartFixture);
wronglyJoined.public_series.current_public_projection.forecast_week='2026-W42';
assert.notEqual(chartSourceFingerprint(wronglyJoined,Date.parse(now)),validKey,
  'Wrong-week public projection must invalidate old chart even with identical observation bytes');
wronglyJoined.public_series.current_public_projection.forecast_week='2026-W43';
assert.equal(chartSourceFingerprint(wronglyJoined,Date.parse(now)),validKey,
  'Correct source restoration must invalidate a prior misjoined screen');
// A cached chart's OBSERVED/STALE badge must change when the immutable
// source evidence crosses its own 90-minute freshness limit, even when no
// public JSON bytes change. It must NOT redraw every 60s while still fresh.
const cutoffMillis=Date.parse(now);
const freshAt1=chartSourceFingerprint(liveChartFixture,cutoffMillis+60000);
const freshAt2=chartSourceFingerprint(liveChartFixture,cutoffMillis+45*60000);
const staleAt=chartSourceFingerprint(liveChartFixture,cutoffMillis+91*60000);
assert.equal(freshAt1,freshAt2,'Stable fresh source must not reset zoom on timer');
assert.notEqual(freshAt1,staleAt,'A source must lose its fresh chart badge after SLA expiry');
assert.equal(staleAt,chartSourceFingerprint(liveChartFixture,cutoffMillis+120*60000),
  'After stale transition keep chart zoom stable until the source changes');
const wrongPublicIssue=structuredClone(liveChartFixture);
wrongPublicIssue.public_series.current_public_projection.public_issue_number=29;
assert.notEqual(chartSourceFingerprint(wrongPublicIssue,Date.parse(now)),validKey,
  'Wrong public issue must invalidate old chart');
const wrongMachineIssue=structuredClone(liveChartFixture);
wrongMachineIssue.pointer.issue_number=30;
assert.notEqual(chartSourceFingerprint(wrongMachineIssue,Date.parse(now)),validKey,
  'Wrong machine issue must invalidate old chart');
const freshDaily=structuredClone(liveChartFixture);
freshDaily.public_live_precision.daily_observations.BTC=[{day:1,close:81111}];
assert.notEqual(chartSourceFingerprint(freshDaily,Date.parse(now)),validKey,
  'A real new observation must update the chart');

assert.match(client, /event\.key==='ArrowRight'/);
assert.match(client, /event\.key==='ArrowLeft'/);

// Exercise the real adapter: switching language must translate its own PATH
// labels without changing the source eligibility or official action.
const pathLatest=structuredClone(latest),pathCompass=structuredClone(compass);
pathLatest.package.rotation_ladder=[];
pathLatest.package.altseason_countdown=[];
pathCompass.capitalization_ladder=[];
const pathDa=inspectOfficialPublicFeeds(pathLatest,pathCompass,{nowUtc:now,lang:'da'});
const pathEn=inspectOfficialPublicFeeds(pathLatest,pathCompass,{nowUtc:now,lang:'en'});
assert.equal(pathDa.path.state,'SOURCE_BOUND');
assert.equal(pathEn.path.next_gate,'Next gate not documented');
assert.equal(pathDa.path.next_gate,'Næste gate ikke dokumenteret');
assert.deepEqual(pathEn.compass,pathDa.compass);
assert.match(client,/inspectOfficialPublicFeeds\(feeds\.latest,feeds\.compass,\{lang\}\)/);

assert.match(css, /\.cycle-step\[data-reference="true"\]/);
assert.doesNotMatch(css, /\.cycle-step:first-child\{/);
// The old five-node Overview rail was intentionally retired. Assert that the
// product now binds the source checkpoint to the full ten-stage PATH rail.
assert.match(read('premium-experience.mjs'), /p\.current_checkpoint\?\.key===x\.key/);
assert.match(read('premium-experience.mjs'), /FROZEN_WEEK_REFERENCE/);
assert.match(html, /id="premium-path-rail"/);
assert.match(client, /document\.addEventListener\('visibilitychange',\(\)=>\{if\(!document.hidden\)load\(\)\}\)/);
assert.match(client, /setInterval\(\(\)=>\{if\(!document.hidden\)load\(\)\},300000\)/);
assert.match(client,/setTimeout\(\(\)=>controller\.abort\(\),10000\)/);
assert.match(client,/signal:controller\.signal/);
assert.match(client,/finally\{clearTimeout\(deadline\);loading=false;refresh\(\)\}/);

assert.match(site,/resolve\(outputDir,"vnext"\)/);
assert.match(site,/await copyFile\(resolve\(siteDir,"vnext-live",file\),resolve\(vnextDir,file\)\)/);
// Price freshness is independent of Compass source expiry; never reuse Pages
// build time or weekly freeze time as fresh hourly close evidence.
const priceStatusSource=client.slice(client.indexOf('function priceSourceAgeStatus('),client.indexOf('function drawStatus(){'));
assert.match(priceStatusSource,/CN_PUBLIC_HOURLY_PRICE_PATH_v1/);
assert.match(html,/id="price-source-warning"/);
const getPriceStatus=new Function('latest','now',priceStatusSource+';return priceSourceAgeStatus(latest,now);');
const priceFixture={public_live_precision:{
 contract:'CN_PUBLIC_LIVE_PRICE_PRECISION_v1',forecast_week:'2026-W43',public_issue_number:30,
 freshness_sla_minutes:90,live_as_of_utc:'2026-10-23T04:00:00Z',
 hourly_price_path:{contract:'CN_PUBLIC_HOURLY_PRICE_PATH_v1',
  semantics:'OBSERVED_HOURLY_CLOSE_NOT_A_PROSPECTIVE_FORECAST',
  source:'HOURLY_SPOT_PASS_ONLY',forecast_week:'2026-W43',public_issue_number:30,
  observed_through_utc:'2026-10-23T04:00:00Z',BTC:[{observed_at_utc:'2026-10-23T04:00:00Z',close:80000}],
  ETH:[{observed_at_utc:'2026-10-23T04:00:00Z',close:2400}]}}};
assert.equal(getPriceStatus(priceFixture,Date.parse('2026-10-23T05:00:00Z')).state,'FRESH');
assert.equal(getPriceStatus(priceFixture,Date.parse('2026-10-23T05:30:00Z')).state,'FRESH');
assert.equal(getPriceStatus(priceFixture,Date.parse('2026-10-23T06:08:00Z')).state,'STALE');
assert.equal(getPriceStatus(priceFixture,Date.parse('2026-10-23T03:59:59Z')).state,'UNAVAILABLE');
for(const mutate of [
 x=>{x.public_live_precision.hourly_price_path.forecast_week='2026-W42'},
 x=>{x.public_live_precision.hourly_price_path.BTC=[]},
 x=>{x.public_live_precision.hourly_price_path.source='SYNTHETIC'},
 x=>{x.public_live_precision.hourly_price_path.observed_through_utc='2026-10-23T03:00:00Z'},
 x=>{x.public_live_precision.freshness_sla_minutes=null}
]){
 const v=structuredClone(priceFixture);mutate(v);
 assert.equal(getPriceStatus(v,Date.parse('2026-10-23T04:30:00Z')).state,'UNAVAILABLE');
}
// Actual status renderer regression: a newer Pages delivery timestamp must
// NEVER disguise the older owner's expired Official Compass freshness.
const statusSlice=client.slice(client.indexOf('function drawStatus(){'),client.indexOf('function drawOverview(){'));
assert.match(statusSlice,/SOURCE_FRESHNESS_EXPIRY_NOT_FORECAST_ETA/);
assert.doesNotMatch(statusSlice,/show\('source-clock',stamp\(feeds\?\.latest\?\.generated_at\)\)/);
const displayStatus=(at,language='da',state='UNAVAILABLE')=>{
 const captured={},fakeFeed={
   latest:{generated_at:'2026-10-20T17:25:58Z'},
   compass:{full_stack:{official_freshness:{
     contract:'OFFICIAL_COMPASS_SOURCE_FRESHNESS_READBACK_v1',
     status:'VERIFIED_OWNER_POLICY',
     semantics:'SOURCE_FRESHNESS_EXPIRY_NOT_FORECAST_ETA',
     valid_until_utc:'2026-10-20T14:00:00Z'
   }}}
 };
 const simulatedDate={now:()=>Date.parse(at),parse:Date.parse};
 new Function('view','feeds','error','tr','stamp','$','show','Date',
   priceStatusSource+statusSlice+'; drawStatus();')(
   {weekly:{state:'DEGRADED'},compass:{state}},
   fakeFeed,false,(da,en)=>language==='en'?en:da,
   utc=>utc,()=>({className:''}),
   (key,val)=>{captured[key]=val},simulatedDate);
 return captured;
};
const afterOwnerExpiry=displayStatus('2026-10-20T17:30:00Z');
assert.match(afterOwnerExpiry['source-status'],/Kompas udløbet/);
assert.match(afterOwnerExpiry['source-clock'],/14:00:00Z/);
assert.doesNotMatch(afterOwnerExpiry['source-clock'],/17:25:58Z/);
const afterOwnerExpiryEnglish=displayStatus('2026-10-20T17:30:00Z','en');
assert.match(afterOwnerExpiryEnglish['source-status'],/Compass expired/);
const beforeExpiryUnaligned=displayStatus('2026-10-20T13:00:00Z');
assert.match(beforeExpiryUnaligned['source-status'],/ikke aktuelt/);
assert.doesNotMatch(beforeExpiryUnaligned['source-status'],/udløbet/);
const eligibleOwner=displayStatus('2026-10-20T13:00:00Z','da','FRESH');
assert.match(eligibleOwner['source-status'],/aktuelt/);

execFileSync(process.execPath,['--check',resolve(dir,'app.mjs')],{stdio:'pipe'});
console.log('PASS vNext: W43 source truth, official freshness, score isolation, negative gates, four-view product shell, i18n and syntax');
