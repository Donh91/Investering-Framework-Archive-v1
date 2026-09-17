# CLEAN G3 INCREMENTAL EDGE v1 - preregistration

Date: 2026-09-15
Status: PREREGISTERED / RESEARCH ONLY / NO LIVE PROMOTION

## Objective

Test whether point-in-time qualified wallet intelligence adds incremental predictive value above G2 capital-path and microstructure for early memecoin discovery, with explicit controls for economic-entity overlap, common funding, manipulation, launch venue and chain regime.

Primary question:

> Does G2 + clean G3 outperform G2 alone out-of-sample on sellable 5x/10x outcomes without materially worsening rug, unsellable or manipulation exposure?

## Why this experiment exists

The prior Ian05012 test found strong G2 signal but could not reconstruct a clean pre-capture buyer graph from the released trade tables. Source-captured smart-wallet fields were useful only as secondary hypothesis evidence. A 5x interaction was interesting but not promotion-grade. This experiment therefore moves the clean G3 question to sources with explicit field-availability / first-buyer semantics and to prospective native events.

## Hard anti-leakage rules

1. Every feature carries an observable-at timestamp or explicit point-in-time provenance.
2. Wallet quality is computed only from outcomes matured before the candidate cutoff.
3. Current wallet labels, current PnL, future token survival and later creator/funder labels cannot be backfilled into historical rows.
4. Unknown remains UNKNOWN. Missing history is never converted to zero edge or zero risk.
5. Address count is not entity count. Router, pool, seeded, dust and transfer-only activity are excluded from self-initiated buyer attribution.
6. Historical research cannot directly change BUY_NOW or production thresholds.

## Experimental arms

A. `G2_ONLY`
- capital velocity
- net real capital flow
- independent buyer breadth where derivable
- buy/sell imbalance
- early sell pressure
- liquidity / slippage
- market-cap / curve state
- entity-adjusted concentration where derivable

B. `RAW_WALLET_COUNT`
- number of candidate wallets meeting minimal historical-activity criteria
- intentionally naive control arm

C. `ASOF_WALLET_QUALITY`
- prior matured outcomes only
- venue / chain-local specialization
- early-entry history
- hold / trim / exit quality where available

D. `ENTITY_ADJUSTED_G3`
- arm C adjusted for same-funder, same-controller, routing, bundle or other economic-entity overlap

E. `G2_PLUS_CLEAN_G3`
- G2 + arm D

F. `G2_PLUS_CLEAN_G3_PLUS_CONTEXT`
- arm E + chain-regime / launch-venue context + exact-CA public propagation timing

## Primary outcomes

1. sellable / mature 2x within 24h
2. sellable 5x
3. sellable 10x

25x / 50x / 100x are sparse-tail research outcomes and are retained in a casebook. They do not receive a classical promotion gate until sample size is sufficient.

Where a source provides only theoretical peak and not realizable execution, the outcome must be labelled `THEORETICAL_MFE_ONLY` and cannot substitute for a sellable outcome.

## Evaluation

Primary split: chronological forward holdout.

Report:
- average precision
- ROC-AUC as secondary diagnostic
- top 1%, 5%, 10% precision
- top-k recall
- relative lift vs cohort base rate
- MFE / MAE
- liquidity survival
- realizability / slippage class
- manipulation / rug / unsellable rate
- false-negative cost on missed tail winners

## Promotion criterion for G3

G3 may only be promoted from hypothesis to shadow-weight candidate if:

1. `G2_PLUS_CLEAN_G3` improves 5x top-bucket precision or recall by at least ~20% relative to `G2_ONLY` on at least two independent out-of-sample cohorts;
2. average precision does not deteriorate materially;
3. 10x direction is non-negative where sample permits;
4. rug / unsellable / manipulation exposure does not materially worsen;
5. the result survives entity/funder adjustment;
6. the effect is not confined to one obsolete launch-mechanic regime.

The ~20% rule is an operational materiality gate, not a statistical law. Statistical uncertainty and sparse-tail sample size must also be shown.

## Source order

1. RED-COHORT / recurring-wallet cohort evidence
2. Chain of Title / creator, self-buy, operator and funding provenance
3. Trenches August forward-capture / explicit feature-availability timing
4. MELT / entity, bundle and behavioral trace resolution
5. full Pump.fun denominator for selection-bias falsification
6. prospective native Pump event shadow capture
7. Robinhood replication after Solana v1 is frozen
8. BNB / Base / Monad replication only after chain-regime contracts exist

## Missed-winner and false-positive audit

Every major 5x+ winner in scope must have matched failures from the same chain, venue, week, launch-age and approximate size / liquidity regime.

Every top-ranked false positive must be classified by primary failure mode:
- manipulated capital path
- same-entity wallet convergence
- creator / funder contamination
- liquidity failure
- sellability failure
- social/KOL burst without independent demand
- regime mismatch
- late / saturated entry
- unknown

## Output

The mission closes only when it produces:
- source and timestamp audit
- point-in-time wallet graph
- entity / funder graph
- G2/G3 ablation table
- matched-control analysis
- false-positive audit
- missed-winner audit
- 25x/50x/100x tail casebook
- chain-regime stratification
- frozen prospective-shadow spec

Authority: research only. No portfolio execution, automatic trading, position sizing, BUY_NOW promotion or threshold rewrite.
