# Conviction Wallet Intelligence - Cohort v1 bootstrap

Date: 2026-10-01
Parent: #1419
Status: HISTORICAL_RESEARCH_BOOTSTRAP / SHADOW_ONLY / ZERO_PROSPECTIVE_CREDIT

## Purpose
Start the actual evidence dataset for #1419. This is not a ranking and not a trading signal.

## Cohort construction rule
Separate cohorts by access mechanism before comparing wallet behavior:
1. launchpad / bonding-curve launches;
2. organic DEX launches;
3. protocol/project token launches with allocations;
4. bridged/migrated tokens.

A historical winner is eligible when a timestamped source supports >= USD 100m market cap or FDV at some point. Market cap and FDV must be stored separately. Current value must not substitute for historical threshold evidence.

## Bootstrap positive candidates

### FARTCOIN - Solana - launchpad
Mint: `9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump`
Launch date source: 2024-10-18.
Current 2026-10-01 CoinDesk snapshot: ~USD 175.3m market cap and FDV.
Admission: VERIFIED_100M_POSITIVE.
Research task: reconstruct earliest independent buyers, graduation/pool transition, retention through 2x/5x/10x, all subsequent qualifying trades by candidate wallets.

### GOAT - Solana - launchpad
Mint: `CzLSujWBLFsSjncfkh59rUFqvafWcY5tzedWJSuypump`
Launch date: 2024-10-10.
Public historical narrative/evidence sources report an historical peak well above USD 100m; current value is below threshold.
Admission: HISTORICAL_100M_POSITIVE_PENDING_PRIMARY_PRICE_SERIES_CONFIRMATION.
Important identity note: public evidence indicates an anonymous human launched the token and Truth Terminal amplified/adopted the narrative after deployment. Do not classify early wallets as project insiders from narrative association alone.

### AIXBT - Base - Virtuals
CA: `0x4F9Fd6Be4a90f2620860d680c0d4d5Fb53d1A825`
Launch date source: 2024-11-02.
Official AIXBT docs confirm Base CA. Binance listed AIXBT spot on 2025-01-10.
Admission: CANDIDATE_PENDING_VERIFIED_HISTORICAL_100M_THRESHOLD.
Reason retained: useful non-Solana comparison with a different launch/access environment.

### ORBIO - Robinhood Chain - calibration seed, not winner cohort admission yet
CA: `0xAa07A0e9209e16aC99708C3EC70159c6eF3128A3`
Seed wallet: `0xe2eba6a5ddf2c0f1ddec262c466551f18396d43a`
Status: CALIBRATION_ONLY until >=100m threshold is independently verified.
Known hypothesis-generating event: ~36.646m ORBIO acquired for ~0.12 WETH on 2026-08-31, followed by later staking/protocol activity. Preserve transfer-vs-buy and beneficial-ownership ambiguity in subsequent movements.

## Required negative denominator
For every wallet promoted into research:
- collect ALL intentional early token bets in the defined observation window, not only winners;
- exclude dust/airdrops/rewards/LP/MM/router/solver/team allocations;
- preserve failures, rugs, flat outcomes and UNKNOWN;
- compare against venue/time-matched base rate.

## Wallet DNA first-pass schema
`wallet_id`
`chain`
`token_ca`
`launch_ts`
`first_intentional_entry_ts`
`launch_age_seconds`
`entry_value_usd`
`entry_fdv_usd`
`entry_liquidity_usd`
`repeat_buy_count`
`retained_after_2x_pct`
`retained_after_5x_pct`
`retained_after_10x_pct`
`max_interim_drawdown_pct`
`staking_or_locking`
`realized_pnl_usd`
`executable_pnl_usd`
`deployer_overlap`
`funding_overlap`
`router_solver_noise`
`independent_cluster_id`
`provenance_state`
`outcome_state`

## First falsifiable hypotheses
H1: wallets with repeated independent early entries plus high retention after 5x outperform simple earliest-buyer ranking prospectively.
H2: independent multi-wallet convergence adds information beyond the strongest individual wallet.
H3: add-on buying after an initial large mark-up is more informative than passive holding alone.
H4: staking/locking after a large unrealized gain is useful only after team/allocation/protocol-role exclusions.
H5: funding-source overlap loses predictive value after router/solver/exchange infrastructure is correctly classified.

## Immediate execution queue
1. Expand verified winner set to 15-25 cases across at least 3 access environments.
2. Reconstruct FARTCOIN and GOAT earliest-wallet sets with chain-native evidence.
3. Run ORBIO seed-wallet cluster reconstruction as calibration.
4. Build matched negatives from same launch venues and weeks.
5. Only then calculate repeatability and candidate Tier A/B/C.
6. Freeze any live CONVICTION_CLUSTER_DETECTED event before observing its outcome.

No BUY/SELL authority. Historical rows cannot earn prospective credit.
