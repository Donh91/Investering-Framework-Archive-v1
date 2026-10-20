# PAICE equity-risk thesis -> crypto drawdown early-warning falsification

**Dato:** 2026-10-18
**Status:** SHADOW_ONLY / SOURCE-CLAIMS-UNVALIDATED / TEST-NOT-RUN
**Område:** Macro Shadow, cross-asset risk transmission, Task 2 scientific research
**Primary folder:** `04_MARKET_LEARNING/macro_shadow/`
**Related folders:** `04_MARKET_LEARNING/external_research/`; `06_RESEARCH_LAB/`; `04_MARKET_LEARNING/handlekompas/research/`
**Supersedes:** Nothing
**Depends on:** Existing FRED Macro Shadow canonical owner, existing Research Lab PIT and no-hindsight integrity gates, existing Compass/CN protection and source boundaries

## Decision and authority

A user supplied images of a Danish-language Lars Christensen / PAICE social-media post and chart (seen in conversation 2026-10-18). On 2026-10-18 the framework owner explicitly approved preserving the research idea. **Approval means source-aware SHADOW research intake, NOT approval of the author's crash prediction, new data collectors, tests on closed Round 3 evidence, trading/portfolio decisions, model promotion, automatic alarms, thresholds, fees or paid data.** The original screenshots remain user-supplied conversation evidence; do not copy, redistribute, or treat them as a licensed public dataset.

**Status at creation:** a documented hypothesis and prospective study design only; no executable backtest, validated PAICE model implementation, scored win rate, new signal, forecast or production integration. Existing active market rules, weekly frozen forecasts, owner clocks, dataset commitments, and source-provider boundaries are unchanged.

Routing: reuse `04_MARKET_LEARNING/macro_shadow/2026-07-05__fred-classic-targeted-series-production-upgrade__canonical.md` (targeted FRED, vintage, slow macro context; explicitly no execution); `04_MARKET_LEARNING/external_research/2026-09-21__late-hike-rotation-regime__shadow.md` (counterargument: high rates can coexist with growth and later breadth expansion); `06_RESEARCH_LAB/shadow_layer_historical_effectiveness_v1/02_MASTER_SHADOW_SENSOR_INVENTORY.md` (macro context, not established incremental predictive edge); Task 1.5 / Task 2 issue #1596 and existing EDGE Compound Governor issue #1530 only if a later evidence-bound material delta appears. No duplicate macro owner, scheduler or new operational queue.

## 1. Source claims, independently verified facts, and unknowns

### A. What the screenshot/post actually argues (CLAIM, NOT EVIDENCE)

The author argues that US stocks are expensive while inflation and nominal yields are elevated; strong corporate earnings and expectations have thus far kept valuations afloat; declining *earnings expectations*, not just trailing earnings, might catalyze a correction. The image purports to show previous S&P 500 peaks before declines of at least 15%, plotting CAPE relative to its decade median against the 12-month *change in inflation*; it depicts current September 2026 toward the upper/right area, plus several historical percentile indicators. It also references AI datacenter financing, Anthropic's alleged sequential growth deceleration, South Korean equity weakness and a PAICE model warning to reduce equity exposure without selling everything.

**Unverified source-specific numerical/model claims (do not admit as measurements):**
- "Nine of ten" historical qualifying peaks with rising inflation and "seven of ten" with expensive CAPE; selection of peaks, dates, sampling, denominator and false alarms are undisclosed.
- Chart percentiles (e.g. 87% 10Y yield increase, 75% CAPE, 71% low equity-risk premium, 63% inflation): not probabilities of a correction, and definitions/measurement vintage not independently replicated.
- Earnings growth around 33% year-on-year and rarity above 8% of months since 1960; sample, index, constituent and publication methodology unavailable.
- Anthropic quarterly revenue growth allegedly ~50% after ~140%; private-company numbers, dates and financial statements not established by the supplied screenshots.
- PAICE's model performance, actual historical as-issued alerts, false positives, warning horizon, lead-time and performance vs buy-and-hold are unknown. A retrospectively selected historical-top chart is **not** an audited out-of-sample alert track record.
- Claims about a Korea five-session drop, particular Friday equity-index changes and the exact chart observation clock require date-aligned original exchange/index sources before analytical use.

### B. Independently checked macro observations (PUBLIC)

