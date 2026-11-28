# Tolks cross-asset macro regime challenge, long-horizon Compass research intake

**Date:** 2026-11-15
**Status:** SHADOW_ONLY / SOURCE_BACKED_RESEARCH_INTAKE / HYPOTHESES_NOT_TESTED
**Area:** macro shadow, cross-asset transmission, long-horizon Compass, Cycle Navigator, Task 2
**Primary folder:** `04_MARKET_LEARNING/macro_shadow/`
**Related folders:** `04_MARKET_LEARNING/external_research/`, `04_MARKET_LEARNING/handlekompas/research/`, `06_RESEARCH_LAB/`
**Supersedes:** Nothing.
**Depends on:** existing FRED targeted/vintage macro owner; Sep 21 late-hike rotation note; Oct 18 PAICE cross-asset early-warning design; global-liquidity causal-chain preregistration; W46 pullback falsification; existing Task 2 #1596, risk #1553 and CN #1516; AGENTS.md and cross-repository source boundary.

## Decision

This is **one bounded research intake**, not a new model, trigger, signal, score, task, workflow, sensor collector, regime override, data purchase, public site change, portfolio action, or claim of predictive edge. It does not activate a test of restricted Round 3 data. It must not displace existing work or enter S1's autonomous merge queue as a release-sensitive change.

Research question: **Does the *change in the expected policy path*, combined with evidence of credit/equity tightening and risk transmission, improve long-horizon crypto regime and drawdown forecasting beyond already-existing Macro Shadow, FRED, crypto flow and price baselines?**

A second question is symmetric: **Can the same framework reliably distinguish a harmful hike regime from a growth-resilient, ample-reserves hike regime in which risk broadens later?** No one-way bearish model is acceptable.

## Exact public primary source and claim boundaries

- Author: @_tolks on X, 2026-11-14 18:10:54 UTC. Original https://x.com/_tolks/status/2121667201212023070 .
- Source thesis (claim, not independently verified forecasting performance): blaming Binance/CZ alone misses a broad macro shock; a changed hiking/policy path, higher DXY/yields and large technology/AI losses may represent a systematic withdrawal of risk capital. Elections, AI regulation and specific fraud allegations are **source opinion/causal narrative, not admitted measurements**. No positive track record, predictive lead time, methodology, original signal issuance clock or no-warning denominator was provided.
- No Tolks chart series or numerical value is admitted from embedded images without separately verifying the exact instrument, time range, return type and timestamp. Social-media opinion may propose a test, never directly determine a Compass forecast.

## Public cross-check, known as of 2026-11-15

### Primary official policy truth

1. Federal Reserve 2026-09-16 statement: +25 bps to 3.75%-4.00%; economic activity described as solid, policy maintaining ample reserves.
   https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm
2. Fed 2026-10-28 statement: target **held** at 3.75%-4.00%, strong activity, 10-2 vote with two dissenters preferring a hike. A second actual hike is **not established** by these meetings.
   https://www.federalreserve.gov/newsevents/pressreleases/monetary20261028a.htm
3. The Fed implementation notes allow T-bill purchases as needed to maintain ample reserves; policy-rate tightening **is not equivalent** to a mechanically verified drain of reserves.
   https://www.federalreserve.gov/newsevents/pressreleases/monetary20261028a1.htm

### Public institutional source, *as reported* (not separately recomputed from vendor tapes)

