# Task 2 #1596 · P0 source admissibility & Round 3 cadence preflight
**Date:** 2026-11-07 (Europe/Copenhagen)  
**Owner:** original Task 2 #1596, original Round 3 private collection owner remains independent.  
**Claim class:** SOURCE_METADATA / NEGATIVE_ADMISSION / NOT_PROSPECTIVE_EDGE.  
**Frozen public branch base:** `0ef8e3905778eb8c0574e5c7e894693743f57ebf`.  
**Runnable audit:** `scripts/research/task2_r1_first_known_and_cadence_preflight_v1.py`; eight adversarial tests `tests/research/test_task2_r1_first_known_and_cadence_preflight_v1.py`. New test suite runs through the **existing** read-only `framework-learning-operations.yml` PR owner gate. No new workflow, schedule, data collector, scheduler, source-vintage, canonical forecaster, AI agent or paid API.

## P1: a chronologically preselected original R1 first case, without looking at the outcome

The **earliest issued** of the 11 original frozen native V3 forecasts is `CMP-20261012-904299b09eca`, **2026-10-12 19:59:38Z**. This is selected on issuer timestamp alone. Original historical raw capture was marked **2026-10-12 17:55:49Z**, first Git committed **19:57:34Z**. The source packet was first Git committed **19:58:03Z**, before issuance. This establishes an INTERNAL archive ordering but NOT original independent vendor first-known or a user delivery. Raw capture age is about 2 hours four minutes, not a general freshness violation without the original per-source rule.

**Original 11-forecast / 24-feature index, 264 feature instances**:
- **22 field instances** are the two BTC/ETH prior-packet delta values that determine the direct 12h directional sign; another **22 price input instances** are in their lineage.
- **22** relative ETH/BTC context instances are not the BTC/ETH 12H sign.
- **198** index instances are context or health/evidence index and NOT direct sign inputs.
- Source index clocks split across actual original clock classes (archive retrieval known, missing retrieval, and funding settlement-not-quote). No original independent vendor-publication/revision timestamp is authenticated. **0 of 11 original R1 forecasts pass full PIT admission**; **0 of 11 original user delivery clocks are known**. This is not 264 independent predictors, 11 independent shocks or 11 valid experimental outcomes.
- The existing causal-source matrix verifies original exact engine AST and the **11 required original source-health predicates**. An original per-packet PASS does not prove every upstream provider vintage; a contextual sensor can block issuance without directly changing the sign.
- The original full historical absence universe is not enumerated. The separate Task 1.5 original receipt distinguishes 824 retrospective price-joined forecasts, 814 original outcomes (314 matured and 500 censored) and 10 missing receipts. No retrospective recovery changes their original statuses.

**Original sources:**
- `04_MARKET_LEARNING/handlekompas/research/2026-10-15__TASK2_R1_NATIVE_V3_ORIGINAL_ADMISSION_v2.json` pinned Git blob `9e728b835de294e5777222c171a89874a69dae95`.
- `04_MARKET_LEARNING/handlekompas/research/2026-10-13__TASK_1_5_EDGE_ADMISSION_GATE_v1.json` pinned Git blob `b7e3dc8c1b1e8f948df72ef32fa762e7667a6bde`.
- Original source causal matrix `scripts/research/task2_r1_original_causal_source_matrix_v1.py` blob `cd6b94abce0c5099a65787ad34ae3a352e8c8cec`, verified current main at source preflight.

**What genuinely unlocks R1**: authenticate the original release of the **direct BTC/ETH hourly price+prior-delta chain** plus mandatory decision-health predicates at each real issuer cutoff; register the full no-forecast/abstention denominator and proper maturity/delivery receipts; group independent market shock units; compare with frozen same-clock B2 momentum and always-HOLD after the prior gates. No ex-post creation of an originally absent vendor record.

## P2: Round 3 restricted-data collection, actual cadence versus original contract