- **US CPI September 2026:** BLS published 2026-10-14 08:30 EDT (=12:30 UTC); headline CPI **+3.7% YoY, +0.6% seasonally adjusted MoM**. Source: https://www.bls.gov/news.release/archives/cpi_10142026.htm . The actual CPI report value is **not knowable before that release**; older expectations must be separately timestamped.
- **US 10-year nominal Treasury yield:** the existing FRED H.15 series `DGS10` is an appropriate public owner; date-stamped ALFRED/FRED observations around Oct 14/15 are >5%. Do **not** treat the publication date, real-time market print and later-revised FRED value as equivalent. Primary reference: https://fred.stlouisfed.org/series/DGS10 .
- These observations support **macro risk context**, not a claim that a 15% S&P decline or crypto liquidation is imminent. At documentation time the PAICE chart's CAPE level and backtest have **not** been independently reconstructed from timestamped source vintages.

## 2. Research question: incremental *early* warning, not confirmation after a dump

**H0 / null:** adding preknown equity valuation + inflation acceleration + earnings-expectations deterioration + credit/funding deterioration to the **existing** macro/crypto risk baseline does **not** provide statistically and economically defensible *incremental* warning of future US equity and crypto drawdowns.

**H1 / challenger:** when actually available as of decision time, **revisions to forward earnings estimates and adverse equity financing/credit conditions**, interacting with high valuations and inflation/rates, may offer earlier or more reliable warnings of major equity stress and subsequent BTC/ETH/altcoin drawdowns than the baseline. Unreliable, late, or nonincremental components are rejected.

The specific falsifiable question is: Can a frozen challenger alert ahead of the beginning of adverse drawdown windows, with acceptable false-alert burden and consistent incremental information, **rather than simply react to rising VIX or already-falling prices**?

**Prior:** weak-to-moderate plausibility. Stretched CAPE and inflation are slow regime conditioners; neither is inherently a market-timing trigger. Improving earnings, policy liquidity and financial conditions are plausible countermechanisms. Equity and crypto may decouple, and crypto beta may react on a different lag.

## 3. Proposed input families and first-known constraints (NO NEW DATA PURCHASE)

| Family | Suggested existing/possible public owner | Mandatory anti-leakage discipline |
| --- | --- | --- |
| Headline/core CPI, *change* in CPI | BLS releases + existing FRED `CPIAUCSL`, `CPILFESL` | Release timestamp + contemporaneously published vintage; calculate delta only from releases known then; no latest-revised retrofill |
| 10Y and real rates, curve | FRED `DGS10`, `DFII10`, `T10Y2Y` | Daily close and vendor publication/availability UTC, no mixing with intraday execution |
| Credit/funding stress | FRED `BAMLH0A0HYM2`, `BAMLC0A0CM`, `NFCI`, `VIXCLS` | Spread/as-of/vintage timing, holiday and stale handling; same upstream families not independent votes |
| Valuation | Shiller CAPE / inflation-adjusted earnings source (availability TBD) | Point-in-time monthly CAPE, methodology and revisions; exclude until actual release history is provable |
| Forward earnings revisions | Timestamped I/B/E/S / FactSet / S&P consensus **only if licensed or legitimately accessible**, otherwise SOURCE_UNAVAILABLE | Forecast-vintage *as known then*, index universe, fiscal-period definitions, survivorship and post-event restatements; NEVER replace with subsequently realized earnings |
| AI data-center credit exposure | Public bond spreads, refinancing and issuer filings only after independently sourced | Treat as exploratory mechanism/context, not an admitted indicator or sector-wide quantitative series without coverage |
| Crypto transmission | Existing BTC, ETH, ETHBTC, breadth, drawdown/outcome owners | Exact freeze/availability, matched horizon, beta/regime control; never promote ETF reporting-lag or proxy breadth to trading permission |

First stage: **coverage and availability audit only**, not a claim that these series are all currently accessible. Favor the framework's already-approved FRED targeted/vintage route. Paid vendor feeds or any new external collection require separate authorization.

## 4. Falsification protocol: design to freeze before feature/outcome inspection

