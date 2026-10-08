# Cycle Navigator Site v2

## Purpose

This folder is the public web presentation layer for Cycle Navigator.

It is intentionally a presentation and live-context surface, not a new market-state engine and not a new source of authority.

## Authority model

1. The official Cycle Navigator state MUST originate from `05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json` and the machine package referenced by its `week_dir`.
2. The public website MAY consume a mechanically generated, privacy-safe snapshot derived from those canonical files. That snapshot is delivery infrastructure only and MUST NOT become an independent authority.
3. Live market prices MAY refresh more frequently for context.
4. Live prices MUST NOT silently change the official weekly state, forecast freeze, structural calls, scorecard, rotation ladder, short-horizon map or altseason countdown.
5. When the canonical public snapshot is unavailable, the UI may show a clearly bounded embedded fallback, but must label the official feed as unavailable.
6. If the canonical package status is `DEGRADED`, the public site must expose that status rather than cosmetically hiding it.
7. Numeric forecast ranges must remain absent when the machine package freezes those fields as `null`.
8. Public-facing Cycle Navigator identity MUST use `public_series.current_public_projection.public_issue_number`; migration-era machine issue numbers must not be exposed as the public CN number.
9. The NOW risk curve MUST be owned by the typed Official Compass capitalization ladder. Legacy weekly rotation text may appear only as structural context outside the live action surface and must not be converted into site-derived action badges.
10. Live Price Range Precision MUST expose its source timestamp and freshness SLA. If the last complete hourly owner observation exceeds the SLA, the UI must show `STALE` rather than `LIVE`.
11. The Pages delivery should refresh after the successful hourly owner chain reaches Native Handlekompas. This is delivery only and cannot alter Official Compass or Cycle Navigator authority.
12. PATH v3 is a two-primary-layer presentation surface: `MARKET CYCLE` and `THIS WEEK'S ROTATION`. Altseason timing remains a compact milestone/watch panel inside MARKET CYCLE rather than a third duplicated phase ladder. None of these presentation layers is an independent market classifier or execution owner.
13. MARKET CYCLE MUST present the crypto journey as a source-owned checkpoint route: BTC leadership → Ethereum leadership → Large + mid rotation → Altseason ignition → Micro acceleration → Broad altseason → Mania / euphoria → Distribution → Exit / protection → Cooldown / re-entry.
14. The MARKET CYCLE route MAY mark a live current checkpoint from typed Official Compass / protection / sell / re-entry state, but the marker is presentation-only. It MUST NOT silently claim that an independently unconfirmed 4–8 week cycle phase has become confirmed.
15. A structured `decision_projection.next_21_30d` or `weeks_4_8` destination may be shown as a separate long-range view. A forward destination MUST NOT masquerade as the current checkpoint.
16. The old PATH short-horizon `DECISION WINDOWS` rail (0–12h / 1–3d / 5–7d / 2–3w / 4–8w) is retired from the primary PATH journey because NOW/Market Compass already owns those horizons.
17. THIS WEEK'S ROTATION MUST read the typed Official Compass `capitalization_ladder` for BTC → ETH → large → mid → small → micro → memes. Weekly CN `rotation_ladder` text is supporting explanation only.
18. Rotation MUST use one compact rail with a visually distinct CURRENT POSITION and NEXT GATE. Seven stacked primary rotation cards are not the preferred v3 presentation.
19. The Rotation rail MAY be framed as Monday baseline → live now → Sunday review, but it MUST NOT fabricate day-by-day asset sequencing or imply that every tier must open before the week ends.
20. MICROCAPS MUST NOT proxy MEMES. MEMES remains unavailable until its own signal exists.
21. The compact Altseason Watch defaults to `ALTSEASON IGNITION` with public meaning `Small caps begin to participate`. Its ETA is a source-owned target/watch window, not a guaranteed phase-start date.
22. As source-owned stages activate, the Altseason Watch target MAY advance to Micro acceleration → Broad altseason → Mania / euphoria → Distribution / protection → Re-entry. The target changes; PATH MUST NOT reintroduce a second long duplicate stage ladder.
23. Distribution MUST read `COMPASS_PROTECTION_TRACKER_v1.distribution_risk`; Exit / Protection MUST read `COMPASS_SELL_ASSESSMENT_v1`; Re-entry MUST read `COMPASS_PROTECTION_TRACKER_v1.reentry_state`. Neither pullback nor distribution context alone may become a frontend sell instruction.
24. PATH MUST NOT synthesize a calendar countdown or more precise ETA from elapsed time, prices, stage order, historical averages or client-side arithmetic. Unsupported timing remains `NO SUPPORTED ETA`.
25. Conditional timing MUST be presented as a watch window with explicit confirmation semantics, for example `1–7 days · only if confirmation arrives`. It is never a countdown.
26. If Official Compass is unavailable or Compass→weekly alignment is not `ALIGNED`, live checkpoint, Rotation, Altseason Watch, protection and exit overlays fail closed. Independently frozen weekly context may remain visible.
27. Pages MUST verify the exact internal Official Compass source binding against the current Cycle Navigator public identity before live PATH overlays are accepted.
28. The compact PATH overview MUST show CURRENT CHECKPOINT and the immediate NEXT CHECKPOINT with gate status. Numeric ETA belongs once on the route. If no checkpoint is known, NEXT WATCH may show the source-owned milestone. Long-range view remains in the cycle header; it must not be repeated as a third overview tile.
29. The current checkpoint may select the furthest sequential live tier already supported by existing Compass semantics. A `HOLD` status may identify the current supported rotation position but MUST NOT be rewritten into `ACTIVE` or `CONFIRMED`.
30. The MARKET CYCLE visual grammar is: blue = current supported checkpoint, amber = next watch target, grey = later/reference phase. Past checkpoints may be visually muted but not rewritten.
31. PATH SHOULD be understandable without internal terms such as owner, lineage, canonical, fail-closed, machine package, action authority or capital transmission.
32. Public display labels MAY simplify internal status vocabulary conservatively, but MUST NOT make a signal more permissive or precise.
33. Longer 2–3 week / 4–8 week prose belongs behind `More cycle context` or another progressive disclosure, not as a repeated primary timeline.
34. The primary mobile acceptance target is that current checkpoint, next watch, cycle route and Altseason Watch are visible within the first PATH viewport plus a short scroll, while Rotation remains compact and scan-friendly.
35. The v3 release contract marker is `CN_PATH_CYCLE_ROTATION_v3`. Release gates MUST reject a regression that restores the old primary Decision Windows rail or requires the retired `3 · ALTCOIN CYCLE TIMER` section.
36. The Market Cycle route MUST mark the immediate sequential phase after CURRENT CHECKPOINT as NEXT. A later source-owned Altseason milestone MAY remain separately marked WATCH.
37. Each supported phase ETA MUST be attached to that phase's incoming route segment and labelled as measured from the current verified snapshot. Conditionality MUST stay explicit. Independent intervals may overlap and MUST NOT be summed or presented as a scheduled arrival.
38. The route's five connector dots MAY encode only a deterministic distance category from the published ETA: up to 7 days = 5, up to 14 = 4, up to 21 = 3, up to 35 = 2, farther = 1, and unsupported = 0. The dots are not elapsed progress, completion, probability or a new market score; they do not animate. When aligned weekly and live timing differ, the frozen weekly sequence is the conservative ceiling and the slower/unsupported weekly window wins.
39. The Altseason Watch panel MUST NOT repeat a numeric ETA already shown on the route; it summarizes target, gate status and whether timing is weekly-supported. Unsupported weekly timing remains unavailable even if a faster live Compass review window exists, with no browser countdown or inferred estimate.
40. The optional weekly range journey is an accountability visual, separate from macro cycle checkpoints and weekly segment permission. It MUST bind CN_PUBLIC_LIVE_PRICE_PRECISION_v1 to the current public issue and forecast week. Grey bands are immutable forecast ranges; blue bars are full observed low–high ranges to date for each window, not per-point prices. Empty future hours and incomplete coverage MUST remain unplotted. No forecast line may be inferred from band midpoints.
41. The weekly graph MUST show observation cutoff and freshness; observations exceeding the existing freshness SLA are labelled STALE SNAPSHOT. Any percentage distance is a labelled observed-range breach relative to its frozen boundary, never a probability, pullback prediction, current spot location or buy/sell signal. The graph consumes only existing sanitized public fields and creates no new raw-data projection or scoring formula.
42. The always-present NOW dip/pullback disclosure MUST consume only typed COMPASS_PROTECTION_TRACKER_v1 and COMPASS_SELL_ASSESSMENT_v1 under an OK public Compass. Source classification, onset watch, qualitative confidence, sell assessment and re-entry stay distinct. Missing depth, severity, duration and sell/rebuy edge MUST remain unquantified or unconfirmed. Ordinary retest wording may translate the published classification but cannot establish that an actual decline is small or confirmed.
43. A protection warning cannot grant a sell, short or early re-entry instruction. LOW/MEDIUM/HIGH evidence quality is qualitative and cannot be converted into probability. The primary risk summary appears once in the expandable risk card, with details behind it.
44. PATH action lenses MUST use the aligned OK Compass action, distinct sell assessment and separate capitalization permissions. MICROCAPS cannot proxy MEMES. Cooldown / re-entry must await fresh source confirmation before a new BTC-leadership checkpoint; no timed cycle restart is permitted.

