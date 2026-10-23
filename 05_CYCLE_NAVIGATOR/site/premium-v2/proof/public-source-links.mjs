/**
 * Premium v2.1 PROOF · public, commit-pinned navigation helpers only.
 * Pure UI projection: NOT an evaluator, attester, source issuer or scorer.
 * A mutable "main" GitHub link is not evidence of the original issued bytes.
 */
const REPOS=new Set([
  'Donh91/Investering-Framework-Archive-v1',
  'Donh91/CycleNavigator-scores'
]);
const ID=/^[a-f0-9]{40}$/i;
const SEGMENT=/^[a-zA-Z0-9._-]+$/;
const SAFE_PREFIX={
  'Donh91/Investering-Framework-Archive-v1':[
    '05_CYCLE_NAVIGATOR/weekly/','05_CYCLE_NAVIGATOR/public_scorecards/',
    '03_WEEKLY_OPERATIONS/cycle_navigator/','04_MARKET_LEARNING/cycle_navigator/public/'
  ],
  'Donh91/CycleNavigator-scores':['forecasts/','scores/','v2/source-receipts/','v2/']
};
export function canonicalPublicSourceLink({repo,source_commit,path}={}){
 if(!REPOS.has(repo)||!ID.test(String(source_commit||''))||
   typeof path!=='string'||path.length>440||
   !SAFE_PREFIX[repo].some(prefix=>path.startsWith(prefix)))return null;
 const parts=path.split('/');
 if(parts.some(segment=>!SEGMENT.test(segment)||segment==='.'||segment==='..'))return null;
 return 'https://github.com/'+repo+'/blob/'+source_commit+'/'+
   parts.map(encodeURIComponent).join('/');
}
export function publicProofView(index,sourceCommit=null){
 if(index?.contract!=='CN_V2_PUBLIC_SCORE_INDEX_v1')return {
  status:'UNAVAILABLE',reason:'SCORE_INDEX_CONTRACT_UNAVAILABLE',score:null,source_url:null
 };
 const f=index?.current_frozen_forecast||{},v=index?.verification||{};
 const source_url=canonicalPublicSourceLink({
  repo:f.original_source_repo,source_commit:sourceCommit,path:f.original_source_path
 });
 // No frontend may promote a bootstrap public mirror into independent proof.
 const proofUnsealed=v.git_commit_is_not_independent_timestamp!==false||
   v.immutable_release_enabled_and_verified!==true||
   v.external_anchor_confirmed!==true||
   v.independent_outcome_reproduction!==true;
 const eligible=Number.isInteger(f.eligible_binary_claims)&&f.eligible_binary_claims>0;
 return {
  contract:'CN_PREMIUM_V2_PROOF_UI_PROJECTION_v1',
  status:proofUnsealed?'PROVISIONAL':'AWAIT_OFFICIAL_ATTESTATION',
  source_issue_number:f.source_issue_number??null,forecast_week:f.forecast_week??null,
  source_url,source_commit:source_url?sourceCommit:null,
  source_manifest_sha256:/^[a-f0-9]{64}$/i.test(String(f.source_manifest_sha256||''))?
    f.source_manifest_sha256:null,
  original_source_issued_at_utc:f.source_weekly_issued_at_utc||null,
  eligible_binary_claims:eligible?f.eligible_binary_claims:0,
  abstained_claims:Number.isInteger(f.abstained_claims)?f.abstained_claims:null,
  edge_score:eligible?f.v2_score??null:null,
  edge_status:eligible?'UNVERIFIED':'ABSTAIN',
  price_range_accuracy:null, // independent score family, never derived here
  publication_verification_status:f.verification||'PROVISIONAL',
  independent_proof_sealed:false,
  reason:!source_url?'EXACT_PUBLIC_ORIGINAL_COMMIT_REQUIRED':
     proofUnsealed?'GITHUB_READBACK_IS_NOT_EXTERNAL_ATTESTATION':'OFFICIAL_SEAL_REQUIRED'
 };
}
