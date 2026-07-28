# WAVE 1 CROSS-MODEL RECONCILIATION — CHATGPT × CLAUDE

```yaml
audit_date: 2026-07-28
claude_wave1_zip_sha256: 5037de9ce264f8bf7d42a9cb481be14272a60d0daea75000f0fb597fe1ac59da
claude_own_research_zip_sha256: 1b3d68762bb0cddbd841ec5f32a9e7d90ca413437c4f7947c50ce9e7837bd800
artifact_integrity: PASS
blind_replication_integrity: BLOCKED
canonical_state_change: NONE
portfolio_action: NONE
```

## Executive verdict

Claude delivered two internally intact research packages. The main Wave 1 package verifies at artifact level, but Missions A and B are not blind replications because frozen owner events, policy definitions, costs and holdout boundaries were not supplied.

Several findings are valuable, but the strongest policy claims are not governance-ready.

## Accepted method learning

1. TDBC and comparable multi-month indicators must use settled bar-end plus actual publication availability.
2. Direct ETH/BTC is mandatory for direct threshold gates.
3. Historical events without honest `knowledge_at` remain quarantined.
4. Raw sensor count cannot be treated as independent evidence count.
5. Jan-Feb versus Feb-Mar anchor fragility is not demonstrated within the tested TDBC surface.

## Counterfactual lock audit

Claude reports 87 BTC events, but 81.6% overlap the previous 90-day event window. They form only 16 connected overlap clusters.

For `FRAMEWORK_LOCKED_3CONF`, the corrected connected-cluster mean return delta versus buy-and-hold is approximately -4.18%, with a 95% cluster-bootstrap interval of [-9.54%, +0.29%].

That supports a real concern about confirmation cost, but does not prove that the actual framework rule is dominated.

The implementation also reverses the sign of `avoided_loss`, and the three-higher-close rule is only a Claude-local proxy.

## TDBC reconciliation

The 1,080 specifications contain:

- 277 unique signal-date sets;
- 134 unique forward-outcome sets;
- 56 unique median six-month results.

Thus 99.9% support is evidence of parameter sign stability, not 1,080 independent confirmations.

The signal remains blocked as an independent economic signal because:

- n is only 3–5 per specification;
- two source-pair variants failed;
- no holdout was enforced;
- no ETF-era event exists;
- a two-bar-early timestamp shift outperformed the baseline;
- halving confounding is unresolved.

Claude's separate claim that 59% of the signal is explained by the halving clock is rejected numerically. Its code uses `.asof()` to fill the unmatured July 2026 six-month target with an earlier historical outcome and estimates the clock on the full overlapping target sample.

## Rotation

Claude's PCA and ridge results do not invalidate the direct 0.0300 event study:

- PCA asks whether a stable cross-sectional second factor exists.
- Ridge asks whether every 20-day ETH/BTC return is predictable.
- The framework test asks whether a direct settled first crossing marks a survival event.

These are different estimands.

Moreover, Claude's R7 walk-forward does not purge the 20-day target horizon. The last training labels use prices from the next test block, so the exact OOS metrics are rejected.

Current decision remains:

```yaml
H7: EARLY_ALERT_ONLY
direct_0_0300_cross: RESEARCH_CHALLENGER_SMALL_N
rotation: NO_ROTATION
```

## Drawdown hazard

The headline cells are repeated daily observations:

- `<-50%` and 31–90 days underwater: 128 daily rows but only 6 episode entries. Episode-first hazard is 66.7%, CI95 22.3%–95.7%.
- `-25/-15%` and >270 days underwater: 38 daily rows but only 4 episode entries. Episode-first hazard is 0%, CI95 0%–60.2%.

The depth × age idea is promising, but the published table is not ready for policy implementation.

## Sensor independence

This is the strongest cross-model agreement:

- ChatGPT: 23 sensors → about 8.9 diagnostic dimensions.
- Claude: 34 sensors → about 7.0 dimensions.

The exact number is not canonical, but the direction is clear: five confirming sensors may represent only two or three dependency clusters.

## Governance

```yaml
promoted_rules: NONE
retired_rules: NONE
canonical_state_change: NONE
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
```

## Wave 1.1 required tests

1. Frozen actual-policy counterfactual with non-overlapping event clusters.
2. Leave-one-cycle-out halving-orthogonalized TDBC.
3. Episode-level drawdown survival model.
4. Beta-neutral alt-minus-BTC rotation portfolio.
5. Purged and embargoed sensor and ETF-flow walk-forward.
