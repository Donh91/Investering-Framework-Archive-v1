# R4P — Pullback Investor Decision Edge: Extreme Risk, ETA, Regime, Portfolio and Re-entry Audit

**Mission:** `COMPASS-HORIZON-EDGE-20261011` | **Requested 2026-10-12**  
**Status:** ADDITIVE AUDIT / EXECUTION PACKET ONLY — no source model, live prediction, retrospective credit or API execution claimed.  
**Existing parent:** Research PR #1573 (R0–R7), Risk-to-Action #1553, Forward Path #1516, EDGE governor #1530, CN vNext #1578 / Draft site PR #1576.  
**Mandate:** Extend R4 (warnings-to-action economics), R3 (14/21D directional path), R5 (adversarial falsification) and UX0/site detail handover **without changing the existing Compass decision authority**.

## 0. Investor questions the audit MUST answer — or visibly mark unknown

The word `HIGH` is not an economic decision. A holder with volatile small/microcaps must distinguish these seven questions:

1. **PROXIMITY:** Is an observable event expected in `0–6h / 6–24h / 1–3d / 4–7d / 8–21d / >21d`, or `UNKNOWN`? Are those pre-registered owner-issued clock windows, or just *risk review* horizons? A user who expects to convert to stablecoins needs an actionable lead time, not an undated badge.
2. **LIKELIHOOD / confidence:** What *precisely defined* event is being predicted by the stated horizon? Is there a validated 1–10 confidence calibration **for that event, within that horizon**, with actual numerator/denominator and reliability, or only qualitative LOW/MEDIUM/HIGH **evidence quality**? `HIGH` risk class is NOT a high numeric probability.
3. **MAGNITUDE:** Is this a routine intraday BTC/ETH retracement, a material broad crypto drawdown, a high-beta altcoin shock, or a severe market break? Source-defined BTC draft SMALL 3–5%, MATERIAL 5–10%, MAJOR >=10% from CN v2 are **research onset labels** only, not current authoritative thresholds or portfolio forecast. Do not misclassify 2% BTC with -30% microcaps as trivial market risk.
4. **ASSET/TIER EXPOSURE:** BTC, ETH, large/mid/small/micro and memes require separate source-aligned stress/relative-performance projections, including source availability, liquidity, timestamp and cap-beta estimates. No BTC-only percentage silently reused as an altcoin loss forecast.
5. **DURATION AND REGIME:** Will it be a quick liquidity flush/retest followed by reclaim, a choppy 3–7d corrective phase, or an independently evidenced 2–3+ week downtrend / bear transition? `MIXED` 2–3w must not be misrepresented as "no downside", and `HOLD_WAIT` must not be portrayed as verified safe to hold positions.
6. **PROTECTION / SELL / STABLECOIN UTILITY:** Under *separately governed* risk and action owners, which choices can be **reviewed** (continue holding, stop new buys, trim review, exit review, hold stables, staged re-entry), and when would they be economically better after spread/slippage/fees/missed upside/market rebounds/asset-specific liquidity/tax complications? No signal may directly authorize a trade or force liquidation.
7. **RECOVERY / RE-ENTRY:** Is there evidence for an isolated short dip with genuine reclaim and liquid re-entry, a partial bounce inside a bearish trend, or a distribution trap? What conditions **must be falsified** before claiming recovery/re-entry? The existing `WAIT_FOR_FLUSH → WAIT_FOR_RECLAIM → REVIEW` progression is not automatic BUY permission.

A site is investor-useful only if these questions are separated into **state / window / size / breadth / duration / longer-term scenario / official action / evidence age / what changes next**. Unsupported answers are `UNASSESSED` or `UNKNOWN`, not marketing labels.

## 1. Verified existing source authority (read fresh at actual execution)

