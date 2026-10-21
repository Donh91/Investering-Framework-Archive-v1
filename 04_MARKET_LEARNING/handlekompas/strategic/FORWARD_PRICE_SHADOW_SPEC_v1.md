# Forward Price Intelligence · shadow-first research v1.0

**Owner request:** 2026-10-21 · **Authority:** RESEARCH_ONLY / SHADOW_NOT_ISSUED / NOT_CALIBRATED. This is a bounded extension of existing Forward Path #1516, Master Monday #1593, Official/Strategic Compass, and existing Task2 #1596, not a parallel market forecaster, new task, cron, model router, or portfolio decision source. Existing #1157 owns adaptive learning, #1156 supervision, #1578 public SITE, #1133 private portfolio scenarios.

## Key decision: direction != price

Official Compass identifies market direction, capital-tier permissions, confidence quality, pullback/distribution risk and invalidation. **None of these implies a numerical price return.** Turning BULLISH into an arbitrary +20% price target would add precision without evidence. Build and score independent priced baselines first. Only later, when same-clock prospective experiments prove net interval/decision lift, allow a preregistered conditioned directional modifier.

Price tasks are separate:
- Terminal close: eventual spot close over a defined horizon. This is NOT min or max during that period.
- Intraperiod envelope: lower and upper bounds on future *path extrema* in a dated UTC interval. For price-range accountability, score realized minimum and realized maximum as a pair; infinitely wide bands are not successes.
- Dated path: only actual originally issued day/hour expected-close checkpoints, with exact timestamp, if such points are independently produced. Never join range midpoints into a blue zigzag.
- Conditional scenarios: e.g., 1–3m/3–6m/6–9m/9–12m macro/breadth/rotation alternatives with dated confirmation/invalidation. Until independently matured, odds UNKNOWN, not fake 80%/90% confidence.

## What actually exists, verified on main

