from __future__ import annotations
import argparse, hashlib, json, math, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def load(p:Path):return json.loads(p.read_text())
def canon(v:Any)->bytes:return (json.dumps(v,sort_keys=True,separators=(',',':'))+'\n').encode()
def sha(v:Any)->str:return hashlib.sha256(canon(v)).hexdigest()
def parse_time(value:Any):
    if isinstance(value,(int,float)):
        try:return datetime.fromtimestamp(value,timezone.utc)
        except Exception:return None
    if isinstance(value,str):
        try:
            dt=datetime.fromisoformat(value.replace('Z','+00:00'))
            return (dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)
        except Exception:return None
    return None
def semantic_identities(value:Any)->set[str]:
    result:set[str]=set()
    if isinstance(value,dict):
        for key,item in value.items():
            if key=='semantic_identity' and isinstance(item,str) and item:result.add(item)
            else:result.update(semantic_identities(item))
    elif isinstance(value,list):
        for item in value:result.update(semantic_identities(item))
    return result
def build_learning_decision_impact(context:dict[str,Any],learning:dict[str,Any]|None,receipt:dict[str,Any],iso_year:int,iso_week:int)->dict[str,Any]:
    base={
        'contract':'LEARNING_DECISION_IMPACT_v1',
        'authority':'SHADOW_MEASUREMENT_ONLY',
        'iso_year':iso_year,
        'iso_week':iso_week,
        'evaluation_horizon_weeks':8,
        'learning_input_present':False,
        'changed_calibration_decision':None,
        'exact_input_responsible':[],
        'potential_incremental_inputs':[],
        'automatic_deletion':False,
        'retirement_review_rule':'After 8 evaluable weekly observations, eight FALSE decisions with zero novel unconsumed inputs triggers retirement/merge review; missing consumption or NOT_EVALUABLE never counts as proof of zero value.',
    }
    if not isinstance(learning,dict) or learning.get('contract')!='MASTER_MONDAY_LEARNING_PACKET_v1':
        return {**base,'assessment_status':'NO_VALID_LEARNING_INPUT','reason':'No valid MASTER_MONDAY_LEARNING_PACKET_v1 was available.'}
    base['learning_input_present']=True
    base['learning_packet_generated_at_utc']=learning.get('generated_at_utc')
    base['learning_packet_sha256']=sha(learning)
    decision_time=parse_time(receipt.get('created_unix'))
    learning_time=parse_time(learning.get('generated_at_utc'))
    if decision_time is not None and learning_time is not None and learning_time>decision_time:
        return {**base,'assessment_status':'NOT_EVALUABLE_LATE_PACKET','reason':'Learning packet was generated after the frozen calibration API decision and is excluded prospectively.'}
    baseline_ids=semantic_identities(context)
    learning_ids=semantic_identities(learning)
    novel=sorted(learning_ids-baseline_ids)
    structured=[]
    for key in ('contradictions','method_improvement_candidates','strengthened','weakened'):
        rows=learning.get(key)
        if isinstance(rows,list) and rows:structured.append(key)
    potential=novel+[f'NONEMPTY:{key}' for key in structured]
    base['baseline_semantic_identity_count']=len(baseline_ids)
    base['learning_semantic_identity_count']=len(learning_ids)
    base['potential_incremental_inputs']=potential
    base['learning_live_consumption_allowed']=learning.get('live_consumption_allowed') is True
    if not potential:
        return {**base,'assessment_status':'EVALUABLE_NO_INCREMENTAL_INPUT','changed_calibration_decision':False,'reason':'The advisory packet added no novel semantic identities or decision-relevant structured deltas beyond the frozen baseline context.'}
    return {**base,'assessment_status':'NOT_EVALUABLE_NOVEL_INPUT_NOT_CONSUMED','reason':'Novel advisory input existed, but the packet is advisory-only and was not allowed to alter the frozen baseline calibration. Fix/authorize the consumer edge before attributing decision impact.'}
