import { mkdir, readFile, rm, writeFile, copyFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { dirname, resolve, relative } from "node:path";
import { fileURLToPath } from "node:url";
const siteDir=dirname(fileURLToPath(import.meta.url)); const repoRoot=resolve(siteDir,"../.."); const outputDir=resolve(siteDir,"dist"); const dataDir=resolve(outputDir,"data");
const POINTER_PATH=resolve(repoRoot,"05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json");
const COMPASS_POINTER_PATH=resolve(repoRoot,"04_MARKET_LEARNING/handlekompas/official/PUBLIC_LATEST_COMPASS.json");
const COMPASS_EVENT_STATUS_PATH=resolve(repoRoot,"04_MARKET_LEARNING/handlekompas/event_refresh/PUBLIC_STATUS.json");
const RANGE_SCORE_PATH=resolve(repoRoot,"05_CYCLE_NAVIGATOR/LATEST_RANGE_SCORE.json");
const PROSPECTIVE_RANGE_PATH=resolve(repoRoot,"05_CYCLE_NAVIGATOR/LATEST_PROSPECTIVE_RANGE.json");
const PUBLIC_SERIES_INDEX_PATH=resolve(repoRoot,"05_CYCLE_NAVIGATOR/public_series/CN_PUBLIC_SERIES_INDEX.json");
const PUBLIC_SITE_FILES=["index.html","styles.css","scoreboard.css","motion.css","journey.css","vibe.css","app.js","compass.js","compass-product-v5.js","compass-product-v5.css","history-scoreboard.js","history-scoreboard.json","motion.js","journey.js","live-context.js","favicon.svg","social-card.svg"];
const pick=(obj,keys)=>Object.fromEntries(keys.filter(k=>Object.prototype.hasOwnProperty.call(obj||{},k)).map(k=>[k,obj[k]]));
const sanitizePointer=p=>pick(p,["iso_year","iso_week","completed_source_week","issue_number","publication_status","status"]);
function sanitizePackage(pkg){return {...pick(pkg,["issue_number","previous_issue_number","generated_unix","status","market_state","base_case_this_week","base_case_2_3_weeks","base_case_4_8_weeks","compass_4_8_weeks","rotation_ladder","altseason_countdown","altseason_mania_window","uncertainties","publication_status"]),evaluation:pkg?.evaluation?pick(pkg.evaluation,["structural_score","price_range_score","score_status","strengths","misses"]):{},forecast_freeze:pkg?.forecast_freeze?pick(pkg.forecast_freeze,["breadth_condition","btc_range_low","btc_range_high","eth_range_low","eth_range_high","structural_calls","forecast_horizon_days","intraday_map"]):{}}}
async function readJson(path){return JSON.parse(await readFile(path,"utf8"))}
async function buildCompassSnapshot(){
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
    return {contract:"PUBLIC_COMPASS_PROJECTION_v1",compass_id:null,issued_at_utc:null,data_status:"NOT_PUBLISHED",market_now:{directional_state:"UNAVAILABLE",regime:"NOT_PUBLISHED",summary:"The official daily Compass has not been published yet."},horizons:{},capitalization_ladder:[],protection_tracker:{contract:"COMPASS_PROTECTION_TRACKER_v1",pullback_risk_state:"UNAVAILABLE",pullback_class:"UNKNOWN",distribution_risk:"UNKNOWN",eta_window:"UNKNOWN",confidence_quality:"LOW",decisive_public_drivers:[],invalidation:"Fresh Official Compass evidence is required.",last_material_change_at:null,data_quality:"DEGRADED",reentry_state:"UNAVAILABLE",reentry_message:"Re-entry review is unavailable.",authority:{portfolio_execution:false,wallet_specific:false,new_market_classifier:false}},sell_assessment:{contract:"COMPASS_SELL_ASSESSMENT_v1",state:"UNAVAILABLE",horizon:"UNKNOWN",eta:"UNKNOWN",reason:"A fresh governed sell/trim decision owner is not available.",protection_context:{pullback_risk_state:"UNAVAILABLE",distribution_risk:"UNKNOWN"},authority:{portfolio_execution:false,new_sell_rule:false,automatic_action:false,protection_is_sell_authority:false}},action_now:"UNAVAILABLE",next_meaningful_change_eta:null,conclusion:"Official daily Compass unavailable. No short-horizon signal is synthesized by the site.",authority:{official_navigation_output:true,portfolio_execution:false,source_override:false},failure_state:String(error?.message||error)};
  }
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
function freezeSignals(freeze){
  const text=[freeze?.ethbtc_condition,freeze?.breadth_condition,...(Array.isArray(freeze?.structural_calls)?freeze.structural_calls:[])].join(" ").toLowerCase();
  const eth=/at or below|weaken|fell|declin/.test(text)?"WEAKENING_OR_AT_RISK":/non-negative|higher|stabili[sz]/.test(text)?"STABLE_OR_SUPPORTED":"UNAVAILABLE";
  const pullback=/pullback|retest/.test(text)?"ACTIVE_WATCH":"NOT_CALLED";
  const broad=/broad[^.]{0,80}(not|unconfirmed|inactive)|not[^.]{0,80}broad|inactive[^.]{0,80}altseason/.test(text)?"UNCONFIRMED":/broad[^.]{0,80}(confirm|expansion)|altseason[^.]{0,80}(confirm|active)/.test(text)?"CONFIRMED_OR_ACTIVE":"UNAVAILABLE";
  return {eth_relative:eth,pullback_watch:pullback,broad_altseason:broad};
}
function sentenceList(markdown,patterns,limit=2){
  const text=String(markdown||"").replace(/\*\*/g,"").replace(/[_#>]/g," ").replace(/\s+/g," ").trim();
  const sentences=text.split(/(?<=[.!?])\s+/).map(s=>s.trim()).filter(Boolean);
  return sentences.filter(s=>patterns.some(p=>p.test(s))).slice(0,limit);
}
async function deriveSinceLastCN(series,currentFreeze){
  try{
    const current=series?.current_public_projection;
    const currentIssue=Number(current?.public_issue_number);
    const previous=(series?.recent_lineage||[]).find(row=>Number(row?.public_issue_number)===currentIssue-1);
    const previousDir=weeklyDir(previous?.machine_week_dir);
    if(!Number.isInteger(currentIssue)||!previousDir||!currentFreeze)return null;
    const previousFreeze=await readJson(resolve(repoRoot,previousDir,"CYCLE_NAVIGATOR_FORECAST_FREEZE.json"));
    const before=freezeSignals(previousFreeze),after=freezeSignals(currentFreeze);
    const changed=[];
    if(before.eth_relative!==after.eth_relative&&after.eth_relative!=="UNAVAILABLE")changed.push(after.eth_relative==="WEAKENING_OR_AT_RISK"?"ETH-relative strength moved to active risk watch.":"ETH-relative condition changed in the current frozen forecast.");
    if(before.pullback_watch!==after.pullback_watch&&after.pullback_watch==="ACTIVE_WATCH")changed.push("Pullback / retest risk moved to active watch.");
    const still=[];
    if(before.broad_altseason==="UNCONFIRMED"&&after.broad_altseason==="UNCONFIRMED")still.push("Broad altseason remains unconfirmed.");
    if(!changed.length&&!still.length)return null;
    return {contract:"CN_PUBLIC_SINCE_LAST_V1",current_public_issue:currentIssue,previous_public_issue:currentIssue-1,changed:changed.slice(0,2),still_true:still.slice(0,2)};
  }catch{return null;}
}
async function deriveLatestCompletedForecast(series){
  try{
    const latest=series?.latest_completed_score;
    const current=series?.current_public_projection;
    const completedIssue=Number(latest?.public_issue_number),currentIssue=Number(current?.public_issue_number);
    const outcome=(series?.recent_lineage||[]).find(row=>Number(row?.public_issue_number)===completedIssue+1);
    if(!Number.isInteger(completedIssue)||currentIssue!==completedIssue+1||!outcome?.published_path||!String(outcome.published_path).startsWith("05_CYCLE_NAVIGATOR/published/"))return null;
    const markdown=await readFile(resolve(repoRoot,outcome.published_path),"utf8");
    const held=sentenceList(markdown,[/Both weekly BTC and ETH ranges contained/i,/Price structure held better/i,/broader regime right/i]);
    const missed=sentenceList(markdown,[/ETH\/BTC weakened/i,/transmission stayed selective/i,/BTC broke both boundaries/i,/main price miss/i]);
    return {contract:"CN_PUBLIC_COMPLETED_FORECAST_RECEIPT_v1",public_issue_number:completedIssue,forecast_week:String(latest?.forecast_week||""),status:String(latest?.status||"FINAL"),price_range_score:Number.isFinite(Number(latest?.price_range_score))?Number(latest.price_range_score):null,held_up:held,missed,exact_ledger_issue:completedIssue};
  }catch{return null;}
}
const sinceLastCN=await deriveSinceLastCN(publicSeriesRaw,standaloneFreeze);
const latestCompletedForecast=await deriveLatestCompletedForecast(publicSeriesRaw);

const snapshot={schema:"CN_PUBLIC_SNAPSHOT_V2",generated_at:new Date().toISOString(),authority:false,pointer:sanitizePointer(pointer),package:sanitizePackage(pkg),public_series:publicSeries,public_scorecard:publicScorecard,range_score:rangeScore,prospective_range:prospectiveRange,public_market_structure_analysis:standaloneFreeze?.market_structure_analysis||null,public_bull_bear_scale:standaloneFreeze?.bull_bear_scale||null,since_last_cn:sinceLastCN,latest_completed_forecast:latestCompletedForecast};
const compass=await buildCompassSnapshot();
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
