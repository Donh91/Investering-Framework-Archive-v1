# Independent self-audit — SITE truth-first personal dashboard (2026-10-19)
Status: DESIGN AUDIT / REVIEW ONLY. No production code changed. PR #1683 companion.

## Verdict
Architecture direction is correct but implementation mission was NOT sufficient to guarantee an honest daily personal dashboard. The user primarily uses SITE daily on iPhone, and may share it with friends. The design must optimize truthful decision utility, attractive visualization, provenance and legibility, not public-marketing simplification. No change to existing canonical decision owners.

## Verified current-code observations
- Global Action Compass §3.1 already requires full cross-read for chat and site; duplicate engine is prohibited.
- Site contract has strong typed ownership, public issue identity, Compass weekly alignment and no invented countdown.
- CORRECTED AFTER MAIN CODE REVIEW: `compass-product-v5.js` has a legacy `friendlyAction` mapping `DE_RISK|PROTECT|EXIT|SELL` to `HOLD`, but it does **not** own the active NOW view while `CN_PREMIUM_COMPASS_OWNER` is true. The active `market-compass-premium.js` maps `DE_RISK|PROTECT|EXIT` to `PROTECT CAPITAL`. Official `action_now` is separate from the typed SELL assessment. This is a regression-test target, **not a proven active P0 production mislabel**. Do not rewrite the working renderer speculatively.
- `market-compass-premium.js` uses `publicCompassText` and hardcoded regex replacements for explanatory copy. Verify these cannot alter essential risk, thresholds, dates, units, source attribution or decision meaning. Formatting must not become a second semantic decision engine.
- Full-stack readback `COMPLETE` vs `PARTIAL_OR_DEGRADED` exists; prove completeness against the full mandatory source inventory, not just successfully loaded subset.
- The previous Sol mission did not explicitly specify a dedicated visual truthfulness acceptance matrix, per-chart observational completeness, personal-vs-share privacy model, or cross-client normalized decision parity with timed source snapshots.

## Severity-ordered remediation design

### P0: semantic fidelity / protective risk
1. Build exact official action vocabulary mapping table (machine state → safe, plain Danish/English site label → risk badge → required explanation). Test every known enum. `DE_RISK` and `SELL` must never silently become reassuring `HOLD`; preserve whether official action is a *market-risk posture* vs an individual portfolio execution instruction. Unknown enum fails closed.
2. Render separately: verified official action, independent nonbinding AI interpretation, weekly frozen CN, source quality, and portfolio-specific action (only if legitimately supported). No color or icon can contradict a warning.
3. Require freshness + source ID + horizon on every action card and every visual that could prompt a trade. Clearly mark stale, partial, unavailable, delayed, and frozen.
4. Never suppress risk merely because the dashboard is publicly shareable. Protect private values at projection boundary, not by rewriting verified public market risk.

### P0: same full Compass in chat and SITE
1. Define normalized, deterministic decision readback schema for all 7 asset rungs and 6 time horizons, including official status, conditional path, source IDs, invalidation, pullback/distribution/SELL/swing/re-entry and missingness.
2. Compare chat and SITE using identical immutable fixtures and evaluation timestamps. Compare semantic decision fields, not narrative phrasing or UI formatting. Mark analysis-only additions clearly; do not require byte-identical freeform interpretation.
3. The chat may run a fresh eligible source cross-read; a static SITE snapshot may lag until existing publishing cadence. Therefore parity is **conditional on same exact source set and as-of time**. If site lags, show the lag, do not claim live parity.
4. Master Monday is weekly frozen input; Official Compass is current action owner; CN frozen weekly and 4–8w owners remain distinct. No synthetic phase or ETA.

### P0: chart and visual scientific honesty
For EACH chart, record: source contract, metric and units, time basis/time zone, sampling and missingness, frozen vs observed distinction, actual observation cutoff, allowed transforms, stale SLA and fallback.
- Forecast range band != forecast line. Never interpolate midpoint into predicted price.
- Observed low/high envelope != intraday price path. Do not draw continuous actual curve unless observed time series exists.
- No invented forward bars, phase percentage, confidence %, ETA, or green/red risk status.
- Precision percentages need exact denominator, scoring version and eligible outcomes; internal structural score != price precision != confirmatory forecast skill.
- Distinguish weekly frozen expectation from hourly current Compass and delayed macro/ETF data; do not combine timestamps in a single unlabeled LIVE badge.
- Charts must visibly display empty/missing observations rather than quietly filling with zero, previous close or smooth interpolation.
- Verify 390px iPhone layouts, DA/EN translations, readable tooltip/axis/legend, accessible contrast and no chart clipping. Visual appeal is a presentation requirement, not evidence.

