import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { officialPullbackDisplay } from './official-pullback-eta.mjs';

const base=dirname(fileURLToPath(import.meta.url));
const seed=JSON.parse(readFileSync(resolve(base,'seed.json'),'utf8'));
const clean=()=>structuredClone(seed);
let count=0;
const run=(name,fn)=>{fn();count++;console.log('PASS',name)};
const view=(edit,lang='da')=>{const x=clean();if(edit)edit(x);return officialPullbackDisplay(x.compass,x.weekly,lang)};

run('W41 canonical archive shows only the possible Day 3–7 date window, never event onset',()=>{
  const p=view();
  assert.equal(p.state,'VALID');
  assert.equal(p.riskState,'BUILDING');
  assert.equal(p.sourceWeek,'2026-W41');
  assert.equal(p.windowKind,'ARCHIVED_SCENARIO_DAY_WINDOW');
  assert.equal(p.windowStartUtc,'2026-10-07');
  assert.equal(p.windowEndUtc,'2026-10-11');
  assert.equal(p.exactOnset,false);
  assert.match(p.headline,/7.*11.*41/);
  assert.match(p.note,/Historisk/);
  assert.match(p.note,/Ikke SELL/);
});

run('Archive English label is an uncertainty, not a guaranteed dip forecast',()=>{
  const p=view(null,'en');
  assert.match(p.headline,/Possible window/);
  assert.match(p.note,/Historic source scenario/);
  assert.match(p.note,/Not SELL/);
});

function makeWeek42(x) {
 x.weekly.forecast_week='2026-W42';
 x.compass.protection_tracker.pullback_risk_state='ELEVATED';
 x.compass.protection_tracker.eta_window='Possible renewed retest during W42; onset timing is unsupported.';
 x.compass.protection_tracker.public_explanation={
   contract:'CN_PUBLIC_PROTECTION_COPY_v1',
   forecast_week:'2026-W42',
   risk_state:'ELEVATED',
   onset_start_utc:null,
   onset_end_utc:null
 };
}

