# TechDev Model Migration and Governance Statistics v1

**Date:** 2026-07-11  
**Status:** DESCRIPTIVE_CORPUS_STATISTICS / NOT_PERFORMANCE_SCORING

## Method

Keyword-family counts were generated across the 203 article texts in the merged Batch 3 corpus. A document is counted in a model family when it contains at least one family term. Families overlap, so row totals must not be summed as independent evidence.

## Article-family presence by publication year

| year | articles | HALVING_CYCLE_ANALOG | ELLIOTT_TIME_DILATION | CROSS_MARKET | LIQUIDITY_BUSINESS_CYCLE | ROTATION | MECHANICAL_TRADING | TOPPING_EXIT |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 17 | 13 | 4 | 2 | 2 | 1 | 0 | 17 |
| 2022 | 68 | 41 | 42 | 26 | 9 | 10 | 52 | 68 |
| 2023 | 54 | 23 | 25 | 23 | 25 | 22 | 12 | 54 |
| 2024 | 38 | 25 | 24 | 14 | 18 | 7 | 4 | 33 |
| 2025 | 21 | 14 | 14 | 17 | 18 | 4 | 0 | 17 |
| 2026 | 3 | 1 | 3 | 1 | 3 | 0 | 1 | 3 |

## Governance-language term counts

| year | HIGH_CONFIDENCE | HEDGED | INVALIDATION | REVISION |
|---:|---:|---:|---:|---:|
| 2021 | 24 | 181 | 42 | 40 |
| 2022 | 101 | 823 | 68 | 184 |
| 2023 | 45 | 411 | 62 | 210 |
| 2024 | 48 | 294 | 24 | 86 |
| 2025 | 33 | 157 | 1 | 69 |
| 2026 | 2 | 15 | 5 | 10 |

## Interpretation

- 2022 contains the densest mechanical-trading and model-transition activity.
- Liquidity and business-cycle language becomes more prominent relative to the corpus in 2023-2025.
- Halving and cycle analog language never disappears, even after the stated methodological migration.
- Hedged and revision language is frequent, which reflects both healthy uncertainty and substantial model flexibility.
- These counts describe attention and language, not accuracy or independent sensor value.

## Governance rule

```text
TERM_FREQUENCY_EQUALS_EDGE: NO
OVERLAPPING_MODEL_FAMILIES_ARE_INDEPENDENT_CONFIRMATIONS: NO
REVISION_LANGUAGE_ERASES_PRIOR_CLAIM: NO
```