- `scripts/data_ping/native_handlekompas.py::protection_tracker` translates the existing structured frozen/weekly CN projection to `NORMAL/BUILDING/ELEVATED/HIGH/CONFIRMED/UNAVAILABLE`, plus `eta_window`, `confidence_quality` qualitative, `last_material_change_at`, `reentry_state`, public drivers and invalidation. It **does not independently generate rapid hourly risk escalation**.
- `scripts/data_ping/compass_event_refresh.py` can request event-driven refresh but is not a new stage, magnitude, or forecast-authority engine. Pre-existing 08:17 / 20:17 plus qualified event refresh cadence must be preserved.
- `sell_assessment()` currently returns `UNAVAILABLE` and explicitly does not promote a warning to SELL. Thus current `HOLD_WAIT` is a current navigation/admission state, **not** validated incumbent-position capital safety or a guaranteed "do not sell" conclusion.
- Latest publicly inspected 2026-10-12 owner snapshot `CMP-20261012-3f1e99c2868e`: `pullback_risk_state=ELEVATED`, qualitative evidence quality `LOW`, public onset start/end `null`, `sell_assessment.state=UNAVAILABLE`, `distribution_risk=UNKNOWN`, current action `HOLD_WAIT`. **No qualified 5-hour vs 3-day ETA and no defensible 1–10 confidence yet.**
- Draft CN public vNext site PR #1576 already has stage/ETA read-only presentation and a two-disclosure investor UI. It remains pinned to historic CN28/W41 seed in deployed preview; future *live* connection is NOT completed.

These are **source observations**, not the proposed research model's verified performance.

## 2. Falsification-oriented scenario matrix

All rows are **scenarios to test, not current market predictions**. The audit must ask "what would happen to the investor if the warning was right, wrong, too early, too late, or directionally right but portfolio-wrong?"

| Scenario | Risk if conflated | What the audit must distinguish | Benchmark / negative control |
|---|---|---|---|
| A. 1–6h harmless BTC dip and altcoins unchanged | Excessive stablecoin switch, fees/tax, missed upside | Intraday normal volatility vs independently eligible material event | Always HOLD / flat naive volatility |
| B. Flash flush, rapid 2–12h reclaim | Warning arrives after trough, sell at bottom; re-entry too late | Warning first-valid-time vs onset/peak/trough/50% recovery, executable venue spreads | No-warning; perfect but infeasible clairvoyance explicitly disallowed |
| C. BTC -3% but high-beta small/micro -20% | BTC-size label understates portfolio tail | Tier-basket drawdown and liquidity, realized adverse path, source confidence | BTC-only risk proxy, explicit tier missingness |
| D. BTC -8%, ETH underperforms, alt liquidity disappears | Cannot execute recommended stablecoin conversion | Source family independence and depth/slippage, market beta | Spot/HOLD with realistic friction |
| E. False alarm 72h before resumed parabolic uptrend | High `HIGH` read looks impressive but destroys upside | Reliability by 0–6/6–24/24–72h, false alarms, early-warning cost | Frozen always-warning and no-warning |
| F. Sideways/retest lasts 5–10d then reclaim | Event scored as crash or "bear" incorrectly | Volatility shock vs duration, sustained trend/reclaim conditions | Equal-horizon persistence |
| G. 2–3w structural bearish rotation / distribution | A quick `HOLD_WAIT` read is mistaken for safe incumbent HOLD | Separate 12h tactical direction vs 14/21d ordered path and structural invalidation | 7d-only and 21d-only matched-clock models |
| H. Trend-down then dead-cat bounce | Re-entry watch mistaken for buy permission | Recovery vs short-cover bounce and volume/breadth/ETHBTC confirmation | Immediate rebound-buy control |
| I. Long bear/cycle cooldown (8w+) | Weekly pullback ETA hides lasting regime change | Structural CN cycle owner, 21–30d vs 14–21d and 4–8w distinct clocks | Naive regime persistence |
| J. Bull market volatility with positive alt rotation | Warning suppresses best risk-on phase | Multi-family supporting and contrary signals, false stress from one proxy | Rotation-positive controls |
| K. Stale/missing ETF/breadth/derivative data | A fake "confidence 9/10" based on partial inputs | DATA_HEALTH, missing family count, observed vs ingested vs published clock | Healthy-only universe, source-outage negative control |
| L. One shock across BTC/ETH + 20 correlated alts | Naively scores 22 independent "correct warnings" | M6/T2 independent family grouping, duplicate event joins | Episode-level N, not asset x interval N |
| M. Several alerts within same ongoing fall | Inflated hit-rate, alert fatigue and late repeated warnings | First qualified freeze per family, dedup, material transition and reset logic | Single-episode vs repeated alerts |
| N. Anticipated -10% BTC but realized -4%, yet -35% illiquid micro | "Wrong" price threshold but relevant portfolio protection, or vice versa | Grade BTC size and individual tier-tail utility **separately** | Asset/tier-specific and portfolio-layer controls |
| O. Accurate fall forecast but no authorized SELL | Marketing says "would have saved 50%" | Information success vs DELIVERED review and actually executable after-cost benefit | No-action baseline; delay and deliverability |
| P. Underlying market already crashed when alert published | Hindsight success, no useful reaction time | First-knowledge vs issue vs delivery vs earliest feasible fill | Lead time <=0 counted late, not predictive win |
| Q. Genuine crash without any warning | Model hides missed events by only scoring issued alerts | Prespecified universe of all eligible episodes including NO_WARNING | Always-NORMAL baseline |
| R. HIGH followed by less risk/normal without event | Escalator suggests inevitability | Stage can RECede, become invalid, or expire; no categorical "high = 24h" | False alarms, decay test |
| S. Bearish 14/21d with bullish next 12h relief rally | Mixed-horizon call misread as contradiction, or sell too early | Role-labeled near-term vs medium structural calls, separate action authority | Horizon-matched controls |
| T. Portfolio concentrated in illiquid memes | Public site provides dangerously false position-specific stablecoin recommendation | Private eligibility/slippage/taxes/position limits; public site general only | Private Portfolio Compass separate; no wallet data on public site |

