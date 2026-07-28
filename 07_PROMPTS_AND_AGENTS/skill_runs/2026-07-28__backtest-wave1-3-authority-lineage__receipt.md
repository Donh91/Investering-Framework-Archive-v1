# Skill-run receipt — Backtest Wave 1.3

```yaml
program: FRAMEWORK_BACKTEST_READINESS_BUILD_v1
wave: BACKTEST_WAVE_1_3
run_date: 2026-07-28
run_type: AUTHORITY_AND_LINEAGE_RECOVERY
branch: agent/backtest-wave1-3-authority-lineage-20260728
```

## Completed

- reconstructed FT-1 rule lineage without inventing execution evidence;
- quarantined FNP-001 from actual-policy replay because it was frozen after its horizon;
- retained TD-97 in the forward-claim ledger with no action authority;
- froze direct ETH/BTC challenger acceptance criteria;
- validated Coinbase ETH-BTC and Kraken ETH/XBT against Binance ETHBTC;
- approved Coinbase as direct outage-confirmation challenger;
- retained Kraken as conditional direct shadow;
- froze selected owner registry;
- ratified prospective decision receipt contract;
- added authority and lineage validators plus six passing tests.

## Source scope

Venue parity used settled UTC daily rows from the byte-visible Binance, Coinbase and Kraken files in the supplied backtest history pack. Full parity rows remain in the external result package; compact metrics and decisions are archived here.

## Explicit non-actions

- no historical A-class event fabricated;
- no actual policy replay;
- no owner replacement;
- no derived ETH/BTC gate authority;
- no final holdout access;
- no framework-state or portfolio change.

```yaml
result_package: BACKTEST_WAVE1_3_AUTHORITY_LINEAGE_20260728.zip
result_package_sha256: 9387dc171f2cb46e56a0aa1bf6ce502aac8c4be0f806892407eb7f3f40068e6b
local_engineering_tests: PASS_6_OF_6
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
canonical_state_change: NONE
portfolio_action: NONE
```