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
28. The compact PATH overview MUST keep CURRENT CHECKPOINT, NEXT WATCH and LONG-RANGE VIEW distinct. It MUST NOT summarize the next watch as the current phase.
29. The current checkpoint may select the furthest sequential live tier already supported by existing Compass semantics. A `HOLD` status may identify the current supported rotation position but MUST NOT be rewritten into `ACTIVE` or `CONFIRMED`.
30. The MARKET CYCLE visual grammar is: blue = current supported checkpoint, amber = next watch target, grey = later/reference phase. Past checkpoints may be visually muted but not rewritten.
31. PATH SHOULD be understandable without internal terms such as owner, lineage, canonical, fail-closed, machine package, action authority or capital transmission.
32. Public display labels MAY simplify internal status vocabulary conservatively, but MUST NOT make a signal more permissive or precise.
33. Longer 2–3 week / 4–8 week prose belongs behind `More cycle context` or another progressive disclosure, not as a repeated primary timeline.
34. The primary mobile acceptance target is that current checkpoint, next watch, cycle route and Altseason Watch are visible within the first PATH viewport plus a short scroll, while Rotation remains compact and scan-friendly.
35. The v3 release contract marker is `CN_PATH_CYCLE_ROTATION_v3`. Release gates MUST reject a regression that restores the old primary Decision Windows rail or requires the retired `3 · ALTCOIN CYCLE TIMER` section.

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