run('W42 official risk with null start/end is WEEK_ONLY, not false precise dates',()=>{
 const p=view(makeWeek42);
 assert.equal(p.windowKind,'WEEK_ONLY');
 assert.equal(p.riskState,'ELEVATED');
 assert.equal(p.exactOnset,false);
 assert.equal(p.windowStartUtc,null);
 assert.equal(p.windowEndUtc,null);
 assert.match(p.headline,/uge 42.*ingen præcis ETA/);
 assert.match(p.note,/Start\/slut.*ikke kvantificeret/);
});
run('W42 English has week context but no fictitious onset',()=>{
 const p=view(makeWeek42,'en');
 assert.match(p.headline,/week 42.*no precise ETA/);
 assert.match(p.note,/Watch only/);
});
run('Governed future structured onset window is display-only not guaranteed event',()=>{
 const p=view(x=>{
   makeWeek42(x);
   x.compass.protection_tracker.public_explanation.onset_start_utc='2026-10-14T00:00:00Z';
   x.compass.protection_tracker.public_explanation.onset_end_utc='2026-10-16T23:59:59Z';
 });
 assert.equal(p.windowKind,'GOVERNED_PROSPECTIVE_WINDOW');
 assert.equal(p.windowStartUtc,'2026-10-14T00:00:00Z');
 assert.equal(p.windowEndUtc,'2026-10-16T23:59:59Z');
 assert.equal(p.exactOnset,false);
 assert.match(p.note,/faktisk start\/slut er ikke bekræftet/);
});
run('Partial date pair cannot create misleading ETA',()=>{
 const p=view(x=>{makeWeek42(x);x.compass.protection_tracker.public_explanation.onset_start_utc='2026-10-14T00:00:00Z'});
 assert.equal(p.windowKind,'INVALID_DATE_PAIR');
 assert.equal(p.windowStartUtc,null);
});
run('Backward date pair must not be shown',()=>{
 const p=view(x=>{makeWeek42(x);x.compass.protection_tracker.public_explanation.onset_start_utc='2026-10-17T00:00:00Z';x.compass.protection_tracker.public_explanation.onset_end_utc='2026-10-14T00:00:00Z'});
 assert.equal(p.windowKind,'INVALID_DATE_PAIR');
});
run('Timestamp without explicit UTC Z may not be promoted to an ETA',()=>{
 const p=view(x=>{makeWeek42(x);x.compass.protection_tracker.public_explanation.onset_start_utc='2026-10-14';x.compass.protection_tracker.public_explanation.onset_end_utc='2026-10-16'});
 assert.equal(p.windowKind,'INVALID_DATE_PAIR');
});
run('No structured contract / mismatched week/risk returns a warning of source mismatch',()=>{
 for(const modify of [
  x=>{x.compass.protection_tracker.public_explanation.contract='OWN_UNVERIFIED';},
  x=>{x.compass.protection_tracker.public_explanation.forecast_week='2026-W41';},
  x=>{x.compass.protection_tracker.public_explanation.risk_state='NORMAL';}
 ]) {
  const p=view(x=>{makeWeek42(x);modify(x)});
  assert.equal(p.windowKind,'SOURCE_MISMATCH');
  assert.equal(p.windowStartUtc,null);
  assert.match(p.headline,/ikke verificeret/);
 }
});
run('Wrong source week prevents the archive Day3–7 mapping',()=>{
 const p=view(x=>{x.weekly.forecast_week='2026-W42'});
 assert.equal(p.windowKind,'NO_SUPPORTED_ONSET');
 assert.equal(p.windowStartUtc,null);
});
run('Unsupported or prose-only variations cannot manufacture ordinal dates',()=>{
 for(const value of ['Possible W41 retest on Day 3–7','Possible W41 retest, particularly Day 7–3; timing and occurrence unconfirmed.','Likely W41 pullback tomorrow','Day 1-7']) {
  const p=view(x=>{x.compass.protection_tracker.eta_window=value});
  assert.equal(p.windowKind,'NO_SUPPORTED_ONSET');
  assert.equal(p.windowStartUtc,null);
 }
});
run('No source + invalid authority fail closed',()=>{
 for(const alter of [
   x=>{x.compass.data_status='DEGRADED';},
   x=>{x.compass.protection_tracker.contract='UNTRUSTED';},
   x=>{x.compass.protection_tracker.authority.portfolio_execution=true;},
   x=>{x.compass.protection_tracker.authority.new_market_classifier=true;},
   x=>{x.weekly.forecast_week='2026-W99';},
   x=>{x.compass.protection_tracker.pullback_risk_state='SELL_NOW';}
 ]) {
  const p=view(alter);
  assert.equal(p.state,'UNAVAILABLE');
  assert.equal(p.windowStartUtc,null);
  assert.equal(p.riskState,'UNAVAILABLE');
 }
});
run('Official NORMAL state is NO ACTIVE WARNING and may not infer weekly downside',()=>{
 const p=view(x=>{x.compass.protection_tracker.pullback_risk_state='NORMAL';x.compass.protection_tracker.eta_window='UNKNOWN'});
 assert.equal(p.state,'VALID');
 assert.equal(p.windowKind,'NO_ACTIVE_WATCH');
 assert.match(p.headline,/Ingen aktiv pullback-watch/);
 assert.equal(p.windowStartUtc,null);
 assert.equal(p.windowEndUtc,null);
});
run('Official UNAVAILABLE risk state cannot be promoted to an ETA or an active warning',()=>{
 const p=view(x=>{x.compass.protection_tracker.pullback_risk_state='UNAVAILABLE'});
 assert.equal(p.state,'UNAVAILABLE');
 assert.equal(p.windowStartUtc,null);
 assert.equal(p.windowKind,'UNAVAILABLE');
});
run('Forecast week input/official Compass remains immutable',()=>{
 const before=JSON.stringify(seed);
 view();
 view(null,'en');
 assert.equal(JSON.stringify(seed),before);
});
console.log('SUCCESS: '+count+' ETA and pullback time-window contract tests. No independent warning or SELL is generated.');
