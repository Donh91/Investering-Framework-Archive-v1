import { mkdir, readFile, rm, writeFile, copyFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
const siteDir=dirname(fileURLToPath(import.meta.url)); const repoRoot=resolve(siteDir,"../.."); const outputDir=resolve(siteDir,"dist"); const dataDir=resolve(outputDir,"data");
const POINTER_PATH=resolve(repoRoot,"05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json");
const PUBLIC_SITE_FILES=["index.html","styles.css","motion.css","journey.css","vibe.css","app.js","history-scoreboard.js","history-scoreboard.json","motion.js","journey.js","live-context.js","favicon.svg","social-card.svg"];
const pick=(obj,keys)=>Object.fromEntries(keys.filter(k=>Object.prototype.hasOwnProperty.call(obj||{},k)).map(k=>[k,obj[k]]));
const sanitizePointer=p=>pick(p,["iso_year","iso_week","completed_source_week","issue_number","publication_status","status"]);
function sanitizePackage(pkg){return {...pick(pkg,["issue_number","previous_issue_number","generated_unix","status","market_state","base_case_this_week","base_case_2_3_weeks","base_case_4_8_weeks","compass_4_8_weeks","rotation_ladder","altseason_countdown","altseason_mania_window","uncertainties","publication_status"]),evaluation:pkg?.evaluation?pick(pkg.evaluation,["structural_score","score_status","strengths","misses"]):{},forecast_freeze:pkg?.forecast_freeze?pick(pkg.forecast_freeze,["breadth_condition","btc_range_low","btc_range_high","eth_range_low","eth_range_high","structural_calls","forecast_horizon_days","intraday_map"]):{}}}
async function readJson(path){return JSON.parse(await readFile(path,"utf8"))}
await rm(outputDir,{recursive:true,force:true}); await mkdir(dataDir,{recursive:true});
const pointer=await readJson(POINTER_PATH); if(!pointer.week_dir) throw new Error("Canonical pointer has no week_dir");
const packagePath=resolve(repoRoot,pointer.week_dir,"CYCLE_NAVIGATOR_MACHINE_PACKAGE.json"); const pkg=await readJson(packagePath);
if(Number(pointer.issue_number)!==Number(pkg.issue_number)) throw new Error("Pointer/package issue mismatch");
const snapshot={schema:"CN_PUBLIC_SNAPSHOT_V2",generated_at:new Date().toISOString(),authority:false,pointer:sanitizePointer(pointer),package:sanitizePackage(pkg)};
await writeFile(resolve(dataDir,"latest.json"),JSON.stringify(snapshot,null,2)+"\n");
for(const file of PUBLIC_SITE_FILES){await copyFile(resolve(siteDir,file),resolve(outputDir,file));}
console.log(`Cycle Navigator public v2 built: issue #${pkg.issue_number}`);