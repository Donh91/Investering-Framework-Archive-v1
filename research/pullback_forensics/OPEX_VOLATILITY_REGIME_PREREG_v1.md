# OPEX_VOLATILITY_REGIME_v1 | Source-first research preregistration and handoff

- **Created:** 2026-11-21 Europe/Copenhagen
- **Status:** RESEARCH_CANDIDATE / PR_REVIEW_PENDING / NO_EMPIRICAL_RESULT
- **Claim level:** HYPOTHESIS, not an edge, strategy, indicator, trading rule or forward forecast
- **Authority:** RESEARCH_ONLY; no source contract, current producer, model weights, official Compass, CN, S1, Alpha Lab, portfolio or execution changes
- **Current source baseline:** Archive main `37f67d7171725499ef0a5bcc174531b2b93fcc64` (21 November 2026, 19:48:41 UTC), read-only inspection; this baseline is a snapshot, not a moving authority
- **Primary owners:** #387 (derivatives evidence gap/capture), #1596 (PIT/scientific comparator), #1553 (pullback warning), #1516 (forward path, only after separate promotion), #1156 (existing S1 routing)
- **Scope and priority:** Low-cost research context under current owners, subordinate to P0 Compass/CN data integrity and S1 closures. No new queue, scheduler, API spend, realtime alert, market engine or workflow.

## 1. Origin, facts and falsifiable question

The owner supplied a screenshot of X posts by IncomeSharks and a response by TOGI describing (a) Wednesday 'theta traps' after two volatile days and (b) monthly Friday US options expiration as potentially producing fakeouts, a bottom or a substantial breakdown. The screenshot has relative timestamps only, not a verified original post publication timestamp or an immutable upstream source. **Original-source timing is UNKNOWN, and the screenshot is idea provenance only; it is not quantitative evidence.** A third-Friday equity-options calendar event is NOT the same as the last-Friday Deribit crypto monthly option expiry. Do not attribute November 20, 2026 US equity losses or BTC moves to OPEX without testing confounders.

The central question is whether knowledge available **before** a particular BTC/ETH option expiry, especially exact expiry clock and legitimate option-positioning evidence, adds out-of-sample information about intraday reversal, downside-event warning, or near-term realized volatility **beyond** existing clock-matched price/volatility/macro/derivatives baselines. First test information edge. Any action edge requires separate legally authorized and cost-aware research after prospective admission. Do not say that expiry causes a crash, fixes price at 'max pain', or reveals signed dealer gamma.

## 2. Independent external evidence reviewed on 2026-11-21

### Strongest supportive work, but outcome definitions differ

1. **Weiss, Gaudiosi, Zhou & Webb, 'Bitcoin option expiration, gamma exposure, and intraday price reversals', Finance Research Letters 107 (2026), 110340.** The publisher abstract reports intraday BTC spot return reversals around Deribit expiry, concentrated in high at-the-money open interest and strongest with negative *estimated* cumulative gamma exposure, alongside spot/perpetual trading increases. Mechanism is *consistent with* dealer hedging, not proven from public OI alone. https://www.sciencedirect.com/science/article/pii/S1544612326008688
2. **'Time-of-day effects in the Bitcoin options market', Finance Research Letters 101 (2026), 110008.** Deribit option trading concentrates around 08:00-09:00 UTC (expiry/settlement) and 14:00-15:00 UTC (US equities); expiry intensity and short tenor matter. This is a warning against naive intraday comparisons. https://www.sciencedirect.com/science/article/pii/S1544612326005374
3. **'Is there an expiration effect in the bitcoin market?', International Review of Economics & Finance 85 (2023), 647-663.** Reports intraday volume, volatility and return differences around certain futures maturities; not proof of exploitable trading PnL or of the Deribit options mechanism. https://www.sciencedirect.com/science/article/pii/S1059056023000515
4. **'Aggregate illiquidity and crypto option returns', Finance Research Letters (2025).** Studies Deribit option-market-maker aggregate gamma inventory and illiquidity; requires rich trade/quote data, not merely raw OI. https://www.sciencedirect.com/science/article/pii/S1544612325012619

### Counterevidence, competing explanations and healthy skepticism