Verified **READ-ONLY** against private `Donh91/secrets` main `c9e16b72585d5d22442f8239f6e8432dc241ec0e`. Authority `GOVERNANCE/COLLECTION_ACTIVATION.json` blob `ff3a4489d22ba005a86b7902ed407d6be58e6758`: `collection_active=true`, active `SC01`, `SC03`, `SC14`, mode `PROSPECTIVE_COLLECTION_ONLY`; hypothesis and outcome scoring both disabled. `health/LATEST_PRIVATE_DATA_HEALTH.json` blob `490bd232e78f35899af61b6d14a6a0382fbe4294`: 1,193 captured raw files, 1,182 post-floor provenance complete but **analysis NOT authorized**, 11 legacy quarantined, no current health failures.

The original private source bindings require:
- `SC01` OKX ETH OI: one observation/hour, nominal **24/day**.
- `SC03` OKX ETH settled funding: **15-minute source check/dedup**, nominal **96/day**, not fabricated 96 distinct settlement observations.
- `SC14` Deribit ETH 25-delta skew: hourly full option chain snapshot, nominal **24/day**.

All three current private `.github/workflows/round3-*.yml` are **temporarily reduced to two scheduled calls per day**, observed current cron at UTC hours 06 and 18, with source-specific minutes. This is an **explicit 2026-10-19 owner critical-budget conservation override**, not accidental inactivity.

| Source | Nominal source-check runs/day | Scheduled runs/day | Difference/day |
|---|---:|---:|---:|
| OKX OI SC01 | 24 | 2 | 22 |
| OKX realized funding SC03 | 96 | 2 | 94 |
| Deribit options SC14 | 24 | 2 | 22 |
| **Total** | **144** | **6** | **138** |

Straight schedule restoration would add **4,140 job starts over 30 days**, before retry/queue/runtime variations. This is NOT 4,140 billable GitHub minutes: no verified per-run P50/P95 compute time and no current month quota+usage receipt are available in this audit. Two jobs per day do not prove full source completeness, and a funded 15-minute REST poll should not be equated with a historical independently vintaged market dataset. Three already-known private capture runs #42371011805, #42308772794 and #42308461011 were checked via their actual GitHub jobs and marked `success`; not enough to prove source completeness or reliable monthly minutes.

**P2 owner-safe decision:** **Do not silently restore the nominal schedule** under the 3,000 GitHub Actions-minute monthly cap or imply it fits. The budget-driven conservation override was deliberate. First obtain actual past 30-day action billed-minute totals + P50/P95 real source-job billable duration + source contract minimum useful opportunity rate. Then choose an eligible bounded cadence tier, independently test actual schedule/run/health receipts, and update through separate original `Donh91/secrets` reviewed PR before modifying the active writers. SC06 continuous L2 depth is still blocked on separate persistent infrastructure and budget; do not treat periodic Actions as a continuous stream. Remote third-party data/value redistribution remains prohibited.

**Private documentation drift:** older private explanatory `GOVERNANCE/CROSS_REPO_DATA_BOUNDARY.md` and `README.md` still contain statements that collection is inactive/terms-held. Current machine activation and source-health receipts demonstrate that wording is stale. A separate reviewed private docs correction may replace the stale explanation **without touching the permission contract, collection code or raw data**.

## Remaining owner gates, no false completion

- P1 scientific R1 first legally admissible original forecast: **BLOCKED_VENDOR_FIRST_KNOWN_AND_INDEPENDENCE**. The on-demand preflight can be completed and validated today; source-vintage truth cannot be manufactured.
- P2 data contractual cadence restoration: **BLOCKED_ACTIONS_MINUTES_AND_ORIGINAL_OWNER_RELEASE**, not masked by green schema QA.
- P3 alert→delivery→after-cost: blocked until actual delivery/fill and frozen no-warning control. Historical M1 latency sensitivity may be tested descriptively, not as portfolio wealth.
- P4 eight-lane scientific Wave 3: prioritize independently acquired/source-permitted cohorts; no indicator tuning on exposed historical data, no reuse of restricted Round 3 for performance tests.

**Definition of done for this P1/P2 unit:** exact public original source preflight deterministic run, negative tests PASS in existing PR-native CI, public owner research report source/main readback and one original issue receipt. This is an actual operational repair/measurement, not scientific edge certification.
