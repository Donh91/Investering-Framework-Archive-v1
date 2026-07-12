# Full Sensor-Level Simulation & Backtest v1

**Dato:** 2026-07-12  
**Status:** CANONICAL  
**Evidence class:** CANONICAL_RESEARCH_EVIDENCE  
**Område:** market learning / full sensor backtest / signal-role governance  
**Primary folder:** `04_MARKET_LEARNING/full_backtests/`  
**Related folders:** `01_CORE_FRAMEWORK/governance/`, `03_WEEKLY_OPERATIONS/shadow_ledger/`, `04_MARKET_LEARNING/truth_layer/`, `04_MARKET_LEARNING/shadow_protocols/`  
**Depends on:** `04_MARKET_LEARNING/truth_layer/DATA_COMPLETION_CONTROL_STATE.json`, `01_CORE_FRAMEWORK/governance/2026-07-12__btc-d-and-stablecoin-role-freeze-v1__canonical.md`, `04_MARKET_LEARNING/shadow_protocols/2026-07-12__transmission-matrix-forward-falsification-protocol-v0-1__canonical.md`  
**Index route:** `00_ARCHIVE_CONTROL/2026-07-12__index-addendum-full-sensor-simulation-backtest-v1.md`  
**Source package SHA-256:** `75e4a4635e390b955cb3b1531cfd004cc2eda9180cb8706e318e69765af26198`  
**Simulation package SHA-256:** `d75eb50829a4d9be51240e8fcf04930a85e85d455e23c6855e45718c67b83c5d`

## Archive decision

```yaml
classification: EXISTING_OWNER_UPDATE
primary_owner: 04_MARKET_LEARNING/full_backtests/2026-07-12__full-sensor-simulation-backtest-v1__canonical.md
durable_unit:
  - completed sensor-level backtest
  - negative evidence blocking unsupported promotion
  - retained shadow-only roles
  - full-portfolio identifiability boundary
  - forward-falsification continuation path
duplicate_policy: NO_PARALLEL_CANONICAL_DOCUMENT
canonical_index_change: NO
indexing_method: EXISTING_INDEX_ADDENDUM
```

The conversational explanation is not archived verbatim. This owner file preserves the durable learning and governance consequence.

## Scope

The run combines:

- CMC direct-source BTC dominance;
- BTC daily price;
- ETH/BTC daily close;
- DeFiLlama stablecoin supply and DEX volume;
- M1 pullback-weather rows;
- M4 rotation-survival attempts and episodes.

This is a full **sensor-level** simulation. It is not a fabricated full portfolio backtest.

## Final verdict

```text
FULL_SENSOR_LEVEL_BACKTEST: COMPLETE
FULL_PORTFOLIO_BACKTEST: NOT_IDENTIFIABLE_FROM_AVAILABLE_DATA
M1_B1_EARLY_WARNING_EDGE: NOT_SUPPORTED
M1_B1_PROTECTIVE_TRIM_SIMULATION: NOT_SUPPORTED
M4_SINGLE_EPISODE_JOINT_SIGNATURE: DOES_NOT_GENERALIZE
STABLECOIN_DEPLOYMENT_CONTEXT: DESCRIPTIVE_AND_POTENTIALLY_USEFUL
STABLECOIN_DEPLOYMENT_STANDALONE_PREDICTOR: NOT_SUPPORTED
BTC_D_ROTATION_SURVIVAL_VETO: PLAUSIBLE_SHADOW_ROLE_ONLY
HISTORICAL_BREADTH_BLOCKER: REMAINS
RULE_PROMOTION: NONE
```

## Source and convention boundary

```text
BTC.D provider: CoinMarketCap
BTC.D convention: CMC_DIRECT_SOURCE_CONVENTION
TradingView CRYPTOCAP equivalence: NO
Stablecoin proxy: STABLECOIN_DEPLOYMENT_PROXY
Velocity claim allowed: NO
```

The CMC series may be used only under its declared provider convention. It must not be silently relabelled as TradingView `CRYPTOCAP:BTC.D` or granted denominator-equivalent threshold authority.

## M1 B1 result

The BTC-return simulation covers 2025-03-01 through 2026-07-02 and contains 21 B1 fires with price follow-through.

Ten days after a B1 fire:

- median BTC return: `+2.7401%`;
- mean BTC return: `+2.0500%`;
- negative-return rate: `28.5714%`;
- observed mean return: `96.55th percentile` versus 10,000 random-date samples.

