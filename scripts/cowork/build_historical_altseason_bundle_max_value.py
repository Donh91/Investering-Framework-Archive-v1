#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import build_historical_altseason_bundle as base

REPO=base.REPO
LAB=REPO/'06_RESEARCH_LAB'/'historical_altseason_pullback_v1'
ART=LAB/'artifacts'
PROMPT_DIR=REPO/'07_PROMPTS_AND_AGENTS'/'historical_altseason_pullback'
DIST=base.DIST
ZIP_PATH=base.ZIP_PATH
MANIFEST_PATH=base.MANIFEST_PATH
SHA_PATH=base.SHA_PATH
STAGE=DIST/'COWORK_RESEARCH_HANDOFF'
RUNTIME=REPO/'00_ARCHIVE_CONTROL'/'research_runtime'
LEDGER=RUNTIME/'HISTORICAL_ALTSEASON_CFGI_PAID_ATTEMPT_LEDGER.json'
GAP_AUTH=RUNTIME/'HISTORICAL_ALTSEASON_CFGI_MARKET_GAPFILL_AUTHORIZATION.json'
TERMINAL=RUNTIME/'CFGI_MARKET_PROVIDER_TERMINAL_RECEIPT.json'
LIMITATION=PROMPT_DIR/'COWORK_CFGI_PROVIDER_LIMITATION.md'

HANDOFF_FILES=[
    base.PROMPT,
    PROMPT_DIR/'COWORK_OPUS5_LAUNCH_INSTRUCTION.md',
    PROMPT_DIR/'COWORK_OPUS5_MAX_VALUE_SIDECARS.md',
    PROMPT_DIR/'COWORK_GITHUB_RESEARCH_MAP.md',
    LIMITATION,
    LAB/'COWORK_READINESS_PROTOCOL.md',
    LAB/'COWORK_OPUS5_RESEARCH_PROTOCOL_ADDENDUM.md',
    LAB/'INTRADAY_EXECUTION_COWORK_ADDENDUM.md',
    LAB/'CLAUDE_COWORK_DEEP_RESEARCH_BRIEF.md',
    LAB/'config.json',
    ART/'RESEARCH_READINESS_MANIFEST.json',
    ART/'CFGI_BILLING.json',
    ART/'CFGI_CUMULATIVE_BILLING.json',
    ART/'CFGI_MARKET_GAPFILL_BILLING.json',
    ART/'CFGI_FIELD_COVERAGE.json',
    ART/'CFGI_COVERAGE.json',
    ART/'FREE_BULK_ARTIFACT_POINTER.json',
    ART/'FREE_SOURCE_AUDIT.json',
    ART/'TIME_INTEGRITY_AUDIT.json',
    RUNTIME/'HISTORICAL_ALTSEASON_CFGI_PAID_RESERVATION.json',
    LEDGER,
    GAP_AUTH,
    TERMINAL,
]


def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda:fh.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()


