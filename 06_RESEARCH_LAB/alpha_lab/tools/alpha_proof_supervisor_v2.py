#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

TERMINAL_STATES = {'SHADOW04_PASS', 'SHADOW04_FAIL', 'HALT_CRITICAL'}

def load_json(path: str | None):
    if not path:
        return None
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return None

def default_state():
    return {
        'state': 'WAIT_SHADOW04',
        'shadow04_attempts': 0,
        'next_action': 'WAIT',
        'portfolio_execution': False,
        'canonical_effect': False,
    }

def canonical_spec_bytes(spec: dict) -> bytes:
    value = dict(spec)
    value.pop('spec_sha256', None)
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()

def bounded_retry(state: dict, reason: str) -> dict:
    attempts = int(state.get('shadow04_attempts', 0)) + 1
    state['shadow04_attempts'] = attempts
    if attempts <= 2:
        state.update(state='WAIT_SHADOW04', next_action='RETRY_SHADOW04', reason=reason)
    else:
        state.update(state='HALT_CRITICAL', next_action='HALT_CRITICAL', reason='retry_budget_exhausted:' + reason)
    return state

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--state', required=True)
    parser.add_argument('--artifact')
    parser.add_argument('--freeze')
    parser.add_argument('--upstream-conclusion', required=True)
    parser.add_argument('--upstream-head-sha', required=True)
    args = parser.parse_args()

    state = load_json(args.state) or default_state()
    state.setdefault('portfolio_execution', False)
    state.setdefault('canonical_effect', False)

    if state.get('state') in TERMINAL_STATES:
        Path(args.state).write_text(json.dumps(state, indent=2) + '\n')
        print(json.dumps(state, indent=2))
        return

    if args.upstream_conclusion != 'success':
        state = bounded_retry(state, 'upstream_' + args.upstream_conclusion)
    else:
        artifact = load_json(args.artifact)
        freeze = load_json(args.freeze)
        if not isinstance(artifact, dict) or not isinstance(freeze, dict):
            state = bounded_retry(state, 'artifact_or_freeze_missing')
        elif artifact.get('test') != 'SHADOW-04-PROSPECTIVE' or freeze.get('test') != 'SHADOW-04-PROSPECTIVE':
            state.update(state='HALT_CRITICAL', next_action='HALT_CRITICAL', reason='unexpected_artifact_contract')
        elif artifact.get('prospective') is not True:
            state.update(state='HALT_CRITICAL', next_action='HALT_CRITICAL', reason='prospective_flag_missing')
        elif freeze.get('source_sha') != args.upstream_head_sha or artifact.get('source_sha') != args.upstream_head_sha:
            state.update(state='HALT_CRITICAL', next_action='HALT_CRITICAL', reason='unreviewed_or_mismatched_source_sha')
        else:
            computed_hash = hashlib.sha256(canonical_spec_bytes(freeze)).hexdigest()
            spec_hash = freeze.get('spec_sha256')
            if not spec_hash or computed_hash != spec_hash or artifact.get('spec_sha256') != spec_hash:
                state.update(state='HALT_CRITICAL', next_action='HALT_CRITICAL', reason='preregistration_hash_mismatch')
            elif int(freeze.get('future_start_block') or 0) != int(artifact.get('future_start_block') or -1):
                state.update(state='HALT_CRITICAL', next_action='HALT_CRITICAL', reason='future_start_block_mismatch')
            elif not artifact.get('first_observed_block') or int(artifact['first_observed_block']) < int(freeze['future_start_block']):
                state.update(state='HALT_CRITICAL', next_action='HALT_CRITICAL', reason='outcome_precedes_frozen_start')
            elif not artifact.get('first_observed_unix') or float(artifact['first_observed_unix']) <= float(freeze.get('frozen_at') or 0):
                state.update(state='HALT_CRITICAL', next_action='HALT_CRITICAL', reason='observation_not_after_freeze')
            elif int(artifact.get('provider_disagreement', 1)) != 0:
                state.update(state='SHADOW04_FAIL', next_action='HALT_CRITICAL', reason='provider_disagreement')
            elif artifact.get('PASS_COLLECTION') is True and int(artifact.get('n', 0)) >= 1000:
                state.update(
                    state='SHADOW04_PASS',
                    next_action='START_SHADOW07',
                    reason='prospective_gate_pass',
                    adjudicated_source_sha=args.upstream_head_sha,
                    spec_sha256=spec_hash,
                )
            else:
                state = bounded_retry(state, 'incomplete_collection')

    Path(args.state).write_text(json.dumps(state, indent=2) + '\n')
    print(json.dumps(state, indent=2))

if __name__ == '__main__':
    main()
