/* S1 Release Control read-only versioned machine projection.
 * Node 22+, public GitHub GET, no scheduler, credential, action or release authority.
 */
import core from './release-core.js';
import { writeFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
const PUBLIC = Object.freeze([
  'Donh91/Investering-Framework-Archive-v1',
  'Donh91/Eksperimenter-framework-',
  'Donh91/CycleNavigator-scores'
]);
const API = 'https://api.github.com/repos/';
const SHA40 = /^[a-f\d]{40}$/i;
const safeUrl = repo => /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(repo) && PUBLIC.includes(repo);
async function getJson(fetcher, repo, route){
  if(!safeUrl(repo) || !route.startsWith('/'))throw Error('UNAUTHORIZED_PUBLIC_SOURCE');
  const response = await fetcher(API + repo + route, {headers:{Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'}});
  if(!response.ok)throw Error('GITHUB_HTTP_'+response.status);
  return response.json();
}
function mapPR(repo,p){
  return {repo,number:p.number,title:String(p.title||''),author:p.user?.login||null,state:p.state||'unknown',merged:!!p.merged_at,merge_commit_sha:p.merge_commit_sha||null,draft:!!p.draft,head:p.head?.sha||'',base:p.base?.sha||'',updated:p.updated_at||null,labels:(p.labels||[]).map(x=>x.name),filesObserved:false,runObserved:false,reviewsObserved:false,files:[],runs:[],reviews:[],changedFiles:p.changed_files,seed:false};
}
async function observePR(fetcher,p){
  const req=[
    getJson(fetcher,p.repo,'/pulls/'+p.number),
    getJson(fetcher,p.repo,'/pulls/'+p.number+'/files?per_page=100'),
    getJson(fetcher,p.repo,'/pulls/'+p.number+'/reviews?per_page=100'),
    getJson(fetcher,p.repo,'/actions/runs?head_sha='+encodeURIComponent(p.head)+'&per_page=100')
  ];
  const r=await Promise.allSettled(req);
  const errors=[];
  for(let i=0;i<r.length;i++)if(r[i].status==='rejected')errors.push('SOURCE_'+['PR','FILES','REVIEWS','RUNS'][i]+'_'+String(r[i].reason.message||r[i].reason).slice(0,80));
  if(r[0].status==='fulfilled'){
    const q=r[0].value;
    if(q.head?.sha!==p.head)errors.push('HEAD_CHANGED_DURING_READBACK');
    else{p.changedFiles=q.changed_files;p.base=q.base?.sha||p.base;p.draft=!!q.draft;p.state=q.state;p.merged=!!q.merged_at;p.merge_commit_sha=q.merge_commit_sha;}
  }
  if(r[1].status==='fulfilled'&&Array.isArray(r[1].value)){
    p.files=r[1].value;
    p.filesObserved=p.files.length<100 && Number.isInteger(p.changedFiles) && p.files.length===p.changedFiles;
    if(!p.filesObserved)errors.push('CHANGED_FILES_PAGINATION_OR_COUNT_INCOMPLETE');
  }
  if(r[2].status==='fulfilled'&&Array.isArray(r[2].value)){
    p.reviews=r[2].value;
    p.reviewsObserved=p.reviews.length<100;
    if(!p.reviewsObserved)errors.push('REVIEWS_PAGINATION_INCOMPLETE');
  }
  if(r[3].status==='fulfilled'&&Array.isArray(r[3].value?.workflow_runs)){
    const runs=r[3].value.workflow_runs;
    p.runObserved=runs.length<100;
    p.runs=runs.filter(x=>x.head_sha===p.head).map(x=>({id:x.id,name:x.name,head_sha:x.head_sha,status:x.status,conclusion:x.conclusion,event:x.event,pr_numbers:(x.pull_requests||[]).map(pr=>pr.number)}));
    if(!p.runObserved)errors.push('WORKFLOW_RUNS_PAGINATION_INCOMPLETE');
  }
  p.risk=core.risk(p);
  if(errors.includes('HEAD_CHANGED_DURING_READBACK')){p.head='';p.risk='UNKNOWN';p.runObserved=false;p.reviewsObserved=false;}
  return {pr:p,errors};
}
async function readRepository(fetcher,repo,limit){
  const [branch,pulls] = await Promise.allSettled([
    getJson(fetcher,repo,'/branches/main'),
    getJson(fetcher,repo,'/pulls?state=open&sort=updated&direction=desc&per_page=100')
  ]);
  const issues=[];
  const main=branch.status==='fulfilled'?branch.value?.commit?.sha:null;
  if(!SHA40.test(main||''))issues.push('MAIN_SHA_UNOBSERVED');
  if(pulls.status!=='fulfilled'||!Array.isArray(pulls.value))issues.push('PR_LIST_UNAVAILABLE');
  const list=pulls.status==='fulfilled'&&Array.isArray(pulls.value)?pulls.value:[];
  if(list.length===100)issues.push('PR_PAGINATION_INCOMPLETE');
  if(list.length>limit)issues.push('PR_DISCOVERY_SAMPLED_NOT_COMPLETE');
  const raw=list.filter(p=>p&&Number.isInteger(p.number)&&SHA40.test(p.head?.sha||'')).slice(0,limit).map(p=>mapPR(repo,p));
  const detail=await Promise.all(raw.map(p=>observePR(fetcher,p)));
  const end=await Promise.allSettled([getJson(fetcher,repo,'/branches/main')]);
  const main2=end[0].status==='fulfilled'?end[0].value?.commit?.sha:null;
  if(main&&main2&&main!==main2)issues.push('MAIN_CHANGED_DURING_READBACK');
  if(!SHA40.test(main2||''))issues.push('FINAL_MAIN_UNOBSERVED');
  return {repo,main_sha:main2===main?main:null,
    observed:!issues.some(x=>x!=='PR_DISCOVERY_SAMPLED_NOT_COMPLETE'),
    discovery_complete:!issues.length,source_issues:issues,
    prs:detail.map(x=>({pr:x.pr,errors:x.errors}))};
}
export async function buildProjection({fetcher=fetch, clock=()=>new Date().toISOString(), repositories=PUBLIC, maxPerRepo=3}={}){
  if(!Array.isArray(repositories)||repositories.some(r=>!safeUrl(r)))throw Error('REPOSITORY_NOT_IN_PUBLIC_ALLOWLIST');
  if(!Number.isInteger(maxPerRepo)||maxPerRepo<1||maxPerRepo>15)throw Error('BOUNDED_LIMIT_REQUIRED');
  const observedAt=clock();
  const all=await Promise.allSettled(repositories.map(r=>readRepository(fetcher,r,maxPerRepo)));
  const sources=[];
  const items=[];
  for(let i=0;i<repositories.length;i++){
    const entry=all[i].status==='fulfilled'?all[i].value:{repo:repositories[i],main_sha:null,observed:false,source_issues:['REPOSITORY_READ_FAILED']};
    sources.push({repo:entry.repo,main_sha:entry.main_sha||null,observed:entry.observed,
      discovery_complete:entry.discovery_complete===true,source_issues:entry.source_issues});
    for(const row of entry.prs||[]){
      let p=row.pr;
      if(!entry.observed){p.risk='UNKNOWN';p.runObserved=false;p.reviewsObserved=false;}
      const out=core.project(p,entry.main_sha,observedAt);
      out.source_issues=[...entry.source_issues,...row.errors];
      if(row.errors.length){
        out.evidence_class='UNOBSERVED';
        out.release_disposition=p.draft||p.risk==='HIGH'?'HOLD':'UNOBSERVED';
      }
      items.push(out);
    }
  }
  return {schema:core.schema,mode:'READ_ONLY_PUBLIC_GITHUB',generated_at:clock(),observed_at:observedAt,
    source_repositories:sources,partial:sources.some(x=>!x.observed||!x.discovery_complete)||items.some(x=>x.source_issues.length>0),
    items,queue_plan:items.filter(x=>x.release_disposition!=='MERGED'&&x.release_disposition!=='CLOSED').slice(0,8).map(x=>({repo:x.repo,pr_number:x.pr_number,head_sha:x.head_sha,next_action:x.next_action})),
    queue_capacity:8,existing_s1_action_limit:3,source_authority:false,release_authority:false,
    formal_approval:false,unattended_s1_closure_proven:false,
    private_sources:{bridge:'UNOBSERVED',alpha_lab:'UNOBSERVED',vault:'UNOBSERVED'},
    prohibitions:['NO_WRITE_OR_MERGE','NO_TRADING','NO_MODEL_SPEND','NO_PRIVATE_DATA','NO_SCHEDULED_SUPERVISOR'],
    provenance_note:'Every item is a current public readback; absence of a required gate never means PASS. This projection is not a merge authorization.'};
}
async function main(){
  const args=process.argv.slice(2);
  if(args.length>2||args.some(a=>a!=='--stdout'&&a!=='--output')&&(args[0]!=='--output'||args.length!==2))throw Error('Usage: node projection-v1.mjs [--stdout | --output FILE]');
  const result=await buildProjection();
  const json=JSON.stringify(result,null,2)+'\n';
  if(args[0]==='--output'&&args[1])await writeFile(args[1],json,{encoding:'utf8',flag:'w'});
  else process.stdout.write(json);
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)main().catch(err=>{console.error('S1_PROJECTION_FAILED:',err.message);process.exitCode=1;});