### User-impact grading

- **Early warning usefulness**: legal as-of freeze and alert deliverability *before* first material event, direction and lead-time coverage, conditional precision/recall, alarm frequency and false alarms.
- **Economic usefulness**: matched initial capital, identical cutoff, available trade costs, two populations (existing holder vs fresh cash), downside protected, missed upside, re-entry regret, realization and position liquidity. Report gross price edge separately from *after-cost realizable* utility. For publicly inaccessible wallets and order books: `NOT_MEASURABLE`.
- **Regime correctness**: independently label `SHORT_DIP`, `MATERIAL_CORRECTION`, `PROLONGED_DOWNTREND`, `STRUCTURAL_BEAR`, `INDETERMINATE` from preregistered metrics and prospective source clocks; not from plain-English postmortem or BTC return alone.
- **Re-entry**: realized trough, reclaim and 50% recovery are outcomes; proposed `reentry_review` only from separately governed current evidence, with double-dip/low-liquidity controls.

## 3. Crucial independent multi-axis contract

The auditor must treat **four different quantities** as distinct, without guessing numeric conversions:

### A. Risk state (qualitative, currently source-owned)
`NORMAL / BUILDING / ELEVATED / HIGH / CONFIRMED / UNAVAILABLE`. This is a **current classified risk context**; higher class does not imply a sooner drop. `CONFIRMED` can mean established canonical *risk conditions*, not an observed event threshold or an unambiguously bearish 2–3w regime.

### B. Onset clock and event distribution (not currently modeled)
Future typed candidate:
`target_event_definition`, `asof_utc`, `valid_from_utc`, `horizon`, `forecast_start/end_utc: nullable`, `clock_status: NOT_PREDICTED / WEEK_ONLY / WINDOW_0_6H / WINDOW_6_24H / WINDOW_1_3D / WINDOW_4_7D / LONGER / UNASSESSED`, `event_size_target`, `source_sha256`, `valid_through`, `invalidation`.
**Do not label an imminent window from a HIGH stage alone.** The clock horizon is a research candidate until independently admitted.

### C. Likelihood 1–10 (proposed research, NOT current live)
An investor's "7/10" must mean a **calibrated risk estimate for a precise event, asset/universe, horizon and minimum loss**, e.g. "material BTC 5%+ in next 72h" with independent validated source, denominators and Brier/log-loss/reliability assessment. It must not mean the seventh of ten UI ladder steps, nor copy `confidence_quality=HIGH`.

