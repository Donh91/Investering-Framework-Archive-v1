# OKX Futures Archive Package

This package is designed for two uses:

1. attach a verified OKX data bundle to the main analysis thread;
2. maintain a reproducible GitHub archive for historical analysis and backtests.

## What is embedded now

The ZIP contains a verified Action-runtime seed sample:

- BTC-USDT-SWAP: 100 consecutive 1H swap candles;
- ETH-USDT-SWAP: 100 consecutive 1H swap candles;
- raw JSON and normalized CSV;
- zero duplicate timestamps;
- zero hourly gaps;
- one current partial candle (`confirm=0`) per instrument.

The seed sample proves field order, continuity and normalization against the installed OKX v1.3 Action.

## What the included exporter fetches

Run:

```bash
python scripts/fetch_okx_archive.py \
  --out data/okx_$(date -u +%Y%m%dT%H%M%SZ) \
  --days 30 \
  --extended
```

The exporter downloads, normalizes and validates:

- BTC and ETH swap OHLCV candles, 1H, 30 days;
- mark-price candles, 1H, 30 days;
- index candles, 1H, 30 days;
- open-interest history, 1H, 60 days with `--extended`;
- funding settlements, 90 days with `--extended`;
- long/short account ratio, 1H, 30 days;
- contract taker-volume, 1H, 30 days;
- current instrument, ticker, mark, index, funding and OI snapshots;
- aligned BTC and ETH 30-day hourly CSV files;
- raw API pages, normalized CSV, manifest, validation report and checksums.

## Data labels

### Open interest

`OKX_ONLY / VENUE_SPECIFIC / DO_NOT_SUM_ABSOLUTE_OI_ACROSS_VENUES`

Use within-venue changes and direction. Do not sum absolute OI across exchanges.

### Long/short account ratio

`ACCOUNT_COUNT_RATIO / NOT_POSITION_SIZE_RATIO / NOT_MARKET_WIDE_POSITIONING`

### Contract taker-volume

`OKX_ONLY / VENUE_SPECIFIC / NOT_MARKET_WIDE_CVD / RAW_LEG_ORDER_PRESERVED`

The exporter intentionally preserves `volume_leg_1` and `volume_leg_2`. It does not assign buy/sell semantics unless separately verified from a current authoritative response.

## Backtest hygiene

- Use only rows that were available at the simulated decision timestamp.
- Treat `confirm=0` candles as partial and exclude them from close-based backtests.
- Preserve source timestamps and retrieval timestamps.
- Avoid lookahead when joining funding settlements and hourly candles.
- Use UTC as the canonical storage timezone.
- Keep raw API pages immutable.
- Recompute normalized files from raw data when normalization logic changes.
- Record the package SHA-256 in the analysis log.

## Network requirement

The included exporter requires an internet-enabled environment. This ChatGPT artifact runtime cannot make arbitrary outbound HTTP requests, so the ZIP embeds the Action-verified seed and a deterministic exporter for the complete archive. No missing historical rows have been fabricated.

## Governance

This is a verified-input archive. It contains no trading advice, portfolio decision, framework state, recovery confirmation, rotation confirmation or rebuy conclusion.
