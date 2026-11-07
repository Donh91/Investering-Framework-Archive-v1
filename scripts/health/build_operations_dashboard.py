from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

UTC = timezone.utc
SEVERITY = {'GREEN': 0, 'AMBER': 1, 'UNKNOWN': 1, 'RED': 2}


def parse_time(value: Any):
    if isinstance(value, (int, float)): return datetime.fromtimestamp(value, UTC)
    if not isinstance(value, str) or not value: return None
    try: return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(UTC)
    except ValueError: return None


def read_json(path: Path):
    if not path.exists(): return None, 'MISSING'
    try: value = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError): return None, 'INVALID_JSON'
    return (value, None) if isinstance(value, dict) else (None, 'INVALID_SHAPE')


def sha256_path(path): return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() and path.is_file() else None


def first_time(obj, keys: Iterable[str]):
    if not obj: return None
    for key in keys:
        stamp=parse_time(obj.get(key))
        if stamp: return stamp
    return None


def normalized_status(value):
    x=str(value or 'UNKNOWN').upper()
    if x in {'GREEN','AMBER','RED'}: return x
    if x in {'PASS','READY','COMPLETE','DURABLE_PASS','SUCCESS','SKIPPED_NO_DELTA','SKIPPED_NO_ELIGIBLE_INPUT'}: return 'GREEN'
    if x in {'PARTIAL','DEGRADED','PENDING','UNKNOWN','RECOVERING','UNAVAILABLE'}: return 'AMBER'
    if x in {'FAIL','FAILED','BLOCKED','SOURCE_UNAVAILABLE'}: return 'RED'
    return 'UNKNOWN'


def combine_status(*values): return max(values,key=lambda v:SEVERITY.get(v,1))


def freshness(timestamp, reference, green_hours, red_hours):
    if timestamp is None: return 'UNKNOWN','TIMESTAMP_UNAVAILABLE',None
    age=round(max(0.0,(reference-timestamp).total_seconds()/3600.0),3)
    if age<=green_hours: return 'GREEN','FRESH',age
    if age<=red_hours: return 'AMBER','DELAYED',age
    return 'RED','STALE',age


def pointer_entry(root,pointer):
    if not isinstance(pointer,dict): return {'path':None,'declared_sha256':None,'actual_sha256':None,'hash_status':'UNKNOWN'}
    rel=pointer.get('path') if isinstance(pointer.get('path'),str) else None; actual=sha256_path(root/rel) if rel else None; declared=pointer.get('sha256') if isinstance(pointer.get('sha256'),str) else None
    state='MISSING' if actual is None else 'UNDECLARED' if declared is None else 'MATCH' if actual==declared else 'MISMATCH'
    return {'path':rel,'declared_sha256':declared,'actual_sha256':actual,'hash_status':state}


def pointer_object(root,pointer):
    if not pointer.get('path'): return None
    return read_json(root/pointer['path'])[0]


def hash_status(pointer): return 'GREEN' if pointer['hash_status']=='MATCH' else 'RED' if pointer['hash_status']=='MISMATCH' else 'AMBER'


def paired_director_receipt(root,pointer):
    rel=pointer.get('path')
    if not isinstance(rel,str): return None,None
    output=root/rel
    for path in (output.with_name('DAILY_DIRECTOR_RECEIPT.json'),output.with_name('receipt.json')):
        value,error=read_json(path)
        if value is not None: return value,str(path.relative_to(root))
        if error not in {None,'MISSING'}: return None,str(path.relative_to(root))
    return None,None


def verified_weekly_target(root: Path, weekly: dict | None):
    if not isinstance(weekly,dict): return None,None,'NOT_A_POINTER'
    rel=weekly.get('machine_package_path'); declared=weekly.get('machine_package_sha256')
    if not isinstance(rel,str) or not rel or not isinstance(declared,str) or not declared: return None,None,'TARGET_UNDECLARED'
    path=root/rel; actual=sha256_path(path)
    if actual is None: return None,rel,'TARGET_MISSING'
    value,error=read_json(path)
    if error: return None,rel,error
    # Backward-compatible byte-hash pointers remain valid. Newer Master Monday
    # packages embed a semantic package_sha256 and the pointer intentionally
    # binds to that value; comparing it to final bytes is self-referential and
    # produced a permanent false RED.
    semantic = value.get('package_sha256') if isinstance(value,dict) else None
    semantic_ok = value.get('contract') == 'MASTER_MONDAY_MACHINE_PACKAGE_v1' and semantic == declared
    if actual != declared and not semantic_ok: return None,rel,'TARGET_HASH_MISMATCH'
    return value,rel,'MATCH'


