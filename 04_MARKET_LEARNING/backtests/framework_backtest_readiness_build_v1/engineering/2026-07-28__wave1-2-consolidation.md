# Backtest Wave 1.2 — consolidation, lineage and decision value

```yaml
source_package: DATA_PING_BACKTEST_HISTORY_PACK_20260727T052808Z.zip
source_sha256: 303d63946fd7696237b8d1a7208fa5aadd877e55aba57d5b51ea17aa46d18c9f
final_holdout_start: 2026-04-26
final_holdout_opened: NO
package_scripts_executed: NO
```

## Decision lineage

FNP-001, FT-1 and TD-97 were admitted to the repair ledger as `B_PARTIALLY_RECONSTRUCTABLE`. None has the exact point-in-time state, decision, execution and cost combination required for actual-policy replay.

FT-1 is the highest-priority repair target because its freeze date, policy version, evaluation deadline and expected confirmation cost are already documented.

## Sensor architecture

Thirty-two sensors are assigned to thirteen dependency clusters. The permanent evidence rule is:

> Count dependency clusters, not raw sensor confirmations.

No sensor is deleted. Each sensor receives a primary role, authority class, lifecycle and fallback policy.

## Rotation Architecture v2

Rotation is separated into:

1. ETH relative strength;
2. selective large-cap rotation;
3. broad alt rotation.

A direct ETH/BTC signal can support the first object without proving the second or third. Binance ETH/BTC spot remains the owner. Kraken ETH/XBT and Coinbase ETH-BTC are candidate direct challengers without gate authority until overlap parity is completed. Derived ETH/USD divided by BTC/USD remains diagnostic only.

## PR #188 salvage

The reusable engineering foundation was salvaged and enhanced:

- block bootstraps;
- purged expanding walk-forward;
- FDR control;
- interval and pinball scores;
- effective rank;
- provenance DAG;
- temporal dependency checks;
- decision and counterfactual ledger contracts;
- connected overlap clusters;
- cluster bootstrap confidence intervals;
- sensor registry validation;
- Rotation Architecture v2 classification.

Stale planning and pre-Wave-1 adjudication text was not copied.

```yaml
local_unit_tests: PASS_21_OF_21
```

## Shadow Simplification Tournament

### BTC five-day target

| Stack | Features | OOS R² | Sign accuracy | Mean missingness |
|---|---:|---:|---:|---:|
| Full | 34 | -2.681 | 49.1% | 6.7% |
| Reduced | 19 | -0.958 | 47.2% | 5.5% |
| Minimal | 11 | -0.970 | 45.4% | 2.7% |

The smaller stacks were materially less bad than the full stack, but none demonstrated predictive edge.

### ETH/BTC twenty-day target

| Stack | OOS R² | Sign accuracy |
|---|---:|---:|
| Full | -1.531 | 32.0% |
| Reduced | -2.572 | 28.3% |
| Minimal | -1.937 | 32.5% |

No stack demonstrated linear ETH/BTC forecasting skill.

## Decision

```yaml
FULL_STACK: REFERENCE
REDUCED_EXECUTION_STACK: SHADOW_DUAL_RUN_ACTIVE
MINIMAL_CORE_STACK: EXPERIMENTAL_CHALLENGER
minimum_prospective_shadow_weeks: 12
preferred_prospective_shadow_weeks: 26
sensor_deletions: NONE
actual_policy_replay: BLOCKED_BY_LINEAGE
canonical_state_change: NONE
portfolio_action: NONE
```
