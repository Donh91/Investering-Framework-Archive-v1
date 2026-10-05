# M3 Deterministic Baseline Delta v1

**Mission:** `RL-CN-SKILL-BASELINE-003`
**Date:** 2026-10-05
**Status:** VERIFIED_NEW_EVIDENCE_FOR_BOUNDED_CROSS_EXAM
**Authority:** RESEARCH_ONLY
**Fresh main:** `734e3a60602565ae3cdf09aa05809d41ff5899d5`

## New evidence since Sol pass 1

A model-free research-only current-era baseline tournament has completed:

`06_RESEARCH_LAB/m3_replay/2026-10-05__RL-CN-SKILL-BASELINE-003__reconstructed-baseline-v1.json`

It compares exact frozen weekly CN ranges for W39 and W40 against mechanical DUMB1.5/DUMB2.0 ranges reconstructed from market data that closed before each forecast freeze.

Important boundary:
- the mechanical ranges were reconstructed after the fact;
- outcomes were not used to construct them;
- they were NOT originally committed/frozen at publication;
- they are therefore research baselines, not historical canonical baseline rows.

## Method

Rows:
- 2026-W39 BTC
- 2026-W39 ETH
- 2026-W40 BTC
- 2026-W40 ETH

N=4 asset-week rows over only two weeks; BTC/ETH within-week correlation means N is not four independent market regimes.

Provider:
Binance public 1d BTCUSDT / ETHUSDT.

Knowledge boundary:
only candles closed before each original CN freeze timestamp.

Mechanical ranges:
anchor close +/-1.5x and 2.0x Wilder ATR14.

ATR:
long recursive warmup, at least 120 pre-freeze daily bars, avoiding the known 60-bar convergence weakness in the old protocol.

## Results

### Means

CN:
- Jaccard: 0.504487
- Winkler10: 13.494651
- containment: 100%

DUMB1.5:
- Jaccard: 0.547552
- Winkler10: 29.499821
- containment: 75%

DUMB2.0:
- Jaccard: 0.460933
- Winkler10: 23.961620
- containment: 89.2857%

### Pairwise

CN vs DUMB1.5:
- Jaccard wins 1, losses 3
- Winkler wins 2, losses 2

CN vs DUMB2.0:
- Jaccard wins 1, losses 3
- Winkler wins 1, losses 3

## Episode structure

### W39 BTC
CN strongly beats both simple bands because the market expanded above them:
- CN Jaccard 0.688, Winkler 11.71, containment 100%
- DUMB1.5 Jaccard 0.381, Winkler 80.01, containment 14.3%
- DUMB2.0 Jaccard 0.445, Winkler 55.62, containment 57.1%

### W39 ETH
Mechanical bands are tighter:
- CN Jaccard 0.485, Winkler 16.14
- DUMB1.5 Jaccard 0.628, Winkler 19.27
- DUMB2.0 Jaccard 0.513, Winkler 15.27

### W40 BTC
Both mechanical baselines beat CN on Jaccard and Winkler:
- CN 0.490 / 11.25
- DUMB1.5 0.689 / 8.00
- DUMB2.0 0.517 / 10.67

### W40 ETH
Both mechanical baselines beat CN on Jaccard and Winkler:
- CN 0.354 / 14.88
- DUMB1.5 0.492 / 10.71
- DUMB2.0 0.369 / 14.28

## Width / insurance interpretation

CN achieved 100% containment in all four rows, but generally used wider intervals.

Research width ratios versus realized weekly width:
- W39 BTC: 1.45
- W39 ETH: 2.06
- W40 BTC: 2.04
- W40 ETH: 2.82

Thus current evidence is consistent with CN behaving partly as a robust uncertainty envelope / tail-insurance range rather than demonstrating consistently tighter placement alpha.

The old canonical v0.1 protocol included an overwide-gaming guard at width ratio >2.5 without SCENARIO. The W40 public text does not visibly label the ETH weekly range as SCENARIO. However current CN production has since moved to `CN_PUBLIC_CONTINUITY_v1`, so this is a methodology-lineage question rather than an automatic historical violation finding.

## New native baseline architecture

Current main now contains:
`scripts/cycle_navigator/deterministic_range_baseline.py`

This is a new independent simple benchmark:
`MEDIAN_4W_ASYMMETRIC_WEEKLY_EXCURSION_FROM_PRIOR_CLOSE_v1`

It is integrated into the current weekly builder and weekly calibration context.

Current persisted baseline inventory starts at:
`05_CYCLE_NAVIGATOR/range_baselines/forecasts/2026/W41.json`

No W39/W40 native baseline forecast or score is present.

Therefore:
- current architecture has repaired the missing baseline problem going forward;
- it does not retroactively prove W39/W40 skill;
- future M3-style evidence should prefer this native benchmark over resurrecting the old v0.1 ATR ledger.

## Bounded questions for GPT-6.1 Sol

Do not rerun the full mission.

1. Does this new W39-W40 evidence materially change your prior `INSUFFICIENT_EVIDENCE` verdict?
2. Is the best interpretation:
   - range alpha,
   - width/containment insurance,
   - mixed skill,
   - or still indeterminate?
3. Does the combination of historical degraded evidence + current reconstructed evidence justify rejecting a strong claim of demonstrated range superiority?
4. What, if anything, can now be said positively about CN range value without confusing containment with alpha?
5. Is the new native W41 baseline architecture sufficient as the correct forward evidence path?
6. Give the smallest final M3 verdict by component.

No public score rewrite.
No canonical role change.
No implementation request.
No portfolio action.
