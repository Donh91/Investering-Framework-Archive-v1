# T2 Sminston BTC Challenger - Source Lineage Audit v0.1

**Date:** 2026-08-31  
**Status:** SOURCE_AUDIT / SHADOW_TESTING  
**Candidate:** `SMINSTON_BTC_CHALLENGER_V0_1`

## 1. Purpose

This audit separates reproducible data from author-derived and unavailable data before any forward evidence is scored.

The source question is not whether a chart looks credible. It is whether a point-in-time observer can freeze the exact information required to reproduce or audit the candidate's decision.

## 2. Source classes

### REPRODUCIBLE

A value or formula can be independently captured from a public point-in-time source with sufficient lineage.

### AUTHOR_DERIVED_WITH_REPRODUCIBLE_INPUTS

The underlying inputs are public/reproducible, but the exact transformed value depends on an author-specific calculation or parameter choice.

### AUTHOR_DERIVED

The result is visible or described by the author, but the exact calculation or history cannot currently be independently reproduced.

### DATA_BLOCKED

The point-in-time value or required semantics are not publicly available enough to produce an auditable test row.

## 3. Structural valuation family

### q05 power-law quantile

**Class:** REPRODUCIBLE_FORWARD_ONLY

Public source:

- https://www.sminstonwith.com/retirement-guide

Captured public formula on 2026-08-31:

```text
q05_price = 2.952e-18 * d^5.8837
```

where `d` is days since 2009-01-03.

Important source behavior:

- the author states that quantile models are refit over time,
- the site provides cutoff / blind-projection tools,
- therefore current coefficients are not historical point-in-time coefficients.

Consequence:

- current q05 is valid for forward capture,
- current q05 formula is invalid for a historical pseudo-backtest unless an archived historical formula is recovered.

### q10 power-law quantile

**Class:** DATA_BLOCKED_AT_REGISTRATION

The concept is public, but an exact q10 formula/value sufficient for independent point-in-time replay was not recovered during this audit.

### OLS residual

**Class:** DATA_BLOCKED_AT_REGISTRATION

The public site describes the OLS power-law model and approximate exponent behavior, but the exact point-in-time residual series needed for the proposed challenger was not recovered in a reproducible form.

### Decay Channel position / oscillator

**Class:** AUTHOR_DERIVED / MEMBER_DEPENDENT

Public source family:

- https://www.sminstonwith.com/chart

The methodology and role are described publicly, but exact decision-ready current and historical point-in-time values are member-gated or otherwise unavailable in the public audit path.

Consequence:

- may be source-captured prospectively if exact values become accessible,
- no historical reconstruction may be called the author's Decay signal,
- no trim threshold may be fitted after outcomes.

## 4. Bottom-quality family

### Bitcoin Research Kit / Bitview

Primary independent data source:

- https://bitview.space/
- https://github.com/bitcoinresearchkit

Audit finding:

BRK/Bitview exposes public daily Bitcoin series derived from Bitcoin Core / on-chain calculations. Direct API retrieval was verified for BTC close, MVRV and LTH supply in loss.

This makes the raw bottom-quality family substantially more reproducible than relying on Sminston screenshots.

### BTC close

**Class:** REPRODUCIBLE

Verified API series:

`price_close`

### MVRV

**Class:** REPRODUCIBLE_RAW

Verified API series:

`mvrv`

Author MVRV Z-score:

**Class:** AUTHOR_DERIVED_WITH_REPRODUCIBLE_INPUTS

Public Sminston source:

- https://www.sminstonwith.com/chart/mvrv-zscore

The raw market/realized-cap family is reproducible through BRK, while the exact Z transform is author-derived and must be captured as a point-in-time author value unless independently reimplemented and versioned.

### LTH supply in loss

**Class:** REPRODUCIBLE_RAW

Verified API series:

`lth_supply_in_loss_share`

For test purposes, the expanding percentile must be calculated only from observations available through the row timestamp. Full-sample percentile ranks displayed today may not be used as historical point-in-time ranks.

### CVDD

**Class:** AUTHOR_DERIVED_WITH_REPRODUCIBLE_INPUTS

Public Sminston source:

- https://www.sminstonwith.com/chart/cvdd

Current site implementation uses Bitcoin Research Kit coin-days-destroyed / price inputs and an empirical scaling choice. The underlying input family is reproducible, but this audit did not independently reconstruct the exact author series end to end.

Consequence:

- author value may be captured forward with timestamp and source,
- independent reconstruction requires a separately versioned transform and equivalence test before it can replace author snapshots.

## 5. Macro-relative mispricing family

### Copper/Gold versus detrended BTC residual

**Class:** AUTHOR_DERIVED / MEMBER_DEPENDENT

Publicly described, but exact point-in-time residual value and complete transform were not recovered in a sufficiently auditable form.

### ISM PMI versus detrended BTC residual

**Class:** AUTHOR_DERIVED / MEMBER_DEPENDENT

Publicly described, but exact point-in-time residual value and complete transform were not recovered in a sufficiently auditable form.

### MODEM

**Class:** AUTHOR_DERIVED / MEMBER_DEPENDENT

Public description indicates a fusion of Bitcoin decay / oscillator information with the sign or regime of ISM PMI into a bounded macro-cycle indicator. The exact transform and current/historical point-in-time values are not public enough for an independent historical reconstruction.

Consequence:

- MODEM is source-capture only until exact values are available,
- no reconstructed proxy may be labelled `MODEM`,
- proxy research, if ever performed, must be separately named and preregistered.

## 6. Point-in-time source binding standard

Every eligible Sminston row must store:

```text
source_url
retrieved_at_utc
source_observation_date_or_timestamp
metric_name
metric_value
metric_unit
source_class
formula_or_transform_version
formula_coefficients_when_applicable
raw_input_series_ids_when_available
content_or_snapshot_hash_when available
availability_state
```

If the site and BRK publish slightly different same-day prices because of update cadence, the row must not silently reconcile them. It must bind the exact price used by the candidate and record the alternative source separately.

## 7. Prohibited practices

The following invalidate a row:

- applying today's refit coefficients to old dates and calling the result point-in-time evidence,
- using today's full-history percentile to score an old row,
- reconstructing a paid metric from similar public variables and calling it the author's metric,
- substituting an updated source value after the row was frozen,
- mixing source timestamps without an explicit cutoff rule,
- using ecosystem data to repair a BTC-only candidate row.

## 8. Audit conclusion by family

```yaml
structural_valuation:
  q05: REPRODUCIBLE_FORWARD_ONLY
  q10: DATA_BLOCKED
  OLS_residual: DATA_BLOCKED
  Decay_Channel: AUTHOR_DERIVED_MEMBER_DEPENDENT

bottom_quality:
  BTC_close: REPRODUCIBLE
  MVRV_raw: REPRODUCIBLE
  MVRV_Z: AUTHOR_DERIVED_WITH_REPRODUCIBLE_INPUTS
  LTH_supply_in_loss: REPRODUCIBLE
  CVDD: AUTHOR_DERIVED_WITH_REPRODUCIBLE_INPUTS

macro_relative:
  CuAu_residual: AUTHOR_DERIVED_MEMBER_DEPENDENT
  PMI_residual: AUTHOR_DERIVED_MEMBER_DEPENDENT
  MODEM: AUTHOR_DERIVED_MEMBER_DEPENDENT
```

## 9. Research implication

The public data are sufficient to start a rigorous q05 structural subtest and a bottom-quality forward capture program.

They are not sufficient to claim that the complete Sminston package has been backtested.

The correct status is therefore:

`PARTIALLY_TESTABLE_FORWARD_ONLY`.
