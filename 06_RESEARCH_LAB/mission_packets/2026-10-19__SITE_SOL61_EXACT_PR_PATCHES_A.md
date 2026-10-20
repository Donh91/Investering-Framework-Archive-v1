# FROZEN GITHUB PR REVIEW SOURCE: #1683
Exact SHA: ac0002837d304631f42fa44e3255a73b83004d52
Base at capture: eeb298aba14d3d0763aef674ca61113a6eb0bfa1
Draft: true
CI: Master Monday Preflight Gate=success | Daily Capture Architecture Gate=success | Data Architecture Gate=success | Full Architecture 1-7 Gate=success | Storage Health Gate=success | Shadow Admission AI Decider=success | Cycle Navigator Public Contract Gate=success | Cycle Navigator Public Product Gate=success | Compass Event Refresh=success | Automation Production Health Gate=success | Experiment Lifecycle Gate=success | Official Daily Compass=success
COMPLETE changed-file list: .github/workflows/weekly-api-calibration-shadow.yml; 05_CYCLE_NAVIGATOR/site/build-public.mjs; 05_CYCLE_NAVIGATOR/site/market-compass-premium.js; 05_CYCLE_NAVIGATOR/site/tests/full-stack-readback.test.mjs; research/master_monday_preflight/2026-10-19__COMPASS_FULL_STACK_PARITY_AND_NONREGRESSION_ADDENDUM.md; research/master_monday_preflight/2026-10-19__SITE_TRUTH_FIRST_INDEPENDENT_DESIGN_AUDIT.md; research/master_monday_preflight/2026-10-19__SIX_REPOSITORY_PROVENANCE_AND_SITE_TRUST_AUDIT.md; research/master_monday_preflight/2026-10-19__SOL_6_1_WEEKLY_INTELLIGENCE_SITE_COMPASS_EXECUTION_MISSION.md; research/master_monday_preflight/2026-10-19__weekly-intelligence-audit-and-contract-gap-review.md; scripts/master_monday/publish_master_monday_outputs.py; tests/master_monday/test_durable_repairs.py
Research input only. This is a GitHub patch excerpt, not full surrounding code. Omitted/unreadable code is UNKNOWN. Do not infer runtime execution.

### .github/workflows/weekly-api-calibration-shadow.yml (patch_chars=1293, included=1293)
```diff
@@ -265,7 +265,9 @@ jobs:
           import hashlib,json,subprocess
           from pathlib import Path
           out=Path(Path('runtime/publish_output_dir.txt').read_text().strip())
-          paths=[out/'MASTER_MONDAY_MACHINE_PACKAGE.json',out/'MASTER_MONDAY_REPORT.md',out/'MASTER_MONDAY_CALIBRATION_SCORECARD.json',out/'MASTER_MONDAY_OPERATIONAL_TRANSLATION.json',out/'MASTER_MONDAY_DELIVERY_POINTER.json',Path('research/api_agent/outputs/weekly/LATEST_MASTER_MONDAY_DELIVERY_POINTER.json')]
+          pointer_bytes=(out/'MASTER_MONDAY_DELIVERY_POINTER.json').read_bytes()
+          audit=out/f"MASTER_MONDAY_WEEKLY_INTELLIGENCE_AUDIT_{hashlib.sha256(pointer_bytes).hexdigest()[:16]}.md"
+          paths=[out/'MASTER_MONDAY_MACHINE_PACKAGE.json',out/'MASTER_MONDAY_REPORT.md',out/'MASTER_MONDAY_CALIBRATION_SCORECARD.json',out/'MASTER_MONDAY_OPERATIONAL_TRANSLATION.json',out/'MASTER_MONDAY_DELIVERY_POINTER.json',audit,Path('research/api_agent/outputs/weekly/LATEST_MASTER_MONDAY_DELIVERY_POINTER.json')]
           rows=[]
           for p in paths:
               path=str(p);blob=subprocess.run(['git','rev-parse',f'HEAD:{path}'],capture_output=True,text=True,check=True).stdout.strip();rows.append({'path':path,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'blob_sha':blob})
```

