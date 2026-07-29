# Agent Work Packages

## Execution rule

Packages are ordered. Agents may prepare later-stage code, but may not publish economic conclusions before prerequisite data, leakage and holdout gates pass. Every delivery must include hashes, source receipts, row counts, time coverage, missingness, transformations, exclusions and known limitations.

## MAR-WP01 — Program inventory and overlap audit

Map all existing sensors, shadow layers, Global Liquidity work, DATA PING fields, Forecast Ledgers, Master Monday inputs, Research Lab outputs and backtest assets.

Deliver:
- overlap matrix;
- reusable data inventory;
- missing data inventory;
- dependency graph;
- no-duplication ruling per proposed feature.

## MAR-WP02 — Liquidity Routing Map

Construct point-in-time flow pathways across:
- ETF primary and secondary demand;
- Coinbase premium and venue basis;
- CME basis and positioning;
- spot taker flow and order-book depth;
- stablecoin issuance, redemption and exchange balances;
- BTC to ETH transmission;
- ETH/BTC;
- breadth by liquidity tier;
- DeFi TVL, DEX volume and bridge flows;
- large, mid, small and micro-cap response.

Methods:
- distributed-lag models;
- transfer entropy as exploratory evidence only;
- Granger-style tests with stationarity controls;
- event studies;
- state-dependent lead-lag networks;
- purged walk-forward validation.

Output candidate: Routing Confidence Score, initially research-only.

## MAR-WP03 — Failed Move Library

Build a labelled event library of:
- failed breakouts and breakdowns;
- failed ETH/BTC reclaims;
- ETF-flow/price divergence;
- funding and OI traps;
- gamma pin and expiry distortions;
- breadth non-confirmation;
- stablecoin growth without market transmission;
- liquidity signals invalidated by macro shocks.

For each event preserve pre-event, trigger, confirmation window, failure window, maximum favourable excursion, maximum adverse excursion and invalidation mechanism.

Required analysis:
- first 6h, 12h, 24h, 48h and 72h signatures;
- nearest-neighbour retrieval;
- survival/hazard model for signal failure;
- false-positive decomposition by regime.

## MAR-WP04 — Liquidity Stress Propagation

Study whether stress follows a repeatable order through:
ETF flows → basis → funding → OI → spot depth → ETH/BTC → breadth → lower-liquidity assets.

Deliver:
- propagation DAG;
- delay distributions;
- bottleneck and amplification nodes;
- reversal paths;
- stress-severity taxonomy;
- early-warning candidates.

Competing paths must include macro shock, exchange-specific shock, leverage-only flush and crypto-native credit event.

## MAR-WP05 — Market DNA Library

Create a versioned regime/event library spanning at minimum:
- 2015 recovery;
- 2017 expansion and distribution;
- 2018 capitulation;
- 2019 rebound;
- March 2020;
- 2020–2021 liquidity expansion;
- 2021 distribution;
- Luna/3AC;
- FTX;
- 2023 recovery;
- ETF approval and post-ETF era;
- Treasury-company era;
- current transition.

Represent each era as sequences of states, not static averages. Include macro, liquidity, price, breadth, derivatives, sentiment, on-chain and institutional dimensions with source availability flags.

Methods:
- hidden/semi-Markov models as challengers;
- change-point detection;
- dynamic time warping for sequence similarity;
- leave-one-era-out validation;
- recurrence and contradiction analysis.

## MAR-WP06 — Opportunity Cost Ledger

Reconstruct every material WAIT, HOLD, REDUCE, EXIT and REBUY decision that can be supported by archived evidence.

Measure:
- avoided drawdown;
- missed upside;
- time out of market;
- re-entry delay;
- decision calibration;
- utility under the user's asymmetric preference: missing the last 10–20% is preferable to a 60–80% drawdown.

No hindsight optimisation. Use only information known at each decision timestamp.

## MAR-WP07 — Regime Transition Atlas

Model transitions among:
Fear → Absorption → Compression → Expansion → Acceleration → Distribution → Deterioration.

Deliver:
- operational state definitions;
- transition probabilities;
- duration distributions;
- skipped-state and loop frequencies;
- precursor features;
- uncertainty intervals;
- regime disagreement diagnostics.

The atlas must permit UNKNOWN and MIXED states rather than forcing every observation into a clean narrative.

## MAR-WP08 — Institutional Behaviour Atlas

Study behaviour rather than personalities:
- ETF issuers and authorised participants;
- CME asset managers, leveraged funds and dealers;
- options dealers;
- treasury companies;
- stablecoin issuers;
- large holders and exchange-linked wallets where attribution is robust.

Separate observable action, inferred motive and unsupported narrative. No actor-level conclusion without reproducible attribution.

## MAR-WP09 — Cross-track incremental value

Compare each candidate against the current framework baseline.

Required metrics:
- Brier score and log loss for probabilistic outputs;
- calibration slope/intercept;
- precision/recall for rare downside events;
- lead time gained;
- false-alarm burden;
- maximum drawdown utility;
- incremental information conditional on existing sensors;
- stability across eras and data sources.

## MAR-WP10 — Independent replication and final archive report

A separate agent receives frozen inputs, contracts and hashes without access to the first analyst's conclusions.

Final ruling per track:
- promote to prospective shadow candidate;
- retain as contextual research;
- merge into an existing sensor;
- continue research due to insufficient evidence;
- reject.