5. **Cayø Largo, 'Does Volatility Rise After a Deribit Options Expiry?' (2026 field note).** Uses 1,224 expiries across six coins in March-September 2026; does not find a robust general post-expiry volatility surge after clock/day adjustment. Non-peer-reviewed, observational and not identical to reversal outcomes. https://cayolargo.fi/research/does-volatility-rise-after-deribit-expiry
6. **'Do hourly Bitcoin options forecast risk beyond a HAR benchmark?', Finance Research Letters (2026).** Tests 56,168 hourly option-chain snapshots, 2020-June 2026, against volatility-persistence benchmarks. Its abstract reports varying incremental usefulness of option-surface dimensions across time. We have NOT independently replicated its evaluation or obtained the underlying data. https://www.sciencedirect.com/science/article/pii/S1544612326013814
7. **Cboe 0DTE market analysis.** Gross option turnover/OI is not net dealer inventory. Balanced customer flows can offset; signed dealer gamma requires additional evidence or explicit uncertainty. SPX conclusions cannot be transferred to BTC by assumption. https://www.cboe.com/insights/posts/volatility-insights-evaluating-the-market-impact-of-spx-0-dte-options/
8. **Deribit settlement, official mechanics.** Standard expiry/settlement at 08:00 UTC. The final delivery price uses a 07:30-08:00 UTC 30-minute index TWAP; Deribit describes special decay of its option/future delta metrics during this window. These are important microstructure and measurement discontinuities. https://support.deribit.com/hc/en-us/articles/29734325712413-Settlement
9. **2026 structural change:** From April 2026 for linear options and August 2026 for inverse options, Deribit uses a two-stage option-to-future-to-cash expiry process. Distinguish contract kinds, fee/accounting mechanics and structural break in provider outputs; do not infer cash settlement PnL changed. https://support.deribit.com/hc/en-us/articles/31424939096093-Inverse-Options and https://support.deribit.com/hc/en-us/articles/31424932728093-Linear-USDC-Options
10. **Official US calendar:** 2026 US standard monthly expiration on **2026-11-20**, versus Deribit monthly option expiry on **2026-11-27 at 08:00 UTC**. Separate event labels and timestamps. https://www.optionseducation.org/referencelibrary/expiration-calendar and https://support.deribit.com/hc/en-us/articles/25944688876957-Contract-Introduction-Policy

### Evidence interpretation

- Supported: expiry and hedging are plausible market microstructure features, with at least some empirically reported intraday effects.
- Not established: a general guaranteed direction, 'almost always Wednesday theta traps', universal post-expiry spike, signed dealer inventory inferred from public OI, BTC-to-microcap transmission, or proven incremental Compass skill.
- Apparent study disagreement is **partly differing estimands** (return reversal vs post-expiry realized volatility); do not select a winner from abstracts.
- Public case analysis for 2026-11-20 is retrospective illustration only. Avoid labeling that day's stock/crypto moves OPEX-caused or a pre-issued Framework warning.

## 3. Existing code and exact boundaries

- `research/pullback_forensics/PULLBACK_FORENSICS_PASSIVE_PILOT_v1.md`: L2b current Deribit **moneyness** skew, explicitly NOT true 25-delta skew; passive shadow, no market authority.
- `scripts/daily_capture/pullback_forensics_collector.py` at blob `0ba74a9e59f4c3b3d5c62db0030f28688190231d`: `build_moneyness_skew` uses `if dte < 1 or dte > 60: continue`, so its **derived L2b skew view excludes 0DTE**. It fetches `public/get_book_summary_by_currency` and `public/get_instruments`. This is a scope mismatch for the new question, not automatically a bug and not proof that complete raw chains were retained.
- `scripts/daily_capture/pullback_forensics_collector_v1_1.py`, `.github/workflows/daily-raw-owner-capture.yml`: collector invoked in an existing scheduled every-four-hours workflow (six cron slots). This is insufficient to resolve minute-scale pre/post-expiry windows. No extra cron is authorized by this packet.
- `06_RESEARCH_LAB/round3_new_information_v1/SOURCE_CONTRACT_REGISTRY_v1.json` includes Deribit true 25-delta skew contract SC14. Its required Greeks and private capture are **not** the same as the L2b moneyness view.
- `AGENTS.md`, `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md`: Round 3 is `PROSPECTIVE_COLLECTION_ONLY`, hypothesis testing and outcome scoring OFF. No Round 3 raw provider values, aggregates, private records or pseudo-backtests in this research, including no exploratory peek. Public source receipts are not model admission or scientific results.
- Existing #387 already owns derivative evidence gaps and history; #1596 owns PIT and scientific controls. This document neither claims live source availability nor edits either owner.

## 4. Data acquisition feasibility, FREE-FIRST (no provider acquisition authorized)

