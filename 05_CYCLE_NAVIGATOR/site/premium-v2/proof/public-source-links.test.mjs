import test from 'node:test';
import assert from 'node:assert/strict';
import {canonicalPublicSourceLink,publicProofView,sourceReadbackProofRows} from './public-source-links.mjs';
const COMMIT='a'.repeat(40);
const INDEX={contract:'CN_V2_PUBLIC_SCORE_INDEX_v1',
 current_frozen_forecast:{
  source_issue_number:29,forecast_week:'2026-W42',
  original_source_repo:'Donh91/Investering-Framework-Archive-v1',
  original_source_path:'05_CYCLE_NAVIGATOR/weekly/2026/W42/CYCLE_NAVIGATOR_V2_EDGE_FREEZE.json',
  source_manifest_sha256:'b'.repeat(64),source_weekly_issued_at_utc:'2026-10-12T06:32:25Z',
  eligible_binary_claims:0,abstained_claims:10,v2_score:null,
  verification:'PROVISIONAL_NOT_EXTERNALLY_PREWINDOW_ATTESTED'},
 verification:{git_commit_is_not_independent_timestamp:true,
  immutable_release_enabled_and_verified:false,external_anchor_confirmed:false,
  independent_outcome_reproduction:false}};
test('public link MUST pin original immutable commit not mutable main',()=>{
 const args={repo:'Donh91/Investering-Framework-Archive-v1',source_commit:COMMIT,
  path:'05_CYCLE_NAVIGATOR/weekly/2026/W42/CYCLE_NAVIGATOR_V2_EDGE_FREEZE.json'};
 const url=canonicalPublicSourceLink(args);
 assert.ok(url?.includes('/blob/'+COMMIT+'/'));assert.equal(canonicalPublicSourceLink({...args,source_commit:'main'}),null);
});
test('refuse private paths, traversal, other repos and query injection',()=>{
 const args={repo:'Donh91/Investering-Framework-Archive-v1',source_commit:COMMIT,
  path:'05_CYCLE_NAVIGATOR/weekly/2026/W42/source.json'};
 assert.equal(canonicalPublicSourceLink({...args,path:'../../secrets/keys.json'}),null);
 assert.equal(canonicalPublicSourceLink({...args,path:'05_CYCLE_NAVIGATOR/weekly/../secrets.json'}),null);
 assert.equal(canonicalPublicSourceLink({...args,path:'05_CYCLE_NAVIGATOR/weekly/w42/file.json?api_key=secret'}),null);
 assert.equal(canonicalPublicSourceLink({...args,repo:'Donh91/secrets'}),null);
});
test('W42 10/10 abstain is not a positive predictive edge',()=>{
 const v=publicProofView(INDEX,COMMIT);
 assert.equal(v.status,'PROVISIONAL');assert.equal(v.edge_status,'ABSTAIN');
 assert.equal(v.edge_score,null);assert.equal(v.abstained_claims,10);
 assert.equal(v.independent_proof_sealed,false);
 assert.ok(v.source_url.endsWith('/CYCLE_NAVIGATOR_V2_EDGE_FREEZE.json'));
});
test('without real commit no exact public link; never synthesize Git SHA',()=>{
 const v=publicProofView(INDEX,null);assert.equal(v.source_url,null);
 assert.equal(v.reason,'EXACT_PUBLIC_ORIGINAL_COMMIT_REQUIRED');
});
test('even impressive flags cannot be promoted to independently VERIFIED in frontend',()=>{
 const f=JSON.parse(JSON.stringify(INDEX));
 f.verification={git_commit_is_not_independent_timestamp:false,
 immutable_release_enabled_and_verified:true,external_anchor_confirmed:true,
 independent_outcome_reproduction:true};
 const v=publicProofView(f,COMMIT);
 assert.equal(v.status,'AWAIT_OFFICIAL_ATTESTATION');
 assert.equal(v.independent_proof_sealed,false);
});

const READBACK={contract:'CN_PUBLIC_SOURCE_READBACK_v1',frozen_claims:[{
 source_repo:'Donh91/Investering-Framework-Archive-v1',
 source_commit:COMMIT,source_path:'05_CYCLE_NAVIGATOR/weekly/2026/W42/CYCLE_NAVIGATOR_V2_EDGE_FREEZE.json',
 forecast_week:'2026-W42',public_issue_number:29,sha256:'1'.repeat(64),
 source_blob_sha1:'2'.repeat(40),claim_count:10,eligible_binary_claims:0,
 abstained_claims:10,verification:'PROVISIONAL'
}]};
test('proof readback source requires pinned public source path/hash and labels only PROVISIONAL',()=>{
 const rows=sourceReadbackProofRows(INDEX,READBACK);
 assert.equal(rows.length,1);
 assert.equal(rows[0].public_issue_number,29);
 assert.equal(rows[0].independent_proof_status,'PROVISIONAL_NOT_SEALED');
 assert.equal(rows[0].edge_accuracy,null);
 assert.ok(rows[0].source_url.includes('/blob/'+COMMIT+'/'));
});
test('reject spoofed provenance and score family mixing in public Proof nav',()=>{
 const s=JSON.parse(JSON.stringify(READBACK));
 s.frozen_claims[0].source_path='05_CYCLE_NAVIGATOR/weekly/2026/W43/CYCLE_NAVIGATOR_V2_EDGE_FREEZE.json';
 assert.equal(sourceReadbackProofRows(INDEX,s).length,0);
 s.frozen_claims[0].source_path='05_CYCLE_NAVIGATOR/weekly/2026/W42/CYCLE_NAVIGATOR_V2_EDGE_FREEZE.json';
 s.frozen_claims[0].source_repo='Donh91/secrets';
 assert.equal(sourceReadbackProofRows(INDEX,s).length,0);
 s.frozen_claims[0].source_repo='Donh91/Investering-Framework-Archive-v1';
 s.frozen_claims[0].eligible_binary_claims=11;
 assert.equal(sourceReadbackProofRows(INDEX,s).length,0);
});