Coinbase Institutional, **2026-11-13**, "Weekly: From Hack to Hawk":
https://www.coinbase.com/institutional/research-insights/research/weekly-market-commentary/weekly-2026-11-13
- Futures reportedly priced about **64 bps of Fed hikes over the coming 12 months**, versus about 37 bps earlier in November. This is a **forward market expectation**, not an enacted FOMC policy path.
- Broad dollar index is reported about **102.9**, highest since April 2025; methodology/time must be preserved. FRED `DTWEXBGS` is a **different** broad dollar index and must not be presented as a mathematically identical DXY series.
- 30-day supply change reportedly **-$11.5 billion** for USDT/USDC/DAI. Treat as a published sample-specific estimate, not an all-stablecoin network total.
- U.S. spot BTC ETF net outflow reportedly about **$1.44 billion** over five trading sessions ending November 11; not equivalent to total investor capital flows or instantaneous BTC spot sales.
- Coinbase also notes crypto-specific amplifiers such as index treatment of Strategy, persistent derivatives positioning, Coinbase premium and BTC technical levels. Those must be retained as alternative and interacting drivers, not explained away by macro.

Chicago Fed NFCI/ANFCI documentation: https://www.chicagofed.org/research/data/nfci/about and weekly publication schedule: https://www.chicagofed.org/research/data/nfci/current-data
These measure aggregate financial conditions across credit, risk and leverage. **Level, slope, calendar release and revisions differ**. The indexes can diagnose tightening but are not crypto leading indicators by definition.

## Conflict discovered in existing canonical archive

Existing 2026-09-21 external research:
`04_MARKET_LEARNING/external_research/2026-09-21__late-hike-rotation-regime__shadow.md`
- H_LATE_HIKE_BREADTH_TRANSMISSION: rates can remain elevated while growth, ample reserves, steady long yields/credit and eventual equity breadth allow later risk transmission.
- Clearly labels this as SHADOW_NOTE_NOT_ACTIVE_TEST and gives no crypto deploy permission.

Existing 2026-10-18 PAICE external macro research:
`04_MARKET_LEARNING/macro_shadow/2026-10-18__paice-equity-earnings-inflation-credit-crypto-drawdown-pit__shadow.md`
- H1 proposed that adverse earnings-expectation revisions, credit/financing and inflation/valuation interaction might give advance notice of equity drawdowns and later crypto stress; **TEST_NOT_RUN**.
- Explicitly requires as-known-then vintage, no-warning denominators and price controls.

Existing causal-chain methodology:
`04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1/PREREGISTERED_ANALYSIS_CONTRACT_v1.md`
- Already specifies requirement vs delivered liquidity, DXY/real yields/credit/volatility transmission, multiple eras, real-time vintage, expanding walk-forward, a final holdout, ablations, and kill criteria.

**Novel contribution is NOT a fresh list of macro data feeds.** It is a falsifiable *two-sided conditional scenario contest*, especially the distinction between actual policy rate and policy-path repricing in the weeks before a decision. It cross-links existing source owners rather than duplicating them.

## Candidate competing scenarios, no live state assignment

1. `GROWTH_RESILIENT_HIKE`: policy rates elevated/higher while growth, credit, reserve liquidity and breadth hold. A subsequent small-cap and crypto broadening is *possible*, never automatic.
2. `POLICY_REPRICING_RISK_OFF`: expected rate path and real yields/dollar tighten, credit/risk and equity breadth weaken; later BTC/ETH/alt stress is the hypothesis.
3. `GROWTH_SHOCK_EASING`: projected cuts and falling nominal yields coincide with earnings/credit deterioration. "Fed will cut" is not intrinsically bullish.
4. `CRYPTO_IDIOSYNCRATIC_STRESS`: crypto ETF, stablecoin, issuer/index, miner or derivatives stress dominates while broad financial conditions remain relatively stable. This is an essential negative control against attributing all shocks to macro.

All four must have pre-known, explicit entry and exit conditions *before future evaluation* and may legitimately return UNKNOWN/INCONCLUSIVE. They cannot be fitted to November 2026 after observing its outcome.

## Proposed source map, reuse only

