/* Product alignment executable negatives. Synthetic fixtures ONLY; no seeded market claims. */
import assert from 'node:assert/strict';
import {decisionModel,pathModel,publicAuditPrompt} from './premium-experience.mjs';
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
assert.deepEqual(pathModel(pInvalid,'en').phases,[],'Partial cycle ladder cannot pretend to be ten phases');
const prompt=publicAuditPrompt('da');
for(const needed of ['scorebook-index.json','source_commit','SHA-256','ABSTAIN','VERIFIED','CycleNavigator-scores']){
 assert.ok(prompt.includes(needed),'AI verification prompt missing '+needed);
}
assert.doesNotMatch(prompt,/OPENAI_API_KEY|private key|seed\.json/);
console.log('PASS 27 source-authority and source-loss premium experience assertions');
