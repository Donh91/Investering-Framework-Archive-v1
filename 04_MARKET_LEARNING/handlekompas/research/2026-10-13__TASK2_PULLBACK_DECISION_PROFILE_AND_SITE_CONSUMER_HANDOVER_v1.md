# TASK 2 · Pullback Decision Profile and Governed Site Consumer Handover (PDP v1)

**Date:** 2026-10-13 Europe/Copenhagen
**Status:** RESEARCH DESIGN + IMPLEMENTATION-READY HANDOVER / NOT LIVE / NO NEW SIGNAL
**Parent mission:** `COMPASS-HORIZON-EDGE-20261011` / Archive research PR #1573 (including its previously staged R4P 20-scenario audit).
**Owner route:** #1530 EDGE-001/M6 experimental warnings and outcomes → #1553 Official Compass protection / delivery and separate economic decision authority → #1516 Forward Path 14/21D scenarios (not an invented current 21D predictor) → Official Compass immutable versioned forecast/public projection → existing CN/site delivery and Draft #1576 with site owner #1578.
**Research source read-first:** `2026-10-12__R4P_PULLBACK_INVESTOR_DECISION_EDGE_DEEP_AUDIT_v1.md`, `2026-10-12__TASK2_R0_R1_EVIDENCE_AND_FALSIFICATION_PREREG_v1.md`, Task1 PR #1592, current main `AGENTS.md`, `04_MARKET_LEARNING/pullback_learning/ELIGIBILITY_STATUS_v1.json`, `04_MARKET_LEARNING/handlekompas/PROTECTION_TRACKER_CONTRACT_v1.md`, EDGE-001 `CHARTER_v1.md`, site PR #1576 `PULLBACK_PROGRESSION_INTERNAL_HANDOVER_2026-10-12.md` and `official-pullback-investor-view.mjs`.

## Decision

**ADMIT this as an explicit, owner-bound Task 2 SIDE-LANE (PDP), not a duplicate research mission or production engine.** The user wants more useful Pullback statuses and levels in the current Compass, shared with the site, but with genuinely measurable distinction between a minor dip, major/high-beta alt decline, prolonged downtrend, false alarm and recoverable re-entry. This is an *economic decision-quality* experiment, not a display of increasing severity alone.

Reuse **all 20 original investor adversarial scenarios A–T** from the R4P audit. Do not copy, rename or retune them in a way that changes preregistration. Supplement them only with explicit site-consumer authority/expiry fixtures below.

### Mandatory five independent decision axes

1. **OFFICIAL RISK STATE (categorical level):** `NORMAL / BUILDING / ELEVATED / HIGH / CONFIRMED / UNAVAILABLE`. Owned by existing `COMPASS_PROTECTION_TRACKER_v1`. This is the five-step risk-level display, *not a 1–5 probability* and not a countdown. `CONFIRMED` is confirmed risk condition only, not necessarily a realized decline or bear regime; may recede.
2. **EVENT AND PROXIMITY:** Exactly *which* event, over which source-valid window, has a prospectively issued ETA? `0–6h, 6–24h, 1–3d, 4–7d, 8–21d, >21d` are RESEARCH TEST WINDOW CANDIDATES, **NOT present live forecast output**. A currently absent qualified `onset_start/end` is `UNKNOWN`. **HIGH does not mean imminent**.
3. **SIZE / DISTRIBUTION BY ASSET:** BTC/ETH material drawdown, large/mid/small/micro/memes separately; only predeclared as-of eligible tier baskets, data sources and liquidity-adjusted adverse excursion. The proposed labels `ORDINARY_DIP / MATERIAL_CORRECTION / ALT_TAIL_SHOCK / STRUCTURAL_BREAK / INDETERMINATE` are **candidate retrospective/forward-study outcome classes**; no official current label from qualitative prose; no BTC loss multiplied by guessed alt beta. A `BTC -2% / micro -20%` scenario must not look harmless.
4. **DURATION AND REGIME:** distinguish `FAST_DIP_AND_RECLAIM / MULTIDAY_CORRECTION / PROLONGED_DOWNTREND / STRUCTURAL_BEAR / UNKNOWN` as *research outcome taxonomy until source/owner ratifies it*. 12–72H tactical can disagree with prospective 7D / 14D / 21D / 21–30D and 4–8W, keep them distinct. An `MIXED` 2–3W market structure is not bullish reassurance; `ELEVATED` is not bear confirmation.
5. **ACTION / POSITION STATE / RE-ENTRY:** display **three independent** official lanes: (a) market/portfolio protection state, (b) existing `action.NOW` for new-cash decision, (c) governed SELL/TRIM decision for incumbent holders, which may remain `UNAVAILABLE`, plus re-entry `INACTIVE/WAIT_FOR_FLUSH/WAIT_FOR_RECLAIM/REVIEW/UNAVAILABLE`. `HOLD_WAIT` is NOT proof that maintaining full high-beta exposure is prudent; `HARD_WAIT` is NOT incumbent-SELL permission; `REVIEW` is not BUY.