| Axis | Existing candidate/source | Control |
|---|---|---|
| Actual policy | Fed FOMC statements + FRED DFF | Decision-publication clock |
| Expected policy | timestamped futures probability / curve if legitimately available | Exchange market timestamp, no ex-post SEP substitution |
| Real and nominal duration price | FRED `DGS2`, `DGS10`, `DFII10`, `T10Y2Y` | As-of daily closings and publication lag |
| Dollar | FRED `DTWEXBGS`, separately licensed DXY only if available | Never equate index methodologies |
| Credit/funding | `BAMLH0A0HYM2`, `BAMLC0A0CM`, `NFCI`, `ANFCI` | Release/vintage and shared-component correlation |
| Actual monetary balance | `WALCL`, `WRESBAL`, `WTREGEN`, `RRPONTSYD` | TGA/RRP decomposition, units and weekly release |
| Inflation/slow activity | CPI/PCE/payroll/growth, exact BLS/FRED release vintages | No slow-macro values before their release |
| Equity transmission | Nasdaq and S&P equal-weight, Russell vs large caps, semiconductors, market breadth | Exact index composition, point-in-time series availability |
| AI leverage/capex | issuer filings/issuer credit or earnings revisions if sourced | SOURCE_UNAVAILABLE until release-bound and legitimate |
| Crypto transmission | existing approved BTC/ETH prices, ETF/stablecoin/ETHBTC/breadth & risk output | Private raw market data stays in restricted plane |

**No new collector is authorized.** First output should be an availability/clock matrix for the original approved source owners. All market data sources not point-in-time admissible remain `SOURCE_BLOCKED`.

## Long-horizon Compass scientific design, not executable yet

- Research endpoints: **4 weeks, 13 weeks, 26 weeks, and 52 weeks**, plus an explicitly separate 1-3/5-7/2-3-week risk warning lane. These are candidate test horizons, not currently available priced forecasts. The existing `scripts/learning/forward_price_admission_horizon_guard.py` explicitly marks 30d/56d priced models `PRICE_MODEL_NOT_IMPLEMENTED`, so no long-horizon price target or calibrated probability can be claimed from this note.
- Compare exactly matched forecast timestamps and available feature clocks. Current 2026-11 case is an **exposed development example**; an untouched future cohort is required.
- Competing baselines: B0 price-only/40-week trend; B1 current Macro Shadow/FRED; B2 B1 plus *rate-path repricing*, not merely the funds-rate level; B3 B1 plus independent equity/credit contagion; B4 existing crypto ETF/stablecoin/breadth inputs; B5 interaction model after redundant features are removed.
- Outcome families: directional 4/13/26/52-week BTC and ETH returns, drawdown / drawdown-onset from forecast timestamp, realized risk, BTC-vs-alt participation and risk-warning lead time. Define event thresholds and loss costs **before** outcome inspection. Distinguish regime scoring from range-price scoring and investor after-cost utility.
- Control macro *reaction*, not just level: rate-expectation change, 2Y/real-yield changes, dollar trend/slope, credit-spread change, equity breadth changes and stability after shocks. Differentiate early warning from a lagging post-crash confirmation.
- Test condition-specific effects and interactions (credit stable vs widening; earnings holding vs deteriorating; reserves ample vs falling; BTC flow stable vs contracting), with sign reversals and ETHBTC/alt separate.
- Use event/era clusters; negative episodes and all eligible nonwarning periods; block bootstrap; shuffled timestamps, instrument substitution, lagged and future-data leakage sentinels; release-vintage checks; ablation for shared drivers; 2024+ ETF regime as separate sample but do not overfit to it.
- Skill gate: no long-horizon promotion unless positive **incremental out-of-sample** skill over best simple control, stable across eras/regimes and robust to source lag and revision; if underpowered mark INCONCLUSIVE.
- Economic gate separate: warning is not an authorized SELL. Compare after-cost counterfactual paper benefit to HOLD and trend only once original investor delivery/fill eligibility and existing economic gate authorize it.
- No retroactive upgrading W46 risk 3/5 to 4/5 or 5/5 from the observed selloff.

## November W46 diagnostic, not a new scored sample

