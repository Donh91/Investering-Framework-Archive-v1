# Hyperliquid listing decay, executed 18m historical study, exact-head receipt
**Date:** 2026-11-10. **Status:** `EXECUTED_NATIVE_CI / DESCRIPTIVE_RETROSPECTIVE / NO_PROVEN_TRADING_EDGE / SHADOW_ONLY`.
**Original domain owners:** Task 2 #1596, Ironflow #1747, derivatives #387; downstream: Meme Alpha Lab #22.

## Native verification and source receipt
- Original PR: https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2078
- Executed HEAD: `1736dc4ba606b493c9e74fd2b7677fe31877f172` at native test time.
- Native Actions run: https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/42874238160, **completed SUCCESS**, all three jobs successful.
- Specific historical 18m job ID `130033179794`, SUCCESS, with **6/6 new synthetic negative tests** plus 28/28 pre-existing Ironflow tests.
- Native Actions artifact **`ironflow-task2-full18m-walkforward`**, artifact ID `13790384408`, ZIP byte count `54,636`, ZIP SHA256 `acbe144603199a862cd62933e0dec7c413796e466e2485679d6a4adcb9cbf644` (locally inspected downloaded Actions ZIP). The ZIP includes three exact result files plus original T1 and walkforward. Short retention, not an immutable raw data archive.
- Exact JSON member `LISTING_DECAY_ENTRY0_20BPS.json`: byte count 81,606, SHA256 `583f08c19d09e9b0c4926495c893b19af2b32bc8ddcb2a6ee74ce14d0c04f037`. Sensitivity 7d: SHA256 `98aa61dc86ff4c21083089f1ed43d5dbcf6f9a94e296505f418cf4bb2075d6a3`; 40bps: `0959996546dfe9d67bd1370b4af6ceae37c865fc65eb3a81bd6b0bff006e3ffe`.
- Public source: **Ironflow (ironflow.sh)** hourly market candles, CC BY 4.0, pinned HF commit `9f262cc27d89112b8c56550cf4c9455346f5eece`; monthly SHA256 members in Actions artifact. Publisher historical data are November-2026-publication retrospective research, not past-time market predictions.

## Actual results, baseline entry
34 native Hyperliquid core perp markets qualify as first-observed-trade **proxies** for new listings, **not 0xArchive's original official 116-listing cohort**. Study requires 45d dataset-left buffer and full 30d outcome maturity, uses UTC first trade day + two full calendar-date boundaries as target entry, then the first trading hourly OPEN at/after target. All 34 have a within-1h 30d exit; no selected asset 30d censorship in this *selected native core* cohort (does not prove all delistings in a broader universe were included).

| Due from entry | N | Falling N | Falling % | Median raw price return |
|---|---:|---:|---:|---:|
| 1d | 34 | 20 | 58.8% | -3.88% |
| 3d | 34 | 22 | 64.7% | -8.17% |
| 7d | 34 | 24 | 70.6% | -18.93% |
| 14d | 34 | 26 | 76.5% | -26.81% |
| 30d | 34 | 31 | 91.2% | -37.21% |

Pairing (33/34; first case PUMP no old 60d matched control in observation window): median 30d new-minus-ex-ante-matched-old token return **-18.996 percentage points**. Month-block resampling (11 paired entry months), exploratory 95% interval **[-24.19,-6.05] percentage points**. 26/33 pairs have negative excess; a naive sign test p=0.00132 would assume pair independence and must NOT be called prospective evidence. Median matched difference remains -14.4pp in the 20 cases after excluding the 14 Sept/Oct 2025 cases, but date-regime controls not fully equivalent.

**Delayed entry +7d**: 34/34 observed 30d exit, 29/34 (85.3%) falling, median -36.52%; matched excess -15.10pp, block-bootstrap CI [-30.70,-9.84]pp. **40bps roundtrip friction** does not change the price-return and paired-excess statistics (it changes only simplistic position-net), as expected. No funding/margin/liquidation/execution depth modeled.

