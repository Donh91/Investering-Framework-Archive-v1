// Research-only no-hindsight admission oracle. Node 20+.

// Independent proof attestation is intentionally NOT implementable by asserting a field in a JSON row.

// Run: node 04_MARKET_LEARNING/handlekompas/research/2026-10-13__task2_r1_no_hindsight_admission_oracle_v1.mjs --self-test

import fs from 'node:fs';

const RESTRICTED_KEY=/wallet|holdings|private_key|api_key|raw_chat|user_trade|password|secret|access_token|refresh_token|authorization|credential|seed_phrase|mnemonic/i;
// Public admission has a closed schema. Unknown metadata cannot hide credentials.
const ROW_KEYS=new Set(['signal_id','family_id','asset','target','source_sha256','signal_state','source_observed_at_utc','source_first_known_at_utc','issued_at_utc','outcome_due_at_utc','original_outcome_status','original_outcome_receipt','first_known_proof','retrospective_actual_direction']);
const RECEIPT_KEYS=new Set(['signal_id','source_sha256','asset','target','issued_at_utc','outcome_due_at_utc','status','result','substitute_later_price_forbidden','signal_state','recorded_at_utc']);
const PROOF_KEYS=new Set(['status','verifier','proof_sha256']);
function allowedObject(value,keys){return value!==null&&typeof value==='object'&&!Array.isArray(value)&&Object.keys(value).every(key=>keys.has(key));}
function closedPublicSchema(row){
 const strings=['signal_id','family_id','asset','target','source_sha256','signal_state','source_observed_at_utc','source_first_known_at_utc','issued_at_utc','outcome_due_at_utc','original_outcome_status'];
 if(!allowedObject(row,ROW_KEYS)||strings.some(key=>typeof row[key]!=='string'))return false;
 if('retrospective_actual_direction' in row&&!['UP','DOWN','FLAT'].includes(row.retrospective_actual_direction))return false;
 const receipt=row.original_outcome_receipt;
 if(receipt!=null){
   if(!allowedObject(receipt,RECEIPT_KEYS))return false;
   if(['signal_id','source_sha256','asset','target','issued_at_utc','outcome_due_at_utc','status','signal_state','recorded_at_utc'].some(key=>typeof receipt[key]!=='string'))return false;
   if(receipt.result!=null&&!['HIT','MISS','ABSTAINED'].includes(receipt.result))return false;
   if('substitute_later_price_forbidden' in receipt&&typeof receipt.substitute_later_price_forbidden!=='boolean')return false;
 }
 const proof=row.first_known_proof;
 if(proof!=null&&(!allowedObject(proof,PROOF_KEYS)||['status','verifier','proof_sha256'].some(key=>typeof proof[key]!=='string')))return false;
 return true;
}

function containsRestrictedKey(value,seen=new Set()){
 if(value===null||typeof value!=="object")return false;
 if(seen.has(value))return false;
 seen.add(value);
 if(Array.isArray(value))return value.some(item=>containsRestrictedKey(item,seen));
 return Object.entries(value).some(([key,child])=>RESTRICTED_KEY.test(key)||containsRestrictedKey(child,seen));
}

function parseStamp(value) {
 if(typeof value!=="string"||!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?Z$/.test(value))return null;
 const ms=Date.parse(value);if(!Number.isFinite(ms))return null;
 const normalized=new Date(ms).toISOString();
 const original=new Date(ms).toISOString().replace(/\.\d{3}Z$/,"Z");
 const expected=value.replace(/(?:\.000)?Z$/,"Z");
 if(expected.includes(".")&&value.includes(".")&&value.split(".")[1].replace("Z","").length<3){
   const padded=value.replace(/\.(\d{1,2})Z$/,(_m,d)=>"."+d.padEnd(3,"0")+"Z");
   return normalized===padded?ms:null;
 }
 return normalized===value||original===value?ms:null;
}