def experiment_outcome_scorecard(context:dict[str,Any], learning:dict[str,Any])->dict[str,Any]|None:
    """Aggregate the original outcome owner's admitted rows, not new forecasts.

    These are context-bound descriptive record counts, not independently
    sampled performance, paired baseline skill or the full historical MM score.
    The original context builder verifies each forecast and evidence binding.
    No return values, source paths, raw provider data or action fields escape.
    """
    try:
        if (context.get('contract')!='WEEKLY_API_CALIBRATION_CONTEXT_v6'
                or context.get('authority')!='SHADOW_ONLY'
                or sha({k:v for k,v in context.items() if k!='context_hash'})!=context.get('context_hash')
                or context.get('experiment_learning')!=learning
                or learning.get('status')!='AVAILABLE'
                or learning.get('authority')!='SHADOW_ONLY_NO_AUTOMATIC_PROMOTION'
                or learning.get('matured_outcome_evidence_available') is not True
                or learning.get('outcome_ingestion_status')!='COMPLETE'
                or learning.get('outcome_ingestion_diagnostics')!=[]):
            return None
        is_hash=lambda v:isinstance(v,str) and re.fullmatch(r'[a-f0-9]{64}',v) is not None
        if not is_hash(learning.get('registry_sha256')) or not is_hash(context.get('freeze_sha256')):
            return None
        def clock(v):
            return parse_time(v) if isinstance(v,str) and v.endswith('Z') else None
        start,end=clock(context.get('window_start_utc')),clock(context.get('window_end_utc'))
        rows=learning.get('new_matured_outcomes')
        if start is None or end is None or not start<end or not isinstance(rows,list) or not rows:
            return None
        counts={'HIT':0,'MISS':0,'CENSORED':0}
        seen_ids=set();seen_hashes=set()
        for row in rows:
            if not isinstance(row,dict) or row.get('source_contract') not in ('MATURED_OUTCOME_v2','MATURED_OUTCOME_v3'):
                return None
            fid,digest=row.get('forecast_id'),row.get('outcome_sha256')
            at=clock(row.get('created_at_utc'))
            if (not isinstance(fid,str) or not fid or fid in seen_ids or not is_hash(digest) or digest in seen_hashes
                    or not is_hash(row.get('forecast_sha256'))
                    or row.get('source_binding_verification')!='CURRENT_FILE_CANONICAL_JSON_SHA256'
                    or at is None or not start<=at<end):
                return None
            seen_ids.add(fid);seen_hashes.add(digest)
            if row.get('status')=='MATURED':
                result,value=row.get('result'),row.get('return_pct')
                if (result not in ('HIT','MISS') or type(value) not in (int,float)
                        or not math.isfinite(value) or not is_hash(row.get('evidence_sha256'))):
                    return None
                counts[result]+=1
            elif row.get('status')=='CENSORED':
                if row.get('result') is not None or row.get('return_pct') is not None or not isinstance(row.get('reason'),str) or not row['reason']:
                    return None
                # The original maturation owner may censor before any market
                # evidence is available. If supplied, path and digest must pair.
                evidence_path,evidence_hash=row.get('evidence_path'),row.get('evidence_sha256')
                if (evidence_path is not None or evidence_hash is not None) and (
                        not isinstance(evidence_path,str) or not evidence_path or not is_hash(evidence_hash)):
                    return None
                counts['CENSORED']+=1
            else:
                return None
        n=counts['HIT']+counts['MISS']
        return {'contract':'MM_EXPERIMENT_OUTCOME_COUNTS_v1',
                'authority':'DESCRIPTIVE_RESEARCH_ONLY',
                'source_binding':'CONTEXT_HASH_AND_ORIGINAL_OWNER_ADMITTED_ROWS',
                'context_sha256':context['context_hash'],'freeze_sha256':context['freeze_sha256'],
                'registry_sha256':learning['registry_sha256'],
                'outcome_record_count':len(rows),'matured_outcome_count':n,
                'hit_count':counts['HIT'],'miss_count':counts['MISS'],'censored_count':counts['CENSORED'],
                'hit_fraction':counts['HIT']/n if n else None,
                'independent_sample_size':None,'matched_baseline_skill':None,
                'forecast_authority':False,'portfolio_action':False}
    except (ValueError,TypeError,KeyError,OverflowError,RecursionError):
        return None

