# M6 Gap-Sensitive Distribution Episode Power Method v1

**Mission:** `RL-DISTRIBUTION-SURVIVAL-META-006`  
**Date:** 2026-10-05  
**Status:** FROZEN_BEFORE_DETERMINISTIC_RECOUNT  
**Authority:** RESEARCH_ONLY  
**Framework main at freeze:** `e9ca9a5ebba21cd57b526af19e06d49ad59b1a60`

## Purpose

Measure how many historically observable drawdown episodes/families exist on the archived Research Lab tape without:
- treating segment-local `ew_index` rebases as crashes;
- silently filling continuity gaps;
- selecting one favorable drawdown or clustering threshold after observing the result.

This is a power census, not an exit backtest.

## Source

`06_RESEARCH_LAB/historical_altseason_pullback_v1/artifacts/hourly_features.csv.gz`

Research windows remain separate:
- `ALTSEASON_2020_2021`
- `MODERN_ANALOGUE_2025_2026`

The large 2022-2024 absence is never bridged.

## Equal-weight alt index reconstruction

Do not consume raw `ew_index` levels across continuity segments.

Reconstruct an observed-endpoint research index:
1. initialize 100 at the first row of each research window;
2. within a continuity segment, compound `ew_return_1h_pct`;
3. when continuity_segment_id changes, carry the last observed index level forward to the next observed endpoint without fabricating a missing-period return;
4. record the exact gap boundary.

A carried level is a continuity convenience, not proof of what happened inside the missing hours.

## Episode detection

For each asset series and each fixed drawdown threshold:
- 20%
- 30%
- 40%

use one deterministic peak -> drawdown -> same-size rebound-confirmed zigzag procedure.

For every episode persist:
- peak timestamp/value;
- threshold-cross timestamp if available;
- trough timestamp/value;
- rebound-confirm timestamp if available;
- drawdown depth;
- peak-to-trough duration;
- whether peak->trough crosses any continuity gap;
- whether peak->rebound confirmation crosses any continuity gap;
- research window.

Open final drawdowns remain right-censored and are recorded as open episodes.

## Gap sensitivity

Never discard the gap information.

Report two populations:
1. ALL_OBSERVED_ENDPOINT_EPISODES
2. PEAK_TO_TROUGH_NO_GAP_EPISODES

An episode crossing a 3-6h gap is not called false, but it is not treated as fully observed path evidence.

## Episode-family clustering sensitivity

Do not select one independence rule after seeing counts.

For each threshold/population, cluster events separately under all three pre-frozen peak-time gaps:
- 7 days
- 14 days
- 30 days

Single-link rule:
consecutive episode peaks separated by less than the selected family gap belong to the same family; otherwise a new family starts.

Report all three family counts.

Do not infer "terminal distribution" from family membership or drawdown depth alone.

## BTC

Run the same 20/30/40% grid on BTC price from the same tape.

Continuity-gap flags use the same source continuity segments.

## Prohibited interpretations

This census cannot establish:
- machine warning lead time;
- sell value;
- altseason-top accuracy;
- statistical power sufficient for a specific effect size;
- independence of BTC and alt episodes;
- historical-as-was framework performance.

It only determines the observable episode/family inventory available to later tests.

## Expected decision

If counts remain very small under no-gap and family clustering, retrospective claims must remain hypothesis-generating and prospective lane C carries the confirmation burden.