Sixth separate attribute: **evidence quality and source clock**. `LOW / MEDIUM / HIGH` is source/evidence quality, NOT numeric confidence that an event occurs. A 1–10 probability index is `NOT_CALIBRATED` until a registered event/horizon, representative PIT, independent episode base rates, probability calibration versus simple comparator, uncertainty, prospective OOS and separate ratification genuinely PASS.

## Baseline source observation: not a prediction

As audited in 2026-10-12 R4P and Task 2 receipts: Pullback Learning was `SUSPENDED_NO_ELIGIBILITY_CONTRACT`, descriptively collected 181 observations but with 0 closed eligible episodes. That is not 181 forecast wins or an actionable research classification. Site vNext Draft PR #1576 had a *read-only* five-stage display and investor dropdown, not a live new risk classifier. The cited 2026-10-12 Official Compass snapshot reported `ELEVATED / LOW evidence quality`, no supported onset end/time, `HOLD_WAIT`, `SELL UNAVAILABLE`. These are dated source facts, not this document's live 13 Oct market assessment. Task 2 must re-read current main and show a source-vintage diff in each future run.

## Task 2 work packages, after existing R0/R1 checkpoint

### PDP-0. Reconcile owners, ownership and implementation preflight

- Pin exact main SHA and current PR #1573/#1576 and current #1592/Task 2 research receipt; read source-first governance and permitted evidence health only. Do not replay privately restricted data to public research.
- Map Official protection tracker, native `protection_tracker`, current CN `decision_projection.protection`, event refresh, M6 warnings, EDGE governor, Pullback Learning suspension, Strategic Compass, DEL/action portfolio, `site/build-public.mjs`, site `official-feed-parity.mjs` / `official-pullback-investor-view.mjs`.
- Identify *real information cadence gap*: hourly native data can deteriorate while an official risk class derived from weekly CN remains unchanged; **observe and quantify**, do not solve by illegally auto-escalating from raw hourly indicators.
- Deduplicate from R4P and 20-scenario matrix. One writer per owner. No new cron or standalone risk engine.

### PDP-1. Prospective severity / event type / time-window experiment (research-only)

- Freeze a candidate event target as `asset_or_tier, source_universe, metric_definition, loss_threshold, onset_anchor, horizon_start/end, censor/blackout_rule`; event target and conditional outcome *before* future data, using existing EDGE/M6/T2 family registry and its corrected independent-family methodology. Missing source/original first-known => `PIT_BLOCKED`.
- Use independent candidate evidence families (price-only controls vs ETH/BTC persistence, genuinely verified breadth by tier, derivatives, flow and liquidity). Recycled/correlated signals do NOT multiply confirming family count.
- For each eligible source state issue a frozen research row with `candidate_severity_state` separate from official state, `candidate_onset_window` nullable, `candidate_event_size` nullable, `candidate_duration` nullable, `candidate_recovery` nullable; `WARN / NO_WARNING / ABSTAIN / UNKNOWN` with full denominator and effective family ID. **No live-risk authority**.
- Compare separate event types and 0–6h/6–24h/1–3d/4–7d/8–21d candidate test horizons to same-clock volatility, persistence, price-only and always-HOLD/NO_WARNING controls; this is NOT permission to call a live event imminent. No retrofit of R4P labels.
- Track evidence age, freeze time, first-known, delivery/executable time, event onset, trough, recovery, directional disagreement, warning first trigger, retraction/decay, failed source. Include false warnings, missed shocks and rebound controls.
- *Warning evaluation metrics:* lead hours (signed), valid target capture, false alert burden per observation family, recall on all enrolled adverse events, tier impact calibration, conditional time-to-trough/recovery, path/phase drift, missingness and abstention. State any insufficient independent N.

### PDP-2. Calibrated probability and multiweek regime challenger (blocked unless source qualified)

- Before a numeric probability exists, test event-specific base rates and candidate probabilities with Brier, log loss, calibration slope/reliability grouped by true independent episode family and severe missingness checks. Leave a no-edge/abstain baseline. If only source `confidence_quality=HIGH`, never convert to `7/10`.
- Distinguish ordinary transient pullback, 72h trend stress, 14D/21D continuation, multiweek regime shift and 4–8W cycle context from distinct frozen owners; no 21–30D silently renamed 14–21D. A 12h relief rally can coexist with poor multiweek structure.
- Quantify false "bear" and late bear confirmation separately. Do not assign `STRUCTURAL_BEAR` from HIGH pullback state or current SELL availability.

