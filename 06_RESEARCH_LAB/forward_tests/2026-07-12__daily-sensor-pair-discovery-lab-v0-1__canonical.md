# Daily Sensor Pair Discovery Lab v0.1

**Dato:** 2026-07-12  
**Status:** CANONICAL_OPERATIONAL_SHADOW_TEST  
**Test ID:** `SENSOR_PAIR_DISCOVERY_LAB_V0_1`  
**Område:** prospective sensor attribution / DATA PING-derived experiments / marginal decision value  
**Primary folder:** `06_RESEARCH_LAB/forward_tests/`  
**Depends on:** Marginal Decision Value & Breadth Truth Program v1, Sensor Survival Audit v1.1, prospective-evidence-ledger v0.1, highest-active-DATA-PING-version rule  
**Authority boundary:** shadow research only; no market call, threshold change, rule promotion or portfolio action

## 1. Purpose

Measure whether predeclared sensor pairs add forward value beyond each component alone and beyond simple baselines. The lab must discover what works in live prospective use, not what can be made to look plausible retrospectively.

## 2. User-interface decision

The user does not operate GitHub. ChatGPT project threads are the user-facing control plane. GitHub is an invisible durable backend.

The prior daily GitHub Issue queue is not the required interface for this test. The lab is driven by user-supplied Custom GPT analyses posted in the newest active DATA PING thread.

## 3. Binding DATA PING thread source rule

The lab may use only data present in DATA PING analyses supplied by the user in Investering project conversations, or a machine handoff derived verbatim from such an analysis.

Resolution order:

1. Find Investering project conversations identified as `DATA PING`, `DATA PING_VN`, `DATA PING VN` or equivalent.
2. Keep only threads containing at least one user-supplied Custom GPT DATA PING analysis.
3. Parse the numeric version and select the highest version actually used.
4. If several threads share that version, select the thread containing the most recent user-supplied DATA PING analysis.
5. Within that thread, select the latest complete analysis message, not the latest casual comment.
6. Freeze source version, thread title, source timestamp, message hash or stable excerpt hash, schema version and data-quality labels before creating rows.
7. If direct project-thread access is unavailable, use `02_DATA_PING/operational_handoffs/latest_thread_source_state.json` only when it explicitly says `THREAD_DERIVED`, identifies the source timestamp/hash and is no more than 36 hours old.
8. If neither path is valid, set `SOURCE_UNAVAILABLE` and create no forecast row.

`Highest version` never means an unused or empty newer thread. `Most recently used` is determined by the timestamp of the latest user-supplied complete DATA PING analysis.

No web search, exchange API, market-data API, Custom GPT invocation or retrospective gap filling is allowed inside this lab. Later DATA PING messages provide the outcome observations.

## 4. Daily run sequence

```text
resolve latest active DATA PING thread
-> validate source completeness and freshness
-> mature due 24h / 72h / 7d outcomes using later DATA PING observations
-> freeze eligible new pair and control rows
-> write dated append-only run artifact
-> update coverage summary and latest state
-> remain silent unless alert criteria are met
```

A day with no new complete DATA PING analysis may mature prior rows if a later valid observation exists, but it may not create duplicate forecasts from the same source message.

## 5. Frozen pair catalog

The canonical machine catalog is `sensor_pair_discovery_v0_1/SENSOR_PAIR_CATALOG.json`.

| Pair | Sensor A | Sensor B | Main question |
|---|---|---|---|
| P01 | ETH/BTC state | point-in-time breadth state | Does the pair improve real-rotation discrimination? |
| P02 | ETF-flow state | price-absorption state | Does the pair distinguish repair from squeeze? |
| P03 | funding/OI state | follow-through state | Does the pair reduce false breakout calls? |
| P04 | stablecoin availability | normalized DEX activity | Does the pair distinguish available from deployed liquidity? |
| P05 | BTC.D survival/reclaim context | ETH/BTC state | Does BTC.D add residual value after relative-strength context? |
| P06 | A1/A2 urgency | C1/C2 lean warning | Does role-correct confluence improve pullback lead without using D as a vote? |
| P07 | sentiment extreme | price absorption | Does sentiment add value only when pressure is absorbed/rejected? |
| P08 | breadth participation | derivatives positioning | Does participation distinguish broad repair from leverage-only movement? |