### 05_CYCLE_NAVIGATOR/site/build-public.mjs (patch_chars=6043, included=6043)
```diff
@@ -269,9 +269,60 @@ async function buildFullStackReadback(compass,weeklyPointer,weeklyPackage){
       Number(weeklyPointer?.issue_number)===Number(weeklyPackage?.issue_number));
   }catch{}
   const mp=master?.pointer;
+  // A pointer digest proves only pointer bytes. Never call the weekly source
+  // aligned unless its referenced immutable machine package is also readable
+  // and matches the exact producer-declared SHA-256.
+  let masterTargetVerified=false,masterMachine=null;
+  try{
+    const p=verifiedRelative(mp?.machine_package_path,"research/api_agent/outputs/weekly/");
+    const expected=mp?.machine_package_sha256;
+    if(p&&typeof expected==="string"&&/^[0-9a-f]{64}$/.test(expected)){
+      // This producer pointer declares the canonical self-digest of the
+      // machine package, NOT the SHA-256 of the entire JSON file bytes.
+      const raw=await readFile(p,"utf8");
+      const target=JSON.parse(raw);
+      masterTargetVerified=target?.contract==="MASTER_MONDAY_MACHINE_PACKAGE_v1"&&
+        Number(target?.iso_year)===Number(mp?.iso_year)&&
+        Number(target?.iso_week)===Number(mp?.iso_week)&&
+        // A valid package from the right week but a different evidence freeze
+        // must not be promoted to the current Monday baseline.
+        typeof mp?.freeze_sha256==="string"&&/^[0-9a-f]{64}$/.test(mp.freeze_sha256)&&
+        target?.freeze_sha256===mp.freeze_sha256&&
+        verifiedRawDigest(raw,target,"package_sha256",expected);
+      if(masterTargetVerified)masterMachine=target;
+    }
+  }catch{}
   const masterAligned=Boolean(mp?.contract==="MASTER_MONDAY_DELIVERY_POINTER_v1"&&mp?.status==="READY"&&
     mp?.iso_week===weeklyPointer?.completed_source_week&&mp?.iso_year===weeklyPointer?.completed_source_year&&
-    master.digest===weeklyPointer?.master_monday_pointer_sha256);
+    master.digest===weeklyPointer?.master_monday_pointer_sha256&&masterTargetVerified);
+  // Source alignment, analytical completeness, and decision authority are
+  // independent. A successful API delivery does not fill absent scorecard or
+  // operational translation fields. Never copy raw API prose to public SITE.
+  const mondayStatus=v=>typeof v==="string"&&/^[A-Z0-9_]{1,80}$/.test(v)?v:"UNAVAILABLE";
+  const scoreStatus=masterAligned?mondayStatus(mp?.scorecard_status):"UNVERIFIED";
+  const translationStatus=masterAligned?mondayStatus(mp?.operational_translation_status):"UNVERIFIED";
+  const apiAnalysisAvailable=masterAligned&&masterMachine?.api_status==="success"&&
+    (typeof masterMachine?.analysis==="string"&&masterMachine.analysis.trim().length>0 ||
+     masterMachine?.analysis&&typeof masterMachine.analysis==="object"&&
+     !String(masterMachine.analysis.status||"").startsWith("UNAVAILABLE"));
+  const analyticalStatuses=new Set(["READY","PASS","AVAILABLE","COMPLETE","SCORED"]);
+  const statusConflict=masterAligned&&(
+    scoreStatus!==mondayStatus(masterMachine?.scorecard?.status)||
+    translationStatus!==mondayStatus(masterMachine?.operational_translation?.status));
+  const mondayAnalytics=masterAligned?
+    (statusConflict?"CONFLICTING_ANALYTICS":
+     apiAnalysisAvailable&&analyticalStatuses.has(scoreStatus)&&analyticalStatuses.has(translationStatus)?"COMPLETE":"PARTIAL_ANALYTICS"):
+    "UNVERIFIED";
+  const mondayPublic=masterAligned?{
+    contract:"PUBLIC_MASTER_MONDAY_WEEKLY_CONTEXT_READBACK_v1",
+    completed_week:`${mp.iso_year}-W${String(mp.iso_week).padStart(2,"0")}`,
+    status:"SOURCE_ALIGNED",analytics_status:mondayAnalytics,
+    api_analysis_status:apiAnalysisAvailable?"AVAILABLE_SHADOW_ONLY":"UNAVAILABLE",
+    scorecard_status:scoreStatus,operational_translation_status:translationStatus,
+    // Source hashes remain internal verification inputs; SITE_CONTRACT forbids
+    // publishing machine hashes or internal paths in the public projection.
+    authority:"WEEKLY_CONTEXT_ONLY_NO_CURRENT_ACTION"
+  }:{contract:"PUBLIC_MASTER_MONDAY_WEEKLY_CONTEXT_READBACK_v1",status:"UNVERIFIED",analytics_status:"UNVERIFIED",authority:"WEEKLY_CONTEXT_ONLY_NO_CURRENT_ACTION"};
   let shadow=null,shadowAligned=false;
   try{
     if(shadowPtr?.contract==="SHADOW_COMPASS_V2_LATEST_POINTER_v1"){
@@ -353,7 +404,7 @@ async function buildFullStackReadback(compass,weeklyPointer,weeklyPackage){
     }
   }catch{}
   const officialValid=officialValidated&&compass?.data_status==="OK"&&official?.compass_id===compass?.compass_id;
-  const quality=officialValid&&nativeAligned&&shadow?.status==="ALIGNED_RESEARCH"&&masterAligned&&strategic&&weeklyAligned?"COMPLETE":"PARTIAL_OR_DEGRADED";
+  const quality=officialValid&&nativeAligned&&shadow?.status==="ALIGNED_RESEARCH"&&masterAligned&&mondayAnalytics==="COMPLETE"&&strategic&&weeklyAligned?"COMPLETE":"PARTIAL_OR_DEGRADED";
   return {
     contract:"PUBLIC_COMPASS_FULL_STACK_READBACK_v1",
     status:quality,
@@ -365,11 +416,13 @@ async function buildFullStackReadback(compass,weeklyPointer,weeklyPackage){
       shadow:shadow?.status||"UNVERIFIED",
       strategic:strategic?.status||"UNVERIFIED",
       master_monday:masterAligned?"SOURCE_ALIGNED":"UNVERIFIED",
+      master_monday_analysis:mondayAnalytics,
       cycle_navigator:weeklyAligned?"WEEKLY_POINTER_ALIGNED":"UNVERIFIED"
     },
     official_freshness:officialValid?officialFreshness:{status:"UNAVAILABLE"},
     official_action:officialValid?compass.action_now:"UNAVAILABLE",
     official_data_status:String(compass?.data_status||"NOT_PUBLISHED"),
+    master_monday:mondayPublic,
     native:nativeValidated?{now:researchEnum(nativeTarget.action.NOW,["HOLD_WAIT","PREPARE","BUY","HOLD","UNAVAILABLE"]),data_health:nativeTarget.DATA_HEALTH||"UNAVAILABLE",checked_at_utc:nativeTarget.generated_at_utc,official_source_aligned:nativeAligned}:{now:"UNAVAILABLE",data_health:"UNVERIFIED",official_source_aligned:false},
     shadow:shadow||{status:"UNVERIFIED",authority:"RESEARCH_ONLY_NO_ACTION_PERMISSION",horizons:{}},
     strategic:strategic||{status:"UNVERIFIED",authority:"CYCLE_NAVIGATOR_ONLY"},
```

