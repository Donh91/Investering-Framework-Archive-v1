import importlib.util, json
from datetime import date,datetime,timedelta,timezone
from pathlib import Path
import pytest
spec=importlib.util.spec_from_file_location('t2',str(Path(__file__).parents[2] / '04_MARKET_LEARNING/handlekompas/research/2026-10-21__task2_hourly_source_7d_rollup_v1.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
NOW=datetime(2026,10,21,10,tzinfo=timezone.utc)

def build(day='2026-10-19',late_hour=None):
    mid=datetime.combine(date.fromisoformat(day),datetime.min.time(),timezone.utc)
    records=[]
    for h in range(24):
        due=mid+timedelta(hours=h); start=due-timedelta(hours=1)
        delay=120 if h==late_hour else 20
        seen=due+timedelta(minutes=delay)
        records.append({'classification':('FIRST_COMMIT_CLOCK_AFTER_90M' if h==late_hour else 'FIRST_COMMIT_CLOCK_WITHIN_90M'),
                        'due_at_utc':m.utc_time(m.utc_time(due.isoformat().replace('+00:00','Z')).isoformat().replace('+00:00','Z')).strftime('%Y-%m-%dT%H:%M:%SZ'),
                        'source_open_at_utc':start.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        'source_path':'03_DAILY_CAPTURE_LOGS/hourly/'+start.strftime('%Y/%m/%Y-%m-%d.csv'),
                        'first_present_main_commit':'a'*40,
                        'first_present_committer_utc':seen.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        'minutes_after_due':float(delay)})
    return {'contract':m.CONTRACT,'utc_due_day':day,'authority':dict(m.AUTHORITY),
            'evidence_semantics':m.SEMANTICS,'main_first_parent_ref_sha':'b'*40,
            'expected_due_hours':24,'records':records,'first_commit_clock_within_90m':23 if late_hour is not None else 24,
            'first_commit_clock_after_90m':1 if late_hour is not None else 0,
            'not_present_in_first_parent_history':0,'clock_anomalies':0}

def test_measured_midnight_and_denominator():
    v=m.validate_day(build(),now=NOW)
    assert v['counts']['first_commit_clock_within_90m']==24

def test_missing_seven_day_denominator_not_synthetic_rate(tmp_path):
    m.record_day(build(),tmp_path,now=NOW)
    s=m.rollup(tmp_path,ending_day='2026-10-19',now=NOW)
    assert s['measured_days']==1 and s['on_time_rate'] is None
    assert s['status']=='INCOMPLETE_DO_NOT_CALCULATE_RATE'

def test_complete_seven_day_rate_and_late(tmp_path):
    for i in range(7):
        day=(date(2026,10,19)-timedelta(days=i)).isoformat()
        m.record_day(build(day,late_hour=2 if i==2 else None),tmp_path,now=NOW)
    s=m.rollup(tmp_path,ending_day='2026-10-19',now=NOW)
    assert s['measured_days']==7 and s['on_time_rate']==round(167/168,6)
    assert s['after_90m']==1 and s['within_90m']==167
    assert s['scientific_admission'].startswith('BLOCKED')

def test_frozen_duplicate_new_run_timestamps_same_day(tmp_path):
    a=build();m.record_day(a,tmp_path,now=NOW)
    b=build();b['evaluated_at_utc']='2026-10-20T23:12:00Z';b['main_first_parent_ref_sha']='c'*40
    assert m.record_day(b,tmp_path,now=NOW)=='ALREADY_RECORDED_IDENTICAL_EVIDENCE'
    b['records'][2]['first_present_main_commit']='d'*40
    assert m.record_day(b,tmp_path,now=NOW)=='FROZEN_DAY_DRIFT_REVIEW_REQUIRED'
    assert json.loads((tmp_path/'2026-10-19.json').read_text())['records'][2]['first_present_main_commit']=='a'*40

@pytest.mark.parametrize('mutation,reason',[
    (lambda x:x['records'].pop(), 'NOT_24_DUE_HOURS'),
    (lambda x:x['records'][0].update(due_at_utc='2026-10-19T01:00:00Z'),'DUPLICATE_MISSING'),
    (lambda x:x['records'][0].update(btc_close=100),'INVALID_OR_PRIVATE'),
    (lambda x:x['records'][0].update(spot_price=123),'INVALID_OR_PRIVATE'),
    (lambda x:x.update(raw_market_data='SECRET'),'UNKNOWN_DAILY_ROOT_FIELD'),
    (lambda x:x.update(first_commit_clock_within_90m=0),'TAMPERED'),
    (lambda x:x['records'][1].update(minutes_after_due=12.0),'CLOCK_LAG_MISMATCH'),
    (lambda x:x['records'][1].update(classification='FIRST_COMMIT_CLOCK_AFTER_90M'),'MISCLASSIFIED_DEADLINE'),
    (lambda x:x.update(evidence_semantics='PROVIDER_FIRST_KNOWN'),'NOT_COMMIT_CLOCK_PROXY'),
    (lambda x:x['authority'].update(portfolio_action=True),'AUTHORITY_NOT_RESEARCH_ONLY'),
    (lambda x:x['records'][0].update(source_path='03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-19.csv'),'INCORRECT_MIDNIGHT'),
])
def test_strict_fail_closed(mutation,reason):
    x=build();mutation(x)
    with pytest.raises(ValueError,match=reason):m.validate_day(x,now=NOW)

def test_unavailable_not_zero(tmp_path):
    x={'contract':m.CONTRACT,'utc_due_day':'2026-10-19',
       'authority':dict(m.AUTHORITY),'measurement_status':'UNAVAILABLE',
       'reason':'SOURCE_GIT_HISTORY_OR_VALIDATION_UNAVAILABLE'}
    assert m.record_day(x,tmp_path,now=NOW)=='NEW_DAY_FROZEN'
    s=m.rollup(tmp_path,ending_day='2026-10-19',now=NOW)
    assert s['measured_days']==0 and s['on_time_rate'] is None

def test_future_day_rejected():
    with pytest.raises(ValueError,match='DAY_NOT_COMPLETE'):
        m.validate_day(build('2026-10-21'),now=NOW)