def receipt_time(data): return first_time(data,('completed_at_utc','created_at_utc','generated_at_utc','timestamp_utc','created_unix'))
def is_api_receipt(path,data): return 'API_AGENT_RECEIPT' in str(data.get('contract') or '') or path.name.endswith('RECEIPT.json') or path.name=='receipt.json'


def collect_api_usage(root,reference):
    """Aggregate receipt-estimated spend; gateway PASS is not downstream value."""
    month=reference.strftime('%Y-%m'); count=input_tokens=output_tokens=unknown_cost_count=0; cost=0.0; latest=None; seen=set()
    by_task={}
    for base in (root/'research/api_agent/outputs',root/'research/api_agent/receipts'):
        for path in base.rglob('*.json') if base.exists() else []:
            data,error=read_json(path)
            if error or data is None or not is_api_receipt(path,data): continue
            identity=str(data.get('response_id') or data.get('request_hash') or data.get('output_hash') or path)
            if identity in seen: continue
            seen.add(identity); stamp=receipt_time(data)
            if stamp and (latest is None or stamp>latest[0]): latest=(stamp,path,data)
            if not stamp or stamp.strftime('%Y-%m')!=month: continue
            count+=1
            raw_cost=data.get('cost_usd')
            if raw_cost is None: raw_cost=data.get('estimated_cost_usd')
            amount=None
            if type(raw_cost) is not bool and data.get('usage_reconciliation_required') is not True:
                try:
                    candidate=float(raw_cost)
                    if math.isfinite(candidate) and candidate>=0: amount=candidate
                except (TypeError,ValueError,OverflowError):
                    pass
            if amount is None: unknown_cost_count+=1
            else: cost+=amount
            usage=data.get('usage') if isinstance(data.get('usage'),dict) else {}
            try:
                it=int(usage.get('input_tokens',data.get('input_tokens',0)) or 0)
                ot=int(usage.get('output_tokens',data.get('output_tokens',0)) or 0)
                input_tokens+=it; output_tokens+=ot
            except (TypeError,ValueError): it=ot=0
            # Group only *the same* already-deduplicated monthly receipts.
            # This is billing/operational telemetry, not trading or learned skill.
            name=str(data.get('task') or data.get('task_id') or 'UNCLASSIFIED')[:100]
            if name not in by_task:
                by_task[name]={'task':name,'receipt_count':0,'cost_usd':0.0,
                               'unknown_cost_receipt_count':0,
                               'input_tokens':0,'output_tokens':0,
                               'gateway_pass_count':0,'retry_receipt_count':0}
            group=by_task[name]
            group['receipt_count']+=1
            if amount is None: group['unknown_cost_receipt_count']+=1
            else: group['cost_usd']+=amount
            group['input_tokens']+=it
            group['output_tokens']+=ot
            # An API gateway PASS is not a verified producer/consumer or ROI.
            if data.get('status')=='PASS': group['gateway_pass_count']+=1
            attempts=data.get('attempt_count')
            if type(attempts) is int and attempts>1: group['retry_receipt_count']+=1
    row=None
    if latest: row={'path':str(latest[1].relative_to(root)),'completed_at_utc':latest[0].isoformat().replace('+00:00','Z'),'status':latest[2].get('status'),'model':latest[2].get('model'),'task':latest[2].get('task',latest[2].get('task_id')),'cost_usd':latest[2].get('cost_usd',latest[2].get('estimated_cost_usd'))}
    breakdown=sorted(({**g,'cost_usd':round(g['cost_usd'],6),
                       'cost_estimate_status':'PARTIAL_UNKNOWN' if g['unknown_cost_receipt_count'] else 'COMPLETE_FROM_RECEIPTS'}
                      for g in by_task.values()),
                     key=lambda r:(-r['unknown_cost_receipt_count'],-r['cost_usd'],-r['receipt_count'],r['task']))
    return {'month':month,'receipt_count':count,'cost_usd':round(cost,6),
            'unknown_cost_receipt_count':unknown_cost_count,
            'cost_estimate_status':'PARTIAL_UNKNOWN' if unknown_cost_count else 'COMPLETE_FROM_RECEIPTS',
            'input_tokens':input_tokens,'output_tokens':output_tokens,'latest':row,
            'spend_by_task':breakdown,
            'spend_breakdown_semantics':'DEDUPED_RECEIPT_ESTIMATES_NOT_PROVIDER_BILLING_OR_CAUSAL_VALUE'}