1. **Pre-register the question, event universe and horizon.** Candidate *research labels*, NOT live signals: S&P 500 peak-to-trough drawdown >=15% over a separately frozen prospective horizon; predefine separate 10% and 20% sensitivity checks and 3/6/12-month windows before running tests. A "peak" must be identifiable without knowing its later maximum. Risk is measured only from the actual as-of warning clock, not the later identified perfect top.
2. **Independent denominators:** include **every eligible decision week/month, non-event, and false alarm**, not only the ten selected crisis peaks. Compare alert opportunity frequency and coverage. In a rare-event problem, "9/10 prior peaks" without a non-crisis denominator does not establish positive predictive value.
3. **PIT baseline:** existing FRED/rates/credit/VIX/liquidity, cross-asset breadth, price/momentum/volatility and existing Compass protection context, *frozen at each clock*. Test additions separately (CAPE; inflation acceleration; earnings revisions; financing stress) and then jointly, with redundancy/collinearity ablations. Avoid double-crediting shared FRED inputs.
4. **Anti-hindsight splits:** chronology-based development/test split with purge/embargo for overlapping 3/6/12-month targets and market-shock clusters; no hyperparameter tuning on an untouched validation interval. Handle small event counts, revisions, regime changes and calendar coverage explicitly; if underpowered report INCONCLUSIVE. Any known 2026-10 episode is **development/context only**, never clean holdout.
5. **Negative and placebo controls:** shuffled/lagged permitted feature timestamps; fake future/revised-time features as contamination sentinels; inverted/mismatched event clocks; regime-matched naïve controls; compare forecast availability and missed periods rather than silently filtering failures.
6. **Evaluation:** event-level time-to-first *eligible* warning before the first drawdown breach, false alarms per year, precision/recall with base rates, Brier/calibration only for actual prospective probabilities, conditional drawdown/MAE, confidence intervals via era-block bootstrap, incremental net information over baseline and stability by regime. Overlap and common shocks must not inflate n. Costs, turnover and investor utility stay **research counterfactuals**, never simulated actual fills unless independently justified.
7. **Crypto linkage is a separate test:** estimate whether equity-risk warnings lead BTC/ETH drawdowns *after* controlling contemporaneous crypto trend/volatility and regime. Test zero/positive/negative lags and out-of-sample incremental lift; do not assume "US stocks crack = crypto sells" is causally established.
8. **Go / no-go:** stop if estimate vintages/source access cannot be established, high false-positive rates erase usefulness, information is merely reactive, results depend on hindsight-labeled tops, incremental uplift disappears after simple baseline controls, or cross-era stability fails. **No backtest executed or positive result claimed by this note.**

Before any implementation, the existing research owner must provide exact eligible source manifests, release calendars, a frozen machine-readable feature/event specification, controls, measurable acceptance gates, and an independent method review. This note alone does NOT authorize changing the frozen Round 3 registry or running Round 3 hypothesis tests (currently OFF).

## 5. Operational constraints / routing

- **Owner:** Existing Macro Shadow / Research Lab scientific evaluation; Task 1.5 / Task 2 #1596 for PIT / no-hindsight methods; #1530 only for verified material deltas. Existing Compass risk-to-action #1553 for context **after** scientific review. This is a read-only proposal/handoff, not a new owner.
- No new scheduled job, supervisor, agent, API route, paid service, monitoring automation, standalone PAICE model, weight, threshold, alert or sales rule.
- Existing FRED rule: `FRED Macro != daily crypto trigger`; no change to Official, Native, Shadow forecasts, Master Monday freezes, Cycle Navigator phase/state or pullback eligibility.
- Do not auto-execute BUY / REDUCE / EXIT, do not use the supplied chart's "red lights" as an owner signal, do not claim PAICE model accuracy, and do not fabricate historical forecast receipts.
- Public repository must remain free of private normalized/provider data, private raw payloads, wallets or credentials. Restricted records stay in `Donh91/secrets`, with exact receipts and permissions. No Round 3 outcome scoring or hypothesis evaluation before separate permission.
- Promotion would require actual PIT record integrity, source licensing, independent review, CI and existing canonical governance; absent these, permanent disposition is **SHADOW_ONLY / RESEARCH-INCONCLUSIVE**.

## 6. Research acceptance checklist (currently ALL OPEN)

- [ ] Source provenance and original PAICE methodology/underlying series documented, or marked unavailable
- [ ] Full historical non-event denominator and alert timestamp policy frozen
- [ ] All chosen feature *first-known UTC* times and original vintages verified
- [ ] Comparable baseline, ablations, placebos and event-cluster controls frozen
- [ ] Separate equity prediction and incremental crypto-warning targets pre-registered
- [ ] Power, overlap, and missingness examined independently
- [ ] Honest zero/negative/positive results, false alarms and abstentions logged
- [ ] Independent scientific review before any promotion
- [ ] Governance and Round 3 firewall separately satisfied

**Immediate deliverable of this case:** a source-categorized, falsifiable Shadow research specification suitable for bounded intake by the existing Task 2 owner. **NOT** evidence that a correction will happen, that PAICE timed one, or that the user's investment allocations should be changed.