## Red-team: hidden open-short risk is extreme
The historical 30d ending prices do NOT validate the proposed stopless leveraged short book.
- **FOGO** ends **-19.14%**, yet from modeled entry its 30d maximum hourly HIGH is **+912.65%**. A hypothetical short sized at 5% of account NAV by *notional*, ignoring actual liquidation/fills, faces approximately **-45.63% whole-account mark-to-market** at that extreme, from this ONE position, before other shorts or fees. If 5% means margin with leverage, liquidation can occur well before the final day.
- **XPL** ends **+54.22%**, maximum adverse short path **+358.55%**.
- **ZEC** ends **+226.74%**, maximum adverse short path **+252.43%**.
- **PONS** ends **+15.39%**, maximum adverse short path **+122.61%**.
- 16/34 cases had adverse-high >25% from entry, 9/34 >50%, 5/34 >100%, 3/34 >200%, 2/34 >300%. Observed HIGH is an hourly candle extreme, not proof executable cover price or native liquidation; it is sufficient to falsify the notion that 30-day ending win percentage represents drawdown safety.
- Median short adverse-high excursion **+23.35%** of entry price, mean **+71.50%**, strongly right-skewed. Ending median is distinct from worst intraperiod short risk.
- Ending outcomes: 31/34 downward, mean underlying 30d return -27.03% vs median -37.21%. Non-typical outsized positive tail distorts results. **Do not calculate a portfolio equity curve, drawdown or annualized Sharpe from these unweighted paths.**

## Material interpretation cautions
1. This is **first observed native core perp market**, **not underlying token creation**, and some entrants are mature crypto tokens (e.g. ZEC, XMR, AXS, DASH, ICP). Do not transfer the result mechanically to DEX microcap launches. Source cannot independently confirm exact first official listing dates or external prelisting token age.
2. Match is a heuristic 5 nearest older perps (60d+), built from observed 24h log momentum, volatility and log notional at entry; no exact cap, sector, market-wide beta, live funding, initial pricing timestamp or original tradebook 44-fill universe. Median paired difference is descriptive, NOT randomized/counterfactual causal evidence.
3. Concentration: 14/34 (41.2%) listings in Sept-Oct 2025. Excluding those months still shows 18/20 declining with median -20.61% and median paired excess -14.41pp, but leaves a smaller sample.
4. By construction first-observed-trade proxy and left censor can omit market types (HIP-3, spots), delisted markets outside timestamp eligibility, or originally launched coins from pre-observation periods. All 34 exits observed is an empirical fact about this cohort, not proof the broad listing universe has no delisting/survivorship bias.
5. No automatic trade authority, no conventional short risk-stop claims, no inference that 0xArchive's 74.6% (44 trades) replicated, and no verified independent forward holdout.
6. Historical cohort was selected after the publisher's X insight, so despite time-ordered source prices this is a **research development sample**, NOT untouched OOS.

## Scientific continuation and owners
- **Claude:** independent code/security/statistical review of exact HEAD and original 30-day risk/causal claims. Prioritize FOGO XPL ZEC price-path checks against original Hyperliquid candleSnapshot, first-trade and possible seed-time errors; quantify whether 5% equity intended margin or notional.
- **Grok:** disprove listing-specific edge with a fully same-clock older-short basket, prior-token momentum, BTC regime-matched placebo, HIP3 separate cohort and official exchange listing dates; crosscheck Coincise contradictory endpoint.
- **Task 2 / S1:** keep original domain #1596 and Ironflow owner #1747; use native review and exact-HEAD CI, do not auto-promote to production or real short execution. Evaluate durability of 11-month bootstrap with last-month holdout and leave-one-month-out, unknown first-known controls; existing Research Parallel Lanes only.
- **Alpha Lab #22:** apply descriptive hypothesis to token lifecycle (t0 original launch vs first perp listing), after-launch dip/maturation, tail winner false-negative penalty, and prospective frozen 1/3/7/14/30d metrics. No new feature authority from this backtest.

**Highest priority next falsifier:** build a margin-aware *path-to-liquidation* independent replay with realistic funding, spreads, execution and portfolio co-occupancy; compare stopless short vs same-regime generic short and spot/perp listing-age cohorts. No capital or API billing authorization in this study.
