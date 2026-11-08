/* Read-only S1 discovery. Never a scheduler, private-data proxy or merge authority.
 * An unavailable GitHub scope is UNKNOWN, not an empty queue.
 */
const OWNER = 'Donh91';
const REPOS = Object.freeze([
  ['Donh91/Investering-Framework-Archive-v1', false],
  ['Donh91/Eksperimenter-framework-', false],
  ['Donh91/CycleNavigator-scores', false],
  ['Donh91/Investering-AI-Audit-Bridge', true],
  ['Donh91/Meme-Alpha-Lab', true]
]);
const EXCLUDED = new Set(['Donh91/secrets']);
const MAX_PAGES = 10;
function headers(token) {
  const h = {Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'};
  if (token) h.Authorization = 'Bearer ' + token;
  return h;
}
function redactError(err) {
  return String(err?.message || err).replace(/Bearer\s+\S+/gi,'Bearer [REDACTED]').slice(0,140);
}
async function collect(fetcher, route, token, maxPages=MAX_PAGES) {
  if (!Number.isInteger(maxPages) || maxPages<1 || maxPages>MAX_PAGES) throw Error('UNSAFE_PAGE_LIMIT');
  if (!route.startsWith('https://api.github.com/')) throw Error('UNAUTHORIZED_HOST');
  const items = [];
  for (let page=1;page<=maxPages;page++) {
    const url=route+(route.includes('?')?'&':'?')+'per_page=100&page='+page;
    const response=await fetcher(url,{headers:headers(token)});
    if (!response.ok) throw Error('GITHUB_HTTP_'+response.status);
    const batch=await response.json();
    if (!Array.isArray(batch)) throw Error('NON_ARRAY_GITHUB_RESPONSE');
    items.push(...batch);
    if (batch.length<100) return {items,complete:true};
  }
  return {items,complete:false};
}
function classify(item,kind) {
  const labels=(item.labels||[]).map(x=>x.name||'');
  const parked=/parked|parking|on.hold|backlog|defer|research|shadow|supersed/i.test((item.title||'')+' '+labels.join(' '));
  const rawAssignees=Array.isArray(item.assignees)?item.assignees:(item.assignee?[item.assignee]:[]);
  const assignees=[...new Set(rawAssignees.map(x=>x?.login).filter(x=>typeof x==='string'&&x.length>0))];
  return {kind,number:item.number,title:item.title,url:item.html_url,updated_at:item.updated_at,
    state:item.state||'UNKNOWN',draft:kind==='PR'?Boolean(item.draft):null,
    labels,parked_hint:parked,assignees,
    author:typeof item.user?.login==='string'?item.user.login:null,
    disposition:'UNOBSERVED_NEEDS_ORIGINAL_OWNER_AND_NATIVE_GATES'};
}
async function discoverRepositories({fetcher,token,maxPages=MAX_PAGES}={}) {
  const known=new Map(REPOS.map(([name,privateRepo])=>[name,privateRepo]));
  const result={repos:known,complete:false,source:'KNOWN_SCOPE_ONLY',warning:'AUTHENTICATED_REPOSITORY_ENUMERATION_UNAVAILABLE'};
  if (!token) return result;
  try {
    const x=await collect(fetcher,'https://api.github.com/user/repos?affiliation=owner&visibility=all',token,maxPages);
    let visibilityUnknown=false;
    for (const r of x.items) {
      if (r?.owner?.login !== OWNER || !r.full_name?.startsWith(OWNER+'/')) continue;
      if (EXCLUDED.has(r.full_name) || r.full_name.toLowerCase()==='donh91/secrets') continue;
      // A missing visibility bit cannot silently become PUBLIC.
      if (typeof r.private !== 'boolean'){visibilityUnknown=true;continue;}
      if (known.get(r.full_name)===true && r.private===false)visibilityUnknown=true;
      known.set(r.full_name,r.private||known.get(r.full_name)===true);
    }
    result.complete=x.complete&&!visibilityUnknown;
    result.source='AUTHENTICATED_OWNER_ENUMERATION';
    result.warning=!x.complete?'REPOSITORY_PAGINATION_INCOMPLETE':
      visibilityUnknown?'REPOSITORY_VISIBILITY_UNOBSERVED':null;
  } catch (err) {
    result.warning='REPOSITORY_ENUMERATION_'+redactError(err);
  }
  return result;
}
async function inventory({fetcher=fetch,token=process.env.GITHUB_TOKEN,
  privateDetails=false,includeClosedParked=false,maxPages=MAX_PAGES}={}) {
  if(privateDetails&&!token) throw Error('PRIVATE_DETAILS_REQUIRE_AUTHENTICATION');
  const d=await discoverRepositories({fetcher,token,maxPages});
  const out={schema:'S1_DISCOVERY_INVENTORY_v1',authority:'READ_ONLY_ADVISORY',
    generated_at:new Date().toISOString(),repository_coverage:d.source,
    coverage_scope:'CREDENTIAL_ACCESSIBLE_OWNER_REPOS_ONLY',
    repository_enumeration_complete:d.complete,complete:d.complete,
    release_permission:false,repos:[],warnings:d.warning?[d.warning]:[]};
  for (const [repo,isPrivate] of d.repos) {
    if (EXCLUDED.has(repo)) continue;
    const entry={repo,visibility:isPrivate?'PRIVATE':'PUBLIC',complete:true,
      open_pr_count:null,open_issue_count:null,parked_hint_count:null,items:[]};
    try {
      const base='https://api.github.com/repos/'+repo+'/';
      const [prs,issues]=await Promise.all([
        collect(fetcher,base+'pulls?state=open',token,maxPages),
        collect(fetcher,base+'issues?state=open',token,maxPages)
      ]);
      entry.complete=prs.complete&&issues.complete;
      if(!entry.complete)out.warnings.push(repo+': OPEN_PAGINATION_INCOMPLETE');
      const prItems=prs.items.filter(x=>Number.isInteger(x.number)).map(x=>classify(x,'PR'));
      const issueItems=issues.items.filter(x=>Number.isInteger(x.number)&&!x.pull_request).map(x=>classify(x,'ISSUE'));
      entry.open_pr_count=prItems.length;
      entry.open_issue_count=issueItems.length;
      entry.parked_hint_count=[...prItems,...issueItems].filter(x=>x.parked_hint).length;
      if(!isPrivate||privateDetails)entry.items=[...prItems,...issueItems];
      else entry.private_details='REDACTED_LOCAL_ONLY';
      if(includeClosedParked) {
        const closed=await collect(fetcher,base+'issues?state=closed&sort=updated&direction=desc',token,maxPages);
        const parked=closed.items.filter(x=>Number.isInteger(x.number)&&!x.pull_request)
          .map(x=>classify(x,'CLOSED_ISSUE')).filter(x=>x.parked_hint);
        entry.closed_parked_candidates_count=parked.length;
        entry.closed_parked_scan_complete=closed.complete;
        if(!closed.complete)out.warnings.push(repo+': CLOSED_RESEARCH_SCAN_INCOMPLETE');
        if(!isPrivate||privateDetails)entry.closed_parked_candidates=parked;
        else entry.closed_parked_candidates='REDACTED_LOCAL_ONLY';
        if(!closed.complete)entry.complete=false;
      }
    }catch(err) {
      entry.complete=false;
      entry.error=redactError(err);
      out.warnings.push(repo+': UNAVAILABLE_COUNTS_UNKNOWN');
      // A partial PR read must never become a verified count if issue scan fails.
      entry.open_pr_count=null;entry.open_issue_count=null;entry.parked_hint_count=null;
      entry.items=[];
    }
    if(!entry.complete)out.complete=false;
    out.repos.push(entry);
  }
  out.warning='OPEN or parked does not imply READY. Closed parked candidates are hints, never auto-reopened. No public private content, new tasks, approvals, merges or schedules are authorized.';
  return out;
}
export {OWNER,REPOS,EXCLUDED,MAX_PAGES,collect,discoverRepositories,inventory,classify};
if (process.argv[1] && import.meta.url === 'file://' + process.argv[1]) {
  const privateDetails=process.argv.includes('--private-details');
  const includeClosedParked=process.argv.includes('--closed-parked');
  inventory({privateDetails,includeClosedParked}).then(x=>process.stdout.write(JSON.stringify(x,null,2)+'\n'))
    .catch(e=>{console.error('DISCOVERY_FAILED',redactError(e));process.exitCode=1;});
}
