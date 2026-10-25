/* Kompas PRO v1: synthetic owner-state negative controls, NO market data. */
import assert from 'node:assert/strict';
import {compassProReadback,compassProLabels} from './compass-pro-readback.mjs';

const view={
 compass:{state:'FRESH',permit_path_live_gates:true,compass_id:'CMP-TEST-PRO',action_now:'HOLD_WAIT'},
 weekly:{state:'DEGRADED',forecast_week:'2026-W43',public_issue_number:30,
  btc_range:{low:77000,high:86500},eth_range:{low:2150,high:2600}}
};
const official={
 contract:'PUBLIC_COMPASS_PROJECTION_v1',data_status:'OK',
 compass_id:'CMP-TEST-PRO',issued_at_utc:'2026-10-25T10:00:00Z',
 weekly_context:{status:'ALIGNED',forecast_week:'2026-W43',public_issue_number:30},
 action_now:'HOLD_WAIT',horizons:{NEXT_1_3D:{eta:'24-72h'}},
 protection_tracker:{
  contract:'COMPASS_PROTECTION_TRACKER_v1',
  authority:{new_market_classifier:false,portfolio_execution:false,wallet_specific:false},
  pullback_risk_state:'ELEVATED',confidence_quality:'LOW',distribution_risk:'UNKNOWN',
  reentry_state:'INACTIVE',
  public_explanation:{
   contract:'CN_PUBLIC_PROTECTION_COPY_v1',forecast_week:'2026-W43',
   risk_state:'ELEVATED',onset_start_utc:null,onset_end_utc:null}
 },
 sell_assessment:{
  contract:'COMPASS_SELL_ASSESSMENT_v1',state:'UNAVAILABLE',
  authority:{new_sell_rule:false,portfolio_execution:false,protection_is_sell_authority:false}
 }
};
const at='2026-10-25T12:00:00Z';
const run=(v=view,c=official,nowUtc=at,lang='da')=>compassProReadback(v,c,{nowUtc,lang});
const good=run();
assert.equal(good.contract,'CN_KOMPAS_PRO_PRESENTATION_v1');
assert.equal(good.status,'OFFICIAL_SOURCE_BOUND');
assert.equal(good.severity,3);
assert.equal(good.evidenceQuality,'Lav');
assert.equal(good.onsetEta,'Ikke dokumenteret','A week-only watch is not onset ETA');
assert.equal(good.depth,'Ikke kvantificeret','Do not infer max drawdown from weekly range');
assert.equal(good.eventProbability,'Ikke kalibreret','Evidence quality is NOT event probability');
assert.match(good.nextReview,/24–72/);
assert.match(good.watchWindow,/uge 43/,'Source watch is separate from onset ETA');
assert.equal(good.sell,'UNAVAILABLE','No SELL decision owner');
assert.equal(good.reentry,'INACTIVE');
assert.match(good.guidance,/trimliste/,'Planning aid only, not official SELL');
assert.equal(good.guidanceKind,'NONBINDING_PREDEFINED_CHECKLIST');
assert.equal(good.sourceWeekly.status,'FROZEN_CURRENT_WEEK');
assert.deepEqual(good.sourceWeekly.btc,{low:77000,high:86500});
assert.deepEqual(good.sourceWeekly.eth,{low:2150,high:2600});
assert.equal(good.forecastRows.length,5);
for(const row of good.forecastRows){
 assert.equal(row.status,'NOT_ISSUED');
 assert.equal(row.btc,null,'Weekly range must not become a horizon forecast');
 assert.equal(row.eth,null);
}
assert.equal(compassProLabels('da').depth,'FORVENTET FALDDYBDE');
assert.equal(compassProLabels('en').depth,'EXPECTED DRAWDOWN');
assert.equal(run(view,official,at,'en').evidenceQuality,'Low');

const high=structuredClone(official);
high.protection_tracker.pullback_risk_state='HIGH';
high.protection_tracker.public_explanation.risk_state='HIGH';
const highResult=run(view,high);
assert.equal(highResult.severity,4);
assert.equal(highResult.sell,'UNAVAILABLE','HIGH cannot confer SELL');
assert.match(highResult.guidance,/automatisk SELL/);

const stale=structuredClone(view);stale.compass.state='UNAVAILABLE';
const stopped=run(stale);
assert.equal(stopped.status,'UNAVAILABLE');
assert.equal(stopped.severity,null);
assert.equal(stopped.sourceWeekly.btc,null,'Stale compass must not show current price authority');
const wrongId=structuredClone(official);wrongId.compass_id='CMP-OTHER';
assert.equal(run(view,wrongId).status,'UNAVAILABLE');
const wrongWeek=structuredClone(official);wrongWeek.weekly_context.forecast_week='2026-W42';
assert.equal(run(view,wrongWeek).status,'UNAVAILABLE');
const wrongIssue=structuredClone(official);wrongIssue.weekly_context.public_issue_number=29;
assert.equal(run(view,wrongIssue).status,'UNAVAILABLE');
const wrongAction=structuredClone(official);wrongAction.action_now='SELL';
assert.equal(run(view,wrongAction).status,'UNAVAILABLE','Different published official action must fail closed');
const futureAction=structuredClone(official),futureView=structuredClone(view);
futureAction.action_now='HOLD_DEFENSIVE_WAIT';futureView.compass.action_now='HOLD_DEFENSIVE_WAIT';
assert.equal(run(futureView,futureAction).status,'OFFICIAL_SOURCE_BOUND',
 'New source-matching official actions must not blank the protection radar');
assert.equal(run(futureView,futureAction).sell,'UNAVAILABLE',
 'A new official action code must not grant SELL without the owner');
const mismatchedWeekly=structuredClone(view);mismatchedWeekly.weekly.state='MISMATCH';
assert.equal(run(mismatchedWeekly).sourceWeekly.btc,null,
 'A mismatched weekly source cannot display original frozen ranges');

const seller=structuredClone(official);
seller.sell_assessment.state='SELL';
seller.sell_assessment.authority.portfolio_execution=true;
assert.equal(run(view,seller).sell,'Ikke tilgængelig','Cannot show unverified SELL capability');

const forgedWindow=structuredClone(official);
forgedWindow.protection_tracker.public_explanation.onset_start_utc='2026-10-30T13:00:00Z';
forgedWindow.protection_tracker.public_explanation.onset_end_utc='2026-10-30T19:00:00Z';
assert.equal(run(view,forgedWindow).onsetEta,'Ikke dokumenteret',
 'Onset dated outside the forecast week must be rejected');
const realWindow=structuredClone(official);
realWindow.protection_tracker.public_explanation.onset_start_utc='2026-10-25T20:00:00Z';
realWindow.protection_tracker.public_explanation.onset_end_utc='2026-10-25T22:00:00Z';
assert.match(run(view,realWindow).onsetEta,/25/,'Only governed typed prospective window can show ETA');
const retro=structuredClone(realWindow);
retro.protection_tracker.public_explanation.onset_start_utc='2026-10-24T20:00:00Z';
assert.equal(run(view,retro).onsetEta,'Ikke dokumenteret',
 'An onset window earlier than the forecast issue is not prospective');

const monday=run(view,official,'2026-10-26T10:00:00Z');
assert.equal(monday.sourceWeekly.status,'HISTORICAL_FROZEN_WEEK');
assert.equal(monday.onsetEta,'Ikke dokumenteret');
assert.match(monday.watchWindow,/Ingen aktuelt/,'Never reissue last week ETA as live');
console.log('PASS Kompas PRO source-bound UI, missing sell/depth/ETA, source mismatch, chronology and archived-week negatives');
