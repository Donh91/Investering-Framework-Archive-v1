# Pullback Progression — existing Official Compass owner handover

**Date:** 2026-10-12 · **Priority:** P1/P0 risk-to-action source gap  
**Canonical issue:** [Archive #1553](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1553) (Workstream B/C/F). **Site existing owner:** [#1578](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1578) / Draft PR #1576.  
**Status:** UI source-label adapter CODED, negative tests CI-gated, **not deployed**; new intraday escalation / calibrated ETA logic **NOT IMPLEMENTED OR PROVEN**. No additional scheduler, scanner, market authority or auto-trading.

## Verified current repo facts

1. The production [protection contract](../../../04_MARKET_LEARNING/handlekompas/PROTECTION_TRACKER_CONTRACT_v1.md) already permits `NORMAL / BUILDING / ELEVATED / HIGH / CONFIRMED / UNAVAILABLE`. Quality is `LOW / MEDIUM / HIGH` **evidence quality**, not calibrated odds.
2. `scripts/data_ping/native_handlekompas.py::protection_tracker` reads the **structured CN decision_projection.protection**, i.e. predominantly the frozen **weekly** baseline. New hourly price/breadth can change `market_now` and trigger event refresh **without updating official pullback severity**. This is a genuine information cadence gap.
3. `scripts/data_ping/compass_event_refresh.py` can request early fresh Compass on canonical material transitions or downside heat. It does **not** have license to produce a more severe risk state or a new ETA. Existing 08:17 and 20:17 Copenhagen Compass schedule must remain.
4. Latest inspected actual source `CMP-20261012-3f1e99c2868e` / 2026-W42: `pullback_risk_state=ELEVATED`, `confidence_quality=LOW`, `onset_start_utc=null`, `onset_end_utc=null`, `SELL=UNAVAILABLE`, `distribution_risk=UNKNOWN`. Hence **NO imminent / probability claim** today.
5. Current Draft PR #1576 now has `official-pullback-eta.mjs`, `official-pullback-stage.mjs`, read-only live `official-feed-parity.mjs`, W41/W42 and negative tests. These display original owner stages, a justified forecast window (if any), and clear `Nært forestående: ikke dokumenteret`. A stage 4/5 is **risk classification**, not evidence of an actually observed market crash.

## Product semantics — three independent axes, not one inevitable sequence

| Axis | Existing allowed values | Future optional governed owner |
|---|---|---|
| Risk stage | NORMAL, BUILDING, ELEVATED, HIGH, CONFIRMED; UNAVAILABLE | Existing Official Compass Protection Tracker; source-only presentation |
| Timing / proximity | Unknown, sourced week-only watch, typed prospective start/end where actually published | **Prospectively** governed horizon statement; no imminent assertion merely because risk HIGH |
| Evidence quality | LOW, MEDIUM, HIGH (qualitative, no odds) | Existing owner, source lineage, PIT complete evidence |
| Event/recovery *outcome*, separate | Not yet observed; threshold event onset/peak/trough/reclaim; re-entry states already exist | Existing EDGE-001/M6 event/outcome owner only after PIT/source/definition gates |
| Asset-specific damage | UNKNOWN until independent BTC/ETH/large/mid/small/micro source basket evidence | Existing EDGE-001/portfolio owners; NEVER assign synthetic cap-tier damage from BTC % |

The risk state may **move backwards or expire**: BUILDING→NORMAL, ELEVATED→BUILDING, HIGH→UNAVAILABLE on source outage (last verified source may be shown as explicitly STALE, not live). Do not display an unconditional progress bar 1→5 implying a pullback must happen.

Public default 10-second view:
`PULLBACK ELEVATED · Forhøjet – følg næste bekræftelse`  
`Muligt i uge 42 · præcis ETA ikke dokumenteret`  
`Lav evidenskvalitet · ikke en sandsynlighed; SELL vurderes separat.`

Only if a **future accepted canonical source** explicitly supports a 0–12/12–24/24–72h onset band with observable issued-before-event freeze may the site say "kort tidshorisont" or "nært forestående" **with the exact source clock, strength and falsifier**. Numerical certainty 70/80/90% requires a separately approved calibration protocol, qualified out-of-sample denominator and reliability error bars. The site never creates it.

## Single owner research/implementation phases — reuse existing #1553 / #1530 / #1578

### Phase 0 — first-party source clocks, no new signal

Inventory existing immutable hourly sequences, official predecessor/current Compass risk history, current CN freeze/week, same-asset time windows and existing M6/EDGE-001 source legality. For each event record: source clock, observed clock, frozen call time, ingest/publish clock, source hashes and canonical owner. Respect public/private boundaries, no private holdings in site. Reproduce October 7/8 delayed severity *as a postmortem*, not as a fake ex-ante forecast.

### Phase 1 — shadow staged *challenge*, not authoritative warning

Reuse existing M6/EDGE-001 shadow research owner to publish a `WEEKLY_BASELINE_CHALLENGED` advisory **only if** preregistered independent evidence families truly support it. Candidate inputs: BTC/ETH relative change and ETH/BTC, breadth/tier transmission, settled ETF net flows, funding/OI/leverage/spot where owner verified. Deduplicate correlated same-provider readings. Fixed persistence/hysteresis and source age are essential to avoid transient 1h false escalations; derive these parameters prospectively in review, not from this prompt. A source gap produces `UNASSESSED` / UNKNOWN, not an upgrade or all-clear.

Shadow output should be additive and initially **NO LIVE RISK AUTHORITY**:
- `research_stage`: WATCH / ESCALATING_CANDIDATE / NEAR_TERM_CANDIDATE / RECOVERY_CANDIDATE / NO_EDGE / UNASSESSED,
- `competing_official_stage` (original official value unchanged),
- `source_issued_utc`, `observation_asof_utc`, `source_sha256`, `valid_through_utc`,
- `independent_evidence_family_ids` and count, `missing_or_conflicting_families`,
- `candidate_onset_window_start/end` nullable and **not public** without explicit source admission,
- `risk_to_alt_tiers` UNKNOWN until source universe and observed metrics have been fixed,
- `invalidation`, `falsifiers`, baseline comparison, effective event family id, `authority=RESEARCH_ONLY`.

### Phase 2 — prospective freeze and independent outcome scoring

At the existing official 08:17/20:17 + truly qualified EVENT_DRIVEN material changes, retain full immutable pre-outcome frozen source identity for **every candidate and NO_WARNING**, including abstentions, null ETA, missing/late observations. Use only established EDGE-001/T2 episode clustering and censored controls (do not count correlated BTC/ETH panic twice). Timewise evaluate +12h, +24h, +72h and 7d horizons; extend once per governed horizon. Score:
- whether warning was made early enough for its promised window, how many hours before onset, and whether the purported severity was observed;
- missed material pullbacks, true negatives, false warnings / premature "imminent", and when a forecast's invalidation actually happened;
- conditional lead-time distribution, warning precision/recall, abstention rate, source coverage and effective N;
- altcoin impact and time to recovery **only** after a fixed admissible tier basket is actually observable;
- action utility separately vs always-NO-WARNING / HOLD baseline, fees/slippage/opportunity costs where justified. No trading from site.

Explicit negative/adversarial controls: Sept 19 false warning, Oct 7/8 postmortem, one bad hour, false breadth correlation, late ETF settlement, uptrend after a watch, source outage, mid-retest rapid reversal, invalid event onset, missing intraday data, future leak and backfill. Historical postmortem **cannot** count as prospective accuracy.

### Phase 3 — only evidence-accepted promotion / Site automatic consumption

After sufficient preregistered independent forward evidence and governance:
- Existing Official Compass owner may publish a **versioned accepted structured risk progression** plus typed `time_proximity` with explicit null support and issue/effective/expiry timestamps. Never overwrite earlier frozen calls.
- Existing `native_handlekompas.py` and its `build_public_projection` publish once from accepted owner; keep `sell_assessment` separately `UNAVAILABLE` unless its OWN review gate changes.
- Existing `site/build-public.mjs` already copies the owner-projected public protection tracker. The vNext **live** feed adapter `official-feed-parity.mjs` now exposes `pullback_stage` ONLY when current feed delivery/Compass identity and weekly projection align; unsupported fields abstain and all source states remain first-party.
- When actual official risk changes and a fresh site build is delivered, the site updates through existing automatic Pages delivery. A new risk taxonomy requires explicit versioned UI/contract acceptance: no silent interpretation of unknown novel values.
- Verify exact main, official/published projection hashes, Pages live readback and iPhone/DA/EN. Existing app chat alert automation is separate; GitHub publish success is not proof of iPhone push notification. No new scheduler.

**Hard stop:** If science cannot qualify a useful near-term onset signal, keep 'nærhed ukendt'. Do not turn weak evidence or high severity into a clock just to improve UX.

## Immediate work packet / ownership handoff

- Risk-signal/internal model and prospective outcomes: **existing #1553 (Official Compass) + #1530 (M6/EDGE-001)**. Avoid separately claiming a new model or automatic trade rule.
- UX/data bridge and release QA: **existing #1578** and Draft PR #1576, with the already-authorized Work owner / existing Supervisor; no separate app/automation or parallel Pages deploy.
- Required first implementation milestone: owner-approved shadow `WEEKLY_BASELINE_CHALLENGED` with 3-or-more genuinely independent families/declared controls, legal PIT readback and prospective frozen NO_WARNING/abstentions; prove it existed **before** any next qualified event. No calibration promise until measured.
