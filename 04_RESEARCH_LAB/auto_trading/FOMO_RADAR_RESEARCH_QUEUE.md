# FOMO RADAR RESEARCH QUEUE

Status: RESEARCH_ONLY / VERY HIGH PRIORITY
Date: 2026-09-12
Source anchor: `source_notes/AT-SRC-0012_FOMO_RADAR_WALLET_INTELLIGENCE.md`
Candidate role: read-only wallet provenance + cohort intelligence for Alpha Lab / future autonomous research

## Core boundary

Do not connect live capital, signing keys or automatic copy-trading.

The research target is the evidence pipeline, not the X performance story.

## P0 - Independent reproducibility audit

Clone only in an isolated research environment and verify:

- installation from a clean environment;
- unit-test suite;
- data schema migrations;
- Robinhood Chain RPC path;
- deterministic parser/provenance behavior;
- documented request budget;
- MIT attribution obligations.

Record exact commit SHA and test artifacts.

## P0 - Duplicate-coverage audit

Compare FOMO Radar with existing owners before adopting anything:

- 563 / Robinhood Chain research-buddy track;
- Nansen MCP/API research queue;
- current Alpha Lab wallet-cluster logic;
- existing Blockscout / chain RPC access;
- existing meme/token research sources.

For each capability classify:

`ALREADY_OWNED / BETTER_EXTERNAL / COMPLEMENTARY / UNIQUE / NOT_NEEDED`.

Do not build a second wallet database if the value is only one missing transform.

## P0 - Provenance adversarial replay

Independently test the most valuable claim: naive wallet trackers can be fooled by pushed/seeded fills.

Create frozen cases for:

1. true wallet-initiated buy;
2. external direct-router recipient spoof;
3. dust push;
4. many-wallet seeded token;
5. genuine small probe from a normally small wallet;
6. partial / unavailable receipt.

Metrics:
- false smart-money attribution rate;
- false suppression of genuine buys;
- precision/recall by provenance class;
- sensitivity to dust/seed thresholds.

Promotion target:
The provenance transform can be borrowed independently even if the rest of FOMO Radar fails.

## P0 - Point-in-time score calibration

Reproduce the repository's strongest scientific discipline: score first, evaluate only later trades.

Compare:

1. raw leaderboard PnL rank;
2. deterministic wallet-quality score;
3. current LLM score schema;
4. LLM score without headline Fomo PnL;
5. LLM score with regime/context features;
6. random / frequency baselines.

Required corrections:
- market / universe benchmark;
- survivorship accounting;
- minimum sample age/count;
- wallet-cluster dependence;
- realized vs marked outcomes separated.

Do not optimize score thresholds on the same forward window used to grade them.

## P1 - Burst signal frozen-forward test

Pre-register exact burst definition before collection.

Candidate features:
- number of trusted independent wallets;
- score-weighted conviction;
- launch age;
- liquidity at alert;
- entry market cap;
- concentration / top-holder share;
- wallet correlation / shared funding;
- provenance-clean fraction;
- time dispersion of buys.

Evaluate after the alert at fixed horizons, for example:
`+15m / +1h / +6h / +24h / +72h`.

Outcomes:
- executable return after estimated entry delay;
- max adverse excursion;
- max favorable excursion;
- liquidity/capacity;
- rug/honeypot/delist loss where observable;
- probability of 2x is secondary, not the sole metric.

Baselines:
- all new liquid launches;
- random launch matched on age/liquidity/mcap;
- raw wallet-count consensus;
- top-one-wallet signal;
- simple volume/momentum screen.

## P1 - Exit-feed validation

Test whether trusted-wallet exits provide incremental risk information after controlling for price momentum and liquidity deterioration.

Questions:
- Does cohort selling lead drawdown or merely follow it?
- Do partial exits differ from broad liquidation?
- Does exit signal value depend on entry cohort quality?
- Is there value as a protective veto even if it has no standalone short edge?

## P1 - Independence / Sybil audit

Four wallets are not four independent opinions if they share:
- funding source;
- deployer relationship;
- transaction timing;
- social source;
- copy-following pattern;
- common relayer artefact beyond protocol necessity.

Build an effective-independent-wallet count and compare it with raw wallet count.

## P1 - Model ablation

The source markets an AI 'judge', but the core edge may be deterministic data cleaning.

Ablate:
- resolver off/on;
- provenance off/on;
- PnL score only;
- deterministic quality metrics;
- LLM judge;
- cohort aggregation;
- regime context.

The LLM remains only if it adds stable forward information beyond transparent features.

## P1 - Regime segmentation

Segment wallet and burst performance by:
- broad Framework risk state;
- Robinhood Chain launch activity/liquidity regime;
- BTC/ETH market stress vs expansion;
- meme risk-on/off environment;
- token liquidity/mcap bucket.

A single global wallet score should not be assumed stationary.

## P2 - Execution realism research

Only after a signal survives read-only forward testing, simulate:
- detection delay;
- RPC polling delay;
- decision latency;
- pool opening/availability;
- spread/slippage;
- price impact by trade size;
- failed transactions;
- max safe size as fraction of liquidity;
- frontrunning/crowding once signals are public.

No real execution before separate promotion and security review.

## Success condition

Promote individual components only if they add measurable, point-in-time value over existing Framework owners.

Likely best-case outcome is NOT 'copy the bot'.

Likely best-case outcome is:

`better wallet attribution + provenance-clean tape + independent cohort features + frozen-forward Alpha Lab evidence`.

## Kill criteria

Kill or reduce priority if:

- provenance improvements cannot be independently reproduced;
- duplicate-coverage audit shows no material advantage over current/Nansen sources;
- score bands fail to separate future outcomes after benchmark correction;
- burst edge disappears under executable latency/slippage;
- effective independent-wallet count collapses after clustering;
- ongoing maintenance exceeds marginal research value.
