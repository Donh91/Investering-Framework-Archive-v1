#!/usr/bin/env python3
"""Task2 research-only, seven-day source-clock evidence continuity.

Consumes the EXISTING daily Git-committer-clock proxy, never provider PIT,
execution, prices, forecasts, outcomes or statistical edge. First daily
snapshot stays immutable; late revisions raise a visible drift flag.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

CONTRACT = 'TASK2_HOURLY_SOURCE_COMMIT_CLOCK_SLA_v1'
WINDOW_CONTRACT = 'TASK2_HOURLY_SOURCE_7DAY_CONTINUITY_v1'
SEMANTICS = 'GIT_COMMITTER_CLOCK_PROXY_NOT_VERIFIED_PUSH_OR_PROVIDER_FIRST_KNOWN'
KINDS = {
    'FIRST_COMMIT_CLOCK_WITHIN_90M':'first_commit_clock_within_90m',
    'FIRST_COMMIT_CLOCK_AFTER_90M':'first_commit_clock_after_90m',
    'NOT_PRESENT_IN_FIRST_PARENT_HISTORY':'not_present_in_first_parent_history',
    'CLOCK_ANOMALY_NOT_ADMITTED':'clock_anomalies',
}
EXPECTED_ROW_KEYS = {'classification','due_at_utc','first_present_main_commit',
                     'first_present_committer_utc','minutes_after_due',
                     'source_open_at_utc','source_path'}
EXPECTED_TOP_KEYS = {'authority','clock_anomalies','contract','evaluated_at_utc',
                     'evidence_semantics','expected_due_hours',
                     'first_commit_clock_after_90m','first_commit_clock_within_90m',
                     'main_first_parent_ref_sha','not_present_in_first_parent_history',
                     'records','utc_due_day','measurement_status','reason'}
AUTHORITY = {'research_only':True,'model_promotion':False,
             'original_outcome_rescore':False,'portfolio_action':False}


def utc_time(value):
    if not isinstance(value,str) or not value.endswith('Z'):
        raise ValueError('UTC_Z_REQUIRED')
    parsed = datetime.fromisoformat(value[:-1] + '+00:00')
    if parsed.utcoffset() != timedelta(0):
        raise ValueError('UTC_Z_REQUIRED')
    return parsed


def parse_day(value):
    if not isinstance(value,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):
        raise ValueError('INVALID_UTC_DAY')
    return date.fromisoformat(value)


def canonical_bytes(doc):
    return (json.dumps(doc,sort_keys=True,separators=(',',':'),ensure_ascii=True)+'\n').encode()


def daily_signature(doc):
    """Only the substantive original-day rows matter on an idempotent reread.

    A new run/head/evaluated_at or a differently spaced JSON serializer is not
    itself revision of the frozen time-of-first-observed-source classification.
    """
    if doc.get('measurement_status') == 'UNAVAILABLE':
        return ('UNAVAILABLE',str(doc.get('reason')))
    return tuple((r['due_at_utc'],r['source_open_at_utc'],r['source_path'],
                  r['classification'],r.get('first_present_main_commit'),
                  r.get('first_present_committer_utc'),r.get('minutes_after_due'))
                 for r in doc['records'])


def validate_day(doc, *, now):
    if not isinstance(doc,dict) or doc.get('contract') != CONTRACT:
        raise ValueError('INVALID_DAILY_CONTRACT')
    if not set(doc).issubset(EXPECTED_TOP_KEYS):
        raise ValueError('UNKNOWN_DAILY_ROOT_FIELD')
    day = parse_day(doc.get('utc_due_day'))
    if day >= now.date():
        raise ValueError('DAY_NOT_COMPLETE')
    if any(doc.get('authority',{}).get(key) is not value for key,value in AUTHORITY.items()):
        raise ValueError('AUTHORITY_NOT_RESEARCH_ONLY')
    if doc.get('measurement_status') == 'UNAVAILABLE':
        if doc.get('reason') != 'SOURCE_GIT_HISTORY_OR_VALIDATION_UNAVAILABLE':
            raise ValueError('UNKNOWN_UNAVAILABLE_REASON')
        return {'day':day.isoformat(),'state':'UNAVAILABLE','counts':None}
    if doc.get('evidence_semantics') != SEMANTICS:
        raise ValueError('NOT_COMMIT_CLOCK_PROXY')
    if not re.fullmatch('[0-9a-f]{40}',str(doc.get('main_first_parent_ref_sha'))):
        raise ValueError('UNBOUND_MAIN_SOURCE')
    if doc.get('expected_due_hours') != 24 or not isinstance(doc.get('records'),list) or len(doc['records']) != 24:
        raise ValueError('NOT_24_DUE_HOURS')
    counts = {k:0 for k in KINDS}
    midnight = datetime.combine(day,datetime.min.time(),tzinfo=timezone.utc)
    for h,row in enumerate(doc['records']):
        if not isinstance(row,dict) or set(row) != EXPECTED_ROW_KEYS:
            raise ValueError('INVALID_OR_PRIVATE_DAILY_ROW')
        due = midnight + timedelta(hours=h)
        start = due - timedelta(hours=1)
        if utc_time(row.get('due_at_utc')) != due or utc_time(row.get('source_open_at_utc')) != start:
            raise ValueError('DUPLICATE_MISSING_OR_WRONG_DUE_CLOCK')
        target_path = '03_DAILY_CAPTURE_LOGS/hourly/' + start.strftime('%Y/%m/%Y-%m-%d.csv')
        if row.get('source_path') != target_path:
            raise ValueError('INCORRECT_MIDNIGHT_SOURCE_PATH')
        kind = row.get('classification')
        if kind not in counts:
            raise ValueError('INVALID_CLOCK_CLASSIFICATION')
        counts[kind] += 1
        stamp,sha,mins = (row.get('first_present_committer_utc'),
                          row.get('first_present_main_commit'),row.get('minutes_after_due'))
        if kind == 'NOT_PRESENT_IN_FIRST_PARENT_HISTORY':
            if stamp is not None or sha is not None or mins is not None:
                raise ValueError('MISSING_ROW_HAS_FAKE_FIRST_KNOWN')
        else:
            if not re.fullmatch('[0-9a-f]{40}',str(sha)) or not isinstance(mins,(int,float)) or isinstance(mins,bool):
                raise ValueError('INVALID_CLOCK_RECEIPT')
            delta = (utc_time(stamp)-due).total_seconds()/60
            if abs(delta - mins)>0.002:
                raise ValueError('CLOCK_LAG_MISMATCH')
            expected = ('CLOCK_ANOMALY_NOT_ADMITTED' if delta < 0 else
                        'FIRST_COMMIT_CLOCK_WITHIN_90M' if delta<=90 else
                        'FIRST_COMMIT_CLOCK_AFTER_90M')
            if kind != expected:
                raise ValueError('MISCLASSIFIED_DEADLINE')
    for kind, field in KINDS.items():
        if doc.get(field) != counts[kind]:
            raise ValueError('TAMPERED_DAILY_TOTALS')
    return {'day':day.isoformat(),'state':'MEASURED',
            'counts':{field:counts[kind] for kind,field in KINDS.items()}}


def rollup(folder, *, ending_day, now):
    ending_day = parse_day(ending_day)
    if ending_day >= now.date():
        raise ValueError('ENDING_DAY_NOT_COMPLETE')
    days, sums, sha = [], {v:0 for v in KINDS.values()}, hashlib.sha256()
    all_measured = True
    for offset in range(6,-1,-1):
        day = ending_day-timedelta(days=offset)
        path = folder/(day.isoformat()+'.json')
        if not path.is_file():
            all_measured=False
            days.append({'day':day.isoformat(),'state':'NOT_COLLECTED','counts':None})
            continue
        payload = path.read_bytes()
        obj = json.loads(payload)
        valid = validate_day(obj,now=now)
        if valid['day'] != day.isoformat():
            raise ValueError('DAY_FILE_CONTENT_MISMATCH')
        valid['receipt_sha256']=hashlib.sha256(payload).hexdigest()
        days.append(valid)
        sha.update(day.isoformat().encode()+b':' + bytes.fromhex(valid['receipt_sha256']))
        if valid['state'] != 'MEASURED':
            all_measured=False
        else:
            for key, count in valid['counts'].items():
                sums[key]+=count
    measured = sum(d['state']=='MEASURED' for d in days)
    return {'contract':WINDOW_CONTRACT,'ending_utc_day':ending_day.isoformat(),
            'seven_consecutive_days':[d['day'] for d in days],
            'days':days, 'measured_days':measured,'missing_or_unavailable_days':7-measured,
            'denominator_due_hours':168,
            'measured_due_hours':24*measured,
            'status':'COMPLETE_PROXY_RESEARCH_ONLY' if all_measured else 'INCOMPLETE_DO_NOT_CALCULATE_RATE',
            'on_time_rate':round(sums['first_commit_clock_within_90m']/168,6) if all_measured else None,
            'within_90m':sums['first_commit_clock_within_90m'] if all_measured else None,
            'after_90m':sums['first_commit_clock_after_90m'] if all_measured else None,
            'absent':sums['not_present_in_first_parent_history'] if all_measured else None,
            'clock_anomalies':sums['clock_anomalies'] if all_measured else None,
            'receipt_chain_sha256':sha.hexdigest(),
            'authority':AUTHORITY,'scientific_admission':'BLOCKED_PROVIDER_FIRST_KNOWN_AND_PUSH_UNVERIFIED',
            'evidence_semantics':SEMANTICS}


def record_day(latest, archive, *, now):
    parsed = validate_day(latest,now=now)
    archive.mkdir(parents=True,exist_ok=True)
    name = archive/(parsed['day']+'.json')
    if name.exists():
        existing = json.loads(name.read_text())
        validate_day(existing,now=now)
        if daily_signature(existing) != daily_signature(latest):
            return 'FROZEN_DAY_DRIFT_REVIEW_REQUIRED'
        return 'ALREADY_RECORDED_IDENTICAL_EVIDENCE'
    name.write_bytes(canonical_bytes(latest))
    return 'NEW_DAY_FROZEN'


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--latest',type=Path,required=True)
    ap.add_argument('--archive',type=Path,required=True)
    ap.add_argument('--rollup',type=Path,required=True)
    args=ap.parse_args()
    now=datetime.now(timezone.utc)
    latest=json.loads(args.latest.read_text())
    result=record_day(latest,args.archive,now=now)
    report=rollup(args.archive,ending_day=latest['utc_due_day'],now=now)
    report['archive_action']=result
    if result=='FROZEN_DAY_DRIFT_REVIEW_REQUIRED':
        report['status']='FROZEN_DAY_DRIFT_REVIEW_REQUIRED'
        report['on_time_rate']=None
    args.rollup.parent.mkdir(parents=True,exist_ok=True)
    args.rollup.write_bytes(canonical_bytes(report))
    print(json.dumps({'status':report['status'],'archive_action':result,
                      'measured_days':report['measured_days']},sort_keys=True))

if __name__=='__main__':
    main()
