import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { officialPullbackInvestorView } from './official-pullback-investor-view.mjs';

const base=dirname(fileURLToPath(import.meta.url));
const frozen=JSON.parse(readFileSync(resolve(base,'seed.json'),'utf8'));
const view=(change,locale='da')=>{
 const d=structuredClone(frozen);
 if(change)change(d);
 return officialPullbackInvestorView(d.compass,d.weekly,locale);
};
const row=(v,k)=>v.rows.find(x=>x.id===k);
let n=0;const run=(label,fn)=>{fn();console.log('PASS',++n,label)};

run('W41 original buyer-facing possible ETA is source-derived, NOT guaranteed',()=>{
 const v=view();
 assert.equal(v.contract,'CN_PULLBACK_INVESTOR_DISCLOSURE_v1');
 assert.equal(v.status,'VALID');
 assert.equal(v.source_risk_state,'BUILDING');
 assert.equal(v.rows.length,10);
 assert.match(row(v,'eta').value,/7.*11.*41/);
 assert.equal(row(v,'eta').source,'OFFICIAL_COMPASS');
});
run('No unsupported 1–10 likelihood ever appears',()=>{
 const v=view();
 assert.equal(row(v,'likelihood').source,'NOT_CALIBRATED');
 assert.match(row(v,'likelihood').value,/Ikke kalibreret/);
 assert.doesNotMatch(row(v,'likelihood').value,/\b[1-9]\/10\b|\d{2}%/);
});
run('No guessed price magnitude, altcoin beta or recovery ETA',()=>{
 const v=view();
 assert.equal(row(v,'magnitude').source,'UNQUANTIFIED');
 assert.equal(row(v,'alt_impact').source,'UNQUANTIFIED');
 assert.equal(row(v,'duration').source,'UNASSESSED');
 assert.match(row(v,'alt_impact').value,/micro\/memes/);
});
run('2–3 week and 4–8 week horizon remain distinct official directions or UNKNOWN',()=>{
 const v=view();
 for(const [rowID,horizon] of [['weeks_2_3','NEXT_2_3W'],['weeks_4_8','CYCLE_ALTCOINS_3_8W']]) {
  const raw=frozen.compass.horizons[horizon]?.expected_direction;
  if(['UP','DOWN','MIXED','SIDEWAYS','NEUTRAL'].includes(raw))assert.ok(row(v,rowID).value.startsWith(raw+' · '));
  else assert.match(row(v,rowID).value,/Ingen verificeret/);
  assert.doesNotMatch(row(v,rowID).value,/SELL NOW|EXIT ALL/);
 }
});
run('No actual bear regime inferred from current risk state',()=>{
 for(const state of ['NORMAL','BUILDING','ELEVATED','HIGH','CONFIRMED']) {
  const v=view(d=>{d.compass.protection_tracker.pullback_risk_state=state;delete d.compass.protection_tracker.public_explanation});
  assert.equal(v.status,'VALID');
  assert.equal(row(v,'bear_transition').source,'NOT_CLASSIFIED');
  assert.match(row(v,'bear_transition').value,/ikke automatisk bear/);
 }
});
run('Current W42 typed explanation can provide source-only watch_for and weakens_if',()=>{
 const v=view(d=>{
  d.weekly.forecast_week='2026-W42';
  const p=d.compass.protection_tracker;
  p.pullback_risk_state='ELEVATED';
  p.public_explanation={contract:'CN_PUBLIC_PROTECTION_COPY_v1',forecast_week:'2026-W42',risk_state:'ELEVATED',
   onset_start_utc:null,onset_end_utc:null,
   watch_for:'Observe recovery breadth and ETH/BTC for source-owned confirmation.',
   weakens_if:'Recovery holds with strengthening market participation.'};
 });
 assert.match(row(v,'eta').value,/uge 42.*ingen præcis ETA/);
 assert.equal(row(v,'watch_for').source,'SOURCE_PUBLIC_EXPLANATION');
 assert.match(row(v,'watch_for').value,/Observe recovery/);
 assert.match(row(v,'weakens_if').value,/Recovery holds/);
 assert.equal(row(v,'likelihood').source,'NOT_CALIBRATED');
});
run('Wrong weekly explanation cannot be imported into current investor view',()=>{
 const v=view(d=>{
  d.compass.protection_tracker.public_explanation={
   contract:'CN_PUBLIC_PROTECTION_COPY_v1',forecast_week:'2026-W42',risk_state:'BUILDING',
   watch_for:'Use leaked future outcomes',weakens_if:'Use future close'
  };
 });
 assert.equal(v.status,'UNAVAILABLE');
 assert.equal(row(v,'eta').source,'UNAVAILABLE');
 assert.notEqual(row(v,'watch_for').value,'Use leaked future outcomes');
});
run('Corrupt source health blocks all owner-based horizon and ETA implications',()=>{
 const v=view(d=>{d.compass.data_status='DEGRADED'});
 assert.equal(v.status,'UNAVAILABLE');
 for(const k of ['eta','weeks_2_3','weeks_4_8','watch_for','weakens_if'])assert.equal(row(v,k).source,'UNAVAILABLE');
});
run('Internationalization changes labels, never owner-raw forecast',()=>{
 const a=view(null,'da'),b=view(null,'en');
 assert.deepEqual(a.rows.map(x=>x.id),b.rows.map(x=>x.id));
 assert.equal(a.source_risk_state,b.source_risk_state);
 assert.equal(row(a,'likelihood').source,row(b,'likelihood').source);
 assert.equal(row(b,'likelihood').value,'Not calibrated · no valid 1–10 score');
 assert.match(row(b,'alt_impact').value,/No validated/);
});
run('Private/wallet/position specifics never read or mutated',()=>{
 const before=JSON.stringify(frozen);
 const v=view(d=>{d.compass.wallet='private';d.compass.user_positions=[{token:'SECRET'}]});
 assert.ok(!JSON.stringify(v).includes('SECRET'));
 assert.ok(!JSON.stringify(v).includes('private'));
 assert.equal(JSON.stringify(frozen),before);
});
console.log('SUCCESS: '+n+' source-only investor drilldown tests with honest absent 1–10/size/alt/market regime.');
