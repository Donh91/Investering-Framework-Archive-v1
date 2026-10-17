import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';

const premium=await readFile(new URL('../market-compass-premium.js',import.meta.url),'utf8');
const header=await readFile(new URL('../public-product.js',import.meta.url),'utf8');
const builder=await readFile(new URL('../build-public.mjs',import.meta.url),'utf8');
const start=premium.indexOf('function officialReadingState(');
const end=premium.indexOf('\nfunction renderPremium(',start);
assert.ok(start>=0&&end>start,'Freshness owner function must exist');
const sandbox={window:{},Date};
vm.createContext(sandbox);
vm.runInContext(premium.slice(start,end)+'\nglobalThis.getReadingState=officialReadingState;',sandbox);
const state=sandbox.getReadingState;
const stamp='2026-10-16T09:30:00Z';
const source='2026-10-16T09:00:00Z';
const expiry='2026-10-16T12:00:00Z';
const clock=t=>Date.parse('2026-10-16T'+t+'Z');
const verified={contract:'PUBLIC_COMPASS_PROJECTION_v1',data_status:'OK',issued_at_utc:stamp,action_now:'HOLD_WAIT',
 full_stack:{source_status:{official:'VERIFIED'},official_freshness:{
  contract:'OFFICIAL_COMPASS_SOURCE_FRESHNESS_READBACK_v1',
  status:'VERIFIED_OWNER_POLICY',source_asof_utc:source,valid_until_utc:expiry}}};
