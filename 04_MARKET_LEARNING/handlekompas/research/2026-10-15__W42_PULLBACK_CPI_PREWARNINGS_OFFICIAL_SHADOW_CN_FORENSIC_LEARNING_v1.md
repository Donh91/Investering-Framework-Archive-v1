# W42 pullback 14–15 October 2026 — frozen Compass / CN / Shadow warning and learning case

**Research case:** W42-OCT14-15-PULLBACK-FORENSIC-v1  
**Prepared:** 2026-10-15, from independently retrieved public GitHub owner artifacts, public Binance spot cross-check and BLS release.  
**Status:** RESEARCH_ONLY / ORIGINAL_FREEZES_UNCHANGED / NO_PNL_EDGE_CLAIM / NO_ACTION_PROMOTION.  
**Owners:** Existing Compass Risk-to-Action #1553; Task 1.5/Task 2 R1 #1596; existing EDGE-001/Compound research #1530, with research lineage merged in #1597. No new scheduler, owner, market model, threshold, episode, automatic trade or calibrated probability is authorized.

## 1. The incident, with as-of and observation discipline

For the investigation made 2026-10-15 ~09:32 UTC (11:32 Europe/Copenhagen), the latest **completed** public Binance spot 1-hour candle ended **09:00 UTC**. These are **post-event external spot observations**, not the canonical archived forecasting input and **never** replacements for the original censored owner outcomes.

| Instrument | Completed-hour spot close | 24h realized | 72h realized | Low in preceding 24h |
| --- | ---: | ---: | ---: | ---: |
| BTCUSDT | $81,380.29 | -2.46% | -2.55% | $80,226.35 |
| ETHUSDT | $2,373.95 | -5.27% | -6.99% | $2,318.00 |
| SOLUSDT | $103.33 | -3.46% | -7.51% | $100.62 |
| ETHBTC | 0.02917 | -2.90% | -4.58% | 0.02888 |

The market's cross-sectional behavior was especially adverse for ETH and alt exposure: ETH fell faster than BTC; ETH/BTC declined. This is observed behavior, **not** proof that a particular indicator had predictive incremental alpha.

The U.S. **September CPI** release was officially scheduled and published **2026-10-14 12:30 UTC / 14:30 Copenhagen**. The original BLS release reported **3.7% headline year-on-year and +0.6% seasonally adjusted month-on-month**. A hotter-than-expected print plausibly contributed to the risk-off episode, but a temporal correlation is not a separately identified causal decomposition of crypto's fall. It is **forbidden** to ascribe knowledge of the actual surprise to any pre-release forecast. BLS primary: https://www.bls.gov/news.release/archives/cpi_10142026.htm ; calendar: https://www.bls.gov/schedule/2026/ .

## 2. What was genuinely known before the macro shock?

**W42 Cycle Navigator** was a previously frozen weekly scenario and **not** an exact 14 October onset signal. Immutable public machine package: 05_CYCLE_NAVIGATOR/weekly/2026/W42/CYCLE_NAVIGATOR_MACHINE_PACKAGE.json, Git blob SHA **819a17d1c7aa35ae4df2cf392b013d195e107a07**. Its one-to-three-day public bull/bear evidence balance was **4/6 (lean bearish)**, 5–7d **5/5**, and the narrative explicitly allowed a renewed downside retest after the sharp prior-week drawdown; ETH/BTC and breadth were weak. Risk warning ELEVATED and distribution UNKNOWN were **not** SELL permissions or a clocked start date.

Frozen W42 full-week range envelopes: BTC **$78,000–$88,000**, ETH **$2,260–$2,720**; observed incident lows remained inside these broad bands. The frozen **day 3–4 ETH envelope $2,320–$2,670 was breached by $2** at the external $2,318 low. Record this near-miss accurately and compare range width/coverage against simple equal-width, ATR/volatility and naïve envelope baselines; broad containment alone is not range alpha, timing skill or strategy utility.

**Official 14 Oct 01:18:44 UTC issuance**, ID CMP-20261014-3aa8ce4931eb, existed **11h11m before CPI**. Original 12h direction was BTC DOWN and ETH DOWN and the *owner-scored* immutable outcome records **CORRECT/CORRECT**, with BTC realized **-0.8075177637%**, ETH **-1.2492623252%** at its exact owner target clock. However, its registered naïve **persistence baseline also correctly predicted DOWN**. This is legitimate as-issued directional evidence, **not** demonstrated incremental model skill above persistence and not proof of forecasting the CPI surprise.