8. Current production routing follows `00_ARCHIVE_CONTROL/2026-09-14__autonomous-data-authority-transition-v1__canonical.md`. Manual DATA PING is not a prerequisite or default upstream for this site.

## PATH product freeze and v3 supersession

PATH v2 was product-frozen on 2026-10-05 after PR #1500. On 2026-10-06, production iPhone screenshots documented a concrete usability regression: Compass decision-window duplication inside PATH, repeated rotation/altseason ladders and excessive vertical density.

That evidence activates the versioned exception permitted by the freeze.

PATH v3 therefore supersedes the v2 **presentation architecture only**.

Frozen v3 product invariants:

- First-scan questions remain: **Where are we in the market journey? → What must unlock next? → Where is capital rotating this week?**
- Primary IA is `MARKET CYCLE` → `THIS WEEK'S ROTATION`, with Altseason Watch embedded as a compact cycle milestone.
- Market Cycle owns the big journey from BTC leadership through altseason and protection.
- Rotation owns the detailed BTC → ETH → large → mid → small → micro → memes live risk curve.
- Short-horizon Compass decision windows are not duplicated as the primary PATH timeline.
- Altseason Watch remains source-owned and conditional; no browser countdown math.
- Current checkpoint and next watch must remain visually and semantically distinct.
- Cosmetic churn alone is not sufficient reason to redesign PATH after v3. Future changes require a documented regression, evidence-backed usability problem or genuinely new source capability.
- Historical branch `feat/cn-path-three-track-v2` remains salvage/history only and MUST NOT be merged or rebased into production as a unit.
- Implementation specification: `05_CYCLE_NAVIGATOR/site/PATH_V3_CYCLE_ROTATION_PRODUCT_SPEC.md`.

