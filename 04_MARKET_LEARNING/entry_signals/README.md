# Entry Signal Ledger v1

Purpose: automatically timestamp the framework's observable graduated altcoin top-up state and later measure whether those signals were useful.

This layer is a learning/audit surface only. It does not execute trades, change framework rules, alter thresholds, or create canonical market state.

## Automatic state observation

Every hourly GitHub run reads fresh repository breadth plus direct ETHBTC/BTC/ETH prices and evaluates only the already-used observable conditions:

- ETHBTC > 0.0300
- Top100 proxy breadth >= 50%
- ETH 24h return > BTC 24h return

All three true => `GRADUATED_ALTCOIN_TOPUP_ACTIVE`.
Otherwise => `WAIT`.

The 50% breadth value and 0.0300 ETHBTC level are recorded as existing framework decision references, not newly optimized parameters. No parameter sweep is allowed in this engine.

## Files

- `LATEST.json`: current machine-readable status and a one-line DATA PING bridge summary.
- `STATE.json`: previous/current state used for transition detection.
- `events/*.json`: immutable activation/deactivation transitions with timestamp and source data.
- `outcomes/*.json`: automatically matured +24h, +72h, +7d, +14d and +30d outcomes.

Outcome rows measure BTC, ETH, ETHBTC and a matched-constituent Top100 equal-weight return where baseline constituent prices are available.

## Execution temperature

`HOT` is descriptive only. It never activates or deactivates the signal and therefore cannot silently modify framework semantics. It exists to distinguish signal validity from entry-quality/chase risk.

## Main-thread/Data Ping use

When a main-thread analysis or DATA PING asks for entry/top-up status, read `04_MARKET_LEARNING/entry_signals/LATEST.json` alongside the normal framework evidence. The field `data_ping_bridge.display_line` is designed for direct inclusion in a compact DATA PING conclusion.

## Historical first event

The first event is seeded from the first accepted 2026-08-20 packet on which the main thread explicitly changed its conclusion to `FIRST GRADUATED ALTCOIN TOP-UP WINDOW: ACTIVE`. The event time is anchored to that accepted packet (`2026-08-20T05:22:15Z`), not a fabricated chat-message timestamp.
