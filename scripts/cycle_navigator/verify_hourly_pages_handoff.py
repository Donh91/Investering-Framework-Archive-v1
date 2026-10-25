#!/usr/bin/env python3
"""Bounded, public-only acknowledgement for existing Hourly -> Pages delivery.
Never issues forecasts or modifies source, private plane, or site state.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
POINTER_PATH = ROOT / '03_DAILY_CAPTURE_LOGS/hourly/LATEST.json'
ORIGIN = 'https://donh91.github.io/Investering-Framework-Archive-v1/data/'
UTC_RE = re.compile(r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?Z$')

class HandoffError(ValueError):
    pass

def require(condition, code):
    if not condition:
        raise HandoffError(code)

def utc(s):
    require(isinstance(s, str) and bool(UTC_RE.fullmatch(s)), 'UTC_TIMESTAMP_FORMAT_INVALID')
    try:
        return datetime.fromisoformat(s.replace('Z', '+00:00'))
    except ValueError as err:
        raise HandoffError('UTC_TIMESTAMP_INVALID') from err

def iso(value):
    return value.isoformat().replace('+00:00', 'Z')

def week_for_close(closed):
    year, week, _ = (closed - timedelta(microseconds=1)).isocalendar()
    return f'{year:04d}-W{week:02d}'

def source_hour(pointer, now):
    require(pointer.get('contract') == 'HOURLY_SEQUENCE_LATEST_POINTER_v2_2', 'SOURCE_CONTRACT')
    # SITE evidence may be PARTIAL if non-spot lanes are incomplete.
    # The market-owner writer and Intraday must never depend on this SITE gate.
    require(pointer.get('status') in ('COMPLETE','PARTIAL'), 'SOURCE_STATUS_NOT_USABLE')
    coverage = pointer.get('spot_complete_hours')
    requested = pointer.get('requested_hours')
    require(type(coverage) is int and type(requested) is int and requested > 0
            and coverage == requested, 'SOURCE_SPOT_COVERAGE_INCOMPLETE')
    close = utc(pointer.get('window_end_utc'))
    retrieved = utc(pointer.get('retrieved_at_utc'))
    require(close.minute == close.second == close.microsecond == 0, 'SOURCE_HOUR_NOT_ALIGNED')
    require(close <= now, 'SOURCE_FUTURE_CLOCK')
    require(retrieved <= now and now-retrieved <= timedelta(minutes=90),
            'SOURCE_POINTER_STALE')
    require(close <= retrieved, 'SOURCE_CUTOFF_AFTER_RETRIEVAL')
    # Anchor to retrieval time, NOT job-end time: a run crossing the hour
    # boundary must not mask otherwise source-usable spot data.
    require(close >= retrieved.replace(minute=0, second=0, microsecond=0),
            'SOURCE_HOUR_DID_NOT_ADVANCE')
    require(now-close <= timedelta(minutes=90), 'SOURCE_OLDER_THAN_SLA')
    return close

def assert_public(snapshot, lineage, expected, now):
    require(snapshot.get('schema') == 'CN_PUBLIC_SNAPSHOT_V2', 'SNAPSHOT_CONTRACT')
    precision = snapshot.get('public_live_precision') or {}
    require(precision.get('contract') == 'CN_PUBLIC_LIVE_PRICE_PRECISION_v1', 'PRECISION_CONTRACT')
    h = precision.get('hourly_price_path') or {}
    require(h.get('contract') == 'CN_PUBLIC_HOURLY_PRICE_PATH_v1', 'HOURLY_CONTRACT')
    through = utc(h.get('observed_through_utc'))
    require(expected <= through <= now, 'PUBLIC_OBSERVATION_NOT_DELIVERED')
    require(now-through <= timedelta(minutes=90), 'PUBLIC_OBSERVATION_EXCEEDS_SLA')
    project = (snapshot.get('public_series') or {}).get('current_public_projection') or {}
    week = project.get('forecast_week')
    issue = project.get('public_issue_number')
    require(isinstance(issue, int) and issue > 0 and week == week_for_close(through),
            'PUBLIC_WEEK_IDENTITY')
    require(precision.get('forecast_week') == week and precision.get('public_issue_number') == issue,
            'PUBLIC_PRECISION_ISSUE')
    require(h.get('forecast_week') == week and h.get('public_issue_number') == issue,
            'PUBLIC_HOURLY_ISSUE')
    require(lineage.get('contract') == 'CN_PUBLICATION_LINEAGE_RELEASE_RECEIPT_v1',
            'LINEAGE_CONTRACT')
    require(lineage.get('source_to_public_equality') == 'PASS', 'LINEAGE_NOT_PASS')
    require(lineage.get('forecast_week') == week and lineage.get('public_issue_number') == issue,
            'LINEAGE_ISSUE')
    require(utc(lineage.get('observed_through_utc')) == through, 'LINEAGE_CLOCK')
    require(lineage.get('prospective_forecast_points_created') == 0,
            'SYNTHETIC_FORECAST_CREATED')
    points = lineage.get('published_points') or {}
    for asset in ('BTC', 'ETH'):
        rows = h.get(asset)
        require(isinstance(rows, list) and len(rows) > 0, 'EMPTY_'+asset)
        require(points.get(asset) == len(rows), 'POINT_COUNT_'+asset)
        require(utc(rows[-1].get('observed_at_utc')) == through, 'LAST_HOUR_'+asset)
        close = rows[-1].get('close')
        require(type(close) in (int, float) and close > 0, 'CLOSE_'+asset)
    return {'state':'DELIVERED','through':iso(through),'week':week,'issue':issue,
            'btc_points':len(h['BTC']),'eth_points':len(h['ETH'])}

def get_public(filename):
    require(filename in ('latest.json', 'publication-lineage.json'), 'URL_NOT_ALLOWLISTED')
    url = ORIGIN + filename
    request = Request(url, headers={'Cache-Control':'no-cache','Pragma':'no-cache',
                                    'Accept':'application/json'})
    with urlopen(request, timeout=12) as response:
        require(response.geturl() == url and response.status == 200, 'HTTP_OR_REDIRECT')
        content = response.read(3_000_001)
    require(len(content) <= 3_000_000, 'PUBLIC_JSON_OVERSIZE')
    return json.loads(content)

def self_test():
    now=utc('2026-10-25T13:12:00Z')
    pointer={'contract':'HOURLY_SEQUENCE_LATEST_POINTER_v2_2',
             'status':'COMPLETE','window_end_utc':'2026-10-25T13:00:00Z',
             'retrieved_at_utc':'2026-10-25T13:09:00Z',
             'spot_complete_hours':26,'requested_hours':26}
    expected=source_hour(pointer,now)
    assert source_hour({**pointer,'status':'PARTIAL'},now)==expected
    assert source_hour(pointer,utc('2026-10-25T14:01:00Z'))==expected
    assert week_for_close(utc('2026-10-26T00:00:00Z'))=='2026-W43'
    assert week_for_close(utc('2026-10-26T01:00:00Z'))=='2026-W44'
    hour={'contract':'CN_PUBLIC_HOURLY_PRICE_PATH_v1','forecast_week':'2026-W43',
          'public_issue_number':30,'observed_through_utc':'2026-10-25T13:00:00Z',
          'BTC':[{'observed_at_utc':'2026-10-25T13:00:00Z','close':81000}],
          'ETH':[{'observed_at_utc':'2026-10-25T13:00:00Z','close':2200}]}
    snap={'schema':'CN_PUBLIC_SNAPSHOT_V2',
          'public_series':{'current_public_projection':{'forecast_week':'2026-W43',
                                                          'public_issue_number':30}},
          'public_live_precision':{'contract':'CN_PUBLIC_LIVE_PRICE_PRECISION_v1',
                                   'forecast_week':'2026-W43','public_issue_number':30,
                                   'hourly_price_path':hour}}
    lineage={'contract':'CN_PUBLICATION_LINEAGE_RELEASE_RECEIPT_v1',
             'source_to_public_equality':'PASS','forecast_week':'2026-W43',
             'public_issue_number':30,'observed_through_utc':'2026-10-25T13:00:00Z',
             'published_points':{'BTC':1,'ETH':1},
             'prospective_forecast_points_created':0}
    assert assert_public(snap,lineage,expected,now)['state']=='DELIVERED'
    cases=[
        (lambda:source_hour({**pointer,'window_end_utc':'2026-10-25T12:00:00Z'},now),
         'SOURCE_HOUR_DID_NOT_ADVANCE'),
        (lambda:source_hour({**pointer,'status':'FAILED'},now),'SOURCE_STATUS_NOT_USABLE'),
        (lambda:source_hour({**pointer,'status':'PARTIAL','spot_complete_hours':25},now),
         'SOURCE_SPOT_COVERAGE_INCOMPLETE'),
        (lambda:source_hour({**pointer,'window_end_utc':'2026-10-25T14:00:00Z'},now),
         'SOURCE_FUTURE_CLOCK'),
        (lambda:assert_public({**snap,'public_live_precision':{
          **snap['public_live_precision'],'hourly_price_path':{
          **hour,'observed_through_utc':'2026-10-25T12:00:00Z'}}},
          lineage,expected,now),'PUBLIC_OBSERVATION_NOT_DELIVERED'),
        (lambda:assert_public(snap,{**lineage,'source_to_public_equality':'FAIL'},
                              expected,now),'LINEAGE_NOT_PASS'),
        (lambda:assert_public(snap,{**lineage,'published_points':{'BTC':2,'ETH':1}},
                              expected,now),'POINT_COUNT_BTC'),
        (lambda:assert_public(snap,{**lineage,'observed_through_utc':'2026-10-25T12:00:00Z'},
                              expected,now),'LINEAGE_CLOCK'),
        (lambda:assert_public(snap,{**lineage,'prospective_forecast_points_created':1},
                              expected,now),'SYNTHETIC_FORECAST_CREATED'),
        (lambda:assert_public({**snap,'public_series':{
          'current_public_projection':{'forecast_week':'2026-W44','public_issue_number':31}}},
          lineage,expected,now),'PUBLIC_WEEK_IDENTITY')
    ]
    for func, expected_error in cases:
        try:
            func()
        except HandoffError as err:
            assert str(err)==expected_error, (expected_error,str(err))
        else:
            raise AssertionError('NEGATIVE_CASE_WENT_GREEN:'+expected_error)
    print('PASS Hourly->Pages handoff source freshness, W43/W44 boundary, live/public lineage, asset clocks, 9 negative cases')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--self-test',action='store_true')
    parser.add_argument('--source-only',action='store_true')
    parser.add_argument('--expected-hour-utc')
    parser.add_argument('--max-wait-seconds',type=int,default=240)
    parser.add_argument('--poll-seconds',type=int,default=12)
    args=parser.parse_args()
    if args.self_test:
        self_test()
        return
    require(0<=args.max_wait_seconds<=300 and 5<=args.poll_seconds<=60,
            'POLL_BUDGET_INVALID')
    now=datetime.now(timezone.utc)
    # When invoked from the Hourly workflow, run strictly source-only preflight.
    # Pages runs with the source-owned expected hour passed through dispatch.
    if args.source_only:
        pointer=json.loads(POINTER_PATH.read_text())
        print('CN_HOURLY_NEW_SOURCE_HOUR '+iso(source_hour(pointer,now)))
        return
    require(args.expected_hour_utc is not None,'DISPATCHED_HOUR_REQUIRED')
    expected=utc(args.expected_hour_utc)
    # A queued Pages run may be late; its delivered public observation MUST
    # still pass the actual public 90-minute SLA when checked above.
    require(expected<=now and now-expected<=timedelta(hours=24),
            'DISPATCHED_SOURCE_HOUR_INVALID')
    print('CN_PAGES_DELIVERY_ACK_STARTED '+iso(expected),flush=True)
    deadline=time.monotonic()+args.max_wait_seconds
    last='PUBLIC_NOT_READ'
    while True:
        try:
            verdict=assert_public(get_public('latest.json'),
                                  get_public('publication-lineage.json'),expected,
                                  datetime.now(timezone.utc))
            print('CN_PAGES_DELIVERY_ACK_PASS '+json.dumps(verdict,sort_keys=True),flush=True)
            return
        except (HandoffError,ValueError,OSError,TimeoutError,json.JSONDecodeError) as err:
            last=str(err) if isinstance(err,HandoffError) else type(err).__name__
        if time.monotonic()>=deadline:
            raise HandoffError('PUBLIC_DELIVERY_UNACKNOWLEDGED:'+last)
        time.sleep(min(args.poll_seconds,max(0,deadline-time.monotonic())))

if __name__=='__main__':
    try:
        main()
    except HandoffError as err:
        print('CN_PAGES_DELIVERY_ACK_FAIL '+str(err),file=sys.stderr)
        sys.exit(1)
