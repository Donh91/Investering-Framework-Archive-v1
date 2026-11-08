/* S1 advisory agent-to-agent discovery: local, optional, never a release gate.
 * Private details may be printed ONLY in an already-authorized private runtime.
 */
import {inventory} from './discovery-inventory-v1.mjs';

const SCHEMA='S1_AGENT_WORK_HUB_v1';
const POLICY=Object.freeze({
  authority:'ADVISORY_ONLY',
  can_block_actions:false,
  release_permission:false,
  creates_tasks:false,
  dispatches_agents:false,
  fallback:'CONTINUE_WITH_ORIGINAL_GITHUB_OWNERS',
  privacy:'CALLER_LOCAL_ONLY_NEVER_PUBLIC_HOSTED'
});
function ownerOf(item){
  const assignees=[...new Set((Array.isArray(item?.assignees)?item.assignees:[]).filter(x=>typeof x==='string'&&x.length))];
  return assignees.length===1
   ?{status:'ASSIGNED_ON_GITHUB',logins:assignees,basis:'NATIVE_GITHUB_ASSIGNEE_NOT_DOMAIN_RATIFICATION'}
   :assignees.length>1
    ?{status:'MULTIPLE_GITHUB_ASSIGNEES',logins:assignees,basis:'NATIVE_GITHUB_ASSIGNEES_NO_SINGLE_OWNER'}
    :{status:'OWNER_UNOBSERVED',logins:[],basis:'AUTHOR_AND_TITLE_NOT_OWNER_PROOF'};
}
function laneOf(item){
  if(item?.kind==='CLOSED_ISSUE')return 'CLOSED_RESEARCH_HINT_NOT_ACTIVE';
  if(item?.parked_hint)return 'PARKED_OR_RESEARCH_HINT_CHECK_ORIGINAL';
  if(item?.kind==='PR'&&item.draft===true)return 'OPEN_DRAFT_HINT';
  if(item?.kind==='PR')return 'OPEN_PR_NOT_READY_PROOF';
  if(item?.kind==='ISSUE')return 'OPEN_ISSUE_ACTIVITY_UNVERIFIED';
  return 'UNOBSERVED';
}
function buildHub(input,{includePrivate=false,includeClosedParked=false}={}){
  if(!input||input.schema!=='S1_DISCOVERY_INVENTORY_v1'||!Array.isArray(input.repos)){
    return {...POLICY,schema:SCHEMA,status:'UNAVAILABLE',coverage_complete:false,
      warning:'SOURCE_INVALID_USE_NATIVE_GITHUB',work:[],repo_summary:[]};
  }
  const work=[],repo_summary=[];
  let coverage=Boolean(input.complete&&input.repository_enumeration_complete);
  for(const repo of input.repos){
    if(!repo||typeof repo.repo!=='string'||repo.repo==='Donh91/secrets')continue;
    const isPrivate=repo.visibility==='PRIVATE';
    if(!repo.complete)coverage=false;
    const readable=!isPrivate||includePrivate;
    repo_summary.push({repo:repo.repo,visibility:repo.visibility,
      source_complete:repo.complete===true,
      open_pr_count:Number.isInteger(repo.open_pr_count)?repo.open_pr_count:null,
      open_issue_count:Number.isInteger(repo.open_issue_count)?repo.open_issue_count:null,
      details:readable?'AS_AVAILABLE':'REDACTED'});
    if(!readable||!Array.isArray(repo.items))continue;
    const sourceItems=repo.items.concat(includeClosedParked&&Array.isArray(repo.closed_parked_candidates)?repo.closed_parked_candidates:[]);
    for(const item of sourceItems){
      if(!['PR','ISSUE','CLOSED_ISSUE'].includes(item?.kind))continue;
      if(!Number.isInteger(item.number)||item.number<1)continue;
      work.push({
        source_repo:repo.repo,visibility:repo.visibility,kind:item.kind,number:item.number,
        source_url:item.url||'https://github.com/'+repo.repo+'/'+(item.kind==='PR'?'pull':'issues')+'/'+item.number,
        title:typeof item.title==='string'?item.title:null,
        author_not_owner:item.author||null,
        owner:ownerOf(item),lane_hint:laneOf(item),
        updated_at:item.updated_at||null,
        activity_proof:'LAST_UPDATE_TIME_IS_NOT_WORK_IN_PROGRESS_PROOF',
        raw_labels:Array.isArray(item.labels)?item.labels:[],
        parked_hint:item.parked_hint===true,
        original_source_recheck_required:true,
        authority:'NO_PERMISSION_TO_MERGE_REOPEN_DISPATCH_OR_OVERRIDE'
      });
    }
  }
  work.sort((a,b)=>String(b.updated_at||'').localeCompare(String(a.updated_at||''))||
    a.source_repo.localeCompare(b.source_repo)||a.number-b.number);
  const owners={};
  let unassigned=0,multiple=0,closedResearchHints=0;
  for(const item of work){
    if(item.kind==='CLOSED_ISSUE'){closedResearchHints++;continue;}
    if(item.owner.status==='ASSIGNED_ON_GITHUB'){
      const login=item.owner.logins[0];owners[login]=(owners[login]||0)+1;
    }else if(item.owner.status==='MULTIPLE_GITHUB_ASSIGNEES')multiple++;
    else unassigned++;
  }
  return {...POLICY,schema:SCHEMA,status:coverage?'OBSERVED_COMPLETE_WITHIN_CREDENTIAL_SCOPE':'PARTIAL',
    generated_at:input.generated_at||null,source_inventory_schema:input.schema,
    repository_scope:input.coverage_scope||'UNKNOWN',coverage_complete:coverage,
    source_warnings:Array.isArray(input.warnings)?input.warnings:[],
    repo_summary,counts:{open_work_items_observed:work.length-closedResearchHints,
      closed_research_hints:closedResearchHints,
      owner_unobserved:unassigned,
      multiple_assignees:multiple,by_assignee:owners},
    work,adoption:'UNPROVEN_UNTIL_NATURAL_AGENT_RUN_RECEIPT',
    note:'Hints are not ownership ratification, CI review, merge permission, or a new queue. If unavailable or stale, skip hub and work from original GitHub.'};
}
export {SCHEMA,POLICY,ownerOf,laneOf,buildHub};
if(process.argv[1]&&import.meta.url==='file://'+process.argv[1]){
  const includePrivate=process.argv.includes('--private-details');
  const closed=process.argv.includes('--closed-parked');
  try{
    const result=await inventory({privateDetails:includePrivate,includeClosedParked:closed});
    process.stdout.write(JSON.stringify(buildHub(result,{includePrivate,includeClosedParked:closed}),null,2)+'\n');
  }catch(_error){
    process.stdout.write(JSON.stringify({...POLICY,schema:SCHEMA,status:'UNAVAILABLE',
      coverage_complete:false,warning:'OPTIONAL_HUB_ERROR_CONTINUE_WITH_NATIVE_GITHUB'},null,2)+'\n');
  }
}
