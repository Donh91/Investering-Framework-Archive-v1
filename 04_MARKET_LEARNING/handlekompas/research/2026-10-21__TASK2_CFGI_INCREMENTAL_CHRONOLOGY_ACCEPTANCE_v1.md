# Task 2 R2 · Incremental CFGI vs price and realized volatility

**Status:** Frozen after the historical period had already been exposed in Task2 research. NOT an unseen holdout, NOT PIT scientific admission, NOT original Kompas skill and NOT investment edge.

## Source and permission split
The study uses existing PUBLIC Daily Live Anchor v3 index snapshots for 4h CFGI composite and original PUBLIC 1h spot CSVs. It does not read restricted Round3 SC01/SC03/SC14 private provider values. The current private Round3 activation explicitly has hypothesis_testing_active=false and outcome_scoring_active=false; that firewall stays closed. Even in the separate public historical research lane, actual first vendor publication, independently known spot price timing, original Compass issuance and first delivery remain unverified.

## Frozen retrospective comparison without model selection
- Exactly two models for each symbol BTC and ETH: BASELINE logistic regression on previous 4h spot momentum and prior 8 completed 1h log-return volatility; AUGMENTED exact same inputs plus original 4h CFGI score centered at 50.
- Common fixed L2 0.3, batch gradient step 0.08, exactly 750 iterations, train-only mean/std and capped standardized values. Score probabilities using proper Brier and log loss; no optimized threshold.
- TRAIN Aug 18-Sep 27; EMBARGO Sep 28; VALIDATION Sep 29-Oct 5; EMBARGO Oct 6-8; INSPECTED-TEST Oct 9-20 2026. Holdout outcomes were previously visible and cannot be presented as scientific OOS.
- Use identical original capture opportunities/price targets, strict row-age/source receipts, exclude duplicate exact symbol/provider-observation timestamps, and record source gaps. No interpolation or new API requests.
- Results are descriptive only, not independent shock-family tests or after-cost executable investor exits. If augmented model loses on Brier, do not force CFGI feature into Kompas. If it improves, that merits a separate genuinely forward frozen prospective study and false-sale/fee robustness; no live model promotion now.
- Output only aggregates, immutable blob identities and counts, not raw market/CFGI component values. Existing PR-only test job; no new scheduled workflow, route, paid backfill or portfolio activity.

## Release and next scientific acceptance
Run original archive/source-clock validation, negative control tests and applicable CI on exact PR head. Reconcile original attempted/censored/abstained forecasts before later original Kompas-vs-price baseline. For pullback EXIT and REENTRY, require original issued typed warnings and actual first delivery, paired HOLD and tier-specific executable spread/depth; action edge is a separate R3/R4 project. Existing CFGI credit note recommends no additional spend now.
