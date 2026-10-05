# M3 Final Research Lab Adjudication v1

**Mission:** `RL-CN-SKILL-BASELINE-003`  
**Date:** 2026-10-05  
**Adjudicator:** ChatGPT 5.6 Sol High  
**Status:** FINAL_RESEARCH_ADJUDICATION  
**Authority:** RESEARCH_ONLY / NO_PUBLIC_SCORE_REWRITE / NO_MARKET_OR_PORTFOLIO_EFFECT  
**Framework head read at adjudication:** `e14b03752413438ae6add75d896fc4d3c3822f15`

## Final verdict by component

### 1. Demonstrated weekly range superiority versus simple baselines
**REJECTED as an established claim.**

The evidence does not support saying Cycle Navigator has already demonstrated stable incremental weekly range alpha over simple mechanical bands.

Reasons:
- the historical matched degraded tournament is adverse versus DUMB1.5/DUMB2.0 on most paired comparisons;
- the current-era W39-W40 reconstructed tournament is mixed and small;
- CN loses Jaccard on 3/4 current reconstructed rows against each simple baseline;
- CN loses Winkler on 2/4 rows versus DUMB1.5 and 3/4 versus DUMB2.0;
- the apparent aggregate Winkler advantage is concentrated in W39 BTC.

This rejects a strong evidentiary claim, not the possibility of future range skill.

### 2. Containment / uncertainty-envelope value
**SUPPORTED, small-N.**

In the W39-W40 reconstructed tournament CN contained all four BTC/ETH weekly realized ranges.

CN mean containment: 100%.

The best current description is therefore:
**broad uncertainty / containment envelope with episode-dependent value**.

This is not equivalent to calibrated alpha.

### 3. Placement / width efficiency
**CONFLICTED / NOT ESTABLISHED.**

The same current sample shows CN is usually wider:
- approximately 39-44% wider than DUMB1.5;
- approximately 4-8% wider than DUMB2.0.

In W40 BTC and ETH, both simple baselines achieved the same 100% containment while beating CN on both Jaccard and Winkler.

The extra CN width therefore had no observed containment benefit in those rows.

### 4. Regime classification
**SUPPORTED descriptively, incremental skill UNKNOWN.**

Recent regime-family accountability is strong in a very small sample, but there is no matched simple comparator establishing incremental classification alpha.

Do not equate 100-point accountability rows with predictive edge.

### 5. Rotation / transmission
**WEAKENED / CONFLICTED.**

The current internal rotation family is roughly 58 mean / 50 median with `PERSISTENT_WEAKNESS`.

Recent weekly rotation rows include repeated MIXED outcomes.

No separate matched transmission baseline is available.

Rotation should not currently be presented internally as a demonstrated forecasting strength.

### 6. Accountability / public-trust mechanism
**SUPPORTED as process value.**

The system now has:
- immutable forecast freezes;
- explicit publication identity;
- source bindings;
- scorecards;
- separate price and structural semantics;
- no synthetic all-in accuracy score.

That creates real accountability value even where predictive alpha remains unknown.

It is process value, not economic alpha.

## Public Price Range Precision interpretation

Current public Price Range Precision uses:

`70% containment + 30% Jaccard`.

That score is legitimate for the stated public accountability purpose.

However, because containment carries 70% weight, it naturally rewards robust/wider bands more than a pure placement-efficiency metric would.

Therefore:

**Price Range Precision must not be interpreted internally as a direct estimate of forecasting alpha.**

It is a continuity/accountability score.

No historical public score is changed by this finding.

## Current-era reconstructed baseline evidence

Artifact:
`06_RESEARCH_LAB/m3_replay/2026-10-05__RL-CN-SKILL-BASELINE-003__reconstructed-baseline-v1.json`

Research-only means:
- CN Jaccard 0.5045, Winkler10 13.49, containment 100%
- DUMB1.5 Jaccard 0.5476, Winkler10 29.50, containment 75%
- DUMB2.0 Jaccard 0.4609, Winkler10 23.96, containment 89.3%

The aggregate Winkler result is dominated by W39 BTC, where the simple bands missed upside expansion.

Influence diagnostic excluding W39 BTC:
- CN mean Winkler ≈ 14.09
- DUMB1.5 ≈ 12.66
- DUMB2.0 ≈ 13.41

Lower is better.

This supports episode-dependent containment value, not stable superiority.

## Historical baseline evidence

The older degraded M5-style sample is adverse to robust superiority:
- CN mean Jaccard ≈ 0.357
- DUMB1.5 ≈ 0.461
- DUMB2.0 ≈ 0.427
- PREVWK ≈ 0.336

Paired comparisons likewise do not demonstrate consistent CN dominance.

Because the historical dataset is explicitly DEGRADED, it is falsification pressure, not current canonical performance.

## Native forward solution now exists

Current main contains:

`scripts/cycle_navigator/deterministic_range_baseline.py`

Method:
`MEDIAN_4W_ASYMMETRIC_WEEKLY_EXCURSION_FROM_PRIOR_CLOSE_v1`

Important strengths:
- deterministic;
- independent from the LLM forecast;
- generated before the CN model call;
- explicitly excluded from model context;
- shadow-only;
- immutable prospective forecast + later score path;
- no automatic promotion.

The first persisted native forecast is:
`05_CYCLE_NAVIGATOR/range_baselines/forecasts/2026/W41.json`

For W41:

BTC:
- CN: 82,000-92,000
- independent baseline: approximately 84,497-90,814

ETH:
- CN: 2,560-2,960
- independent baseline: approximately 2,641-2,893

This is the correct future evidence path.

Do not retrofit native-baseline scores to W39/W40.

## Sol review

Initial compact M3 pass:
- verdict `INSUFFICIENT_EVIDENCE`
- cost approximately $0.0542.

Bounded cross-examination after deterministic W39-W40 baseline:
- verdict remains `INSUFFICIENT_EVIDENCE`
- cost approximately $0.0717.
- containment-envelope value supported;
- general range alpha conflicted;
- strong demonstrated consistent superiority rejected;
- W41 native benchmark judged suitable in principle as forward design.

## Claude status

The broad M3 folder/provenance audit remains a non-blocking external challenge.

It may reopen M3 only on a material source-backed contradiction, such as:
- frozen-before-outcome failure;
- score lineage mismatch;
- retrospective mutation;
- baseline independence failure;
- a reproducibility issue that changes the conclusions above.

## Research recommendation

Preserve the current CN product and public score lineage.

Going forward:
1. keep Price Range Precision as an accountability score;
2. keep it semantically separate from range alpha;
3. score the independent native baseline after each matured week;
4. compare CN versus baseline on containment **and** width/midpoint error;
5. do not promote a range-skill claim from a single volatility-expansion week;
6. do not demote CN from a single tight-baseline win either;
7. accumulate prospective evidence before any method or product change.

## Queue decision

M3 is closed as **FINAL_RESEARCH_ADJUDICATION**.

M4 `RL-AUTOTRADING-EVIDENCE-004` is released.

No public score, historical score, market state, portfolio action, model weight or canonical forecast rule is changed by this adjudication.
