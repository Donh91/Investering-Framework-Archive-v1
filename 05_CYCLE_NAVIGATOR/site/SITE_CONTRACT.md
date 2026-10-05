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
12. PATH is a three-track presentation surface: `MARKET CYCLE`, `ROTATION`, and `ALTCOIN CYCLE TIMER`. None of these tracks is an independent market classifier or execution owner.
13. MARKET CYCLE MUST use only structured public `decision_projection.weeks_4_8` / `next_21_30d` fields for canonical phase placement and forward destination. If the structured phase is unavailable or `UNCLEAR`, the public phase MUST remain `UNCLEAR`; free-form Monday text MUST NOT be converted into a canonical cycle phase by the browser.
14. ROTATION MUST read the typed Official Compass `capitalization_ladder` for live BTC → ETH → large → mid → small → micro → memes status and ETA. Frozen weekly `rotation_ladder` text may be shown only as supporting context.
15. ALTCOIN CYCLE TIMER defaults to `ALTSEASON IGNITION` with the public meaning `Small-cap expansion gate`. Its displayed ETA is an ETA to that governed target gate, not a guarantee that the phase itself begins inside the window. The ETA MUST come from the governed SMALL_CAPS Compass row when available. As governed stages activate, the focus may advance one useful step at a time through Micro acceleration → Broad altseason → Mania / Euphoria. During parabolic/mania conditions the next highlighted phase may switch to Distribution; any governed sell/trim state may switch focus to Exit / Protection.
16. PATH MUST NOT synthesize a calendar countdown or a more precise ETA from elapsed time, prices, stage order, historical averages, or client-side arithmetic. If the relevant governed source does not publish an ETA, the public result is `NO SUPPORTED ETA`.
17. The Altcoin Cycle sequence may show Participation → ETH unlock → Large/Mid transmission → Altseason Ignition → Micro acceleration → Broad altseason → Mania/Euphoria → Distribution → Exit/Protection → Re-entry, but later sequence steps are references only until their governing sources activate them.
18. Distribution MUST read `COMPASS_PROTECTION_TRACKER_v1.distribution_risk`; Exit / Protection MUST read `COMPASS_SELL_ASSESSMENT_v1`; Re-entry MUST read `COMPASS_PROTECTION_TRACKER_v1.reentry_state`. Neither pullback nor distribution context alone may become a frontend sell instruction.
19. If the Official Compass is unavailable, live Rotation and Altcoin Cycle states fail closed to `UNAVAILABLE`; independently frozen Monday context may remain visible.
20. Pages MUST verify the exact internal Official Compass source binding against the current canonical Cycle Navigator pointer before PATH may use that Compass as a live weekly overlay. The public delivery receipt may expose only alignment status, public issue identity and forecast week; internal paths, hashes and machine issue identifiers remain private.
21. If Compass→weekly alignment is `MISMATCH` or `UNVERIFIED`, PATH MUST keep the frozen Monday path visible but fail live Rotation, Altcoin Cycle, protection and exit overlays closed until lineage is aligned. This delivery safeguard MUST NOT make the independently verified NOW Compass unavailable.
22. Every prominent Altcoin Cycle ETA MUST remain visibly described as a conditional target-gate/review window, not a guaranteed phase-start date or automatic sell date.
23. The Altcoin Cycle Timer MUST visually separate the live `NOW POSITION` from the amber `WATCH TARGET`. The current marker is presentation-only and may select the furthest sequential stage whose governed live owner is already `HOLD`, `ACTIVE` or `CONFIRMED`; it MUST NOT upgrade the underlying stage status or turn a target into a current phase.
24. A target ETA MAY appear in the large Altcoin Timer headline only when the source-owned ETA is supported and the governed target status is already `HOLD`, `ACTIVE` or `CONFIRMED`. Conditional or unsupported ETAs remain visible on the relevant timeline row but MUST be withheld from the headline.
25. The compact PATH overview MUST preserve the same NOW-vs-target distinction as the detailed Altcoin Timer. It MUST NOT summarize the watch target as though it were the current phase.
26. The premium NOW recommendation MUST expose its next governed review window prominently. That window is a reassessment horizon, not a promise that the action changes at expiry.
27. Hourly Native Handlekompas may be shown as a clearly labeled context-only freshness monitor. It MUST expose age/staleness and MUST NOT replace Official Compass as the action, horizon, Bull/Bear or execution owner.
28. The NOW conclusion triad MUST label short-horizon direction by its actual horizon and MUST NOT present a 0–12h directional state as the weekly market phase. The 5–7d Official Compass outlook remains visually separate.
29. The NOW risk field MUST pair the governed pullback state with the source-owned protection ETA/window when available and keep distribution status as separate context. A pullback watch MUST NOT be presented as an automatic sell or short instruction.
30. The NOW triad MAY link to a presentation-only decision detail panel that explains the same governed fields for investors and swing traders. The panel MUST NOT introduce new thresholds, forecasts, execution rules or site-side market classification.
31. Conditional PATH timing MUST be presented as a watch window with explicit confirmation semantics, not as a countdown. Presentation may translate units such as `1-7d conditional` into plain English such as `1–7 days · only if confirmation arrives`, but MUST preserve the source-owned timing and MUST NOT add precision.
32. MARKET CYCLE MAY show a visual route and short-horizon decision-window rail for orientation. A long-cycle stage may light only when the structured long-cycle owner supports that placement. When the long-cycle phase is `UNCLEAR` or unavailable, the site MUST say that the exact cycle phase is not confirmed rather than infer a stage from price action or weekly prose.
33. The big-picture PATH surface SHOULD preserve both expert and fast-scan value: short-horizon direction, week-ahead direction, long-cycle availability, the full cycle route, and the longer explanation remain distinct layers rather than being collapsed into one market-phase label.
34. A structured forward destination MUST NOT be labeled as the current market-cycle phase. Until an independently supported current long-cycle phase exists, PATH must keep the current cycle position explicitly unconfirmed while it may separately highlight the next supported destination.
35. PATH presentation SHOULD translate internal implementation vocabulary into public investment language without changing the underlying state. Terms such as owner, lineage, fail-closed, canonical, frozen Monday and machine package must not be required knowledge for understanding the public PATH surface.
36. Public display labels MAY simplify internal status vocabulary for readability, for example HARD_WAIT → WAIT, LOCKED/INACTIVE → NOT ACTIVE and UNAVAILABLE → NO SIGNAL, provided the raw state remains unchanged and the display never makes the signal more permissive.
37. PATH SHOULD expose a compact reading guide that makes the visual grammar self-explanatory: blue means current/now, amber means next watch, and grey means not confirmed or not yet supported.
38. Public PATH horizon labels MAY translate raw `UNAVAILABLE` into `NOT READY` and data-health `OK/PASS` into `UP TO DATE`, provided the underlying values remain untouched and no unavailable signal is represented as active.
39. Public Altcoin stage naming SHOULD prefer market language over implementation language, for example `Large + mid caps join` and `Small caps begin to participate`, while preserving the exact source state and timing rules.
40. When the exact long-cycle stage is not supported, PATH MAY still show a blue current-context marker describing the published weekly setup, but it MUST explicitly say that the cycle stage is not confirmed and MUST NOT place that marker on a specific cycle node.
41. A non-conditional future horizon attached to a WAIT-like Altcoin state SHOULD be labeled as a review window rather than an event ETA. Conditional gates remain watch windows. Neither presentation may imply that the phase begins automatically when the window expires.
42. The public Altcoin sequence SHOULD label the ETH step in market language such as `Ethereum leadership` rather than implementation shorthand such as `Ethereum unlock`, while leaving the internal key and authority unchanged.

8. Current production routing follows `00_ARCHIVE_CONTROL/2026-09-14__autonomous-data-authority-transition-v1__canonical.md`. Manual DATA PING is not a prerequisite or default upstream for this site.

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
