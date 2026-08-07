# PDLT v1.1-RUN

Status: READY FOR IMPLEMENTATION / SHADOW ONLY

## Objective

Test whether CFGI component sequencing provides prospective deterioration lead-time beyond the existing framework, and whether OpenAI can extract additional incremental value without future-data leakage.

## Primary estimands

- B - A: deterministic incremental value of CFGI.
- D - C: incremental value of CFGI when read by the same OpenAI forward model.

Secondary:

- C - A: OpenAI value without CFGI.
- D - B: OpenAI value on top of CFGI.
- D - A: total challenger result, not attribution.

## Arms

A. Framework baseline, deterministic, no CFGI, no OpenAI.

B. Framework + CFGI, deterministic.

C. Framework + OpenAI, no CFGI.

D. Framework + CFGI + OpenAI.

All arms must share the same cutoff timestamp and event window.

## CFGI budget

Historical discovery:

- MARKET 4h: 720 rows x 10 fields = 7,200 credits.
- BTC + ETH 4h: 120 rows x 2 symbols x 10 fields = 2,400 credits.
- MARKET + BTC + ETH 1d: 90 rows x 3 symbols x 10 fields = 2,700 credits.

Historical total = 12,300 credits.

Prospective 15m event burst:

- 16 rows x 3 symbols x 10 fields = 480 credits.
- 12 planned bursts = 5,760 credits.
- 4 reserve bursts = 1,920 credits.

Planned total = 18,060 credits.
Absolute maximum = 19,980 credits.
Hard cap = 20,000 credits.

Normal five-times-daily CFGI owner captures are reused. PDLT must not buy duplicate normal snapshots.

## CFGI epoch boundary

CFGI data before and after 2026-07-08 are tagged separately:

- LEGACY_PRE_20260708
- UPGRADED_POST_20260708

Cross-epoch candidate logic should prefer deltas, slopes, ranks, percentiles, acceleration, ordering and divergence over absolute raw thresholds.

## OpenAI budget

Discovery and critic: gpt-5.6-sol.
Forward arms C and D: gpt-5.6-terra, medium reasoning.

Planned cap: $5.
Soft stop: $8.
Hard cap: $10.

store=false. No web, file search or external tools during frozen forward forecasts.

## Candidate limits

Maximum:

- 3 candidates.
- 4 CFGI components per candidate.
- 4 sequence steps.
- 2 symbols.
- 2 timeframes.

Candidate definitions are immutable after freeze.

## Outcomes

PULLBACK_72H

Primary continuous measure: maximum adverse excursion over the following 72 hours. Binary threshold must be frozen from pre-holdout historical price distributions before holdout evaluation.

HEAVY_PULLBACK_7D

Same principle over 7 days with a materially larger threshold.

PRICE_DISTRIBUTION_14D

Must be defined without CFGI inputs. It should require a deterministic combination of material adverse excursion, break of a frozen price anchor, failed reclaim, persistence below the anchor and subsequent downside/lower-low confirmation.

ECOSYSTEM_DISTRIBUTION_14D

Secondary research label. May include breadth and ETH/BTC deterioration, but it cannot be the primary success label for proving CFGI value.

## Prospective census

Produce one frozen daily MARKET observation across A/B/C/D at the same timestamp. This is mandatory for base-rate, false-negative, Brier and calibration measurement.

## Event bursts

Event bursts exist only for higher-resolution sequencing and lead-time analysis.

- 72 hour cooldown.
- Events within one 14 day deterioration episode share one episode id.
- Earliest qualifying warning is retained for lead-time scoring.
- Later warnings cannot replace it.

## Statistics

Evaluate on independent episodes, not every raw 15m/4h row as independent samples.

Primary metrics:

- Brier score.
- Calibration.
- Precision / recall.
- False-positive rate.
- Median warning lead-time.
- MAE after warning.
- MFE after warning.
- Missed-upside.
- Damage-avoided proxy.

Confidence intervals must resample at episode level.

## Evidence gates

Under 30 matured independent observations: INSUFFICIENT_EVIDENCE.

30 matured observations: provisional review permitted.

90 matured observations plus at least 3 materially different regimes: component/frequency change review permitted.

No automatic canonical promotion.

## Kill criteria

Immediate stop or version boundary on:

- future-data leakage;
- timestamp alignment failure;
- candidate mutation after freeze;
- outcome mutation after freeze;
- unhandled CFGI epoch contamination;
- OpenAI prompt/model drift without a version boundary;
- CFGI hard-cap risk;
- OpenAI hard-cap risk;
- billing receipt mismatch;
- independent execution receipt failure.

Candidate-specific kill is allowed after sufficient matured observations when CFGI adds no incremental value, the OpenAI challenger adds no value, false positives dominate protection value, opportunity cost dominates avoided damage, or a candidate only duplicates an existing framework signal.

Negative results remain archived and are not repaired by retroactive candidate edits.

## Archive routing

- Candidate specs -> existing experiment lifecycle.
- Observations -> existing experiment lifecycle.
- Frozen forecasts -> Forecast Memory.
- Mature outcomes -> Outcome Memory.
- Raw CFGI experiment pulls -> compressed cold/raw evidence with receipts.
- Independent verification -> existing experiment execution plane.
- Weekly summary -> only new matured findings, failures or materially changed evidence.

No new canonical framework rule is created by this experiment.
