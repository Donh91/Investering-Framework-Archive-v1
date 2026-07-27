# MASTER MONDAY 2026-W31 — DATA PING DERIVED RAW

run_id: MASTER_MONDAY_W31_20260727T174239Z
status: DATA_PING_DERIVED_RECOVERY
source_resolution: ACCEPTED_MULTI_RUN_EVIDENCE_CHAIN
primary_current_run: run_586b93af2ad54a49b13f7453e7ea40e2
latest_longitudinal_run: run_b43a7f8d213c4e63a5e60ca9cb19d764
latest_ota_observation_utc: 2026-07-27T17:28:59Z
data_quality: MEDIUM_LOW_CURRENT__MEDIUM_HIGH_SETTLED_WEEK

## Settled W30 actuals

- BTC weekly low/high: 63,100.00 / 66,956.15 USDT.
- ETH weekly low/high: 1,843.14 / 1,956.45 USDT.
- BTC first-three-day low/high: 63,100.00 / 66,956.15 USDT.
- ETH first-three-day low/high: 1,843.14 / 1,956.45 USDT.
- 26 July CEST settled closes used in the H7 sequence: BTC 64,858.02, ETH 1,925.91 and direct ETH/BTC 0.02969.
- Direct ETH/BTC did not produce a settled close above 0.0300 during the scored F4 window.

## Current Monday chain

### Morning direct-feed state — 07:02:46Z

- Binance BTCUSDT: 65,396.00, +1.487% over 24h.
- Binance ETHUSDT: 1,966.82, +4.316% over 24h.
- Direct Binance ETHBTC: 0.03009, live touch above 0.0300, not settled.
- Breadth: 58.43% advancers, median +0.30%.
- Latest settled ETF flows: BTC -240.1M and ETH -70.7M USD.

### Afternoon update — 14:39:04Z

- CoinGecko BTC: 64,988; ETH: 1,948.67; derived ETH/BTC: 0.0299851.
- Breadth fell to 37.50% advancers.
- OKX BTC last: 64,932.6; ETH last: 1,936.11.
- Binance direct and derived feature families unavailable under geo restriction.

### Evening update — 17:10:00Z

- CoinGecko BTC: 64,835; ETH: 1,938.14; derived ETH/BTC: 0.0298934.
- OKX BTC last: 64,800.00; ETH last: 1,935.64.
- Breadth fell to 23.86% advancers, median return -0.60%.
- OKX BTC OI USD rose 0.95% from the prior update; ETH OI USD fell 3.36%.
- Total market cap fell 0.74% while reported 24h volume rose 8.38% versus the prior update.

### OTA24 — 17:28:59Z

- BTC 27 July in-progress: approximately 65,000.01, with intraday low 64,418.01.
- Direct ETH/BTC 27 July in-progress high: 0.03020; observed running value approximately 0.02988.
- 26 July UTC session touched 0.03000 intraday and settled below at 0.02989.
- 27 July remained in progress and cannot be classified as a settled rejection.

## Deterministic derived state

```yaml
weekly_repair_survived: YES
eth_relative_transmission_candidate: YES_BUT_FOLLOW_THROUGH_WEAKENED
breadth_confirmation: NO
etf_flow_confirmation: NO
settled_0_0300_confirmation: NO
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_cap_window: WATCH_ONLY_NOT_OPEN
portfolio_action: NONE
```

## Experiment state

- H7: `EARLY_TRANSMISSION_CANDIDATE_NOT_ROTATION_CONFIRMATION`; no rescore.
- H7 row 6: pending settlement at 2026-07-27T22:00:00Z.
- F1: `NO_FAILURE_OBSERVED_TO_DATE`; final score withheld until 2026-07-28T00:00:00Z.
- F4: `GATE_UNMET`, closed and not reopened.
- F5: `TRIGGERED`, not retriggered.
- Low-vol 5D: not matured at run time.

This file contains source-resolved operational evidence. Final interpretation belongs to `03_framework_ratified_final.md`.