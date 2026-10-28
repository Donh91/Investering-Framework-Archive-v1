import './tests/full-stack-readback.test.mjs';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
const site=dirname(fileURLToPath(import.meta.url));
const dist=resolve(site,'dist');
const compass=JSON.parse(await readFile(resolve(dist,'data/compass.json'),'utf8'));
const index=await readFile(resolve(dist,'legacy/index.html'),'utf8');
// Premium is now the canonical homepage. The former integrated Compass renderer
// intentionally belongs exclusively to /legacy/, not the premium root.
const premiumHome=await readFile(resolve(dist,'index.html'),'utf8');
const renderer=await readFile(resolve(dist,'compass-product-v5.js'),'utf8');
const premiumRenderer=await readFile(resolve(site,'market-compass-premium.js'),'utf8');
const premiumVNextRenderer=await readFile(resolve(site,'vnext-live/premium-experience.mjs'),'utf8');
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
if(!premiumRenderer.includes('compositeIntel(compass,readingState)')||!premiumRenderer.includes("const verified=readingState==='CURRENT'"))throw Error('active premium renderer does not bind integrated Compass to current Official freshness');
if(!premiumRenderer.includes('CN_PREMIUM_COMPASS_OWNER = true'))throw Error('premium owner not detected');
if(!premiumVNextRenderer.includes('compassProReadback(view,feeds?.compass,{lang})'))throw Error('Kompas PRO approved premium vNext source readback not wired');
if(!premiumRenderer.includes('RESEARCH_ONLY')&&!premiumRenderer.includes('Model research')&&!premiumRenderer.includes('Research direction'))throw Error('premium research disclosure absent');
// Independent end-to-end producer-digest and weekly-source regression checks.
const root=resolve(site,'../..');
const j=async p=>JSON.parse(await readFile(resolve(root,p),'utf8'));
const sortKeys=v=>Array.isArray(v)?v.map(sortKeys):v&&typeof v==='object'?Object.fromEntries(Object.keys(v).sort().map(k=>[k,sortKeys(v[k])])):v;
const digest=(o,key)=>{const value={...o};delete value[key];return createHash('sha256').update(JSON.stringify(sortKeys(value))+'\n').digest('hex');};

// Producer canonical JSON can contain numbers such as 82116.0. Parsing into
// JavaScript collapses that spelling to 82116, changing a JSON-rehashed digest.
// Verify the IMMUTABLE producer bytes, with exactly the top-level hash field
// removed, as the public builder already does. Fail closed on altered bytes.
function verifiedRawDigest(raw, data, field, expected) {
  if (!data || !/^[a-f0-9]{64}$/.test(String(expected || '')) || data[field] !== expected) return false;
  const needle=JSON.stringify(field)+':'+JSON.stringify(expected);
  let depth=0,inString=false,escaped=false,pos=-1;
  for(let i=0;i<raw.length;i++){
    const c=raw[i];
    if(!inString&&depth===1&&c==='"'&&raw.startsWith(needle,i)){pos=i;break;}
    if(inString){
      if(escaped)escaped=false;
      else if(c==='\\')escaped=true;
      else if(c==='"')inString=false;
    }else if(c==='"')inString=true;
    else if(c==='{'||c==='[')depth++;
    else if(c==='}'||c===']')depth--;
  }
  if(pos<0||raw[pos-1]!==',')return false;
  return createHash('sha256').update(raw.slice(0,pos-1)+raw.slice(pos+needle.length),'utf8').digest('hex')===expected;
}

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
const [shRaw,stRaw]=await Promise.all([readFile(resolve(root,shp.forecast_path),'utf8'),readFile(resolve(root,stp.anchor_path),'utf8')]);
const sh=JSON.parse(shRaw),st=JSON.parse(stRaw);
const shCurrent=sh.source_bindings?.auto_market_state?.packet_sha256===ap.packet_sha256
 && ap.packet_sha256===op.source_packet_sha256
 && sh.source_bindings?.cycle_navigator?.machine_package_sha256===wp.machine_package_sha256
 && Number(sh.source_bindings?.cycle_navigator?.iso_week)===Number(wp.iso_week);
