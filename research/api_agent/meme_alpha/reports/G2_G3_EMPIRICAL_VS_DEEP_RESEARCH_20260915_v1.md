# Meme Alpha Lab - G2/G3 empirical test vs independent deep research

Date: 2026-09-15  
Status: RESEARCH COMPLETE FOR THIS TRANCHE, NO LIVE PROMOTION  
Empirical workflow: https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/35011887166  
Empirical source pin: `ian05012/solana-memecoin-dataset@7070d00e1e4492f8604d988549d91785cc5f43f7`

## Executive verdict

The two independent lanes converge on the same architectural conclusion:

> **G2 capital-path / microstructure should remain the primary early discovery layer. Raw smart-wallet convergence is not a sufficient standalone edge. G3 should be treated as an incremental, point-in-time-qualified confirmation layer only after activity, entity/funder, manipulation and regime controls.**

The empirical lane strongly supports G2 for 2x and 5x outcomes in this selected June-2026 cohort, but the released Ian trade log cannot support a clean reconstructed AS-OF G3-at-capture test under the current token join/timestamp semantics. Source-captured G3 fields therefore remain secondary hypothesis evidence only.

A potentially useful 5x interaction appeared: G2 + source-captured G3 improved top-5%-bucket precision from 3.01% to 4.35% and recall from 37.5% to 54.2%. However the holdout contains only 24 5x positives and the source-captured wallet labels are not independently derivability-audited, so this is **HYPOTHESIS_ONLY**, not evidence for production promotion.

The 25x and 50x events were absent from the final chronological holdout. That is itself important evidence of regime nonstationarity and means this source cannot validate extreme-tail logic prospectively by itself.

## Lane A - our empirical test

### Data and design

- 44,460 source snapshots, 31,013 unique token mints.
- Earliest snapshot per mint retained to avoid later-snapshot leakage.
- 60/20/20 chronological split, no random split as primary evidence.
- Common balanced logistic model across arms so model-class differences do not masquerade as feature value.
- 31 usable G2 features.
- Primary G3 was intended to be reconstructed AS-OF from prior matured outcomes plus timestamped funding edges.
- Current/source GMGN smart-wallet annotations were isolated into a secondary arm because their upstream label derivability cannot be independently reconstructed from this release.
- Source bytes were SHA-256 pinned in the workflow artifact.

### Source audit correction

The release's `max_return_1h/6h/24h/3d` columns are not semantically consistent with `reaches_2x` across the corpus: more than 44,400 rows are zero in the `max_return_*` fields while the source has thousands of `reaches_2x=true` observations. They were therefore excluded from primary outcome construction.

Corrected outcome semantics:

- 2x: source `reaches_2x` directly.
- 5x/10x/25x/50x: non-null `runner_peak_x` only; missing remains UNKNOWN.
- `staged_exit_return`: separate simulated-realizability outcome, never substituted for theoretical peak.

### Corrected base rates on canonical earliest snapshots

| Outcome | Known rows | Overall rate |
|---|---:|---:|
| 2x within 24h | 29,834 | 8.477% |
| peak >=5x | 29,596 | 0.973% |
| peak >=10x | 29,596 | 0.220% |
| peak >=25x | 29,596 | 0.041% |
| peak >=50x | 29,596 | 0.017% |

### Chronological holdout results

Final 20% holdout:

| Outcome | Arm | Holdout base | AP | ROC-AUC | Top 5% precision | Lift | Top 5% recall |
|---|---|---:|---:|---:|---:|---:|---:|
| 2x/24h | G2 only | 4.05% | 32.24% | 0.935 | 30.10% | 7.43x | 37.04% |
| 2x/24h | source-captured G3 secondary | 4.05% | 17.23% | 0.845 | 21.07% | 5.20x | 25.93% |
| 2x/24h | G2 + source G3 secondary | 4.05% | 30.24% | 0.933 | 28.09% | 6.93x | 34.57% |
| >=5x peak | G2 only | 0.400% | 2.52% | 0.895 | 3.01% | 7.52x | 37.50% |
| >=5x peak | source-captured G3 secondary | 0.400% | 1.97% | 0.740 | 3.01% | 7.52x | 37.50% |
| >=5x peak | G2 + source G3 secondary | 0.400% | 3.17% | 0.889 | 4.35% | 10.86x | 54.17% |
| >=10x peak | G2 only | 0.117% | 0.64% | 0.651 | 1.00% | 8.59x | 42.86% |
| >=10x peak | G2 + source G3 secondary | 0.117% | 0.58% | 0.749 | 0.67% | 5.73x | 28.57% |

Caution: only 24 >=5x and 7 >=10x positives exist in the final holdout. The 25x/50x classes have zero positives in validation/test, so no metric is reported and no inference is permitted.

### G3 source limitation / falsifier

The released trade tables did not yield a usable current-token pre-capture buyer set under the canonical token/timestamp join used by the point-in-time harness. Therefore:

