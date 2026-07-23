# Experiment Enrichment Protocol v1

**Status:** CANONICAL_OPERATIONAL_PROTOCOL  
**Effective:** 2026-07-21  
**Last integrated:** 2026-07-23  
**Owner:** Main Framework / ChatGPT  
**Runtime owner:** Daily Sensor + Swing Lab  
**Scope:** DATA PING, automations, Master Monday, Cycle Navigator, TechDev inputs, Research Lab outputs and independent online market baselines.

## 1. Purpose

Every new market input must contribute to cumulative learning.

The framework must not treat DATA PINGs, automation outputs or online observations as isolated snapshots. Each input is used to:

1. validate and reconcile source quality;
2. append evidence to existing experiments;
3. activate a new experiment only when the hypothesis is materially distinct;
4. preserve exact timestamps, methods, horizons and missing fields;
5. score experiments when their evaluation windows mature;
6. aggregate recurring patterns into reusable framework knowledge.

## 2. Update-existing-first rule

Before creating a new experiment, search active and historical experiments for the same:

- hypothesis family;
- sensor set;
- market regime;
- evaluation horizon;
- confirmation and falsification logic.

If a match exists, append a new evidence row and update maturity status. Do not create duplicate parallel experiments merely because a new DATA PING arrived.

A new experiment is permitted only when at least one of these changes materially:

- causal hypothesis;
- market regime;
- measurement method;
- asset cohort;
- decision horizon;
- confirmation/falsification rule.

## 3. Trigger contract

Run this protocol whenever any of the following appears:

- DATA PING or source packet;
- automation result;
- Master Monday closeout or addendum;
- Cycle Navigator publication or scorecard;
- TechDev update;
- Research Lab package;
- material manual market observation;
- scheduled independent online baseline.

Each trigger must produce either:

- `EXPERIMENT_EVIDENCE_APPENDED`;
- `EXPERIMENT_CREATED`;
- `NO_MATERIAL_EXPERIMENT_DELTA`;
- `EXPERIMENT_MATURED_AND_SCORED`;
- `SOURCE_INPUT_REJECTED_WITH_REASON`.

## 4. Source precedence and replacement rules

Use this priority order:

1. authoritative raw rows from the current source run;
2. primary official source rows;
3. approved API or exchange source;
4. secondary cross-check;
5. deterministic derivation;
6. model interpretation.

Online data may supplement missing DATA PING fields or replace stale/invalid fields, but must never silently overwrite a newer valid raw observation.

When sources conflict:

- preserve both values;
- record timestamps, venue and method;
- identify the preferred value and why;
- mark the field `CONFLICT_PRESERVED` until resolved.

## 5. Minimum independent market baseline

When a DATA PING is absent or incomplete, collect the best available current baseline for:

### Price and structure

- BTC price;
- ETH price;
- direct ETH/BTC;
- recent high/low and gate distances;
- BTC dominance and total market cap when available.

### Flow and positioning

- latest completed BTC and ETH ETF session;
- IBIT and rolling ETF sums when available;
- spot taker flow or approved proxy;
- futures funding;
- open interest and OI delta;
- basis;
- taker buy/sell ratio;
- account and top-position ratios.

### Participation and sentiment

- CFGI Market, BTC and ETH across available horizons;
- 1H, 24H and 7D price breadth;
- large-cap and mid-cap relative participation when measurable.

### Liquidity and macro

- stablecoin supply/history;
- TVL/history;
- market-wide CVD;
- macro core and liquidity indicators;

Missing sensors must remain explicit. No synthetic replacement may be presented as the missing canonical sensor.

## 6. Evidence row requirements

Every experiment update must preserve:

- `observed_at_utc` and local timestamp;
- source snapshot or retrieval receipt;
- source scope and venue;
- method version;
- raw or derived status;
- values used;
- prior value and delta when comparable;
- data quality;
- source conflicts;
- missing fields;
- whether the evidence strengthens, weakens or does not change the hypothesis;
- next evaluation time/window.

## 7. Experiment lifecycle

Allowed statuses:

- `DRAFT`;
- `LIVE`;
- `LIVE_STRENGTHENED`;
- `LIVE_WEAKENED`;
- `MATURED_PENDING_SCORE`;
- `CONFIRMED`;
- `PARTIAL`;
- `FALSIFIED`;
- `INCONCLUSIVE`;
- `RETIRED`.

No experiment may remain indefinitely live after its evaluation window matures. It must be scored or explicitly marked inconclusive with the missing evidence stated.

## 8. Core active experiment families

Maintain and enrich these families when relevant:

