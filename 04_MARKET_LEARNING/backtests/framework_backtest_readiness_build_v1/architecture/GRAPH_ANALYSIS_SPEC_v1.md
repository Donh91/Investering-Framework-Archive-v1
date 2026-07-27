# BACKTEST GRAPH ANALYSIS SPEC v1

```yaml
spec_id: BACKTEST_GRAPH_ANALYSIS_SPEC_v1
status: DESIGN_FROZEN_EXECUTION_LOCKED
purpose: DIAGNOSTIC_AND_RESEARCH_ONLY_UNTIL_REPLICATED
```

## 1. Why graph analysis belongs in the Backtest Build

The framework is a network of sources, derived features, gates, events, states and decisions. Pairwise tests alone cannot show:

- which sensors are merely different names for the same information;
- which signals arrive first and which only confirm afterward;
- which combinations repeatedly precede successful transitions;
- which contradiction patterns precede false transitions;
- where a lookahead path or hidden source dependency enters the system;
- which states are stable and which are short-lived narrative labels.

Graph analysis is therefore used as a structural diagnostic. It does not create causal claims by itself.

## 2. Graph families

### G1. Provenance DAG

Node classes:

- source endpoint or archived artifact;
- receipt and raw payload;
- normalized dataset;
- feature;
- event;
- test;
- result;
- conclusion;
- framework recommendation.

Required edge fields:

- transformation method;
- code version;
- input hash;
- output hash;
- event time range;
- maximum input knowledge time;
- authority role;
- direct, derived or proxy class.

Blocking conditions:

- cycles in the provenance DAG;
- conclusion without a path to owner data;
- feature without method identity;
- test result depending on a quarantined preliminary output.

### G2. Temporal dependency DAG

Every edge carries `available_at_utc` or a deterministic availability rule.

For each decision node, calculate the latest upstream knowledge time. The path fails if any upstream value becomes available after the decision.

Red-team fixtures must include:

- same-day ETF flow used before US close;
- monthly FRED average used before month-end;
- annual FRED average used before year-end;
- 2M business-cycle bar used at bar start;
- in-progress candle treated as settled;
- future universe membership used in historical breadth.

### G3. Sensor redundancy graph

Nodes are point-in-time features. Edges are calculated separately for each walk-forward era and regime.

Edge diagnostics:

- Pearson and Spearman correlation;
- rank correlation of changes;
- conditional mutual information estimate;
- shared missingness;
- same-source dependency;
- partial correlation after controlling for BTC return and volatility;
- sign and magnitude stability across folds.

A high correlation does not automatically remove a sensor. Removal requires ablation evidence that the sensor adds no incremental out-of-sample value or interpretability.

### G4. Lead-lag network

Candidate lags must be preregistered. Default diagnostic grid:

- 1, 2, 3, 5, 7, 10, 20 and 30 settled sessions;
- 1 and 2 completed months for macro series;
- completed 2M bars for business-cycle data.

Each directed edge must record:

- source node;
- target outcome or event;
- lag;
- sample count;
- independent episode count;
- training-fold effect;
- validation-fold effect;
- final holdout effect;
- uncertainty interval;
- multiple-testing adjusted status;
- era stability.

Edges discovered only in full-sample exploration remain `EXPLORATORY_ONLY`.

### G5. Event co-occurrence graph

Nodes are preregistered events such as:

- direct ETH/BTC transmission candidate;
- 0.0300 settled gate;
- 0.0275 failure;
- breadth confirmation or conflict;
- ETF inflow or outflow state;
- funding and OI state;
- flush event;
- repair event;
- business-cycle transition;
- framework state change.

Edges represent same-episode co-occurrence within a frozen time window. Results must distinguish:

- simultaneous conditions;
- lead condition;
- confirmation condition;
- veto condition;
- post-event consequence.

### G6. State-transition graph

Nodes are framework states. Directed edges are observed transitions.

Required metrics:

- transition count;
- transition probability;
- median state duration;
- survival curve;
- transition timing error versus retrospective outcome;
- forbidden transitions;
- false-transition rate;
- missed-transition rate;
- action authority associated with each state.

The graph cannot be treated as a Markov model until the state process and observation interval justify that assumption.

### G7. Contradiction graph

Nodes are sensors or state assertions. An edge represents systematic disagreement.

Examples:

- ETH/BTC strengthening while breadth contracts;
- price repair while ETF flow deteriorates;
- price strength while OI deleverages;
- macro reconstruction improving while point-in-time official data are unavailable;
- CFGI improvement while risk breadth weakens.

Contradiction edges are grouped by outcome:

- successful transition;
- failed transition;
- delayed transition;
- unresolved or censored event.

The purpose is to learn which disagreements are healthy absorption and which are hidden deterioration.

### G8. Failure-path graph

A failure path begins at a candidate event and ends at confirmation, invalidation or censoring.

Example path:

`ETHBTC candidate -> intraday 0.0300 touch -> no settled confirmation -> breadth contraction -> ETH OI decline -> fallback`

Required outputs:

- common failure sequences;
- time between nodes;
- conditional failure hazard;
- earliest reliable veto;
- false veto frequency;
- missing-data nodes that prevent adjudication.

## 3. Graph construction rules

1. No graph is built from silently forward-filled event data.
2. Missing observations are represented as missingness nodes or absent edges, not zero.
3. All edge weights include sample size.
4. Overlapping windows are clustered into episodes.
5. Regime and era graphs are reported separately before any pooled graph.
6. Venue-specific derivatives remain separate layers.
7. Graph structure learned on training data is evaluated on validation and holdout periods.
8. Edge pruning thresholds are frozen before holdout.
9. No centrality metric receives framework authority.
10. All graph artifacts must be reproducible from owner dataset hashes and code version.

## 4. Required artifacts

- `provenance_nodes.csv`
- `provenance_edges.csv`
- `temporal_dependency_failures.csv`
- `sensor_redundancy_edges.csv`
- `lead_lag_edges.csv`
- `event_cooccurrence_edges.csv`
- `state_transition_edges.csv`
- `contradiction_edges.csv`
- `failure_paths.csv`
- `graph_run_manifest.json`
- static PNG or SVG renderings for audit convenience;
- machine-readable GraphML or JSON graph export.

## 5. Promotion boundary

Graph evidence may:

- identify redundant sensors;
- identify candidate sequencing rules;
- identify missing-data bottlenecks;
- propose a new hypothesis;
- propose an ablation test;
- improve archive retrieval and lineage.

Graph evidence may not by itself:

- change a threshold;
- promote rotation;
- unlock rebuy or entry;
- change a portfolio rule;
- claim causality;
- create a canonical sensor.

Any graph-derived hypothesis must enter the test matrix as a new preregistered challenger and use untouched data where possible.
