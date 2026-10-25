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

/**
 * Join the bootstrap score index to a PUBLIC GitHub source readback.
 * A readback's original source_commit is a navigation address / byte identity,
 * NOT evidence that the original claim predated the market outcome.
 * A valid score index + readback never grants independent VERIFIED status.
 */
export function sourceReadbackProofRows(index,receipt){
 if(index?.contract!=='CN_V2_PUBLIC_SCORE_INDEX_v1'||
    receipt?.contract!=='CN_PUBLIC_SOURCE_READBACK_v1'||
    !Array.isArray(receipt.frozen_claims))return [];
 const result=[];
 for(const record of receipt.frozen_claims.slice(0,30)){
   if(!Number.isInteger(record?.public_issue_number)||
      !/^\d{4}-W\d{2}$/.test(String(record.forecast_week||''))||
      record.source_repo!=='Donh91/Investering-Framework-Archive-v1'||
      record.verification!=='PROVISIONAL'||
      !/^[a-f0-9]{64}$/i.test(String(record.sha256||''))||
      !/^[a-f0-9]{40}$/i.test(String(record.source_blob_sha1||'')))continue;
   const token=record.forecast_week.replace('-W','/W');
   if(!record.source_path.includes('/'+token+'/'))continue;
   const source_url=canonicalPublicSourceLink({
     repo:record.source_repo,source_commit:record.source_commit,path:record.source_path});
   if(!source_url)continue;
   const count=Number(record.claim_count),eligible=Number(record.eligible_binary_claims),
     abstained=Number(record.abstained_claims);
   if(![count,eligible,abstained].every(Number.isInteger)||
     count<0||eligible<0||abstained<0||eligible+abstained>count)continue;
   result.push({
     contract:'CN_PREMIUM_V2_SOURCE_RECEIPT_NAV_v1',
     public_issue_number:record.public_issue_number,forecast_week:record.forecast_week,
     source_url,source_commit:record.source_commit,source_path:record.source_path,
     source_sha256:record.sha256,source_blob_sha1:record.source_blob_sha1,
     total_claims:count,eligible_binary_claims:eligible,abstained_claims:abstained,
     edge_accuracy:null,independent_proof_status:'PROVISIONAL_NOT_SEALED',
     score_authority:false,source_git_commit_is_independent_timestamp:false
   });
 }
 return result.sort((a,b)=>b.public_issue_number-a.public_issue_number);
}
