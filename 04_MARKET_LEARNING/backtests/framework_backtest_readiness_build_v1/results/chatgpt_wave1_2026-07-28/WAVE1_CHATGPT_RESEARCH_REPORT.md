# BACKTEST WAVE 1 — ChatGPT Research 1–5

```yaml
program: FRAMEWORK_BACKTEST_READINESS_BUILD_v1
run_date: 2026-07-28
execution_owner: CHATGPT_PLUS_LOCAL_CONTROLLED_ENGINE
status: COMPLETED_WITH_EXPLICIT_BLOCKERS
economic_authority: RESEARCH_ONLY
final_holdout_opened: NO
claude_results_seen: NO
canonical_state_change: NONE
portfolio_action: NONE
```

## Input integrity

Four byte-visible source packages were used. All ZIP CRC checks passed.

| Package | Bytes | SHA-256 | Detached checksums |
|---|---:|---|---|
| DATA PING BACKTEST HISTORY PACK 20260727T052808Z.zip | 190,546,648 | `303d63946fd7696237b8d1a7208fa5aadd877e55aba57d5b51ea17aa46d18c9f` | 180/180 PASS |
| TDBC v1 TechDev Business Cycle 2026-07-26.zip | 237,291 | `e83d3b95e94fba331767feae92bd052ed7f752a1a5305d63621030b293bc5d4c` | 17/17 PASS |
| DATA_PING_BACKTEST_HISTORY_PACK_20260727T114012Z.zip | 930,818 | `26df6c5bba68b503ec1744b2ca03b8beecb37ce14abc8f3ced636017b2910521` | 257/257 PASS |
| data_ping_uge30_2026.zip | 702,338 | `c0745b6c0b961fd3765ffa051dc6f2d07db611c86654871122e59e6d4f6abe98` | CRC PASS |

The corrected final master `DATA_PING_BACKTEST_HISTORY_PACK_FINAL_20260727T183529Z.zip` was not used because its exact bytes were not present. Preliminary result files embedded in packages were excluded from evidence.

## Executive verdict

| Research | Verdict | Main result |
|---|---|---|
| R1 Point-in-time replay | `POINT_IN_TIME_CONTAMINATED_AND_DECISION_REPLAY_BLOCKED` | TDBC phase was assigned up to about 60 days too early; 2/3 framework events lack `knowledge_at`; visible FRED rows are latest-vintage rather than ALFRED initial release. |
| R2 Counterfactual deployment | `PARTIAL_PROXY_ACTUAL_FRAMEWORK_POLICY_BLOCKED` | Being out before a flush clearly helped. A five-day delay beat immediate rebuy in 63% of 27 events, but its confidence interval crossed zero. |
| R3 Rotation survival | `H7_ALONE_NOT_VALIDATED_DIRECT_003_CROSS_PROMISING_SMALL_N` | H7-like early transmission had a negative median 20-day ETH/BTC outcome. Direct settled 0.0300 crossings were stronger, especially with breadth, but small-N blocks promotion. |
| R4 Range tournament | `INSUFFICIENT_EVIDENCE_PILOT_ONLY` | Cycle Navigator had the best overlap and sharpness. ATR-2x had the best proper interval score. Only two fully prospective weeks were available. |
| R5 Sensor independence | `REDUNDANCY_CONFIRMED_NO_LINEAR_OOS_EDGE_DEMONSTRATED` | Twenty-three sensors compressed to about 8.9 correlation dimensions. Breadth and dominance added the most marginal information, but all tested linear models had negative out-of-sample R². |

# R1. Point-in-time state and decision replay

## Framework decision ledger

The visible ledger contains three historical records: FNP-001, FT-1 and TD-97. Only TD-97 contains a usable `knowledge_at`.

```yaml
events_total: 3
missing_knowledge_at: 2
missing_rate: 66.67%
```

The missing timestamps were not inferred. An honest full historical replay of the actual framework policy is therefore blocked.

## Macro-vintage boundary

The visible FRED files explicitly describe latest-vintage observations. They are not ALFRED initial-release vintages.

```yaml
historical_revised_macro_replay: DESCRIPTIVE_ONLY
historical_real_time_macro_replay: BLOCKED
```

Monthly values may only become available after period completion and publication. Annual values may only become available after year-end and publication.

## TDBC lookahead finding

The supplied master panel assigns an anchor-1 two-month TDBC phase from the start of the bar, although the phase requires the completed bar. A defensible point-in-time version can only activate the phase after bar completion.

```yaml
days_compared: 3205
phase_divergence_days: 1207
phase_divergence_rate: 37.66%
phase_transitions: 58
median_premature_transition: 60_days
```

The July 2026 `RED_RISING_PARABOLIC` phase illustrates the defect:

- naive availability: 2026-07-01
- defensible availability: 2026-07-25
- premature lead: 24 days

Earlier completed bars commonly produced 57–61 days of premature phase assignment. This is a material lookahead defect, not a cosmetic timestamp issue.

## ETF timing

All 651 ETF rows carried an approximate 21:00 UTC knowledge timestamp.

```yaml
known_by_08_00_CEST: 0%
known_by_CEST_daily_close: 100%
```

Same-session ETF flow cannot be used in a morning decision. A simple rotation proxy differed on 15 of 928 ETF-era days depending on morning versus post-close information:

- four false morning permits;
- eleven permits visible only after the settled flow became available.

## R1 decision

Repair is required before historical state-machine scoring:

1. remove TDBC bar-start assignment;
2. obtain first-release macro vintages;
3. reconstruct or quarantine missing `knowledge_at`;
4. freeze decision time for each policy.

No historical framework-skill claim may use the current TDBC daily panel as point-in-time evidence.

# R2. Counterfactual deployment and regret ledger

Because the actual historical framework policy is not reconstructable, this is a policy-proxy experiment rather than a canonical framework backtest.

Independent flush events were frozen as:

```text
BTC settled one-day return <= -8%
OR
BTC settled three-day return <= -12%
```

Events were clustered with a 60-day cooldown.

```yaml
independent_events: 27
evaluation_horizon: 60_days
round_trip_cost: 0.20%
```

| Policy | Median return | Mean return | Positive rate | Median max drawdown | No-entry rate |
|---|---:|---:|---:|---:|---:|
| Always invested | -1.85% | 2.56% | 44.44% | -23.58% | 0% |
| Immediate rebuy | 5.51% | 11.58% | 55.56% | -20.73% | 0% |
| Delay 1 | 7.08% | 13.02% | 59.26% | -20.73% | 0% |
| Delay 3 | 4.19% | 11.39% | 59.26% | -20.73% | 0% |
| Delay 5 | 6.76% | 14.74% | 62.96% | -20.63% | 0% |
| Mechanical 70/30 | 3.38% | 11.52% | 55.56% | -20.73% | 0% |
| Two-positive-close confirmation | 0.82% | 11.29% | 51.85% | -16.50% | 11.11% |
| ATR repair confirmation | 0.00% | 15.01% | 48.15% | -11.70% | 22.22% |
| Framework-like repair proxy | 0.13% | 10.66% | 51.85% | -16.50% | 14.81% |
| Cash | 0.00% | 0.00% | 0% | 0.00% | 100% |

Five-day delay versus immediate rebuy:

```yaml
median_return_delta: +3.72_percentage_points
outperform_rate: 62.96%
bootstrap_95pct_CI: [-2.15pp, +9.23pp]
```

The confidence interval crosses zero. The direction is promising but unresolved.

The framework-like proxy had a median delta of -1.21 percentage points versus immediate rebuy and a 14.81% no-entry rate.

## R2 decision

Two findings survive:

1. remaining invested through a flush was materially worse than being out before it;
2. the current confirmation logic has not been demonstrated to be optimal after a flush.

A fixed five-day delay becomes a research challenger only. No rebuy rule changes.

# R3. Rotation survival and transition replay

Two event families were tested on direct Binance ETH/BTC CEST-settled data.

## H7-like early transmission

Frozen definition:

- at least three consecutive positive direct ETH/BTC log increments;
- ETH outperformed BTC in every final-three session;
- ETH/BTC stayed above 0.0275;
- 20-day event cooldown.

```yaml
independent_events: 79
median_ETHBTC_return_20d: -2.89%
positive_20d_rate: 37.18%
bootstrap_median_CI: [-4.75%, -1.20%]
```

Breadth above 50% did not rescue this event family:

```yaml
events: 44
median_20d: -3.28%
positive_rate: 36.36%
```

H7-like early transmission is therefore admissible as a candidate alert, not rotation confirmation.

## Direct settled 0.0300 first crossing

Frozen definition:

- direct ETH/BTC settled close crossed above 0.0300 from below;
- 20-day event cooldown.

```yaml
independent_events: 11
median_20d: +5.92%
positive_20d_rate: 72.73%
bootstrap_median_CI: [-1.81%, +18.92%]
```

With breadth above 50%:

```yaml
events: 8
median_20d: +7.01%
positive_20d_rate: 87.50%
bootstrap_median_CI: [+2.33%, +18.92%]
```

With breadth above 50% and non-rising BTC dominance:

```yaml
events: 4
median_20d: +14.19%
positive_20d_rate: 100%
```

The final subset is much too small for promotion. H7 ETF-positive had only six events, and the full breadth, dominance and flow combination had three.