const shHash=verifiedRawDigest(shRaw,sh,'forecast_sha256',shp.forecast_sha256);
if(shCurrent&&shHash&&!['ALIGNED_RESEARCH','STALE_RESEARCH'].includes(f.shadow.status))throw Error('valid current Shadow suppressed');
if(shCurrent&&!shHash&&f.shadow.status!=='UNVERIFIED')throw Error('tampered Shadow promoted');
if(!shCurrent&&f.shadow?.status==='ALIGNED_RESEARCH')throw Error('historical Shadow promoted as current research');
if(f.shadow?.status==='STALE_RESEARCH'&&f.shadow?.current_source_aligned!==false&&
  !shCurrent)throw Error('source diverged but stale flag omitted');
if(f.shadow?.status==='ALIGNED_RESEARCH'&&f.shadow?.current_source_aligned!==true)throw Error('aligned Shadow lacks exact source proof');
if(shHash){const altered=shRaw.replace(/}\s*$/,',"tampered":true}\n');if(verifiedRawDigest(altered,{...sh,tampered:true},'forecast_sha256',shp.forecast_sha256))throw Error('tampered Shadow not detected');}
const stBound=st.source_bindings?.cycle_navigator||{};
const stCurrent=Number(stBound.iso_year)===Number(wp.iso_year)&&Number(stBound.iso_week)===Number(wp.iso_week)
 && Number(stBound.issue_number)===Number(wp.issue_number)&&stBound.sha256===wp.machine_package_sha256;
const stHash=verifiedRawDigest(stRaw,st,'anchor_sha256',stp.anchor_sha256);
// Regression: producer evidence with an original decimal "N.0" must still
// hash-pass, but a one-byte source change cannot pass the same digest.
if(stRaw.includes('"btc_usdt":82116.0')&&
   (!stHash||verifiedRawDigest(stRaw.replace('"btc_usdt":82116.0','"btc_usdt":82116'),st,'anchor_sha256',stp.anchor_sha256)))
  throw Error('original numeric spelling / byte integrity regression');
if(stCurrent&&stHash&&f.strategic.status!=='BOUND_WEEKLY_ANCHOR')throw Error('current strategic source suppressed');
if((!stCurrent||!stHash)&&f.strategic.status!=='UNVERIFIED')throw Error('stale or tampered strategic anchor promoted');
if(stHash){const altered=stRaw.replace(/}\s*$/,',"tampered":true}\n');if(verifiedRawDigest(altered,{...st,tampered:true},'anchor_sha256',stp.anchor_sha256))throw Error('tampered strategic not detected');}
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
if(!index.includes('./compass-product-v5.js')) throw Error('Legacy Compass renderer not activated');
if(!premiumHome.includes('<base href="./vnext/">')||!premiumHome.includes('PREMIUM LIVE')||!premiumHome.includes('role="tablist"'))
 throw Error('Premium canonical homepage shell not activated');
if(!premiumHome.includes('src="./app.mjs"')||premiumHome.includes('src="./public-product.js"')||premiumHome.includes('src="./compass-product-v5.js"'))
 throw Error('Premium homepage contaminated by legacy renderer');
for(const token of ['MARKET COMPASS','CURRENT MOMENTUM','NEXT 1–3 DAYS','NEXT 5–7 DAYS','ALTCOIN ACTION · OFFICIAL COMPASS','Bitcoin → memes','CURRENT POSITION','NEXT IF CONFIRMED','NEXT WINDOW','Time horizon: now → 5–7 days.','ROTATION POSITION','EXPECTED WINDOW','Scheduled slots are targets, not guaranteed publication times.','MARKET MOVE DETECTED','Compass reassessment in progress','COMPASS UPDATES','Current-state proxy, not a validated 12-hour forecast.','PROTECTION & RE-ENTRY','PULLBACK RISK','RE-ENTRY','portfolio actions stay private','MARKET WEATHER · LIVE COMPASS','Directional pressure','1–3 DAYS','5–7 DAYS','2–3 WEEKS','Evidence balance · not probability','AWAITING COMPASS']) if(!renderer.includes(token)) throw Error(`renderer missing ${token}`);
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