| Candidate | What it may support | Observed/claimed availability | Decision |
| --- | --- | --- | --- |
| Existing 4h Pullback Forensics L2b | DTE 1-60d and moneyness-skew context | Existing implemented public code, actual historical completeness and eligible private/raw access unverified | AUDIT metadata first; do not turn it into 0DTE |
| Deribit current public REST | Current listed contracts, expiry clocks, marks, OI / selected Greeks via exact endpoints | Real-time snapshots; historical PIT chain cannot be reconstructed from a present-day response | SOURCE CAPABILITY ONLY, no new job yet |
| Deribit SC14 restricted Round 3 | True 25-delta skew prospective snapshots | Registration and historic activation reported; latest private health **not read** | FIREWALL CLOSED for analysis |
| Tardis.dev options_chain | Historical Deribit tick/snapshot options-chain data and local receipt timestamps | Vendor documents coverage since 2019, **not verified entitlement/cost/license for project** | DUE DILIGENCE ONLY, no purchase |
| Amberdata Deribit options | Historical OI/quotes/trades | Product documentation only; entitlement/terms/cost unchecked | DUE DILIGENCE ONLY |
| Existing allowed BTC/ETH hourly candles | Price-only counterfactuals and matched controls | Subject to exact original archive clocks, gaps and current owner admissibility | REUSE when permitted |
| US monthly OPEX calendar | Pre-known fixed event dates | Official options industry calendar | DESCRIPTIVE EVENT METADATA ONLY |

Data contract to request before coding: `source_contract_id, instrument, venue, contract_kind, expiry_utc, observation_utc, provider_event_utc, first_available_utc, retrieval_end_utc, received_utc, raw_hash, provider_clock_health, active_contracts, expiration_status, selected 0DTE chain completeness, units, schema/mapping versions, source-retrieval license, source_tier`. Public control plane may contain only allowed value-free metadata; sensitive provider values stay in authorized restricted storage. Unknown timestamps or units -> `UNKNOWN`, not zero/fill.

For historical comparisons the *actual snapshot captured before the modeled prediction time* is mandatory. Later historical download may be a legitimate historical source only if its original per-row event time, availability semantics, completeness, licensing and no future feature leakage are established. Current API re-query is never a past snapshot.

## 5. Preregistered experiments, NO RUN OR OUTCOME NOW

All hypotheses use independently eligible, pre-specified cohorts, family grouping for overlapping events, walk-forward train/test splitting with event embargo, no post-hoc threshold tuning, uncertainty and missing-data disclosure. Zero results until original owner authorizes a legal dataset and stage.

**H0: Clock-only/calendar null.** At 08:00 UTC, after matching weekday, hour, baseline volatility, trend, asset, era, US-session overlap and major scheduled catalysts, expiry dates offer no incremental BTC/ETH direction, reversal or realized-volatility information. Simple placebo: 08:00 UTC on non-expiry days and equivalent Fridays. Do not mix US Friday expiration with Deribit 08:00 UTC.

**H1: Expiry intraday reversal.** On legally observed Deribit BTC/ETH expiry events with pre-event feature freeze, compare signs of pre-window [-120,-35] min and post [+5,+65] min log returns, with supporting windows 15/30/120 min and alternative nonoverlapping definitions predeclared. A reversal is opposing *nonzero* signs; exclude zero/flat, censored or unavailable separately. Control for diurnal patterns and prior trend. Event microstructure window [-30,0] min is separately described, not leaked as a predictive feature before its freeze.

**H2: Conditional ATM concentration and gamma proxy.** Test whether pre-registered ATM OI concentration / strike distribution adds lift conditional on liquidity, realized volatility, skew and momentum. Report gamma sign as `UNKNOWN` without actual signed dealer-position data; unsigned GEX proxy is allowed only in a distinctly named non-causal exploratory sensitivity, never called net dealer gamma. Cboe-like dealer feedback is a hypothesis, not a demonstrated identification.

**H3: Post-expiry volatility.** Compare 0-1h, 1-6h and 6-12h realized variance with identical UTC/hour matched non-expiry controls; report signed price outcomes separately from absolute returns, to avoid falsely converting 'reversal' into 'more volatility'. Use realized volatility benchmarks, including HAR/lagged RV and time-of-day seasonal baseline, not a naive zero predictor.

**H4: US equity OPEX-to-crypto transmission.** Distinct US OPEX dates, index expiry types (AM vs PM where documented), VIX/SPX/Nasdaq risk-off, earnings/macro catalysts, equity-market hours and BTC spot/perp outcomes. Must show incremental signal beyond equity drawdown, VIX, ETF flows and plain BTC momentum; one November 20, 2026 case is not a cohort.

**H5: Wednesday theta-trap claim.** Define two *prior* volatile sessions using only finished contemporaneous realized-volatility observations and a frozen training quantile; compare Wednesday vs Tuesday/Thursday (and matched event weekdays) for subsequent realized-vs-implied movement. Avoid calling stock or crypto spot sideways a theta-loss proof. An options-buyer PnL claim requires the *actual entry premium, expiry, instrument, executable quotes, spread and transaction-cost convention* at the pre-event decision time. With only spot candles, theta-trap option PnL is `NOT_TESTABLE`.

