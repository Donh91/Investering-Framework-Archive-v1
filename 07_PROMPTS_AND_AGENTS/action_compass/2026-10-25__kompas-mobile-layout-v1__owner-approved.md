# Kompas · mobile-first layout contract v1.0

Approved by owner: 2026-10-25. This document captures the preferred presentation for future Kompas readbacks and site design. Presentation-only; it does not alter official signal authority, market models, thresholds, execution permissions, or data.

## Screen order
1. **KOMPAS** title, local date and source freshness.
2. **MARKEDSSTATUS** as the largest text: official action (e.g. HOLD / AFVENT). Adjacent 1–3-day directional interpretation clearly labeled *analysis*, not official permission.
3. **Bull/Bear** two visually balanced values sourced from the official scale, clearly stating these are directional scores, **not calibrated probabilities**. If the analyst or shadow view differs, disclose separately with confidence.
4. Compact BTC, ETH, BTC dominance quote strip, including observation time, source and whether snapshot or live.
5. **01 Taktisk overblik**: columns horizon / expected direction / permitted action. Horizons 24h, 1–3d, 5–7d, 2–3w, 4–8w. Missing forecasts stay unavailable.
6. **02 Handlingskompas**: columns asset class / status / action. BTC, ETH, large, mid, small, micro, memes. Keep microcaps HARD WAIT and missing meme authority unavailable as appropriate.
7. **03 Market signals**: pullback/retest, distribution/exit, re-entry, altseason, each with evidence-grounded state.
8. **04 What changes the view?** concise bull confirmation, bear confirmation, next decision window. Never invent precise ETA or price ranges.
9. **YOUR ACTION NOW**: one short concrete decision line, explicitly distinguish hold/wait from sell authority.

## Style
- Danish, premium, minimalist, mobile-first, high contrast, generous whitespace; restrained red/green for genuine risk/status only.
- Clear hierarchy, concise labels, short readable tables. No embedded external market widgets in chat.
- No invented certainty, no fabricated fresh prices, no invented live connections.
- Official GitHub Compass is binding for action. Native readback, CN, Master Monday and Shadow v2 can inform context but Shadow is advisory only; no automatic promotion to BUY/SELL.
- Display independent evidence and limitations; separate observation, forecast, confidence, and permission.

## Implementation boundary
This is a **design specification and preference**, not a site release. Site integration should reuse existing Kompas and Cycle Navigator owners, official data contracts, PR review and existing governance. Do not introduce a competing owner, workflow, automation or decision engine. No main branch modification without governed merge.

## Owner-approved Kompas PRO consolidation · v1.1 · 2026-10-25

The owner explicitly approved merging the best of KOMPAS PRO into this existing mobile-first layout for both chat and the current Cycle Navigator site. This supersedes **presentation priority only**, not a canonical signal owner, forecast model, risk classifier, thresholds, source routing or GitHub release policy.

**Core product promise:** Compass is an investment DECISION SUPPORT surface, not an ambiguous market report. Always show a clear **separate assistant judgement** alongside the exact official state, with its evidence, validity horizon, severity, uncertainty and conditions under which the judgement should change. Human user alone makes portfolio trade decisions. A deterministic website must label a pre-authored risk-preparation guide as `planning guidance / not a new live AI recommendation`, never impersonate a fresh AI forecast.

Priority stack (mobile):
1. **OFFICIAL NOW / WHAT I RECOMMEND**: Show source-verified canonical action, then a separate clearly labeled assistant assessment or static planning checklist. Translate `HOLD_WAIT` to specific practical exposure guidance where evidence supports it, but NEVER convert this to a machine `REDUCER`, `EXIT` or `BUY` permission.
2. **BULL / BEAR**: Original official categorical 0–10 evidence balance, NOT probabilities, plus independently labeled Shadow/analyst challenge with qualitative confidence. Do not synthesize an uncalibrated bearish number.
3. **PULLBACK INTELLIGENCE**: Source-owned NORMAL / BUILDING / ELEVATED / HIGH / CONFIRMED five-level ordinal rail; clearly label `3/5` as ordinal placement only. Display **evidence quality** LOW/MEDIUM/HIGH, **event occurrence confidence/probability** only if separately prospectively calibrated (otherwise NOT CALIBRATED), **onset ETA** only from bound governed typed prospective onset window (otherwise UNKNOWN), **expected percentage depth and drawdown band** only if separately frozen source exists (otherwise NOT ISSUED), **next review/decision window** explicitly distinct from event ETA, and **invalidation / next escalation evidence**. An ELEVATED source state with LOW confidence does not imply that a major decline is expected.
4. **PROTECTION & SELL NAVIGATOR**: Four explicit rows: (a) official current action; (b) `PREPARE PROTECTION PLAN` as a nonbinding human checklist when warranted; (c) actual `SELL / TRIM` availability from separately governed decision owner; (d) re-entry eligibility + verified trigger/window if any. Display `SELL UNAVAILABLE (NO GOVERNED OWNER)` rather than silently hiding the capability. The planning checklist is NEVER execution authority. Offer conditions for reducing speculative beta, keeping core, and reviewing buyback only as transparent human guidance, not hidden automatic trading rules.
5. **FORWARD PRICE INTELLIGENCE**: BTC/ETH USD ranges by independent forecast horizon (1–3d, 5–7d, 2–3w, 21–30d, 4–8w), with issuance/source/week, confidence/coverage, base/bull/bear (only if real issued scenarios), projected drawdown severity (only with calibrated measured reference), backtest coverage and original frozen receipt when available. A frozen whole-week W43 range must NOT become a 1–3d prediction, a coming-W44 band or a 4–8w estimate. NEVER invent, interpolate, extrapolate or fill empty cells from live spot price, historical candles or qualitative analysis.
6. **TACTICAL + ASSET TABLES**: Preserve the mandatory two narrow three-column tables; action and interpretation are separate; no implied meme permission.
7. **YOUR ACTION NOW + CHANGES IF**: One decisive plain-language assistant recommendation with qualification and at least one bull/bear confirmation and a next review window. On site, this is a static, transparent status interpretation, not a claimed live AI inference.

Already-existing owners to extend, NOT replace:
- Market authority: `04_MARKET_LEARNING/handlekompas/official/LATEST_COMPASS.json`, Native, Shadow v2 and strategic/CN prospective anchors.
- Protection/SELL: `COMPASS_PROTECTION_TRACKER_v1` and `COMPASS_SELL_ASSESSMENT_v1`; no active SELL authority is bound in the checked 2026-10-25 packet.
- Forecast/science: existing issue #1516 Forward Path Engine and existing W42+ CN Price Range owner; no parallel forecast engine, scheduler or backfill-as-prospective.
- SITE: existing #1578, its `05_CYCLE_NAVIGATOR/site/vnext-live/` premium interface and source-verified public readbacks, keeping DA/EN, the existing styling and mobile ergonomics.

**Non-negotiable negative tests:** stale source, conflicting week/source ID, withheld SELL, risk HIGH with no SELL, low-quality evidence, unissued ETA/depth, 7d weekly range misrepresented as 1–3d or future week, no official action via Shadow, missing meme owner, public/private data separation.

**Status:** Product/design approval by user; any runtime code remains governed by exact-head PR review, testing, merge and a live post-merge readback. A merged spec does not prove a live feature. 