`IAN05012 = USABLE_FOR_G2_AND_SECONDARY_SOURCE_CAPTURED_G3__NOT_YET_USABLE_FOR_PRIMARY_RECONSTRUCTED_ASOF_G3_AT_CAPTURE`

This is a source capability verdict, not a claim that real AS-OF wallet edge does not exist. The clean G3 question moves to sources with explicit first-buyer/field-availability semantics and to prospective native Pump event capture.

## Lane B - independent deep research synthesis

The dedicated asynchronous research runner was unavailable in this session, so the independent lane was completed synchronously across primary papers, public datasets, reproducibility records and current venue statistics. This lane did not use the empirical model output to select its conclusions.

### 1. Early structural/behavioral information is genuinely useful, but graduation is not our target

Marino et al., *Predicting the success of new crypto-tokens: the Pump.fun case* (2026), finds that conditioning bonding-curve progress on structural and behavioral launch variables materially improves graduation prediction. This supports G2 as an information-bearing layer, but graduation is only an intermediate lifecycle state and cannot be equated with Moonshot return.

Source: https://arxiv.org/abs/2602.14860

### 2. Raw recurring-wallet convergence is heavily selection-biased

RED-COHORT v1.1.1 covers 1,578,333 buyer events across 166,098 launches and 1,012 persistent wallet cohorts. After excluding cohort wallets from the outcome and matching on ten launch-quality covariates, cohort-touched launches show +16.1% non-cohort buyer-count lift, but only +6.3% SOL-inflow lift with a 95% CI spanning zero. The naive pooled buyer-count effect was +130.9%, and activity-matched placebo cohorts produced even larger apparent lift in earlier analysis.

Interpretation for Alpha Lab: **cohort recurrence can contain information, but raw co-entry is not evidence of causal smart-money edge.** G3 must be incremental to G2 and activity controls, not a standalone trigger.

Sources:
- https://zenodo.org/records/21765387
- https://arxiv.org/abs/2607.02795

### 3. Address count is not entity count

MemeTrans covers >40k migrated launches, >30M launchpad transactions and ~180M post-migration transactions, with 122 features plus bundle-level data that can reveal multiple accounts controlled by the same entity. Its high-risk task reports substantial loss reduction from manipulation-aware features.

Interpretation: independent-buyer breadth and independent-smart-wallet convergence must be entity-adjusted where evidence supports linkage. Common funding is a relationship feature, not proof of identity or insider status.

Source: https://arxiv.org/abs/2602.13480

### 4. Manipulation is too common in high-return memes to train on chart peaks naively

The cross-chain study *A Midsummer Meme's Dream* analyzes 34,988 tokens across Ethereum, BNB, Solana and Base and reports manipulation indicators in roughly 82.8% of >100% return tokens in its classification. The September-2026 Pump.fun study *Meme Coin Factories* analyzes all ~15M launches over two years and identifies wash trading, creator-address obfuscation, coordinated selling, copycats and social-media manipulation.

Interpretation: theoretical MFE is not enough. Moonshot outcomes must become manipulation-adjusted and realizability-aware.

Sources:
- https://arxiv.org/abs/2507.01963
- https://arxiv.org/abs/2609.10246

### 5. Social propagation should be modeled as timing/independence, not text sentiment

A 2026 study aligns 14,499 public Telegram channels and >20M messages with >17,000 cryptocurrencies. Manipulation-like events exhibit extreme temporal synchronization and can precede price moves by seconds, while their language is hard to distinguish from organic discussion.

Interpretation: CA propagation root count, independent-source count and wallet-to-public-propagation lead time are more promising than positive/negative language scores.

Source: https://arxiv.org/abs/2609.01176

### 6. Early integrity screening can work within minutes

*Catching the Rug* studies 6.4M Solana memecoins and uses first-five-minute transaction features for early fraud prediction, with multi-source fusion improving cross-platform generalization.

Interpretation: G0/G1 integrity should precede G2/G3 scoring, so the model does not learn 'successful manipulation' as desirable alpha.

Source: search/publication record for `Catching the Rug: Early Prediction of Fraudulent Memecoins on Solana via Machine Learning`, 2026.

### 7. Graduation survival is venue- and regime-dependent

MemeFees' 2026-09-14 snapshot reports pump.fun graduates above their own graduation market cap at ~45% after 1h, 13% after 24h and 7% after 7d, whereas other launch mechanisms differ materially. Pump.fun's July BOOST change also coincided with a large jump in graduation rate, demonstrating that launchpad mechanics can move base rates quickly.

Interpretation: regime/venue state must be explicit, and Runner/Exitability cannot be collapsed into Discovery.

Sources:
- https://memefees.com/stats/survival
- https://www.theblock.co/news/defi/2026-07-29-pump-fun-token-graduation-rate-jumps-boost-changes-launch-incentives-409815

### 8. Exitability requires direct depth or an explicit executable proxy

