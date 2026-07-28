# BACKTEST BUILD — Wave 1 priority and model division

```yaml
program: FRAMEWORK_BACKTEST_READINESS_BUILD_v1
freeze_date: 2026-07-28
status: PREREGISTERED_PLAN
canonical_execution_owner: CHATGPT_PLUS_GITHUB_ENGINE
external_challenger: CLAUDE_OPUS_5_MAX
claude_role: BLIND_REPLICATOR_PLUS_ADVERSARIAL_EXPERIMENT
final_master_summary: RECEIVED
final_master_exact_bytes_in_active_runtime: NOT_VISIBLE
readiness_gate_G20: NO
economic_execution: LOCKED_PENDING_GATES
framework_state_change: NONE
portfolio_action: NONE
```

## Governing split

ChatGPT owns all truth-bearing tests, owner selection, point-in-time reconstruction, implementation, receipts, graph lineage, adjudication and final governance.

Claude is not the primary backtest engine. Claude receives frozen inputs and contracts for blind replication and adversarial challenge. Claude outputs remain non-binding until artifact parity, source lineage and method comparison have been completed.

The two models must not see each other's results before their respective result hashes are frozen.

## Top five canonical tests owned by ChatGPT

### 1. Point-in-time state and decision replay

**Purpose:** determine whether historical framework state and decisions survive when only information actually available at each timestamp is used.

**Primary outputs:**

- `timestamp`
- `knowledge_cutoff`
- `state_pit`
- `state_latest_vintage`
- `state_divergence_flag`
- `decision_pit`
- `decision_latest_vintage`
- `decision_would_have_differed`
- `missing_knowledge_at_flag`

**Required controls:**

- ALFRED initial-release vintages where available;
- publication lags for FRED and macro series;
- ETF session publication timing;
- settled-only market rows;
- direct-versus-derived authority;
- quarantine of framework events lacking reconstructable `knowledge_at`.

**Primary falsifier:** material state or decision divergence caused by revised or future-known data.

**Priority:** 1.

### 2. Counterfactual deployment and regret ledger

**Purpose:** measure both protection value and false-negative opportunity cost of actual framework policies.

**Frozen policy families:**

- actual framework policy;
- immediate rebuy;
- delayed rebuy at 1, 2, 3 and 5 settled days;
- mechanical 70/30 policy;
- buy-and-hold;
- simple ATR-band policy;
- BTC-specific partial deployment;
- tiered alt deployment.

**Primary outputs per independent event:**

- `event_id`
- `policy_id`
- `entry_timestamp`
- `exit_or_end_timestamp`
- `realized_return`
- `max_drawdown`
- `time_under_water`
- `foregone_return`
- `avoided_loss`
- `regret_sign`
- `turnover`
- `cost_adjusted_result`

BTC and altcoin policies must be scored separately. Overlapping events must not be treated as independent.

**Primary falsifier:** the framework fails to improve downside-adjusted outcome versus simple controls, or confirmation cost dominates protection value.

**Priority:** 2.

### 3. Rotation survival and transition replay

**Purpose:** test the framework's central public and operational edge: distinguishing early transmission from real rotation.

**Sequence:**

`ETH leadership -> direct ETH/BTC persistence -> BTC.D behaviour -> breadth survival -> deployment/flow confirmation -> selective rotation -> broad rotation`

**Required distinctions:**

- direct ETH/BTC versus derived proxy;
- touch versus settled close versus persistence;
- large-cap breadth versus mid/small-cap breadth;
- pre-ETF versus ETF-era segments;
- first signal versus 5-, 10-, 20- and 30-day survival;
- false rotation, slow rotation and unresolved outcomes.

**Primary outputs:**

- sequence start under frozen first-crossing rule;
- survival duration;
- failure node;
- BTC.D reclaim timing;
- breadth survival state;
- deployment confirmation;
- false-positive and false-negative labels;
- opportunity cost by asset tier.

**Primary falsifier:** ETH/BTC plus breadth gates do not materially improve rotation classification or deployable outcomes versus simpler price-only rules.

**Priority:** 3.

### 4. Cycle Navigator range-skill tournament

**Purpose:** determine whether Cycle Navigator ranges add skill beyond mechanical volatility bands.

**Models:**

