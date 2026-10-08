import { mkdir, readFile, rm, writeFile, copyFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { dirname, resolve, relative } from "node:path";
import { fileURLToPath } from "node:url";
const siteDir=dirname(fileURLToPath(import.meta.url)); const repoRoot=resolve(siteDir,"../.."); const outputDir=resolve(siteDir,"dist"); const dataDir=resolve(outputDir,"data");
const POINTER_PATH=resolve(repoRoot,"05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json");
const COMPASS_POINTER_PATH=resolve(repoRoot,"04_MARKET_LEARNING/handlekompas/official/PUBLIC_LATEST_COMPASS.json");
const INTERNAL_COMPASS_POINTER_PATH=resolve(repoRoot,"04_MARKET_LEARNING/handlekompas/official/LATEST_COMPASS.json");
const COMPASS_EVENT_STATUS_PATH=resolve(repoRoot,"04_MARKET_LEARNING/handlekompas/event_refresh/PUBLIC_STATUS.json");
const HOURLY_POINTER_PATH=resolve(repoRoot,"03_DAILY_CAPTURE_LOGS/hourly/LATEST.json");
const NATIVE_COMPASS_POINTER_PATH=resolve(repoRoot,"04_MARKET_LEARNING/handlekompas/LATEST.json");
const AUTO_MARKET_STATE_POINTER_PATH=resolve(repoRoot,"04_MARKET_LEARNING/entry_signals/auto_market_state/LATEST.json");
const SHADOW_COMPASS_V2_POINTER_PATH=resolve(repoRoot,"04_MARKET_LEARNING/handlekompas/shadow_v2/LATEST.json");
const STRATEGIC_COMPASS_POINTER_PATH=resolve(repoRoot,"04_MARKET_LEARNING/handlekompas/strategic/LATEST_STRATEGIC_COMPASS.json");
const MASTER_MONDAY_HANDOFF_PATH=resolve(repoRoot,"LATEST_HANDOFF.json");
const RANGE_SCORE_PATH=resolve(repoRoot,"05_CYCLE_NAVIGATOR/LATEST_RANGE_SCORE.json");
const PROSPECTIVE_RANGE_PATH=resolve(repoRoot,"05_CYCLE_NAVIGATOR/LATEST_PROSPECTIVE_RANGE.json");
const PUBLIC_SERIES_INDEX_PATH=resolve(repoRoot,"05_CYCLE_NAVIGATOR/public_series/CN_PUBLIC_SERIES_INDEX.json");
const PUBLIC_SITE_FILES=["index.html","styles.css","scoreboard.css","motion.css","journey.css","vibe.css","app.js","compass.js","compass-product-v5.js","compass-product-v5.css","history-scoreboard.js","history-scoreboard.json","motion.js","journey.js","live-context.js","favicon.svg","apple-touch-icon.png","manifest.webmanifest","social-card.svg"];
const pick=(obj,keys)=>Object.fromEntries(keys.filter(k=>Object.prototype.hasOwnProperty.call(obj||{},k)).map(k=>[k,obj[k]]));
const sanitizePointer=p=>pick(p,["iso_year","iso_week","completed_source_week","issue_number","publication_status","status"]);
function sanitizeDecisionProjection(dp){
  if(!dp||dp.contract!=="CYCLE_NAVIGATOR_DECISION_PROJECTION_v1")return null;
  return {
    contract:dp.contract,
    next_1_3d:pick(dp.next_1_3d||{},["direction","summary"]),
    next_5_7d:pick(dp.next_5_7d||{},["direction","summary"]),
    next_2_3w:pick(dp.next_2_3w||{},["direction","summary"]),
    next_21_30d:pick(dp.next_21_30d||{},["direction","summary","regime_destination","expected_path","action_posture","confidence"]),
    weeks_4_8:pick(dp.weeks_4_8||{},["state","warning","direction","action_posture","summary","eta","confidence"]),
    protection:pick(dp.protection||{},["pullback_risk_state","pullback_class","distribution_risk","eta_window","confidence_quality","drivers","invalidation"])
  };
}
function sanitizePackage(pkg){return {...pick(pkg,["issue_number","previous_issue_number","generated_unix","status","market_state","base_case_this_week","base_case_2_3_weeks","base_case_4_8_weeks","compass_4_8_weeks","rotation_ladder","altseason_countdown","altseason_mania_window","uncertainties","publication_status"]),market_cycle_context:pick(pkg.market_cycle_context||{},["current_phase","why","next_gate"]),decision_projection:sanitizeDecisionProjection(pkg?.decision_projection),evaluation:pkg?.evaluation?pick(pkg.evaluation,["structural_score","price_range_score","score_status","strengths","misses"]):{},forecast_freeze:pkg?.forecast_freeze?pick(pkg.forecast_freeze,["breadth_condition","btc_range_low","btc_range_high","eth_range_low","eth_range_high","structural_calls","forecast_horizon_days","intraday_map"]):{}}}
async function readJson(path){return JSON.parse(await readFile(path,"utf8"))}
async function buildCompassSnapshot(weeklyPointer){
  try{
    const pointer=await readJson(COMPASS_POINTER_PATH);
    if(pointer?.contract!=="PUBLIC_COMPASS_LATEST_POINTER_v1") throw new Error("Unexpected public Compass pointer contract");
    const rel=pointer.public_projection_path;
    if(typeof rel!=="string"||!rel.startsWith("04_MARKET_LEARNING/handlekompas/official/public/")) throw new Error("Public Compass pointer escaped public projection root");
    const projectionPath=resolve(repoRoot,rel);
    if(relative(repoRoot,projectionPath).startsWith("..")) throw new Error("Public Compass path escaped repository");
    const projectionBytes=await readFile(projectionPath);
    const projectionContentSha=createHash("sha256").update(projectionBytes).digest("hex");
    if(projectionContentSha!==pointer?.public_projection_content_sha256) throw new Error("Public Compass pointer/projection content hash mismatch");
    const projection=JSON.parse(projectionBytes.toString("utf8"));
    if(projection?.contract!=="PUBLIC_COMPASS_PROJECTION_v1") throw new Error("Unexpected public Compass projection contract");
    if(projection?.compass_id!==pointer?.compass_id) throw new Error("Public Compass pointer/projection id mismatch");
    projection.weekly_context={contract:"CN_COMPASS_WEEKLY_ALIGNMENT_v1",status:"UNVERIFIED",forecast_week:null,public_issue_number:null,authority:false,semantics:"DELIVERY_ALIGNMENT_ONLY"};
    try{
      const internalPointer=await readJson(INTERNAL_COMPASS_POINTER_PATH);
      if(internalPointer?.contract!=="OFFICIAL_DAILY_COMPASS_LATEST_POINTER_v1") throw new Error("Unexpected internal Compass pointer contract");
      if(internalPointer?.compass_id!==projection.compass_id) throw new Error("Public/internal Compass id mismatch");
      const internalRel=internalPointer.compass_path;
      if(typeof internalRel!=="string"||!internalRel.startsWith("04_MARKET_LEARNING/handlekompas/official/daily/")) throw new Error("Internal Compass pointer escaped daily root");
      const internalPath=resolve(repoRoot,internalRel);
      if(relative(repoRoot,internalPath).startsWith("..")) throw new Error("Internal Compass path escaped repository");
      const internalBytes=await readFile(internalPath);
      const internalContentSha=createHash("sha256").update(internalBytes).digest("hex");
      if(internalContentSha!==internalPointer?.compass_content_sha256) throw new Error("Internal Compass pointer/content hash mismatch");
      const internalCompass=JSON.parse(internalBytes.toString("utf8"));
      if(internalCompass?.compass_id!==projection.compass_id) throw new Error("Internal/public Compass artifact mismatch");
      const cnBinding=internalCompass?.source_bindings?.cycle_navigator||{};
      const weeklyYear=Number(weeklyPointer?.iso_year),weeklyWeek=Number(weeklyPointer?.iso_week),weeklyIssue=Number(weeklyPointer?.issue_number);
      const boundYear=Number(cnBinding?.iso_year),boundWeek=Number(cnBinding?.iso_week),boundIssue=Number(cnBinding?.issue_number);
      const machineSha=String(cnBinding?.machine_package?.content_sha256||"");
      const aligned=cnBinding?.status==="PASS"&&Number.isInteger(weeklyYear)&&Number.isInteger(weeklyWeek)&&Number.isInteger(weeklyIssue)&&boundYear===weeklyYear&&boundWeek===weeklyWeek&&boundIssue===weeklyIssue&&machineSha!==""&&machineSha===String(weeklyPointer?.machine_package_sha256||"");
      projection.weekly_context={
        contract:"CN_COMPASS_WEEKLY_ALIGNMENT_v1",
        status:aligned?"ALIGNED":"MISMATCH",
        forecast_week:Number.isInteger(weeklyYear)&&Number.isInteger(weeklyWeek)?`${weeklyYear}-W${String(weeklyWeek).padStart(2,"0")}`:null,
        public_issue_number:aligned&&Number.isInteger(Number(weeklyPointer?.public_issue_number))?Number(weeklyPointer.public_issue_number):null,
        authority:false,
        semantics:"DELIVERY_ALIGNMENT_ONLY"
      };
    }catch{
      // Preserve the independently verified public Compass for NOW. Only PATH
      // live gates will fail closed when weekly lineage cannot be proven.
    }
    const [hourlyPointer,nativePointer]=await Promise.all([
      readJson(HOURLY_POINTER_PATH).catch(()=>null),
      readJson(NATIVE_COMPASS_POINTER_PATH).catch(()=>null)
    ]);
    projection.public_data_health={
      contract:"CN_PUBLIC_DATA_HEALTH_v1",
      hourly_status:typeof hourlyPointer?.status==="string"?hourlyPointer.status:"UNAVAILABLE",
      hourly_retrieved_at_utc:typeof hourlyPointer?.retrieved_at_utc==="string"?hourlyPointer.retrieved_at_utc:null,
      latest_complete_market_hour_utc:typeof hourlyPointer?.window_end_utc==="string"?hourlyPointer.window_end_utc:null,
      native_checked_at_utc:typeof nativePointer?.generated_at_utc==="string"?nativePointer.generated_at_utc:null,
      native_data_health:typeof nativePointer?.data_health==="string"?nativePointer.data_health:"UNAVAILABLE",
      weekly_cycle_navigator_available:true,
      authority:false
    };
    if(!projection.protection_tracker){
      projection.protection_tracker={
        contract:"COMPASS_PROTECTION_TRACKER_v1",
        pullback_risk_state:"UNAVAILABLE",
        pullback_class:"UNKNOWN",
        distribution_risk:"UNKNOWN",
        eta_window:"UNKNOWN",
        confidence_quality:"LOW",
        decisive_public_drivers:[],
        invalidation:"Fresh Official Compass evidence with the protection tracker is required.",
        last_material_change_at:null,
        data_quality:"DEGRADED",
        reentry_state:"UNAVAILABLE",
        reentry_message:"Re-entry review is unavailable until a fresh Official Compass publishes the canonical tracker.",
        authority:{portfolio_execution:false,wallet_specific:false,new_market_classifier:false}
      };
    }
    return projection;
  }catch(error){
    return {contract:"PUBLIC_COMPASS_PROJECTION_v1",compass_id:null,issued_at_utc:null,data_status:"NOT_PUBLISHED",weekly_context:{contract:"CN_COMPASS_WEEKLY_ALIGNMENT_v1",status:"UNVERIFIED",forecast_week:null,public_issue_number:null,authority:false,semantics:"DELIVERY_ALIGNMENT_ONLY"},market_now:{directional_state:"UNAVAILABLE",regime:"NOT_PUBLISHED",summary:"The official daily Compass has not been published yet."},horizons:{},capitalization_ladder:[],protection_tracker:{contract:"COMPASS_PROTECTION_TRACKER_v1",pullback_risk_state:"UNAVAILABLE",pullback_class:"UNKNOWN",distribution_risk:"UNKNOWN",eta_window:"UNKNOWN",confidence_quality:"LOW",decisive_public_drivers:[],invalidation:"Fresh Official Compass evidence is required.",last_material_change_at:null,data_quality:"DEGRADED",reentry_state:"UNAVAILABLE",reentry_message:"Re-entry review is unavailable.",authority:{portfolio_execution:false,wallet_specific:false,new_market_classifier:false}},sell_assessment:{contract:"COMPASS_SELL_ASSESSMENT_v1",state:"UNAVAILABLE",horizon:"UNKNOWN",eta:"UNKNOWN",reason:"A fresh governed sell/trim decision owner is not available.",protection_context:{pullback_risk_state:"UNAVAILABLE",distribution_risk:"UNKNOWN"},authority:{portfolio_execution:false,new_sell_rule:false,automatic_action:false,protection_is_sell_authority:false}},action_now:"UNAVAILABLE",next_meaningful_change_eta:null,conclusion:"Official daily Compass unavailable. No short-horizon signal is synthesized by the site.",authority:{official_navigation_output:true,portfolio_execution:false,source_override:false},failure_state:String(error?.message||error)};
  }
}
// PUBLIC_COMPASS_FULL_STACK_READBACK_v1: one safe, source-bound interpretation surface
// over the existing official decision + independent non-binding model research.
function verifiedRelative(p,prefix){
  if(typeof p!=="string"||!p.startsWith(prefix))return null;
  const resolved=resolve(repoRoot,p);
  const allowed=resolve(repoRoot,prefix);
  const within=relative(allowed,resolved);
  return within&&within!==".."&&!within.startsWith("../")&&!within.startsWith("..\\")?resolved:null;
}
function publicNarrative(s){
  if(typeof s!=="string"||s.length>650||/[0-9\\$%]|0x[0-9a-f]{8}|https?:|wallet|address|secret|token[-_ ]?key/i.test(s))return null;
  return s.trim()||null;
}
const researchEnum=(v,allowed,fallback="UNAVAILABLE")=>allowed.includes(v)?v:fallback;
// Producer digests canonical sorted-key JSON, with its hash field removed.
function sortedCanonical(v){
  if(Array.isArray(v))return v.map(sortedCanonical);
  if(v&&typeof v==="object")return Object.fromEntries(Object.keys(v).sort().map(k=>[k,sortedCanonical(v[k])]));
  return v;
}
function verifiedModelDigest(obj,field,expected){
  if(!obj||typeof expected!=="string"||!/^([a-f0-9]{64})$/.test(expected)||obj[field]!==expected)return false;
  const copy={...obj};delete copy[field];
  const digest=createHash("sha256").update(JSON.stringify(sortedCanonical(copy))+"\n").digest("hex");
  return digest===expected;
}
const directionValues=["UP","DOWN","SIDEWAYS","MIXED","NO_EDGE","UNAVAILABLE"];
async function buildFullStackReadback(compass,weeklyPointer,weeklyPackage){
  const [official,auto,native,shadowPtr,strategicPtr,master]=await Promise.all([
    readJson(INTERNAL_COMPASS_POINTER_PATH).catch(()=>null),
    readJson(AUTO_MARKET_STATE_POINTER_PATH).catch(()=>null),
    readJson(NATIVE_COMPASS_POINTER_PATH).catch(()=>null),
    readJson(SHADOW_COMPASS_V2_POINTER_PATH).catch(()=>null),
    readJson(STRATEGIC_COMPASS_POINTER_PATH).catch(()=>null),
    (async()=>{
      try{
        const handoff=await readJson(MASTER_MONDAY_HANDOFF_PATH);
        const meta=handoff?.pointers?.latest_weekly_output;
        const path=verifiedRelative(meta?.path,"research/api_agent/outputs/weekly/");
        if(!path)return null;
        const bytes=await readFile(path);
        const digest=createHash("sha256").update(bytes).digest("hex");
        if(digest!==meta?.sha256)return null;
        return {pointer:JSON.parse(bytes.toString("utf8")),digest};
      }catch{return null;}
    })()
  ]);
  const officialSource=official?.source_packet_sha256;
  const autoSource=auto?.packet_sha256;
  let autoValidated=false,nativeAligned=false;
  try{
    const p=verifiedRelative(auto?.packet_path,"04_MARKET_LEARNING/entry_signals/auto_market_state/runs/");
    const packet=p?await readJson(p):null;
    autoValidated=Boolean(packet?.contract==="AUTO_MARKET_STATE_PACKET_v1"&&
      verifiedModelDigest(packet,"packet_sha256",autoSource));
  }catch{}
  try{
    const p=verifiedRelative(native?.handlekompas_path,"04_MARKET_LEARNING/handlekompas/runs/");
    const run=p?await readJson(p):null;
    nativeAligned=Boolean(autoValidated&&officialSource&&officialSource===autoSource&&
      native?.source_packet_sha256===autoSource&&run?.contract==="NATIVE_HANDLEKOMPAS_v1"&&
      verifiedModelDigest(run,"handlekompas_sha256",native?.handlekompas_sha256)&&
      run?.source?.packet_sha256===autoSource&&run?.action?.NOW===native?.NOW);
  }catch{}
  let weeklyAligned=false;
  try{
    const p=verifiedRelative(String(weeklyPointer?.week_dir||"")+"/CYCLE_NAVIGATOR_MACHINE_PACKAGE.json","05_CYCLE_NAVIGATOR/weekly/");
    const bytes=p?await readFile(p):null;
    weeklyAligned=Boolean(bytes&&createHash("sha256").update(bytes).digest("hex")===weeklyPointer?.machine_package_sha256&&
      Number(weeklyPointer?.issue_number)===Number(weeklyPackage?.issue_number));
  }catch{}
  const mp=master?.pointer;
  const masterAligned=Boolean(mp?.contract==="MASTER_MONDAY_DELIVERY_POINTER_v1"&&mp?.status==="READY"&&
    mp?.iso_week===weeklyPointer?.completed_source_week&&mp?.iso_year===weeklyPointer?.completed_source_year&&
    master.digest===weeklyPointer?.master_monday_pointer_sha256);
  let shadow=null,shadowAligned=false;
  try{
    if(shadowPtr?.contract==="SHADOW_COMPASS_V2_LATEST_POINTER_v1"){
      const p=verifiedRelative(shadowPtr.forecast_path,"04_MARKET_LEARNING/handlekompas/shadow_v2/forecasts/");
      if(p){
        const x=await readJson(p);
        shadowAligned=autoValidated&&weeklyAligned&&x?.contract==="SHADOW_COMPASS_V2_FORECAST_v1"&&
          x?.forecast_id===shadowPtr.forecast_id&&
          verifiedModelDigest(x,"forecast_sha256",shadowPtr.forecast_sha256)&&
          x?.source_fingerprint===shadowPtr?.source_fingerprint&&
          Number(x?.source_bindings?.cycle_navigator?.iso_week)===Number(weeklyPointer?.iso_week)&&
          Number(x?.source_bindings?.cycle_navigator?.iso_year)===Number(weeklyPointer?.iso_year)&&
          x?.source_bindings?.cycle_navigator?.machine_package_sha256===weeklyPointer?.machine_package_sha256&&
          x?.source_bindings?.auto_market_state?.packet_sha256===autoSource&&
          x?.source_bindings?.auto_market_state?.packet_sha256===officialSource;
        if(shadowAligned){
          const ageHours=(Date.now()-Date.parse(x.issued_at_utc))/3600000;
          const sourceAgeHours=(Date.now()-Date.parse(auto?.packet_generated_at_utc))/3600000;
          const aged=!Number.isFinite(ageHours)||ageHours<0||ageHours>12||
                       !Number.isFinite(sourceAgeHours)||sourceAgeHours<0||sourceAgeHours>3;
          const horizons={};
          for(const [publicKey,sourceKey] of [["12h","12h"],["1_3d","72h"],["5_7d","168h"]]){
            const h=x?.model_output?.horizons?.[sourceKey]||{};
            horizons[publicKey]={
              direction:researchEnum(h.direction,directionValues),
              confidence:researchEnum(h.confidence,["LOW","MEDIUM","HIGH"],"LOW"),
              pullback_risk:researchEnum(h.pullback_risk,["NORMAL","BUILDING","ELEVATED","HIGH","UNAVAILABLE"]),
              transmission_state:researchEnum(h.transmission_state,["WEAK","MIXED","STRONG","UNCONFIRMED","UNAVAILABLE"]),
              interpretation:publicNarrative(h.expected_path)
            };
          }
          shadow={status:aged?"STALE_RESEARCH":"ALIGNED_RESEARCH",model:"GPT-6.1 Sol",issued_at_utc:x.issued_at_utc,
             authority:"RESEARCH_ONLY_NO_ACTION_PERMISSION",horizons};
        }
      }
    }
  }catch{}
  let strategic=null;
  try{
    if(strategicPtr?.contract==="STRATEGIC_COMPASS_LATEST_POINTER_v1"){
      const p=verifiedRelative(strategicPtr.anchor_path,"04_MARKET_LEARNING/handlekompas/strategic/anchors/");
      if(p){
        const anchor=await readJson(p);
        if(anchor.contract==="STRATEGIC_COMPASS_ANCHOR_v1"&&anchor.anchor_id===strategicPtr.anchor_id&&
           verifiedModelDigest(anchor,"anchor_sha256",strategicPtr.anchor_sha256)&&
           anchor.source_fingerprint===strategicPtr.source_fingerprint&&
           Number(anchor?.source_bindings?.cycle_navigator?.iso_year)===Number(weeklyPointer?.iso_year)&&
           Number(anchor?.source_bindings?.cycle_navigator?.iso_week)===Number(weeklyPointer?.iso_week)&&
           Number(anchor?.source_bindings?.cycle_navigator?.issue_number)===Number(weeklyPointer?.issue_number)&&
           anchor?.source_bindings?.cycle_navigator?.sha256===weeklyPointer?.machine_package_sha256&&weeklyAligned){
          strategic={status:"BOUND_WEEKLY_ANCHOR",issued_at_utc:anchor.issued_at_utc,
            horizon_21_30d:{direction:researchEnum(anchor?.strategic_21_30d?.direction,directionValues),
              action:researchEnum(anchor?.strategic_21_30d?.action_posture,["WAIT","HOLD","UNAVAILABLE"]),
              summary:publicNarrative(anchor?.strategic_21_30d?.summary)},
            horizon_4_8w:{direction:researchEnum(anchor?.cycle_4_8w?.direction,directionValues),
              status:researchEnum(anchor?.cycle_4_8w?.state,["UNCLEAR","CONSOLIDATION","ROTATION","DISTRIBUTION","UNAVAILABLE"])},
            authority:"CYCLE_NAVIGATOR_OWNED_NOT_NEW_SITE_FORECAST"};
        }
      }
    }
  }catch{}
  const officialValid=compass?.data_status==="OK"&&official?.compass_id===compass?.compass_id;
  const quality=officialValid&&nativeAligned&&shadow?.status==="ALIGNED_RESEARCH"&&masterAligned&&strategic&&weeklyAligned?"COMPLETE":"PARTIAL_OR_DEGRADED";
  return {
    contract:"PUBLIC_COMPASS_FULL_STACK_READBACK_v1",
    status:quality,
    generated_at_utc:new Date().toISOString(),
    source_status:{
      official:officialValid?"VERIFIED":"DEGRADED",
      auto_market_state:autoValidated?"HASH_VERIFIED":"UNVERIFIED",
      native:nativeAligned?"SOURCE_ALIGNED":"UNVERIFIED",
      shadow:shadow?.status||"UNVERIFIED",
      strategic:strategic?.status||"UNVERIFIED",
      master_monday:masterAligned?"SOURCE_ALIGNED":"UNVERIFIED",
      cycle_navigator:weeklyAligned?"WEEKLY_POINTER_ALIGNED":"UNVERIFIED"
    },
    official_action:officialValid?compass.action_now:"UNAVAILABLE",
    official_data_status:String(compass?.data_status||"NOT_PUBLISHED"),
    native:nativeAligned?{now:researchEnum(native.NOW,["HOLD_WAIT","PREPARE","BUY","HOLD","UNAVAILABLE"]),data_health:native.data_health||"UNAVAILABLE",checked_at_utc:native.generated_at_utc}:{now:"UNAVAILABLE",data_health:"UNVERIFIED"},
    shadow:shadow||{status:"UNVERIFIED",authority:"RESEARCH_ONLY_NO_ACTION_PERMISSION",horizons:{}},
    strategic:strategic||{status:"UNVERIFIED",authority:"CYCLE_NAVIGATOR_ONLY"},
    weekly:{status:String(weeklyPointer?.status||"UNAVAILABLE"),iso_week:weeklyPointer?.iso_week||null,iso_year:weeklyPointer?.iso_year||null,direction_2_3w:researchEnum(weeklyPackage?.decision_projection?.next_2_3w?.direction,directionValues)},
    protective_action_authority:"OFFICIAL_COMPASS_ONLY",
    conclusion:"Official decisions stay source-owned. Model research is context, not a confirmed buy/sell or an altseason trigger."
  };
}

async function buildCompassEventSnapshot(){
  try{
    const event=await readJson(COMPASS_EVENT_STATUS_PATH);
    if(event?.contract!=="PUBLIC_COMPASS_EVENT_STATUS_v1") throw new Error("Unexpected Compass event status contract");
    return pick(event,["contract","status","detected_at_utc","cause_codes","message","authority"]);
  }catch{
    return {contract:"PUBLIC_COMPASS_EVENT_STATUS_v1",status:"IDLE",detected_at_utc:null,cause_codes:[],message:null,authority:{official_compass_change:false,portfolio_execution:false}};
  }
}
await rm(outputDir,{recursive:true,force:true}); await mkdir(dataDir,{recursive:true});
const pointer=await readJson(POINTER_PATH); if(!pointer.week_dir) throw new Error("Canonical pointer has no week_dir");
const packagePath=resolve(repoRoot,pointer.week_dir,"CYCLE_NAVIGATOR_MACHINE_PACKAGE.json"); const pkg=await readJson(packagePath);
if(Number(pointer.issue_number)!==Number(pkg.issue_number)) throw new Error("Pointer/package issue mismatch");
const standaloneFreeze=await readJson(resolve(repoRoot,pointer.week_dir,"CYCLE_NAVIGATOR_FORECAST_FREEZE.json")).catch(()=>null);
const rangeScore=await readJson(RANGE_SCORE_PATH).catch(()=>null);
const prospectiveRange=await readJson(PROSPECTIVE_RANGE_PATH).catch(()=>null);
const publicSeriesRaw=await readJson(PUBLIC_SERIES_INDEX_PATH).catch(()=>null);
let publicScorecard=null;
if(publicSeriesRaw?.latest_completed_score?.scorecard_path){
  const rel=String(publicSeriesRaw.latest_completed_score.scorecard_path);
  if(!rel.startsWith("05_CYCLE_NAVIGATOR/public_scorecards/")||rel.includes("..")) throw new Error("Public CN scorecard path escaped approved root");
  publicScorecard=await readJson(resolve(repoRoot,rel));
}
const publicSeries=publicSeriesRaw?{
  contract:publicSeriesRaw.contract,
  latest_published:pick(publicSeriesRaw.latest_published||{},["public_issue_number","forecast_week"]),
  latest_completed_score:pick(publicSeriesRaw.latest_completed_score||{},["public_issue_number","forecast_week","price_range_score","market_structure_status","status"]),
  current_public_projection:pick(publicSeriesRaw.current_public_projection||{},["public_issue_number","forecast_week","publication_status"])
}:null;

function weeklyDir(value){
  const rel=String(value||"");
  return rel.startsWith("05_CYCLE_NAVIGATOR/weekly/")&&!rel.includes("..")?rel:null;
}
const comparisonFields=[
  ["ETH/BTC condition","ethbtc_condition"],
  ["Breadth condition","breadth_condition"]
];
function exactFreezeComparison(previousFreeze,currentFreeze){
  const changed=[],stillTrue=[];
  for(const [label,key] of comparisonFields){
    const previous=typeof previousFreeze?.[key]==="string"?previousFreeze[key].trim():"";
    const current=typeof currentFreeze?.[key]==="string"?currentFreeze[key].trim():"";
    if(!previous||!current)continue;
    const row={label,previous,current};
    (previous===current?stillTrue:changed).push(row);
  }
  return {changed:changed.slice(0,2),still_true:stillTrue.slice(0,2)};
}
function publicStructureAnalysis(freeze){
  const expected=["REGIME_RESILIENCE","LEADERSHIP","ROTATION_TRANSMISSION","BREADTH_PERSISTENCE","FLOW_QUALITY_FRAGILITY"];
  const governed=freeze?.market_structure_analysis;
  const governedDims=Array.isArray(governed?.dimensions)?governed.dimensions:[];
  if(governed?.contract==="CN_PUBLIC_MARKET_STRUCTURE_ANALYSIS_v1"&&governed?.scoring_authority===false&&governedDims.length===5&&governedDims.every((x,i)=>x?.id===expected[i]&&typeof x?.label==="string"&&typeof x?.analysis==="string"&&x.analysis.trim())){
    return {contract:"CN_PUBLIC_MARKET_STRUCTURE_PRESENTATION_v1",source:"CYCLE_NAVIGATOR_FORECAST_FREEZE.market_structure_analysis.dimensions",dimensions:governedDims.map(x=>({id:x.id,label:x.label,analysis:x.analysis}))};
  }
  const legacy=freeze?.market_structure_v2;
  const legacyDims=Array.isArray(legacy?.dimensions)?legacy.dimensions:[];
  if(legacy?.contract==="CN_PUBLIC_MARKET_STRUCTURE_V2"&&legacy?.status==="FROZEN_PROSPECTIVE"&&legacyDims.length===5&&legacyDims.every(x=>typeof x?.label==="string"&&typeof x?.forecast==="string"&&x.forecast.trim())){
    return {contract:"CN_PUBLIC_MARKET_STRUCTURE_PRESENTATION_v1",source:"CYCLE_NAVIGATOR_FORECAST_FREEZE.market_structure_v2.dimensions",dimensions:legacyDims.map(x=>({id:x.id,label:x.label,analysis:x.forecast}))};
  }
  return null;
}
async function deriveSinceLastCN(series,currentFreeze){
  try{
    const current=series?.current_public_projection;
    const currentIssue=Number(current?.public_issue_number);
    const previous=(series?.recent_lineage||[]).find(row=>Number(row?.public_issue_number)===currentIssue-1);
    const previousDir=weeklyDir(previous?.machine_week_dir);
    if(!Number.isInteger(currentIssue)||!previousDir||!currentFreeze)return null;
    const previousFreeze=await readJson(resolve(repoRoot,previousDir,"CYCLE_NAVIGATOR_FORECAST_FREEZE.json"));
    const comparison=exactFreezeComparison(previousFreeze,currentFreeze);
    if(!comparison.changed.length&&!comparison.still_true.length)return null;
    return {contract:"CN_PUBLIC_SINCE_LAST_V1",comparison_method:"EXACT_GOVERNED_FIELD_EQUALITY",current_public_issue:currentIssue,previous_public_issue:currentIssue-1,...comparison};
  }catch{return null;}
}
async function deriveLatestCompletedForecast(series,currentPackage){
  try{
    const latest=series?.latest_completed_score;
    const completedIssue=Number(latest?.public_issue_number);
    const scorecardPath=String(latest?.scorecard_path||"");
    if(!Number.isInteger(completedIssue)||!scorecardPath.startsWith("05_CYCLE_NAVIGATOR/public_scorecards/")||scorecardPath.includes(".."))return null;
    await readFile(resolve(repoRoot,scorecardPath),"utf8");
    const currentPublicIssue=Number(series?.current_public_projection?.public_issue_number);
    const evaluation=currentPublicIssue===completedIssue+1?currentPackage?.evaluation:null;
    const held=Array.isArray(evaluation?.strengths)?evaluation.strengths.filter(x=>typeof x==="string"&&x.trim()).slice(0,2):[];
    const missed=Array.isArray(evaluation?.misses)?evaluation.misses.filter(x=>typeof x==="string"&&x.trim()).slice(0,2):[];
    return {contract:"CN_PUBLIC_COMPLETED_FORECAST_RECEIPT_v1",public_issue_number:completedIssue,forecast_week:String(latest?.forecast_week||""),status:String(latest?.status||"FINAL"),price_range_score:typeof latest?.price_range_score==="number"&&Number.isFinite(latest.price_range_score)?latest.price_range_score:null,held_up:held,missed,exact_ledger_issue:completedIssue};
  }catch{return null;}
}
const sinceLastCN=await deriveSinceLastCN(publicSeriesRaw,standaloneFreeze);
const latestCompletedForecast=await deriveLatestCompletedForecast(publicSeriesRaw,pkg);

// Presentation-only Danish prose from the same bound weekly synthesis. Legacy sources use the curated UI catalog.
function publicTranslations(source){
  const allowed=new Set();
  const walk=v=>{if(typeof v==="string")allowed.add(v);else if(Array.isArray(v))v.forEach(walk);else if(v&&typeof v==="object")Object.values(v).forEach(walk);};
  const safe=sanitizePackage(source);walk(safe);
  // Only already public forecast/evaluation prose can be a translation source.
  walk(publicStructureAnalysis(standaloneFreeze));walk(standaloneFreeze?.intraday_map);walk(standaloneFreeze?.bull_bear_scale);const copy=source?.decision_projection?.protection?.public_explanation;
  if(copy?.contract==='CN_PUBLIC_PROTECTION_COPY_v1')for(const key of ['summary','watch_for','weakens_if']){const text=copy[key];if(typeof text==='string'&&text.length<=600&&!/\d/.test(text))walk(text);}
  const digits=t=>JSON.stringify(t.match(/[+−-]?\d+(?:[.,]\d+)*(?:%)?/g)||[]);
  return (Array.isArray(source?.public_translations)?source.public_translations:[]).filter(x=>x&&typeof x.en==='string'&&typeof x.da==='string'&&x.en.length>15&&x.en.length<=3000&&x.da.length<=4000&&x.da.trim()&&allowed.has(x.en)&&digits(x.en)===digits(x.da)).map(x=>({en:x.en,da:x.da})).slice(0,160);
}
const snapshot={schema:"CN_PUBLIC_SNAPSHOT_V2",generated_at:new Date().toISOString(),authority:false,presentation_translations:publicTranslations(pkg),pointer:sanitizePointer(pointer),package:sanitizePackage(pkg),public_series:publicSeries,public_scorecard:publicScorecard,range_score:rangeScore,prospective_range:prospectiveRange,public_market_structure_analysis:publicStructureAnalysis(standaloneFreeze),public_bull_bear_scale:standaloneFreeze?.bull_bear_scale||null,since_last_cn:sinceLastCN,latest_completed_forecast:latestCompletedForecast};
const compass=await buildCompassSnapshot(pointer);
compass.full_stack=await buildFullStackReadback(compass,pointer,pkg);
const compassEvent=await buildCompassEventSnapshot();
await writeFile(resolve(dataDir,"latest.json"),JSON.stringify(snapshot,null,2)+"\n");
await writeFile(resolve(dataDir,"compass.json"),JSON.stringify(compass,null,2)+"\n");
await writeFile(resolve(dataDir,"compass-event.json"),JSON.stringify(compassEvent,null,2)+"\n");
for(const file of PUBLIC_SITE_FILES){await copyFile(resolve(siteDir,file),resolve(outputDir,file));}
const indexPath=resolve(outputDir,"index.html"); let index=await readFile(indexPath,"utf8");
if(!index.includes("./compass-product-v5.css")) index=index.replace("</head>",'  <link rel="stylesheet" href="./compass-product-v5.css" />\n</head>');
if(!index.includes("./compass-product-v5.js")) index=index.replace("</body>",'  <script src="./compass-product-v5.js" defer></script>\n</body>');
await writeFile(indexPath,index,"utf8");
console.log(`Cycle Navigator public v2 built: issue #${pkg.issue_number}; Compass ${compass.compass_id||compass.data_status}`);