def validate_provider_bounded()->dict:
    cfg=json.loads((LAB/'config.json').read_text())
    cumulative=json.loads((ART/'CFGI_CUMULATIVE_BILLING.json').read_text())
    ledger=json.loads(LEDGER.read_text())
    reservation=json.loads((RUNTIME/'HISTORICAL_ALTSEASON_CFGI_PAID_RESERVATION.json').read_text())
    gap=json.loads((ART/'CFGI_MARKET_GAPFILL_BILLING.json').read_text())
    terminal=json.loads(TERMINAL.read_text())
    readiness=json.loads((ART/'RESEARCH_READINESS_MANIFEST.json').read_text())

    fp=ledger['input_fingerprint_sha256']
    assert cumulative['contract']=='HISTORICAL_ALTSEASON_CFGI_CUMULATIVE_BILLING_v1' and cumulative['status']=='PASS'
    assert ledger['contract']=='HISTORICAL_ALTSEASON_CFGI_PAID_ATTEMPT_LEDGER_v2'
    assert fp==cumulative['input_fingerprint_sha256']==reservation['input_fingerprint_sha256']==gap['input_fingerprint_sha256']==terminal['input_fingerprint_sha256']
    assert ledger['cumulative_actual_credits_used']==cumulative['cumulative_actual_credits_used']==terminal['verified_prior_cumulative_actual_credits_used']==10518
    assert terminal['status']=='TERMINAL_PROVIDER_NO_HISTORICAL_ROWS'
    assert terminal['requested_symbols']==['MARKET'] and terminal['returned_symbols']==[] and terminal['returned_row_count']==0
    assert terminal['preserved_existing_symbols']==['BTC','ETH'] and terminal['no_additional_paid_retry_authorized'] is True
    assert terminal['conservative_cumulative_credit_upper_bound']<=cfg['cfgi']['expected_credit_hard_cap']
    assert terminal['conservative_credits_remaining_lower_bound']>=cfg['cfgi']['minimum_credits_reserve']
    assert gap['contract']=='CFGI_MARKET_GAPFILL_BILLING_v2_TERMINAL' and gap['status']=='TERMINAL_PROVIDER_NO_HISTORICAL_ROWS'
    assert gap['requested_symbols']==['MARKET'] and gap['returned_symbols']==[] and gap['preserved_existing_symbols']==['BTC','ETH']
    assert readiness['contract']=='RESEARCH_READINESS_MANIFEST_v3_1_PROVIDER_BOUNDED'
    assert readiness['readiness_verdict']=='PASS' and not readiness['blockers']
    assert readiness['cfgi']['time_alignment_contract']=='CFGI_ASOF_1H_NO_LOOKAHEAD_v1' and readiness['cfgi']['no_lookahead'] is True
    assert readiness['cfgi']['market_historical_availability']=='NOT_TESTABLE_PROVIDER_UNAVAILABLE'
    assert readiness['cfgi']['symbol_coverage']['MARKET']['asof_available_slots']==0
    for sym in ['BTC','ETH']:
        assert readiness['cfgi']['symbol_coverage'][sym]['asof_available_slots']>0,sym
    assert readiness['automatic_promotion'] is False and readiness['historical_findings_max_classification']=='FORWARD_TEST'
    return {'cumulative':cumulative,'terminal':terminal,'readiness':readiness}