function inspectRow(row,asOfUtc){
 const fail=(category,reason)=>({signal_id:"REDACTED",family_id:"REDACTED",original_outcome_status:["MATURED","CENSORED","MISSING","PENDING"].includes(row?.original_outcome_status)?row.original_outcome_status:"UNKNOWN",admission:category,reason,registered_scored:false,trade_edge_admitted:false});
 const asOf=parseStamp(asOfUtc);
 if(asOf===null)return fail("QUARANTINED","AS_OF_CLOCK_MISSING_OR_INVALID");
 if(!row||typeof row!=="object"||Array.isArray(row))return fail("QUARANTINED","ROW_SCHEMA_INVALID");
 if(containsRestrictedKey(row))return fail("QUARANTINED","RESTRICTED_RECORD_MUST_NOT_ENTER_PUBLIC_ORACLE");
 if(!closedPublicSchema(row))return fail("QUARANTINED","UNKNOWN_PUBLIC_SCHEMA_FIELD");
 const required=["signal_id","family_id","asset","target","source_sha256","signal_state","source_observed_at_utc","source_first_known_at_utc","issued_at_utc","outcome_due_at_utc","original_outcome_status"];
 if(required.some(k=>typeof row[k]!=="string"||!row[k].trim()))return fail("QUARANTINED","REQUIRED_FIELD_MISSING");
 if(!/^[a-f0-9]{64}$/.test(row.source_sha256))return fail("QUARANTINED","INVALID_SOURCE_SHA256");
 if(!["DIRECTIONAL","ABSTAIN","NO_EDGE"].includes(row.signal_state))return fail("QUARANTINED","UNRECOGNIZED_SIGNAL_STATE");
 if(!["MATURED","CENSORED","MISSING","PENDING"].includes(row.original_outcome_status))return fail("QUARANTINED","UNRECOGNIZED_OUTCOME_STATE");
 const obs=parseStamp(row.source_observed_at_utc),known=parseStamp(row.source_first_known_at_utc),issued=parseStamp(row.issued_at_utc),due=parseStamp(row.outcome_due_at_utc);
 if([obs,known,issued,due].some(x=>x===null)||obs>known||issued>=due||issued>asOf)return fail("QUARANTINED","BAD_OR_OUT_OF_ORDER_ISSUE_OUTCOME_CLOCK");
 const receipt=row.original_outcome_receipt;
 if(row.original_outcome_status==="MATURED"||row.original_outcome_status==="CENSORED"){
   if(!receipt||receipt.signal_id!==row.signal_id||receipt.source_sha256!==row.source_sha256||receipt.asset!==row.asset||receipt.target!==row.target||receipt.issued_at_utc!==row.issued_at_utc||receipt.outcome_due_at_utc!==row.outcome_due_at_utc||receipt.status!==row.original_outcome_status||receipt.signal_state!==row.signal_state)return fail("QUARANTINED","ORIGINAL_RECEIPT_BINDING_CONFLICT");
   const recorded=parseStamp(receipt.recorded_at_utc);
   if(recorded===null||recorded<due||recorded>asOf||due>asOf)return fail("QUARANTINED","OUTCOME_NOT_MATURE_AT_EXPLICIT_AS_OF");
 } else if(receipt!=null)return fail("QUARANTINED","MISSING_OR_PENDING_WITH_ORIGINAL_RECEIPT");
 if(row.original_outcome_status==="CENSORED"&&(receipt?.result!=null||receipt?.substitute_later_price_forbidden!==true))return fail("QUARANTINED","CENSORED_RECEIPT_MUTATED_OR_SUBSTITUTION_ALLOWED");
 if(row.original_outcome_status==="MATURED"&&!["HIT","MISS","ABSTAINED"].includes(receipt?.result))return fail("QUARANTINED","INVALID_ORIGINAL_OUTCOME_RESULT");
 const base={signal_id:"REDACTED",family_id:"REDACTED",original_outcome_status:row.original_outcome_status,registered_scored:false,trade_edge_admitted:false,issued_at_utc:row.issued_at_utc};
 if(known>issued)return {...base,admission:"PIT_BLOCKED",reason:"SOURCE_FIRST_KNOWN_AFTER_FORECAST_ISSUE"};
 if(row.signal_state!=="DIRECTIONAL")return {...base,admission:"NON_DIRECTIONAL_PARTICIPATION",reason:row.signal_state};
 if(row.original_outcome_status==="CENSORED")return {...base,admission:"CENSORED_IMMUTABLE",reason:"NO_RETROACTIVE_MATURATION"};
 if(row.original_outcome_status==="MISSING")return {...base,admission:"MISSING_ORIGINAL_RECEIPT",reason:"UNMATCHED_OUTCOME_NOT_ASSUMED_CENSORED"};
 if(row.original_outcome_status==="PENDING")return {...base,admission:"PENDING_MATURITY",reason:"NOT_YET_MATURED"};
 if(!row.first_known_proof||row.first_known_proof.status!=="INDEPENDENT_VERIFIED"||typeof row.first_known_proof.verifier!=="string"||!row.first_known_proof.verifier.trim()||!row.first_known_proof.proof_sha256||!/^[0-9a-f]{64}$/.test(row.first_known_proof.proof_sha256))
   return {...base,admission:"SOURCE_FIRST_KNOWN_PROOF_PENDING",reason:"DECLARED_CLOCK_IS_NOT_INDEPENDENT_PUBLICATION_PROOF"};
 // A checked metadata flag is only a candidate. Independent auditor must authenticate proof externally.
 return {...base,admission:"EXTERNAL_PIT_ATTESTATION_REQUIRED",reason:"SELF_DECLARED_REVIEW_CANNOT_CERTIFY_SOURCE_FIRST_KNOWABLE"};
}

