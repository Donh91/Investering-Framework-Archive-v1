/** Read-only pre-deploy Pages artifact identity/visibility guard.
 * REST visibility is a mitigation, not proof that deploy-pages' separate
 * Actions results service is ready. No deployment retry or success claim.
 */
import {pathToFileURL} from 'node:url';
const NAME='github-pages', MAX_ATTEMPTS=6, SETTLE_MS=5000;
const positive=x=>typeof x==='string'&&/^[1-9][0-9]{0,15}$/.test(x)&&Number.isSafeInteger(Number(x));
const sha=x=>typeof x==='string'&&/^[a-f0-9]{40}$/.test(x);
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));
export function pagesArtifactConfig(env){
 const repo=env.GITHUB_REPOSITORY,run=env.GITHUB_RUN_ID,attempt=env.GITHUB_RUN_ATTEMPT,id=env.PAGES_ARTIFACT_ID,head=env.GITHUB_SHA;
 if(typeof repo!=='string'||!/^[-A-Za-z0-9_.]+\/[-A-Za-z0-9_.]+$/.test(repo)||repo.split('/').some(x=>x==='.'||x==='..')||
    env.GITHUB_REF!=='refs/heads/main'||![run,attempt,id].every(positive)||!sha(head)||
    typeof env.GH_TOKEN!=='string'||!env.GH_TOKEN.trim())throw Error('CN_PAGES_ARTIFACT_CONFIG_INVALID');
 return {repo,run:Number(run),attempt:Number(attempt),id:Number(id),head,token:env.GH_TOKEN};
}
export function inspectArtifactList(body,c){
 if(!body||!Number.isSafeInteger(body.total_count)||body.total_count<0||!Array.isArray(body.artifacts))
  throw Error('CN_PAGES_ARTIFACT_LIST_INVALID');
 if(body.total_count>1||body.artifacts.length>1)throw Error('CN_PAGES_ARTIFACT_DUPLICATE');
 if(body.total_count!==body.artifacts.length)throw Error('CN_PAGES_ARTIFACT_LIST_INCONSISTENT');
 if(!body.total_count)return null;
 const a=body.artifacts[0];
 if(a?.name!==NAME||a.id!==c.id||a.workflow_run?.id!==c.run||a.workflow_run?.head_sha!==c.head||
    a.workflow_run?.head_branch!=='main'||a.expired!==false||!Number.isSafeInteger(a.size_in_bytes)||a.size_in_bytes<=0)
  throw Error('CN_PAGES_ARTIFACT_IDENTITY_MISMATCH');
 return {id:a.id,run:c.run,attempt:c.attempt,head:c.head,size:a.size_in_bytes};
}
export async function waitPagesArtifact(c,{fetchImpl=fetch,sleep=pause}={}){
 const url='https://api.github.com/repos/'+c.repo.split('/').map(encodeURIComponent).join('/')+'/actions/runs/'+c.run+'/artifacts?name=github-pages&per_page=2';
 for(let i=0;i<MAX_ATTEMPTS;i++){
  let response=null;
  try{
   response=await fetchImpl(url,{headers:{Accept:'application/vnd.github+json',Authorization:'Bearer '+c.token,'X-GitHub-Api-Version':'2022-11-28'},redirect:'error',signal:AbortSignal.timeout(5000)});
  }catch{ /* bounded retry for network/timeout; no token or response logged */ }
  if(response){
   if(response.status===200){
    let body;try{const raw=await response.text();if(raw.length>65536)throw Error('oversize');body=JSON.parse(raw)}
    catch{throw Error('CN_PAGES_ARTIFACT_LIST_INVALID')}
    const a=inspectArtifactList(body,c);
    if(a){
     // Small bounded propagation buffer for the distinct results service.
     await sleep(SETTLE_MS);
     return {...a,polls:i+1,status:'REST_VISIBLE_NOT_DEPLOYED'};
    }
   }else if(![429,500,502,503,504].includes(response.status)){
    throw Error('CN_PAGES_ARTIFACT_HTTP_'+response.status);
   }
  }
  if(i+1<MAX_ATTEMPTS)await sleep(Math.min(8000,2000*(i+1)));
 }
 throw Error('CN_PAGES_ARTIFACT_VISIBILITY_TIMEOUT');
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
 try{const c=pagesArtifactConfig(process.env);console.log('CN_PAGES_ARTIFACT_READBACK '+JSON.stringify(await waitPagesArtifact(c)))}
 catch(e){console.error(e.message);process.exitCode=1}
}
