# 30 | Original 12h Compass decision dependencies vs R1 admission

**Task 2 Phase II · 2026-10-23 · source-bound forensic research, not scientific R1 PASS.**

## Executive verdict

The original October 14 v3 `NEXT_12H` **direction value** is computed primarily from two previous-packet return deltas, BTCUSDT and ETHUSDT. Those are **NOT** the entire original forecast-availability dependency graph. The original auto-market packet's `decision_context_status` also gates direction output and is computed from **11 registry-required source health lanes**; source-stale/future/absent data can force `UNAVAILABLE` before any direction. The published 24 `evidence_snapshot.selected_features` are a *compact reporting index*, neither 24 equal direction votes nor a certification that all are numerically causal. Do not demand arbitrary 24-factor predictive replays when the declared decision kernel is narrower, but **do not** erase the required status, provenance, policy and source-clock dependencies.

## Exact frozen code evidence (historical original, not current HEAD)

| Object | Original immutable source | Code/data identity |
| --- | --- | --- |
| Auto Market State producer | `scripts/data_ping/auto_market_state.py` at original Oct14 source snapshot `86112a8d4c4efbf05826a3c3ca1d3a690f968883` | Git blob `6196286539bd3e3688dc3bbcf322b15112b6` |
| Original native Compass engine | `scripts/data_ping/native_handlekompas.py` at same SHA | Git blob `d00d38bed517861fa2487dce42d330bf05812f6d` |
| Original source-admission registry | `02_DATA_PING/source_integrations/2026-09-02__auto-market-state-source-admission-v1_1.json` at same SHA | Git blob `322325f23fb6f1bdb7ef1d34dd0d438ef5deea67` |
| Source timing and original 6-cohort | `25_PHASE_II_OCT14_SOURCE_AND_TARGET_CLOCK_CENSUS_20261023.json` | Six original source-clocks, original capture and issue time, 2 older data cases |
| Full original coverage | `29_FULL_70_ORIGINAL_AS_ISSUED_HORIZON_COVERAGE_20261023.json` | 70 original forecasts, 210 horizon slots; no 1–3d or 5–7d UP/DOWN in the cohort |
| Structural exact earlier test | `27_PHASE_II_NEXT12H_B2_STRUCTURAL_IDENTITY_20261023.json` | 256-case sign/gate truth table (NOT full Python runtime replay) |

## Three dependency strata

### 1. Numerical directional kernel (original 12h)

In `auto_market_state.py`, `assemble()` takes actual observed hourly BTC and ETH closes in `normalized_state.live_market`, resolves the **earlier auto packet**, then computes `deltas_since_prior_auto_packet` as `current / predecessor - 1` where predecessor is nonzero. In the original `native_handlekompas.py`:

- `_delta_pct(auto_state, "btc_usdt")` and `_delta_pct(auto_state, "eth_usdt")` read these two deltas.
- `derive_market_now()` labels BULLISH only when **both deltas > 0**, BEARISH only when **both < 0**, NEUTRAL when both equal 0 (unless exact repeated observation), MIXED when they disagree/are incomplete.
- `horizon_map()` maps BULLISH to `NEXT_12H.UP`, BEARISH to `NEXT_12H.DOWN`; it does not numerically vote BTC.D, funding, ETF, sentiment or stablecoins into the 12h UP/DOWN sign at this code version.
- The no-new-hourly-observation check uses **current and predecessor observation-open timestamps**, BTC/ETH delta==0 and ETHBTC delta==0 or unavailable. A repeated source observation is `UNAVAILABLE` (not neutral market direction).

**Caveat:** These are original v3-source instructions at the checked code blob. The six old v2 issues, other model generations, and higher-horizon CN-conditioned directions must NOT inherit this code proof unless their original engine blobs/versions are separately checked.

### 2. Required source-health eligibility graph (must not be dropped)

Original `auto_market_state.py` `decision_lanes(registry)` selects source rows with `decision_context_required != false`; `assemble()` then marks `blockers` for all selected lanes whose health is not PASS and emits `decision_context_status=DEGRADED` if any. The **11 mandatory lanes in the original immutable registry** are:

1. `hourly_market`
2. `live_anchor`
3. `btc_dominance`
4. `derivatives`
5. `breadth`
6. `settled_etf`
7. `stablecoin_liquidity`
8. `macro_risk`
9. `sentiment`
10. `altseason_context`
11. `entry_signal_reference`

`catalyst_context` was optional `decision_context_required=false`; degraded catalyst metadata explains packet `validation_status=DEGRADED` without necessarily blocking `decision_context_status=PASS`. In `native_handlekompas.py`, `_health_ok()` requires validation != FAIL, context PASS, no blockers **AND** original owner freshness passing at issue-time. Otherwise `horizon_map()` emits `UNAVAILABLE` for **all** horizons regardless of numeric BTC/ETH signal. There are therefore **upstream non-price gates that determine eligibility/abstention**, even though only BTC/ETH delta signs determine emitted 12h `UP/DOWN`.

