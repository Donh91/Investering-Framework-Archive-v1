# DAILY CAPTURE ARCHITECTURE v2

Status: ACTIVE SHADOW INPUT AFTER MERGE

## Purpose

Build continuous sequence memory without losing point-in-time market evidence.

The daily data system is split into two complementary lanes:

1. Hourly Sequence Capture, for sources that can be reconstructed as completed hourly observations.
2. Live Anchor Capture, for ephemeral or point-in-time sources that cannot be reconstructed faithfully later.

Neither lane is a canonical DATA PING and neither lane may change framework state, model weights or portfolio actions.

## Lane A, Hourly Sequence Capture

Schedule, Europe/Copenhagen:

- 11:55
- 23:55

Each run requests the latest 14 completed hours. The intended 12-hour coverage therefore has a two-hour overlap between runs. Rows are merged deterministically by UTC hour, so overlap increases resilience without creating duplicate observations.

Permanent hourly fields include, where sources are available:

- BTC 1h OHLCV, return and intrahour range
- ETH 1h OHLCV, return and intrahour range
- ETH/BTC 1h OHLC, return and intrahour range
- BTC and ETH open interest and 1h OI change
- BTC and ETH global long/short ratio
- actual funding events, without forward fill
- deterministic price/OI relationship states

No interpolation and no forward fill are permitted.

Permanent storage:

`03_DAILY_CAPTURE_LOGS/hourly/YYYY/MM/YYYY-MM-DD.csv`

Each sequence run also writes a compact manifest under:

`03_DAILY_CAPTURE_LOGS/hourly/runs/`

Raw source payloads are retained as GitHub Actions artifacts for 14 days and are not committed as repetitive permanent bulk history.

## Lane B, Live Point-in-Time Anchors

Schedule, Europe/Copenhagen:

- 06:13
- 10:47
- 15:22
- 19:38
- 23:11

These captures preserve data that is difficult or impossible to reconstruct retrospectively, including:

- Binance point-in-time order-book depth and trade microstructure
- OKX current swap funding, open interest and mark price
- Top-100 breadth snapshot
- CFGI 4h snapshot when enabled
- FRED macro context once per day at the morning anchor
- CFGI 1d context once per day when enabled

Spot hourly candles are no longer redundantly downloaded on every live anchor. They belong to the hourly sequence lane.

Permanent storage:

`03_DAILY_CAPTURE_LOGS/captures/`

Raw point-in-time payloads are retained as GitHub Actions artifacts for 14 days.

## Storage policy

The live daily pipeline must not permanently commit repeated full owner payload bundles five times per day. This avoids repository growth and prevents the monthly raw-storage ceiling from blocking otherwise valid observations.

A bounded permanent cold-lane checkpoint is retained once per day at the morning anchor for the ephemeral owners that cannot be reconstructed later. It excludes the large FRED history and redundant spot-candle history. The cold checkpoint has its own storage ceiling and is allowed to degrade without suppressing the compact market observation. If the cold checkpoint reaches its ceiling, the live anchor still commits and the raw source bundle remains available in the 14-day Actions artifact.

Permanent Git history is intentionally compact:

- hourly CSV rows
- hourly run manifests
- live-anchor compact indexes
- one bounded daily raw checkpoint for ephemeral source replay
- source health and lineage metadata embedded in the compact records
- weekly sequence/calibration packs

All five live-anchor raw bundles and both hourly source bundles remain available temporarily through Actions artifacts for debugging and readback.

## Authority

Both lanes are `SHADOW_OBSERVATION_ONLY` / non-binding evidence.

They may not:

- change framework state
- change model weights
- create portfolio action
- overwrite forecasts
- infer missing data
- interpolate missing observations
- forward-fill unavailable data
- convert source failure to zero

Capture density is evidence density, not market confirmation.

## Weekly bridge

Every Sunday at 23:45 Europe/Copenhagen, the weekly builder reads both:

- `03_DAILY_CAPTURE_LOGS/captures`
- `03_DAILY_CAPTURE_LOGS/hourly`

and produces:

`03_DAILY_CAPTURE_LOGS/weekly/LATEST_WEEKLY_CALIBRATION.json`

The weekly pack now includes deterministic sequence evidence such as:

- hourly coverage versus the 168 expected weekly hours
- spot completeness
- OI completeness
- long/short completeness
- BTC and ETH up/down hour counts
- largest hourly move and range expansion
- price/OI state counts
- ETH/BTC up/down hour counts

It does not perform market interpretation or forecast scoring by itself.

The pointed weekly pack is an explicit input for:

- RAW weekly calibration
- Forecast Ledger evaluation
- Master Monday preparation
- Specialist weekly review
- Pullback sequence replay

## Promotion path

Hourly Sequence Capture and Live Anchor Capture run in parallel with canonical DATA PING. Replacement or promotion requires separate parity evidence and explicit governance approval.
