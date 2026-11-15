# Task 2 / Kompas Pro 2.x | W46 emergency pre-W47 diagnostic, 15 November 2026

**Scientific owner:** original [Archive Task 2 #1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596). **Risk owner:** #1553; original CN #1516/#1593; source #1827.  
**Status:** `READ_ONLY_EXTERNAL_SPOT_RESEARCH_EXECUTED / NATIVE_ASTRA_NOT_RUN / W46_FINAL_NOT_MATURE / NO_MODEL_PROMOTION`  
**Original source baseline:** Archive main `ccda63aca7c70d09156ac15f0ecb5c5a2247c13b` before research branch; original W46 forecast Git blob `88032832eb5bf5ebbedcd0dcd5f136c6e2ed2961`.  
**Data capture:** public Binance Spot hourly BTCUSDT, ETHUSDT, queried at **2026-11-15 12:56:33 UTC**. The Binance HTTP payload was observed but not preserved byte-for-byte in this report, so `PIT_NATIVE_VERIFIED=false`, `RAW_PAYLOAD_SHA=null`. UTC daily close follows the last 23:00-23:59 candle and is **not** taken from the current price ticker. Reproducible source query: `GET /api/v3/klines?symbol=BTCUSDT&interval=1h&startTime=1794182400000&endTime=<original-capture-end>&limit=168` and ETH equivalent, original [Binance documentation](https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data). Provider retrospective price availability is not evidence it was available in the ORIGINAL production source/consumer.

**Companion machine-ready diagnostic:** `W46_PREWEEK_BINANCE_SPOT_DIAGNOSTIC_20261115_v1.json`. No original forecast, risk threshold, source producer, score or official public site changed.

## 1. Critical Astra-execution truth

Owner explicitly requested immediate Astra HIGH model run with newly relevant pre-W47 content. This was technically audited. **The original V2 route cannot execute.**
- `.github/workflows/owner-bound-daily-director-manual.yml`, original `astra-realdata-task2-v2` job starts with literal `false &&`. An apparently correct owner issue_comment trigger therefore CANNOT launch it. Do not write a paid-looking trigger comment and claim success.
- Original `research/api_agent/coordination/ASTRA_TASK2_REALDATA_V2_ADMISSION_V1.json` has `authorized_paid_dispatch=false`, `source_readiness=MISSING_VERIFIED_ALPHA_V4_DECISION_FILL_EXIT_COST_RECEIPTS` and `tool_billing_status=NOT_PROVEN_BOUNDED_BY_OWNER_10USD_RESERVATION`. No source/legal/cost gate proof to reverse it.
- Original PR [#2115](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2115) is **CLOSED, UNMERGED** (verified 15 Nov). Two older Astra HIGH runs 43419077122/43436726016 already completed and are reviewed in `2026-11-14_ASTRA_HIGH_AUDITED_RESULTS_REGISTER_v1.md`; NEVER rerun their consumed IDs, nor claim this research is Astra.
- Global API $50/month owner ceiling, $4 reserve and original $40 code guard are separate. Existing canonical risk ledger still conservatively holds the two historical Astra liabilities ($3 + $10) pending independently verified per-model provider reconciliation. It is NOT a real invoice. The distinct new paid attempt has no approved budget admission or safe runnable executor. **NO MODEL POST, NO RESERVATION, NO BILLING, NO RETRY.**
- One cannot technically override an actual literal false safety block through a GitHub comment. To re-enable a new safe source-only Astra route would require its OWN reviewed exact-head HIGH_IMPACT change, enforceable provider total spend and source/custody/prerequisite checks. Do not bypass the original finance/security closure. An owner wanting Astra via a separate native model session must truly run that session; this chat cannot label itself as Astra.

**Completed THIS turn:** model-assisted research interpretation by the current assistant, current GitHub source audit and deterministic calculations on actual retrieved Binance hourly public spot records. NOT a paid `gpt-6-astra` run.

## 2. What 5 postissue complete days actually show, BTC and ETH

Original CN W46 was issued **Mon 9 Nov 10:52:34.925867 UTC**, after separate original **10:33:42 UTC 0/7** version. Compare only **Tue 10 through Sat 14 Nov, UTC daily close**, five full postissue days. Monday is omitted to avoid original issuance mixing, Sunday 15 Nov is incomplete. One week is ONE dependent week cluster, not five independent scientific replicates.

**B0 cheap constant-price comparator:** Monday Nov 9 09:00-09:59 UTC completed Binance hourly close held constant across all Tue-Sat targets. BTC `74,288.01 USDT`, ETH `2,108.92 USDT`. This specific bar completed BEFORE the 10:52 issuance, avoiding intrabar and future bar leakage. Its retrospective retrieval and actual original production availability are not proven. For equal-width close-coverage B0 bands, use each exact CN day's original `high-low` width re-centered on this fixed B0 price. This is a **developmental matched-width diagnostic**.

| Asset | CN forecast-closing MAE, Tue-Sat | Same-clock B0 MAE | CN close in original band | Equal-width B0 close in band | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| BTC | **4,145.08 USDT** | **3,940.96 USDT** | 2/5 | 2/5 | CN worse in point MAE; same close coverage |
| ETH | **146.93 USDT** | **143.24 USDT** | 0/5 | 0/5 | CN worse in point MAE; neither band adapted |

The 5-day negative result is **one W46 outcome**, not an independent proof of generic lack of forecast skill. This result remains untrusted for official scoring because source first-published, consumer first-delivered, exact original provider and full source capture are not sealed. It is nonetheless a concrete material **falsification candidate**: additional forecast sophistication did not beat this simplest preknown price on these five original closing targets.

| UTC target close | BTC actual Binance | BTC original CN | ETH actual Binance | ETH original CN |
| --- | ---: | ---: | ---: | ---: |
| 10 Nov | 73,796.06 | 74,255.12 | 2,053.21 | 2,102.85 |
| 11 Nov | 74,015.19 | 74,421.08 | 2,056.36 | 2,109.68 |
| 12 Nov | 71,460.00 | 74,207.22 | 2,019.74 | 2,100.87 |
| 13 Nov | 68,314.00 | 74,633.72 | 1,929.88 | 2,118.42 |
| 14 Nov | 64,150.00 | 74,943.51 | 1,769.20 | 2,131.20 |

This table records original *expected close* vs independent retrospective Binance completed UTC daily closes, not original official market capture. It does not combine range min/max scoring or uncalibrated evidence balance into probabilities.

**Frozen weekly lower breach timestamps (hour-level, not tick level):**
- BTC original weekly low `71,289.02`. First postissue Binance 1h bar with LOW below floor: **2026-11-12 15:00 UTC**, bar low `71,255.02`. Lowest observed since issuance through captured completed hours: `62,006.00`.
- ETH original weekly low `1,964.54`. First postissue Binance 1h bar with LOW below floor: **2026-11-13 03:00 UTC**, bar low `1,917.01`. Lowest observed through capture: `1,711.08`.
- Latest **fully completed** 1h candle in this query ended **2026-11-15 12:00:00 UTC**: BTC close `65,351.00`, ETH close `1,823.69`. These are staleable external spot observations, NOT official Kompas live now, and the 15 Nov daily/weekly closes have **NOT** matured.

**Key causal nuance:** original Kompas DID carry bearish evidence balance `Bull 3 / Bear 7`, DOWN short term and `ELEVATED` pullback risk. The scientifically relevant problem is **severity escalation and downside magnitude/path calibration**, not claiming the framework had NO warning at all. Risk `ELEVATED -> HIGH` after BTC 12 Nov weekly-floor breach is an **EX POST counterfactual for shadow testing only**, not an original risk 4/5 signal.

## 3. Why W47 demands a different research emphasis

Public external context as first observed by the researcher 15 Nov, to be source-screened before W47 original issuance, **NOT admissible retroactively for Nov 9 W46 forecast or original protected market authority**:

| New evidence | Source/publication | Interpretation to TEST, not a predetermined signal |
| --- | --- | --- |
| $1.07bn US spot BTC ETF weekly outflows, two successive >$1bn weeks; seven-day $1.91bn run | [The Block, 2026-11-14](https://www.theblock.co/news/markets/2026-11-14-bitcoin-etfs-lose-1-billion-for-the-second-week-in-a-row-as-crypto-funds-except-one-continue-bleeding-440337) | Persisting institutional spot selling can condition drawdown episodes only where original settlement/publication times are qualified |
| USDT/USDC/DAI 30d supply contraction **$11.5bn**, US ETF outflows earlier period | [Coinbase Institutional, 2026-11-13](https://www.coinbase.com/institutional/research-insights/research/weekly-market-commentary/weekly-2026-11-13) | Test absolute stablecoin supply and ETF flow persistence separate from USDT.D ratio and Bitcoin price. No dual counting same upstream data |
| US retail sales and Industrial Production Tue Nov17, FOMC minutes Wed Nov18 2pm ET = **20:00 CET** | [Federal Reserve, November 2026 calendar](https://www.federalreserve.gov/newsevents/2026-November.htm), [US Bank Nov13 week-ahead calendar](https://www.usbank.com/content/dam/usbank/en/documents/pdfs/corporate-and-commercial-banking/econ-weekly-pdf-11-13-26.pdf) | Event-time/first-publication safeguards, stress scenario and exception freshness, NOT knowledge of outcomes or an assertion that macro events will be bearish |
| Weekend volatility and BTC near $64k–$65k in dated reports | [15 Nov timestamped morning report](https://charliedesk.com/market/report/2026-11-15), checked against independent Binance 1h spot | Potential gap risk between last equities/ETF session and Monday reopening; avoid late Fri ETF data relabelled as weekend net flow |

**Important unique W47 design:** separate original W46 negative data and hindsight from W47 prospective:
- W46 remains calibration **development/failure analysis**. The Sunday official close/weekly outcome must mature only after `2026-11-16T00:00:00Z`.
- W47 first official original CN issue and Challenger A freeze are scheduled Monday Nov16, and can be genuine forward tests only when first available source timestamp, first-in-main SHA and consumer delivery are verified.
- PR #2124 Challenger A and #2130 original issuer hook were verified **MERGED**; #2129 first-original-main-score-lock was verified **OPEN** on 15 Nov. No implied LIVE W47 sample, no posthoc score. Other site exception/release PRs remain separate.
- Existing Task2 #1596 14-horizon ledger, #1553 risk, #1516 CN, #1827 source and #1157 Strategist authority remain original owners. No second forecast engine or automation.

## 4. Single strongest falsifiable next hypothesis (rather than 10 new models)

**H-W47-RISK-01, preregistration candidate only:** On original independently issued valid risk decisions, a source-safe *consecutive downside escalation* from (a) original day-range breach to (b) a verified weekly-envelope breach, plus a minimal pre-known volatility/momentum qualifier, may increase **warning severity lead time** for a later independent 72h >=5% BTC/ETH adverse episode relative to original ELEVATED and simple price/ATR baseline, **without** losing too much false-alarm/false-exit cost.

- **No fitted threshold from W46.** Existing original 31 Oct Pullback Radar SHADOW episode definition and original #1553 warnings must be reused; no new 4/5 score or reweighting.
- **Frozen target:** independently sourced first full 72h after issue for original eligible episodes, with per-hour source delay and actual delivery; missed upside, false alarms and silent/UNKNOWN hours included.
- **Simplest B0:** pre-known ATR/volatility + price drawdown with SAME eligibility and warning budget. B1: original freeze/official risk as issued. C1: single consecutive breach/acceleration challenger, original model controls otherwise unchanged.
- **Kill rule:** C1 fails to improve cost-adjusted 72h severity/lead-time jointly relative to B0/B1 on independent forward shock/quiet event groups, or source first-known is unresolved -> `REJECTED / SOURCE_BLOCKED`, no new code. No claim of confidence or 100% accuracy from one extreme week.
- **Cross-check:** historical W39–W45 equal-width negative, corrected HRE source clock (intrabar close-time and timestamp-unit negatives), Source-to-Official `protection_tracker` pass-through. Explicitly ask whether severity stalled at upstream fixed weekly risk state vs stale source versus no intraweek severity transition policy. Do not treat later external ETF evidence as early data.
- **Paper execution G3:** original Alpha v4 decision/fill/exit rows remain 0 on reviewed last source: `NO_AFTER_COST_RESULT`. Use risk-only research utilities until original complete dollar execution source exists.

## 5. Original-owner acceptance, exact work and release gate

1. **NOW FREE:** Original Task2 #1596 audits this note's five daily-close rows against independently archived hourly Binance OHLC; original #1827 tests source/clock lineage. Independently source-seal or mark `EXTERNAL_RETROSPECTIVE_ONLY`; do not overwrite original source. Original #1553 diagnoses the upstream risk state producer and tests the smallest failing negative. #1516 verifies existing daily expected-close scorer vs per-day original bands, no method version substitution.
2. **AFTER MON 16 NOV issue (no paid automatically):** check that original W47 CN and Challenger A truly issued before every outcome; no late/missing source promotion. Confirm first-main-score lock or report source-blocked. At most one existing active heavy lane.
3. **PAID ASTRA attempt remains BLOCKED:** only a newly reviewed safe source-only one-shot with actual model API access, per-work-id unique identity, enforceable total cost, original owner/CI and budget admission could begin. A fresh user mandate does not make a deliberately blocked job runnable. If available later, reuse existing 27k-char Astra Master Packet and the historical readback; do not pay again for the same W39–W45 test.
4. **Independent adjudication:** ask original Claude Bridge #173 to judge hypotheses and math **after** actual native evidence or original scientific handoff through #1596, not label this as an Astra response. Archive original #1512/#1157 dispatch at most ONE implementable delta with fully source-backed falsifier; S1 does not access Vault, change market scores or trade.

**Bottom line:** deterministic source-backed pre-W47 comparison **actually executed**. In this single exposed down week CN expected-close MAE did not beat the earliest completed-bar flat-price comparator. More importantly, the system did carry bearish risk context but the source-issued downside magnitude and severity did not adapt after repeated floor breaches. This is a concrete design/falsification finding for original Task2 #1596, **NOT** a proven general trading edge, an authentic Astra call, a source-qualified official score, or a finished W46 final forecast evaluation.
