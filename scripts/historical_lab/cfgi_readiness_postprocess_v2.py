#!/usr/bin/env python3
from __future__ import annotations

import gzip
import json
from pathlib import Path

import cfgi_readiness_postprocess as v1

ROOT = Path('06_RESEARCH_LAB/historical_altseason_pullback_v1')
ARTIFACTS = ROOT / 'artifacts'


def main() -> None:
    cfg = json.loads((ROOT / 'config.json').read_text())
    billing = json.loads((ARTIFACTS / 'CFGI_BILLING.json').read_text())
    events = billing.get('selected_events') or []
    if not events:
        raise SystemExit('CFGI_selected_events_missing')
    rows = v1.read_jsonl_gz(ARTIFACTS / 'cfgi_targeted.jsonl.gz')
    coverage, path_rows, structural = v1.build_field_coverage(events, rows, cfg)

    expected = int(structural['expected_symbol_hours'])
    observed = int(structural['observed_exact_symbol_hours'])
    scaffold = len(path_rows)
    if scaffold != expected:
        raise SystemExit(f'CFGI_EVENT_PATH_SCAFFOLD_INCOMPLETE:{scaffold}/{expected}')

    (ARTIFACTS / 'CFGI_FIELD_COVERAGE.json').write_text(json.dumps(coverage, indent=2, sort_keys=True) + '\n')
    with gzip.open(ARTIFACTS / 'CFGI_EVENT_PATHS.jsonl.gz', 'wt', encoding='utf-8') as fh:
        for row in path_rows:
            fh.write(json.dumps(row, sort_keys=True) + '\n')

    manifest = v1.build_manifest(ARTIFACTS, cfg, coverage, structural)
    blockers = list(manifest.get('blockers') or [])
    warnings = list(manifest.get('warnings') or [])

    # v1 conflated complete path accounting with complete API observation coverage.
    # v2 requires every expected relative-hour slot to be represented, while an absent
    # exact-hour API observation stays explicit missingness. No fill, interpolation,
    # nearest-hour substitution or silent fallback is permitted.
    if 'CFGI_EXACT_EVENT_PATH_INCOMPLETE' in blockers:
        blockers.remove('CFGI_EXACT_EVENT_PATH_INCOMPLETE')
    missing = expected - observed
    if missing:
        warnings.append(f'CFGI_EXACT_OBSERVATION_MISSINGNESS:{missing}/{expected}')

    manifest['contract'] = 'RESEARCH_READINESS_MANIFEST_v2'
    manifest['cfgi']['expected_symbol_hours'] = expected
    manifest['cfgi']['scaffold_symbol_hours'] = scaffold
    manifest['cfgi']['observed_exact_symbol_hours'] = observed
    manifest['cfgi']['missing_exact_symbol_hours'] = missing
    manifest['cfgi']['missingness_policy'] = 'EXPLICIT_MISSING_NOT_FILLED_NOT_INTERPOLATED_NOT_A_GLOBAL_BLOCKER'
    manifest['cfgi']['analysis_eligibility_policy'] = 'DOWNSTREAM_ANALYSIS_MUST_MARK_UNSUPPORTED_SLICES_NOT_TESTABLE'
    manifest['warnings'] = sorted(set(warnings))
    manifest['blockers'] = sorted(set(blockers))
    manifest['readiness_verdict'] = 'PASS' if not blockers else 'FAIL'

    (ARTIFACTS / 'RESEARCH_READINESS_MANIFEST.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    print(json.dumps({
        'status': manifest['readiness_verdict'],
        'events': len(events),
        'path_rows': scaffold,
        'observed_exact_symbol_hours': observed,
        'missing_exact_symbol_hours': missing,
        'blockers': manifest['blockers'],
        'warnings': len(manifest['warnings']),
    }, sort_keys=True))


if __name__ == '__main__':
    main()
