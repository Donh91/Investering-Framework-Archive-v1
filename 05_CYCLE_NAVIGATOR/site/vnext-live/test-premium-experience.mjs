/* Product alignment executable negatives. Synthetic fixtures ONLY; no seeded market claims. */
import assert from 'node:assert/strict';
import {decisionModel,pathModel,publicAuditPrompt,riskStageLabel,priceSequenceModel} from './premium-experience.mjs';
const bullBear={
 contract:'OFFICIAL_COMPASS_BULL_BEAR_DISPLAY_v1',
 semantics:'EVIDENCE_BALANCE_NOT_PROBABILITY',
 resolution:'COARSE_CATEGORICAL_DIRECTION',mapping_version:'DIRECTION_ONLY_COARSE_v1',
 owner:'OFFICIAL_COMPASS',source_of_truth_contract:'MARKET_WEATHER_SOURCE_OF_TRUTH_v1',
 authority:{site_synthesis_allowed:false,new_market_classifier:false,probability_model:false,portfolio_execution:false},
 horizons:{'1_3d':{status:'OK',bull:5,bear:5,bias:'NEUTRAL'}}
};
const official={
 contract:'PUBLIC_COMPASS_PROJECTION_v1',data_status:'OK',
 horizons:{NEXT_12H:{expected_direction:'MIXED'}},
 bull_bear_scale:bullBear,
 protection_tracker:{
  contract:'COMPASS_PROTECTION_TRACKER_v1',
  authority:{new_market_classifier:false,portfolio_execution:false},
  pullback_risk_state:'ELEVATED',distribution_risk:'UNKNOWN',confidence_quality:'LOW',
  reentry_state:'UNAVAILABLE'
 },
 sell_assessment:{state:'UNAVAILABLE'}
};
const keys=['BTC','ETH','LARGE_MID','ALT_IGNITION','MICRO','BROAD','MANIA','DISTRIBUTION','PROTECTION','REENTRY'];
const view={
 weekly:{forecast_week:'2026-W43',public_issue_number:30},
 compass:{state:'FRESH',permit_path_live_gates:true,action_now:'HOLD_WAIT',compass_id:'CMP-TEST-W43'},
 path:{state:'SOURCE_BOUND',source_issue:30,source_week:'2026-W43',source_identity:'CMP-TEST-W43',
  current_checkpoint:{key:'BTC',label:'BTC leadership',status:'FROZEN_WEEK_REFERENCE'},
  next_checkpoint:{key:'ETH',label:'ETH leadership'},
  next_gate:'ETH/BTC still needs confirmation',
  source_label:'CN30 / 2026-W43',
  altseason:{target:'Altseason ignition',status:'WATCH_ONLY'},
  full_phases:keys.map((key,index)=>({key,label:key,index,status:'REFERENCE_ONLY'})),
  rotation:[{key:'BTC',action:'HOLD',eta:'now'},{key:'MEMES',action:'UNAVAILABLE',eta:null}]
 }
};
const now=decisionModel(view,official,'da');
assert.equal(now.eligible,true);
assert.equal(now.action,'HOLD_WAIT');
assert.equal(now.direction,'MIXED');
assert.equal(now.bull,5);
assert.equal(now.bear,5);
assert.equal(now.bias,'NEUTRAL');
assert.equal(now.riskIndex,2);
assert.equal(now.riskState,'ELEVATED');
assert.equal(now.sell,'UNAVAILABLE');
assert.equal(now.distribution,'UNKNOWN');
assert.notEqual(now.riskWindow,'UNAVAILABLE');
const en=decisionModel(view,official,'en');
assert.match(en.riskLabel,/Elevated/);
const stale=structuredClone(view);stale.compass.state='UNAVAILABLE';
const staleDecision=decisionModel(stale,official,'da');
assert.equal(staleDecision.eligible,false);
assert.equal(staleDecision.action,'UTILGÆNGELIG');
assert.equal(staleDecision.bull,null);
assert.equal(staleDecision.riskIndex,-1);
assert.equal(staleDecision.sell,'UTILGÆNGELIG');
const unjoined=structuredClone(view);unjoined.compass.permit_path_live_gates=false;
assert.equal(decisionModel(unjoined,official).eligible,false);
const forged=structuredClone(official);forged.bull_bear_scale.horizons['1_3d'].bull=7;
assert.equal(decisionModel(view,forged).bull,null,'Invalid scale must not create false evidence');
const notAllowed=structuredClone(official);notAllowed.protection_tracker.authority.portfolio_execution=true;
assert.equal(decisionModel(view,notAllowed).riskIndex,-1,'A future trade-authority escalation must fail shut');
const safety=structuredClone(official);safety.protection_tracker.pullback_risk_state='HIGH';
assert.equal(decisionModel(view,safety).riskIndex,3);
assert.equal(decisionModel(view,safety).sell,'UNAVAILABLE','Pullback HIGH does not confer SELL');
const p=pathModel(view,'en');
assert.equal(p.eligible,true);
assert.equal(p.phases.length,10);
assert.equal(p.phases[0].kind,'reference');
assert.equal(p.phases[1].kind,'next');
assert.equal(p.phases[2].kind,'unverified');
assert.equal(p.rotation[1].action,'UNAVAILABLE','MEMES do not inherit MICRO');
assert.match(p.source,/CN #30 · 2026-W43 · CMP-TEST-W43/,'Readback must show original source identity, not a nonexistent adapter label');
assert.equal(p.rotation[1].eta,'No verified ETA');
const wrongIdentity=structuredClone(view);wrongIdentity.path.source_identity='CMP-FORGED';
assert.equal(pathModel(wrongIdentity,'en').eligible,false,'Wrong Compass source must not promote path');
const wrongIssue=structuredClone(view);wrongIssue.path.source_issue=31;
assert.equal(pathModel(wrongIssue,'en').eligible,false,'Wrong public CN number must not promote path');
const wrongWeek=structuredClone(view);wrongWeek.path.source_week='2026-W42';
assert.equal(pathModel(wrongWeek,'en').eligible,false,'Historic source week must not be promoted live');
const pStale=pathModel(stale,'en');
assert.equal(pStale.eligible,false);
assert.equal(pStale.now,'Current cycle phase unverified');
assert.equal(pStale.phases.every(x=>x.kind==='unverified'),true);
assert.deepEqual(pStale.rotation,[],'An expired Compass cannot show live action tiers');
const pInvalid=structuredClone(view);pInvalid.path.full_phases=pInvalid.path.full_phases.slice(0,5);
assert.equal(pathModel(pInvalid,'en').eligible,false,'Truncated official phase output cannot be promoted live');
assert.equal(pathModel(pInvalid,'en').phases.length,10,'A source-loss fallback keeps the ten canonical reference phases');
assert.ok(pathModel(pInvalid,'en').phases.every(x=>x.kind==='unverified'));
const noSourcePath=structuredClone(view);noSourcePath.path={state:'UNAVAILABLE',full_phases:[]};
assert.equal(pathModel(noSourcePath,'da').phases.length,10,'Expired source must preserve the neutral 10-stage map');
assert.equal(pathModel(noSourcePath,'da').now,'Aktuel cyklusfase ikke verificeret');
assert.deepEqual(pathModel(noSourcePath,'da').rotation,[]);
assert.equal(riskStageLabel('BUILDING','da'),'Opbygning');
assert.equal(riskStageLabel('BUILDING','en'),'Building');
assert.equal(riskStageLabel('CONFIRMED','da'),'Bekræftet');
assert.equal(riskStageLabel('MAGIC','da'),'UNAVAILABLE');
const prompt=publicAuditPrompt('da');
for(const needed of ['scorebook-index.json','source_commit','SHA-256','ABSTAIN','VERIFIED','CycleNavigator-scores']){
 assert.ok(prompt.includes(needed),'AI verification prompt missing '+needed);
}
assert.doesNotMatch(prompt,/OPENAI_API_KEY|private key|seed\.json/);
console.log('PASS 27 source-authority and source-loss premium experience assertions');


// Verified owner-published D1–2 / D3–4 / D5–7 provisional price evidence.
 // Distinct from settled weekly Price Range and future Direction/Pullback Edge.
const precisionFixture={
 public_live_precision:{
  contract:'CN_PUBLIC_LIVE_PRICE_PRECISION_v1',
  authority:'PUBLIC_FORECAST_ACCOUNTABILITY_ONLY_NO_PORTFOLIO_AUTHORITY',
  score_family:'PRICE_RANGE_PRECISION',formula:'70pct_containment_plus_30pct_jaccard',
  forecast_week:'2026-W43',public_issue_number:30,
  live_as_of_utc:'2026-10-23T04:00:00Z',freshness_sla_minutes:90,
  window_scores:{
   day_1_2:{phase:'COMPLETE',score_to_date:72.5,rows_scored:2,rows_total:2,
    observed_hours:48,expected_hours_final:48,coverage_complete_to_date:true},
   day_3_4:{phase:'LIVE',score_to_date:63.2,rows_scored:2,rows_total:2,
    observed_hours:42,expected_hours_final:48,coverage_complete_to_date:true},
   day_5_7:{phase:'NOT_STARTED',score_to_date:null,rows_scored:0,rows_total:2,
    observed_hours:0,expected_hours_final:72,coverage_complete_to_date:false}
  }
 }
};
const snapshotAt=Date.parse('2026-10-23T05:00:00Z');
const sequence=priceSequenceModel(view,precisionFixture,snapshotAt);
assert.equal(sequence.state,'FRESH');
assert.equal(sequence.week,'2026-W43');
assert.equal(sequence.windows.length,3);
assert.deepEqual(sequence.windows.map(x=>x.score),[72.5,63.2,null]);
assert.deepEqual(sequence.windows.map(x=>x.state),['CLOSED_PROVISIONAL','LIVE_PROVISIONAL','PENDING']);
const later=priceSequenceModel(view,precisionFixture,Date.parse('2026-10-23T06:08:00Z'));
assert.equal(later.state,'STALE');
assert.ok(later.windows.every(x=>x.score===null),'Stale rows cannot appear as live scores');
const badWeek=structuredClone(precisionFixture);
badWeek.public_live_precision.forecast_week='2026-W42';
assert.equal(priceSequenceModel(view,badWeek,snapshotAt).state,'UNAVAILABLE');
const badFamily=structuredClone(precisionFixture);
badFamily.public_live_precision.score_family='PULLBACK_EDGE';
assert.equal(priceSequenceModel(view,badFamily,snapshotAt).state,'UNAVAILABLE');
const partial=structuredClone(precisionFixture);
partial.public_live_precision.window_scores.day_3_4.rows_scored=1;
assert.equal(priceSequenceModel(view,partial,snapshotAt).windows[1].score,null);
const corrupted=structuredClone(precisionFixture);
corrupted.public_live_precision.window_scores.day_1_2.score_to_date=110;
assert.equal(priceSequenceModel(view,corrupted,snapshotAt).windows[0].score,null);
assert.equal(priceSequenceModel(view,precisionFixture,Date.parse('2026-10-23T03:00:00Z')).state,'UNAVAILABLE');
console.log('PASS source-joined live price-range sequences, stale/partial/future/source negatives');