def direct_system(root,path,contract,green_hours,red_hours,reference,missing_reason):
    value,error=read_json(root/path)
    if error: return {'status':'AMBER' if error=='MISSING' else 'RED','reason':missing_reason if error=='MISSING' else error,'path':str(path),'timestamp_utc':None,'age_hours':None},value
    stamp=first_time(value,('generated_at_utc','created_at_utc','completed_at_utc')); fresh,reason,age=freshness(stamp,reference,green_hours,red_hours); semantic='GREEN' if value.get('contract')==contract else 'RED'
    return {'status':combine_status(fresh,semantic),'reason':reason if semantic=='GREEN' else 'INVALID_CONTRACT','path':str(path),'timestamp_utc':stamp.isoformat().replace('+00:00','Z') if stamp else None,'age_hours':age},value


def upstream_health_system(value,error,reference):
    if error:
        return {
            'status':'UNKNOWN' if error=='MISSING' else 'RED',
            'reason':error,
            'generated_at_utc':None,
            'age_hours':None,
            'freshness_status':'UNKNOWN',
            'semantic_status':None,
            'input_error':error,
        }
    stamp=first_time(value,('generated_at_utc','created_at_utc','completed_at_utc'))
    fresh,fresh_reason,age=freshness(stamp,reference,18,30)
    semantic=normalized_status(value.get('status') if value else None)
    return {
        'status':combine_status(fresh,semantic),
        'reason':fresh_reason if fresh!='GREEN' else None,
        'generated_at_utc':value.get('generated_at_utc') if value else None,
        'age_hours':age,
        'freshness_status':fresh,
        'semantic_status':value.get('status') if value else None,
        'input_error':None,
    }



# Advisory source-coverage readback. No producer, market, forecast or release authority.
# Each lane retains its own observed source clock. A successful scheduled workflow
# is NOT a successful source, verified event, consumer ACK or trading edge.
SOURCE_COVERAGE_LANES = (
    ('hourly', 'hourly-sequence-capture.yml', 'HOURLY', '03_DAILY_CAPTURE_LOGS/hourly/LATEST.json',
     'HOURLY_SEQUENCE_LATEST_POINTER_v2_2', ('window_end_utc',), 3),
    ('daily_live_anchor', 'daily-raw-owner-capture.yml', 'SIX_PER_LOCAL_DAY', '03_DAILY_CAPTURE_LOGS/captures/LATEST.json',
     'DAILY_LIVE_ANCHOR_LATEST_POINTER_v1', ('captured_at_utc',), 10),
    ('settled_etf', 'daily-settled-etf-calibration.yml', 'SETTLED_SESSION_DAILY', '03_DAILY_CAPTURE_LOGS/etf/LATEST.json',
     'DAILY_SETTLED_ETF_LATEST_POINTER_v2', ('verification_completed_at_utc', 'retrieved_at_utc'), 72),
    ('stablecoin_liquidity', 'daily-stablecoin-liquidity.yml', 'DAILY', '03_DAILY_CAPTURE_LOGS/stablecoin_liquidity/LATEST.json',
     'DEFILLAMA_STABLECOIN_LIQUIDITY_OWNER_v1_1', ('retrieved_at_utc',), 48),
    ('market_breadth', 'rich-breadth-checkpoint.yml', 'CHECKPOINT', '03_DAILY_CAPTURE_LOGS/breadth_rich/LATEST.json',
     'RICH_BREADTH_CHECKPOINT_v1', ('retrieved_at_utc',), 48),
    ('btc_dominance', 'research-owner-btcd-daily.yml', 'DAILY', '03_DAILY_CAPTURE_LOGS/btc_d_cmc/latest/BTC_D_CMC_RAW_SOURCE.json',
     None, ('status.timestamp',), 48),
    ('news_intelligence', 'situation-room-daily-static.yml', 'DAILY_DISCOVERY', '03_DAILY_CAPTURE_LOGS/catalyst_overlay/situation_room/LATEST.json',
     'SITUATION_ROOM_DAILY_OWNER_LATEST_POINTER_v1', (), 48),
    ('entry_signals', 'entry-signal-ledger.yml', 'EVENT_AND_HOURLY_FALLBACK', '04_MARKET_LEARNING/entry_signals/LATEST.json',
     'ENTRY_SIGNAL_LATEST_v1', ('generated_at_utc',), 4),
    ('edge_research', None, 'PROSPECTIVE_EVENT_DRIVEN', 'research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json',
     'EXPERIMENT_LIFECYCLE_REGISTRY_v1', ('generated_at_utc',), 72),
)