This freeze constrains presentation churn only. It does not block source-owned Compass/Cycle Navigator updates, scoring/accountability fixes, privacy repairs or safety/reliability corrections.

## NEXT DAYS / short-horizon rule

The shortcut `NEXT DAYS` surface is governed by the active Weekly Cycle Navigator Publication Contract v1.1.

Preferred source:

- `forecast_freeze.intraday_map.day_1_2`
- `forecast_freeze.intraday_map.day_3_4`
- `forecast_freeze.intraday_map.day_5_7`

These values are frozen OFFICIAL Cycle Navigator publication fields. Unsupported buckets MUST be `UNAVAILABLE`; the website must not fill them from LIVE prices, Daily Director shadow output, historical DATA PING, narrative interpolation or a parallel site forecast engine.

Backward-compatible transition rule for an already-published Cycle Navigator issue that predates the structured `intraday_map` field:

- `build-public.mjs` MAY expose a verbatim explicit `Near-term risk:` label already present in that issue's OFFICIAL readable/X-ready publication;
- the public snapshot MUST label this state `RISK_BIAS_ONLY`;
- a risk-bias fallback is not a reconstructed 24–72h directional price forecast and must not be presented as one;
- if neither a structured OFFICIAL intraday map nor an explicit OFFICIAL near-term-risk label exists, the correct public result is `UNAVAILABLE` / `NOT PUBLISHED`.

