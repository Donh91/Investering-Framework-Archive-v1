# CROSS-STRATEGY META-LEARNING CONTRACT v1

Status: LOCKED UNTIL EVIDENCE GATE PASSES
Owner: #937
Scientific lifecycle: #885

## Purpose

Learn recurrent edge primitives across independently adjudicated external strategies without turning a collection of marketing claims into false consensus.

This layer is downstream of case-level reverse engineering. It may not be used to rescue a weak individual case.

## Activation gate

Meta-learning remains `LOCKED` until the canonical registry satisfies all three conditions:

1. at least 5 candidates have reached source-alpha adjudication stage;
2. at least 3 candidates have settled source-alpha rulings (`VERIFIED` or `REJECTED`);
3. at least 2 candidates have settled copyability rulings (`VERIFIED` or `NOT_COPYABLE`).

The deterministic gate is implemented in `scripts/experiments/external_alpha_registry.py`.

Current seeded registry has four candidates and therefore must remain locked.

## Independence requirement

Do not count two systems as independent support merely because they have different names.

Before cross-case evidence is combined, record possible dependency:

- shared codebase;
- shared creator/team;
- shared data source;
- shared signal provider;
- copied strategy rules;
- same wallet cohort;
- same venue-specific structural edge;
- same market/regime exposure.

Correlated cases may still be informative but must not inflate evidence count.

## Unit of learning

The unit is a primitive, not a brand.

Candidate primitive families include:

- entry/selection gate;
- explicit no-trade gate;
- feature normalization;
- dynamic feature selection;
- multi-timeframe confirmation;
- regime gating;
- DCA / scale-in logic;
- exit / time-loss logic;
- position sizing;
- execution style / maker-taker preference;
- liquidity/capacity guard;
- provenance / anti-manipulation filter;
- latency-decay model;
- risk veto;
- disagreement / uncertainty gate.

## Evidence table

For each primitive, preserve per-case rows containing:

- candidate ID;
- source-alpha ruling;
- copyability ruling;
- market/venue;
- regime coverage;
- implementation form;
- ablation result;
- effect size after costs;
- uncertainty;
- failure modes;
- version/time window;
- independence notes.

No primitive receives a global score from case count alone.

## Required comparisons

When a recurrent primitive appears across cases, test at least:

1. existing Framework baseline without the primitive;
2. baseline + primitive;
3. source-specific version of the primitive;
4. simplified/generalized version;
5. regime-conditioned version where justified.

Use common clock, cost, latency and data-integrity rules.

## Anti-storytelling rules

Do not conclude that a primitive is universal because:

- two successful bots both mention it;
- it appears in a viral thread;
- it improves in-sample performance;
- an LLM can narrate why it should work;
- multiple dependent systems use the same upstream feed.

A cross-strategy hypothesis must remain falsifiable and earn incremental value in the Framework's own data.

## Transfer decision

A primitive may become `TRANSFER_CANDIDATE` only if:

- at least one external case provides source-level evidence for it;
- the primitive is separable enough for ablation;
- Framework-native testing shows incremental post-cost value;
- failure/kill conditions are explicit;
- no existing owner already provides the same value more simply.

External recurrence raises research priority. It does not grant production authority.

## Long-run objective

Over time, this layer may create an empirical "strategy genome" describing which mechanisms repeatedly survive across different successful systems.

The genome is not a recipe assembled from all discovered tricks. It is a map of independently tested primitives, their regime dependencies, interactions and failure modes.

The desired end-state is a Framework-native strategy architecture whose components were selected because they repeatedly survived falsification, not because any one external bot was famous.
