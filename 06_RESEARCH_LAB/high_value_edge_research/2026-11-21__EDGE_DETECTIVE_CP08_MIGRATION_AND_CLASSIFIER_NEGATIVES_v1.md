# EDGE DETECTIVE CP08 | Asymmetric Solana migration drawdowns and negative classifier utility

**2026-11-21 CET | RESEARCH_ONLY, AUTHOR-REPORTED AGGREGATES + DETERMINISTIC ARITHMETIC. NO NEW TRADING EDGE.** This adds an independent failure mode to the existing #1512 / Alpha original #194/#98/#77/#85 program. It is NOT permission to create a new migration strategy, scanner, source contract, schedule or early-veto threshold.

## 1. Source-reported migration aftermath, cohort not general population

Original source: `loopholetape/pumpfun-launches`, provider's public `README.md` under license CC BY 4.0, release described as **2026-11-12** and reviewed **2026-11-21** via connected Hugging Face filesystem; https://huggingface.co/datasets/loopholetape/pumpfun-launches. The source's `graduation_pools` config tracks **48,438 observed pools opened 2026-09-23 11:10 UTC to 2026-11-05 23:59 UTC**. Provider defines a *full pool* as `complete=1`, `n_trades >=5`, and `open_reserve_lam >= 50 SOL`, yielding **32,325 pools**.

Provider reports **18,738/32,325 = 58.0%** ended the first 30 minutes at or below **10% of opening trade price**, and **19,445/32,325 = 60.2%** ever touched that threshold within the 30m period. Median time to first 90% drawdown among those touching it is **511 seconds**. For 2026-11-05 alone, **262/487 = 53.8%** of qualifying full pools ended there. These are **source-reported observed outcome frequencies**, NOT independently re-played chain prices; exact source content bytes/commit are not hash attested here. Source provider itself warns migration and pool capture have separate known issues and that its nine-cell exploratory relation between an earlier drain and later collapse is unvalidated.

**What this DOES show:** in the provider's **selected, high-reserve, sufficiently traded and fully captured migrated-pool cohort**, a huge first-30-minute post-migration decline is common. It challenges naive 'graduated means safe' or 'migrated liquidity means price will hold'. **What it does NOT show:** the base rate for all launches, all Solana venues, a positive return from shorting/avoiding a pool, that 58% of *tradable* entries lose 90%, or a causal explanation. Exact buy price/latency, route exit, transaction fees, non-starters, winners sacrificed and initial time/identity are absent from this aggregate.

### Hypothesis to original research owners, NOT tested

Predefine separate `POST_MIGRATION_SURVIVOR_V1` *as a candidate within existing Phoenix/Strategy Arena*, not as new autonomous executable lane. Ask if entering only after observing an **independently verified liquidity-and-buy-breadth survivor state** beats immediate same-size migration-entry and always-WAIT on **net realizable 24h/72h** outcomes. Stratify by original launchpad, mayhem, quote mint, synthetic migration, price/liquidity discontinuity and eligible issue time. Controls: unconditional *always wait* and *immediate-entry* at the same actually reachable source clock, same mint/pool and size; include tokens missing a pool and all failed/unknown exits. Avoid post-outcome 30m survivor filtering when the decision is placed at minute zero.

No threshold/algorithm tuning from the above 30m labels. Research verdict `LARGE_REPORTED_AFTER_MIGRATION_DRAWDOWN_BASE_RATE` but `SURVIVOR_ACTION_EDGE_UNKNOWN`.

## 2. CP03 confusion-matrix sanity check, same previous 292 selected cases (NOT holdout)

CP03's limited seven-block Hugging Face Dataset Viewer subset yielded **292** rows after source/feature, SOL-only/classic and rug-after-feature screens. It counted **184** provider-defined `rugged=1`, **108** `rugged=0`. Those are operational labels based on creator sales/curve decline, NOT documented economic losses or fraud convictions. The thresholds below were selected after inspection and cannot validate predictiveness.

`f10_insider_share>0.20` labeling *risk*:
- TP **66**, FP **9**, FN **118**, TN **99** (total 292).
- Of flagged, 66/75 = **88.0%** were later provider-rug-labeled, **compared to 184/292 = 63.0%** overall in this already-selected population.
- Sensitivity **66/184 = 35.9%**: **64.1% of rug-labelled rows were NOT flagged**. Specificity **99/108 = 91.7%**. As a forced binary classifier, accuracy **(66+99)/292 = 56.5%**, **BELOW** simply predicting rug for all **184/292 = 63.0%**. This is not an economic utility comparison because a selective trade veto has different opportunity costs than a balanced classification score.
- 9 of 75 flagged were labelled *not rugged*. Those **are NOT known economically sellable winners**; missing their opportunity cost is a separate severe blocker.

`f10_bundle_wallets>=5` labeling risk:
- TP **35**, FP **6**, FN **149**, TN **102**.
- Flagged provider-rug rate **35/41 = 85.4%**, but sensitivity **35/184 = 19.0%**, specificity **102/108 = 94.4%**; classifier accuracy **(35+102)/292 = 46.9%**.
- The two filters share the same 292 rows and correlation, and cannot be added as independent evidence or used as production selection gates.

**Meaning:** high risk *enrichment* among chosen flagged rows can coexist with very low coverage; a striking 88% 'precision' is not equivalent to more profits, more missed-winner protection, better discovery or an edge after costs. Need compare conditional selective *decision utility* vs original no-filter and simple developer/liquidity baselines, at identical source clocks, accounting for both false vetoes and real saleable outcomes.

## 3. Additional independently sourced segment caveat, do not train on mixture blindly

The same provider `KNOWN_ISSUES.md` reports that mayhem mode is **27.7%** of its full launch rows and has radically different outcomes: among resolved SOL-quoted launches, its rug label rate is **89.1%** versus **61.4%** for classic; graduation around **0.02%** versus **3.06%**. These are provider operational outcomes, subject to label and decoder definitions. They should NOT be treated as live independent warning edge: mayhem status may be known at launch, and its distribution changes both baseline prevalence and sampling composition.

Prior CP03 explicitly excluded mayhem, which limits the sample appropriately. For later clean cohorts, either separate the mayhem and classic baselines or explicitly show reweighting and source-first-known at decision time; never promote a model 'discovering' mayhem effects while claiming to predict insider risk.

## 4. Economy-first decision and kill rules

1. **Do not BUY just because a pool graduated.** Graduation is a lifecycle and market-structure fact, not safety or return evidence.
2. **Do not blanket AVOID at 20% insider share** because the convenience sample shows low sensitivity, no capacity evidence, no independent creator/wallet clustering and unknown false-veto loss.
3. **Separate information and action:** unusual insider share, source-confirmed migration and effective-reserve discrepancies are potential research context. They become action signals only after a complete prospective economic opportunity universe proves net utility against simple baselines.
4. **If exact pre-event observation and two-way exit cannot be shown at $100/$500/$1000, STOP at `SOURCE_BLOCKED`.** No market-cap high, pool opened, rug label or classification AUC substitutes.
5. **If a precise filter only improves proxy label prediction without improving *spendable after-cost profit or avoided sellable loss*, KILL the trading enhancement.** Retain failures as a scientific record.

**CP08 disposition:** `STRONG_SOURCE_REPORTED_BASE_RATE_WARNING` (selected migrated cohort), `LABEL_CLASSIFIER_WEAK_COVERAGE` (non-representative 292), `NO_ESTABLISHED_INFORMATION_EDGE_OVER_BASELINE`, `NO_ACTION_EDGE`. Existing #1512 and Alpha original source and outcome owners retain all work and release authority.