### PDP-3. Holder vs fresh cash, high-beta/illiquid alt portfolio utility (blocked until economic tape admissible)

- Two strictly different baselines: existing-holder full HOLD vs fresh-cash WAIT, with identically timed price-only protective control. Do not use paper signal as an executed trade.
- Research-only counterfactuals `TRIM_REVIEW / STABLECOIN_HOLD / STAGGERED_REENTRY` require event knowledge before first feasible fill, legal owner permission, liquidity, market impact, spread/slippage, gas/fees/turnover/re-entry delay, false-sale cost, missed upside, severe microcap sellability. No wallet/size/fill proof = `ECONOMIC_EDGE_NOT_MEASURABLE`.
- Separate crypto market signal from personal asset-specific portfolio execution. No wallet addresses, holdings, quantities, source-restricted data or position-specific SELL recommendations in the public repo/site.
- Compare across all R4P scenarios A–T and additional investor scenarios under identical target source and control clocks. Investor utility must survive V-shaped recoveries and selected positive pumps as well as crashes.

### PDP-4. Governed Compass ↔ site consumer bridge (KEY TO THIS USER REQUEST)

**Only approved official status flows to the primary site risk display. Research evidence MUST NOT silently update the official public stage.**

```text
EDGE/M6/Pullback research + immutable outcome rows
    ↓  research-only candidate; NO current market permission
existing Research Governance + #1530 material-delta review
    ↓  independent PIT, episode N, comparator and economic validation
#1553 Official Compass protection owner (+ #1516 path where relevant)
    ↓  explicit OWNER-RATIFIED, VERSIONED prospective model/contract update
Official immutable Compass freeze + governed public projection
    ↓  source hash, timestamp, status, expiry and identity checks
existing site/build-public.mjs + vNext official-feed-parity.mjs
    ↓  presentation-only, DA/EN 390/430 iPhone source-bound updates
site Overblik / Kompas: risk stage, ETA, magnitude/duration when approved;
SELL and re-entry remain independent.
```

- Research has a separate optional **research status** readback with `RESEARCH_ONLY / EXPERIMENTAL / NO_AUTO_PROMOTION`. It may show non-sensitive counts and whether research is in progress *only* after separately approved public disclosure. It may NEVER occupy the official risk-stage/ETA/SELL field or derive future event chance.
- On each future accepted Official Compass change, normal existing publish/refresh delivery is allowed to update the site, but a GitHub workflow success **alone** is not evidence that public Pages/browser uses the new commit. Verify publicly served snapshot, exact official compass ID/hash, matched CN week, source age, site build, actual phone readback.
- The site shall **not** query a private source, raw research features, draft PR head or any noncanonical candidate JSON as an official status. There is no new direct research API in this mission.
- If new site metadata fields for size/duration/event target eventually gain canonical ratification, add them through an opt-in schema extension with `null` defaults and backward compatibility; confirm no site alerts/percent derivation or state change for older records.
- If official severity changes because of approved code and newly eligible evidence, it is the **official owner** that makes the new stage, not the site. Current stages already legal: `NORMAL / BUILDING / ELEVATED / HIGH / CONFIRMED`; new number of stages requires its own explicit governance.
- Mark `stage_changed_at`, `issued_at`, `valid_through`, `risk_source_week`, `first_knowledge` where available; do not synthesize timestamps or confidence. A stale/invalid source goes `UNAVAILABLE` for fresh risk, with a clearly historical last-verified class only if UI separates it.
- Site UI in #1576 is already coded source-only. No duplicate side-panel. Reuse existing small categorical escalator and dropdown. Do not touch production Pages without #1578 release gates.

### PDP-5. Compact investor facing Compass status profile: approved for RESEARCHED UX only

One possible *presentation shape*, not a new active forecast:
```text
PULLBACK-PROFIL  ·  kilde og tidspunkt
Risiko        ELEVATED (OFFICIEL, kvalitativ)       // show only actual source
Timing        INGEN VALIDERET ETA
Størrelse     UKENDT for BTC/ETH; alt-tier UKENDT
Varighed      UKENDT; hurtig dip vs trend ikke afgjort
2–3 uger     MIXED/UP/DOWN if official, else UKENDT
Handling      NOW: HOLD_WAIT [new-cash/navigation]
Eksist. salg  SELL-VURDERING: IKKE TILGÆNGELIG
Re-entry     only source-owned state; otherwise UKENDT
Næste test    exact source-owned falsifier when available
```
For site: first line + tiny risk escalator, other facts inside **existing** collapsed investor dropdown; for chat Kompas: one short compact protection subsection, preserving the existing two 3-column mobile tables and NO widgets.
`HOLD_WAIT` text must say "markedets nuværende handlingsgate, ikke en personlig vurdering af, at det er sikkert at være fuldt investeret." Never invent full stablecoin conversion advice.