Existing `04_MARKET_LEARNING/handlekompas/research/2026-11-13__W46_PULLBACK_FAILURE_RPL_V1.md` identifies a Friday BTC price below issued Friday and weekly lower bounds (partial-week snapshot), a static ELEVATED risk pass-through and incomplete long-horizon original source coverage. The file prescribes existing original Task 2, risk and CN owners, and has already rejected repeated generic studies.

This macro challenger should therefore ask:
- Did *before-issuance* policy-path repricing and broad risk transmission contain nonredundant information absent from the issuer?
- Could that information have legally reached the issuer/consumer before a loss, and would it reduce false-warning or delayed-warning cost?
- Or were the macro indicators already late, redundant with BTC trend, or too coarsely published?

No asserted answer is allowed until admitted data and real prospective outcomes exist.

## Stop / falsification conditions

1. No authenticated historical first-known event clocks or no published source for expected Fed path.
2. The effect disappears after BTC trend, real yields, dollar, credit and equity breadth.
3. Benefit exists only for current-vintage levels, disappearing on as-known-then changes or actual future outcomes.
4. Forward lift is concentrated in a single crisis (especially 2026-Nov) or reverses in late-hike growth-led expansion.
5. The "macro" model wins only by calling everything risk-off, has excessive false alarms, loses rebound upside or provides no longer lead time.
6. One unverified source label, social post or retrospective AI-sector claim is being used as a proxy for objective data.
7. No incremental utility for a legitimate investor after latency and trading frictions. Or the candidate adds no value beyond current existing models.

## Disposition and next finite action

- **Preserve** this bounded source-aware hypothesis with status `SHADOW_ONLY / NOT_EXECUTED`.
- **Deduplicate** within existing Macro Shadow/Research Lab, especially Sep 21 late-hike, Oct 18 PAICE, Global Liquidity causal-chain, Task 2 #1596 and W46 risk #1553.
- **Next action for existing research owner only:** produce a one-page as-of availability/first-known matrix and a pre-registered, signed competing scenario spec; review before any analysis. If covered by existing owners, append the new conditional policy-path distinction there, do not start a second experiment.
- **No new automation, workflow, API spend, model agent, source collector, release authority, public site output, state alteration, threshold, or merge is requested or granted.**
- Source note is suitable for reviewer consideration. An approved paper is not a successful backtest; a PR is not a merged source of truth.


## Academic cross-check: macro sensitivity does not establish predictable lead time

- IMF Working Paper 2023/163, *The Crypto Cycle and US Monetary Policy*: https://www.imf.org/en/publications/wp/issues/2023/08/04/the-crypto-cycle-and-us-monetary-policy-534834 . The study reports that a common crypto factor explained around 80% of variation in prices in its sample and that US monetary contraction negatively affected that factor through risk taking. These are *sample-specific empirical findings*, **not** 2026-out-of-sample results or a calibrated long-horizon Bitcoin forecast.
- IMF Global Financial Stability Note 2022, *Cryptic Connections*: https://www.imf.org/en/publications/global-financial-stability-notes/issues/2022/01/10/cryptic-connections-511776 . Equity-crypto spillovers became more pronounced after the pandemic. The co-movement is potentially **bidirectional**; a falling Nasdaq does not by itself prove Nasdaq caused the next Bitcoin fall.
- IMF Working Paper 2023/213, *New Evidence on Spillovers Between Crypto Assets and Financial Markets*: https://www.imf.org/en/publications/wp/issues/2023/09/30/new-evidence-on-spillovers-between-crypto-assets-and-financial-markets-539476 . Cross-market spillover direction and intensity vary in financial stress periods, so static correlation/cross-asset risk flags may mislead.

**Implication:** retain bidirectional and common-driver null hypotheses. Study **incremental before-event lead time** against price-only and existing financial-condition controls, not retrospective correlation. An econometric finding for 2017-2023 cannot be imported as a verified 2024-2026 ETF-era predictive coefficient without revalidation.