Trench Autopsy's public Exit-Liquidity Standard distinguishes aggregator liquidity from directly measured quote-vault depth and preserves observation gaps/NULLs rather than manufacturing precise death times.

Interpretation: `liquidity_usd` remains context, not proof that a 25x/50x peak was realizable.

Source: https://github.com/TrenchAutopsy/exit-liquidity-standard

## Cross-lane adjudication

| Hypothesis | Empirical lane | Independent lane | Verdict |
|---|---|---|---|
| G2 early capital/microstructure contains useful information | Strong 2x and 5x holdout ranking in selected Ian cohort | Behavioral/structural variables improve early success/risk prediction | **KEEP, P0** |
| Raw smart-wallet count is enough | Secondary G3 weaker than G2 at 2x, no clean primary AS-OF test | RED-COHORT shows severe activity/selection bias | **DOWNGRADE** |
| G3 may add value conditional on G2 | 5x combined secondary arm improved tail concentration, but only 24 positives and label provenance uncertain | Cohort evidence leaves room for modest conditional effect after matching | **KEEP AS HYPOTHESIS, NOT PROMOTED** |
| Common funder/co-entry proves cabal/insider | Not testable cleanly here | Entity research supports linkage controls, not attribution | **REJECT ATTRIBUTION** |
| Address breadth equals independent buyer breadth | Not resolved in Ian | Bundle/entity data says no | **REJECT, ENTITY-ADJUST** |
| Peak multiple is sufficient outcome | Ian peaks are too sparse and not executable proof | Manipulation research + exit-depth evidence strongly reject naive peaks | **REJECT** |
| Graduation is success | Ian outcome differs from graduation | Current survival data strongly shows post-grad attrition | **REJECT** |
| One static model can span regimes | Holdout base rate fell materially and 25x/50x events disappeared from later split | BOOST and launchpad differences alter base rates | **REJECT, REGIME-CONDITION** |
| Social text sentiment is a strong propagation detector | not tested | Telegram study shows manipulation language can look organic | **DOWNGRADE TEXT, KEEP TIMING/GRAPH** |

## Frozen feature families for the next prospective-shadow design

These are **feature families, not thresholds**:

1. `independent_net_capital_acceleration`
   - net quote inflow velocity
   - buyer breadth acceleration
   - capital per independent buyer
   - buy/sell imbalance and first-sell latency

2. `entity_adjusted_participation`
   - address breadth vs resolved-entity breadth
   - bundle/sniper cluster share
   - entity-adjusted top-holder concentration

3. `asof_wallet_quality_convergence`
   - wallet reputation computed strictly from outcomes matured before candidate time
   - venue/regime-specific history
   - independent-funder adjustment
   - persistence vs quick-flip behavior

4. `creator_funder_provenance`
   - prior launches and outcomes known AS-OF
   - creator self-buy/transfer behavior
   - funding relationships as probabilistic graph evidence only

5. `propagation_lead_structure`
   - first exact-CA public timestamp
   - number of independent propagation roots
   - wallet-convergence-to-public-call lead time
   - propagation acceleration rather than sentiment text

6. `integrity_manipulation_guard`
   - wash/circular activity
   - creator obfuscation indicators
   - coordinated sell/bundle risk
   - early concentration and sellability

7. `regime_venue_state`
   - launchpad version/mechanics
   - incentive regime
   - launch density and current graduation/survival base rates

8. `exitability_survival`
   - direct sell-side depth or validated executable proxy
   - slippage at intended size
   - liquidity survival
   - smart/entity distribution after MFE thresholds

## What is explicitly NOT promoted

- Current wallet win rate applied backwards in time.
- `smart_wallet_count` alone.
- Cohort synchrony alone.
- Common funder = same owner / insider.
- Raw holder count without entity adjustment.
- Graduation as a profit label.
- Theoretical chart peak as realizable return.
- Binary social-presence or text-sentiment score as a primary trigger.
- A universal threshold shared across launchpad/regime changes.

## Next empirical sequence

1. **Move clean primary G3 test away from Ian's released trade join** to RED-COHORT / Chain of Title / Trenches Forward Capture and prospective native Pump-event data.
2. Run denominator replication so G2's strong selected-cohort metrics are tested against the full launch population rather than graduated/trending-biased candidates.
3. Add entity/bundle controls from MELT before calling buyer/wallet breadth independent.
4. Reconstruct SmugCalls temporal tails and combine with direct/executable exit proxies so 5x/10x/25x/50x are measured as realizable opportunities, not screenshots.
5. Freeze a compact feature set after cross-dataset adjudication, then run an untouched prospective shadow cohort.

## Promotion rule

No feature family above changes `BUY_NOW`, wallet weights or production thresholds from this report. Promotion requires:

`point-in-time clean -> source falsifiers pass -> incremental matched-control value -> independent replication -> prospective shadow -> sellability/exitability validation`.
