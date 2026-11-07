/* Validate one S1 Agent Brief CI artifact before an existing owner reads it.
 * This is structural/source-reference QA only, NEVER a release authorization.
 */
import {readFileSync} from 'node:fs';
import {pathToFileURL} from 'node:url';
const SHA=/^[a-f0-9]{40}$/i;
const HEX64=/^[a-f0-9]{64}$/i;
export function validateAgentBriefArtifact(packet,expectedPrHead){
 const failures=[];
 const fail=(code)=>failures.push(code);
 if(!SHA.test(expectedPrHead||''))fail('EXPECTED_HEAD_REQUIRED');
 if(!packet||typeof packet!=='object'||Array.isArray(packet))return {status:'REJECTED',failures:[...failures,'PACKET_NOT_OBJECT'],merge_authorized:false};
 if(packet.contract!=='S1_AGENT_BRIEF_CI_ARTIFACT_v1')fail('ARTIFACT_CONTRACT_MISMATCH');
 if(!SHA.test(packet.candidate_pr_head_sha||'')||packet.candidate_pr_head_sha!==expectedPrHead)fail('CANDIDATE_PR_HEAD_MISMATCH');
 if(packet.authority!=='ADVISORY_READ_ONLY'||packet.can_merge!==false||packet.can_schedule!==false||packet.can_spend!==false||packet.public_only!==true)fail('FORBIDDEN_ARTIFACT_AUTHORITY');
 const b=packet.brief;
 if(!b||typeof b!=='object'||Array.isArray(b))return {status:'REJECTED',failures:[...failures,'BRIEF_MISSING'],merge_authorized:false};
 if(b.schema!=='S1_AGENT_OPERATIONS_BRIEF_v1')fail('BRIEF_SCHEMA_MISMATCH');
 if(b.source_alignment!=='MATCHED'||!['OBSERVED_ADVISORY','OBSERVED_ADVISORY_SAMPLED'].includes(b.state))fail('SOURCE_NOT_ALIGNED');
 const main=b.archive_main_sha;
 if(!SHA.test(main||'')||packet.original_source_main_sha!==main||b.original_context_main_sha!==main||b.original_pr_main_sha!==main)fail('SOURCE_MAIN_BINDING_MISMATCH');
 if(!b.observed_at_utc||packet.source_observed_at_utc!==b.observed_at_utc||!Number.isFinite(Date.parse(b.observed_at_utc)))fail('SOURCE_CLOCK_BINDING_INVALID');
 if(!b.invariant||b.invariant.release_permission!==false||b.invariant.no_new_scheduler!==true||b.invariant.no_new_canonical_queue!==true||b.invariant.no_new_identity!==true||b.invariant.action_cap_per_existing_s1_tick!==3)fail('ORIGINAL_AUTHORITY_OR_ACTION_CAP_INVALID');
 if(b.existing_s1_action_limit!==3||b.queue_slots_visible!==8||b.existing_actors?.S1?.natural_closure_proven!=='UNOBSERVED'||b.existing_actors?.Grok?.formal_approval_proven!==false)fail('AUTONOMY_OR_APPROVAL_MISREPRESENTED');
 const cov=b.source_coverage;
 if(!cov||cov.private_bridge!=='UNOBSERVED'||cov.private_alpha_lab!=='UNOBSERVED'||cov.independent_recovery!=='UNOBSERVED')fail('PRIVATE_RECOVERY_BOUNDARY_VIOLATED');
 const sources=Array.isArray(cov?.canonical_sources)?cov.canonical_sources:[];
 if(!sources.length)fail('ORIGINAL_CANONICAL_SOURCES_MISSING');
 for(const x of sources){
   if(!x||x.status!=='OBSERVED'||x.freshness!=='FRESH_ADVISORY'||!SHA.test(x.blob_sha||'')||
       typeof x.source_ref!=='string'||!x.source_ref.startsWith('https://github.com/Donh91/Investering-Framework-Archive-v1/blob/'+main+'/'))
     fail('ORIGINAL_SOURCE_IDENTITY_UNVERIFIED');
 }
 const prSource=cov?.public_github_repository;
 if(!prSource||prSource.repo!=='Donh91/Investering-Framework-Archive-v1'||prSource.main_sha!==main||prSource.observed!==true)fail('PUBLIC_PR_SOURCE_UNVERIFIED');
 const triage=Array.isArray(b.public_pr_triage)?b.public_pr_triage:[];
 if(!triage.length||triage.length>8)fail('ORIGINAL_PR_SAMPLE_INVALID');
 for(const p of triage){
   if(!p||!SHA.test(p.head_sha||'')||p.main_sha!==main||p.eligible_for_merge_from_brief!==false||p.natural_S1_execution_proven!==false||p.pr_dependencies_verified!==false)fail('PR_HINT_HAS_UNVERIFIED_PRIVILEGE');
 }
 if(b.state==='OBSERVED_ADVISORY_SAMPLED'){
   if(prSource?.discovery_complete!==false||!Array.isArray(prSource.source_issues)||!prSource.source_issues.includes('PR_DISCOVERY_SAMPLED_NOT_COMPLETE'))fail('SAMPLED_DISCOVERY_MISCLASSIFIED');
 }else if(prSource?.discovery_complete!==true)fail('COMPLETE_DISCOVERY_UNVERIFIED');
 return {status:failures.length?'REJECTED':'ADVISORY_SOURCE_IDENTITIES_VERIFIED',failures,merge_authorized:false,production_verified:false,natural_S1_proven:false};
}
async function main(){
 const args=process.argv.slice(2);
 if(args.length!==2)throw Error('Usage: node verify-agent-brief-v1.mjs ARTIFACT.json EXPECTED_EXACT_PR_HEAD_SHA');
 const bytes=readFileSync(args[0]);
 if(!bytes.length||bytes.length>1e6)throw Error('ARTIFACT_BYTES_OUT_OF_BOUNDS');
 const response=validateAgentBriefArtifact(JSON.parse(bytes.toString('utf8')),args[1]);
 console.log(JSON.stringify(response));
 if(response.status!=='ADVISORY_SOURCE_IDENTITIES_VERIFIED')process.exitCode=1;
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)main().catch(e=>{console.error('S1_ARTIFACT_REJECTED',e.message);process.exitCode=1;});
