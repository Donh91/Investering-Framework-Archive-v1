# Research Parallel Lanes reference | Historical event replay source-clock failsafe

**Source-backed methodology** from actual HRE Task2 native GitHub Actions [run 42390995602](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/42390995602), [PR #2010](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2010) and cross-era [run 42391907367](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/42391907367), [PR #2012](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2012).
**Authority:** METHOD_REFERENCE_ONLY. No new agents, paid dispatch, historical prediction truth, market/portfolio promotion, source redistribution or scheduling permission.
**Original research owner:** Task2 #1596. [Complete source/results ledger](../../../research/historical_reality_engine/README.md) (the canonical path from repo root is `research/historical_reality_engine/README.md`).

## What the live data actually revealed

1. **An exchange's raw 1-hour kline `close_time` can be the last trade timestamp inside that hour, not the hour's nominal completion.** Binance source 2020-02 bar opened at 1582110000000 and original source `close_time=1582112132286` (35.5 minutes after open). A February 2021 bar had raw close `1613014854773`. A naive historical replay admitting the candle as soon as this field appears would leak a final future 1h OHLC to an earlier clock. To correctly simulate only completed bars, use open_time + the full interval; require available real observation time where known. This does NOT prove the vendor first published at that exact nominal time.
2. **Real vendor-signed monthly archives can have missing hourly buckets.** In the 2020 Feb+Mar BTC and ETH current Binance source files, each had 1,433 actual 1h rows versus 1,440 expected. Maintain actual missingness, and ABSTAIN for lookback/outcome windows crossing the gaps; do not fill, stitch remote years, or convert missing to quiet.
3. **Time units changed historically.** Binance SPOT source documentation says timestamps from 2025 onward are microseconds; earlier sources are milliseconds. Normalize and adversarially test boundary switching and source raw submillisecond last-trade times.
4. **An archived ZIP hosted today is not proof of original-era first publication.** Repeated source SHA256 may reproduce a price tape but does not establish original live source availability, which is required to credit any actual 2020-2025 historic issued signal. Use retrospective replay truth, not ORIGINAL_ISSUED.
5. **USDT is not silently USD**. Instrument, price venue, delisting availability, provider revisions and source legal rights must be bound.
6. **Retrospective event slices are selected after knowing events.** 72h forward labels taken on consecutive daily cutoffs overlap; low naive warning recall in historical cases is an exploratory baseline, NOT an independent crisis predictor, a 4/5 Official Pullback Risk recommendation, or economic edge. Always match non-event controls and real outcome maturity.
7. **Forecast band coverage alone can be gamed by excessively wide ranges.** Historical 2021 seven-day low/high controls had only two complete eligible Monday freezes per asset. Keep interval width/sharpness and frozen same-clock benchmark, distinguish original weekly CN from simulated 2021 controls.

## Checklist for a historical replay job before and after parallelization

- Record whether source is (a) ORIGINAL_ISSUED with authenticated original publication/delivery, (b) FROZEN_RETROSPECTIVE of a fixed modern model on older public market truth, or (c) CHALLENGER_DEVELOPMENT learned post-event.
- Freeze model/script/head and research hypothesis before outcome inspection; pin revision SHA256, venue and asset identity, producer source provider documented timestamp units and the earliest *correct* completed-bar clock.
- Preserve distinct `market_event_at`, `bar_open_at`, `bar_nominal_end_at`, `provider_first_known_at`, `collector_observed_at`, `forecast_issued_at`, `user_delivered_at` and `outcome_matured_at` as applicable, with null/UNKNOWN not invented.
- Validate actual source SHA checksum, ZIP path/sizes, finite OHLC, duplicates, monotonicity, actual missing intervals, quote parity, immutable historical universe and official ETF/source availability by era. No source URL/README is code execution authority.
- Admit only fully completed historic candles and legal observation vintages before the decision cutoff. Any missing lookback/target period becomes an explicitly counted abstention. Embargo overlapping labels and block dependent event families.
- Score real original issued predictions separately from retrospective current-model simulations and from post-hoc challengers. Keep naive price-only, always-HOLD, quiet false-alarm and realistic after-cost baselines.
- Parallel independent GitHub Actions jobs may share a source manifest but must have separate source-correct receipts/job IDs. No job may consume another's post-outcome labels as input before clock maturity.
- Route material reproducible repair under original owner to existing Codex/PR/CI/S1. A research report is not a code release. Negative results must be retained and scanned for true next dependency.
- If a method repeatedly fails due to the same source-clock issue and a skill would measurably reduce the error, create a new candidate and evaluate with skill-quality-gate before any registry promotion.

**Actual executable example:** `scripts/research/hre_native_replay_pilot_v1.py` with tests `tests/research/test_hre_native_replay_pilot_v1.py`; run outputs are native and research-only, not a current market signal.
