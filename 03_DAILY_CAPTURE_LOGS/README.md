# DAILY CAPTURE ARCHITECTURE v2.2

Status: ACTIVE SHADOW INPUT AFTER MERGE

## Purpose

Build continuous, auditable market sequence memory for weekly calibration without pretending that every source has hourly truth.

The system deliberately separates three complementary lanes:

1. **Hourly Sequence Capture** for data that can be reconstructed faithfully as completed hourly observations.
2. **Live Point-in-Time Anchors** for ephemeral observations that cannot be reconstructed later with the same evidentiary meaning.
3. **Daily Settled ETF Calibration** for slow/session-final flow data that should not be sampled as if it were hourly.

All three lanes are non-binding calibration evidence. They do not replace canonical DATA PING and may not change framework state, model weights, forecasts or portfolio actions.

## Lane A — Hourly Sequence Capture

Production schedule, UTC:

- every hour at `:05 UTC`

The schedule authority is `.github/workflows/hourly-sequence-capture.yml`; this README mirrors that production cadence and must not be treated as a separate schedule owner. UTC is deliberate because the underlying Binance/OKX 1h observations are UTC-aligned. Daylight-saving transitions must not skip or duplicate a source hour.

Each run requests the latest **26 completed hours**. Hourly materialization therefore gives roughly 25 hours of deterministic overlap. Rows are merged by UTC hour, so overlap improves resilience and can self-heal temporary missed runs without duplicating permanent observations.

The owner CSV `timestamp_utc` is the **candle-open timestamp**. A row labelled `14:00Z` represents the completed 14:00-15:00 UTC candle, whose close becomes observable at 15:00Z. Consumers that make prospective forecasts must anchor their forecast clock to the observable close, not to the candle-open label.

Permanent hourly fields include, where source data are available:

- BTC 1h OHLCV, return and intrahour range
- ETH 1h OHLCV, return and intrahour range
- direct ETH/BTC 1h OHLC, return and intrahour range
- BTC and ETH quote volume
- BTC and ETH trade count
- BTC and ETH taker-buy base volume
- BTC and ETH taker-buy quote volume
- deterministic taker-sell quote volume
- BTC and ETH taker-buy quote share
- BTC and ETH open interest and 1h OI change
- BTC and ETH global long/short ratio
- actual funding events, without forward fill
- deterministic price/OI relationship states

The additional spot-flow fields are extracted from the Binance kline payload already being retrieved. They do not require an additional API request.

No interpolation and no forward fill are permitted.

Permanent storage:

`03_DAILY_CAPTURE_LOGS/hourly/YYYY/MM/YYYY-MM-DD.csv`

Each sequence run also writes a compact manifest under:

`03_DAILY_CAPTURE_LOGS/hourly/runs/`

Raw source payloads are retained as GitHub Actions artifacts for 14 days and are not committed as repetitive permanent bulk history.

## Lane B — Live Point-in-Time Anchors

Production schedule, Europe/Copenhagen:

- 02:13
- 06:13
- 10:13
- 14:13
- 18:13
- 22:13

The schedule authority is `.github/workflows/daily-raw-owner-capture.yml`; this README mirrors that production cadence and must not be treated as a separate schedule owner.

The **06:13** anchor is the daily slow-context / cold-lane identity: FRED macro context and CFGI 1d context are collected there in addition to the normal tactical owners. Manual workflow dispatch also enables those slow-context owners. The other scheduled anchors retain the normal 4-hour tactical cadence without pretending slow sources have new observations every four hours.

These captures preserve observations that are difficult or impossible to reconstruct retrospectively with equivalent semantics, including:

- Binance point-in-time order-book depth and trade microstructure
- OKX current swap funding, open interest and mark price
- Top-100 breadth snapshot
- CFGI 4h snapshot when enabled
- FRED macro context once per day at the 06:13 morning anchor
- CFGI 1d context once per day when enabled

Spot hourly candles belong to the Hourly Sequence lane and are not redundantly downloaded by every live anchor.

Permanent storage:

`03_DAILY_CAPTURE_LOGS/captures/`

Raw point-in-time payloads are retained as GitHub Actions artifacts for 14 days.

### Reliability invariant

A successfully collected live anchor is **committed before downstream research materialization**.

A failure in blinded Full-vs-Reduced research, experimentation or another downstream consumer must not cause an otherwise valid breadth/microstructure/derivatives observation to disappear from permanent weekly evidence. Downstream research may degrade independently after the market observation is durably written.

## Lane C — Daily Settled ETF Calibration

Schedule, Europe/Copenhagen:

- 08:05 daily

This lane uses the existing Farside BTC and ETH owner collector but applies a stricter publication-finality gate for weekly calibration:

- retrieve both canonical tables twice;
- wait at least 60 seconds between retrievals;
- require BTC and ETH rows from the same settled session;
- require every issuer/fund cell to be known — no dash/unknown cells;
- require local-total parity;
- require normalized rows to be identical across both retrievals.

This protects the archive from treating a partially published Farside row as final merely because its currently visible numeric cells happen to tie to the displayed total.

Permanent compact storage:

`03_DAILY_CAPTURE_LOGS/etf/`

