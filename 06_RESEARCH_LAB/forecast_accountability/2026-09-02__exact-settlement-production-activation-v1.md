# Exact Settlement Production Activation v1

Status: PROSPECTIVE_SHADOW_ACTIVATION
Date: 2026-09-02

## Purpose

Activate the exact-settlement infrastructure from PR #721 and PR #722 for newly created, scientifically admitted price-family forecasts without changing or reclassifying any historical forecast or outcome.

## Frozen-at-creation rule

The active experiment forecast producer may attach `FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1` only while creating a new `FROZEN_FORECAST_v1`, before its first canonical persistence.

Eligibility is bounded to the shared settlement price-family whitelist. Unsupported metrics remain on their existing settlement semantics.

Existing tracked forecasts are not scanned, tagged, migrated or rewritten. Forecasts created before this activation remain historical legacy observations even when their metric path would be supported today.

## Maturation separation

Exact-settlement forecasts are adjudicated only through the forecast-bound settlement evidence lane:

`FORECAST_SETTLEMENT_PRICE_OWNER_v1`
-> `FORECAST_SETTLEMENT_EVIDENCE_v1`
-> canonical `outcome_maturation_engine.py`
-> `FORECAST_SETTLEMENT_OUTCOME_BINDING_v1`

The wrapper presents the canonical maturation engine with exactly one forecast and its own evidence document. Evidence belonging to another forecast cannot compete merely because target timestamps match.

Before legacy maturation, a fail-closed subset builder removes every forecast declaring `FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1`. The legacy first-capture-after-due path therefore cannot adjudicate an exact-settlement forecast.

## Scientific authority boundary

Correct settlement is necessary evidence infrastructure, not a forecast-skill result.

This activation grants no:
- portfolio authority,
- framework-state authority,
- model-weight authority,
- automatic promotion,
- historical rescore authority,
- scientific skill authority.

G3/G4, replication quality, baseline comparison, dependence-adjusted power and subsequent forward evidence remain independent gates.

## First-production acceptance

After merge, the first newly created supported price-family forecast must be read back from `main` and show:

- `scientific_admission.status = QUALIFIED_FOR_FORWARD_TEST`,
- `settlement_contract_version = FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1`,
- `settlement_activation_semantics = FROZEN_AT_CREATION_PROSPECTIVE_ONLY`,
- a future `outcome_due_utc`,
- no historical file mutation.

A matured production outcome must not be claimed until its frozen future due time has actually passed and settlement evidence has been collected from a fully closed source candle.

## Failure policy

Missing, unavailable, unconfirmed, schema-incompatible, future or hash-mismatched settlement evidence fails closed. Retrieval delay never moves the adjudicated target observation.
