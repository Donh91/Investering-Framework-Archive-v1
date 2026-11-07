/* S1 Agent Operations Brief v1.
 * Read-only on-demand condensation of existing source-derived projections.
 * Does not own a queue, grant permission, schedule jobs, or record S1 outcomes.
 */
import {writeFile} from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
import {buildAgentContext} from './agent-context-v1.mjs';
import {buildProjection} from './projection-v1.mjs';

const MAIN_REPO='Donh91/Investering-Framework-Archive-v1';
const SHA40=/^[a-f0-9]{40}$/i;
const SCOPED_SOURCES=['operations','handoff','codex_ready','remediation'];
function string(x,max=200){return typeof x==='string'?x.slice(0,max):null;}
function source(context,id){return context.source_files?.find(s=>s.id===id)||null;}
function admittedSource(context,id){const s=source(context,id);
 return s?.status==='OBSERVED'&&s.freshness==='FRESH_ADVISORY'&&s.main_sha===context.main_sha?s:null;
}
function mapRequiredAction(a,s){return {
 kind:'CANONICAL_SYSTEM_ACTION_HINT',priority:string(a.priority,24),system:string(a.system,80),
 reason:string(a.reason,130),owner:s.owner,
 original_source_ref:s.source_url,observed_at_utc:s.observed_at_utc,
 allowed_next:'ORIGINAL_OWNER_READBACK_AND_TRIAGE',release_permission:false
};}
function mapCodexTask(t,s){return {
 kind:'EXISTING_CODEX_READY_HINT',candidate_id:string(t.id,150),
 original_signature:string(t.original_signature,80),finding:string(t.finding,250),
 risk_class:string(t.risk_class,75),
 original_owner:'EXISTING_CODEX_INTAKE',
 original_source_ref:t.source_url||s.source_url,
 observed_at_utc:s.observed_at_utc,route:'ORIGINAL_CODEX_INTAKE_ONLY',
 code_executed_proven:false,release_permission:false
};}
function mapPr(p, aligned,complete){
 const gates=p.required_gates||{};
 const reasons=Object.entries(gates).filter(([,value])=>value!=='PROVEN')
   .map(([name,value])=>({gate:name,status:string(value,60)||'UNOBSERVED'}));
 return {
  kind:'EXISTING_ORIGINAL_PR',repo:string(p.repo,110),pr_number:p.pr_number,
  head_sha:SHA40.test(p.head_sha||'')?p.head_sha:null,
  main_sha:SHA40.test(p.main_sha||'')?p.main_sha:null,
  original_source_ref:p.source_ref,
  source_observed_at:p.observed_at,
  next_action:p.next_action||{code:'RECHECK',label:'Re-read original authoritative source'},
  provisional_disposition:string(p.release_disposition,32)||'UNOBSERVED',
  original_owner:string(p.owner,100),
  risk:string(p.risk,25)||'UNKNOWN',
  required_gate_gaps:reasons,
  source_alignment:aligned?'MATCHED_WITH_CANONICAL_MAIN':'UNOBSERVED',
  discovery_complete:complete,
  pr_dependencies_verified:false,
  eligible_for_merge_from_brief:false,
  natural_S1_execution_proven:false
 };
}
export function composeBrief(context,projection,observedAt){
 if(context?.schema!=='S1_AGENT_OPERATIONS_CONTEXT_v1'||projection?.schema!=='S1_RELEASE_PROJECTION_v1')
  throw Error('ORIGINAL_PROJECTION_CONTRACT_MISMATCH');
 if(context.merge_authorized!==false||projection.release_authority!==false||
    context.production_verified!==false||projection.unattended_s1_closure_proven!==false)
  throw Error('UNTRUSTED_SOURCE_AUTHORITY_CLAIM');
 const repo=projection.source_repositories?.find(s=>s.repo===MAIN_REPO);
 const alignment=SHA40.test(context.main_sha||'')&&repo&&repo.main_sha===context.main_sha&&repo.observed===true;
 const verifiedBase=Boolean(alignment&&!context.partial);
 const safe=verifiedBase&&!projection.partial;
 const sampleOnly=verifiedBase&&projection.partial&&
   Array.isArray(repo?.source_issues)&&repo.source_issues.length>0&&
   repo.source_issues.every(x=>x==='PR_DISCOVERY_SAMPLED_NOT_COMPLETE')&&
   Array.isArray(projection.items)&&projection.items.length>0&&projection.items.every(x=>
     Array.isArray(x.source_issues)&&x.source_issues.every(y=>y==='PR_DISCOVERY_SAMPLED_NOT_COMPLETE'));
 const classification=safe?'OBSERVED_ADVISORY':sampleOnly?'OBSERVED_ADVISORY_SAMPLED':'PARTIAL_OR_STALE_RECHECK';
 const op=admittedSource(context,'operations');
 const codex=admittedSource(context,'codex_ready');
 const normalized=Array.isArray(projection.items)?projection.items.filter(p=>p.repo===MAIN_REPO&&Number.isSafeInteger(p.pr_number)&&p.pr_number>0):[];
 const ranked=normalized.slice().sort((a,b)=>{
  const priority=v=>v.release_disposition==='BLOCKED'?5:v.risk==='HIGH'?4:v.release_disposition==='HOLD'?3:2;
  return priority(b)-priority(a)||a.pr_number-b.pr_number;
 });
 const originalActions=op?.summary?.original_required_actions?.slice(0,8).map(a=>mapRequiredAction(a,op))||[];
 const codexTasks=codex?.summary?.task_refs?.slice(0,8).map(t=>mapCodexTask(t,codex))||[];
 const selected=ranked.filter(p=>SHA40.test(p.head_sha||'')).slice(0,8)
   .map(p=>mapPr(p,Boolean(alignment),repo?.discovery_complete===true));
 return {
  schema:'S1_AGENT_OPERATIONS_BRIEF_v1',
  mode:'PUBLIC_READ_ONLY_ORIGINAL_SOURCE_TRIAGE',
  observed_at_utc:observedAt,
  archive_main_sha:alignment?context.main_sha:null,
  original_context_main_sha:context.main_sha||null,
  original_pr_main_sha:repo?.main_sha||null,
  source_alignment:alignment?'MATCHED':'UNOBSERVED',
  state:classification,
  source_scope:sampleOnly?'VERIFIED_PUBLIC_PR_SAMPLE_NOT_EXHAUSTIVE':safe?'SOURCE_SET_OBSERVED':'PARTIAL_OR_UNVERIFIED',
  source_coverage:{canonical_sources:context.source_files?.map(s=>({
    id:s.id,status:s.status,freshness:s.freshness,
    source_ref:s.source_url,source_path:s.source_path,
    main_sha:s.main_sha||null,blob_sha:s.blob_sha||null,
    sha256:s.sha256||null,bytes:Number.isSafeInteger(s.bytes)&&s.bytes>0?s.bytes:null,
    generated_at_utc:s.generated_at_utc||null,observed_at_utc:s.observed_at_utc||null
  }))||[],
    public_github_repository:repo||null,
    private_bridge:'UNOBSERVED',private_alpha_lab:'UNOBSERVED',independent_recovery:'UNOBSERVED'},
  original_actions:originalActions,
  original_codex_ready_hints:codexTasks,
  public_pr_triage:selected,
  queue_slots_visible:8,existing_s1_action_limit:3,
  permitted_next:'VALIDATE_ORIGINAL_SOURCE_AND_ROUTE_TO_EXISTING_OWNER',
  permitted_readonly_parallel_research:true,
  parallel_original_PR_independence_proven:false,
  existing_actors:{
   S1:{source:'00_FMOS/S1/MISSION.md',role:'ORIGINAL_SCHEDULED_SUPERVISOR',natural_closure_proven:'UNOBSERVED'},
   Strategist:{role:'ORIGINAL_STRATEGIC_RESEARCH',can_advise:true},
   Codex:{role:'ORIGINAL_QUALIFIED_ENGINEERING_INTAKE',may_use_original_ready_authority_only:true},
   Grok:{role:'EXISTING_PRIVATE_BRIDGE_ADVISOR',formal_approval_proven:false}
  },
  invariant:{no_new_scheduler:true,no_new_canonical_queue:true,no_new_identity:true,release_permission:false,
   no_real_trading:true,no_model_spend:true,no_private_source_publication:true,
   action_cap_per_existing_s1_tick:3,monday_0930_1030_copenhagen_read_only:true,
   interactive_work_is_natural_S1_completion:false},
  handoff:'Read all source refs on actual original SHA at action time. This brief cannot approve, merge, close, schedule, attest external custody or prove autonomous execution.'
 };
}
export async function buildAgentBrief({fetcher=fetch,clock=()=>new Date().toISOString(),
  sources=SCOPED_SOURCES,maxPerRepo=3}={}){
 const [context,projection]=await Promise.all([
   buildAgentContext({fetcher,clock,sources}),
   buildProjection({fetcher,clock,repositories:[MAIN_REPO],maxPerRepo})
 ]);
 return composeBrief(context,projection,clock());
}