The two source retrieval bundles remain available as 14-day Actions artifacts.

ETF evidence is settled-daily calibration evidence. It is intentionally **not hourly**.

## Source-appropriate cadence boundaries

Higher sampling frequency is not evidence quality by itself.

Hourly Sequence is materialized hourly because its underlying price, ETH/BTC, spot-flow and derivatives series are genuinely 1h-granular and because prospective 1h research requires a newly completed source candle. That cadence does **not** authorize hourly sampling or synthetic updates for slower sources.

The architecture intentionally does **not** synthesize hourly observations for slower data families:

- CFGI remains on its source-appropriate 4h/daily cadence when enabled and is also available through canonical DATA PING.
- ETF flows are settled daily.
- FRED macro context is slow/daily.
- stablecoin supply, TVL and broader DeFi/liquidity context remain DATA PING/source-cadence inputs rather than fake hourly series.

The hourly lane is optimized for the market path where hourly sequence is genuinely valuable:

`price -> ETH/BTC -> volume/spot demand -> OI/leverage -> persistence/failure`

The live-anchor lane complements that path with:

`breadth -> microstructure -> current derivatives -> sentiment/context`

## Storage policy

The live daily pipeline must not permanently commit repeated full owner payload bundles at every one of the six scheduled live anchors. This avoids repository growth and prevents the monthly raw-storage ceiling from blocking otherwise valid observations.

A bounded permanent cold-lane checkpoint is retained once per day at the 06:13 anchor for the ephemeral owners that cannot be reconstructed later. It excludes large redundant histories. The cold checkpoint may degrade without suppressing the compact market observation; raw source bundles remain available temporarily in Actions artifacts.

Permanent Git history is intentionally compact:

- hourly CSV rows merged by UTC hour
- compact hourly run manifests
- live-anchor compact indexes
- one bounded daily raw checkpoint for ephemeral replay
- settled ETF compact records
- source health and lineage metadata
- weekly enriched calibration artifacts

The hourly schedule increases materialization frequency, not permanent row density: a given UTC source hour is still represented once in the merged daily CSV. Repeated raw source bundles remain temporary 14-day Actions artifacts.

## Weekly calibration bridge

Two weekly builds are intentional.

### Sunday 23:45 Europe/Copenhagen — PRE-CLOSE

Creates a useful near-end-of-week package for Sunday review, while explicitly remaining pre-close.

### Monday 02:25 Europe/Copenhagen — FINAL

Runs after:

- Sunday UTC week close at 24:00 UTC / 02:00 CPH during CEST;
- the first post-close Hourly Sequence materialization at 00:05 UTC, which includes the completed 23:00-24:00 UTC closing candle through the 26-hour overlap window;
- the separate final market-close package scheduled after week completion.

The final build targets the **previous completed ISO week**, not the new Monday week.

The weekly builder reads:

- `03_DAILY_CAPTURE_LOGS/captures`
- `03_DAILY_CAPTURE_LOGS/hourly`
- `03_DAILY_CAPTURE_LOGS/etf`

and writes the normal weekly calibration pack plus two explicit high-value artifacts:

`03_DAILY_CAPTURE_LOGS/weekly/YYYY/Www/WEEKLY_HOURLY_ENRICHED.csv`

`03_DAILY_CAPTURE_LOGS/weekly/YYYY/Www/WEEKLY_SEQUENCE_FACTS.json`

The enriched hourly CSV preserves the full week-level sequence and adds deterministic features including:

- 4h / 12h / 24h / 48h / 72h BTC returns
- 4h / 12h / 24h / 48h / 72h ETH returns
- 4h / 12h / 24h / 48h / 72h ETH/BTC returns
- ETH-minus-BTC relative return over the same horizons
- BTC and ETH OI change over the same horizons
- direct ETH/BTC versus ETH/BTC derived from ETHUSDT/BTCUSDT
- preserved spot-flow and leverage fields

The sequence-facts artifact adds deterministic audit/calibration facts such as:

- expected 168 weekly UTC hours
- observed and missing hours
- exact missing-hour list
- maximum contiguous gap
- per-field completeness
- BTC/ETH/ETHBTC weekly ranges
- Day1–2 actual ranges
- Day3–4 actual ranges
- Day5–7 actual ranges
- settled ETF sequence available for the week
- latest rolling 4/12/24/48/72h features

The weekly builder does not perform market interpretation or forecast scoring by itself.

The weekly pack is an explicit input for:

- RAW weekly calibration
- Forecast Ledger evaluation
- Master Monday preparation
- Specialist weekly review
- Pullback sequence replay

## Authority

All lanes are `SHADOW_OBSERVATION_ONLY` or `SHADOW_CALIBRATION_INPUT_ONLY`.

They may not:

- change framework state
- change model weights
- create portfolio action
- overwrite forecasts
- infer unavailable source data
- interpolate missing observations
- forward-fill unavailable observations
- convert source failure to zero
- turn capture density into market confirmation

## Promotion path

Hourly Sequence Capture, Live Anchor Capture and Daily Settled ETF Calibration run in parallel with canonical DATA PING. Any replacement, promotion or authority change requires separate parity evidence and explicit governance approval.
