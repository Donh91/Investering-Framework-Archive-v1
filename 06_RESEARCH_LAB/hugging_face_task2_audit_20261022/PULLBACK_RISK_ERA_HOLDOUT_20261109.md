# Pullback Failure Atlas, 9 Nov 2026, original Risk #1553

**NEW deterministic observation:** leave-one-selected-era-out robustness of the existing HRE 2022-26 retrospective 72h severe-downside warning matrix. Source is original immutable Git blob 2f46169590ae208f724d783c70a545bfceb228fb from native original run 42391907367 and PR #2012, reused by merged PR #2040. No new exchange fetch, provider, model or Actions workflow.

Original source has five hand-selected eras and 418 overlapping daily cutoff observations **per asset**. Existing PR #2040 proves the more sensitive price-only challenger produces BTC +3 detected severe overlapping windows and +9 false alarms (equal-cost loss +6), ETH +7 detected and +15 false alarms (equal-cost loss +8).

## New four-era leave-one-out robustness (challenger minus existing baseline, equal hypothetical unit loss)

| Held-out original era | BTC extra FP / fewer FN | BTC loss difference | ETH extra FP / fewer FN | ETH loss difference |
|---|---:|---:|---:|---:|
| Terra 2022 | +8 / 2 | +6 | +12 / 5 | +7 |
| FTX 2022 | +6 / 3 | +3 | +12 / 6 | +6 |
| USDC 2023 | +8 / 3 | +5 | +14 / 7 | +7 |
| August 2024 | +7 / 2 | +5 | +10 / 6 | +4 |
| February 2026 | +7 / 2 | +5 | +12 / 4 | +8 |

All five four-era subsets for both assets therefore preserve higher *hypothetical classification loss* for the more sensitive price-only candidate at equal unit penalties. There is no verified independent sample of 418 crises: daily 72h labels overlap, and original market families were selected after the fact. Leave-one-out of a retrospectively selected era is *not* a clean temporal holdout and establishes neither statistical confidence nor investor trade utility.

## Why level 3/5 persisted, what is demonstrably still unknown

This analysis **does not answer** what originally caused Compass to show 3/5 before each crash. True original 3/5 escalation, risk transition, source freshness, exact original decision time, delivery receipts and matched noncrisis periods must first be reconstructed from original issued packets, not today’s price tape. Task2 Wave B can audit a grid only when all original timestamps and non-warning slots exist. Owner #1553 remains OPEN; no historical warning or user delivery inferred from simulated price thresholds.

**Next factual work:** for each original stress episode and matched no-crash control, preserve the UTC event definition/anchor, full 72h prior decision slots including NOT_ISSUED and SOURCE_MISSING, original severity, vendor first-known, issue time, actual consumer delivery, lead-to-trough, recovery and false alarm cost. Fail closed / label source unavailable when clocks are missing. No official risk level, SELL, alert, schedule, source writer or weights changed.