This transition adapter is deterministic delivery logic only. It has zero authority to invent, score or promote a new market call.

## Composite Compass evidence for chat and website (2026-10-08)

Every standard Kompas invocation in chat and the Cycle Navigator NOW Compass share the source-selection and action-authority semantics of `07_PROMPTS_AND_AGENTS/action_compass/2026-09-16__global-action-compass-invocation-contract-v1__canonical.md` Section 3.1.

The existing Pages builder attaches `PUBLIC_COMPASS_FULL_STACK_READBACK_v1` under `PUBLIC_COMPASS_PROJECTION_v1.full_stack`. It cross-reads the current Official Compass, Auto Market State, Native Handlekompas, non-binding Shadow Compass v2, current governed Master Monday and Cycle Navigator, and Strategic Compass. The site displays this as ONE cohesive Compass surface inside NOW, not another cycle/timeline inside PATH.

**Non-negotiable:** Official Compass alone owns confirmed action, capitalization permissions, protection/sell/re-entry, and official Bull/Bear. Source-bound Shadow v2 offers analytical disagreement and direction but has no permission to create BUY/SELL. The weekly Cycle Navigator owns 4-8w. When official data are degraded or stale, the official view remains WAIT/UNAVAILABLE; a research view can be shown only with a visible source-age caveat. Missing/mismatched evidence is explicitly degraded or unverified.

The integrated site readback is an allowlisted public presentation object, not a parallel forecast engine or a fresh model run. It must not include restricted provider values, raw source packets, internal paths, credentials or portfolio data. It must never fabricate timing, percentages, score, signal, certainty or trading permissions. The PATH product design and existing Official Compass deployment triggers are preserved. A trusted completed `Shadow Compass v2` workflow on `main` additionally requests a Pages rebuild through GitHub `workflow_run` because ordinary `GITHUB_TOKEN` pushes do not trigger downstream `push` workflows. It does not create additional AI/model calls and it ignores untrusted PR workflow completions.

## Privacy-safe public delivery

The public browser MUST NOT require direct access to the framework repository.

`build-public.mjs` reads the canonical pointer and referenced machine package during deployment and produces `dist/data/latest.json` containing only the fields needed by the public dashboard.

The public snapshot MUST NOT expose:

- repository owner or username;
- repository name or Git provider URL;
- `week_dir` or internal file paths;
- machine package hashes or internal provenance paths;
- unrelated framework files, research, queues, workflows or implementation details.

The deployment output is limited to the website assets plus the sanitized public snapshot.

## Refresh cadence

- Live market pulse: approximately every 60 seconds.
- Public Cycle Navigator snapshot: refreshed whenever the canonical Cycle Navigator publication files change and the hosting platform rebuilds the site.
- The browser may re-check the same-origin public snapshot approximately every 5 minutes.
- Official signal cadence: governed by the existing Cycle Navigator publication workflow, not by the site.

## Data sources

### Canonical weekly layer

Private/internal authority:

- `05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json`
- `${week_dir}/CYCLE_NAVIGATOR_MACHINE_PACKAGE.json`

Public delivery artifact:

- `/data/latest.json`

The public artifact is a mechanically selected subset of canonical fields. It must never infer or rewrite state. Strategic `decision_projection` delivery MUST be field-minimized to what PATH actually presents; internal scenario weights, asset-specific 21–30d directions and falsification details are not public-site dependencies.