In the 70 original issues, 6 source-stale forecasts originally failed closed, and 4 additional source-PASS 12h issues correctly emitted `UNAVAILABLE` on `UNCHANGED_NO_NEW_OBSERVATION`; this is a narrow original safety observation, not a certified economic benefit.

### 3. Contextual features, forward CN and investment decision

The 24 `evidence_snapshot.selected_features` include breadth, stablecoin, BTC.D, ETF, sentiment, OKX funding and other explainability context. They are **NOT** 24 independent 12h numerical direction predictors, but their owning *lane health* may enter the required availability graph. Specifically original funding `observed_at` sometimes stored scheduled **future settlement** rather than quote observation time; #1749's prospective metadata fix does not rewrite original custody or establish historical provider first-known.

The `NEXT_1_3D` and `NEXT_5_7D` directional labels derive from original weekly **Cycle Navigator structured decision projections** when source health is PASS. Original frozen W41, W42 and W43 CN source versions are all MIXED for these horizons. At source-stale issue-time, both labels are UNAVAILABLE. The original October 12–20 70-record census has zero long-horizon UP/DOWN labels; no directional hit rate can be computed. CN *range forecasts, probability-free risk context, PATH and portfolio action* have distinct scientific/economic contracts.

## Narrowest scientifically honest original R1 source request

For **one outcome-blind, prespecified** original post-prior-block v3 directional issue, collect the following evidence without reading private Round3 outcomes:

| Dependency | Original evidence required | Blocker if absent |
| --- | --- | --- |
| Identity and original issuance | Original immutable forecast blob, self SHA, source packet and exact original issue clock, immutable engine blob; original delivery separated from issue | `ORIGINAL_ISSUE_VERSION_UNKNOWN` |
| Two BTC/ETH price inputs | Original completed hourly current AND prior auto-packet BTCUSDT/ETHUSDT exact source/time/receipt/hash and production code; both available **as of issue**, no later provider version grafted | `PRICE_FIRST_KNOWN_OR_PRIOR_PACKET_UNKNOWN` |
| Observation integrity | Current/prior original hourly observation-open timestamps and no-new-observation branch, no interpolation of omitted/partial hours | `NO_NEW_OBSERVATION_OR_BAR_FINALITY_UNKNOWN` |
| Eligibility source gates | Original 11 required health-lane receipts with exact status and timestamp/vintage, snapshot commits, owner policy/registry and blockers at issue, without assuming provider first-known from a Git timestamp | `REQUIRED_GATE_PROVENANCE_UNKNOWN` |
| Publication time | Original completed capture/upload AND separately authenticated original auto-packet publication/canonical commit/issue relation | `PACKET_OR_FORECAST_ORIGINAL_PUBLISH_UNKNOWN` |
| Frozen outcome definition | Original target close/reference timestamp, complete attempted denominator, missingness and overlap event block; keep prospective holdout separate | `TARGET_CLOCK_OR_INDEPENDENCE_UNKNOWN` |

**Admission rule:** A verified two-delta numerical recomputation + provenance of all original source eligibility gates is needed for an honest 12h *source-function* replay. It still does **not** guarantee original vendor source first-known of all required data, independent event count, a valid causal skill claim or an economic action comparison. Missing evidence remains `NOT_IDENTIFIABLE` or `NOT_ADMITTED`; do not retroactively change original forecasts, feature weights, source blockers, Round3 data or scores.

## Next finite research action, not another model tournament

1. Use the existing owner #1596 and research PR #1747 to attempt one fully timestamped original **v3 directional** R1 decision DAG reconstruction, first ranked by source lineage and issue time only (not ex-post success). The Oct14 13:49:20Z directional original is a plausible source-clock candidate but **not** a claim of unique independent event; check prior overlap and source owner first-known before admitting it.
2. Check original hourly current/prior packets and **11 status gates** against frozen original capture receipts and provider/source first-available bounds. If one gate cannot be authenticated, record exact failure and halt promotion, but retain machine evidence and negative results.
3. After genuine R1 and independent cohorts are available, compare the 12h **availability/abstention policy** against a separately defined *cheap filter control* rather than replaying the same two-delta B2 directional signal and calling zero lift an independent competition.

## Scope and resources

This note is an original-code dependency reconstruction and limited original-source census. It is **not** a new backtest or R1 acceptance. The user-approved pinned HF BTCUSDT 1h source QA remains valid, but the Parquet bytes could not be downloaded in this session; therefore no new C1 historical benchmark is claimed. No HF Jobs/GPU, GitHub Actions dispatch, external API purchase, new task, Grok Bridge check, production write, historical source edit, or portfolio action.