def fallback_scorecard(context:dict[str,Any])->dict[str,Any]:
    learning=context.get('experiment_learning') if isinstance(context.get('experiment_learning'),dict) else {}
    registry_status=str(learning.get('status') or 'UNAVAILABLE_CONTEXT')
    matured=learning.get('new_matured_outcomes')
    registry_available=(registry_status=='AVAILABLE')
    evidence_available=(registry_available and learning.get('matured_outcome_evidence_available') is True and isinstance(matured,list))
    if not registry_available:
        return {
            'status':'UNAVAILABLE_EXPERIMENT_REGISTRY',
            'experiment_registry_status':registry_status,
            'outcome_ingestion_status':learning.get('outcome_ingestion_status','UNAVAILABLE'),
            'analysis_layer':{},
            'operational_translation_layer':{},
            'matured_outcome_count':None,
            'reason':'Experiment registry evidence is unavailable; an unavailable registry cannot be represented as a valid empty matured-outcome set.',
        }
    if not evidence_available:
        return {
            'status':'INCOMPLETE_EXPERIMENT_OUTCOME_INGESTION',
            'experiment_registry_status':registry_status,
            'outcome_ingestion_status':learning.get('outcome_ingestion_status','INCOMPLETE'),
            'analysis_layer':{},
            'operational_translation_layer':{},
            'matured_outcome_count':None,
            'reason':'Experiment registry is available, but matured-outcome evidence ingestion is incomplete. This lane is degraded without misreporting the registry itself as unavailable.',
        }
    if matured:
        observed=experiment_outcome_scorecard(context,learning)
        if observed is not None:
            return {'status':'DEGRADED','experiment_registry_status':registry_status,
                    'outcome_ingestion_status':'COMPLETE',
                    'analysis_layer':{'experiment_outcome_counts':observed},
                    'operational_translation_layer':{},
                    'matured_outcome_count':observed['matured_outcome_count'],
                    'reason':'Original owner outcome counts restored. Full analysis/translation and paired calibration score remain unavailable.'}
    return {
        'status':'INCOMPLETE_EXPERIMENT_OUTCOME_INGESTION' if matured else 'PENDING_MATURED_OUTCOMES',
        'experiment_registry_status':registry_status,
        'analysis_layer':{},
        'operational_translation_layer':{},
        'matured_outcome_count':None if matured else 0,
        'reason':'Owner outcome records failed scorecard context or row integrity checks; no counts admitted.' if matured else 'A valid experiment registry supplied zero newly matured outcomes; formal outcome scoring remains pending.',
    }
def calibration_context_matches_freeze(context:dict[str,Any], freeze:dict[str,Any])->bool:
    try:
        return (context.get('contract')=='WEEKLY_API_CALIBRATION_CONTEXT_v6'
                and context.get('authority')=='SHADOW_ONLY'
                and all(type(context.get(k)) is int and context[k]==freeze.get(k) for k in ('iso_year','iso_week'))
                and isinstance(freeze.get('freeze_sha256'),str)
                and re.fullmatch(r'[a-f0-9]{64}',freeze['freeze_sha256']) is not None
                and context.get('freeze_sha256')==freeze['freeze_sha256']
                and sha({k:v for k,v in context.items() if k!='context_hash'})==context.get('context_hash'))
    except (ValueError,TypeError,OverflowError,RecursionError):
        return False