/* Partial source diagnostic for existing agents, NOT an alternative queue.
 * A stale handoff with a fresh Codex original may expose bounded read-only
 * source pointers; it never admits the full brief or grants S1 action.
 */
const DIAGNOSTIC_ORIGINAL_PATHS=Object.freeze({
  operations:'LATEST_OPERATIONS_DASHBOARD.json',
  handoff:'LATEST_HANDOFF.json',
  codex_ready:'LATEST_CODEX_READY_TASKS.json',
  remediation:'LATEST_REMEDIATION_QUEUE.json'
});
export function buildReadbackStatus(brief,candidateHead,{admitted=false}={}){
 if(!SHA40.test(candidateHead||''))throw Error('CANDIDATE_HEAD_REQUIRED');
 if(!brief||brief.schema!=='S1_AGENT_OPERATIONS_BRIEF_v1'||admitted!==Boolean(admitted))
   throw Error('INVALID_ORIGINAL_BRIEF_DIAGNOSTIC');
 const main=brief.source_alignment==='MATCHED'&&SHA40.test(brief.archive_main_sha||'')
   ?brief.archive_main_sha:null;
 const prefix=main?'https://github.com/'+MAIN_REPO+'/blob/'+main+'/':null;
 const rows=(Array.isArray(brief.source_coverage?.canonical_sources)
   ?brief.source_coverage.canonical_sources:[]).slice(0,4).map(s=>{
   const expected=DIAGNOSTIC_ORIGINAL_PATHS[s?.id];
   const identity=Boolean(main&&expected&&s.source_path===expected&&
     s.source_ref===prefix+expected&&s.main_sha===main&&SHA40.test(s.blob_sha||'')&&
     /^[a-f0-9]{64}$/i.test(s.sha256||'')&&
     Number.isSafeInteger(s.bytes)&&s.bytes>0&&
     s.status==='OBSERVED'&&
     ['FRESH_ADVISORY','STALE'].includes(s.freshness));
   return {
     id:expected?s.id:'UNRECOGNIZED',
     status:identity?'OBSERVED':'UNOBSERVED',
     freshness:identity?s.freshness:'UNOBSERVED',
     original_source_ref:identity?s.source_ref:null,
     source_main_sha:identity?main:null,
     source_blob_sha:identity?s.blob_sha:null,
     source_sha256:identity?s.sha256:null,
     source_bytes:identity?s.bytes:null,
     identity_verified_in_source_context:identity,
     action_permission:false
   };
 });
 const codex=rows.find(x=>x.id==='codex_ready'&&x.identity_verified_in_source_context&&x.freshness==='FRESH_ADVISORY');
 const raw=Array.isArray(brief.original_codex_ready_hints)?brief.original_codex_ready_hints:[];
 const candidates=main&&codex?raw.slice(0,8).filter(h=>
   h?.kind==='EXISTING_CODEX_READY_HINT'&&h.original_owner==='EXISTING_CODEX_INTAKE'&&
   h.code_executed_proven===false&&h.release_permission===false&&
   typeof h.candidate_id==='string'&&/^[a-z0-9._:-]{1,150}$/i.test(h.candidate_id)&&
   typeof h.original_source_ref==='string'&&
   h.original_source_ref.startsWith(prefix+'research/codex/intake/')&&
   !h.original_source_ref.includes('..')
 ).map(h=>({
   candidate_id:h.candidate_id,original_source_ref:h.original_source_ref,
   original_queue_source_ref:codex.original_source_ref,
   source_main_sha:main,source_ledger_blob_sha:codex.source_blob_sha,
   source_ledger_sha256:codex.source_sha256,
   pointer_only:true,candidate_file_revalidated:false,
   original_intake_recheck_required:true,code_execution_proven:false,
   action_permission:false,merge_authorized:false
 })):[];
 return {
   contract:'S1_AGENT_BRIEF_ADMISSION_STATUS_v1',candidate_pr_head_sha:candidateHead,
   observed_at_utc:brief.observed_at_utc||null,original_main_sha:main,
   status:admitted?'ADMITTED_SOURCE_IDENTITIES_ONLY':'WITHHELD_RECHECK_ORIGINAL_SOURCE',
   source_statuses:rows,source_issues:Array.isArray(brief.source_coverage?.public_github_repository?.source_issues)
     ?brief.source_coverage.public_github_repository.source_issues.slice(0,8).filter(x=>typeof x==='string').map(x=>x.slice(0,100)):[],
   original_codex_ready_hint_count:admitted?raw.length:null,
   read_only_original_codex_candidate_pointers:candidates,
   partial_research_possible:candidates.length>0,
   full_brief_admitted:admitted,requires_live_original_source_recheck:true,
   source_decision_age_policy_unchanged:true,
   source_refresh_cadence_verified_in_this_packet:false,
   merge_authorized:false,eligible_for_original_action:false,
   natural_s1_execution_proven:false,independent_recovery_verified:false,
   private_bridge:'UNOBSERVED',production_verified:false
 };
}

async function cli(){
 const args=process.argv.slice(2);
 if(args.length && !(args.length===1&&args[0]==='--stdout') &&
    !(args.length===2&&args[0]==='--output'&&args[1]))throw Error('Usage: node agent-brief-v1.mjs [--stdout | --output FILE]');
 const content=JSON.stringify(await buildAgentBrief(),null,2)+'\n';
 if(args[0]==='--output')await writeFile(args[1],content,{encoding:'utf8',flag:'w'});
 else process.stdout.write(content);
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)cli().catch(e=>{console.error('S1_AGENT_BRIEF_FAILED',e.message);process.exitCode=1});