**H6: Consumer usefulness conditional on H1-H5.** Compare baseline Compass/Pullback warnings against baseline plus expiry context on *the same exact issued clocks and coverage* only after source-admission; evaluate missed warnings, lead time, false warnings, abstentions, coverage, max adverse excursion, false exits and retained upside. No composite 'accuracy' banner without underlying numerator/denominator and no automatic output to Kompas, CN or Alpha Lab.

## 6. Pre-specified baselines, exclusions, and kill gates

- Baselines: (B0) simple clock-matched no-information; (B1) price momentum/persistence, (B2) past realized-volatility/HAR and clock seasonality; (B3) existing source-eligible Compass/Pullback as actually frozen; (B4) each plus *admitted* pre-event option features. Same sample, same timestamps, same abstention denominator and same cost assumptions.
- Leakage negatives: shuffled event labels, future-shifted OI, post-expiry Greek reuse, altered provider availability time, historical 'today' chain substituted as prior chain, signed gamma inferred from OI, mislabelled 25-delta from moneyness, missing zero-filled, US/Deribit conflation. Each must fail admissibility or lose the effect.
- Measurement negatives: Deribit 07:30-08:00 TWAP/Greeks decay, special API pause around 08:00, option-to-future settlement transition (April/August 2026), instrument-unit changes, daylight savings on US clocks, calendar holiday shifts, incomplete/delisted expiry membership, stale/overlapping chain snapshots.
- Uncertainty: event family N, independent weekly/monthly/quarterly cohorts, multiple testing, block-bootstrap by event/date when appropriate, explicit source attrition; do not count BTC and ETH in the same systemic episode as independent market events.
- **KILL** if source admissibility fails; all apparent signal disappears against matched strong baselines; multiple-testing/era fragility dominates; provider cost/privacy/operational complexity outweighs prospective benefit; significant false-exit opportunity cost; or a required test would cross Round 3/firewall/authority rules.
- **RETAIN_SHADOW** only for reproducible, prospectively testable incremental information with insufficient event-family power.
- **PROMOTION ELIGIBILITY ONLY** after an original-owner PIT audit, protected out-of-sample proof, independent reviewer, documented economic utility and a separately ratified governance/release path. Information edge != action edge.

## 7. Precise execution order and delivery receipt

1. **Existing owner #387 / LOW research:** metadata-only census of already retained Deribit option-chain evidence: capture windows, DTE coverage and 0DTE gap, source timestamps, schema/units, complete vs partial, license and source first-known clock. No private raw values, no Round 3 analysis. Compare the old 4h collector to the new hypothesis; preserve original L2b behavior.
2. **#1596 scientific gate:** establish whether a legally admissible non-Round-3 historical dataset exists. If not: `BLOCKED_SOURCE_HISTORY` plus exact prospective collection proposal to existing authorized owner, with budget estimate, not a data purchase or new API mission.
3. **Only after step 2:** produce immutable preregistered experiment config, synthetic first-known/unit/clock negative tests and source admission receipt, reuse existing research execution machinery. No duplicate issue/queue, no automated live change.
4. **Only after eligible history/new matured prospective cohorts:** run B0-B4 without reading sealed Round 3; publish all denominators, missingness, negative results and event-level controls in permitted location.
5. **#1553 and #1516 after independent scientific review:** decide `REJECT`, `RETAIN_SHADOW` or `PROPOSE_SEPARATE_PROMOTION_REVIEW`. If eventual UI work, descriptive calendar and status only; `gamma_sign=UNKNOWN`, `signal=UNVALIDATED`, no official forecast/BUY/SELL authority by default.
6. **S1 #1156:** observe original research owner's dispositions through existing cadence, deduplicate against work-in-flight; no additional S1 task, paid mission, auto-merge, or hidden delegation from this packet.

**Acceptance of this PR is only acceptance of a source-backed, falsifiable research brief.** PR merge must not be described as hypothesis tested, source acquired, a working 0DTE indicator, a delivered risk alert, scientific proof or trading readiness.

## 8. Explicit current execution receipt (as of authoring)

- `external_literature_review=COMPLETE_AT_ABSTRACT_AND_OFFICIAL_DOC_LEVEL`
- `current_archive_source_and_dedup=READ_ONLY_CHECKED_AT_PINNED_SHA`
- `non_Round3_options_data_verified_for_test=NO`
- `Round3_raw_data_read=NO`
- `backtest_or_study_effect_estimate_run=NO`
- `code_changed=NO`
- `paid_API_or_vendor_data_used=NO`
- `live_Compass_CN_Alpha_portfolio_changed=NO`
- `independent_review=REQUIRED_BEFORE_MERGE`

Owner-present research authorization in the conversation permitted preparing this PR; it did NOT override the above separate data, science, governance and release gates.
