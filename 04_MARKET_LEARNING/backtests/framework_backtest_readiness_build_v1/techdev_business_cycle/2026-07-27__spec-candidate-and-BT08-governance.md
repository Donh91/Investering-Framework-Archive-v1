# TechDev Business Cycle — exact-spec candidate and BT08 governance

## Status

```yaml
broad_indicator_identity: CORROBORATED
exact_formula_candidate: MACD_12_26_9_OF_COPPER_GOLD_ON_2M_BARS
second_signal_candidate: RSI_14_OF_COPPER_GOLD_ON_2M_BARS
primary_anchor_candidate: JAN_FEB_YEAR_ANCHORED
series_type: RECONSTRUCTION_NOT_VENDOR_SERIES
exact_spec_ratification: PENDING_PRIMARY_ARCHIVE_EXCERPTS
BT08_execution_status: LOCKED
upstream_BT08_results: QUARANTINED
current_positive_bar: IN_PROGRESS_NOT_SETTLED
canonical_state_effect: NONE
```

## Evidence upgrade

The Claude megapack provides:

- executable reconstruction code;
- daily copper and gold inputs;
- both Jan-Feb and Feb-Mar 2M anchor variants;
- MACD line, signal and histogram;
- RSI and Stoch-RSI fields;
- a stated TechDev issue lineage: Issues 62, 65, 67, 69, 75, 85, 86 and 94;
- a corrected color convention claim: histogram above zero is TechDev red, and below zero is TechDev green;
- output values consistent with the previously supplied chart and TDBC package.

This is materially stronger than a visual guess. The exact source excerpts are not embedded in the supplied ZIP, so the formula remains a high-confidence documented candidate rather than a fully ratified primary-source specification.

## Settlement rule

A 2M bar is knowable only after it closes. Plotting or indexing the value at the bar start is allowed for chart alignment, but not for tradable event timing.

```yaml
plot_date: BAR_START_ALLOWED
knowledge_time: BAR_END_REQUIRED
event_time_for_backtest: FIRST_TIMESTAMP_AFTER_SETTLEMENT
in_progress_bar_usage: PROHIBITED
```

The Jul-Aug 2026 Jan-Feb-anchored bar cannot confirm a red flip before settlement at the end of August.

## Anchor sensitivity

The Jan-Feb and Feb-Mar variants disagree about the newest flip. This must be treated as a structural robustness boundary.

Future BT08 must preregister:

1. Jan-Feb as the primary candidate because it is claimed to match the TradingView calendar convention;
2. Feb-Mar as a mandatory sensitivity test;
3. no post-result anchor selection;
4. no indicator promotion if the decision-relevant conclusion depends entirely on anchor choice.

## Why the supplied BT08 result is quarantined

The upstream code creates events from 2M rows indexed at their start dates and measures forward returns from those same dates. The daily phase table also forward-fills the completed bar value from its start date. That leaks up to two months of future information.

Consequently, the supplied event medians, phase medians and drawdowns are descriptive outputs of the reconstruction pipeline, not valid point-in-time backtest results.

## Required controlled BT08 contract

Before execution, BT08 must define:

- primary and sensitivity anchors;
- exact price-source and futures-roll conventions;
- event knowledge time at settled bar end;
- exclusion of incomplete bars;
- event independence and overlapping-window treatment;
- fixed forward horizons;
- pre-institutional versus post-institutional strata;
- multiple-testing and small-sample treatment;
- ETH/BTC transmission tempo as a separately preregistered conditional outcome;
- no market-state or portfolio authority from five to seven events.

## Current interpretation boundary

The reconstruction may become a valuable macro readiness and regime-context layer. It is not currently a timing trigger, rotation confirmation, rebuy permission or portfolio action source.