### 05_CYCLE_NAVIGATOR/site/market-compass-premium.js (patch_chars=2154, included=2154)
```diff
@@ -365,12 +365,17 @@ function compositeIntel(compass, readingState='UNAVAILABLE'){
  stale?'A previous model outlook exists, but its market observations are stale. No fresh directional model edge is claimed.':
  'An independent current model direction has not been verified.';
  const lanes=[['12H',d('12h')],['1–3D',d('1_3d')],['5–7D',d('5_7d')],['2–3W',f.weekly?.direction_2_3w||'UNAVAILABLE'],['21–30D',st.horizon_21_30d?.direction||'UNAVAILABLE'],['4–8W',st.horizon_4_8w?.direction||'UNAVAILABLE']];
+ const monday=f.master_monday||{};
+ const mondayReading=monday.status==='SOURCE_ALIGNED'
+   ?String(monday.completed_week||'UNKNOWN')+' · '+(monday.analytics_status==='COMPLETE'?'ANALYSIS COMPLETE':monday.analytics_status==='CONFLICTING_ANALYTICS'?'ANALYTICAL SOURCE CONFLICT':'ANALYSIS PARTIAL')
+   :'SOURCE UNVERIFIED';
  return '<section class="compass-synthesis" data-contract="PUBLIC_COMPASS_FULL_STACK_READBACK_v1" aria-label="Combined Compass intelligence">'
  +'<div class="synthesis-head"><div><span>COMBINED COMPASS INTELLIGENCE</span><strong>Official actions + independent model research</strong></div><small>'+esc(f.status==='COMPLETE'?'SOURCE-ALIGNED':'PARTIAL EVIDENCE')+'</small></div>'
  +'<div class="synthesis-proof"><div><span>OFFICIAL ACTION</span><strong>'+esc(verified?recommendation(compass.action_now).action:'UNAVAILABLE · NOT CURRENT')+'</strong></div>'
  +'<div><span>RESEARCH PERSPECTIVE</span><strong>'+esc(current?'Source-aligned model view':stale?'Stale model observation':'Not verified')+'</strong></div></div>'
  +'<div class="synthesis-horizons">'+lanes.map(([label,value])=>'<div><span>'+esc(label)+'</span><strong>'+esc(publicState(value))+'</strong></div>').join('')+'</div>'
  +'<p class="synthesis-analysis">'+esc(analysis)+'</p>'
+ +'<small class="synthesis-boundary">MONDAY BASELINE · '+esc(mondayReading)+' · Frozen weekly context, not a current action.</small>'
  +'<small class="synthesis-boundary">Research direction is not a BUY / SELL instruction. Approved action and market-cycle phase remain governed by the official signals.</small></section>';
 }
 function refreshStatusBanner(compass, event) {
```

