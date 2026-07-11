# TechDev Historical Outcome Scoring Protocol v1

**Date:** 2026-07-11  
**Status:** CANONICAL / FROZEN_FOR_WAVE_1  
**Scope:** Historical TechDev roadmap, timing, range, rotation, topping-signal and trade claims

## Objective

Score original claims honestly without allowing later revisions, broad language or model replacement to retroactively improve them.

## Source precedence

```text
1. User-verified project actuals and frozen exchange or market-data ledgers
2. Yahoo Finance BTC-USD daily OHLC archive held in the project File Library
3. Investing.com BTC and ETH daily historical data held in the project archive
4. Source-backed later TechDev issue only for a reported action or revision, never as independent market actual
5. Memory or unsourced summaries are not eligible actuals
```

A row is `NOT_EVALUABLE` when the required actual series or action record is missing.

## Sampling conventions

### Price targets and ranges

- Use daily high and low for whether a target or range was touched.
- Use daily close only when the original claim explicitly required a close.
- A terminal-top or terminal-bottom claim is not supported merely because the range was visited before price later made a materially higher high or lower low within the same declared cycle window.
- A near miss is `PARTIAL` only if the distance to the nearest boundary is 5% or less and the directional window was otherwise correct.

### Timing

- Use the exact stated window.
- Month-only claims run from the first through the final calendar day of that month.
- Q1/Q2 means January 1 through June 30 unless the source narrows it.
- “This week” means publication time through the following Sunday UTC.
- “In the next N weeks” begins at publication time.
- An open-ended “eventually” claim is not timing-scorable.

### Roadmap

Roadmap scoring requires a falsifiable sequence or directional state. A broad bullish statement receives no credit merely because price was higher years later.

### Rotation

Rotation requires material relative outperformance in the stated window and must be tested with the exact referenced pair or dominance series. A single ETH/BTC cross or one strong alt day is insufficient.

### Topping signals

Mechanical threshold state and analyst interpretation are scored separately:

```text
MECHANICAL_TRIGGER
PROVISIONAL_TRIGGER
ANALYST_OVERRIDE
ACTION_RECOMMENDATION
```

A local heat signal can be useful without identifying the macro top. These outcomes must not be blended.

### Trades

A trade needs:

```text
entry
entry_time_or_executable_window
stop
profit_target_or_exit_rule
instrument
```

Daily leveraged ETF path dependency is included. Author-reported PNL is not accepted as verified performance without independent price data.

## Outcome labels

```yaml
SUPPORTED:
  definition: Core claim and stated window were met without violating the original invalidation.

PARTIAL:
  definition: Direction or region had useful value, but timing, magnitude, terminal classification or action quality was materially incomplete.

NOT_SUPPORTED:
  definition: Target, range, sequence or timing window failed, or the original invalidation was reached.

NOT_EVALUABLE:
  definition: Claim was not falsifiable as written or required actual data are absent.

OPEN:
  definition: Original window has not matured by the audit cutoff.
```

## Revision treatment

```text
Original row is scored against its original window.
A revised target receives a new row.
A timing extension receives a new row.
A changed analogy receives a new model row.
A moved invalidation does not prevent the original invalidation from being scored.
A later correct call does not repair an earlier miss.
```

## Category baselines

| Category | Baseline |
|---|---|
| Broad direction | Buy-and-hold or simple trend state from publication date |
| Timing | Uniform broad window of equal length, plus no-timing baseline |
| Price range | Prior-volatility naive range and no-target baseline |
| Rotation | BTC-only and first-cross ETH/BTC baselines |
| Topping signal | Hold-core and simple drawdown-trigger baseline |
| Trade | Hold underlying, cash and stated stop/target strategy |
| Framework action | Actual framework action versus no-action counterfactual |

Wave 1 uses categorical scoring and does not claim baseline superiority until benchmark calculations are complete.

## No blended score

```text
ONE_OVERALL_TECHDEV_ACCURACY_PERCENT: FORBIDDEN
ROADMAP_TIMING_RANGE_TRADE_BLEND: FORBIDDEN
PRIORITY_SELECTED_SAMPLE_PRESENTED_AS_ALL_CLAIMS: FORBIDDEN
```

Results must be reported by category with sample selection disclosed.

## Wave 1 selection rule

Wave 1 includes claims with the highest framework relevance:

- major BTC roadmap and target chains
- terminal bottom and top zones
- explicit timing windows
- broad alt rotation calls
- Topping Signals #1-#8
- explicit exit and de-risking logic
- source-backed trades with defined entries, stops and targets
- major model replacements

Individual minor-alt targets remain outside Wave 1 unless they affected portfolio governance.

## Audit cutoff

```yaml
audit_cutoff: 2026-07-11
open_2026_calendar_year_claims: KEEP_OPEN_UNTIL_WINDOW_MATURITY
current_live_framework_change_from_historical_scoring: NO_AUTOMATIC_CHANGE
```
