import assert from 'node:assert/strict';
import test from 'node:test';
import {validateAgentBriefArtifact} from './verify-agent-brief-v1.mjs';
const H='a'.repeat(40),M='b'.repeat(40),B='c'.repeat(40);
const REPO='Donh91/Investering-Framework-Archive-v1';
const now='2026-11-07T13:00:00Z';
const verify=(p,h=H)=>validateAgentBriefArtifact(p,h,{now});
const packet=()=>({
 contract:'S1_AGENT_BRIEF_CI_ARTIFACT_v1',
 candidate_pr_head_sha:H,original_source_main_sha:M,source_observed_at_utc:now,
 authority:'ADVISORY_READ_ONLY',can_merge:false,can_schedule:false,can_spend:false,public_only:true,
 brief:{
  schema:'S1_AGENT_OPERATIONS_BRIEF_v1',source_alignment:'MATCHED',state:'OBSERVED_ADVISORY_SAMPLED',
  archive_main_sha:M,original_context_main_sha:M,original_pr_main_sha:M,observed_at_utc:now,
  invariant:{release_permission:false,no_new_scheduler:true,no_new_canonical_queue:true,no_new_identity:true,
   action_cap_per_existing_s1_tick:3},
  existing_s1_action_limit:3,queue_slots_visible:8,
  existing_actors:{S1:{natural_closure_proven:'UNOBSERVED'},Grok:{formal_approval_proven:false}},
  source_coverage:{
   private_bridge:'UNOBSERVED',private_alpha_lab:'UNOBSERVED',independent_recovery:'UNOBSERVED',
   canonical_sources:[{id:'handoff',status:'OBSERVED',freshness:'FRESH_ADVISORY',main_sha:M,blob_sha:B,sha256:'d'.repeat(64),bytes:1024,
      source_ref:`https://github.com/${REPO}/blob/${M}/LATEST_HANDOFF.json`}],
   public_github_repository:{repo:REPO,main_sha:M,observed:true,discovery_complete:false,
      source_issues:['PR_DISCOVERY_SAMPLED_NOT_COMPLETE']}
  },
  public_pr_triage:[{repo:REPO,pr_number:1996,head_sha:H,main_sha:M,
    eligible_for_merge_from_brief:false,natural_S1_execution_proven:false,pr_dependencies_verified:false}]
 }
});
test('bounded original source evidence is admitted only as read-only advisory',()=>{
 const r=verify(packet(),H);
 assert.equal(r.status,'ADVISORY_SOURCE_IDENTITIES_VERIFIED');
 assert.deepEqual(r.failures,[]);
 assert.equal(r.merge_authorized,false);
 assert.equal(r.natural_S1_proven,false);
});
test('wrong or missing exact PR head fail closed',()=>{
 const p=packet();
 assert.ok(verify(p,'f'.repeat(40)).failures.includes('CANDIDATE_PR_HEAD_MISMATCH'));
 assert.ok(verify(p,'short').failures.includes('EXPECTED_HEAD_REQUIRED'));
});
test('source main, clock and source locator must be coherent',()=>{
 for(const tamper of [
  p=>p.original_source_main_sha='d'.repeat(40),
  p=>p.brief.original_context_main_sha='e'.repeat(40),
  p=>p.brief.source_coverage.canonical_sources[0].source_ref='https://github.com/Donh91/secrets/blob/'+M+'/private.json',
  p=>p.brief.observed_at_utc='2026-11-07T13:01:00Z',
  p=>p.brief.source_coverage.canonical_sources[0].blob_sha='short',
  p=>p.brief.source_coverage.canonical_sources[0].sha256='bad-hash',
  p=>p.brief.source_coverage.canonical_sources[0].bytes=-1,
  p=>p.brief.source_coverage.canonical_sources[0].main_sha='f'.repeat(40)
 ]){
  const p=packet();tamper(p);
  assert.equal(verify(p,H).status,'REJECTED');
 }
});
test('false permissions, S1 autonomy and Grok formal approval cannot pass',()=>{
 for(const tamper of [
  p=>p.can_merge=true,
  p=>p.brief.invariant.release_permission=true,
  p=>p.brief.invariant.action_cap_per_existing_s1_tick=4,
  p=>p.brief.existing_s1_action_limit=9,
  p=>p.brief.existing_actors.S1.natural_closure_proven='PASS',
  p=>p.brief.existing_actors.Grok.formal_approval_proven=true,
  p=>p.brief.public_pr_triage[0].eligible_for_merge_from_brief=true,
  p=>p.brief.public_pr_triage[0].natural_S1_execution_proven=true,
  p=>p.brief.source_coverage.private_bridge='AVAILABLE'
 ]){
  const p=packet();tamper(p);
  assert.equal(verify(p,H).status,'REJECTED');
 }
});
test('sampled PR inventory must never masquerade as complete',()=>{
 const p=packet();p.brief.source_coverage.public_github_repository.discovery_complete=true;
 assert.ok(verify(p,H).failures.includes('SAMPLED_DISCOVERY_MISCLASSIFIED'));
 const q=packet();q.brief.state='OBSERVED_ADVISORY';
 assert.ok(verify(q,H).failures.includes('COMPLETE_DISCOVERY_UNVERIFIED'));
});
test('missing body, source, or original PR is not admissible',()=>{
 for(const mutate of [
  p=>delete p.brief,
  p=>p.brief.source_coverage.canonical_sources=[],
  p=>p.brief.public_pr_triage=[],
  p=>p.brief.source_coverage.public_github_repository.observed=false
 ]){
  const p=packet();mutate(p);
  assert.equal(verify(p,H).status,'REJECTED');
 }
});
test('matched complete public discovery is allowed without merge permission',()=>{
 const p=packet();p.brief.state='OBSERVED_ADVISORY';
 p.brief.source_coverage.public_github_repository.discovery_complete=true;
 p.brief.source_coverage.public_github_repository.source_issues=[];
 const r=verify(p,H);
 assert.equal(r.status,'ADVISORY_SOURCE_IDENTITIES_VERIFIED');
 assert.equal(r.merge_authorized,false);
});

test('historical replay is invalid after 90 minutes although source SHA matches',()=>{
 const sample=packet();
 const stale=validateAgentBriefArtifact(sample,H,{now:'2026-11-07T15:00:01Z'});
 assert.equal(stale.status,'REJECTED');
 assert.ok(stale.failures.includes('ARTIFACT_SOURCE_STALE_OR_FUTURE'));
 assert.equal(stale.current_main_rechecked,false);
 assert.equal(stale.eligible_for_original_action,false);
});
test('future source clock outside bounded drift fails closed',()=>{
 const sample=packet();
 const future=validateAgentBriefArtifact(sample,H,{now:'2026-11-07T12:57:00Z'});
 assert.equal(future.status,'REJECTED');
 assert.ok(future.failures.includes('ARTIFACT_SOURCE_STALE_OR_FUTURE'));
});
test('fresh archive proof remains advisory and never becomes current main readback',()=>{
 const sample=packet();
 const good=validateAgentBriefArtifact(sample,H,{now:'2026-11-07T13:00:01Z'});
 assert.equal(good.status,'ADVISORY_SOURCE_IDENTITIES_VERIFIED');
 assert.equal(good.current_main_rechecked,false);
 assert.equal(good.eligible_for_original_action,false);
 assert.equal(good.merge_authorized,false);
});
