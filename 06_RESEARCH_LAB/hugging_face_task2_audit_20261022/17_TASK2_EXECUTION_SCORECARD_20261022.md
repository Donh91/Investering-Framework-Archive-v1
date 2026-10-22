# 17 | Task 2 Work + Codex execution scorecard, 22 October 2026

**Verdict: VERIFIED_PARTIAL / SCIENCE_BLOCKED.** Two distinct durable outputs were produced in this authorized session: bounded OKX funding-clock repair in [draft PR #1749](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1749), and an executed pinned HF BTCUSDT 1h T1 quality study in [this draft PR #1747](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1747), companion [receipt](16_PINNED_BTCUSDT_1H_T1_QA_20261022.md) and [QA script](16_PINNED_BTCUSDT_1H_T1_QA.py). **No original forecast row was scientifically admitted and no economic edge was established.** These are Work-session observations, separated below from pre-existing Task 2 records.

## Current authority and P0 reconciliation

| Item | Freshly checked evidence | Remaining limit |
| --- | --- | --- |
| Public main | `a77d61bffc851a33382020997d88f9b61e32ccb3`; `AGENTS.md` Git blob `72d0846eb9687fb54c320845dab8cd10e46b62fa` | Re-read before any future merge |
| #1746 | **MERGED** at `52cb3492c3fbb43e83ab920394111979972fe229`, head `c8a63a9455f8c659f8715b7a30b774ad5c855aa1`; matrix, floor validator and monitor file blobs on current main exactly match PR file blobs; three head checks SUCCESS | Natural monitor after merge is zero-row, not proof of a real post-floor row |
| #1748 | **MERGED** at `64b1f1b79aeba70115d5720fb2cbdf1f4e896e6b`, head `59b4d1aabc973f5a5c6bef06d241ed610d4a1d1c`; materializer and evidence-controller blobs on current main exactly match PR file blobs; three head checks SUCCESS | First eligible source/materializer row is not yet observed |
| Natural Shared Row monitor | Main `monitor/LATEST.json` generated **2026-10-22T20:19:40Z**, after those merges: revision `1.2-consumer-source-bound-integrity`, `PASS`, `NOT_READY_NO_SHARED_ROWS`, 0 raw/eligible rows and 0 divergences | `POST_FIX_OBSERVATION`: real postmerge run, but no real row exercised the source guard; 24 Oct 12:00Z remains the frozen future floor |
| Open Archive PRs | Three when checked: #1733, draft #1747 and draft #1749 | No duplicate P0 patch was made |

Local current-main tests for the P0 area: `python -m unittest tests.research.test_shared_row_p0_integrity tests.research.test_shared_row_consumer_integrity tests.research.test_shared_row_activation_phase_gate -q`, **57 passed**. Existing GitHub PR checks were inspected separately; local results do not replace natural producer/consumer evidence.

## New engineering result, exact owner

The existing CODEX_READY candidate `codex-research-task2-okx-funding-settlement-clock-v1`, signature `4e2c6df9c10d30c4b1d9`, was bound through its preflight transition receipt. Main still mapped OKX `funding_time` (scheduled settlement epoch) into a feature `observed_at`. PR #1749 only changes the native Compass evidence snapshot, one new regression test and the candidate's required transition receipt. It keeps `observed_at` and per-field `retrieved_at` unknown, preserves a distinct `settlement_at_utc`, and exposes a Git-bound Daily Live Anchor *batch* time only as `source_batch_captured_at_utc`; it does not call that a provider first-known time. Values, feature eligibility, forecast horizons and action policy are unchanged. The original issued snapshots remain immutable.

Pre-fix six new tests produced four failures and one error. Revised-head local tests: **45 passed** including the existing Official Compass suite; an isolated mutation removing the `capture <= packet` guard made the after-packet negative test fail. Same-fixture differential execution against original main changed only `evidence_snapshot` and enclosing `compass_sha256`, with horizons, data status and protection state identical. An independent non-writing advisory of the first head found no P0/P1 and raised a P2 ambiguity about placing batch capture in `retrieved_at`; the revised head addressed it. The same reviewer re-read exact head `238c7d67b0c6c1ce951fd06183eba6e6e64254ee` and found no concrete P0/P1, with only the residual reminder that value/health `ELIGIBLE_PRESENT` is not PIT admission. GitHub showed **10 SUCCESS and 8 SKIPPED check runs** on that exact head. This is **not** a formal GitHub APPROVED review. PR #1749 remains draft pending formal release safeguards and an immediate source/recovery safepoint; no merge or postmerge producer claim is made here.

## Scientific source result and stage state

The HF FREE account `FrameworkCN` was verified. One public `linxy/CryptoCoin` BTCUSDT 1h file was fetched by immutable revision `9288a8d3f5e8a3fd0af814c2429b4cb565356908`; downloaded 9,050,531 bytes matched its pinned LFS SHA-256 `712fedb852b6eb26a2864959cf3c6c7cc1ee0ca80565ad12a264b84c0eb12772`. The QA found **80,317 rows, 28 gap boundaries, 128 omitted hours, 14 partial/non-full close timestamps**, no duplicate open hour and no impossible OHLC or negative volume. Six adverse fixtures passed. This is **T1 source QA only**; its Oct 22 repository revision cannot prove Oct 12-13 original issuer availability. See receipt #16 for exact method, schema caveat and rights boundary.

The following counts are **from the existing frozen original-v3 R1 ledger**, re-read in this session, not newly generated rows: 11 original issued attempts, nine outcome receipts present and two absent at that original snapshot (both later located), 10 unique public source packets, seven capture blobs, **0/11 PIT admitted**, and zero *certified* independent event families. All 11 lack verified provider first-publication/revision and first user delivery; no-forecast and no-warning denominators are `UNKNOWN_NOT_ENUMERATED`. The new HF result changes the original admission count by **0**. The two originally absent outcomes are not silently classified as censored or missing forever.

| Stage | Session state | Reason |
| --- | --- | --- |
| R0/R1 | PREVIOUS_COHORT_RECONCILED / NOT_IDENTIFIABLE_YET | Original Git/internal capture clock is not independent per-field provider first-known; delivery and event-family proof missing |
| R2 | NOT_EXECUTED | No genuinely admitted original cohort for a same-clock preregistered framework baseline |
| R3 | NOT_EXECUTED | No original first-actionable delivery, executable fill and paired holder/cash after-cost cohort |
| R4/R5 | NOT_EXECUTED | No valid independent test cohort or authorized complexity promotion |
| R6/R7 | PROSPECTIVE_COLLECTION_ONLY | Frozen 2026-10-24T12:00:00Z core floor is in the future; no matured T4 result |
| HF | 1 new T1 file, 0 new T2/T3/T4 admissions | Research source, not historic issuer evidence; no model challenger run |

No Round 3 private analysis or outcome scoring was opened. No Alpha/News owner was changed. No new scheduler, agent, model, paid compute, portfolio decision or threshold was introduced.

## Resource and release truth

Owner reported 96% Work/Codex usage after reset, but account quota telemetry is **USAGE_UNVERIFIED** here. Owner also reported the October GitHub Actions minutes exhausted until 1 November. In contrast, exact PR-head check runs were observed on GitHub during this session, so account billing/reset state remains **UNKNOWN**; successful PR checks do not prove scheduled producers are healthy. No manual workflow rerun or paid minutes were requested. HF account was FREE; **0 HF Jobs/GPU and 0 paid OpenAI API calls** in this session. One 9,050,531-byte public file was downloaded for QA. Local Python `duckdb` was used without cloud compute.

**Next cheapest evidence step:** choose one original v3 forecast and bind each required feature to an original immutable capture plus independently defensible provider availability, then bind first actual user delivery and its as-issued target. Keep all 11 attempts and unknown/no-signal opportunities in the denominator. Only if that R1 admission succeeds, freeze a matched same-clock price-only R2 trial before scoring. Separately, observe the first naturally produced post-floor Shared Row row under the merged P0 guards. No further HF model or paid source work is justified to bypass those clocks.
