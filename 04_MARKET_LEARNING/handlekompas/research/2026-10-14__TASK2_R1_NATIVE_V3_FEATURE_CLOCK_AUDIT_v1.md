# Task 2 R1 · Native Compass source clocks, CFGI PIT progress and OKX funding settlement-time defect

**Date:** 2026-10-14. **Scope:** research-only frozen public metadata audit. **Original forecast population:** the *entire* nine-record native-v3 12h-outcome subset from the previously sealed, **17 originally issued** Compass files (2026-10-12/13). **PIT code/source reference:** `098c50d36b222c4c8ffa179a5879d36a74194bc4`.

**Machine record:** [2026-10-14__TASK2_R1_NATIVE_V3_FEATURE_CLOCK_AUDIT_v1.json](2026-10-14__TASK2_R1_NATIVE_V3_FEATURE_CLOCK_AUDIT_v1.json), cross-referenced against [R1 original attempt/outcome census](2026-10-14__TASK2_R1_NATIVE_V3_12H_CENSUS_v1.md). Neither this research nor the subsequent code review modifies any original forecast, original outcome, private source data, strategy, production signal or automated decision.

## 1. Exact-source readbacks — nine forecasts, not nine independent events

For each of nine issued native-v3 forecasts, the originally embedded `evidence_snapshot.full_feature_universe_reference.packet_path` was followed to the auto-market-state source packet at the **same exact historical Git head**. Its self-declared packet SHA-256 matched the original forecast pointer. The earliest available Git path-commit timestamp of every source packet preceded the corresponding forecast's declared issued-at timestamp.

| Exact sample | Verifiable count |
| --- | ---: |
| Original issued native-v3 forecasts with original 12h outcomes | **9** |
| Earlier packet in accessible Git path history; source packet hash pointer matches | **9 / 9** |
| Feature entries originally selected into the nine outputs (24 each) | **216** |
| Features with explicit retrieved-at timestamps | **81** |
| Features **without** explicit retrieved-at (not necessarily unavailable) | **135** |
| Features with explicit retrieved-at strictly after issuance | **0** |
| CFGI observation features in selected set (4 each: state, market, BTC, ETH) | **36** |
| CFGI feature entries with retrieved-at before issuance | **36 / 36** |
| Selected entries whose `observed_at` points after issue **because it is OKX's scheduled funding settlement time** | **12 entries in 6 forecasts** |

Earliest first-path Git packet commits were between **66 seconds and 6,944 seconds** before declared issuance, depending on packet re-use. The largest lead is not nine independent fresh captures; it reflects original re-use of an earlier source packet and requires an independent freshness check.

**CFGI scientific significance:** We now have good *contemporaneous archived retrieval metadata* for the **October 2026 v3-era** CFGI composite features included in native Compass, unlike the selected **2025-dated historical CFGI values fetched retrospectively in August 2026**. October 2026 CFGI features are a stronger first *as-of-feature-lineage* candidate, especially because each explicit retrieval timestamp predates issuance. However, a self-declared source timestamp and Git committer date are not external provider publication receipts; the release/public-delivery route and exact provider first-known/vintage must be adjudicated. All historical AI/CFGI-vs-baseline edge conclusions remain blocked.

**Denominator integrity:** These nine rows overlap market regimes and BTC/ETH outcomes, and they are nine rows, not nine independent market shocks. The full 17-issued-file window includes six v2-legacy forecasts and two v3 forecasts whose 12h outcomes were absent at the pinned snapshot. Do not discard them, invent data, reclassify, or call the nine a holdout.

## 2. Concrete source-code defect: funding settlement time mislabeled as quote observation

Current file: `scripts/data_ping/native_handlekompas.py`, Git blob `d00d38bed517861fa2487dce42d330bf05812f6d` (reviewed against the present version at the time of this audit). It builds `selected_features`, mapping:

- `btc_funding`: `_feature(..., observed_at=nested(derivative_live, "BTC-USDT-SWAP", "funding", "funding_time"), source_owner="OKX_LIVE_SWAP")`.
- `eth_funding`: identical route on `ETH-USDT-SWAP`.

Upstream collector `scripts/data_terminal/okx_swap_owner_collector.py` receives OKX `fundingRate` and `fundingTime` and stores `funding_time` as a millisecond timestamp. **OKX distinguishes the current/estimated rate from the upcoming settlement time.** Its own historical description and its API field semantics support that `fundingTime` denotes settlement, not when the current rate was published. Primary vendor references: [OKX funding calculation notice](https://www.okx.com/en-eu/help/okx-to-optimize-funding-rate-calculation) and [OKX API documentation](https://www.okx.com/docs-v5/en/).

In **six** of the nine original issues, `btc_funding` and `eth_funding` consequently carry `observed_at` after the issuance clock; the other three do not. This is a **demonstrable provenance field-semantics defect**, **not proof** that the quoted funding rate itself was unknowable at decision time. A current-period or predicted funding rate can be retrieved before the following settlement. Claiming automatic lookahead from a scheduled future settlement would itself be a scientific error.

**Required code owner fix (no historical rewrite):**
1. Define **provider quote as-of/retrieval time** and **scheduled settlement time** as *different* typed fields. Preserve original `funding_time` explicitly as `settlement_at_utc` (or equivalent metadata), not `observed_at`.
2. Bind the quote's actual capture timestamp from the underlying live-anchor receipt/source producer, check `capture_at <= forecast_issued_at`, and leave first-known state `UNKNOWN` or `BLOCKED` if capture timestamp is missing. **Never fabricate retrieval times from a future settlement** or silently substitute clock `datetime.now()` inside the historical builder.
3. Test past-settlement, future-settlement, missing-capture and 1h/8h settlement examples with deterministic fixtures; preserve original source packets/outcomes unmodified. The fix needs an independent domain/security review plus CI and a new versioned forward compatibility check before production semantics change.
4. Join CFGI's source `timestamp`, `retrieved_at_utc`, original v3 provider version and 2026-07-08 engine-era status in the R1 owner ledger. These source-clock decisions are distinct from funding semantics and must not be pooled.

## 3. Evidence classes and actual result

- `PUBLIC_ARCHIVE_PACKET_PRESENT_PREISSUE`: **9/9 at pinned head** — archive chronology only.
- `CFGI_SELECTED_FEATURE_RETRIEVED_AT_PREISSUE`: **36/36 entries** — original stated retrieval clocks; not independent vendor first-known certification.
- `FUNDING_SETTLEMENT_MISLABELS_OBSERVED_AT`: **12/216 entries**, in six forecasts — original-field defect; not evidence that the rate was learned after settlement.
- `SOURCE_RETRIEVED_AT_EXPLICITLY_ABSENT`: **135/216 entries** — needs upstream capture binding, not automatic exclusion.
- `ORIGINAL_OUTCOME_AND_SOURCE_PROVIDER_PIT_ADMISSION`: **BLOCKED**.
- `INDEPENDENT_HISTORICAL_R2_SCORE / AI_NET_EDGE / CFGI_INCREMENTAL_EDGE`: **NOT EXECUTED / NOT ESTABLISHED**.

**Handoff owner:** existing [Task1.5/R1 issue #1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596) and existing native Handlekompas code owner, not a new engine, issue domain or scheduler. Priority is to correct metadata semantic leakage **before** treating `observed_at > issued_at` as either a predictive signal or an indisputable data leak.

**Next R1 path:** Use a complete, chronology-checked original selected-feature ensemble, not post-hoc copied market snapshots, and a pre-registered simple persistence/volatility benchmark; test only on independently verified source first-known receipts and independently clustered events. There is **no permission** to promote this October sample into a retroactively selected holdout or to rewrite its original outcomes.