### P1: daily dashboard information architecture
Top view should answer in <= one screen: CURRENT OFFICIAL ACTION, what changed since prior valid issue, key reason(s), risk, age, and NEXT REASSESSMENT (not phase ETA).
Below: asset ladder BTC→ETH→large→mid→small→micro→memes; time horizons; cycle timeline and confirmed/missing gates; forecast-vs-realized chart; pullback/distribution/protection; evidence health and sources; weekly Master Monday recap; optional independent AI perspective clearly nonbinding.
Do not repeat full ladders or show irrelevant technical internal remediation on public site. The user can share the same page with friends; keep explanations readable and complete without revealing private portfolio/wallet information.

### P1: personal-use vs shareable public boundary
Site may be public, but its owner-centric usefulness must not be reduced. Keep all non-sensitive **market** warnings and uncertainty. Private position sizes, portfolio holdings, wallet IDs, nonpublic API usage/receipts, raw private provider payloads and private strategy secrets must never ship to Pages. If future personal-only information is desired, require a separately approved authenticated privacy architecture, NOT localStorage-as-security or hidden HTML. No new access architecture is authorized here.

### P1: completeness and observability
The dashboard must expose separate labels:
- DATA HEALTH (fresh, stale, missing, conflict)
- ANALYSIS COVERAGE (full, partial, unavailable)
- DECISION AUTHORITY (official vs nonbinding research)
- FORECAST VALIDITY (frozen/eligible vs unscored)
- SITE DELIVERY (latest deployed snapshot vs upstream latest verified)
Do not turn consumer PASS into a claim that every analytical field is complete.
Weekly machine-only audit must include per-chart provenance and any chat/site semantic mismatches and false-freshness incidents, without creating a new source of truth or publicizing private internals.

## Adversarial acceptance tests (must fail before targeted fix, pass after)
A. `DE_RISK` or `SELL` source maps to visually reassuring HOLD -> FAIL.
B. Frozen weekly WAIT + current official PREPARE -> UI must distinguish both; no contradiction masked.
C. Same immutable snapshot in chat/SITE -> identical normalized official decision; site older -> visible age and no fake LIVE.
D. Current partial full-stack with missing required source -> not COMPLETE.
E. Range band-only forecast rendered as invented daily predicted curve -> FAIL.
F. Missing observation interpolated as actual; stale ETF/macro labeled LIVE -> FAIL.
G. Unscored matured outcome displayed as validated predictive accuracy -> FAIL.
H. Private holding, wallet or restricted API receipt included in public snapshot -> FAIL.
I. 390px mobile graph axis clipping or critical warning hidden behind decoration -> FAIL.
J. Change in UI copy turns official negative gate into affirmative action -> FAIL.
K. Official distribution warning vs shadow bullish view -> verified risk remains dominant, shadow explicitly NON-BINDING.
L. DA/EN switch changes enum interpretation -> FAIL.
M. SITE static screenshot shared externally contains no secret or misleading freshness indicator.

## Execution guardrails
- Read fresh main and current open PR overlap before touching code.
- Extend **existing** source projection/validator/tests; do not replace working site or create duplicate Compass.
- Prioritize P0 safety mappings and exact semantic parity; then visual truthfulness; then weekly machine audit and aesthetics.
- Small scoped PRs with actual CI and mutation-sensitive regression tests. Existing required independent reviews/branch protection remain. No autonomous portfolio trade, new model router/scheduler, API budget increase, shadow promotion, or historical rewrite.
- Owner-approved API research can propose fixes, but only authorized existing executor writes/merges. This file does not launch Sol 6.1.

## Final acceptance
The user can open SITE daily and receive a beautiful but evidence-faithful complete Compass summary; same-source chat output agrees on official decisions; weekly forecast stays frozen; visual gaps are honestly shown; risks are never softened; friends can read the public market analysis without receiving the owner's private information. Report verified tests and first natural production readback before claiming DONE.


## Owner correction — 2026-10-19
The owner declined the newly proposed “Frozen weekly forecast vs actual market” illustrative chart. **Do not implement that proposed chart or use it as an acceptance criterion.** Do not delete or alter any pre-existing, source-verified charts or the independently owned PR #1680 visual work without a separate explicit change request. Prioritize data-integrity fixes, regression tests and the existing site information architecture.