assert.equal(state(verified,clock('10:00:00')),'CURRENT');
assert.equal(state(verified,clock('12:00:00')),'CURRENT');
assert.equal(state(verified,clock('12:00:00.001')),'LAST_VERIFIED');
assert.equal(state(verified,clock('15:00:00')),'LAST_VERIFIED');
assert.equal(state({...verified,data_status:'DEGRADED'},clock('10:00:00')),'UNAVAILABLE');
assert.equal(state({...verified,contract:'UNTRUSTED'},clock('10:00:00')),'UNAVAILABLE');
assert.equal(state({...verified,issued_at_utc:'2099-01-01T00:00:00Z'},clock('10:00:00')),'UNAVAILABLE');
assert.equal(state({...verified,full_stack:{source_status:{official:'UNVERIFIED'},official_freshness:verified.full_stack.official_freshness}},clock('10:00:00')),'UNAVAILABLE');
assert.equal(state({...verified,full_stack:{source_status:{official:'VERIFIED'},official_freshness:{status:'UNAVAILABLE'}}},clock('10:00:00')),'UNAVAILABLE');
assert.equal(state({...verified,full_stack:{source_status:{official:'VERIFIED'},official_freshness:{...verified.full_stack.official_freshness,source_asof_utc:'2026-10-17T00:00:00Z'}}},clock('10:00:00')),'UNAVAILABLE');
assert.match(builder,/source_bindings\?\.auto_market_state\?\.freshness/,'Use the original verified owner policy');
assert.match(builder,/official_freshness:officialValid\?officialFreshness/,'Projected owner policy');
assert.match(header,/window\.CNOfficialReadingState\?\.\(officialCompass\)/,'Header must share state function');
assert.match(premium,/LAST VERIFIED ACTION · NOT CURRENT/,'Stale must be explicitly historical');
assert.match(premium,/dataOk \? '<div class="premium-action-window"/,'Only CURRENT shows APPLIES NOW window');
assert.match(premium,/scheduleFreshnessExpiry\(snapshot,compass,event\)/,'Expiration schedules in-place rerender');

// Grok exact-head negative control: stale or unavailable cannot synthesize
// ACTION NOW: WAIT via the *real* pullbackCard function.
const pbStart=premium.indexOf('function pullbackCard(');
const pbEnd=premium.indexOf('\nfunction compositeIntel(',pbStart);
assert.ok(pbStart>0&&pbEnd>pbStart);
const ctx={
  Date, esc:String,clean:v=>typeof v==='string'&&v.trim()?v.trim():null,
  publicState:v=>String(v||'UNAVAILABLE').replaceAll('_',' '),
  publicCompassText:v=>String(v||''),
  recommendation:raw=>({action:raw==='HOLD'?'HOLD':'WAIT',
    copy:raw==='HOLD'?'Hold source-verified positioning.':'Stay patient. Do not infer a new risk-on call.'})
};
vm.createContext(ctx);
vm.runInContext(premium.slice(pbStart,pbEnd)+';globalThis.pull=pullbackCard;',ctx);
const pbComp={...verified,action_now:'HOLD'};
const currentPb=ctx.pull(pbComp,'CURRENT');
const stalePb=ctx.pull(pbComp,'LAST_VERIFIED');
const unavailablePb=ctx.pull({...pbComp,data_status:'DEGRADED'},'UNAVAILABLE');
assert.match(currentPb,/ACTION NOW · COMPASS<\/span><strong>HOLD/);
for(const html of [stalePb,unavailablePb]){
  assert.doesNotMatch(html,/ACTION NOW · COMPASS/,'No ACTION NOW when source is not current');
  assert.doesNotMatch(html,/<strong>WAIT<\/strong>/,'No fabricated WAIT');
  assert.doesNotMatch(html,/Stay patient/,'No recommendation fallback');
  assert.match(html,/UNAVAILABLE/,'Action must be explicitly unavailable');
}
assert.match(stalePb,/LAST VERIFIED COMPASS ACTION · NOT CURRENT/);
assert.match(unavailablePb,/COMPASS ACTION UNAVAILABLE/);

// Combined Compass intelligence must not promote hash verified (but expired)
// records into a current official action either.
const ciStart=premium.indexOf('function compositeIntel(');
const ciEnd=premium.indexOf('\nfunction refreshStatusBanner(',ciStart);
assert.ok(ciStart>0&&ciEnd>ciStart);
vm.runInContext(premium.slice(ciStart,ciEnd)+';globalThis.combined=compositeIntel;',ctx);
const ciComp={...pbComp,full_stack:{...verified.full_stack,
  contract:'PUBLIC_COMPASS_FULL_STACK_READBACK_v1',shadow:{status:'UNVERIFIED'},
  strategic:{}}};
assert.match(ctx.combined(ciComp,'CURRENT'),/OFFICIAL ACTION<\/span><strong>HOLD/);
assert.match(ctx.combined(ciComp,'LAST_VERIFIED'),/UNAVAILABLE · NOT CURRENT/);
assert.doesNotMatch(ctx.combined(ciComp,'UNAVAILABLE'),/WAIT · DATA DEGRADED/);

// A source can expire between hourly/full product renders. A premium
// freshness event must update the existing hero without re-creating the DOM.
const heroStart=header.indexOf('function syncHeroFreshness(');
const heroEnd=header.indexOf('\nfunction pathEta(',heroStart);
assert.ok(heroStart>0&&heroEnd>heroStart);
const el=()=>({textContent:''});
const word=el(),heroCopy=el(),next=el(),confirm=el(),risk=el();
const officialWord={textContent:'HOLD'},officialCopy={textContent:'Verified Official decision'};
const documentRoot={
 querySelector:s=>s==='.action-hero .action-word'?word:
 s==='.action-hero > p'?heroCopy:
 s==='#premiumMarketCompass aside > strong'?officialWord:
 s==='#premiumMarketCompass aside > p'?officialCopy:null,
 querySelectorAll:s=>s==='.action-hero .hero-lines > div strong'?[el(),next,confirm,risk]:[]
};
const heroContext={document:{getElementById:()=>documentRoot},snapshot:{},officialCompass:{},
 window:{CNOfficialReadingState:()=> 'CURRENT'}};
vm.createContext(heroContext);
vm.runInContext(header.slice(heroStart,heroEnd)+';globalThis.sync=syncHeroFreshness;',heroContext);
heroContext.sync();
assert.equal(word.textContent,'HOLD');
heroContext.window.CNOfficialReadingState=()=> 'LAST_VERIFIED';
heroContext.sync();
assert.equal(word.textContent,'NO CURRENT CALL');
assert.match(next.textContent,/No current 1–3-day action/);
assert.match(confirm.textContent,/verification required/);
assert.match(risk.textContent,/unavailable/);
heroContext.window.CNOfficialReadingState=()=> 'UNAVAILABLE';
heroContext.sync();
assert.equal(word.textContent,'NO CURRENT CALL');
assert.doesNotMatch(next.textContent,/Stay hold/);

// Translation contract for newly introduced action/freshness copy.
const lang=JSON.parse(await readFile(new URL('../i18n-da.json',import.meta.url),'utf8'));
for(const key of ['CURRENT OFFICIAL COMPASS','LAST VERIFIED COMPASS · NOT CURRENT',
  'OFFICIAL COMPASS UNAVAILABLE','NO CURRENT CALL','NEXT SCHEDULED CHECK',
  'LAST VERIFIED ACTION · NOT CURRENT','COMPASS ACTION UNAVAILABLE',
  'No current 1–3-day action. Await a fresh verified Official Compass.']){
  assert.ok(lang.exact[key]?.length>3,'Danish UI copy missing: '+key);
}
assert.ok(lang.phrases['Historical action only. This is NOT a current recommendation. Last issued']);
assert.match(builder,/\/\(\?:Z\|\[\+-\]/,'Timestamp freshness must use explicit zone');


// P1-A negative control: missing Official horizon posture must NEVER become
// a generated WAIT/AFVENT recommendation in LAST_VERIFIED or UNAVAILABLE.
const actStart=premium.indexOf('function actionFromLane(');
const actEnd=premium.indexOf('\nfunction capSummary(',actStart);
assert.ok(actStart>0&&actEnd>actStart);
const actCtx={};vm.createContext(actCtx);
vm.runInContext(premium.slice(actStart,actEnd)+';globalThis.fromLane=actionFromLane;',actCtx);
assert.equal(actCtx.fromLane(undefined),'UNAVAILABLE');
assert.equal(actCtx.fromLane({}),'UNAVAILABLE');
assert.equal(actCtx.fromLane({action_posture:null}),'UNAVAILABLE');
assert.equal(actCtx.fromLane({action_posture:'HOLD'}),'HOLD');
assert.equal(actCtx.fromLane({action_posture:'WAIT'}),'WAIT');
assert.equal(actCtx.fromLane({action_posture:'PREPARE'}),'PREPARE');
// The actual 3 cards receive empty lanes for non-current officialView.
assert.match(premium,/HORIZONS\.map\(\(h\) => horizonCard\(snapshot, officialView, scale, h\)\)/);
assert.match(premium,/premium-horizon-meta.*actionFromLane\(lane\)/);
// P2 user-facing copy must distinguish expired evidence from missing evidence.
assert.match(premium,/lastVerified \? 'Previously verified Compass · not current\.'/);
for(const txt of [
  'See the source-verified Official Compass horizons below.',
  'Previously verified Compass · not current.',
  'Official Compass unavailable · no current reading.'
])assert.ok(lang.exact[txt]?.length>5,'Missing Danish translation: '+txt);

// P1: The PATH tab uses the SAME Official freshness state as NOW and the
// header; hash-aligned but expired data must never remain live rotation.
const pathStart=header.indexOf('function pathWeeklyAlignment(');
const pathEnd=header.indexOf('\nfunction statusActive(',pathStart);
assert.ok(pathStart>0&&pathEnd>pathStart,'PATH alignment source exists');
const pathState={current:'CURRENT'};
const pathCtx={window:{CNOfficialReadingState:()=>pathState.current}};
vm.createContext(pathCtx);
vm.runInContext(header.slice(pathStart,pathEnd)+';globalThis.pathAligned=pathWeeklyAlignment;globalThis.pathNotice=pathAlignmentNotice;',pathCtx);
const pathData={public_series:{current_public_projection:{public_issue_number:29,forecast_week:'2026-W42'}}};
const pathOfficial={...verified,weekly_context:{contract:'CN_COMPASS_WEEKLY_ALIGNMENT_v1',status:'ALIGNED',
  public_issue_number:29,forecast_week:'2026-W42'}};
const currentPath=pathCtx.pathAligned(pathData,pathOfficial);
assert.equal(currentPath.ok,true);
assert.equal(currentPath.readingState,'CURRENT');
assert.equal(pathCtx.pathNotice(currentPath),'');
pathState.current='LAST_VERIFIED';
const expiredPath=pathCtx.pathAligned(pathData,pathOfficial);
assert.equal(expiredPath.ok,false);
assert.equal(expiredPath.status,'OFFICIAL_EXPIRED');
assert.match(pathCtx.pathNotice(expiredPath),/LAST VERIFIED COMPASS · NOT CURRENT/);
assert.doesNotMatch(pathCtx.pathNotice(expiredPath),/LIVE SIGNALS REFRESHING/);
pathState.current='UNAVAILABLE';
const missingPath=pathCtx.pathAligned(pathData,pathOfficial);
assert.equal(missingPath.ok,false);
assert.equal(missingPath.status,'OFFICIAL_UNAVAILABLE');
assert.match(pathCtx.pathNotice(missingPath),/OFFICIAL COMPASS UNAVAILABLE/);
pathState.current='CURRENT';
assert.equal(pathCtx.pathAligned(pathData,{...pathOfficial,data_status:'DEGRADED'}).ok,false);
assert.equal(pathCtx.pathAligned(pathData,{...pathOfficial,weekly_context:{...pathOfficial.weekly_context,public_issue_number:28}}).ok,false);
assert.match(header,/liveCompass=alignment\.ok\?compass:null/,'PATH may consume live segments only after freshness and weekly alignment');
assert.match(header,/pathReadingState=alignment\.readingState/,'PATH records the state that actually rendered');

// The original 30-second freshness check must re-render an already mounted
// PATH at expiry, independent of the five-minute full product reload.
const refreshStart=header.indexOf('function refreshPathIfReadingChanged(');
const refreshEnd=header.indexOf('\nfunction freshness(',refreshStart);
assert.ok(refreshStart>0&&refreshEnd>refreshStart);
let pathCalls=0;
const live={current:'CURRENT'};
const refreshCtx={
 window:{CNOfficialReadingState:()=>live.current},
 snapshot:pathData, officialCompass:pathOfficial, pathReadingState:'CURRENT',
 document:{getElementById:id=>id==='productPath'?{}:null},
 renderPath:()=>{pathCalls++;refreshCtx.pathReadingState=live.current;}
};
vm.createContext(refreshCtx);
vm.runInContext(header.slice(refreshStart,refreshEnd)+';globalThis.recheck=refreshPathIfReadingChanged;',refreshCtx);
refreshCtx.recheck();
assert.equal(pathCalls,0,'No unnecessary PATH rerender before expiry');
live.current='LAST_VERIFIED';refreshCtx.recheck();
assert.equal(pathCalls,1,'Expiry must refresh PATH immediately when observed');
refreshCtx.recheck();
assert.equal(pathCalls,1,'Identical stale state is not a repeated rerender');
live.current='UNAVAILABLE';refreshCtx.recheck();
assert.equal(pathCalls,2,'Missing owner reading revokes prior PATH permissions');
assert.match(header,/refreshPathIfReadingChanged\(\);/,'The real 30-second freshness path must consume expiry transition');
console.log('PATH_OFFICIAL_EXPIRY_FAIL_CLOSED');

console.log('OFFICIAL_COMPASS_FRESHNESS_3STATE_PASS');