Prospective research specification:
- Predefine binary or survival-analysis events by *size, horizon, asset basket, anchored baseline and censoring* before any outcomes. Event probability must state **conditional on as-of information**.
- Fit/challenge strictly on older PIT-eligible windows; honest chronological walk-forward/OOS evaluation; cluster overlapping warnings and families; baseline comparison versus simple volatility/event base rates; calibration curves by grouped probability bins, Brier, log-loss, ECE and confidence intervals; cross-regime stability and drift.
- Any 1–10 presentation is an **explicitly calibrated display bin**, with published bin-to-conditional-event-rate policy, `effective_family_n`, bounds and lower/upper intervals. Sparse bins, correlated episodes, or weak calibration => `NOT CALIBRATED` rather than an invented number.
- Do not conflate predicted incidence with `LOW/MEDIUM/HIGH` *input evidence quality*. Valid endpoints may remain `ABSTAIN` indefinitely.

### D. Magnitude, alt beta and regime continuation (candidate, separate validation)
Define source-specific forecast or scenario *ranges* for BTC/ETH/tier basket realized adverse excursion; no mechanically multiplying BTC decline by a guessed alt beta. Separate size from **duration** (trough horizon, time-to-reclaim, 14/21d continuation odds) and from **directional market regime** (normal dip / correction / distribution / bearish trend).

Outputs are *scenario envelopes* or `UNKNOWN` until registered, not "forecast loss -25%" created from the present risk badge.

## 4. Private portfolio and stablecoin decision economics

One market indicator CANNOT safely tell a user to convert an entire existing high-beta portfolio to stables. The economic audit should compare **two entirely separate decision populations** with identical risk-free/stablecoin denomination assumptions:

