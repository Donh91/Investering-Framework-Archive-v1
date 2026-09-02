# Historical Outcome Supersession Overlay v1

Status: REPLAY_DIAGNOSTIC_ONLY
Date: 2026-09-02

## Purpose

Correct the evidentiary interpretation of historical forecast outcomes produced under superseded resolver or settlement-time semantics without mutating, deleting or silently replacing any original outcome.

## Frozen replay population

Replay eligibility is defined **without using the original verdict**.

A row is eligible when all of the following are true:

1. the source object is an existing `FROZEN_FORECAST_v1`;
2. an existing `MATURED_OUTCOME_v3` is present for the same forecast id;
3. the original outcome lineage matches the immutable forecast hash when that hash is declared;
4. the forecast does not already declare `FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1`;
5. the metric belongs to the shared supported exact-settlement price family;
6. the target-unit contract is compatible with `FORECAST_TARGET_UNITS_v2` or predates the explicit field without declaring a conflicting contract.

The population therefore includes historical HIT, MISS and CENSORED outcomes symmetrically. Selection does not target the known blackout or only adverse outcomes.

## Replay mechanics

For each eligible row, the replay lane creates a deterministic replay envelope derived from the immutable original forecast. The envelope adds exact-settlement semantics only inside the replay lane and binds the original forecast SHA-256.

The historical settlement owner then retrieves the last fully closed 1-minute source candle at or before the frozen due time. Raw provider bytes and source clocks are retained and hash-bound.

The canonical `outcome_maturation_engine.py` is reused through the forecast-bound exact maturation wrapper. Replay outcomes are written only to a dedicated replay root, never to canonical `outcome_memory`.

## Supersession overlay

`FORECAST_OUTCOME_SUPERSESSION_v1` binds:

- original forecast path and SHA-256,
- original outcome path and SHA-256,
- original verdict and recorded settlement metadata,
- deterministic replay-envelope SHA-256,
- exact replay evidence path and SHA-256,
- replay outcome path and SHA-256,
- whether the terminal verdict changed.

Every overlay declares `supersedes_without_mutating=true`.

## Authority boundary

Historical replay is diagnostic and is not forward evidence. It has no portfolio, framework-state, model-weight, canonical-promotion, scientific-skill or historical-rewrite authority.

Replay results may identify broken evidence, quantify timing bias and support remediation. They may not be used as retrospective proof of forecast skill.

## Operational bounds

Framework Learning Operations attempts at most 10 new historical replays per run. The ceiling applies to attempts, not successes, preventing provider outages from expanding into an unbounded historical crawl.

The replay step is `continue-on-error`. Source failure cannot block current production learning operations. Successful immutable replay artifacts from the same run remain eligible for persistence.

Production workflow calls never enable fixture mode. Fixtures exist only for CI.

## Acceptance gates

Before merge:

- live-repository no-network census must complete without original lineage mismatch;
- fixture integration must prove an original CENSORED outcome can replay through the real owner + canonical maturation path to a different verdict without changing either original file;
- idempotent replay must return no-op;
- exact-settlement forecasts must be excluded from the historical population;
- production workflow must preserve the 10-attempt ceiling and omit fixture mode;
- existing settlement and historical replay guards must remain green.
