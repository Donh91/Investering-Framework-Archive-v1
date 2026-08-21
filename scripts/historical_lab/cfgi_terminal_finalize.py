#!/usr/bin/env python3
from __future__ import annotations

import gzip
import json
from pathlib import Path

import cfgi_readiness_postprocess_v3 as v3

ROOT = Path('06_RESEARCH_LAB/historical_altseason_pullback_v1')
ART = ROOT / 'artifacts'
CONFIG = ROOT / 'config.json'
TERMINAL = Path('00_ARCHIVE_CONTROL/research_runtime/CFGI_MARKET_PROVIDER_TERMINAL_RECEIPT.json')


def main() -> None:
    cfg = json.loads(CONFIG.read_text())
    billing = json.loads((ART / 'CFGI_BILLING.json').read_text())
    cumulative = json.loads((ART / 'CFGI_CUMULATIVE_BILLING.json').read_text())
    terminal = json.loads(TERMINAL.read_text())
    events = billing.get('selected_events') or []
    if not events:
        raise SystemExit('CFGI_selected_events_missing')

    assert terminal['contract'] == 'CFGI_MARKET_PROVIDER_TERMINAL_RECEIPT_v1'
    assert terminal['status'] == 'TERMINAL_PROVIDER_NO_HISTORICAL_ROWS'
    assert terminal['requested_symbols'] == ['MARKET']
    assert terminal['returned_symbols'] == [] and terminal['returned_row_count'] == 0
    assert terminal['preserved_existing_symbols'] == ['BTC', 'ETH']
    assert terminal['no_fill'] is True and terminal['no_interpolation'] is True and terminal['no_proxy_substitution'] is True
    assert terminal['no_additional_paid_retry_authorized'] is True
    assert terminal['verified_prior_cumulative_actual_credits_used'] == cumulative['cumulative_actual_credits_used'] == 10518
    assert terminal['conservative_cumulative_credit_upper_bound'] <= cfg['cfgi']['expected_credit_hard_cap']
    assert terminal['conservative_credits_remaining_lower_bound'] >= cfg['cfgi']['minimum_credits_reserve']

    raw = v3.read_jsonl_gz(ART / 'cfgi_targeted.jsonl.gz')
    coverage, path_rows, structural = v3.build(cfg, events, raw)
    (ART / 'CFGI_FIELD_COVERAGE.json').write_text(json.dumps(coverage, indent=2, sort_keys=True) + '\n')
    with gzip.open(ART / 'CFGI_EVENT_PATHS.jsonl.gz', 'wt', encoding='utf-8') as fh:
        for row in path_rows:
            fh.write(json.dumps(row, sort_keys=True) + '\n')

    manifest = v3.build_manifest(cfg, billing, coverage, structural)
    market_blocker = 'CFGI_REQUIRED_SYMBOL_ZERO_ASOF_COVERAGE:MARKET'
    blockers = [x for x in manifest.get('blockers', []) if x != market_blocker]
    warnings = list(manifest.get('warnings', []))
    warnings.append('CFGI_MARKET_HISTORICAL_PROVIDER_UNAVAILABLE:MARKET:NOT_TESTABLE')

    for sym in ['BTC', 'ETH']:
        if int(coverage['symbol_coverage'][sym].get('asof_available_slots') or 0) <= 0:
            blockers.append(f'CFGI_REQUIRED_OBSERVED_SYMBOL_ZERO_ASOF_COVERAGE:{sym}')
    if int(coverage['symbol_coverage']['MARKET'].get('asof_available_slots') or 0) != 0:
        blockers.append('CFGI_TERMINAL_PROVIDER_RECEIPT_CONFLICT_MARKET_ROWS_PRESENT')

    terminal_gap = {
        'contract': 'CFGI_MARKET_GAPFILL_BILLING_v2_TERMINAL',
        'status': 'TERMINAL_PROVIDER_NO_HISTORICAL_ROWS',
        'input_fingerprint_sha256': terminal['input_fingerprint_sha256'],
        'enrichment_run_id': terminal['enrichment_run_id'],
        'requested_symbols': ['MARKET'],
        'returned_symbols': [],
        'row_count': 0,
        'preserved_existing_symbols': ['BTC', 'ETH'],
        'actual_credits_used_from_headers': None,
        'credit_accounting_status': terminal['failed_run_credit_accounting_status'],
        'verified_prior_cumulative_actual_credits_used': terminal['verified_prior_cumulative_actual_credits_used'],
        'conservative_additional_credit_upper_bound': terminal['conservative_additional_credit_upper_bound'],
        'conservative_cumulative_credit_upper_bound': terminal['conservative_cumulative_credit_upper_bound'],
        'conservative_credits_remaining_lower_bound': terminal['conservative_credits_remaining_lower_bound'],
        'hard_cap_credits': terminal['hard_cap_credits'],
        'minimum_reserve_credits': terminal['minimum_reserve_credits'],
        'historical_availability': 'NOT_TESTABLE_PROVIDER_UNAVAILABLE',
        'no_fill': True,
        'no_interpolation': True,
        'no_proxy_substitution': True,
        'no_additional_paid_retry_authorized': True,
    }
    (ART / 'CFGI_MARKET_GAPFILL_BILLING.json').write_text(json.dumps(terminal_gap, indent=2, sort_keys=True) + '\n')

    manifest['contract'] = 'RESEARCH_READINESS_MANIFEST_v3_1_PROVIDER_BOUNDED'
    manifest['warnings'] = sorted(set(warnings))
    manifest['blockers'] = sorted(set(blockers))
    manifest['readiness_verdict'] = 'PASS' if not blockers else 'FAIL'
    manifest['cfgi']['market_historical_availability'] = 'NOT_TESTABLE_PROVIDER_UNAVAILABLE'
    manifest['cfgi']['market_terminal_receipt'] = str(TERMINAL)
    manifest['cfgi']['required_observed_symbols'] = ['BTC', 'ETH']
    manifest['cfgi']['provider_unavailable_symbols'] = ['MARKET']
    manifest['cfgi']['missingness_policy'] = 'EXPLICIT_MISSING_NOT_FILLED_NOT_INTERPOLATED_PROVIDER_UNAVAILABLE_SLICES_NOT_TESTABLE'
    manifest['cfgi']['analysis_eligibility_policy'] = 'BTC_ETH_CFGI_SLICES_ELIGIBLE_WHERE_SUPPORTED_MARKET_CFGI_SLICES_NOT_TESTABLE'
    manifest['cfgi']['billing_accounting'] = {
        'verified_cumulative_actual_credits_used': terminal['verified_prior_cumulative_actual_credits_used'],
        'failed_gapfill_actual_credits_used_from_headers': None,
        'conservative_cumulative_credit_upper_bound': terminal['conservative_cumulative_credit_upper_bound'],
        'conservative_credits_remaining_lower_bound': terminal['conservative_credits_remaining_lower_bound'],
    }
    manifest['automatic_promotion'] = False
    manifest['historical_findings_max_classification'] = 'FORWARD_TEST'

    for name in ['CFGI_FIELD_COVERAGE.json', 'CFGI_EVENT_PATHS.jsonl.gz', 'CFGI_MARKET_GAPFILL_BILLING.json']:
        p = ART / name
        manifest['artifact_state'][name] = {'exists': True, 'bytes': p.stat().st_size, 'sha256': v3.sha256(p)}

    (ART / 'RESEARCH_READINESS_MANIFEST.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    print(json.dumps({
        'status': manifest['readiness_verdict'],
        'contract': manifest['contract'],
        'market': manifest['cfgi']['market_historical_availability'],
        'btc_asof': coverage['symbol_coverage']['BTC']['asof_available_slots'],
        'eth_asof': coverage['symbol_coverage']['ETH']['asof_available_slots'],
        'market_asof': coverage['symbol_coverage']['MARKET']['asof_available_slots'],
        'blockers': manifest['blockers'],
        'conservative_cumulative_credit_upper_bound': terminal['conservative_cumulative_credit_upper_bound'],
    }, sort_keys=True))
    if manifest['readiness_verdict'] != 'PASS':
        raise SystemExit(2)


if __name__ == '__main__':
    main()
