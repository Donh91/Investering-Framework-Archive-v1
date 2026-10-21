#!/usr/bin/env python3
"""Task 2 matched fixed-clock windows: price-only EX-POST development diagnostics.

No original Compass/CFGI forecast inference; no executable fill, source refresh,
selection of winning parameters, portfolio action, threshold change or new owner.
Uses the frozen, blob-verified original 25,506h synthetic survivor index.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

CONTRACT = 'TASK2_MATCHED_FIXED_WINDOWS_PRICE_ONLY_v1'
WINDOW_HOURS = 336
WARMUP_HOURS = 48
STARTING_CAPITAL = 10_000.0
HOUR_MS = 3_600_000
ERA_NAMES = ('ALTSEASON_2020_2021', 'MODERN_ANALOGUE_2025_2026')
CLASSIFICATION = 'EX_POST_FIXED_CLOCK_NONOVERLAPPING_DEVELOPMENT_NOT_PIT_NOT_EDGE'


def windows_from_segments(segments, *, warmup=WARMUP_HOURS, window=WINDOW_HOURS):
    """Fixed start anchored by archive segment, never by detected outcome.

    Warmup can overlap prior evaluated hours but scored terminal intervals do
    not. Discard short or incomplete tails without future interpolation.
    """
    if not isinstance(warmup, int) or not isinstance(window, int) or warmup <= 0 or window <= 0:
        raise ValueError('BAD_FROZEN_WINDOW_DIMENSIONS')
    windows = []
    for segment_index, segment in enumerate(segments):
        era = segment.get('era')
        rows = segment.get('rows')
        if era not in ERA_NAMES or not isinstance(rows, list):
            raise ValueError('SOURCE_SEGMENT_ERA_OR_ROWS_UNRECOGNIZED')
        for i in range(1, len(rows)):
            if rows[i][0] - rows[i-1][0] != HOUR_MS:
                raise ValueError('CROSSED_HOURLY_GAP_OR_DUPLICATE_SOURCE')
        for start in range(warmup, len(rows) - window + 1, window):
            view = rows[start-warmup:start+window]
            assert len(view) == warmup + window
            windows.append({'era':era, 'source_segment':segment_index,
                            'score_start_utc':datetime.fromtimestamp(rows[start][0]/1000, tz=timezone.utc).isoformat(),
                            'score_end_utc':datetime.fromtimestamp(rows[start+window-1][0]/1000, tz=timezone.utc).isoformat(),
                            'tape':view})
    return windows


def first_price_trigger(tape, lookback, threshold, *, warmup=WARMUP_HOURS):
    """Warning uses only complete current/past closes; fill strictly next close."""
    if lookback < 1 or not (0 < threshold < 1) or len(tape) <= warmup or lookback > warmup:
        raise ValueError('BAD_FROZEN_SIGNAL_DIMENSIONS')
    for i in range(warmup, len(tape)-1):
        peak = max(price for _, price in tape[i-lookback:i+1])
        if peak <= 0 or not math.isfinite(peak):
            raise ValueError('BAD_PRICE')
        if tape[i][1] / peak - 1 <= -threshold:
            return i+1
    return None


def evaluate_window(tape, sale_index, trim_fraction, reentry_hours, cost_per_side, *, warmup=WARMUP_HOURS):
    """Equal-start-capital no-leverage HOLD comparison and one mechanical trim.

    Reentry at prespecified elapsed-hour clock. Indicative *close* is never
    certified executable; no tax, venue depth or post-hoc optimal trough.
    """
    if not (0 < trim_fraction <= 1) or not isinstance(reentry_hours, int) or reentry_hours < 1 or not (0 <= cost_per_side < 1):
        raise ValueError('BAD_FROZEN_EXECUTION_CONFIG')
    if len(tape) <= warmup or not all(math.isfinite(p) and p > 0 for _,p in tape):
        raise ValueError('INVALID_PRICE_TAPE')
    initial_price = tape[warmup][1]
    terminal_price = tape[-1][1]
    holder_units = STARTING_CAPITAL / initial_price
    benchmark = holder_units * terminal_price
    if sale_index is None:
        return {'status':'NO_SIGNAL', 'delta_vs_hold_pct_initial':0.0,
                'sale_attempted':False, 'reentered':False, 'left_in_cash':False}
    if not (warmup+1 <= sale_index < len(tape)):
        raise ValueError('SALE_BEFORE_KNOWLEDGE_OR_OUTSIDE_WINDOW')
    sale_price = tape[sale_index][1]
    cash = holder_units * trim_fraction * sale_price * (1-cost_per_side)
    units = holder_units * (1-trim_fraction)
    reentry_idx = sale_index + reentry_hours
    reentered = reentry_idx < len(tape)
    if reentered:
        units += cash * (1-cost_per_side) / tape[reentry_idx][1]
        cash = 0.0
    delta = (units*terminal_price + cash - benchmark) / STARTING_CAPITAL * 100.0
    if not math.isfinite(delta):
        raise ValueError('NONFINITE_RESEARCH_DELTA')
    return {'status':'ONE_TRIM', 'delta_vs_hold_pct_initial':delta,
            'sale_attempted':True, 'reentered':reentered, 'left_in_cash':not reentered}


def execute(archive=None):
    from scripts.research import task2_archive_price_only_stress_v1 as prior
    if archive is None:
        archive = prior.ART
    proven = prior.preflight(archive)
    segments = prior.load_price_segments(prior.locked_read(archive / prior.PRICE.name, prior.PRICE_BLOB))
    ws = windows_from_segments(segments)
    if len(ws) < 2 or {w['era'] for w in ws} != set(ERA_NAMES):
        raise ValueError('INSUFFICIENT_FIXED_CLOCK_HISTORY')
    configs = prior.fixture_grid()
    if len(configs) != 576 or len(set(configs)) != 576:
        raise ValueError('PARAMETER_CENSUS_CHANGED')
    result={}
    for era in ERA_NAMES:
        era_windows=[w for w in ws if w['era']==era]
        if not era_windows:
            raise ValueError('NO_FIXED_WINDOWS_IN_ERA')
        tallies=defaultdict(lambda: {'attempts':0,'no_signal':0,'trim':0,'reentered':0,'unreentered_cash':0,'better':0,'worse':0,'equal':0,'delta_pct_sum':0.0})
        deltas_by_cost=defaultdict(list)
        for w in era_windows:
            tape=w['tape']
            triggers={(lb,threshold):first_price_trigger(tape,lb,threshold) for lb in prior.LOOKBACK_H for threshold in prior.THRESHOLDS}
            for threshold,lb,trim,reentry,cost in configs:
                z=evaluate_window(tape,triggers[(lb,threshold)],trim,reentry,cost)
                k=f'{cost:.3f}'
                d=tallies[k]
                d['attempts']+=1
                if z['status']=='NO_SIGNAL':d['no_signal']+=1
                else:
                    d['trim']+=1
                    if z['reentered']:d['reentered']+=1
                    else:d['unreentered_cash']+=1
                delta=z['delta_vs_hold_pct_initial']
                d['delta_pct_sum']+=delta
                deltas_by_cost[k].append(delta)
                if delta>1e-9:d['better']+=1
                elif delta< -1e-9:d['worse']+=1
                else:d['equal']+=1
        costs=[]
        for cost in prior.COSTS:
            k=f'{cost:.3f}'
            v=tallies[k]
            expected=len(era_windows)*(len(configs)//len(prior.COSTS))
            if v['attempts']!=expected or v['no_signal']+v['trim']!=expected or v['better']+v['worse']+v['equal']!=expected:
                raise ValueError('INCOMPLETE_FIXED_WINDOW_DENOMINATOR')
            costs.append({'one_side_cost_pct':cost*100,'comparisons':expected,
                          'no_signal':v['no_signal'],'sale_attempts':v['trim'],
                          'reentered':v['reentered'],'unreentered_cash':v['unreentered_cash'],
                          'better_than_hold':v['better'],'worse_than_hold':v['worse'],'equal_to_hold':v['equal'],
                          'mean_delta_pct_initial_descriptive':round(v['delta_pct_sum']/expected,6),
                          'median_delta_pct_initial_descriptive':round(statistics.median(deltas_by_cost[k]),6)})
        result[era]={'fixed_full_14d_windows':len(era_windows),
                     'source_segments':len([seg for seg in segments if seg['era']==era]),
                     'first_scored_utc':era_windows[0]['score_start_utc'],
                     'last_scored_utc':era_windows[-1]['score_end_utc'],
                     'complete_window_comparisons':len(era_windows)*576,
                     'cost_scenarios':costs,
                     'claimed_independent_shock_families':0}
    return {'contract':CONTRACT,'classification':CLASSIFICATION,
            'window_hours':WINDOW_HOURS,'warmup_hours':WARMUP_HOURS,
            'nominal_full_grid_per_window':576,'original_source_preflight':proven,
            'eras':result,'historical_episodes_used_to_time_entries':False,
            'no_signal_denominator_preserved':True,
            'claim_of_compass_accuracy':False,'claim_of_cfgi_edge':False,
            'claim_of_out_of_sample_edge':False,'executable_after_cost_fill_verified':False,
            'chosen_best_parameter':None,'new_market_policy':False,
            'note':'Nonoverlapping fixed clock intervals, shared price windows across controls. Correlated variants and structural era differences prohibit inference.'}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    summary=execute()
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,sort_keys=True))


if __name__=='__main__':
    main()
