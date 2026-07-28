# Skill-run receipt — Backtest Wave 1.1

```yaml
program: FRAMEWORK_BACKTEST_READINESS_BUILD_v1
run_date: 2026-07-28
wave: 1.1
branch: agent/backtest-wave1-1-chatgpt-20260728
execution_owner: CHATGPT_CONTROLLED_ENGINE
```

## Executed tests

1. Owner-policy replay readiness audit.
2. Leave-one-cycle-out halving-orthogonalized TDBC under bar-end authority.
3. Episode-level landmark drawdown-hazard evaluation with leave-one-episode-out predictions.
4. Prior-day-membership top-50 alt basket with lagged beta hedge and direct ETH/BTC event gates.
5. One-day-lagged, horizon-purged expanding walk-forward for BTC 5D and ETH/BTC 20D targets.

## Controls

- no source-package script executed;
- direct ETH/BTC used for rotation events;
- alt membership selected from prior-day quote volume;
- target horizons purged from train/test boundaries;
- final 90-day holdout beginning 2026-04-26 excluded and not scored;
- 2010 pre-halving TDBC event excluded from halving matching;
- 2026 TDBC event excluded as unmatured;
- actual owner-policy replay stopped rather than replaced by a proxy.

## Result package

```yaml
name: BACKTEST_WAVE1_1_CHATGPT_20260728.zip
bytes: 93727
sha256: acab2178a861b975dfedc3b2ed43607025b0cf848030eb0e1027ca5e765d2863
artifacts: 16
```

## Non-actions

- no owner policy was fabricated;
- no final holdout was opened;
- no threshold optimization;
- no TDBC promotion;
- no drawdown-hazard implementation;
- no broad-rotation declaration;
- no ETF predictive promotion;
- no canonical state change;
- no portfolio action.

```yaml
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
canonical_state_change: NONE
portfolio_action: NONE
```
