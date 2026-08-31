"""Read-only audit probes. No network, paid API calls or repository writes."""
from __future__ import annotations
import ast
import contextlib
import csv
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
RESULTS = []

def record(fid, probe, defect, **details):
    RESULTS.append(dict(id=fid, probe=probe, defect_reproduced=defect, **details))

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[name] = obj
    spec.loader.exec_module(obj)
    return obj

def read(path):
    return json.loads(Path(path).read_text())

def stamp(value):
    return datetime.fromisoformat(str(value).replace('Z', '+00:00'))

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))

def run():
    py = list(ROOT.glob('scripts/**/*.py')) + list(ROOT.glob('tests/**/*.py'))
    syntax = []
    for p in py:
        try: ast.parse(p.read_text())
        except (SyntaxError, UnicodeError) as e: syntax.append(dict(path=str(p.relative_to(ROOT)), error=type(e).__name__))
    record('SCAN', 'Python syntax', bool(syntax), checked=len(py), failures=syntax)
    json_paths = list(ROOT.rglob('*.json'))
    broken = []
    for p in json_paths:
        if '.git' in p.parts: continue
        try: read(p)
        except (ValueError, UnicodeError) as e: broken.append(dict(path=str(p.relative_to(ROOT)), error=type(e).__name__))
    record('SCAN', 'JSON parse integrity', bool(broken), checked=len(json_paths), failures=broken)

    cal = module('audit_weekly', 'scripts/api_agent/build_weekly_calibration_context.py')
    start, end = stamp('2026-08-24T00:00:00Z'), stamp('2026-08-31T00:00:00Z')
    outcome_root = ROOT/'research/framework_memory/outcome_memory'
    actual = [read(p) for p in outcome_root.rglob('*.json')]
    expected = [v for v in actual if v.get('contract') in {'MATURED_OUTCOME_v2','MATURED_OUTCOME_v3'} and v.get('created_at_utc') and start <= stamp(v['created_at_utc']) < end]
    got = cal.load_experiment_learning(ROOT/'research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json',outcome_root,start,end)
    record('H2','Actual weekly outcomes included',len(got.get('new_matured_outcomes') or []) != len(expected),eligible_count=len(expected),returned_count=len(got.get('new_matured_outcomes') or []),contract_counts=dict(Counter(v.get('contract') for v in actual)))

    entry = module('audit_entry', 'scripts/entry_signal/entry_signal_ledger.py')
    with tempfile.TemporaryDirectory() as raw:
        root=Path(raw)
        bad=root/'STATE.json';bad.write_text('{')
        try: v=entry.read_json(bad); swallowed=v is None
        except (ValueError, OSError): swallowed=False
        record('H7','Corrupt state indistinguishable from absent state',swallowed)
        entry.EVENTS=root/'events';entry.OUTCOMES=root/'outcomes'
        base_time=stamp('2026-08-01T00:00:00Z')
        baseline=dict(btc_usdt=100.,eth_usdt=100.,ethbtc=1.,constituents={'synthetic':100.})
        dump(entry.EVENTS/'event.json',dict(event_id='synthetic',event_type='ACTIVATION',event_time_utc=base_time.isoformat(),market_snapshot=baseline))
        current=dict(btc_usdt=125.,eth_usdt=125.,ethbtc=1.,constituents={'synthetic':125.},price_observation_utc=(base_time+timedelta(hours=168)).isoformat())
        entry.update_outcomes(current,base_time+timedelta(hours=168))
        value=read(entry.OUTCOMES/'synthetic.json')['horizons'].get('24h',{})
        false_label=value.get('age_hours')==168 and value.get('btc_return_since_signal_pct') is not None
        record('M4','168-hour observation stamped as 24-hour return',false_label,horizon=value)

    weekly = module('audit_hourly', 'scripts/daily_capture/build_weekly_calibration.py')
    with tempfile.TemporaryDirectory() as raw:
        root=Path(raw)
        with (root/'fixture.csv').open('w') as f:
            f.write('timestamp_utc,btc_close\n2026-08-24T00:00:00Z,100\nBROKEN,101\n2026-08-24T02:00:00Z,102\n')
        try:
            rows=weekly.load_hourly_rows(root,2026,35)
            record('M3','Valid CSV rows following malformed timestamp survive',len(rows)!=2,valid_rows=len(rows),expected=2)
        except (ValueError,OSError) as e: record('M3','Malformed CSV explicitly rejected',False,error=type(e).__name__)

    lifecycle=module('audit_lifecycle','scripts/evidence_lifecycle/validate_lifecycle_receipt.py')
    try:
        result=lifecycle.parse_time('2026-08-24T12:00:00')
        naive_ok=result.tzinfo is None
    except ValueError: naive_ok=False
    record('M13','Naive timestamp accepted by UTC lifecycle validator',naive_ok)

    close=module('audit_weekly_close','scripts/daily_capture/build_weekly_market_close_package.py')
    first=int(start.timestamp()*1000)
    candles=[[first+i*3600000,'100','110','90','105','1',first+(i+1)*3600000-1] for i in range(168)]
    candles[50]=list(candles[49])
    close.fetch_klines=lambda *args:candles
    with tempfile.TemporaryDirectory() as raw:
        argv=sys.argv
        sys.argv=['weekly-close','--output-root',raw,'--mode','final','--now-utc','2026-08-31T00:05:00Z']
        try:
            with contextlib.redirect_stdout(io.StringIO()):close.main()
            package=read(Path(raw)/'2026/W35/WEEKLY_MARKET_CLOSE_PACKAGE.json')
            record('N2','Duplicate hour masks missing hour',package['completeness']=='COMPLETE',rows=len(candles),unique_hours=len({r[0] for r in candles}),completeness=package['completeness'])
        except (ValueError,SystemExit) as e:
            record('N2','Duplicate hour explicitly rejected',False,error=str(e))
        finally:sys.argv=argv

    budgets=['check_api_lane_budget.py','check_monthly_cost_guard.py']
    for filename in budgets:
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);(root/'receipt.json').write_text('{')
            flags=['--task','DAILY_DIRECTOR_SHADOW','--cap-usd','4'] if 'lane' in filename else ['--hard-stop-usd','20']
            p=subprocess.run([sys.executable,str(ROOT/'scripts/api_agent'/filename),'--receipt-root',str(root),*flags],capture_output=True,text=True,cwd=ROOT)
            record('H4','Budget guard with truncated JSON: '+filename,p.returncode==0,exit_code=p.returncode,output=p.stdout.strip())
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);dump(root/'receipt.json',dict(task='DAILY_DIRECTOR_SHADOW',created_at_utc=datetime.now(timezone.utc).isoformat(),estimated_cost_usd=float('nan')))
            p=subprocess.run([sys.executable,str(ROOT/'scripts/api_agent'/filename),'--receipt-root',str(root),*flags],capture_output=True,text=True,cwd=ROOT)
            record('N1','Budget guard with non-finite cost: '+filename,p.returncode==0,exit_code=p.returncode,output=p.stdout.strip())

    freshness=ROOT/'scripts/api_agent/check_director_freshness.py'
    with tempfile.TemporaryDirectory() as raw:
        root=Path(raw)
        dump(root/'context.json',dict(latest_capture=dict(run_id='SYNTHETIC_UNSEEN_OLD',captured_at_utc='2026-08-08T14:01:34Z')))
        p=subprocess.run([sys.executable,str(freshness),'--context',str(root/'context.json'),'--output-root',str(root/'outputs')],capture_output=True,text=True,cwd=ROOT)
        record('D4','Freshness gate accepts unseen ancient capture','fresh_ready=true' in p.stdout,exit_code=p.returncode,output=p.stdout.strip())

    adapter=module('audit_etf','scripts/experiments/etf_absorption_transmission_v1.py')
    etf_paths=sorted((ROOT/'03_DAILY_CAPTURE_LOGS/etf').rglob('*.json'))
    versions=Counter();valid=0;rejected=Counter();logical=defaultdict(list);false_final=[]
    for path in etf_paths:
        v=read(path)
        versions[v.get('contract')]+=1
        if v.get('contract')!='DAILY_SETTLED_ETF_CALIBRATION_v2':continue
        try:adapter.validate_owner_record(path);valid+=1
        except ValueError as e:rejected[str(e).split(':')[0]]+=1
        for row in v.get('rows',[]):
            logical[(row.get('date'),row.get('asset'))].append(dict(path=str(path.relative_to(ROOT)),retrieved_at_utc=v.get('retrieved_at_utc'),total=row.get('reported_total'),final=row.get('session_final'),unknown=sum(x is None for x in row.get('fund_values',[]))))
            if row.get('session_final') and any(x is None for x in row.get('fund_values',[])):
                false_final.append(dict(path=str(path.relative_to(ROOT)),asset=row.get('asset'),session_date=row.get('date'),unknown=row.get('unknown_fund_cell_count')))
    conflicts=[dict(session_date=k[0],asset=k[1],versions=vs) for k,vs in logical.items() if len({x['total'] for x in vs if x['final']})>1]
    record('H3','Validate real ETF owner records',valid==0,accepted=valid,rejected=dict(rejected),contracts=dict(versions))
    record('D1','Conflicting final ETF totals',bool(conflicts),logical_rows=len(logical),conflicts=conflicts)
    record('D2','Final ETF rows contain unknown fund values',bool(false_final),rows=false_final)

    execution=read(ROOT/'LATEST_CODEX_EXECUTION_STATE.json')
    receipt_counts=defaultdict(Counter); missing=[]
    for row in execution.get('tasks',[]):
        path=row.get('transition_receipt_path')
        if not path:continue
        exists=(ROOT/path).is_file();state=row.get('state')
        receipt_counts[state]['exists' if exists else 'absent']+=1
        if not exists:missing.append(dict(signature=row.get('signature'),state=state,path=path))
    record('D3','Transition paths by lifecycle state',None,counts={k:dict(v) for k,v in receipt_counts.items()},missing=missing)

    observations=defaultdict(list)
    for path in (ROOT/'research/experiment_lifecycle/observations').rglob('*.json'):
        v=read(path); observations[(v.get('candidate_id'),v.get('observed_at_utc'))].append((str(path.relative_to(ROOT)),v))
    duplicate_keys=[k for k,v in observations.items() if len(v)>1]
    conflicting=[]
    for k,vs in observations.items():
        states={v.get('state') or v.get('evaluation_status') or v.get('status') for _,v in vs}
        if len(states)>1: conflicting.append(dict(candidate_id=k[0],observed_at_utc=k[1],states=sorted(map(str,states)),records=len(vs)))
    record('D7','Duplicate candidate/time observation keys',bool(duplicate_keys),files=sum(len(v) for v in observations.values()),distinct_keys=len(observations),duplicate_keys=len(duplicate_keys),redundant_records=sum(len(v)-1 for v in observations.values()))
    record('D5','Conflicting candidate/time observation verdicts',bool(conflicting),conflicts=conflicting)

    from jsonschema import Draft202012Validator
    cases=[('H5','02_DATA_PING/operational_handoffs/accepted_log_receipt.schema.json','02_DATA_PING/operational_handoffs/accepted_logs/**/*.json'),('H10','03_WEEKLY_OPERATIONS/master_monday/process/master_monday_run_receipt.schema.json','03_WEEKLY_OPERATIONS/master_monday/*/run_receipt*.json'),('M6','research/codex/CODEX_RESEARCH_CANDIDATE.schema.json','research/codex/intake/**/*.json')]
    for fid,schema,pattern in cases:
        validator=Draft202012Validator(read(ROOT/schema));fails=[];paths=list(ROOT.glob(pattern))
        for p in paths:
            errs=list(validator.iter_errors(read(p)))
            if errs:fails.append(dict(path=str(p.relative_to(ROOT)),errors=[str(e.json_path)+': '+e.message for e in errs]))
        record(fid,'Archive schema validation',bool(fails),checked=len(paths),failed=len(fails),failures=fails)

    result=dict(contract='INDEPENDENT_CODE_AUDIT_v1',base_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),generated_at_utc=datetime.now(timezone.utc).isoformat(),scope='CONTROL_PLANE_ONLY_NO_ROUND3_ANALYSIS',probes=RESULTS)
    print(json.dumps(result,indent=2,allow_nan=False))

if __name__=='__main__':run()