def analytical_translation(context:dict[str,Any],freeze:dict[str,Any],
                           api:dict[str,Any],receipt:dict[str,Any],api_status:str)->dict[str,Any]:
    """Preserve the existing shadow model's typed hypotheses, not live forecasts.

    The current v3 API output has no action/phase/operational-translation field.
    Do not infer one from prose, price targets or a successful transport.
    Projection is deliberately value-free: only candidate horizons, directions,
    counts and receipt hashes; actual science admission remains the original owner.
    """
    base={'contract':'MM_SHADOW_ANALYTICAL_TRANSLATION_v1','status':'DEGRADED',
          'authority':'SHADOW_ONLY_NO_ACTION_OR_FORECAST_AUTHORITY',
          'candidate_status':'UNAVAILABLE','candidate_horizon_counts':{},
          'candidate_direction_counts':{},'candidate_count':None,
          'phase':'UNAVAILABLE','rotation':'UNAVAILABLE','forecast_authority':False,
          'portfolio_action':False,'model_weight_change':False,
          'model_utilization_verified':False}
    if api_status!='success':
        return {**base,'reason':'API_FAILED'}
    try:
        if not calibration_context_matches_freeze(context,freeze):
            return {**base,'reason':'CONTEXT_FREEZE_MISMATCH'}
        if (not isinstance(receipt,dict) or receipt.get('contract')!='API_AGENT_RECEIPT_v3'
                or receipt.get('task')!='WEEKLY_CALIBRATION_SHADOW' or receipt.get('status')!='PASS'
                or receipt.get('untrusted_input_envelope') is not True
                or not isinstance(receipt.get('response_id'),str) or not receipt['response_id']
                or receipt.get('context_hash')!=sha(context) or receipt.get('output_hash')!=sha(api)):
            return {**base,'reason':'GATEWAY_RECEIPT_MISMATCH'}
        required={'status','summary','evidence_for','evidence_against','uncertainties','hypotheses','forecast_candidates'}
        if not isinstance(api,dict) or set(api)!=required or not isinstance(api['summary'],str) or not api['summary'].strip():
            return {**base,'reason':'OUTPUT_CONTRACT_INVALID'}
        if api['status']!='READY':
            return {**base,'reason':'MODEL_ANALYSIS_NOT_READY'}
        if any(not isinstance(api[k],list) or not all(isinstance(v,str) for v in api[k])
               for k in ('evidence_for','evidence_against','uncertainties','hypotheses')):
            return {**base,'reason':'OUTPUT_CONTRACT_INVALID'}
        candidates=api['forecast_candidates']
        if not isinstance(candidates,list) or type(receipt.get('forecast_candidate_count')) is not int or receipt['forecast_candidate_count']!=len(candidates):
            return {**base,'reason':'CANDIDATE_COUNT_MISMATCH'}
        # Reuse original gateway validator, then enforce exact schema and finite
        # numeric types (Python bool is an int; JSON NaN is not a valid target).
        root=str(Path(__file__).resolve().parents[2])
        if root not in sys.path:sys.path.insert(0,root)
        from scripts.api_agent.api_gateway import validate_output
        validate_output(api)
        fields={'metric_path','direction','target_mode','threshold_pct','target_value','range_low','range_high','horizon_days','rationale'}
        seen=set();horizons={};directions={}
        for c in candidates:
            if (set(c)!=fields or type(c['horizon_days']) is not int
                    or not isinstance(c['metric_path'],str) or not isinstance(c['rationale'],str)
                    or any(c[k] is not None and (type(c[k]) not in (int,float) or not math.isfinite(c[k]))
                           for k in ('threshold_pct','target_value','range_low','range_high'))):
                return {**base,'reason':'CANDIDATE_CONTRACT_INVALID'}
            # One metric/horizon identity cannot contribute multiple competing
            # rows to a single directional count. Preserve unresolved conflict.
            key=(c['metric_path'].strip(),c['horizon_days'])
            if key in seen:
                return {**base,'reason':'DUPLICATE_OR_CONFLICTING_CANDIDATE'}
            seen.add(key)
            h=str(c['horizon_days']);d=c['direction']
            horizons[h]=horizons.get(h,0)+1;directions[d]=directions.get(d,0)+1
        return {**base,'reason':'TYPED_SHADOW_CANDIDATES_ONLY_NO_OPERATIONAL_DECISION',
                'candidate_status':'VALIDATED_UNADMITTED' if candidates else 'NO_CANDIDATES',
                'candidate_count':len(candidates),'candidate_horizon_counts':horizons,
                'candidate_direction_counts':directions,
                'context_sha256':context['context_hash'],'freeze_sha256':freeze['freeze_sha256'],
                'gateway_context_sha256':receipt['context_hash'],'gateway_output_sha256':receipt['output_hash']}
    except (ValueError,TypeError,KeyError,AttributeError,OverflowError,RecursionError):
        return {**base,'reason':'OUTPUT_CONTRACT_INVALID'}

