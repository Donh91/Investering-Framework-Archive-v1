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

At **equal hypothetical penalties (miss-cost ratio k=1)**, all five four-era subsets for both assets show higher classification loss for the sensitive price-only candidate. This is not a sign-invariant or economic verdict. The comparison changes with the relative cost of a missed severe window versus a false alarm. There is no verified independent sample of 418 crises: daily 72h labels overlap, and original market families were selected after the fact. Leave-one-out of a retrospectively selected era is *not* a clean temporal holdout and establishes neither statistical confidence nor investor trade utility.

## Cost-ratio falsification, independently prompted by Claude Audit-04a

The primary source of this retrospective sensitivity remains the **same immutable HRE matrix**, not a new test set. Denote `k = hypothetical loss of missed severe-window outcome / hypothetical loss of a false alarm`, with false-alarm penalty fixed to one unit. For a four-era subset, challenger minus baseline hypothetical loss is `extra_fp - k × fewer_fn`. Lower is better. **No economic k is predeclared and these units are NOT observed trading costs.** The five selected eras were chosen in hindsight and overlapping cutoffs cannot be counted as independent market shocks.

| Illustrative k | BTC subsets where challenger is strictly better | ETH subsets where challenger is strictly better |
|---:|---:|---:|
| 1 | 0/5 | 0/5 |
| 2 | 0/5 | 1/5 |
| 3 | 2/5 | 4/5 |
| 5 | 5/5 | 5/5 |
| 10 | 5/5 | 5/5 |

The four-era break-even ratio ranges approximately BTC 2–4 and ETH 1.67–3. Therefore **the sign is determined by an assumed cost ratio**, not a robust superiority/inferiority finding. All five subsets are based on only five preselected event families, and BTC improvement is just three additional overlapping true-positive cutoffs over the full 418. The correct conclusion is **INSUFFICIENT_EVIDENCE_FOR_ECONOMIC_EDGE**, not candidate promotion or candidate rejection.

Original baseline BTC caught 8 of 46 severe overlapping-window positives (~17.4% recall), and ETH caught 15 of 88 (~17.0%). The more sensitive price-only challenger caught 11/46 and 22/88 (~23.9% and 25.0%) with higher false-alarm counts. These are NOT real original issued/delivered 3/5 or 4/5 risk levels. The principal new prospective research question is whether independently first-known *non-price* evidence can move issued risk severity in time without unacceptable false positives and missed delivery. A fixed k or preregistered k interval and matched non-stress controls must be frozen **before** scoring forward.

## Why level 3/5 persisted, what is demonstrably still unknown

This analysis **does not answer** what originally caused Compass to show 3/5 before each crash. True original 3/5 escalation, risk transition, source freshness, exact original decision time, delivery receipts and matched noncrisis periods must first be reconstructed from original issued packets, not today’s price tape. Task2 Wave B can audit a grid only when all original timestamps and non-warning slots exist. Owner #1553 remains OPEN; no historical warning or user delivery inferred from simulated price thresholds.

**Next factual work:** for each original stress episode and matched no-crash control, preserve the UTC event definition/anchor, full 72h prior decision slots including NOT_ISSUED and SOURCE_MISSING, original severity, vendor first-known, issue time, actual consumer delivery, lead-to-trough, recovery and false alarm cost. Fail closed / label source unavailable when clocks are missing. No official risk level, SELL, alert, schedule, source writer or weights changed.
