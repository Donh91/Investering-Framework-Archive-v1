#!/usr/bin/env python3
import argparse, hashlib, json, math, os, subprocess, tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / '04_MARKET_LEARNING/shadow_registry/REGISTRY.json'
OUTDIR = ROOT / '04_MARKET_LEARNING/shadow_registry/weekly'
LATEST = ROOT / '04_MARKET_LEARNING/shadow_registry/LATEST.json'
SCHEMA_PATH = ROOT / '06_RESEARCH_LAB/historical_sensor_recovery_v1/SHADOW_SENSOR_REGISTRY_SCHEMA.json'
ENTRY_OUTPUT = '04_MARKET_LEARNING/entry_signals/PERFORMANCE_SUMMARY.json'
ENTRY_PRODUCER = 'scripts/entry_signal/entry_signal_ledger.py'


def git_last(path: str):
    p = subprocess.run(['git','log','-1','--format=%H|%cI','--',path], cwd=ROOT, text=True, capture_output=True)
    s = p.stdout.strip()
    if not s or '|' not in s:
        return {'commit': None, 'committed_at': None}
    sha, ts = s.split('|',1)
    return {'commit': sha, 'committed_at': ts}


def load_json(path: Path):
    try:
        return json.loads(path.read_text(), parse_constant=reject_nonfinite)
    except (OSError, UnicodeError, ValueError):
        return None


def reject_nonfinite(value):
    raise ValueError('non-finite JSON number')