Existing binding role restrictions remain:

- breadth has zero predictive/action authority;
- BTC.D predictive weight remains zero;
- A3 remains quarantined;
- D remains confirmation/veto and is not an independent pair vote;
- stablecoin supply and normalized DEX activity are distinct availability/activity axes but do not prove deployment;
- missing fields make the relevant pair ineligible rather than negative.

## 6. Required controls

Every eligible pair row must be accompanied by comparable frozen controls:

- sensor A alone;
- sensor B alone;
- price/regime baseline available in the same DATA PING;
- `ALWAYS_WAIT` baseline;
- deterministic placebo label generated from the frozen row ID, never from future outcomes;
- current framework interpretation, recorded separately and never rewritten after the fact.

A pair is useful only if it improves marginal decision value relative to the strongest relevant control, not merely if its raw hit rate exceeds 50%.

## 7. Horizons and outcomes

Frozen horizons:

```text
24h
72h
7d
```

Outcomes may be populated only after the horizon closes and a later source-backed DATA PING observation supplies the required actuals. Required evaluation fields include direction, state persistence, false positive, false negative, lead time, maximum adverse excursion when available, realized move when available, and decision divergence from `ALWAYS_WAIT`.

Overlapping 7-day rows are not treated as independent event windows. Coverage reporting must expose raw rows and effective independent windows separately.

## 8. Decision-value scoring

The lab reports, per pair, component and baseline:

- eligible rows;
- mature rows;
- independent event windows;
- directional hit rate;
- false-positive and false-negative rates;
- Brier score when probabilistic state is available;
- lead-time distribution;
- adverse-excursion distribution when supplied;
- decision divergence count;
- incremental value versus best single sensor;
- incremental value versus price/regime baseline;
- incremental value versus placebo;
- regime and data-quality stratification.

No single blended score may hide severe misses. Raw metrics remain visible.

## 9. Evidence gates

```text
0-9 mature eligible rows: INSUFFICIENT_SAMPLE
10-19: EARLY_SIGNAL_ONLY
20-39 plus >=3 independent windows: FORWARD_CANDIDATE
40+ plus >=5 independent windows, placebo beaten, best single sensor beaten,
and no concentrated severe-failure mode: GOVERNANCE_REVIEW_PERMITTED
```

Passing a gate permits review only. It does not promote a sensor, change weights, alter a threshold or authorize action.

Multiple-testing control is mandatory. The lab must report the full frozen catalog, including failed pairs; it may not publish only the best-performing pair.

## 10. Storage contract

```text
06_RESEARCH_LAB/forward_tests/sensor_pair_discovery_v0_1/
  SENSOR_PAIR_CATALOG.json
  sensor_pair_row.schema.json
  latest_state.json
  runs/YYYY-MM-DD__sensor-pair-run.json
  coverage/coverage_summary.json
```

Daily run artifacts are append-only. `latest_state.json` and `coverage_summary.json` are replaceable pointers backed by dated run artifacts.

## 11. Notification policy

Normal successful runs are silent. Notify only for:

- three consecutive `SOURCE_UNAVAILABLE` runs;
- source-version regression or thread-selection conflict;
- schema or hash inconsistency;
- duplicate/frozen-field mutation attempt;
- a pair reaching `FORWARD_CANDIDATE` or `GOVERNANCE_REVIEW_PERMITTED`;
- a material severe-failure concentration that invalidates an apparent edge.

## 12. Current initialization state

```yaml
test_status: ACTIVE_SHADOW_PILOT
highest_known_data_ping_version: V4
latest_exact_source_row: PENDING_NEXT_DIRECT_THREAD_CAPTURE
prospective_rows_created_at_initialization: 0
retrospective_rows_promoted: 0
rule_promotion: NONE
portfolio_authority: ZERO
```

The first valid row must come from a newly resolved source-backed DATA PING analysis. Existing conversation summaries are not silently converted into prospective rows.