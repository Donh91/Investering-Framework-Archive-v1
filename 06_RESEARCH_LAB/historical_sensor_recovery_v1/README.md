# Historical Sensor & Research Recovery Audit v1

Status: RESEARCH_ONLY
Authority: NON_CANONICAL
Portfolio execution: FORBIDDEN
Automatic rule/threshold/weight changes: FORBIDDEN

## Purpose

Recover old sensors, signals, hypotheses, shadow layers, research artifacts and forward-test concepts already present in the repository/archive, then classify them before any reactivation.

The goal is not to revive old logic blindly. The goal is to create a durable shadow-learning surface that can answer, over time:

- did this sensor lead existing canonical evidence,
- was it redundant,
- was it noisy,
- did it only work in one regime,
- did it improve timing around pullbacks/reloads/rotation,
- does it deserve a prospective forward test.

## Bounded workflow

1. Inventory archived/research/shadow material.
2. Recover the contemporaneous definition, provenance and intended horizon where possible.
3. Classify each candidate as one of:
   - ACTIVE_CANONICAL
   - ACTIVE_SHADOW
   - DORMANT_RECOVERABLE
   - RESEARCH_ONLY
   - SUPERSEDED
   - UNTESTABLE
4. Backfill only where source data and historical definition support it.
5. Never use an outcome discovered later as if it were available at the original decision time.
6. Promote selected recoverable candidates into passive shadow runtime only.
7. Mature outcomes automatically.
8. Score weekly marginal/incremental value versus the canonical stack.
9. Any promotion beyond shadow requires separate prospective review.

## Existing architecture this audit must reuse

The repository already contains `04_MARKET_LEARNING/entry_signals/` with immutable events, state, outcomes and performance summaries. This audit must extend that learning pattern instead of building a competing system.

The repository also already contains historical/shadow forward-test artifacts, breadth forward material, Cycle Navigator, DATA PING learning, forecasts, experiments and external research. These are first-class recovery sources.

## Required anti-overfit rules

- no historical hindsight masquerading as a live signal,
- no automatic threshold optimization,
- no survivor-only relabeling without disclosure,
- no promotion from historical fit alone,
- no double-counting redundant sensors as independent confirmation,
- no canonical decision impact from this layer,
- all source gaps remain explicit.

## Intended long-run output

A `SHADOW_SENSOR_REGISTRY.json` plus weekly evidence summaries that classify each candidate as:

`KEEP`, `WATCH`, `REDUNDANT`, `NOISE`, `REGIME_SPECIFIC`, `UNTESTABLE`, or `PROMOTION_CANDIDATE`.

`PROMOTION_CANDIDATE` means only that a separate forward-test proposal may be opened. It never changes live framework semantics automatically.
