# TechDev Deferred Low-Value Research Lanes

**Date:** 2026-07-11  
**Status:** DEFERRED_BY_VALUE / USER_PRIORITY_CONFIRMED  
**Scope:** Step 3 requested by the user

## Decision

The following lanes are deliberately not executed now:

```yaml
author_reported_mechanical_system_reconstruction: DEFERRED
exhaustive_small_altcoin_target_scoring: DEFERRED
meme_and_microcap_target_backfill: DEFERRED
all_historical_trade_reproduction: DEFERRED
```

This is not a source gap. The archive remains preserved. The decision is a marginal-value choice after the complete-corpus audit.

## Why the mechanical-system lane is deferred

A valid reconstruction would require:

- exact versioned rules for every RSI/MACD, dots/trackline and later system change;
- exact instrument and executable close convention;
- transaction costs, slippage and taxes;
- leveraged ETF path dependency where relevant;
- separation of mechanical exits from later discretionary overrides;
- independent reproduction of author-reported backtests.

Without those inputs, a result would create false precision.

## Why exhaustive minor-alt scoring is deferred

A valid asset-by-asset audit would require:

- complete historical OHLC for each token;
- token migrations, redenominations and delistings;
- circulating-supply history for market-cap-adjusted targets;
- liquidity and executable-venue checks;
- project death and survivorship-bias treatment;
- exact target revision lineage.

The expected decision value is lower than macro, rotation, risk and forward calibration.

## Reopen conditions

```text
MECHANICAL_SYSTEMS:
Reopen only when an exact versioned specification and full executable price series exist,
or when the system is proposed for live framework use.

MINOR_ALT_TARGETS:
Reopen only for assets that materially affect the user's portfolio,
or for a representative pre-registered sample designed to test target methodology.

HISTORICAL_TRADES:
Reopen only when entry, stop, exit rule, instrument and adjusted price series are complete.
```

## Binding consequence

```text
DEFERRED_DOES_NOT_MEAN_VALIDATED
DEFERRED_DOES_NOT_MEAN_REJECTED
NO_EXECUTION_AUTHORITY_GRANTED
ARCHIVE_PRESERVATION_CONTINUES
```
