# False Positive & Negative Control Analysis

## Historical result

No false-positive or false-negative rate can be estimated. Eligible exact historical event count is `0`.

The absence of a complete event universe also means the archive cannot establish how many non-events, missed opportunities or matched non-trigger periods existed.

## Negative controls required for any future test

1. Matched non-trigger periods.
2. Timestamp-shift/placebo signals.
3. Component-only baselines.
4. ETH/BTC-only baseline.
5. BTC-dominance-only baseline.
6. Breadth-only baseline.
7. Simple combined baseline.
8. Current-stack same-window comparator, only prospectively on the same frozen window.

### Sensor-specific controls

- **Pre-Trigger:** stablecoin-flow only, large-cap-volume-share only, ETH/BTC only, BTC.D only and simple combinations.
- **Type 3:** simple `high BTC.D + weak breadth` veto.
- **ETF-era pullback/divergence:** ETF + ETH/BTC + breadth baseline, with BTC and ecosystem outcomes separated.
- **CCE:** independence-null/dependence benchmark.
- **ODM:** full fixed horizon panel, no best-horizon selection.

## Adversarial conclusion

A complex sensor that cannot beat or complement a simpler baseline must be classified `REDUNDANT` or `NOISE` after sufficient prospective sample. Historical complexity receives no presumption of value.
