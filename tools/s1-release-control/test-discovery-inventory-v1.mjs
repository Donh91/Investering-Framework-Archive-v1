import test from 'node:test';
import assert from 'node:assert/strict';
import {inventory,classify,REPOS,collect,discoverRepositories} from './discovery-inventory-v1.mjs';
const repoPayload=[
  {full_name:'Donh91/Investering-Framework-Archive-v1',private:false,owner:{login:'Donh91'}},
  {full_name:'Donh91/Investering-AI-Audit-Bridge',private:true,owner:{login:'Donh91'}},
  {full_name:'Donh91/New-Public-Repo',private:false,owner:{login:'Donh91'}},
  {full_name:'Donh91/secrets',private:true,owner:{login:'Donh91'}},
  {full_name:'Other/unrelated',private:false,owner:{login:'Other'}}
];
function fixture(url,{headers}={}){
  assert.match(url,/^https:\/\/api\.github\.com\//);
  if(url.includes('/user/repos')){assert.equal(headers.Authorization,'Bearer test-token');return Promise.resolve({ok:true,json:async()=>repoPayload});}
  if(url.includes('/pulls?'))return Promise.resolve({ok:true,json:async()=>[{number:7,title:'sensitive private PR',html_url:'https://github.com/x/y/pull/7'}]});
  if(url.includes('state=closed'))return Promise.resolve({ok:true,json:async()=>[{number:19,title:'PARKED research',state:'closed'},{number:20,title:'other'}]});
  return Promise.resolve({ok:true,json:async()=>[{number:8,title:'research parked',html_url:'https://github.com/x/y/issues/8'},{number:7,pull_request:{url:'x'}}]});
}
test('authenticated discover covers new owner repos but never secrets or foreign',async()=>{
 const r=await discoverRepositories({fetcher:fixture,token:'test-token'});
 assert.equal(r.complete,true);
 assert.equal(r.source,'AUTHENTICATED_OWNER_ENUMERATION');
 assert.equal(r.repos.get('Donh91/New-Public-Repo'),false);
 assert.equal(r.repos.has('Donh91/secrets'),false);
 assert.equal(r.repos.has('Other/unrelated'),false);
});
test('private source data redacted by default; no release authority',async()=>{
 const x=await inventory({fetcher:fixture,token:'test-token'});
 assert.equal(x.complete,true);
 assert.equal(x.repository_enumeration_complete,true);
 assert.equal(x.repos.length,REPOS.length+1);
 assert.equal(x.repos[3].open_pr_count,1);
 assert.equal(x.repos[3].open_issue_count,1);
 assert.deepEqual(x.repos[3].items,[]);
 assert.equal(x.repos[3].private_details,'REDACTED_LOCAL_ONLY');
 assert.equal(x.repos[0].items.length,2);
 assert.equal(x.repos.some(r=>r.repo==='Donh91/secrets'),false);
 assert.equal(x.release_permission,false);
});
test('no token means known scope ONLY, never all-repo coverage',async()=>{
 const x=await inventory({fetcher:async url=>({ok:true,json:async()=>url.includes('/pulls?')?[]:[]}),token:''});
 assert.equal(x.complete,false);
 assert.equal(x.repository_enumeration_complete,false);
 assert.equal(x.repository_coverage,'KNOWN_SCOPE_ONLY');
 assert.equal(x.repos.length,REPOS.length);
 await assert.rejects(()=>inventory({fetcher:fixture,token:'',privateDetails:true}),/PRIVATE_DETAILS_REQUIRE_AUTHENTICATION/);
});
test('403 on repository discovery or item read yields UNKNOWN rather than zero',async()=>{
 const x=await inventory({fetcher:async()=>({ok:false,status:403}),token:'test-token'});
 assert.equal(x.complete,false);
 assert.equal(x.repos[3].open_pr_count,null);
 assert.equal(x.repos[3].open_issue_count,null);
 assert.equal(x.repos[3].complete,false);
});
test('parked closed research is opt-in hint, cannot authorize reopen or merge',async()=>{
 const x=await inventory({fetcher:fixture,token:'test-token',includeClosedParked:true});
 assert.equal(x.repos[0].closed_parked_candidates_count,1);
 assert.equal(x.repos[3].closed_parked_candidates,'REDACTED_LOCAL_ONLY');
 assert.equal(x.repos[0].closed_parked_candidates[0].disposition,'UNOBSERVED_NEEDS_ORIGINAL_OWNER_AND_NATIVE_GATES');
});
test('pagination cap cannot claim exhaustive inventory',async()=>{
 const page=Array.from({length:100},(_,i)=>({number:i+1,title:'PR '+i}));
 const fetcher=async()=>({ok:true,json:async()=>page});
 const x=await collect(fetcher,'https://api.github.com/repos/Donh91/Anything/pulls?state=open','test-token',1);
 assert.equal(x.complete,false);
 assert.equal(x.items.length,100);
});
test('parked status is a hint, not a release gate',()=>{
 const x=classify({number:4,title:'parked research',labels:[]},'ISSUE');
 assert.equal(x.parked_hint,true);
 assert.equal(x.disposition,'UNOBSERVED_NEEDS_ORIGINAL_OWNER_AND_NATIVE_GATES');
});

test('enumeration missing visibility is PARTIAL, never implicit public',async()=>{
 const altered=repoPayload.concat({full_name:'Donh91/Visibility-Omitted',owner:{login:'Donh91'}});
 const f=async url=>({ok:true,json:async()=>url.includes('/user/repos')?altered:[]});
 const d=await discoverRepositories({fetcher:f,token:'test-token'});
 assert.equal(d.complete,false);
 assert.equal(d.warning,'REPOSITORY_VISIBILITY_UNOBSERVED');
 assert.equal(d.repos.has('Donh91/Visibility-Omitted'),false);
});
test('known-private repository cannot be downgraded by contradictory enumeration',async()=>{
 const altered=repoPayload.map(x=>x.full_name==='Donh91/Investering-AI-Audit-Bridge'?{...x,private:false}:x);
 const f=async url=>({ok:true,json:async()=>url.includes('/user/repos')?altered:[]});
 const d=await discoverRepositories({fetcher:f,token:'test-token'});
 assert.equal(d.complete,false);
 assert.equal(d.repos.get('Donh91/Investering-AI-Audit-Bridge'),true);
});

test('restricted data plane is excluded even with noncanonical case',async()=>{
 const changed=repoPayload.concat({full_name:'Donh91/SeCrEtS',private:true,owner:{login:'Donh91'}});
 const f=async url=>({ok:true,json:async()=>url.includes('/user/repos')?changed:[]});
 const d=await discoverRepositories({fetcher:f,token:'test-token'});
 assert.equal([...d.repos.keys()].some(x=>x.toLowerCase()==='donh91/secrets'),false);
});