- **Incumbent holder:** continue HOLD, REVIEW_SMALL_TRIM, REVIEW_LARGE_TRIM, REVIEW_FULL_EXIT, and liquidity-protected WAIT. These are **research counterfactuals**, not live trading recommendations. Gate every actionable arm by an independently authorized SELL review owner (#1071/#1133).
- **Fresh cash:** WAIT / PREPARE / STAGGERED_BUY / NO_EDGE, as a different question. `HARD_WAIT` for fresh memecoin buys cannot imply SELL of old tokens.
- **Re-entry:** genuine tradable dips after actual costs, spread and slippage, 24/7 timing, liquidity availability, recovery-into-downtrend / second-leg outcomes, exit tax/realization costs where law applies (requires private personal context).
- **Tail of alts:** concentration, venue, chain, pool depth, availability, partial fill, beta variability. Keep wallets, holdings, transaction data, tax jurisdiction and personally identifiable context OFF the public archive/site. If current permissions don't allow private Portfolio Compass data, return an UNKNOWN economic receipt, not simulated wallet P&L.

No automatic trade execution, no site-generated SELL, and no claim that a correct down-move call was practically profitable.

## 5. Temporal regime bridge: when does "pullback" become "bear"?

Test three **separate source-owned clock horizons**:
- `NOW/12–72H`: detection and available current conditions. A bullish 12h bounce may coexist with a bearish 2–3w structure.
- `5–7D`: price zone, tactical path and possible retest; frozen CN price intervals do **not** give event ordering or a promised onset.
- `14/21D/2–3W`: separately frozen conditional path, confirmed vs falsified turning points, relief rallies inside downtrends; source #1516 (do not relabel existing 21–30D as 14/21D).
- `21–30D and 4–8W`: longer strategic and cycle context, unchanged authority; bearish cycle overlay not derived from Pullback state.

A true regime switch requires a **versioned, independently reviewed regime classifier** or approved structured CN projection with explicit persistence, breadth/ETHBTC/flows/capital transmission, drawdown and invalidation; none currently produces a verified live "bear transition at X" from the Pullback tracker.

If sources conflict, present honest:
`TACTICAL_RISK_ELEVATED · STRUCTURAL_2_3W_UNASSESSED · SELL_UNAVAILABLE`. Never silently turn HOLD_WAIT into "hold because bearish will recover", nor into SELL.

## 6. The smallest coherent site presentation (existing PR #1576; no redesign)

**Above the fold**, keep existing Overblik and Kompas layout unchanged except one compact risk "escalator":
- 5 **discrete categorical** segments, not a continuously filling percentage bar: `NORMAL | BUILDING | ELEVATED | HIGH | CONFIRMED`, highlight the exact official source class, no animation implying inevitable onset. On a valid downgrade, highlight moves backwards. Stale/missing => no highlighted segment, label `KILDE MANGLER`.
- Immediately adjacent small text: `Risk state · source-issued time`, `Possible ETA or UNKNOWN`. `Evidenskvalitet LOW/MEDIUM/HIGH` optional small inline.
- Risk class segment is NOT `1/10...10/10 likelihood`, and `HIGH` alone is NOT imminent. No synthetic alt %-fall, regime classification or BUY/SELL.

**Existing** native Pullback disclosure under Kompas tables, extended with only truthful typed fields:
`Onset ETA / expected trough/recovery (if typed)`, `size-class BTC/ETH`, `alt impact by cap-tier`, `duration scenario`, `12–72H vs 5–7D vs 2–3W and 4–8W context`, `quality, contrary evidence/invalidation`, `source time and freshness`, `separate SELL/TRIM state`, `re-entry state`, `how the signal will be scored`. Unavailable entries show `IKKE MODELLERET/INGEN VALIDERET ETA`. Most are initially unavailable: honesty improves the product.

No new site data-collection/API spend, scheduler, LLM classification, decorative graph, sound or chart is required. The existing canonical public feed adapter is the future integration point. Site cannot create missing research conclusions.

## 7. Pre-registration and no-hindsight scoring design

Use existing EDGE-001/M6/T2 event-family research and CN v2 Pullback Edge scorebook; DO NOT overwrite Score Era or Price Range Precision. Freeze event-specific binary targets and lead-window hypotheses *before event start*. Include explicit `NO_WARNING` time states, alerts invalidated by positive alt rotation, and no-data/noneligible.

Per verified episode/family, independently score:
- **warning quality** (did an eligible alert precede the right declared event/size/window?),
- **lead-time** (hours before first threshold crossing; late alert cannot become ex-ante hit),
- **clock calibration** (where supportably forecast vs actual onset/trough/recovery),
- **severity and tier prediction** (size bands conditional on source-eligible basket),
- **regime transition** (14/21D true downtrend versus temporary dip),
- **re-entry call quality** and realized executable opportunity,
- **economic utility** with opportunity cost and friction (only if data admitted),
- **survival/probability calibration** (only after independent sample sufficiency).

Publish separated families, effective N, coverage, abstentions, raw misses, false alarms and delayed source deliveries. A flashy generic "Pullback score 92%" across 8 partly overlapping cases is unacceptable.

### Adversarial acceptance and kill criteria

- Negative replay of Oct 7/8 **does not** receive forecast credit from postmortem. Sept 19 repeated warning events are a single correlated family. One valid family is not N=12.
- A saved `HIGH` alone must never cause `IMMINENT`, 7/10, 10% BTC loss, a SELL instruction, "bear confirmed", or forecast dates in any public consumer.
- Scope of scored universe must include eligible NON-events to estimate false alarm and base rates, not just down weeks.
- Counterfactual HOLDER/SELL and CASH/BUY must be separately time-executable; missing quote/liquidity makes economic claim `NOT_MEASURABLE`, even if price later fell.
- Shadow alert vs official action source precedence: never masquerade as canonical; source mismatch or stale clock fail closed.
- Unknown future risk stages or numeric 1–10 outputs without schema version => `UNSUPPORTED/UNAVAILABLE`, never inferred.

## 8. Exact mission insertion, owner-bound stages and next run

**R0 + R1:** append this addendum's `SCENARIO_MATRIX` and `SOURCE_FIRST_CLOCK` to the existing audited cohort registry; dedup overlap with #1553 and #1530. Owner/prerequisite receipt, no additional API request just because user asked for research.

**R3-P (Forward Path, #1516):** prospectively classify `SHORT_DIP / CORRECTION / TREND_DOWN / INDETERMINATE` against 14/21d and 21–30d separate timebases, with scenario falsifiers. **No retroactive 21d extrapolation** from 7d outcomes.

**R4-P (Risk-to-Action, #1553):** reproduce HOLDER vs CASH and alt-tier impact/no-warning false-alarm economy; design conditionally valid clock + size + confidence research. Any missing SELL rule remains `UNAVAILABLE`, and value-of-information cannot be a made-up P&L.

**R5-P (independent adversarial):** run table scenarios A–T (source gaps, correlated events, timing, market turns, illiquid alts, bear vs relief rally, portfolio tail). Require explicit `NEGATIVE_EVIDENCE` and kill criteria.

**R6-P:** prospective freeze / maturation under existing EDGE/CN ledgers (no new workflow). Bring matured, independently admitted findings to existing Master Monday/governed official projection; never auto-promote.

**UX0-SITE (#1578):** add minimal categorical-stage escalator and existing dropdown fields on Draft site PR #1576, preserve DA/EN and source integrity. Site release blocked on native 390/430 iPhone QA, official feed parity, fallbacks, source age and independent release gate. No production change by the research addendum alone.

Each run must use the **same mission ID**, existing research artifacts and receipt format; `EXECUTED` only upon an actual source/PIT run with exact results, not this staged plan. R4-P value may be `ECONOMIC_EDGE_NOT_MEASURABLE` and numeric confidence `NOT_CALIBRATED`; that is a valid finding.

**Routing note:** The user referred to an API Edge audit "already running". This document is queued via the existing PR/issue source of truth. An API executor that is ALREADY active must fresh-read this addendum and explicitly acknowledge it in its next stage receipt; **creating this file/comment alone does not inject instructions into a currently-running external model session**. Do not claim API run started or modified without a concrete run receipt.

## 9. Newly verified first-party Pullback Learning eligibility blocker (2026-10-12)

Direct fresh-main readback (not a subjective estimate):

- `04_MARKET_LEARNING/pullback_learning/ELIGIBILITY_STATUS_v1.json` git blob `84053fac2da1800d01d5a13b24e0371152c43339`: `SUSPENDED_NO_ELIGIBILITY_CONTRACT`. `observation_collection=true` and `adaptive_descriptive_statistics=true` are permitted; **mechanical_research_classification=false, new_episode_creation=false, existing_episode_maturation=false, canonical_market_state=false, portfolio_execution=false, rebuy_permission=false**. Must be independently governed for future eligibility.
- `04_MARKET_LEARNING/pullback_learning/LATEST.json` git blob `9d28a17a9256be1c7d31d8d3354156b9b9ba7a87`, generated 2026-10-12T16:11:36Z: `sample=181` accumulated descriptive readings (adaptive observation_count 180), but `REGIME_NOT_ACTIVE`, `ELIGIBILITY_CONTRACT_UNAVAILABLE`. This is **NOT 181 independent timed predictions**.
- `04_MARKET_LEARNING/pullback_learning/PERFORMANCE_SUMMARY.json` git blob `5007dc1ff593d585df210ac3f3f524856967b9b5`: **closed_episode_count=0**, `INSUFFICIENT_SAMPLE`, hypothetical 10% trim/reload uplift and hit-rate are **NULL**. The mentioned 10/30 episode descriptive floors are not prospective out-of-sample evidence, and do not lift suspension.

**R4P gating:** Current Pullback Learning itself cannot supply calibrated 1–10 odds, active intraday event classification, portfolio trim/re-entry economics or a convincing bear-regime transition. Do not bypass its eligibility suspension using an EDGE/M6 shadow score or retired breadth proxies. Existing M6/EDGE-001 may continue bounded research **independently** under #1530/#1553; canonical risk escalation requires separate promotion acceptance. All present investor dropdown outputs must fail closed on unsupported likelihood/magnitude/duration/alt-tier data.

**Source-vintage:** These exact blobs are a 12 Oct 2026 audit snapshot; each executing API stage must fresh-read latest main and report when the source has changed.