def main()->int:
    base.validate_readiness()
    v=validate_provider_bounded()
    for path in HANDOFF_FILES:
        if not path.exists() or not path.is_file() or path.stat().st_size==0:
            raise SystemExit(f'COWORK_COMPACT_HANDOFF_BLOCKED missing={path.relative_to(REPO)}')
    if DIST.exists():
        shutil.rmtree(DIST)
    STAGE.mkdir(parents=True,exist_ok=True)
    files=[]
    for src in HANDOFF_FILES:
        rel=src.relative_to(REPO)
        dest=STAGE/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,dest)
        files.append({'source_path':rel.as_posix(),'size_bytes':src.stat().st_size,'sha256':sha256(src)})

    t=v['terminal']; r=v['readiness']; c=v['cumulative']
    manifest={
        'contract':'COWORK_GITHUB_NATIVE_HANDOFF_MANIFEST_v3_1_PROVIDER_BOUNDED',
        'generated_at_utc':datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z'),
        'repo':'Donh91/Investering-Framework-Archive-v1',
        'authoritative_ref':'main',
        'delivery_model':'COMPACT_INSTRUCTIONS_PLUS_DIRECT_GITHUB_READ',
        'readiness_verdict':r['readiness_verdict'],
        'readiness_contract':r['contract'],
        'cfgi_time_alignment_contract':r['cfgi']['time_alignment_contract'],
        'mandatory_provider_limitation':'MARKET_CFGI_HISTORICAL_NOT_TESTABLE_PROVIDER_UNAVAILABLE',
        'mandatory_preflight_file':str(LIMITATION.relative_to(REPO)),
        'cfgi_observed_symbols':['BTC','ETH'],
        'cfgi_provider_unavailable_symbols':['MARKET'],
        'automatic_promotion':False,
        'historical_findings_max_classification':'FORWARD_TEST',
        'heavy_bulk_delivery':'BOUND_GITHUB_ACTIONS_ARTIFACT_VIA_FREE_BULK_ARTIFACT_POINTER',
        'cowork_entrypoint':'07_PROMPTS_AND_AGENTS/historical_altseason_pullback/COWORK_OPUS5_LAUNCH_INSTRUCTION.md',
        'research_map':'07_PROMPTS_AND_AGENTS/historical_altseason_pullback/COWORK_GITHUB_RESEARCH_MAP.md',
        'expected_output_zip':'HISTORICAL_ALTSEASON_COWORK_OPUS5_RESEARCH_PACKAGE.zip',
        'cfgi_billing':{
            'verified_cumulative_actual_credits_used':c['cumulative_actual_credits_used'],
            'failed_gapfill_actual_credits_used_from_headers':None,
            'conservative_cumulative_credit_upper_bound':t['conservative_cumulative_credit_upper_bound'],
            'hard_cap_credits':t['hard_cap_credits'],
            'conservative_credits_remaining_lower_bound':t['conservative_credits_remaining_lower_bound'],
            'minimum_reserve_credits':t['minimum_reserve_credits'],
        },
        'files':files,
    }
    manifest_dest=STAGE/'COWORK_HANDOFF_MANIFEST.json'
    manifest_dest.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    MANIFEST_PATH.parent.mkdir(parents=True,exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8')

    with zipfile.ZipFile(ZIP_PATH,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as zf:
        for path in sorted(STAGE.rglob('*')):
            if path.is_file():
                zf.write(path,arcname=str(Path('COWORK_RESEARCH_HANDOFF')/path.relative_to(STAGE)))
    with zipfile.ZipFile(ZIP_PATH,'r') as zf:
        if zf.testzip() is not None:
            raise SystemExit('COWORK_COMPACT_HANDOFF_BLOCKED corrupt_zip')
        names=set(zf.namelist())
        required=[
            'COWORK_RESEARCH_HANDOFF/COWORK_HANDOFF_MANIFEST.json',
            'COWORK_RESEARCH_HANDOFF/07_PROMPTS_AND_AGENTS/historical_altseason_pullback/COWORK_OPUS5_MASTER_RESEARCH_PROMPT.md',
            'COWORK_RESEARCH_HANDOFF/07_PROMPTS_AND_AGENTS/historical_altseason_pullback/COWORK_OPUS5_LAUNCH_INSTRUCTION.md',
            'COWORK_RESEARCH_HANDOFF/07_PROMPTS_AND_AGENTS/historical_altseason_pullback/COWORK_GITHUB_RESEARCH_MAP.md',
            'COWORK_RESEARCH_HANDOFF/07_PROMPTS_AND_AGENTS/historical_altseason_pullback/COWORK_CFGI_PROVIDER_LIMITATION.md',
            'COWORK_RESEARCH_HANDOFF/06_RESEARCH_LAB/historical_altseason_pullback_v1/artifacts/RESEARCH_READINESS_MANIFEST.json',
            'COWORK_RESEARCH_HANDOFF/06_RESEARCH_LAB/historical_altseason_pullback_v1/artifacts/CFGI_MARKET_GAPFILL_BILLING.json',
            'COWORK_RESEARCH_HANDOFF/00_ARCHIVE_CONTROL/research_runtime/CFGI_MARKET_PROVIDER_TERMINAL_RECEIPT.json',
            'COWORK_RESEARCH_HANDOFF/06_RESEARCH_LAB/historical_altseason_pullback_v1/artifacts/FREE_BULK_ARTIFACT_POINTER.json',
        ]
        for req in required:
            if req not in names:
                raise SystemExit(f'COWORK_COMPACT_HANDOFF_BLOCKED zip_missing={req}')
    zip_hash=sha256(ZIP_PATH)
    SHA_PATH.write_text(f'{zip_hash}  {ZIP_PATH.name}\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','contract':manifest['contract'],'readiness':manifest['readiness_verdict'],'handoff_file_count':len(files),'zip':str(ZIP_PATH.relative_to(REPO)),'zip_sha256':zip_hash,'cfgi_verified_actual_credits':c['cumulative_actual_credits_used'],'cfgi_conservative_credit_upper_bound':t['conservative_cumulative_credit_upper_bound']},sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
