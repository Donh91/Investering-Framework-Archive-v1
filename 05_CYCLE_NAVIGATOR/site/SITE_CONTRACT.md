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

The public artifact is a mechanically selected subset of canonical fields. It must never infer or rewrite state.

### Live context layer

CoinGecko public simple-price endpoint for BTC and ETH spot USD prices and 24-hour change. ETH/BTC is calculated in-browser from the two spot prices.

The live context layer is explicitly non-authoritative for Cycle Navigator state.

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