- price-range and path accuracy;
- repair survival and retention;
- breakout acceptance versus fakeout;
- ETF durability and price translation;
- spot-flow versus price divergence;
- OI/funding/basis leverage quality;
- ETH/BTC rotation proximity and persistence;
- large-cap accumulation before mid-cap transmission;
- breadth transmission across 1H, 24H and 7D;
- CFGI horizon divergence and subsequent price behavior;
- stablecoin/liquidity lead-lag;
- pullback-warning de-escalation and re-escalation;
- early rotation false-positive and false-negative patterns.

## 9. Capital-transmission ladder

Track evidence separately for:

1. BTC structural leadership;
2. ETH relative leadership;
3. selective large-cap accumulation;
4. broad large-cap participation;
5. mid-cap transmission;
6. small-cap transmission;
7. microcap/meme risk expansion.

Do not infer downstream accumulation solely from BTC or ETH strength. Each tier requires its own participation evidence.

## 10. Scoring and learning

At maturity, score:

- direction;
- range containment;
- timing;
- confirmation sequence;
- false-positive/false-negative result;
- source quality;
- regime compatibility.

Append the result to a cumulative learning ledger. Recurring patterns may graduate into framework rules only after sufficient repeated evidence and explicit ratification.

## 11. Governance boundary

Experiment logging is shadow/non-binding unless separately ratified.

It may not by itself:

- change canonical market state;
- open a portfolio window;
- create a buy/sell instruction;
- alter Cycle Navigator history;
- advance the latest accepted DATA PING pointer;
- override TechDev or Main Framework authority.

## 12. Repository layout

Use:

- `03_WEEKLY_OPERATIONS/forecast_experiments/governance/` for protocols;
- `03_WEEKLY_OPERATIONS/forecast_experiments/registry/` for active pointers;
- `03_WEEKLY_OPERATIONS/forecast_experiments/YYYY-Www/` for experiment definitions and evidence;
- `03_WEEKLY_OPERATIONS/forecast_experiments/scored/` for matured results;
- `03_WEEKLY_OPERATIONS/forecast_experiments/learning/` for cumulative pattern summaries.

All records are append-only except active registry pointers, which may be updated after successful readback.

## 13. Embedded continuous forward-evidence accumulation

Continuous forward-evidence accumulation is a mandatory subroutine of the existing `Daily Sensor + Swing Lab`. It is not a separate scheduler, test or engine.

Every daily run must read and apply:

- `06_RESEARCH_LAB/protocols/2026-07-23__continuous-forward-evidence-accumulation-v1__operational.md`;
- `06_RESEARCH_LAB/forward_tests/shared_evidence/decision_distribution_row.schema.json`;
- `06_RESEARCH_LAB/forward_tests/shared_evidence/decision_distribution_ledger_v1.csv`;
- `06_RESEARCH_LAB/forward_tests/shared_evidence/latest_state.json`.

The embedded subroutine may write only for the existing owners:

- `FRLP_V0_1`;
- `GATE_BTC_PARTIAL_FT_1`;
- `PULLBACK_EDGE_20260708_01_OUTCOMES`;
- `FNP_CUMULATIVE`.

For every eligible real-time observation it must:

1. freeze the source state before the outcome is known;
2. preserve source hash, horizon, benchmark, observation unit, independent-event identity, overlap group and right-censoring;
3. mature only from later verified evidence;
4. preserve MFE, MAE, drawdown, avoided drawdown, missed upside, opportunity cost and false-permission cost where available;
5. keep day-level paths and independent-event summaries separate;
6. use matched observational units for signal and control;
7. leave missing values as `UNKNOWN`;
8. prevent duplicates by evidence ID and source hash;
9. update shared coverage state only after branch, PR, merge and main readback.

A valid source row is not automatically a valid outcome row. A non-divergent observation is not a decision-divergence outcome. Overlapping days from one causal cluster may not count as independent successes.

The normal daily run remains silent when no eligible row or material maturity exists. This embedded function does not consume an additional automation slot.

## 14. Retrospective review cadence

Use the accumulated shared evidence for:

- weekly coverage and maturity reconciliation;
- relationship and baseline review after 20 to 30 new eligible outcomes;
- quarterly distribution, regime-stability, overlap and simplification audits.

Historical event studies and prospective rows must remain separated in every later analysis.

## 15. Embedded-runtime authority boundary

```text
STANDALONE_SCHEDULER: NO
RUNTIME_OWNER: DAILY_SENSOR_PLUS_SWING_LAB
NEW_TEST: NO
NEW_ENGINE: NO
AUTOMATIC_RULE_PROMOTION: NO
MARKET_STATE_CHANGE: NO
GATE_CHANGE: NO
REBUY_CHANGE: NO
PORTFOLIO_ACTION: NO
```
