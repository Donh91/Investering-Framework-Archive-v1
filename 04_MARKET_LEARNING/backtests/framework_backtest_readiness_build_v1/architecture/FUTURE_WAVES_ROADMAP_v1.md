# Durable Backtest and Framework Research Roadmap

This roadmap preserves recommendations across later threads and waves.

## Wave 1.2 — Consolidation, lineage and decision value

Completed:

- Decision Lineage Repair Ledger;
- Sensor Role & Dependency Registry;
- Rotation Architecture v2;
- PR #188 engineering salvage;
- Shadow Simplification Tournament;
- prospective dual-run contract.

## Wave 1.3 — Authority and lineage recovery

1. Recover FT-1 as the first A-class replayable policy event.
2. Recover FNP-001 original freeze, decision and no-action receipt.
3. Link TD-97 evaluation receipts without turning it into a portfolio event.
4. Validate Kraken ETH/XBT and Coinbase ETH-BTC against Binance across at least 30 settled overlapping sessions.
5. Build the exact point-in-time owner registry for selected ETF, macro and direct-pair gates.

Exit gate:

```yaml
A_class_policy_events: at_least_1
approved_direct_ETHBTC_challenger: at_least_1
owner_registry: FINAL_FOR_SELECTED_TEST
```

## Wave 1.4 — Actual policy replay

Run only after Wave 1.3 passes:

- actual rebuy lock;
- actual new-entry lock;
- actual trim or no-trim decision;
- actual rotation permission;
- connected interval clusters;
- correct costs and drawdown-avoided sign;
- separate BTC, ETH, large-cap and broad-alt policies.

No proxy may be called the actual framework policy.

## Wave 2 — Decision value and nonlinear veto research

- test whether sensors add veto or permit value after price is known;
- nested purged walk-forward;
- interaction models with strict complexity budgets;
- calibration rather than raw direction accuracy;
- failure-path graph analysis;
- cluster-aware evidence counts;
- no final-holdout tuning.

## Wave 2.1 — Prospective scoreboards

- Cycle Navigator: 12-week minimum, 26-week preferred;
- full versus reduced shadow stack;
- range score, interval score, breach timing and state accuracy;
- source-outage resilience;
- payload and runtime reduction;
- no retrospective range tuning.

## Wave 2.2 — Flow and deployment

- ETF price-to-flow versus flow-to-price with publication lags;
- BTC and ETH asymmetry;
- confirmation value versus prediction;
- stablecoin and deployment measures under point-in-time rules;
- missing never becomes zero.

## Wave 3 — Final controlled holdout

Open once only when:

```yaml
final_master_bytes: VERIFIED
owner_registry: FINAL
decision_lineage: SUFFICIENT_A_ROWS
test_contracts: FROZEN
code_and_result_hashes: FROZEN
shadow_tournament: MATURE
readiness_gate_G20: YES
```

## Permanent principles

- fewer sensors can be better, but deletion requires prospective evidence;
- ETH strength is not broad rotation;
- direct gates require direct owner data;
- TDBC remains slow context until independent edge is demonstrated;
- ETF flow remains descriptive or confirmatory until predictive edge is demonstrated;
- raw sensor count is not independent evidence count;
- null and failed tests remain archived;
- backtests never create automatic portfolio actions.
