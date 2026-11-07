/* S1 Agent Operations Context v1
 * Canonical public source metadata only. No secrets, source writes, scheduling,
 * privileged API calls, merge approval, review, S1 attribution or trading.
 */
import { createHash } from 'node:crypto';
import { writeFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';

const REPO='Donh91/Investering-Framework-Archive-v1';
const API='https://api.github.com/repos/'+REPO;
const HTTPS='https://github.com/'+REPO;
const SHA40=/^[0-9a-f]{40}$/i;
const PATHS=Object.freeze([
 {id:'operations',path:'LATEST_OPERATIONS_DASHBOARD.json',maxAgeMinutes:180,owner:'ORIGINAL_OPERATIONS_DASHBOARD'},
 {id:'handoff',path:'LATEST_HANDOFF.json',maxAgeMinutes:180,owner:'ORIGINAL_AUTOMATION_HANDOFF'},
 {id:'codex_ready',path:'LATEST_CODEX_READY_TASKS.json',maxAgeMinutes:1440,owner:'ORIGINAL_CODEX_INTAKE'},
 {id:'codex_execution',path:'LATEST_CODEX_EXECUTION_STATE.json',maxAgeMinutes:1440,owner:'ORIGINAL_CODEX_EXECUTION_LEDGER'},
 {id:'remediation',path:'LATEST_REMEDIATION_QUEUE.json',maxAgeMinutes:720,owner:'ORIGINAL_REMEDIATION_CONTROLLER'},
 {id:'automation_health',path:'research/architecture_health/LATEST_AUTOMATION_HEALTH.json',maxAgeMinutes:360,owner:'ORIGINAL_AUTOMATION_HEALTH'},
 {id:'architecture_health',path:'research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json',maxAgeMinutes:360,owner:'ORIGINAL_ARCHITECTURE_HEALTH'}
]);
const headFor=(path,sha)=>HTTPS+'/blob/'+sha+'/'+path;
function safeCount(v){return Number.isSafeInteger(v)&&v>=0?v:null;}
function jsonSafe(s){if(typeof s!=='string'||s.length>2e6)throw Error('SOURCE_BYTES_UNBOUNDED');return JSON.parse(s)}
function digest(bytes){return createHash('sha256').update(bytes).digest('hex')}
function gitBlobSha1(bytes){return createHash('sha1').update('blob '+bytes.length+'\0').update(bytes).digest('hex')}
function ageOf(sourceTime,observedAt,maxAgeMinutes){
 const t=Date.parse(sourceTime),n=Date.parse(observedAt);
 if(!Number.isFinite(t)||!Number.isFinite(n)||t>n+60000)return {status:'UNOBSERVED',minutes:null};
 const minutes=Math.max(0,Math.floor((n-t)/60000));
 return {status:minutes<=maxAgeMinutes?'FRESH_ADVISORY':'STALE',minutes};
}
async function get(fetcher,url){
 const response=await fetcher(url,{headers:{Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'}});
 if(!response||!response.ok)throw Error('GITHUB_HTTP_'+String(response?.status||'UNOBSERVED'));
 return response.json();
}
async function mainSha(fetcher){
 const j=await get(fetcher,API+'/branches/main');
 if(!SHA40.test(j?.commit?.sha||''))throw Error('MAIN_SHA_UNOBSERVED');
 return j.commit.sha;
}
function publicSafeSummary(id,data){
 if(!data||typeof data!=='object'||Array.isArray(data))return {};
 if(id==='operations')return {
   overall_status:typeof data.overall_status==='string'?data.overall_status:null,
   openai_api_spend_estimate_usd:null, // private/sensitive billing and charge-once authority intentionally excluded
   incident_count:safeCount(data.incidents?.open_count)??null,
   source_coverage:typeof data.source_coverage==='string'?data.source_coverage:null,
   original_required_actions:Array.isArray(data.required_actions)?data.required_actions.slice(0,8)
     .filter(x=>x&&typeof x.priority==='string'&&typeof x.reason==='string'&&typeof x.system==='string')
     .map(x=>({priority:x.priority,reason:x.reason,system:x.system,owner:'ORIGINAL_OPERATIONS_DASHBOARD',advisory_only:true})):[]

 };
 if(id==='handoff')return {
   codex_ready_task_count:safeCount(data.codex_ready_task_count),
   open_incident_sample_count:Array.isArray(data.open_incidents)?data.open_incidents.length:null,
   open_incident_list_truncated:typeof data.open_incidents_truncated==='boolean'?data.open_incidents_truncated:null
 };
 if(id==='codex_ready')return {
   codex_ready_task_count:Array.isArray(data.tasks)?data.tasks.length:null,
   source_is_queue_authority:true,
   task_refs:Array.isArray(data.tasks)?data.tasks.slice(0,8).map(t=>({
     id:typeof t.candidate_id==='string'?t.candidate_id:null,
     owner:'EXISTING_CODEX_INTAKE',
     route:typeof t.route==='string'?t.route:'UNOBSERVED',
     state:typeof t.lifecycle_state==='string'?t.lifecycle_state:'UNOBSERVED',
     source_path:typeof t.candidate_path==='string'&&t.candidate_path.startsWith('research/codex/intake/')&&!t.candidate_path.includes('..')?t.candidate_path:null,
     finding:typeof t.finding==='string'?t.finding.slice(0,200):null,
     original_signature:typeof t.signature==='string'?t.signature.slice(0,80):null,
     observed_at_utc:typeof t.last_observed_at_utc==='string'?t.last_observed_at_utc:null,
     risk_class:typeof t.risk_class==='string'?t.risk_class:null,
     source_is_remediation_authority:false,code_execution_proven:false
   })):[]
 };
 if(id==='codex_execution')return {
   summary:Object.fromEntries(['codex_ready','in_remediation','needs_more_evidence','post_fix_observation','resolved','total']
     .map(k=>[k,safeCount(data.summary?.[k])])),
   queue_authority:data.queue_authority==='LATEST_CODEX_READY_TASKS.json'?'LATEST_CODEX_READY_TASKS.json':'UNOBSERVED',
   source_is_queue_authority:false
 };
 if(id==='remediation')return {
   summary:Object.fromEntries(['active_remediation','codex_ready','needs_more_evidence','research_intake','research_intake_errors','total']
     .map(k=>[k,safeCount(data.summary?.[k])])),
   automatic_merge:data.automatic_merge===true?'REQUIRES_REEVALUATION':false,
   automatic_code_write:data.automatic_code_write===true?'REQUIRES_REEVALUATION':false
 };
 if(id==='automation_health')return {
   reported_status:typeof data.status==='string'?data.status:null,
   reported_green_count:safeCount(data.green_count),reported_amber_count:safeCount(data.amber_count),
   reported_red_count:safeCount(data.red_count)
 };
 if(id==='architecture_health')return {
   reported_status:typeof data.status==='string'?data.status:null,
   reported_aggregate_system_health_claim:data.aggregate_system_health_claim===false?false:'UNOBSERVED'
 };
 return {};
}
async function readFrozenSource(fetcher,main,id,observedAt){
 const spec=PATHS.find(x=>x.id===id);
 if(!spec||!SHA40.test(main))throw Error('INVALID_CANONICAL_SOURCE');
 const sourceUrl=API+'/contents/'+spec.path+'?ref='+main;
 const pinnedUrl=headFor(spec.path,main);
 try{
   const body=await get(fetcher,sourceUrl);
   if(!SHA40.test(body.sha||'')||body.encoding!=='base64'||typeof body.content!=='string')throw Error('SOURCE_CONTENT_IDENTITY_INVALID');
   const bytes=Buffer.from(body.content.replace(/\s/g,''),'base64');
   if(bytes.length===0||bytes.length>2e6||bytes.length!==body.size)throw Error('SOURCE_BYTE_COUNT_INVALID');
   if(gitBlobSha1(bytes)!==body.sha)throw Error('SOURCE_BLOB_SHA_MISMATCH');
   const data=jsonSafe(bytes.toString('utf8'));
   const generated=typeof data.generated_at_utc==='string'?data.generated_at_utc:null;
   const age=ageOf(generated,observedAt,spec.maxAgeMinutes);
   const summary=publicSafeSummary(id,data);
   if(id==='codex_ready'&&Array.isArray(summary.task_refs))summary.task_refs=summary.task_refs.map(task=>({
     ...task,source_url:task.source_path?headFor(task.source_path,main):null
   }));
   return {id,status:age.status==='UNOBSERVED'?'UNOBSERVED':'OBSERVED',freshness:age.status,
     age_minutes:age.minutes,source_contract:typeof data.contract==='string'?data.contract:null,
     owner:spec.owner,main_sha:main,blob_sha:body.sha,sha256:digest(bytes),
     bytes:bytes.length,source_path:spec.path,source_url:pinnedUrl,
     generated_at_utc:generated,observed_at_utc:observedAt,
     summary,release_authority:false};
 }catch(err){
   return {id,status:'UNOBSERVED',freshness:'UNOBSERVED',owner:spec.owner,
     main_sha:main,source_path:spec.path,source_url:pinnedUrl,
     reason:String(err.message||err).slice(0,120),release_authority:false};
 }
}
export async function buildAgentContext({fetcher=fetch,clock=()=>new Date().toISOString(),sources=PATHS.map(x=>x.id)}={}){
 if(!Array.isArray(sources)||!sources.length||sources.length>PATHS.length||new Set(sources).size!==sources.length||
     sources.some(id=>!PATHS.some(x=>x.id===id)))throw Error('SOURCE_ALLOWLIST_REQUIRED');
 const observedAt=clock();let before=null,after=null,errors=[];
 try{before=await mainSha(fetcher)}catch(e){errors.push('MAIN_PREFLIGHT_'+String(e.message||e).slice(0,80))}
 const rows=before?await Promise.all(sources.map(id=>readFrozenSource(fetcher,before,id,observedAt))):[];
 if(before)try{after=await mainSha(fetcher)}catch(e){errors.push('MAIN_RECHECK_'+String(e.message||e).slice(0,80))}
 const consistent=Boolean(before&&after&&before===after);
 if(before&&!consistent)errors.push('MAIN_CHANGED_OR_INACCESSIBLE_DURING_READBACK');
 const identified=consistent?rows.map(r=>r):rows.map(r=>({...r,status:'UNOBSERVED',freshness:'UNOBSERVED',reason:'MAIN_IDENTITY_INVALIDATED'}));
 const failures=identified.filter(r=>r.status!=='OBSERVED'||r.freshness!=='FRESH_ADVISORY').map(r=>r.id);
 const codex=identified.find(x=>x.id==='codex_ready');
 const handoff=identified.find(x=>x.id==='handoff');
 return {
   schema:'S1_AGENT_OPERATIONS_CONTEXT_v1',mode:'PUBLIC_CANONICAL_METADATA_READ_ONLY',
   observed_at_utc:observedAt,source_repo:REPO,main_sha:consistent?before:null,
   main_preflight_sha:before,main_final_sha:after,
   source_files:identified,source_errors:errors,
   partial:!consistent||failures.length>0,missing_or_stale_sources:failures,
   source_readback_verified:consistent&&identified.length===sources.length&&identified.every(x=>x.status==='OBSERVED'),
   source_freshness_all_advisory_pass:consistent&&failures.length===0,
   existing_owners:{
     S1:{source:'00_FMOS/S1/MISSION.md',role:'ELITE_CLOSURE_EXISTING_ONLY',autonomy_proven:'UNOBSERVED'},
     Strategist:{role:'ORIGINAL_STRATEGIC_OWNER',source:'ORIGINAL_REPO_CONTRACT',advisory_only:true},
     Codex:{role:'ORIGINAL_CODEX_INTAKE',queue_authority:'LATEST_CODEX_READY_TASKS.json',
       ready_count_observed:codex?.summary?.codex_ready_task_count??null,
       code_executed_proven:'UNOBSERVED'},
     Grok:{role:'BRIDGE_ADVISORY_EXISTING_ONLY',source:'PRIVATE_BRIDGE_ORIGINAL',evidence:'UNOBSERVED',formal_approval:false}
   },
   workflow_boundaries:{
     existing_s1_issue:HTTPS+'/issues/1156',s1_max_original_prs_per_tick:3,
     monday_read_only_copenhagen:'09:30-10:30',
     canonical_handoff_count:handoff?.summary?.codex_ready_task_count??null,
     new_scheduler:false,new_identity:false,new_authority:false,
     private_bridge:'UNOBSERVED_UNTIL_ORIGINAL_AUTHENTICATED_REVIEW',
     private_alpha_lab:'UNOBSERVED_UNTIL_ORIGINAL_AUTHENTICATED_REVIEW',
     independent_recovery:'UNOBSERVED',billing_release_permission:'UNOBSERVED'
   },
   consumer_instructions:{
     first:'Verify this exact main SHA and source byte/digest/readback before action.',
     second:'Re-read original PR HEAD, required checks, governance, owner and recovery at action time.',
     third:'Use only existing original owner and authorized route. This packet cannot authorize a merge.',
     forbidden:['AUTO_MERGE_FROM_PROJECTION','SYNTHETIC_S1_AUTONOMY','GROK_FORMAL_APPROVAL','PRIVATE_DATA_PUBLICATION','MODEL_BUDGET_OVERRIDE']
   },
   promotion_status:'ADVISORY_PROJECTION_ONLY',merge_authorized:false,production_verified:false,
   execution_provenance:'INTERACTIVE_OR_ON_DEMAND_READ_ONLY_NOT_SCHEDULED_S1'
 };
}
async function cli(){
 const args=process.argv.slice(2);
 if(args.length&&!(args.length===1&&args[0]==='--stdout')&&!(args.length===2&&args[0]==='--output'&&args[1]))throw Error('Usage: node agent-context-v1.mjs [--stdout | --output FILE]');
 const value=JSON.stringify(await buildAgentContext(),null,2)+'\n';
 if(args[0]==='--output')await writeFile(args[1],value,{encoding:'utf8',flag:'w'});
 else process.stdout.write(value);
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)cli().catch(e=>{console.error('S1_AGENT_CONTEXT_FAIL',e.message);process.exitCode=1});
