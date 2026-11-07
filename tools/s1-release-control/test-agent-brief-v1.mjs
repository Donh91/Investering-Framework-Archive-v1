import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
import {composeBrief} from './agent-brief-v1.mjs';
const SHA='a'.repeat(40), ALT='b'.repeat(40), SRC='https://github.com/Donh91/Investering-Framework-Archive-v1/blob/'+SHA+'/LATEST_OPERATIONS_DASHBOARD.json';
const REPO='Donh91/Investering-Framework-Archive-v1';
function src(id,summary={}){return {
 id,status:'OBSERVED',freshness:'FRESH_ADVISORY',owner:'ORIGINAL_'+id.toUpperCase(),
 main_sha:SHA,blob_sha:'c'.repeat(40),source_url:SRC,observed_at_utc:'2026-11-07T13:00:00Z',
 summary,release_authority:false
};}
const ctx=()=>({
 schema:'S1_AGENT_OPERATIONS_CONTEXT_v1',main_sha:SHA,partial:false,
 merge_authorized:false,production_verified:false,
 source_files:[
  src('operations',{original_required_actions:[{priority:'P1',system:'automation_health',reason:'SOURCE_AMBER'}]}),
  src('codex_ready',{task_refs:[{id:'case1',finding:'SAFE_CANDIDATE',source_url:SRC,
    original_signature:'abcdef',risk_class:'B_CODEX_PR_RESEARCH',route:'CODEX_PR'}]}),
  src('handoff',{})
 ]
});
const one=(n,risk='LOW',release_disposition='PROPOSED')=>({
 repo:REPO,pr_number:n,head_sha:'b'.repeat(40),main_sha:SHA,source_ref:'https://github.com/'+REPO+'/pull/'+n,
 observed_at:'2026-11-07T13:00:00Z',next_action:{code:'REVIEW',label:'Qualify original'},
 owner:'Donh91',risk,release_disposition,
 required_gates:{owner_release:'UNOBSERVED',recovery:'UNOBSERVED'}
});
const rel=()=>({schema:'S1_RELEASE_PROJECTION_v1',release_authority:false,
 unattended_s1_closure_proven:false,partial:false,
 source_repositories:[{repo:REPO,main_sha:SHA,observed:true,discovery_complete:true}],
 items:[one(1996),one(1982,'HIGH','HOLD'),one(1877,'LOW','BLOCKED')]
});
test('advisory brief preserves exact source owner hints and 3 PR cap without merge authority',()=>{
 const a=composeBrief(ctx(),rel(),'2026-11-07T13:02:00Z');
 assert.equal(a.schema,'S1_AGENT_OPERATIONS_BRIEF_v1');
 assert.equal(a.source_alignment,'MATCHED');
 assert.equal(a.state,'OBSERVED_ADVISORY');
 assert.equal(a.original_actions[0].reason,'SOURCE_AMBER');
 assert.equal(a.original_actions[0].original_source_ref,SRC);
 assert.equal(a.original_codex_ready_hints[0].candidate_id,'case1');
 assert.equal(a.public_pr_triage[0].pr_number,1877);
 assert.equal(a.existing_s1_action_limit,3);
 assert.equal(a.invariant.release_permission,false);
 assert.equal(a.invariant.no_new_canonical_queue,true);
 assert.equal(a.existing_actors.Grok.formal_approval_proven,false);
 for(const p of a.public_pr_triage){
  assert.equal(p.eligible_for_merge_from_brief,false);
  assert.equal(p.natural_S1_execution_proven,false);
  assert.equal(p.pr_dependencies_verified,false);
 }
});
test('different original main SHAs force recheck without inventing completion',()=>{
 const r=rel();r.source_repositories[0].main_sha=ALT;
 const a=composeBrief(ctx(),r,'2026-11-07T13:02:00Z');
 assert.equal(a.archive_main_sha,null);
 assert.equal(a.source_alignment,'UNOBSERVED');
 assert.equal(a.state,'PARTIAL_OR_STALE_RECHECK');
 assert.ok(a.public_pr_triage.every(p=>p.source_alignment==='UNOBSERVED'));
 assert.equal(a.permitted_readonly_parallel_research,true);
});
test('a stale or inaccessible canonical owner cannot become an actionable hint',()=>{
 const c=ctx();c.partial=true;
 c.source_files[0].freshness='STALE';
 c.source_files[1].status='UNOBSERVED';
 const a=composeBrief(c,rel(),'2026-11-07T13:02:00Z');
 assert.equal(a.state,'PARTIAL_OR_STALE_RECHECK');
 assert.deepEqual(a.original_actions,[]);
 assert.deepEqual(a.original_codex_ready_hints,[]);
 assert.equal(a.invariant.release_permission,false);
});
test('source attempts to grant release or autonomy are rejected',()=>{
 for(const patch of [{merge_authorized:true},{production_verified:true}]){
  assert.throws(()=>composeBrief({...ctx(),...patch},rel(),'2026-11-07T13:02:00Z'),/UNTRUSTED_SOURCE_AUTHORITY_CLAIM/);
 }
 for(const patch of [{release_authority:true},{unattended_s1_closure_proven:true}]){
  assert.throws(()=>composeBrief(ctx(),{...rel(),...patch},'2026-11-07T13:02:00Z'),/UNTRUSTED_SOURCE_AUTHORITY_CLAIM/);
 }
});
test('corrupt schema or empty source data cannot synthesize original work',()=>{
 assert.throws(()=>composeBrief({...ctx(),schema:'FAKE'},rel(),'now'),/CONTRACT_MISMATCH/);
 const c=ctx();c.source_files=[];
 const r=rel();r.items=[];
 const a=composeBrief(c,r,'2026-11-07T13:02:00Z');
 assert.deepEqual(a.original_actions,[]);
 assert.deepEqual(a.original_codex_ready_hints,[]);
 assert.deepEqual(a.public_pr_triage,[]);
});
test('PR hints never exceed 8 or S1 limit 3',()=>{
 const r=rel();r.items=Array.from({length:22},(_,i)=>one(i+1));
 const a=composeBrief(ctx(),r,'2026-11-07T13:02:00Z');
 assert.equal(a.public_pr_triage.length,8);
 assert.equal(a.existing_s1_action_limit,3);
 assert.equal(a.queue_slots_visible,8);
 assert.equal(a.parallel_original_PR_independence_proven,false);
});

