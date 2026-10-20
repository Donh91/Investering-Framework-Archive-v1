# Task 2 · First whole-window native v3 Compass 12h source census

**Recorded:** 2026-10-14. **Scope:** source-anchored public Git provenance only; **NOT** a sealed holdout, originally first-known provider certification, price-baseline backtest or independent predictive edge. **Frozen exact Git head:** `098c50d36b222c4c8ffa179a5879d36a74194bc4` (historical research snapshot, not moving `main`).

**Machine receipt:** [TASK2_R1_NATIVE_V3_12H_CENSUS_v1.json](2026-10-14__TASK2_R1_NATIVE_V3_12H_CENSUS_v1.json). Original user-issued files and original outcome files remain untouched.

## What we enumerated directly

Enumerated **all** `official/daily/2026/10/{12,13}` original Compass JSON files and **all** corresponding `official/outcomes/2026/10/{12,13}/*_12h.json` files at the frozen Git revision. This is a fixed two-day exploratory cohort, not a user-selected sample of winning forecasts.

| Category | Exact source count |
| --- | ---: |
| Original issued Compass JSONs | **17** |
| Original scoring contract v2 | **6** |
| Original scoring contract v3 | **11** |
| v3 with recorded 12h outcome at this exact head | **9** |
| v3 without 12h outcome in this pinned head | **2** |
| v3 recorded outcomes matching original Compass ID and SHA pointer | **9 of 9** |
| v3 12h target-observation timestamp exactly matching original target | **9 of 9** |

Raw original outcome labels across the **nine highly dependent observations**: BTC `CORRECT=4, INCORRECT=4, ABSTAINED=1`; ETH `CORRECT=3, INCORRECT=5, ABSTAINED=1`. These labels are transcriptions of native outcomes, **not an independent trial-level accuracy estimate**, and there is no matched mechanical benchmark or independent source first-known proof. Original results span overlapping hours and asset paths.

The **six v2** issued forecasts have no native 12h outcome in these two date folders at this frozen snapshot. They are not v3 scoring failures, and may have legacy historical scoring contract limitations. The **two v3** missing outcome files (`CMP-20261013-aecf113aab74`, `CMP-20261013-af3bcdea9173`) are `ABSENT_AT_SNAPSHOT` only; do not label them `MISSING_RECEIPT`, `CENSORED`, or `PENDING` without the original owner ledger and as-of policy.

All 17 original issued files initially declare `12h PENDING_MATURITY` at issue; this is a **forecast-era state**, not a later truth status. The nine outcomes are later materializations and must be evaluated using original first-seen stamps/contract chronology separately.

## Native-v3 example strengthened beyond legacy-v1 target-clock case

`CMP-20261012-468da783e9d8`:
- Original v3 forecast Git blob: `5239ba0450c97e425e5d5791e9c6c6cfa07e1613`, declared issuance **2026-10-12T23:24:24Z**; first path commit `749f995d129ded0f86acd74c8d13eb00741418fa` at **23:24:26Z**.
- Contemporaneous source packet path `04_MARKET_LEARNING/entry_signals/auto_market_state/runs/2026/10/12/232245_a3021c904445.json`, blob `48a061318da52279c761cff46456a17f0822954f`; first path commit `7ed9e997573fc23b2b89fd4998b69391e4063306` at **23:22:45Z**. The original source packet SHA-256 pointer matches the packet's self-declared SHA-256. The path commit predates declared issuance by **99 seconds**.
- 12h outcome blob `34b7ed2820c07c7cdd221e547f26891e0f2ce426`, first outcome commit `d7e53ac6c46e477a66aa5f8bccb33ffb929ef61b` at **2026-10-13T16:10:25Z**. Native v3 outcome has identical `target_at_utc=target_observation_at_utc=2026-10-13T11:00:00Z`. Recorded labels: BTC/ETH both `INCORRECT`. Preserve them; never exclude misses.
- This proves an archived **internal source → issue → outcome** chronology, not that every upstream vendor field or source vintage was first legally knowable before issuance or independently delivered to the end-user.

The previous [legacy-v1 original issuance case](2026-10-14__TASK2_R1_ORIGINAL_COMPASS_ISSUANCE_CASE_v1.md) had a 3,546-second mismatch between target and observation; the present v3 snapshot avoids that particular technical defect. It does **not** close the wider R1 scientific gate.

## Next admission gate for existing Task 1.5 / Task 2 owner (#1596)

1. Independently authenticate source-provider publication/availability and source revisions **as of each original issue**, including native timeframe and original forecast publication/delivery. Git commit metadata alone is insufficient.
2. Reconcile all original attempts, outcomes, abstentions, missing/censored/pending states, including the 2 v3 no-outcome files and overlapping same-day forecasts in the larger original owner population. Keep v2 and v3 score contracts strictly separate.
3. Freeze independent event-family clusters, prevent overlap leakage, and pre-register same-clock, same-capital, same-universe cheap baselines (persistence, price/volatility, momentum) before any historical model-comparison test.
4. Carry exact source hashes, provider first-known receipts and comparison attempts inside the restricted data plane when required; publish only value-free status and hashes in the public repo.
5. Only then may a **newly authorized, bounded** R2 experiment be admitted; no retrospective conversion of this exploratory window into a holdout.

**Scientific status:** `PUBLIC_GIT_LINEAGE_AND_TARGET_CLOCK_RECONCILIATION_COMPLETE`; `INDEPENDENT_PROVIDER_PIT=BLOCKED`; `VERIFIED_INDEPENDENT_FAMILY_N=UNKNOWN`; `HISTORICAL_R2_RUNS=0`; `AFTER_COST_EDGE=NOT_ESTABLISHED`. No site/Kompas changes, portfolio trades, source purchases, new workflow or additional owner.
