import './tests/full-stack-readback.test.mjs';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { runInNewContext } from 'node:vm';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
const site=dirname(fileURLToPath(import.meta.url));
const dist=resolve(site,'dist');
const compass=JSON.parse(await readFile(resolve(dist,'data/compass.json'),'utf8'));
const index=await readFile(resolve(dist,'index.html'),'utf8');
const renderer=await readFile(resolve(dist,'compass-product-v5.js'),'utf8');
const premiumRenderer=await readFile(resolve(site,'market-compass-premium.js'),'utf8');
const event=JSON.parse(await readFile(resolve(dist,'data/compass-event.json'),'utf8'));
const f=compass.full_stack;
if(f?.contract!=='PUBLIC_COMPASS_FULL_STACK_READBACK_v1')throw Error('missing combined Compass');
if(!['COMPLETE','PARTIAL_OR_DEGRADED'].includes(f.status))throw Error('invalid combined status');
if(f.protective_action_authority!=='OFFICIAL_COMPASS_ONLY')throw Error('official action boundary changed');
if(f.shadow?.authority!=='RESEARCH_ONLY_NO_ACTION_PERMISSION')throw Error('model authority boundary changed');
if(f.official_data_status!==compass.data_status)throw Error('official status discrepancy');
if(f.source_status?.cycle_navigator!=='WEEKLY_POINTER_ALIGNED'&&f.weekly?.direction_2_3w!=='UNAVAILABLE')throw Error('unverified 2-3w direction leaked');
if(compass.data_status!=='OK'&&f.official_action!=='UNAVAILABLE')throw Error('degraded action falsely promoted');
if(f.shadow?.status==='ALIGNED_RESEARCH'||f.shadow?.status==='STALE_RESEARCH'){
 for(const key of ['12h','1_3d','5_7d']) if(!f.shadow.horizons?.[key])throw Error('missing independent horizon');
}
if(!renderer.includes('fullStackSection(c)'))throw Error('missing combined renderer');
if(!premiumRenderer.includes('compositeIntel(compass)'))throw Error('active premium renderer ignores integrated Compass');
if(!premiumRenderer.includes('CN_PREMIUM_COMPASS_OWNER = true'))throw Error('premium owner not detected');
if(!premiumRenderer.includes('RESEARCH_ONLY')&&!premiumRenderer.includes('Model research')&&!premiumRenderer.includes('Research direction'))throw Error('premium research disclosure absent');
// Execute the active premium rendering code in an isolated mock DOM. Merely
// finding disclaimers in a source comment is not an acceptance test.
const honestyScope = {window: {}, document: {readyState:'loading', addEventListener() {}}};
const honestyInstrumented = premiumRenderer.replace(/\}\)\(\);\s*$/,
  'globalThis.__honestyProbe = {renderPremium, freshNearTermReading, mixedNearTermReading, twelveHourMethodDisclosure};})();');