test('versioned shared JSON schema explicitly prohibits release authority and false autonomy',()=>{
 const schema=JSON.parse(readFileSync(new URL('./schemas/agent-brief-v1.schema.json',import.meta.url),'utf8'));
 assert.equal(schema.properties.schema.const,'S1_AGENT_OPERATIONS_BRIEF_v1');
 assert.equal(schema.properties.existing_s1_action_limit.const,3);
 assert.ok(schema.properties.state.enum.includes('OBSERVED_ADVISORY_SAMPLED'));
 assert.ok(schema.properties.source_scope.enum.includes('VERIFIED_PUBLIC_PR_SAMPLE_NOT_EXHAUSTIVE'));
 assert.equal(schema.properties.queue_slots_visible.const,8);
 assert.equal(schema.properties.invariant.properties.no_new_scheduler.const,true);
 assert.equal(schema.properties.invariant.properties.release_permission.const,false);
 assert.equal(schema.properties.invariant.properties.no_private_source_publication.const,true);
 assert.equal(schema.properties.public_pr_triage.items.properties.eligible_for_merge_from_brief.const,false);
 assert.equal(schema.properties.public_pr_triage.items.properties.natural_S1_execution_proven.const,false);
 for(const x of ['private_bridge','private_alpha_lab','independent_recovery'])
  assert.equal(schema.properties.source_coverage.properties[x].const,'UNOBSERVED');
});

test('verified bounded PR sample remains usable for research but never claims full coverage',()=>{
 const r=rel();
 r.partial=true;
 r.source_repositories[0].discovery_complete=false;
 r.source_repositories[0].source_issues=['PR_DISCOVERY_SAMPLED_NOT_COMPLETE'];
 r.items=r.items.map(p=>({...p,source_issues:['PR_DISCOVERY_SAMPLED_NOT_COMPLETE']}));
 const a=composeBrief(ctx(),r,'2026-11-07T13:02:00Z');
 assert.equal(a.source_alignment,'MATCHED');
 assert.equal(a.state,'OBSERVED_ADVISORY_SAMPLED');
 assert.equal(a.source_scope,'VERIFIED_PUBLIC_PR_SAMPLE_NOT_EXHAUSTIVE');
 assert.equal(a.parallel_original_PR_independence_proven,false);
 assert.ok(a.public_pr_triage.every(p=>p.discovery_complete===false));
 assert.ok(a.public_pr_triage.every(p=>p.eligible_for_merge_from_brief===false));
});
test('one source error beyond intended sampling invalidates advisory sample qualification',()=>{
 const r=rel();
 r.partial=true;
 r.source_repositories[0].source_issues=['PR_DISCOVERY_SAMPLED_NOT_COMPLETE'];
 r.items=r.items.map(p=>({...p,source_issues:['PR_DISCOVERY_SAMPLED_NOT_COMPLETE']}));
 r.items[0].source_issues.push('RUNS_RATE_LIMITED');
 const a=composeBrief(ctx(),r,'2026-11-07T13:02:00Z');
 assert.equal(a.state,'PARTIAL_OR_STALE_RECHECK');
 assert.equal(a.source_scope,'PARTIAL_OR_UNVERIFIED');
});