def effective_delivery_status(api_status: str, api: dict[str, Any],
                              translation: dict[str, Any], scorecard: dict[str, Any],
                              consumer_verified: bool) -> str:
    """Transport success and consumer receipt are not analytical completeness.

    The current gateway schema cannot produce translation or scorecard.
    Preserve delivery, but do not certify incomplete products as READY.
    A genuinely empty, available outcome population may remain pending.
    """
    if not consumer_verified or api_status != 'success' or api.get('status') != 'READY':
        return 'DEGRADED'
    if not isinstance(translation, dict) or translation.get('status') != 'READY':
        return 'DEGRADED'
    if not isinstance(scorecard, dict):
        return 'DEGRADED'
    if scorecard.get('status') == 'READY':
        return 'READY'
    if (scorecard.get('status') == 'PENDING_MATURED_OUTCOMES'
            and scorecard.get('experiment_registry_status') == 'AVAILABLE'
            and type(scorecard.get('matured_outcome_count')) is int
            and scorecard['matured_outcome_count'] == 0):
        return 'READY'
    return 'DEGRADED'


def build_weekly_intelligence_audit(machine:dict[str,Any],pointer:dict[str,Any],
                                    machine_file_sha256:str,pointer_file_sha256:str,
                                    freeze:dict[str,Any]|None=None,preflight:dict[str,Any]|None=None)->str:
    """Compact derived evidence index; NEVER a new market or scientific authority.

    Master Monday runs before CN/SITE final publication. Downstream states
    therefore remain PENDING_DOWNSTREAM instead of falsely claiming success.
    Only allowlisted metadata is copied; API analysis and restricted payloads
    are deliberately excluded.
    """
    def safe_status(value:Any)->str:
        s=str(value or 'UNAVAILABLE').upper()
        return s if re.fullmatch(r'[A-Z0-9_:-]{1,96}',s) else 'UNAVAILABLE'
    def safe_sha(value:Any)->str|None:
        return value if isinstance(value,str) and re.fullmatch(r'[0-9a-f]{64}',value) else None
    year=int(machine['iso_year']);week=int(machine['iso_week'])
    if year<2000 or year>9999:
        raise ValueError('weekly_audit_invalid_iso_week')
    try:
        datetime.fromisocalendar(year,week,1)
    except ValueError as exc:
        raise ValueError('weekly_audit_invalid_iso_week') from exc
    if year!=int(pointer['iso_year']) or week!=int(pointer['iso_week']):
        raise ValueError('weekly_audit_pointer_week_mismatch')
    digest=safe_sha(machine.get('package_sha256'))
    if digest is None or digest!=safe_sha(pointer.get('machine_package_sha256')):
        raise ValueError('weekly_audit_machine_digest_mismatch')
    if not safe_sha(machine_file_sha256) or not safe_sha(pointer_file_sha256):
        raise ValueError('weekly_audit_file_hash_invalid')
    receipt=machine.get('api_receipt') if isinstance(machine.get('api_receipt'),dict) else {}
    model=str(receipt.get('model') or 'UNAVAILABLE')
    model=model if re.fullmatch(r'[a-zA-Z0-9_.-]{1,80}',model) else 'UNAVAILABLE'
    cost=receipt.get('estimated_cost_usd')
    cost=round(float(cost),6) if isinstance(cost,(int,float)) and not isinstance(cost,bool) and 0<=cost<=1000 else None
    learning=machine.get('learning_decision_impact') if isinstance(machine.get('learning_decision_impact'),dict) else {}
    scorecard=machine.get('scorecard') if isinstance(machine.get('scorecard'),dict) else {}
    freeze=freeze if isinstance(freeze,dict) else {}
    preflight=preflight if isinstance(preflight,dict) else {}
    meta=preflight.get('meta') if isinstance(preflight.get('meta'),dict) else {}
    quality=preflight.get('quality') if isinstance(preflight.get('quality'),dict) else {}
    def safe_count(value:Any)->int|None:
        return value if type(value) is int and 0<=value<=10000000 else None
    index={
        'contract':'MASTER_MONDAY_WEEKLY_INTELLIGENCE_AUDIT_v1',
        'authority':'DERIVED_EVIDENCE_INDEX_ONLY_NO_NEW_FORECAST_OR_ACTION',
        'completed_week':f'{year}-W{week:02d}',
        'source_provenance':{
            'freeze_self_sha256':safe_sha(machine.get('freeze_sha256')),
            'preflight_self_sha256':safe_sha(machine.get('preflight_sha256')),
            'context_sha256':safe_sha(machine.get('context_hash')),
            'machine_self_sha256':digest,
            'machine_file_sha256':machine_file_sha256,
            'delivery_pointer_file_sha256':pointer_file_sha256,
            'settled_week_close_sha256':safe_sha((freeze.get('final_week_close') or {}).get('package_sha256')) if isinstance(freeze.get('final_week_close'),dict) else None,
            'weekly_capture_bridge_sha256':safe_sha((freeze.get('weekly_capture_bridge') or {}).get('sha256')) if isinstance(freeze.get('weekly_capture_bridge'),dict) else None,
        },
        'delivery':{
            'preflight':safe_status(pointer.get('preflight_status')),
            'api':safe_status(machine.get('api_status')),
            'producer':safe_status(pointer.get('producer_status')),
            'consumer':safe_status(pointer.get('consumer_receipt_status')),
            'consumer_state':safe_status(pointer.get('consumer_receipt_state')),
            'overall':safe_status(pointer.get('status')),
        },
        'analysis_completeness':{
            'scorecard':safe_status(pointer.get('scorecard_status')),
            'operational_translation':safe_status(pointer.get('operational_translation_status')),
            'learning_decision_impact':safe_status(learning.get('assessment_status')),
            'experiment_learning':safe_status(pointer.get('experiment_learning_status')),
        },
        'evidence_quality':{
            'blocking_gap_count':safe_count(meta.get('blocking_gap_count')),
            'confidence_reducing_gap_count':safe_count(meta.get('confidence_reducing_gap_count')),
            'planned_core_actions':safe_count(meta.get('planned_core_actions')),
            'core_pass':safe_count(quality.get('PASS')),
            'core_partial':safe_count(quality.get('PARTIAL')),
            'core_unavailable':safe_count(quality.get('UNAVAILABLE')),
        },
        'outcome_and_learning':{
            'registry_matured_count_not_scored_or_admitted':safe_count(scorecard.get('matured_outcome_count')),
            'baseline_semantic_identity_count':safe_count(learning.get('baseline_semantic_identity_count')),
            'learning_semantic_identity_count':safe_count(learning.get('learning_semantic_identity_count')),
            'changed_calibration_decision':learning.get('changed_calibration_decision') if type(learning.get('changed_calibration_decision')) is bool else None,
            'forecast_skill':'UNPROVEN_NOT_INFERRED',
        },
        'api_accounting':{'model':model,'estimated_cost_usd':cost},
        'downstream_not_yet_claimed':{
            'cycle_navigator':'PENDING_DOWNSTREAM_OWNER',
            'site':'PENDING_DOWNSTREAM_OWNER',
            'official_compass':'SEPARATE_CURRENT_ACTION_OWNER',
        },
        'scientific_firewall':'FORECAST_SKILL_NOT_INFERRED_FROM_WEEKLY_SCORE_OR_MATURED_COUNT',
        'restricted_payloads_included':False,
    }
    return '# MASTER MONDAY WEEKLY INTELLIGENCE AUDIT — '+index['completed_week']+'\n\n'+(
        'Derived metadata only. Original immutable producer files and downstream '
        'consumer receipts remain authoritative.\n\n```json\n'+
        json.dumps(index,sort_keys=True,ensure_ascii=False,indent=2)+'\n```\n')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',type=Path,required=True);ap.add_argument('--preflight',type=Path,required=True);ap.add_argument('--context',type=Path,required=True);ap.add_argument('--api-output',type=Path);ap.add_argument('--api-receipt',type=Path);ap.add_argument('--api-status',required=True);ap.add_argument('--output-dir',type=Path,required=True);ap.add_argument('--learning-packet',type=Path,default=Path('research/framework_learning/LATEST_MASTER_MONDAY_LEARNING_PACKET.json'));a=ap.parse_args()
    freeze=load(a.freeze);preflight=load(a.preflight);context=load(a.context);api=load(a.api_output) if a.api_output and a.api_output.exists() else {};receipt=load(a.api_receipt) if a.api_receipt and a.api_receipt.exists() else {}
    learning=load(a.learning_packet) if a.learning_packet.exists() else None
    learning_impact=build_learning_decision_impact(context,learning,receipt,int(freeze['iso_year']),int(freeze['iso_week']))
    analysis=api.get('analysis') or api.get('calibration') or api.get('summary') or {'status':'UNAVAILABLE_API_FAILURE' if a.api_status!='success' else 'UNAVAILABLE_NOT_PRODUCED'}
    translation=analytical_translation(context,freeze,api,receipt,a.api_status)
    registry_fallback=fallback_scorecard(context)
    # Current gateway schema has no scorecard. Never override failed
    # deterministic evidence admission with an arbitrary model object.
    scorecard=registry_fallback
    if not calibration_context_matches_freeze(context,freeze):
        scorecard={'status':'DEGRADED','experiment_registry_status':'UNVERIFIED',
                   'matured_outcome_count':None,'analysis_layer':{},'operational_translation_layer':{},
                   'reason':'Calibration context and freeze identity mismatch.'}
    shadow_path=Path('research/api_agent/outputs/shadow_admission/LATEST_SHADOW_ADMISSION_DECISION.json')
    shadow=load(shadow_path) if shadow_path.exists() else {'contract':'SHADOW_ADMISSION_AI_DECISION_v1','overall_status':'NOT_YET_AVAILABLE','candidate_decisions':[],'master_monday_summary':'No autonomous shadow-admission decision has been published yet.'}
    shadow_reporting={'mode':'REPORT_AFTER_DECISION_NO_APPROVAL_PROMPT','human_confirmation_required':False,'decision':shadow}
    machine={'contract':'MASTER_MONDAY_MACHINE_PACKAGE_v1','created_at_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'iso_year':freeze['iso_year'],'iso_week':freeze['iso_week'],'freeze_sha256':freeze['freeze_sha256'],'preflight_sha256':preflight['package_sha256'],'context_hash':context['context_hash'],'api_status':a.api_status,'api_receipt':receipt,'analysis':analysis,'operational_translation':translation,'scorecard':scorecard,'shadow_admission':shadow_reporting,'learning_decision_impact':learning_impact,'authority':{'portfolio_action':False,'canonical_promotion':False,'model_weight_change':False}}
    # Existing machine writer carries only the shared feature reference, not
    # duplicated outcomes or a new decision authority.
    root=str(Path(__file__).resolve().parents[2])
    if root not in sys.path:sys.path.insert(0,root)
    from scripts.research.cn_mm_core_shadow_bridge_v1 import calibration_feature_binding, calibration_learning_binding
    machine['cn_mm_calibration_feature_binding']=calibration_feature_binding(context,freeze)
    machine['cn_mm_calibration_learning_binding']=calibration_learning_binding(context,freeze,receipt,a.api_status)
    machine['package_sha256']=sha(machine);a.output_dir.mkdir(parents=True,exist_ok=True)
    files={'MASTER_MONDAY_MACHINE_PACKAGE.json':machine,'MASTER_MONDAY_CALIBRATION_SCORECARD.json':scorecard,'MASTER_MONDAY_OPERATIONAL_TRANSLATION.json':translation,'MASTER_MONDAY_SHADOW_ADMISSION.json':shadow_reporting,'MASTER_MONDAY_LEARNING_DECISION_IMPACT.json':learning_impact}
    for name,obj in files.items():(a.output_dir/name).write_bytes(canon(obj))
    machine_path=a.output_dir/'MASTER_MONDAY_MACHINE_PACKAGE.json'
    handoff_manifest=Path('/tmp/master_monday_consumer_handoff.json')
    subprocess.run([
        sys.executable,'scripts/orchestration/build_framework_handoff_manifest.py',
        '--repo-root','.',
        '--output',str(handoff_manifest),
    ],check=True)
    subprocess.run([
        sys.executable,'scripts/orchestration/consumer_receipt.py',
        '--repo-root','.',
        '--manifest',str(handoff_manifest),
        '--consumer','MASTER_MONDAY',
        '--target',str(machine_path),
        '--self-hash-field','package_sha256',
        '--max-manifest-age-seconds','900',
        '--declared','MASTER_MONDAY_EVIDENCE_FREEZE',
        '--declared','MASTER_MONDAY_PREFLIGHT_PACKAGE',
    ],check=True)
    machine=load(machine_path)
    consumer_receipt=machine.get('consumer_receipt') if isinstance(machine.get('consumer_receipt'),dict) else {}
    consumer_verified=consumer_receipt.get('consumption_state')=='VERIFIED'
    producer_status='READY' if a.api_status=='success' else 'READY_WITH_API_FAILURE'
    effective_status=effective_delivery_status(a.api_status,api,translation,scorecard,consumer_verified)
    experiment_status=(context.get('experiment_learning') or {}).get('status','UNAVAILABLE_CONTEXT') if isinstance(context.get('experiment_learning'),dict) else 'UNAVAILABLE_CONTEXT'
    report=f"# MASTER MONDAY — {freeze['iso_year']}-W{int(freeze['iso_week']):02d}\n\nPreflight: **{preflight['packet']['status']}**\n\nAPI calibration: **{a.api_status.upper()}**\n\nExperiment registry evidence: **{experiment_status}**\n\nConsumer receipt: **{consumer_receipt.get('status','UNAVAILABLE')}**\n\nLearning decision impact: **{learning_impact.get('assessment_status','UNKNOWN')}**\n\n## Analysis layer\n\n```json\n{json.dumps(analysis,ensure_ascii=False,indent=2)}\n```\n\n## Operational translation\n\n```json\n{json.dumps(translation,ensure_ascii=False,indent=2)}\n```\n\n## Calibration scorecard\n\n```json\n{json.dumps(scorecard,ensure_ascii=False,indent=2)}\n```\n\n## Learning decision impact — 8 week shadow measurement\n\n```json\n{json.dumps(learning_impact,ensure_ascii=False,indent=2)}\n```\n\n## Autonomous shadow admission\n\nThis section is reporting-only. The OpenAI API lifecycle decision does not require owner confirmation.\n\n```json\n{json.dumps(shadow,ensure_ascii=False,indent=2)}\n```\n"
    (a.output_dir/'MASTER_MONDAY_REPORT.md').write_text(report)
    pointer={'contract':'MASTER_MONDAY_DELIVERY_POINTER_v1','iso_year':freeze['iso_year'],'iso_week':freeze['iso_week'],'status':effective_status,'producer_status':producer_status,'machine_package_path':str(machine_path),'machine_package_sha256':machine['package_sha256'],'report_path':str(a.output_dir/'MASTER_MONDAY_REPORT.md'),'preflight_status':preflight['packet']['status'],'freeze_sha256':freeze['freeze_sha256'],'experiment_learning_status':experiment_status,'scorecard_status':scorecard.get('status','UNKNOWN'),'operational_translation_status':translation.get('status','UNKNOWN'),'shadow_admission_status':shadow.get('overall_status','UNKNOWN'),'shadow_admission_human_confirmation_required':False,'consumer_receipt_status':consumer_receipt.get('status','UNAVAILABLE'),'consumer_receipt_state':consumer_receipt.get('consumption_state','UNKNOWN'),'learning_decision_impact_status':learning_impact.get('assessment_status'),'learning_changed_calibration_decision':learning_impact.get('changed_calibration_decision')}
    pointer_path=a.output_dir/'MASTER_MONDAY_DELIVERY_POINTER.json'
    pointer_path.write_bytes(canon(pointer))
    # Version by exact delivered pointer bytes: retries or receipt corrections
    # get new immutable sidecars even if the machine self-digest is unchanged.
    pointer_file_sha256=hashlib.sha256(pointer_path.read_bytes()).hexdigest()
    audit_path=a.output_dir/f"MASTER_MONDAY_WEEKLY_INTELLIGENCE_AUDIT_{pointer_file_sha256[:16]}.md"
    audit=build_weekly_intelligence_audit(
        machine,pointer,
        hashlib.sha256(machine_path.read_bytes()).hexdigest(),
        pointer_file_sha256,
        freeze,preflight,
    )
    if audit_path.exists() and audit_path.read_text()!=audit:
        raise ValueError('weekly_audit_immutable_snapshot_collision')
    audit_path.write_text(audit)
if __name__=='__main__':main()