- Original Official Compass owns 12h/72h/168h and execution layer. Do not replace it.
- Original weekly CN has D1–2, D3–4, D5–7 source ranges, a frozen weekly range/score, and an optional daily-price path that legitimately remains UNAVAILABLE when it was not issued.
- Strategic Compass has a 21–30D directional/textual owner and 4–8W CN SHADOW context, but does not issue independently proven numeric 14/21D or 2027 target curves.
- Existing CN Deep Navy chart 7/14/21 viewport (#1730) and source-bound Forward Outlook (#1729) are presentation, not proof of issued numeric dates.
- Existing offline source preflight #1731 rejects future-time and invalid D8–14 / D15–21 range candidates. It does not generate them.
- Reuse baseline B1: scripts/cycle_navigator/deterministic_range_baseline.py (prior four complete 168h weeks, asymmetrical median excursion); reuse prefreeze daily spot source-owner scripts/learning/forecast_b1_source_owner.py, with strict currency/source parity. Source-dependent private data remains in Donh91/secrets, not public GitHub.
- Existing CoinGecko Top100 7d,30d,200d optional fields are backward-looking source context (capture-only, not outcome-admitted) and cannot reconstruct missing historical intraday minima or initial provider publication.
- Prior retrospective range research reported little incremental benefit from simple direction tilts and volatility-width tweaks; do not assume a complex model will outperform cheap baselines.
- Task2 R0/R1 original provider first-known, first published and eligible cohorts remain necessary for historic skill claims. Round3 remains PROSPECTIVE_COLLECTION_ONLY with testing/scoring OFF.

## New offline baseline (scope of this PR only)

scripts/learning/forward_price_shadow.py supplies pure deterministic build_shadow(input) with no network, file writes, cron, release side effects or automatic reweighting. Strict input: BTC/ETH, actual USD source/venue, 252–366 contiguous complete daily OHLC records, original per-bar first-known claim, source-manifest digest and a canonical-row digest checked against exact input bytes, and issued/cutoff age <=48h. Enforce each daily bar closes BEFORE its first-known timestamp; no future candle or gap. Reject invalid OHLC and malformed price values, missing evidence and USDT units masquerading as USD.

At issue, anchor to last fully settled daily close. For h = 1,7,14,21 calendar days, enumerate historical h-day blocks that already ended at/before the source cutoff. For each, calculate its MIN-low and MAX-high relative to its preceding day's close, as log excursion. Take fixed exploratory q10 lower and q90 upper and rebase to the last settled close. These are **hypothetical baseline endpoints**, not calibrated 80% coverage nor a sourced provider forecast. Record raw overlapping-window count; fewer than 12 nonoverlap block opportunities => ABSTAIN that horizon. Overlapping windows inflate nominal sample size; even 12 nonoverlap blocks may be low power. Both assets run independently; no ETH/BTC conditioning yet. Hash the candidate. Do not output to public Compass, current frozen ledger, X or SITE.

Source manifest hash/canonical bar digest prove input consistency but **do not prove original provider first-known/published clocks**; input flag is an assertion, and output makes this limitation explicit. No real bar data is distributed with PR. All tests use synthetic bars.

## Full owner-preserving integration design (NOT implemented by this PR)

**Stage A: Source custody & natural issuance.** Use existing #1516 and #1593 producers only, with no new schedule. Acquire authentically settled USD price bars and first-known source receipts via existing data plane and source owner, fail CLOSED if unavailable. Freeze each prospective shadow run BEFORE target opens: forecast_id, asset, quote, venue, source-owner, issue week and public issue, issued_at_utc, source first-known/cutoff, original raw/normalized hashes, code/parameters, original target UTC start/end, horizon, lower/upper values or UNAVAILABLE/ABSTAIN. Keep failed/no-issue attempts in denominator. The existing append-only forecast ledger owns storage, not a new system. Git commit timestamps alone do not prove true earlier provider availability; source and first delivery separately verified.

**Stage B: Forecast quality.** Compete on SAME original issue/asset/window against:
B0 flat price/no-change or fixed historical envelope;
B1 existing 4W median weekly excursion baseline;
B2 this 252–366d empirical excursion candidate;
B3 predeclared volatility-only scale, with fair same-clock training and never auto-picked on the test cohort;
S1 conditional direction/regime/rotation challenger **only if** a future R2 outcome-admitted prospective study warrants it. Initial directional coefficient is ZERO, because a bullish statement alone has no numeric drift calibration. Optional monthly scenario tracks use existing macro/Copper-Gold owner as slow context, not a cycle-top probability or forced price target.

**Stage C: Long-horizon semantics.** Short intraday 1h/4h/12h belongs with the separate hourly Official/Shadow owner and genuine hourly source candles, not a naive daily->hourly interpolation. 24h, 3d, 7d, D8–14, D15–21 get horizon-specific original envelopes with exact UTC clock. 21–30d and 4–8w stay source-owned, shadow until properly issued. 1–3m/3–6m/6–9m/9–12m use conditional broad waypoints with evidence and falsifiers, NOT numeric bands until enough as-of data and independent future outcomes support them. Never recreate subscriber roadmap target prices.

**Stage D: Score after maturation.** Keep issued forecast bytes unchanged, append matured outcome ONLY later. For any exact UTC horizon compute actual hourly/daily high+low with complete source coverage; separately terminal close if forecast exists. Metrics: two-sided **joint excursion coverage**, lower/upper misses, interval width relative to anchor, width + tail-breach interval penalty (predeclared), regret from false narrow/wide calls, and missingness/ABSTAIN rates. Direction score separate from price range; conditional probability/Brier/CRPS only when legitimate frozen probabilistic forecasts exist. Calculate matched paired difference vs B0/B1/B3. Cluster overlapping daily issue windows and both assets in shared regimes; no sample-size inflation from overlapping 21d dates, duplicates, forecast revision or multiple variants. Carry negative and null results. First delivered/actionable times + costs only for separate R3 investor value, never conflate information with portfolio profitability.

**Stage E: Adaptive evolution, without rewriting history.** Frozen challenger method+sha+issue and all failed/missing sources in existing #1157. Future algorithm version v2 only through preregistered challenger after first-known PIT and held-out tests; preserve all historical issued v1. If coverage, width, lead time or investor usefulness do not beat cheap matched controls, RETAIN_SHADOW or KILL—not promote by growing complexity.

### Realistic timeline
**Weeks 1–4** after legitimate future source-bound shadow issuance: check 100% original freeze/custody and no-lookahead, missingness, real natural issuer delivery, first short 1d/7d matured outcomes, negative tests, and observed adverse gaps. 21d produces very few *independent* matured forecast origins in this period; do not call this calibrated. Prototype supports no auto-model updates.
**After >=12 genuinely independent matured episodes per asset/horizon**: exploratory low-power comparisons, still no official weights/price-source promotion. **Before meaningful incremental skill claim** seek >=30 independent preregistered episodes across >=2 regimes, independent source clocks, frozen matched baseline, sensible multiplicity correction and exposure to adverse events; thresholds are proposed REVIEW gates, not binding scientific authority. 14/21d often requires many months; 3–12m needs actual months/years for many maturing original issues. A daily run is not an independent 21d experiment.

### Release topology
Phase 1 = THIS PR: shadow priced baseline, synthetic tests, document, existing Official Compass CI test import. Safe to merge as **research-only** only if exact HEAD 7/7+ as applicable, negative tests and reviewer/security/governance pass. No active market output.
Phase 2 = existing #1516/#1593 source/prospective shadow ledger integration + natural first-issued and first-matured readback. Separate owner-authorized implementation PR ONLY once data-source custody/readback is real; not automatically from Phase 1 merge.
Phase 3 = existing SITE #1578 consumes only signed/sanitized public issuer projection. Keep existing original weekly blue-dashed forecast vs green actual graph intact; 14/21d absent means labelled NO PRICE FORECAST, never synthetic blue line. Draw sparse dated interval bars, not an interpolated future price curve. Private #1133 may compute deterministic scenario sensitivity to holdings, no private position leak or action. No new chart dependency.
Phase 4 = existing Task2 #1596 and Adaptive Evolution #1157 adjudicate R0/R1 -> outcome-blind prereg -> fair R2 price-edge -> R3 executable-value -> heldout/forward maturation -> owner-approved bounded promotion or KILL.

## Mandatory adversarial SOL 6.1 API review

Use existing Framework Learning Supervisor temporary exact-HEAD review, bounded API budget. The Sol result is ADVISORY, not a formal GitHub APPROVED. Identify concrete P0/P1 defects: off-by-one window indexing; overlaps/effective sample claims; legal source time; hash-to-bytes binding vs real first-known; USD vs USDT/venues; unfinished daily bars; 10/90 excursion range semantics and uncalibrated joint coverage; mutation/retrofit hazard; inappropriate adaptation after 3–4w; fair model tournament; exclusion/censorship; public/private data boundary; duplication with existing #1516/#1593/Task2; impact on existing Compass signals and graphs. State anything not tested. If code or science is unsafe, request correction and keep draft; never ask Sol to authorize a merge or autopublish.

Public site/X never reference the external paid analyst, their original estimates, images, or subscriber-only source content; a future sources/methodology page needs separately authenticated owner approval.