function auditCohort(rows,asOfUtc){
 if(parseStamp(asOfUtc)===null)throw Error("AS_OF_CLOCK_MISSING_OR_INVALID");
 if(!Array.isArray(rows))throw Error("INPUT_MUST_BE_ARRAY");
 const seen=new Set(),accepted=[],categories={},families=new Map();
 for(const row of rows){
  const id=row?.signal_id;
  if(typeof id!=="string"||!id.trim())throw Error("MISSING_SIGNAL_ID");
  if(seen.has(id))throw Error("DUPLICATE_ORIGINAL_SIGNAL_ID");
  seen.add(id);
  const result=inspectRow(row,asOfUtc);
  // Output only cohort-local opaque labels. No supplied identifier, including
  // a wallet or credential disguised as a valid string, enters public logs.
  result.signal_id=`ROW_${accepted.length+1}`;
  if(result.admission!=="QUARANTINED"){
    if(!families.has(row.family_id))families.set(row.family_id,`FAMILY_${families.size+1}`);
    result.family_id=families.get(row.family_id);
  }
  accepted.push(result);
  categories[result.admission]=(categories[result.admission]||0)+1;
 }
 const uniqueFamilies=new Set(families.values());
 return {contract:"TASK2_R1_CAUSAL_SOURCE_ADMISSION_PREFLIGHT_v1",research_only:true,evaluation_as_of_utc:asOfUtc,attempted_original_signal_rows:rows.length,retained_rows:accepted.length,declared_family_identifiers:uniqueFamilies.size,verified_independent_market_families:null,admission_counts:categories,registered_directional_skill_rows_admitted:0,portfolio_execution_rows_admitted:0,original_censor_rewrites:0,source_first_known_certification:"REQUIRES_INDEPENDENT_EXTERNAL_ATTESTATION",model_promotion_allowed:false,trade_execution_allowed:false,rows:accepted};
}