### scripts/master_monday/publish_master_monday_outputs.py (patch_chars=10933, included=7800)
```diff
@@ -1,5 +1,5 @@
 from __future__ import annotations
-import argparse, hashlib, json, subprocess, sys
+import argparse, hashlib, json, re, subprocess, sys
 from datetime import datetime, timezone
 from pathlib import Path
 from typing import Any
@@ -98,6 +98,106 @@ def fallback_scorecard(context:dict[str,Any])->dict[str,Any]:
         'matured_outcome_count':len(matured),
         'reason':'WEEKLY_CALIBRATION_SHADOW validated output contract does not currently include a scorecard field.' if matured else 'A valid experiment registry supplied zero newly matured outcomes; formal outcome scoring remains pending.',
     }
+def build_weekly_intelligence_audit(machine:dict[str,Any],pointer:dict[str,Any],
+                                    machine_file_sha256:str,pointer_file_sha256:str,
+                                    freeze:dict[str,Any]|None=None,preflight:dict[str,Any]|None=None)->str:
+    """Compact derived evidence index; NEVER a new market or scientific authority.
+
+    Master Monday runs before CN/SITE final publication. Downstream states
+    therefore remain PENDING_DOWNSTREAM instead of falsely claiming success.
+    Only allowlisted metadata is copied; API analysis and restricted payloads
+    are deliberately excluded.
+    """
+    def safe_status(value:Any)->str:
+        s=str(value or 'UNAVAILABLE').upper()
+        return s if re.fullmatch(r'[A-Z0-9_:-]{1,96}',s) else 'UNAVAILABLE'
+    def safe_sha(value:Any)->str|None:
+        return value if isinstance(value,str) and re.fullmatch(r'[0-9a-f]{64}',value) else None
+    year=int(machine['iso_year']);week=int(machine['iso_week'])
+    if year<2000 or year>9999:
+        raise ValueError('weekly_audit_invalid_iso_week')
+    try:
+        datetime.fromisocalendar(year,week,1)
+    except ValueError as exc:
+        raise ValueError('weekly_audit_invalid_iso_week') from exc
+    if year!=int(pointer['iso_year']) or week!=int(pointer['iso_week']):
+        raise ValueError('weekly_audit_pointer_week_mismatch')
+    digest=safe_sha(machine.get('package_sha256'))
+    if digest is None or digest!=safe_sha(pointer.get('machine_package_sha256')):
+        raise ValueError('weekly_audit_machine_digest_mismatch')
+    if not safe_sha(machine_file_sha256) or not safe_sha(pointer_file_sha256):
+        raise ValueError('weekly_audit_file_hash_invalid')
+    receipt=machine.get('api_receipt') if isinstance(machine.get('api_receipt'),dict) else {}
+    model=str(receipt.get('model') or 'UNAVAILABLE')
+    model=model if re.fullmatch(r'[a-zA-Z0-9_.-]{1,80}',model) else 'UNAVAILABLE'
+    cost=receipt.get('estimated_cost_usd')
+    cost=round(float(cost),6) if isinstance(cost,(int,float)) and not isinstance(cost,bool) and 0<=cost<=1000 else None
+    learning=machine.get('learning_decision_impact') if isinstance(machine.get('learning_decision_impact'),dict) else {}
+    scorecard=machine.get('scorecard') if isinstance(machine.get('scorecard'),dict) else {}
+    freeze=freeze if isinstance(freeze,dict) else {}
+    preflight=preflight if isinstance(preflight,dict) else {}
+    meta=preflight.get('meta') if isinstance(preflight.get('meta'),dict) else {}
+    quality=preflight.get('quality') if isinstance(preflight.get('quality'),dict) else {}
+    def safe_count(value:Any)->int|None:
+        return value if type(value) is int and 0<=value<=10000000 else None
+    index={
+        'contract':'MASTER_MONDAY_WEEKLY_INTELLIGENCE_AUDIT_v1',
+        'authority':'DERIVED_EVIDENCE_INDEX_ONLY_NO_NEW_FORECAST_OR_ACTION',
+        'completed_week':f'{year}-W{week:02d}',
+        'source_provenance':{
+            'freeze_self_sha256':safe_sha(machine.get('freeze_sha256')),
+            'preflight_self_sha256':safe_sha(machine.get('preflight_sha256')),
+            'context_sha256':safe_sha(machine.get('context_hash')),
+            'machine_self_sha256':digest,
+            'machine_file_sha256':machine_file_sha256,
+            'delivery_pointer_file_sha256':pointer_file_sha256,
+            'settled_week_close_sha256':safe_sha((freeze.get('final_week_close') or {}).get('package_sha256')) if isinstance(freeze.get('final_week_close'),dict) else None,
+            'weekly_capture_bridge_sha256':safe_sha((freeze.get('weekly_capture_bridge') or {}).get('sha256')) if isinstance(freeze.get('weekly_capture_bridge'),dict) else None,
+        },
+        'delivery':{
+            'preflight':safe_status(pointer.get('preflight_status')),
+            'api':safe_status(machine.get('api_status')),
+            'producer':safe_status(pointer.get('producer_status')),
+            'consumer':safe_status(pointer.get('consumer_receipt_status')),
+            'consumer_state':safe_status(pointer.get('consumer_receipt_state')),
+            'overall':safe_status(pointer.get('status')),
+        },
+        'analysis_completeness':{
+            'scorecard':safe_status(pointer.get('scorecard_status')),
+            'operational_translation':safe_status(pointer.get('operational_translation_status')),
+            'learning_decision_impact':safe_status(learning.get('assessment_status')),
+            'experiment_learning':safe_status(pointer.get('experiment_learning_status')),
+        },
+        'evidence_quality':{
+            'blocking_gap_count':safe_count(meta.get('blocking_gap_count')),
+            'confidence_reducing_gap_count':safe_count(meta.get('confidence_reducing_gap_count')),
+            'planned_core_actions':safe_count(meta.get('planned_core_actions')),
+            'core_pass':safe_count(quality.get('PASS')),
+            'core_partial':safe_count(quality.get('PARTIAL')),
+            'core_unavailable':safe_count(quality.get('UNAVAILABLE')),
+        },
+        'outcome_and_learning':{
+            'registry_matured_count_not_scored_or_admitted':safe_count(scorecard.get('matured_outcome_count')),
+            'baseline_semantic_identity_count':safe_count(learning.get('baseline_semantic_identity_count')),
+            'learning_semantic_identity_count':safe_count(learning.get('learning_semantic_identity_count')),
+            'changed_calibration_decision':learning.get('changed_calibration_decision') if type(learning.get('changed_calibration_decision')) is bool else None,
+            'forecast_skill':'UNPROVEN_NOT_INFERRED',
+        },
+        'api_accounting':{'model':model,'estimated_cost_usd':cost},
+        'downstream_not_yet_claimed':{
+            'cycle_navigator':'PENDING_DOWNSTREAM_OWNER',
+            'site':'PENDING_DOWNSTREAM_OWNER',
+            'official_compass':'SEPARATE_CURRENT_ACTION_OWNER',
+        },
+        'scientific_firewall':'FORECAST_SKILL_NOT_INFERRED_FROM_WEEKLY_SCORE_OR_MATURED_COUNT',
+        'restricted_payloads_included':False,
+    }
+    return '# MASTER MONDAY WEEKLY INTELLIGENCE AUDIT — '+index['completed_week']+'\n\n'+(
+        'Derived metadata only. Original immutable producer files and downstream '
+        'consumer receipts remain authoritative.\n\n```json\n'+
+        json.dumps(index,sort_keys=True,ensure_ascii=False,indent=2)+'\n```\n')
+
+
 def main():
     ap=argparse.ArgumentParser();ap.add_argument('--freeze',type=Path,required=True);ap.add_argument('--preflight',type=Path,required=True);ap.add_argument('--context',type=Path,required=True);ap.add_argument('--api-output',type=Path);ap.add_argument('--api-receipt',type=Path);ap.add_argument('--api-status',required=True);ap.add_argument('--output-dir',type=Path,required=True);ap.add_argument('--learning-packet',type=Path,default=Path('research/framework_learning/LATEST_MASTER_MONDAY_LEARNING_PACKET.json'));a=ap.parse_args()
     freeze=load(a.freeze);preflight=load(a.preflight);context=load(a.context);api=load(a.api_output) if a.api_output and a.api_output.exists() else {};receipt=load(a.api_receipt) if a.
[TRUNCATED 3133 chars - no claim of full coverage]
```