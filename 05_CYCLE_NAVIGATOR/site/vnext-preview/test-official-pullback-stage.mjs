import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { officialPullbackStage } from './official-pullback-stage.mjs';

const seed=JSON.parse(readFileSync(resolve(dirname(fileURLToPath(import.meta.url)),'seed.json'),'utf8'));
const run=(name,fn)=>{fn();console.log('PASS '+name)};
const view=(fn,lang='da')=>{
 const d=structuredClone(seed);
 if(fn)fn(d);
 return officialPullbackStage(d.compass,d.weekly,lang);
};
const editRisk=(state)=>(d)=>{
 d.compass.protection_tracker.pullback_risk_state=state;
 d.compass.protection_tracker.public_explanation=null;
 d.compass.protection_tracker.eta_window='No explicit onset';
};
run('Original frozen W41 BUILDING is a watch, not imminent or automatic sell',()=>{
 const s=view();
 assert.equal(s.contract,'CN_PUBLIC_PULLBACK_STAGE_PRESENTATION_v1');
 assert.equal(s.authority,'PRESENTATION_ONLY');
 assert.equal(s.sourceRiskState,'BUILDING');
 assert.equal(s.ordinalRiskClass,1);
 assert.match(s.stageLabel,/Opbygning/);
 assert.match(s.etaLabel,/7.*11.*41/);
 assert.match(s.proximityLabel,/ikke dokumenteret/);
 assert.equal(s.sellPermission,false);
 assert.equal(s.confirmedMarketDecline,false);
 assert.equal(s.alertQualified,null);
});
run('5 governed severity statuses map to editorial source names with no inevitability or new odds',()=>{
 const cases=[
  ['NORMAL',0,/ingen aktiv varsling/],
  ['BUILDING',1,/Opbygning/],
  ['ELEVATED',2,/Forhøjet/],
  ['HIGH',3,/Høj risiko/],
  ['CONFIRMED',4,/Bekræftet risikotilstand/]
 ];
 for(const [state,ordinal,re] of cases) {
  const x=view(editRisk(state));
  assert.equal(x.sourceRiskState,state);
  assert.equal(x.ordinalRiskClass,ordinal);
  assert.match(x.stageLabel,re);
  assert.match(x.proximityLabel,/ikke dokumenteret/);
  assert.equal(x.sellPermission,false);
  assert.equal(x.confirmedMarketDecline,false);
  assert.equal(x.qualitySemantics,'EVIDENCE_QUALITY_NOT_PROBABILITY');
 }
});
run('NORMAL with week context does not manufacture imminent retest',()=>{
 const s=view(editRisk('NORMAL'));
 assert.equal(s.windowKind,'NO_ACTIVE_WATCH');
 assert.match(s.etaLabel,/Ingen aktiv/);
});
run('Qualitative LOW/MEDIUM/HIGH explicitly labels evidence quality, not probability',()=>{
 for(const [q,re] of [['LOW',/Lav evidens/],['MEDIUM',/Middel evidens/],['HIGH',/Høj evidens/]]) {
  const s=view(d=>{d.compass.protection_tracker.confidence_quality=q});
  assert.match(s.qualityLabel,re);
  assert.equal(s.qualitySemantics,'EVIDENCE_QUALITY_NOT_PROBABILITY');
 }
 const s=view(d=>{d.compass.protection_tracker.confidence_quality='90%'});
 assert.match(s.qualityLabel,/ukendt/);
});
run('DA and EN label the exact same official risk and window, no invented signal',()=>{
 const a=view(null,'da'),b=view(null,'en');
 assert.equal(a.ordinalRiskClass,b.ordinalRiskClass);
 assert.equal(a.sourceRiskState,b.sourceRiskState);
 assert.equal(a.windowKind,b.windowKind);
 assert.match(b.stageLabel,/Building/);
 assert.match(b.proximityLabel,/not evidenced/);
 assert.match(b.qualityLabel,/Low evidence/);
});
run('W42 typed no-onset delivers week warning without fake imminent countdown',()=>{
 const s=view(d=>{
   d.weekly.forecast_week='2026-W42';
   const p=d.compass.protection_tracker;
   p.pullback_risk_state='ELEVATED';
   p.public_explanation={contract:'CN_PUBLIC_PROTECTION_COPY_v1',
     forecast_week:'2026-W42',risk_state:'ELEVATED',
     onset_start_utc:null,onset_end_utc:null};
 });
 assert.equal(s.windowKind,'WEEK_ONLY');
 assert.equal(s.ordinalRiskClass,2);
 assert.match(s.etaLabel,/uge 42.*ingen præcis ETA/);
 assert.match(s.proximityLabel,/ikke dokumenteret/);
 assert.equal(s.sellPermission,false);
});
run('Valid future source window still does NOT become imminent probability',()=>{
 const s=view(d=>{
   d.weekly.forecast_week='2026-W42';
   const p=d.compass.protection_tracker;
   p.pullback_risk_state='HIGH';
   p.public_explanation={contract:'CN_PUBLIC_PROTECTION_COPY_v1',
     forecast_week:'2026-W42',risk_state:'HIGH',
     onset_start_utc:'2026-10-14T00:00:00Z',
     onset_end_utc:'2026-10-16T23:59:59Z'};
 });
 assert.equal(s.windowKind,'GOVERNED_PROSPECTIVE_WINDOW');
 assert.match(s.etaLabel,/Prognosevindue/);
 assert.match(s.proximityLabel,/ikke dokumenteret/);
 assert.equal(s.confirmedMarketDecline,false);
});
run('Unhealthy/unavailable/forged source cannot claim any progressive stage',()=>{
 for(const modify of [
  d=>{d.compass.data_status='DEGRADED';},
  d=>{d.compass.protection_tracker.contract='BROWSER_PREDICTION';},
  d=>{d.compass.protection_tracker.authority.new_market_classifier=true;},
  editRisk('UNAVAILABLE'),
  editRisk('SURE_DIP_IN_2_HOURS')
 ]) {
  const x=view(modify);
  assert.equal(x.status,'UNAVAILABLE');
  assert.equal(x.ordinalRiskClass,null);
  assert.equal(x.sellPermission,false);
  assert.equal(x.alertQualified,null);
 }
});
run('Source input and frozen bytes are unchanged',()=>{
 const before=JSON.stringify(seed);
 officialPullbackStage(seed.compass,seed.weekly,'en');
 assert.equal(JSON.stringify(seed),before);
});
console.log('SUCCESS: 9 progressive-risk presentation tests; no future price, onset, probability or trade permission predicted.');