function selfTest(){
 const asOfUtc="2026-10-13T00:00:00Z";
 const base={signal_id:"S1",family_id:"F1",asset:"BTC",target:"UP_4H",source_sha256:"a".repeat(64),signal_state:"DIRECTIONAL",source_observed_at_utc:"2026-10-12T09:00:00Z",source_first_known_at_utc:"2026-10-12T09:02:00Z",issued_at_utc:"2026-10-12T09:05:00Z",outcome_due_at_utc:"2026-10-12T13:00:00Z",original_outcome_status:"MATURED"};
 base.original_outcome_receipt={signal_id:base.signal_id,source_sha256:base.source_sha256,asset:base.asset,target:base.target,issued_at_utc:base.issued_at_utc,outcome_due_at_utc:base.outcome_due_at_utc,status:"MATURED",result:"HIT",signal_state:base.signal_state,recorded_at_utc:"2026-10-12T13:05:00Z"};
 const caseRows=[
 ["VALID_METADATA_ONLY",base,"SOURCE_FIRST_KNOWN_PROOF_PENDING"],
 ["FAKE_SELF_ATTESTATION",{...base,first_known_proof:{status:"INDEPENDENT_VERIFIED",verifier:"fixture",proof_sha256:"b".repeat(64)}},"EXTERNAL_PIT_ATTESTATION_REQUIRED"],
 ["FUTURE_FIRST_KNOWN",{...base,source_first_known_at_utc:"2026-10-12T09:07:00Z"},"PIT_BLOCKED"],
 ["NON_EXISTENT_CLOCK",{...base,issued_at_utc:"2026-02-30T09:00:00Z"},"QUARANTINED"],
 ["AFTER_MATURITY_ISSUANCE",{...base,issued_at_utc:"2026-10-12T13:00:00Z"},"QUARANTINED"],
 ["BAD_SOURCE_HASH",{...base,source_sha256:"bad"},"QUARANTINED"],
 ["BAD_ORIGINAL_RESULT",{...base,original_outcome_receipt:{...base.original_outcome_receipt,result:"WIN"}},"QUARANTINED"],
 ["WRONG_OUTCOME_OWNER",{...base,original_outcome_receipt:{...base.original_outcome_receipt,signal_id:"S2"}},"QUARANTINED"],
 ["WRONG_DUE_CLOCK",{...base,original_outcome_receipt:{...base.original_outcome_receipt,outcome_due_at_utc:"2026-10-12T15:00:00Z"}},"QUARANTINED"],
 ["BACKDATED_ISSUANCE",{...base,issued_at_utc:"2026-10-12T09:03:00Z"},"QUARANTINED"],
 ["CENSOR_PRESERVED",{...base,original_outcome_status:"CENSORED",original_outcome_receipt:{...base.original_outcome_receipt,status:"CENSORED",result:null,substitute_later_price_forbidden:true},retrospective_actual_direction:"UP"},"CENSORED_IMMUTABLE"],
 ["CENSOR_RETROSCORED_ILLEGAL",{...base,original_outcome_status:"CENSORED",original_outcome_receipt:{...base.original_outcome_receipt,status:"CENSORED",result:"HIT",substitute_later_price_forbidden:true}},"QUARANTINED"],
 ["NO_EDGE_NOT_WIN",{...base,signal_state:"NO_EDGE",original_outcome_receipt:{...base.original_outcome_receipt,signal_state:"NO_EDGE",result:"ABSTAINED"}},"NON_DIRECTIONAL_PARTICIPATION"],
 ["ABSTAIN_NOT_WIN",{...base,signal_state:"ABSTAIN",original_outcome_receipt:{...base.original_outcome_receipt,signal_state:"ABSTAIN",result:"ABSTAINED"}},"NON_DIRECTIONAL_PARTICIPATION"],
 ["MISSING_OWNER_OUTCOME",{...base,original_outcome_status:"MISSING",original_outcome_receipt:null,retrospective_actual_direction:"UP"},"MISSING_ORIGINAL_RECEIPT"],
 ["MISSING_CONFLICT",{...base,original_outcome_status:"MISSING"},"QUARANTINED"],
 ["PENDING",{...base,original_outcome_status:"PENDING",original_outcome_receipt:null},"PENDING_MATURITY"],
 ["RESTRICTED_WALLET_FIELD",{...base,user_wallet:"0xFAKE"},"QUARANTINED"],
 ["NESTED_RESTRICTED_PRIVATE_KEY",{...base,metadata:{private_key:"fixture-only"}},"QUARANTINED"],
 ["ARRAY_NESTED_RESTRICTED_WALLET",{...base,metadata:[{wallet:"0xFAKE"}]},"QUARANTINED"],
 ["NESTED_ACCESS_TOKEN",{...base,metadata:{access_token:"fixture-only"}},"QUARANTINED"],
 ["TOP_LEVEL_PASSWORD",{...base,password:"fixture-only"},"QUARANTINED"],
 ["RECEIPT_CLIENT_SECRET",{...base,original_outcome_receipt:{...base.original_outcome_receipt,client_secret:"fixture-only"}},"QUARANTINED"],
 ["UNKNOWN_METADATA_DENIED",{...base,metadata:{novel_field:"fixture-only"}},"QUARANTINED"],
 ["ALLOWED_DIRECTION_NESTED_TOKEN_DENIED",{...base,original_outcome_status:"MISSING",original_outcome_receipt:null,retrospective_actual_direction:{bearerToken:"fixture-only"}},"QUARANTINED"],
 ["RECEIPT_RESULT_CONTAINER_DENIED",{...base,original_outcome_receipt:{...base.original_outcome_receipt,result:{unexpected:"fixture-only"}}},"QUARANTINED"],
 ["PROOF_VERIFIER_CONTAINER_DENIED",{...base,first_known_proof:{status:"INDEPENDENT_VERIFIED",verifier:{unexpected:"fixture-only"},proof_sha256:"b".repeat(64)}},"QUARANTINED"],
 ["WRONG_SOURCE_AFTER_ISSUE",{...base,source_observed_at_utc:"2026-10-12T09:08:00Z",source_first_known_at_utc:"2026-10-12T09:09:00Z"},"PIT_BLOCKED"],
 ["FUTURE_MATURED", {...base,outcome_due_at_utc:"2026-10-14T13:00:00Z",original_outcome_receipt:{...base.original_outcome_receipt,outcome_due_at_utc:"2026-10-14T13:00:00Z",recorded_at_utc:"2026-10-14T13:05:00Z"}}, "QUARANTINED"],
 ["RECEIPT_BEFORE_DUE",{...base,original_outcome_receipt:{...base.original_outcome_receipt,recorded_at_utc:"2026-10-12T12:59:00Z"}},"QUARANTINED"],
 ["NO_EDGE_RETRO_PROMOTION",{...base,original_outcome_receipt:{...base.original_outcome_receipt,signal_state:"NO_EDGE",result:"ABSTAINED"}},"QUARANTINED"],
 ["UNKNOWN_SIGNAL",{...base,signal_state:"FUTURE_CLAIM"},"QUARANTINED"],
 ];
 let checks=0;
 for(const [name,data,expected] of caseRows){const a=inspectRow(data,asOfUtc);if(a.admission!==expected)throw Error(`${name}: expected ${expected}, got ${a.admission} (${a.reason})`);checks++;}
 const separate=auditCohort([base,{...base,signal_id:"S2",family_id:"F1",original_outcome_receipt:{...base.original_outcome_receipt,signal_id:"S2"}}],asOfUtc);
 if(separate.attempted_original_signal_rows!==2||separate.declared_family_identifiers!==1||separate.registered_directional_skill_rows_admitted!==0)throw Error("dependent pair must not create two independent edge trials");
 checks++;
 let duplicate=false;try{auditCohort([base,base],asOfUtc)}catch(e){duplicate=String(e).includes("DUPLICATE_ORIGINAL_SIGNAL_ID");}
 if(!duplicate)throw Error("duplicate original IDs not rejected");checks++;
 const sensitive="0x"+"ab".repeat(20);
 const privateId={...base,signal_id:sensitive,family_id:sensitive,original_outcome_receipt:{...base.original_outcome_receipt,signal_id:sensitive}};
 if(JSON.stringify(auditCohort([privateId],asOfUtc)).includes(sensitive))throw Error("identifier echoed in public result");checks++;
 if(JSON.stringify(inspectRow({...privateId,password:"fixture"},asOfUtc)).includes(sensitive))throw Error("quarantined identifier echoed");checks++;
 if(JSON.stringify(inspectRow({...base,original_outcome_status:sensitive},asOfUtc)).includes(sensitive))throw Error("invalid status echoed");checks++;
 if(inspectRow(base).reason!=="AS_OF_CLOCK_MISSING_OR_INVALID")throw Error("missing evaluation clock admitted");checks++;
 return {status:"SELF_TEST_PASS",negative_and_positive_controls:checks,synthetic_examples_only:true,historical_market_rows_scored:0,automatic_trading_authority:false};
}

const args=process.argv.slice(2);
if(args.length===1&&args[0]==='--self-test'){
 console.log(JSON.stringify(selfTest(),null,2));
}else if(args.length===4&&args[0]==='--input'&&args[2]==='--as-of'){
 try {
  const x=JSON.parse(fs.readFileSync(args[1],'utf8'));
  console.log(JSON.stringify(auditCohort(x,args[3]),null,2));
 } catch {
  console.error('INPUT_REJECTED_NO_RAW_DETAILS');
  process.exitCode=1;
 }
}else {
 console.error('Usage: node task2_r1_no_hindsight_admission_oracle_v1.mjs --self-test | --input path-to-JSON-array --as-of UTC-ISO-TIMESTAMP');
 process.exitCode=2;
}