**No new score display** until a truly calibrated event probability score earns separate ratification. Labels `LOW/MEDIUM/HIGH` remain evidence strength, NOT likelihood.

### PDP-6. Release/test/learning matrix

All 20 R4P scenarios A–T remain mandatory. Add explicit consumer negative controls:
1. Official HIGH, onset null → no imminent ETA, no probability, no SELL.
2. Official ELEVATED with LOW quality and bearish 12h but MIXED 2–3W → distinct short/medium information, no forced regime.
3. Official BUY/HOLD source conflict → never construct a new trading action, show source inconsistency/UNKNOWN.
4. Previously HIGH, now NORMAL or UNAVAILABLE → risk stage may recede/expire, no progress filling all prior dots.
5. Candidate research `NEAR_TERM_CANDIDATE` with official NORMAL → site official remains NORMAL, research status if shown separate, not auto-promoted.
6. Candidate research `-20% micro` but tier basket source missing → public impact UNKNOWN.
7. Expired Compass or unmatched CN week → no LIVE class/ETA; no fallback into unreconciled old weekly seed.
8. New future optional duration/probability keys unsupported by site schema → ignored/UNKNOWN, no display crash.
9. Distribution confirmed but SELL unavailable → keep separate; no disguised SELL.
10. Re-entry `REVIEW` → NOT BUY; no transaction recommendation.
11. Restricted private source arrives → public builder refuses raw values/wallet/PII.
12. W42 source displayed in static W41 preview → archival, NEVER live.
13. Apparent ~80% scored interval coverage but 0 independent family controls → research stays NOT_DEMONSTRATED.
14. Live official source changed while site still old → record SITE_DELIVERY_LAG, do not claim synced.
15. Danish/English switch, iPhone 390/430 and VoiceOver: no overflow, stage semantics preserved.
16. Notification claim: GitHub site updates are not proof of actual ChatGPT/iPhone push delivery.

Required QA: read-only code/test fixtures under existing respective owners, independently reviewed exact-head PR, source-binding and privacy-negative tests, actual successful CI, pre/post screenshot, Pages/app preview LIVE vs PINNED label, rollback proof, no prod change unless passed. Existing #1576 site CI does not establish live release; old W41 static seed must not be confused with latest official source.

### PDP-7. Compounding handover and acceptance

- For each qualified outcome, existing #1530 governor records `material_delta / NOOP / COLLECT / FALSIFY / CONCLUSION_REVIEW`, error family, event-clock, false warning / missed event, eligible independent N, source age, cost and next experiment; only matured, eligible evidence enters Master Monday CN precision learning.
- Research finding `WARNING != SELL` cannot be overridden by site pressure. Risk/proximity/size/duration/action labels remain separately calibrated and versioned. Preserve every negative finding.
- Approval gate for future official *calibrated numeric score or severity escalation rule*: temporal proof + representative prospective cohort (adverse & controls) + independent family N + simple same-clock comparator + false alarm/cost evaluation + versioned schema and thresholds + security/privacy review + existing owner explicit ratification + source-to-site proof + rollback. Absent any gate => **NO OFFICIAL PROMOTION**.
- "Automatic site update" means **the existing deployment consumes accepted canonical public projections when their immutable source changes and successfully deploys**; it does not mean direct consumption of unadjudicated research.
- Track stage result `PDP_PROFILE_DESIGN_STAGED` now, not `PDP_IMPLEMENTED` or `SCIENTIFIC_EDGE_PROVEN`. The upcoming Task 2 executor shall acknowledge exact document SHA in its next checkpoint; old external API sessions cannot be assumed to read the new doc automatically.

## Precise next Task 2 execution order

1. Read this file + current R4P + Task2 R0/R1 receipt + owner #1553 / #1530 / #1516 + site #1576.
2. Deliver `PDP-0` owner clock/status matrix; quantify weekly-to-hourly stale-severity discordance (read-only, no new thresholds).
3. Prepare, under existing owner, eligible source/target/family preregistration for `PDP-1`, including no-warning/false-positive controls and input clock.
4. Build `PDP-4` site-source handover fixture matrix for the already-coded #1576 adapter and put a bounded design comment there. No direct research feed.
5. Only after eligible pre-frozen independent prospective events accrue, run `PDP-2/3` calibration and economics. On inadequate N or inaccessible restricted data, report blockers and continue safe negative tests.
6. Produce durable receipt under existing Task2/EDGE owner, with `PDP` stage, source commit, eligible independent families, passed/failed negative tests, next exact owner, effective site source hash/age and known site deployment status.

**DO NOT call a design or drafted PR scientific validation; do not claim a future running agent consumed this addendum until it leaves its next exact source-read receipt.**