## R3 decision

The current governance distinction is supported:

```text
early transmission candidate != rotation confirmation
```

H7-like early transmission mean-reverted on median. The direct settled 0.0300 crossing is the stronger research candidate. Breadth appears useful, but venue, era and holdout replication remain mandatory.

No rotation-state change.

# R4. Cycle Navigator range-skill tournament

Only Cycle Navigator #16 and #17 were fully prospective and matured.

```yaml
weeks: 2
asset_week_observations: 4
```

Cycle Navigator #15 was retained as a bridge observation but excluded from the primary result.

| Method | Mean containment | Mean Jaccard | Mean normalized interval score | Mean width | Breach rate |
|---|---:|---:|---:|---:|---:|
| Cycle Navigator | 93.06% | 61.37% | 24.79% | 10.75% | 50% |
| ATR 2x | 100% | 54.28% | 13.19% | 13.19% | 0% |
| EWMA 90% | 100% | 37.87% | 19.09% | 19.09% | 0% |
| ATR 3x | 100% | 36.19% | 19.78% | 19.78% | 0% |
| Historical 90% quantile | 100% | 22.92% | 31.34% | 31.34% | 0% |
| Previous-week range | 68.65% | 50.38% | 58.52% | 7.08% | 100% |

Cycle Navigator produced the best overlap and tightest useful ranges. ATR-2x produced the best proper interval score and no breaches.

The two Cycle Navigator breaches were:

- CN #16 ETH: two breach days, first 2026-07-15;
- CN #17 BTC: one breach day, first 2026-07-21.

## R4 decision

The current sample cannot support a range-skill claim. Continue prospective scoring without method changes. The proper score must remain width-adjusted, not containment alone.

# R5. Sensor independence, ablation and graph

Common ETF-era sample:

```yaml
rows: 427
period: 2024-07-29_to_2026-06-30
sensors: 23
```

The sensor set covered price and relative price, breadth, derivatives, ETF flow, dominance, sentiment and business-cycle state.

## Redundancy structure

```yaml
pca_participation_ratio_diagnostic: 8.91
first_component_variance_share: 24.79%
first_five_components_cumulative_share: approximately_62.43%
```

Strong clusters included:

- ETH/BTC z-score and percentile;
- BTC and ETH funding;
- BTC and ETH open interest;
- business-cycle MACD and RSI;
- BTC ETF-flow z-score and streak;
- ETH ETF-flow z-score and streak;
- breadth advancing and breadth outperforming BTC;
- a broader volatility, drawdown, sentiment and breadth-above-MA50 risk cluster.

This confirms that raw sensor count materially overstates independent evidence dimensions.

## Walk-forward ablation

Target: 20-day direct ETH/BTC return.

```yaml
price_only_OOS_R2: -2.655
price_only_sign_accuracy: 39.33%
```

Incremental family effects relative to price-only:

| Added family | MSE improvement | Delta R² | Sign-accuracy change |
|---|---:|---:|---:|
| Breadth | +0.003203 | +0.271 | -2.00 pp |
| Dominance | +0.002496 | +0.211 | +1.00 pp |
| Derivatives | +0.001776 | +0.150 | +1.00 pp |
| ETF | +0.000603 | +0.051 | +1.67 pp |
| Sentiment | -0.006767 | -0.572 | negative |
| Business cycle | -0.007662 | -0.648 | +6.33 pp |

Every tested linear model retained negative out-of-sample R². No predictive edge was demonstrated.

## R5 decision

Material redundancy is confirmed. Breadth and dominance are the strongest incremental diagnostic candidates in this linear setup. Sentiment and business-cycle features did not improve squared-error prediction.

This does not automatically demote sensors. Sensors may still possess veto, source-QA, state-description or nonlinear value. Promotion requires a separately preregistered model and holdout.

# Governance conclusion

```yaml
R1_action: REPAIR_POINT_IN_TIME_CONTRACTS
R2_action: PROMOTE_DELAY_5_TO_RESEARCH_CHALLENGER_ONLY
R3_action: KEEP_H7_AS_EARLY_ALERT_TEST_DIRECT_0030_AS_STRONGER_CHALLENGER
R4_action: CONTINUE_PROSPECTIVE_SCORING_NO_SKILL_CLAIM
R5_action: SIMPLIFY_EVIDENCE_COUNTING_TEST_BREADTH_AND_DOMINANCE_INCREMENTALLY
final_holdout_opened: NO
canonical_rule_change: NONE
rotation_change: NONE
rebuy_change: NONE
new_entry_change: NONE
portfolio_action: NONE
```

The next valid step is artifact-level comparison with Claude after its outputs are frozen, followed by repair of point-in-time inputs and only then a controlled holdout run.