Owner artifact: 04_MARKET_LEARNING/handlekompas/official/outcomes/2026/10/14/CMP-20261014-3aa8ce4931eb_12h.json, Git blob **a8726869fe8594a19f3194c8c95b0a5b0f4a55b2**.

## 3. Complete *observed* five-attempt Official 14 October v3 12h readback (not an exhaustive all-version census)

Do not select only winning forecasts. These five owner outcomes are original records present when checked 15 Oct; the table is an audited **set of retrieved same-day attempts**, not a claim that all historical models/hours were exhaustively inventoried.

| Original issue UTC (Copenhagen +2) | Official 12h direction | Immutable owner BTC / ETH status | Owner realized BTC / ETH | Interpretation |
| --- | --- | --- | --- | --- |
| 14 Oct 01:18Z (03:18) | DOWN / DOWN | CORRECT / CORRECT | -0.81% / -1.25% | Genuine pre-CPI risk direction; naïve persistence also hit |
| 14 Oct 07:42Z (09:42) | MIXED / MIXED | ABSTAINED / ABSTAINED | -2.06% / -2.94% | No usable downside direction despite subsequent decline |
| 14 Oct 11:55Z (13:55) | UNAVAILABLE / UNAVAILABLE | ABSTAINED / ABSTAINED | -2.06% / -2.94% | No usable direction before publication |
| 14 Oct 13:49Z (15:49) | DOWN / DOWN | CORRECT / CORRECT | -1.31% / -2.33% | **Post-CPI** downside continuation, naïve persistence also hit |
| 14 Oct 21:47Z (23:47) | UNAVAILABLE / UNAVAILABLE | ABSTAINED / ABSTAINED | -1.22% / -3.38% | Missed chance to provide usable direction ahead of overnight leg |

Corresponding exact owner outcome paths under 04_MARKET_LEARNING/handlekompas/official/outcomes/2026/10/14/:
- CMP-20261014-3aa8ce4931eb_12h.json
- CMP-20261014-18699903db9f_12h.json
- CMP-20261014-e84827a7fb53_12h.json
- CMP-20261014-cdd1f365da26_12h.json
- CMP-20261014-34b416163f12_12h.json

**Warning on denominator:** same-day 12h target periods overlap; some original owners evaluate near-candle 12h windows that began **before declared issuance**. The native v3 receipt's effective window can be 12h while **forward time remaining after issuance is shorter**. The owner outcome preserves the native target clock but independently attested provider-first-known availability, investor-visible delivery and truly post-issuance exposure window are **not fully established**. Never re-score or declare an unbiased independent sample from these five overlapping outcomes.

Two CORRECT rows (of five observations) must **not** become a reported "40% model accuracy"; three abstentions are neither hits nor misses. A correct directional forecast with HOLD may be valuable, but "action_utility.result=PROTECTIVE" is the owner's **navigation proxy**, not after-fees avoided loss, executed selling, or outperforming buy-and-hold.

## 4. Shadow v2 identified another downside leg, with material limits

Original frozen Shadow output 04_MARKET_LEARNING/handlekompas/shadow_v2/forecasts/2026/10/14/SCV2-20261014-214817-0e099c6982e5.json, blob **490a1ad4beaf3e01df98da1feea39bb36cce8ba0**, issued **14 Oct 21:48:17 UTC (23:48 Copenhagen)**, using an older source packet generated **18:59:05Z**, source hash **9ae91623e8e2ab9e0d1a31fe996b9ce4e97cf2f6880ccc08a29c96071731e4f3**.

At issue, Shadow **12h DOWN / MEDIUM** with ELEVATED pullback risk and DETERIORATING transmission; **72h MIXED / LOW** and **168h NO_EDGE / LOW**. BTC was expected to be more resilient than ETH/observed alts, with intermittent rebounds; no unconditional crash magnitude or onset hour was forecast. Post-issue public Binance tape subsequently reached a BTC low of **$80,226.35** and ETH low of **$2,318.00**. These are **exploratory temporal corroboration**, not native matured owner results and not a calibrated hit claim. At the investigation cutoff ~09:32Z on Oct15, a literal 12h from Shadow's 21:48Z issuance was not yet complete. Do **not** retrofit the 18:00Z source candle as if it were a fresh 21:48Z close.

Importantly this forecast was **after** the CPI shock and after a significant first selloff, but **before** the next overnight decline. Log it as forecasting **continuation / a second leg**, not anticipating the catalyst itself. Shadow shares source families with Official and CN; three labels are **not three independent forecast votes**.

## 5. Independent T12 intraday challenger: positives, failure modes, censoring

