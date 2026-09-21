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
    return {contract:"PUBLIC_COMPASS_PROJECTION_v1",compass_id:null,issued_at_utc:null,data_status:"NOT_PUBLISHED",market_now:{directional_state:"UNAVAILABLE",regime:"NOT_PUBLISHED",summary:"The official daily Compass has not been published yet."},horizons:{},capitalization_ladder:[],protection_tracker:{contract:"COMPASS_PROTECTION_TRACKER_v1",pullback_risk_state:"UNAVAILABLE",pullback_class:"UNKNOWN",distribution_risk:"UNKNOWN",eta_window:"UNKNOWN",confidence_quality:"LOW",decisive_public_drivers:[],invalidation:"Fresh Official Compass evidence is required.",last_material_change_at:null,data_quality:"DEGRADED",reentry_state:"UNAVAILABLE",reentry_message:"Re-entry review is unavailable.",authority:{portfolio_execution:false,wallet_specific:false,new_market_classifier:false}},action_now:"UNAVAILABLE",next_meaningful_change_eta:null,conclusion:"Official daily Compass unavailable. No short-horizon signal is synthesized by the site.",authority:{official_navigation_output:true,portfolio_execution:false,source_override:false},failure_state:String(error?.message||error)};
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
const rangeScore=await readJson(RANGE_SCORE_PATH).catch(()=>null);
const prospectiveRange=await readJson(PROSPECTIVE_RANGE_PATH).catch(()=>null);
const publicSeries=await readJson(PUBLIC_SERIES_INDEX_PATH).catch(()=>null);
let publicScorecard=null;
if(publicSeries?.latest_completed_score?.scorecard_path){
  const rel=String(publicSeries.latest_completed_score.scorecard_path);
  if(!rel.startsWith("05_CYCLE_NAVIGATOR/public_scorecards/")||rel.includes("..")) throw new Error("Public CN scorecard path escaped approved root");
  publicScorecard=await readJson(resolve(repoRoot,rel));
}
const snapshot={schema:"CN_PUBLIC_SNAPSHOT_V2",generated_at:new Date().toISOString(),authority:false,pointer:sanitizePointer(pointer),package:sanitizePackage(pkg),public_series:publicSeries,public_scorecard:publicScorecard,range_score:rangeScore,prospective_range:prospectiveRange};
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