### Live context layer

CoinGecko public simple-price endpoint for BTC and ETH spot USD prices and 24-hour change. ETH/BTC is calculated in-browser from the two spot prices.

The live context layer is explicitly non-authoritative for Cycle Navigator state.

## Public precision continuity

The public website follows the established Cycle Navigator public precision presentation. Internal precision expansion is not a reason to expand or redesign the public score surface.

- Keep the existing public score semantics and historical presentation stable.
- Do not expose every internal precision family merely because it exists internally.
- Do not replace a long-running public score with a newer internal component score.
- Do not silently recompute historical public scores under newer internal methodology.
- A public precision-model change requires explicit owner approval and a versioned migration separate from internal calibration work.

## Public experience

The public release exposes:

- current official cycle state;
- live BTC, ETH and ETH/BTC pulse;
- OFFICIAL `NEXT DAYS` intraday map when published, otherwise an explicitly bounded OFFICIAL risk-bias fallback or `NOT PUBLISHED`;
- prior-issue reproducible structural score;
- this-week base case;
- 2 to 3 week base case;
- 4 to 8 week cycle direction when published;
- rotation ladder;
- altseason countdown and path-to-mania sequence reference;
- what worked and what did not;
- frozen confirmation tests;
- publication and source-week status;
- mobile-native share action.

## Design rule

The website can make the weekly report more visual, legible and engaging than the X post, but it must not make the underlying evidence sound more certain than the machine package supports.

## Deployment target

Preferred privacy-preserving production target: a free static host that can build from the private repository and publish only `05_CYCLE_NAVIGATOR/site/dist`.

Current recommended target: Cloudflare Pages free plan with Git integration.

Build command:

`node 05_CYCLE_NAVIGATOR/site/build-public.mjs`

Build output directory:

`05_CYCLE_NAVIGATOR/site/dist`

The production website remains plain HTML, CSS and browser JavaScript so the presentation is portable and is not coupled to one hosting vendor.


## PATH daily-journey revision (2026-10-08)

This section supersedes earlier PATH layout requirements where they conflict. Source authority and frozen scoring contracts remain unchanged.

- Market Cycle is a compact macro-phase list. `market_cycle_context.current_phase` is the accepted Monday regime and may be UNAVAILABLE. A projected destination or tactical ETH HOLD cannot become today's macro phase. The cycle conclusion is integrated here; tactical investor/swing decisions are in NOW.
- The single Altcoin / Rotation journey retains Compass-owned checkpoints from BTC/ETH through takeoff, mania, distribution, exit and governed re-entry. Arrival ETAs sit between nodes and explicitly describe timing from the source observation, not travel duration. Missing or conditional timing cannot become a countdown.
- Takeoff readiness becomes 100% only on an active/confirmed small-cap permission. ACTIVE WATCH, BUILDING, PREPARE and WAIT never unlock takeoff. Unquantified readiness shows individual source-owned gates instead of an invented percentage. MEMES retain independent permission and liquidity requirements.
- `forecast_freeze.daily_price_path`, contract `CN_FROZEN_DAILY_PRICE_PATH_v1`, is produced by the existing weekly LLM synthesis. Each PUBLISHED asset has exactly seven ordered UTC expected-close/low/high points within its weekly range. Unsupported assets have empty points and a reason. No historical freeze is rewritten or given retrospectively fitted daily points.
- `public_live_precision.daily_observations`, contract `CN_PUBLIC_DAILY_OBSERVATIONS_v1`, comes from the existing PASS/OK hourly capture. Daily low/high and last observed close require contiguous valid coverage from UTC day start to the source cutoff. Duplicate timestamps do not add coverage; missing/non-finite values create gaps. Future or unclosed hours cannot enter actuals.
- Blue means frozen forecast; green means actual price. The envelope shows daily forecast low/high, whiskers show daily observed low/high. Straight segments connect real daily points; no fabricated intraday wiggles. Current-day actuals are partial and closing deviation stays pending. Day disclosures expose exact dates, prices, coverage and source time. Historical interval-only forecasts retain their original corridors with an explicit missing-daily-forecast note.
- Daily-path presentation does not alter the six-row, three-window public precision formula, frozen hash, scorecards or final settlement.
- Protection `public_explanation`, contract `CN_PUBLIC_PROTECTION_COPY_v1`, is generated inside the existing weekly LLM call, validated and projected through Compass. It has no action authority; it cannot introduce numbers, probabilities or trading instructions. Structured onset day bounds become calendar dates for possible onset only. Legacy copies fall back to bounded plain-English state explanation. Only explicit source Day N–N legacy timing is formatted as dates; no prose becomes a new risk classifier.
- NOW MIXED includes a concise no-clear-direction explanation. The pullback disclosure preserves expanded state across the automatic Compass refresh. No browser LLM call, API credential, second forecast engine or new workflow is introduced.

