/* S1 Release Control: on-demand, read-only inventory. Not a scheduler or release authority.
 * Private details stay in the authenticated caller's local stdout, never a public artifact.
 */
const REPOS = Object.freeze([
  ['Donh91/Investering-Framework-Archive-v1',false],
  ['Donh91/Eksperimenter-framework-',false],
  ['Donh91/CycleNavigator-scores',false],
  ['Donh91/Investering-AI-Audit-Bridge',true],
  ['Donh91/Meme-Alpha-Lab',true]
]);
const LIMIT=10;
function classify(item,kind){
  const labels=(item.labels||[]).map(x=>x.name||'');
  const text=(item.title||'')+' '+labels.join(' ');
  const parked=/parked|parking|on.hold|backlog|defer|research|shadow/i.test(text);
  return {kind,number:item.number,title:item.title,url:item.html_url,updated_at:item.updated_at,
    draft:kind==='PR'?Boolean(item.draft):null,labels,parked_hint:parked,
    disposition:'UNOBSERVED_NEEDS_ORIGINAL_OWNER_AND_NATIVE_GATES'};
}
async function inventory({fetcher=fetch,token=process.env.GITHUB_TOKEN,privateDetails=false}={}){
  const out={schema:'S1_DISCOVERY_INVENTORY_v1',authority:'READ_ONLY_ADVISORY',
    generated_at:new Date().toISOString(),complete:true,release_permission:false,
    repos:[],warnings:[]};
  for(const [repo,isPrivate] of REPOS){
    const entry={repo,visibility:isPrivate?'PRIVATE':'PUBLIC',complete:true,
      open_pr_count:null,open_issue_count:null,parked_hint_count:null,items:[]};
    try{
      const results={};
      for(const [kind,path] of [['PR','pulls?state=open'],['ISSUE','issues?state=open']]){
        const items=[];
        let exhausted=false;
        for(let page=1;page<=LIMIT;page++){
          const url='https://api.github.com/repos/'+repo+'/'+path+'&per_page=100&page='+page;
          const headers={Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'};
          if(token)headers.Authorization='Bearer '+token;
          const response=await fetcher(url,{headers});
          if(!response.ok)throw Error('GITHUB_HTTP_'+response.status+'_'+kind);
          const batch=await response.json();
          if(!Array.isArray(batch))throw Error('INVALID_'+kind+'_RESPONSE');
          items.push(...batch);
          if(batch.length<100){exhausted=true;break;}
        }
        if(!exhausted){entry.complete=false;out.complete=false;out.warnings.push(repo+': '+kind+' pagination cap');}
        results[kind]=items;
      }
      const prs=results.PR.map(x=>classify(x,'PR'));
      const issues=results.ISSUE.filter(x=>!x.pull_request).map(x=>classify(x,'ISSUE'));
      entry.open_pr_count=prs.length;entry.open_issue_count=issues.length;
      entry.parked_hint_count=[...prs,...issues].filter(x=>x.parked_hint).length;
      if(!isPrivate||privateDetails)entry.items=[...prs,...issues];
      else entry.private_details='REDACTED_LOCAL_ONLY';
    }catch(err){
      entry.complete=false;out.complete=false;
      entry.error=String(err.message||err).replace(/Bearer\s+\S+/gi,'Bearer [REDACTED]');
      out.warnings.push(repo+': unavailable, counts UNKNOWN');
    }
    out.repos.push(entry);
  }
  out.warning='OPEN is not READY. Parked hints are discovery-only. Closed historical research requires original-owner ledger inspection. Never publish private inventory or use this output as merge consent.';
  return out;
}
export {REPOS,inventory,classify};
if(process.argv[1]&&import.meta.url==='file://'+process.argv[1]){
  const privateDetails=process.argv.includes('--private-details');
  inventory({privateDetails}).then(x=>process.stdout.write(JSON.stringify(x,null,2)+'\n'))
    .catch(e=>{console.error('DISCOVERY_FAILED',String(e.message));process.exitCode=1;});
}
