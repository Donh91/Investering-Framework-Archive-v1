import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';
import test from 'node:test';
const load=path=>JSON.parse(readFileSync(new URL('./schemas/'+path,import.meta.url),'utf8'));
const agent=load('agent-context-v1.schema.json');
const release=load('release-projection-v1.schema.json');
test('both machine schemas are versioned and prohibit release authority',()=>{
 assert.equal(agent.$schema,'https://json-schema.org/draft/2020-12/schema');
 assert.equal(release.$schema,'https://json-schema.org/draft/2020-12/schema');
 assert.equal(agent.properties.schema.const,'S1_AGENT_OPERATIONS_CONTEXT_v1');
 assert.equal(release.properties.schema.const,'S1_RELEASE_PROJECTION_v1');
 assert.equal(agent.properties.merge_authorized.const,false);
 assert.equal(agent.properties.production_verified.const,false);
 for(const key of ['release_authority','source_authority','formal_approval','unattended_s1_closure_proven']){
  assert.equal(release.properties[key].const,false,key);
 }
 assert.equal(release.properties.items.items.properties.merge_authorized.const,false);
 assert.equal(release.properties.items.items.properties.production_verified.const,false);
});
test('original owner, source identity, clocks and unknowns are structurally required',()=>{
 for(const field of ['observed_at_utc','main_sha','source_files','partial','workflow_boundaries','existing_owners','execution_provenance'])
   assert.ok(agent.required.includes(field),field);
 const item=agent.properties.source_files.items;
 for(const field of ['id','status','owner','main_sha','source_path','source_url','release_authority'])assert.ok(item.required.includes(field));
 assert.deepEqual(item.properties.status.enum,['OBSERVED','UNOBSERVED']);
 assert.deepEqual(item.properties.freshness.enum,['FRESH_ADVISORY','STALE','UNOBSERVED']);
 assert.equal(item.properties.release_authority.const,false);
 assert.equal(agent.properties.workflow_boundaries.properties.new_scheduler.const,false);
 assert.equal(agent.properties.workflow_boundaries.properties.new_identity.const,false);
 assert.equal(agent.properties.workflow_boundaries.properties.new_authority.const,false);
 assert.equal(agent.properties.workflow_boundaries.properties.s1_max_original_prs_per_tick.const,3);
});
test('versioned PR facts cannot omit permission or source quality',()=>{
 const row=release.properties.items.items;
 for(const field of ['head_sha','main_sha','evidence_class','required_gates','next_action','execution_provenance','merge_authorized','production_verified'])
   assert.ok(row.required.includes(field),field);
 assert.ok(row.properties.release_disposition.enum.includes('UNOBSERVED'));
 assert.ok(row.properties.release_disposition.enum.includes('BLOCKED'));
 assert.ok(row.properties.risk.enum.includes('UNKNOWN'));
 assert.equal(release.properties.queue_plan.maxItems,8);
 assert.equal(release.properties.existing_s1_action_limit.const,3);
});