Acceptance remains gated on Python contract tests, public release checks, exact-head CI, deployed source readback and real mobile browser inspection. A source test or screenshot transfer failure is not visual acceptance.


## Frozen-week instrument and bilingual presentation (2026-10-08)

- The weekly accountability chart uses self-hosted TradingView Lightweight Charts 5.2.0, with its license, notice and user-visible attribution. Official technical reference: https://github.com/tradingview/lightweight-charts/blob/master/.github/skills/lightweight-charts/SKILL.md . No paid service, browser API key or remote chart CDN is required.
- One BTC/ETH instrument replaces the two SVG plots. Price axis, UTC weekdays, crosshair, reset, touch interaction and a single accessible daily readout expose the immutable forecast and eligible daily observations. Blue is forecast, green is observed evidence. Low/high whiskers are measurements, not fabricated OHLC candles.
- Interval-only legacy freezes remain three authentic corridors with an explicit missing-daily-line explanation. Prospective seven-day forecasts show only their actual published straight daily segments. Separate observed runs never bridge missing coverage. Hidden scale anchors use published bounds solely for scale placement; they never become displayed forecasts.
- DA/ENG is a keyboard-accessible segmented control in the upper right. Browser preference supplies the initial language; a deliberate choice persists locally. Interface, current narratives, dates, chart readouts, proof explanations and historical UI labels switch reversibly. Identifiers, exact source values and downloadable immutable raw records stay canonical.
- Current/legacy public narratives have a curated Danish catalog. Future weekly narrative translations are requested as exact en/da presentation pairs inside the existing weekly synthesis, without another model call or a new forecast engine. The public build only accepts pairs whose English source exists in the already sanitized public fields and whose numeric tokens are identical. Unsupported translations never alter a forecast or score. The first future bilingual synthesis remains prospectively verifiable; no historical freeze is regenerated.
- Translation observers preserve source text independently of displayed language and follow automatic refreshes. Chart instances are removed before replacement. New UI assets use content hashes to avoid stale browser files.
- Validation for this revision: existing release checks plus future-timestamp/wrong-date/invalid-range and translation-projection tests, local DOM translation round-trip/refresh checks and final deployed browser readback. User visual approval remains PENDING; do not mark the graph accepted on technical checks alone.

## PATH clarity and conservative timing (2026-10-08)

- Market Cycle is a four-chapter sequence, not a loose phase inventory: leadership → rotation → altseason → protection/reset. It is labelled as a typical map, never a forecast. No chapter is highlighted when the weekly regime is unavailable.
- Compass owns live checkpoint and gate status. The frozen Master Monday altseason sequence backstops timing. Where their ETAs disagree, PATH displays the slower weekly window; a weekly `No supported ETA` cannot be replaced by a faster live review window.
- Five connector dots express only published time-distance categories: all five within one week, four within two weeks, three within three weeks, two within five weeks, one beyond five weeks, none when unsupported. They never animate and never imply progress, odds or readiness.
- The weekly instrument remains a pane/series-primitive presentation over self-hosted Lightweight Charts v5. Window capsules, subtle separators and corridor styling improve scanability without creating candles, midpoints or fitted movement.
