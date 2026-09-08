# Cycle Navigator Site v1

## Purpose

This folder is the public web presentation layer for Cycle Navigator.

It is intentionally a presentation and live-context surface, not a new market-state engine and not a new source of authority.

## Authority model

1. The official Cycle Navigator state MUST come from `05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json` and the machine package referenced by its `week_dir`.
2. Live market prices MAY refresh more frequently for context.
3. Live prices MUST NOT silently change the official weekly state, forecast freeze, structural calls, scorecard, rotation ladder or altseason countdown.
4. When the canonical feed is unavailable, the UI may show a clearly bounded embedded fallback, but must label the official feed as unavailable.
5. If the canonical package status is `DEGRADED`, the public site must expose that status rather than cosmetically hiding it.
6. Numeric forecast ranges must remain absent when the machine package freezes those fields as `null`.

## Refresh cadence

- Live market pulse: approximately every 60 seconds.
- Canonical Cycle Navigator pointer/package: approximately every 5 minutes.
- Official signal cadence: governed by the existing Cycle Navigator publication workflow, not by the site.

## Data sources

### Canonical weekly layer

Public raw files from `Donh91/Investering-Framework-Archive-v1`:

- `05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json`
- `${week_dir}/CYCLE_NAVIGATOR_MACHINE_PACKAGE.json`

### Live context layer

CoinGecko public simple-price endpoint for BTC and ETH spot USD prices and 24-hour change. ETH/BTC is calculated in-browser from the two spot prices.

The live context layer is explicitly non-authoritative for Cycle Navigator state.

## Public experience

The first release exposes:

- current official cycle state;
- live BTC, ETH and ETH/BTC pulse;
- prior-issue reproducible structural score;
- this-week base case;
- 2 to 3 week base case;
- rotation ladder;
- altseason countdown;
- what worked and what did not;
- frozen confirmation tests;
- publication and source-week status;
- mobile-native share action.

## Design rule

The website can make the weekly report more visual, legible and engaging than the X post, but it must not make the underlying evidence sound more certain than the machine package supports.

## Deployment target

Preferred deployment target: ChatGPT Sites.

The files are deliberately plain HTML, CSS and browser JavaScript so the presentation can be imported or recreated without coupling the framework to a specific frontend stack.
