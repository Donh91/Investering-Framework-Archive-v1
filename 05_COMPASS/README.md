# 05_COMPASS — Action Compass

**Status:** OPERATIONAL_DERIVATIVE  
**Authority:** NAVIGATION_ONLY / NO_PORTFOLIO_EXECUTION_AUTHORITY  
**Canonical binding:** `../00_ARCHIVE_CONTROL/2026-09-16__action-compass-operational-binding-v1__canonical.md`

## Purpose

Action Compass (`COMPASS` / `KOMPAS` / former Handlekompas action posture) is the framework's frozen daily tactical navigation artifact.

It answers, at a known point in time:

- what the market state looked like **now**;
- what direction the evidence supported for the **next 12 hours**;
- what direction/action posture the evidence supported for **1–3 days**;
- what direction/action posture the evidence supported for **5–7 days**;
- where BTC, ETH, large caps, midcaps, small caps and microcaps sat in the deployment/rotation ladder;
- what had to happen for each ladder segment to advance or invalidate;
- exactly which evidence was available when the call was frozen.

The daily freeze is deliberately immutable. Later outcomes are stored separately. This makes Compass a prospective decision-history dataset rather than a narrative that can be rewritten after the fact.

## Position in the machine

```text
current autonomous collectors + governed machine outputs
                    |
                    v
              ACTION COMPASS
        daily frozen tactical derivative
           /          |           \
          v           v            v
   user action     CN context    outcome scoring
   navigation      / website      + learning
```

Compass is **not** a new market-state engine. It derives from current eligible machine evidence and current market observations. It cannot rewrite Master Monday, a frozen Cycle Navigator issue, model weights, thresholds or portfolio execution state.

Cycle Navigator remains the slower weekly strategic forecast/accountability product. Compass is the faster daily tactical layer. A disagreement between them is preserved as `cn_alignment` instead of silently forcing one to match the other.

## Canonical interfaces

Current pointer:

`05_COMPASS/LATEST_COMPASS.json`

Immutable daily freezes:

`05_COMPASS/daily/YYYY/MM/YYYY-MM-DD__DAILY_COMPASS.json`

Optional event freezes:

`05_COMPASS/events/YYYY/MM/<timestamp>__EVENT_COMPASS.json`

Outcome records:

`05_COMPASS/outcomes/YYYY/MM/<freeze-id>__H12.json`  
`05_COMPASS/outcomes/YYYY/MM/<freeze-id>__H72.json`  
`05_COMPASS/outcomes/YYYY/MM/<freeze-id>__H168.json`

Schema:

`05_COMPASS/schema/COMPASS_SCHEMA_V1.json`

## Horizon contract

Every eligible freeze exposes the same four views:

| Horizon | Meaning |
|---|---|
| `NOW` | current market/action posture |
| `H12` | next 12 hours |
| `D1_3` | next 1–3 days |
| `D5_7` | next 5–7 days |

Directional vocabulary is fixed to `BULLISH`, `NEUTRAL` or `BEARISH`. Action vocabulary is fixed to `HOLD`, `WAIT`, `PREPARE`, `DEPLOY` or `DE_RISK`.

`DEPLOY` is intentionally hard to reach. The deterministic v1 compiler will not infer broad deployment from price alone; missing breadth/transmission evidence keeps smaller-cap ladders fail-closed.

## Capitalization ladder

The ladder is always emitted in this order:

```text
BTC -> ETH -> LARGE_CAP -> MID_CAP -> SMALL_CAP -> MICRO_CAP
```

Every rung carries:

- `status`;
- `eta`;
- `why`;
- `trigger`;
- `invalidation`.

This is also the canonical compact answer to the framework's altcoin-status question. A separate duplicate altcoin narrative is not required when the ladder is present.

## Evidence breadth and the “100 datapoints” rule

Compass does not fabricate an exact 100-point packet. Instead each freeze stores the scalar observations actually available from eligible sources and reports:

- `observed_scalar_points`;
- `minimum_breadth_target: 100`;
- whether that target was met;
- expected and available source families;
- missing source families;
- a SHA-256 over the frozen evidence-point keys.

This lets later research cross-measure a call against a broad contemporaneous evidence set while preserving missing data as missing data. More than 100 valid observations is allowed; fewer than 100 is recorded as degraded evidence breadth, never silently padded.

## Prospective scoring

The daily workflow scores matured freezes separately at approximately:

- `+12h` (`H12`);
- `+72h` (`H72` / 1–3 day endpoint);
- `+168h` (`H168` / 5–7 day endpoint).

The scorer resolves market prices at the original maturity timestamp from historical candles, so a daily scoring job does not need to run at the exact maturity minute. Forecast freezes are never edited to add outcomes.

Direction scoring v1 is deliberately simple and pre-registered: realized BTC/ETH market-return proxy above +1% = `BULLISH`, below -1% = `BEARISH`, otherwise `NEUTRAL`. Exact directional match scores 100; a neutral-versus-directional near miss scores 50; opposite direction scores 0. ETH/BTC realization is stored separately for rotation learning.

Capitalization-ladder performance is preserved for later richer scoring only when segment-level outcome data is actually available. The v1 scorer must not invent small/microcap outcomes from BTC/ETH proxies.

## Daily cadence

`.github/workflows/action-compass-daily.yml` runs once daily at `06:45 UTC` and can also be dispatched manually. It:

1. checks out current `main`;
2. builds one immutable daily freeze if that date does not already exist;
3. updates `LATEST_COMPASS.json`;
4. scores all matured unscored H12/H72/H168 horizons using historical observations;
5. validates the contract;
6. commits machine artifacts back to `main` only when something changed.

The implementation is deterministic Python + public/read-only market endpoints. No LLM/API spend is required for routine daily generation.

## Website / Cycle Navigator boundary

The Cycle Navigator public build may mechanically ingest the public-safe subset of `LATEST_COMPASS.json` and its exact target freeze. Compass may power a distinct **current Compass** surface or short-horizon context.

It must never silently rewrite:

- the weekly CN forecast freeze;
- the weekly CN scorecard;
- historical public CN claims;
- null/unsupported weekly ranges.

## Fail-closed rules

- A daily freeze path is immutable once created.
- Missing source data remains missing.
- Missing breadth/transmission evidence cannot be promoted into a broad altseason/deployment claim.
- The pointer may move; a freeze may not.
- Outcome files are append-only per freeze/horizon.
- No Compass artifact grants trade execution authority.