Every tested 10-bps protective-exposure variant underperformed BTC buy-and-hold on terminal return.

Least damaging variant:

```text
25% reduction for 1 day
strategy return: -29.5136%
buy-and-hold return: -28.5225%
relative loss: -0.9911pp
drawdown difference: -0.9426pp
```

Best drawdown variant:

```text
25% reduction for 14 days
drawdown improvement: +0.5256pp
relative return loss: -1.3723pp
```

B1 therefore behaves more like a contemporaneous/post-stress dominance condition than a mechanical early trim signal.

## M4 transmission result

The broader weekly non-overlapping test rejects generalization of the one successful July 2025 episode.

For `FALLING_EXPANDING_NO_RECENT_RECLAIM`:

| Horizon | N | Median ETH/BTC return | Positive rate |
|---:|---:|---:|---:|
| 7d | 18 | -1.4129% | 16.67% |
| 14d | 18 | -3.3583% | 27.78% |
| 30d | 18 | -7.9761% | 22.22% |

The single real M4 episode remains genuine but is not a general rule.

## Stablecoin strategy result

A three-day-persistent `EXPANDING_DEPLOYMENT` shadow exposure returned `+17.5447%` after 10-bps switching costs, but the result is regime-dependent:

```text
2024: +16.9533%
2025: +10.0270%
2026 YTD: -8.6535%
```

The top five positive days contributed 38.18 arithmetic return points against a total arithmetic return sum of 21.53 points. The result is tail-concentrated, not broad predictive consistency.

## Robustness attack

108 nearby transmission configurations were tested without promoting a best row:

```text
positive full-sample: 89 / 108
positive in both 2024–2025 train and 2026 test: 3 / 108
```

The three apparent survivors had only 0.61% exposure and two switches in 2026, making their test success economically trivial.

## Canonical role consequence

```text
BTC.D B1 early-warning weight: 0
BTC.D standalone action authority: 0
BTC.D rotation-survival context: RETAIN_SHADOW
Stablecoin deployment standalone action authority: 0
Stablecoin deployment transmission context: RETAIN_SHADOW
Joint transmission signature: FORWARD_FALSIFICATION_ONLY
```

This role freeze is owned by:

```text
01_CORE_FRAMEWORK/governance/2026-07-12__btc-d-and-stablecoin-role-freeze-v1__canonical.md
```

Prospective continuation is owned by:

```text
04_MARKET_LEARNING/shadow_protocols/2026-07-12__transmission-matrix-forward-falsification-protocol-v0-1__canonical.md
03_WEEKLY_OPERATIONS/shadow_ledger/TRANSMISSION_MATRIX_FORWARD_LOG_v0_1.csv
```

## Full portfolio boundary

A defensible portfolio replay still requires frozen historical:

- breadth and universe membership;
- holdings and weights;
- action-to-size mapping;
- liquidity and transaction-cost assumptions by tier;
- rebuy and exit execution rules;
- broader source-backed M3 decisions.

A present-day reconstruction of those missing inputs would create false precision and is rejected.

## Backup and recovery

The original canonical research subset is preserved in the independent Vault as a targeted research snapshot:

```yaml
backup_product: TARGETED_SNAPSHOT
snapshot_root: snapshots/2026-07-12-full-sensor-backtest/source-tree/
manifest: manifests/2026-07-12__full-sensor-backtest-targeted-snapshot-manifest.md
receipt: receipts/2026-07-12__full-sensor-backtest-targeted-snapshot-receipt.json
snapshot_frozen_source_sha: 732a21f41d0292b3156451574f5d7b759ce3a97d
result: PASS_TARGETED_RESEARCH_SNAPSHOT
paths_verified: 11/11
research_package_backup: PASS
owner_upgrade_merge_sha: ba40c6cb70121f6e3291ff882f8bd73a13386f9a
current_owner_version_in_snapshot: NO
skill_run_receipt_in_snapshot: NO
post_merge_delta_status: PENDING
full_git_mirror_status: NOT_CONFIGURED
```

This means the research package is protected, while the later PR #8 owner upgrade, index-addendum update and Skill-run receipt still require a post-merge delta or later canonical snapshot. The targeted snapshot is not a full Git mirror.

## Implementation receipt

```text
07_PROMPTS_AND_AGENTS/skill_runs/2026-07-12__archive-governance-full-sensor-backtest__receipt.md
```

No market call. No portfolio action. No automatic rule ratification.