Original T12 files under 04_MARKET_LEARNING/intraday_execution/direction_predictions/2026/10/14/:
- **07:37:39Z**: BTC 24H DOWN, ETH 24H NO_EDGE.
- **13:43:41Z**, after CPI: BTC 4H & 24H DOWN (5/6 vote agreement), ETH 4H & 24H DOWN (8/8). The strong intra-system ETH agreement remains **WARMUP** with no calibrated probability.
- **18:38:01Z**, after the early selloff: BTC 4H/24H DOWN 6/6, ETH 4H/24H DOWN 8/8, yet **24H horizons were not mature** at investigation cutoff.
- **22:19:09Z**: BTC DOWN but ETH **UP** on available horizons despite another subsequent ETH downside leg, a concrete vulnerable reversal hypothesis / contradictory signal to retain, not hide.

At least the **13:43Z 4H BTC & ETH** owner outcomes and the **22:19Z 4H BTC & ETH** owner outcomes are **CENSORED: EXACT_DUE_OWNER_CANDLE_MISSING_AFTER_GRACE**. Exact missed owner candles must remain censored even if current external Binance history contains the outcome. Do not substitute later data into the original register or score them as correct/incorrect. Owner calibration from 2026-10-15 07:25:40Z had 476 scored outcome rows, all T12 SHADOW_ONLY; group-local "independent" count is not global market shock independence.

This investigation is a useful **case-finding diagnostic**, but independent pre-shock T12 probability, frequency and incremental value have not been demonstrated. Require full issuance/rejected/pending/censored denominator.

## 6. Leading weakness and misleading recovery indicators

- ETH/BTC showed persistent weakness before and through the incident; ETH drawdown exceeded BTC and SOL was also weak. Use the ratio as an **as-of challenger predictor**, not a retrofitted justification.
- Top-100 proxy breadth jumped to **85/100 advancers** in the 14 Oct 01:14Z owner checkpoint but later fell to **12/100** at 15 Oct 04:51Z. The universes/membership hashes and rolling 24h observations differ. These are *two* snapshots from the same upstream family, **not independent repeated confirmations**. This is evidence of **failed persistence**, not evidence that 85% breadth was a proven buy.
- As of 15 Oct 04:36Z, CFGI market score ~29 (Fear), BTC 28 (Fear) and ETH 20 (Extreme Fear); these are descriptive post-selloff observations, **not** evidence of a prescient prior signal or automatic BUY.
- Latest provided **settled** ETF session in the Oct15 packet was **13 Oct**, BTC +$175.7m and ETH +$24.8m, even though the market subsequently fell. ETF flows are **time-lagged, flow-confirmation alternatives**, not permission to infer spot bid or an all-sessions net positive trend.
- Altseason source 15 Oct: BlockchainCenter 30d 49, 90d 45, 365d 39 (different windows/universes), none a confirmed broad altseason. The 14 Oct intraday breadth recovery must not be mislabeled "altseason ignition".

## 7. P0: Warning-to-action capability remains unproven

On 15 Oct the latest Official Daily Compass CMP-20261015-af12d4acf722 (blob **e0327828436b3b766e98559a435343d2815c9509**, issued **07:31:07Z**) changed to **NEXT_12H UP** because BTC and ETH gained relative to a prior packet. It retained **HOLD_WAIT**. This is consistent with the known code semantic where current/last-packet direction is extended as a descriptive near-term continuation; it is **not** verified predictive identification of a new bull phase. It should be tested against conditional rebound and downtrend baselines, not reclassified as a true reversal on one green interval.

The Official Protection Tracker said **pullback risk ELEVATED**, **distribution UNKNOWN**, **re-entry INACTIVE** and Sell Assessment **UNAVAILABLE_NO_GOVERNED_SELL_OWNER**. **No actual automated pre-sell warning delivery, wallet-specific trim, PnL saving or timely exit is verified**. Nor does a "HOLD" posture imply capital moved to cash.

**Pullback Learning ELIGIBILITY_STATUS_v1** has been **SUSPENDED_NO_ELIGIBILITY_CONTRACT since 2026-08-31**: observation collection and adaptive descriptive statistics allowed, but new mechanical episode classification, maturation, rebuy permission, portfolio actions and automatic rule changes disabled. This is a real **capability/authority gap**, not a failed live "pullback algorithm prediction" to falsify. Do not infer WARN→REDUCE/EXIT from the separate weekly risk warning; never resurrect retired proxy-entry/breadth authorities through a backdoor.

