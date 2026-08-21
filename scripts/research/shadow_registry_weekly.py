#!/usr/bin/env python3
import argparse, json, subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / '04_MARKET_LEARNING/shadow_registry/REGISTRY.json'
OUTDIR = ROOT / '04_MARKET_LEARNING/shadow_registry/weekly'
LATEST = ROOT / '04_MARKET_LEARNING/shadow_registry/LATEST.json'


def git_last(path: str):
    p = subprocess.run(['git','log','-1','--format=%H|%cI','--',path], cwd=ROOT, text=True, capture_output=True)
    s = p.stdout.strip()
    if not s or '|' not in s:
        return {'commit': None, 'committed_at': None}
    sha, ts = s.split('|',1)
    return {'commit': sha, 'committed_at': ts}


def load_json(path: Path):
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def iso_week(now):
    y,w,_ = now.isocalendar()
    return f'{y}-W{w:02d}'


def evaluate_sensor(sensor):
    evid = []
    missing = 0
    for rel in sensor.get('evidence_paths', []):
        p = ROOT / rel
        exists = p.exists()
        if not exists: missing += 1
        evid.append({'path': rel, 'exists': exists, **git_last(rel)})
    result = {
        'sensor_id': sensor['sensor_id'],
        'family': sensor.get('family'),
        'status': sensor.get('status'),
        'registry_relevance_state': sensor.get('relevance_state'),
        'evaluator': sensor.get('evaluator'),
        'evidence': evid,
        'evidence_path_count': len(evid),
        'missing_path_count': missing,
        'calibration_readiness': 'SOURCE_MISSING' if missing else ('SCORABLE' if sensor.get('evaluator') not in (None,'NONE_RECOVERY_REQUIRED','RESEARCH_ARTIFACT_ONLY') else 'RECOVERY_REQUIRED')
    }
    if sensor['sensor_id'] == 'ENTRY_SIGNAL_LEDGER':
        perf = load_json(ROOT / '04_MARKET_LEARNING/entry_signals/PERFORMANCE_SUMMARY.json')
        if perf:
            result['entry_signal_summary'] = {
                'activation_event_count': perf.get('activation_event_count'),
                'generated_at_utc': perf.get('generated_at_utc'),
                'horizons': {k: {
                    'matured_event_count': v.get('matured_event_count'),
                    'btc_mean_return_pct': v.get('btc_mean_return_pct'),
                    'eth_mean_return_pct': v.get('eth_mean_return_pct'),
                    'matched_top100_mean_return_pct': v.get('matched_top100_mean_return_pct')
                } for k,v in (perf.get('horizons') or {}).items()}
            }
    return result


def validate_registry(reg):
    assert reg.get('authority') == 'RESEARCH_ONLY_NON_CANONICAL'
    assert reg.get('automatic_rule_changes') is False
    assert reg.get('portfolio_execution') is False
    assert reg.get('promotion_requires_separate_review') is True
    sensors = reg.get('sensors') or []
    assert sensors and len({s['sensor_id'] for s in sensors}) == len(sensors)
    for s in sensors:
        assert s.get('status') in {'ACTIVE_CANONICAL','ACTIVE_SHADOW','DORMANT_RECOVERABLE','RESEARCH_ONLY','SUPERSEDED','UNTESTABLE'}
        assert s.get('relevance_state') in {'KEEP','WATCH','REDUNDANT','NOISE','REGIME_SPECIFIC','UNTESTABLE','PROMOTION_CANDIDATE'}
    return True


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--validate-only',action='store_true'); args=ap.parse_args()
    reg=load_json(REGISTRY); assert reg, 'registry missing/invalid'
    validate_registry(reg)
    if args.validate_only:
        print('SHADOW_REGISTRY_VALIDATION_PASS'); return
    now=datetime.now(timezone.utc); week=iso_week(now)
    rows=[evaluate_sensor(s) for s in reg['sensors']]
    out={
      'contract':'SHADOW_WEEKLY_RELEVANCE_SNAPSHOT_v1',
      'week':week,
      'generated_at_utc':now.isoformat(),
      'authority':'RESEARCH_ONLY_NON_CANONICAL',
      'automatic_rule_changes':False,
      'portfolio_execution':False,
      'promotion_requires_separate_review':True,
      'anti_double_counting':'RELATED_SHADOWS_MUST_NOT_BE_TREATED_AS_INDEPENDENT_CONFIRMATIONS',
      'sensors':rows,
      'summary':{
        'sensor_count':len(rows),
        'scorable_count':sum(r['calibration_readiness']=='SCORABLE' for r in rows),
        'recovery_required_count':sum(r['calibration_readiness']=='RECOVERY_REQUIRED' for r in rows),
        'source_missing_count':sum(r['calibration_readiness']=='SOURCE_MISSING' for r in rows),
        'promotion_candidates':[r['sensor_id'] for r in rows if r['registry_relevance_state']=='PROMOTION_CANDIDATE']
      },
      'interpretation_rule':'This runtime records evidence availability and pre-registered evaluator outputs. It does not infer NOISE, REDUNDANT or PROMOTION from file presence alone.'
    }
    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR/f'{week}.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    LATEST.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out['summary'],sort_keys=True))

if __name__=='__main__': main()