def source_coverage_snapshot(root, reference, automation):
    """Non-authoritative source/cron/consumer separation, read-only and fail-closed."""
    observed_workflows = {
        x.get('workflow'): x for x in (automation or {}).get('workflows', [])
        if isinstance(x, dict) and isinstance(x.get('workflow'), str)
    }
    rows = []
    for lane, workflow, cadence, rel, contract, clock_keys, max_age_hours in SOURCE_COVERAGE_LANES:
        row, error = read_json(root / rel)
        clock = None
        if row is not None:
            for key in clock_keys:
                v = row
                for part in key.split('.'):
                    v = v.get(part) if isinstance(v, dict) else None
                clock = parse_time(v)
                if clock is not None:
                    break
            if lane == 'news_intelligence':
                # News pointer has a separate dated discovery row. A 6/6 fetch
                # is NEVER evidence of 6/6 event recall/verified news.
                key = row.get('path')
                prefix = '03_DAILY_CAPTURE_LOGS/catalyst_overlay/situation_room/'
                if isinstance(key, str) and key.startswith(prefix) and '..' not in key.split('/'):
                    source, source_error = read_json(root / key)
                    clock = first_time(source, ('detection_time_utc',)) if source else None
                    if source_error or not source or source.get('run_id') != row.get('run_id'):
                        error = 'NEWS_DATED_SOURCE_OR_BINDING_INVALID'
                    elif (source.get('run_status') != 'PASS' or
                          source.get('daily_result') not in {'PASS', 'READY', 'NO_VERIFIED_EVENTS_COMPLETE_COVERAGE'}):
                        error = 'NEWS_DISCOVERY_NOT_VERIFIED'
                else:
                    error = 'NEWS_OWNER_DATED_PATH_INVALID'
        # No inferred PASS from transport or success on the schedule.
        if error or row is None:
            source_state = 'MISSING_OR_DEGRADED'
            reason = error or 'MISSING'
        elif contract is not None and row.get('contract') != contract:
            source_state, reason = 'MISSING_OR_DEGRADED', 'OWNER_CONTRACT_MISMATCH'
        elif lane == 'hourly' and (
            row.get('status') != 'COMPLETE' or
            type(row.get('requested_hours')) is not int or
            any(type(row.get(k)) is not int or row[k] < row['requested_hours']
                for k in ('spot_complete_hours', 'spot_flow_complete_hours',
                          'long_short_complete_hours', 'derivatives_oi_complete_hours'))
        ):
            source_state, reason = 'MISSING_OR_DEGRADED', 'HOURLY_COMPLETENESS_UNPROVEN'
        elif lane == 'daily_live_anchor' and (
            row.get('status') != 'COMPLETE' or
            row.get('anchor_core_passed') != row.get('anchor_core_planned') or
            not row.get('anchor_core_planned')
        ):
            source_state, reason = 'MISSING_OR_DEGRADED', 'DAILY_ANCHOR_INCOMPLETE'
        elif lane == 'settled_etf' and row.get('status') != 'PASS':
            source_state, reason = 'MISSING_OR_DEGRADED', 'SETTLED_ETF_NOT_PASS'
        elif lane == 'btc_dominance' and (
            not isinstance(row.get('status'), dict) or
            str(row['status'].get('error_code')) != '0'
        ):
            source_state, reason = 'MISSING_OR_DEGRADED', 'BTC_D_OWNER_ERROR'
        elif lane == 'entry_signals' and (
            not isinstance(row.get('authority'), dict) or
            row['authority'].get('portfolio_execution') is not False
        ):
            source_state, reason = 'MISSING_OR_DEGRADED', 'ENTRY_AUTHORITY_INVALID'
        else:
            source_state, reason = 'OBSERVED_SOURCE', 'SOURCE_ROW_PRESENT'
        if source_state == 'OBSERVED_SOURCE' and clock is None:
            source_state, reason = 'UNKNOWN_TIME', 'SOURCE_CLOCK_UNAVAILABLE'
        age_hours = None
        if clock is not None:
            age_hours = round((reference - clock).total_seconds() / 3600, 3)
            if age_hours < -0.0834:
                source_state, reason = 'UNKNOWN_TIME', 'SOURCE_CLOCK_IN_FUTURE'
            elif source_state == 'OBSERVED_SOURCE' and age_hours > max_age_hours:
                source_state, reason = 'DELAYED_SOURCE', 'BEYOND_OBSERVATIONAL_AGE_WINDOW'
        workflow_row = observed_workflows.get(workflow) if workflow else None
        scheduled = (workflow_row or {}).get('live', {}).get('latest_scheduled_run')
        if not isinstance(scheduled, dict):
            schedule_state = 'NATIVE_SCHEDULE_UNVERIFIED'
        elif scheduled.get('event') != 'schedule':
            schedule_state = 'NATIVE_SCHEDULE_UNVERIFIED'
        elif scheduled.get('conclusion') == 'success':
            schedule_state = 'LAST_SCHEDULE_SUCCESS_NOT_COVERAGE'
        else:
            schedule_state = 'LAST_SCHEDULE_NOT_SUCCESS'
        rows.append({
            'lane': lane, 'cadence': cadence, 'workflow': workflow,
            'source_path': rel, 'source_state': source_state, 'reason': reason,
            'source_age_hours': age_hours,
            'source_observation_utc': clock.isoformat().replace('+00:00', 'Z') if clock else None,
            'last_native_schedule_state': schedule_state,
            'consumer_delivery': 'NOT_ATTESTED_BY_THIS_SNAPSHOT',
            'source_first_known': 'NOT_ATTESTED_BY_THIS_SNAPSHOT',
            'science_or_edge_admission': 'NOT_ATTESTED_BY_THIS_SNAPSHOT',
        })
    return {
        'contract': 'OPERATIONS_SOURCE_COVERAGE_OBSERVER_v1',
        'authority': 'READ_ONLY_ADVISORY_NO_MODEL_OR_RELEASE_AUTHORITY',
        'generated_at_utc': reference.isoformat().replace('+00:00', 'Z'),
        'source_count': len(rows),
        'rows': rows,
        'semantics': 'A fetched source, complete rolling window, scheduled workflow SUCCESS, verified event, consumer ACK and scientific admission are separate claims. UNKNOWN is not zero.',
    }


