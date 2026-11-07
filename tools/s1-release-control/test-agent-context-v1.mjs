import assert from 'node:assert/strict';
import test from 'node:test';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {buildAgentContext} from './agent-context-v1.mjs';
const S='a'.repeat(40), B='b'.repeat(40), D='d'.repeat(40);
const root='https://api.github.com/repos/Donh91/Investering-Framework-Archive-v1';
const observed='2026-11-07T13:30:00Z';
const file='LATEST_CODEX_READY_TASKS.json';
const data={contract:'CODEX_READY_TASKS_v1',generated_at_utc:'2026-11-07T12:20:00Z',tasks:[
 {candidate_id:'s1-bounded-case',candidate_path:'research/codex/intake/2026/11/s1-bounded-case.json',lifecycle_state:'ACTIVE'},
 {candidate_id:'t2-case',candidate_path:'research/codex/intake/2026/11/t2-case.json'}
]};
function makeResponse(value,status=200){return {ok:status===200,status,json:async()=>value};}
function fake({mainAfter=S,deny=false,badBlob=false,spoofBlob=false,untrusted=false,stale=false}={}){
 let branches=0;const calls=[];
 const fetcher=async (url,opts)=>{
  calls.push({url,opts});
  assert.equal(opts.method,undefined);
  assert.equal(opts.headers.Authorization,undefined);
  assert.equal(opts.headers['X-GitHub-Api-Version'],'2022-11-28');
  if(url===root+'/branches/main'){branches++;return makeResponse({commit:{sha:branches===1?S:mainAfter}});}
  if(url===root+'/contents/'+file+'?ref='+S){
   if(deny)return makeResponse({},403);
   const body={...data,generated_at_utc:stale?'2026-10-01T00:00:00Z':data.generated_at_utc};
   const content=Buffer.from(JSON.stringify(body),'utf8');
   return makeResponse({encoding:'base64',content:content.toString('base64'),
     sha:badBlob?'short':spoofBlob?B:createHash('sha1').update('blob '+content.length+'\\0').update(content).digest('hex'),size:untrusted?content.length+1:content.length});
  }
  throw Error('EXTRA_OR_PRIVATE_ROUTE:'+url);
 };
 return {fetcher,calls};
}
test('agent canonical source is pinned to double-read main and content digest',async()=>{
 const {fetcher,calls}=fake();
 const out=await buildAgentContext({fetcher,clock:()=>observed,sources:['codex_ready']});
 assert.equal(out.schema,'S1_AGENT_OPERATIONS_CONTEXT_v1');
 assert.equal(out.main_sha,S);
 assert.equal(out.partial,false);
 assert.equal(out.source_readback_verified,true);
 const source=out.source_files[0];
 assert.match(source.blob_sha,/^[a-f0-9]{40}$/);
 assert.match(source.sha256,/^[0-9a-f]{64}$/);
 assert.equal(source.freshness,'FRESH_ADVISORY');
 assert.ok(source.source_url.includes('/blob/'+S+'/'+file));
 assert.equal(out.existing_owners.Codex.ready_count_observed,2);
 assert.equal(source.summary.task_refs.length,2);
 assert.equal(source.summary.task_refs[0].finding,null);
 assert.ok(source.summary.task_refs[0].source_url?.includes('/blob/'+S+'/research/codex/intake/'));

 assert.equal(out.merge_authorized,false);
 assert.equal(out.existing_owners.Grok.formal_approval,false);
 assert.equal(calls.length,3);
 assert.ok(calls.every(x=>x.url.startsWith(root)));
});
test('explicit no-read on private Bridge, Alpha and restricted data plane',async()=>{
 const {fetcher,calls}=fake();
 const out=await buildAgentContext({fetcher,clock:()=>observed,sources:['codex_ready']});
 assert.equal(calls.filter(x=>/Bridge|Alpha-Lab|secrets/.test(x.url)).length,0);
 assert.equal(out.workflow_boundaries.private_bridge,'UNOBSERVED_UNTIL_ORIGINAL_AUTHENTICATED_REVIEW');
 assert.equal(out.production_verified,false);
});
test('main changing during scan invalidates even previously valid source',async()=>{
 const {fetcher}=fake({mainAfter:D});
 const out=await buildAgentContext({fetcher,clock:()=>observed,sources:['codex_ready']});
 assert.equal(out.main_sha,null);
 assert.equal(out.partial,true);
 assert.equal(out.source_readback_verified,false);
 assert.equal(out.source_files[0].status,'UNOBSERVED');
 assert.ok(out.source_errors.includes('MAIN_CHANGED_OR_INACCESSIBLE_DURING_READBACK'));
});
test('denied, malformed blob or truncated bytes remain UNOBSERVED',async()=>{
 for(const options of [{deny:true},{badBlob:true},{spoofBlob:true},{untrusted:true}]){
  const {fetcher}=fake(options);
  const out=await buildAgentContext({fetcher,clock:()=>observed,sources:['codex_ready']});
  assert.equal(out.source_files[0].status,'UNOBSERVED');
  assert.equal(out.partial,true);
  assert.equal(out.merge_authorized,false);
 }
});
test('stale information can be read but never shown as fresh admission',async()=>{
 const {fetcher}=fake({stale:true});
 const out=await buildAgentContext({fetcher,clock:()=>observed,sources:['codex_ready']});
 assert.equal(out.source_files[0].status,'OBSERVED');
 assert.equal(out.source_files[0].freshness,'STALE');
 assert.equal(out.partial,true);
 assert.equal(out.source_freshness_all_advisory_pass,false);
});
test('owner and source allowlists reject extra paths, duplicate and missing entries',async()=>{
 const {fetcher}=fake();
 for(const sources of [[],['codex_ready','codex_ready'],['secrets'],['../../env'],['codex_ready','unknown']]){
  await assert.rejects(()=>buildAgentContext({fetcher,sources}),/SOURCE_ALLOWLIST_REQUIRED/);
 }
});
test('immutable source contract is never a release or autonomous S1 receipt',async()=>{
 const {fetcher}=fake();
 const out=await buildAgentContext({fetcher,clock:()=>observed,sources:['codex_ready']});
 assert.equal(out.existing_owners.S1.autonomy_proven,'UNOBSERVED');
 assert.equal(out.execution_provenance,'INTERACTIVE_OR_ON_DEMAND_READ_ONLY_NOT_SCHEDULED_S1');
 assert.equal(out.promotion_status,'ADVISORY_PROJECTION_ONLY');
 assert.ok(out.consumer_instructions.forbidden.includes('AUTO_MERGE_FROM_PROJECTION'));
});
test('mutation negative: removal of SHA check must be detected',()=>{
 const source=readFileSync(new URL('./agent-context-v1.mjs',import.meta.url),'utf8');
 assert.match(source,/main!==?after|before===after/);
 assert.match(source,/SOURCE_BYTE_COUNT_INVALID/);
 assert.match(source,/SOURCE_CONTENT_IDENTITY_INVALID/);
 assert.doesNotMatch(source,/github_pat_|ghp_|sk-proj-|api\.openai\.com/);
 assert.doesNotMatch(source,/\b(?:POST|PATCH|DELETE|PUT)\b/);
});
