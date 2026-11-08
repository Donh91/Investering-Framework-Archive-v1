/* S1 advisory agent-to-agent discovery: local, optional, never a release gate.
 * Private details may be printed ONLY in an already-authorized private runtime.
 */
import {inventory, REPOS, EXCLUDED} from './discovery-inventory-v1.mjs';
const KNOWN_PRIVATE = new Set(REPOS.filter(([, privateRepo])=>privateRepo).map(([repo])=>repo.toLowerCase()));
const KNOWN_PUBLIC = new Set(REPOS.filter(([, privateRepo])=>!privateRepo).map(([repo])=>repo.toLowerCase()));
const EXCLUDED_NORMALIZED = new Set([...EXCLUDED].map(repo=>repo.toLowerCase()));

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
function safeSourceWarnings(warnings){
  if(!Array.isArray(warnings))return [];
  return warnings.map(value=>{
    if(typeof value!=='string')return 'SOURCE_WARNING_REDACTED';
    if(/^(?:AUTHENTICATED_REPOSITORY_ENUMERATION_UNAVAILABLE|REPOSITORY_PAGINATION_INCOMPLETE|REPOSITORY_VISIBILITY_UNOBSERVED)$/.test(value))return value;
    if(/^REPOSITORY_ENUMERATION_GITHUB_HTTP_\d{3}$/.test(value))return value;
    const match=value.match(/^Donh91\/[a-z0-9._-]+:\s*(OPEN_PAGINATION_INCOMPLETE|CLOSED_RESEARCH_SCAN_INCOMPLETE|UNAVAILABLE_COUNTS_UNKNOWN)$/i);
    return match?'REPO_'+match[1].toUpperCase():'SOURCE_WARNING_REDACTED';
  });
}
function buildHub(input,{includePrivate=false,includeClosedParked=false}={}){
  if(!input||input.schema!=='S1_DISCOVERY_INVENTORY_v1'||!Array.isArray(input.repos)){
    return {...POLICY,schema:SCHEMA,status:'UNAVAILABLE',coverage_complete:false,
      warning:'SOURCE_INVALID_USE_NATIVE_GITHUB',work:[],repo_summary:[]};
  }
  const work=[],repo_summary=[];
  let coverage=Boolean(input.complete&&input.repository_enumeration_complete);
  for(const repo of input.repos){
    if(!repo||typeof repo.repo!=='string'){coverage=false;continue;}
    const normalized=repo.repo.toLowerCase();
    // Never surface restricted data-plane work, even when the source uses mixed case.
    if(EXCLUDED_NORMALIZED.has(normalized))continue;
    if(!/^Donh91\/[a-z0-9._-]+$/i.test(repo.repo)){coverage=false;continue;}
    const knownPrivate=KNOWN_PRIVATE.has(normalized);
    const knownPublic=KNOWN_PUBLIC.has(normalized);
    // Dynamic repositories require explicit native owner-enumeration provenance.
    // A self-declared PUBLIC field alone does not authorize public output.
    const verifiedDynamic=repo.visibility_source==='AUTHENTICATED_OWNER_ENUMERATION'&&
      input.repository_coverage==='AUTHENTICATED_OWNER_ENUMERATION'&&
      input.repository_enumeration_complete===true;
    const visibility=knownPrivate?'PRIVATE':
      repo.visibility==='PUBLIC'||repo.visibility==='PRIVATE'?repo.visibility:'UNKNOWN';
    const visibilityProven=visibility!=='UNKNOWN'&&
      (knownPrivate?repo.visibility==='PRIVATE':knownPublic||verifiedDynamic);
    if(!repo.complete||!visibilityProven)coverage=false;
    const readable=visibilityProven&&(visibility==='PUBLIC'||(visibility==='PRIVATE'&&includePrivate));
    repo_summary.push({repo:readable?repo.repo:null,visibility,
      source_complete:repo.complete===true&&visibilityProven,
      open_pr_count:readable&&Number.isInteger(repo.open_pr_count)?repo.open_pr_count:null,
      open_issue_count:readable&&Number.isInteger(repo.open_issue_count)?repo.open_issue_count:null,
      details:readable?'AS_AVAILABLE':'REDACTED'});
    if(!readable||!Array.isArray(repo.items))continue;
    const sourceItems=repo.items.concat(includeClosedParked&&Array.isArray(repo.closed_parked_candidates)?repo.closed_parked_candidates:[]);
    for(const item of sourceItems){
      if(!['PR','ISSUE','CLOSED_ISSUE'].includes(item?.kind))continue;
      if(!Number.isInteger(item.number)||item.number<1)continue;
      work.push({
        source_repo:repo.repo,visibility,kind:item.kind,number:item.number,
        source_url:'https://github.com/'+repo.repo+'/'+(item.kind==='PR'?'pull':'issues')+'/'+item.number,
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
    generated_at:/^\d{4}-\d{2}-\d{2}T/.test(input.generated_at||'')?input.generated_at:null,
    source_inventory_schema:input.schema,
    repository_scope:input.coverage_scope==='CREDENTIAL_ACCESSIBLE_OWNER_REPOS_ONLY'?
      input.coverage_scope:'UNKNOWN',coverage_complete:coverage,
    source_warnings:safeSourceWarnings(input.warnings),
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