def build_dashboard(repo_root,reference=None):
    reference=reference or datetime.now(UTC); handoff,handoff_error=read_json(repo_root/'LATEST_HANDOFF.json'); automation,automation_error=read_json(repo_root/'research/architecture_health/LATEST_AUTOMATION_HEALTH.json'); architecture,architecture_error=read_json(repo_root/'research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json'); pointers=handoff.get('pointers',{}) if handoff else {}
    capture_pointer=pointer_entry(repo_root,pointers.get('latest_capture')); director_pointer=pointer_entry(repo_root,pointers.get('latest_director_output')); weekly_pointer=pointer_entry(repo_root,pointers.get('latest_weekly_output')); capture=pointer_object(repo_root,capture_pointer); director=pointer_object(repo_root,director_pointer); weekly=pointer_object(repo_root,weekly_pointer); director_receipt,director_receipt_path=paired_director_receipt(repo_root,director_pointer); weekly_target,weekly_target_path,weekly_target_hash_status=verified_weekly_target(repo_root,weekly)
    capture_time=first_time(capture,('captured_at_utc','snapshot_utc','generated_at_utc','created_at_utc')); director_time=first_time(director,('completed_at_utc','generated_at_utc','created_at_utc','captured_at_utc')) or receipt_time(director_receipt); weekly_time=first_time(weekly,('completed_at_utc','generated_at_utc','created_at_utc','freeze_recorded_at_utc','published_at_utc')) or first_time(weekly_target,('completed_at_utc','generated_at_utc','created_at_utc','freeze_recorded_at_utc','published_at_utc'))
    capture_fresh,capture_reason,capture_age=freshness(capture_time,reference,8,16); director_fresh,director_reason,director_age=freshness(director_time,reference,12,30); weekly_fresh,weekly_reason,weekly_age=freshness(weekly_time,reference,24*8,24*15); weekly_target_integrity='GREEN' if weekly_target_hash_status in {'MATCH','NOT_A_POINTER'} else 'RED' if weekly_target_hash_status=='TARGET_HASH_MISMATCH' else 'AMBER'
    director_output_status=(director or {}).get('status'); director_execution_status=(director_receipt or {}).get('status'); semantic_source=director_output_status or director_execution_status; director_semantic=normalized_status(semantic_source)
    if str(director_execution_status or '').upper()=='SKIPPED_NO_DELTA': director_semantic='GREEN'; director_reason='EXPECTED_SKIP_NO_COMPARABLE_DELTA'
    elif str(director_execution_status or '').upper()=='SKIPPED_NO_ELIGIBLE_INPUT': director_semantic='GREEN'; director_reason='EXPECTED_SKIP_NO_ELIGIBLE_INPUT'
    elif str(director_execution_status or '').upper()=='SKIPPED_OWNER_RUN_ALREADY_ANALYZED': director_semantic='GREEN'; director_reason='EXPECTED_SKIP_OWNER_RUN_ALREADY_ANALYZED'
    elif director_fresh=='GREEN' and director_semantic!='GREEN': director_reason=f"SEMANTIC_STATUS_{str(semantic_source or 'UNKNOWN').upper()}"
    experiment_system,experiment=direct_system(repo_root,Path('research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json'),'EXPERIMENT_LIFECYCLE_REGISTRY_v1',36,72,reference,'NO_EXPERIMENT_REGISTRY_YET'); sync_system,sync=direct_system(repo_root,Path('research/experiment_lifecycle/LATEST_EXPERIMENT_RECEIPT_SYNC.json'),'EXPERIMENT_RECEIPT_SYNC_v1',48,96,reference,'NO_EXPERIMENT_RECEIPT_SYNC_YET')
    if sync and sync.get('status')=='UNAVAILABLE': sync_system['status']='AMBER'; sync_system['reason']='EXECUTION_PLANE_UNAVAILABLE'
    if sync and sync.get('status')=='FAIL': sync_system['status']='RED'; sync_system['reason']='RECEIPT_SYNC_FAILED'
    remediation_system,remediation=direct_system(repo_root,Path('research/remediation/LATEST_REMEDIATION_QUEUE.json'),'REMEDIATION_MATURATION_ENGINE_v1',18,36,reference,'NO_REMEDIATION_QUEUE_YET')
    automation_system=upstream_health_system(automation,automation_error,reference); automation_system.update({'red_count':automation.get('red_count') if automation else None,'amber_count':automation.get('amber_count') if automation else None,'blockers':automation.get('blockers',[]) if automation else []})
    architecture_system=upstream_health_system(architecture,architecture_error,reference); architecture_system.update({'blockers':architecture.get('blockers',[]) if architecture else []})
    systems={'daily_capture':{'status':combine_status(capture_fresh,hash_status(capture_pointer)),'reason':capture_reason,'age_hours':capture_age,'timestamp_utc':capture_time.isoformat().replace('+00:00','Z') if capture_time else None,'pointer':capture_pointer},'openai_daily_director':{'status':combine_status(director_fresh,hash_status(director_pointer),director_semantic),'reason':director_reason,'age_hours':director_age,'timestamp_utc':director_time.isoformat().replace('+00:00','Z') if director_time else None,'semantic_status':semantic_source,'execution_status':director_execution_status,'pointer':director_pointer,'receipt_path':director_receipt_path},'weekly_output':{'status':combine_status(weekly_fresh,hash_status(weekly_pointer),weekly_target_integrity),'reason':weekly_reason if weekly_target_integrity=='GREEN' else weekly_target_hash_status,'age_hours':weekly_age,'timestamp_utc':weekly_time.isoformat().replace('+00:00','Z') if weekly_time else None,'pointer':weekly_pointer,'target_path':weekly_target_path,'target_hash_status':weekly_target_hash_status},'automation_health':automation_system,'architecture_health':architecture_system,'experiment_lifecycle':experiment_system,'experiment_receipt_sync':sync_system,'remediation_maturation':remediation_system}
    actions=[]
    for name,system in systems.items():
        reason=system.get('reason') or system.get('input_error') or system.get('blockers') or (f"SEMANTIC_STATUS_{str(system.get('semantic_status') or system.get('status') or 'UNKNOWN').upper()}" if system.get('status') in {'AMBER','UNKNOWN'} else 'REQUIRED_INPUT_UNAVAILABLE')
        if system['status']=='RED': actions.append({'priority':'P0','system':name,'reason':reason})
        elif system['status'] in {'AMBER','UNKNOWN'}: actions.append({'priority':'P1','system':name,'reason':reason})
    actions.sort(key=lambda row:(row['priority'],row['system'])); overall='GREEN'
    for system in systems.values(): overall=combine_status(overall,system['status'])
    dispatch=read_json(repo_root/'research/experiment_lifecycle/LATEST_EXPERIMENT_DISPATCH_MANIFEST.json')[0] or {}
    dashboard={'contract':'OPERATIONS_DASHBOARD_v1_2','authority':'OPERATIONAL_OBSERVABILITY_ONLY','generated_at_utc':reference.isoformat().replace('+00:00','Z'),'overall_status':overall,'source_status':{'latest_handoff':handoff_error or 'PASS','automation_health':automation_error or 'PASS','architecture_health':architecture_error or 'PASS'},'systems':systems,'agent_activity':{'openai_api':collect_api_usage(repo_root,reference),'pending_forecast_candidates':len(handoff.get('pending_forecast_candidates',[])) if handoff else 0,'experiments':{'candidate_count':(experiment or {}).get('candidate_count',0),'state_counts':(experiment or {}).get('state_counts',{}),'dispatch_request_count':dispatch.get('request_count',0)},'remediation':{'codex_ready':((remediation or {}).get('summary') or {}).get('codex_ready',0),'needs_more_evidence':((remediation or {}).get('summary') or {}).get('needs_more_evidence',0),'automatic_code_write':(remediation or {}).get('automatic_code_write',False),'automatic_merge':(remediation or {}).get('automatic_merge',False)}},'incidents':{'open_count':len(handoff.get('open_incidents',[])) if handoff else 0,'paths':handoff.get('open_incidents',[]) if handoff else [],'truncated':handoff.get('open_incidents_truncated') if handoff else None,'incident_file_count':handoff.get('incident_file_count') if handoff else None,'resolved_count':handoff.get('resolved_incident_count') if handoff else None,'invalid_resolution_receipts':handoff.get('invalid_incident_resolution_receipts',[]) if handoff else []},'required_actions':actions}
    dashboard['source_coverage']=source_coverage_snapshot(repo_root,reference,automation)
    canonical=json.dumps(dashboard,sort_keys=True,separators=(',',':')).encode(); dashboard['dashboard_sha256']=hashlib.sha256(canonical).hexdigest(); return dashboard