- frozen Cycle Navigator forecast;
- previous-week range;
- ATR grids;
- EWMA volatility bands;
- realized-volatility random walk;
- GARCH(1,1), where stable;
- split-conformal interval;
- simple unconditional historical quantile band.

**Primary scoring:**

- interval/Winkler score;
- pinball loss for lower and upper bounds;
- daily containment;
- breach count and first-breach timing;
- width ratio;
- direction bias;
- calibration and sharpness;
- CRPS only for genuinely probabilistic outputs.

Containment alone is forbidden as the primary score. Evaluation uses purged chronological walk-forward and an untouched final holdout.

**Primary falsifier:** Cycle Navigator does not outperform simple, width-adjusted baselines after costs of range width and breach timing are included.

**Priority:** 4.

### 5. Sensor independence, effective evidence and ablation graph

**Purpose:** measure how many genuinely distinct evidence dimensions the framework has and which sensors add decision value after price structure is known.

**Methods:**

- correlation and rank correlation;
- PCA/eigenvalue spectrum;
- hierarchical clustering;
- distance correlation where useful;
- conditional mutual information after price and volatility controls;
- leave-one-cluster-out ablation;
- regime-segmented analysis;
- provenance graph from source to feature to event to state to decision to outcome.

No single decimal `effective_N` may be promoted without a frozen estimator, uncertainty interval and robustness analysis.

**Primary outputs:**

- dependency clusters;
- incremental information after price;
- decision changes under ablation;
- outcome changes under ablation;
- sensors that are explanatory only;
- sensors with unique veto or permit value;
- contradiction paths and data-quality dependence.

**Primary falsifier:** most apparent confirmation collapses into one price/structure cluster with no incremental decision value.

**Priority:** 5.

## Claude challenge track

Claude receives two exact-overlap tasks and three orthogonal adversarial tasks.

### Exact overlap A

Blind replication of the Counterfactual Deployment and Regret Ledger on a frozen event subset and frozen policy definitions.

### Exact overlap B

Independent point-in-time leakage audit on the same frozen event subset, without access to ChatGPT's reconstructed states or conclusions.

### Orthogonal challenge C

TDBC specification curve:

- MACD fast/slow/signal surfaces;
- anchor definitions;
- ratio construction;
- venue/source variants;
- share of the specification surface supporting each claim;
- stationary block bootstrap;
- explicit small-N uncertainty.

### Orthogonal challenge D

External-asset validation of business-cycle phase claims using long-history assets such as gold, copper miners, NDX and EM. This tests whether the phase mapping is a general risk-asset relationship or a BTC-specific narrative.

### Orthogonal challenge E

Placebo and negative-control laboratory:

- shifted timestamps;
- permuted labels within valid blocks;
- fake thresholds;
- random sensor bundles with matched complexity;
- alternative event-start rules;
- pre-ETF/ETF-era reversals;
- tests for result sensitivity to one or two influential episodes.

## Comparison protocol

1. Freeze datasets, event IDs, policies, metrics and code/results hash boundaries.
2. ChatGPT and Claude work independently.
3. Neither model receives the other's narrative conclusion before freezing outputs.
4. Compare row parity before comparing prose.
5. Classify disagreements as:
   - data/input mismatch;
   - temporal mismatch;
   - implementation mismatch;
   - statistical-method mismatch;
   - interpretation mismatch.
6. Re-run only the minimal disputed component.
7. Preserve both null and failed results.
8. Final governance belongs to ChatGPT after evidence reconciliation.

## Execution order

```yaml
step_1: final-master byte audit when exact file becomes visible
step_2: owner-registry final freeze
step_3: synthetic statistical-engine validation
step_4: provenance and temporal DAG implementation
step_5: Wave_1 preregistration lock
step_6: run PIT replay
step_7: run counterfactual ledger
step_8: run rotation survival replay
step_9: run range tournament
step_10: run sensor independence and ablation graph
step_11: receive blind Claude artifacts
step_12: reconcile rows and methods
step_13: untouched chronological holdout
step_14: governance conclusions and new research queue
```

## Non-actions

- no rule promotion from historical fit alone;
- no threshold tuning on the final holdout;
- no use of package-supplied preliminary results as evidence;
- no silent substitution of venue, market type or derived series;
- no portfolio action from a backtest result;
- no canonical state change from this plan.