if(honestyInstrumented===premiumRenderer) throw Error('premium active render scope unavailable for behavioral test');
runInNewContext(honestyInstrumented, honestyScope, {timeout:1500});
const honesty=honestyScope.__honestyProbe;
if(!honesty || typeof honesty.renderPremium!=='function' || typeof honesty.twelveHourMethodDisclosure!=='function') throw Error('premium behavioral disclosure hooks unavailable');
const sourceMethod='Current BTC/ETH direction extrapolated, not an independently validated 12H forecast.';
const noSource='No fresh verified 0–12H reading is available.';
if(!honesty.freshNearTermReading(true,'UP') || !honesty.freshNearTermReading(true,'BULLISH') || honesty.freshNearTermReading(true,'NO NEW READING') || honesty.freshNearTermReading(true,'MIXED') || honesty.freshNearTermReading(true,'STALE') || honesty.freshNearTermReading(true,'NEW_UNKNOWN_STATE') || honesty.freshNearTermReading(false,'UP')) throw Error('premium 12H availability condition unsafe');
if(!honesty.mixedNearTermReading(true,'MIXED') || !honesty.mixedNearTermReading(true,'SIDEWAYS') || honesty.mixedNearTermReading(false,'MIXED'))throw Error('premium mixed 12H evidence class invalid');
if(!honesty.twelveHourMethodDisclosure(true,'UP').includes(sourceMethod))throw Error('valid current 12H continuation method disclosure absent');
for(const [available,state] of [[true,'NO NEW READING'],[true,'NOT READY'],[true,'UNCLEAR'],[false,'UP']]){
 const text=honesty.twelveHourMethodDisclosure(available,state);
 if(!text.includes(noSource)||text.includes(sourceMethod))throw Error('missing 12H source claimed as current');
}
function actualPremiumMarkup(c) {
 let markup='';
 const root={querySelectorAll:()=>[],querySelector:()=>null,classList:{add(){}},prepend(section){markup=section.innerHTML;honestyScope.__lastMarkup=markup;}};
 honestyScope.document.getElementById=id=>id==='productNow'?root:null;
 honestyScope.document.createElement=()=>({
   innerHTML:'',querySelectorAll:()=>[],querySelector:()=>null
 });
 if(honesty.renderPremium({package:{}},c,null)!==true)throw Error('premium renderer failed to install in mock DOM');
 return markup;
}
const testProjection={...compass,contract:'PUBLIC_COMPASS_PROJECTION_v1',data_status:'OK',action_now:'HOLD',issued_at_utc:new Date(Date.now()-60000).toISOString(),full_stack:{...compass.full_stack,source_status:{...compass.full_stack.source_status,official:'VERIFIED'},official_freshness:{contract:'OFFICIAL_COMPASS_SOURCE_FRESHNESS_READBACK_v1',status:'VERIFIED_OWNER_POLICY',source_asof_utc:new Date(Date.now()-120000).toISOString(),valid_until_utc:new Date(Date.now()+3600000).toISOString()}}};
const staleMarkup=actualPremiumMarkup({...testProjection,market_now:{...(compass.market_now||{}),directional_state:'UNCHANGED_NO_NEW_OBSERVATION'}});
if(!staleMarkup.includes(noSource)||staleMarkup.includes(sourceMethod)||staleMarkup.includes('The 0–12h pressure reading is a current-state observation'))throw Error('rendered NO NEW READING card falsely asserts available 12H direction');
const freshMarkup=actualPremiumMarkup({...testProjection,market_now:{...(compass.market_now||{}),directional_state:'UP'}});
if(!freshMarkup.includes(sourceMethod)||freshMarkup.includes(noSource))throw Error('rendered active NOW card lost continuation-proxy caveat');
const mixedMethod='Current BTC/ETH conditions are mixed or sideways; no clear 0–12H direction or independently validated 12H forecast.';
const mixedMarkup=actualPremiumMarkup({...testProjection,market_now:{...(compass.market_now||{}),directional_state:'MIXED'}});
if(!mixedMarkup.includes(mixedMethod)||mixedMarkup.includes(noSource)||mixedMarkup.includes(sourceMethod))throw Error('rendered fresh MIXED falsely asserts a directional 12H forecast or missing data');
const unknownMarkup=actualPremiumMarkup({...testProjection,market_now:{...(compass.market_now||{}),directional_state:'STALE'}});
if(!unknownMarkup.includes(noSource)||unknownMarkup.includes(sourceMethod))throw Error('unknown 12H label did not fail closed');
const degradedMarkup=actualPremiumMarkup({...testProjection,data_status:'UNAVAILABLE'});
if(!degradedMarkup.includes(noSource)||degradedMarkup.includes(sourceMethod))throw Error('rendered degraded NOW card falsely asserts available 12H direction');
for(const badProjection of [
 {...testProjection,full_stack:{...testProjection.full_stack,source_status:{official:'DEGRADED'}}},
 {...testProjection,full_stack:{...testProjection.full_stack,official_freshness:{...testProjection.full_stack.official_freshness,valid_until_utc:new Date(Date.now()-1000).toISOString()}}},
 {...testProjection,full_stack:{...testProjection.full_stack,official_freshness:{status:'UNAVAILABLE'}}}
]){
 const bad=actualPremiumMarkup({...badProjection,market_now:{directional_state:'BULLISH'}});
 if(!bad.includes(noSource)||bad.includes(sourceMethod)||bad.includes('APPLIES NOW'))throw Error('stale/unverified official source presented as current');
}
// No polling/network refresh is needed to expire an already rendered action.
const realDate=Date;let clock=Date.now(),expiryCallback=null,scheduledDelay=null;
honestyScope.Date=class extends realDate {static now(){return clock;}};
honestyScope.setTimeout=(callback,delay)=>{expiryCallback=callback;scheduledDelay=delay;return 1;};
honestyScope.clearTimeout=()=>{};
actualPremiumMarkup(testProjection);
if(typeof expiryCallback!=='function'||!(scheduledDelay>0&&scheduledDelay<=3600001))throw Error('owner expiry did not schedule invalidation');
clock=Date.parse(testProjection.full_stack.official_freshness.valid_until_utc)+1;
expiryCallback();
if(!honestyScope.__lastMarkup.includes(noSource)||honestyScope.__lastMarkup.includes('APPLIES NOW'))throw Error('expired visible action survived without polling');
honestyScope.Date=realDate;delete honestyScope.setTimeout;delete honestyScope.clearTimeout;
if(!premiumRenderer.includes("visibilitychange")||!premiumRenderer.includes("'pageshow'")||!premiumRenderer.includes("'focus'"))throw Error('suspended page has no freshness resume check');
if(premiumRenderer.includes('The bearish 0–12h pressure reading'))throw Error('hard-coded bearish HOLD investor copy may contradict owner');
const chatPrompt=await readFile(resolve(site,'../..','07_PROMPTS_AND_AGENTS/prompts/HANDLEKOMPAS_v1.md'),'utf8');
const sourceHonesty=chatPrompt.match(/## Forecast evidence, honesty and user-visible accountability \(Task 1\.5 P0\)([\s\S]*?)## Mandatory rendering rules/)?.[1]||'';
if(!sourceHonesty.includes('12H = fortsættelse af seneste BTC/ETH-retning'))throw Error('Chat KOMPAS missing 12H continuation disclosure');
if(!sourceHonesty.includes('**NO UNSOURCED CONFIDENCE:**')||!sourceHonesty.includes('A numeric probability / success likelihood requires a prospectively issued, scored and adequately calibrated probability for the identical event/horizon.'))throw Error('Chat KOMPAS missing governed calibrated-probability requirement');
if(chatPrompt.includes('**Confidence:** <0–100%>'))throw Error('Chat KOMPAS still mandates uncalibrated 0–100% confidence');
const route=JSON.parse(await readFile(resolve(site,'../../07_PROMPTS_AND_AGENTS/action_compass/GLOBAL_ACTION_COMPASS_ROUTE_v1.json'),'utf8'));
const canonicalPath='07_PROMPTS_AND_AGENTS/action_compass/2026-09-16__global-action-compass-invocation-contract-v1__canonical.md';
if(route.canonical_contract!==canonicalPath)throw Error('active Kompas global contract route changed without guard review');
for(const trigger of ['kompas','handlekompas','compass'])if(!route.hard_triggers?.includes(trigger))throw Error('required ChatGPT hard trigger missing');
const globalContract=await readFile(resolve(site,'../..',canonicalPath),'utf8');
if(!globalContract.includes('P0 current-direction vs forecast honesty')||!globalContract.includes('Official NEXT_12H.expected_direction')||!globalContract.includes('P0 confidence and delivery honesty')||!globalContract.includes('not automatically a frozen research forecast'))throw Error('active global Kompas contract missing Task 1.5 truthfulness guard');
const bilingual=JSON.parse(await readFile(resolve(site,'i18n-da.json'),'utf8')).exact;
for(const original of [
  sourceMethod,
  mixedMethod,
  'Keep existing positioning. BTC/ETH conditions are mixed; there is no clear directional 12H signal. Do not broaden high-beta exposure based on mixed conditions alone.',
  'Near-term BTC/ETH conditions are mixed, with no clear directional edge. Wait for a verified change; mixed conditions are not a short or sell signal.',
  'No fresh verified 0–12H reading is available. The continuation method is not an independently validated 12H forecast.',
  'Keep existing positioning. The 0–12h pressure reading is a current-state observation, not a validated 12H forecast or the 5–7 day base case. Do not broaden high-beta exposure from this signal alone.',
  'Keep existing positioning. No fresh verified 0–12H reading is available; do not infer a new near-term direction or broaden high-beta exposure from missing evidence.',
  'No fresh verified 0–12H pressure reading is available. Use the separate weekly context and await verified near-term evidence; missingness is not a swing, short or sell signal.'
]){
  if(typeof bilingual[original]!=='string'||!bilingual[original].trim()||bilingual[original]===original)throw Error('DA translation missing for 12H safety disclosure: '+original);
}
if(!staleMarkup.includes('No fresh verified 0–12H reading is available. The continuation method is not an independently validated 12H forecast.'))throw Error('missing-data active render not covered by bilingual catalog');
if(!freshMarkup.includes(sourceMethod))throw Error('fresh active render not covered by bilingual catalog');
// Independent end-to-end producer-digest and weekly-source regression checks.
const root=resolve(site,'../..');
const j=async p=>JSON.parse(await readFile(resolve(root,p),'utf8'));
const sortKeys=v=>Array.isArray(v)?v.map(sortKeys):v&&typeof v==='object'?Object.fromEntries(Object.keys(v).sort().map(k=>[k,sortKeys(v[k])])):v;
const digest=(o,key)=>{const value={...o};delete value[key];return createHash('sha256').update(JSON.stringify(sortKeys(value))+'\n').digest('hex');};
const [op,ap,wp,shp,stp]=await Promise.all([
 j('04_MARKET_LEARNING/handlekompas/official/LATEST_COMPASS.json'),
 j('04_MARKET_LEARNING/entry_signals/auto_market_state/LATEST.json'),
 j('05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json'),
 j('04_MARKET_LEARNING/handlekompas/shadow_v2/LATEST.json'),
 j('04_MARKET_LEARNING/handlekompas/strategic/LATEST_STRATEGIC_COMPASS.json')]);
// Producer preserves original numeric spellings (e.g. Python 1.0); avoid JS reserialization for Auto State.
const rawAuto=await readFile(resolve(root,ap.packet_path),'utf8');
const autoToken=',"packet_sha256":"'+ap.packet_sha256+'"';
if(rawAuto.indexOf(autoToken)<0)throw Error('Auto SHA marker missing');
const actualAutoHash=createHash('sha256').update(rawAuto.replace(autoToken,''),'utf8').digest('hex');
if(actualAutoHash!==ap.packet_sha256)throw Error('Auto packet immutable source digest mismatch');
if(f.source_status.auto_market_state!=='HASH_VERIFIED')throw Error('valid Auto State incorrectly declared unverified');
const sh=await j(shp.forecast_path),st=await j(stp.anchor_path);
const shCurrent=sh.source_bindings?.auto_market_state?.packet_sha256===ap.packet_sha256
 && ap.packet_sha256===op.source_packet_sha256
 && sh.source_bindings?.cycle_navigator?.machine_package_sha256===wp.machine_package_sha256
 && Number(sh.source_bindings?.cycle_navigator?.iso_week)===Number(wp.iso_week);
const shHash=digest(sh,'forecast_sha256')===shp.forecast_sha256;
if(shCurrent&&shHash&&!['ALIGNED_RESEARCH','STALE_RESEARCH'].includes(f.shadow.status))throw Error('valid current Shadow suppressed');
if(shCurrent&&!shHash&&f.shadow.status!=='UNVERIFIED')throw Error('tampered Shadow promoted');
if(!shCurrent&&f.shadow?.status==='ALIGNED_RESEARCH')throw Error('historical Shadow promoted as current research');
if(f.shadow?.status==='STALE_RESEARCH'&&f.shadow?.current_source_aligned!==false&&
  !shCurrent)throw Error('source diverged but stale flag omitted');
if(f.shadow?.status==='ALIGNED_RESEARCH'&&f.shadow?.current_source_aligned!==true)throw Error('aligned Shadow lacks exact source proof');
if(shHash){const mut=structuredClone(sh);mut.model_output={...sh.model_output,tampered:true};if(digest(mut,'forecast_sha256')===shp.forecast_sha256)throw Error('tampered Shadow not detected');}
const stBound=st.source_bindings?.cycle_navigator||{};
const stCurrent=Number(stBound.iso_year)===Number(wp.iso_year)&&Number(stBound.iso_week)===Number(wp.iso_week)
 && Number(stBound.issue_number)===Number(wp.issue_number)&&stBound.sha256===wp.machine_package_sha256;
const stHash=digest(st,'anchor_sha256')===stp.anchor_sha256;
if(stCurrent&&stHash&&f.strategic.status!=='BOUND_WEEKLY_ANCHOR')throw Error('current strategic source suppressed');
if((!stCurrent||!stHash)&&f.strategic.status!=='UNVERIFIED')throw Error('stale or tampered strategic anchor promoted');
if(stHash){const mut=structuredClone(st);mut.strategic_21_30d={...st.strategic_21_30d,tampered:true};if(digest(mut,'anchor_sha256')===stp.anchor_sha256)throw Error('tampered strategic not detected');}
if(/source_bindings|packet_sha256|wallet_address|portfolio_actions|api_key/i.test(JSON.stringify(f)))throw Error('restricted evidence leaked');
if(compass.contract!=='PUBLIC_COMPASS_PROJECTION_v1') throw Error('wrong Compass contract');
if(event.contract!=='PUBLIC_COMPASS_EVENT_STATUS_v1') throw Error('wrong Compass event status contract');
if(!['IDLE','REASSESSMENT_REQUESTED'].includes(event.status)) throw Error('wrong Compass event status');
if(compass.data_status==='OK'){
  for(const h of ['NEXT_12H','NEXT_1_3D','NEXT_5_7D','CYCLE_ALTCOINS_3_8W']) if(!compass.horizons?.[h]) throw Error(`missing ${h}`);
  if(compass.horizons?.NEXT_2_3W===undefined && compass.bull_bear_scale?.horizons?.['2_3w']?.status==='OK') throw Error('2-3w Bull Bear cannot exist without governed Compass horizon');
  if(compass.bull_bear_scale){
    const scale=compass.bull_bear_scale;
    if(scale.contract!=='OFFICIAL_COMPASS_BULL_BEAR_DISPLAY_v1') throw Error('wrong Bull Bear display contract');
    if(scale.semantics!=='EVIDENCE_BALANCE_NOT_PROBABILITY') throw Error('wrong Bull Bear semantics');
    if(scale.owner!=='OFFICIAL_COMPASS') throw Error('wrong Bull Bear owner');
    if(scale.source_of_truth_contract!=='MARKET_WEATHER_SOURCE_OF_TRUTH_v1') throw Error('wrong Market Weather source-of-truth contract');
    if(scale.mapping_version!=='DIRECTION_ONLY_COARSE_v1'||scale.resolution!=='COARSE_CATEGORICAL_DIRECTION') throw Error('wrong Market Weather mapping semantics');
    if(scale?.authority?.site_synthesis_allowed!==false||scale?.authority?.new_market_classifier!==false||scale?.authority?.portfolio_execution!==false) throw Error('Bull Bear authority leak');
    for(const key of ['1_3d','5_7d','2_3w']){
      const row=scale.horizons?.[key];
      if(!row) throw Error(`missing Bull Bear ${key}`);
      if(row.status==='OK'){
        if(!Number.isInteger(row.bull)||!Number.isInteger(row.bear)||row.bull<0||row.bull>10||row.bear<0||row.bear>10||row.bull+row.bear!==10) throw Error(`invalid Bull Bear ${key}`);
      }else if(row.bull!==null||row.bear!==null) throw Error(`unavailable Bull Bear ${key} must remain null`);
    }
  }
  const protection=compass.protection_tracker;
  if(protection?.contract!=='COMPASS_PROTECTION_TRACKER_v1') throw Error('missing protection tracker');
  if(!['NORMAL','BUILDING','ELEVATED','HIGH','CONFIRMED','UNAVAILABLE'].includes(protection.pullback_risk_state)) throw Error('wrong pullback risk state');
  if(!['NONE','WARNING','CONFIRMED','UNKNOWN'].includes(protection.distribution_risk)) throw Error('wrong distribution risk');
  if(!['INACTIVE','WAIT_FOR_FLUSH','WAIT_FOR_RECLAIM','REVIEW','UNAVAILABLE'].includes(protection.reentry_state)) throw Error('wrong re-entry state');
  const alt=compass.horizons.CYCLE_ALTCOINS_3_8W;
  if(!alt.action_posture||!alt.expected_path) throw Error('incomplete altcoin action lane');
  const segments=(compass.capitalization_ladder||[]).map(x=>x.segment).join(',');
  if(segments!=='BTC,ETH,LARGE_CAPS,MID_CAPS,SMALL_CAPS,MICROCAPS,MEMES') throw Error('wrong capitalization ladder');
  const sell=compass.sell_assessment;
  if(sell?.contract!=='COMPASS_SELL_ASSESSMENT_v1') throw Error('missing sell assessment');
  if(sell.state!=='UNAVAILABLE') throw Error('unexpected live sell authority');
  if(sell?.authority?.portfolio_execution!==false||sell?.authority?.new_sell_rule!==false||sell?.authority?.protection_is_sell_authority!==false) throw Error('sell authority leak');
  const meme=(compass.capitalization_ladder||[]).find(x=>x.segment==='MEMES');
  if(!meme||meme.status!=='UNAVAILABLE'||meme.action!=='UNAVAILABLE'||meme.direction!=='UNAVAILABLE') throw Error('meme rung must fail closed');
}
if(!index.includes('./compass-product-v5.js')) throw Error('Compass renderer not activated');
for(const token of ['MARKET COMPASS','NEXT 12 HOURS','NEXT 1–3 DAYS','NEXT 5–7 DAYS','ALTCOIN ACTION · OFFICIAL COMPASS','Bitcoin → memes','CURRENT POSITION','NEXT IF CONFIRMED','NEXT WINDOW','Time horizon: now → 5–7 days.','ROTATION POSITION','EXPECTED WINDOW','08:17 / 20:17 CPH','nextCompassAt','MARKET MOVE DETECTED','Compass reassessment in progress','NEXT SCHEDULED COMPASS','event refresh can publish earlier','PROTECTION & RE-ENTRY','PULLBACK RISK','RE-ENTRY','portfolio actions stay private','MARKET WEATHER · LIVE COMPASS','Directional pressure','1–3 DAYS','5–7 DAYS','2–3 WEEKS','Evidence balance · not probability','AWAITING COMPASS']) if(!renderer.includes(token)) throw Error(`renderer missing ${token}`);
if(/HANDLEKOMPAS|MASTER MONDAY/.test(renderer)) throw Error('internal product language leaked');
if(/source_bindings|evidence_snapshot/.test(JSON.stringify(compass))) throw Error('private Compass evidence leaked');
const protectionText=JSON.stringify(compass.protection_tracker||{});
for(const key of ['wallet_address','holdings','positions','portfolio_actions']) if(Object.prototype.hasOwnProperty.call(compass.protection_tracker||{},key)) throw Error(`private protection field leaked: ${key}`);
if(/0x[a-f0-9]{8,}/i.test(protectionText)) throw Error('wallet address leaked into protection tracker');
if(compass.protection_tracker?.authority?.portfolio_execution!==false) throw Error('protection tracker execution authority leak');
if(compass.sell_assessment?.authority?.portfolio_execution!==false) throw Error('sell assessment execution authority leak');
if(/source_packet_sha256|heat_detail|market_snapshot/.test(JSON.stringify(event))) throw Error('private event evidence leaked');
if(!renderer.includes("c?.bull_bear_scale")||!renderer.includes("OFFICIAL_COMPASS_BULL_BEAR_DISPLAY_v1")) throw Error('Market Weather must read Official Compass Bull Bear payload');
if(/expected_direction[^\n]{0,160}(bull|bear)/i.test(renderer)) throw Error('client-side Bull Bear signal synthesis detected');
console.log(JSON.stringify({full_stack:f.status,shadow:f.shadow.status,strategic:f.strategic.status,source_status:f.source_status}));
console.log(JSON.stringify({status:'PASS',compass_id:compass.compass_id,data_status:compass.data_status,altcoin_action:compass.horizons?.CYCLE_ALTCOINS_3_8W?.action_posture||null,pullback_risk:compass.protection_tracker?.pullback_risk_state||null,reentry_state:compass.protection_tracker?.reentry_state||null,rotation_position_ui:true}));