def render_markdown(data):
    lines=['# Operations Dashboard','',f"Overall: **{data['overall_status']}**",f"Generated: `{data['generated_at_utc']}`",'','## Systems','','| System | Status | Detail | Age hours |','|---|---:|---|---:|']
    for name,system in data['systems'].items(): lines.append(f"| `{name}` | **{system['status']}** | {system.get('reason') or system.get('semantic_status') or '-'} | {system.get('age_hours') if system.get('age_hours') is not None else '-'} |")
    coverage=data.get('source_coverage') or {}
    if coverage.get('rows'):
        lines+=['','## Source coverage (advisory, not producer/consumer acceptance)','','| Lane | Cadence | Source state | Schedule observation | Source age (h) | Consumer |','|---|---|---|---|---:|---|']
        for item in coverage['rows']:
            lines.append(f"| {item['lane']} | {item['cadence']} | {item['source_state']} ({item['reason']}) | {item['last_native_schedule_state']} | {item['source_age_hours'] if item['source_age_hours'] is not None else '-'} | UNKNOWN |")
        lines+=['','A successful schedule does not prove a complete source, verified news, point-in-time first-known, consumer readback or financial edge.']
    usage=data['agent_activity']['openai_api']; exp=data['agent_activity']['experiments']; rem=data['agent_activity']['remediation']; cost_label=(f"${usage['cost_usd']:.6f} known subtotal, {usage.get('unknown_cost_receipt_count',0)} unknown-cost receipts" if usage.get('unknown_cost_receipt_count') else f"${usage['cost_usd']:.6f} from receipts"); lines+=['','## AI and learning activity','',f"- OpenAI receipts this month: **{usage['receipt_count']}**",f"- OpenAI estimated cost this month: **{cost_label}**",f"- Pending forecast candidates: **{data['agent_activity']['pending_forecast_candidates']}**",f"- Experiment candidates: **{exp['candidate_count']}**",f"- Experiment dispatch requests: **{exp['dispatch_request_count']}**",f"- Codex-ready remediation tasks: **{rem['codex_ready']}**",f"- Needs-more-evidence items: **{rem['needs_more_evidence']}**",'','## Incidents','',f"Open incident references: **{data['incidents']['open_count']}**"]
    if usage.get('spend_by_task'):
        lines+=['','### API spend by task (receipt estimates only)','',
                '| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |',
                '|---|---:|---:|---:|---:|---:|']
        for group in usage['spend_by_task'][:12]:
            lines.append(f"| `{group['task']}` | {group['receipt_count']} | ${group['cost_usd']:.6f} | {group.get('unknown_cost_receipt_count',0)} | {group['gateway_pass_count']} | {group['retry_receipt_count']} |")
        lines+=['','A gateway PASS alone is not measured downstream value or investment edge.']
    lines+=['','## Required actions','']
    if data['required_actions']: lines.extend(f"- **{row['priority']}** `{row['system']}` - {row['reason']}" for row in data['required_actions'])
    else: lines.append('- None')
    lines+=['',f"Dashboard SHA-256: `{data['dashboard_sha256']}`",'']; return '\n'.join(lines)


def main():
    p=argparse.ArgumentParser(); p.add_argument('--repo-root',type=Path,required=True); p.add_argument('--json-output',type=Path,required=True); p.add_argument('--md-output',type=Path,required=True); p.add_argument('--reference-time'); a=p.parse_args(); result=build_dashboard(a.repo_root,parse_time(a.reference_time) if a.reference_time else None); a.json_output.parent.mkdir(parents=True,exist_ok=True); a.md_output.parent.mkdir(parents=True,exist_ok=True); a.json_output.write_text(json.dumps(result,sort_keys=True,separators=(',',':'))+'\n'); a.md_output.write_text(render_markdown(result)); print(json.dumps({'status':result['overall_status'],'dashboard_sha256':result['dashboard_sha256']},sort_keys=True))

if __name__=='__main__': main()