def entry_evaluator_binding(sensor):
    """Bind only the existing evaluator, never infer one from a label/path."""
    result = {'status': 'UNAVAILABLE', 'reason': 'NO_REGISTERED_EVALUATOR_BINDING',
              'scientific_validity': 'NOT_CERTIFIED_BY_REGISTRY'}
    if sensor.get('sensor_id') != 'ENTRY_SIGNAL_LEDGER' or sensor.get('evaluator') != 'ENTRY_SIGNAL_PERFORMANCE_SUMMARY_v1':
        return result, None
    output = ROOT / ENTRY_OUTPUT
    producer = ROOT / ENTRY_PRODUCER
    try:
        raw = output.read_bytes()
        value = json.loads(raw, parse_constant=reject_nonfinite)
    except (OSError, UnicodeError, ValueError):
        raw, value = b'', None
    if not producer.is_file() or not isinstance(value, dict):
        result['reason'] = 'EVALUATOR_OUTPUT_OR_PRODUCER_UNAVAILABLE'
        return result, None
    count = value.get('activation_event_count')
    horizons = value.get('horizons')
    valid = (value.get('contract') == sensor['evaluator']
             and type(count) is int and count >= 0
             and isinstance(horizons, dict) and bool(horizons))
    try:
        stamp = datetime.fromisoformat(value['generated_at_utc'].replace('Z', '+00:00'))
        valid = valid and stamp.utcoffset() is not None
    except (KeyError, TypeError, AttributeError, ValueError):
        valid = False
    if isinstance(horizons, dict):
        for row in horizons.values():
            if not isinstance(row, dict):
                valid = False
                continue
            matured = row.get('matured_event_count')
            if type(matured) is not int or matured < 0 or type(count) is not int or matured > count:
                valid = False
            for key in ('btc_mean_return_pct', 'eth_mean_return_pct', 'matched_top100_mean_return_pct'):
                x = row.get(key)
                if key not in row or (x is not None and (type(x) not in (int, float) or not math.isfinite(x))):
                    valid = False
    if not valid:
        result['reason'] = 'EVALUATOR_OUTPUT_CONTRACT_INVALID'
        return result, None
    result.update(status='PASS', reason='REGISTERED_EVALUATOR_OUTPUT_VALID',
                  contract=value['contract'], output_path=ENTRY_OUTPUT,
                  producer_path=ENTRY_PRODUCER,
                  output_sha256=hashlib.sha256(raw).hexdigest(),
                  producer_sha256=hashlib.sha256(producer.read_bytes()).hexdigest(),
                  validation_scope='OUTPUT_CONTRACT_SHAPE_NOT_OUTCOME_ACCURACY')
    return result, value


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
    binding, perf = entry_evaluator_binding(sensor)
    result = {
        'sensor_id': sensor['sensor_id'],
        'family': sensor.get('family'),
        'status': sensor.get('status'),
        'registry_relevance_state': sensor.get('relevance_state'),
        'evaluator': sensor.get('evaluator'),
        'evidence': evid,
        'evidence_path_count': len(evid),
        'missing_path_count': missing,
        'evaluator_binding': binding,
        'calibration_readiness': 'SOURCE_MISSING' if missing else ('SCORABLE' if binding['status'] == 'PASS' else 'RECOVERY_REQUIRED')
    }
    if perf is not None:
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
    schema = load_json(SCHEMA_PATH)
    if not isinstance(schema, dict) or schema.get('schema_version') != 'SHADOW_SENSOR_REGISTRY_v1':
        raise ValueError('shadow registry owner schema missing/invalid')
    if not isinstance(reg, dict) or reg.get('authority') != 'RESEARCH_ONLY_NON_CANONICAL':
        raise ValueError('shadow registry authority invalid')
    for field, required in schema['authority'].items():
        if reg.get(field) is not required:
            raise ValueError('shadow registry authority invalid: ' + field)
    sensors = reg.get('sensors') or []
    if not isinstance(sensors, list) or not sensors or any(not isinstance(s, dict) for s in sensors):
        raise ValueError('shadow registry sensors missing/invalid')
    identifiers = set()
    list_fields = {'source_definition_paths', 'input_sources', 'outcome_horizons',
                   'known_overlap_with_canonical', 'data_quality_limitations'}
    for s in sensors:
        for field in schema['required_sensor_fields']:
            if field not in s:
                raise ValueError('missing sensor field: ' + field)
            value = s[field]
            if field in list_fields:
                if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value):
                    raise ValueError('invalid sensor list: ' + field)
            elif field == 'forward_observation_enabled':
                if type(value) is not bool:
                    raise ValueError('invalid forward observation flag')
            elif not isinstance(value, str) or not value.strip():
                raise ValueError('invalid sensor field: ' + field)
        if s['sensor_id'] in identifiers:
            raise ValueError('duplicate sensor_id')
        identifiers.add(s['sensor_id'])
        if s['status'] not in schema['allowed_status']:
            raise ValueError('invalid sensor status')
        if s['relevance_state'] not in schema['allowed_relevance_state']:
            raise ValueError('invalid sensor relevance_state')
        if not s['source_definition_paths']:
            raise ValueError('sensor definition provenance missing')
        for rel in s['source_definition_paths']:
            p = (ROOT / rel).resolve()
            if not p.is_relative_to(ROOT.resolve()) or not p.is_file():
                raise ValueError('sensor definition source unavailable: ' + rel)
        if not isinstance(s.get('evidence_paths'), list) or not s['evidence_paths']:
            raise ValueError('sensor evidence paths missing')
        for rel in s['evidence_paths']:
            if not isinstance(rel, str) or not rel.strip() or not (ROOT / rel).resolve().is_relative_to(ROOT.resolve()):
                raise ValueError('invalid sensor evidence path')
    return True


def persist_snapshot(out):
    """Keep the first weekly evidence immutable; refresh only the LATEST view."""
    body = json.dumps(out, indent=2, sort_keys=True, allow_nan=False) + '\n'
    OUTDIR.mkdir(parents=True, exist_ok=True)
    weekly_path = OUTDIR / (out['week'] + '.json')
    try:
        with weekly_path.open('x') as fh:
            fh.write(body)
        disposition = 'CREATED'
    except FileExistsError:
        existing = load_json(weekly_path)
        if not isinstance(existing, dict) or existing.get('week') != out['week']:
            raise ValueError('existing weekly snapshot invalid; preserved without replacement')
        disposition = 'PRESERVED_EXISTING'
    LATEST.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', dir=LATEST.parent, delete=False) as fh:
        temporary = Path(fh.name)
        fh.write(body)
    try:
        os.replace(temporary, LATEST)
    finally:
        temporary.unlink(missing_ok=True)
    return disposition


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--validate-only',action='store_true'); args=ap.parse_args()
    reg=load_json(REGISTRY)
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
    disposition = persist_snapshot(out)
    print(json.dumps({**out['summary'], 'weekly_snapshot_persistence': disposition},sort_keys=True))

if __name__=='__main__': main()