## 8. Falsifiable lessons / existing owners, ranked

| Rank | Hypothesis or operational gap | Controlled test and falsifier | Existing owner |
| --- | --- | --- | --- |
| P0-A | Early downside awareness is not converted to actionable investor protection | Whole-denominator, issuance-first warning→alert delivery→decision→hypothetical fills. Compare capital-matched HOLD, dynamic cash/trim, fees, slippage, missed rebounds and false warnings. No unapproved live execution | #1553 and Task2 R1/R2+ |
| P0-B | Official NEXT_12H is largely a price-delta nowcast repackaged as forward direction | Enumerate full v2/v3 separate cohorts; compare exact same-clock price-persistence, session momentum and conditional reversal. Demand incremental uplift on truly future after-issuance prices and independent shock families | #1596 |
| P0-C | CENSORED due-candle gaps suppress evaluability | Diagnose exact original owner capture chronology, missing candle pipeline and denominator; prospectively repair source logging without rewriting original outcomes. Separate illustrative cross-check analysis | #1596 + existing capture owner |
| P0-D | Pullback Learning cannot classify episodes because eligibility authority is suspended | Source-backed research-only eligibility specification; negative tests of old retired gates; independent review before any episode restart, code changes or user alert. Never assume proxy breadth is an action gate | #1553 |
| P1-A | Breadth rebounds can be short-lived | Track first-known membership-fixed breadth, persistence over successive samples and ETHBTC divergence. Baseline simple breadth slope and BTC-only momentum; exclude duplicate shared-upstream votes | #1596 / existing CN rotation |
| P1-B | Shadow continuation forecasts may recognize second selloff legs | Register all forecasts including NO_EDGE and wrong-side UP, exclude overdue/missing windows; compare to simple trend continuation, conditional on CPI/policy shock | #1596 / Shadow v2 owner |
| P1-C | Weekly CN range containment masks poor timing/excessive width | Compare W42 full band and day-3/4 ETH miss to strictly as-of ATR/volatility/naïve equal-coverage bands; proper scoring rule, event timing, and loss utility | #1596 / CN owner |
| P1-D | Macro surprise should be conditioned on release clock, not known before release | Freeze economic calendar as known before release; pre-vs-post CPI subgroup. Do NOT feed released CPI result into pre-release forecasts | #1596 / Task2 R1 |
| P1-E | T12 intraday agreement may overstate confidence | Full cohort by 1H/4H/24H, censored, abstained, family cluster, distinct issuance/vote groups; evaluate ETH UP misses as well as DOWN wins, no thresholds tuned on the crisis | #1596 |
| P1-F | Latest Official 12h UP can flip on a rebound while protection risk remains ELEVATED | Prospective 12h retest/continuation checks without changing live rule; distinguish "market now", prediction and SELL decisions; compare fixed persistence and state duration | #1553 / #1596 |
| P2 | Positive lagged ETF flows and fear readings do not guarantee price reversal | Compare as-of settled ETF timing, flows by ETH/BTC, CFGI sentiment and live liquidity, with negative controls and stale-flow flag | Task2 macro/rotation owner |

**Disconfirm the optimistic hypothesis:** a naïve same-clock momentum filter with matched issuance could identify the same down legs; the W42 broad CN bands could be too wide to add value; the stronger signals occurred only **after** the downside had started; investor capital may not have been defensibly saved because authorized action was unchanged. All these outcomes must remain possible.

## 9. Acceptance and routing contract

This file is an append-only incident learning **candidate**, NOT an R1-admitted causal or after-cost backtest, not a retrospective portfolio signal, not a standalone scanner, not a new source-of-truth or proposed automatic action. Main original immutable Compass/CN/Shadow predictions and owner outcomes remain unchanged.

Before any Task2 scientific claim: verify original first-known provider releases, original issue/delivery clocks, source/target timing, all issuance/abstention/censoring records and independent event-family clustering. Reproduce cheap baselines and investor utility with as-of restrictions; external post-event prices are **separate holdout-safe sensitivity diagnostics only when preregistered**. Nothing from this case is allowed to tune and then validate on the same event. Original control-plane research lineage in PR #1597 and research release doc 2026-10-14__TASK2_R1_EXPLORATORY_BASELINE_AND_SIMULATION_RELEASE_v1.md remain canonical research ancestors.

**Existing case handover anchors:** #1553 issue comment 6189071002; #1596 issue comment 6189077180 (pre-existing bounded comments). No new duplicate issue, automation, action owner, paid agent, portfolio execution, source threshold, calibration weight or webhook was created by this study.
